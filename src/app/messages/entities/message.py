"""
Entidad Message - Representa un mensaje de WhatsApp del cliente.
"""

from datetime import datetime
from typing import Optional


class Message:
    """
    Representa un mensaje recibido vía WhatsApp.
    """

    def __init__(
        self,
        texto_mensaje: str,
        numero_remitente: str,
        timestamp: Optional[datetime] = None,
        message_sid: Optional[str] = None,
        sentimiento: Optional[str] = None,
        tema: Optional[str] = None,
        resumen: Optional[str] = None,
        _id: Optional[str] = None
    ):
        self._id = _id
        self.texto_mensaje = texto_mensaje
        # Limpiar el prefijo "whatsapp:" si existe
        self.numero_remitente = numero_remitente.replace("whatsapp:", "") if numero_remitente else numero_remitente
        self.message_sid = message_sid
        self.timestamp = timestamp or datetime.utcnow()
        self.sentimiento = sentimiento  # "positivo", "negativo", "neutro"
        self.tema = tema  # "Servicio al Cliente", "Calidad del Producto", etc.
        self.resumen = resumen

    def to_dict(self):
        """Convierte la entidad a un diccionario para MongoDB"""
        data = {
            "texto_mensaje": self.texto_mensaje,
            "numero_remitente": self.numero_remitente,
            "timestamp": self.timestamp,
            "sentimiento": self.sentimiento,
            "tema": self.tema,
            "resumen": self.resumen
        }
        if self.message_sid:
            data["message_sid"] = self.message_sid
        if self._id:
            data["_id"] = self._id
        return data

    @classmethod
    def from_dict(cls, data: dict):
        """Crea una instancia desde un diccionario de MongoDB"""
        return cls(
            texto_mensaje=data.get("texto_mensaje"),
            numero_remitente=data.get("numero_remitente"),
            timestamp=data.get("timestamp"),
            message_sid=data.get("message_sid"),
            sentimiento=data.get("sentimiento"),
            tema=data.get("tema"),
            resumen=data.get("resumen"),
            _id=str(data.get("_id")) if data.get("_id") else None
        )

    def __repr__(self):
        return f"Message(remitente={self.numero_remitente}, sentimiento={self.sentimiento}, tema={self.tema})"
