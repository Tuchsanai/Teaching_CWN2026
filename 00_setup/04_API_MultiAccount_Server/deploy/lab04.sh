#!/usr/bin/env bash
# LAB 004 · deploy the API + static web page as SIBLING containers on the
# OUTER Docker Desktop daemon (the same daemon that runs devtools).
#
# Runs on the control host whose `docker` talks to the outer daemon. From devtools,
# drive it with deploy/remote.sh (temporary SSH ControlMaster). It refuses to run
# against any other daemon, e.g. the inner daemon inside devtools.
#
#   bash deploy/lab04.sh check        # daemon, devtools, source credential files (existence only), ports
#   bash deploy/lab04.sh build        # build lab04-api and lab04-web images
#   bash deploy/lab04.sh token        # create deploy/.secrets/api_token (not printed)
#   bash deploy/lab04.sh creds        # copy selected credentials devtools -> named volume
#   bash deploy/lab04.sh up           # start both containers, then verify reachability
#   bash deploy/lab04.sh verify       # re-run the reachability checks only
#   bash deploy/lab04.sh smoke        # readiness checks (no model call)
#   bash deploy/lab04.sh smoke --live # + one real chat per default account (authenticated test)
#   bash deploy/lab04.sh status | logs [N] | down [--purge]
#
# Never prints credential or token values. Only touches resources labelled lab04=<role>.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$HERE")"
CONF="${LAB04_ENV:-$HERE/lab04.env}"
[ -f "$CONF" ] || CONF="$HERE/lab04.env.example"
# shellcheck disable=SC1090
source "$CONF"
SECRETS="$HERE/.secrets"
TOKEN_FILE="$SECRETS/api_token"
LOADER=lab04-creds-loader
APP_UID=10001

say()  { printf '\033[1;34m[lab04]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[lab04]\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31m[lab04]\033[0m %s\n' "$*" >&2; exit 1; }
split() { tr ',' ' ' <<<"$1"; }

# ------------------------------------------------------------- config ---
# Everything below ends up in docker arguments, so validate it before use.
validate_config() {
  local v a seen
  match() { [[ "$2" =~ $3 ]] || die "config: $1='$2' is not allowed"; }
  : "${PROBE_HOST:=127.0.0.1}" "${BROWSER_HOST:=localhost}"
  match EXPECTED_DOCKER_NAME "$EXPECTED_DOCKER_NAME" '^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$'
  for v in DEVTOOLS_CONTAINER API_CONTAINER WEB_CONTAINER ACCOUNTS_VOLUME NETWORK; do
    match "$v" "${!v}" '^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$'
  done
  for v in API_IMAGE WEB_IMAGE; do match "$v" "${!v}" '^[a-z0-9][a-z0-9_./-]{0,127}(:[A-Za-z0-9_.-]{1,64})?$'; done
  for v in SRC_CLAUDE_BASE SRC_CODEX_BASE; do
    match "$v" "${!v}" '^/[A-Za-z0-9._/-]+$'
    [[ "${!v}" != *..* ]] || die "config: $v must not contain '..'"
  done
  seen=","
  for a in $(split "$CLAUDE_ACCOUNTS"); do match CLAUDE_ACCOUNTS "$a" '^yolo[1-5]$'
    [[ "$seen" != *",$a,"* ]] || die "config: duplicate account $a"; seen+="$a,"; done
  for a in $(split "$CODEX_ACCOUNTS"); do match CODEX_ACCOUNTS "$a" '^cyolo[1-5]$'
    [[ "$seen" != *",$a,"* ]] || die "config: duplicate account $a"; seen+="$a,"; done
  [ -n "$(split "$CLAUDE_ACCOUNTS")" ] && [ -n "$(split "$CODEX_ACCOUNTS")" ] \
    || die "config: need at least one account per provider"
  match BIND_ADDR "$BIND_ADDR" '^(127\.0\.0\.1|0\.0\.0\.0|[0-9]{1,3}(\.[0-9]{1,3}){3})$'
  match PROBE_HOST "$PROBE_HOST" '^[A-Za-z0-9][A-Za-z0-9.-]{0,252}$'
  match BROWSER_HOST "$BROWSER_HOST" '^[A-Za-z0-9][A-Za-z0-9.-]{0,252}$'
  for v in API_PORT WEB_PORT; do
    match "$v" "${!v}" '^[0-9]{4,5}$'; [ "${!v}" -ge 1024 ] && [ "${!v}" -le 65535 ] || die "config: $v out of range"
  done
  [ "$API_PORT" != "$WEB_PORT" ] || die "config: API_PORT and WEB_PORT must differ"
  for v in CLI_TIMEOUT_S PER_ACCOUNT_CONCURRENCY MAX_CONCURRENCY; do match "$v" "${!v}" '^[0-9]{1,4}$'; done
  match CODEX_SANDBOX "$CODEX_SANDBOX" '^(read-only|workspace-write)$'
  match CLAUDE_COPY_CLAUDE_JSON "${CLAUDE_COPY_CLAUDE_JSON:-0}" '^[01]$'
}

