#!/bin/bash
# LAB 5 · step 6: real training on the cluster, one approach at a time.
#   default (LAB 5): 400 first receipts of the Training Set (shuffled with seed 0) · 1 Epoch · Effective Batch 8 -> 50 updates
#   A = 1 replica per node (model split over the node's 2 GPUs) · B = 1 replica per GPU
#   accum = EB / replicas · every approach starts again from the base model (new processes)
# Runs from the control machine (container) under nohup. Every remote process is started with nohup,
# so training keeps going even if an SSH connection drops; the wait loop retries SSH errors (exit 255)
# instead of treating them as "finished".
# Usage: N1=ip:sshport N2=ip:sshport COORD=ip:extport nohup setsid bash run_train.sh > run_train.log 2>&1 &
#   or   NODES="ip:sshport ip:sshport ..." COORD=ip:extport ...      (1 or more nodes, first = Node 1)
#   APPROACHES="A B" · LIMIT=400 (receipts) · EB=8 · EPOCHS=1 · OUT=/workspace/lab5/train_2node
set -u
KEY=${KEY:-/workspace/vastai_lab/Devtool_SSH/devtoolSSH}
OUT=${OUT:-/workspace/lab5/train_2node}
NODES=${NODES:-"$N1 $N2"}; read -r -a NL <<< "$NODES"; N1=${NL[0]}; K=${#NL[@]}
COORD=${COORD:-127.0.0.1:9000}
LIMIT=${LIMIT:-400}; EB=${EB:-8}; EPOCHS=${EPOCHS:-1}
[ $((LIMIT % EB)) -eq 0 ] || { echo "LIMIT $LIMIT must be a multiple of EB $EB"; exit 1; }
STEPS=$((EPOCHS * LIMIT / EB))
ssh_n() {  # host:port cmd   (retries up to 20x on SSH errors, keeps the remote exit code otherwise)
  local hp=$1; shift; local rc
  for i in $(seq 20); do
    ssh -i "$KEY" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
        -o ConnectTimeout=20 -o ServerAliveInterval=30 -p "${hp#*:}" "root@${hp%:*}" "$@"
    rc=$?; [ $rc -ne 255 ] && return $rc
    echo "  (ssh ${hp%:*} dropped, retry $i)" >&2; sleep 15
  done
  return 255
}
ENVS='export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu; cd /workspace/lab5'
W="--train-limit $LIMIT"

running() {  # 0 = something still running on any node
  local hp
  for hp in "${NL[@]}"; do ssh_n "$hp" "pgrep -f '^python (coordinator|worker).py' >/dev/null" && return 0; done
  return 1
}

run() {  # name mode replicas accum
  local name=$1 mode=$2 n=$3 accum=$4 d="$OUT/$1" i=0 hp c
  local t0=$(date +%s)
  echo "=== $name start $(date +%T)  replicas $n · accum $accum · updates $STEPS"
  for hp in "${NL[@]}"; do ssh_n "$hp" "rm -rf $d; mkdir -p $d"; done
  ssh_n "$N1" "$ENVS; nohup python coordinator.py --replicas $n --steps $STEPS --warmup 0 \
      --out $d/coordinator.json > $d/coordinator.log 2>&1 < /dev/null &"
  sleep 3
  for hp in "${NL[@]}"; do
    i=$((i+1)); if [ $i -eq 1 ]; then c=127.0.0.1:9000; else c=$COORD; fi
    if [ "$mode" = A ]; then
      ssh_n "$hp" "$ENVS; nohup python worker.py --mode A --gpus 0,1 --accum $accum --coord $c $W \
          --save-adapter $d/adapter --out $d > $d/worker_n$i.log 2>&1 < /dev/null &"
    else
      for g in 0 1; do
        ssh_n "$hp" "$ENVS; nohup python worker.py --mode B --gpus $g --accum $accum --coord $c $W \
            --save-adapter $d/adapter --out $d > $d/worker_n${i}_g$g.log 2>&1 < /dev/null &"
      done
    fi
  done
  sleep 30
  while running; do
    ssh_n "$N1" "grep -h 'step ' $d/coordinator.log | tail -1" | sed "s/^/  [$name $(date +%T)] /"
    sleep 60
  done
  echo "=== $name finished $(date +%T)  wall $(( $(date +%s) - t0 )) s"
  ssh_n "$N1" "tail -1 $d/coordinator.log"
  echo "$(( $(date +%s) - t0 ))" | ssh_n "$N1" "cat > $d/round_wall_s.txt"
}

for hp in "${NL[@]}"; do ssh_n "$hp" "mkdir -p $OUT"; done
for ap in ${APPROACHES:-A B}; do
  if [ "$ap" = A ]; then n=$K; else n=$((2 * K)); fi
  [ $((EB % n)) -eq 0 ] || { echo "skip $ap: EB $EB not divisible by $n replicas"; continue; }
  run "$ap" "$ap" "$n" $((EB / n))
done
ssh_n "$N1" "touch $OUT/ALL_DONE"
echo ALL_DONE
