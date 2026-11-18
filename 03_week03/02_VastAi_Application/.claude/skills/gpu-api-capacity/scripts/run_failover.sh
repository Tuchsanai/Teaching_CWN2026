#!/bin/bash
# LAB 6 · replica ล่มกลางทาง: 2 replica x 4 process · batch 32 · round-robin
# ยิงผู้ใช้ N คน 45 วินาที · ปิด replica 1 กะทันหันที่วินาที 15 · เปิดคืนที่วินาที 30
# (start --wait = คำสั่งจบเมื่อ replica 1 อุ่นโมเดลเสร็จครบทุก process → เวลาที่ใช้จนพร้อมรับงาน)
# ทำ 2 รอบ: NGINX ไม่ส่งซ้ำ (fo_noretry) กับ NGINX ส่งคำขอที่ล้มไป replica อื่น (fo_retry)
#   bash code/run_failover.sh <ผู้ใช้ N>
cd /workspace/lab6
N=${1:?ใส่จำนวนผู้ใช้}
C=code/cluster.sh
run() { # name, retry
  echo "=== $(date '+%T') $1 : up 2 4 32 --lb round_robin --retry $2"
  bash $C up 2 4 32 --lb round_robin --retry "$2" > "results/${1}_up.log" 2>&1 || { echo "up failed"; tail "results/${1}_up.log"; return 1; }
  tail -1 "results/${1}_up.log"
  python code/loadgen.py --name "$1" --users "$N" --duration 45 \
    --at "15:bash code/cluster.sh kill 1" --at "30:bash code/cluster.sh start 1 --wait" --track gpu1 \
    > "results/${1}.log" 2>&1
  tail -9 "results/${1}.log"
}
run fo_noretry off
run fo_retry on
echo "ALL DONE $(date '+%T')"