require_outer_daemon() {
  command -v docker >/dev/null || die "docker CLI not found"
  local name
  name="$(docker info --format '{{.Name}}' 2>/dev/null)" || die "cannot reach a Docker daemon"
  if [ "$name" != "$EXPECTED_DOCKER_NAME" ]; then
    die "this docker CLI talks to daemon '$name', expected '$EXPECTED_DOCKER_NAME'.
       Inside devtools the default daemon is the INNER one: containers made there are not
       siblings of devtools and their ports are not published on the Windows host.
       Run this on the control host (see deploy/remote.sh) instead."
  fi
}

# ---------------------------------------------------- ownership guards ---
# $1 = kind (container|volume|network), $2 = name, $3 = expected lab04 label value.
# Returns 0 if ours, 1 if absent; dies if it exists but belongs to someone else.
owned() {
  local kind="$1" name="$2" role="$3" fmt label
  case "$kind" in
    container) fmt='{{index .Config.Labels "lab04"}}' ;;
    volume|network) fmt='{{index .Labels "lab04"}}' ;;
  esac
  docker "$kind" inspect "$name" >/dev/null 2>&1 || return 1
  label="$(docker "$kind" inspect -f "$fmt" "$name" 2>/dev/null || true)"
  [ "$label" = "$role" ] || die "$kind '$name' exists but is not labelled lab04=$role; refusing to touch it"
  return 0
}
remove_own() { if owned container "$1" "$2"; then docker rm -f "$1" >/dev/null; fi; }

token_hash() {
  [ -s "$TOKEN_FILE" ] || die "no API token yet: run 'bash deploy/lab04.sh token'"
  sha256sum <"$TOKEN_FILE" | cut -d' ' -f1
}

# `|| true`: a refused connection must show up as HTTP 000 / FAIL, not abort the script.
# The Bearer header is fed through a pipe, so the token never appears in argv.
curl_auth() {
  curl -sS -H @<(printf 'Authorization: Bearer %s\n' "$(cat "$TOKEN_FILE")") "$@" || true
}
http_code() { curl -s -o /dev/null --max-time 10 -w '%{http_code}' "$@" || true; }

