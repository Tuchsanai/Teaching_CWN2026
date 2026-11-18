#!/bin/bash
# LAB 5 · step 5: the same 4 runs as step 4, on a 2-node cluster.
# Runs from the control machine (container); the coordinator lives on Node 1.
#   A = 1 replica per node (model split over the node's 2 GPUs)   -> 2 replicas
#   B = 1 replica per GPU                                          -> 4 replicas
# Effective Batch stays 8 / 32, so each replica accumulates half as many receipts as on 1 node.
# Usage: [SKIP="A_eb8"] N1=ip:sshport N2=ip:sshport COORD=ip:extport nohup bash run_2node.sh > runs_2node.log 2>&1 &
#   or   NODES="ip:sshport ip:sshport ip:sshport" COORD=ip:extport ...   (2 or more nodes, first = Node 1)
#   RUNS / STEPS / WARMUP / OUT as in run_node1.sh · replicas: A = nodes · B = 2 x nodes · accum = EB / replicas
set -u
KEY=${KEY:-/workspace/vastai_lab/Devtool_SSH/devtoolSSH}
OUT=${OUT:-/workspace/lab5/runs_2node}
NODES=${NODES:-"$N1 $N2"}; read -r -a NL <<< "$NODES"; N1=${NL[0]}
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
  local i=0 hp c busy
  for hp in "${NL[@]}"; do
    i=$((i+1)); if [ $i -eq 1 ]; then c=127.0.0.1:9000; else c=$COORD; fi
    if [ "$mode" = A ]; then
      ssh_n "$hp" "$ENVS; mkdir -p $d; nohup python worker.py --mode A --gpus 0,1 --accum $accum --coord $c \
          --out $d > $d/worker_n$i.log 2>&1 < /dev/null &"
    else
      for g in 0 1; do
        ssh_n "$hp" "$ENVS; mkdir -p $d; nohup python worker.py --mode B --gpus $g --accum $accum --coord $c \
            --out $d > $d/worker_n${i}_g$g.log 2>&1 < /dev/null &"
      done
    fi
  done
  # wait until the coordinator and every worker on every node have exited
  # (pattern anchored on "^python" so pgrep does not match this ssh command line itself)
  while :; do
    busy=0
    for hp in "${NL[@]}"; do ssh_n "$hp" "pgrep -f '^python (coordinator|worker).py' >/dev/null" && busy=1; done
    [ $busy -eq 1 ] || break
    sleep 20
  done
  echo "=== $name finished $(date +%T)"; ssh_n "$N1" "tail -1 $d/coordinator.log"
}

for hp in "${NL[@]}"; do ssh_n "$hp" "mkdir -p $OUT"; done
K=${#NL[@]}
for name in ${RUNS:-A_eb8 B_eb8 A_eb32 B_eb32}; do
  mode=${name%%_eb*}; eb=${name#*_eb}
  if [ "$mode" = A ]; then n=$K; else n=$((2 * K)); fi
  [ $((eb % n)) -eq 0 ] || { echo "skip $name: EB $eb not divisible by $n replicas"; continue; }
  if [ "$eb" -le 8 ]; then s=20; w=3; else s=8; w=2; fi
  run "$name" "$mode" "$n" $((eb / n)) "${STEPS:-$s}" "${WARMUP:-$w}"
done
ssh_n "$N1" "touch $OUT/ALL_DONE"
echo ALL_DONE
