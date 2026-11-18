#!/bin/bash
set -e
T0=$(date +%s)
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq && apt-get install -y -qq nginx build-essential python3-dev curl openssl >/dev/null
systemctl disable nginx 2>/dev/null || true; service nginx stop 2>/dev/null || true; pkill -x nginx || true
T1=$(date +%s)
pip install -q uv
uv venv -q /opt/vllm-env --python 3.12
VIRTUAL_ENV=/opt/vllm-env uv pip install -q vllm --torch-backend=auto
T2=$(date +%s)
echo "APT_SEC=$((T1-T0)) VLLM_SEC=$((T2-T1)) TOTAL_SEC=$((T2-T0))" > /workspace/lab6/install_time.txt
/opt/vllm-env/bin/python -c "import vllm,torch;print(\"vllm\",vllm.__version__,\"torch\",torch.__version__,torch.version.cuda)" >> /workspace/lab6/install_time.txt
echo DONE >> /workspace/lab6/install_time.txt
