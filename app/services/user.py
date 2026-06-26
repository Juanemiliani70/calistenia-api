from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import Usuario, TipoUsuario
from app.models.student import Alumno
from app.models.teacher import Profesor
from app.schemas.teacher import ProfesorUpdate

# ── HU-09 — GESTIÓN DE ROLES ──────────────────────────────────────────────────

def cambiar_rol(db: Session, id_usuario: int, nuevo_rol: TipoUsuario) -> Usuario:
    """
    HU-09 — Cambia el rol de un usuario.
    Solo accesible por admins.
    """
    usuario = db.query(Usuario).filter(Usuario.id == id_usuario).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    usuario.tipo = nuevo_rol
    db.commit()
    db.refresh(usuario)
    return usuario

def listar_usuarios(db: Session) -> list[Usuario]:
    """
    HU-09 — Lista todos los usuarios del sistema.
    Solo accesible por admins.
    """
    return db.query(Usuario).filter(Usuario.is_active == True).all()

# ── HU-10 — EDICIÓN DE PERFIL ─────────────────────────────────────────────────

def editar_perfil_profesor(db: Session, id_usuario: int, datos: ProfesorUpdate) -> Profesor:
    """
    HU-10 — Actualiza los datos del perfil del profesor.
    """
    profesor = db.query(Profesor).filter(Profesor.id_usuario == id_usuario).first()
    if not profesor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de profesor no encontrado"
        )

    # Actualiza solo los campos que vienen en el request
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(profesor, campo, valor)

    db.commit()
    db.refresh(profesor)
    return profesor

def editar_perfil_alumno(db: Session, id_usuario: int, datos: dict) -> Alumno:
    """
    HU-10 — Actualiza los datos del perfil del alumno.
    """
    alumno = db.query(Alumno).filter(Alumno.id_usuario == id_usuario).first()
    if not alumno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de alumno no encontrado"
        )

    for campo, valor in datos.items():
        setattr(alumno, campo, valor)

    db.commit()
    db.refresh(alumno)
    return alumno

# ── HU-11 — ELIMINACIÓN DE CUENTA ────────────────────────────────────────────

def eliminar_usuario(db: Session, id_usuario: int) -> dict:
    """
    HU-11 — Baja lógica del usuario (is_active = False).
    Solo accesible por admins.
    """
    usuario = db.query(Usuario).filter(Usuario.id == id_usuario).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    if not usuario.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya está eliminado"
        )

    usuario.is_active = False
    db.commit()
    return {"message": f"Usuario {usuario.email} eliminado correctamente."}