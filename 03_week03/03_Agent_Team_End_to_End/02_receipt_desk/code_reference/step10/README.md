# code_step10 · train + gate (copies of what ran)
- prep_cord.py   : CORD-v2 -> team JSONL (train 400 seed 0, val 98, test 95 + 20 unreadable)
- run_train.sh   : the team's train_lora.py unchanged, 1 GPU (python) or 2 GPU (torchrun), same args
- run_eval.sh    : the team's evaluate.py unchanged (--backend hf, --allow-small-test-set)
- pipeline.sh    : tmux pipeline on the GPU box: 2-GPU train -> evals on GPU0/GPU1 in parallel
- make_report.py : speed table, graphs, sample answers -> results/model (no weights)
- cost_now.sh    : status + rent cost of the e2e-receipt instance
