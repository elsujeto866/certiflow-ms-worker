"""
Orquestador que centraliza el flujo de procesamiento de un PDF:
- validación
- extracción de texto
- procesamiento con OpenAI
- generación de Excel (opcional)

Proporciona una API simple para que las rutas llamen `orchestrator.process_file(...)`.
"""
from typing import Optional, Dict, Any
import time
from app.services.pdf_service import PDFService
from app.services.openai_service import OpenAIService
from app.services.excel_service import ExcelService
from app.utils.file_utils import save_uploaded_file
from app.core.logging import get_logger
from app.models.exceptions import PDFProcessingError, OpenAIError, ExcelGenerationError

logger = get_logger(__name__)


class Orchestrator:
    def __init__(self):
        self.pdf_service = PDFService()
        self.openai_service = OpenAIService()
        self.excel_service = ExcelService()

    async def process_file(self, file_bytes: bytes, filename: Optional[str] = None, template_name: Optional[str] = None, output_format: str = "json") -> Dict[str, Any]:
        """Procesa el archivo en pasos y devuelve un dict con resultados.

        Args:
            file_bytes: contenido del archivo en bytes
            filename: nombre del archivo (opcional)
            template_name: plantilla de Excel a usar (opcional)
            output_format: 'json' o 'excel'

        Returns:
            dict con keys: data (structured), excel_path (opcional), metadata
        """
        start_time = time.time()

        # Validar PDF
        if not self.pdf_service.validate_pdf(file_bytes):
            raise PDFProcessingError("El archivo no es un PDF válido")

        # Extraer texto
        text = self.pdf_service.extract_text_from_pdf(file_bytes)

        logger.info("Texto extraído completo:\n%s", text)

        # Procesar con OpenAI
        structured = self.openai_service.extract_structured_data(text)

        #excel_path = None
        #if output_format.lower() == "excel":
        #    excel_path = self.excel_service.generate_excel_report(structured, template_name)

        processing_time = time.time() - start_time

        metadata = {
            "processing_time": processing_time,
            "filename": filename,
        }

        return {
            "data": structured,
            #"excel_path": excel_path,
            "metadata": metadata
        }


# Singleton orquestador por conveniencia
orchestrator = Orchestrator()
