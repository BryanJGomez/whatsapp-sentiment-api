from pymongo import MongoClient
from src.config.settings import settings

# Función para crear una conexión a MongoDB.

# Usa las configuraciones centralizadas desde settings.py
# para conectarse a MongoDB y retornar la base de datos configurada.

def create_mongo_client():

    client = MongoClient(settings.MONGO_URI)
    return client[settings.MONGO_DB_NAME]
