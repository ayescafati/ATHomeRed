# app/infra/db/database.py
from __future__ import annotations
import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import MetaData
from dotenv import load_dotenv

# Carga .env desde la raíz del repo por defecto; ajustá si lo tenés en otro lado
load_dotenv()


def _build_url() -> str:
    dialect = os.getenv("DB_DIALECT", "sqlite").lower()

    if dialect == "postgresql":
        user = os.getenv("DB_USER", "")
        pwd  = os.getenv("DB_PASSWORD", "")
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")  # 5432 directo, 6543 pool (pgBouncer)
        db   = os.getenv("DB_NAME", "postgres")
        ssl  = os.getenv("DB_SSLMODE", "require")  # Supabase exige SSL

        # URL-encode por si hay símbolos
        user_enc = quote_plus(user or "")
        pwd_enc  = quote_plus(pwd or "")

        return f"postgresql+psycopg2://{user_enc}:{pwd_enc}@{host}:{port}/{db}?sslmode={ssl}"

    # default local (MVP)
    return "sqlite:///./app.db"

DATABASE_URL = _build_url()

# Log “seguro” para depurar (en producción, bajá el verbosity)
if os.getenv("DB_DEBUG", "0") == "1":
    masked = DATABASE_URL
    if "://" in masked and "@" in masked:
        # enmascara la contraseña
        prefix, rest = masked.split("://", 1)
        creds, tail = rest.split("@", 1)
        if ":" in creds:
            u, p = creds.split(":", 1)
            creds = f"{u}:***"
        masked = f"{prefix}://{creds}@{tail}"
    print("[DB] Using:", masked)

ENGINE = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=5,
    future=True,
)

SessionLocal = sessionmaker(bind=ENGINE, autoflush=False, autocommit=False, expire_on_commit=False)

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
