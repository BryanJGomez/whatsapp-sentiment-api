"""
Definición de colecciones, esquemas e índices para MongoDB.
Este archivo contiene la estructura de la base de datos.
"""

from pymongo.database import Database
from pymongo import ASCENDING, DESCENDING


MENSAJES_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["texto_mensaje", "numero_remitente", "timestamp"],
        "properties": {
            "texto_mensaje": {
                "bsonType": "string",
                "description": "Texto del mensaje enviado por el cliente"
            },
            "numero_remitente": {
                "bsonType": "string",
                "description": "Número de teléfono del remitente (formato internacional: +503XXXXXXXX)"
            },
            "message_sid": {
                "bsonType": "string",
                "description": "ID único del mensaje proporcionado por Twilio (MessageSid)"
            },
            "timestamp": {
                "bsonType": "date",
                "description": "Fecha y hora de recepción del mensaje en formato UTC"
            },
            "sentimiento": {
                "bsonType": ["string", "null"],
                "enum": ["positivo", "negativo", "neutro", None],
                "description": "Sentimiento detectado por la IA tras el análisis"
            },
            "tema": {
                "bsonType": ["string", "null"],
                "enum": ["Servicio al Cliente", "Calidad del Producto", "Precio", "Limpieza", "Ambiente", "Otros", None],
                "description": "Tema o categoría principal identificada en el mensaje"
            },
            "resumen": {
                "bsonType": ["string", "null"],
                "description": "Resumen breve generado por la IA sobre el contenido del mensaje"
            },
            "analizado_en": {
                "bsonType": ["date", "null"],
                "description": "Fecha y hora en que el mensaje fue analizado por la IA"
            }
        }
    }
}

MENSAJES_INDEXES = [
    # Índice para ordenar por fecha (usado en mensajes recientes)
    {
        "keys": [("timestamp", DESCENDING)],
        "options": {"name": "timestamp_desc"}
    },
    # Índice para filtrar por sentimiento
    {
        "keys": [("sentimiento", ASCENDING)],
        "options": {"name": "sentimiento_asc"}
    },
    # Índice para agrupar por tema
    {
        "keys": [("tema", ASCENDING)],
        "options": {"name": "tema_asc"}
    },
    # Índice para filtrar mensajes analizados
    {
        "keys": [("analizado_en", ASCENDING)],
        "options": {"name": "analizado_en_asc"}
    },
    # Índice para buscar por número de remitente
    {
        "keys": [("numero_remitente", ASCENDING)],
        "options": {"name": "numero_remitente_asc"}
    },
    # Índice único para MessageSid de Twilio (evita duplicados)
    {
        "keys": [("message_sid", ASCENDING)],
        "options": {"name": "message_sid_unique", "unique": True, "sparse": True}
    },
    # Índice compuesto para análisis tema-sentimiento
    {
        "keys": [("tema", ASCENDING), ("sentimiento", ASCENDING)],
        "options": {"name": "tema_sentimiento_compound"}
    },
]

def create_collections_and_indexes(db: Database, collection_name: str = "mensajes"):
    """
    Crea la colección con validación de esquema e índices.

    Args:
        db: Instancia de la base de datos MongoDB
        collection_name: Nombre de la colección (default: "mensajes")
    """
    # Verificar si la colección ya existe
    existing_collections = db.list_collection_names()

    if collection_name not in existing_collections:
        # Crear colección con validación de esquema
        db.create_collection(
            collection_name,
            validator=MENSAJES_SCHEMA
        )
        print(f"Colección '{collection_name}' creada con esquema de validación")
    else:
        print(f"ℹColección '{collection_name}' ya existe")

    # Obtener la colección
    collection = db[collection_name]

    # Crear índices
    print(f"\n Creando índices para '{collection_name}'...")
    for index_config in MENSAJES_INDEXES:
        try:
            collection.create_index(
                index_config["keys"],
                **index_config.get("options", {})
            )
            index_name = index_config["options"].get("name", "unnamed")
            print(f"   Índice '{index_name}' creado")
        except Exception as e:
            print(f"    Error creando índice: {str(e)}")

    print(f"\n Colección '{collection_name}' configurada correctamente\n")


def drop_collection(db: Database, collection_name: str = "mensajes"):
    """
    Elimina una colección de la base de datos.
    ADVERTENCIA: Esta operación es irreversible.

    Args:
        db: Instancia de la base de datos MongoDB
        collection_name: Nombre de la colección a eliminar
    """
    db[collection_name].drop()
    print(f" Colección '{collection_name}' eliminada")


def get_collection_stats(db: Database, collection_name: str = "mensajes") -> dict:
    """
    Obtiene estadísticas de la colección.

    Args:
        db: Instancia de la base de datos MongoDB
        collection_name: Nombre de la colección

    Returns:
        dict: Diccionario con estadísticas de la colección
    """
    collection = db[collection_name]

    stats = {
        "total_documentos": collection.count_documents({}),
        "indices": collection.index_information(),
        "nombre": collection_name,
        "database": db.name
    }

    return stats
