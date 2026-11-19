#!/bin/bash
# Whole step on the GPU machine, run inside tmux so it survives a dropped connection.
# Each stage leaves a marker in $W/stage/, so running this again continues at the first unfinished stage.
W=${W:-/workspace/e2e_sitesafe}; C=$W/code_step08; EPOCHS=${EPOCHS:-30}; T=$W/team_train; D=$W/dataset/data_fixed.yaml
PY=/venv/main/bin/python; R=$W/runs; O=$W/model_results; BEST=$R/train/weights/best.pt
mkdir -p $W/stage $O; cd $W
stage(){ n=$1; shift; [ -f $W/stage/$n.ok ] && { echo "== $n: already done"; return 0; }
  echo "== $n: start $(date -u +%T)"
  if "$@"; then touch $W/stage/$n.ok; echo "== $n: ok $(date -u +%T)"; else echo "== $n: FAILED"; exit 1; fi; }
stage 1_install /venv/main/bin/pip install -q -r $T/requirements.txt matplotlib
stage 2_data $PY $C/fix_data_yaml.py $W/dataset
stage 3_map_before $PY $C/map_eval.py --model yolo11s.pt --data $D --out $O --tag before
stage 4_train $PY $C/train.py --data $D --project $R --name train --epochs $EPOCHS --imgsz 640 --seed 0
stage 5_map_after $PY $C/map_eval.py --model $BEST --data $D --out $O --tag after
stage 6_threshold $PY $C/select_threshold.py --team $T --data $D --model $BEST --out $O
stage 7_gate_before $PY $C/baseline_gate.py --team $T --data $D --model yolo11s.pt --threshold $O/threshold.json --output $O/metrics_before.json
# the team's evaluation: exit code 1 means "gate not passed", which is a result, not a crash
gate_after(){ rm -f $O/metrics_after.json
  $PY $T/evaluate.py --data $D --model $BEST --model-version ppe-yolo-v1 --threshold $O/threshold.json \
    --allow-small-test --device 0 --output $O/metrics_after.json; echo "evaluate.py exit code $?"; [ -f $O/metrics_after.json ]; }
stage 8_gate_after gate_after
stage 9_examples $PY $C/make_examples.py --team $T --data $D --model $BEST --threshold $O/threshold.json --out $O
cp $R/train/results.png $R/train/results.csv $R/train/train_time.json $R/train/args.yaml $O/ 2>/dev/null
echo PIPELINE_DONE
