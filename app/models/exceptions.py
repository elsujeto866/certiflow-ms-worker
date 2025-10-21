"""
Excepciones personalizadas para la aplicación.
"""


class CertiflowException(Exception):
    """Excepción base para la aplicación."""
    def __init__(self, message: str, error_code: str | None = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class PDFProcessingError(CertiflowException):
    """Error en el procesamiento de PDF."""
    pass


class OpenAIError(CertiflowException):
    """Error en la comunicación con OpenAI."""
    pass


class ExcelGenerationError(CertiflowException):
    """Error en la generación de archivos Excel."""
    pass


class FileValidationError(CertiflowException):
    """Error en la validación de archivos."""
    pass


class TemplateNotFoundError(CertiflowException):
    """Error cuando no se encuentra una plantilla."""
    pass