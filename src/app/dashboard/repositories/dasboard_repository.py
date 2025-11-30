from datetime import datetime
from typing import List
from src.config.settings import settings
from src.frameworks.logging.logger import setup_logger
from src.frameworks.http.error_handlers import DatabaseError
from src.frameworks.db.serializers import serialize_mongo_document

logger = setup_logger(__name__)

class DashboardRepository():
    """Repositorio para gestionar datos del dashboard en MongoDB"""

    def __init__(self, mongo_db, test=False):
        self.mongo_db = mongo_db
        self.test = test
        collection_name = settings.MONGO_COLLECTION_MENSAJES

        if test:
            collection_name += "_test"

        self.collection = mongo_db[collection_name]
        logger.info(f"DashboardRepository inicializado para colección '{collection_name}'")

    def get_statistics(self) -> dict:
        """
        Obtiene estadísticas generales del dashboard.

        Returns:
            Diccionario con estadísticas
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

    def get_sentiment_distribution(self) -> dict:
        """
        Obtiene la distribución de sentimientos.

        Returns:
            Diccionario con conteo por sentimiento
        """
        logger.debug("Calculando distribución de sentimientos")

        pipeline = [
            {"$match": {"sentimiento": {"$ne": None}}},
            {"$group": {
                "_id": "$sentimiento",
                "count": {"$sum": 1}
            }}
        ]

        cursor = self.collection.aggregate(pipeline)
        results = serialize_mongo_document(list(cursor))

        # Convertir a formato más legible
        distribution = {
            "positivo": 0,
            "negativo": 0,
            "neutro": 0
        }

        for item in results:
            if item["_id"] in distribution:
                distribution[item["_id"]] = item["count"]

        logger.info(f"Distribución calculada: {distribution}")
        return distribution

    def get_top_topics(self, limit: int = 5) -> List[dict]:
        """
        Obtiene los temas más frecuentes.

        Args:
            limit: Número de temas a retornar

        Returns:
            Lista de temas con su frecuencia
        """
        logger.debug(f"Obteniendo top {limit} temas")

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

    def get_recent_messages(self, limit: int = 10) -> List[dict]:
        """
        Obtiene los mensajes más recientes.

        Args:
            limit: Número máximo de mensajes a retornar

        Returns:
            Lista de mensajes serializados
        """
        logger.debug(f"Obteniendo últimos {limit} mensajes")

        cursor = self.collection.find().sort("timestamp", -1).limit(limit)
        messages = serialize_mongo_document(list(cursor))

        logger.info(f"{len(messages)} mensajes recientes obtenidos")
        return messages
