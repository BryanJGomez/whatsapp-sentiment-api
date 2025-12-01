"""
Blueprint para manejar webhooks de Twilio WhatsApp.
"""

from flask import Blueprint, jsonify, request, current_app
from src.frameworks.logging.logger import setup_logger
from src.frameworks.http.decorators import handle_errors
from src.frameworks.http.error_handlers import ValidationError
from src.app.messages.entities.message import Message

logger = setup_logger(__name__)


def webhook_blueprint(message_queue, message_repository):
    """
    Crea el blueprint para webhooks de Twilio.

    Args:
        message_queue: Servicio de cola para mensajes
        message_repository: Repositorio de mensajes
    """

    blueprint = Blueprint("webhook", __name__)

    @blueprint.route("/whatsapp", methods=["POST"])
    @handle_errors
    def receive_whatsapp_message():
        """
        Webhook para recibir mensajes de Twilio WhatsApp.
        Twilio envía los datos en formato form-urlencoded con los campos:
        - Body: Texto del mensaje
        - From: Número del remitente (formato: whatsapp:+1234567890)
        - To: Número receptor
        - MessageSid: ID único del mensaje de Twilio
        """
        # Obtener datos del formulario
        message_body = request.form.get("Body")
        from_number = request.form.get("From")
        message_sid = request.form.get("MessageSid")

        # Validar que tengamos los datos necesarios
        if not message_body:
            raise ValidationError("Campo 'Body' es requerido")

        if not from_number:
            raise ValidationError("Campo 'From' es requerido")

        message = Message(
            texto_mensaje=message_body,
            numero_remitente=from_number,
            message_sid=message_sid
        )
        message_id = message_repository.save(message)

        # 2. Encolar para procesamiento asíncrono
        message_queue.enqueue(
            texto_mensaje=message_body,
            numero_remitente=from_number,
            message_id=message_id
        )

        # 3. Emitir evento Socket.IO (mensaje recibido, análisis pendiente)
        try:
            socketio_manager = current_app.socketio_manager
            socketio_manager.emit_message_received({
                "message_id": message_id,
                "numero_remitente": from_number,
                "texto_mensaje": message_body
            })
        except Exception as e:
            logger.warning(f"No se pudo emitir evento Socket.IO: {e}")

        # 4. Responder INMEDIATAMENTE (sin esperar análisis)
        response = {
            "code": "SUCCESS",
            "message": "Mensaje recibido y en proceso de análisis",
            "data": {
                "message_id": message_id,
                "status": "success",
            }
        }
        return jsonify(response), 200

    @blueprint.route("/whatsapp/test", methods=["POST"])
    @handle_errors
    def test_webhook():
        """
        Endpoint de prueba para simular mensajes sin usar Twilio.

        FLUJO ASÍNCRONO:
        1. Guarda mensaje
        2. Encola para procesamiento
        3. Responde inmediatamente
        """
        data = request.get_json()

        if not data or "texto_mensaje" not in data or "numero_remitente" not in data:
            raise ValidationError("Se requieren 'texto_mensaje' y 'numero_remitente' en el body JSON")

        message = Message(
            texto_mensaje=data["texto_mensaje"],
            numero_remitente=data["numero_remitente"],
            message_sid=data.get("message_sid")
        )
        message_id = message_repository.save(message)

        message_queue.enqueue(
            texto_mensaje=data["texto_mensaje"],
            numero_remitente=data["numero_remitente"],
            message_id=message_id
        )

        # 2.5 Emitir evento Socket.IO
        try:
            socketio_manager = current_app.socketio_manager
            socketio_manager.emit_message_received({
                "message_id": message_id,
                "numero_remitente": data["numero_remitente"],
                "texto_mensaje": data["texto_mensaje"]
            })
        except Exception as e:
            logger.warning(f"No se pudo emitir evento Socket.IO: {e}")

        # 3. Responder inmediatamente
        return jsonify({
            "code": "SUCCESS",
            "message": "Mensaje encolado para análisis",
            "data": {
                "message_id": message_id,
                "status": "SUCCESS",
                "info": "El análisis se completará en segundos. Consulta /api/mensajes-recientes para ver el resultado"
            }
        }), 200

    @blueprint.route("/queue/status", methods=["GET"])
    @handle_errors
    def queue_status():
        """
        Endpoint para ver el estado de la cola.
        """
        queue_size = message_queue.get_queue_size()

        return jsonify({
            "code": "SUCCESS",
            "data": {
                "pending_messages": queue_size,
                "queue_name": message_queue.queue_name
            }
        }), 200

    return blueprint
