from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# Contexto de encriptación — usa bcrypt para hashear contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── CONTRASEÑAS ──────────────────────────────────────────────────────────────

def hashear_password(password: str) -> str:
    """Recibe la contraseña en texto plano y devuelve el hash para guardar en la BD."""
    return pwd_context.hash(password)

def verificar_password(password_plano: str, password_hasheado: str) -> bool:
    """Compara la contraseña ingresada con el hash guardado en la BD."""
    return pwd_context.verify(password_plano, password_hasheado)

# ── TOKENS JWT ───────────────────────────────────────────────────────────────

def crear_access_token(data: dict) -> str:
    """
    Genera un access token JWT de corta duración.
    Contiene el id y tipo del usuario — expira en ACCESS_TOKEN_EXPIRE_MINUTES.
    """
    payload = data.copy()
    expiracion = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expiracion, "type": "access"})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def crear_refresh_token(data: dict) -> str:
    """
    Genera un refresh token JWT de larga duración.
    Se usa para obtener un nuevo access token sin volver a iniciar sesión.
    Expira en REFRESH_TOKEN_EXPIRE_DAYS.
    """
    payload = data.copy()
    expiracion = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload.update({"exp": expiracion, "type": "refresh"})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verificar_token(token: str) -> dict:
    """
    Decodifica y valida un token JWT.
    Lanza JWTError si el token es inválido o expiró.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])