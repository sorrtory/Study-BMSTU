#!/usr/bin/env bash
set -euo pipefail

psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" --set ON_ERROR_STOP=1 \
  --file /docker-entrypoint-initdb.d/jsonb/001_schema.sql
psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" --set ON_ERROR_STOP=1 \
  --file /docker-entrypoint-initdb.d/jsonb/002_indexes.sql

psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" --set ON_ERROR_STOP=1 \
  --file /docker-entrypoint-initdb.d/normalized/001_schema.sql
psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" --set ON_ERROR_STOP=1 \
  --file /docker-entrypoint-initdb.d/normalized/002_indexes.sql
