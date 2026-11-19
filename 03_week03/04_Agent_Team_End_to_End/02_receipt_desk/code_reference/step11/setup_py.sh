#!/bin/bash
# Step 11 · Python side of the setup (runs in tmux "pyset" in parallel with apt). Log: step11/pyset.log
set -x
S=/workspace/e2e_receipt/step11; cd $S
uv venv -q --python 3.12 $S/venv-app && \
  uv pip install -q --python $S/venv-app/bin/python fastapi uvicorn aio-pika httpx pydantic pillow python-multipart && echo APPVENV_DONE
uv venv -q --python 3.12 $S/venv-vllm && \
  uv pip install -q --python $S/venv-vllm/bin/python vllm peft && echo VLLM_DONE
$S/venv-vllm/bin/python -c "import vllm,torch,transformers,peft;print('versions',vllm.__version__,torch.__version__,transformers.__version__,peft.__version__)"
# merge best LoRA (2-GPU run) into the base model -> one plain model for vLLM
$S/venv-vllm/bin/python $S/merge_lora.py /workspace/e2e_receipt/models/Qwen3-VL-2B-Instruct /workspace/e2e_receipt/step10/runs/best $S/merged && echo MERGE_DONE
echo PYSET_FINISHED
