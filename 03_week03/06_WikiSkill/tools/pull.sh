#!/bin/bash
# ดึงผลจาก container มาเก็บบนเครื่อง:  bash tools/pull.sh
#   runs/<workspace>/   = raw/ wiki/ skills/ history/ state.json ของ WikiSkill แต่ละ workspace
#   results/runs/<label>/<โจทย์>-r<รอบ>/ = grade.json metrics.json + โค้ดที่ Agent เขียน
# Validation Set เก็บเฉพาะคะแนนและต้นทุน (ไม่มีผลรายข้อและโค้ด) · Training และ Test เก็บครบ
set -e
cd "$(dirname "$0")/.."
export MSYS_NO_PATHCONV=1
C=${LAB_CONTAINER:-multi-account}
mkdir -p results runs
rm -rf results/runs runs/*
docker exec "$C" python3 /workspace/wklab/tools/pack_results.py "$@" | tar xf -
find results/runs -name grade.json | wc -l | xargs echo "Trial ที่เก็บแล้ว:"
ls runs
