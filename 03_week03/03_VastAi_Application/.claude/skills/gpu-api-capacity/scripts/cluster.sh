#!/bin/bash
# LAB 5 · เปิด/ดู/ปิด ระบบ AI server ตรวจภาพ หลัง NGINX Load Balancer (พอร์ต 8080 จุดเดียว)
#
#   cluster.sh up <replica 1-2> <process ต่อ replica> <batch สูงสุด> [--lb round_robin|least_conn] [--slow <replica>:<ms>]
#                                                                      เปิดระบบใหม่ (ปิดของเดิมก่อน)
#        --lb    วิธีแจกงานของ NGINX: round_robin (ค่าเริ่ม แจกวนทีละตัว) | least_conn (ส่งให้ตัวที่งานค้างน้อยสุด)
#        --slow  ให้ replica ที่เลือก (0 หรือ 1) ช้าลงรูปละ <ms> มิลลิวินาที เช่น --slow 1:40 = replica 1 (GPU 1) ช้าลงรูปละ 40 ms
#        --retry off (ค่าเริ่ม) = คำขอที่ส่งไป process ที่ล่มแล้วล้ม NGINX ตอบ error กลับผู้ใช้ทันที
#                on            = NGINX ส่งคำขอที่ล้ม (ต่อไม่ติด / ขาดกลางทาง / 502 / 503) ไปให้ process ตัวถัดไปแทน
#   cluster.sh kill  <replica>                                         ปิดกะทันหัน (kill -9) ทุก process ของ replica นั้น
#   cluster.sh start <replica> [--wait]                                เปิด replica นั้นคืนด้วยค่าเดิม (--wait = รอจนพร้อม)
#   cluster.sh status                                                  replica ไหนเปิดอยู่ ตั้งค่าอะไร
#   cluster.sh down                                                    ปิดทั้งระบบ (server ทุกตัว + NGINX)
#
# replica r ใช้ GPU r · process p ของ replica r ฟัง 127.0.0.1:(9000 + r*100 + p) ภายในเครื่องเท่านั้น
# NGINX ฟัง 0.0.0.0:8080 แล้วแจกคำขอให้ทุก process ตามวิธีที่เลือก (round-robin หรือ least_conn)
set -euo pipefail

BASE=/workspace/lab5
CODE=$BASE/code
RUN=$BASE/run                       # pid · log · ค่าที่ตั้งไว้
ENV_FILE=$BASE/.env                 # เก็บ API_KEY (สุ่มครั้งแรก ใช้ค่าเดิมทุกครั้ง)
CONF=$RUN/cluster.conf
NGINX_CONF=/etc/nginx/conf.d/lab5_lb.conf
LB_PORT=8080
PY_BIN=$(dirname "$(command -v python)")
mkdir -p "$RUN"

port_of() { echo $((9000 + $1 * 100 + $2)); }

ensure_key() {
  if ! grep -qs '^API_KEY=.\+' "$ENV_FILE"; then
    umask 077
    echo "API_KEY=$(python -c 'import secrets;print(secrets.token_urlsafe(32))')" > "$ENV_FILE"
    echo "สร้าง API key ใหม่ไว้ที่ $ENV_FILE"
  else
    echo "ใช้ API key เดิมจาก $ENV_FILE"
  fi
}

stop_servers() {
  for f in "$RUN"/server_*.pid; do
    [ -e "$f" ] || continue
    pid=$(cat "$f"); kill "$pid" 2>/dev/null || true
    for _ in $(seq 20); do kill -0 "$pid" 2>/dev/null || break; sleep 0.5; done
    kill -9 "$pid" 2>/dev/null || true
    rm -f "$f"
  done
  # server ที่เปิดแบบเดี่ยวจากขั้นก่อน (run_single.sh ฟัง 0.0.0.0:8080)
  pkill -f 'uvicorn server:app' 2>/dev/null || true
  sleep 1
}

