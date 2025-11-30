"""
Servicio de cola de mensajes con Redis.
"""

import json
import redis
from typing import Optional, Dict
from src.config.settings import settings
from src.frameworks.logging.logger import setup_logger

logger = setup_logger(__name__)


class MessageQueue:
    """Servicio para encolar y procesar mensajes de forma asíncrona"""

    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True
        )
        self.queue_name = "message_queue"
        logger.info(f"MessageQueue inicializado en {settings.REDIS_HOST}:{settings.REDIS_PORT}")

    def enqueue(self, texto_mensaje: str, numero_remitente: str, message_id: str) -> bool:
        """
        Encola un mensaje para procesamiento asíncrono.

        Args:
            texto_mensaje: Texto del mensaje
            numero_remitente: Número del remitente
            message_id: ID del mensaje en MongoDB

        Returns:
            True si se encoló exitosamente
        """
        try:
            message_data = {
                "texto_mensaje": texto_mensaje,
                "numero_remitente": numero_remitente,
                "message_id": message_id
            }

            # Agregar a la cola (LPUSH = añadir al inicio)
            self.client.lpush(self.queue_name, json.dumps(message_data))

            logger.info(f"Mensaje encolado: {message_id}")
            return True

        except Exception as e:
            logger.error(f"Error al encolar mensaje: {e}")
            return False

    def dequeue(self, timeout: int = 0) -> Optional[Dict]:
        """
        Saca un mensaje de la cola (bloqueante).

        Args:
            timeout: Segundos a esperar (0 = esperar indefinidamente)

        Returns:
            Diccionario con datos del mensaje o None
        """
        try:
            # BRPOP = bloquear hasta que haya un elemento (desde el final)
            result = self.client.brpop(self.queue_name, timeout=timeout)

            if result:
                queue_name, message_json = result
                message_data = json.loads(message_json)
                logger.info(f"Mensaje sacado de cola: {message_data.get('message_id')}")
                return message_data

            return None

        except Exception as e:
            logger.error(f"Error al sacar mensaje de cola: {e}")
            return None

    def get_queue_size(self) -> int:
        """
        Obtiene el número de mensajes en la cola.

        Returns:
            Número de mensajes pendientes
        """
        try:
            return self.client.llen(self.queue_name)
        except Exception as e:
            logger.error(f"Error al obtener tamaño de cola: {e}")
            return 0

    def clear_queue(self):
        """Limpia toda la cola (útil para testing)"""
        try:
            self.client.delete(self.queue_name)
            logger.warning("Cola de mensajes limpiada")
        except Exception as e:
            logger.error(f"Error al limpiar cola: {e}")
