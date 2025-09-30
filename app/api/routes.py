"""
Rutas principales de la API para el procesamiento de documentos.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import FileResponse
from typing import Optional
import time
from datetime import datetime

from app.models.schemas import (
    PDFUploadResponse, ProcessingResponse, ExtractedData, 
    ProcessingRequest, ErrorResponse
)
from app.services.pdf_service import PDFService
from app.services.openai_service import OpenAIService
from app.services.excel_service import ExcelService
from app.models.exceptions import (
    CertiflowException, PDFProcessingError, 
    OpenAIError, ExcelGenerationError
)
from app.utils.file_utils import validate_file, save_uploaded_file
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

# Servicios
pdf_service = PDFService()
openai_service = OpenAIService()
excel_service = ExcelService()


@router.post("/upload-pdf/", response_model=PDFUploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Endpoint para subir un archivo PDF.
    
    Args:
        file: Archivo PDF a procesar
        
    Returns:
        PDFUploadResponse: Información sobre el archivo subido
    """
    try:
        logger.info(f"Recibido archivo: {file.filename}")
        
        # Validar archivo
        await validate_file(file)
        
        # Leer contenido
        content = await file.read()
        
        # Validar que sea un PDF válido
        if not pdf_service.validate_pdf(content):
            raise HTTPException(status_code=400, detail="El archivo no es un PDF válido")
        
        # Guardar archivo
        file_path = await save_uploaded_file(file, content)
        
        return PDFUploadResponse(
            message="Archivo PDF subido exitosamente",
            filename=file.filename,
            file_size=len(content),
            upload_time=datetime.now()
        )
        
    except CertiflowException as e:
        logger.error(f"Error de aplicación: {e.message}")
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post("/extract-data/", response_model=ProcessingResponse)
async def extract_data(
    file: UploadFile = File(...),
    extract_specific_fields: Optional[str] = Form(None),
    template_name: Optional[str] = Form(None),
    output_format: str = Form("json")
):
    """
    Endpoint principal para extraer datos de un PDF.
    
    Args:
        file: Archivo PDF a procesar
        extract_specific_fields: Campos específicos a extraer (JSON string)
        template_name: Nombre de plantilla Excel a usar
        output_format: Formato de salida ("json" o "excel")
        
    Returns:
        ProcessingResponse: Datos extraídos y información del procesamiento
    """
    start_time = time.time()
    
    try:
        logger.info(f"Iniciando procesamiento de {file.filename}")
        
        # Validar archivo
        await validate_file(file)
        content = await file.read()
        
        if not pdf_service.validate_pdf(content):
            raise HTTPException(status_code=400, detail="El archivo no es un PDF válido")
        
        # Paso 1: Extraer texto del PDF
        logger.info("Extrayendo texto del PDF")
        extracted_text = pdf_service.extract_text_from_pdf(content)
        
        # Paso 2: Procesar con OpenAI
        logger.info("Procesando con OpenAI")
        structured_data = openai_service.extract_structured_data(extracted_text)
        
        # Crear objeto de respuesta
        extracted_data = ExtractedData(
            extracted_fields=structured_data,
            processing_time=time.time() - start_time
        )
        
        excel_file_path = None
        
        # Paso 3: Generar Excel si se solicita
        if output_format.lower() == "excel":
            logger.info("Generando archivo Excel")
            excel_file_path = excel_service.generate_excel_report(
                structured_data, 
                template_name
            )
        
        processing_time = time.time() - start_time
        
        return ProcessingResponse(
            success=True,
            message="Procesamiento completado exitosamente",
            extracted_data=extracted_data,
            excel_file_path=excel_file_path,
            processing_time=processing_time,
            timestamp=datetime.now()
        )
        
    except PDFProcessingError as e:
        logger.error(f"Error procesando PDF: {e.message}")
        raise HTTPException(status_code=400, detail=f"Error procesando PDF: {e.message}")
    except OpenAIError as e:
        logger.error(f"Error con OpenAI: {e.message}")
        raise HTTPException(status_code=500, detail=f"Error procesando con IA: {e.message}")
    except ExcelGenerationError as e:
        logger.error(f"Error generando Excel: {e.message}")
        raise HTTPException(status_code=500, detail=f"Error generando Excel: {e.message}")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/download-excel/{filename}")
async def download_excel(filename: str):
    """
    Endpoint para descargar archivos Excel generados.
    
    Args:
        filename: Nombre del archivo a descargar
        
    Returns:
        FileResponse: Archivo Excel para descargar
    """
    try:
        file_path = f"output/{filename}"
        
        # Verificar que el archivo existe
        import os
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Archivo no encontrado")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        logger.error(f"Error descargando archivo: {e}")
        raise HTTPException(status_code=500, detail="Error descargando archivo")


@router.get("/templates/")
async def list_templates():
    """
    Endpoint para listar plantillas disponibles.
    
    Returns:
        dict: Lista de plantillas disponibles
    """
    try:
        templates = excel_service.list_templates()
        return {
            "templates": templates,
            "count": len(templates)
        }
    except Exception as e:
        logger.error(f"Error listando plantillas: {e}")
        raise HTTPException(status_code=500, detail="Error listando plantillas")