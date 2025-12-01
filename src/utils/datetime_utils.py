from datetime import datetime
from typing import Optional
import pytz
from src.config.settings import settings


def format_timestamp_to_local(
    timestamp: str,
    timezone: str = None,
    format: str = None
) -> str:
    """
    Convierte un timestamp UTC a hora local en el formato especificado.

    Args:
        timestamp: String con el timestamp en formato ISO 8601
        timezone: Zona horaria de destino (por defecto la de settings)
        format: Formato de salida (por defecto el de settings)

    Returns:
        String con la fecha y hora formateada en hora local
    """
    if timezone is None:
        timezone = settings.TIMEZONE
    if format is None:
        format = settings.DATETIME_FORMAT

    try:
        # Parsear el timestamp
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        else:
            dt = timestamp

        # Si el timestamp no tiene timezone, asumimos UTC
        if dt.tzinfo is None:
            dt = pytz.UTC.localize(dt)

        # Convertir a la zona horaria local
        local_tz = pytz.timezone(timezone)
        local_dt = dt.astimezone(local_tz)

        # Formatear y retornar
        return local_dt.strftime(format)
    except Exception as e:
        # En caso de error, retornar el timestamp original
        return timestamp


def format_timestamp_humanized(
    timestamp: str,
    timezone: str = 'America/El_Salvador'
) -> str:
    """
    Convierte un timestamp a un formato más legible y humanizado.

    Args:
        timestamp: String con el timestamp en formato ISO 8601
        timezone: Zona horaria de destino

    Returns:
        String con la fecha en formato legible (ej: "30 Nov 2025, 7:51 PM")
    """
    try:
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        else:
            dt = timestamp

        if dt.tzinfo is None:
            dt = pytz.UTC.localize(dt)

        local_tz = pytz.timezone(timezone)
        local_dt = dt.astimezone(local_tz)

        # Meses en español
        meses = {
            1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr',
            5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Ago',
            9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
        }

        mes = meses[local_dt.month]
        hora_12 = local_dt.strftime('%I:%M %p')

        return f"{local_dt.day} {mes} {local_dt.year}, {hora_12}"
    except Exception as e:
        return timestamp
