"""
Rutas principales de la API para el procesamiento de documentos.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import FileResponse
from typing import Optional, Dict, Any
import time
from datetime import datetime

from app.models.schemas import (
    PDFUploadResponse, ProcessingResponse, ExtractedData, 
    ProcessingRequest, ErrorResponse
)
from app.services.pdf_service import PDFService
from app.services.openai_service import OpenAIService
from app.services.excel_service import ExcelService
from app.services.orchestrator import orchestrator
from app.models.exceptions import (
    CertiflowException, PDFProcessingError, 
    OpenAIError, ExcelGenerationError
)
from app.utils.file_utils import validate_file, save_uploaded_file
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()




@router.post("/extract-personal-data/", response_model=Dict[str, Any])
async def extract_personal_data(file: UploadFile = File(..., description="Archivo PDF del cual extraer datos personales")):
    """
    Endpoint específico para extraer datos personales de un PDF.
    Retorna únicamente: nombre, cédula, email, provincia, ciudad, dirección, teléfono, celular, edad
    
    Args:
        file: Archivo PDF a procesar (required)
        
    Returns:
        Dict con los datos personales extraídos en formato JSON
        
    Example:
        curl -X POST "http://localhost:8000/api/v1/extract-personal-data/" \
             -H "accept: application/json" \
             -H "Content-Type: multipart/form-data" \
             -F "file=@documento.pdf"
    """
    start_time = time.time()
    
    try:
        # Validar que se recibió un archivo
        if not file or not file.filename:
            raise HTTPException(
                status_code=400, 
                detail="No se recibió ningún archivo. Asegúrate de enviar un archivo PDF en el campo 'file'."
            )
        
        logger.info(f"Iniciando extracción de datos personales de {file.filename}")
        
        # Validar archivo
        await validate_file(file)
        content = await file.read()
        
        # Validar que el contenido no esté vacío
        if not content:
            raise HTTPException(
                status_code=400,
                detail="El archivo está vacío o no se pudo leer correctamente."
            )

        # Procesar usando el Orchestrator (valida, extrae, procesa, opcionalmente genera Excel)
        logger.info("Procesando archivo con Orchestrator")
        # Orchestrator espera bytes; la extracción de texto (si es bloqueante) se ejecuta dentro
        result = await orchestrator.process_file(content, filename=file.filename, output_format="json")
        personal_data = result["data"]

        processing_time = time.time() - start_time
        logger.info(f"Extracción completada en {processing_time:.2f} segundos")

        return {
            "success": True,
            "data": {
                "nombre": personal_data.get("nombre"),
                "cedula": personal_data.get("cedula"), 
                "email": personal_data.get("email"),
                "provincia": personal_data.get("provincia"),
                "ciudad": personal_data.get("ciudad"),
                "direccion": personal_data.get("direccion"),
                "telefono": personal_data.get("telefono"),
                "celular": personal_data.get("celular"),
                "edad": personal_data.get("edad")
            },
            "metadata": {
                "processing_time": processing_time,
                "filename": file.filename,
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except PDFProcessingError as e:
        logger.error(f"Error procesando PDF: {e.message}")
        raise HTTPException(status_code=400, detail=f"Error procesando PDF: {e.message}")
    except OpenAIError as e:
        logger.error(f"Error con OpenAI: {e.message}")
        raise HTTPException(status_code=500, detail=f"Error procesando con IA: {e.message}")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


