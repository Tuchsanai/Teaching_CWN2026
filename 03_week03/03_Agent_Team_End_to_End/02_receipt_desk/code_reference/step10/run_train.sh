#!/bin/bash
# Usage (on the GPU machine, inside tmux): ./run_train.sh 1|2
# Same arguments for both runs; only the number of processes/GPUs changes.
set -u
NG=$1
cd /workspace/e2e_receipt/step10
export PATH=/venv/main/bin:$PATH HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false
MODEL=/workspace/e2e_receipt/models/Qwen3-VL-2B-Instruct
ARGS="--model $MODEL --train-file data/train.jsonl --output-dir runs/g$NG \
      --epochs 1 --global-batch-size 16 --per-device-batch-size 1 --learning-rate 1e-4 --lora-r 16 \
      --seed 0 --logging-steps 5"
T0=$(date +%s.%N)
if [ "$NG" = 1 ]; then
  CUDA_VISIBLE_DEVICES=0 python train/train_lora.py $ARGS
else
  CUDA_VISIBLE_DEVICES=0,1 torchrun --standalone --nproc_per_node 2 train/train_lora.py $ARGS
fi
RC=$?
T1=$(date +%s.%N)
echo "{\"gpus\": $NG, \"rc\": $RC, \"wall_s\": $(echo "$T1 - $T0" | bc), \"start\": $T0, \"end\": $T1}" > runs/wall_g$NG.json
echo "TRAIN_DONE rc=$RC"
