from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.database import Base

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    # Clave primaria autoincremental
    id = Column(Integer, primary_key=True, index=True)

    # Clave foránea — vincula el token con su usuario
    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    # El token en sí — string largo generado con JWT
    token = Column(String, nullable=False, unique=True)

    # Si el token fue revocado — True cuando el usuario cierra sesión
    revocado = Column(Boolean, default=False)

    # Fecha de expiración — después de esta fecha el token no es válido
    expires_at = Column(DateTime, nullable=False)

    # Fecha de creación
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación con la tabla usuarios
    usuario = relationship("Usuario", back_populates="refresh_tokens")