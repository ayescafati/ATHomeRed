"""
Test de integración: verificar creación de profesionales con matrículas vía Repository
"""

from datetime import date, timedelta
from uuid import uuid4

from app.infra.persistence.database import SessionLocal
from app.infra.repositories.profesional_repository import ProfesionalRepository
from app.domain.entities.usuarios import Profesional
from app.domain.value_objects.objetos_valor import Ubicacion, Matricula


def test_crear_profesional_con_matriculas():
    """
    Test de integración: crear profesional con matrículas usando el repositorio
    Este test verifica que la corrección aplicada funciona correctamente.
    """
    session = SessionLocal()
    repo = ProfesionalRepository(session)

    try:
        # Setup: crear ubicación
        ubicacion = Ubicacion(
            provincia="Córdoba",
            departamento="Capital",
            barrio="Centro",
            calle="San Jerónimo",
            numero="123",
        )

        # Setup: crear matrícula
        hoy = date.today()
        matricula = Matricula(
            numero=f"TEST-{uuid4().hex[:8].upper()}",
            provincia="Córdoba",
            vigente_desde=hoy,
            vigente_hasta=hoy + timedelta(days=365),
        )

        # Action: crear profesional con matrícula
        profesional = Profesional(
            id=uuid4(),
            nombre="Test",
            apellido="Consistency",
            email=f"test.consistency.{uuid4()}@test.com",
            celular="351-9999999",
            ubicacion=ubicacion,
            activo=True,
            verificado=False,
            matriculas=[matricula],
            especialidades=[],
            disponibilidades=[],
        )

        profesional_creado = repo.crear(profesional)

        # Assert: verificar que se creó correctamente
        assert profesional_creado is not None
        assert profesional_creado.id is not None
        assert len(profesional_creado.matriculas) == 1
        assert profesional_creado.matriculas[0].numero == matricula.numero
        assert profesional_creado.matriculas[0].provincia == matricula.provincia

        # Cleanup
        repo.eliminar(profesional_creado.id)
        session.commit()

        print(
            f"✅ Test passed: Professional created with {len(profesional_creado.matriculas)} matricula(s)"
        )

    finally:
        session.close()


def test_crear_profesional_sin_matriculas_debe_funcionar():
    """
    Test: crear profesional sin matrículas debe funcionar técnicamente
    (aunque viola la regla de negocio RN-001)
    """
    session = SessionLocal()
    repo = ProfesionalRepository(session)

    try:
        ubicacion = Ubicacion(
            provincia="Córdoba",
            departamento="Capital",
            barrio="Centro",
            calle="Independencia",
            numero="456",
        )

        profesional = Profesional(
            id=uuid4(),
            nombre="Sin",
            apellido="Matricula",
            email=f"sin.matricula.{uuid4()}@test.com",
            celular="351-8888888",
            ubicacion=ubicacion,
            activo=True,
            verificado=False,
            matriculas=[],  # Sin matrículas
            especialidades=[],
            disponibilidades=[],
        )

        # Debe funcionar técnicamente (aunque viola RN-001)
        profesional_creado = repo.crear(profesional)

        assert profesional_creado is not None
        assert len(profesional_creado.matriculas) == 0

        # Cleanup
        repo.eliminar(profesional_creado.id)
        session.commit()

        print(
            "✅ Test passed: Professional created without matriculas (violates RN-001)"
        )

    finally:
        session.close()


if __name__ == "__main__":
    print("=== Test 1: Crear profesional CON matrículas ===")
    test_crear_profesional_con_matriculas()

    print("\n=== Test 2: Crear profesional SIN matrículas ===")
    test_crear_profesional_sin_matriculas_debe_funcionar()

    print("\n✅ All tests passed!")
