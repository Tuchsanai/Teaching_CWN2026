#!/bin/bash
# LAB 5 · step 6: real training on the 2-node cluster, one approach at a time.
#   400 first receipts of the Training Set (shuffled with seed 0) · 1 Epoch · Effective Batch 8 -> 50 updates
#   A = 2 replicas (1 per node, model split over the node's 2 GPUs), accum 4
#   B = 4 replicas (1 per GPU), accum 2 · B starts again from the base model (new processes)
# Runs from the control machine (container) under nohup. Every remote process is started with nohup,
# so training keeps going even if an SSH connection drops; the wait loop retries SSH errors (exit 255)
# instead of treating them as "finished".
# Usage: N1=ip:sshport N2=ip:sshport COORD=ip:extport nohup setsid bash run_train.sh > run_train.log 2>&1 &
set -u
KEY=${KEY:-/workspace/vastai_lab/Devtool_SSH/devtoolSSH}
OUT=/workspace/lab5/train_2node
LIMIT=400; STEPS=50
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

running() {  # 0 = something still running on either node
  ssh_n "$N1" "pgrep -f '^python (coordinator|worker).py' >/dev/null" && return 0
  ssh_n "$N2" "pgrep -f '^python worker.py' >/dev/null" && return 0
  return 1
}

run() {  # name mode replicas accum
  local name=$1 mode=$2 n=$3 accum=$4 d="$OUT/$1"
  local t0=$(date +%s)
  echo "=== $name start $(date +%T)  replicas $n · accum $accum · updates $STEPS"
  ssh_n "$N1" "$ENVS; rm -rf $d; mkdir -p $d; nohup python coordinator.py --replicas $n --steps $STEPS --warmup 0 \
      --out $d/coordinator.json > $d/coordinator.log 2>&1 < /dev/null &"
  ssh_n "$N2" "rm -rf $d; mkdir -p $d"
  sleep 3
  if [ "$mode" = A ]; then
    ssh_n "$N1" "$ENVS; nohup python worker.py --mode A --gpus 0,1 --accum $accum --coord 127.0.0.1:9000 $W \
        --save-adapter $d/adapter --out $d > $d/worker_n1.log 2>&1 < /dev/null &"
    ssh_n "$N2" "$ENVS; nohup python worker.py --mode A --gpus 0,1 --accum $accum --coord $COORD $W \
        --save-adapter $d/adapter --out $d > $d/worker_n2.log 2>&1 < /dev/null &"
  else
    for g in 0 1; do
      ssh_n "$N1" "$ENVS; nohup python worker.py --mode B --gpus $g --accum $accum --coord 127.0.0.1:9000 $W \
          --save-adapter $d/adapter --out $d > $d/worker_n1_g$g.log 2>&1 < /dev/null &"
      ssh_n "$N2" "$ENVS; nohup python worker.py --mode B --gpus $g --accum $accum --coord $COORD $W \
          --save-adapter $d/adapter --out $d > $d/worker_n2_g$g.log 2>&1 < /dev/null &"
    done
  fi
  sleep 30
  while running; do
    ssh_n "$N1" "grep -h 'step ' $d/coordinator.log | tail -1" | sed "s/^/  [$name $(date +%T)] /"
    sleep 60
  done
  echo "=== $name finished $(date +%T)  wall $(( $(date +%s) - t0 )) s"
  ssh_n "$N1" "tail -1 $d/coordinator.log"
  echo "$(( $(date +%s) - t0 ))" | ssh_n "$N1" "cat > $d/round_wall_s.txt"
}

ssh_n "$N1" "mkdir -p $OUT"; ssh_n "$N2" "mkdir -p $OUT"
run A A 2 4
run B B 4 2
ssh_n "$N1" "touch $OUT/ALL_DONE"
echo ALL_DONE
