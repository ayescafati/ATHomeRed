"""
Servicio de autenticación: lógica de negocio mínima pero funcional.

- Hasheamos contraseñas con Argon2 y verificamos con passlib.
- Armamos y validamos JWTs (HS256) para sesiones cortas.
- Registramos usuarios y manejamos el login con control de intentos fallidos.
"""

from typing import Optional
from datetime import datetime, timedelta
import os

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError

from app.infra.repositories.usuario_repository import UsuarioRepository

# Config de seguridad

# Elegimos HS256 para el MVP; en producción cuidamos bien el SECRET_KEY.
ALGORITHM = "HS256"

# Tomamos la clave del entorno; si falta, usamos un default solo para dev.
SECRET_KEY = os.getenv("AT_HOME_RED_SECRET", "dev-secret-change-me")

# Definimos un TTL corto para el access token (en minutos).
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
)

# Optamos por Argon2 para evitar líos de bcrypt en algunos Windows.
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class AuthService:
    """Encapsulamos la lógica de autenticación en un servicio."""

    def __init__(self, db: Session):
        # Guardamos la sesión y armamos el repo de usuarios a partir de ella.
        self.db = db
        self.usuario_repo = UsuarioRepository(db)

    # PASSWORD HASHING

    @staticmethod
    def hash_password(password: str) -> str:
        """Devolvemos el hash Argon2 de la contraseña."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verificamos si la contraseña en texto coincide con el hash Argon2."""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            # Preferimos responder False ante cualquier excepción por seguridad.
            return False

    # JWT TOKENS

    @staticmethod
    def crear_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Creamos un JWT con expiración usando SECRET_KEY y HS256.

        `data` suele traer: {"sub": user_id, "email": email, "roles": [...]}"""
        to_encode = data.copy()
        expire = datetime.utcnow() + (
            expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire})
        token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return token

    @staticmethod
    def validar_access_token(token: str) -> Optional[dict]:
        """Decodificamos el JWT y devolvemos el payload, o None si no va."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if not payload.get("sub"):
                return None
            return payload
        except JWTError:
            return None

    # REGISTRO

    def registrar_usuario(
        self,
        email: str,
        password: str,
        nombre: str,
        apellido: str,
        celular: Optional[str] = None,
        es_profesional: bool = False,
        es_solicitante: bool = True,
    ) -> dict:
        """Registramos un usuario nuevo y devolvemos datos básicos para la API/UI."""
        # Mantenemos roles excluyentes y garantizamos al menos uno.
        if es_profesional and es_solicitante:
            raise ValueError(
                "Un usuario no puede ser profesional y solicitante a la vez"
            )
        if not es_profesional and not es_solicitante:
            # Para el MVP preferimos default a solicitante.
            es_solicitante = True

        # Verificamos unicidad de email.
        if self.usuario_repo.obtener_por_email(email):
            raise ValueError("El email ya está registrado")

        # Hasheamos la contraseña antes de persistir.
        password_hash = self.hash_password(password)

        # Creamos el usuario en la base.
        usuario = self.usuario_repo.crear_usuario(
            email=email,
            password_hash=password_hash,
            nombre=nombre,
            apellido=apellido,
            celular=celular,
            es_profesional=es_profesional,
            es_solicitante=es_solicitante,
        )

        # Armamos una respuesta sin datos sensibles.
        return {
            "id": str(usuario.id),
            "usuario_id": str(usuario.id),
            "email": usuario.email,
            "nombre": usuario.nombre,
            "apellido": usuario.apellido,
            "roles": [
                r
                for r, active in (
                    (
                        "profesional",
                        bool(getattr(usuario, "es_profesional", False)),
                    ),
                    (
                        "solicitante",
                        bool(getattr(usuario, "es_solicitante", False)),
                    ),
                )
                if active
            ],
        }

    # LOGIN

    def login(
        self,
        email: str,
        password: str,
        ip_address: Optional[
            str
        ] = None,  # Lo reservamos para auditoría/rate-limit.
        user_agent: Optional[str] = None,  # Ídem: nos sirve para trazabilidad.
    ) -> dict:
        """Autenticamos y devolvemos {access_token, token_type} cuando todo sale bien."""
        # Si el usuario está temporalmente bloqueado, cortamos el flujo.
        if self.usuario_repo.esta_bloqueado(email):
            raise PermissionError(
                "Usuario temporalmente bloqueado por intentos fallidos. "
                "Intenta más tarde."
            )

        usuario = self.usuario_repo.obtener_por_email(email)
        if not usuario:
            # No exponemos si existe: registramos el intento y devolvemos mensaje genérico.
            self.usuario_repo.incrementar_intentos_fallidos(email)
            raise ValueError("Credenciales inválidas")

        if not usuario.activo:
            raise ValueError("Usuario inactivo")

        if not usuario.password_hash or not self.verify_password(
            password, usuario.password_hash
        ):
            self.usuario_repo.incrementar_intentos_fallidos(email)
            raise ValueError("Credenciales inválidas")

        # Llegamos acá con login correcto: reseteamos intentos y guardamos último acceso.
        self.usuario_repo.resetear_intentos_fallidos(usuario.id)
        self.usuario_repo.actualizar_ultimo_login(usuario.id)

        # Construimos los roles que vamos a meter en el token.
        roles = []
        if getattr(usuario, "es_profesional", False):
            roles.append("profesional")
        if getattr(usuario, "es_solicitante", False):
            roles.append("solicitante")

        access_token = self.crear_access_token(
            data={
                "sub": str(usuario.id),
                "email": usuario.email,
                "roles": roles,
            },
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        return {"access_token": access_token, "token_type": "bearer"}

    # LOGOUT / REFRESH (stubs)

    def logout(self, refresh_token: str) -> bool:
        """Dejamos asentado que esto va como stub hasta implementar refresh tokens."""
        raise NotImplementedError(
            "Logout/refresh no implementados en esta versión mínima"
        )

    def refresh_access_token(self, refresh_token: str) -> dict:
        """Mantenemos el stub de refresh para una versión futura."""
        raise NotImplementedError(
            "Logout/refresh no implementados en esta versión mínima"
        )
