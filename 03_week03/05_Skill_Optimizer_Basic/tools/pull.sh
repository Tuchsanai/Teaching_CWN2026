#!/bin/bash
# ดึงผลการวัดจาก container มาเก็บที่ results/ บนเครื่อง:  bash tools/pull.sh
#   results/results.json
#   results/runs/<รุ่น>/<โจทย์>-r<รอบ>/  = grade.json metrics.json + โค้ดที่ Agent เขียน (sandbox/)
# Validation Set เก็บเฉพาะคะแนนและต้นทุน (ไม่มีผลรายข้อ คำสั่ง และโค้ด) เพื่อไม่ให้รั่วเข้าการแก้สกิล
#   bash tools/pull.sh --unseal   = ดึงของ Validation Set ทั้งหมด (ใช้หลังตัดสินครบทุกรุ่นแล้วเท่านั้น)
set -e
cd "$(dirname "$0")/.."
export MSYS_NO_PATHCONV=1
C=${LAB_CONTAINER:-multi-account}
mkdir -p results
rm -rf results/runs
docker exec "$C" python3 /workspace/sklab/tools/pack_results.py "$@" | tar xf - -C results
find results/runs -name grade.json | wc -l | xargs echo "Trial ที่เก็บแล้ว:"
