"""
Tests unitarios para las entities del domain
"""

import pytest
from datetime import date, time
from uuid import uuid4

from app.domain.entities.usuarios import (
    Usuario,
    Profesional,
    Solicitante,
    Paciente,
)
from app.domain.value_objects.objetos_valor import (
    Ubicacion,
    Disponibilidad,
    Matricula,
)
from app.domain.entities.catalogo import Especialidad


class TestUbicacion:
    """Tests para Ubicacion (Value Object)"""

    def test_crear_ubicacion(self, ubicacion_buenos_aires):
        """Crear una ubicación correctamente"""
        assert ubicacion_buenos_aires.provincia == "Buenos Aires"
        assert ubicacion_buenos_aires.departamento == "CABA"
        assert ubicacion_buenos_aires.barrio == "Flores"
        assert ubicacion_buenos_aires.latitud == -34.6037

    def test_ubicaciones_iguales_son_equivalentes(self):
        """Dos ubicaciones con los mismos datos son equivalentes"""
        ub1 = Ubicacion(
            provincia="Buenos Aires",
            departamento="CABA",
            barrio="Flores",
            calle="Av. Acoyte",
            numero=1234,
            latitud=-34.6037,
            longitud=-58.3816,
        )
        ub2 = Ubicacion(
            provincia="Buenos Aires",
            departamento="CABA",
            barrio="Flores",
            calle="Av. Acoyte",
            numero=1234,
            latitud=-34.6037,
            longitud=-58.3816,
        )

        assert ub1 == ub2


class TestEspecialidad:
    """Tests para Especialidad"""

    def test_crear_especialidad(self, especialidad_cardiologia):
        """Crear una especialidad"""
        assert especialidad_cardiologia.id == 1
        assert especialidad_cardiologia.nombre == "Cardiología"

    def test_especialidades_diferentes(
        self, especialidad_cardiologia, especialidad_dermatologia
    ):
        """Especialidades diferentes tienen IDs distintos"""
        assert especialidad_cardiologia.id != especialidad_dermatologia.id
        assert (
            especialidad_cardiologia.nombre != especialidad_dermatologia.nombre
        )


class TestUsuario:
    """Tests para Usuario (clase abstracta)"""

    def test_nombre_completo(self, profesional_cardiologia):
        """La propiedad nombre_completo funciona"""
        assert profesional_cardiologia.nombre_completo == "Juan Pérez"

    def test_activar_usuario(self, profesional_cardiologia):
        """Activar un usuario desactivado"""
        profesional_cardiologia.activo = False
        profesional_cardiologia.activar()
        assert profesional_cardiologia.activo is True

    def test_desactivar_usuario(self, profesional_cardiologia):
        """Desactivar un usuario activo"""
        profesional_cardiologia.activo = True
        profesional_cardiologia.desactivar()
        assert profesional_cardiologia.activo is False

    def test_datos_contacto(self, profesional_cardiologia):
        """El método datos_contacto retorna info formateada"""
        contacto = profesional_cardiologia.datos_contacto()
        assert "Juan Pérez" in contacto
        assert "juan.perez@example.com" in contacto
        assert "1123456789" in contacto


class TestProfesional:
    """Tests para Profesional"""

    def test_crear_profesional(self, profesional_cardiologia):
        """Crear un profesional correctamente"""
        assert profesional_cardiologia.nombre == "Juan"
        assert profesional_cardiologia.apellido == "Pérez"
        assert profesional_cardiologia.verificado is True
        assert len(profesional_cardiologia.especialidades) > 0

    def test_profesional_no_verificado_por_defecto(
        self, ubicacion_buenos_aires, especialidad_cardiologia
    ):
        """Un profesional nuevo no está verificado por defecto"""
        prof = Profesional(
            id=uuid4(),
            nombre="Test",
            apellido="Prof",
            email="test@example.com",
            celular="123456789",
            ubicacion=ubicacion_buenos_aires,
            especialidades=[especialidad_cardiologia],
        )

        assert prof.verificado is False

    def test_agregar_disponibilidad(
        self, profesional_cardiologia, disponibilidad_miercoles_tarde
    ):
        """Agregar disponibilidad a un profesional"""
        cantidad_inicial = len(profesional_cardiologia.disponibilidades)

        profesional_cardiologia.agregar_disponibilidad(
            disponibilidad_miercoles_tarde
        )

        assert (
            len(profesional_cardiologia.disponibilidades)
            == cantidad_inicial + 1
        )
        assert (
            disponibilidad_miercoles_tarde
            in profesional_cardiologia.disponibilidades
        )

    def test_profesional_hereda_de_usuario(self, profesional_cardiologia):
        """Profesional tiene métodos de Usuario"""
        profesional_cardiologia.desactivar()
        assert profesional_cardiologia.activo is False

        profesional_cardiologia.activar()
        assert profesional_cardiologia.activo is True

    def test_profesional_con_multiples_especialidades(
        self,
        ubicacion_buenos_aires,
        especialidad_cardiologia,
        especialidad_dermatologia,
    ):
        """Un profesional puede tener múltiples especialidades"""
        prof = Profesional(
            id=uuid4(),
            nombre="Multi",
            apellido="Especialista",
            email="multi@example.com",
            celular="123456789",
            ubicacion=ubicacion_buenos_aires,
            especialidades=[
                especialidad_cardiologia,
                especialidad_dermatologia,
            ],
        )

        assert len(prof.especialidades) == 2
        assert especialidad_cardiologia in prof.especialidades
        assert especialidad_dermatologia in prof.especialidades


