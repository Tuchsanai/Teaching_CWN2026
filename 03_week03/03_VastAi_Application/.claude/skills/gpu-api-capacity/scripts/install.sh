#!/bin/bash
# skill v0 · ติดตั้งสิ่งที่ server / ตัวเปิดระบบ / ตัวยิงโหลดใช้ บนเครื่องเช่า (image PyTorch 2.8 + CUDA 12.8 มี torch อยู่แล้ว)
#   bash /workspace/lab5/code/install.sh   → /workspace/lab5/install_time.txt จบด้วย DONE
# รายการแพ็กเกจรวบรวมจาก import ของ server.py · loadgen.py · report.py และ NGINX ที่ cluster.sh ต้องใช้
set -euo pipefail
LOG=/workspace/lab5/install_time.txt
mkdir -p /workspace/lab5/results /workspace/lab5/run
t0=$(date +%s)
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq nginx curl libgl1 libglib2.0-0 >/dev/null
# ไม่ให้ NGINX ของระบบเปิดค้างพอร์ต 80 · cluster.sh เปิด NGINX เองที่พอร์ต 8080
(nginx -s stop 2>/dev/null || pkill -x nginx || true)
python -m pip install -q --upgrade pip
python -m pip install -q ultralytics fastapi "uvicorn[standard]" python-multipart opencv-python-headless \
  psutil nvidia-ml-py matplotlib pillow
python - <<'EOF' | tee "$LOG"
import torch, ultralytics, fastapi, cv2
print("torch", torch.__version__, "cuda", torch.version.cuda, "gpus", torch.cuda.device_count())
print("ultralytics", ultralytics.__version__, "fastapi", fastapi.__version__, "opencv", cv2.__version__)
EOF
nginx -v 2>&1 | tee -a "$LOG"
echo "install_s $(( $(date +%s) - t0 ))" | tee -a "$LOG"
echo DONE | tee -a "$LOG"
