from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime

from app.models.student import Alumno, EstadoAlumno
from app.models.teacher import Profesor
from app.schemas.student import AlumnoRevision

def obtener_alumnos_pendientes(db: Session, id_profesor: int) -> list[Alumno]:
    """
    Devuelve la lista de alumnos en estado pendiente.
    Solo puede ser llamado por un profesor (HU-06).
    """
    return db.query(Alumno).filter(Alumno.estado == EstadoAlumno.pendiente).all()

def revisar_alumno(db: Session, id_alumno: int, datos: AlumnoRevision, id_profesor: int) -> Alumno:
    """
    Aprueba o rechaza un alumno pendiente.
    Solo puede ser llamado por un profesor (HU-06).
    """
    # Verificar que el alumno existe
    alumno = db.query(Alumno).filter(Alumno.id == id_alumno).first()
    if not alumno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alumno no encontrado"
        )

    # Verificar que el alumno está en estado pendiente
    if alumno.estado != EstadoAlumno.pendiente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El alumno ya fue revisado"
        )

    # Actualizar el estado del alumno
    alumno.estado = datos.estado
    alumno.id_profesor_revisor = id_profesor
    alumno.fecha_revision = datetime.utcnow()

    db.commit()
    db.refresh(alumno)
    return alumno

def obtener_alumno(db: Session, id_alumno: int) -> Alumno:
    """Devuelve un alumno por su id."""
    alumno = db.query(Alumno).filter(Alumno.id == id_alumno).first()
    if not alumno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alumno no encontrado"
        )
    return alumno

def obtener_alumnos_aprobados(db: Session, id_profesor: int) -> list[Alumno]:
    """Devuelve la lista de alumnos aprobados por un profesor específico."""
    return db.query(Alumno).filter(
        Alumno.estado == EstadoAlumno.aprobado,
        Alumno.id_profesor_revisor == id_profesor
    ).all()