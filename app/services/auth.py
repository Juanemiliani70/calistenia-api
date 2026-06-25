from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime

from app.models.user import Usuario, TipoUsuario
from app.models.student import Alumno
from app.models.teacher import Profesor
from app.models.token import RefreshToken
from app.schemas.student import AlumnoCreate
from app.schemas.teacher import ProfesorCreate
from app.core.security import hashear_password, verificar_password, crear_access_token, crear_refresh_token, verificar_token

# ── REGISTRO ─────────────────────────────────────────────────────────────────

def registrar_alumno(db: Session, datos: AlumnoCreate) -> Usuario:
    """
    Crea un nuevo usuario de tipo alumno.
    El alumno queda en estado 'pendiente' hasta que un profesor lo apruebe (HU-06).
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
        tipo=TipoUsuario.alumno,
    )
    db.add(usuario)
    db.flush()  # Genera el id del usuario sin hacer commit todavía

    # Crear el perfil del alumno vinculado al usuario
    alumno = Alumno(
        id_usuario=usuario.id,
        nombre=datos.nombre,
        apellido=datos.apellido,
        nivel=datos.nivel,
    )
    db.add(alumno)
    db.commit()
    db.refresh(usuario)
    return usuario

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