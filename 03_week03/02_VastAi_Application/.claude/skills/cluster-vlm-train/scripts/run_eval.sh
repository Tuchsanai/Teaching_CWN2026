#!/bin/bash
# LAB 5 · step 7: evaluate Base / Fine-tuned A / Fine-tuned B on the 100-receipt Test Set,
# one model copy per GPU, one shard per GPU on every node (LAB 5: 2 nodes x 2 GPUs = 4 shards), then score on Node 1.
# Runs from the control machine (container). Remote processes run under nohup, so an SSH drop
# does not stop them; SSH errors (exit 255) are retried.
# Usage: N1=ip:sshport N2=ip:sshport nohup setsid bash run_eval.sh > run_eval.log 2>&1 &
#   or   NODES="ip:sshport ..." [MODELS=base,A,B] ...   (MODELS = which models to read with; adapters must be
#        at /workspace/lab5/adapters/<A|B> on every node for the fine-tuned ones)
set -u
KEY=${KEY:-/workspace/vastai_lab/Devtool_SSH/devtoolSSH}
OUT=${OUT:-/workspace/lab5/eval}
MODELS=${MODELS:-base,A,B}
NODES=${NODES:-"$N1 $N2"}; read -r -a NL <<< "$NODES"; N1=${NL[0]}; K=${#NL[@]}; S=$((2 * K))
O="-i $KEY -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=20 -o ServerAliveInterval=30"
ssh_n() {
  local hp=$1; shift; local rc
  for i in $(seq 20); do
    ssh $O -p "${hp#*:}" "root@${hp%:*}" "$@"; rc=$?; [ $rc -ne 255 ] && return $rc
    echo "  (ssh ${hp%:*} dropped, retry $i)" >&2; sleep 15
  done
  return 255
}
ENVS='export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu; cd /workspace/lab5'
start() {  # node gpu shard host
  ssh_n "$1" "$ENVS; mkdir -p $OUT; pgrep -f '^python eval[.]py run --gpu $2 ' >/dev/null || \
    { setsid nohup python eval.py run --gpu $2 --shard $3/$S --host $4 --models $MODELS --out $OUT >> $OUT/shard$3.log 2>&1 < /dev/null & sleep 2; }"
}
T0=$(date +%s)
echo "=== eval start $(date +%T)  $S shards · models $MODELS"
for i in $(seq 0 $((K - 1))); do for g in 0 1; do start "${NL[$i]}" $g $((2 * i + g)) n$((i + 1)); done; done
sleep 60
while :; do
  n=0; prog=""
  for i in $(seq 0 $((K - 1))); do
    for g in 0 1; do s=$((2 * i + g)); ssh_n "${NL[$i]}" "grep -q '^DONE' $OUT/shard$s.log" && n=$((n+1)); done
    prog="$prog $(ssh_n "${NL[$i]}" "tail -qn1 $OUT/shard$((2 * i)).log $OUT/shard$((2 * i + 1)).log" | tr '\n' ' ')"
  done
  echo "[$(date +%T)] done $n/$S ·$prog"
  [ $n -eq $S ] && break
  # a shard that died without DONE is restarted (it resumes from its jsonl)
  for i in $(seq 0 $((K - 1))); do for g in 0 1; do s=$((2 * i + g))
    ssh_n "${NL[$i]}" "grep -q '^DONE' $OUT/shard$s.log || pgrep -f '^python eval[.]py run .*shard $s/$S' >/dev/null" || { echo "restart shard $s"; start "${NL[$i]}" $g $s n$((i + 1)); }
  done; done
  sleep 60
done
echo "=== all shards done $(date +%T)  wall $(( $(date +%s) - T0 )) s"
# bring the other nodes' shards to Node 1, then score there
for i in $(seq 1 $((K - 1))); do for g in 0 1; do s=$((2 * i + g))
  ssh_n "${NL[$i]}" "cat $OUT/predictions_shard$s.jsonl" > /tmp/ps$s.jsonl
  ssh_n "$N1" "cat > $OUT/predictions_shard$s.jsonl" < /tmp/ps$s.jsonl
done; done
echo "$(( $(date +%s) - T0 ))" | ssh_n "$N1" "cat > $OUT/eval_wall_s.txt"
ssh_n "$N1" "$ENVS; python eval.py report --models $MODELS --out $OUT 2>&1 | tee $OUT/report.log"
ssh_n "$N1" "touch $OUT/ALL_DONE"
echo ALL_DONE
