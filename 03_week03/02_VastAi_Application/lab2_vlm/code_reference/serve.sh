#!/bin/bash
# LAB 2 · OpenAI-compatible receipt server (vLLM, port 8000) on the rented machine.
#   receipt-base = Qwen/Qwen3-VL-2B-Instruct
#   receipt-ft   = the same base + LoRA adapter from step 3 (/workspace/lab2/out/adapter)
# Both models share one GPU: vLLM loads the base once and applies the adapter per request.
#
# Usage (on the rented machine):
#   bash serve.sh start    # detach from SSH, keep running, restart vLLM if it dies
#   bash serve.sh status   # is it up? how long did start-up take?
#   bash serve.sh stop
#
# The API key is generated once with openssl and kept only on this machine
# (/workspace/lab2/secret/api_key, mode 600). It is passed to vLLM through the
# VLLM_API_KEY environment variable so it never shows up in `ps` or in the logs.
set -u
LAB=/workspace/lab2
VENV=$LAB/venv
ADAPTER=$LAB/out/adapter
BASE=Qwen/Qwen3-VL-2B-Instruct
PORT=8000
RUN=$LAB/serve
SECRET=$LAB/secret/api_key
mkdir -p "$RUN"

supervise() {                      # runs detached; restarts vLLM if it exits
  export VLLM_API_KEY="$(cat "$SECRET")" HF_HUB_OFFLINE=1
  date +%s > "$RUN/start_time"
  rm -f "$RUN/ready_time"
  for try in 1 2 3 4 5; do
    echo "[$(date '+%F %T')] starting vLLM (try $try)" >> "$RUN/serve.log"
    "$VENV/bin/vllm" serve "$BASE" \
      --host 0.0.0.0 --port $PORT \
      --served-model-name receipt-base \
      --enable-lora --max-lora-rank 8 --max-loras 1 \
      --lora-modules receipt-ft="$ADAPTER" \
      --max-model-len 8192 --limit-mm-per-prompt '{"image":1}' \
      --gpu-memory-utilization 0.85 \
      >> "$RUN/serve.log" 2>&1
    echo "[$(date '+%F %T')] vLLM exited with code $?, restarting in 10 s" >> "$RUN/serve.log"
    sleep 10
  done
}

wait_ready() {                     # record how long start-up took
  for _ in $(seq 1 180); do
    if curl -sf -o /dev/null "http://127.0.0.1:$PORT/health"; then
      now=$(date +%s); echo "$now" > "$RUN/ready_time"
      echo "ready after $(( now - $(cat "$RUN/start_time") )) s" | tee -a "$RUN/serve.log"
      return 0
    fi
    sleep 5
  done
  echo "not ready after 15 min, see $RUN/serve.log"; return 1
}

case "${1:-start}" in
  start)
    if curl -sf -o /dev/null "http://127.0.0.1:$PORT/health"; then echo "already running"; exit 0; fi
    if [ ! -s "$SECRET" ]; then        # new random key, only on this machine
      mkdir -p "$(dirname "$SECRET")"; chmod 700 "$(dirname "$SECRET")"
      ( umask 077; openssl rand -hex 32 > "$SECRET" )
      echo "new API key written to $SECRET"
    fi
    : > "$RUN/serve.log"
    setsid nohup bash "$0" _supervise > /dev/null 2>&1 < /dev/null &
    echo $! > "$RUN/pid"
    sleep 2; wait_ready ;;
  _supervise) supervise ;;
  status)
    if curl -sf -o /dev/null "http://127.0.0.1:$PORT/health"; then
      echo "up · start-up took $(( $(cat "$RUN/ready_time") - $(cat "$RUN/start_time") )) s"
    else echo "down"; fi ;;
  stop)
    [ -f "$RUN/pid" ] && pkill -TERM -s "$(cat "$RUN/pid")" 2>/dev/null
    pkill -f "vllm serve $BASE" 2>/dev/null; echo "stopped" ;;
  *) echo "usage: $0 start|status|stop"; exit 1 ;;
esac
