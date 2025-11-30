"""
Manejo centralizado de errores y excepciones personalizadas.
"""

from flask import jsonify
from werkzeug.exceptions import HTTPException
from src.frameworks.logging.logger import setup_logger

logger = setup_logger(__name__)


class APIError(Exception):
    """Excepción base para errores de la API"""

    def __init__(self, message: str, status_code: int = 500, payload: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}

    def to_dict(self):
        """Convierte el error a un diccionario JSON"""
        error_dict = {
            'error': self.message,
            'status': self.status_code,
            'code': self.__class__.__name__
        }
        if self.payload:
            error_dict.update(self.payload)
        return error_dict


class ValidationError(APIError):
    """Error de validación de datos"""
    def __init__(self, message: str, payload: dict = None):
        super().__init__(message, status_code=400, payload=payload)


class NotFoundError(APIError):
    """Recurso no encontrado"""
    def __init__(self, message: str = "Recurso no encontrado", payload: dict = None):
        super().__init__(message, status_code=404, payload=payload)


class UnauthorizedError(APIError):
    """Error de autenticación"""
    def __init__(self, message: str = "No autorizado", payload: dict = None):
        super().__init__(message, status_code=401, payload=payload)


class DatabaseError(APIError):
    """Error de base de datos"""
    def __init__(self, message: str = "Error en la base de datos", payload: dict = None):
        super().__init__(message, status_code=500, payload=payload)


def register_error_handlers(app):
    """
    Registra los manejadores de errores en la aplicación Flask.

    Args:
        app: Instancia de Flask
    """

    @app.errorhandler(APIError)
    def handle_api_error(error):
        """Maneja errores personalizados de la API"""
        logger.error(f"{error.__class__.__name__}: {error.message}", extra=error.payload)
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Maneja excepciones HTTP de Werkzeug"""
        logger.warning(f"HTTP {error.code}: {error.description}")
        response = jsonify({
            'error': error.description or 'Error en la solicitud',
            'status': error.code,
            'code': error.name
        })
        response.status_code = error.code
        return response

    @app.errorhandler(404)
    def not_found(error):
        """Maneja errores 404"""
        logger.warning(f"Endpoint no encontrado: {error}")
        return jsonify({
            'error': 'Endpoint no encontrado',
            'status': 404,
            'code': 'NotFound'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Maneja errores 500"""
        logger.error(f"Error interno del servidor: {error}", exc_info=True)
        return jsonify({
            'error': 'Error interno del servidor',
            'status': 500,
            'code': 'InternalServerError'
        }), 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Maneja cualquier excepción no capturada"""
        logger.critical(f"Error inesperado: {error}", exc_info=True)
        return jsonify({
            'error': 'Error inesperado en el servidor',
            'status': 500,
            'code': 'UnexpectedError'
        }), 500
