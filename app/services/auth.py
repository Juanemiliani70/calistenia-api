from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta

from app.models.user import Usuario, TipoUsuario
from app.models.student import Alumno, EstadoAlumno
from app.models.teacher import Profesor
from app.models.token import RefreshToken
from app.schemas.student import AlumnoCreate
from app.schemas.teacher import ProfesorCreate
from app.core.security import hashear_password, verificar_password, crear_access_token, crear_refresh_token, verificar_token
from app.core.config import settings


# ── REGISTRO ─────────────────────────────────────────────────────────────────

def registrar_alumno(db: Session, datos: AlumnoCreate) -> tuple[Usuario, str]:
    """
    HU-02 — Crea un nuevo usuario de tipo alumno.
    El alumno debe ingresar el código de invitación de su profesor para unirse a su academia.
    Devuelve el usuario y el token de verificación para enviar por email.
    """
    if db.query(Usuario).filter(Usuario.email == datos.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )

    # Validar que el código de invitación corresponda a un profesor existente
    profesor = db.query(Profesor).filter(
        Profesor.codigo_invitacion == datos.codigo_invitacion
    ).first()

    if not profesor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código de invitación inválido"
        )

    usuario = Usuario(
        email=datos.email,
        password=hashear_password(datos.password),
        tipo=TipoUsuario.alumno,
    )
    db.add(usuario)
    db.flush()

    alumno = Alumno(
        id_usuario=usuario.id,
        id_profesor=profesor.id,
        nombre=datos.nombre,
        apellido=datos.apellido,
        nivel=datos.nivel,
    )
    db.add(alumno)
    db.commit()
    db.refresh(usuario)

    token_verificacion = crear_access_token(
        data={"sub": str(usuario.id), "tipo": "email_verification"},
    )

    return usuario, token_verificacion

def registrar_profesor(db: Session, datos: ProfesorCreate) -> Usuario:
    """
    Crea un nuevo usuario de tipo profesor.
    El profesor tiene acceso inmediato sin necesidad de aprobación.
    """
    # Verificar que el email no esté registrado
    if db.query(Usuario).filter(Usuario.email == datos.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )

    # Crear el usuario base
    usuario = Usuario(
        email=datos.email,
        password=hashear_password(datos.password),
        tipo=TipoUsuario.profesor,
    )
    db.add(usuario)
    db.flush()

    # Crear el perfil del profesor vinculado al usuario
    profesor = Profesor(
        id_usuario=usuario.id,
        nombre=datos.nombre,
        apellido=datos.apellido,
        especialidad=datos.especialidad,
        años_experiencia=datos.años_experiencia,
        descripcion_bio=datos.descripcion_bio,
    )
    db.add(profesor)
    db.commit()
    db.refresh(usuario)
    token_verificacion = crear_access_token(
        data={"sub": str(usuario.id), "tipo": "email_verification"},
    )
    return usuario, token_verificacion

def verificar_email(db: Session, token: str) -> Usuario:
    """
    HU-05 — Verifica el email del usuario a partir del token recibido.
    """
    try:
        payload = verificar_token(token)
        id_usuario = int(payload.get("sub"))
        tipo = payload.get("tipo")

        if tipo != "email_verification":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido"
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido o expirado"
        )

    usuario = db.query(Usuario).filter(Usuario.id == id_usuario).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    if usuario.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya fue verificado"
        )

    usuario.email_verified = True
    db.commit()
    db.refresh(usuario)
    return usuario

# ── LOGIN ─────────────────────────────────────────────────────────────────────

def login(db: Session, email: str, password: str) -> dict:
    """
    Valida las credenciales y devuelve access token y refresh token.
    Lanza error si el email no existe, la contraseña es incorrecta,
    o la cuenta no está activa.
    """
    # Buscar el usuario por email
    usuario = db.query(Usuario).filter(Usuario.email == email).first()

    # Verificar que existe y la contraseña es correcta
    if not usuario or not verificar_password(password, usuario.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )

    # Verificar que la cuenta está activa
    if not usuario.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta está desactivada"
        )

    # Verificar que confirmó el email
    if not usuario.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debes verificar tu email antes de iniciar sesión"
        )
    
     # Si es alumno, validar que su profesor lo haya aprobado (HU-06)
    if usuario.tipo == TipoUsuario.alumno and usuario.alumno:
        if usuario.alumno.estado == EstadoAlumno.pendiente:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tu cuenta está pendiente de aprobación por tu profesor"
            )
        if usuario.alumno.estado == EstadoAlumno.rechazado:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tu solicitud fue rechazada por el profesor"
            )

    # Generar tokens
    payload = {"sub": str(usuario.id), "tipo": usuario.tipo.value}
    access_token = crear_access_token(payload)
    refresh_token = crear_refresh_token(payload)

    # Guardar el refresh token en la BD
    db_token = RefreshToken(
        id_usuario=usuario.id,
        token=refresh_token,
        expires_at=datetime.utcnow() + __import__('datetime').timedelta(days=7)
    )
    db.add(db_token)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

# ── RECUPERACIÓN DE CONTRASEÑA ────────────────────────────────────────────────

def solicitar_recuperacion(db: Session, email: str) -> tuple[Usuario, str] | None:
    """
    HU-08 — Genera un token de recuperación de contraseña.
    Devuelve None si el email no existe (por seguridad no revelamos si existe).
    """
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        return None

    token = crear_access_token(
        data={"sub": str(usuario.id), "tipo": "password_reset"},
    )
    return usuario, token

def resetear_password(db: Session, token: str, nueva_password: str) -> Usuario:
    """
    HU-08 — Actualiza la contraseña del usuario a partir del token de recuperación.
    """
    try:
        payload = verificar_token(token)
        id_usuario = int(payload.get("sub"))
        tipo = payload.get("tipo")

        if tipo != "password_reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido"
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido o expirado"
        )

    usuario = db.query(Usuario).filter(Usuario.id == id_usuario).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    usuario.password = hashear_password(nueva_password)
    db.commit()
    db.refresh(usuario)
    return usuario