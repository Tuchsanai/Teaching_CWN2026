#!/bin/bash
# cap.sh <name>: pause 2s then snapshot+screenshot to retry-watch/<name>
D="$(dirname "$0")"
"$D/pw.sh" -s=lab05-human snapshot --filename=$D/$1.yml >/dev/null
"$D/pw.sh" -s=lab05-human screenshot --filename=$D/$1.png >/dev/null
