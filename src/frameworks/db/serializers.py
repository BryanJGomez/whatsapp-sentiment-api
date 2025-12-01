"""
Utilidades para serialización de datos de MongoDB a JSON.
"""

from datetime import datetime
from bson import ObjectId
from src.utils.datetime_utils import format_timestamp_to_local


def serialize_mongo_document(doc, format_dates: bool = True):
    """
    Convierte un documento de MongoDB a un diccionario serializable a JSON.

    Maneja tipos especiales de MongoDB:
    - ObjectId -> str

    Args:
        doc: Documento o lista de documentos de MongoDB

    Returns:
        Documento serializable a JSON
    """
    if doc is None:
        return None

    if isinstance(doc, list):
        return [serialize_mongo_document(item, format_dates) for item in doc]

    if isinstance(doc, dict):
        return {
            key: serialize_mongo_document(value, format_dates)
            for key, value in doc.items()
        }

    if isinstance(doc, ObjectId):
        return str(doc)

    if isinstance(doc, datetime):
        if format_dates:
            return format_timestamp_to_local(doc.isoformat())
        return doc.isoformat()

    return doc


def mongo_to_dict(cursor):
    """
    Convierte un cursor de MongoDB a una lista de diccionarios serializables.

    Args:
        cursor: Cursor de MongoDB (resultado de find() o aggregate())

    Returns:
        Lista de diccionarios serializables a JSON
    """
    documents = list(cursor)
    return serialize_mongo_document(documents)
