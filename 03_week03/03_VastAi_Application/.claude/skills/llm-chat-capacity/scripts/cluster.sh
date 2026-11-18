#!/usr/bin/env bash
# cluster.sh — เปิด/ปิด/ดูสถานะระบบแชทบอท shop-bot (vLLM 1–2 ตัว + NGINX หน้าบ้าน)
#
#   ./cluster.sh start  [--gpus 1|2] [--mode batch|single] [--lb least_conn|round_robin]
#   ./cluster.sh lb     least_conn|round_robin     # สลับวิธีกระจายงาน (reload NGINX, vLLM ไม่ต้องเปิดใหม่)
#   ./cluster.sh status
#   ./cluster.sh stop
#   ./cluster.sh keyfile                           # บอกที่เก็บ API key (ไม่แสดงค่า)
#
# ผู้ใช้ทุกคนเรียกที่ http://<เครื่อง>:8000/v1/...  model = shop-bot  พร้อม header
#   Authorization: Bearer <key ในไฟล์ $KEY_FILE>
# คำตอบทุกครั้งมี header  X-vLLM-Backend: vllm-1|vllm-2  บอกว่าไป vLLM ตัวไหน
set -euo pipefail

# ---------- ค่าตั้งต้น (แก้ได้ด้วยตัวแปรแวดล้อม) ----------
BASE=${BASE:-/workspace/lab6}
MODEL_PATH=${MODEL_PATH:-/workspace/models/Qwen3-4B-Instruct-2507}
SERVED_NAME=${SERVED_NAME:-shop-bot}
MAX_LEN=${MAX_LEN:-4096}
VLLM_BIN=${VLLM_BIN:-/opt/vllm-env/bin/vllm}
LB_PORT=${LB_PORT:-8000}
BACKEND_PORT0=${BACKEND_PORT0:-8001}       # vllm-1 = 8001, vllm-2 = 8002
GPU_UTIL=${GPU_UTIL:-0.90}
READY_TIMEOUT=${READY_TIMEOUT:-900}

RUN=$BASE/run; LOGS=$BASE/logs; SECRETS=$BASE/secrets
KEY_FILE=$SECRETS/api_key
STATE=$RUN/state.env
NGINX_CONF=$RUN/nginx.conf
mkdir -p "$RUN" "$LOGS" "$SECRETS"; chmod 700 "$SECRETS"

say() { echo "[cluster] $*"; }
die() { echo "[cluster] ERROR: $*" >&2; exit 1; }

ensure_key() {   # สุ่ม key ครั้งแรกครั้งเดียว เก็บบนเครื่องนี้ (สิทธิ์ 600) ไม่พิมพ์ค่าออกจอ
  if [[ ! -s $KEY_FILE ]]; then
    ( umask 077; echo "sk-shop-$(openssl rand -hex 24)" > "$KEY_FILE" )
    say "สร้าง API key ใหม่ไว้ที่ $KEY_FILE"
  fi
  chmod 600 "$KEY_FILE"
}

load_state() { [[ -f $STATE ]] && source "$STATE" || true; }
save_state() { printf 'GPUS=%s\nMODE=%s\nLB=%s\n' "$GPUS" "$MODE" "$LB" > "$STATE"; }

