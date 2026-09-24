#!/usr/bin/env bash
# LAB 004 · drive deploy/lab04.sh on the control host FROM devtools.
#
# devtools is only the control/authoring center: its default `docker` is a nested
# (inner) daemon, so it cannot create sibling containers. The outer Docker Desktop
# daemon is reached through a control host over SSH (class setup:
# root@host.docker.internal port 22022). This script opens ONE temporary OpenSSH
# ControlMaster connection (you type the password once, interactively), then reuses
# it with `ssh -S <socket>` for every step.
#
#   bash deploy/remote.sh open            # password prompt once; socket in a private temp dir
#   bash deploy/remote.sh daemon          # which daemon does the control host's docker use?
#   bash deploy/remote.sh sync            # copy this folder to REMOTE_DIR (never deploy/.secrets)
#   bash deploy/remote.sh run check       # run `bash deploy/lab04.sh check` on the control host
#   bash deploy/remote.sh run build|token|creds|up|verify|smoke [--live]|status|logs [N]|down [--purge]
#   bash deploy/remote.sh reveal-token    # YOU run this to see the API token (never an AI agent)
#   bash deploy/remote.sh close           # close the master connection, delete the temp dir
#
# Nothing persistent is changed: no ~/.ssh/config, no keys, no known_hosts outside the
# temp dir (-F /dev/null, UserKnownHostsFile in the temp dir), no stored password.
set -euo pipefail

SSH_USER="${LAB04_SSH_USER:-root}"
SSH_HOST="${LAB04_SSH_HOST:-host.docker.internal}"
SSH_PORT="${LAB04_SSH_PORT:-22022}"
REMOTE_DIR="${LAB04_REMOTE_DIR:-/root/workspace/CWN/Teaching/00_setup/04_API_MultiAccount_Server}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$HERE")"
CTL_DIR="${TMPDIR:-/tmp}/lab04-ssh-$(id -u)"
SOCK="$CTL_DIR/ctl"

say() { printf '\033[1;34m[remote]\033[0m %s\n' "$*"; }
die() { printf '\033[1;31m[remote]\033[0m %s\n' "$*" >&2; exit 1; }

[[ "$SSH_USER" =~ ^[a-z_][a-z0-9_-]{0,31}$ ]] || die "bad LAB04_SSH_USER"
[[ "$SSH_HOST" =~ ^[A-Za-z0-9][A-Za-z0-9.-]{0,252}$ ]] || die "bad LAB04_SSH_HOST"
[[ "$SSH_PORT" =~ ^[0-9]{1,5}$ ]] || die "bad LAB04_SSH_PORT"
[[ "$REMOTE_DIR" =~ ^/[A-Za-z0-9._/-]+$ && "$REMOTE_DIR" != *..* ]] || die "bad LAB04_REMOTE_DIR"

SSH_OPTS=(-F /dev/null -p "$SSH_PORT"
          -o UserKnownHostsFile="$CTL_DIR/known_hosts" -o StrictHostKeyChecking=ask
          -o PubkeyAuthentication=no -o PreferredAuthentications=keyboard-interactive,password)
TARGET="$SSH_USER@$SSH_HOST"

alive() { [ -S "$SOCK" ] && ssh "${SSH_OPTS[@]}" -S "$SOCK" -O check "$TARGET" >/dev/null 2>&1; }

# Run one command on the control host through the existing master. BatchMode: if the
# master is gone, fail instead of asking for a password again.
rssh() {
  alive || die "no open connection: run 'bash deploy/remote.sh open' first"
  ssh "${SSH_OPTS[@]}" -S "$SOCK" -o ControlMaster=no -o BatchMode=yes "$TARGET" "$@"
}

cmd_open() {
  if alive; then say "already open ($SOCK)"; return; fi
  ( umask 077; mkdir -p "$CTL_DIR" ); chmod 700 "$CTL_DIR"
  say "connecting to $TARGET port $SSH_PORT (type the password when asked; it is not stored)"
  ssh "${SSH_OPTS[@]}" -o ControlMaster=yes -o ControlPath="$SOCK" -o ControlPersist=2h -fN "$TARGET"
  alive || die "master connection did not come up"
  say "open. Reused with ssh -S $SOCK; closes by itself after 2 h idle, or run 'close'."
}

cmd_daemon() {
  local local_name remote_name
  local_name="$(docker info --format '{{.Name}}' 2>/dev/null || echo n/a)"
  remote_name="$(rssh "docker info --format '{{.Name}}'")"
  say "devtools default docker daemon : $local_name   (nested/inner: NOT used for this lab)"
  say "control host docker daemon     : $remote_name   (must be docker-desktop)"
  [ "$remote_name" = docker-desktop ] || die "control host is not talking to the outer Docker Desktop daemon"
}

cmd_sync() {
  say "copying $ROOT -> $TARGET:$REMOTE_DIR (excluding deploy/.secrets and caches)"
  tar -C "$ROOT" -cf - \
      --exclude='./deploy/.secrets' --exclude='__pycache__' --exclude='*.pyc' . \
    | rssh "mkdir -p '$REMOTE_DIR' && tar -xf - -C '$REMOTE_DIR' --no-same-owner"
  rssh "cd '$REMOTE_DIR' && chmod +x deploy/lab04.sh deploy/remote.sh api/wrappers/lab04-cli && ls -1"
}

cmd_run() {
  local sub="${1:-}" arg="${2:-}"
  case "$sub" in
    check|build|creds|up|verify|status) [ -z "$arg" ] || die "'$sub' takes no argument" ;;
    token) [ -z "$arg" ] || [ "$arg" = --rotate ] || die "token [--rotate]" ;;
    smoke) [ -z "$arg" ] || [ "$arg" = --live ] || die "smoke [--live]" ;;
    down)  [ -z "$arg" ] || [ "$arg" = --purge ] || die "down [--purge]" ;;
    logs)  [ -z "$arg" ] || [[ "$arg" =~ ^[0-9]{1,5}$ ]] || die "logs [N]" ;;
    *) die "run: unknown step '$sub'" ;;
  esac
  rssh "cd '$REMOTE_DIR' && bash deploy/lab04.sh $sub $arg"
}

cmd_reveal_token() {
  printf 'This prints the API token to YOUR terminal. Do not paste it into an AI chat, a screenshot or a commit.\nType yes to continue: ' >&2
  local ans; read -r ans; [ "$ans" = yes ] || die "cancelled"
  rssh "cat '$REMOTE_DIR/deploy/.secrets/api_token'"; echo
}

cmd_close() {
  if alive; then ssh "${SSH_OPTS[@]}" -S "$SOCK" -O exit "$TARGET" >/dev/null 2>&1 || true; fi
  rm -rf -- "$CTL_DIR"
  say "closed; removed $CTL_DIR"
}

case "${1:-}" in
  open) cmd_open ;;
  daemon) cmd_daemon ;;
  sync) cmd_sync ;;
  run) shift; cmd_run "$@" ;;
  reveal-token) cmd_reveal_token ;;
  close) cmd_close ;;
  *) sed -n '2,22p' "$0"; exit 2 ;;
esac
