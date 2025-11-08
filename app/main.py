"""App FastAPI principal.

Armamos la API, agregamos un healthcheck, montamos el router
de auth y servimos un frontend estático mínimo para probar rápido en el browser.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

# Importamos SOLO el router de auth para evitar efectos secundarios de __init__ en routers.
from app.api.routers.auth import router as auth_router


def create_app() -> FastAPI:
    """Crea y configura la aplicación FastAPI."""
    app = FastAPI(title="ATHomeRed API", version="0.1.0")

    # Healthcheck sencillo para ver si la API respira.
    @app.get("/health")
    def health() -> JSONResponse:
        return JSONResponse({"status": "ok"})

    # Incluimos el router de autenticación (su prefijo está definido adentro del router).
    app.include_router(auth_router)

    # Servimos archivos estáticos del frontend mínimo.
    # /static -> JS/CSS/imagenes de prueba para el login básico.
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    # Endpoint raíz que entrega el index.html (pantalla mínima de prueba).
    @app.get("/")
    def index() -> FileResponse:
        return FileResponse("app/static/index.html")

    return app


# Instancia global para que uvicorn pueda levantar app
app = create_app()