write_nginx_conf() {   # $1 = least_conn | round_robin   ใช้ $GPUS จาก state
  local lb=$1 key; key=$(cat "$KEY_FILE")
  local servers="" maps="" i port
  for ((i=1; i<=GPUS; i++)); do
    port=$((BACKEND_PORT0 + i - 1))
    servers+="        server 127.0.0.1:${port} max_fails=0;"$'\n'
    maps+="        127.0.0.1:${port} vllm-${i};"$'\n'
  done
  local method=""; [[ $lb == least_conn ]] && method="        least_conn;"
  ( umask 077; cat > "$NGINX_CONF" <<EOF
worker_processes auto;
worker_rlimit_nofile 16384;
pid $RUN/nginx.pid;
error_log $LOGS/nginx_error.log warn;
events { worker_connections 4096; }
http {
    log_format lab6 '\$time_local "\$request" \$status upstream=\$upstream_addr rt=\$request_time';
    access_log $LOGS/nginx_access.log lab6;
    map_hash_bucket_size 256;   # key ยาว ต้องขยาย bucket ของ map
    # สถานะ API key: ตรงกับ key ที่สุ่มไว้ = 1, อื่น ๆ = 0
    map \$http_authorization \$key_ok {
        "Bearer ${key}" 1;
        default 0;
    }
    # แปลงที่อยู่ backend เป็นชื่อ vllm-N
    map \$upstream_addr \$backend_name {
${maps}        default \$upstream_addr;
    }
    upstream vllm_pool {
${method}
${servers}        keepalive 64;
    }
    server {
        listen ${LB_PORT};
        add_header X-vLLM-Backend \$backend_name always;
        add_header X-LB-Method ${lb} always;

        location = /health { proxy_pass http://vllm_pool/health; }
        location / {
            default_type application/json;
            if (\$key_ok = 0) {
                return 401 '{"error":"invalid or missing API key"}';
            }
            proxy_pass http://vllm_pool;
            proxy_http_version 1.1;
            proxy_set_header Connection "";
            proxy_set_header Host \$host;
            # streaming: ส่ง token ต่อทันที ไม่พักในบัฟเฟอร์
            proxy_buffering off;
            proxy_cache off;
            proxy_request_buffering off;
            chunked_transfer_encoding on;
            proxy_read_timeout 600s;
            proxy_send_timeout 600s;
        }
    }
}
EOF
  )
  if ! nginx -t -c "$NGINX_CONF" >/dev/null 2>&1; then
    nginx -t -c "$NGINX_CONF" || true; die "nginx config ผิด"
  fi
}

nginx_running() { [[ -f $RUN/nginx.pid ]] && kill -0 "$(cat "$RUN/nginx.pid")" 2>/dev/null; }

start_nginx() {
  if nginx_running; then nginx -c "$NGINX_CONF" -s reload; say "NGINX reload ($LB)";
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
  local have; have=$(nvidia-smi -L | wc -l)
  (( have >= GPUS )) || die "เครื่องนี้มี GPU $have ใบ ไม่พอสำหรับ --gpus $GPUS"
  [[ -x $VLLM_BIN ]] || die "ไม่พบ vLLM ที่ $VLLM_BIN"
  [[ -d $MODEL_PATH ]] || die "ไม่พบโมเดลที่ $MODEL_PATH"
  if ls "$RUN"/vllm-*.pid >/dev/null 2>&1; then die "ระบบเปิดอยู่แล้ว — ./cluster.sh stop ก่อน"; fi

  ensure_key
  write_nginx_conf "$LB"   # ตรวจ config NGINX ก่อนเปิด vLLM
  # batch = Continuous Batching ค่าปกติของ vLLM (พร้อมกันสูงสุด 256) · single = ตอบทีละ 1 คำถาม
  local seqs=256; [[ $MODE == single ]] && seqs=1
  local t0=$SECONDS i port
  for ((i=1; i<=GPUS; i++)); do
    port=$((BACKEND_PORT0 + i - 1))
    # setsid + nohup: ทำงานต่อแม้ SSH หลุด
    CUDA_VISIBLE_DEVICES=$((i-1)) VLLM_API_KEY="$(cat "$KEY_FILE")" \
      setsid nohup "$VLLM_BIN" serve "$MODEL_PATH" \
        --served-model-name "$SERVED_NAME" \
        --host 127.0.0.1 --port "$port" \
        --max-model-len "$MAX_LEN" \
        --max-num-seqs "$seqs" \
        --gpu-memory-utilization "$GPU_UTIL" \
        > "$LOGS/vllm-$i.log" 2>&1 < /dev/null &
    echo $! > "$RUN/vllm-$i.pid"
    say "vllm-$i: GPU $((i-1)) พอร์ต $port mode=$MODE (max-num-seqs=$seqs) log=$LOGS/vllm-$i.log"
  done
  save_state
  for ((i=1; i<=GPUS; i++)); do
    port=$((BACKEND_PORT0 + i - 1))
    wait_ready "$port" || { cmd_stop; die "vllm-$i ไม่พร้อมใน ${READY_TIMEOUT}s — ดู $LOGS/vllm-$i.log"; }
    say "vllm-$i พร้อม"
  done
  start_nginx
  local took=$((SECONDS - t0))
  echo "server_start_sec=$took gpus=$GPUS mode=$MODE lb=$LB" > "$LOGS/start_time.txt"
  say "เปิดเสร็จใน ${took}s · endpoint http://<เครื่อง>:$LB_PORT/v1 · model=$SERVED_NAME · key อยู่ที่ $KEY_FILE"
}

cmd_lb() {
  local lb=${1:-}; [[ $lb == least_conn || $lb == round_robin ]] || die "ใช้: lb least_conn|round_robin"
  load_state; [[ -n ${GPUS:-} ]] || die "ระบบยังไม่ได้เปิด"
  LB=$lb; save_state; write_nginx_conf "$LB"; start_nginx
}

cmd_status() {
  load_state
  if [[ -z ${GPUS:-} ]]; then say "ระบบปิดอยู่"; return 0; fi
  say "ตั้งค่า: gpus=$GPUS mode=$MODE lb=$LB model=$SERVED_NAME max_len=$MAX_LEN"
  local i port pid st
  for ((i=1; i<=GPUS; i++)); do
    port=$((BACKEND_PORT0 + i - 1)); pid=$(cat "$RUN/vllm-$i.pid" 2>/dev/null || echo -)
    if [[ $pid != - ]] && kill -0 "$pid" 2>/dev/null; then
      curl -sf "http://127.0.0.1:$port/health" >/dev/null 2>&1 && st="พร้อม" || st="กำลังโหลด"
    else st="ไม่ทำงาน"; fi
    say "vllm-$i  GPU $((i-1))  พอร์ต $port  pid $pid  $st"
  done
  if nginx_running; then say "NGINX  พอร์ต $LB_PORT  pid $(cat "$RUN/nginx.pid")  ทำงาน ($LB)"; else say "NGINX  ไม่ทำงาน"; fi
  nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv,noheader | sed 's/^/[cluster] GPU /'
}

cmd_stop() {
  nginx_running && nginx -c "$NGINX_CONF" -s stop && say "ปิด NGINX" || true
  local f pid
  for f in "$RUN"/vllm-*.pid; do
    [[ -e $f ]] || continue
    pid=$(cat "$f")
    kill -- -"$pid" 2>/dev/null || kill "$pid" 2>/dev/null || true
    for _ in $(seq 30); do kill -0 "$pid" 2>/dev/null || break; sleep 1; done
    kill -9 -- -"$pid" 2>/dev/null || true
    rm -f "$f"; say "ปิด $(basename "$f" .pid)"
  done
  rm -f "$STATE"
}

case ${1:-} in
  start)   shift; cmd_start "$@";;
  lb)      shift; cmd_lb "$@";;
  status)  cmd_status;;
  stop)    cmd_stop;;
  keyfile) ensure_key; echo "$KEY_FILE";;
  *) sed -n '2,13p' "$0"; exit 1;;
esac
