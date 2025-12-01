"""
Servidor de desarrollo con Flask + SocketIO.
Este script se usa SOLO en desarrollo local para evitar problemas con gunicorn.
En producción se debe usar gunicorn con eventlet (ver gunicorn_config.py).
"""
import eventlet
eventlet.monkey_patch()

from src.main import app, socketio
from src.config.settings import settings
from src.frameworks.logging.logger import setup_logger

logger = setup_logger(__name__)

if __name__ == "__main__":

    # Usar socketio.run() en lugar de app.run() para soportar WebSockets
    socketio.run(
        app,
        host="0.0.0.0",
        port=8080,
        debug=True,
        use_reloader=True,  # Hot reload en desarrollo
        log_output=True,
        allow_unsafe_werkzeug=True  # Necesario para desarrollo
    )
