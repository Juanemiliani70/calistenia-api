from fastapi import APIRouter

# Importamos los routers de cada módulo
from app.api.v1.endpoints import auth, students, users

# Router principal de la versión 1 de la API
api_router = APIRouter(prefix="/api/v1")

# Registramos cada router con su prefijo
# Todos los endpoints de auth quedan bajo /api/v1/auth/...
api_router.include_router(auth.router)

# Todos los endpoints de alumnos quedan bajo /api/v1/alumnos/...
api_router.include_router(students.router)

#endpoints users
api_router.include_router(users.router)