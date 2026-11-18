#!/usr/bin/env bash
# เปิด vLLM server ตัวเดียว (พอร์ต 8000, OpenAI API) ให้บริการ 2 ชื่อโมเดล
#   qwen3-4b-base      = Qwen/Qwen3-4B-Instruct-2507 (โมเดลเดิม)
#   qwen3-4b-sabaijai  = โมเดลเดิม + LoRA adapter ที่เทรนใน LAB 3
# API key: อ่านจาก $VLLM_API_KEY หรือไฟล์ $KEY_FILE ถ้าไม่มีจะสุ่มใหม่และเก็บไว้ในไฟล์ (chmod 600) ไม่พิมพ์ค่าออกจอ
set -euo pipefail

BASE_MODEL="${BASE_MODEL:-Qwen/Qwen3-4B-Instruct-2507}"
ADAPTER_DIR="${ADAPTER_DIR:-/workspace/lab3/results/adapter}"
KEY_FILE="${KEY_FILE:-/workspace/lab3/.vllm_api_key}"
PORT="${PORT:-8000}"
LOG="${LOG:-/workspace/lab3/serve.log}"

if [ -z "${VLLM_API_KEY:-}" ]; then
  if [ ! -s "$KEY_FILE" ]; then
    umask 077
    python3 -c 'import secrets; print("sk-" + secrets.token_urlsafe(32))' > "$KEY_FILE"
  fi
  VLLM_API_KEY="$(cat "$KEY_FILE")"
fi
export VLLM_API_KEY   # vLLM อ่าน key จากตัวแปรนี้ จึงไม่โผล่ใน ps/command line

# ปิด server ตัวเก่า (ถ้ามี) แล้วเปิดใหม่เบื้องหลัง
pkill -f "vllm serve" 2>/dev/null || true
sleep 2

nohup vllm serve "$BASE_MODEL" \
  --served-model-name qwen3-4b-base \
  --enable-lora \
  --lora-modules "qwen3-4b-sabaijai=$ADAPTER_DIR" \
  --max-lora-rank 8 \
  --max-loras 1 \
  --host 0.0.0.0 --port "$PORT" \
  --dtype bfloat16 \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.85 \
  > "$LOG" 2>&1 &
echo "vLLM starting (pid $!) log: $LOG"

# รอจน /v1/models ตอบ (สูงสุด 10 นาที)
for i in $(seq 1 120); do
  if curl -sf -H "Authorization: Bearer $VLLM_API_KEY" "http://127.0.0.1:$PORT/v1/models" >/dev/null; then
    echo "ready: $(curl -s -H "Authorization: Bearer $VLLM_API_KEY" "http://127.0.0.1:$PORT/v1/models" \
      | python3 -c 'import json,sys; print(", ".join(m["id"] for m in json.load(sys.stdin)["data"]))')"
    exit 0
  fi
  if ! pgrep -f "vllm serve" >/dev/null; then echo "vLLM exited, see $LOG"; tail -30 "$LOG"; exit 1; fi
  sleep 5
done
echo "timeout waiting for vLLM"; exit 1