write_nginx() {  # $1 = รายการพอร์ต server · $2 = round_robin | least_conn · $3 = retry on | off
  local retry_conf="proxy_next_upstream off;                 # ล้มแล้วตอบ error เลย ไม่ส่งซ้ำ"
  if [ "${3:-off}" = on ]; then
    retry_conf="proxy_next_upstream error timeout http_502 http_503 non_idempotent;  # ล้มแล้วส่งตัวถัดไป (POST ด้วย)
        proxy_next_upstream_tries 0;           # ลองได้ทุกตัวในกลุ่ม
        proxy_connect_timeout 2s;"
  fi
  {
    echo "upstream lab5_servers {"
    echo "    zone lab5_servers 64k;   # ทุก worker ของ NGINX ใช้ตัวนับร่วมกัน (least_conn ต้องเห็นงานค้างรวม)"
    if [ "$2" = least_conn ]; then
      echo "    least_conn;              # ส่งให้ตัวที่มีคำขอค้างอยู่น้อยที่สุด"
    else
      echo "    # ไม่ระบุวิธีแจก = round-robin (แจกวนทีละตัว)"
    fi
    for p in $1; do echo "    server 127.0.0.1:$p max_fails=0;"; done
    echo "    keepalive 64;"
    echo "}"
    cat <<EOF
server {
    listen $LB_PORT;
    client_max_body_size 20m;
    location / {
        proxy_pass http://lab5_servers;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host \$host;
        proxy_set_header Authorization \$http_authorization;
        proxy_read_timeout 120s;
        $retry_conf
        add_header X-Upstream \$upstream_addr always;
    }
}
EOF
  } > "$NGINX_CONF"
  rm -f /etc/nginx/sites-enabled/default
  sed -i 's/^worker_processes .*/worker_processes 8;/' /etc/nginx/nginx.conf  # เครื่องมี CPU หลายร้อย core ไม่ต้องเปิด worker ทุก core
  nginx -t -q
  if pgrep -x nginx >/dev/null; then nginx -s reload; else nginx < /dev/null > /dev/null 2>&1; fi
}

start_proc() {  # $1 replica · $2 process · $3 batch สูงสุด · $4 mode · $5 slow ms · $6 = restart (เปิดคืนระหว่างระบบรับงาน)
  local r=$1 p=$2 port; port=$(port_of "$1" "$2")
  set -a; . "$ENV_FILE"; set +a
  # เปิดคืนระหว่างที่ replica อื่นรับงานอยู่: container นี้ได้ CPU จริงแค่ ~26 core (cgroup cpu.max) แม้มองเห็น 192 core
  # ถ้าปล่อย torch เปิด thread เต็ม 192 ตัวต่อ process ตอนอุ่นโมเดล ทั้ง container จะถูก throttle จน replica ที่ยังดี
  # NGINX และตัวยิงโหลดค้างไปด้วย → ตอนเปิดคืนจึงจำกัด thread และลดลำดับความสำคัญ CPU (nice) ให้ตัวที่รับงานอยู่ได้ CPU ก่อน
  local prefix=() thr=()
  if [ "${6:-}" = restart ]; then
    prefix=(nice -n 10)
    thr=(OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2)
  fi
  env "${thr[@]}" CUDA_VISIBLE_DEVICES=$r MODEL_PATH=$BASE/best.pt MODE=$4 MAX_BATCH=$3 REPLICA="gpu$r-p$p" SLOW_MS=$5 \
    nohup "${prefix[@]}" "$PY_BIN/uvicorn" server:app --app-dir "$CODE" --host 127.0.0.1 --port "$port" \
    --workers 1 --log-level warning >> "$RUN/server_${r}_${p}.log" 2>&1 < /dev/null &
  echo $! > "$RUN/server_${r}_${p}.pid"
}

load_conf() {
  [ -f "$CONF" ] || { echo "ยังไม่เคยเปิดระบบ (cluster.sh up ก่อน)"; exit 1; }
  . "$CONF"
  [[ "${1:-}" =~ ^[0-9]+$ ]] && (( $1 < REPLICAS )) || { echo "replica ต้องเป็น 0..$((REPLICAS - 1))"; exit 1; }
}

cmd_kill() {  # ปิดกะทันหัน: kill -9 ไม่ให้ server ได้ปิดตัวอย่างสุภาพ คำขอที่ค้างอยู่ขาดกลางทาง
  load_conf "${1:-}"; local r=$1
  for ((p = 0; p < PROCS; p++)); do
    pidf="$RUN/server_${r}_${p}.pid"
    [ -f "$pidf" ] || continue
    kill -9 "$(cat "$pidf")" 2>/dev/null || true
    rm -f "$pidf"
  done
  echo "$(date '+%T.%3N') ปิดกะทันหัน replica $r (GPU $r) ทั้ง $PROCS process แล้ว (kill -9)"
}

