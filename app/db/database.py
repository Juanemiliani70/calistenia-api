# SQLAlchemy — motor de base de datos y sesiones
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Configuración central de la app — lee el DATABASE_URL del .env
from app.core.config import settings

# Crear el motor de conexión a PostgreSQL
# El DATABASE_URL viene del .env: postgresql://usuario:password@localhost:5432/calistenia_db
engine = create_engine(settings.DATABASE_URL)

# Fábrica de sesiones — cada request a la API abre y cierra una sesión
# autocommit=False → los cambios no se guardan hasta hacer commit explícito
# autoflush=False → no sincroniza automáticamente con la BD antes de cada query
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base para todos los modelos SQLAlchemy
# Todos los modelos (Usuario, Alumno, Profesor) van a heredar de esta clase
class Base(DeclarativeBase):
    pass

# Función generadora de sesión — se usa como dependencia en los endpoints de FastAPI
# Garantiza que la sesión siempre se cierre al terminar el request, incluso si hay error
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()