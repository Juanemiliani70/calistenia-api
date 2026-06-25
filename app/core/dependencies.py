from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError

from app.db.database import get_db
from app.models.user import Usuario, TipoUsuario
from app.core.security import verificar_token

# Le indica a FastAPI dónde está el endpoint de login para obtener el token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_usuario_actual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Dependencia que se usa en los endpoints protegidos.
    Verifica el token JWT y devuelve el usuario autenticado.
    Lanza 401 si el token es inválido o expiró.
    """
    credenciales_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verificar_token(token)
        id_usuario: str = payload.get("sub")
        if id_usuario is None:
            raise credenciales_exception
    except JWTError:
        raise credenciales_exception

    # Buscar el usuario en la BD
    usuario = db.query(Usuario).filter(Usuario.id == int(id_usuario)).first()
    if usuario is None or not usuario.is_active:
        raise credenciales_exception

    return usuario

def get_profesor_actual(usuario: Usuario = Depends(get_usuario_actual)) -> Usuario:
    """
    Dependencia que verifica que el usuario autenticado sea un profesor.
    Lanza 403 si el usuario es alumno.
    """
    if usuario.tipo != TipoUsuario.profesor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido a profesores"
        )
    return usuario

def get_admin_actual(usuario: Usuario = Depends(get_usuario_actual)) -> Usuario:
    """
    Dependencia que verifica que el usuario autenticado sea admin.
    Lanza 403 si no es admin.
    """
    if usuario.tipo != TipoUsuario.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido a administradores"
        )
    return usuario