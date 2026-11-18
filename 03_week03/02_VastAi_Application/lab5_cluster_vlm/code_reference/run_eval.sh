#!/bin/bash
# LAB 5 · step 7: evaluate Base / Fine-tuned A / Fine-tuned B on the 100-receipt Test Set,
# one model copy per GPU, 4 shards in parallel on 2 nodes x 2 GPUs, then score on Node 1.
# Runs from the control machine (container). Remote processes run under nohup, so an SSH drop
# does not stop them; SSH errors (exit 255) are retried.
# Usage: N1=ip:sshport N2=ip:sshport nohup setsid bash run_eval.sh > run_eval.log 2>&1 &
set -u
KEY=${KEY:-/workspace/vastai_lab/Devtool_SSH/devtoolSSH}
OUT=/workspace/lab5/eval
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
start() {  # node gpu shard
  ssh_n "$1" "$ENVS; mkdir -p $OUT; pgrep -f '^python eval[.]py run --gpu $2 ' >/dev/null || \
    { setsid nohup python eval.py run --gpu $2 --shard $3/4 --host $4 --out $OUT >> $OUT/shard$3.log 2>&1 < /dev/null & sleep 2; }"
}
T0=$(date +%s)
echo "=== eval start $(date +%T)"
start "$N1" 0 0 n1; start "$N1" 1 1 n1; start "$N2" 0 2 n2; start "$N2" 1 3 n2
sleep 60
while :; do
  n=0
  for s in 0 1; do ssh_n "$N1" "grep -q '^DONE' $OUT/shard$s.log" && n=$((n+1)); done
  for s in 2 3; do ssh_n "$N2" "grep -q '^DONE' $OUT/shard$s.log" && n=$((n+1)); done
  prog=$(ssh_n "$N1" "tail -qn1 $OUT/shard0.log $OUT/shard1.log" | tr '\n' ' ')
  prog="$prog $(ssh_n "$N2" "tail -qn1 $OUT/shard2.log $OUT/shard3.log" | tr '\n' ' ')"
  echo "[$(date +%T)] done $n/4 · $prog"
  [ $n -eq 4 ] && break
  # a shard that died without DONE is restarted (it resumes from its jsonl)
  for s in 0 1; do ssh_n "$N1" "grep -q '^DONE' $OUT/shard$s.log || pgrep -f '^python eval[.]py run .*shard $s/4' >/dev/null" || { echo "restart shard $s"; start "$N1" $s $s n1; }; done
  for g in 0 1; do s=$((g+2)); ssh_n "$N2" "grep -q '^DONE' $OUT/shard$s.log || pgrep -f '^python eval[.]py run .*shard $s/4' >/dev/null" || { echo "restart shard $s"; start "$N2" $g $s n2; }; done
  sleep 60
done
echo "=== all shards done $(date +%T)  wall $(( $(date +%s) - T0 )) s"
# bring Node 2 shards to Node 1, then score there
for s in 2 3; do ssh_n "$N2" "cat $OUT/predictions_shard$s.jsonl" > /tmp/ps$s.jsonl; done
for s in 2 3; do ssh_n "$N1" "cat > $OUT/predictions_shard$s.jsonl" < /tmp/ps$s.jsonl; done
echo "$(( $(date +%s) - T0 ))" | ssh_n "$N1" "cat > $OUT/eval_wall_s.txt"
ssh_n "$N1" "$ENVS; python eval.py report --out $OUT 2>&1 | tee $OUT/report.log"
ssh_n "$N1" "touch $OUT/ALL_DONE"
echo ALL_DONE
