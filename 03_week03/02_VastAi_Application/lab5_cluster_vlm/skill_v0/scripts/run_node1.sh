#!/bin/bash
# LAB 5 · step 4: 4 baseline runs on Node 1 (coordinator + replicas on the same machine).
# Usage: [RUNS="A_eb8 B_eb8 A_eb32 B_eb32"] [STEPS=n WARMUP=n] nohup bash run_node1.sh > runs_node1.log 2>&1 &
#   RUNS   = runs to measure, each <A|B>_eb<Effective Batch> (default: the 4 runs of LAB 5)
#   STEPS / WARMUP = weight updates per run / first updates not counted
#            (default per run: EB <= 8 -> 20 / 3 · otherwise 8 / 2)
#   replicas on 1 node: A = 1 (model over GPU 0,1) · B = 2 (1 per GPU) · accum = EB / replicas
set -u
# driver 535 + CUDA 12.8 image: use the host driver libs, not the forward-compat ones (error 804)
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu
cd "$(dirname "$0")"
SECRET=/workspace/lab5/cluster_secret
[ -s "$SECRET" ] || { umask 077; python -c "import secrets;print(secrets.token_hex(32))" > "$SECRET"; }
OUT=${OUT:-/workspace/lab5/runs_node1}
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

for name in ${RUNS:-A_eb8 B_eb8 A_eb32 B_eb32}; do
  mode=${name%%_eb*}; eb=${name#*_eb}
  if [ "$mode" = A ]; then n=1; else n=2; fi
  [ $((eb % n)) -eq 0 ] || { echo "skip $name: EB $eb not divisible by $n replicas"; continue; }
  if [ "$eb" -le 8 ]; then s=20; w=3; else s=8; w=2; fi
  run "$name" "$mode" "$n" $((eb / n)) "${STEPS:-$s}" "${WARMUP:-$w}"
done
touch "$OUT/ALL_DONE"
