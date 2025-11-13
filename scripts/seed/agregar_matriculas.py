"""
Agregar matrículas para profesionales existentes que no tengan ninguna.
"""

import sys
from pathlib import Path
from uuid import uuid4
from datetime import date, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from app.infra.persistence.database import SessionLocal


def agregar_matriculas():
    session = SessionLocal()
    try:
        print("\n== Agregando matrículas para profesionales sin matrícula ==\n")
        # Obtener provincia (Córdoba) o crear si no existe
        prov = session.execute(
            text("SELECT id FROM athome.provincia WHERE nombre = :n LIMIT 1"),
            {"n": "Córdoba"},
        ).fetchone()
        if not prov:
            prov_id = str(uuid4())
            session.execute(
                text("INSERT INTO athome.provincia (id, nombre) VALUES (:id, :nombre)"),
                {"id": prov_id, "nombre": "Córdoba"},
            )
            session.commit()
            prov = session.execute(
                text("SELECT id FROM athome.provincia WHERE nombre = :n LIMIT 1"),
                {"n": "Córdoba"},
            ).fetchone()
        provincia_id = str(prov[0])

        profs = session.execute(text("SELECT id FROM athome.profesional")).fetchall()
        if not profs:
            print("No hay profesionales en la base de datos.")
            return

        hoy = date.today()
        created = 0
        for idx, p in enumerate(profs, 1):
            pid = str(p[0])
            exists = session.execute(
                text(
                    "SELECT id FROM athome.matricula WHERE profesional_id = :pid LIMIT 1"
                ),
                {"pid": pid},
            ).fetchone()
            if exists:
                continue
            nro = f"AUTO-{idx:04d}"
            session.execute(
                text(
                    "INSERT INTO athome.matricula (id, profesional_id, provincia_id, nro_matricula, vigente_desde, vigente_hasta) "
                    "VALUES (:id, :pid, :prov, :nro, :desde, :hasta)"
                ),
                {
                    "id": str(uuid4()),
                    "pid": pid,
                    "prov": provincia_id,
                    "nro": nro,
                    "desde": hoy,
                    "hasta": hoy + timedelta(days=3650),
                },
            )
            created += 1
        session.commit()
        print(f"Matrículas creadas: {created}")
    finally:
        session.close()


if __name__ == "__main__":
    agregar_matriculas()
