#!/bin/bash
# Usage (on the GPU machine, inside tmux): ./run_eval.sh <gpu> <name> <adapter|none> <set: val|test>
# val  = CORD validation (98 readable) -> used to fix the threshold decision before touching test
# test = CORD test (95 readable with a printed total) + 20 unreadable receipts (M5)
set -u
GPU=$1; NAME=$2; AD=$3; SET=$4
cd "${STEP_DIR:-/workspace/e2e_receipt/step10}"
export PATH=/venv/main/bin:$PATH HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false
MODEL=${MODEL:-/workspace/e2e_receipt/models/Qwen3-VL-2B-Instruct}
EXTRA=""; [ "$AD" != none ] && EXTRA="--adapter $AD"
if [ "$SET" = val ]; then SETS="--test-set data/val.jsonl"; else SETS="--test-set data/test.jsonl --unreadable-set data/unreadable.jsonl"; fi
T0=$(date +%s)
CUDA_VISIBLE_DEVICES=$GPU python train/evaluate.py $SETS --backend hf --model $MODEL $EXTRA \
   --allow-small-test-set --sweep 0.50,0.70,0.80,0.85,0.90,0.95,0.99 --out-dir eval/${NAME}_$SET
RC=$?
echo "{\"rc\": $RC, \"wall_s\": $(( $(date +%s) - T0 ))}" > eval/${NAME}_$SET/wall.json
echo "EVAL_DONE $NAME $SET rc=$RC"
