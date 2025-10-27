from __future__ import annotations

from datetime import date, time
from decimal import Decimal
from typing import List, Optional
import uuid

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
    Index,
    text, 
)
from sqlalchemy.dialects.postgresql import UUID, VARCHAR as Varchar
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column, relationship
from sqlalchemy import MetaData


# Base con esquema por defecto "athome"

metadata = MetaData(schema="athome")
class Base(DeclarativeBase):
    metadata = metadata



# Ubicación (catálogos normalizados hasta DIRECCION)
class ProvinciaORM(Base):
    __tablename__ = "provincia"
    __table_args__ = (
        UniqueConstraint("nombre", name="uq_provincia_nombre"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    nombre: Mapped[str] = mapped_column(Varchar(50), nullable=False)

    departamentos: Mapped[List["DepartamentoORM"]] = relationship(
        back_populates="provincia", cascade="all, delete-orphan"
    )


class DepartamentoORM(Base):
    __tablename__ = "departamento"
    __table_args__ = (
        UniqueConstraint("provincia_id", "nombre", name="uq_departamento_provincia_nombre"),
        Index("ix_departamento_provincia", "provincia_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    provincia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("athome.provincia.id", ondelete="RESTRICT"), nullable=False
    )
    nombre: Mapped[str] = mapped_column(Varchar(50), nullable=False)

    provincia: Mapped["ProvinciaORM"] = relationship(back_populates="departamentos")
    barrios: Mapped[List["BarrioORM"]] = relationship(
        back_populates="departamento", cascade="all, delete-orphan"
    )


class BarrioORM(Base):
    __tablename__ = "barrio"
    __table_args__ = (
        UniqueConstraint("departamento_id", "nombre", name="uq_barrio_departamento_nombre"),
        Index("ix_barrio_departamento", "departamento_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    departamento_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("athome.departamento.id", ondelete="RESTRICT"), nullable=False
    )
    nombre: Mapped[str] = mapped_column(Varchar(50), nullable=False)

    departamento: Mapped["DepartamentoORM"] = relationship(back_populates="barrios")
    direcciones: Mapped[List["DireccionORM"]] = relationship(
        back_populates="barrio", cascade="all, delete-orphan"
    )


class DireccionORM(Base):
    __tablename__ = "direccion"
    __table_args__ = (
        Index("ix_direccion_barrio", "barrio_id"),
        CheckConstraint(
            "(latitud is null and longitud is null) or (latitud between -90 and 90 and longitud between -180 and 180)",
            name="ck_dir_latlon",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    barrio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("athome.barrio.id", ondelete="RESTRICT"), nullable=False
    )
    calle: Mapped[str] = mapped_column(Varchar(100), nullable=False)
    numero: Mapped[int] = mapped_column(nullable=False)
    # opcional (las completa el backend vía geocoding)
    latitud: Mapped[Optional[float]] = mapped_column(Float)
    longitud: Mapped[Optional[float]] = mapped_column(Float)

    barrio: Mapped["BarrioORM"] = relationship(back_populates="direcciones")



# Catálogo de Especialidades
class EspecialidadORM(Base):
    __tablename__ = "especialidades"
    id_especialidad: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(Varchar(80), nullable=False, unique=True)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    tarifa: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)



# Profesional y M2M con Especialidades
profesional_especialidad = Table(
    "profesional_especialidad",
    Base.metadata,
    Column("profesional_id", UUID(as_uuid=True), ForeignKey("athome.profesionales.id", ondelete="CASCADE"), primary_key=True),
    Column("especialidad_id", Integer, ForeignKey("athome.especialidades.id_especialidad", ondelete="CASCADE"), primary_key=True),
)

class PacienteResponsableORM(Base):
    """
    Vínculo entre un Paciente y un Usuario que actúa como Responsable,
    etiquetado con una relación de catálogo (MADRE, PADRE, TIO, etc.).
    """
    __tablename__ = "paciente_responsable"
    __table_args__ = (
        # Evitar duplicados exactos del vínculo
        UniqueConstraint("paciente_id", "responsable_usuario_id", "relacion_id",
                         name="uq_pacresp_paciente_responsable_rel"),
        # Opcional: asegurar 0/1 principal por paciente (ver trigger si querés forzarlo fuerte)
        Index("ix_pacresp_paciente", "paciente_id"),
        Index("ix_pacresp_responsable_usuario", "responsable_usuario_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )

    paciente_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("athome.pacientes.id", ondelete="CASCADE"), nullable=False
    )
    responsable_usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("athome.usuarios.id", ondelete="RESTRICT"), nullable=False
    )
    relacion_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("athome.relacion_responsable.id", ondelete="RESTRICT"), nullable=False
    )

    # Atributos del vínculo
    es_principal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    vigente_desde: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    vigente_hasta: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Relaciones ORM
    paciente: Mapped["PacienteORM"] = relationship("PacienteORM", back_populates="responsables")
    responsable_usuario: Mapped["UsuarioORM"] = relationship("UsuarioORM")
    relacion: Mapped["RelacionResponsableORM"] = relationship("RelacionResponsableORM")

# Catálogo: relación Responsable ↔ Paciente
class RelacionResponsableORM(Base):
    __tablename__ = "relacion_responsable"
    __table_args__ = (UniqueConstraint("codigo", name="uq_relacion_responsable_codigo"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(Varchar(30), nullable=False)   # MADRE, PADRE, TIO, TIA, TUTOR, YO_MISMO, etc.
    descripcion: Mapped[str] = mapped_column(Varchar(100), nullable=False)


# Usuario (roles exclusivos)
class UsuarioORM(Base):
    __tablename__ = "usuarios"
    __table_args__ = (
        UniqueConstraint("email", name="uq_usuarios_email"),
        # Exclusividad: un usuario profesional no puede ser paciente ni responsable
        CheckConstraint(
            "NOT (es_profesional = TRUE AND (es_paciente = TRUE OR es_responsable = TRUE))",
            name="ck_usuario_roles_exclusivos"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    nombre: Mapped[str]   = mapped_column(Varchar(50), nullable=False)
    apellido: Mapped[str] = mapped_column(Varchar(50), nullable=False)
    email: Mapped[str]    = mapped_column(Varchar(50), nullable=False)  # único por uq
    celular: Mapped[str]  = mapped_column(Varchar(50), nullable=True)

    # roles
    es_paciente: Mapped[bool]     = mapped_column(Boolean, nullable=False, default=False)
    es_responsable: Mapped[bool]  = mapped_column(Boolean, nullable=False, default=False)
    es_profesional: Mapped[bool]  = mapped_column(Boolean, nullable=False, default=False)


# Profesional
class ProfesionalORM(Base):
    __tablename__ = "profesionales"
    __table_args__ = (UniqueConstraint("usuario_id", name="uq_profesional_usuario"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )

    # 1–a–1 con usuarios (contiene nombre, apellido, email, celular)
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("athome.usuarios.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Datos propios del profesional
    direccion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("athome.direccion.id"), nullable=False
    )
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    verificado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # (opcional) número visible/legacy
    matricula: Mapped[Optional[str]] = mapped_column(Varchar(50))

    # Relaciones
    usuario: Mapped["UsuarioORM"] = relationship("UsuarioORM")
    direccion: Mapped["DireccionORM"] = relationship("DireccionORM")

    especialidades: Mapped[List["EspecialidadORM"]] = relationship(
        "EspecialidadORM", secondary=profesional_especialidad, lazy="joined"
    )
    disponibilidades: Mapped[List["DisponibilidadORM"]] = relationship(
        "DisponibilidadORM", back_populates="profesional", cascade="all, delete-orphan"
    )
    publicaciones: Mapped[List["PublicacionORM"]] = relationship(
        "PublicacionORM", back_populates="profesional", cascade="all, delete-orphan"
    )
    matriculas: Mapped[List["MatriculaORM"]] = relationship(
        "MatriculaORM", back_populates="profesional", cascade="all, delete-orphan"
    )
    valoraciones: Mapped[List["ValoracionORM"]] = relationship(
        "ValoracionORM", back_populates="profesional", cascade="all, delete-orphan"
    )



# Disponibilidad (bloques de agenda)
class DisponibilidadORM(Base):
    __tablename__ = "disponibilidad"
    __table_args__ = (
        CheckConstraint("hora_inicio < hora_fin", name="ck_disp_horas"),
        Index("ix_disp_profesional", "profesional_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    profesional_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("athome.profesionales.id", ondelete="CASCADE"), nullable=False
    )
    # MVP: string "0,1,3" (L=0..D=6)
    dias_semana_text: Mapped[str] = mapped_column("dias_semana", Text, nullable=False)
    hora_inicio: Mapped[time] = mapped_column(Time, nullable=False)
    hora_fin: Mapped[time] = mapped_column(Time, nullable=False)

    profesional: Mapped["ProfesionalORM"] = relationship("ProfesionalORM", back_populates="disponibilidades")

    @property
    def dias_semana(self) -> List[str]:
        return [s for s in (self.dias_semana_text or "").split(",") if s]

    @dias_semana.setter
    def dias_semana(self, value: List[str]) -> None:
        self.dias_semana_text = ",".join(value or [])


# Publicación (anuncios del profesional)
class PublicacionORM(Base):
    __tablename__ = "publicaciones"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    profesional_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("athome.profesionales.id", ondelete="CASCADE"), nullable=False
    )
    especialidad_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("athome.especialidades.id_especialidad", ondelete="RESTRICT"), nullable=False
    )
    titulo: Mapped[str] = mapped_column(Text, nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    fecha_publicacion: Mapped[date] = mapped_column(Date, nullable=False)

    profesional: Mapped["ProfesionalORM"] = relationship("ProfesionalORM", back_populates="publicaciones")
    especialidad: Mapped["EspecialidadORM"] = relationship("EspecialidadORM")


# Responsable (familiar/tutor)
class ResponsableORM(Base):
    __tablename__ = "responsables"
    __table_args__ = (UniqueConstraint("usuario_id", name="uq_responsable_usuario"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )

    # 1–a–1 con usuarios (contiene nombre, apellido, email, celular)
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("athome.usuarios.id", ondelete="CASCADE"),
        nullable=False,
    )

    direccion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("athome.direccion.id"), nullable=False
    )
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    usuario: Mapped["UsuarioORM"] = relationship("UsuarioORM")
    direccion: Mapped["DireccionORM"] = relationship("DireccionORM")


# Paciente
class PacienteORM(Base):
    __tablename__ = "pacientes"
    __table_args__ = (UniqueConstraint("usuario_id", name="uq_paciente_usuario"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )

    # 1–a–1 con usuarios (contiene nombre, apellido, email, celular)
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("athome.usuarios.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Datos propios del paciente
    fecha_nacimiento: Mapped[date] = mapped_column(Date, nullable=False)
    notas: Mapped[str] = mapped_column(Text, nullable=False)

    # Domicilio
    direccion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("athome.direccion.id"), nullable=False
    )

    # Relación N:M con responsables (a través de la tabla vínculo)
    responsables: Mapped[List["PacienteResponsableORM"]] = relationship(
        "PacienteResponsableORM",
        back_populates="paciente",
        cascade="all, delete-orphan",
    )

    # Conveniencia: autoresponsable si hay vínculo YO_MISMO
    @property
    def es_autoresponsable(self) -> bool:
        return any(
            pr.responsable_usuario_id == self.usuario_id and getattr(pr.relacion, "codigo", None) == "YO_MISMO"
            for pr in (self.responsables or [])
        )


# Estados de consulta
class EstadoConsultaORM(Base):
    __tablename__ = "estado_consulta"
    __table_args__ = (UniqueConstraint("codigo", name="uq_estado_consulta_codigo"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # valores esperados: "PENDIENTE", "CONFIRMADA", "CANCELADA", "COMPLETADA"
    codigo: Mapped[str] = mapped_column(Varchar(20), nullable=False)
    descripcion: Mapped[str] = mapped_column(Varchar(100), nullable=False)

# Consulta + Evento
class ConsultaORM(Base):
    __tablename__ = "consultas"
    __table_args__ = (
        CheckConstraint("hora_inicio < hora_fin", name="ck_consulta_horas"),
        Index("ix_consulta_profesional", "profesional_id"),
        Index("ix_consulta_paciente", "paciente_id"),
        Index("ix_consulta_fecha", "fecha"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))

    paciente_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("athome.pacientes.id", ondelete="CASCADE"), nullable=False
    )
    profesional_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("athome.profesionales.id", ondelete="CASCADE"), nullable=False
    )
    direccion_servicio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("athome.direccion.id"), nullable=False
    )

    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    hora_inicio: Mapped[time] = mapped_column(Time, nullable=False)
    hora_fin: Mapped[time] = mapped_column(Time, nullable=False)

    estado_id: Mapped[int] = mapped_column(Integer, ForeignKey("athome.estado_consulta.id"), nullable=False)

    notas: Mapped[str] = mapped_column(Text, nullable=False)

    paciente: Mapped["PacienteORM"] = relationship("PacienteORM")
    profesional: Mapped["ProfesionalORM"] = relationship("ProfesionalORM")
    direccion_servicio: Mapped["DireccionORM"] = relationship("DireccionORM")
    estado: Mapped["EstadoConsultaORM"] = relationship("EstadoConsultaORM")

    eventos: Mapped[List["EventoORM"]] = relationship("EventoORM", back_populates="consulta", cascade="all, delete-orphan")


class EventoORM(Base):
    __tablename__ = "eventos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    consulta_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("athome.consultas.id", ondelete="CASCADE"), nullable=False
    )

    tipo: Mapped[str] = mapped_column(Varchar(20), nullable=False)   # guarda los valores de TipoEvento
    datos: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    consulta: Mapped["ConsultaORM"] = relationship("ConsultaORM", back_populates="eventos")


# Matrícula (policy de provincia + vigencia)
class MatriculaORM(Base):
    __tablename__ = "matriculas"
    __table_args__ = (
        UniqueConstraint("profesional_id", "provincia_id", "nro_matricula", name="uq_matricula_prof_prov_nro"),
        CheckConstraint("vigente_hasta >= vigente_desde", name="ck_matricula_fechas"),
        Index("ix_matricula_profesional", "profesional_id"),
        Index("ix_matricula_provincia", "provincia_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))

    profesional_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("athome.profesionales.id", ondelete="CASCADE"), nullable=False
    )
    provincia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("athome.provincia.id", ondelete="RESTRICT"), nullable=False
    )

    nro_matricula: Mapped[str] = mapped_column(Varchar(50), nullable=False)

    vigente_desde: Mapped[date] = mapped_column(Date, nullable=False)
    vigente_hasta: Mapped[date] = mapped_column(Date, nullable=False)  # ← NOT NULL

    profesional: Mapped["ProfesionalORM"] = relationship("ProfesionalORM", back_populates="matriculas")
    provincia: Mapped["ProvinciaORM"] = relationship("ProvinciaORM")


# Valoración
class ValoracionORM(Base):
    __tablename__ = "valoraciones"
    __table_args__ = (
        CheckConstraint("puntuacion BETWEEN 1 AND 5", name="ck_valoracion_rango"),
        Index("ix_valoracion_profesional", "profesional_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    profesional_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("athome.profesionales.id", ondelete="CASCADE"), nullable=False
    )
    paciente_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("athome.pacientes.id", ondelete="CASCADE"), nullable=False
    )
    puntuacion: Mapped[int] = mapped_column(Integer, nullable=False)
    comentario: Mapped[Optional[str]] = mapped_column(Text)
    creado_en: Mapped[date] = mapped_column(Date, nullable=False, server_default=text("CURRENT_DATE"))

    profesional: Mapped["ProfesionalORM"] = relationship("ProfesionalORM", back_populates="valoraciones")
    paciente: Mapped["PacienteORM"] = relationship("PacienteORM")



__all__ = [
    # base
    "Base",
    # ubicación
    "ProvinciaORM",
    "DepartamentoORM",
    "BarrioORM",
    "DireccionORM",
    # usuarios / perfiles / catálogos
    "UsuarioORM",
    "RelacionResponsableORM",
    "PacienteResponsableORM",
    "PacienteORM",
    "ResponsableORM",
    "ProfesionalORM",
    # catálogos de servicio
    "EspecialidadORM",
    # relaciones y flujos
    "profesional_especialidad",
    "DisponibilidadORM",
    "PublicacionORM",
    "EstadoConsultaORM",
    "ConsultaORM",
    "EventoORM",
    "MatriculaORM",
    "ValoracionORM",
]

