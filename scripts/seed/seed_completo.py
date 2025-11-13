"""
Script de semilla completo para ATHomeRed
Dominio: Enfermería y Acompañamiento Terapéutico

Este script crea datos iniciales realistas para todas las tablas del sistema:
- Estados y catálogos base
- Especialidades
- Ubicaciones (provincias, departamentos, barrios)
- Usuarios (profesionales y solicitantes)
- Pacientes
- Disponibilidades
- Consultas/citas
- Valoraciones

Orden de ejecución respeta dependencias de FK.
"""

import sys
from pathlib import Path
from decimal import Decimal
from datetime import date, time, datetime, timedelta
from uuid import uuid4
import random

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from sqlalchemy.orm import Session
from app.infra.persistence.database import SessionLocal
from app.infra.persistence.usuarios import UsuarioORM
from app.infra.persistence.perfiles import ProfesionalORM, SolicitanteORM
from app.infra.persistence.paciente import PacienteORM
from app.infra.persistence.agenda import DisponibilidadORM, ConsultaORM
from app.infra.persistence.servicios import EspecialidadORM
from app.infra.persistence.valoraciones import ValoracionORM
from app.services.auth_service import AuthService


# ============================================================================
# DATOS BASE
# ============================================================================

PROVINCIAS = [
    {
        "nombre": "Córdoba",
        "departamentos": ["Capital", "Colón", "Punilla", "Santa María"],
    },
    {
        "nombre": "Buenos Aires",
        "departamentos": ["La Plata", "San Isidro", "Vicente López", "Lomas de Zamora"],
    },
    {"nombre": "Santa Fe", "departamentos": ["La Capital", "Rosario", "Castellanos"]},
]

BARRIOS_CORDOBA = [
    "Nueva Córdoba",
    "Centro",
    "Alberdi",
    "General Paz",
    "Güemes",
    "Villa Carlos Paz",
    "Alta Córdoba",
    "Cerro de las Rosas",
    "Arguello",
]

ESPECIALIDADES = [
    {
        "nombre": "Acompañamiento Terapéutico",
        "descripcion": "Acompañamiento terapéutico profesional para personas con discapacidad, adultos mayores y personas en procesos de recuperación. Incluye contención emocional, seguimiento de tratamientos, apoyo en actividades diarias y acompañamiento en salidas.",
        "tarifa": Decimal("3500.00"),
    },
    {
        "nombre": "Enfermería General",
        "descripcion": "Cuidados de enfermería profesional a domicilio. Administración de medicamentos, control de signos vitales, curaciones simples, inyecciones y seguimiento de tratamientos médicos.",
        "tarifa": Decimal("4000.00"),
    },
    {
        "nombre": "Enfermería Especializada",
        "descripcion": "Enfermería con formación especializada en áreas específicas (gerontología, pediatría, cuidados intensivos). Incluye procedimientos complejos, manejo de equipamiento médico y cuidados post-operatorios.",
        "tarifa": Decimal("5500.00"),
    },
    {
        "nombre": "Acompañamiento Geriátrico",
        "descripcion": "Atención especializada para adultos mayores. Cuidados geriátricos, prevención de caídas, estimulación cognitiva, manejo de enfermedades crónicas y apoyo en movilidad.",
        "tarifa": Decimal("3800.00"),
    },
    {
        "nombre": "Acompañamiento en Salud Mental",
        "descripcion": "Acompañamiento terapéutico especializado en salud mental. Contención en crisis, seguimiento de tratamiento psiquiátrico, apoyo en terapias, acompañamiento en actividades y contención familiar.",
        "tarifa": Decimal("4200.00"),
    },
    {
        "nombre": "Apoyo a Personas con Discapacidad",
        "descripcion": "Apoyo integral para personas con discapacidad. Integración social, apoyo en rehabilitación, actividades recreativas, estimulación y asistencia en actividades de la vida diaria.",
        "tarifa": Decimal("3600.00"),
    },
    {
        "nombre": "Cuidados Paliativos",
        "descripcion": "Cuidado integral para pacientes con enfermedades terminales. Control de síntomas, administración de medicación, apoyo emocional, acompañamiento familiar y confort del paciente.",
        "tarifa": Decimal("4800.00"),
    },
    {
        "nombre": "Rehabilitación Domiciliaria",
        "descripcion": "Apoyo en procesos de rehabilitación física y cognitiva a domicilio. Acompañamiento en ejercicios de kinesiología, estimulación cognitiva, seguimiento de evolución y motivación.",
        "tarifa": Decimal("4000.00"),
    },
]

