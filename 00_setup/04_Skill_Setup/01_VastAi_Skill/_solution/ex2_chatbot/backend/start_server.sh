#!/usr/bin/env bash
# start_server.sh — เปิด ninfer-serve (OpenAI-compatible) ที่พอร์ต 8080 แบบเบื้องหลัง
# วิธีใช้:  NINFER_API_KEY=รหัสลับของคุณ bash start_server.sh
#   (ไม่ใส่ NINFER_API_KEY = สุ่มให้และเก็บไว้ที่ /workspace/ninfer_api_key.txt)
set -euo pipefail
cd /workspace/ninfer
KEYFILE=/workspace/ninfer_api_key.txt
if [ -z "${NINFER_API_KEY:-}" ]; then
  [ -f $KEYFILE ] || head -c 24 /dev/urandom | od -An -tx1 | tr -d ' \n' > $KEYFILE
  NINFER_API_KEY=$(cat $KEYFILE)
  echo "สุ่ม API key ให้แล้ว: cat $KEYFILE"
fi
pkill -f ninfer-serve 2>/dev/null && sleep 3 || true

setsid nohup ./build/apps/ninfer-serve models/qwen3_8_27b_nvfp4.ninfer \
  --host 0.0.0.0 --port 8080 \
  --max-context 16384 --kv-capacity auto --max-concurrency 4 --kv-dtype fp8 \
  --spec mtp --draft-tokens 3 --lm-head-draft \
  --no-thinking --cors --api-key "$NINFER_API_KEY" \
  > /workspace/ninfer.log 2>&1 < /dev/null &

echo "กำลังโหลดโมเดลเข้า GPU (ดู log: tail -f /workspace/ninfer.log)"
s=$(date +%s)
for i in $(seq 1 120); do
  if curl -sf localhost:8080/health >/dev/null; then
    echo "พร้อมแล้ว! ใช้เวลา $(( $(date +%s) - s ))s"; exit 0
  fi
  pgrep -f ninfer-serve >/dev/null || { echo "server ล้ม:"; tail -30 /workspace/ninfer.log; exit 1; }
  sleep 5
done
echo "ยังไม่พร้อมหลัง 10 นาที — ดู /workspace/ninfer.log"; exit 1
