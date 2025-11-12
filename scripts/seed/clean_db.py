"""
Script para limpiar todas las tablas antes de ejecutar el seed
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def clean_database():
    """Limpia todas las tablas de datos"""
    db_url = os.getenv("SUPABASE_DB_URL")
    
    conn = psycopg2.connect(db_url)
    conn.set_session(autocommit=False)
    cursor = conn.cursor()
    
    print("=" * 70)
    print("LIMPIANDO BASE DE DATOS")
    print("=" * 70)
    print()
    
    try:
        print("🗑️  Eliminando datos en orden correcto...")
        
        # Orden inverso de dependencias
        tables = [
            'disponibilidad',
            'publicacion',
            'consulta',
            'paciente',
            'solicitante',
            'matricula',
            'profesional_especialidad',
            'profesional',
            'usuario',
            'direccion',
            'barrio',
            'departamento',
            'provincia',
            'relacion_solicitante',
            'especialidad',
        ]
        
        for table in tables:
            cursor.execute(f"DELETE FROM athome.{table}")
            count = cursor.rowcount
            print(f"  ✓ {table:<30} {count:>5} registros eliminados")
        
        conn.commit()
        print()
        print("✅ Base de datos limpiada exitosamente")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        cursor.close()
        conn.close()
    
    print("=" * 70)

if __name__ == "__main__":
    clean_database()
