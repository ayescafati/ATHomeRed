"""
Script para ejecutar el seed SQL completo usando SQLAlchemy.
"""

from app.infra.persistence.database import SessionLocal
from sqlalchemy import text
import os


def ejecutar_seed():
    s = SessionLocal()

    print("=" * 80)
    print("EJECUTANDO SEED COMPLETO")
    print("=" * 80)

    # Leer archivo SQL
    seed_file = os.path.join(
        os.path.dirname(__file__), "..", "seed", "seed_completo_uuid.sql"
    )

    print(f"\n📄 Leyendo archivo: {seed_file}")

    with open(seed_file, "r", encoding="utf-8") as f:
        sql_content = f.read()

    try:
        print("\n🚀 Ejecutando seed...")
        s.execute(text(sql_content))
        s.commit()

        print("\n✅ Seed ejecutado correctamente")

        # Verificación
        print("\n📊 Verificación de datos insertados:")

        queries = [
            ("Provincias", "SELECT COUNT(*) FROM athome.provincia"),
            ("Departamentos", "SELECT COUNT(*) FROM athome.departamento"),
            ("Barrios", "SELECT COUNT(*) FROM athome.barrio"),
            ("Direcciones", "SELECT COUNT(*) FROM athome.direccion"),
            ("Especialidades", "SELECT COUNT(*) FROM athome.especialidad"),
            ("Relaciones", "SELECT COUNT(*) FROM athome.relacion_solicitante"),
            ("Usuarios", "SELECT COUNT(*) FROM athome.usuario"),
            ("Profesionales", "SELECT COUNT(*) FROM athome.profesional"),
            ("Matrículas", "SELECT COUNT(*) FROM athome.matricula"),
            ("Solicitantes", "SELECT COUNT(*) FROM athome.solicitante"),
            ("Pacientes", "SELECT COUNT(*) FROM athome.paciente"),
        ]

        for nombre, query in queries:
            count = s.execute(text(query)).scalar()
            print(f"   {nombre:20s}: {count:3d}")

        print("\n📈 Distribución por especialidad:")
        result = s.execute(
            text(
                """
            SELECT 
              e.nombre,
              COUNT(p.id) as cantidad
            FROM athome.especialidad e
            LEFT JOIN athome.profesional p ON e.nombre = p.especialidad_nombre
            GROUP BY e.nombre
            ORDER BY cantidad DESC
        """
            )
        ).fetchall()

        for row in result:
            print(f"   {row[0]:50s}: {row[1]:2d} profesionales")

        print("\n" + "=" * 80)
        print("✅ SEED COMPLETADO")
        print("=" * 80)

    except Exception as e:
        s.rollback()
        print(f"\n❌ ERROR: {e}")
        raise
    finally:
        s.close()


if __name__ == "__main__":
    ejecutar_seed()
