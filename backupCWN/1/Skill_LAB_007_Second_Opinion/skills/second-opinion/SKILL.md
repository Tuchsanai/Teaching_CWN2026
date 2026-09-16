---
name: second-opinion
description: ขอความเห็นที่สองโดยส่งคำถามเดียวกันให้ Claude อีกบัญชี (yolo2) และ Codex (cyolo1) พร้อมกัน แล้วเทียบคำตอบเป็นตาราง ใช้เมื่อผู้ใช้พูดว่า "ขอความเห็นที่สอง", "ให้ทั้ง Claude และ Codex ตอบ", "เทียบคำตอบสองค่าย" หรือพิมพ์ /second-opinion ตามด้วยคำถาม
argument-hint: "<คำถาม>"
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/ask-both.sh *)
---

# ความเห็นที่สองจากสองค่าย

คำถาม: $ARGUMENTS (ถ้าว่าง ให้ใช้คำถามล่าสุดของผู้ใช้ในบทสนทนา)

## ขั้นตอน

1. รันหนึ่งครั้ง: `${CLAUDE_SKILL_DIR}/scripts/ask-both.sh "<คำถาม>"` (สคริปต์ตรวจล็อกอินเอง เรียกสองบัญชีขนานกัน และพิมพ์คำตอบทั้งสองฝั่ง; ตั้งค่า `CLAUDE_MODEL`, `CLAUDE_EFFORT`, `CODEX_MODEL`, `CODEX_EFFORT` ได้ถ้าผู้ใช้ระบุ ค่าเริ่มต้น opus/high และ gpt-6-astra/medium)
2. อ่านผลทั้งสองฝั่ง แล้วเขียนรายงานตามรูปแบบใน [references/report.md](references/report.md)
3. ห้ามเรียก yolo2 หรือ cyolo1 เองซ้ำนอกสคริปต์ ห้ามอ่านไฟล์ credential ห้ามล็อกอินแทนผู้ใช้ และไม่ต้องคำนวณคำตอบเอง หน้าที่ของคุณคือเทียบและสรุป
