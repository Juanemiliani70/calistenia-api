from pydantic import BaseModel
from datetime import datetime

# Schema base — campos comunes
class ProfesorBase(BaseModel):
    nombre: str
    apellido: str
    especialidad: str | None = None
    años_experiencia: int | None = None
    descripcion_bio: str | None = None

# Schema para registrar un profesor
class ProfesorCreate(ProfesorBase):
    email: str
    password: str

# Schema para actualizar el perfil del profesor (HU-10)
class ProfesorUpdate(BaseModel):
    nombre: str | None = None
    apellido: str | None = None
    especialidad: str | None = None
    años_experiencia: int | None = None
    descripcion_bio: str | None = None

# Schema para la respuesta — lo que devuelve la API
class ProfesorResponse(ProfesorBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True