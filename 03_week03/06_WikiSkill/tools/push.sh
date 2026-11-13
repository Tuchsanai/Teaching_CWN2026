#!/bin/bash
# ส่งเครื่องมือ ชุดโจทย์ และสกิลที่ใช้เทียบ จากเครื่องเข้า container (รันซ้ำได้):  bash tools/push.sh
set -e
cd "$(dirname "$0")/.."
export MSYS_NO_PATHCONV=1
C=${LAB_CONTAINER:-multi-account}
W=/workspace/wklab
B=../05_Skill_Optimizer/skills/money-coder
docker exec "$C" mkdir -p $W/ws $W/baselines
tar cf - -C ../../00_resource/skills --exclude=examples --exclude=__pycache__ skill-optimizer | docker exec -i "$C" tar xf - -C $W
tar cf - --exclude=runs --exclude=__pycache__ --exclude=results.json suite wikiskill tools/pack_results.py | docker exec -i "$C" tar xf - -C $W
# สกิลของบท 05 (Skill Optimizer) ที่ใช้เทียบบน Test Set: baselines/<รุ่น>/skills/money-coder/SKILL.md
for v in v0 v3; do
  docker exec "$C" mkdir -p $W/baselines/$v/skills/money-coder
  docker exec -i "$C" tee $W/baselines/$v/skills/money-coder/SKILL.md < $B/$v/SKILL.md > /dev/null
done
docker exec "$C" bash -lc "cd $W && ls -d skill-optimizer suite wikiskill baselines/*/skills/*"
