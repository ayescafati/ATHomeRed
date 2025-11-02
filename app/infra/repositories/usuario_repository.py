"""
Repository para operaciones CRUD de usuarios (autenticación).
"""

from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.infra.persistence.usuarios import UsuarioORM


class UsuarioRepository:
    """
    Repositorio para gestionar usuarios en el contexto de autenticación.

    TODO: Implementar métodos para:
    - Crear usuario con password hash
    - Buscar por email
    - Actualizar último login
    - Gestionar bloqueos por intentos fallidos
    """

    def __init__(self, db: Session):
        self.db = db

    # CRUD BÁSICO

    def crear_usuario(
        self,
        email: str,
        password_hash: str,
        nombre: str,
        apellido: str,
        celular: Optional[str] = None,
        es_profesional: bool = False,
        es_solicitante: bool = True,
    ) -> UsuarioORM:
        """
        Crea un nuevo usuario con contraseña hasheada.

        TODO: Implementar
        - Validar que email no exista
        - Crear UsuarioORM con los datos
        - Guardar en DB
        - Retornar usuario creado

        IMPORTANTE: NO hashear la password aquí, debe venir ya hasheada.
        """
        raise NotImplementedError("TODO: Implementar crear_usuario")

    def obtener_por_email(self, email: str) -> Optional[UsuarioORM]:
        """
        Busca un usuario por su email.

        TODO: Implementar
        - Buscar usuario donde email = email
        - Retornar usuario o None
        """
        raise NotImplementedError("TODO: Implementar obtener_por_email")

    def obtener_por_id(self, usuario_id: int) -> Optional[UsuarioORM]:
        """
        Busca un usuario por su ID.

        TODO: Implementar
        - Buscar usuario por ID
        - Retornar usuario o None
        """
        raise NotImplementedError("TODO: Implementar obtener_por_id")

    def actualizar_password(
        self, usuario_id: int, nuevo_password_hash: str
    ) -> bool:
        """
        Actualiza la contraseña de un usuario.

        TODO: Implementar
        - Buscar usuario por ID
        - Actualizar password_hash
        - Guardar cambios
        - Retornar True si exitoso
        """
        raise NotImplementedError("TODO: Implementar actualizar_password")

    # AUTENTICACIÓN

    def actualizar_ultimo_login(self, usuario_id: int) -> bool:
        """
        Actualiza la fecha de último login.

        TODO: Implementar
        - Buscar usuario
        - Actualizar ultimo_login = datetime.utcnow()
        - Resetear intentos_fallidos = 0
        - Guardar cambios
        """
        raise NotImplementedError("TODO: Implementar actualizar_ultimo_login")

    def incrementar_intentos_fallidos(self, email: str) -> int:
        """
        Incrementa el contador de intentos fallidos.

        TODO: Implementar
        - Buscar usuario por email
        - Incrementar intentos_fallidos
        - Si intentos >= 5, bloquear_hasta = now + 15 minutos
        - Guardar cambios
        - Retornar cantidad de intentos
        """
        raise NotImplementedError(
            "TODO: Implementar incrementar_intentos_fallidos"
        )

    def resetear_intentos_fallidos(self, usuario_id: int) -> bool:
        """
        Resetea el contador de intentos fallidos a 0.

        TODO: Implementar
        - Buscar usuario
        - intentos_fallidos = 0
        - bloqueado_hasta = None
        - Guardar cambios
        """
        raise NotImplementedError(
            "TODO: Implementar resetear_intentos_fallidos"
        )

    def esta_bloqueado(self, email: str) -> bool:
        """
        Verifica si un usuario está bloqueado por intentos fallidos.

        TODO: Implementar
        - Buscar usuario por email
        - Si bloqueado_hasta es None: return False
        - Si bloqueado_hasta > datetime.utcnow(): return True
        - Si bloqueado_hasta <= datetime.utcnow(): desbloquear y return False
        """
        raise NotImplementedError("TODO: Implementar esta_bloqueado")

    # ==================== VERIFICACIÓN ====================

    def marcar_como_verificado(self, usuario_id: int) -> bool:
        """
        Marca un usuario como verificado (email confirmado).

        TODO: Implementar
        - Buscar usuario
        - verificado = True
        - Guardar cambios
        """
        raise NotImplementedError("TODO: Implementar marcar_como_verificado")

    def activar_desactivar(self, usuario_id: int, activo: bool) -> bool:
        """
        Activa o desactiva un usuario.

        TODO: Implementar
        - Buscar usuario
        - activo = activo
        - Guardar cambios
        """
        raise NotImplementedError("TODO: Implementar activar_desactivar")
