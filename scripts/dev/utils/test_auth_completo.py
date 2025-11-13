"""
Script de prueba para verificar la implementación completa de autenticación.

Prueba:
1. Registro de usuario
2. Login (obtener access_token y refresh_token)
3. Uso del access_token en /me
4. Refresh del access_token
5. Logout de una sesión
6. Verificar auditoría de login
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.infra.persistence.database import DATABASE_URL
from app.services.auth_service import AuthService
from app.infra.repositories.auth_repository import AuthRepository
from datetime import datetime


def test_auth_completo():
    """Prueba el flujo completo de autenticación"""

    print("\n" + "=" * 60)
    print("PRUEBA COMPLETA DE AUTENTICACIÓN")
    print("=" * 60 + "\n")

    engine = create_engine(DATABASE_URL)
    db = Session(bind=engine)

    try:
        auth_service = AuthService(db)
        auth_repo = AuthRepository(db)

        email_test = f"test_auth_{datetime.utcnow().timestamp()}@example.com"

        print("REGISTRO DE USUARIO")
        print("-" * 40)
        try:
            usuario = auth_service.registrar_usuario(
                email=email_test,
                password="SecurePass123!",
                nombre="Test",
                apellido="Auth",
                es_profesional=False,
                es_solicitante=True,
            )
            print(f"Usuario registrado: {usuario['email']}")
            print(f"   ID: {usuario['id']}")
        except Exception as e:
            print(f"Error en registro: {e}")
            return

        print("\n  LOGIN")
        print("-" * 40)
        try:
            tokens = auth_service.login(
                email=email_test,
                password="SecurePass123!",
                ip_address="127.0.0.1",
                user_agent="Python Test Script",
            )
            print(f"   Login exitoso")
            print(f"   Access Token: {tokens['access_token'][:30]}...")
            print(f"   Refresh Token: {tokens['refresh_token'][:30]}...")
            print(f"   Token Type: {tokens['token_type']}")

            access_token = tokens["access_token"]
            refresh_token = tokens["refresh_token"]
        except Exception as e:
            print(f"  Error en login: {e}")
            return

        print("\n   VALIDAR ACCESS TOKEN")
        print("-" * 40)
        try:
            payload = auth_service.validar_access_token(access_token)
            print(f"   Token válido")
            print(f"   Usuario ID: {payload['sub']}")
            print(f"   Email: {payload['email']}")
            print(f"   Roles: {payload['roles']}")
        except Exception as e:
            print(f"   Error validando token: {e}")

        print("\n   REFRESH ACCESS TOKEN")
        print("-" * 40)
        try:
            new_tokens = auth_service.refresh_access_token(refresh_token)
            print(f"   Nuevo access token generado")
            print(f"   New Access Token: {new_tokens['access_token'][:30]}...")
            print(f"   (El refresh token se mantiene igual)")
        except Exception as e:
            print(f"   Error en refresh: {e}")

        print("\n   VERIFICAR AUDITORÍA DE LOGIN")
        print("-" * 40)
        try:
            from app.infra.persistence.auth import AuditoriaLoginORM

            auditorias = (
                db.query(AuditoriaLoginORM)
                .filter(AuditoriaLoginORM.email == email_test)
                .all()
            )

            print(f" Registros de auditoría encontrados: {len(auditorias)}")
            for i, aud in enumerate(auditorias, 1):
                print(f"   {i}. {' EXITOSO' if aud.exitoso else 'FALLIDO'}")
                print(f"      Fecha: {aud.fecha}")
                print(f"      IP: {aud.ip_address}")
                print(f"      User Agent: {aud.user_agent}")
                if aud.motivo:
                    print(f"      Motivo: {aud.motivo}")
        except Exception as e:
            print(f"Error verificando auditoría: {e}")

        print("\nLOGOUT (REVOCAR REFRESH TOKEN)")
        print("-" * 40)
        try:
            resultado = auth_service.logout(refresh_token)
            if resultado:
                print(f"Sesión cerrada exitosamente")
            else:
                print(f"Token no encontrado (puede estar ya revocado)")
        except Exception as e:
            print(f"Error en logout: {e}")

        print("\nINTENTAR REFRESH DESPUÉS DE LOGOUT")
        print("-" * 40)
        try:
            auth_service.refresh_access_token(refresh_token)
            print(f"ERROR: El refresh debería haber fallado")
        except ValueError as ve:
            print(f"Correctamente bloqueado: {ve}")
        except Exception as e:
            print(f"Error inesperado: {e}")

        print("\n ESTADÍSTICAS")
        print("-" * 40)
        from app.infra.persistence.auth import RefreshTokenORM

        total_tokens = db.query(RefreshTokenORM).count()
        tokens_revocados = (
            db.query(RefreshTokenORM)
            .filter(RefreshTokenORM.revocado == True)
            .count()
        )

        print(f"   Total refresh tokens: {total_tokens}")
        print(f"   Tokens revocados: {tokens_revocados}")
        print(f"   Tokens activos: {total_tokens - tokens_revocados}")

        print("\n" + "=" * 60)
        print("PRUEBA COMPLETA FINALIZADA")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n  ERROR GENERAL: {e}")
        import traceback

        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_auth_completo()
