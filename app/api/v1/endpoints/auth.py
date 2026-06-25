from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.student import AlumnoCreate, AlumnoResponse
from app.schemas.teacher import ProfesorCreate, ProfesorResponse
from app.schemas.token import Token, TokenRefresh
from app.schemas.user import UsuarioResponse
from app.services.auth import registrar_alumno, registrar_profesor, login
from app.core.dependencies import get_usuario_actual
from app.models.user import Usuario

# Router con prefijo /auth — todos los endpoints de este archivo empiezan con /auth
router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/register/alumno", response_model=AlumnoResponse, status_code=status.HTTP_201_CREATED)
def register_alumno(datos: AlumnoCreate, db: Session = Depends(get_db)):
    """
    HU-02 — Registro de alumno.
    Crea una cuenta de alumno en estado pendiente.
    No requiere autenticación.
    """
    usuario = registrar_alumno(db, datos)
    return usuario.alumno

@router.post("/register/profesor", response_model=ProfesorResponse, status_code=status.HTTP_201_CREATED)
def register_profesor(datos: ProfesorCreate, db: Session = Depends(get_db)):
    """
    HU-03 — Registro de profesor.
    Crea una cuenta de profesor con acceso inmediato.
    No requiere autenticación.
    """
    usuario = registrar_profesor(db, datos)
    return usuario.profesor

@router.post("/login", response_model=Token)
def login_usuario(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    HU-07 — Inicio de sesión.
    Recibe email y contraseña, devuelve access token y refresh token.
    Usa OAuth2PasswordRequestForm — espera los campos 'username' y 'password'.
    """
    return login(db, email=form_data.username, password=form_data.password)

@router.get("/me", response_model=UsuarioResponse)
def get_me(usuario_actual: Usuario = Depends(get_usuario_actual)):
    """
    Devuelve los datos del usuario autenticado.
    Requiere token JWT válido en el header Authorization: Bearer <token>.
    """
    return usuario_actual