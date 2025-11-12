"""
Ejemplo de uso del CatalogoRepository

Demuestra cómo:
- Listar especialidades
- Crear una nueva especialidad
- Crear publicaciones para profesionales
- Obtener tarifas
"""

from decimal import Decimal
from datetime import date
from uuid import UUID

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

        # 1. Listar todas las especialidades
        print("\n1. Listando especialidades disponibles:")
        especialidades = repo.listar_especialidades()
        for esp in especialidades:
            print(f"   - [{esp.id}] {esp.nombre}")

        # 2. Buscar especialidad por nombre
        print("\n2. Buscando especialidades de ATHomeRed:")

        # Buscar Acompañamiento Terapéutico
        acomp_terap = repo.obtener_especialidad_por_nombre(
            "Acompañamiento Terapéutico"
        )
        if acomp_terap:
            print(
                f"   Encontrada: {acomp_terap.nombre} (ID: {acomp_terap.id})"
            )
            tarifa = repo.obtener_tarifa_especialidad(acomp_terap.id)
            print(f"   Tarifa base: ${tarifa}")

        # Buscar Enfermería
        enfermeria = repo.obtener_especialidad_por_nombre("Enfermería")
        if enfermeria:
            print(f"   Encontrada: {enfermeria.nombre} (ID: {enfermeria.id})")
            tarifa = repo.obtener_tarifa_especialidad(enfermeria.id)
            print(f"   Tarifa base: ${tarifa}")

        # 3. Crear nueva especialidad (comentado para no duplicar)
        # print("\n3. Creando nueva especialidad:")
        # try:
        #     # Ejemplo: Agregar especialidad en cuidados paliativos
        #     nueva = repo.crear_especialidad(
        #         nombre="Cuidados Paliativos",
        #         descripcion="Cuidado integral para pacientes con enfermedades terminales",
        #         tarifa=Decimal("4500.00")
        #     )
        #     print(f"   Creada: {nueva.nombre} (ID: {nueva.id})")
        #     db.commit()
        # except ValueError as e:
        #     print(f"   Error: {e}")
        #     db.rollback()

        # 4. Listar publicaciones de un profesional
        # (Necesitas un UUID válido de un profesional existente)
        print("\n4. Ejemplo de consulta de publicaciones:")
        print("   repo.listar_publicaciones_por_profesional(profesional_id)")
        print("   → Retorna lista de publicaciones del profesional")

        # 5. Crear publicación (ejemplo comentado)
        # print("\n5. Crear publicación para profesional:")
        # try:
        #     profesional_id = UUID("...") # UUID del profesional
        #     publicacion = repo.crear_publicacion(
        #         profesional_id=profesional_id,
        #         especialidad_id=1,
        #         titulo="Acompañamiento terapéutico a domicilio",
        #         descripcion="Atención personalizada para adultos mayores y personas con discapacidad. Experiencia en contención emocional y seguimiento de tratamientos.",
        #         fecha_publicacion=date.today()
        #     )
        #     print(f"   Creada publicación: {publicacion.titulo}")
        #     db.commit()
        # except ValueError as e:
        #     print(f"   Error: {e}")
        #     db.rollback()

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
