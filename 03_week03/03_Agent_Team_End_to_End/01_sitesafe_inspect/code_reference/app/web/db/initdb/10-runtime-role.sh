#!/bin/sh
# Runs once, when the db volume is created (postgres image: /docker-entrypoint-initdb.d).
# Creates the runtime login used by web and dispatcher (DATABASE_URL). It is a member of
# sitesafe_web, which schema.sql grants: no UPDATE / DELETE on result_overrides (NFR-07).
# The table owner (POSTGRES_USER) is used only by migrate / seed / test reset (DATABASE_OWNER_URL).
set -eu
: "${WEB_DB_USER:=sitesafe_app}"
: "${WEB_DB_PASSWORD:?WEB_DB_PASSWORD is required}"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
     -v web_user="$WEB_DB_USER" -v web_password="$WEB_DB_PASSWORD" <<'SQL'
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'sitesafe_web') THEN
        CREATE ROLE sitesafe_web NOLOGIN;
    END IF;
END;
$$;
CREATE ROLE :"web_user" LOGIN PASSWORD :'web_password' IN ROLE sitesafe_web;
SQL
