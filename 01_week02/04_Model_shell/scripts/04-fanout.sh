#!/bin/bash
# การทดลอง 4: กระจายงานให้หลายบัญชีพร้อมกัน (fan-out) แล้วรวมผล (fan-in) ผ่านไฟล์
cd "$(dirname "$0")"
QG='ร้านลด 10% เมื่อซื้อครบ 1000 บาท และลด 15% เมื่อซื้อครบ 2000 บาท ใช้สิทธิ์ได้ขั้นเดียว
ค่าส่ง 50 บาท ยกเว้นค่าส่งเมื่อยอดหลังหักส่วนลดตั้งแต่ 1500 บาทขึ้นไป
หายอดจ่ายจริงของยอดซื้อ 999, 1000, 1800, 2000 บาท ตอบเป็นตาราง ยอดซื้อ | ส่วนลด | ยอดหลังลด | ค่าส่ง | ยอดจ่าย
ห้ามสร้างไฟล์หรือรันคำสั่งอื่น'

mkdir -p out && rm -f out/*

run() {  # run <บัญชี> <คำสั่ง...> : จับเวลาแต่ละบัญชี แล้วเขียนคำตอบลง out/<บัญชี>.md
  local acc=$1; shift
  local s=$(date +%s)
  "$@" > "out/$acc.md" 2>/dev/null
  echo "$acc $(( $(date +%s) - s ))" >> out/times.txt
}

echo "=== fan-out: 4 บัญชีพร้อมกันด้วย & แล้วรอด้วย wait ==="
T0=$(date +%s)
run yolo1  yolo1  --model fable --effort low -p "$QG" &
run yolo2  yolo2  --model opus  --effort low -p "$QG" &
run cyolo1 cyolo1 exec --skip-git-repo-check --model gpt-6-astra -c model_reasoning_effort=low "$QG" &
run cyolo2 cyolo2 exec --skip-git-repo-check --model gpt-6-sol   -c model_reasoning_effort=low "$QG" &
wait
T1=$(date +%s)
sort out/times.txt
SUM=$(awk '{s+=$2} END {print s}' out/times.txt)
echo "รันพร้อมกันใช้ $(( T1 - T0 )) วินาที · ถ้ารันทีละบัญชีจะใช้ประมาณ $SUM วินาที"

echo "=== fan-in: yolo3 (opus) อ่าน out/*.md ทั้ง 4 ไฟล์ แล้วตัดสิน ==="
yolo3 --model opus --effort medium -p "โจทย์:
$QG
คำตอบจาก 4 บัญชีอยู่ในไฟล์ out/yolo1.md out/yolo2.md out/cyolo1.md out/cyolo2.md ในโฟลเดอร์ปัจจุบัน
อ่านทั้ง 4 ไฟล์ คำนวณเองอีกรอบ แล้วตอบ 1) ตารางที่ถูกต้อง 2) ตาราง บัญชี | ถูก/ผิด | แถวที่ผิด 3) สรุป 1 บรรทัด
ห้ามแก้ไฟล์ใด ๆ" | tee out/verdict.md
