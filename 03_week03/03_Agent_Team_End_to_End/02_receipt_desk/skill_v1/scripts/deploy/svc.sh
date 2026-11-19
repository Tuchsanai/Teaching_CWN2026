#!/bin/bash
# Step 11 · runs ON the GPU machine. One tmux session per service (no Docker there).
# usage: svc.sh start|stop|restart|status|log <svc|all>
#   svc = rabbitmq vllm0 vllm1 nginx gateway worker0 worker1
# Secrets come from $S/secrets.env (chmod 600, written by gpu.sh) and are never echoed.
S=${S:-/workspace/e2e_receipt/step11}
APP=$S/app                       # copy of ./app/ai (package "ai")
MODEL=$S/merged                  # Qwen3-VL-2B-Instruct + best LoRA (2-GPU run) merged
LOG=$S/logs; mkdir -p $LOG $S/gateway-data
ALL="rabbitmq vllm0 vllm1 nginx gateway worker0 worker1"
envs="set -a; . $S/secrets.env; set +a"
cmd_of() {
  case $1 in
    rabbitmq) echo "cd /var/lib/rabbitmq; exec runuser -u rabbitmq -- env HOME=/var/lib/rabbitmq /usr/lib/rabbitmq/bin/rabbitmq-server" ;;
    vllm0|vllm1) g=${1#vllm}; p=$((8001+g))
      echo "$envs; CUDA_VISIBLE_DEVICES=$g exec $S/venv-vllm/bin/vllm serve $MODEL --served-model-name receipt-vlm --host 127.0.0.1 --port $p --api-key \"\$VLLM_API_KEY\" --gpu-memory-utilization 0.85 --max-model-len 8192 --limit-mm-per-prompt '{\"image\":1}' --max-num-seqs 8" ;;
    nginx) echo "exec nginx -c $APP/ai/nginx/nginx.conf -g 'daemon off; pid $S/nginx.pid;'" ;;
    gateway) echo "$envs; cd $APP && GATEWAY_DATA_DIR=$S/gateway-data GATEWAY_PORT=8000 exec $S/venv-app/bin/python -m ai.gateway.main" ;;
    worker0|worker1) echo "$envs; cd $APP && WORKER_ID=$1 GATEWAY_URL=http://127.0.0.1:8000 VLLM_URL=http://127.0.0.1:8080 SERVED_MODEL=receipt-vlm exec $S/venv-app/bin/python -m ai.worker.worker" ;;
    *) echo "unknown service $1" >&2; exit 2 ;;
  esac
}
port_of() { case $1 in vllm0) echo 8001;; vllm1) echo 8002;; nginx) echo 8080;; gateway) echo 8000;; rabbitmq) echo 5672;; esac; }
start() {
  tmux has-session -t $1 2>/dev/null && { echo "$1 already running"; return; }
  tmux new -d -s $1 "bash -c \"$(cmd_of $1 | sed 's/"/\\"/g')\" >> $LOG/$1.log 2>&1"
  echo "$1 started"
}
stop() {
  if [ $1 = rabbitmq ]; then runuser -u rabbitmq -- env HOME=/var/lib/rabbitmq rabbitmqctl stop >/dev/null 2>&1; fi
  if [ $1 = nginx ] && [ -f $S/nginx.pid ]; then kill $(cat $S/nginx.pid) 2>/dev/null; fi
  tmux has-session -t $1 2>/dev/null && { tmux send-keys -t $1 C-c; sleep 2; tmux kill-session -t $1 2>/dev/null; }
  [ $1 = vllm0 ] || [ $1 = vllm1 ] && pkill -f "port $(port_of $1)" 2>/dev/null
  echo "$1 stopped"
}
status() {
  t=down; tmux has-session -t $1 2>/dev/null && t=up
  p=$(port_of $1); h=""
  case $1 in
    vllm*) h=$(curl -s -o /dev/null -w '%{http_code}' -m 3 127.0.0.1:$p/health) ;;
    gateway) h=$(curl -s -o /dev/null -w '%{http_code}' -m 3 127.0.0.1:8000/healthz) ;;
    nginx) h=$(curl -s -o /dev/null -w '%{http_code}' -m 3 127.0.0.1:8080/health) ;;
    rabbitmq) h=$(runuser -u rabbitmq -- env HOME=/var/lib/rabbitmq rabbitmqctl -q status >/dev/null 2>&1 && echo ok || echo no) ;;
    worker*) h=$(pgrep -f "WORKER_ID=$1" >/dev/null && echo pid || ps aux | grep -c "[a]i.worker.worker") ;;
  esac
  printf '%-9s tmux=%-4s port=%-5s health=%s\n' $1 $t "${p:--}" "$h"
}
act=$1; shift; svcs="$*"; [ "$svcs" = all ] || [ -z "$svcs" ] && svcs=$ALL
[ $act = stop ] && [ "$*" = all ] && svcs=$(echo $ALL | tr ' ' '\n' | tac | tr '\n' ' ')
for s in $svcs; do
  case $act in
    start) start $s ;; stop) stop $s ;; restart) stop $s; start $s ;;
    status) status $s ;; log) tail -n 40 $LOG/$s.log ;;
    *) echo "usage: svc.sh start|stop|restart|status|log <svc|all>"; exit 1 ;;
  esac
done
