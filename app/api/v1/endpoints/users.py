from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.database import get_db
from app.models.user import Usuario, TipoUsuario
from app.schemas.user import UsuarioResponse
from app.schemas.teacher import ProfesorUpdate, ProfesorResponse
from app.schemas.student import AlumnoResponse
from app.services.user import (
    cambiar_rol, listar_usuarios,
    editar_perfil_profesor, editar_perfil_alumno,
    eliminar_usuario
)
from app.core.dependencies import get_usuario_actual, get_admin_actual

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

# Schema inline para cambio de rol
class CambioRol(BaseModel):
    nuevo_rol: TipoUsuario

# ── HU-09 — GESTIÓN DE ROLES ─────────────────────────────────────────────────

@router.get("/", response_model=list[UsuarioResponse])
def listar(
    db: Session = Depends(get_db),
    admin: Usuario = Depends(get_admin_actual)
):
    """
    HU-09 — Lista todos los usuarios activos.
    Solo accesible por admins.
    """
    return listar_usuarios(db)

@router.patch("/{id_usuario}/rol", response_model=UsuarioResponse)
def cambiar_rol_usuario(
    id_usuario: int,
    datos: CambioRol,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(get_admin_actual)
):
    """
    HU-09 — Cambia el rol de un usuario.
    Solo accesible por admins.
    """
    return cambiar_rol(db, id_usuario, datos.nuevo_rol)

# ── HU-10 — EDICIÓN DE PERFIL ────────────────────────────────────────────────

@router.patch("/me/perfil")
def editar_perfil(
    datos: ProfesorUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """
    HU-10 — Edita el perfil del usuario autenticado.
    Detecta si es alumno o profesor y actualiza el perfil correspondiente.
    """
    if usuario.tipo == TipoUsuario.profesor:
        return editar_perfil_profesor(db, usuario.id, datos)
    else:
        return editar_perfil_alumno(db, usuario.id, datos.model_dump(exclude_unset=True))

# ── HU-11 — ELIMINACIÓN DE CUENTA ────────────────────────────────────────────

@router.delete("/{id_usuario}")
def eliminar(
    id_usuario: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(get_admin_actual)
):
    """
    HU-11 — Baja lógica del usuario.
    Solo accesible por admins.
    """
    return eliminar_usuario(db, id_usuario)