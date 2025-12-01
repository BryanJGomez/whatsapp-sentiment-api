"""
Servicio de análisis de sentimiento usando Google Gemini.
"""

import json
import hashlib
import re
import google.generativeai as genai
from typing import Optional
from src.config.settings import settings
from src.frameworks.logging.logger import setup_logger

logger = setup_logger(__name__)


class SentimentAnalysisService:
    """Servicio para analizar sentimiento de mensajes usando Google Gemini"""

    def __init__(self, redis_cache=None):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        self.cache = redis_cache

    def analyze_message(self, texto_mensaje: str) -> dict:
        """
        Analiza un mensaje de cliente y retorna sentimiento, tema y resumen.

        Si hay caché habilitado, primero busca si ya se analizó un mensaje idéntico.

        Args:
            texto_mensaje: Texto del mensaje a analizar

        Returns:
            Dict con: sentimiento, tema, resumen

        Example:
            {
                "sentimiento": "positivo",
                "tema": "Calidad del Producto",
                "resumen": "El cliente está satisfecho con el sabor del café"
            }
        """
        # Si hay caché, verificar si ya se analizó este mensaje
        if self.cache:
            cache_key = self._get_cache_key(texto_mensaje)
            cached_result = self.cache.get(cache_key)
            if cached_result:
                return cached_result

        prompt = self._build_prompt(texto_mensaje)

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text

            # Limpiar respuesta (Gemini a veces añade markdown)
            cleaned_text = self._clean_json_response(response_text)

            # Parsear el JSON de la respuesta
            analysis = json.loads(cleaned_text)

            # Validar que tenga los campos requeridos
            required_fields = ["sentimiento", "tema", "resumen"]
            for field in required_fields:
                if field not in analysis:
                    raise ValueError(f"Campo requerido '{field}' no encontrado en la respuesta")

            # Guardar en caché si está habilitado
            if self.cache:
                cache_key = self._get_cache_key(texto_mensaje)
                self.cache.set(cache_key, analysis, ttl=86400)

            return analysis

        except json.JSONDecodeError as e:
            logger.error(f"Error al parsear respuesta JSON de Gemini: {e}")
            logger.error(f"Respuesta original: {response_text}")
            # Retornar valores por defecto si falla el parsing
            return {
                "sentimiento": "neutro",
                "tema": "Otros",
                "resumen": "No se pudo analizar el mensaje correctamente"
            }
        except Exception as e:
            logger.error(f"Error al analizar mensaje con Gemini: {e}")
            raise

    def _clean_json_response(self, text: str) -> str:
        """
        Limpia la respuesta de Gemini removiendo markdown y espacios extra.

        Args:
            text: Texto de respuesta de Gemini

        Returns:
            JSON limpio
        """
        # Remover bloques de código markdown
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        # Remover espacios al inicio y final
        text = text.strip()
        return text

    def _get_cache_key(self, texto_mensaje: str) -> str:
        """
        Genera una clave de caché única para un mensaje.

        Args:
            texto_mensaje: Texto del mensaje

        Returns:
            Hash MD5 del mensaje para usar como clave
        """
        # Normalizar el texto (lowercase, sin espacios extra)
        normalized = texto_mensaje.lower().strip()
        # Generar hash MD5
        return f"sentiment:{hashlib.md5(normalized.encode()).hexdigest()}"

    def _build_prompt(self, texto_mensaje: str) -> str:
        """
        Construye el prompt para Claude con instrucciones específicas.

        Args:
            texto_mensaje: Mensaje del cliente

        Returns:
            Prompt formateado
        """
        return f"""Eres un asistente experto en análisis de sentimiento para "Café de El Salvador", una cadena de cafeterías.

Analiza el siguiente mensaje de un cliente y devuelve ÚNICAMENTE un objeto JSON (sin markdown, sin explicaciones adicionales) con la siguiente estructura:

{{
  "sentimiento": "positivo" | "negativo" | "neutro",
  "tema": "Servicio al Cliente" | "Calidad del Producto" | "Precio" | "Limpieza" | "Ambiente" | "Otros",
  "resumen": "Breve resumen en una oración de 10-15 palabras"
}}

Criterios:
- sentimiento: "positivo" si el cliente está satisfecho, "negativo" si está insatisfecho, "neutro" si es neutral o pregunta
- tema: Categoriza el mensaje en uno de los temas predefinidos
- resumen: Resume la esencia del mensaje en una oración concisa

Mensaje del cliente:
"{texto_mensaje}"

Responde SOLO con el objeto JSON, sin formato markdown ni texto adicional:"""
