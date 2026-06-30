from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.database import Base

class NivelAlumno(enum.Enum):
    principiante = "principiante"
    intermedio = "intermedio"
    avanzado = "avanzado"

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

    # Profesor al que pertenece este alumno — se completa al registrarse con el código de invitación
    id_profesor = Column(Integer, ForeignKey("profesores.id"), nullable=False)

    # Datos personales
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)

    # Nivel de experiencia en calistenia
    nivel = Column(Enum(NivelAlumno), default=NivelAlumno.principiante)

    # Estado de aprobación por parte del profesor (HU-06)
    estado = Column(Enum(EstadoAlumno), default=EstadoAlumno.pendiente)

    # Profesor que revisó la solicitud — puede ser distinto si en el futuro se permite transferencia
    id_profesor_revisor = Column(Integer, ForeignKey("profesores.id"), nullable=True)

    # Fecha en que fue aprobado o rechazado
    fecha_revision = Column(DateTime, nullable=True)

    # Fecha de creación del perfil
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación con la tabla usuarios
    usuario = relationship("Usuario", back_populates="alumno")

    # Relación con el profesor al que pertenece (su academia)
    profesor = relationship("Profesor", foreign_keys=[id_profesor], back_populates="alumnos")

    # Relación con el profesor que lo revisó
    profesor_revisor = relationship("Profesor", foreign_keys=[id_profesor_revisor])