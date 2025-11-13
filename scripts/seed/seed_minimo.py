"""
Script de semilla mínimo para ATHomeRed
Crea solo datos esenciales para pruebas rápidas

Incluye:
- Catálogos base (estados, relaciones)
- 3 especialidades principales
- 2 profesionales
- 2 solicitantes con pacientes
- Algunas consultas básicas
"""

import sys
from pathlib import Path
from decimal import Decimal
from datetime import date, timedelta
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from app.infra.persistence.database import SessionLocal
from app.infra.persistence.usuarios import UsuarioORM
from app.infra.persistence.perfiles import ProfesionalORM, SolicitanteORM
from app.infra.persistence.paciente import PacienteORM
from app.infra.persistence.servicios import EspecialidadORM
from app.services.auth_service import AuthService


def seed_minimo():
    """Carga datos mínimos para testing"""

    session = SessionLocal()
    auth_service = AuthService(session)

    print("\n" + "=" * 70)
    print("🌱 SEMILLA MÍNIMA - ATHomeRed")
    print("=" * 70 + "\n")

    try:
        # 1. Estados de consulta
        print("[1/5] Creando estados...")
        estados = [
            {"codigo": "pendiente", "descripcion": "Pendiente"},
            {"codigo": "confirmada", "descripcion": "Confirmada"},
            {"codigo": "completada", "descripcion": "Completada"},
            {"codigo": "cancelada", "descripcion": "Cancelada"},
        ]
        for estado in estados:
            session.execute(
                text(
                    "INSERT INTO athome.estado_consulta (codigo, descripcion) "
                    "VALUES (:codigo, :descripcion) ON CONFLICT DO NOTHING"
                ),
                estado,
            )
        session.commit()
        print("✓ Estados creados\n")

        # 2. Relaciones
        print("[2/5] Creando relaciones...")
        relaciones = ["Yo mismo", "Madre", "Padre", "Hijo", "Tutor/a"]
        for rel in relaciones:
            session.execute(
                text(
                    "INSERT INTO athome.relacion_solicitante (nombre) "
                    "VALUES (:nombre) ON CONFLICT DO NOTHING"
                ),
                {"nombre": rel},
            )
        session.commit()
        print("✓ Relaciones creadas\n")

        # 3. Especialidades
        print("[3/5] Creando especialidades...")
        especialidades = [
            {
                "nombre": "Enfermería General",
                "descripcion": "Cuidados de enfermería a domicilio",
                "tarifa": Decimal("4000.00"),
            },
            {
                "nombre": "Acompañamiento Terapéutico",
                "descripcion": "Acompañamiento terapéutico profesional",
                "tarifa": Decimal("3500.00"),
            },
            {
                "nombre": "Cuidados Geriátricos",
                "descripcion": "Atención especializada para adultos mayores",
                "tarifa": Decimal("3800.00"),
            },
        ]

        esp_ids = {}
        for esp in especialidades:
            result = session.execute(
                text(
                    "SELECT id_especialidad FROM athome.especialidad WHERE nombre = :nombre"
                ),
                {"nombre": esp["nombre"]},
            ).fetchone()

            if result:
                esp_ids[esp["nombre"]] = result[0]
            else:
                obj = EspecialidadORM(**esp)
                session.add(obj)
                session.flush()
                esp_ids[esp["nombre"]] = obj.id_especialidad

            print(f"  ✓ {esp['nombre']}")

        session.commit()
        print()

        # 4. Profesionales
        print("[4/5] Creando profesionales...")
        profesionales_data = [
            {
                "nombre": "María",
                "apellido": "González",
                "email": "maria.gonzalez@athomered.com",
                "celular": "351-1234567",
                "especialidades": ["Enfermería General"],
            },
            {
                "nombre": "Carlos",
                "apellido": "Fernández",
                "email": "carlos.fernandez@athomered.com",
                "celular": "351-7654321",
                "especialidades": [
                    "Acompañamiento Terapéutico",
                    "Cuidados Geriátricos",
                ],
            },
        ]

        prof_ids = []
        password = "Password123!"

        for prof in profesionales_data:
            user_id = str(uuid4())

            usuario = UsuarioORM(
                id=user_id,
                nombre=prof["nombre"],
                apellido=prof["apellido"],
                email=prof["email"],
                celular=prof["celular"],
                es_profesional=True,
                es_solicitante=False,
                password_hash=auth_service.hash_password(password),
                activo=True,
                verificado=True,
            )
            session.add(usuario)
            session.flush()

            profesional = ProfesionalORM(usuario_id=user_id, verificado=True)
            session.add(profesional)
            session.flush()

            prof_id = profesional.id

            # Asociar especialidades
            for esp_nombre in prof["especialidades"]:
                if esp_nombre in esp_ids:
                    session.execute(
                        text(
                            "INSERT INTO athome.profesional_especialidad "
                            "(profesional_id, especialidad_id) VALUES (:p, :e)"
                        ),
                        {"p": prof_id, "e": esp_ids[esp_nombre]},
                    )

            prof_ids.append(prof_id)
            print(f"  ✓ {prof['nombre']} {prof['apellido']}")

        # Asegurar que existe al menos una provincia (necesaria para matriculas)
        prov_res = session.execute(
            text("SELECT id FROM athome.provincia WHERE nombre = :n LIMIT 1"),
            {"n": "Córdoba"},
        ).fetchone()
        if not prov_res:
            prov_id = str(uuid4())
            session.execute(
                text(
                    "INSERT INTO athome.provincia (id, nombre) VALUES (:id, :nombre) ON CONFLICT DO NOTHING"
                ),
                {"id": prov_id, "nombre": "Córdoba"},
            )
            session.commit()
            prov_res = session.execute(
                text("SELECT id FROM athome.provincia WHERE nombre = :n LIMIT 1"),
                {"n": "Córdoba"},
            ).fetchone()

        provincia_id = str(prov_res[0])

        # Crear matrículas para cada profesional si no existen
        hoy = date.today()
        for idx_m, prof_id in enumerate(prof_ids, 1):
            nro = f"MIN-{idx_m:04d}"
            exists = session.execute(
                text(
                    "SELECT id FROM athome.matricula WHERE profesional_id = :pid AND nro_matricula = :nro"
                ),
                {"pid": prof_id, "nro": nro},
            ).fetchone()
            if not exists:
                session.execute(
                    text(
                        "INSERT INTO athome.matricula (id, profesional_id, provincia_id, nro_matricula, vigente_desde, vigente_hasta) "
                        "VALUES (:id, :pid, :prov, :nro, :desde, :hasta)"
                    ),
                    {
                        "id": str(uuid4()),
                        "pid": prof_id,
                        "prov": provincia_id,
                        "nro": nro,
                        "desde": hoy,
                        "hasta": hoy + timedelta(days=3650),
                    },
                )

        session.commit()
        print()

        # 5. Solicitantes y Pacientes
        print("[5/5] Creando solicitantes y pacientes...")
        solicitantes_data = [
            {
                "nombre": "Ana",
                "apellido": "Martínez",
                "email": "ana.martinez@email.com",
                "celular": "351-9876543",
                "paciente": {
                    "nombre": "Ana",
                    "apellido": "Martínez",
                    "fecha_nacimiento": date(1965, 5, 10),
                    "relacion": "Yo mismo",
                    "notas": "Paciente post-operatorio",
                },
            },
            {
                "nombre": "Roberto",
                "apellido": "López",
                "email": "roberto.lopez@email.com",
                "celular": "351-5554433",
                "paciente": {
                    "nombre": "Elena",
                    "apellido": "Castro",
                    "fecha_nacimiento": date(1940, 3, 15),
                    "relacion": "Madre",
                    "notas": "Adulta mayor con diabetes",
                },
            },
        ]

        for sol in solicitantes_data:
            user_id = str(uuid4())

            usuario = UsuarioORM(
                id=user_id,
                nombre=sol["nombre"],
                apellido=sol["apellido"],
                email=sol["email"],
                celular=sol["celular"],
                es_profesional=False,
                es_solicitante=True,
                password_hash=auth_service.hash_password(password),
                activo=True,
                verificado=True,
            )
            session.add(usuario)
            session.flush()

            solicitante = SolicitanteORM(usuario_id=user_id)
            session.add(solicitante)
            session.flush()

            sol_id = solicitante.id

            # Paciente
            pac = sol["paciente"]
            rel_result = session.execute(
                text("SELECT id FROM athome.relacion_solicitante WHERE nombre = :n"),
                {"n": pac["relacion"]},
            ).fetchone()

            paciente = PacienteORM(
                id=str(uuid4()),
                nombre=pac["nombre"],
                apellido=pac["apellido"],
                fecha_nacimiento=pac["fecha_nacimiento"],
                notas=pac["notas"],
                solicitante_id=sol_id,
                relacion_id=rel_result[0] if rel_result else None,
            )
            session.add(paciente)

            print(f"  ✓ {sol['nombre']} {sol['apellido']} → Paciente: {pac['nombre']}")

        session.commit()

        print("\n" + "=" * 70)
        print("✅ SEMILLA MÍNIMA COMPLETADA")
        print("=" * 70)
        print("\n📊 Datos creados:")
        print("   • 3 Especialidades")
        print("   • 2 Profesionales")
        print("   • 2 Solicitantes con pacientes")
        print("\n🔐 Credenciales:")
        print(f"   Password para todos: {password}")
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_minimo()
