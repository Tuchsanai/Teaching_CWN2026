#!/bin/bash
# ดึงผลจาก container มาเก็บบนเครื่อง:  bash tools/pull.sh
#   runs/<ชื่อการรัน>/ = RUN.json state.json setup/ reference/ skills_v*/ turns/ evo/evolver_workspace/ legs/
# rollout ของ Validation Set เก็บเฉพาะคะแนนและต้นทุน (ไม่มีผลรายข้อและโค้ด) · Training และ Test เก็บครบ
set -e
cd "$(dirname "$0")/.."
export MSYS_NO_PATHCONV=1
C=${LAB_CONTAINER:-multi-account}
mkdir -p runs results
# กันการดึงผลซ้อนกัน 2 ครั้งพร้อมกัน (รอจนอีกครั้งหนึ่งเสร็จ)
until mkdir runs/.pull.lock 2>/dev/null; do sleep 2; done
trap 'rmdir runs/.pull.lock' EXIT
for d in $(docker exec "$C" bash -c 'ls /workspace/evlab/ws'); do rm -rf "runs/$d"; done
docker exec "$C" python3 /workspace/evlab/tools/pack_results.py "$@" | tar xf -
find runs -name grade.json | wc -l | xargs echo "rollout ที่เก็บแล้ว:"
ls runs
