#!/usr/bin/env bash
# Deploy the chat app as ONE container on the outer Docker host (sibling of devtools).
#   scripts/deploy.sh [--check] [--refresh-logins]
#     --check           verify daemon, list existing objects, check the port; change nothing
#     --refresh-logins  copy login files again even if the private volume already has them
#
# docker goes to DOCKER_HOST (ssh://...) through scripts/ssh-shim; nothing is bind-mounted from
# the control host, because the daemon does not share its filesystem.
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/remote-env.sh
source scripts/port.sh
docker() { rdocker "$@"; }   # every docker call in this script (and port.sh) targets the outer daemon

check_only=0; refresh=0
for a in "$@"; do
  case "$a" in
    --check) check_only=1 ;;
    --refresh-logins) refresh=1 ;;
    *) echo "unknown option: $a" >&2; exit 2 ;;
  esac
done

die() { echo "ERROR: $*" >&2; exit 1; }
step() { printf '\n== %s\n' "$*"; }
env_get() { python3 scripts/envfile.py get .env "$1"; }
env_set() { python3 scripts/envfile.py set .env "$1" "$2"; }
[ -f .env ] || die ".env is missing (copy .env.example and fill DOCKER_HOST / SSH_* / REMOTE_SOURCE_DIR)"
chmod 600 .env

cname="$(env_get APP_CONTAINER_NAME)"; cname="${cname:-ai-chat-app}"
image="$(env_get APP_IMAGE)"; image="${image:-ai-chat-app:latest}"
acc_volume="$(env_get ACCOUNTS_VOLUME)"; acc_volume="${acc_volume:-ai-chat-accounts}"
web_volume="$(env_get WEB_VOLUME)"; web_volume="${web_volume:-ai-chat-web}"
remote_src="$(env_get REMOTE_SOURCE_DIR)"
tok_file="$(env_get API_TOKEN_FILE)"; tok_file="${tok_file:-secrets/api_token}"

# ---------------------------------------------------------------- target daemon
step "target Docker daemon"
[ -n "$REMOTE_DOCKER_HOST" ] || die "DOCKER_HOST is empty in .env"
[ -S "$LAB_SSH_CONTROL_PATH" ] || die "SSH ControlMaster socket not found (SSH_CONTROL_PATH in .env)"
inner_id="$(command docker -H unix:///var/run/docker.sock info -f '{{.ID}}' 2>/dev/null || true)"
target_id="$(docker info -f '{{.ID}}' 2>/dev/null)" || die "cannot reach the Docker daemon in DOCKER_HOST"
target_name="$(docker info -f '{{.Name}}')"
if [ "$target_id" = "$inner_id" ] || [ "$target_name" = "$(hostname)" ]; then
  die "DOCKER_HOST reaches devtools' own inner Docker daemon, not the outer host. Refusing."
fi
echo "daemon: $(docker info -f '{{.Name}} · {{.OperatingSystem}} · Docker {{.ServerVersion}}') — not devtools' inner daemon"
echo "control host over SSH: $(rssh hostname)"
echo "existing containers (only '$cname' belongs to this project):"
docker ps -a --format '  {{.Names}}  [{{.Status}}]  {{.Ports}}'
echo "project volumes present: $(docker volume ls -q | grep -xE "$acc_volume|$web_volume" | tr '\n' ' ' || true)"

# ---------------------------------------------------------------- port
step "port on the Docker host"
# Docker Desktop publishes on the host machine; anything already answering there is "busy" too.
extra_port_busy() {
  local h
  for h in $(python3 scripts/candidate_hosts.py "$REMOTE_DOCKER_HOST"); do
    [ "$h" = 127.0.0.1 ] && continue
    if [ -n "$(docker ps -q --filter "name=^${cname}$")" ] && [ "$1" = "$(own_port "$cname")" ]; then return 1; fi
    timeout 3 bash -c "exec 3<>/dev/tcp/$h/$1" 2>/dev/null && return 0
  done
  return 1
}
probe_image="$image"
docker image inspect "$probe_image" >/dev/null 2>&1 || { probe_image=alpine:3.20; }
if [ "$probe_image" = alpine:3.20 ]; then
  # alpine has no python3: fall back to the published-port list + host connect check only
  host_listening_ports() { :; }
  host_can_bind() { return 0; }
fi
preferred="$(env_get APP_PORT)"; preferred="${preferred:-8004}"
port="$(pick_port "$preferred" "$cname" "$probe_image")"
[ "$port" = "$preferred" ] || echo "port $preferred is in use on the Docker host; using $port"
echo "port to use: $port"
[ "$check_only" = 0 ] || { echo; echo "--check: nothing was changed"; exit 0; }
env_set APP_PORT "$port"

