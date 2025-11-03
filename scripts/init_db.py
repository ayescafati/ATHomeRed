"""
Script de inicialización de la base de datos
Crea todas las tablas usando Alembic
o SQLAlchemy metadata
"""
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.infra.persistence.database import ENGINE
from app.infra.persistence.base import Base


def main():
    """
    Crea todas las tablas en la base de datos.
    
    NOTA: En producción, usa Alembic migrations:
          alembic upgrade head
    
    Este script es útil para desarrollo/testing rápido.
    """
    print("=" * 60)
    print("🔧 INICIALIZANDO BASE DE DATOS")
    print("=" * 60)
    
    # Importar todos los modelos para que SQLAlchemy los registre
    from app.infra.persistence import (
        usuarios,
        perfiles,
        paciente,
        ubicacion,
        servicios,
        agenda,
        valoraciones,
        matriculas,
        publicaciones,
        relaciones,
        auth
    )
    
    print(f"\n Base de datos: {ENGINE.url}")
    
    # Crear todas las tablas
    print("\n  Creando tablas...")
    Base.metadata.create_all(bind=ENGINE)
    
    print("\n Tablas creadas exitosamente!")
    print("\n Tablas creadas:")
    for table_name in Base.metadata.tables.keys():
        print(f"   - {table_name}")
    
    print("\n" + "=" * 60)
    print(" Base de datos inicializada")
    print("=" * 60)
    

if __name__ == "__main__":
    main()
