"""
Servicio para integración con OpenAI API.
"""
import openai
from typing import Dict, Any, Optional
import json
import time
from app.core.config import settings
from app.models.exceptions import OpenAIError
from app.core.logging import get_logger

logger = get_logger(__name__)


class OpenAIService:
    """Servicio para manejar la integración con OpenAI."""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.max_tokens = settings.openai_max_tokens
    
    def extract_structured_data(self, text: str, extraction_schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extrae datos estructurados del texto usando OpenAI.
        
        Args:
            text: Texto del cual extraer información
            extraction_schema: Schema opcional para guiar la extracción
            
        Returns:
            Dict con los datos extraídos estructurados
            
        Raises:
            OpenAIError: Si hay error en la comunicación con OpenAI
        """
        try:
            start_time = time.time()
            logger.info("Iniciando extracción de datos con OpenAI")
            
            # Construir el prompt
            prompt = self._build_extraction_prompt(text, extraction_schema)
            
            # Llamar a OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un experto en extracción de información de documentos. "
                                 "Debes extraer información relevante y estructurarla en formato JSON. "
                                 "Si no encuentras información específica, usa null."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=0.1,  # Baja temperatura para respuestas más consistentes
                response_format={"type": "json_object"}
            )
            
            # Procesar respuesta
            content = response.choices[0].message.content
            extracted_data = json.loads(content)
            
            processing_time = time.time() - start_time
            logger.info(f"Extracción completada en {processing_time:.2f} segundos")
            
            # Agregar metadatos
            extracted_data["_metadata"] = {
                "processing_time": processing_time,
                "model_used": self.model,
                "tokens_used": response.usage.total_tokens if response.usage else None
            }
            
            return extracted_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Error decodificando JSON de OpenAI: {e}")
            raise OpenAIError(f"Respuesta inválida de OpenAI: {e}")
        except Exception as e:
            logger.error(f"Error en OpenAI API: {e}")
            raise OpenAIError(f"Error comunicándose con OpenAI: {e}")
    
    def _build_extraction_prompt(self, text: str, schema: Optional[Dict[str, Any]] = None) -> str:
        """
        Construye el prompt para la extracción de datos.
        
        Args:
            text: Texto a procesar
            schema: Schema opcional para guiar la extracción
            
        Returns:
            str: Prompt construido
        """
        base_prompt = f"""
Analiza el siguiente texto y extrae información relevante en formato JSON:

TEXTO:
{text}

INSTRUCCIONES:
- Extrae información como: fechas, nombres de empresas, contactos, direcciones, números, etc.
- Organiza la información de manera lógica en un objeto JSON
- Si no encuentras información específica, usa null
- Mantén los datos originales sin modificar
"""
        
        if schema:
            base_prompt += f"\nUSA ESTE SCHEMA COMO GUÍA:\n{json.dumps(schema, indent=2)}"
        
        base_prompt += "\nDevuelve SOLO el JSON, sin explicaciones adicionales."
        
        return base_prompt
    
    def test_connection(self) -> bool:
        """
        Prueba la conexión con OpenAI API.
        
        Returns:
            bool: True si la conexión es exitosa
        """
        try:
            response = self.client.models.list()
            return bool(response.data)
        except Exception as e:
            logger.error(f"Error probando conexión OpenAI: {e}")
            return False