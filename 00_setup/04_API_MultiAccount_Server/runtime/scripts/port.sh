#!/usr/bin/env bash
# Port checks against the Docker host that will actually run the app container.
# Sourced by deploy.sh; can also be run alone:  scripts/port.sh [--write]
#   prints the Docker host's used/published ports and the port that would be used,
#   and with --write records that port as APP_PORT in .env.
# Never stops or changes other containers/services: a busy port is simply skipped.

PORT_RANGE_START="${PORT_RANGE_START:-8004}"
PORT_RANGE_END="${PORT_RANGE_END:-8099}"

# Ports that other containers publish, or are configured to publish (stopped ones included).
docker_claimed_ports() {  # $1 = our container name (ignored)
  local ids
  ids="$(docker ps -aq)"
  [ -n "$ids" ] || return 0
  # shellcheck disable=SC2086
  docker inspect --format '{{.Name}}|{{range $p, $b := .HostConfig.PortBindings}}{{range $b}}{{.HostPort}} {{end}}{{end}}|{{range $p, $b := .NetworkSettings.Ports}}{{range $b}}{{.HostPort}} {{end}}{{end}}' $ids \
    | while IFS='|' read -r cname a b; do
        [ "${cname#/}" = "$1" ] && continue
        for p in $a $b; do [ -n "$p" ] && echo "$p"; done
      done | sort -un
}

# Ports with a listening socket in the Docker host's network namespace.
# Uses a throwaway --network host container, so it is correct even when the Docker
# daemon is not on this machine. Needs an image that has python3.
host_listening_ports() {  # $1 = probe image
  docker run --rm -i --network host --user 65534 --entrypoint python3 "$1" - <<'PY'
ports = set()
for f in ("/proc/net/tcp", "/proc/net/tcp6"):
    try:
        for line in open(f).read().splitlines()[1:]:
            parts = line.split()
            if parts[3] == "0A":  # LISTEN
                ports.add(int(parts[1].rsplit(":", 1)[1], 16))
    except OSError:
        pass
print("\n".join(str(p) for p in sorted(ports)))
PY
}

# Try to actually bind the port on the Docker host (0.0.0.0 conflicts with any address).
host_can_bind() {  # $1 = probe image, $2 = port
  docker run --rm --network host --user 65534 --entrypoint python3 "$1" -c '
import socket, sys
s = socket.socket()
try:
    s.bind(("0.0.0.0", int(sys.argv[1])))
except OSError:
    sys.exit(1)
' "$2"
}

# Port currently published by our own container (a redeploy may keep it).
own_port() {  # $1 = our container name
  docker inspect --format '{{range $p, $b := .NetworkSettings.Ports}}{{range $b}}{{.HostPort}} {{end}}{{end}}' "$1" 2>/dev/null \
    | tr ' ' '\n' | grep -E '^[0-9]+$' | sort -u | head -1
}

# pick_port PREFERRED CONTAINER PROBE_IMAGE  -> prints the port to use (stdout), notes on stderr
pick_port() {
  local preferred="$1" cname="$2" image="$3" claimed listening ours p
  ours="$(own_port "$cname")"
  claimed="$(docker_claimed_ports "$cname")"
  listening="$(host_listening_ports "$image")" || { echo "cannot inspect Docker host ports" >&2; return 1; }
  echo "Docker host: ports published/configured by other containers: ${claimed:-none}" | tr '\n' ' ' >&2; echo >&2
  echo "Docker host: listening ports: ${listening:-none}" | tr '\n' ' ' >&2; echo >&2
  for p in "$preferred" $(seq "$PORT_RANGE_START" "$PORT_RANGE_END"); do
    if grep -qx "$p" <<<"$claimed"; then continue; fi
    if [ -n "$ours" ] && [ "$p" = "$ours" ]; then echo "$p"; return 0; fi  # held by our own container
    if grep -qx "$p" <<<"$listening"; then continue; fi
    # optional extra check supplied by the caller (e.g. something already answering on the host)
    if declare -F extra_port_busy >/dev/null && extra_port_busy "$p"; then continue; fi
    if host_can_bind "$image" "$p"; then echo "$p"; return 0; fi
  done
  echo "no free port in $PORT_RANGE_START-$PORT_RANGE_END on the Docker host" >&2
  return 1
}

if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  set -euo pipefail
  cd "$(dirname "$0")/.."
  [ -f .env ] || cp .env.example .env
  preferred="$(python3 scripts/envfile.py get .env APP_PORT)"; preferred="${preferred:-8004}"
  cname="$(python3 scripts/envfile.py get .env APP_CONTAINER_NAME)"; cname="${cname:-ai-chat-app}"
  image="${PROBE_IMAGE:-python:3.12-slim}"
  chosen="$(pick_port "$preferred" "$cname" "$image")"
  if [ "$chosen" != "$preferred" ]; then echo "APP_PORT $preferred is busy on the Docker host; using $chosen"; fi
  echo "port to use: $chosen"
  if [ "${1:-}" = "--write" ]; then python3 scripts/envfile.py set .env APP_PORT "$chosen"; echo "saved APP_PORT=$chosen in .env"; fi
fi
