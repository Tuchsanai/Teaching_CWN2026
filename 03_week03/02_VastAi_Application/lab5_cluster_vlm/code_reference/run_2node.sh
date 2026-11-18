#!/bin/bash
# LAB 5 · step 5: the same 4 runs as step 4, on a 2-node cluster.
# Runs from the control machine (container); the coordinator lives on Node 1.
#   A = 1 replica per node (model split over the node's 2 GPUs)   -> 2 replicas
#   B = 1 replica per GPU                                          -> 4 replicas
# Effective Batch stays 8 / 32, so each replica accumulates half as many receipts as on 1 node.
# Usage: [SKIP="A_eb8"] N1=ip:sshport N2=ip:sshport COORD=ip:extport nohup bash run_2node.sh > runs_2node.log 2>&1 &
set -u
KEY=${KEY:-/workspace/vastai_lab/Devtool_SSH/devtoolSSH}
OUT=/workspace/lab5/runs_2node
ssh_n() {  # host:port cmd
  local hp=$1; shift
  ssh -i "$KEY" -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -o LogLevel=ERROR \
      -p "${hp#*:}" "root@${hp%:*}" "$@"
}
ENVS='export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu; cd /workspace/lab5'

run() {  # name mode replicas accum steps warmup
  case " ${SKIP:-} " in *" $1 "*) echo "=== $1 skipped (already done)"; return;; esac
  local name=$1 mode=$2 n=$3 accum=$4 steps=$5 warm=$6 d="$OUT/$1"
  echo "=== $name $(date +%T)  replicas $n · accum $accum · steps $steps"
  ssh_n "$N1" "$ENVS; mkdir -p $d; nohup python coordinator.py --replicas $n --steps $steps --warmup $warm \
      --out $d/coordinator.json > $d/coordinator.log 2>&1 < /dev/null &"
  sleep 3
  if [ "$mode" = A ]; then
    ssh_n "$N1" "$ENVS; nohup python worker.py --mode A --gpus 0,1 --accum $accum --coord 127.0.0.1:9000 \
        --out $d > $d/worker_n1.log 2>&1 < /dev/null &"
    ssh_n "$N2" "$ENVS; mkdir -p $d; nohup python worker.py --mode A --gpus 0,1 --accum $accum --coord $COORD \
        --out $d > $d/worker_n2.log 2>&1 < /dev/null &"
  else
    for g in 0 1; do
      ssh_n "$N1" "$ENVS; nohup python worker.py --mode B --gpus $g --accum $accum --coord 127.0.0.1:9000 \
          --out $d > $d/worker_n1_g$g.log 2>&1 < /dev/null &"
      ssh_n "$N2" "$ENVS; mkdir -p $d; nohup python worker.py --mode B --gpus $g --accum $accum --coord $COORD \
          --out $d > $d/worker_n2_g$g.log 2>&1 < /dev/null &"
    done
  fi
  # wait until the coordinator and every worker on both nodes have exited
  # (pattern anchored on "^python" so pgrep does not match this ssh command line itself)
  while ssh_n "$N1" "pgrep -f '^python (coordinator|worker).py' >/dev/null" || ssh_n "$N2" "pgrep -f '^python worker.py' >/dev/null"; do
    sleep 20
  done
  echo "=== $name finished $(date +%T)"; ssh_n "$N1" "tail -1 $d/coordinator.log"
}

ssh_n "$N1" "mkdir -p $OUT"; ssh_n "$N2" "mkdir -p $OUT"
run A_eb8  A 2 4  20 3
run B_eb8  B 4 2  20 3
run A_eb32 A 2 16 8  2
run B_eb32 B 4 8  8  2
ssh_n "$N1" "touch $OUT/ALL_DONE"
echo ALL_DONE
