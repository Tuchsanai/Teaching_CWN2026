#!/usr/bin/env bash
# Control ONLY this project's app container on the outer Docker host.
#   scripts/app.sh status|stop|start|restart|logs|health
# Uses DOCKER_HOST / SSH_* from .env through scripts/ssh-shim. Never touches other containers.
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/remote-env.sh
cname="$(python3 scripts/envfile.py get .env APP_CONTAINER_NAME)"; cname="${cname:-ai-chat-app}"
tok_file="$(python3 scripts/envfile.py get .env API_TOKEN_FILE)"; tok_file="${tok_file:-secrets/api_token}"
case "${1:-status}" in
  status)  rdocker ps -a --filter "name=^${cname}$" --format '{{.Names}}  {{.Status}}  {{.Ports}}' ;;
  stop)    rdocker stop "$cname" ;;
  start)   rdocker start "$cname" ;;
  restart) rdocker restart "$cname" ;;
  logs)    rdocker logs --tail "${2:-100}" "$cname" 2>&1 | python3 scripts/redact.py "$tok_file" ;;
  health)  url="$(python3 scripts/envfile.py get .env APP_TEST_URL)"; python3 -c 'import sys,urllib.request;print(urllib.request.urlopen(sys.argv[1].rstrip("/")+"/health",timeout=5).read().decode())' "$url" ;;
  *) echo "usage: $0 status|stop|start|restart|logs [N]|health" >&2; exit 2 ;;
esac
