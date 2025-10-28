from __future__ import annotations

import uuid
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import UniqueConstraint, ForeignKey, text, Integer
from sqlalchemy.dialects.postgresql import UUID, VARCHAR as Varchar
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SCHEMA
from .servicios import profesional_especialidad  # tabla puente profesional<->especialidad

if TYPE_CHECKING:
    from .usuarios import UsuarioORM
    from .ubicacion import DireccionORM
    from .servicios import EspecialidadORM
    from .agenda import DisponibilidadORM, ConsultaORM
    from .publicaciones import PublicacionORM
    from .matriculas import MatriculaORM
    from .valoraciones import ValoracionORM
    from .paciente import PacienteORM


class ProfesionalORM(Base):
    __tablename__ = "profesional"
    __table_args__ = (
        UniqueConstraint("usuario_id", name="uq_profesional_usuario"),
        {"schema": SCHEMA},
    )

    # PK
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    # FK al dueño de la cuenta (usuario)
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.usuario.id", ondelete="CASCADE"),
        nullable=False,
    )

    direccion_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.direccion.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Atributos de estado
    activo: Mapped[bool] = mapped_column(nullable=False, server_default=text("true"))
    verificado: Mapped[bool] = mapped_column(nullable=False, server_default=text("false"))

    # Campo libre/legacy si necesitás almacenar un número simple además del esquema de Matricula
    matricula: Mapped[Optional[str]] = mapped_column(Varchar(50), nullable=True)

    # Relaciones principales
    usuario: Mapped["UsuarioORM"] = relationship("UsuarioORM")
    direccion: Mapped[Optional["DireccionORM"]] = relationship("DireccionORM")

    # Muchas especialidades vía tabla puente
    especialidades: Mapped[List["EspecialidadORM"]] = relationship(
        "EspecialidadORM",
        secondary=profesional_especialidad,
        lazy="joined",
        back_populates="profesionales",  # asegurate de definir esto en EspecialidadORM
    )

    # Disponibilidades (agenda base del profesional)
    disponibilidades: Mapped[List["DisponibilidadORM"]] = relationship(
        "DisponibilidadORM",
        back_populates="profesional",
        cascade="all, delete-orphan",
    )

    # Publicaciones/ofertas del profesional
    publicaciones: Mapped[List["PublicacionORM"]] = relationship(
        "PublicacionORM",
        back_populates="profesional",
        cascade="all, delete-orphan",
    )

    # Matrículas (por provincia + vigencia)
    matriculas: Mapped[List["MatriculaORM"]] = relationship(
        "MatriculaORM",
        back_populates="profesional",
        cascade="all, delete-orphan",
    )

    # Valoraciones recibidas
    valoraciones: Mapped[List["ValoracionORM"]] = relationship(
        "ValoracionORM",
        back_populates="profesional",
        cascade="all, delete-orphan",
    )

    # Consultas del profesional
    consultas: Mapped[List["ConsultaORM"]] = relationship(
        "ConsultaORM",
        back_populates="profesional",
        cascade="all, delete-orphan",
    )


class SolicitanteORM(Base):
    __tablename__ = "solicitante"
    __table_args__ = (
        UniqueConstraint("usuario_id", name="uq_solicitante_usuario"),
        {"schema": SCHEMA},
    )

    # PK
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    # FK a usuario (dueño de la cuenta)
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.usuario.id", ondelete="CASCADE"),
        nullable=False,
    )

    direccion_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.direccion.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Estado
    activo: Mapped[bool] = mapped_column(nullable=False, server_default=text("true"))

    # Relaciones
    usuario: Mapped["UsuarioORM"] = relationship("UsuarioORM")
    direccion: Mapped[Optional["DireccionORM"]] = relationship("DireccionORM")

    # 1–1 actual: un solicitante tiene a lo sumo un paciente
    paciente: Mapped[Optional["PacienteORM"]] = relationship(
        "PacienteORM",
        back_populates="solicitante",
        uselist=False,
        cascade="all, delete-orphan",
    )
