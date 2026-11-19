#!/bin/bash
# Step 11 · web + db + dispatcher on this machine (docker compose project receiptdesk-e2e, port 3420)
# usage: web.sh env | up | down | ps | logs [svc] | status | mode mock|gateway | psql "SQL"
# Keys are never printed: app/.env is written from ../.env (GATEWAY_API_KEY) with random DB/session secrets.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; APP="$ROOT/app"
P=receiptdesk-e2e
GW_URL="${GW_URL:-http://210.130.226.136:41588}"   # public port of 8000 (gateway) on the e2e-receipt machine
dc() { docker compose -p $P --project-directory "$APP" -f "$APP/docker-compose.yml" --env-file "$APP/.env" "$@"; }
setv() { # setv KEY VALUE  -> replace or append in app/.env
  python - "$APP/.env" "$1" "$2" <<'PY'
import sys,re,os
p,k,v=sys.argv[1:]; t=open(p).read() if os.path.exists(p) else ''
t=re.sub(rf'(?m)^{k}=.*\n?','',t); t=t.rstrip('\n')+('\n' if t.strip() else '')+f'{k}={v}\n'
open(p,'w',newline='\n').write(t)
PY
}
case "$1" in
  env)
    [ -f "$APP/.env" ] || : > "$APP/.env"
    KEY=$(grep -E '^GATEWAY_API_KEY=' "$ROOT/.env" | head -1 | cut -d= -f2- | tr -d '\r')
    setv GATEWAY_API_KEY "$KEY"; setv GATEWAY_URL "$GW_URL"; setv AI_MODE gateway; setv WEB_PORT 3420; setv BUG_MODE 0
    grep -q '^POSTGRES_PASSWORD=' "$APP/.env" || setv POSTGRES_PASSWORD "$(python -c 'import secrets;print(secrets.token_hex(16))')"
    grep -q '^SESSION_SECRET=' "$APP/.env" || setv SESSION_SECRET "$(python -c 'import secrets;print(secrets.token_hex(32))')"
    awk -F= '{print "  " $1 " (" length($2) " chars)"}' "$APP/.env" ;;
  up)     dc up -d --build ;;
  down)   dc down ;;
  ps)     dc ps ;;
  logs)   shift; dc logs --tail 80 "$@" ;;
  status) dc ps --format '{{.Service}} {{.State}} {{.Status}} {{.Ports}}'; curl -s -m 5 localhost:3420/api/health; echo ;;
  mode)   setv AI_MODE "$2"; dc up -d web dispatcher ;;
  psql)   shift; dc exec -T db psql -U receiptdesk -d receiptdesk -c "$*" ;;
  rows)   shift; dc exec -T db psql -U receiptdesk -d receiptdesk -A -t -F "|" -c "$*" ;;   # machine-readable
  *) echo "usage: $0 env|up|down|ps|logs|status|mode mock|gateway|psql SQL|rows SQL"; exit 1 ;;
esac