PROFESIONALES = [
    {
        "nombre": "María Laura",
        "apellido": "González",
        "email": "ml.gonzalez@athomered.com",
        "celular": "351-5551001",
        "especialidades": ["Enfermería General", "Enfermería Especializada"],
        "matricula": "ENF-5432",
        "barrio": "Nueva Córdoba",
    },
    {
        "nombre": "Carlos Eduardo",
        "apellido": "Fernández",
        "email": "ce.fernandez@athomered.com",
        "celular": "351-5551002",
        "especialidades": ["Acompañamiento Terapéutico", "Acompañamiento Geriátrico"],
        "matricula": "AT-7891",
        "barrio": "Centro",
    },
    {
        "nombre": "Ana Sofía",
        "apellido": "Martínez",
        "email": "as.martinez@athomered.com",
        "celular": "351-5551003",
        "especialidades": ["Acompañamiento en Salud Mental"],
        "matricula": "PSI-2341",
        "barrio": "Alberdi",
    },
    {
        "nombre": "Roberto Daniel",
        "apellido": "López",
        "email": "rd.lopez@athomered.com",
        "celular": "351-5551004",
        "especialidades": ["Enfermería Especializada", "Cuidados Paliativos"],
        "matricula": "ENF-8765",
        "barrio": "General Paz",
    },
    {
        "nombre": "Gabriela Beatriz",
        "apellido": "Sánchez",
        "email": "gb.sanchez@athomered.com",
        "celular": "351-5551005",
        "especialidades": [
            "Apoyo a Personas con Discapacidad",
            "Rehabilitación Domiciliaria",
        ],
        "matricula": "AT-5567",
        "barrio": "Güemes",
    },
    {
        "nombre": "Jorge Luis",
        "apellido": "Rodríguez",
        "email": "jl.rodriguez@athomered.com",
        "celular": "351-5551006",
        "especialidades": ["Acompañamiento Geriátrico", "Enfermería General"],
        "matricula": "ENF-9012",
        "barrio": "Alta Córdoba",
    },
    {
        "nombre": "Silvia Marcela",
        "apellido": "Díaz",
        "email": "sm.diaz@athomered.com",
        "celular": "351-5551007",
        "especialidades": [
            "Acompañamiento Terapéutico",
            "Acompañamiento en Salud Mental",
        ],
        "matricula": "AT-3456",
        "barrio": "Cerro de las Rosas",
    },
    {
        "nombre": "Fernando Adrián",
        "apellido": "Pérez",
        "email": "fa.perez@athomered.com",
        "celular": "351-5551008",
        "especialidades": ["Enfermería Especializada", "Rehabilitación Domiciliaria"],
        "matricula": "ENF-6789",
        "barrio": "Arguello",
    },
]

