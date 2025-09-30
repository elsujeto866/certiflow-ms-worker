"""
Aplicación principal FastAPI.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import uvicorn

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.api.routes import router
from app.models.schemas import HealthResponse, ErrorResponse
from app.models.exceptions import CertiflowException

# Configurar logging
setup_logging()
logger = get_logger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Microservicio para procesar PDFs con IA y generar reportes Excel",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(router, prefix="/api/v1", tags=["document-processing"])


@app.exception_handler(CertiflowException)
async def certiflow_exception_handler(request, exc: CertiflowException):
    """Manejador para excepciones personalizadas."""
    logger.error(f"CertiflowException: {exc.message}")
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            message=exc.message,
            error_code=exc.error_code
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Manejador para excepciones generales."""
    logger.error(f"Excepción no manejada: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            message="Error interno del servidor"
        ).dict()
    )


@app.get("/", response_model=dict)
async def root():
    """Endpoint raíz con información básica."""
    return {
        "service": settings.app_name,
        "version": settings.version,
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Endpoint de health check."""
    # TODO: Agregar verificaciones de servicios externos
    services_status = {
        "openai": "unknown",  # Se podría verificar con openai_service.test_connection()
        "file_system": "ok",
        "logging": "ok"
    }
    
    return HealthResponse(
        status="healthy",
        version=settings.version,
        timestamp=datetime.now(),
        services=services_status
    )


@app.on_event("startup")
async def startup_event():
    """Eventos a ejecutar al iniciar la aplicación."""
    logger.info(f"Iniciando {settings.app_name} v{settings.version}")
    
    # Crear directorios necesarios
    import os
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    logger.info("Aplicación iniciada correctamente")


@app.on_event("shutdown")
async def shutdown_event():
    """Eventos a ejecutar al cerrar la aplicación."""
    logger.info("Cerrando aplicación...")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )