#!/bin/bash
# bench.sh <label> <skills_dir> <bench...>   e.g. bench.sh old /c/.../_solution/skills B1 B1 B2 B3
# runs each benchmark from a clean workspace, writes results/<label>-<bench>-<i>.{jsonl,metrics.json,verify.json}
source /c/t/s04b/eval/lib.sh
label=$1; skills=$2; shift 2
cd /c/t/s04b/eval
echo "$(date +%T) START $label" >> /c/t/s04b/logs/events.log
install_skills "$skills"
i=0
for b in "$@"; do
  i=$((i+1)); name=C:/t/s04b/eval/results/$label-$b-$i
  reset_ws
  echo "$(date +%T) RUN $name" >> /c/t/s04b/logs/events.log
  ./run-app.sh $name C:/t/s04b/eval/prompts/$b.txt
  PYTHONIOENCODING=utf-8 python verify.py $b $name.metrics.json > $name.verify.json 2>&1
  mkdir -p $name.ws && docker cp multi-account:/workspace/. $name.ws/ >/dev/null 2>&1
  echo "$(date +%T) DONE $name $(cat $name.verify.json)" >> /c/t/s04b/logs/events.log
done
echo "$(date +%T) END $label" >> /c/t/s04b/logs/events.log
