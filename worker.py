"""
Worker para procesar mensajes de la cola en background.
"""

import signal
import sys
from flask_socketio import SocketIO
from src.frameworks.db.mongo import create_mongo_client
from src.frameworks.cache.redis_cache import RedisCache
from src.frameworks.queue.message_queue import MessageQueue
from src.frameworks.websocket.socketio_manager import SocketIOManager
from src.app.messages.repositories.message_repository import MessageRepository
from src.app.messages.services.sentiment_analysis_service import SentimentAnalysisService
from src.frameworks.logging.logger import setup_logger
from src.config.settings import settings

logger = setup_logger(__name__)

# Variable global para manejar shutdown graceful
shutdown_requested = False


def signal_handler(signum, frame):
    """Maneja señales de shutdown"""
    global shutdown_requested
    logger.warning("Señal de shutdown recibida, terminando worker...")
    shutdown_requested = True


def process_message(message_data: dict, repository: MessageRepository,
                   sentiment_service: SentimentAnalysisService,
                   socketio_manager: SocketIOManager = None):
    """
    Procesa un mensaje de la cola: analiza con IA y actualiza en MongoDB.

    Args:
        message_data: Dict con texto_mensaje, numero_remitente, message_id
        repository: Repositorio de mensajes
        sentiment_service: Servicio de análisis
        socketio_manager: Gestor de Socket.IO para notificar al frontend
    """
    try:
        message_id = message_data["message_id"]
        texto_mensaje = message_data["texto_mensaje"]
        numero_remitente = message_data["numero_remitente"]

        logger.info(f"Procesando mensaje {message_id} de {numero_remitente}")

        # Analizar con Gemini
        analysis = sentiment_service.analyze_message(texto_mensaje)

        # Actualizar en MongoDB
        repository.update_analysis(
            message_id=message_id,
            sentimiento=analysis["sentimiento"],
            tema=analysis["tema"],
            resumen=analysis["resumen"]
        )

        logger.info(f"Mensaje {message_id} procesado: {analysis['sentimiento']}/{analysis['tema']}")

        # Emitir evento Socket.IO al frontend (si está disponible)
        if socketio_manager:
            socketio_manager.emit_message_analyzed({
                "message_id": message_id,
                "sentimiento": analysis["sentimiento"],
                "tema": analysis["tema"],
                "resumen": analysis["resumen"],
                "numero_remitente": numero_remitente
            })
            logger.debug(f"Evento Socket.IO emitido para mensaje {message_id}")

    except Exception as e:
        logger.error(f"Error procesando mensaje {message_data.get('message_id')}: {e}")
        # Aquí podrías implementar lógica de reintento o dead letter queue


def main():
    """Función principal del worker"""
    global shutdown_requested

    # Registrar handlers para shutdown graceful
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    logger.info("Worker iniciando...")

    # Validar configuraciones
    logger.info("Validando configuraciones...")
    settings.validate()
    logger.info("Configuraciones validadas")

    # Inicializar dependencias
    logger.info("Inicializando dependencias...")
    mongo_client = create_mongo_client()
    redis_cache = RedisCache()
    message_queue = MessageQueue()
    message_repository = MessageRepository(mongo_client)
    sentiment_service = SentimentAnalysisService(redis_cache=redis_cache)

    # Inicializar Socket.IO para emitir eventos al frontend
    # Nota: El worker NO ejecuta el servidor SocketIO, solo emite eventos via Redis pub/sub
    socketio = SocketIO(message_broker=f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0')
    socketio_manager = SocketIOManager(socketio)

    logger.info("Dependencias inicializadas")

    logger.info(f"Worker escuchando cola '{message_queue.queue_name}'...")

    # Loop principal
    while not shutdown_requested:
        try:
            # Esperar mensaje (bloqueante, timeout de 5 segundos)
            message_data = message_queue.dequeue(timeout=5)

            if message_data:
                process_message(message_data, message_repository, sentiment_service, socketio_manager)
            else:
                # No hay mensajes, continuar esperando
                logger.debug("Esperando mensajes en la cola...")

        except KeyboardInterrupt:
            logger.warning("KeyboardInterrupt recibido, cerrando worker...")
            break
        except Exception as e:
            logger.error(f"Error en loop principal del worker: {e}")
            # Continuar procesando a pesar del error

    logger.info("Worker detenido correctamente")


if __name__ == "__main__":
    main()
