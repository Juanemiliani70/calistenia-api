from pydantic import BaseModel
from datetime import datetime
from app.models.student import NivelAlumno, EstadoAlumno

class AlumnoBase(BaseModel):
    nombre: str
    apellido: str
    nivel: NivelAlumno = NivelAlumno.principiante

# Schema para registrar un alumno — ahora requiere el código de invitación del profesor
class AlumnoCreate(AlumnoBase):
    email: str
    password: str
    codigo_invitacion: str

class AlumnoRevision(BaseModel):
    estado: EstadoAlumno

# Schema para la respuesta — incluye el id del profesor al que pertenece
class AlumnoResponse(AlumnoBase):
    id: int
    id_profesor: int
    estado: EstadoAlumno
    created_at: datetime

    class Config:
        from_attributes = True