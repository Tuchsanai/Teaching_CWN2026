#!/usr/bin/env bash
# เปิด AI server (vLLM, OpenAI-compatible) เสิร์ฟ 2 ชื่อโมเดลบน GPU ใบเดียว:
#   receipt-base = โมเดลเดิม · receipt-ft = โมเดลเดิม + LoRA adapter
# ใช้: bash serve.sh [โฟลเดอร์ adapter]   (API key อ่านจาก /workspace/receipt_api_key.txt)
set -euo pipefail
cd "$(dirname "$0")"
ADAPTER="${1:-/workspace/lab4/out/adapter}"
MODEL_ID="$(python -c 'import receipt_common as c; print(c.MODEL_ID)')"
setsid nohup vllm serve "$MODEL_ID" \
  --served-model-name receipt-base \
  --enable-lora --lora-modules "receipt-ft=$ADAPTER" --max-lora-rank 16 \
  --host 0.0.0.0 --port 8000 \
  --api-key "$(cat /workspace/receipt_api_key.txt)" \
  --max-model-len 8192 --gpu-memory-utilization 0.85 \
  --limit-mm-per-prompt '{"image":1}' \
  > /workspace/lab4/vllm.log 2>&1 < /dev/null &
echo "เริ่ม vLLM แล้ว · ดู log ที่ /workspace/lab4/vllm.log"