SOLICITANTES_PACIENTES = [
    {
        "solicitante": {
            "nombre": "Patricia",
            "apellido": "Romero",
            "email": "patricia.romero@email.com",
            "celular": "351-6661001",
            "barrio": "Nueva Córdoba",
        },
        "pacientes": [
            {
                "nombre": "Patricia",
                "apellido": "Romero",
                "fecha_nacimiento": date(1958, 3, 15),
                "relacion": "Yo mismo",
                "notas": "Requiere acompañamiento post-operatorio. Cirugía de cadera reciente.",
            }
        ],
    },
    {
        "solicitante": {
            "nombre": "Ricardo",
            "apellido": "Molina",
            "email": "ricardo.molina@email.com",
            "celular": "351-6661002",
            "barrio": "Alberdi",
        },
        "pacientes": [
            {
                "nombre": "Elena",
                "apellido": "Castro",
                "fecha_nacimiento": date(1935, 7, 22),
                "relacion": "Madre",
                "notas": "Adulta mayor con diabetes tipo 2. Requiere control de glucemia y administración de insulina.",
            }
        ],
    },
    {
        "solicitante": {
            "nombre": "Claudia",
            "apellido": "Torres",
            "email": "claudia.torres@email.com",
            "celular": "351-6661003",
            "barrio": "Centro",
        },
        "pacientes": [
            {
                "nombre": "Miguel",
                "apellido": "Torres",
                "fecha_nacimiento": date(2005, 11, 8),
                "relacion": "Hijo",
                "notas": "Joven con discapacidad intelectual. Requiere acompañamiento para actividades recreativas y sociales.",
            }
        ],
    },
    {
        "solicitante": {
            "nombre": "Daniel",
            "apellido": "Vargas",
            "email": "daniel.vargas@email.com",
            "celular": "351-6661004",
            "barrio": "General Paz",
        },
        "pacientes": [
            {
                "nombre": "Marta",
                "apellido": "Giménez",
                "fecha_nacimiento": date(1942, 4, 30),
                "relacion": "Tía",
                "notas": "Paciente oncológica en cuidados paliativos. Requiere control del dolor y acompañamiento.",
            }
        ],
    },
    {
        "solicitante": {
            "nombre": "Andrea",
            "apellido": "Benítez",
            "email": "andrea.benitez@email.com",
            "celular": "351-6661005",
            "barrio": "Güemes",
        },
        "pacientes": [
            {
                "nombre": "Andrea",
                "apellido": "Benítez",
                "fecha_nacimiento": date(1985, 9, 12),
                "relacion": "Yo mismo",
                "notas": "Paciente con trastorno bipolar. Requiere acompañamiento terapéutico durante fase de estabilización.",
            }
        ],
    },
    {
        "solicitante": {
            "nombre": "Sergio",
            "apellido": "Acosta",
            "email": "sergio.acosta@email.com",
            "celular": "351-6661006",
            "barrio": "Alta Córdoba",
        },
        "pacientes": [
            {
                "nombre": "Juan Carlos",
                "apellido": "Acosta",
                "fecha_nacimiento": date(1948, 1, 18),
                "relacion": "Padre",
                "notas": "Post-ACV. Requiere rehabilitación física y acompañamiento en ejercicios.",
            }
        ],
    },
]

ESTADOS_CONSULTA = [
    {"codigo": "pendiente", "descripcion": "Pendiente de confirmación"},
    {"codigo": "confirmada", "descripcion": "Confirmada por el profesional"},
    {"codigo": "en_curso", "descripcion": "Consulta en curso"},
    {"codigo": "completada", "descripcion": "Consulta completada"},
    {"codigo": "cancelada", "descripcion": "Cancelada"},
    {"codigo": "reprogramada", "descripcion": "Reprogramada"},
]

RELACIONES = [
    "Yo mismo",
    "Madre",
    "Padre",
    "Hijo",
    "Hija",
    "Hermano",
    "Hermana",
    "Esposo",
    "Esposa",
    "Abuelo",
    "Abuela",
    "Tío",
    "Tía",
    "Tutor/a",
    "Otro familiar",
]


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================


