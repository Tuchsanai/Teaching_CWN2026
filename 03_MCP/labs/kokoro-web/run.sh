#!/usr/bin/env bash
# เริ่มเว็บ Kokoro TTS Lab ที่ http://127.0.0.1:8765 แบบ background
# หยุดด้วย:  kill "$(cat server.pid)"
set -euo pipefail
cd "$(dirname "$0")"
export KOKORO_DEVICE="${KOKORO_DEVICE:-cpu}"
PY="${PYTHON:-$(command -v python3)}"
nohup "$PY" -m uvicorn app:app --host 127.0.0.1 --port 8765 > server.log 2>&1 &
echo $! > server.pid
echo "kokoro-web started pid=$(cat server.pid) url=http://127.0.0.1:8765 device=$KOKORO_DEVICE log=$(pwd)/server.log"
