"""
Script de demostración: crear datos de prueba sin circularidades
Orden: CATÁLOGOS → USUARIO → SOLICITANTE/PROFESIONAL → PACIENTE → DISPONIBILIDAD → CITAS
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text, insert
from sqlalchemy.orm import Session
from app.infra.persistence.database import ENGINE
from uuid import uuid4
from datetime import date, time


def demo_data():
    """Crea datos de demostración en orden correcto"""

    with Session(ENGINE) as session:
        print("\n" + "=" * 70)
        print("🌱 CREANDO DATOS DE DEMOSTRACIÓN (SIN CIRCULARIDADES)")
        print("=" * 70)

        # 1️⃣ RELACIONES (Catálogo)
        print("\n[1/8] Creando catálogo de relaciones...")
        try:
            session.execute(
                text(
                    """
                INSERT INTO athome.relacion_solicitante (nombre) 
                VALUES ('Yo mismo'), ('Madre'), ('Padre'), ('Tutor/a')
                ON CONFLICT DO NOTHING
            """
                )
            )
            session.commit()
            print("  ✅ Relaciones creadas")
        except Exception as e:
            print(f"  ℹ️ Relaciones ya existen: {e}")
            session.rollback()

        # 2️⃣ ESTADO CONSULTA (Catálogo)
        print("\n[2/8] Creando estados de consulta...")
        try:
            session.execute(
                text(
                    """
                INSERT INTO athome.estado_consulta (codigo, descripcion)
                VALUES 
                  ('pendiente', 'Pendiente de confirmación'),
                  ('confirmada', 'Confirmada'),
                  ('cancelada', 'Cancelada'),
                  ('completada', 'Completada')
                ON CONFLICT (codigo) DO NOTHING
            """
                )
            )
            session.commit()
            print("  ✅ Estados creados")
        except Exception as e:
            print(f"  ℹ️ Estados ya existen: {e}")
            session.rollback()

        # 3️⃣ ESPECIALIDADES (Catálogo)
        print("\n[3/8] Creando especialidades...")
        try:
            session.execute(
                text(
                    """
                INSERT INTO athome.especialidad (nombre, descripcion, tarifa)
                VALUES 
                  ('Acompañante Terapéutico', 'Acompañamiento terapéutico y contención emocional', 1500.00),
                  ('Enfermero', 'Cuidados de enfermería domiciliaria', 2000.00),
                  ('Enfermero Especializado', 'Enfermería especializada (gerontología, pediatría, etc)', 2500.00),
                  ('Acompañante con Formación en Psicología', 'Acompañante con formación psicológica', 1800.00)
                ON CONFLICT (nombre) DO NOTHING
            """
                )
            )
            session.commit()
            print("  ✅ Especialidades creadas")
        except Exception as e:
            print(f"  ℹ️ Especialidades ya existen: {e}")
            session.rollback()

        # 4️⃣ UBICACIONES (Provincia → Departamento → Barrio → Dirección)
        print("\n[4/8] Creando ubicaciones...")

        # Provincia
        prov_id = str(uuid4())
        session.execute(
            text(
                f"""
            INSERT INTO athome.provincia (id, nombre) 
            VALUES ('{prov_id}', 'Córdoba')
            ON CONFLICT (nombre) DO NOTHING
        """
            )
        )
        session.commit()

        # Get provincia
        prov_res = session.execute(
            text(
                """
            SELECT id FROM athome.provincia WHERE nombre = 'Córdoba' LIMIT 1
        """
            )
        )
        prov_id = str(prov_res.scalar())

        # Departamento
        dept_id = str(uuid4())
        session.execute(
            text(
                f"""
            INSERT INTO athome.departamento (id, provincia_id, nombre)
            VALUES ('{dept_id}', '{prov_id}', 'Capital')
            ON CONFLICT (provincia_id, nombre) DO NOTHING
        """
            )
        )
        session.commit()

        # Get departamento
        dept_res = session.execute(
            text(
                f"""
            SELECT id FROM athome.departamento WHERE provincia_id = '{prov_id}' LIMIT 1
        """
            )
        )
        dept_id = str(dept_res.scalar())

        # Barrio
        barrio_id = str(uuid4())
        session.execute(
            text(
                f"""
            INSERT INTO athome.barrio (id, departamento_id, nombre)
            VALUES ('{barrio_id}', '{dept_id}', 'Centro')
            ON CONFLICT (departamento_id, nombre) DO NOTHING
        """
            )
        )
        session.commit()

        # Get barrio
        barrio_res = session.execute(
            text(
                f"""
            SELECT id FROM athome.barrio WHERE departamento_id = '{dept_id}' LIMIT 1
        """
            )
        )
        barrio_id = str(barrio_res.scalar())

        # Direcciones
        dir1_id = str(uuid4())
        dir2_id = str(uuid4())
        session.execute(
            text(
                f"""
            INSERT INTO athome.direccion (id, barrio_id, calle, numero)
            VALUES 
              ('{dir1_id}', '{barrio_id}', 'Av. Hipólito Yrigoyen', 123),
              ('{dir2_id}', '{barrio_id}', 'Independencia', 456)
            ON CONFLICT DO NOTHING
        """
            )
        )
        session.commit()
        print("  ✅ Ubicaciones creadas")

        # 5️⃣ USUARIO SOLICITANTE
        print("\n[5/8] Creando usuario solicitante...")
        user_sol_id = str(uuid4())
        session.execute(
            text(
                f"""
            INSERT INTO athome.usuario (id, nombre, apellido, email, es_solicitante, es_profesional, 
                                        password_hash, intentos_fallidos, activo, verificado)
            VALUES ('{user_sol_id}', 'Carlos', 'Pérez', 'carlos@demo.com', true, false, 
                    'hashed_pwd_123', 0, true, true)
            ON CONFLICT (email) DO NOTHING
        """
            )
        )
        session.commit()

        # Get usuario
        user_res = session.execute(
            text(
                """
            SELECT id FROM athome.usuario WHERE email = 'carlos@demo.com' LIMIT 1
        """
            )
        )
        user_sol_id = str(user_res.scalar())
        print(f"  ✅ Usuario solicitante: {user_sol_id}")

        # SOLICITANTE
        sol_id = str(uuid4())
        session.execute(
            text(
                f"""
            INSERT INTO athome.solicitante (id, usuario_id, direccion_id, activo)
            VALUES ('{sol_id}', '{user_sol_id}', '{dir1_id}', true)
            ON CONFLICT DO NOTHING
        """
            )
        )
        session.commit()
        print(f"  ✅ Solicitante creado: {sol_id}")

        # 6️⃣ PACIENTE
        print("\n[6/8] Creando paciente...")
        pac_id = str(uuid4())

        # Get relacion "Yo mismo"
        rel_res = session.execute(
            text(
                """
            SELECT id FROM athome.relacion_solicitante WHERE nombre = 'Yo mismo' LIMIT 1
        """
            )
        )
        rel_id = rel_res.scalar()

        session.execute(
            text(
                f"""
            INSERT INTO athome.paciente (id, nombre, apellido, fecha_nacimiento, notas, 
                                        direccion_id, solicitante_id, relacion_id)
            VALUES ('{pac_id}', 'Carlos', 'Pérez', '1990-05-15', 'Paciente demo', 
                    '{dir1_id}', '{sol_id}', {rel_id})
            ON CONFLICT DO NOTHING
        """
            )
        )
        session.commit()
        print(f"  ✅ Paciente creado: {pac_id}")

        # 7️⃣ USUARIO PROFESIONAL
        print("\n[7/8] Creando usuario profesional...")
        user_prof_id = str(uuid4())
        session.execute(
            text(
                f"""
            INSERT INTO athome.usuario (id, nombre, apellido, email, es_solicitante, es_profesional,
                                        password_hash, intentos_fallidos, activo, verificado)
            VALUES ('{user_prof_id}', 'Juan', 'García', 'juan@demo.com', false, true,
                    'hashed_pwd_456', 0, true, true)
            ON CONFLICT (email) DO NOTHING
        """
            )
        )
        session.commit()

        # Get usuario prof
        user_prof_res = session.execute(
            text(
                """
            SELECT id FROM athome.usuario WHERE email = 'juan@demo.com' LIMIT 1
        """
            )
        )
        user_prof_id = str(user_prof_res.scalar())

        # PROFESIONAL
        prof_id = str(uuid4())
        session.execute(
            text(
                f"""
            INSERT INTO athome.profesional (id, usuario_id, direccion_id, activo, verificado, matricula)
            VALUES ('{prof_id}', '{user_prof_id}', '{dir2_id}', true, true, 'MAT-2024-001')
            ON CONFLICT DO NOTHING
        """
            )
        )
        session.commit()
        print(f"  ✅ Profesional creado: {prof_id}")

        # 8️⃣ DISPONIBILIDAD
        print("\n[8/8] Creando disponibilidades...")
        dias = ["lunes", "martes", "miércoles", "jueves", "viernes"]
        for dia in dias:
            disp_id = str(uuid4())
            session.execute(
                text(
                    f"""
                INSERT INTO athome.disponibilidad (id, profesional_id, dias_semana, hora_inicio, hora_fin)
                VALUES ('{disp_id}', '{prof_id}', '{dia}', '08:00:00', '18:00:00')
                ON CONFLICT DO NOTHING
            """
                )
            )
        session.commit()
        print(f"  ✅ Disponibilidades L-V 8:00-18:00")

        # 📊 RESUMEN
        print("\n" + "=" * 70)
        print("✅ DATOS DE DEMOSTRACIÓN CREADOS EXITOSAMENTE")
        print("=" * 70)
        print(
            "\n📌 ATHOME - Plataforma de Acompañantes Terapéuticos y Enfermeros"
        )
        print(
            "   Especialidades: Acompañante Terapéutico, Enfermero, Enfermero Especializado"
        )
        print(f"\n🔑 IDs PARA SWAGGER:")
        print(f"  • Paciente ID:      {pac_id}")
        print(f"  • Acompañante/Enfermero ID:   {prof_id}")
        print(f"  • Solicitante ID:   {sol_id}")
        print(f"  • Usuario Sol. ID:  {user_sol_id}")
        print(f"  • Usuario Prof. ID: {user_prof_id}")
        print(f"  • Dirección 1 ID:   {dir1_id}")
        print("\n💡 Próximos pasos:")
        print("  1. Abre http://localhost:8000/docs")
        print("  2. Usa los IDs de arriba en los requests")
        print("  3. Crea consultas entre paciente y acompañante/enfermero")
        print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        demo_data()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
