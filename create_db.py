# create_db.py (puede estar en la raíz del proyecto)
from app.infra.persistence.database import ENGINE
from app.infra.persistence.models import *

print("Creando tablas en la base de datos...")
Base.metadata.create_all(bind=ENGINE)
print("✅ Tablas creadas exitosamente.")