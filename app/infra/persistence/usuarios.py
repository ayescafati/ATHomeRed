from __future__ import annotations
import uuid
from typing import Optional
from sqlalchemy import UniqueConstraint, CheckConstraint, text
from sqlalchemy.dialects.postgresql import UUID, VARCHAR as Varchar
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, SCHEMA

class UsuarioORM(Base):
    __tablename__ = "usuario"
    __table_args__ = (
        UniqueConstraint("email", name="uq_usuario_email"),
        CheckConstraint(
            "NOT (es_profesional = TRUE AND es_solicitante = TRUE)",
            name="ck_usuario_roles_exclusivos",
        ),
        CheckConstraint(
            "(es_profesional = TRUE) OR (es_solicitante = TRUE)",
            name="ck_usuario_al_menos_un_rol",
        ),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    nombre: Mapped[str] = mapped_column(Varchar(50), nullable=False)
    apellido: Mapped[str] = mapped_column(Varchar(50), nullable=False)
    email: Mapped[str] = mapped_column(Varchar(50), nullable=False)
    celular: Mapped[Optional[str]] = mapped_column(Varchar(50))

    es_solicitante: Mapped[bool] = mapped_column(default=True, nullable=False)
    es_profesional: Mapped[bool] = mapped_column(default=False, nullable=False)

