#!/bin/bash
cd /workspace/lab3/code
for try in 1 2 3 4 5; do
  echo "=== attempt \ \Wed Nov 18 07:47:24 +07 2026 ==="
  python train.py --data_dir ../data --out_dir ../results && { echo TRAIN_OK; exit 0; }
  sleep 10
done
echo TRAIN_FAILED
