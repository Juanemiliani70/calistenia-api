from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.models.user import TipoUsuario

# Schema base — campos comunes a todos los schemas de usuario
class UsuarioBase(BaseModel):
    email: EmailStr
    tipo: TipoUsuario

# Schema para crear un usuario — incluye la contraseña
class UsuarioCreate(UsuarioBase):
    password: str

# Schema para la respuesta — nunca devuelve la contraseña
class UsuarioResponse(UsuarioBase):
    id: int
    email_verified: bool
    is_active: bool
    created_at: datetime

    # Permite que Pydantic lea los datos desde un modelo SQLAlchemy
    class Config:
        from_attributes = True