def limpiar_tablas(session: Session):
    """Limpia todas las tablas en orden inverso a las dependencias"""
    print("\n🗑️  Limpiando tablas existentes...")

    tablas = [
        "valoracion",
        "consulta",
        "disponibilidad",
        "paciente",
        "profesional_especialidad",
        "matricula",
        "profesional",
        "solicitante",
        "refresh_token",
        "usuario",
        "barrio",
        "departamento",
        "provincia",
        "direccion",
        "especialidad",
        "estado_consulta",
        "relacion_solicitante",
    ]

    for tabla in tablas:
        try:
            session.execute(text(f"DELETE FROM athome.{tabla}"))
            session.commit()
            print(f"  ✓ Tabla {tabla} limpiada")
        except Exception as e:
            session.rollback()
            print(f"  ⚠ No se pudo limpiar {tabla}: {str(e)[:80]}")

    print("✓ Limpieza completada\n")


def crear_catalogos_base(session: Session):
    """Crea catálogos base: estados y relaciones"""
    print("📋 [1/8] Creando catálogos base...")

    # Estados de consulta
    for estado in ESTADOS_CONSULTA:
        session.execute(
            text(
                "INSERT INTO athome.estado_consulta (codigo, descripcion) "
                "VALUES (:codigo, :descripcion) "
                "ON CONFLICT (codigo) DO NOTHING"
            ),
            estado,
        )
    print(f"  ✓ {len(ESTADOS_CONSULTA)} estados de consulta creados")

    # Relaciones solicitante-paciente
    for relacion in RELACIONES:
        session.execute(
            text(
                "INSERT INTO athome.relacion_solicitante (nombre) "
                "VALUES (:nombre) "
                "ON CONFLICT (nombre) DO NOTHING"
            ),
            {"nombre": relacion},
        )
    print(f"  ✓ {len(RELACIONES)} tipos de relación creados")

    session.commit()


def crear_especialidades(session: Session) -> dict:
    """Crea especialidades y retorna mapeo nombre->id"""
    print("🏥 [2/8] Creando especialidades...")

    especialidades_map = {}

    for esp_data in ESPECIALIDADES:
        # Verificar si existe
        result = session.execute(
            text(
                "SELECT id_especialidad FROM athome.especialidad WHERE nombre = :nombre"
            ),
            {"nombre": esp_data["nombre"]},
        ).fetchone()

        if result:
            especialidades_map[esp_data["nombre"]] = result[0]
            print(f"  ℹ '{esp_data['nombre']}' ya existe")
        else:
            # Crear nueva
            especialidad = EspecialidadORM(
                nombre=esp_data["nombre"],
                descripcion=esp_data["descripcion"],
                tarifa=esp_data["tarifa"],
            )
            session.add(especialidad)
            session.flush()
            especialidades_map[esp_data["nombre"]] = especialidad.id_especialidad
            print(f"  ✓ '{esp_data['nombre']}' creada (${esp_data['tarifa']})")

    session.commit()
    print(f"✓ Total: {len(especialidades_map)} especialidades\n")
    return especialidades_map


