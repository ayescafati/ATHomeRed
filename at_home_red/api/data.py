from __future__ import annotations

from collections import defaultdict
from datetime import date, time
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from ..enumeraciones import DiaSemana
from ..modelos.catalogo import Disponibilidad, Especialidad, Publicacion
from ..modelos.objetos_valor import Ubicacion
from ..modelos.usuarios import Paciente, Profesional, Responsable


class InMemoryDataStore:
    """Repositorio en memoria con datos de ejemplo."""

    def __init__(self) -> None:
        self._especialidades: Dict[int, Especialidad] = {}
        self._profesionales: Dict[UUID, Profesional] = {}
        self._responsables: Dict[UUID, Responsable] = {}
        self._disponibilidades: Dict[UUID, List[Disponibilidad]] = defaultdict(
            list
        )
        self._publicaciones: Dict[UUID, List[Publicacion]] = defaultdict(list)
        self._seed()

    def _seed(self) -> None:
        especialidad_at = Especialidad(
            id_especialidad=1,
            nombre="Acompanamiento Terapeutico",
            categoria="Salud Mental",
            descripcion="Apoyo domiciliario para pacientes con necesidades de contencion.",
            tarifa=3500.0,
        )
        especialidad_enfermeria = Especialidad(
            id_especialidad=2,
            nombre="Enfermeria Domiciliaria",
            categoria="Salud General",
            descripcion="Servicios de enfermeria general y control de signos vitales.",
            tarifa=4200.0,
        )
        self._especialidades = {
            especialidad_at.id_especialidad: especialidad_at,
            especialidad_enfermeria.id_especialidad: especialidad_enfermeria,
        }

        profesional_1 = Profesional(
            id=uuid4(),
            nombre="Ana",
            apellido="Martinez",
            email="ana.martinez@example.com",
            celular="+54 9 11 4000 0001",
            ubicacion=Ubicacion(
                calle="Av. Cabildo",
                numero="1234",
                barrio="Belgrano",
                ciudad="Buenos Aires",
                provincia="Buenos Aires",
                latitud=-34.5607,
                longitud=-58.4560,
            ),
            activo=True,
            verificado=True,
            matricula="MN-1234",
            especialidades=[especialidad_at],
        )

        profesional_2 = Profesional(
            id=uuid4(),
            nombre="Bruno",
            apellido="Lopez",
            email="bruno.lopez@example.com",
            celular="+54 9 11 4000 0002",
            ubicacion=Ubicacion(
                calle="Sucre",
                numero="678",
                barrio="Belgrano",
                ciudad="Buenos Aires",
                provincia="Buenos Aires",
                latitud=-34.5621,
                longitud=-58.4499,
            ),
            activo=True,
            verificado=False,
            matricula="MN-5678",
            especialidades=[especialidad_enfermeria],
        )

        paciente_1 = Paciente(
            id=uuid4(),
            nombre="Mateo",
            apellido="Gomez",
            fecha_nacimiento=date(2015, 6, 16),
            cobertura="Prepaga Azul",
            notas="Requiere acompanamiento diario de 4 horas.",
            ubicacion=Ubicacion(
                calle="Av. Santa Fe",
                numero="2450",
                barrio="Palermo",
                ciudad="Buenos Aires",
                provincia="Buenos Aires",
                latitud=-34.5898,
                longitud=-58.4156,
            ),
        )

        responsable_1 = Responsable(
            id=uuid4(),
            nombre="Lucia",
            apellido="Gomez",
            email="lucia.gomez@example.com",
            celular="+54 9 11 5000 0001",
            ubicacion=Ubicacion(
                calle="Av. Santa Fe",
                numero="2450",
                barrio="Palermo",
                ciudad="Buenos Aires",
                provincia="Buenos Aires",
                latitud=-34.5898,
                longitud=-58.4156,
            ),
            activo=True,
            pacientes=[paciente_1],
            relacion_con_paciente="Madre",
        )

        self._profesionales = {
            profesional_1.id: profesional_1,
            profesional_2.id: profesional_2,
        }
        self._responsables = {responsable_1.id: responsable_1}

        disponibilidad_1 = Disponibilidad(
            dias_semana=[DiaSemana.LU, DiaSemana.MI, DiaSemana.VI],
            hora_inicio=time(8, 0),
            hora_fin=time(12, 0),
        )
        disponibilidad_2 = Disponibilidad(
            dias_semana=[DiaSemana.MA, DiaSemana.JU],
            hora_inicio=time(14, 0),
            hora_fin=time(18, 0),
        )
        self._disponibilidades[profesional_1.id] = [disponibilidad_1]
        self._disponibilidades[profesional_2.id] = [disponibilidad_2]

        publicacion_1 = Publicacion(
            profesional=profesional_1,
            titulo="Acompanamiento en trastornos del espectro autista",
            descripcion="Plan de intervencion personalizado, coordinacion con equipo interdisciplinario.",
            especialidad=especialidad_at,
            fecha_publicacion=date.today(),
        )
        publicacion_2 = Publicacion(
            profesional=profesional_2,
            titulo="Enfermeria domiciliaria para adultos mayores",
            descripcion="Control de medicacion, curaciones y monitoreo de signos vitales.",
            especialidad=especialidad_enfermeria,
            fecha_publicacion=date.today(),
        )
        self._publicaciones[profesional_1.id] = [publicacion_1]
        self._publicaciones[profesional_2.id] = [publicacion_2]

    def list_profesionales(
        self, especialidad: Optional[str] = None, ciudad: Optional[str] = None
    ) -> List[Profesional]:
        profesionales = list(self._profesionales.values())
        if especialidad:
            criterio = especialidad.strip().lower()
            profesionales = [
                p
                for p in profesionales
                if any(e.nombre.lower() == criterio for e in p.especialidades)
            ]
        if ciudad:
            criterio_ciudad = ciudad.strip().lower()
            profesionales = [
                p
                for p in profesionales
                if p.ubicacion.ciudad.lower() == criterio_ciudad
            ]
        return profesionales

    def get_profesional(self, profesional_id: UUID) -> Optional[Profesional]:
        return self._profesionales.get(profesional_id)

    def get_disponibilidades(
        self, profesional_id: UUID
    ) -> List[Disponibilidad]:
        return list(self._disponibilidades.get(profesional_id, []))

    def get_publicaciones_de_profesional(
        self, profesional_id: UUID
    ) -> List[Publicacion]:
        return list(self._publicaciones.get(profesional_id, []))

    def list_especialidades(self) -> List[Especialidad]:
        return list(self._especialidades.values())

    def list_publicaciones(
        self,
        especialidad: Optional[str] = None,
        ciudad: Optional[str] = None,
    ) -> List[Publicacion]:
        publicaciones: List[Publicacion] = [
            pub
            for pub_list in self._publicaciones.values()
            for pub in pub_list
        ]
        if especialidad:
            criterio = especialidad.strip().lower()
            publicaciones = [
                pub
                for pub in publicaciones
                if pub.especialidad.nombre.lower() == criterio
            ]
        if ciudad:
            criterio_ciudad = ciudad.strip().lower()
            publicaciones = [
                pub
                for pub in publicaciones
                if pub.profesional.ubicacion.ciudad.lower() == criterio_ciudad
            ]
        return publicaciones

    def list_responsables(self) -> List[Responsable]:
        return list(self._responsables.values())

    def get_responsable(self, responsable_id: UUID) -> Optional[Responsable]:
        return self._responsables.get(responsable_id)


_DATA_STORE = InMemoryDataStore()


def get_data_store() -> InMemoryDataStore:
    """FastAPI dependency."""
    return _DATA_STORE
