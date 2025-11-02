"""
Router para autenticación y autorización
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.api.schemas import TokenSchema, LoginRequest, RegisterRequest

router = APIRouter()

# TODO: Configurar OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post("/register", status_code=status.HTTP_201_CREATED)
def registrar_usuario(data: RegisterRequest):
    """
    Registra un nuevo usuario en el sistema.

    TODO: Implementar
    - Hash de contraseña (bcrypt)
    - Validación de email único
    - Creación de usuario en DB
    - Envío de email de verificación
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint en desarrollo",
    )


@router.post("/login", response_model=TokenSchema)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Autentica un usuario y devuelve un token JWT.

    TODO: Implementar
    - Validar credenciales
    - Generar token JWT
    - Incluir roles/permisos en el token
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint en desarrollo",
    )


@router.post("/logout")
def logout():
    """
    Cierra la sesión del usuario.

    TODO: Implementar (opcional, depende de la estrategia de tokens)
    - Invalidar token en blacklist
    - Limpiar sesión
    """
    return {"message": "Sesión cerrada correctamente"}


@router.get("/me")
def obtener_usuario_actual(token: str = Depends(oauth2_scheme)):
    """
    Obtiene la información del usuario autenticado.

    TODO: Implementar
    - Decodificar token JWT
    - Obtener usuario de DB
    - Retornar datos del usuario
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint en desarrollo",
    )
