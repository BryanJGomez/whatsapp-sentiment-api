from src.frameworks.http.flask import create_flask_app
from src.frameworks.db.mongo import create_mongo_client
from src.frameworks.db.redis import create_redis_client
from src.frameworks.cache.redis_cache import RedisCache
from src.frameworks.queue.message_queue import MessageQueue
from src.frameworks.websocket.socketio_manager import SocketIOManager
from src.frameworks.db.collections import create_collections_and_indexes
from src.config.settings import settings
from src.frameworks.logging.logger import setup_logger

# Importar blueprints
from src.app.dashboard.http.dashboard_blueprint import dashboard_blueprint
from src.app.messages.http.webhook_blueprint import webhook_blueprint

# Importar repositorios
from src.app.messages.repositories.message_repository import MessageRepository
from src.app.dashboard.repositories.dashboard_repository import DashboardRepository

# Importar servicios
from src.app.messages.services.sentiment_analysis_service import SentimentAnalysisService

# Importar usecases
from src.app.dashboard.usecases.manage_dashboard_usecase import DashboardUsecase
from src.app.messages.usecases.message_usecases import MessageUsecase


# Validar configuraciones al inicio
settings.validate()

# Crear clientes de base de datos
mongo_client = create_mongo_client()
mongo_db = mongo_client[settings.MONGO_DB_NAME]
redis_client = create_redis_client()

# Inicializar colecciones e índices de MongoDB
logger = setup_logger(__name__)
create_collections_and_indexes(
    mongo_db,
    collection_name=settings.MONGO_COLLECTION_MENSAJES
)

# Crear cliente de caché Redis
redis_cache = RedisCache()

# Crear cola de mensajes
message_queue = MessageQueue()

# Crear repositorios
message_repository = MessageRepository(mongo_db)
dashboard_repository = DashboardRepository(mongo_db)

# Crear servicios
sentiment_analysis_service = SentimentAnalysisService(redis_cache=redis_cache)

# Casos de uso
message_usecase = MessageUsecase(message_repository, sentiment_analysis_service)
dashboard_usecase = DashboardUsecase(dashboard_repository)

# Configurar blueprints
blueprints = [
    webhook_blueprint(message_queue, message_repository),
    dashboard_blueprint(dashboard_usecase)
]

# Crear aplicación Flask con Socket.IO
app, socketio = create_flask_app(blueprints)

# Crear gestor de Socket.IO (global para que worker.py pueda acceder)
socketio_manager = SocketIOManager(socketio)

# Exponer socketio y socketio_manager como atributos de app para acceso global
app.socketio = socketio
app.socketio_manager = socketio_manager
