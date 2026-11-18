#!/bin/bash
set -e
t0=$(date +%s)
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq && apt-get install -y -qq nginx build-essential python3-dev curl >/dev/null
t1=$(date +%s)
pip install -q uv
uv venv -q -p 3.11 /opt/vllm-env
VIRTUAL_ENV=/opt/vllm-env uv pip install -q vllm
t2=$(date +%s)
echo "apt_sec=$((t1-t0)) vllm_sec=$((t2-t1)) total_sec=$((t2-t0))" > /workspace/lab6/logs/install_time.txt
/opt/vllm-env/bin/python -c "import vllm;print(vllm.__version__)" >> /workspace/lab6/logs/install_time.txt
