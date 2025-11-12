"""
Script de ayuda para comandos comunes del proyecto
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))


def mostrar_ayuda():
    """Muestra comandos útiles del proyecto"""
    print(
        """
╔════════════════════════════════════════════════════════════╗
║               ATHomeRed - Comandos Útiles                  ║
╚════════════════════════════════════════════════════════════╝

📋 CONFIGURACIÓN INICIAL:
   python scripts/test_connection.py      # Probar conexión a BD
   python scripts/create_schema.py        # Crear esquema 'athome' (solo 1ra vez)
   python scripts/init_db.py              # Crear tablas (desarrollo)
   alembic upgrade head                   # Aplicar migraciones (producción)

🗄️  BASE DE DATOS (Alembic):
   python scripts/create_schema.py                  # Crear esquema (PRIMERO)
   alembic revision --autogenerate -m "descripción"  # Nueva migración
   alembic upgrade head                              # Aplicar migraciones
   alembic downgrade -1                             # Revertir última
   alembic current                                  # Ver versión actual
   alembic history                                  # Ver historial

🚀 EJECUTAR SERVIDOR:
   uvicorn app.main:app --reload          # Desarrollo (auto-reload)
   uvicorn app.main:app --host 0.0.0.0   # Producción

🧪 TESTING:
   pytest                                 # Ejecutar todos los tests
   pytest tests/test_profesional.py      # Test específico
   pytest -v                             # Verbose
   pytest --cov=app                      # Con coverage

📦 DEPENDENCIAS:
   pip install -r requirements.txt       # Instalar dependencias
   pip freeze > requirements.txt         # Actualizar requirements

🔧 UTILIDADES:
   python scripts/seed_data.py           # Cargar datos de prueba
   python scripts/clean_db.py            # Limpiar base de datos

📚 DOCUMENTACIÓN:
   http://localhost:8000/docs             # Swagger UI (ejecutar servidor primero)
   http://localhost:8000/redoc            # ReDoc

╔════════════════════════════════════════════════════════════╗
║                  Archivos Importantes                       ║
╚════════════════════════════════════════════════════════════╝

📁 Configuración:
   .env                    # Variables de entorno (NO subir a Git)
   .env.example           # Plantilla de .env (SÍ subir)
   requirements.txt       # Dependencias Python
   alembic.ini           # Config de migraciones

📁 Código:
   app/domain/           # Entidades y lógica de negocio
   app/infra/            # Repositorios y persistencia
   app/api/              # Endpoints y schemas

📁 Scripts:
   scripts/init_db.py            # Crear BD
   scripts/test_connection.py    # Probar conexión
   scripts/seed_data.py          # Datos de prueba

📁 Migraciones:
   alembic/versions/     # Historial de migraciones

╔════════════════════════════════════════════════════════════╗
║                     Documentación                           ║
╚════════════════════════════════════════════════════════════╝

📖 README.md                          # Inicio del proyecto
📖 ARCHITECTURE.md                    # Arquitectura
📖 ANALISIS_DOMAIN_INFRA.md          # Análisis técnico
📖 CAMBIOS_COMPLETADOS.md            # Últimos cambios
📖 PROFESIONAL_REPOSITORY_GUIDE.md   # Guía de repositorios

╔════════════════════════════════════════════════════════════╗
║                    Variables de Entorno                     ║
╚════════════════════════════════════════════════════════════╝

En .env (copia .env.example y modifica):

# PostgreSQL (Producción):
DB_DIALECT=postgresql
DB_HOST=tu-host.supabase.co
DB_PORT=5432
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_NAME=postgres
DB_SSLMODE=require

# SQLite (Desarrollo local):
DB_DIALECT=sqlite
# (automático: sqlite:///./app.db)

"""
    )


if __name__ == "__main__":
    mostrar_ayuda()
