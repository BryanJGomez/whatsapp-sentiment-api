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

    def get_statistics(self) -> dict:
        """
        Obtiene estadísticas generales del dashboard.

        Returns:
            Diccionario con estadísticas
        """
        total = self.collection.count_documents({})

        pipeline_sentimientos = [
            {"$match": {"sentimiento": {"$ne": None}}},
            {"$group": {
                "_id": "$sentimiento",
                "count": {"$sum": 1}
            }}
        ]

        cursor = self.collection.aggregate(
            pipeline_sentimientos,
            readConcern={"level": "majority"}
        )
        sentimientos = serialize_mongo_document(list(cursor))

        total_analizados = sum(item["count"] for item in sentimientos)
        count_positivo = next((item["count"] for item in sentimientos if item["_id"] == "positivo"), 0)
        count_negativo = next((item["count"] for item in sentimientos if item["_id"] == "negativo"), 0)

        # Calcular porcentajes
        porcentaje_positivo = round((count_positivo / total_analizados * 100)) if total_analizados > 0 else 0
        porcentaje_negativo = round((count_negativo / total_analizados * 100)) if total_analizados > 0 else 0

        # Obtener tema principal con read_concern
        pipeline_tema = [
            {"$match": {"tema": {"$ne": None}}},
            {"$group": {
                "_id": "$tema",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 1}
        ]

        cursor_tema = self.collection.aggregate(
            pipeline_tema,
            readConcern={"level": "majority"}
        )
        temas = serialize_mongo_document(list(cursor_tema))
        tema_principal = temas[0]["_id"] if temas else "N/A"

        stats = {
            "total_mensajes": total,
            "sentimiento_positivo": porcentaje_positivo,
            "sentimiento_negativo": porcentaje_negativo,
            "tema_principal": tema_principal
        }

        return stats

    def get_sentiment_distribution(self) -> dict:
        """
        Obtiene la distribución de sentimientos en porcentajes.

        Returns:
            Diccionario con porcentaje por sentimiento
        """
        pipeline = [
            {"$match": {"sentimiento": {"$ne": None}}},
            {"$group": {
                "_id": "$sentimiento",
                "count": {"$sum": 1}
            }}
        ]

        cursor = self.collection.aggregate(
            pipeline,
            readConcern={"level": "majority"}
        )
        results = serialize_mongo_document(list(cursor))

        total = sum(item["count"] for item in results)

        distribution = {
            "positivo": 0,
            "negativo": 0,
            "neutro": 0
        }

        for item in results:
            if item["_id"] in distribution and total > 0:
                distribution[item["_id"]] = round((item["count"] / total) * 100)

        return distribution

    def get_top_topics(self, limit: int = 5) -> List[dict]:
        """
        Obtiene los temas más frecuentes.

        Args:
            limit: Número de temas a retornar

        Returns:
            Lista de temas con su frecuencia
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

        cursor = self.collection.aggregate(
            pipeline,
            readConcern={"level": "majority"}
        )
        results = serialize_mongo_document(list(cursor))

        topics = [
            {
                "tema": item["_id"],
                "cantidad": item["count"]
            }
            for item in results
        ]

        return topics

    def get_recent_messages(self, limit: int = 10) -> List[dict]:
        """
        Obtiene los mensajes más recientes.

        Args:
            limit: Número máximo de mensajes a retornar

        """
        cursor = self.collection.find().sort("timestamp", -1).limit(limit)
        messages = serialize_mongo_document(list(cursor))
        return messages
