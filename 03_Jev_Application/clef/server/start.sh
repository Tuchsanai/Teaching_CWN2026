#!/bin/bash
# รันบน Vast instance: (setsid nohup bash start.sh > start.log 2>&1 < /dev/null &)
set -e
mkdir -p /workspace && cd /workspace
python3 -m pip uninstall -y torchcodec >/dev/null 2>&1 || true   # torchcodec ใน cu129-nightly build กับ CUDA 13 → import vllm พัง
python3 -m pip install -q hf_transfer fastapi uvicorn pillow requests
export HF_HUB_ENABLE_HF_TRANSFER=1
set -a; . /workspace/server.env; set +a
exec python3 -m uvicorn server:app --app-dir /workspace --host 0.0.0.0 --port 8000 > /workspace/server.log 2>&1