cmd_start() {  # เปิด replica คืนด้วยค่าที่ตั้งตอน up
  load_conf "${1:-}"; local r=$1 wait=${2:-}
  local slow=0; if (( r == ${SLOW_REPLICA:--1} )); then slow=$SLOW_MS; fi
  for ((p = 0; p < PROCS; p++)); do
    pidf="$RUN/server_${r}_${p}.pid"
    if [ -f "$pidf" ] && kill -0 "$(cat "$pidf")" 2>/dev/null; then continue; fi
    start_proc "$r" "$p" "$MAX_BATCH" "$MODE" "$slow" restart
  done
  echo "$(date '+%T.%3N') สั่งเปิด replica $r (GPU $r) คืนแล้ว ($PROCS process กำลังโหลดโมเดล · nice 10 · 2 thread)"
  if [ "$wait" = --wait ]; then
    for ((p = 0; p < PROCS; p++)); do
      until curl -sf "http://127.0.0.1:$(port_of "$r" "$p")/health" >/dev/null; do sleep 0.5; done
    done
    echo "$(date '+%T.%3N') replica $r พร้อมรับงานครบทุก process"
  fi
}

cmd_up() {
  local R=${1:-} P=${2:-} B=${3:-}
  shift 3 2>/dev/null || true
  local LB=round_robin SLOW_R=-1 SLOW_MS=0 RETRY=off
  while (( $# )); do
    case "$1" in
      --lb) LB=${2:-}; shift 2 ;;
      --retry) RETRY=${2:-}; shift 2 ;;
      --slow) [[ "${2:-}" =~ ^([0-9]+):([0-9]+)$ ]] || { echo "--slow ต้องเป็น <replica>:<ms> เช่น 1:40"; exit 1; }
              SLOW_R=${BASH_REMATCH[1]}; SLOW_MS=${BASH_REMATCH[2]}; shift 2 ;;
      *) echo "ไม่รู้จักตัวเลือก $1"; exit 1 ;;
    esac
  done
  [[ "$LB" =~ ^(round_robin|least_conn)$ ]] || { echo "--lb ต้องเป็น round_robin หรือ least_conn"; exit 1; }
  [[ "$RETRY" =~ ^(on|off)$ ]] || { echo "--retry ต้องเป็น on หรือ off"; exit 1; }
  [[ "$R" =~ ^[12]$ ]] || { echo "จำนวน replica ต้องเป็น 1 หรือ 2"; exit 1; }
  [[ "$P" =~ ^[1-9][0-9]*$ ]] || { echo "จำนวน process ต้องเป็นจำนวนเต็ม ≥ 1"; exit 1; }
  [[ "$B" =~ ^[1-9][0-9]*$ ]] || { echo "batch สูงสุดต้องเป็นจำนวนเต็ม ≥ 1"; exit 1; }
  local ngpu; ngpu=$(nvidia-smi -L | wc -l)
  (( R <= ngpu )) || { echo "เครื่องนี้มี GPU $ngpu ใบ เปิด $R replica ไม่ได้"; exit 1; }
  (( SLOW_R < R )) || { echo "--slow เลือก replica $SLOW_R แต่เปิดแค่ replica 0..$((R - 1))"; exit 1; }
  command -v nginx >/dev/null || { echo "ยังไม่ได้ติดตั้ง NGINX (apt-get install -y nginx)"; exit 1; }

  ensure_key
  echo "ปิด server เดิมทั้งหมด..."; stop_servers

  local mode=single; (( B > 1 )) && mode=microbatch
  local ports=""
  for ((r = 0; r < R; r++)); do
    local slow=0; if (( r == SLOW_R )); then slow=$SLOW_MS; fi
    for ((p = 0; p < P; p++)); do
      port=$(port_of $r $p); ports="$ports $port"
      : > "$RUN/server_${r}_${p}.log"
      start_proc "$r" "$p" "$B" "$mode" "$slow"
      if (( slow > 0 )); then echo "  เปิด replica $r (GPU $r) process $p → 127.0.0.1:$port (ช้าลงรูปละ $slow ms)"
      else echo "  เปิด replica $r (GPU $r) process $p → 127.0.0.1:$port"; fi
    done
  done
  printf 'REPLICAS=%s\nPROCS=%s\nMAX_BATCH=%s\nMODE=%s\nLB=%s\nRETRY=%s\nSLOW_REPLICA=%s\nSLOW_MS=%s\nPORTS="%s"\nSTARTED="%s"\n' \
    "$R" "$P" "$B" "$mode" "$LB" "$RETRY" "$SLOW_R" "$SLOW_MS" "${ports# }" "$(date '+%F %T')" > "$CONF"
  write_nginx "$ports" "$LB" "$RETRY"
  echo "NGINX ฟัง 0.0.0.0:$LB_PORT → $LB ไป ${ports# } · ส่งคำขอที่ล้มซ้ำ: $RETRY"

  echo "รอ server ทุก process อุ่นโมเดลเสร็จ..."
  local deadline=$((SECONDS + 300))
  for port in $ports; do
    until curl -sf "http://127.0.0.1:$port/health" >/dev/null; do
      (( SECONDS < deadline )) || { echo "พอร์ต $port ไม่พร้อมภายใน 300 วินาที ดู log ใน $RUN"; exit 1; }
      sleep 2
    done
    echo "  127.0.0.1:$port พร้อม"
  done
  curl -sf "http://127.0.0.1:$LB_PORT/health" >/dev/null || { echo "NGINX ตอบไม่ได้"; exit 1; }
  local slowtxt="ไม่มี replica ช้า"; if (( SLOW_R >= 0 )); then slowtxt="replica $SLOW_R ช้าลงรูปละ $SLOW_MS ms"; fi
  echo "เปิดเสร็จ: replica $R · process $P ต่อ replica · batch สูงสุด $B ($mode) · แจกงานแบบ $LB · $slowtxt · เข้าทางพอร์ต $LB_PORT"
}

