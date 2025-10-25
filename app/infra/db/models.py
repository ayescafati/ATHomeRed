from __future__ import annotations

from datetime import date, time
from decimal import Decimal
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    JSON,
    Time,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    Text,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


# GUID helper para SQLite/Postgres cuando se almacena UUID como string(36)
class GUID(String):  # type: ignore[misc]
    def __init__(self) -> None:  # pragma: no cover
        super().__init__(length=36)


# Tabla puente M2M: Profesional - Especialidad
profesional_especialidad = Table(
    "profesional_especialidad",
    Base.metadata,
    Column("profesional_id", GUID(), ForeignKey("profesionales.id", ondelete="CASCADE"), primary_key=True),
    Column("especialidad_id", Integer, ForeignKey("especialidades.id_especialidad"), primary_key=True),
)



# Ubicación
class UbicacionORM(Base):
    __tablename__ = "ubicaciones"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=lambda: str(uuid4()))
    calle: Mapped[str] = mapped_column(Text, nullable=False)
    numero: Mapped[str] = mapped_column(Text, nullable=False)
    barrio: Mapped[str] = mapped_column(Text, nullable=False)
    departamento: Mapped[str] = mapped_column(Text, nullable=False)
    provincia: Mapped[str] = mapped_column(Text, nullable=False)


# Catálogo de Especialidades (con tarifa base)
class EspecialidadORM(Base):
    __tablename__ = "especialidades"

    id_especialidad: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    categoria: Mapped[str] = mapped_column(Text, nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    # Para precisión monetaria usamos Decimal con Numeric:
    tarifa: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)


# Profesional
class ProfesionalORM(Base):
    __tablename__ = "profesionales"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=lambda: str(uuid4()))
    nombre: Mapped[str] = mapped_column(Text, nullable=False)
    apellido: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    celular: Mapped[str] = mapped_column(Text, nullable=False)

    ubicacion_id: Mapped[str] = mapped_column(GUID(), ForeignKey("ubicaciones.id"), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    verificado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # (legacy) una sola matrícula en string; mantenemos por compatibilidad si tenías datos
    matricula: Mapped[str] = mapped_column(Text, nullable=False)

    ubicacion: Mapped[UbicacionORM] = relationship("UbicacionORM")
    especialidades: Mapped[List[EspecialidadORM]] = relationship(
        "EspecialidadORM",
        secondary=profesional_especialidad,
        lazy="joined",
    )
    # Relaciones 1:N
    disponibilidades: Mapped[List["DisponibilidadORM"]] = relationship(
        "DisponibilidadORM", back_populates="profesional", cascade="all, delete-orphan"
    )
    publicaciones: Mapped[List["PublicacionORM"]] = relationship(
        "PublicacionORM", back_populates="profesional", cascade="all, delete-orphan"
    )
    # nuevas relaciones imprescindibles:
    matriculas: Mapped[List["MatriculaORM"]] = relationship(
        "MatriculaORM", back_populates="profesional", cascade="all, delete-orphan"
    )
    valoraciones: Mapped[List["ValoracionORM"]] = relationship(
        "ValoracionORM", back_populates="profesional", cascade="all, delete-orphan"
    )
    
    matriculas: Mapped[List["MatriculaORM"]] = relationship(
        "MatriculaORM", back_populates="profesional", cascade="all, delete-orphan"
    )
    valoraciones: Mapped[List["ValoracionORM"]] = relationship(
        "ValoracionORM", back_populates="profesional", cascade="all, delete-orphan"
    )


# Disponibilidad (bloques de agenda)
class DisponibilidadORM(Base):
    __tablename__ = "disponibilidades"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=lambda: str(uuid4()))
    profesional_id: Mapped[str] = mapped_column(GUID(), ForeignKey("profesionales.id", ondelete="CASCADE"), nullable=False)

    # Guardamos días como texto "0,1,3" (L=0..D=6) para MVP; luego podés normalizar.
    dias_semana_text: Mapped[str] = mapped_column("dias_semana", Text, nullable=False)
    hora_inicio: Mapped[time] = mapped_column(Time, nullable=False)
    hora_fin: Mapped[time] = mapped_column(Time, nullable=False)

    profesional: Mapped[ProfesionalORM] = relationship("ProfesionalORM", back_populates="disponibilidades")

    __table_args__ = (
        CheckConstraint("hora_inicio < hora_fin", name="ck_disp_horas"),
    )

    # Convenience para exponer lista[str] al estilo del dominio
    @property
    def dias_semana(self) -> List[str]:
        return [s for s in (self.dias_semana_text or "").split(",") if s]

    @dias_semana.setter
    def dias_semana(self, value: List[str]) -> None:
        self.dias_semana_text = ",".join(value or [])


