"""
Configuración principal de la aplicación.
Maneja variables de entorno y configuraciones globales.
"""
try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback para versiones anteriores de pydantic
    from pydantic import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Configuración de la aplicación usando variables de entorno."""
    
    # Configuración de la aplicación
    app_name: str = "Certiflow API Worker"
    version: str = "1.0.0"
    debug: bool = False
    
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_max_tokens: int = 4000
    
    # Configuración de archivos
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: list = [".pdf"]
    upload_dir: str = "uploads"
    templates_dir: str = "templates"
    
    # Configuración del servidor
    host: str = "127.0.0.1"
    port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Instancia global de configuración
settings = Settings()