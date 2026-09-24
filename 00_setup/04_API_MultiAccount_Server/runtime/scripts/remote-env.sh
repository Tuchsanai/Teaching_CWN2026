# Sourced by deploy/test scripts. Reads connection settings from .env and defines:
#   rdocker ...   docker CLI against the outer daemon (ssh shim first in PATH for this command only)
#   rssh CMD      shell command on the control host through the same ControlMaster
_env() { python3 "$(dirname "${BASH_SOURCE[0]}")/envfile.py" get "$(dirname "${BASH_SOURCE[0]}")/../.env" "$1"; }
REMOTE_DOCKER_HOST="$(_env DOCKER_HOST)"
LAB_SSH_CONTROL_PATH="$(_env SSH_CONTROL_PATH)"
LAB_SSH_KNOWN_HOSTS="$(_env SSH_KNOWN_HOSTS)"
export LAB_SSH_CONTROL_PATH LAB_SSH_KNOWN_HOSTS
SHIM_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/ssh-shim" && pwd)"
# docker's own credential helper in devtools fails for public pulls; an empty config avoids it
ANON_DOCKER_CONFIG="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/.docker-anon"
mkdir -p "$ANON_DOCKER_CONFIG"; [ -s "$ANON_DOCKER_CONFIG/config.json" ] || echo '{}' > "$ANON_DOCKER_CONFIG/config.json"
rdocker() { PATH="$SHIM_DIR:$PATH" DOCKER_HOST="$REMOTE_DOCKER_HOST" DOCKER_CONFIG="$ANON_DOCKER_CONFIG" command docker "$@"; }
rssh() {
  python3 - "$REMOTE_DOCKER_HOST" <<'PY' > /dev/null || { echo "DOCKER_HOST is not ssh://" >&2; return 2; }
import sys; from urllib.parse import urlparse; sys.exit(0 if urlparse(sys.argv[1]).scheme == "ssh" else 1)
PY
  local u h p
  read -r u h p < <(python3 -c 'import sys;from urllib.parse import urlparse as P;x=P(sys.argv[1]);print(x.username or "root",x.hostname,x.port or 22)' "$REMOTE_DOCKER_HOST")
  "$SHIM_DIR/ssh" -p "$p" -l "$u" "$h" "$@"
}