# Publicación (anuncios del profesional)
class PublicacionORM(Base):
    __tablename__ = "publicaciones"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=lambda: str(uuid4()))
    profesional_id: Mapped[str] = mapped_column(GUID(), ForeignKey("profesionales.id", ondelete="CASCADE"), nullable=False)
    especialidad_id: Mapped[int] = mapped_column(Integer, ForeignKey("especialidades.id_especialidad"), nullable=False)
    titulo: Mapped[str] = mapped_column(Text, nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    fecha_publicacion: Mapped[date] = mapped_column(Date, nullable=False)

    profesional: Mapped[ProfesionalORM] = relationship("ProfesionalORM", back_populates="publicaciones")
    especialidad: Mapped[EspecialidadORM] = relationship("EspecialidadORM")


# Responsable (familiar/tutor)
class ResponsableORM(Base):
    __tablename__ = "responsables"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=lambda: str(uuid4()))
    nombre: Mapped[str] = mapped_column(Text, nullable=False)
    apellido: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    celular: Mapped[str] = mapped_column(Text, nullable=False)

    ubicacion_id: Mapped[str] = mapped_column(GUID(), ForeignKey("ubicaciones.id"), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    relacion_con_paciente: Mapped[str] = mapped_column(Text, nullable=False)

    ubicacion: Mapped[UbicacionORM] = relationship("UbicacionORM")
    pacientes: Mapped[List["PacienteORM"]] = relationship(
        "PacienteORM", back_populates="responsable", cascade="all, delete-orphan"
    )


# Paciente
class PacienteORM(Base):
    __tablename__ = "pacientes"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=lambda: str(uuid4()))
    nombre: Mapped[str] = mapped_column(Text, nullable=False)
    apellido: Mapped[str] = mapped_column(Text, nullable=False)
    fecha_nacimiento: Mapped[date] = mapped_column(Date, nullable=False)
    cobertura: Mapped[str] = mapped_column(Text, nullable=False)
    notas: Mapped[str] = mapped_column(Text, nullable=False)

    ubicacion_id: Mapped[str] = mapped_column(GUID(), ForeignKey("ubicaciones.id"), nullable=False)
    responsable_id: Mapped[str] = mapped_column(GUID(), ForeignKey("responsables.id", ondelete="CASCADE"), nullable=False)

    ubicacion: Mapped[UbicacionORM] = relationship("UbicacionORM")
    responsable: Mapped[ResponsableORM] = relationship("ResponsableORM", back_populates="pacientes")


# Consulta (solicitud/cita) + Evento (Observer/Auditoria)
class ConsultaORM(Base):
    __tablename__ = "consultas"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=lambda: str(uuid4()))
    paciente_id: Mapped[str] = mapped_column(GUID(), ForeignKey("pacientes.id", ondelete="CASCADE"), nullable=False)
    profesional_id: Mapped[str] = mapped_column(GUID(), ForeignKey("profesionales.id", ondelete="CASCADE"), nullable=False)

    # NUEVO: lugar donde se realiza la consulta
    ubicacion_servicio_id: Mapped[str] = mapped_column(GUID(), ForeignKey("ubicaciones.id"), nullable=False)

    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    hora_inicio: Mapped[time] = mapped_column(Time, nullable=False)
    hora_fin: Mapped[time] = mapped_column(Time, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False)  # pendiente, confirmada, cancelada
    notas: Mapped[str] = mapped_column(Text, nullable=False)

    paciente: Mapped[PacienteORM] = relationship("PacienteORM")
    profesional: Mapped[ProfesionalORM] = relationship("ProfesionalORM")
    ubicacion_servicio: Mapped[UbicacionORM] = relationship("UbicacionORM")

    __table_args__ = (
        CheckConstraint("hora_inicio < hora_fin", name="ck_consulta_horas"),
    )



class EventoORM(Base):
    __tablename__ = "eventos"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=lambda: str(uuid4()))
    consulta_id: Mapped[str] = mapped_column(GUID(), ForeignKey("consultas.id", ondelete="CASCADE"), nullable=False)
    tipo: Mapped[str] = mapped_column(Text, nullable=False)  # ej: SolicitudCreada, CitaProgramada, etc.
    datos: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    consulta: Mapped[ConsultaORM] = relationship("ConsultaORM", backref="eventos")


# Matricula (imprescindible para Policy de provincia+vigencia)
class MatriculaORM(Base):
    __tablename__ = "matriculas"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=lambda: str(uuid4()))
    profesional_id: Mapped[str] = mapped_column(GUID(), ForeignKey("profesionales.id", ondelete="CASCADE"), nullable=False)
    numero: Mapped[str] = mapped_column(Text, nullable=False)
    provincia: Mapped[str] = mapped_column(Text, nullable=False)
    vigente_desde: Mapped[date] = mapped_column(Date, nullable=False)
    vigente_hasta: Mapped[Optional[date]] = mapped_column(Date)

    profesional: Mapped["ProfesionalORM"] = relationship("ProfesionalORM", back_populates="matriculas")

    __table_args__ = (
        CheckConstraint("vigente_hasta IS NULL OR vigente_hasta >= vigente_desde", name="ck_matricula_fechas"),
        UniqueConstraint("numero", "provincia", "profesional_id", name="uq_matricula_num_prov_prof"),
    )


class ValoracionORM(Base):
    __tablename__ = "valoraciones"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=lambda: str(uuid4()))
    profesional_id: Mapped[str] = mapped_column(GUID(), ForeignKey("profesionales.id", ondelete="CASCADE"), nullable=False)
    paciente_id: Mapped[str] = mapped_column(GUID(), ForeignKey("pacientes.id", ondelete="CASCADE"), nullable=False)
    puntuacion: Mapped[int] = mapped_column(Integer, nullable=False)
    comentario: Mapped[Optional[str]] = mapped_column(Text)
    creado_en: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)

    profesional: Mapped["ProfesionalORM"] = relationship("ProfesionalORM", back_populates="valoraciones")
    paciente: Mapped["PacienteORM"] = relationship("PacienteORM")

    __table_args__ = (
        CheckConstraint("puntuacion BETWEEN 1 AND 5", name="ck_valoracion_rango"),
    )



__all__ = [
    "UbicacionORM",
    "EspecialidadORM",
    "ProfesionalORM",
    "DisponibilidadORM",
    "PublicacionORM",
    "ResponsableORM",
    "PacienteORM",
    "profesional_especialidad",
    "ConsultaORM",
    "EventoORM",
    "MatriculaORM",
    "ValoracionORM",
]
