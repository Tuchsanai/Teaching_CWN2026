#!/bin/bash
# Start train.py detached from the SSH session; if it dies it is restarted and resumes from ckpt.
cd /workspace/lab4/code
export HF_HUB_OFFLINE=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
for try in 1 2 3; do
  /workspace/lab4/venv/bin/python train.py --data /workspace/lab4/data --out /workspace/lab4/out && exit 0
  echo "train.py exited with error (try $try), restarting from checkpoint" >> /workspace/lab4/out/train.log
  sleep 5
done
