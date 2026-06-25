from pydantic import BaseModel
from datetime import datetime
from app.models.student import NivelAlumno, EstadoAlumno

# Schema base — campos comunes
class AlumnoBase(BaseModel):
    nombre: str
    apellido: str
    nivel: NivelAlumno = NivelAlumno.principiante

# Schema para registrar un alumno — se usa en el endpoint de registro
class AlumnoCreate(AlumnoBase):
    email: str
    password: str

# Schema para aprobar o rechazar un alumno — se usa en el endpoint de HU-06
class AlumnoRevision(BaseModel):
    estado: EstadoAlumno
    
# Schema para la respuesta — lo que devuelve la API
class AlumnoResponse(AlumnoBase):
    id: int
    estado: EstadoAlumno
    created_at: datetime

    class Config:
        from_attributes = True