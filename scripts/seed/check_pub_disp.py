"""
Script para verificar el estado de publicaciones y disponibilidades
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def check_publicaciones_disponibilidades():
    """Verifica el estado de publicaciones y disponibilidades"""
    db_url = os.getenv("SUPABASE_DB_URL")
    
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    print("=" * 70)
    print("VERIFICACIÓN DE PUBLICACIONES Y DISPONIBILIDADES")
    print("=" * 70)
    print()
    
    # Verificar publicaciones
    print("📢 PUBLICACIONES:")
    print("-" * 70)
    cursor.execute("SELECT COUNT(*) FROM athome.publicacion")
    count_pub = cursor.fetchone()[0]
    print(f"  Total de publicaciones: {count_pub}")
    
    if count_pub > 0:
        cursor.execute("""
            SELECT 
                pub.titulo,
                u.nombre || ' ' || u.apellido as profesional,
                e.nombre as especialidad,
                pub.fecha_publicacion
            FROM athome.publicacion pub
            JOIN athome.profesional p ON pub.profesional_id = p.id
            JOIN athome.usuario u ON p.usuario_id = u.id
            JOIN athome.especialidad e ON pub.especialidad_id = e.id_especialidad
            LIMIT 5
        """)
        print("\n  Ejemplos de publicaciones:")
        for row in cursor.fetchall():
            print(f"    - {row[0]} ({row[1]}, {row[2]}) - {row[3]}")
    else:
        print("  ⚠️  No hay publicaciones en la base de datos")
    
    print()
    print("-" * 70)
    print()
    
    # Verificar disponibilidades
    print("📅 DISPONIBILIDADES:")
    print("-" * 70)
    cursor.execute("SELECT COUNT(*) FROM athome.disponibilidad")
    count_disp = cursor.fetchone()[0]
    print(f"  Total de disponibilidades: {count_disp}")
    
    if count_disp > 0:
        cursor.execute("""
            SELECT 
                u.nombre || ' ' || u.apellido as profesional,
                d.dias_semana,
                d.hora_inicio,
                d.hora_fin
            FROM athome.disponibilidad d
            JOIN athome.profesional p ON d.profesional_id = p.id
            JOIN athome.usuario u ON p.usuario_id = u.id
            LIMIT 5
        """)
        print("\n  Ejemplos de disponibilidades:")
        for row in cursor.fetchall():
            print(f"    - {row[0]}: {row[1]} de {row[2]} a {row[3]}")
    else:
        print("  ⚠️  No hay disponibilidades en la base de datos")
    
    print()
    print("=" * 70)
    
    # Resumen y explicación
    print()
    print("📋 EXPLICACIÓN:")
    print("-" * 70)
    print()
    print("PUBLICACIONES:")
    print("  Las publicaciones son 'anuncios' o 'tarjetas' que los profesionales")
    print("  crean para ofrecer sus servicios en una especialidad específica.")
    print("  Contienen: título, descripción, especialidad, y fecha de publicación.")
    print("  Son como un 'perfil público' del profesional para una especialidad.")
    print()
    print("DISPONIBILIDADES:")
    print("  Las disponibilidades definen los horarios en los que el profesional")
    print("  está disponible para atender consultas.")
    print("  Contienen: días de la semana, hora de inicio y hora de fin.")
    print("  Ejemplo: 'Lunes a Viernes de 9:00 a 17:00'")
    print()
    print("=" * 70)
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_publicaciones_disponibilidades()
