#!/usr/bin/env bash
# cluster.sh — เปิด/ปิด/ดูสถานะระบบแชทบอท shop-bot (vLLM 1–2 ตัว หลัง NGINX)
#
#   ./cluster.sh start [--gpus 1|2] [--mode batch|single] [--lb least_conn|round_robin]
#   ./cluster.sh lb least_conn|round_robin   # สลับวิธีกระจายงาน (reload NGINX อย่างเดียว ไม่เปิด vLLM ใหม่)
#   ./cluster.sh status
#   ./cluster.sh stop
#
# ผู้ใช้เรียก http://<เครื่อง>:8000/v1/chat/completions  model=shop-bot
#   header: Authorization: Bearer <key ในไฟล์ $KEY_FILE>
# ทุกคำตอบมี header X-Served-By: vllm-1 | vllm-2  บอกว่าไป vLLM ตัวไหน
set -euo pipefail

BASE=${BASE:-/workspace/lab6}
MODEL_PATH=${MODEL_PATH:-/workspace/models/Qwen3-4B-Instruct-2507}
SERVED_NAME=${SERVED_NAME:-shop-bot}
MAX_LEN=${MAX_LEN:-4096}
VLLM_BIN=${VLLM_BIN:-/opt/vllm-env/bin/vllm}
LB_PORT=${LB_PORT:-8000}
PORT0=${PORT0:-8001}                 # vllm-1 = 8001 (GPU 0), vllm-2 = 8002 (GPU 1)
GPU_MEM=${GPU_MEM:-0.90}
READY_TIMEOUT=${READY_TIMEOUT:-900}

RUN=$BASE/run; LOGS=$BASE/logs; SECRETS=$BASE/secrets
KEY_FILE=$SECRETS/api_key
STATE=$RUN/state.env
NGINX_CONF=$RUN/nginx.conf
mkdir -p "$RUN" "$LOGS" "$SECRETS"; chmod 700 "$SECRETS"

say() { echo "[cluster] $*"; }
die() { echo "[cluster] ERROR: $*" >&2; exit 1; }

ensure_key() {   # สุ่ม key ครั้งแรกครั้งเดียว เก็บบนเครื่องนี้ สิทธิ์ 600 ไม่พิมพ์ค่าออกจอ
  if [[ ! -s $KEY_FILE ]]; then
    ( umask 077; echo "sk-shop-$(openssl rand -hex 24)" > "$KEY_FILE" )
    say "สุ่ม API key ใหม่ เก็บไว้ที่ $KEY_FILE"
  fi
  chmod 600 "$KEY_FILE"
}

load_state() { if [[ -f $STATE ]]; then source "$STATE"; fi; }
save_state() { printf 'GPUS=%s\nMODE=%s\nLB=%s\n' "$GPUS" "$MODE" "$LB" > "$STATE"; }

