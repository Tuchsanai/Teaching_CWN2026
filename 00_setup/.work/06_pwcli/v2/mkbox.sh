#!/bin/bash
# fresh student-like container + borrowed yolo1/yolo2 credentials (never printed)
set -e
N=${1:-pwcli-lab06-test}
docker rm -f $N >/dev/null 2>&1 || true
docker run -d --name $N tuchsanai/multi-account-devtool:2569_1 >/dev/null
for i in $(seq 1 30); do docker exec $N test -d /root/ai-accounts/.Claude/yolo2 2>/dev/null && break; sleep 2; done
for a in yolo1 yolo2; do
  docker cp /root/workspace/.Claude/$a/.credentials.json $N:/root/ai-accounts/.Claude/$a/.credentials.json
  docker exec $N bash -c "chmod 600 /root/ai-accounts/.Claude/$a/.credentials.json; f=/root/ai-accounts/.Claude/$a/.claude.json; [ -s \$f ] || echo '{\"hasCompletedOnboarding\":true,\"theme\":\"dark\"}' > \$f"
done
docker exec $N bash -lc 'for a in yolo1 yolo2; do printf "%s: " $a; $a auth status --text 2>&1 | head -1; done; ls -la /workspace'
