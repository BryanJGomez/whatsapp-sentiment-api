"""
Casos de uso para el dashboard.
"""

from src.frameworks.logging.logger import setup_logger
from src.app.dashboard.repositories.dashboard_repository import DashboardRepository

logger = setup_logger(__name__)


class DashboardUsecase:
    """
    Caso de uso único para todas las operaciones del dashboard.
    Recibe en el constructor el repositorio a utilizar.
    El caso de uso debe funcionar independientemente de la implementación del repositorio.
    """

    def __init__(self, dashboard_repository: DashboardRepository):
        self.dashboard_repository = dashboard_repository

    def get_statistics(self) -> dict:
        """
        Obtiene estadísticas generales del dashboard.

        Returns:
            Dict con estadísticas
        """
        return self.dashboard_repository.get_statistics()

    def get_sentiment_distribution(self) -> dict:
        """
        Obtiene la distribución de sentimientos.

        Returns:
            Dict con conteo por sentimiento
        """
        return self.dashboard_repository.get_sentiment_distribution()

    def get_top_topics(self, limit: int = 5) -> list:
        """
        Obtiene los temas más frecuentes.

        Args:
            limit: Número de temas a retornar

        Returns:
            Lista de temas con su frecuencia
        """
        return self.dashboard_repository.get_top_topics(limit)

    def get_recent_messages(self, limit: int = 10) -> list:
        """
        Obtiene los mensajes más recientes.

        Args:
            limit: Número de mensajes a retornar

        Returns:
            Lista de mensajes
        """
        return self.dashboard_repository.get_recent_messages(limit)
