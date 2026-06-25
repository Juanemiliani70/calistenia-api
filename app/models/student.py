from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.database import Base

# Enum para el nivel del alumno
class NivelAlumno(enum.Enum):
    principiante = "principiante"
    intermedio = "intermedio"
    avanzado = "avanzado"

# Enum para el estado de aprobación del alumno (HU-06)
class EstadoAlumno(enum.Enum):
    pendiente = "pendiente"
    aprobado = "aprobado"
    rechazado = "rechazado"

class Alumno(Base):
    __tablename__ = "alumnos"

    # Clave primaria autoincremental
    id = Column(Integer, primary_key=True, index=True)

    # Clave foránea — vincula el alumno con su usuario
    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=False, unique=True)

    # Datos personales
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)

    # Nivel de experiencia en calistenia
    nivel = Column(Enum(NivelAlumno), default=NivelAlumno.principiante)

    # Estado de aprobación por parte del profesor (HU-06)
    # Comienza en pendiente hasta que un profesor lo apruebe
    estado = Column(Enum(EstadoAlumno), default=EstadoAlumno.pendiente)

    # Profesor que revisó la solicitud — puede ser null si aún no fue revisada
    id_profesor_revisor = Column(Integer, ForeignKey("profesores.id"), nullable=True)

    # Fecha en que fue aprobado o rechazado
    fecha_revision = Column(DateTime, nullable=True)

    # Fecha de creación del perfil
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación con la tabla usuarios — accede al email, password, etc.
    usuario = relationship("Usuario", back_populates="alumno")

    # Relación con el profesor que lo revisó
    profesor_revisor = relationship("Profesor", foreign_keys=[id_profesor_revisor])