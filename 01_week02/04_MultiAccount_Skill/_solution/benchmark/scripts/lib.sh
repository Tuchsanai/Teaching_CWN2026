#!/bin/bash
# shared helpers for the s04b benchmark
export MSYS_NO_PATHCONV=1
C=multi-account
EV=C:/t/s04b/eval
install_skills() {  # $1 = host dir containing yolo cyolo agent-team
  docker exec $C sh -c 'for d in .Claude .Codex; do cd /root/ai-accounts/$d/shared/skills && rm -rf yolo cyolo agent-team; done'
  if [ -n "$1" ]; then
    for d in .Claude .Codex; do for s in yolo cyolo agent-team; do docker cp "$1/$s" $C:/root/ai-accounts/$d/shared/skills/ >/dev/null; done; done
    docker exec $C sh -c 'find /root/ai-accounts/.Claude/shared/skills /root/ai-accounts/.Codex/shared/skills -name __pycache__ -prune -exec rm -rf {} +' 
  fi
  docker exec $C bash -lc 'for n in 1 2 3 4 5; do yolo$n --version; cyolo$n --version; done' >/dev/null 2>&1
}
reset_ws() {
  docker exec $C sh -c 'rm -rf /workspace/.agent-team /workspace/team-demo /workspace/demo /workspace/held-out /workspace/* /tmp/agent-team* /tmp/ma-* /tmp/ma_* /tmp/yolo* /tmp/cyolo* /tmp/team* 2>/dev/null; mkdir -p /workspace/held-out'
  for p in part1 part2 part3; do docker cp $EV/data/$p.txt $C:/workspace/held-out/ >/dev/null; done
}
