# app/infra/persistence/database.py
from __future__ import annotations
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./app.db"

if os.getenv("DB_DEBUG", "0") == "1":
    print(f"[DB] Using: {DATABASE_URL}")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