def crear_ubicaciones(session: Session) -> dict:
    """Crea provincias, departamentos y barrios. Retorna IDs"""
    print("📍 [3/8] Creando ubicaciones...")

    ubicaciones = {
        "provincias": {},
        "departamentos": {},
        "barrios": {},
    }

    # Provincias y departamentos
    for prov_data in PROVINCIAS:
        prov_id = str(uuid4())
        session.execute(
            text(
                "INSERT INTO athome.provincia (id, nombre) "
                "VALUES (:id, :nombre) "
                "ON CONFLICT (nombre) DO NOTHING"
            ),
            {"id": prov_id, "nombre": prov_data["nombre"]},
        )

        result = session.execute(
            text("SELECT id FROM athome.provincia WHERE nombre = :nombre"),
            {"nombre": prov_data["nombre"]},
        ).fetchone()

        prov_id = str(result[0])
        ubicaciones["provincias"][prov_data["nombre"]] = prov_id

        # Departamentos de esta provincia
        for dept_nombre in prov_data["departamentos"]:
            dept_id = str(uuid4())
            session.execute(
                text(
                    "INSERT INTO athome.departamento (id, nombre, provincia_id) "
                    "VALUES (:id, :nombre, :provincia_id) "
                    "ON CONFLICT (nombre, provincia_id) DO NOTHING"
                ),
                {"id": dept_id, "nombre": dept_nombre, "provincia_id": prov_id},
            )

            result = session.execute(
                text(
                    "SELECT id FROM athome.departamento "
                    "WHERE nombre = :nombre AND provincia_id = :prov_id"
                ),
                {"nombre": dept_nombre, "prov_id": prov_id},
            ).fetchone()

            ubicaciones["departamentos"][dept_nombre] = str(result[0])

    print(f"  ✓ {len(ubicaciones['provincias'])} provincias creadas")
    print(f"  ✓ {len(ubicaciones['departamentos'])} departamentos creados")

    # Barrios (asumimos en Capital, Córdoba)
    dept_capital_id = ubicaciones["departamentos"].get("Capital")
    if dept_capital_id:
        for barrio_nombre in BARRIOS_CORDOBA:
            barrio_id = str(uuid4())
            session.execute(
                text(
                    "INSERT INTO athome.barrio (id, nombre, departamento_id) "
                    "VALUES (:id, :nombre, :dept_id) "
                    "ON CONFLICT (nombre, departamento_id) DO NOTHING"
                ),
                {"id": barrio_id, "nombre": barrio_nombre, "dept_id": dept_capital_id},
            )

            result = session.execute(
                text(
                    "SELECT id FROM athome.barrio "
                    "WHERE nombre = :nombre AND departamento_id = :dept_id"
                ),
                {"nombre": barrio_nombre, "dept_id": dept_capital_id},
            ).fetchone()

            ubicaciones["barrios"][barrio_nombre] = str(result[0])

    print(f"  ✓ {len(ubicaciones['barrios'])} barrios creados")

    session.commit()
    print("✓ Ubicaciones creadas\n")
    return ubicaciones


def crear_profesionales(
    session: Session, especialidades_map: dict, ubicaciones: dict
) -> list:
    """Crea profesionales con sus especialidades"""
    print("👨‍⚕️ [4/8] Creando profesionales...")

    auth_service = AuthService(session)
    profesionales_ids = []

    for idx, prof_data in enumerate(PROFESIONALES, 1):
        # Verificar si el usuario ya existe
        existing = session.execute(
            text("SELECT u.id FROM athome.usuario u WHERE u.email = :email"),
            {"email": prof_data["email"]},
        ).fetchone()

        if existing:
            # Obtener el profesional existente
            prof_result = session.execute(
                text("SELECT p.id FROM athome.profesional p WHERE p.usuario_id = :uid"),
                {"uid": str(existing[0])},
            ).fetchone()

            if prof_result:
                profesionales_ids.append(str(prof_result[0]))
                print(
                    f"  {idx}. ℹ {prof_data['nombre']} {prof_data['apellido']} ya existe"
                )
                continue

        # Crear usuario
        usuario_id = str(uuid4())
        password_hash = auth_service.hash_password("Password123!")

        usuario = UsuarioORM(
            id=usuario_id,
            nombre=prof_data["nombre"],
            apellido=prof_data["apellido"],
            email=prof_data["email"],
            celular=prof_data["celular"],
            es_profesional=True,
            es_solicitante=False,
            password_hash=password_hash,
            activo=True,
            verificado=True,
        )
        session.add(usuario)
        session.flush()

        # Crear perfil profesional
        profesional = ProfesionalORM(
            usuario_id=usuario_id,
            verificado=True,
        )
        session.add(profesional)
        session.flush()

        prof_id = profesional.id

        # Asociar especialidades
        especialidades_ids = [
            especialidades_map[esp_nombre]
            for esp_nombre in prof_data["especialidades"]
            if esp_nombre in especialidades_map
        ]

        for esp_id in especialidades_ids:
            session.execute(
                text(
                    "INSERT INTO athome.profesional_especialidad "
                    "(profesional_id, especialidad_id) "
                    "VALUES (:prof_id, :esp_id)"
                ),
                {"prof_id": prof_id, "esp_id": esp_id},
            )

        # REGLA DE NEGOCIO: Todo profesional debe tener al menos una matrícula
        # Crear matrícula obligatoria
        try:
            provincia_id = ubicaciones.get("provincias", {}).get("Córdoba")
        except Exception:
            provincia_id = None

        if not provincia_id:
            # Si no hay provincia, saltar la creación de matrícula y loggear warning
            print("    ⚠ No se pudo crear matrícula (falta provincia)")
        else:
            nro_matricula = prof_data.get("matricula", f"PROF-{idx:04d}")
            exists = session.execute(
                text(
                    "SELECT id FROM athome.matricula WHERE profesional_id = :pid AND nro_matricula = :nro"
                ),
                {"pid": prof_id, "nro": nro_matricula},
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
                        "nro": nro_matricula,
                        "desde": date.today(),
                        "hasta": date.today().replace(year=date.today().year + 10),
                    },
                )

        profesionales_ids.append(prof_id)

        print(
            f"  {idx}. ✓ {prof_data['nombre']} {prof_data['apellido']} "
            f"({', '.join(prof_data['especialidades'])})"
        )

    session.commit()
    print(f"✓ Total: {len(profesionales_ids)} profesionales creados\n")
    return profesionales_ids


