from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.database import Base

class Profesor(Base):
    __tablename__ = "profesores"

    # Clave primaria autoincremental
    id = Column(Integer, primary_key=True, index=True)

    # Clave foránea — vincula el profesor con su usuario
    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=False, unique=True)

    # Datos personales
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)

    # Datos profesionales
    especialidad = Column(String, nullable=True)
    años_experiencia = Column(Integer, nullable=True)
    descripcion_bio = Column(String, nullable=True)

    # Fecha de creación del perfil
    created_at = Column(DateTime, default=datetime.utcnow)

    # Fecha de última actualización
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación con la tabla usuarios — accede al email, password, etc.
    usuario = relationship("Usuario", back_populates="profesor")

    # Relación con los alumnos que este profesor revisó
    alumnos_revisados = relationship(
        "Alumno",
        foreign_keys="Alumno.id_profesor_revisor",
        back_populates="profesor_revisor"
    )