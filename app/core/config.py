# Importación de BaseSettings — permite leer variables de entorno automáticamente
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Nombre de la aplicación
    APP_NAME: str = "Calistenia API"
    
    # Versión de la API
    APP_VERSION: str = "0.1.0"
    
    # URL de conexión a PostgreSQL - se lee del .env
    DATABASE_URL: str
    
    # Clave secreta para firmar los tokens JWT - se lee del .env
    SECRET_KEY: str
    
    # Algoritmo de encriptación para JWT
    ALGORITHM: str = "HS256"
    
    # Tiempo de expiración del access token en minutos
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Tiempo de expiración del refresh token en días
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    class Config:
        # Indica a Pydantic que lea las variables desde el archivo .envPy
        env_file = ".env"
        # Hace que las variables sean case-insensitive
        case_sensitive = False

# Instancia global — se importa desde cualquier parte del proyecto
# En lugar de crear un nuevo Settings() cada vez, siempre usamos este objeto
settings = Settings()