# ---------------------------------------------------------------- token
step "API token (owner-only file, never printed)"
mkdir -p "$(dirname "$tok_file")"; chmod 700 "$(dirname "$tok_file")"
if [ ! -s "$tok_file" ]; then
  (umask 077; python3 -c 'import secrets; print(secrets.token_urlsafe(32))' > "$tok_file")
  echo "generated a new random token in $tok_file"
else
  echo "using existing token in $tok_file"
fi
chmod 600 "$tok_file"

# ---------------------------------------------------------------- accounts
step "accounts with login data in devtools (file presence only)"
src_base="$(env_get SOURCE_ACCOUNTS_BASE)"; src_base="${src_base:-/root/ai-accounts}"
detect() {
  local n found=()
  for n in 1 2 3 4 5; do [ -s "$src_base/$1/$2$n/$3" ] && found+=("$2$n"); done
  local IFS=,; echo "${found[*]:-}"
}
claude_accounts="$(detect .Claude yolo .credentials.json)"
codex_accounts="$(detect .Codex cyolo auth.json)"
echo "claude=[${claude_accounts:-none}] codex=[${codex_accounts:-none}]"
[[ ",$claude_accounts," == *",yolo1,"* ]] || die "primary Claude account yolo1 has no login data"
[[ ",$codex_accounts," == *",cyolo1,"* ]] || die "primary Codex account cyolo1 has no login data"
env_set CLAUDE_ACCOUNTS "$claude_accounts"
env_set CODEX_ACCOUNTS "$codex_accounts"

# ---------------------------------------------------------------- complete source copy on the control host
step "complete source copy -> control host: REMOTE_SOURCE_DIR"
[ -n "$remote_src" ] || die "REMOTE_SOURCE_DIR is empty in .env"
src_list() { find . -type f ! -path './.env' ! -path './secrets/*' ! -path './.docker-anon/*' ! -path '*/__pycache__/*' \
             ! -path './.pytest_cache/*' ! -path './tests/artifacts/*' ! -path './tests/e2e/node_modules/*' | sort; }
src_list | tar -cf - -T - | rssh "set -e; mkdir -p '$remote_src.new'; tar -xf - -C '$remote_src.new'; rm -rf '$remote_src.old'; \
  if [ -d '$remote_src' ]; then mv '$remote_src' '$remote_src.old'; fi; mv '$remote_src.new' '$remote_src'; rm -rf '$remote_src.old'"
local_sums="$(src_list | xargs sha256sum | sha256sum | cut -d' ' -f1)"
remote_sums="$(src_list | rssh "cd '$remote_src' && xargs sha256sum | sha256sum" | cut -d' ' -f1)"
[ "$local_sums" = "$remote_sums" ] || die "source copy on the control host does not match"
echo "copied $(src_list | wc -l) files; checksums match; .env and secrets/ not included"

# ---------------------------------------------------------------- build
step "build the one app image on the outer daemon"
docker compose build app
docker run --rm --network none --entrypoint sh "$image" -c \
  'echo "claude $(claude --version) | codex $(codex --version)"; ls /usr/local/bin | grep -cE "^c?yolo[1-5]$" | sed "s/^/launchers: /"; \
   n=$(find / -xdev \( -name .credentials.json -o -name auth.json -o -name api_token \) -not -path "*/node_modules/*" 2>/dev/null | wc -l); echo "login/token files in image: $n"'

# ---------------------------------------------------------------- web page volume
step "web page -> named volume $web_volume (read-only in the app)"
docker volume create "$web_volume" >/dev/null
tar -C web -cf - index.html | docker run --rm -i --network none --user 0:0 -v "$web_volume:/w" --entrypoint sh "$image" \
  -c 'set -e; tar -xf - -C /w --no-same-owner; chown root:root /w/index.html; chmod 644 /w/index.html; chmod 755 /w'
local_sum="$(sha256sum web/index.html | cut -d' ' -f1)"
vol_sum="$(docker run --rm --network none -v "$web_volume:/w:ro" --entrypoint sha256sum "$image" /w/index.html | cut -d' ' -f1)"
[ "$local_sum" = "$vol_sum" ] || die "index.html in volume does not match (checksum)"
echo "index.html in volume; sha256 matches ($local_sum)"

