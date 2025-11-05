"""Smoke test de la API en modo local: consulta /health, registra un usuario,
hace login para obtener un JWT y pega a /api/v1/auth/me con el token."""

from __future__ import annotations

import sys
from pathlib import Path
from dotenv import load_dotenv

# Metemos la raíz del proyecto en sys.path para poder importar con paths
# absolutos (evitamos imports relativos incómodos).
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Cargamos variables desde .env (credenciales, flags, etc.).
load_dotenv()

from fastapi.testclient import TestClient
from app.main import app

# Cliente HTTP de pruebas para FastAPI (levanta la app en memoria)
client = TestClient(app)


def run():
    """Corre el flujo básico: health -> register -> login -> me."""
    # Ping de salud: si esto falla, algo básico está roto.
    r = client.get("/health")
    print("health:", r.status_code, r.json())

    # Alta de usuario de prueba (datos inventados, tranqui).
    payload = {
        "nombre": "Demo",
        "apellido": "User",
        "email": "demo@example.com",
        "celular": None,
        "password": "Password#123",
        "es_profesional": False,
        "es_solicitante": True,
    }
    r = client.post("/api/v1/auth/register-json", json=payload)
    print("register:", r.status_code, r.text)

    # Login con las credenciales recién registradas
    r = client.post(
        "/api/v1/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    print("login:", r.status_code, r.text)
    # Guardamos el token si el login anduvo; si no, seguimos sin auth
    token = None
    if r.status_code == 200:
        token = r.json().get("access_token")

    # Hacemos /me para ver quién soy con (o sin) token; útil para chequear permisos.
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    r = client.get("/api/v1/auth/me", headers=headers)
    print("me:", r.status_code, r.text)


if __name__ == "__main__":
    # Entrada estándar de script: ejecutamos el smoke-test
    run()