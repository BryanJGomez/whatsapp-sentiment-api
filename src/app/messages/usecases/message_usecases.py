"""
Casos de uso para procesar mensajes de WhatsApp.
"""

from src.frameworks.logging.logger import setup_logger
from src.app.messages.entities.message import Message
from src.app.messages.repositories.message_repository import MessageRepository
from src.app.messages.services.sentiment_analysis_service import SentimentAnalysisService

logger = setup_logger(__name__)


class MessageUsecase:
    """
    Caso de uso único para todas las operaciones de mensajes.
    Maneja el procesamiento y persistencia de mensajes de WhatsApp.
    """

    def __init__(self, message_repository: MessageRepository, sentiment_service: SentimentAnalysisService):
        self.message_repository = message_repository
        self.sentiment_service = sentiment_service

    def save_message(self, message: Message) -> str:
        """
        Guarda un nuevo mensaje.

        Args:
            message: Entidad Message a guardar

        Returns:
            ID del mensaje guardado
        """
        logger.debug(f"Guardando mensaje de {message.numero_remitente}")
        return self.message_repository.save(message)

    def update_analysis(self, message_id: str, sentimiento: str, tema: str, resumen: str):
        """
        Actualiza un mensaje con los resultados del análisis.

        Args:
            message_id: ID del mensaje
            sentimiento: Sentimiento detectado
            tema: Tema identificado
            resumen: Resumen generado
        """
        logger.debug(f"Actualizando análisis para mensaje {message_id}")
        self.message_repository.update_analysis(message_id, sentimiento, tema, resumen)
