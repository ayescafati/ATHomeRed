"""
Agregar direcciones a profesionales que no tienen
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.infra.persistence.database import SessionLocal
from sqlalchemy import text
from uuid import uuid4
import random

session = SessionLocal()

print("=" * 70)
print("AGREGAR DIRECCIONES A PROFESIONALES")
print("=" * 70)

# Obtener barrio default (Centro, Capital, Córdoba)
print("\n1. Buscando barrio default...")
barrio = session.execute(text("""
    SELECT b.id, b.nombre, d.nombre as depto, p.nombre as prov
    FROM athome.barrio b
    JOIN athome.departamento d ON b.departamento_id = d.id
    JOIN athome.provincia p ON d.provincia_id = p.id
    WHERE b.nombre = 'Centro' AND d.nombre = 'Capital'
    LIMIT 1
""")).fetchone()

if not barrio:
    print("❌ No se encontró barrio 'Centro' en Capital")
    print("   Ejecutar seed_completo.py primero")
    session.close()
    exit(1)

barrio_id = barrio[0]
print(f"✅ Usando: {barrio[1]}, {barrio[2]}, {barrio[3]}")

# Obtener profesionales sin dirección
print("\n2. Buscando profesionales sin direccion_id...")
profs = session.execute(text("""
    SELECT p.id, u.nombre, u.apellido
    FROM athome.profesional p
    JOIN athome.usuario u ON p.usuario_id = u.id
    WHERE p.direccion_id IS NULL
    ORDER BY u.nombre
""")).fetchall()

if not profs:
    print("✅ Todos los profesionales ya tienen dirección")
    session.close()
    exit(0)

print(f"   Encontrados: {len(profs)} profesionales sin dirección")

# Calles para asignar (nombres realistas de Córdoba)
CALLES = [
    "San Jerónimo", "Obispo Trejo", "9 de Julio", "27 de Abril",
    "Belgrano", "Colón", "Caseros", "Dean Funes", "Independencia",
    "Vélez Sarsfield", "Humberto Primo", "Rivadavia"
]

print("\n3. Creando direcciones...")
for idx, prof in enumerate(profs, 1):
    prof_id, nombre, apellido = prof
    
    # Generar datos realistas
    calle = random.choice(CALLES)
    numero = random.randint(100, 9999)
    
    # Crear dirección
    dir_id = str(uuid4())
    session.execute(text("""
        INSERT INTO athome.direccion (id, calle, numero, barrio_id)
        VALUES (:id, :calle, :num, :barrio)
    """), {
        "id": dir_id,
        "calle": calle,
        "num": numero,
        "barrio": barrio_id
    })
    
    # Actualizar profesional
    session.execute(text("""
        UPDATE athome.profesional SET direccion_id = :dir WHERE id = :pid
    """), {"dir": dir_id, "pid": prof_id})
    
    print(f"   {idx}. {nombre} {apellido:20s} → {calle} {numero}")

session.commit()

# Verificar
print("\n4. Verificando...")
result = session.execute(text("""
    SELECT 
        COUNT(*) as total,
        COUNT(direccion_id) as con_direccion
    FROM athome.profesional
""")).fetchone()

print(f"   Total: {result[0]}")
print(f"   Con dirección: {result[1]}")
print(f"   Sin dirección: {result[0] - result[1]}")

session.close()

print("\n" + "=" * 70)
print("✅ DIRECCIONES AGREGADAS EXITOSAMENTE")
print("=" * 70)
print("\nAhora todos los profesionales tienen ubicación completa:")
print("  - provincia, departamento, barrio, calle, numero")
print("  - Se pueden hacer búsquedas geográficas")
print("  - profesional.ubicacion ya NO estará vacío")