class TestSolicitante:
    """Tests para Solicitante"""

    def test_crear_solicitante(self, solicitante):
        """Crear un solicitante"""
        assert solicitante.nombre == "Carlos"
        assert solicitante.apellido == "López"
        assert solicitante.pacientes == []

    def test_solicitante_activo_por_defecto(self, ubicacion_buenos_aires):
        """Un solicitante es activo por defecto"""
        sol = Solicitante(
            id=uuid4(),
            nombre="Test",
            apellido="Solicitante",
            email="test@example.com",
            celular="123456789",
            ubicacion=ubicacion_buenos_aires,
        )

        assert sol.activo is True

    def test_agregar_paciente(self, solicitante, paciente):
        """Agregar un paciente al solicitante"""
        assert paciente in solicitante.pacientes

    def test_agregar_mismo_paciente_dos_veces(self, solicitante, paciente):
        """No se puede agregar el mismo paciente dos veces"""
        cantidad_inicial = len(solicitante.pacientes)

        solicitante.agregar_paciente(paciente)

        assert len(solicitante.pacientes) == cantidad_inicial

    def test_solicitante_pacientes_lista_vacia_al_inicio(self, solicitante):
        """Un solicitante comienza sin pacientes"""
        assert isinstance(solicitante.pacientes, list)
        assert len(solicitante.pacientes) == 0

    def test_solicitante_hereda_de_usuario(self, solicitante):
        """Solicitante tiene métodos de Usuario"""
        solicitante.desactivar()
        assert solicitante.activo is False

        assert "Carlos López" == solicitante.nombre_completo


class TestPaciente:
    """Tests para Paciente (NO hereda de Usuario)"""

    def test_crear_paciente(self, paciente):
        """Crear un paciente"""
        assert paciente.nombre == "Roberto"
        assert paciente.apellido == "Fernández"
        assert paciente.fecha_nacimiento == date(1979, 5, 15)
        assert paciente.relacion == "self"

    def test_edad_paciente(self, paciente):
        """Calcular edad del paciente"""
        edad = paciente.edad()
        assert edad == 46

    def test_edad_paciente_en_fecha_especifica(self, paciente):
        """Calcular edad en una fecha específica"""
        fecha_test = date(2025, 5, 10)
        edad = paciente.edad(fecha_test)
        assert edad == 45

        fecha_test2 = date(2025, 5, 20)
        edad2 = paciente.edad(fecha_test2)
        assert edad2 == 46

    def test_edad_paciente_en_dia_cumpleaños(self, paciente):
        """Calcular edad el día del cumpleaños"""
        fecha_test = date(2025, 5, 15)
        edad = paciente.edad(fecha_test)
        assert edad == 46

    def test_paciente_hijo(self, paciente_hijo):
        """Paciente con relación 'hijo'"""
        assert paciente_hijo.relacion == "hijo"
        assert paciente_hijo.nombre == "Lucas"

    def test_paciente_con_notas(self, solicitante):
        """Paciente puede tener notas"""
        paciente = Paciente(
            id=uuid4(),
            nombre="Test",
            apellido="Paciente",
            fecha_nacimiento=date(2000, 1, 1),
            ubicacion=solicitante.ubicacion,
            solicitante_id=solicitante.id,
            notas="Alergias a penicilina",
        )

        assert paciente.notas == "Alergias a penicilina"

    def test_nombre_completo_paciente(self, paciente):
        """Paciente tiene nombre completo como propiedad"""
        assert paciente.nombre_completo == "Roberto Fernández"

    def test_paciente_no_es_usuario(self, paciente):
        """Paciente NO hereda de Usuario"""
        assert not isinstance(paciente, Usuario)
        assert not hasattr(paciente, "activar")


class TestIntegracionEntities:
    """Tests de integración entre entities"""

    def test_flujo_creacion_solicitante_con_pacientes(
        self, solicitante, paciente, paciente_hijo
    ):
        """Flujo completo: crear solicitante con pacientes"""
        assert solicitante.nombre_completo == "Carlos López"
        assert len(solicitante.pacientes) == 2

        assert paciente.solicitante_id == solicitante.id
        assert paciente_hijo.solicitante_id == solicitante.id

    def test_flujo_profesional_con_especialidades(
        self, profesional_cardiologia, disponibilidad_miercoles_tarde
    ):
        """Flujo completo: profesional con especialidades y disponibilidades"""
        profesional_cardiologia.agregar_disponibilidad(
            disponibilidad_miercoles_tarde
        )

        assert len(profesional_cardiologia.especialidades) >= 1
        assert len(profesional_cardiologia.disponibilidades) == 2
        assert len(profesional_cardiologia.matriculas) >= 1

    def test_diferencia_usuario_vs_paciente(
        self, profesional_cardiologia, paciente
    ):
        """Los profesionales son usuarios, los pacientes no"""
        assert isinstance(profesional_cardiologia, Usuario)
        assert not isinstance(paciente, Usuario)

        assert hasattr(profesional_cardiologia, "activar")
        assert not hasattr(paciente, "activar")
