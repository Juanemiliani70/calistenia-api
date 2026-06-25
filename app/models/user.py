# Tipos de columnas de SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship

# Fecha y hora actual
from datetime import datetime

# Enum de Python para definir valores posibles
import enum

# Base de la que heredan todos los modelos
from app.db.database import Base

# Enum para el tipo de usuario — define los valores válidos en la BD
class TipoUsuario(enum.Enum):
    alumno = "alumno"
    profesor = "profesor"
    admin = "admin"

class Usuario(Base):
    # Nombre de la tabla en PostgreSQL
    __tablename__ = "usuarios"

    # Clave primaria autoincremental
    id = Column(Integer, primary_key=True, index=True)

    # Email único — se usa para iniciar sesión
    email = Column(String, unique=True, index=True, nullable=False)

    # Contraseña hasheada con bcrypt — nunca se guarda en texto plano
    password = Column(String, nullable=False)

    # Tipo de cuenta: alumno, profesor o admin
    tipo = Column(Enum(TipoUsuario), nullable=False)

    # Si el usuario confirmó su email
    email_verified = Column(Boolean, default=False)

    # Si la cuenta está activa — False cuando se hace baja lógica
    is_active = Column(Boolean, default=True)

    # Fecha de creación — se setea automáticamente al crear el registro
    created_at = Column(DateTime, default=datetime.utcnow)

    # Fecha de última actualización
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones con otras tablas
    # uselist=False → es una relación 1 a 1 (un usuario tiene un solo perfil)
    alumno = relationship("Alumno", back_populates="usuario", uselist=False)
    profesor = relationship("Profesor", back_populates="usuario", uselist=False)
    refresh_tokens = relationship("RefreshToken", back_populates="usuario")