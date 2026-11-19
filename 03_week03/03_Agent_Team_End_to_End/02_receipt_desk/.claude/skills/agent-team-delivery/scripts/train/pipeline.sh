#!/bin/bash
# Runs the rest of step 10 on the GPU machine without needing the SSH session (start in tmux).
# 1) wait for the 1-GPU run  2) 2-GPU run  3) evaluations on both GPUs in parallel
cd "${STEP_DIR:-/workspace/e2e_receipt/step10}"
while [ ! -f runs/wall_g1.json ]; do sleep 10; done
[ -f runs/wall_g2.json ] || ./run_train.sh 2 > runs/train_g2.log 2>&1
AD=runs/g2   # model from the 2-GPU run (as the brief asks)
# GPU0: fine-tuned on validation first (threshold decision), then on test
( ./run_eval.sh 0 ft $AD val  > eval/ft_val.log 2>&1;  ./run_eval.sh 0 ft $AD test > eval/ft_test.log 2>&1 ) &
# GPU1: base model on test (and validation for reference)
( ./run_eval.sh 1 base none test > eval/base_test.log 2>&1; ./run_eval.sh 1 base none val > eval/base_val.log 2>&1 ) &
wait
echo PIPELINE_DONE > eval/PIPELINE_DONE
