from pymongo import MongoClient
from src.config.settings import settings


def create_mongo_client() -> MongoClient:
    """
    Crea y retorna un cliente de MongoDB.

    Returns:
        MongoClient: Cliente de MongoDB configurado
    """
    client = MongoClient(settings.MONGO_URI)
    return client
