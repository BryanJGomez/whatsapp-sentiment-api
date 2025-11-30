import os
import redis
from src.config.settings import settings

def create_redis_client():

    host = settings.REDIS_HOST
    port = settings.REDIS_PORT

    return redis.StrictRedis(host = host, port = port)
