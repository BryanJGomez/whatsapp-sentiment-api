"""
Configuración y creación de la aplicación Flask.
Importa configuraciones desde config/settings.py
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from src.config.settings import settings
from src.frameworks.logging.logger import setup_logger
from src.frameworks.http.error_handlers import register_error_handlers

logger = setup_logger()


def create_flask_app(blueprints: list):
    """
    Crea y configura la aplicación Flask con los blueprints inyectados.

    Args:
        blueprints: Lista de blueprints (controladores) a registrar

    Returns:
        Flask: Aplicación Flask configurada
    """
    app = Flask(__name__)

    # Configuraciones básicas de Flask
    app.config['ENV'] = settings.FLASK_ENV
    app.config['DEBUG'] = settings.FLASK_DEBUG
    app.config['JSON_AS_ASCII'] = False  # Para caracteres UTF-8
    app.config['JSON_SORT_KEYS'] = False  # No ordenar keys en JSON

    # CONFIGURACIÓN DE CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": settings.CORS_ORIGINS,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        },
        r"/webhook/*": {
            "origins": "*",  # Webhooks de Twilio
            "methods": ["POST", "GET"]
        }
    })

    # Configuración de Socket.IO coon redis message Queue
    # Necesario para múltiples workers/procesos (Gunicorn, Railway)
    if settings.REDIS_PASSWORD:
        redis_url = f'redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/0'
    else:
        redis_url = f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0'

    socketio = SocketIO(
        app,
        cors_allowed_origins=settings.SOCKETIO_CORS_ORIGINS,
        async_mode=settings.SOCKETIO_ASYNC_MODE,
        message_queue=redis_url,  # Crucial para múltiples workers
        logger=False,  # Usar nuestro logger
        engineio_logger=False,
        ping_timeout=60,
        ping_interval=25
    )

    # REGISTRAR BLUEPRINTS (Controladores)
    for blueprint in blueprints:
        # Los webhooks se registran en /webhook, el resto en /api
        if blueprint.name == "webhook":
            app.register_blueprint(blueprint, url_prefix='/webhook')
        else:
            app.register_blueprint(blueprint, url_prefix='/api')

    # ENDPOINTS GLOBALES
    @app.route('/', methods=['GET'])
    def root():
        """Endpoint raíz con información de la API"""
        return jsonify({
            "nombre": "WhatsApp Sentiment Analysis API",
            "version": "1.0.0",
            "endpoints": {
                "health": "/health",
                "webhook": "/webhook/whatsapp",
                "estadisticas": "/api/estadisticas",
                "distribucion": "/api/sentimientos",
                "temas": "/api/temas",
                "mensajes": "/api/mensajes-recientes",
                "sentimientos_tema": "/api/sentimientos-por-tema"
            }
        }), 200

    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            "status": "ok",
            "environment": settings.FLASK_ENV
        }), 200

    @app.route('/api/health/socketio', methods=['GET'])
    def socketio_health():
        """Health check para Socket.IO"""
        return jsonify({
            "status": "ok",
            "socketio": "enabled",
            "async_mode": settings.SOCKETIO_ASYNC_MODE,
            "cors_origins": settings.SOCKETIO_CORS_ORIGINS
        }), 200

    # Registrar manejadores de errores personalizados
    register_error_handlers(app)

    return app, socketio
