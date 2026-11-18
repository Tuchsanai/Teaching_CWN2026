#!/bin/bash
# LAB 6 · เทียบวิธีแจกงาน round-robin vs least_conn (2 replica x 4 process, batch 32)
cd /workspace/lab6
C=code/cluster.sh
run() { # name, up-args...
  local name=$1; shift
  echo "=== $(date '+%T') $name : cluster.sh up $*"
  bash $C up "$@" > results/${name}_up.log 2>&1 || { echo "up failed for $name"; tail results/${name}_up.log; return 1; }
  tail -1 results/${name}_up.log
  python code/loadgen.py --name "$name" > results/${name}.log 2>&1
  tail -2 results/${name}.log
}
run lc2     2 4 32 --lb least_conn
run rr_slow 2 4 32 --lb round_robin --slow 1:40
run lc_slow 2 4 32 --lb least_conn  --slow 1:40
echo "ALL DONE $(date '+%T')"
