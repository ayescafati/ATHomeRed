"""
Ejemplo de uso del CatalogoRepository

Demuestra cómo:
- Listar especialidades
- Crear una nueva especialidad
- Crear publicaciones para profesionales
- Obtener tarifas
"""

from app.infra.persistence.database import SessionLocal
from app.infra.repositories.catalogo_repository import CatalogoRepository


def ejemplo_uso_catalogo():
    """Ejemplos de uso del repositorio de catálogo"""

    db = SessionLocal()
    try:
        repo = CatalogoRepository(db)

        print("=" * 60)
        print("EJEMPLOS DE USO: CatalogoRepository")
        print("=" * 60)

        print("\n1. Listando especialidades disponibles:")
        especialidades = repo.listar_especialidades()
        for esp in especialidades:
            print(f"   - [{esp.id}] {esp.nombre}")

        print("\n2. Buscando especialidades de ATHomeRed:")

        acomp_terap = repo.obtener_especialidad_por_nombre(
            "Acompañamiento Terapéutico"
        )
        if acomp_terap:
            print(
                f"   Encontrada: {acomp_terap.nombre} (ID: {acomp_terap.id})"
            )
            tarifa = repo.obtener_tarifa_especialidad(acomp_terap.id)
            print(f"   Tarifa base: ${tarifa}")

        enfermeria = repo.obtener_especialidad_por_nombre("Enfermería")
        if enfermeria:
            print(f"   Encontrada: {enfermeria.nombre} (ID: {enfermeria.id})")
            tarifa = repo.obtener_tarifa_especialidad(enfermeria.id)
            print(f"   Tarifa base: ${tarifa}")

        print("\n4. Ejemplo de consulta de publicaciones:")
        print("   repo.listar_publicaciones_por_profesional(profesional_id)")
        print("   → Retorna lista de publicaciones del profesional")

        print("\n" + "=" * 60)
        print("FIN DE EJEMPLOS")
        print("=" * 60)

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    ejemplo_uso_catalogo()
