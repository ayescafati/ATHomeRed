"""
Script para cargar especialidades iniciales de ATHomeRed

Especialidades del dominio:
- Acompañamiento Terapéutico
- Enfermería
- Geriatría
- Salud Mental
- Discapacidad
- Cuidados Paliativos
"""

from decimal import Decimal

from app.infra.persistence.database import SessionLocal
from app.infra.persistence.servicios import EspecialidadORM


def seed_especialidades_athomered():
    """Carga las especialidades principales de ATHomeRed"""

    db = SessionLocal()

    especialidades_data = [
        {
            "nombre": "Acompañamiento Terapéutico",
            "descripcion": "Acompañamiento terapéutico para personas con discapacidad, adultos mayores, y personas en procesos de recuperación. Incluye contención emocional, seguimiento de tratamientos y apoyo en actividades diarias.",
            "tarifa": Decimal("3500.00"),
        },
        {
            "nombre": "Enfermería",
            "descripcion": "Cuidados de enfermería profesional a domicilio. Administración de medicamentos, curaciones, control de signos vitales, cuidados post-operatorios y toma de muestras.",
            "tarifa": Decimal("4000.00"),
        },
        {
            "nombre": "Geriatría",
            "descripcion": "Atención especializada para adultos mayores. Cuidados geriátricos, prevención de caídas, manejo de enfermedades crónicas y apoyo en movilidad.",
            "tarifa": Decimal("3800.00"),
        },
        {
            "nombre": "Salud Mental",
            "descripcion": "Acompañamiento en procesos de salud mental. Incluye acompañamiento en crisis, seguimiento de tratamiento psiquiátrico, apoyo en terapias y contención familiar.",
            "tarifa": Decimal("3700.00"),
        },
        {
            "nombre": "Discapacidad",
            "descripcion": "Apoyo y acompañamiento para personas con discapacidad. Integración social, apoyo en rehabilitación, actividades recreativas y estimulación.",
            "tarifa": Decimal("3600.00"),
        },
        {
            "nombre": "Cuidados Paliativos",
            "descripcion": "Cuidado integral para pacientes con enfermedades terminales. Control de síntomas, apoyo emocional, acompañamiento familiar y confort del paciente.",
            "tarifa": Decimal("4500.00"),
        },
        {
            "nombre": "Rehabilitación",
            "descripcion": "Apoyo en procesos de rehabilitación física y cognitiva. Acompañamiento en ejercicios, estimulación cognitiva y seguimiento de evolución.",
            "tarifa": Decimal("3900.00"),
        },
        {
            "nombre": "Cuidados Post-Quirúrgicos",
            "descripcion": "Atención especializada en el periodo post-operatorio. Curaciones, control de evolución, administración de medicamentos y prevención de complicaciones.",
            "tarifa": Decimal("4200.00"),
        },
    ]

    try:
        print("=" * 70)
        print("CARGANDO ESPECIALIDADES DE ATHOMERED")
        print("=" * 70)

        for idx, esp_data in enumerate(especialidades_data, 1):
            existente = (
                db.query(EspecialidadORM)
                .filter(EspecialidadORM.nombre == esp_data["nombre"])
                .first()
            )

            if existente:
                print(
                    f"{idx}. [EXISTE] '{esp_data['nombre']}' ya existe (ID: {existente.id_especialidad})"
                )
            else:
                especialidad = EspecialidadORM(
                    nombre=esp_data["nombre"],
                    descripcion=esp_data["descripcion"],
                    tarifa=esp_data["tarifa"],
                )
                db.add(especialidad)
                db.flush()
                print(
                    f"{idx}. [OK] '{esp_data['nombre']}' creada (ID: {especialidad.id_especialidad}, Tarifa: ${esp_data['tarifa']})"
                )

        db.commit()

        print("\n" + "=" * 70)
        print("CARGA COMPLETADA EXITOSAMENTE")
        print("=" * 70)

        total = db.query(EspecialidadORM).count()
        print(f"\nTotal de especialidades en el sistema: {total}")

        print("\nEspecialidades disponibles:")
        especialidades = (
            db.query(EspecialidadORM).order_by(EspecialidadORM.nombre).all()
        )
        for esp in especialidades:
            print(f"  [{esp.id_especialidad}] {esp.nombre} - ${esp.tarifa}")

    except Exception as e:
        print(f"[ERROR] Error durante la carga: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("\nATHomeRed - Seed de Especialidades\n")
    seed_especialidades_athomered()
    print("\nProceso finalizado\n")
