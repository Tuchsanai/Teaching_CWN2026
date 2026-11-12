#!/bin/bash
# ส่งเครื่องมือ ชุดโจทย์ และสกิลทุกรุ่น จากเครื่องเข้า container (รันซ้ำได้):  bash tools/push.sh
set -e
cd "$(dirname "$0")/.."
export MSYS_NO_PATHCONV=1
C=${LAB_CONTAINER:-multi-account}
W=/workspace/sklab
docker exec "$C" mkdir -p $W/skills
tar cf - -C ../../00_resource/skills --exclude=examples --exclude=__pycache__ skill-optimizer | docker exec -i "$C" tar xf - -C $W
tar cf - --exclude=runs --exclude=__pycache__ --exclude=results.json suite | docker exec -i "$C" tar xf - -C $W
tar cf - --exclude=__pycache__ -C skills money-coder | docker exec -i "$C" tar xf - -C $W/skills
tar cf - tools/pack_results.py | docker exec -i "$C" tar xf - -C $W
docker exec "$C" bash -lc "cd $W && ls -d skill-optimizer suite skills/money-coder/*"