def crear_disponibilidades(session: Session, profesionales_ids: list):
    """Crea disponibilidades para los profesionales"""
    print("📅 [5/8] Creando disponibilidades...")

    horarios = [
        {"dias": "lunes,miércoles,viernes", "inicio": time(9, 0), "fin": time(13, 0)},
        {"dias": "martes,jueves", "inicio": time(14, 0), "fin": time(18, 0)},
        {
            "dias": "lunes,martes,miércoles,jueves,viernes",
            "inicio": time(8, 0),
            "fin": time(12, 0),
        },
        {"dias": "sábado", "inicio": time(9, 0), "fin": time(13, 0)},
    ]

    count = 0
    for prof_id in profesionales_ids:
        # Asignar 2 disponibilidades aleatorias a cada profesional
        for horario in random.sample(horarios, min(2, len(horarios))):
            disponibilidad = DisponibilidadORM(
                id=str(uuid4()),
                profesional_id=prof_id,
                dias_semana_text=horario["dias"],
                hora_inicio=horario["inicio"],
                hora_fin=horario["fin"],
            )
            session.add(disponibilidad)
            count += 1

    session.commit()
    print(f"  ✓ {count} disponibilidades creadas")
    print("✓ Disponibilidades configuradas\n")


def crear_solicitantes_y_pacientes(session: Session, ubicaciones: dict) -> tuple:
    """Crea solicitantes y sus pacientes"""
    print("👤 [6/8] Creando solicitantes y pacientes...")

    auth_service = AuthService(session)
    solicitantes_ids = []
    pacientes_ids = []

    for idx, data in enumerate(SOLICITANTES_PACIENTES, 1):
        sol_data = data["solicitante"]

        # Verificar si el solicitante ya existe
        existing = session.execute(
            text("SELECT u.id FROM athome.usuario u WHERE u.email = :email"),
            {"email": sol_data["email"]},
        ).fetchone()

        if existing:
            # Obtener el solicitante existente
            sol_result = session.execute(
                text("SELECT s.id FROM athome.solicitante s WHERE s.usuario_id = :uid"),
                {"uid": str(existing[0])},
            ).fetchone()

            if sol_result:
                sol_id = str(sol_result[0])
                solicitantes_ids.append(sol_id)

                # Obtener pacientes existentes
                pac_results = session.execute(
                    text("SELECT id FROM athome.paciente WHERE solicitante_id = :sid"),
                    {"sid": sol_id},
                ).fetchall()

                for pac in pac_results:
                    pacientes_ids.append(str(pac[0]))

                print(
                    f"  {idx}. ℹ Solicitante: {sol_data['nombre']} {sol_data['apellido']} ya existe"
                )
                continue

        # Crear usuario solicitante
        usuario_id = str(uuid4())
        password_hash = auth_service.hash_password("Password123!")

        usuario = UsuarioORM(
            id=usuario_id,
            nombre=sol_data["nombre"],
            apellido=sol_data["apellido"],
            email=sol_data["email"],
            celular=sol_data["celular"],
            es_profesional=False,
            es_solicitante=True,
            password_hash=password_hash,
            activo=True,
            verificado=True,
        )
        session.add(usuario)
        session.flush()

        # Crear perfil solicitante
        solicitante = SolicitanteORM(usuario_id=usuario_id)
        session.add(solicitante)
        session.flush()

        sol_id = solicitante.id
        solicitantes_ids.append(sol_id)

        print(f"  {idx}. ✓ Solicitante: {sol_data['nombre']} {sol_data['apellido']}")

        # Crear pacientes asociados
        for pac_data in data["pacientes"]:
            # Obtener ID de relación
            relacion_result = session.execute(
                text(
                    "SELECT id FROM athome.relacion_solicitante WHERE nombre = :nombre"
                ),
                {"nombre": pac_data["relacion"]},
            ).fetchone()

            relacion_id = relacion_result[0] if relacion_result else None

            paciente_id = str(uuid4())
            paciente = PacienteORM(
                id=paciente_id,
                nombre=pac_data["nombre"],
                apellido=pac_data["apellido"],
                fecha_nacimiento=pac_data["fecha_nacimiento"],
                notas=pac_data["notas"],
                solicitante_id=sol_id,
                relacion_id=relacion_id,
            )
            session.add(paciente)
            pacientes_ids.append(paciente_id)

            edad = date.today().year - pac_data["fecha_nacimiento"].year
            print(
                f"    → Paciente: {pac_data['nombre']} {pac_data['apellido']} "
                f"({edad} años) - {pac_data['relacion']}"
            )

    session.commit()
    print(
        f"✓ Total: {len(solicitantes_ids)} solicitantes, {len(pacientes_ids)} pacientes\n"
    )
    return solicitantes_ids, pacientes_ids


