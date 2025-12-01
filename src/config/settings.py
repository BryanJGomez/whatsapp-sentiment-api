import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Configuración centralizada de la aplicación"""

    # MongoDB
    MONGO_URI = os.getenv('MONGO_URI')
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'whatsapp_sentiment')
    MONGO_COLLECTION_MENSAJES = os.getenv('MONGO_COLLECTION_MENSAJES', 'mensajes')

    # Redis
    REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

    # Google Gemini
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')

    # Flask
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')

    # Socket.IO (para producción con Vercel + Railway)
    SOCKETIO_CORS_ORIGINS = os.getenv('SOCKETIO_CORS_ORIGINS', '*')
    SOCKETIO_ASYNC_MODE = os.getenv('SOCKETIO_ASYNC_MODE', 'eventlet')  # eventlet para producción

    # Configuración de timezone y formato de fechas
    TIMEZONE = os.getenv('TIMEZONE', 'America/El_Salvador')
    DATETIME_FORMAT = os.getenv('DATETIME_FORMAT', '%Y-%m-%d %H:%M:%S')

    @classmethod
    def validate(cls):
        """Valida que las configuraciones críticas estén presentes"""
        errors = []

        if not cls.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY no está configurada correctamente")

        if not cls.MONGO_URI:
            errors.append("❌ MONGO_URI no está configurada")

        if not cls.MONGO_DB_NAME:
            errors.append("MONGO_DB_NAME no está configurada")

        if not cls.MONGO_COLLECTION_MENSAJES:
            errors.append("MONGO_COLLECTION_MENSAJES no está configurada")

        if errors:
            for error in errors:
                print(error)
            # Solo lanzar error si es crítico (MongoDB)
            if not cls.MONGO_URI or not cls.MONGO_DB_NAME:
                raise ValueError("Configuraciones críticas faltantes")


settings = Settings()
