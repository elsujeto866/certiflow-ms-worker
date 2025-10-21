"""
Utilidades de validación y helpers generales.
"""
import re
from typing import Any, Dict, List, Optional
from datetime import datetime
import json
from app.core.logging import get_logger

logger = get_logger(__name__)


def is_valid_email(email: str) -> bool:
    """
    Valida si un string es un email válido.
    
    Args:
        email: String a validar
        
    Returns:
        bool: True si es un email válido
    """
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_phone(phone: str) -> bool:
    """
    Valida si un string es un número de teléfono válido.
    
    Args:
        phone: String a validar
        
    Returns:
        bool: True si es un teléfono válido
    """
    if not phone or not isinstance(phone, str):
        return False
    
    # Remover espacios y caracteres comunes
    clean_phone = re.sub(r'[\s\-\(\)\+]', '', phone)
    
    # Verificar que solo contenga números y tenga longitud apropiada
    return bool(re.match(r'^\d{7,15}$', clean_phone))


def extract_dates_from_text(text: str) -> List[str]:
    """
    Extrae fechas de un texto.
    
    Args:
        text: Texto del cual extraer fechas
        
    Returns:
        List[str]: Lista de fechas encontradas
    """
    if not text:
        return []
    
    date_patterns = [
        r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # DD/MM/YYYY, DD-MM-YYYY
        r'\d{2,4}[/-]\d{1,2}[/-]\d{1,2}',  # YYYY/MM/DD, YYYY-MM-DD
        r'\d{1,2}\s+de\s+\w+\s+de\s+\d{4}',  # DD de MMMM de YYYY (español)
        r'\w+\s+\d{1,2},\s+\d{4}',  # Month DD, YYYY (inglés)
    ]
    
    dates = []
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        dates.extend(matches)
    
    return list(set(dates))  # Remover duplicados


def extract_numbers_from_text(text: str) -> List[str]:
    """
    Extrae números de un texto.
    
    Args:
        text: Texto del cual extraer números
        
    Returns:
        List[str]: Lista de números encontrados
    """
    if not text:
        return []
    
    # Patrones para diferentes tipos de números
    patterns = [
        r'\$\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?',  # Moneda ($1,000.00)
        r'\d{1,3}(?:,\d{3})*(?:\.\d{2})?',  # Números con comas y decimales
        r'\d+\.\d+',  # Decimales
        r'\d+',  # Enteros
    ]
    
    numbers = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        numbers.extend(matches)
    
    return numbers


def clean_text(text: str) -> str:
    """
    Limpia y normaliza texto.
    
    Args:
        text: Texto a limpiar
        
    Returns:
        str: Texto limpio
    """
    if not text:
        return ""
    
    # Remover caracteres especiales excesivos
    text = re.sub(r'\s+', ' ', text)  # Múltiples espacios -> un espacio
    text = re.sub(r'\n+', '\n', text)  # Múltiples saltos -> un salto
    text = text.strip()
    
    return text


def format_confidence_score(score: float) -> str:
    """
    Formatea un score de confianza para mostrar.
    
    Args:
        score: Score de confianza (0.0 - 1.0)
        
    Returns:
        str: Score formateado con porcentaje
    """
    if score is None:
        return "N/A"
    
    percentage = score * 100
    return f"{percentage:.1f}%"


def sanitize_filename(filename: str) -> str:
    """
    Sanitiza un nombre de archivo removiendo caracteres no válidos.
    
    Args:
        filename: Nombre de archivo original
        
    Returns:
        str: Nombre de archivo sanitizado
    """
    if not filename:
        return "unnamed_file"
    
    # Remover caracteres no válidos
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remover espacios múltiples
    sanitized = re.sub(r'\s+', '_', sanitized)
    
    # Limitar longitud
    if len(sanitized) > 100:
        name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
        sanitized = name[:95] + ('.' + ext if ext else '')
    
    return sanitized


def validate_json_string(json_string: str) -> bool:
    """
    Valida si un string es JSON válido.
    
    Args:
        json_string: String a validar
        
    Returns:
        bool: True si es JSON válido
    """
    try:
        json.loads(json_string)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def safe_get_nested_value(data: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    Obtiene un valor anidado de un diccionario de forma segura.
    
    Args:
        data: Diccionario de datos
        key_path: Ruta de claves separadas por punto (ej: "user.profile.name")
        default: Valor por defecto si no se encuentra
        
    Returns:
        Any: Valor encontrado o valor por defecto
    """
    try:
        keys = key_path.split('.')
        value = data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
        
    except Exception:
        return default


def calculate_processing_stats(start_time: float, end_time: float, 
                             input_size: int, output_size: int | None = None) -> Dict[str, Any]:
    """
    Calcula estadísticas de procesamiento.
    
    Args:
        start_time: Tiempo de inicio (timestamp)
        end_time: Tiempo de fin (timestamp)
        input_size: Tamaño de entrada en bytes
        output_size: Tamaño de salida en bytes (opcional)
        
    Returns:
        Dict: Estadísticas de procesamiento
    """
    processing_time = end_time - start_time
    
    stats = {
        "processing_time_seconds": round(processing_time, 3),
        "input_size_bytes": input_size,
        "input_size_mb": round(input_size / (1024 * 1024), 3),
        "throughput_mb_per_second": round((input_size / (1024 * 1024)) / max(processing_time, 0.001), 3)
    }
    
    if output_size is not None:
        stats.update({
            "output_size_bytes": output_size,
            "output_size_mb": round(output_size / (1024 * 1024), 3),
            "compression_ratio": round(output_size / max(input_size, 1), 3)
        })
    
    return stats


def create_error_context(error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Crea contexto de error para logging y debugging.
    
    Args:
        error: Excepción ocurrida
        context: Contexto adicional
        
    Returns:
        Dict: Contexto de error estructurado
    """
    error_context = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "timestamp": datetime.now().isoformat(),
    }
    
    if context:
        error_context["context"] = context
    
    return error_context