def crear_consultas(session: Session, profesionales_ids: list, pacientes_ids: list):
    """Crea consultas de ejemplo"""
    print("📋 [7/8] Creando consultas...")

    estados = ["pendiente", "confirmada", "completada", "cancelada"]
    hoy = date.today()

    # Obtener IDs de estados
    estados_ids = {}
    for estado in estados:
        result = session.execute(
            text("SELECT id FROM athome.estado_consulta WHERE codigo = :codigo"),
            {"codigo": estado},
        ).fetchone()
        if result:
            estados_ids[estado] = result[0]

    consultas_count = 0

    # Crear 15-20 consultas variadas
    for _ in range(20):
        prof_id = random.choice(profesionales_ids)
        pac_id = random.choice(pacientes_ids)

        # Fecha aleatoria (últimos 30 días o próximos 30 días)
        dias_offset = random.randint(-30, 30)
        fecha_consulta = hoy + timedelta(days=dias_offset)

        # Horario aleatorio
        hora_inicio = time(random.randint(8, 16), random.choice([0, 30]))
        hora_fin = time(
            (hora_inicio.hour + random.randint(1, 3)) % 24, hora_inicio.minute
        )

        # Estado según la fecha
        if dias_offset < -7:
            estado = "completada"
        elif dias_offset < 0:
            estado = random.choice(["completada", "cancelada"])
        elif dias_offset < 7:
            estado = random.choice(["pendiente", "confirmada"])
        else:
            estado = "pendiente"

        consulta = ConsultaORM(
            id=str(uuid4()),
            paciente_id=pac_id,
            profesional_id=prof_id,
            fecha=fecha_consulta,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            estado_id=estados_ids.get(estado),
            notas=f"Consulta {estado} - Generada automáticamente",
        )
        session.add(consulta)
        consultas_count += 1

    session.commit()
    print(f"  ✓ {consultas_count} consultas creadas")
    print("✓ Consultas generadas\n")


