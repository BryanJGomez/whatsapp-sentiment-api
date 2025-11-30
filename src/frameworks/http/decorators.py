"""
Decoradores para manejo de errores en controladores.
Permite centralizar el manejo de excepciones en un solo lugar.
"""

from functools import wraps
from flask import jsonify
from pymongo.errors import PyMongoError
from src.frameworks.logging.logger import setup_logger
from src.frameworks.http.error_handlers import (
    APIError,
    ValidationError,
    DatabaseError,
    NotFoundError,
    UnauthorizedError
)

logger = setup_logger(__name__)


def handle_errors(f):
    """
    Decorador para manejar errores en endpoints de Flask.

    Este decorador captura todas las excepciones que pueden ocurrir
    en las capas inferiores (usecase, repository) y las convierte
    en respuestas HTTP apropiadas.

    Uso:
        @blueprint.route('/endpoint')
        @handle_errors
        def mi_endpoint():
            return {"data": "..."}
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Ejecutar la función del endpoint
            return f(*args, **kwargs)

        except PyMongoError as e:
            # Errores específicos de MongoDB
            logger.error(f"Error de MongoDB: {str(e)}", exc_info=True)
            raise DatabaseError("Error al consultar la base de datos")

        except ValidationError as e:
            # Errores de validación (ya formateados)
            logger.warning(f"Validación fallida: {e.message}")
            raise

        except NotFoundError as e:
            # Recursos no encontrados
            logger.info(f"Recurso no encontrado: {e.message}")
            raise

        except UnauthorizedError as e:
            # Problemas de autenticación
            logger.warning(f"Acceso no autorizado: {e.message}")
            raise

        except DatabaseError as e:
            # Otros errores de base de datos
            logger.error(f"Error de base de datos: {e.message}")
            raise

        except APIError as e:
            # Otros errores de API personalizados
            logger.error(f"Error de API: {e.message}")
            raise

        except Exception as e:
            # Cualquier otro error no esperado
            logger.critical(f"Error inesperado en {f.__name__}: {str(e)}", exc_info=True)
            raise APIError(
                "Error inesperado al procesar la solicitud",
                status_code=500,
                payload={"detail": str(e)}
            )

    return decorated_function
