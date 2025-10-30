"""
Repository para operaciones de autenticación y gestión de tokens.
"""
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.infra.persistence.auth import RefreshTokenORM, AuditoriaLoginORM
from app.infra.persistence.usuarios import UsuarioORM


class AuthRepository:
    """
    Repositorio para gestionar autenticación, tokens y auditoría.
    
    TODO: Implementar métodos para:
    - Crear y validar refresh tokens
    - Revocar tokens
    - Registrar intentos de login
    - Limpiar tokens expirados
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    # REFRESH TOKENS
    
    def crear_refresh_token(
        self, 
        usuario_id: int, 
        token: str, 
        expira_en: datetime,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> RefreshTokenORM:
        """
        Crea un nuevo refresh token para el usuario.
        
        TODO: Implementar
        - Crear RefreshTokenORM
        - Guardar en DB
        - Retornar el token creado
        """
        raise NotImplementedError("TODO: Implementar crear_refresh_token")
    
    def obtener_refresh_token(self, token: str) -> Optional[RefreshTokenORM]:
        """
        Busca un refresh token por su valor.
        
        TODO: Implementar
        - Buscar token en DB
        - Verificar que no esté revocado
        - Verificar que no esté expirado
        """
        raise NotImplementedError("TODO: Implementar obtener_refresh_token")
    
    def revocar_refresh_token(self, token: str) -> bool:
        """
        Revoca un refresh token (logout).
        
        TODO: Implementar
        - Buscar token
        - Marcar como revocado=True
        - Guardar cambios
        """
        raise NotImplementedError("TODO: Implementar revocar_refresh_token")
    
    def revocar_todos_tokens_usuario(self, usuario_id: int) -> int:
        """
        Revoca todos los tokens de un usuario (logout de todas las sesiones).
        
        TODO: Implementar
        - Buscar todos los tokens del usuario
        - Marcar todos como revocados
        - Retornar cantidad de tokens revocados
        """
        raise NotImplementedError("TODO: Implementar revocar_todos_tokens_usuario")
    
    def limpiar_tokens_expirados(self) -> int:
        """
        Elimina tokens expirados de la DB (tarea de mantenimiento).
        
        TODO: Implementar
        - Buscar tokens donde expira_en < datetime.utcnow()
        - Eliminar de DB
        - Retornar cantidad eliminada
        """
        raise NotImplementedError("TODO: Implementar limpiar_tokens_expirados")
    
    # AUDITORÍA
    
    def registrar_intento_login(
        self,
        email: str,
        exitoso: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        motivo: Optional[str] = None
    ) -> AuditoriaLoginORM:
        """
        Registra un intento de login en la tabla de auditoría.
        
        TODO: Implementar
        - Crear AuditoriaLoginORM
        - Guardar en DB
        - Retornar el registro
        """
        raise NotImplementedError("TODO: Implementar registrar_intento_login")
    
    def obtener_intentos_fallidos_recientes(
        self, 
        email: str, 
        minutos: int = 15
    ) -> int:
        """
        Cuenta intentos de login fallidos en los últimos X minutos.
        
        TODO: Implementar
        - Buscar intentos fallidos del email
        - Filtrar por fecha (últimos X minutos)
        - Contar y retornar
        
        Útil para: Detectar ataques de fuerza bruta
        """
        raise NotImplementedError("TODO: Implementar obtener_intentos_fallidos_recientes")
