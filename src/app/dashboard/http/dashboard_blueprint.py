from flask import Blueprint, jsonify, request
from src.frameworks.logging.logger import setup_logger
from src.frameworks.http.decorators import handle_errors

logger = setup_logger(__name__)


def dashboard_blueprint(dashboard_usecase):
    """
    Crea el blueprint del dashboard con todos los endpoints de visualización.

    Args:
        dashboard_usecase: UseCase único para todas las operaciones del dashboard
    """

    blueprint = Blueprint("dashboard", __name__)

    @blueprint.route("/estadisticas", methods=["GET"])
    @handle_errors
    def get_statistics():
        """Obtiene estadísticas generales del dashboard"""
        stats = dashboard_usecase.get_statistics()

        return jsonify({
            "code": "SUCCESS",
            "message": "Estadísticas obtenidas correctamente",
            "data": stats
        }), 200

    @blueprint.route("/distribucion-sentimientos", methods=["GET"])
    @handle_errors
    def get_sentiment_distribution():
        """Obtiene la distribución de sentimientos (positivo, negativo, neutro)"""
        distribution = dashboard_usecase.get_sentiment_distribution()

        return jsonify({
            "code": "SUCCESS",
            "message": "Distribución de sentimientos obtenida",
            "data": distribution
        }), 200

    @blueprint.route("/temas-frecuentes", methods=["GET"])
    @handle_errors
    def get_top_topics():
        """Obtiene los temas más frecuentes mencionados por los clientes"""
        limit = request.args.get("limit", default=20, type=int)
        topics = dashboard_usecase.get_top_topics(limit=limit)

        return jsonify({
            "code": "SUCCESS",
            "message": "Temas frecuentes obtenidos",
            "data": topics
        }), 200

    @blueprint.route("/mensajes-recientes", methods=["GET"])
    @handle_errors
    def get_recent_messages():
        """Obtiene los mensajes más recientes con su análisis"""
        limit = request.args.get("limit", default=10, type=int)
        messages = dashboard_usecase.get_recent_messages(limit=limit)

        return jsonify({
            "code": "SUCCESS",
            "message": "Mensajes recientes obtenidos",
            "data": messages
        }), 200

    return blueprint
