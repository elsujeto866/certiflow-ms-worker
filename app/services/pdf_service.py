"""
Servicio para procesar archivos PDF y extraer texto.
"""
import PyPDF2
from io import BytesIO
from typing import str
from app.models.exceptions import PDFProcessingError
from app.core.logging import get_logger

logger = get_logger(__name__)


class PDFService:
    """Servicio para manejar operaciones con archivos PDF."""
    
    def __init__(self):
        pass
    
    def extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """
        Extrae texto de un archivo PDF.
        
        Args:
            pdf_content: Contenido del PDF en bytes
            
        Returns:
            str: Texto extraído del PDF
            
        Raises:
            PDFProcessingError: Si hay error en el procesamiento
        """
        try:
            logger.info("Iniciando extracción de texto del PDF")
            
            # Crear un objeto BytesIO con el contenido del PDF
            pdf_file = BytesIO(pdf_content)
            
            # Leer el PDF con PyPDF2
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Verificar que el PDF no esté vacío
            if len(pdf_reader.pages) == 0:
                raise PDFProcessingError("El PDF no contiene páginas")
            
            # Extraer texto de todas las páginas
            extracted_text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        extracted_text += f"\n--- Página {page_num + 1} ---\n"
                        extracted_text += page_text
                except Exception as e:
                    logger.warning(f"Error extrayendo texto de página {page_num + 1}: {e}")
                    continue
            
            if not extracted_text.strip():
                raise PDFProcessingError("No se pudo extraer texto del PDF")
            
            logger.info(f"Texto extraído exitosamente. Longitud: {len(extracted_text)} caracteres")
            return extracted_text.strip()
            
        except PyPDF2.errors.PdfReadError as e:
            logger.error(f"Error leyendo PDF: {e}")
            raise PDFProcessingError(f"Error leyendo el archivo PDF: {e}")
        except Exception as e:
            logger.error(f"Error inesperado procesando PDF: {e}")
            raise PDFProcessingError(f"Error procesando PDF: {e}")
    
    def validate_pdf(self, pdf_content: bytes) -> bool:
        """
        Valida que el contenido sea un PDF válido.
        
        Args:
            pdf_content: Contenido del archivo en bytes
            
        Returns:
            bool: True si es un PDF válido
        """
        try:
            pdf_file = BytesIO(pdf_content)
            PyPDF2.PdfReader(pdf_file)
            return True
        except Exception:
            return False