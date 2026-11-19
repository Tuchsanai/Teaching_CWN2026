#!/bin/bash
# Web side on this PC (db + migrate + web + dispatcher) with docker compose, real gateway on the GPU machine.
# Run from the lesson folder in Git Bash:  code_step09/web.sh up -d --build | ps | logs dispatcher | down ...
# Settings: ./app/.env (web settings, test passwords) + ./.env (GATEWAY_API_KEY only is used from it).
cd "$(dirname "$0")/../app" || exit 1
exec docker compose -p sitesafe-e2e --env-file ../.env --env-file .env "$@"
