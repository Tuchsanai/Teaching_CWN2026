#!/usr/bin/env bash
# เตรียมเครื่องที่เช่า: ติดตั้ง library → โหลดโมเดล และเตรียม dataset พร้อมกัน
# ใช้ (บนเครื่องที่เช่า, ต้องมี HF_TOKEN ใน environment): bash setup.sh
set -euo pipefail
cd "$(dirname "$0")"
uv venv --python 3.12 /workspace/venv
. /workspace/venv/bin/activate
uv pip install vllm peft datasets matplotlib pillow
MODEL_ID="$(python -c 'import receipt_common as c; print(c.MODEL_ID)')"
hf download "$MODEL_ID" > download.log 2>&1 &
python prepare_data.py --out data
wait
echo "SETUP_DONE"