# ------------------------------------------------------------ commands ---
cmd_check() {
  require_outer_daemon
  say "daemon: $(docker info --format '{{.Name}} · server {{.ServerVersion}} · {{.OperatingSystem}}')"
  local running ok=1 a f p c
  running="$(docker inspect -f '{{.State.Running}}' "$DEVTOOLS_CONTAINER" 2>/dev/null || echo missing)"
  [ "$running" = true ] || die "container '$DEVTOOLS_CONTAINER' is not running on this daemon ($running)"
  say "devtools container '$DEVTOOLS_CONTAINER': running (read-only checks; never modified)"
  for a in $(split "$CLAUDE_ACCOUNTS"); do
    f="$SRC_CLAUDE_BASE/$a/.credentials.json"
    if docker exec "$DEVTOOLS_CONTAINER" test -s "$f"; then say "source present: claude/$a"; else warn "source MISSING: $f"; ok=0; fi
  done
  for a in $(split "$CODEX_ACCOUNTS"); do
    f="$SRC_CODEX_BASE/$a/auth.json"
    if docker exec "$DEVTOOLS_CONTAINER" test -s "$f"; then say "source present: codex/$a"; else warn "source MISSING: $f"; ok=0; fi
  done
  for p in "$API_PORT" "$WEB_PORT"; do
    c="$(docker ps --filter "publish=$p" --format '{{.Names}}' | grep -vxE "$API_CONTAINER|$WEB_CONTAINER" || true)"
    if [ -n "$c" ]; then warn "host port $p is already published by: $c"; ok=0
    elif [ "$(http_code "http://$PROBE_HOST:$p/")" != 000 ] && ! owned container "$API_CONTAINER" api >/dev/null \
         && ! owned container "$WEB_CONTAINER" web >/dev/null; then
      warn "something already answers on $PROBE_HOST:$p"; ok=0
    else say "port $p: free (or already ours)"; fi
  done
  for c in "$API_CONTAINER:api" "$WEB_CONTAINER:web" "$LOADER:loader"; do owned container "${c%%:*}" "${c#*:}" || true; done
  owned volume "$ACCOUNTS_VOLUME" accounts || true
  owned network "$NETWORK" net || true
  [ "$ok" = 1 ] && say "check: OK" || die "check: fix the items above first"
}

cmd_build() {
  require_outer_daemon
  say "building $API_IMAGE (FastAPI + Claude Code + Codex CLI + yoloN/cyoloN wrappers, no credentials)"
  docker build --pull -t "$API_IMAGE" "$ROOT/api"
  say "building $WEB_IMAGE (static index.html, CSP connect-src = API port $API_PORT)"
  docker build --pull \
    --build-arg API_ORIGINS="http://127.0.0.1:$API_PORT http://localhost:$API_PORT" \
    -t "$WEB_IMAGE" "$ROOT/web"
  say "versions inside $API_IMAGE (through the container-local wrappers):"
  docker run --rm --network none --entrypoint /bin/sh "$API_IMAGE" -c \
    '/opt/lab04/bin/yolo1 --version; /opt/lab04/bin/cyolo1 --version'
}

cmd_token() {
  if [ -s "$TOKEN_FILE" ] && [ "${1:-}" != "--rotate" ]; then
    say "token already exists: $TOKEN_FILE (use 'token --rotate' to replace, then 'up')"
    return
  fi
  ( umask 077; mkdir -p "$SECRETS"
    od -An -N32 -tx1 /dev/urandom | tr -d ' \n' >"$TOKEN_FILE" )
  chmod 600 "$TOKEN_FILE"
  say "new API token written to $TOKEN_FILE (value not shown)."
  say "open it yourself when you need to paste it into the web page."
}

cmd_creds() {
  require_outer_daemon
  docker image inspect "$API_IMAGE" >/dev/null 2>&1 || die "build the image first"
  owned volume "$ACCOUNTS_VOLUME" accounts || docker volume create --label lab04=accounts "$ACCOUNTS_VOLUME" >/dev/null
  local dirs=() a
  for a in $(split "$CLAUDE_ACCOUNTS"); do dirs+=("/data/accounts/claude/$a"); done
  for a in $(split "$CODEX_ACCOUNTS"); do dirs+=("/data/accounts/codex/$a"); done
  # Paths go in as positional arguments, never spliced into the shell string.
  docker run --rm --user 0 --network none -v "$ACCOUNTS_VOLUME:/data/accounts" \
    --entrypoint /bin/sh "$API_IMAGE" -c 'mkdir -p -- "$@"' sh "${dirs[@]}"

  # A stopped container that only mounts the volume; docker cp writes into it.
  remove_own "$LOADER" loader
  docker create --name "$LOADER" --label lab04=loader --network none \
    -v "$ACCOUNTS_VOLUME:/data/accounts" --entrypoint /bin/true "$API_IMAGE" >/dev/null
  trap 'remove_own "$LOADER" loader || true' EXIT

  # devtools -> tar stream -> loader. Nothing is written to the control host's disk or printed.
  copy() { docker cp "$DEVTOOLS_CONTAINER:$1" - | docker cp - "$LOADER:$2/"; }
  for a in $(split "$CLAUDE_ACCOUNTS"); do
    copy "$SRC_CLAUDE_BASE/$a/.credentials.json" "/data/accounts/claude/$a"
    if [ "${CLAUDE_COPY_CLAUDE_JSON:-0}" = 1 ]; then
      copy "$SRC_CLAUDE_BASE/$a/.claude.json" "/data/accounts/claude/$a"
    fi
    say "copied claude/$a"
  done
  for a in $(split "$CODEX_ACCOUNTS"); do
    copy "$SRC_CODEX_BASE/$a/auth.json" "/data/accounts/codex/$a"
    say "copied codex/$a"
  done
  remove_own "$LOADER" loader; trap - EXIT

  docker run --rm --user 0 --network none -v "$ACCOUNTS_VOLUME:/data/accounts" \
    --entrypoint /bin/sh "$API_IMAGE" -c \
    "chown -R $APP_UID:$APP_UID /data/accounts && chmod -R u=rwX,go= /data/accounts"
  say "volume $ACCOUNTS_VOLUME contents (existence only):"
  docker run --rm --network none -v "$ACCOUNTS_VOLUME:/data/accounts:ro" --entrypoint /bin/sh "$API_IMAGE" -c \
    'for f in /data/accounts/claude/*/.credentials.json /data/accounts/codex/*/auth.json; do
       [ -s "$f" ] && echo "  present  $f" || echo "  MISSING  $f"; done'
  warn "these are COPIES. If either side refreshes a login, the other copy may stop working;"
  warn "re-login in devtools and run 'creds' again (see README section 9)."
}

cmd_up() {
  require_outer_daemon
  local hash; hash="$(token_hash)"
  docker image inspect "$API_IMAGE" >/dev/null 2>&1 || die "build the images first"
  owned volume "$ACCOUNTS_VOLUME" accounts || die "run 'creds' first"
  owned network "$NETWORK" net || docker network create --label lab04=net "$NETWORK" >/dev/null
  remove_own "$API_CONTAINER" api
  remove_own "$WEB_CONTAINER" web

  # Read-only rootfs. Writable: /tmp (per-request cwd/TMPDIR), /home/app (fixed HOME), the volume.
  docker run -d --name "$API_CONTAINER" --label lab04=api --hostname lab04-api \
    --network "$NETWORK" -p "$BIND_ADDR:$API_PORT:8000" \
    --read-only \
    --tmpfs "/tmp:rw,nosuid,nodev,size=512m,uid=$APP_UID,gid=$APP_UID,mode=0700" \
    --tmpfs "/home/app:rw,nosuid,nodev,size=256m,uid=$APP_UID,gid=$APP_UID,mode=0700" \
    --cap-drop ALL --security-opt no-new-privileges:true \
    --pids-limit 512 --memory 3g --cpus 2 \
    -v "$ACCOUNTS_VOLUME:/data/accounts" \
    -e API_TOKEN_SHA256="$hash" \
    -e CORS_ORIGINS="http://127.0.0.1:$WEB_PORT,http://localhost:$WEB_PORT" \
    -e CLAUDE_ACCOUNTS="$CLAUDE_ACCOUNTS" -e CODEX_ACCOUNTS="$CODEX_ACCOUNTS" \
    -e CLI_TIMEOUT_S="$CLI_TIMEOUT_S" -e PER_ACCOUNT_CONCURRENCY="$PER_ACCOUNT_CONCURRENCY" \
    -e MAX_CONCURRENCY="$MAX_CONCURRENCY" -e CODEX_SANDBOX="$CODEX_SANDBOX" \
    --restart unless-stopped "$API_IMAGE" >/dev/null

  docker run -d --name "$WEB_CONTAINER" --label lab04=web --hostname lab04-web \
    --network "$NETWORK" -p "$BIND_ADDR:$WEB_PORT:8080" \
    --read-only --tmpfs "/tmp:rw,nosuid,nodev,size=16m,uid=101,gid=101" \
    --cap-drop ALL --security-opt no-new-privileges:true \
    --pids-limit 64 --memory 64m \
    --restart unless-stopped "$WEB_IMAGE" >/dev/null

  say "waiting for $API_CONTAINER to become healthy…"
  local i s=starting
  for i in $(seq 1 45); do
    s="$(docker inspect -f '{{.State.Health.Status}}' "$API_CONTAINER" 2>/dev/null || echo gone)"
    [ "$s" = healthy ] && break
    [ "$s" = gone ] && die "API container exited; see: bash deploy/lab04.sh logs"
    sleep 2
  done
  [ "$s" = healthy ] || die "API not healthy after 90 s (status: $s); see logs"
  cmd_verify
  say "browser (Windows host): http://$BROWSER_HOST:$WEB_PORT  → API http://127.0.0.1:$API_PORT"
  say "token file on the control host: $TOKEN_FILE"
}

# Reachability, checked two ways, because the control host may itself be a container
# whose localhost is NOT the Docker Desktop host (use PROBE_HOST=host.docker.internal there).
cmd_verify() {
  require_outer_daemon
  local fail=0 code
  say "published ports: $(docker port "$API_CONTAINER" 8000 2>/dev/null | head -1) (api), $(docker port "$WEB_CONTAINER" 8080 2>/dev/null | head -1) (web)"
  if docker run --rm --network "$NETWORK" --entrypoint /opt/venv/bin/python "$API_IMAGE" -c '
import sys, urllib.request
for u in sys.argv[1:]:
    urllib.request.urlopen(u, timeout=5).read(64)' \
      "http://$API_CONTAINER:8000/health" "http://$WEB_CONTAINER:8080/" >/dev/null 2>&1; then
    say "  PASS container network: $API_CONTAINER:8000 and $WEB_CONTAINER:8080 answer on $NETWORK"
  else warn "  FAIL container network check on $NETWORK"; fail=1; fi
  code="$(http_code "http://$PROBE_HOST:$API_PORT/health")"
  if [ "$code" = 200 ]; then say "  PASS published API  $PROBE_HOST:$API_PORT/health (HTTP 200)"
  else warn "  FAIL published API  $PROBE_HOST:$API_PORT/health (HTTP $code)"; fail=1; fi
  code="$(http_code "http://$PROBE_HOST:$WEB_PORT/")"
  if [ "$code" = 200 ]; then say "  PASS published web  $PROBE_HOST:$WEB_PORT/ (HTTP 200)"
  else warn "  FAIL published web  $PROBE_HOST:$WEB_PORT/ (HTTP $code)"; fail=1; fi
  if [ "$fail" = 1 ]; then
    warn "a published-port FAIL from this control host is not proof that the Windows browser fails:"
    warn "set PROBE_HOST correctly (127.0.0.1 on the Docker Desktop host itself, host.docker.internal"
    warn "from a container) and confirm in the browser. Not marking this as PASS."
    return 1
  fi
}

cmd_smoke() {
  require_outer_daemon
  local H="http://$PROBE_HOST:$API_PORT" W="http://$PROBE_HOST:$WEB_PORT" pass=0 fail=0 code body
  result() { if [ "$1" = PASS ]; then pass=$((pass+1)); else fail=$((fail+1)); fi; printf '  %-4s %s\n' "$1" "$2"; }
  expect() { if [ "$2" = "$3" ]; then result PASS "$1 (HTTP $2)"; else result FAIL "$1 (HTTP $2, expected $3)"; fi; }

  say "readiness checks via $PROBE_HOST (no model is called)"
  code="$(http_code "$H/health")"; expect "GET /health" "$code" 200
  code="$(http_code "$H/v1/models")"; expect "GET /v1/models without token -> 401" "$code" 401
  code="$(curl_auth -o /dev/null -w '%{http_code}' "$H/v1/models")"; expect "GET /v1/models with token" "$code" 200
  body="$(curl_auth "$H/v1/models")"
  grep -q '"credential_file_present":true' <<<"$body" \
    && result PASS "at least one account has a credential file (NOT proof of login)" \
    || result FAIL "no account has a credential file in the volume"

  # CORS is checked with the browser's origins; the probe host only changes where curl connects.
  local pre=(-X OPTIONS -H "Access-Control-Request-Method: POST" -H "Access-Control-Request-Headers: authorization,content-type")
  { curl -s -D - -o /dev/null "${pre[@]}" -H "Origin: http://localhost:$WEB_PORT" "$H/v1/chat/completions" || true; } \
    | grep -qi "^access-control-allow-origin: http://localhost:$WEB_PORT" \
    && result PASS "CORS allows the web page origin" || result FAIL "CORS does not allow the web page origin"
  { curl -s -D - -o /dev/null "${pre[@]}" -H "Origin: http://evil.example" "$H/v1/chat/completions" || true; } \
    | grep -qi "^access-control-allow-origin" \
    && result FAIL "CORS allowed a foreign origin" || result PASS "CORS rejects a foreign origin"

  local q='"messages":[{"role":"user","content":"hi"}]'
  code="$(curl_auth -o /dev/null -w '%{http_code}' -H 'Content-Type: application/json' \
    -d "{\"model\":\"gpt-6-astra\",\"reasoning_effort\":\"none\",$q}" "$H/v1/chat/completions")"
  expect "gpt-6-astra + effort none rejected" "$code" 400
  code="$(curl_auth -o /dev/null -w '%{http_code}' -H 'Content-Type: application/json' \
    -d "{\"model\":\"fable\",\"reasoning_effort\":\"minimal\",$q}" "$H/v1/chat/completions")"
  expect "fable + effort minimal rejected" "$code" 400
  code="$(curl_auth -o /dev/null -w '%{http_code}' -H 'Content-Type: application/json' \
    -d "{\"model\":\"fable\",\"max_completion_tokens\":50,$q}" "$H/v1/chat/completions")"
  expect "max_completion_tokens rejected" "$code" 400
  local n spare=""
  for n in 1 2 3 4 5; do [[ ",$CLAUDE_ACCOUNTS," == *",yolo$n,"* ]] || { spare="yolo$n"; break; }; done
  if [ -n "$spare" ]; then
    code="$(curl_auth -o /dev/null -w '%{http_code}' -H 'Content-Type: application/json' \
      -d "{\"model\":\"fable\",\"account\":\"$spare\",$q}" "$H/v1/chat/completions")"
    expect "account $spare (not enabled for this API) rejected" "$code" 400
  fi
  code="$(curl_auth -o /dev/null -w '%{http_code}' -H 'Content-Type: application/json' \
    -d "{\"model\":\"gpt-6-astra\",\"account\":\"$(split "$CLAUDE_ACCOUNTS" | cut -d' ' -f1)\",$q}" "$H/v1/chat/completions")"
  expect "Claude account name on a Codex model rejected" "$code" 400

  code="$(http_code "$W/")"; expect "web page GET /" "$code" 200
  { curl -s -D - -o /dev/null "$W/" || true; } | grep -qi "^content-security-policy: .*connect-src http://127.0.0.1:$API_PORT" \
    && result PASS "web page CSP limits connect-src to the API" || result FAIL "web page CSP header missing"

  if [ "${1:-}" = --live ]; then
    say "AUTHENTICATED checks: one real reply per default account (uses account quota)"
    local c x model
    for c in "claude:fable" "codex:gpt-6-astra"; do
      model="${c#*:}"
      x="$(curl_auth -w '\n%{http_code}' -H 'Content-Type: application/json' --max-time $((CLI_TIMEOUT_S+30)) \
        -d "{\"model\":\"$model\",\"reasoning_effort\":\"low\",\"messages\":[{\"role\":\"user\",\"content\":\"ตอบคำว่า pong เพียงคำเดียว\"}]}" \
        "$H/v1/chat/completions")"
      code="${x##*$'\n'}"; body="${x%$'\n'*}"
      expect "real reply from ${c%%:*} default account ($model/low)" "$code" 200
      printf '       %s\n' "$(head -c 300 <<<"$body")"
    done
  else
    say "skipped authenticated checks (add --live). Readiness != authenticated model success."
  fi
  say "smoke: $pass PASS, $fail FAIL"
  [ "$fail" = 0 ]
}

cmd_status() {
  require_outer_daemon
  docker ps -a --filter label=lab04 --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
  curl -s --max-time 5 "http://$PROBE_HOST:$API_PORT/health" && echo \
    || warn "API not reachable on $PROBE_HOST:$API_PORT from this control host"
}

cmd_logs() {
  require_outer_daemon
  local n="${1:-100}"; [[ "$n" =~ ^[0-9]{1,5}$ ]] || die "logs: N must be a number"
  owned container "$API_CONTAINER" api || die "no $API_CONTAINER container"
  docker logs --tail "$n" "$API_CONTAINER"
}

cmd_down() {
  require_outer_daemon
  remove_own "$API_CONTAINER" api; remove_own "$WEB_CONTAINER" web; remove_own "$LOADER" loader
  say "lab04 containers removed"
  if [ "${1:-}" = --purge ]; then
    if owned volume "$ACCOUNTS_VOLUME" accounts; then docker volume rm "$ACCOUNTS_VOLUME" >/dev/null; say "credential volume $ACCOUNTS_VOLUME deleted"; fi
    if owned network "$NETWORK" net; then docker network rm "$NETWORK" >/dev/null; say "network $NETWORK deleted"; fi
  else
    say "kept volume $ACCOUNTS_VOLUME (credential copies). Use 'down --purge' to delete it."
  fi
}

validate_config
case "${1:-}" in
  check|build|creds|up|verify|status) cmd="cmd_$1"; shift; "$cmd" "$@" ;;
  token|smoke|logs|down) cmd="cmd_$1"; shift; "$cmd" "$@" ;;
  *) sed -n '2,20p' "$0"; exit 2 ;;
esac
