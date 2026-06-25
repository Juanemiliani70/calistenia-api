from pydantic import BaseModel

# Schema para la respuesta del login — lo que devuelve la API al iniciar sesión
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# Schema para refrescar el access token usando el refresh token
class TokenRefresh(BaseModel):
    refresh_token: str

# Schema con los datos que contiene el token JWT internamente
class TokenData(BaseModel):
    id_usuario: int | None = None
    tipo: str | None = None