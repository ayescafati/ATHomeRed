"""
Router de autenticación real (MVP): registro, login y me con JWT.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from typing import Optional

from app.api.schemas import TokenSchema, LoginRequest, RegisterRequest
from app.api.dependencies import get_db
from app.services.auth_service import AuthService
from app.infra.repositories.usuario_repository import UsuarioRepository

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register-json", status_code=status.HTTP_201_CREATED)
def registrar_usuario(data: RegisterRequest, db=Depends(get_db)):
    """Crea un usuario nuevo y devuelve sus datos básicos (sin password)."""
    svc = AuthService(db)
    try:
        creado = svc.registrar_usuario(
            email=data.email,
            password=data.password,
            nombre=data.nombre,
            apellido=data.apellido,
            celular=data.celular,
            es_profesional=data.es_profesional,
            es_solicitante=data.es_solicitante,
        )
        return creado
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.post("/login", response_model=TokenSchema)
def login(creds: LoginRequest, db=Depends(get_db)):
    """Autentica con email/password y devuelve un access_token (bearer)."""
    svc = AuthService(db)
    try:
        return svc.login(email=creds.email, password=creds.password)
    except PermissionError as pe:
        raise HTTPException(status_code=423, detail=str(pe))
    except ValueError:
        # Mensaje genérico para no revelar detalles
        raise HTTPException(status_code=401, detail="Credenciales inválidas")


@router.get("/me")
def obtener_usuario_actual(
    authorization: Optional[str] = Header(default=None),
    db=Depends(get_db),
):
    """Decodifica el token Bearer y devuelve el perfil básico del usuario."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Falta token Bearer")
    token = authorization.split(" ", 1)[1]
    svc = AuthService(db)
    payload = svc.validar_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Token sin 'sub'")

    repo = UsuarioRepository(db)
    user = repo.obtener_por_id(sub)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return {
        "id": str(user.id),
        "email": user.email,
        "nombre": user.nombre,
        "apellido": user.apellido,
        "roles": [
            r
            for r, active in (
                ("profesional", bool(getattr(user, "es_profesional", False))),
                ("solicitante", bool(getattr(user, "es_solicitante", False))),
            )
            if active
        ],
        "activo": bool(getattr(user, "activo", True)),
        "verificado": bool(getattr(user, "verificado", False)),
        "ultimo_login": getattr(user, "ultimo_login", None),
    }
