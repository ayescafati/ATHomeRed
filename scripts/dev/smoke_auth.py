"""Smoke test de la API en modo local: consulta /health, registra un usuario,
hace login para obtener un JWT y pega a /api/v1/auth/me con el token."""

from __future__ import annotations

from fastapi.testclient import TestClient
from app.main import app

import sys
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv()


client = TestClient(app)


def run():
    """Corre el flujo básico: health -> register -> login -> me."""
    r = client.get("/health")
    print("health:", r.status_code, r.json())

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

    r = client.post(
        "/api/v1/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    print("login:", r.status_code, r.text)

    token = None
    if r.status_code == 200:
        token = r.json().get("access_token")

    headers = {"Authorization": f"Bearer {token}"} if token else {}
    r = client.get("/api/v1/auth/me", headers=headers)
    print("me:", r.status_code, r.text)


if __name__ == "__main__":
    run()
