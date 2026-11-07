#!/bin/bash
# การทดลอง 2: ส่งข้อมูลเข้าทาง stdin ด้วยท่อ |
cd "$(dirname "$0")"
printf 'ลูกค้า,ยอดซื้อ\nA,999\nB,1000\nC,1500\nD,2400\n' > orders.csv
echo "=== ข้อมูลใน orders.csv ==="
cat orders.csv

echo "=== 1) cat orders.csv | yolo1 -p \"คำสั่ง\" (ข้อมูลมาทาง stdin · คำสั่งมาทาง argument) ==="
cat orders.csv | yolo1 --model fable --effort low -p "ข้อมูล CSV มาทาง stdin: ลด 10% เมื่อซื้อครบ 1000 บาท ตอบเป็นตาราง ลูกค้า | ยอดจ่าย"

echo "=== 2) { คำสั่ง; ข้อมูล; } | cyolo1 exec - (ส่งพรอมต์ทั้งก้อนทาง stdin · - คืออ่านจาก stdin) ==="
{ echo "ลด 10% เมื่อซื้อครบ 1000 บาท ตอบเป็นตาราง ลูกค้า | ยอดจ่าย จากข้อมูล CSV นี้"; cat orders.csv; } \
  | cyolo1 exec --skip-git-repo-check --model gpt-6-astra -c model_reasoning_effort=low - 2>/dev/null

echo "=== 3) ต่อท่อข้ามบัญชี: yolo1 เขียน → | → cyolo1 แปลงเป็น JSON (ไม่มีไฟล์ตรงกลาง) ==="
yolo1 --model fable --effort low -p "เขียนชื่อผลไม้ไทย 3 ชนิด บรรทัดละชนิด ไม่ต้องมีคำอธิบาย" \
  | { echo "แปลงรายการต่อไปนี้เป็น JSON array ของ string ตอบ JSON อย่างเดียว"; cat; } \
  | cyolo1 exec --skip-git-repo-check --model gpt-6-astra -c model_reasoning_effort=low - 2>/dev/null
