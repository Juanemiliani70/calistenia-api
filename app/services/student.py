from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime

from app.models.student import Alumno, EstadoAlumno
from app.models.teacher import Profesor
from app.schemas.student import AlumnoRevision

def obtener_alumnos_pendientes(db: Session, id_profesor: int) -> list[Alumno]:
    """
    HU-06 — Lista los alumnos pendientes que pertenecen a la academia de este profesor.
    """
    return db.query(Alumno).filter(
        Alumno.id_profesor == id_profesor,
        Alumno.estado == EstadoAlumno.pendiente
    ).all()

def revisar_alumno(db: Session, id_alumno: int, datos: AlumnoRevision, id_profesor: int) -> Alumno:
    """
    HU-06 — Aprueba o rechaza un alumno pendiente.
    Solo puede revisar alumnos que pertenezcan a su propia academia.
    """
    alumno = db.query(Alumno).filter(
        Alumno.id == id_alumno,
        Alumno.id_profesor == id_profesor
    ).first()

    if not alumno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alumno no encontrado en tu academia"
        )

    if alumno.estado != EstadoAlumno.pendiente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El alumno ya fue revisado"
        )

    alumno.estado = datos.estado
    alumno.id_profesor_revisor = id_profesor
    alumno.fecha_revision = datetime.utcnow()

    db.commit()
    db.refresh(alumno)
    return alumno

def obtener_alumno(db: Session, id_alumno: int, id_profesor: int) -> Alumno:
    """Devuelve un alumno por su id — solo si pertenece a la academia del profesor."""
    alumno = db.query(Alumno).filter(
        Alumno.id == id_alumno,
        Alumno.id_profesor == id_profesor
    ).first()
    if not alumno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alumno no encontrado en tu academia"
        )
    return alumno

def obtener_alumnos_aprobados(db: Session, id_profesor: int) -> list[Alumno]:
    """Devuelve la lista de alumnos aprobados que pertenecen a este profesor."""
    return db.query(Alumno).filter(
        Alumno.estado == EstadoAlumno.aprobado,
        Alumno.id_profesor == id_profesor
    ).all()