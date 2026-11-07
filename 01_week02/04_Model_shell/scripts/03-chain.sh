#!/bin/bash
# การทดลอง 3: ต่อโมเดลเป็นสาย A → B → C ส่งงานต่อผ่านตัวแปร (ไม่เขียนไฟล์)
cd "$(dirname "$0")"
QG='ร้านลด 10% เมื่อซื้อครบ 1000 บาท และลด 15% เมื่อซื้อครบ 2000 บาท ใช้สิทธิ์ได้ขั้นเดียว
ค่าส่ง 50 บาท ยกเว้นค่าส่งเมื่อยอดหลังหักส่วนลดตั้งแต่ 1500 บาทขึ้นไป
หายอดจ่ายจริงของยอดซื้อ 999, 1000, 1800, 2000 บาท ตอบเป็นตาราง ยอดซื้อ | ส่วนลด | ยอดหลังลด | ค่าส่ง | ยอดจ่าย
ห้ามสร้างไฟล์หรือรันคำสั่งอื่น'

echo "=== โหนด 1 · yolo1 (fable) ร่าง → \$DRAFT ==="
DRAFT=$(yolo1 --model fable --effort low -p "$QG")
echo "$DRAFT"

echo "=== โหนด 2 · cyolo1 (gpt-6-astra) ตรวจ \$DRAFT → \$REVIEW ==="
REVIEW=$(cyolo1 exec --skip-git-repo-check --model gpt-6-astra -c model_reasoning_effort=medium \
"ตรวจคำตอบด้านล่าง คำนวณเองอีกรอบ ตอบสั้น ๆ ว่าแถวไหนถูกหรือผิด
โจทย์:
$QG
คำตอบที่ต้องตรวจ:
$DRAFT" 2>/dev/null)
echo "$REVIEW"

echo "=== โหนด 3 · yolo2 (opus) รวม \$DRAFT + \$REVIEW → \$FINAL ==="
FINAL=$(yolo2 --model opus --effort medium -p "โจทย์:
$QG
ร่างจาก yolo1:
$DRAFT
ผลตรวจจาก cyolo1:
$REVIEW
ตอบตารางสุดท้ายที่ถูกต้อง และสรุป 1 บรรทัดว่าร่างถูกหรือผิด")
echo "$FINAL"

echo "=== ขนาดข้อมูลที่ไหลผ่านแต่ละตัวแปร ==="
echo "DRAFT=${#DRAFT} ตัวอักษร · REVIEW=${#REVIEW} ตัวอักษร · FINAL=${#FINAL} ตัวอักษร"
