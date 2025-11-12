#!/usr/bin/env bash
set -euo pipefail

echo "==> DB: ${DATABASE_URL:-<unset>}"
echo "==> ALEMBIC_CONFIG: ${ALEMBIC_CONFIG:-<none>}"
echo "==> PYTEST_ARGS: ${PYTEST_ARGS:-tests}"

if [[ "${MIGRATE_ON_START:-0}" == "1" ]]; then
  echo "Esperando Postgres en $DB_HOST:$DB_PORT/$DB_NAME ..."
  until pg_isready -h "$DB_HOST" -p "${DB_PORT:-5432}" -U "$DB_USER" -d "$DB_NAME" -t 1; do
    sleep 1
  done
  echo "Postgres OK."
  echo "Ejecutando migraciones Alembic..."
  alembic upgrade head
else
  echo "[SKIP] Migraciones y Postgres (MIGRATE_ON_START=${MIGRATE_ON_START:-0})"
  # Asegurar DATABASE_URL dummy para partes del código que lo lean
  export DATABASE_URL="sqlite:///:memory:"
fi

echo "Lanzando pytest: -s ${PYTEST_ARGS}"
pytest -s ${PYTEST_ARGS}