# ---------------------------------------------------------------- logins + token into the private volume
step "login files + token -> private volume $acc_volume"
docker volume create "$acc_volume" >/dev/null
vol_sh() { docker run --rm -i --network none --user 0:0 -v "$acc_volume:/data" --entrypoint sh "$image" -c "$@"; }
vol_sh 'mkdir -p /data/accounts/.Claude /data/accounts/.Codex /data/secrets
  chown 10001:10001 /data /data/accounts /data/accounts/.Claude /data/accounts/.Codex /data/secrets
  chmod 700 /data/accounts /data/secrets' </dev/null
sync_one() {  # $1 = .Claude|.Codex  $2 = account  $3 = login file
  local dst="/data/accounts/$1/$2"
  if [ "$refresh" = 0 ] && vol_sh "test -s '$dst/$3'" </dev/null; then
    echo "  $2: login already in the volume (kept, not overwritten)"; return
  fi
  # content only flows through the pipe: never printed, logged, or put in an image
  tar -C "$src_base/$1/$2" -cf - -- "$3" | vol_sh "set -e; umask 077; mkdir -p '$dst'
    tar -xf - -C '$dst' --no-same-owner --no-same-permissions
    chown -R 10001:10001 '$dst'; chmod 700 '$dst'; chmod 600 '$dst/$3'"
  echo "  $2: copied $3 (owner app uid 10001, 0600 — the CLI can refresh it in place)"
}
IFS=, read -ra list <<<"$claude_accounts"; for a in "${list[@]}"; do sync_one .Claude "$a" .credentials.json; done
IFS=, read -ra list <<<"$codex_accounts";  for a in "${list[@]}"; do sync_one .Codex "$a" auth.json; done
vol_sh 'set -e; umask 077; cat > /data/secrets/api_token.new; chown 10001:10001 /data/secrets/api_token.new
  chmod 400 /data/secrets/api_token.new; mv /data/secrets/api_token.new /data/secrets/api_token' < "$tok_file"
echo "  token: /data/secrets/api_token (owner app, 0400)"

# ---------------------------------------------------------------- start
step "re-check the port, then start"
again="$(pick_port "$port" "$cname" "$probe_image")"
if [ "$again" != "$port" ]; then echo "port $port was taken meanwhile; using $again"; port="$again"; env_set APP_PORT "$port"; fi
APP_PORT="$port" docker compose up -d --no-build app
echo "waiting for /health (max 90 s)"
status=""
for _ in $(seq 1 45); do
  status="$(docker inspect --format '{{.State.Health.Status}}' "$cname" 2>/dev/null || true)"
  [ "$status" = healthy ] && break
  [ "$(docker inspect --format '{{.State.Running}}' "$cname" 2>/dev/null)" = true ] || break
  sleep 2
done
if [ "$status" != healthy ]; then
  echo "container is not healthy (status: ${status:-not running}); last log lines, secrets redacted:" >&2
  docker logs --tail 60 "$cname" 2>&1 | python3 scripts/redact.py "$tok_file" >&2
  exit 1
fi
echo "container $cname: healthy"
docker ps --filter "name=^${cname}$" --format '  {{.Names}}  {{.Image}}  {{.Ports}}'

# ---------------------------------------------------------------- inside the app container
step "CLI versions inside the app container"
docker exec "$cname" sh -c 'echo "yolo1  -> $(yolo1 --version)"; echo "cyolo1 -> $(cyolo1 --version)"'
step "one real short answer per provider, no tools (inside the app container)"
docker exec "$cname" python3 -m app.smoke

# ---------------------------------------------------------------- URLs
step "URLs"
bind="$(env_get APP_BIND)"; bind="${bind:-127.0.0.1}"
case "$bind" in 127.0.0.1|0.0.0.0) user_host=localhost ;; *) user_host="$bind" ;; esac
env_set APP_URL "http://$user_host:$port/"
echo "your browser (on the machine running Docker Desktop): http://$user_host:$port/"
test_url=""
for cand in $(python3 scripts/candidate_hosts.py "$REMOTE_DOCKER_HOST"); do
  if python3 - "$cand" "$port" <<'PY' 2>/dev/null; then test_url="http://$cand:$port/"; break; fi
import json, sys, urllib.request
host, port = sys.argv[1], sys.argv[2]
h = f"[{host}]" if ":" in host else host
with urllib.request.urlopen(f"http://{h}:{port}/health", timeout=4) as r:
    sys.exit(0 if json.load(r).get("status") == "ok" else 1)
PY
done
env_set APP_TEST_URL "$test_url"
if [ -n "$test_url" ]; then echo "reachable from devtools (Playwright): $test_url"
else echo "WARNING: no address reachable from devtools answered /health on port $port" >&2; fi
echo; echo "done. APP_PORT=$port   token: cat $tok_file"
