"""
Script para inicializar/migrar la base de datos MongoDB.
- Crea colecciones con esquemas de validación
- Crea índices para optimizar consultas
- Migra datos existentes si es necesario
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.frameworks.db.mongo import create_mongo_client
from src.frameworks.db.collections import (
    create_collections_and_indexes,
    get_collection_stats
)
from src.config.settings import settings


def main():
    """Función principal de inicialización"""
    print("=" * 60)
    print("🚀 INICIALIZACIÓN DE BASE DE DATOS MONGODB")
    print("=" * 60)

    # Validar configuración
    settings.validate()

    # Conectar a MongoDB
    print("\n📡 Conectando a MongoDB...")
    mongo_client = create_mongo_client()

    # Nombre de la colección
    collection_name = settings.MONGO_COLLECTION_MENSAJES

    # Crear/actualizar colección con esquema e índices
    print(f"\n🗄️  Configurando colección '{collection_name}'...")
    create_collections_and_indexes(mongo_client, collection_name)

    # Mostrar estadísticas
    print("\n📊 Estadísticas de la colección:")
    stats = get_collection_stats(mongo_client, collection_name)
    print(f"   Base de datos: {stats['database']}")
    print(f"   Colección: {stats['nombre']}")
    print(f"   Total de documentos: {stats['total_documentos']}")
    print(f"   Índices creados: {len(stats['indices'])}")
    for index_name in stats['indices'].keys():
        print(f"      - {index_name}")

    print("\n" + "=" * 60)
    print("✅ INICIALIZACIÓN COMPLETADA")
    print("=" * 60)


if __name__ == "__main__":
    main()
