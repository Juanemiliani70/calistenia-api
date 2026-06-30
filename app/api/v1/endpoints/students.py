from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.student import AlumnoResponse, AlumnoRevision
from app.services.student import (
    obtener_alumnos_pendientes,
    obtener_alumnos_aprobados,
    obtener_alumno,
    revisar_alumno
)
from app.core.dependencies import get_profesor_actual, get_usuario_actual
from app.models.user import Usuario
from app.models.teacher import Profesor

router = APIRouter(prefix="/alumnos", tags=["Alumnos"])

@router.get("/pendientes", response_model=list[AlumnoResponse])
def listar_pendientes(
    db: Session = Depends(get_db),
    profesor: Usuario = Depends(get_profesor_actual)
):
    """
    HU-06 — Lista todos los alumnos en estado pendiente.
    Solo accesible por profesores.
    """
    profesor_perfil = db.query(Profesor).filter(Profesor.id_usuario == profesor.id).first()
    return obtener_alumnos_pendientes(db, profesor_perfil.id)

@router.patch("/{id_alumno}/revision", response_model=AlumnoResponse)
def revisar_solicitud(
    id_alumno: int,
    datos: AlumnoRevision,
    db: Session = Depends(get_db),
    profesor: Usuario = Depends(get_profesor_actual)
):
    """
    HU-06 — Aprueba o rechaza un alumno pendiente.
    Solo accesible por profesores.
    """
    profesor_perfil = db.query(Profesor).filter(Profesor.id_usuario == profesor.id).first()
    return revisar_alumno(db, id_alumno, datos, profesor_perfil.id)

@router.get("/aprobados", response_model=list[AlumnoResponse])
def listar_aprobados(
    db: Session = Depends(get_db),
    profesor: Usuario = Depends(get_profesor_actual)
):
    """
    Lista todos los alumnos aprobados por el profesor autenticado.
    Solo accesible por profesores.
    """
    profesor_perfil = db.query(Profesor).filter(Profesor.id_usuario == profesor.id).first()
    return obtener_alumnos_aprobados(db, profesor_perfil.id)

@router.get("/{id_alumno}", response_model=AlumnoResponse)
def obtener_detalle_alumno(
    id_alumno: int,
    db: Session = Depends(get_db),
    profesor: Usuario = Depends(get_profesor_actual)
):
    """
    Devuelve el detalle de un alumno por su id.
    Solo accesible por el profesor al que pertenece el alumno.
    """
    profesor_perfil = db.query(Profesor).filter(Profesor.id_usuario == profesor.id).first()
    return obtener_alumno(db, id_alumno, profesor_perfil.id)