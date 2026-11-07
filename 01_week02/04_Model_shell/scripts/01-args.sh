#!/bin/bash
# การทดลอง 1: ส่งโจทย์ทาง argument → คำตอบออกทาง stdout
cd "$(dirname "$0")"
Q='ซื้อครบ 1000 บาทลด 10%: ยอดซื้อ 999, 1000, 1500 บาท จ่ายเท่าไร? ตอบเป็นตารางสั้น ๆ'

echo "=== 1) Claude: yolo1 --model fable --effort low -p \"\$Q\" ==="
yolo1 --model fable --effort low -p "$Q"

echo "=== 2) Codex: cyolo1 exec --model gpt-6-astra -c model_reasoning_effort=low \"\$Q\" ==="
cyolo1 exec --skip-git-repo-check --model gpt-6-astra -c model_reasoning_effort=low "$Q" 2>/dev/null

echo "=== 3) Codex มี 2 ช่องทางออก: stdout (คำตอบ) กับ stderr (หัวรายงาน) ==="
cyolo1 exec --skip-git-repo-check --model gpt-6-astra -c model_reasoning_effort=low "ตอบคำว่า OK คำเดียว" > out-stdout.txt 2> out-stderr.txt
echo "stdout มี $(wc -l < out-stdout.txt) บรรทัด: $(cat out-stdout.txt)"
echo "stderr มี $(wc -l < out-stderr.txt) บรรทัด (หัวรายงาน เช่น ชื่อโมเดล จำนวนโทเคน)"

echo "=== 4) ลืมใส่ \"\" ครอบ \$Q: shell ตัดโจทย์ตามช่องว่าง ==="
set -- $Q
echo "ถ้าไม่ใส่ \"\" โมเดลจะได้ argument $# ชิ้น ชิ้นแรกคือ: $1"

echo "=== 5) ระดับ effort ที่ CLI รับได้ (อ่านจาก --help ของเวอร์ชันจริง) ==="
yolo1 --help | grep -A1 -- '--effort' | head -3
