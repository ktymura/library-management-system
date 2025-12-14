#!/usr/bin/env bash
set -euo pipefail

# Wymagane zmienne z .env (docker-compose wstrzyknie je do kontenera db)
: "${USER_DB_NAME?}" "${USER_DB_USER?}" "${USER_DB_PASSWORD?}"
: "${CATALOG_DB_NAME?}" "${CATALOG_DB_USER?}" "${CATALOG_DB_PASSWORD?}"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres <<EOSQL
DO \$\$
BEGIN
   IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '${USER_DB_USER}') THEN
      EXECUTE format('CREATE ROLE %I LOGIN PASSWORD %L', '${USER_DB_USER}', '${USER_DB_PASSWORD}');
   END IF;
   IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '${CATALOG_DB_USER}') THEN
      EXECUTE format('CREATE ROLE %I LOGIN PASSWORD %L', '${CATALOG_DB_USER}', '${CATALOG_DB_PASSWORD}');
   END IF;
END
\$\$;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres <<EOSQL
SELECT format('CREATE DATABASE %I OWNER %I', '${USER_DB_NAME}', '${USER_DB_USER}')
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = '${USER_DB_NAME}')
\gexec
SELECT format('CREATE DATABASE %I OWNER %I', '${CATALOG_DB_NAME}', '${CATALOG_DB_USER}')
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = '${CATALOG_DB_NAME}')
\gexec
EOSQL
