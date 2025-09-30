"""
Modelos Pydantic para requests y responses de la API.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class PDFUploadResponse(BaseModel):
    """Respuesta después de subir un PDF."""
    message: str
    filename: str
    file_size: int
    upload_time: datetime


class ExtractedData(BaseModel):
    """Estructura de datos extraídos del PDF."""
    # Campos comunes que podrías extraer
    document_type: Optional[str] = Field(None, description="Tipo de documento")
    date: Optional[str] = Field(None, description="Fecha del documento")
    company_name: Optional[str] = Field(None, description="Nombre de la empresa")
    contact_info: Optional[Dict[str, Any]] = Field(None, description="Información de contacto")
    
    # Campo flexible para datos específicos
    extracted_fields: Dict[str, Any] = Field(default_factory=dict, description="Campos extraídos específicos")
    
    # Metadatos
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Nivel de confianza de la extracción")
    processing_time: Optional[float] = Field(None, description="Tiempo de procesamiento en segundos")


class ProcessingRequest(BaseModel):
    """Request para procesar un documento."""
    extract_specific_fields: Optional[List[str]] = Field(None, description="Campos específicos a extraer")
    template_name: Optional[str] = Field(None, description="Nombre de la plantilla Excel a usar")
    output_format: str = Field("json", description="Formato de salida: json, excel")


class ProcessingResponse(BaseModel):
    """Respuesta del procesamiento completo."""
    success: bool
    message: str
    extracted_data: Optional[ExtractedData] = None
    excel_file_path: Optional[str] = None
    processing_time: float
    timestamp: datetime


class ErrorResponse(BaseModel):
    """Respuesta de error estándar."""
    error: bool = True
    message: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class HealthResponse(BaseModel):
    """Respuesta del endpoint de health check."""
    status: str
    version: str
    timestamp: datetime
    services: Dict[str, str]  # Status de servicios externos