cmd_status() {
  if [ ! -f "$CONF" ]; then echo "ยังไม่เคยเปิดระบบ"; return; fi
  . "$CONF"
  echo "ตั้งค่า: replica $REPLICAS · process $PROCS ต่อ replica · batch สูงสุด $MAX_BATCH ($MODE) · แจกงานแบบ ${LB:-round_robin} · ส่งคำขอที่ล้มซ้ำ ${RETRY:-off} · เปิดเมื่อ $STARTED"
  if (( ${SLOW_REPLICA:--1} >= 0 )); then echo "replica $SLOW_REPLICA ช้าลงรูปละ $SLOW_MS ms"; fi
  if pgrep -x nginx >/dev/null; then echo "NGINX: เปิดอยู่ (พอร์ต $LB_PORT)"; else echo "NGINX: ปิด"; fi
  for ((r = 0; r < REPLICAS; r++)); do
    for ((p = 0; p < PROCS; p++)); do
      port=$(port_of $r $p); pidf="$RUN/server_${r}_${p}.pid"
      if [ -f "$pidf" ] && kill -0 "$(cat "$pidf")" 2>/dev/null; then
        h=$(curl -s -m 3 "http://127.0.0.1:$port/health" || echo '{}')
        st=$(python -c 'import json,sys;d=json.loads(sys.argv[1] or "{}");print(d.get("status","no-answer"),"max_batch="+str(d.get("max_batch","?")),"slow_ms="+str(d.get("slow_ms_per_image",0)))' "$h")
        echo "  replica $r (GPU $r) process $p  127.0.0.1:$port  pid $(cat "$pidf")  $st"
      else
        echo "  replica $r (GPU $r) process $p  127.0.0.1:$port  ปิดอยู่"
      fi
    done
  done
}

cmd_down() {
  stop_servers
  if pgrep -x nginx >/dev/null; then nginx -s stop || pkill -x nginx || true; fi
  [ -f "$CONF" ] && sed -i 's/^STARTED=.*/STARTED="(ปิดแล้ว)"/' "$CONF"
  echo "ปิดทั้งระบบแล้ว (server ทุก process + NGINX)"
}

case "${1:-}" in
  up) shift; cmd_up "$@" ;;
  kill) shift; cmd_kill "$@" ;;
  start) shift; cmd_start "$@" ;;
  status) cmd_status ;;
  down) cmd_down ;;
  *) sed -n '2,15p' "$0"; exit 1 ;;
esac
