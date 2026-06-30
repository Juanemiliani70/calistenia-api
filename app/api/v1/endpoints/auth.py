from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.student import AlumnoCreate, AlumnoResponse
from app.schemas.teacher import ProfesorCreate, ProfesorResponse
from app.schemas.token import Token
from app.schemas.user import UsuarioResponse
from app.services.auth import (
    registrar_alumno, registrar_profesor,
    verificar_email, login,
    solicitar_recuperacion, resetear_password
)
from app.services.email import (
    enviar_email_verificacion,
    enviar_email_recuperacion
)
from app.core.dependencies import get_usuario_actual
from app.models.user import Usuario, TipoUsuario
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/auth", tags=["Autenticación"])

# Schema inline para recuperación de contraseña
class SolicitudRecuperacion(BaseModel):
    email: EmailStr

class NuevaPassword(BaseModel):
    token: str
    nueva_password: str

@router.post("/register/alumno", response_model=AlumnoResponse, status_code=status.HTTP_201_CREATED)
async def register_alumno(
    datos: AlumnoCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    HU-02 — Registro de alumno.
    Crea la cuenta y envía email de verificación en background.
    """
    usuario, token = registrar_alumno(db, datos)
    # Envía el email en background para no bloquear la respuesta
    background_tasks.add_task(enviar_email_verificacion, usuario.email, token)
    return usuario.alumno

@router.post("/register/profesor", response_model=ProfesorResponse, status_code=status.HTTP_201_CREATED)
async def register_profesor(
    datos: ProfesorCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    HU-03 — Registro de profesor.
    Crea la cuenta y envía email de verificación en background.
    """
    usuario, token = registrar_profesor(db, datos)
    background_tasks.add_task(enviar_email_verificacion, usuario.email, token)
    return usuario.profesor

@router.get("/verificar-email")
def verificar_email_endpoint(token: str, db: Session = Depends(get_db)):
    """
    HU-05 — Verifica el email del usuario a partir del token recibido.
    El usuario hace clic en el enlace del email y llega a este endpoint.
    """
    usuario = verificar_email(db, token)
    return {"message": f"Email verificado correctamente. Ya podés iniciar sesión, {usuario.email}."}

@router.post("/login", response_model=Token)
def login_usuario(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    HU-07 — Inicio de sesión.
    """
    return login(db, email=form_data.username, password=form_data.password)

@router.get("/me", response_model=UsuarioResponse)
def get_me(
    usuario_actual: Usuario = Depends(get_usuario_actual),
    db: Session = Depends(get_db)
):
    """
    Devuelve los datos del usuario autenticado, incluyendo su nombre.
    """
    nombre = None
    if usuario_actual.tipo == TipoUsuario.alumno and usuario_actual.alumno:
        nombre = usuario_actual.alumno.nombre
    elif usuario_actual.tipo == TipoUsuario.profesor and usuario_actual.profesor:
        nombre = usuario_actual.profesor.nombre

    return UsuarioResponse(
        id=usuario_actual.id,
        email=usuario_actual.email,
        tipo=usuario_actual.tipo,
        nombre=nombre,
        email_verified=usuario_actual.email_verified,
        is_active=usuario_actual.is_active,
        created_at=usuario_actual.created_at,
    )

@router.post("/recuperar-password")
async def solicitar_recuperacion_endpoint(
    datos: SolicitudRecuperacion,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    HU-08 — Solicitud de recuperación de contraseña.
    Siempre devuelve el mismo mensaje por seguridad.
    """
    resultado = solicitar_recuperacion(db, datos.email)
    if resultado:
        usuario, token = resultado
        background_tasks.add_task(enviar_email_recuperacion, usuario.email, token)
    return {"message": "Si el email existe, recibirás un enlace de recuperación."}

@router.post("/resetear-password")
def resetear_password_endpoint(datos: NuevaPassword, db: Session = Depends(get_db)):
    """
    HU-08 — Restablece la contraseña usando el token de recuperación.
    """
    resetear_password(db, datos.token, datos.nueva_password)
    return {"message": "Contraseña actualizada correctamente."}

@router.get("/mi-codigo-invitacion")
def obtener_mi_codigo(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """
    Devuelve el código de invitación del profesor autenticado,
    para que lo comparta con sus alumnos.
    """
    from app.models.teacher import Profesor
    profesor = db.query(Profesor).filter(Profesor.id_usuario == usuario.id).first()
    if not profesor:
        raise HTTPException(status_code=404, detail="Solo los profesores tienen código de invitación")
    return {"codigo_invitacion": profesor.codigo_invitacion}