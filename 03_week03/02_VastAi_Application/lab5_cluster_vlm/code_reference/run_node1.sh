#!/bin/bash
# LAB 5 · step 4: 4 baseline runs on Node 1 (coordinator + replicas on the same machine).
# Usage: nohup bash run_node1.sh > runs_node1.log 2>&1 &
set -u
# driver 535 + CUDA 12.8 image: use the host driver libs, not the forward-compat ones (error 804)
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu
cd "$(dirname "$0")"
SECRET=/workspace/lab5/cluster_secret
[ -s "$SECRET" ] || { umask 077; python -c "import secrets;print(secrets.token_hex(32))" > "$SECRET"; }
OUT=/workspace/lab5/runs_node1
mkdir -p "$OUT"

run() {  # name mode replicas accum steps warmup
  local name=$1 mode=$2 n=$3 accum=$4 steps=$5 warm=$6 d="$OUT/$1"
  mkdir -p "$d"; echo "=== $name $(date +%T)"
  python coordinator.py --replicas "$n" --steps "$steps" --warmup "$warm" --out "$d/coordinator.json" > "$d/coordinator.log" 2>&1 &
  local cpid=$!; sleep 2
  if [ "$mode" = A ]; then
    python worker.py --mode A --gpus 0,1 --accum "$accum" --out "$d" > "$d/worker_r0.log" 2>&1 &
  else
    for g in $(seq 0 $((n-1))); do
      python worker.py --mode B --gpus "$g" --accum "$accum" --out "$d" > "$d/worker_g$g.log" 2>&1 &
    done
  fi
  wait
  echo "=== $name finished $(date +%T)"; tail -1 "$d/coordinator.log"
}

run A_eb8  A 1 8  20 3
run B_eb8  B 2 4  20 3
run A_eb32 A 1 32 8  2
run B_eb32 B 2 16 8  2
touch "$OUT/ALL_DONE"
