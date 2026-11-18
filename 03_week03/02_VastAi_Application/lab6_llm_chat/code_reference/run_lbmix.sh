#!/bin/bash
set -e
cd /workspace/lab6
for lb in round_robin least_conn; do
  bash cluster.sh lb $lb
  sleep 5
  /opt/vllm-env/bin/python loadtest.py --levels 448 --duration 120 --warmup 30 --no-repeat      --long-frac 0.2 --long-max-tokens 600 --vllm-ports 8001,8002 --label mix_$lb --out results > results/loadtest_mix_$lb.log 2>&1
  sleep 20
done
bash cluster.sh lb least_conn
echo DONE > results/lbmix_done.txt
