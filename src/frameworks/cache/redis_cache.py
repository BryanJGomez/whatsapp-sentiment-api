"""
Cliente Redis para cachear datos.
"""

import json
import redis
from src.config.settings import settings
from src.frameworks.logging.logger import setup_logger

logger = setup_logger(__name__)


class RedisCache:
    """Cliente Redis para operaciones de caché"""

    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            decode_responses=True  # Decodifica automáticamente a strings
        )
        pass

    def get(self, key: str):
        """
        Obtiene un valor del caché.

        Args:
            key: Clave a buscar

        Returns:
            Valor deserializado o None si no existe
        """
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error al obtener del cache: {e}")
            return None

    def set(self, key: str, value: dict, ttl: int = 3600):
        """
        Guarda un valor en el caché.

        Args:
            key: Clave
            value: Valor a guardar (dict)
            ttl: Tiempo de vida en segundos (default: 1 hora)
        """
        try:
            self.client.setex(
                key,
                ttl,
                json.dumps(value)
            )
        except Exception as e:
            logger.error(f"Error al guardar en cache: {e}")

    def delete(self, key: str):
        """Elimina una clave del caché"""
        try:
            self.client.delete(key)
        except Exception as e:
            logger.error(f"Error al eliminar del cache: {e}")

    def flush_all(self):
        """Limpia todo el caché (usar con precaución)"""
        self.client.flushall()
        logger.warning("Cache completamente limpiado")
