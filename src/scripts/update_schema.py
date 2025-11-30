"""
Script para actualizar el esquema de validación de una colección existente.
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.frameworks.db.mongo import create_mongo_client
from src.frameworks.db.collections import MENSAJES_SCHEMA
from src.config.settings import settings


def main():
    """Actualizar el validador de la colección"""
    print("=" * 60)
    print("🔧 ACTUALIZANDO ESQUEMA DE VALIDACIÓN")
    print("=" * 60)

    # Validar configuración
    settings.validate()

    # Conectar a MongoDB
    print("\n📡 Conectando a MongoDB...")
    mongo_client = create_mongo_client()

    # Nombre de la colección
    collection_name = settings.MONGO_COLLECTION_MENSAJES

    # Actualizar el validador
    print(f"\n🗄️  Actualizando validador de '{collection_name}'...")
    try:
        mongo_client.command({
            "collMod": collection_name,
            "validator": MENSAJES_SCHEMA
        })
        print(f"✅ Validador actualizado correctamente")
    except Exception as e:
        print(f"❌ Error actualizando validador: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ ACTUALIZACIÓN COMPLETADA")
    print("=" * 60)


if __name__ == "__main__":
    main()
