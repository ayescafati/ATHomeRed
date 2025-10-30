"""
Dependencias compartidas para los endpoints de la API
"""
from typing import Generator
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.infra.persistence.database import SessionLocal
from app.infra.repositories.profesional_repository import ProfesionalRepository
from app.infra.repositories.consulta_repository import ConsultaRepository
from app.infra.repositories.paciente_repository import PacienteRepository
from app.infra.repositories.valoracion_repository import ValoracionRepository
# TODO: Descomentar cuando se implementen
# from app.infra.repositories.auth_repository import AuthRepository
# from app.infra.repositories.usuario_repository import UsuarioRepository
# from app.services.auth_service import AuthService


# Database Session 

def get_db() -> Generator[Session, None, None]:
    """
    Dependency que provee una sesión de base de datos.
    Se cierra automáticamente al finalizar el request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Repositories

def get_profesional_repository(
    db: Session = Depends(get_db)
) -> ProfesionalRepository:
    """Dependency para el repositorio de profesionales"""
    return ProfesionalRepository(db)


def get_consulta_repository(
    db: Session = Depends(get_db)
) -> ConsultaRepository:
    """Dependency para el repositorio de consultas"""
    return ConsultaRepository(db)


def get_paciente_repository(
    db: Session = Depends(get_db)
) -> PacienteRepository:
    """Dependency para el repositorio de pacientes"""
    return PacienteRepository(db)


def get_valoracion_repository(
    db: Session = Depends(get_db)
) -> ValoracionRepository:
    """Dependency para el repositorio de valoraciones"""
    return ValoracionRepository(db)


# Repositories de Auth (TODO)

# def get_auth_repository(db: Session = Depends(get_db)) -> AuthRepository:
#     """Dependency para el repositorio de autenticación"""
#     return AuthRepository(db)


# def get_usuario_repository(db: Session = Depends(get_db)) -> UsuarioRepository:
#     """Dependency para el repositorio de usuarios"""
#     return UsuarioRepository(db)


# def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
#     """Dependency para el servicio de autenticación"""
#     return AuthService(db)


# Authentication & Authorization

# TODO: Implementar estas dependencies para proteger endpoints
# Descomentar y completar cuando AuthService esté implementado

# from fastapi.security import OAuth2PasswordBearer
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# async def get_current_user(
#     token: str = Depends(oauth2_scheme),
#     db: Session = Depends(get_db)
# ):
#     """
#     Obtiene el usuario autenticado desde el JWT token.
#     
#     TODO: Implementar
#     1. Validar token con AuthService.validar_access_token(token)
#     2. Extraer usuario_id del payload
#     3. Buscar usuario en DB con UsuarioRepository
#     4. Verificar que usuario existe y está activo
#     5. Retornar usuario
#     
#     Si falla: Lanzar HTTPException 401 Unauthorized
#     """
#     raise NotImplementedError("TODO: Implementar get_current_user")


# async def get_current_active_user(
#     current_user = Depends(get_current_user)
# ):
#     """
#     Verifica que el usuario actual esté activo.
#     
#     TODO: Implementar
#     - Verificar current_user.activo == True
#     - Si no: HTTPException 400 "Usuario inactivo"
#     
#     Uso: Proteger endpoints que requieren usuario activo
#     """
#     raise NotImplementedError("TODO: Implementar get_current_active_user")


# async def get_current_verified_user(
#     current_user = Depends(get_current_active_user)
# ):
#     """
#     Verifica que el usuario esté verificado (email confirmado).
#     
#     TODO: Implementar
#     - Verificar current_user.verificado == True
#     - Si no: HTTPException 403 "Email no verificado"
#     
#     Uso: Proteger endpoints que requieren email verificado
#     """
#     raise NotImplementedError("TODO: Implementar get_current_verified_user")


# Role-Based Access Control (RBAC)

# def require_role(allowed_roles: list[str]):
#     """
#     Dependency factory para verificar roles de usuario.
#     
#     TODO: Implementar
#     - Crear una dependency que verifique current_user.roles
#     - Si el rol no está en allowed_roles: HTTPException 403 Forbidden
#     
#     Uso en routers:
#     @router.get("/admin", dependencies=[Depends(require_role(["admin"]))])
#     """
#     async def role_checker(current_user = Depends(get_current_active_user)):
#         # TODO: Implementar verificación de roles
#         # if current_user.rol not in allowed_roles:
#         #     raise HTTPException(status_code=403, detail="No tienes permisos")
#         raise NotImplementedError("TODO: Implementar require_role")
#     return role_checker


# def require_profesional():
#     """
#     Verifica que el usuario actual sea un profesional.
#     
#     TODO: Implementar
#     - Verificar current_user.es_profesional == True
#     - Si no: HTTPException 403 "Solo profesionales"
#     
#     Uso: Proteger endpoints exclusivos de profesionales
#     @router.post("/consultas/confirmar", dependencies=[Depends(require_profesional)])
#     """
#     async def profesional_checker(current_user = Depends(get_current_active_user)):
#         raise NotImplementedError("TODO: Implementar require_profesional")
#     return profesional_checker


# def require_solicitante():
#     """
#     Verifica que el usuario actual sea un solicitante.
#     
#     TODO: Implementar
#     - Verificar current_user.es_solicitante == True
#     - Si no: HTTPException 403 "Solo solicitantes"
#     
#     Uso: Proteger endpoints exclusivos de solicitantes
#     @router.post("/consultas/crear", dependencies=[Depends(require_solicitante)])
#     """
#     async def solicitante_checker(current_user = Depends(get_current_active_user)):
#         raise NotImplementedError("TODO: Implementar require_solicitante")
#     return solicitante_checker


# Resource Ownership Policies

# async def verificar_propietario_consulta(
#     consulta_id: int,
#     current_user = Depends(get_current_active_user),
#     consulta_repo: ConsultaRepository = Depends(get_consulta_repository)
# ):
#     """
#     Verifica que el usuario sea dueño de la consulta (paciente o profesional asignado).
#     
#     TODO: Implementar
#     1. Obtener consulta por ID
#     2. Verificar que current_user sea:
#        - El paciente de la consulta, O
#        - El profesional asignado, O
#        - Un admin
#     3. Si no: HTTPException 403 "No tienes acceso a esta consulta"
#     
#     Uso: Proteger endpoints de consultas específicas
#     @router.get("/consultas/{consulta_id}", dependencies=[Depends(verificar_propietario_consulta)])
#     """
#     raise NotImplementedError("TODO: Implementar verificar_propietario_consulta")


# async def verificar_propietario_paciente(
#     paciente_id: int,
#     current_user = Depends(get_current_active_user),
#     paciente_repo: PacienteRepository = Depends(get_paciente_repository)
# ):
#     """
#     Verifica que el usuario sea el solicitante del paciente.
#     
#     TODO: Implementar
#     1. Obtener paciente por ID
#     2. Verificar que paciente.solicitante_id == current_user.id
#     3. Si no: HTTPException 403 "No tienes acceso a este paciente"
#     
#     Uso: Proteger endpoints de pacientes específicos
#     @router.put("/pacientes/{paciente_id}", dependencies=[Depends(verificar_propietario_paciente)])
#     """
#     raise NotImplementedError("TODO: Implementar verificar_propietario_paciente")