def crear_valoraciones(session: Session):
    """Crea valoraciones para consultas completadas"""
    print("⭐ [8/8] Creando valoraciones...")

    # Obtener consultas completadas
    consultas_completadas = session.execute(
        text(
            """
            SELECT c.id, c.paciente_id, c.profesional_id
            FROM athome.consulta c
            JOIN athome.estado_consulta e ON c.estado_id = e.id
            WHERE e.codigo = 'completada'
            LIMIT 10
            """
        )
    ).fetchall()

    comentarios = [
        "Excelente atención, muy profesional y cálido trato.",
        "Muy buen servicio, puntual y comprometido con el paciente.",
        "Profesional muy capacitado, explicó todo claramente.",
        "Muy satisfechos con la atención brindada.",
        "Excelente cuidado y seguimiento del tratamiento.",
        "Muy recomendable, trato humano y profesional.",
        "Superó nuestras expectativas, muy buen trabajo.",
    ]

    valoraciones_count = 0

    for consulta in consultas_completadas:
        # Crear valoración con probabilidad del 70%
        if random.random() < 0.7:
            valoracion = ValoracionORM(
                id=str(uuid4()),
                consulta_id=str(consulta[0]),
                paciente_id=str(consulta[1]),
                profesional_id=str(consulta[2]),
                puntuacion=random.randint(4, 5),  # Mayormente positivas
                comentario=random.choice(comentarios),
                fecha_creacion=datetime.now() - timedelta(days=random.randint(1, 30)),
            )
            session.add(valoracion)
            valoraciones_count += 1

    session.commit()
    print(f"  ✓ {valoraciones_count} valoraciones creadas")
    print("✓ Valoraciones completadas\n")


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================


def main(limpiar=False):
    """Ejecuta la semilla completa"""
    print("\n" + "=" * 70)
    print("🌱 SEMILLA COMPLETA - ATHomeRed")
    print("   Enfermería y Acompañamiento Terapéutico")
    print("=" * 70 + "\n")

    session = SessionLocal()

    try:
        # Limpiar si se solicita
        if limpiar:
            limpiar_tablas(session)

        # Ejecutar en orden
        crear_catalogos_base(session)
        especialidades_map = crear_especialidades(session)
        ubicaciones = crear_ubicaciones(session)
        profesionales_ids = crear_profesionales(
            session, especialidades_map, ubicaciones
        )
        crear_disponibilidades(session, profesionales_ids)
        solicitantes_ids, pacientes_ids = crear_solicitantes_y_pacientes(
            session, ubicaciones
        )
        crear_consultas(session, profesionales_ids, pacientes_ids)
        crear_valoraciones(session)

        print("\n" + "=" * 70)
        print("✅ SEMILLA COMPLETADA EXITOSAMENTE")
        print("=" * 70)
        print("\n📊 Resumen de datos creados:")
        print(f"   • Especialidades: {len(especialidades_map)}")
        print(f"   • Profesionales: {len(profesionales_ids)}")
        print(f"   • Solicitantes: {len(solicitantes_ids)}")
        print(f"   • Pacientes: {len(pacientes_ids)}")
        print("\n🔐 Credenciales de prueba:")
        print("   Email: cualquier email de profesional o solicitante")
        print("   Password: Password123!")
        print("\n")

    except Exception as e:
        print(f"\n❌ Error durante la ejecución: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    import sys

    # Si se pasa --limpiar como argumento, limpia las tablas primero
    limpiar = "--limpiar" in sys.argv or "--clean" in sys.argv
    main(limpiar=limpiar)
