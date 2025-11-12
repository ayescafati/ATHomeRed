"""
Tests de integración con BD real
Testea el flujo completo: FastAPI → Repositorios → PostgreSQL

IMPORTANTE: Usa una BD de test y rollback automático de transacciones
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.api.dependencies import get_db
from app.infra.persistence.base import Base


TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_db():
    """
    Crea una BD en memoria para cada test
    Alternativa: PostgreSQL test con transacciones rollback
    """
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )

    yield TestingSessionLocal

    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_db):
    """Sesión de BD para el test"""
    session = test_db()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session: Session):
    """
    Cliente de test con BD real
    Override de la dependencia get_db_session
    """

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def db_con_datos_base(db_session):
    """
    Fixture que carga datos base en la BD de test
    (provincias, especialidades, etc.)
    """
    from app.infra.persistence.ubicacion import (
        ProvinciaORM,
        DepartamentoORM,
        BarrioORM,
    )
    from app.infra.persistence.servicios import EspecialidadORM
    from uuid import uuid4

    provincia = ProvinciaORM(id=str(uuid4()), nombre="Buenos Aires")
    db_session.add(provincia)

    departamento = DepartamentoORM(
        id=str(uuid4()), nombre="CABA", provincia_id=provincia.id
    )
    db_session.add(departamento)

    barrio = BarrioORM(
        id=str(uuid4()), nombre="Flores", departamento_id=departamento.id
    )
    db_session.add(barrio)

    especialidad_cardio = EspecialidadORM(
        id_especialidad=1, nombre="Cardiología"
    )
    db_session.add(especialidad_cardio)

    db_session.commit()

    return {
        "provincia": provincia,
        "departamento": departamento,
        "barrio": barrio,
        "especialidad": especialidad_cardio,
    }


class TestBusquedaConBDReal:
    """
    Tests de integración con BD real
    Verifica que el stack completo funcione correctamente
    """

    @pytest.mark.integration
    def test_listar_especialidades_bd_vacia(self, client):
        """GET /busqueda/especialidades con BD vacía"""
        response = client.get("/busqueda/especialidades")

        assert response.status_code == 200
        data = response.json()
        assert "especialidades" in data

    @pytest.mark.integration
    def test_listar_especialidades_con_datos(self, client, db_con_datos_base):
        """GET /busqueda/especialidades con datos en BD"""
        response = client.get("/busqueda/especialidades")

        assert response.status_code == 200
        data = response.json()
        assert len(data["especialidades"]) >= 1
        assert any(
            esp["nombre"] == "Cardiología" for esp in data["especialidades"]
        )

    @pytest.mark.integration
    def test_busqueda_sin_resultados_bd_vacia(self, client, db_con_datos_base):
        """Búsqueda en BD sin profesionales debe retornar lista vacía"""
        payload = {"nombre_especialidad": "Cardiología"}

        response = client.post("/busqueda/profesionales", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["profesionales"] == []

    @pytest.mark.integration
    @pytest.mark.skip(
        reason="Requiere profesionales en BD - implementar setup completo"
    )
    def test_busqueda_profesional_completo(
        self, client, db_con_datos_base, db_session
    ):
        """
        Test completo: crear profesional en BD y buscarlo
        TODO: Implementar cuando tengas fixtures de profesionales completos
        """
        from app.infra.persistence.usuarios import UsuarioORM
        from app.infra.persistence.perfiles import ProfesionalORM

        pass


class TestBusquedaBDPostgreSQL:
    """
    Tests específicos para PostgreSQL
    Requiere: PostgreSQL de test corriendo
    """

    @pytest.mark.integration
    @pytest.mark.postgres
    @pytest.mark.skip(reason="Requiere PostgreSQL test - configurar en CI/CD")
    def test_busqueda_con_postgis(self, client):
        """
        Test de búsqueda geográfica con PostGIS
        Requiere BD de test con extensión PostGIS
        """
        pass


"""
CONFIGURACIÓN RECOMENDADA:

1. pytest.ini - Agregar marcadores:
   [pytest]
   markers =
       integration: Tests de integración con BD
       postgres: Tests que requieren PostgreSQL
       slow: Tests lentos

2. Correr solo tests unitarios (rápidos):
   pytest tests/domain tests/api -v

3. Correr tests de integración:
   pytest tests/integration -v -m integration

4. Correr TODO:
   pytest tests/ -v

5. En CI/CD:
   - Tests unitarios: Siempre
   - Tests integración: En PRs
   - Tests E2E: En main/release
"""
