"""
Policies de integridad de negocio
Validaciones que garantizan la consistencia de la lógica de dominio
"""

from uuid import UUID
from sqlalchemy.orm import Session
from app.infra.persistence.usuarios import UsuarioORM
from app.infra.persistence.paciente import PacienteORM
from app.infra.persistence.perfiles import ProfesionalORM
from app.api.exceptions import (
    ResourceNotFoundException,
    ForbiddenException,
)
from sqlalchemy import select


class IntegrityPolicies:
    """Policies de integridad para validar reglas de negocio"""

    @staticmethod
    def validar_usuario_activo(session: Session, usuario_id: UUID) -> UsuarioORM:
        """
        Policy 1: Solo usuarios ACTIVOS pueden operar en el sistema

        Raises:
            ForbiddenException: Si el usuario está inactivo
            ResourceNotFoundException: Si el usuario no existe
        """
        usuario = session.execute(
            select(UsuarioORM).where(UsuarioORM.id == usuario_id)
        ).scalar_one_or_none()

        if not usuario:
            raise ResourceNotFoundException(f"Usuario {usuario_id} no encontrado")

        if not usuario.activo:
            raise ForbiddenException(f"Usuario {usuario_id} está inactivo")

        return usuario

    @staticmethod
    def validar_profesional_disponible(
        session: Session, profesional_id: UUID
    ) -> ProfesionalORM:
        """
        Policy 2: Solo profesionales VERIFICADOS y ACTIVOS pueden tener citas

        Raises:
            ResourceNotFoundException: Si el profesional no existe
            ForbiddenException: Si no está activo o verificado
        """
        profesional = session.execute(
            select(ProfesionalORM).where(ProfesionalORM.id == profesional_id)
        ).scalar_one_or_none()

        if not profesional:
            raise ResourceNotFoundException(
                f"Profesional {profesional_id} no encontrado"
            )

        if not profesional.activo:
            raise ForbiddenException(f"Profesional {profesional_id} no está activo")

        if not profesional.verificado:
            raise ForbiddenException(f"Profesional {profesional_id} no está verificado")

        return profesional

    @staticmethod
    def validar_solicitante_es_dueno(
        session: Session, paciente_id: UUID, solicitante_id: UUID
    ) -> PacienteORM:
        """
        Policy 3: Solo el solicitante DUEÑO del paciente puede crear citas para ese paciente

        Validación de permisos: Solicitante → Paciente (1-a-1)

        Raises:
            ResourceNotFoundException: Si el paciente no existe
            ForbiddenException: Si el solicitante no es el dueño del paciente
        """
        paciente = session.execute(
            select(PacienteORM).where(PacienteORM.id == paciente_id)
        ).scalar_one_or_none()

        if not paciente:
            raise ResourceNotFoundException(f"Paciente {paciente_id} no encontrado")

        if paciente.solicitante_id != solicitante_id:
            raise ForbiddenException(
                f"Solicitante {solicitante_id} no es el dueño del paciente {paciente_id}"
            )

        return paciente

    @staticmethod
    def validar_paciente_existe(session: Session, paciente_id: UUID) -> PacienteORM:
        """Valida que un paciente existe (sin policy de permisos)"""
        paciente = session.execute(
            select(PacienteORM).where(PacienteORM.id == paciente_id)
        ).scalar_one_or_none()

        if not paciente:
            raise ResourceNotFoundException(f"Paciente {paciente_id} no encontrado")

        return paciente
