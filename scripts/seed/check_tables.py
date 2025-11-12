"""Script para verificar el estado de las tablas"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.infra.persistence.database import SessionLocal
from sqlalchemy import text

def check_tables():
    session = SessionLocal()
    
    print("\n" + "=" * 60)
    print("📊 ESTADO DE LAS TABLAS")
    print("=" * 60 + "\n")
    
    tables = [
        'usuario',
        'profesional',
        'solicitante',
        'paciente',
        'especialidad',
        'profesional_especialidad',
        'consulta',
        'disponibilidad',
        'valoracion',
        'estado_consulta',
        'relacion_solicitante',
        'provincia',
        'departamento',
        'barrio',
        'direccion',
        'matricula',
    ]
    
    for table in tables:
        try:
            count = session.execute(text(f"SELECT COUNT(*) FROM athome.{table}")).scalar()
            status = "✓" if count > 0 else "✗"
            print(f"{status} {table:30} {count:3} registros")
        except Exception as e:
            print(f"✗ {table:30} ERROR: {str(e)[:40]}")
    
    session.close()
    print("\n" + "=" * 60 + "\n")

if __name__ == "__main__":
    check_tables()
