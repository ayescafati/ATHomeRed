'''Aplica en la base el SQL offline de Alembic (alembic.sql) 
usando SQLAlchemy: detecta encoding, separa por “;” y ejecuta 
todo dentro de una transacción.'''


from __future__ import annotations

import sys
from pathlib import Path
from contextlib import closing

from dotenv import load_dotenv
from sqlalchemy import text

# Metemos la raíz del repo en sys.path para poder importar con rutas absolutas
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Cargamos variables de entorno desde .env (clásico para credenciales/DSN/etc.)
load_dotenv()

from app.infra.persistence.database import ENGINE

# Archivo donde Alembic vuelca el SQL offline (generado con --sql)
SQL_FILE = ROOT / "alembic.sql"


def iter_statements(sql_text: str):
    """
    Generador que separa el texto SQL en statements individuales.
    Corta cada vez que encuentra un ';' al final de línea.
    Además saltea la línea de DSN que algunos entornos imprimen.
    """    
    buf = []
    for line in sql_text.splitlines():
        # Saltamos la línea con el DSN "enmascarado" que mete nuestro env
        if line.startswith("[DB] Using:"):
            continue
        buf.append(line)
        # Cuando una línea termina en ';', cerramos el statement
        if line.strip().endswith(";"):
            stmt = "\n".join(buf).strip()
            if stmt:
                yield stmt
            buf = []
    # Si quedó algo sin el ';' final, también lo devolvemos (por las dudas)
    tail = "\n".join(buf).strip()
    if tail:
        yield tail


def main() -> int:
    # Chequeo rápido: si no existe el SQL, avisamos cómo generarlo y salimos
    if not SQL_FILE.exists():
        print(f"[apply_sql] File not found: {SQL_FILE}")
        print("Run:  .\\.venv\\Scripts\\python.exe -m alembic upgrade head --sql > alembic.sql")
        return 2

    # Leemos los bytes crudos porque PowerShell con '>' a veces guarda en UTF-16
    raw = SQL_FILE.read_bytes()
    # Probamos varios encodings comunes para evitar quilombos de decodificación
    for enc in ("utf-8-sig", "utf-8", "utf-16", "utf-16-le", "utf-16-be"):
        try:
            sql_text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        # Si ninguno calza, avisamos y salimos con código de error
        print("[apply_sql] Could not decode alembic.sql with common encodings.")
        return 3
    # Partimos el archivo en sentencias ejecutables    
    stmts = list(iter_statements(sql_text))
    print(f"[apply_sql] Executing {len(stmts)} statements from {SQL_FILE.name}...")

    # Ejecutamos todo dentro de una transacción (si una falla, se hace rollback)
    with ENGINE.begin() as conn:
        for i, stmt in enumerate(stmts, 1):
            # Podemos descomentar este print para debuggear el primer renglón de cada stmt
            # print(f"[apply_sql] {i}: {stmt.splitlines()[0][:80]}...")            
            conn.execute(text(stmt))
    print("[apply_sql] Done.")
    return 0


if __name__ == "__main__":
    # Salimos con el código de retorno de main   
    raise SystemExit(main())
