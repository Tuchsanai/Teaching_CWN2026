#!/bin/bash
# Step 15 · second stack for tests: compose project receiptdesk-mock, AI_MODE=mock, port 3421, own DB volume.
# usage: mock.sh env | up | down | ps | logs [svc] | status | stop-reader | start-reader | restart-dbq | token-file
# Values are never printed. Env file: app/.env.mock (random secrets, ENABLE_TEST_RESET=1).
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; APP="$ROOT/app"; ENVF="$APP/.env.mock"
P=${P:-receiptdesk-mock}
dc() { docker compose -p $P --project-directory "$APP" -f "$APP/docker-compose.yml" --env-file "$ENVF" "$@"; }
rnd() { python -c "import secrets;print(secrets.token_hex($1))"; }
case "$1" in
  env)
    if [ ! -f "$ENVF" ]; then
      { echo "AI_MODE=mock"; echo "WEB_PORT=${MOCK_PORT:-3421}"; echo "BUG_MODE=0"; echo "ENABLE_TEST_RESET=1";
        echo "TEST_RESET_TOKEN=$(rnd 24)"; echo "POSTGRES_PASSWORD=$(rnd 16)"; echo "SESSION_SECRET=$(rnd 32)"; } > "$ENVF"
    fi
    awk -F= '{print "  " $1 " (" length($2) " chars)"}' "$ENVF" ;;
  up)     dc up -d ;;
  down)   dc down ;;
  ps)     dc ps ;;
  logs)   shift; dc logs --tail 80 "$@" ;;
  status) dc ps --format '{{.Service}} {{.State}} {{.Status}}'; curl -s -m 5 localhost:${MOCK_PORT:-3421}/api/health; echo ;;
  stop-reader)  dc stop dispatcher ;;
  start-reader) dc start dispatcher ;;
  restart-dbq)  dc restart db; dc restart dispatcher ;;
  *) echo "usage: $0 env|up|down|ps|logs|status|stop-reader|start-reader|restart-dbq"; exit 1 ;;
esac
