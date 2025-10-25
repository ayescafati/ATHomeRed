# create_db.py (puede estar en la raíz del proyecto)
from app.infra.db.database import Base, ENGINE
from app.infra.db.models import *

print("Creando tablas en la base de datos...")
Base.metadata.create_all(bind=ENGINE)
print("✅ Tablas creadas exitosamente.")