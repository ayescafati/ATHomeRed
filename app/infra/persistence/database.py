from __future__ import annotations

import os
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import MetaData
from dotenv import load_dotenv

# Cargamos variables desde .env (para local).
# Si tu .env está en otro lado, ajustá la ruta antes de llamar a load_dotenv().
load_dotenv()


def _build_url() -> str:
    """Arma la DATABASE_URL a partir del .env, con fallback a SQLite local.

    Priorizamos DATABASE_URL completa si viene seteada (p. ej., de producción).
    Si no, construimos según DB_DIALECT (postgresql|sqlite). Para Postgres,
    escapamos usuario y password por si traen símbolos raros.
    """
    direct_url = os.getenv("DATABASE_URL")
    if direct_url and direct_url.strip():
        return direct_url.strip()

    dialect = os.getenv("DB_DIALECT", "sqlite").lower()

    if dialect == "postgresql":
        user = os.getenv("DB_USER", "")
        pwd = os.getenv("DB_PASSWORD", "")
        host = os.getenv("DB_HOST", "localhost")
        # Nota: 5432 es el puerto típico; 6543 se usa a veces con pgBouncer.
        port = os.getenv("DB_PORT", "5432")
        db = os.getenv("DB_NAME", "postgres")
        # En Supabase y otros PaaS suele exigirse SSL.
        ssl = os.getenv("DB_SSLMODE", "require")

        # URL-encode por si hay caracteres especiales (espacios, @, :, etc.).
        user_enc = quote_plus(user or "")
        pwd_enc = quote_plus(pwd or "")

        return (
            f"postgresql+psycopg2://{user_enc}:{pwd_enc}"
            f"@{host}:{port}/{db}?sslmode={ssl}"
        )

    # Default bien simple para desarrollo/MVP: SQLite en archivo local.
    return "sqlite:///./app.db"


# URL de conexión resultante (la usamos en el engine).
DATABASE_URL = _build_url()

# Logueo “seguro” para debug: mostramos la URL pero enmascarando la contraseña.
# Dejalo activado solo si seteás DB_DEBUG=1 en el entorno.
if os.getenv("DB_DEBUG", "0") == "1":
    masked = DATABASE_URL
    if "://" in masked and "@" in masked:
        # Enmascaramos la pass para no filtrar secretos en consola.
        prefix, rest = masked.split("://", 1)
        creds, tail = rest.split("@", 1)
        if ":" in creds:
            u, p = creds.split(":", 1)
            creds = f"{u}:***"
        masked = f"{prefix}://{creds}@{tail}"
    print("[DB] Using:", masked)

# Engine de SQLAlchemy: pre_ping para evitar conexiones zombis,
# pool chiquito para dev, y future=True para la API moderna.
ENGINE = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=5,
    future=True,
)

# Session factory: sin autoflush/commit automático y sin expirar objetos al commit.
SessionLocal = sessionmaker(
    bind=ENGINE,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_session():
    """Dependency/generator de sesión para FastAPI.

    Entrega una sesión por request y la cierra pase lo que pase.
    Usalo con Depends(get_session) en tus endpoints/servicios.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()