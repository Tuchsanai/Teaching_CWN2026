#!/usr/bin/env bash
# gpu-queue-capacity: start/stop the parts of the LAB 9 system on the rented Vast.ai machine.
# Built from the commands that ran in LAB 9 (image vastai/pytorch, Python in /venv/main, no Docker on the machine).
#   bash stack.sh setup            pip packages into /venv/main + apt rabbitmq-server, then start RabbitMQ
#   bash stack.sh rabbit           start RabbitMQ (as user rabbitmq, HOME=/var/lib/rabbitmq) if it is not up
#   bash stack.sh sync [PORT]      synchronous API (sync_server.py) on GPU 0, default port 8001 (internal)
#   bash stack.sh gateway          gateway.py on port 8000 (the port opened to the outside)
#   bash stack.sh worker GPU       worker.py on GPU <GPU>, name gpu<GPU>
#   bash stack.sh stop sync|gateway|worker GPU|all
#   bash stack.sh status
# Code lives in /workspace/lab9/code, logs and results in /workspace/lab9. Every server runs with
# setsid nohup, so a dropped SSH session does not stop it. The API key is made once in
# /workspace/lab9/api_key.txt (mode 600) and is never printed.
set -u
W=/workspace/lab9; C=$W/code; PY=/venv/main/bin
mkdir -p "$W" "$W/images"

ensure_key() {
  [ -s "$W/api_key.txt" ] && return 0
  (umask 077; $PY/python -c "import secrets;print(secrets.token_urlsafe(32))" > "$W/api_key.txt")
}

wait_http() {  # wait_http PORT PATH SECONDS
  for _ in $(seq "$3"); do
    code=$(curl -s -o /dev/null -w '%{http_code}' -H "X-API-Key: $(cat "$W/api_key.txt")" "http://127.0.0.1:$1$2")
    [ "$code" = "200" ] && { echo "ready :$1$2"; return 0; }
    sleep 1
  done
  echo "NOT READY :$1$2 (see logs in $W)"; return 1
}

rabbit() {
  if timeout 10 rabbitmq-diagnostics -q ping >/dev/null 2>&1; then echo "rabbitmq already up"; return 0; fi
  mkdir -p /var/lib/rabbitmq /var/log/rabbitmq
  chown -R rabbitmq:rabbitmq /var/lib/rabbitmq /var/log/rabbitmq
  su rabbitmq -s /bin/sh -c "HOME=/var/lib/rabbitmq setsid nohup /usr/sbin/rabbitmq-server > /var/log/rabbitmq/startup.out 2>&1 < /dev/null &"
  for _ in $(seq 40); do
    timeout 10 rabbitmq-diagnostics -q ping >/dev/null 2>&1 && { echo "rabbitmq up"; return 0; }
    sleep 3
  done
  echo "RABBITMQ NOT UP"; tail -5 /var/log/rabbitmq/startup.out; return 1
}

case "${1:-status}" in
  setup)
    s=$(date +%s); export DEBIAN_FRONTEND=noninteractive
    (apt-get update -qq && apt-get install -y -qq rabbitmq-server > "$W/apt.log" 2>&1; echo "apt-rc=$?") &
    $PY/pip install -q diffusers transformers accelerate safetensors pillow fastapi uvicorn \
        aio-pika pika hf_transfer matplotlib > "$W/pip.log" 2>&1; echo "pip-rc=$?"
    $PY/pip install -q -U brotli >> "$W/pip.log" 2>&1     # avoids the brotli error seen when loading the model
    wait
    rabbit
    echo "setup_sec=$(( $(date +%s) - s ))" | tee "$W/setup_time.txt"
    ;;
  rabbit) rabbit ;;
  sync)
    ensure_key; port=${2:-8001}
    cd "$C" && setsid nohup $PY/uvicorn sync_server:app --host 0.0.0.0 --port "$port" --backlog 2048 \
        --timeout-keep-alive 600 > "$W/sync_server.log" 2>&1 < /dev/null &
    wait_http "$port" /health 240 ;;
  gateway)
    ensure_key; rabbit || exit 1
    cd "$C" && setsid nohup $PY/uvicorn gateway:app --host 0.0.0.0 --port 8000 >> "$W/gateway.log" 2>&1 < /dev/null &
    wait_http 8000 /stats 60 ;;
  worker)
    g=${2:?GPU index}
    cd "$C" && setsid nohup $PY/python worker.py --gpu "$g" --name "gpu$g" > "$W/worker_gpu$g.log" 2>&1 < /dev/null &
    for _ in $(seq 240); do grep -q "waiting for jobs" "$W/worker_gpu$g.log" 2>/dev/null && { echo "worker gpu$g ready"; exit 0; }; sleep 1; done
    echo "WORKER gpu$g NOT READY"; tail -5 "$W/worker_gpu$g.log"; exit 1 ;;
  stop)
    case "${2:-}" in
      sync) pkill -f "uvicorn sync_server:app" ;;
      gateway) pkill -f "uvicorn gateway:app" ;;
      worker) pkill -f "worker.py --gpu ${3:?GPU index} " ;;
      all) pkill -f "uvicorn sync_server:app"; pkill -f "uvicorn gateway:app"; pkill -f "worker.py --gpu" ;;
      *) echo "stop sync|gateway|worker GPU|all"; exit 2 ;;
    esac; sleep 2; echo "stopped ${2}" ;;
  status)
    pgrep -af "uvicorn (sync_server|gateway):app|worker.py --gpu|loadtest.py|killtest.py" | cut -c1-120
    timeout 10 rabbitmq-diagnostics -q ping >/dev/null 2>&1 && echo "rabbitmq: up" || echo "rabbitmq: down"
    nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used --format=csv,noheader ;;
  *) sed -n 2,12p "$0"; exit 2 ;;
esac
