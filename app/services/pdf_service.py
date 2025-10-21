"""
Servicio para procesar archivos PDF y extraer texto usando pdfplumber.

Esta implementación usa `pdfplumber` para extraer texto página a página.
Es más robusta en muchos PDFs y ofrece utilidades adicionales para tablas y metadatos.
"""
from io import BytesIO
from typing import Optional

import pdfplumber

from app.models.exceptions import PDFProcessingError
from app.core.logging import get_logger

logger = get_logger(__name__)


class PDFService:
    """Servicio para manejar operaciones con archivos PDF usando pdfplumber."""

    def __init__(self):
        pass

    def extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """
        Extrae texto de un archivo PDF usando pdfplumber.

        Args:
            pdf_content: Contenido del PDF en bytes

        Returns:
            str: Texto extraído del PDF

        Raises:
            PDFProcessingError: Si hay error en el procesamiento
        """
        try:
            logger.info("Iniciando extracción de texto del PDF (pdfplumber)")

            pdf_file = BytesIO(pdf_content)

            with pdfplumber.open(pdf_file) as pdf:
                if not pdf.pages:
                    raise PDFProcessingError("El PDF no contiene páginas")

                extracted_text = ""
                for page_num, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text() or ""
                        if page_text.strip():
                            extracted_text += f"\n--- Página {page_num + 1} ---\n"
                            extracted_text += page_text
                    except Exception as e:
                        logger.warning(f"Error extrayendo texto de página {page_num + 1}: {e}")
                        continue

            if not extracted_text.strip():
                raise PDFProcessingError("No se pudo extraer texto del PDF")

            logger.info(f"Texto extraído exitosamente. Longitud: {len(extracted_text)} caracteres")
            return extracted_text.strip()

        except Exception as e:
            logger.error(f"Error inesperado procesando PDF con pdfplumber: {e}")
            raise PDFProcessingError(f"Error procesando PDF: {e}")

    def validate_pdf(self, pdf_content: bytes) -> bool:
        """
        Valida que el contenido sea un PDF válido intentando abrirlo con pdfplumber.

        Args:
            pdf_content: Contenido del archivo en bytes

        Returns:
            bool: True si es un PDF válido
        """
        try:
            pdf_file = BytesIO(pdf_content)
            with pdfplumber.open(pdf_file):
                return True
        except Exception:
            return False