#!/bin/bash
# ส่งตัวรัน EvoSkill v2 ข้อมูลของ benchmark และสกิลที่ใช้เทียบ จากเครื่องเข้า container (รันซ้ำได้):  bash tools/push.sh
set -e
cd "$(dirname "$0")/.."
export MSYS_NO_PATHCONV=1
C=${LAB_CONTAINER:-multi-account}
W=/workspace/evlab
docker exec "$C" mkdir -p $W/ws $W/baselines $W/tools
tar cf - -C ../../00_resource/skills --exclude=examples --exclude=__pycache__ skill-optimizer | docker exec -i "$C" tar xf - -C $W
tar cf - --exclude=__pycache__ evoskill bench tools/pack_results.py | docker exec -i "$C" tar xf - -C $W
# สกิลของบทก่อนหน้า ที่ใช้เทียบบน Test Set: baselines/<ชื่อ>/skills/<สกิล>/SKILL.md
docker exec "$C" mkdir -p $W/baselines/so-v3/skills/money-coder
docker exec -i "$C" tee $W/baselines/so-v3/skills/money-coder/SKILL.md < ../05_Skill_Optimizer_Basic/skills/money-coder/v3/SKILL.md > /dev/null
tar cf - -C ../06_WikiSkill/runs/w2 skills | docker exec -i "$C" bash -c "mkdir -p $W/baselines/wiki-w2 && tar xf - -C $W/baselines/wiki-w2"
docker exec "$C" bash -lc "cd $W && ls -d skill-optimizer evoskill bench baselines/*/skills/*"
