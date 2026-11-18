#!/bin/bash
# Start train.py detached from the SSH session; if it dies it is restarted and resumes from ckpt.
# Extra arguments go to train.py, e.g.  bash run_train.sh --epochs 1
cd /workspace/lab2/code
export HF_HUB_OFFLINE=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
for try in 1 2 3; do
  /workspace/lab2/venv/bin/python train.py --data /workspace/lab2/data --out /workspace/lab2/out "$@" && exit 0
  echo "train.py exited with error (try $try), restarting from checkpoint" >> /workspace/lab2/out/train.log
  sleep 5
done
