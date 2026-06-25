# Importamos todos los modelos para que Alembic los detecte
# al momento de generar las migraciones de base de datos.
# Sin estas importaciones, Alembic no vería las tablas y no generaría el SQL correcto.

from app.models.user import Usuario, TipoUsuario
from app.models.student import Alumno, NivelAlumno, EstadoAlumno
from app.models.teacher import Profesor
from app.models.token import RefreshToken