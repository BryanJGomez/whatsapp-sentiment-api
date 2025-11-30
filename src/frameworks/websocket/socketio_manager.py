"""
Gestor de Socket.IO para comunicación en tiempo real.
Maneja eventos de WebSocket para notificar al frontend sobre cambios.
"""

from flask_socketio import SocketIO, emit, join_room, leave_room
from src.frameworks.logging.logger import setup_logger

logger = setup_logger(__name__)


class SocketIOManager:
    """
    Gestor centralizado de Socket.IO.

    Eventos emitidos:
    - 'message_received': Cuando llega un nuevo mensaje al webhook
    - 'message_analyzed': Cuando el worker termina de analizar un mensaje
    - 'stats_updated': Cuando las estadísticas del dashboard cambian
    """

    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self._register_handlers()
        logger.info("SocketIOManager inicializado")

    def _register_handlers(self):
        """Registra los event handlers de Socket.IO"""

        @self.socketio.on('connect')
        def handle_connect():
            """Cliente conectado al WebSocket"""
            logger.info(f"Cliente conectado via WebSocket")
            emit('connected', {'message': 'Conectado al servidor de análisis en tiempo real'})

        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Cliente desconectado del WebSocket"""
            logger.info(f"Cliente desconectado")

        @self.socketio.on('join_dashboard')
        def handle_join_dashboard():
            """Cliente se une al room del dashboard para recibir actualizaciones"""
            join_room('dashboard')
            logger.info(f"Cliente se unió al room 'dashboard'")
            emit('joined', {'room': 'dashboard'})

        @self.socketio.on('leave_dashboard')
        def handle_leave_dashboard():
            """Cliente sale del room del dashboard"""
            leave_room('dashboard')
            logger.info(f"Cliente salió del room 'dashboard'")

    def emit_message_received(self, message_data: dict):
        """
        Notifica que se recibió un nuevo mensaje (sin analizar aún).

        Args:
            message_data: Dict con message_id, numero_remitente, texto_mensaje
        """
        logger.info(f"Emitiendo evento 'message_received' para mensaje {message_data.get('message_id')}")
        self.socketio.emit(
            'message_received',
            {
                'message_id': message_data.get('message_id'),
                'numero_remitente': message_data.get('numero_remitente'),
                'texto_mensaje': message_data.get('texto_mensaje'),
                'status': 'pending_analysis'
            },
            room='dashboard'
        )

    def emit_message_analyzed(self, analysis_data: dict):
        """
        Notifica que se completó el análisis de un mensaje.

        Args:
            analysis_data: Dict con message_id, sentimiento, tema, resumen
        """
        logger.info(f"Emitiendo evento 'message_analyzed' para mensaje {analysis_data.get('message_id')}")
        self.socketio.emit(
            'message_analyzed',
            {
                'message_id': analysis_data.get('message_id'),
                'sentimiento': analysis_data.get('sentimiento'),
                'tema': analysis_data.get('tema'),
                'resumen': analysis_data.get('resumen'),
                'status': 'analyzed'
            },
            room='dashboard'
        )

    def emit_stats_updated(self, stats: dict):
        """
        Notifica que las estadísticas del dashboard fueron actualizadas.

        Args:
            stats: Dict con estadísticas actualizadas
        """
        logger.debug("Emitiendo evento 'stats_updated'")
        self.socketio.emit(
            'stats_updated',
            stats,
            room='dashboard'
        )

    def emit_error(self, error_data: dict):
        """
        Notifica un error al frontend.

        Args:
            error_data: Dict con información del error
        """
        logger.warning(f"Emitiendo evento 'error': {error_data.get('message')}")
        self.socketio.emit(
            'error',
            error_data,
            room='dashboard'
        )
