from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import date

from app.domain.entities.usuarios import Paciente
from app.domain.value_objects.objetos_valor import Ubicacion
from app.infra.persistence.paciente import PacienteORM
from app.infra.persistence.ubicacion import DireccionORM
from app.infra.repositories.direccion_repository import DireccionRepository


class PacienteRepository:
    """
    Repositorio para gestionar la persistencia de Pacientes.
    Implementa el patrón Repository para abstraer el acceso a datos.
    """

    def __init__(self, session: Session):
        self.session = session
        self.direccion_repo = DireccionRepository(session)

    def _to_domain(self, orm: PacienteORM) -> Paciente:
        """
        Convierte un modelo ORM a entidad de dominio.

        Args:
            orm: Modelo ORM del paciente

        Returns:
            Entidad Paciente del dominio
        """
        # Obtener ubicación si existe
        ubicacion = None
        if orm.direccion_id:
            direccion_orm = (
                self.session.query(DireccionORM)
                .filter(DireccionORM.id == orm.direccion_id)
                .first()
            )

            if direccion_orm:
                # Reutilizar el método del DireccionRepository
                ubicacion = self.direccion_repo._to_domain(direccion_orm)

        # Si no hay dirección, crear una ubicación vacía
        if ubicacion is None:
            ubicacion = Ubicacion(
                provincia="", departamento="", barrio="", calle="", numero=""
            )

        return Paciente(
            id=orm.id,
            nombre=orm.nombre,
            apellido=orm.apellido,
            ubicacion=ubicacion,
            solicitante_id=orm.solicitante_id,
            relacion=orm.relacion.nombre if orm.relacion else "self",
            fecha_nacimiento=orm.fecha_nacimiento or date(2000, 1, 1),
            notas=orm.notas or "",
        )

    def _to_orm(
        self, paciente: Paciente, solicitante_id: UUID, orm: PacienteORM = None
    ) -> PacienteORM:
        """
        Convierte una entidad de dominio a modelo ORM.

        Args:
            paciente: Entidad Paciente del dominio
            solicitante_id: UUID del solicitante responsable
            orm: Modelo ORM existente (para actualización)

        Returns:
            Modelo ORM del paciente
        """
        if orm is None:
            # Crear nuevo ORM
            orm = PacienteORM(
                id=paciente.id,
                nombre=paciente.nombre,
                apellido=paciente.apellido,
                fecha_nacimiento=paciente.fecha_nacimiento,
                notas=paciente.notas,
                solicitante_id=solicitante_id,
            )
        else:
            # Actualizar ORM existente
            orm.nombre = paciente.nombre
            orm.apellido = paciente.apellido
            orm.fecha_nacimiento = paciente.fecha_nacimiento
            orm.notas = paciente.notas
            # No actualizamos solicitante_id en update (es inmutable)

        return orm

    def obtener_por_id(self, id: UUID) -> Optional[Paciente]:
        """
        Obtiene un paciente por su ID.

        Args:
            id: UUID del paciente

        Returns:
            Paciente o None si no existe
        """
        orm = (
            self.session.query(PacienteORM)
            .filter(PacienteORM.id == id)
            .first()
        )

        return self._to_domain(orm) if orm else None

    def listar_todos(self, limite: int = 100) -> List[Paciente]:
        """
        Lista todos los pacientes.

        Args:
            limite: Número máximo de pacientes a retornar

        Returns:
            Lista de pacientes
        """
        orms = self.session.query(PacienteORM).limit(limite).all()
        return [self._to_domain(orm) for orm in orms]

    def listar_por_solicitante(self, solicitante_id: UUID) -> List[Paciente]:
        """
        Lista los pacientes de un solicitante.

        Args:
            solicitante_id: UUID del solicitante

        Returns:
            Lista de pacientes
        """
        orms = (
            self.session.query(PacienteORM)
            .filter(PacienteORM.solicitante_id == solicitante_id)
            .all()
        )

        return [self._to_domain(orm) for orm in orms]

    def buscar_por_nombre(
        self, nombre: str, apellido: str = None
    ) -> List[Paciente]:
        """
        Busca pacientes por nombre y opcionalmente por apellido.

        Args:
            nombre: Nombre del paciente
            apellido: Apellido del paciente (opcional)

        Returns:
            Lista de pacientes que coinciden
        """
        query = self.session.query(PacienteORM).filter(
            PacienteORM.nombre.ilike(f"%{nombre}%")
        )

        if apellido:
            query = query.filter(PacienteORM.apellido.ilike(f"%{apellido}%"))

        orms = query.all()
        return [self._to_domain(orm) for orm in orms]

    def crear(
        self,
        paciente: Paciente,
        solicitante_id: UUID,
        direccion_id: Optional[UUID] = None,
    ) -> Paciente:
        """
        Crea un nuevo paciente en la base de datos.

        Args:
            paciente: Entidad Paciente del dominio
            solicitante_id: UUID del solicitante responsable
            direccion_id: (Opcional) ID de dirección existente.
                         Si no se proporciona y el paciente tiene ubicación,
                         se crea automáticamente usando DireccionRepository.

        Returns:
            Paciente creado con datos actualizados

        Example:
            # Opción 1: Con dirección existente
            paciente_repo.crear(paciente, solicitante_id, direccion_id=uuid_existente)

            # Opción 2: Crear dirección automáticamente
            paciente.ubicacion = Ubicacion(...)
            paciente_repo.crear(paciente, solicitante_id)  # Crea la dirección
        """
        # Si no se proporciona direccion_id, intentar crear desde ubicacion
        if direccion_id is None and paciente.ubicacion:
            # Crear dirección usando DireccionRepository
            direccion_orm = self.direccion_repo.crear_con_jerarquia(
                paciente.ubicacion
            )
            direccion_id = direccion_orm.id

        # Crear el paciente ORM
        orm = self._to_orm(paciente, solicitante_id)
        orm.direccion_id = direccion_id

        self.session.add(orm)
        self.session.commit()
        self.session.refresh(orm)

        return self._to_domain(orm)

    def actualizar(
        self, paciente: Paciente, direccion_id: Optional[UUID] = None
    ) -> Optional[Paciente]:
        """
        Actualiza un paciente existente.

        Args:
            paciente: Entidad Paciente con datos actualizados
            direccion_id: (Opcional) Nueva dirección existente.
                         Si no se proporciona pero paciente.ubicacion cambió,
                         se crea automáticamente.

        Returns:
            Paciente actualizado o None si no existe

        Example:
            # Opción 1: Actualizar solo datos básicos
            paciente.nombre = "Juan Carlos"
            paciente_repo.actualizar(paciente)

            # Opción 2: Cambiar a dirección existente
            paciente_repo.actualizar(paciente, direccion_id=nueva_direccion_id)

            # Opción 3: Cambiar ubicación (crea dirección automáticamente)
            paciente.ubicacion = Ubicacion(...)
            paciente_repo.actualizar(paciente)  # Crea nueva dirección
        """
        orm = (
            self.session.query(PacienteORM)
            .filter(PacienteORM.id == paciente.id)
            .first()
        )

        if not orm:
            return None

        # Manejar actualización de dirección
        if direccion_id:
            # Dirección explícita proporcionada
            orm.direccion_id = direccion_id
        elif paciente.ubicacion:
            # Verificar si la ubicación cambió
            ubicacion_actual = None
            if orm.direccion_id:
                direccion_orm = (
                    self.session.query(DireccionORM)
                    .filter(DireccionORM.id == orm.direccion_id)
                    .first()
                )
                if direccion_orm:
                    ubicacion_actual = self.direccion_repo._to_domain(
                        direccion_orm
                    )

            if ubicacion_actual != paciente.ubicacion:
                # La ubicación cambió, crear nueva dirección
                nueva_direccion = self.direccion_repo.crear_con_jerarquia(
                    paciente.ubicacion
                )
                orm.direccion_id = nueva_direccion.id

        # Actualizar campos básicos usando solicitante_id existente
        orm = self._to_orm(paciente, orm.solicitante_id, orm)

        self.session.commit()
        self.session.refresh(orm)

        return self._to_domain(orm)

    def eliminar(self, id: UUID) -> bool:
        """
        Elimina un paciente (hard delete).

        Args:
            id: UUID del paciente

        Returns:
            True si se eliminó, False si no existía
        """
        orm = (
            self.session.query(PacienteORM)
            .filter(PacienteORM.id == id)
            .first()
        )

        if not orm:
            return False

        self.session.delete(orm)
        self.session.commit()
        return True

    def contar_pacientes(self, solicitante_id: UUID = None) -> int:
        """
        Cuenta el número de pacientes.

        Args:
            solicitante_id: Si se especifica, cuenta solo los pacientes de ese solicitante

        Returns:
            Número de pacientes
        """
        query = self.session.query(PacienteORM)

        if solicitante_id:
            query = query.filter(PacienteORM.solicitante_id == solicitante_id)

        return query.count()
