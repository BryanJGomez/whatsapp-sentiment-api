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
            decode_responses=True  # Decodifica automáticamente a strings
        )
        logger.info(f"RedisCache conectado a {settings.REDIS_HOST}:{settings.REDIS_PORT}")

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
                logger.debug(f"Cache HIT: {key}")
                return json.loads(value)
            logger.debug(f"Cache MISS: {key}")
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
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
        except Exception as e:
            logger.error(f"Error al guardar en cache: {e}")

    def delete(self, key: str):
        """Elimina una clave del caché"""
        try:
            self.client.delete(key)
            logger.debug(f"Cache DELETE: {key}")
        except Exception as e:
            logger.error(f"Error al eliminar del cache: {e}")

    def flush_all(self):
        """Limpia todo el caché (usar con precaución)"""
        self.client.flushall()
        logger.warning("Cache completamente limpiado")
