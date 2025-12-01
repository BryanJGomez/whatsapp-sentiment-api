import os
import redis
from src.config.settings import settings

def create_redis_client():
    host = settings.REDIS_HOST
    port = settings.REDIS_PORT
    password = settings.REDIS_PASSWORD

    print(f"Connecting to Redis at {host}:{port}")
    print(f"Using password: {'Yes' if password else 'No'}")

    # Se usa el Connection Pool para una gestión robusta de las conexiones
    pool = redis.ConnectionPool(
        host=host,
        port=port,
        password=password,
        # Habilita la reconexión automática en caso de fallo
        retry_on_timeout=True,
        # Aumenta el tiempo de espera por si la conexión es lenta/inactiva
        socket_timeout=3600,
        decode_responses=True # Para obtener strings en lugar de bytes
    )

    # Devuelve el cliente StrictRedis usando el pool
    return redis.StrictRedis(connection_pool=pool)
