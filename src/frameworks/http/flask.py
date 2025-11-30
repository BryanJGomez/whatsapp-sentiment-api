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

    # CONFIGURACIÓN DE FLASK
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

    # CONFIGURACIÓN DE SOCKET.IO
    socketio = SocketIO(
        app,
        cors_allowed_origins=settings.SOCKETIO_CORS_ORIGINS,
        async_mode=settings.SOCKETIO_ASYNC_MODE,
        logger=False,  # Usar nuestro logger
        engineio_logger=False,
        ping_timeout=60,
        ping_interval=25
    )
    logger.info(f"Socket.IO inicializado con async_mode={settings.SOCKETIO_ASYNC_MODE}")

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
                "distribucion": "/api/distribucion-sentimientos",
                "temas": "/api/temas-frecuentes",
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

    # REGISTRAR MANEJADORES DE ERRORES
    register_error_handlers(app)

    return app, socketio
