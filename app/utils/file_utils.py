"""
Utilidades para manejo de archivos.
"""
from fastapi import UploadFile, HTTPException
from pathlib import Path
import os
import uuid
from typing import List
from app.core.config import settings
from app.models.exceptions import FileValidationError
from app.core.logging import get_logger

logger = get_logger(__name__)


async def validate_file(file: UploadFile) -> None:
    """
    Valida un archivo subido.
    
    Args:
        file: Archivo a validar
        
    Raises:
        FileValidationError: Si el archivo no es válido
    """
    # Verificar que se subió un archivo
    if not file:
        raise FileValidationError("No se proporcionó ningún archivo")
    
    # Verificar nombre del archivo
    if not file.filename:
        raise FileValidationError("El archivo no tiene nombre")
    
    # Verificar extensión
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in settings.allowed_extensions:
        raise FileValidationError(
            f"Extensión no permitida. Extensiones permitidas: {settings.allowed_extensions}"
        )
    
    # Verificar tamaño (se hace leyendo el archivo)
    content = await file.read()
    await file.seek(0)  # Resetear posición para futuros usos
    
    if len(content) > settings.max_file_size:
        max_mb = settings.max_file_size / (1024 * 1024)
        raise FileValidationError(f"El archivo excede el tamaño máximo de {max_mb}MB")
    
    if len(content) == 0:
        raise FileValidationError("El archivo está vacío")
    
    logger.info(f"Archivo validado: {file.filename} ({len(content)} bytes)")


async def save_uploaded_file(file: UploadFile, content: bytes) -> str:
    """
    Guarda un archivo subido en el sistema de archivos.
    
    Args:
        file: Archivo subido
        content: Contenido del archivo en bytes
        
    Returns:
        str: Ruta donde se guardó el archivo
        
    Raises:
        FileValidationError: Si hay error guardando el archivo
    """
    try:
        # Crear directorio de uploads si no existe
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(exist_ok=True)
        
        # Generar nombre único para el archivo
        file_extension = Path(file.filename).suffix.lower()
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = upload_dir / unique_filename
        
        # Guardar archivo
        with open(file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"Archivo guardado: {file_path}")
        return str(file_path)
        
    except Exception as e:
        logger.error(f"Error guardando archivo: {e}")
        raise FileValidationError(f"Error guardando archivo: {e}")


def cleanup_old_files(directory: str, max_age_hours: int = 24) -> int:
    """
    Limpia archivos antiguos de un directorio.
    
    Args:
        directory: Directorio a limpiar
        max_age_hours: Edad máxima en horas para mantener archivos
        
    Returns:
        int: Número de archivos eliminados
    """
    try:
        dir_path = Path(directory)
        if not dir_path.exists():
            return 0
        
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        deleted_count = 0
        
        for file_path in dir_path.iterdir():
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                        logger.info(f"Archivo eliminado: {file_path}")
                    except Exception as e:
                        logger.warning(f"No se pudo eliminar {file_path}: {e}")
        
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error limpiando directorio {directory}: {e}")
        return 0


def get_file_info(file_path: str) -> dict:
    """
    Obtiene información de un archivo.
    
    Args:
        file_path: Ruta del archivo
        
    Returns:
        dict: Información del archivo
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return {"error": "Archivo no encontrado"}
        
        stat = path.stat()
        return {
            "name": path.name,
            "size": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "extension": path.suffix.lower(),
            "is_file": path.is_file(),
            "is_dir": path.is_dir()
        }
        
    except Exception as e:
        return {"error": str(e)}


def ensure_directory_exists(directory: str) -> bool:
    """
    Asegura que un directorio existe, creándolo si es necesario.
    
    Args:
        directory: Ruta del directorio
        
    Returns:
        bool: True si el directorio existe o se creó exitosamente
    """
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creando directorio {directory}: {e}")
        return False


def list_files_in_directory(directory: str, extension: str = None) -> List[dict]:
    """
    Lista archivos en un directorio.
    
    Args:
        directory: Directorio a listar
        extension: Filtrar por extensión (opcional)
        
    Returns:
        List[dict]: Lista de información de archivos
    """
    try:
        dir_path = Path(directory)
        if not dir_path.exists():
            return []
        
        files = []
        for file_path in dir_path.iterdir():
            if file_path.is_file():
                if extension and not file_path.suffix.lower() == extension.lower():
                    continue
                
                files.append(get_file_info(str(file_path)))
        
        return sorted(files, key=lambda x: x.get("modified", 0), reverse=True)
        
    except Exception as e:
        logger.error(f"Error listando archivos en {directory}: {e}")
        return []