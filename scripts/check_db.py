"""Chequea la base: conecta, muestra versión y DB actual, intenta asegurar el
schema 'athome' y la extensión 'pgcrypto', lista tablas (incluida 'usuario' y
'alembic_version') y resume cantidad de tablas por schema. No toca datos."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from contextlib import closing

from dotenv import load_dotenv
from sqlalchemy import text

# Agregamos la raíz del proyecto a sys.path para imports limpios.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Cargamos variables de entorno desde .env (DSN, usuario, pass, etc.).
load_dotenv()

# Reutilizamos la configuración de DB de la app.
from app.infra.persistence.database import ENGINE, DATABASE_URL


def mask_url(url: str) -> str:
    """Enmascara la contraseña de una URL de conexión para imprimirla segura."""
    try:
        if "://" in url and "@" in url:
            prefix, rest = url.split("://", 1)
            creds, tail = rest.split("@", 1)
            if ":" in creds:
                u, _ = creds.split(":", 1)
                creds = f"{u}:***"
            return f"{prefix}://{creds}@{tail}"
    except Exception:
        # Si algo falla, devolvemos la URL original sin romper el flujo.
        pass
    return url


def main() -> int:
    # Mostramos el DSN con la clave tapada para no filtrar secretos.
    print("[check_db] Using DSN:", mask_url(DATABASE_URL))
    try:
        # Abrimos conexión y garantizamos el cierre al terminar.
        with closing(ENGINE.connect()) as conn:
            # Ping básico: versión de Postgres y base actual.
            r = conn.execute(text("select version(), current_database()"))
            version, db = r.fetchone()
            print("[check_db] Connected!", version)
            print("[check_db] Current database:", db)
            # Chequeos rápidos: schema y extensión necesarios.
            # Nota: crear extensiones puede requerir permisos elevados.
            try:
                conn.execute(text("create schema if not exists athome"))
                conn.execute(text("create extension if not exists pgcrypto"))
                print("[check_db] Ensured schema 'athome' and extension 'pgcrypto'.")
            except Exception as e:
                print("[check_db] Note: couldn't create schema/extension (permission?):", e)

            # Listado de tablas del schema 'athome' y verificación de 'usuario'.
            try:
                print("[check_db] Listing tables in schema 'athome':")
                rows = conn.execute(text(
                    """
                    select table_name
                    from information_schema.tables
                    where table_schema = 'athome'
                    order by table_name
                    """
                )).fetchall()
                if not rows:
                    print("[check_db] No tables found in schema 'athome'.")
                else:
                    names = [r[0] for r in rows]
                    print(" - " + "\n - ".join(names))
                    if 'usuario' in names:
                        # Conteo opcional para verificar contenido.
                        cnt = conn.execute(text("select count(*) from athome.usuario")).scalar_one()
                        print(f"[check_db] Table athome.usuario exists. Rows: {cnt}")
                    else:
                        print("[check_db] Table athome.usuario NOT found.")

                # Ubicación de la tabla de migraciones 'alembic_version'.
                av = conn.execute(text(
                    """
                    select table_schema, table_name
                    from information_schema.tables
                    where table_name = 'alembic_version'
                    order by table_schema
                    """
                )).fetchall()
                if av:
                    print("[check_db] Found alembic_version table in schemas:")
                    for s, t in av:
                        print(f" - {s}.{t}")
                else:
                    print("[check_db] No alembic_version table found in any schema.")

                # Resumen: cantidad de tablas por schema de usuario.
                print("[check_db] Table counts per schema (excluding information_schema/pg_catalog):")
                counts = conn.execute(text(
                    """
                    select table_schema, count(*)
                    from information_schema.tables
                    where table_schema not in ('information_schema','pg_catalog')
                    group by table_schema
                    order by table_schema
                    """
                )).fetchall()
                for s, c in counts:
                    print(f" - {s}: {c}")
            except Exception as e:
                # Si falla el listado, informamos pero mantenemos el resto.
                print("[check_db] Error listing tables:", e)
        return 0
    except Exception as e:
        # Error de conexión: sugerimos pasos típicos para levantar el entorno.
        print("[check_db] Connection failed:", e)
        print("\nTips:\n- Ensure PostgreSQL is installed and running on host/port from .env (default 127.0.0.1:5432).\n- If using Docker Desktop, install it and run: docker compose -f docker/docker-compose.yml up -d\n- For native Windows install: create DB 'athomedb', then in psql run: \n    CREATE EXTENSION IF NOT EXISTS pgcrypto;\n    CREATE SCHEMA IF NOT EXISTS athome;\n- Update .env (DB_USER/DB_PASSWORD) to match your local install.\n")
        return 1


if __name__ == "__main__":
    # Salimos con el código que devuelve main.
    raise SystemExit(main())
