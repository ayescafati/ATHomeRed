"""
SEED COMPLETO usando ORM
Genera 100 profesionales y 50 pacientes con coherencia edad-especialidad
"""

import random
from datetime import date, timedelta
from app.infra.persistence.database import SessionLocal
from app.infra.persistence.ubicacion import (
    ProvinciaORM,
    DepartamentoORM,
    BarrioORM,
    DireccionORM,
)
from app.infra.persistence.servicios import EspecialidadORM
from app.infra.persistence.relaciones import RelacionSolicitanteORM
from app.infra.persistence.usuarios import UsuarioORM
from app.infra.persistence.perfiles import ProfesionalORM, SolicitanteORM
from app.infra.persistence.matriculas import MatriculaORM
from app.infra.persistence.paciente import PacienteORM


def seed_completo():
    s = SessionLocal()

    print("=" * 80)
    print("SEED COMPLETO - 100 Profesionales + 50 Pacientes")
    print("=" * 80)

    try:
        # 1. Provincia
        print("\n1️⃣  Creando provincia...")
        prov = ProvinciaORM(nombre="Ciudad Autónoma de Buenos Aires")
        s.add(prov)
        s.flush()

        # 2. Departamentos (Comunas)
        print("2️⃣  Creando comunas...")
        comunas = []
        for i in [1, 4, 8, 9, 10, 11, 12, 13]:
            dep = DepartamentoORM(provincia_id=prov.id, nombre=f"Comuna {i}")
            s.add(dep)
            comunas.append(dep)
        s.flush()

        # 3. Barrios
        print("3️⃣  Creando barrios...")
        barrios_data = [
            (0, ["Retiro", "San Nicolás", "Montserrat"]),
            (1, ["La Boca", "Barracas", "Parque Patricios"]),
            (2, ["Villa Lugano", "Villa Soldati", "Villa Riachuelo"]),
            (3, ["Liniers", "Mataderos", "Parque Avellaneda"]),
            (4, ["Floresta", "Villa Luro", "Monte Castro"]),
            (5, ["Villa Devoto", "Villa del Parque", "Villa Santa Rita"]),
            (6, ["Saavedra", "Villa Urquiza", "Villa Pueyrredón"]),
            (7, ["Belgrano", "Colegiales", "Núñez"]),
        ]

        barrios = []
        for comuna_idx, nombres in barrios_data:
            for nombre in nombres:
                barrio = BarrioORM(
                    departamento_id=comunas[comuna_idx].id, nombre=nombre
                )
                s.add(barrio)
                barrios.append(barrio)
        s.flush()

        # 4. Direcciones (2 por barrio)
        print("4️⃣  Creando direcciones...")
        calles_por_barrio = [
            ["Av. del Libertador", "Reconquista"],
            ["Av. Corrientes", "Maipú"],
            ["Av. de Mayo", "Perú"],
            ["Caminito", "Brandsen"],
            ["Av. Montes de Oca", "Iriarte"],
            ["Av. Caseros", "Uspallata"],
            ["Av. Cruz", "Soldado de la Frontera"],
            ["Mariano Acosta", "Av. Int. Roca"],
            ["Av. Gral. Paz", "Pergamino"],
            ["Ramón Falcón", "Montiel"],
            ["Av. Emilio Castro", "Murguiondo"],
            ["Av. Directorio", "Lacarra"],
            ["Av. Avellaneda", "Bahía Blanca"],
            ["Av. Rivadavia", "Corvalán"],
            ["Álvarez Jonte", "J. V. González"],
            ["Nueva York", "Asunción"],
            ["Cuenca", "Av. Nazca"],
            ["Álvarez Jonte", "Helguera"],
            ["Av. Ricardo Balbín", "Vedia"],
            ["Av. Triunvirato", "Bauness"],
            ["Artigas", "Bolivia"],
            ["Av. Cabildo", "Juramento"],
            ["Av. Federico Lacroze", "Conesa"],
            ["Av. Cabildo", "Crisólogo Larralde"],
        ]

        direcciones = []
        for i, barrio in enumerate(barrios):
            for j, calle in enumerate(calles_por_barrio[i]):
                dir = DireccionORM(
                    barrio_id=barrio.id,
                    calle=calle,
                    numero=str(random.randint(100, 9000)),
                )
                s.add(dir)
                direcciones.append(dir)
        s.flush()

        # 5. Especialidades
        print("5️⃣  Creando especialidades...")
        especialidades = [
            EspecialidadORM(nombre="Acompañamiento Terapéutico General", tarifa=15000),
            EspecialidadORM(
                nombre="Acompañamiento Terapéutico Geriatría", tarifa=15000
            ),
            EspecialidadORM(
                nombre="Acompañamiento Terapéutico (Especialización TEA/TDAH)",
                tarifa=15000,
            ),
            EspecialidadORM(nombre="Enfermería", tarifa=18000),
            EspecialidadORM(nombre="Enfermería Geriátrica", tarifa=18000),
            EspecialidadORM(nombre="Cuidados Paliativos", tarifa=25000),
        ]
        for esp in especialidades:
            s.add(esp)
        s.flush()

        # 6. Relaciones
        print("6️⃣  Creando relaciones...")
        relaciones_data = [
            (35, "Yo mismo"),
            (36, "Madre"),
            (37, "Padre"),
            (38, "Hijo"),
            (39, "Hija"),
            (40, "Hermano"),
            (41, "Hermana"),
            (42, "Esposo"),
            (43, "Esposa"),
            (44, "Abuelo"),
            (45, "Abuela"),
            (46, "Tío"),
            (47, "Tía"),
            (48, "Tutor/a"),
            (49, "Otro familiar"),
        ]
        for id_rel, nombre in relaciones_data:
            s.add(RelacionSolicitanteORM(id=id_rel, nombre=nombre))
        s.flush()

        # 7. 100 Profesionales
        print("\n7️⃣  Creando 100 profesionales...")
        nombres = [
            "Juan",
            "María",
            "Carlos",
            "Ana",
            "Roberto",
            "Laura",
            "Diego",
            "Patricia",
            "Miguel",
            "Gabriela",
            "Fernando",
            "Claudia",
            "Ricardo",
            "Silvia",
            "Jorge",
            "Mónica",
            "Pablo",
            "Sandra",
            "Martín",
            "Liliana",
        ]
        apellidos = [
            "González",
            "Rodríguez",
            "Fernández",
            "López",
            "Martínez",
            "Sánchez",
            "Pérez",
            "García",
            "Romero",
            "Díaz",
            "Torres",
            "Álvarez",
            "Ruiz",
            "Moreno",
            "Jiménez",
            "Muñoz",
            "Castillo",
            "Castro",
            "Ortiz",
            "Silva",
        ]

        especialidades_dist = (
            [especialidades[0]] * 30
            + [especialidades[1]] * 15  # 30 AT General
            + [especialidades[2]] * 10  # 15 AT Geriatría
            + [especialidades[3]] * 20  # 10 AT TEA/TDAH
            + [especialidades[4]] * 15  # 20 Enfermería
            + [especialidades[5]]  # 15 Enfermería Geriátrica
            * 10  # 10 Cuidados Paliativos
        )

        profesionales = []
        for i in range(100):
            usuario = UsuarioORM(
                nombre=nombres[i % len(nombres)],
                apellido=apellidos[i % len(apellidos)],
                email=f"profesional{i+1}@athomered.com",
                telefono=f"11{5000+i:08d}",
                password_hash="$2b$12$LQv3c1yqBwWFcZquKMjJ3eH7P7KbT7J7J7J7J7J7J7J7J7J7J7J7J7",
            )
            s.add(usuario)
            s.flush()

            profesional = ProfesionalORM(
                usuario_id=usuario.id,
                especialidad_nombre=especialidades_dist[i].nombre,
                direccion_id=random.choice(direcciones).id,
                biografia=f"Profesional con amplia experiencia en {especialidades_dist[i].nombre}.",
                anios_experiencia=(i % 25) + 1,
            )
            s.add(profesional)
            s.flush()

            # Matrícula
            provincia_mat = (
                "Ciudad Autónoma de Buenos Aires" if i % 2 == 0 else "Buenos Aires"
            )
            prefijo_loc = "CABA" if i % 2 == 0 else "PBA"
            prefijo_tipo = (
                "AT" if "Acompañamiento" in especialidades_dist[i].nombre else "EF"
            )
            nro = f"{prefijo_loc}-{prefijo_tipo}-{100000+i:06d}"

            matricula = MatriculaORM(
                profesional_id=profesional.id,
                provincia_nombre=provincia_mat,
                nro_matricula=nro,
            )
            s.add(matricula)
            profesionales.append(profesional)

            if (i + 1) % 10 == 0:
                print(f"   Creados {i+1}/100 profesionales...")

        s.flush()
        print("   ✅ 100 profesionales creados")

        # 8. 50 Pacientes
        print("\n8️⃣  Creando 50 pacientes...")
        nombres_ninos = [
            "Mateo",
            "Sofía",
            "Benjamín",
            "Martina",
            "Lucas",
            "Emma",
            "Thiago",
            "Valentina",
            "Santino",
            "Isabella",
        ]
        nombres_adultos = [
            "Carlos",
            "María",
            "Roberto",
            "Ana",
            "Jorge",
            "Laura",
            "Fernando",
            "Patricia",
            "Diego",
            "Claudia",
        ]
        nombres_mayores = [
            "Alberto",
            "Rosa",
            "Héctor",
            "Elsa",
            "Raúl",
            "Mirta",
            "Oscar",
            "Nora",
            "Rubén",
            "Lidia",
        ]

        for i in range(50):
            # Determinar especialidad random
            prof_random = random.choice(profesionales)
            esp_nombre = prof_random.especialidad_nombre

            # Asignar edad coherente
            if esp_nombre == "Acompañamiento Terapéutico (Especialización TEA/TDAH)":
                edad = random.randint(5, 17)
                nombre_paciente = random.choice(nombres_ninos)
                relacion_id = random.choice([36, 37, 48])  # Madre, Padre, Tutor
            elif esp_nombre in [
                "Acompañamiento Terapéutico Geriatría",
                "Enfermería Geriátrica",
                "Cuidados Paliativos",
            ]:
                edad = random.randint(65, 90)
                nombre_paciente = random.choice(nombres_mayores)
                relacion_id = random.choice(
                    [35, 38, 39, 42, 43]
                )  # Yo mismo, Hijo, Hija, Esposo/a
            else:
                edad = random.randint(25, 70)
                nombre_paciente = random.choice(nombres_adultos)
                relacion_id = random.choice([35, 36, 37, 40, 41, 42, 43, 49])

            fecha_nac = date.today() - timedelta(days=edad * 365)

            # Crear usuario solicitante
            usuario_sol = UsuarioORM(
                nombre=f"Solicitante{i+1}",
                apellido=apellidos[i % len(apellidos)],
                email=f"solicitante{i+1}@athomered.com",
                telefono=f"11{6000+i:08d}",
                password_hash="$2b$12$LQv3c1yqBwWFcZquKMjJ3eH7P7KbT7J7J7J7J7J7J7J7J7J7J7J7J7",
            )
            s.add(usuario_sol)
            s.flush()

            solicitante = SolicitanteORM(
                usuario_id=usuario_sol.id, direccion_id=random.choice(direcciones).id
            )
            s.add(solicitante)
            s.flush()

            paciente = PacienteORM(
                nombre=nombre_paciente,
                apellido=apellidos[i % len(apellidos)],
                fecha_nacimiento=fecha_nac,
                notas=f"Paciente con {esp_nombre}. Edad: {edad} años.",
                solicitante_id=solicitante.id,
                relacion_id=relacion_id,
            )
            s.add(paciente)

            if (i + 1) % 10 == 0:
                print(f"   Creados {i+1}/50 pacientes...")

        s.commit()
        print("   ✅ 50 pacientes creados")

        print("\n" + "=" * 80)
        print("✅ SEED COMPLETADO")
        print("=" * 80)
        print("\n📊 Totales:")
        print("   Provincias: 1")
        print("   Departamentos: 8")
        print("   Barrios: 24")
        print("   Direcciones: 48")
        print("   Especialidades: 6")
        print("   Relaciones: 15")
        print("   Profesionales: 100")
        print("   Solicitantes: 50")
        print("   Pacientes: 50")

    except Exception as e:
        s.rollback()
        print(f"\n❌ ERROR: {e}")
        raise
    finally:
        s.close()


if __name__ == "__main__":
    seed_completo()
