"""
Script para ejecutar el seed completo en la base de datos
"""
import os
import sys
from pathlib import Path
import psycopg2
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_database_url():
    """Obtiene la URL de la base de datos"""
    return os.getenv("SUPABASE_DB_URL") or os.getenv("DATABASE_URL")

def run_seed():
    """Ejecuta el archivo seed SQL"""
    # Leer el archivo SQL
    seed_file = Path(__file__).parent / "seed_completo_uuid.sql"
    
    if not seed_file.exists():
        print(f"❌ Error: No se encuentra el archivo {seed_file}")
        sys.exit(1)
    
    print(f"📄 Leyendo seed desde: {seed_file}")
    
    with open(seed_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Conectar a la base de datos
    db_url = get_database_url()
    if not db_url:
        print("❌ Error: No se encontró la URL de la base de datos en el archivo .env")
        print("   Necesitas configurar SUPABASE_DB_URL o DATABASE_URL")
        sys.exit(1)
    
    print(f"🔌 Conectando a la base de datos...")
    
    try:
        # Usar psycopg2 directamente para mejor control de transacciones
        conn = psycopg2.connect(db_url)
        conn.set_session(autocommit=False)  # Manejar transacción manualmente
        cursor = conn.cursor()
        
        print("✅ Conexión establecida")
        print("🚀 Ejecutando seed...")
        
        # Ejecutar el SQL completo (ya tiene BEGIN/COMMIT internos)
        cursor.execute(sql_content)
        
        print("✅ Seed ejecutado exitosamente!")
        
        cursor.close()
        conn.close()
            
    except Exception as e:
        print(f"❌ Error al ejecutar el seed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 60)
    print("EJECUTANDO SEED DE BASE DE DATOS - AtHomeRed")
    print("=" * 60)
    print()
    
    run_seed()
    
    print()
    print("=" * 60)
    print("✨ PROCESO COMPLETADO")
    print("=" * 60)
