#!/usr/bin/env bash
# wrapper: log every playwright-cli command with UTC time + monotonic elapsed
LOG="$(dirname "$0")/commands.log"
t0=$(cut -d' ' -f1 /proc/uptime)
ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
out=$(playwright-cli -s=trip "$@" 2>&1); rc=$?
t1=$(cut -d' ' -f1 /proc/uptime)
el=$(awk -v a="$t0" -v b="$t1" 'BEGIN{printf "%.2f", b-a}')
printf '%s | mono %s→%s | %ss | rc=%s | playwright-cli -s=trip %s\n' "$ts" "$t0" "$t1" "$el" "$rc" "$*" >> "$LOG"
echo "$out"
echo "[rc=$rc elapsed=${el}s]"
