#!/bin/bash
# ดึงโฟลเดอร์ runs/ จาก container มาเก็บบนเครื่อง:  bash tools/pull.sh
#   runs/<รุ่น>/skills/                    = สกิลของรุ่นนั้น
#   runs/<รุ่น>/trials/<โจทย์>-r<รอบ>/      = grade.json metrics.json + โค้ดที่ Agent เขียน (sandbox/)
#   runs/<รุ่น>/gate.txt failures.txt …    = ผลของคำสั่งที่ไม่เรียกโมเดล
#   runs/ISSUES.md report.md results.json
# Validation Set เก็บเฉพาะคะแนนและต้นทุน (ไม่มีผลรายข้อ คำสั่ง และโค้ด) เพื่อไม่ให้รั่วเข้าการแก้สกิล
#   bash tools/pull.sh --unseal   = ดึงของ Validation Set ทั้งหมด (ใช้หลังตัดสินครบทุกรุ่นแล้วเท่านั้น)
set -e
cd "$(dirname "$0")/.."
export MSYS_NO_PATHCONV=1
C=${LAB_CONTAINER:-multi-account}
mkdir -p runs
docker exec -i "$C" python3 - "$@" < tools/pack_results.py | tar xf - -C runs
find runs -name grade.json | wc -l | xargs echo "Trial ที่เก็บแล้ว:"
ls -d runs/*/skills 2>/dev/null | xargs echo "สกิลที่เก็บแล้ว:"
