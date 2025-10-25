# test_connection.py
from app.infra.db.database import ENGINE, DATABASE_URL
from sqlalchemy import text

def main():
    print("URL efectiva:", DATABASE_URL)
    with ENGINE.connect() as conn:
        # Detecta motor por el driver
        is_sqlite = DATABASE_URL.startswith("sqlite")
        if is_sqlite:
            # SQLite no tiene version(); usa PRAGMA
            v = conn.execute(text("select sqlite_version();")).scalar_one()
            who = "sqlite"
        else:
            v = conn.execute(text("select version();")).scalar_one()
            who = conn.execute(text("select current_user;")).scalar_one()

        print("Connected as:", who)
        print("Server:", v)

if __name__ == "__main__":
    main()
