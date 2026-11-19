#!/bin/bash
# Step 11 · install the serving stack on the rented GPU machine (no Docker there).
# Runs inside tmux session "setup" on the GPU machine. Log: /workspace/e2e_receipt/step11/setup.log
set -x
S=/workspace/e2e_receipt/step11
mkdir -p $S && cd $S
export DEBIAN_FRONTEND=noninteractive
# 1) NGINX + RabbitMQ as plain packages (started later by gpu.sh, not by systemd)
apt-get update -qq && apt-get install -y -qq nginx rabbitmq-server tmux >/dev/null && echo APT_DONE
# 2) app venv: gateway + workers (team code needs fastapi, uvicorn, aio-pika, httpx, pillow, multipart)
uv venv -q --python 3.12 $S/venv-app && \
  uv pip install -q --python $S/venv-app/bin/python fastapi uvicorn aio-pika httpx pydantic pillow python-multipart && echo APPVENV_DONE
# 3) vLLM venv (own torch) + peft to merge the LoRA
uv venv -q --python 3.12 $S/venv-vllm && \
  uv pip install -q --python $S/venv-vllm/bin/python vllm peft && echo VLLM_DONE
$S/venv-vllm/bin/python -c "import vllm,torch,transformers,peft;print('versions',vllm.__version__,torch.__version__,transformers.__version__,peft.__version__)"
echo SETUP_FINISHED
