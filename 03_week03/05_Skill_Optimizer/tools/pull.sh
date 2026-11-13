#!/bin/bash
# ดึงผลการวัดและสกิลทุกรุ่นจาก container มาเก็บบนเครื่อง:  bash tools/pull.sh
#   results/results.json
#   results/runs/<รุ่น>/<โจทย์>-r<รอบ>/  = grade.json metrics.json + โค้ดที่ Agent เขียน (sandbox/)
#   skills/money-coder/                  = สกิลทุกรุ่นและ ISSUES.md ที่สร้างใน container
# Validation Set เก็บเฉพาะคะแนนและต้นทุน (ไม่มีผลรายข้อ คำสั่ง และโค้ด) เพื่อไม่ให้รั่วเข้าการแก้สกิล
#   bash tools/pull.sh --unseal   = ดึงของ Validation Set ทั้งหมด (ใช้หลังตัดสินครบทุกรุ่นแล้วเท่านั้น)
set -e
cd "$(dirname "$0")/.."
export MSYS_NO_PATHCONV=1
C=${LAB_CONTAINER:-multi-account}
W=/workspace/sklab
mkdir -p results skills
rm -rf results/runs
docker exec -i "$C" python3 - "$@" < tools/pack_results.py | tar xf - -C results
docker exec "$C" tar cf - --exclude=__pycache__ --exclude=.ipynb_checkpoints -C $W/skills money-coder | tar xf - -C skills
find results/runs -name grade.json | wc -l | xargs echo "Trial ที่เก็บแล้ว:"
ls skills/money-coder | xargs echo "สกิลที่เก็บแล้ว:"
