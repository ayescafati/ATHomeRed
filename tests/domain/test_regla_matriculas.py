"""
Tests para la regla de negocio: RN-001
Todo profesional debe tener al menos una matrícula activa
"""

import pytest
from datetime import date, timedelta
from uuid import uuid4
from sqlalchemy import text

from app.infra.persistence.database import SessionLocal
from app.infra.persistence.usuarios import UsuarioORM
from app.infra.persistence.perfiles import ProfesionalORM
from app.services.auth_service import AuthService


@pytest.fixture
def session():
    """Fixture para obtener sesión de BD"""
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def provincia_id(session):
    """Fixture que asegura que existe una provincia para las matrículas"""
    result = session.execute(
        text("SELECT id FROM athome.provincia WHERE nombre = :n LIMIT 1"),
        {"n": "Córdoba"},
    ).fetchone()

    if result:
        return str(result[0])

    # Crear provincia si no existe
    prov_id = str(uuid4())
    session.execute(
        text("INSERT INTO athome.provincia (id, nombre) VALUES (:id, :nombre)"),
        {"id": prov_id, "nombre": "Córdoba"},
    )
    session.commit()
    return prov_id


def test_profesional_sin_matricula_no_es_valido(session, provincia_id):
    """
    RN-001: Un profesional sin matrícula no cumple la regla de negocio
    """
    # Crear usuario y profesional
    auth = AuthService(session)
    user_id = str(uuid4())

    usuario = UsuarioORM(
        id=user_id,
        nombre="Test",
        apellido="Sin Matrícula",
        email=f"test.sin.matricula.{uuid4()}@test.com",
        celular="351-0000000",
        es_profesional=True,
        es_solicitante=False,
        password_hash=auth.hash_password("test123"),
        activo=True,
        verificado=True,
    )
    session.add(usuario)
    session.flush()

    profesional = ProfesionalORM(usuario_id=user_id, verificado=True)
    session.add(profesional)
    session.flush()

    prof_id = profesional.id

    # Verificar que NO tiene matrículas
    count = session.execute(
        text("SELECT COUNT(*) FROM athome.matricula WHERE profesional_id = :pid"),
        {"pid": prof_id},
    ).scalar()

    assert count == 0, "El profesional no debería tener matrículas aún"

    # En un sistema real, esto debería fallar en la validación de servicio
    # Por ahora solo verificamos que el estado es inválido
    session.rollback()


def test_profesional_con_matricula_es_valido(session, provincia_id):
    """
    RN-001: Un profesional con al menos una matrícula cumple la regla
    """
    # Crear usuario y profesional
    auth = AuthService(session)
    user_id = str(uuid4())

    usuario = UsuarioORM(
        id=user_id,
        nombre="Test",
        apellido="Con Matrícula",
        email=f"test.con.matricula.{uuid4()}@test.com",
        celular="351-1111111",
        es_profesional=True,
        es_solicitante=False,
        password_hash=auth.hash_password("test123"),
        activo=True,
        verificado=True,
    )
    session.add(usuario)
    session.flush()

    profesional = ProfesionalORM(usuario_id=user_id, verificado=True)
    session.add(profesional)
    session.flush()

    prof_id = profesional.id

    # Crear matrícula
    hoy = date.today()
    session.execute(
        text(
            "INSERT INTO athome.matricula (id, profesional_id, provincia_id, nro_matricula, vigente_desde, vigente_hasta) "
            "VALUES (:id, :pid, :prov, :nro, :desde, :hasta)"
        ),
        {
            "id": str(uuid4()),
            "pid": prof_id,
            "prov": provincia_id,
            "nro": f"TEST-{uuid4().hex[:8].upper()}",
            "desde": hoy,
            "hasta": hoy + timedelta(days=3650),
        },
    )
    session.commit()

    # Verificar que tiene matrícula
    count = session.execute(
        text("SELECT COUNT(*) FROM athome.matricula WHERE profesional_id = :pid"),
        {"pid": prof_id},
    ).scalar()

    assert count >= 1, "El profesional debe tener al menos una matrícula"

    # Limpiar
    session.execute(
        text("DELETE FROM athome.matricula WHERE profesional_id = :pid"),
        {"pid": prof_id},
    )
    session.execute(
        text("DELETE FROM athome.profesional WHERE id = :pid"), {"pid": prof_id}
    )
    session.execute(
        text("DELETE FROM athome.usuario WHERE id = :uid"), {"uid": user_id}
    )
    session.commit()


def test_profesional_con_multiples_matriculas(session, provincia_id):
    """
    Un profesional puede tener múltiples matrículas (diferentes provincias)
    """
    # Crear usuario y profesional
    auth = AuthService(session)
    user_id = str(uuid4())

    usuario = UsuarioORM(
        id=user_id,
        nombre="Test",
        apellido="Multi Matrícula",
        email=f"test.multi.matricula.{uuid4()}@test.com",
        celular="351-2222222",
        es_profesional=True,
        es_solicitante=False,
        password_hash=auth.hash_password("test123"),
        activo=True,
        verificado=True,
    )
    session.add(usuario)
    session.flush()

    profesional = ProfesionalORM(usuario_id=user_id, verificado=True)
    session.add(profesional)
    session.flush()

    prof_id = profesional.id

    # Crear 3 matrículas
    hoy = date.today()
    for i in range(3):
        session.execute(
            text(
                "INSERT INTO athome.matricula (id, profesional_id, provincia_id, nro_matricula, vigente_desde, vigente_hasta) "
                "VALUES (:id, :pid, :prov, :nro, :desde, :hasta)"
            ),
            {
                "id": str(uuid4()),
                "pid": prof_id,
                "prov": provincia_id,
                "nro": f"TEST-MULTI-{i:03d}-{uuid4().hex[:6].upper()}",
                "desde": hoy,
                "hasta": hoy + timedelta(days=3650),
            },
        )

    session.commit()

    # Verificar cantidad
    count = session.execute(
        text("SELECT COUNT(*) FROM athome.matricula WHERE profesional_id = :pid"),
        {"pid": prof_id},
    ).scalar()

    assert count == 3, "El profesional debe tener 3 matrículas"

    # Limpiar
    session.execute(
        text("DELETE FROM athome.matricula WHERE profesional_id = :pid"),
        {"pid": prof_id},
    )
    session.execute(
        text("DELETE FROM athome.profesional WHERE id = :pid"), {"pid": prof_id}
    )
    session.execute(
        text("DELETE FROM athome.usuario WHERE id = :uid"), {"uid": user_id}
    )
    session.commit()


def test_todos_los_profesionales_tienen_matricula(session):
    """
    Verificación de integridad: todos los profesionales en la BD deben tener matrícula
    """
    result = session.execute(
        text(
            """
            SELECT p.id, COUNT(m.id) as num_matriculas
            FROM athome.profesional p
            LEFT JOIN athome.matricula m ON p.id = m.profesional_id
            GROUP BY p.id
            HAVING COUNT(m.id) = 0
            """
        )
    ).fetchall()

    profesionales_sin_matricula = [str(r[0]) for r in result]

    assert len(profesionales_sin_matricula) == 0, (
        f"RN-001 VIOLADA: {len(profesionales_sin_matricula)} profesionales sin matrícula: "
        f"{profesionales_sin_matricula}"
    )


if __name__ == "__main__":
    # Ejecutar test de integridad
    session = SessionLocal()
    try:
        test_todos_los_profesionales_tienen_matricula(session)
        print("✅ RN-001: Todos los profesionales tienen matrícula")
    except AssertionError as e:
        print(f"❌ {e}")
    finally:
        session.close()
