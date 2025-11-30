"""
Sistema de logging centralizado para la aplicación.
Configura logs con formato estructurado y niveles apropiados.
"""

import logging
import sys
from datetime import datetime
from src.config.settings import settings


class ColoredFormatter(logging.Formatter):
    """Formatter con colores para terminal"""

    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{log_color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


def setup_logger(name: str = __name__) -> logging.Logger:
    """
    Configura y retorna un logger con el nombre especificado.

    Args:
        name: Nombre del logger (generalmente __name__ del módulo)

    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)

    # Evitar duplicar handlers si ya existe
    if logger.handlers:
        return logger

    # Nivel de log según configuración
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Formato de log
    if settings.FLASK_ENV == 'development':
        # En desarrollo: formato con colores y más detallado
        formatter = ColoredFormatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        # En producción: formato JSON estructurado
        formatter = logging.Formatter(
            '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s",'
            '"function":"%(funcName)s","line":%(lineno)d,"message":"%(message)s"}',
            datefmt='%Y-%m-%dT%H:%M:%S'
        )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # No propagar a loggers padre
    logger.propagate = False

    return logger


# Logger global de la aplicación
app_logger = setup_logger('maic')