write_nginx_conf() {   # $1 = least_conn | round_robin
  local lb=$1 key servers="" names="" i port method=""
  key=$(cat "$KEY_FILE")
  for ((i=1; i<=GPUS; i++)); do
    port=$((PORT0 + i - 1))
    servers+="        server 127.0.0.1:${port} max_fails=0;"$'\n'
    names+="        127.0.0.1:${port} vllm-${i};"$'\n'
  done
  [[ $lb == least_conn ]] && method="        least_conn;"
  ( umask 077; cat > "$NGINX_CONF" <<EOF
worker_processes auto;
worker_rlimit_nofile 16384;
pid $RUN/nginx.pid;
error_log $LOGS/nginx_error.log warn;
events { worker_connections 4096; }
http {
    log_format lab6 '\$time_local "\$request" \$status backend=\$upstream_addr rt=\$request_time';
    access_log $LOGS/nginx_access.log lab6;
    map_hash_bucket_size 256;
    map \$http_authorization \$key_ok {
        "Bearer ${key}" 1;
        default 0;
    }
    map \$upstream_addr \$backend_name {
${names}        default none;
    }
    upstream vllm_pool {
${method}
${servers}        keepalive 64;
    }
    server {
        listen ${LB_PORT};
        add_header X-Served-By \$backend_name always;
        add_header X-LB-Method ${lb} always;
        location = /health { proxy_pass http://vllm_pool/health; }
        location / {
            default_type application/json;
            if (\$key_ok = 0) { return 401 '{"error":"invalid or missing API key"}\n'; }
            proxy_pass http://vllm_pool;
            proxy_http_version 1.1;
            proxy_set_header Connection "";
            proxy_buffering off;              # streaming: ส่ง token ต่อทันที
            proxy_cache off;
            proxy_request_buffering off;
            proxy_read_timeout 600s;
            proxy_send_timeout 600s;
        }
    }
}
EOF
  )
  nginx -t -c "$NGINX_CONF" >/dev/null 2>&1 || { nginx -t -c "$NGINX_CONF"; die "config NGINX ผิด"; }
}

nginx_running() { [[ -f $RUN/nginx.pid ]] && kill -0 "$(cat "$RUN/nginx.pid")" 2>/dev/null; }
start_or_reload_nginx() {
  if nginx_running; then nginx -c "$NGINX_CONF" -s reload; say "NGINX reload → $LB"
  else nginx -c "$NGINX_CONF"; say "NGINX เปิดที่พอร์ต $LB_PORT ($LB)"; fi
}

wait_ready() {   # $1 = port
  local t0=$SECONDS
  until curl -sf "http://127.0.0.1:$1/health" >/dev/null 2>&1; do
    (( SECONDS - t0 > READY_TIMEOUT )) && return 1
    sleep 2
  done
}

cmd_start() {
  GPUS=1; MODE=batch; LB=least_conn
  while [[ $# -gt 0 ]]; do
    case $1 in
      --gpus) GPUS=$2; shift 2;;
      --mode) MODE=$2; shift 2;;
      --lb)   LB=$2;   shift 2;;
      *) die "ไม่รู้จักตัวเลือก $1";;
    esac
  done
  [[ $GPUS == 1 || $GPUS == 2 ]] || die "--gpus ต้องเป็น 1 หรือ 2"
  [[ $MODE == batch || $MODE == single ]] || die "--mode ต้องเป็น batch หรือ single"
  [[ $LB == least_conn || $LB == round_robin ]] || die "--lb ต้องเป็น least_conn หรือ round_robin"
  (( $(nvidia-smi -L | wc -l) >= GPUS )) || die "GPU ไม่พอสำหรับ --gpus $GPUS"
  [[ -x $VLLM_BIN ]] || die "ไม่พบ vLLM ที่ $VLLM_BIN"
  [[ -d $MODEL_PATH ]] || die "ไม่พบโมเดลที่ $MODEL_PATH"
  ls "$RUN"/vllm-*.pid >/dev/null 2>&1 && die "ระบบเปิดอยู่แล้ว — สั่ง ./cluster.sh stop ก่อน"

  ensure_key
  write_nginx_conf "$LB"
  # batch = Continuous Batching ค่าปกติของ vLLM (max-num-seqs 256) · single = ตอบทีละ 1 คำถาม
  local seqs=256; [[ $MODE == single ]] && seqs=1
  local t0=$SECONDS i port
  for ((i=1; i<=GPUS; i++)); do
    port=$((PORT0 + i - 1))
    # setsid + nohup: vLLM ไม่ผูกกับ SSH session ทำงานต่อแม้การเชื่อมต่อหลุด
    CUDA_VISIBLE_DEVICES=$((i - 1)) setsid nohup "$VLLM_BIN" serve "$MODEL_PATH" \
      --served-model-name "$SERVED_NAME" --host 127.0.0.1 --port "$port" \
      --max-model-len "$MAX_LEN" --max-num-seqs "$seqs" \
      --gpu-memory-utilization "$GPU_MEM" --disable-uvicorn-access-log \
      > "$LOGS/vllm-$i.log" 2>&1 < /dev/null &
    echo $! > "$RUN/vllm-$i.pid"
    say "เปิด vllm-$i: GPU $((i - 1)) พอร์ต $port mode=$MODE (max-num-seqs=$seqs)"
  done
  for ((i=1; i<=GPUS; i++)); do
    port=$((PORT0 + i - 1))
    wait_ready "$port" || { tail -30 "$LOGS/vllm-$i.log"; die "vllm-$i ไม่พร้อมใน ${READY_TIMEOUT}s"; }
    say "vllm-$i พร้อม"
  done
  save_state
  start_or_reload_nginx
  echo "READY_SEC=$((SECONDS - t0))" > "$RUN/last_start.txt"
  say "ระบบพร้อมใน $((SECONDS - t0)) วินาที → http://127.0.0.1:$LB_PORT/v1  model=$SERVED_NAME"
}

cmd_lb() {
  local lb=${1:-}; [[ $lb == least_conn || $lb == round_robin ]] || die "ใช้: ./cluster.sh lb least_conn|round_robin"
  load_state; [[ -n ${GPUS:-} ]] || die "ระบบยังไม่เปิด"
  LB=$lb; write_nginx_conf "$LB"; start_or_reload_nginx; save_state
}

cmd_status() {
  load_state
  if [[ -z ${GPUS:-} ]]; then say "ระบบปิดอยู่"; return 0; fi
  say "ตั้งค่า: GPUS=$GPUS MODE=$MODE LB=$LB · API key ที่ $KEY_FILE"
  local i port pid st
  for ((i=1; i<=GPUS; i++)); do
    port=$((PORT0 + i - 1)); pid=$(cat "$RUN/vllm-$i.pid" 2>/dev/null || echo -)
    if kill -0 "$pid" 2>/dev/null && curl -sf "http://127.0.0.1:$port/health" >/dev/null; then st=พร้อม
    elif kill -0 "$pid" 2>/dev/null; then st=กำลังโหลด; else st=ดับ; fi
    say "vllm-$i  GPU $((i - 1))  พอร์ต $port  pid $pid  $st"
  done
  if nginx_running; then say "NGINX พอร์ต $LB_PORT ทำงาน ($LB)"; else say "NGINX ดับ"; fi
  nvidia-smi --query-gpu=index,memory.used,utilization.gpu,temperature.gpu --format=csv,noheader \
    | sed 's/^/[cluster] GPU /'
}

cmd_stop() {
  if nginx_running; then nginx -c "$NGINX_CONF" -s quit 2>/dev/null || kill "$(cat "$RUN/nginx.pid")"; fi
  local f pid
  for f in "$RUN"/vllm-*.pid; do
    [[ -f $f ]] || continue
    pid=$(cat "$f")
    kill -- "-$pid" 2>/dev/null || kill "$pid" 2>/dev/null || true   # ฆ่าทั้ง process group
    for _ in $(seq 30); do kill -0 "$pid" 2>/dev/null || break; sleep 1; done
    kill -9 -- "-$pid" 2>/dev/null || true
    rm -f "$f"
  done
  rm -f "$STATE"
  say "ปิดระบบแล้ว (API key ยังเก็บไว้ที่ $KEY_FILE)"
}

case ${1:-} in
  start)  shift; cmd_start "$@";;
  lb)     shift; cmd_lb "$@";;
  status) cmd_status;;
  stop)   cmd_stop;;
  *) sed -n '2,11p' "$0"; exit 1;;
esac
