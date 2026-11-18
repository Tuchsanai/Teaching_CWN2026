#!/bin/bash
# เปิด server 1 process บน GPU ใบแรก พอร์ต 8080 โหมดทีละคำขอ (batch = 1)
cd /workspace/lab6/code
set -a; . /workspace/lab6/.env; set +a
export MODEL_PATH=/workspace/lab6/best.pt MODE=single REPLICA=gpu0-single CUDA_VISIBLE_DEVICES=0
exec uvicorn server:app --host 0.0.0.0 --port 8080 --workers 1 --log-level warning
