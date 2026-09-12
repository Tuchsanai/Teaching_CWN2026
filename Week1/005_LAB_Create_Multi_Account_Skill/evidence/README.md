# หลักฐานการทดลอง LAB 005 (2026-09-09)

รันในคอนเทนเนอร์ `tuchsanai/devtools:2569_1` (Ubuntu 24.04) ชื่อ `devtools-lab004-ab-00c090` Claude Code 2.1.266, codex-cli 0.153.4, `BASE_PATH=/root/ai-accounts` ผู้สร้าง skill คือ `yolo1 -p --model opus --effort high` ใช้เวลา 358 s · 29 turns · list price $1.39 · PASS 9 / SKIP 8 / FAIL 0 ทุกไฟล์ปิดบังอีเมลและชื่อองค์กร ไม่มี token หรือ credential

| ไฟล์ | คืออะไร |
|---|---|
| `container-setup/00-bootstrap.sh` | ติดตั้ง Claude Code + Codex CLI ในคอนเทนเนอร์ (ตาม LAB 001 ขั้นที่ 1–2) |
| `container-setup/01-lab001-result.sh` | สร้างโครงสร้าง `$BASE_PATH` และ wrapper `yolo1–5`, `cyolo1–5` ให้เท่ากับผลลัพธ์ของ LAB 001 |
| `prompt-step2.txt` | พรอมต์ที่ใช้จริง (ตรงกับกรอบใน README ทุกตัวอักษร) |
| `05-step2-result.md` | ข้อความสรุปที่ Claude ตอบเมื่อทำเสร็จ |
| `05-step2-stats.json` | เวลา จำนวนรอบ ค่าใช้จ่าย และโทเคน |
| `06-skill-report.md` | `skill-report.md` ที่ AI เขียน |
| `07-step2-toolcalls.txt`, `07b-step2-session-full.txt` | ลำดับเครื่องมือที่ Claude เรียก (ย่อ / เต็ม) |
| `generated-skills/yolo/SKILL.md`, `generated-skills/cyolo/SKILL.md` | SKILL.md ที่ AI สร้าง (ฉบับ Claude สำเนาฝั่ง Codex เหมือนกันทุกไบต์) |
| `previous-fable-medium/` | การทดลองรอบแรกในวันเดียวกัน (ผู้สร้าง Fable · medium, ค่าเริ่มต้นสกิล fable/medium) ผ่านทั้งหมดเช่นกัน เก็บไว้เทียบ |
