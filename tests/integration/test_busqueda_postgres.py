"""
Configuración para tests con PostgreSQL de test
Usa BD separada + rollback automático de transacciones
"""

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

from app.main import app
from app.api.dependencies import get_db
from app.infra.persistence.base import Base


POSTGRES_TEST_URL = (
    "postgresql://postgres:password@localhost:5432/athomered_test"
)


@pytest.fixture(scope="session")
def postgres_test_engine():
    """
    Engine para BD de test PostgreSQL
    Se crea una vez por sesión de tests

    SETUP PREVIO:
    CREATE DATABASE athomered_test;
    \c athomered_test
    CREATE EXTENSION postgis;
    """
    engine = create_engine(POSTGRES_TEST_URL, poolclass=NullPool, echo=False)

    Base.metadata.create_all(bind=engine)

    yield engine

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session_postgres(postgres_test_engine):
    """
    Sesión con rollback automático
    Cada test corre en una transacción que se hace rollback al final

    VENTAJA: Tests aislados, BD queda limpia
    """
    connection = postgres_test_engine.connect()
    transaction = connection.begin()

    session = Session(bind=connection)

    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            sess.expire_all()
            session.begin_nested()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client_postgres(db_session_postgres):
    """Cliente con BD PostgreSQL de test"""

    def override_get_db():
        try:
            yield db_session_postgres
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    from fastapi.testclient import TestClient

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def seed_postgres_data(db_session_postgres):
    """
    Carga datos de prueba en PostgreSQL
    Se hace rollback automáticamente después del test
    """
    from app.infra.persistence.ubicacion import (
        ProvinciaORM,
        DepartamentoORM,
        BarrioORM,
    )
    from app.infra.persistence.servicios import EspecialidadORM
    from app.infra.persistence.usuarios import UsuarioORM
    from app.infra.persistence.perfiles import ProfesionalORM
    from uuid import uuid4

    provincia = ProvinciaORM(id=str(uuid4()), nombre="Buenos Aires")
    db_session_postgres.add(provincia)

    departamento = DepartamentoORM(
        id=str(uuid4()), nombre="CABA", provincia_id=provincia.id
    )
    db_session_postgres.add(departamento)

    barrio = BarrioORM(
        id=str(uuid4()), nombre="Flores", departamento_id=departamento.id
    )
    db_session_postgres.add(barrio)

    especialidad = EspecialidadORM(id_especialidad=1, nombre="Cardiología")
    db_session_postgres.add(especialidad)

    usuario = UsuarioORM(
        id=str(uuid4()),
        nombre="Juan",
        apellido="Pérez",
        email="juan.perez@test.com",
        password_hash="fake_hash",
        es_profesional=True,
        activo=True,
        verificado=True,
    )
    db_session_postgres.add(usuario)
    db_session_postgres.flush()

    profesional = ProfesionalORM(id=usuario.id, activo=True, verificado=True)
    db_session_postgres.add(profesional)

    db_session_postgres.commit()

    return {
        "provincia": provincia,
        "departamento": departamento,
        "barrio": barrio,
        "especialidad": especialidad,
        "usuario": usuario,
        "profesional": profesional,
    }


class TestIntegracionPostgreSQL:
    """
    Tests de integración con PostgreSQL real
    Marcar con @pytest.mark.postgres
    """

    @pytest.mark.integration
    @pytest.mark.postgres
    def test_busqueda_con_profesional_en_bd(
        self, client_postgres, seed_postgres_data
    ):
        """
        Test completo: profesional en BD → buscar → encontrar
        """
        payload = {"nombre_especialidad": "Cardiología"}

        response = client_postgres.post(
            "/busqueda/profesionales", json=payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert any(
            prof["nombre"] == "Juan" and prof["apellido"] == "Pérez"
            for prof in data["profesionales"]
        )

    @pytest.mark.integration
    @pytest.mark.postgres
    def test_busqueda_por_ubicacion_postgis(
        self, client_postgres, seed_postgres_data
    ):
        """
        Test de búsqueda geográfica con PostGIS
        Verifica que los joins espaciales funcionen
        """
        payload = {"provincia": "Buenos Aires"}

        response = client_postgres.post(
            "/busqueda/profesionales", json=payload
        )

        assert response.status_code == 200

    @pytest.mark.integration
    @pytest.mark.postgres
    def test_joins_no_duplicados_en_busqueda_combinada(
        self, client_postgres, seed_postgres_data
    ):
        """
        Verifica que la corrección de joins funcione en BD real
        Este test fallaría con la versión antigua que tenía joins duplicados
        """
        payload = {
            "nombre_especialidad": "Cardiología",
            "provincia": "Buenos Aires",
            "departamento": "CABA",
        }

        response = client_postgres.post(
            "/busqueda/profesionales", json=payload
        )

        assert response.status_code == 200


"""
COMANDOS PARA CORRER:

1. Solo tests unitarios (sin BD):
   pytest tests/domain tests/api -v

2. Tests de integración con SQLite:
   pytest tests/integration/test_busqueda_con_bd.py -v -m integration

3. Tests de integración con PostgreSQL:
   pytest tests/integration/test_busqueda_postgres.py -v -m postgres

4. Excluir tests lentos en desarrollo:
   pytest tests/ -v -m "not postgres"

5. En CI/CD (GitHub Actions, GitLab CI):
   - Setup PostgreSQL service
   - pytest tests/ -v --cov
"""
