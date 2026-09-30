#!/bin/bash
# usage: log.sh <playwright-cli args...>  — appends command, output, exit code to lab4/stale.txt
cd /workspace
out=$(playwright-cli "$@" 2>&1); code=$?
{ echo "\$ playwright-cli $*"; echo "$out"; echo "[exit code: $code]"; echo; } >> lab4/stale.txt
echo "\$ playwright-cli $*"; echo "$out"; echo "[exit code: $code]"
