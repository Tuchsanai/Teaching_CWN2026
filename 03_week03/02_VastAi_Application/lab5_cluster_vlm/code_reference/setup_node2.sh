#!/bin/bash
# LAB 5 · step 5: prepare Node 2 the same way as Node 1 (packages, model, dataset, code).
# HF_TOKEN is read from stdin (never written to disk, never echoed) and unset afterwards.
# Usage (on Node 2):  printf '%s\n' "$HF_TOKEN" | bash setup_node2.sh > setup.log 2>&1
set -u
read -r T; export HF_TOKEN="$T"; unset T
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu
cd /workspace/lab5
s=$(date +%s)
pip install -q transformers==5.23.0 peft==0.21.3 datasets==5.2.0 accelerate==1.16.0 \
    matplotlib==3.11.2 brotli==1.2.1 nvidia-ml-py==13.615.71 && echo "pip rc=0 sec=$(( $(date +%s) - s ))"
s=$(date +%s)
hf download Qwen/Qwen3-VL-8B-Instruct --local-dir /workspace/models/Qwen3-VL-8B-Instruct > dl.log 2>&1
echo "model rc=$? sec=$(( $(date +%s) - s ))"
s=$(date +%s)
python receipt_data.py prepare --out /workspace/lab5/data > prep.log 2>&1
echo "data rc=$? sec=$(( $(date +%s) - s ))"
unset HF_TOKEN
rm -f ~/.cache/huggingface/token ~/.huggingface/token
echo SETUP_DONE
