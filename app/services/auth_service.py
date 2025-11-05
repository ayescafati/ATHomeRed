"""
Servicio de autenticación - Lógica de negocio para auth.
"""
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# TODO: Instalar dependencias
# pip install python-jose[cryptography] passlib[bcrypt] python-multipart


class AuthService:
    """
    Servicio con la lógica de negocio de autenticación.
    
    TODO: Implementar:
    - Hash y verificación de contraseñas (bcrypt)
    - Generación y validación de JWT
    - Registro de usuarios
    - Login/Logout
    - Refresh de tokens
    """
    
    def __init__(self, db: Session):
        self.db = db
        # TODO: Inyectar AuthRepository y UsuarioRepository
        # self.auth_repo = AuthRepository(db)
        # self.usuario_repo = UsuarioRepository(db)
    
    # PASSWORD HASHING
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hashea una contraseña usando bcrypt.
        
        TODO: Implementar
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)
        """
        raise NotImplementedError("TODO: Implementar hash_password con bcrypt")
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verifica si una contraseña coincide con el hash.
        
        TODO: Implementar
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(plain_password, hashed_password)
        """
        raise NotImplementedError("TODO: Implementar verify_password con bcrypt")
    
    # JWT TOKENS
    
    @staticmethod
    def crear_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Crea un JWT access token.
        
        TODO: Implementar
        from jose import jwt
        
        - Copiar data
        - Agregar exp (expiration time)
        - Codificar con jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        - Retornar token
        
        Data debe incluir: {"sub": user_id, "email": email, "roles": [...]}
        """
        raise NotImplementedError("TODO: Implementar crear_access_token con JWT")
    
    @staticmethod
    def validar_access_token(token: str) -> Optional[dict]:
        """
        Valida y decodifica un JWT access token.
        
        TODO: Implementar
        from jose import jwt, JWTError
        
        - Decodificar token con jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        - Verificar que tenga "sub" (user_id)
        - Retornar payload o None si es inválido
        """
        raise NotImplementedError("TODO: Implementar validar_access_token")
    
    # REGISTRO
    
    def registrar_usuario(
        self,
        email: str,
        password: str,
        nombre: str,
        apellido: str,
        celular: Optional[str] = None,
        es_profesional: bool = False
    ) -> dict:
        """
        Registra un nuevo usuario.
        
        TODO: Implementar
        1. Validar que email no exista (usuario_repo.obtener_por_email)
        2. Hashear password (hash_password)
        3. Crear usuario (usuario_repo.crear_usuario)
        4. TODO OPCIONAL: Enviar email de verificación
        5. Retornar {"success": True, "usuario_id": ...}
        """
        raise NotImplementedError("TODO: Implementar registrar_usuario")
    
    # LOGIN
    
    def login(
        self, 
        email: str, 
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> dict:
        """
        Autentica un usuario.
        
        TODO: Implementar
        1. Verificar si está bloqueado (usuario_repo.esta_bloqueado)
        2. Buscar usuario por email (usuario_repo.obtener_por_email)
        3. Verificar password (verify_password)
        4. Si es correcto:
           - Actualizar último login
           - Resetear intentos fallidos
           - Generar access_token y refresh_token
           - Guardar refresh_token en DB
           - Registrar auditoría exitosa
           - Retornar {"access_token": ..., "refresh_token": ..., "token_type": "bearer"}
        5. Si es incorrecto:
           - Incrementar intentos fallidos
           - Registrar auditoría fallida
           - Lanzar excepción
        """
        raise NotImplementedError("TODO: Implementar login")
    
    # LOGOUT
    
    def logout(self, refresh_token: str) -> bool:
        """
        Cierra sesión revocando el refresh token.
        
        TODO: Implementar
        - Revocar refresh_token (auth_repo.revocar_refresh_token)
        - Retornar True si exitoso
        """
        raise NotImplementedError("TODO: Implementar logout")
    
    # REFRESH TOKEN
    
    def refresh_access_token(self, refresh_token: str) -> dict:
        """
        Genera un nuevo access token usando un refresh token.
        
        TODO: Implementar
        1. Obtener refresh_token de DB (auth_repo.obtener_refresh_token)
        2. Validar que no esté revocado ni expirado
        3. Buscar usuario asociado
        4. Generar nuevo access_token
        5. Retornar {"access_token": ..., "token_type": "bearer"}
        """
        raise NotImplementedError("TODO: Implementar refresh_access_token")
