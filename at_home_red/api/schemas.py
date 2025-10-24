from __future__ import annotations

from datetime import date, time
from typing import List, Optional
from uuid import UUID

try:
    from pydantic import BaseModel, ConfigDict
except ImportError:  # pragma: no cover - handled at runtime
    from pydantic import BaseModel  # type: ignore

    ConfigDict = None  # type: ignore


class APIModel(BaseModel):
    """Base schema with compatibility between Pydantic v1 and v2."""

    class Config:
        from_attributes = True


if (
    "ConfigDict" in globals() and ConfigDict is not None
):  # pragma: no cover - depends on pydantic version
    APIModel.model_config = ConfigDict(from_attributes=True)  # type: ignore[attr-defined]


class UbicacionSchema(APIModel):
    calle: str
    numero: str
    barrio: str
    ciudad: str
    provincia: str
    latitud: float
    longitud: float

    @classmethod
    def from_domain(cls, ubicacion) -> "UbicacionSchema":
        return cls(
            calle=ubicacion.calle,
            numero=ubicacion.numero,
            barrio=ubicacion.barrio,
            ciudad=ubicacion.ciudad,
            provincia=ubicacion.provincia,
            latitud=ubicacion.latitud,
            longitud=ubicacion.longitud,
        )


class EspecialidadSchema(APIModel):
    id_especialidad: int
    nombre: str
    categoria: str
    descripcion: str
    tarifa: float

    @classmethod
    def from_domain(cls, especialidad) -> "EspecialidadSchema":
        return cls(
            id_especialidad=especialidad.id_especialidad,
            nombre=especialidad.nombre,
            categoria=especialidad.categoria,
            descripcion=especialidad.descripcion,
            tarifa=especialidad.tarifa,
        )


class DisponibilidadSchema(APIModel):
    dias_semana: List[str]
    hora_inicio: time
    hora_fin: time

    @classmethod
    def from_domain(cls, disponibilidad) -> "DisponibilidadSchema":
        return cls(
            dias_semana=list(disponibilidad.dias_semana),
            hora_inicio=disponibilidad.hora_inicio,
            hora_fin=disponibilidad.hora_fin,
        )


class PacienteSchema(APIModel):
    id: UUID
    nombre: str
    apellido: str
    fecha_nacimiento: date
    cobertura: str
    notas: str
    ubicacion: UbicacionSchema

    @classmethod
    def from_domain(cls, paciente) -> "PacienteSchema":
        return cls(
            id=paciente.id,
            nombre=paciente.nombre,
            apellido=paciente.apellido,
            fecha_nacimiento=paciente.fecha_nacimiento,
            cobertura=paciente.cobertura,
            notas=paciente.notas,
            ubicacion=UbicacionSchema.from_domain(paciente.ubicacion),
        )


class ProfesionalSummarySchema(APIModel):
    id: UUID
    nombre: str
    apellido: str
    ciudad: str
    provincia: str
    verificado: bool

    @classmethod
    def from_domain(cls, profesional) -> "ProfesionalSummarySchema":
        return cls(
            id=profesional.id,
            nombre=profesional.nombre,
            apellido=profesional.apellido,
            ciudad=profesional.ubicacion.ciudad,
            provincia=profesional.ubicacion.provincia,
            verificado=profesional.verificado,
        )


class PublicacionSchema(APIModel):
    profesional_id: UUID
    titulo: str
    descripcion: str
    especialidad: EspecialidadSchema
    fecha_publicacion: date
    profesional: Optional[ProfesionalSummarySchema] = None

    @classmethod
    def from_domain(
        cls, publicacion, include_profesional: bool = False
    ) -> "PublicacionSchema":
        profesional_summary = (
            ProfesionalSummarySchema.from_domain(publicacion.profesional)
            if include_profesional
            else None
        )
        return cls(
            profesional_id=publicacion.profesional.id,
            titulo=publicacion.titulo,
            descripcion=publicacion.descripcion,
            especialidad=EspecialidadSchema.from_domain(
                publicacion.especialidad
            ),
            fecha_publicacion=publicacion.fecha_publicacion,
            profesional=profesional_summary,
        )


class ProfesionalSchema(APIModel):
    id: UUID
    nombre: str
    apellido: str
    email: str
    celular: str
    ubicacion: UbicacionSchema
    activo: bool
    verificado: bool
    matricula: str
    especialidades: List[EspecialidadSchema]
    disponibilidades: List[DisponibilidadSchema]
    publicaciones: List[PublicacionSchema]

    @classmethod
    def from_domain(
        cls,
        profesional,
        *,
        disponibilidades,
        publicaciones,
    ) -> "ProfesionalSchema":
        return cls(
            id=profesional.id,
            nombre=profesional.nombre,
            apellido=profesional.apellido,
            email=profesional.email,
            celular=profesional.celular,
            ubicacion=UbicacionSchema.from_domain(profesional.ubicacion),
            activo=profesional.activo,
            verificado=profesional.verificado,
            matricula=profesional.matricula,
            especialidades=[
                EspecialidadSchema.from_domain(e)
                for e in profesional.especialidades
            ],
            disponibilidades=[
                DisponibilidadSchema.from_domain(d) for d in disponibilidades
            ],
            publicaciones=[
                PublicacionSchema.from_domain(p, include_profesional=False)
                for p in publicaciones
            ],
        )


class ResponsableSchema(APIModel):
    id: UUID
    nombre: str
    apellido: str
    email: str
    celular: str
    ubicacion: UbicacionSchema
    activo: bool
    relacion_con_paciente: str
    pacientes: List[PacienteSchema]

    @classmethod
    def from_domain(cls, responsable) -> "ResponsableSchema":
        return cls(
            id=responsable.id,
            nombre=responsable.nombre,
            apellido=responsable.apellido,
            email=responsable.email,
            celular=responsable.celular,
            ubicacion=UbicacionSchema.from_domain(responsable.ubicacion),
            activo=responsable.activo,
            relacion_con_paciente=responsable.relacion_con_paciente,
            pacientes=[
                PacienteSchema.from_domain(p) for p in responsable.pacientes
            ],
        )
