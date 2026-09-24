#!/bin/bash
# wrapper: logs each playwright-cli command to commands.log
L="$(dirname "$0")/commands.log"
S=$(cut -d' ' -f1 /proc/uptime); U=$(date -u +%FT%TZ)
playwright-cli "$@"; RC=$?
E=$(cut -d' ' -f1 /proc/uptime)
echo "$U | mono $S→$E | $(awk "BEGIN{printf \"%.2f\", $E-$S}") | rc=$RC | playwright-cli $*" >> "$L"
exit $RC
