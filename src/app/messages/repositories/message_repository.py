"""
Repositorio de mensajes - Maneja la persistencia de mensajes en MongoDB.
"""

from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from src.config.settings import settings
from src.frameworks.logging.logger import setup_logger
from src.frameworks.db.serializers import serialize_mongo_document
from src.app.messages.entities.message import Message

logger = setup_logger(__name__)


class MessageRepository:
    """Repositorio para gestionar mensajes en MongoDB"""

    def __init__(self, mongo_db, test=False, socketio_manager=None, dashboard_repository=None):
        self.mongo_db = mongo_db
        self.test = test
        self.socketio_manager = socketio_manager
        self.dashboard_repository = dashboard_repository
        collection_name = settings.MONGO_COLLECTION_MENSAJES

        if test:
            collection_name += "_test"

        self.collection = mongo_db[collection_name]
        logger.info(f"MessageRepository inicializado para colección '{collection_name}'")

    def save(self, message: Message) -> str:
        """
        Guarda un nuevo mensaje en la base de datos.

        Args:
            message: Entidad Message a guardar
        """
        doc = message.to_dict()
        result = self.collection.insert_one(doc)
        message_id = str(result.inserted_id)

        logger.info(f"Mensaje guardado: {message_id}")
        return message_id

    def update_analysis(self, message_id: str, sentimiento: str, tema: str, resumen: str, numero_remitente: str = None):
        """
        Actualiza un mensaje con los resultados del análisis de IA.
        También emite eventos Socket.IO al frontend con las estadísticas actualizadas.

        Args:
            message_id: ID del mensaje a actualizar
            sentimiento: Sentimiento detectado (positivo, negativo, neutro)
            tema: Tema identificado
            resumen: Resumen generado por la IA
            numero_remitente: Número del remitente (opcional, para eventos Socket.IO)
        """
        self.collection.update_one(
            {"_id": ObjectId(message_id)},
            {"$set": {
                "sentimiento": sentimiento,
                "tema": tema,
                "resumen": resumen,
                "analizado_en": datetime.utcnow()
            }}
        )

        logger.info(f"Análisis: {message_id} → {sentimiento}/{tema}")

        self._emit_analysis_events(message_id, sentimiento, tema, resumen, numero_remitente)

    def _emit_analysis_events(self, message_id: str, sentimiento: str, tema: str, resumen: str, numero_remitente: str = None):
        """
        Emite eventos Socket.IO después de actualizar el análisis.

        Args:
            message_id: ID del mensaje analizado
            sentimiento: Sentimiento detectado
            tema: Tema identificado
            resumen: Resumen generado
            numero_remitente: Número del remitente
        """
        if not self.socketio_manager:
            return

        try:
            # 1. Notificar que el mensaje fue analizado
            self.socketio_manager.emit_message_analyzed({
                "message_id": message_id,
                "sentimiento": sentimiento,
                "tema": tema,
                "resumen": resumen,
                "numero_remitente": numero_remitente
            })

            # 2. Emitir estadísticas actualizadas del dashboard
            if self.dashboard_repository:
                try:
                    # Obtener estadísticas frescas (con read concern majority)
                    updated_stats = self.dashboard_repository.get_statistics()
                    distribucion = self.dashboard_repository.get_sentiment_distribution()
                    temas = self.dashboard_repository.get_top_topics(limit=6)

                    # Combinar en un solo payload
                    full_stats = {
                        **updated_stats,
                        "distribucion_sentimientos": distribucion,
                        "temas_frecuentes": temas
                    }

                    self.socketio_manager.emit_stats_updated(full_stats)
                except Exception as stats_error:
                    logger.error(f"Error obteniendo/emitiendo stats: {stats_error}", exc_info=True)

        except Exception as socket_error:
            logger.warning(f"Error emitiendo eventos Socket.IO: {socket_error}")

    def find_recent(self, limit: int = 10) -> List[dict]:
        """
        Obtiene los mensajes más recientes.

        Args:
            limit: Número máximo de mensajes a retornar
        """
        cursor = self.collection.find().sort("timestamp", -1).limit(limit)
        messages = serialize_mongo_document(list(cursor))
        return messages

    def get_sentiment_distribution(self) -> dict:
        """
        Obtiene la distribución de sentimientos.
        """
        pipeline = [
            {"$match": {"sentimiento": {"$ne": None}}},
            {"$group": {
                "_id": "$sentimiento",
                "count": {"$sum": 1}
            }}
        ]

        cursor = self.collection.aggregate(pipeline)
        results = serialize_mongo_document(list(cursor))

        distribution = {
            "positivo": 0,
            "negativo": 0,
            "neutro": 0
        }

        for item in results:
            if item["_id"] in distribution:
                distribution[item["_id"]] = item["count"]

        return distribution

    def get_top_topics(self, limit: int = 5) -> List[dict]:
        """
        Obtiene los temas más frecuentes.
        """
        pipeline = [
            {"$match": {"tema": {"$ne": None}}},
            {"$group": {
                "_id": "$tema",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]

        cursor = self.collection.aggregate(pipeline)
        topics = serialize_mongo_document(list(cursor))

        logger.info(f"Top temas obtenidos: {len(topics)} resultados")
        return topics

    def get_statistics(self) -> dict:
        """
        Obtiene estadísticas generales del dashboard.
        """
        logger.debug("Calculando estadísticas generales")

        total = self.collection.count_documents({})
        analizados = self.collection.count_documents({"sentimiento": {"$ne": None}})
        pendientes = total - analizados

        stats = {
            "total_mensajes": total,
            "mensajes_analizados": analizados,
            "mensajes_pendientes": pendientes
        }

        logger.info(f"Estadísticas: {stats}")
        return stats
