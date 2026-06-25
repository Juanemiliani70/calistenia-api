# MAIN.PY: PUNTO DE ENTRADA DE LA APLICACION

# Importación principal de FastAPI
from fastapi import FastAPI

# Permite configurar CORS — necesario para que Flutter pueda hacer requests a la API
from fastapi.middleware.cors import CORSMiddleware

# Configuración de la aplicación (variables de entorno)
from app.core.config import settings

from app.api.v1.router import api_router

# Creación de la instancia principal de la aplicación
app = FastAPI(
    title="Calistenia API",
    description="Backend para la app de calistenia — Sprint 1: Autenticación y Gestión de Usuarios",
    version="0.1.0",
)

# Configuración de CORS
# En desarrollo permitimos cualquier origen — en producción esto se restringe
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar todos los endpoints bajo /api/v1
app.include_router(api_router)

# Ruta raíz — sirve para verificar que la API está funcionando
@app.get("/")
def root():
    return {"message": "Calistenia API funcionando", "version": "0.1.0"}

# Ruta de health check — útil para el deploy
@app.get("/health")
def health():
    return {"status": "ok"}