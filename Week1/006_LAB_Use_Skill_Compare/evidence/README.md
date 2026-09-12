# หลักฐานการทดลอง LAB 006 (2026-09-09)

รันในคอนเทนเนอร์ `tuchsanai/devtools:2569_1` (Ubuntu 24.04) ชื่อ `devtools-lab004-ab-00c090` Claude Code 2.1.266, codex-cli 0.153.4 ผู้เรียก `yolo1` = Opus · high, `cyolo1` = gpt-6-astra · medium (ค่าเริ่มต้นของ CLI) ทุกไฟล์ปิดบังอีเมลและชื่อองค์กรเป็น `<email>` / `<ORG>` ไม่มี token หรือ credential

ลำดับการวัด: (1) ก่อนมี skill รันประโยคทดสอบ 6 ครั้ง (`ab-driver.sh noskill` = Claude `-p` ×2 + Codex `exec` ×2 แล้วหน้าสนทนาอีกฝั่งละ 1) (2) สร้าง skill ตาม LAB 005 (3) มี skill รันแบบเดียวกันอีก 6 ครั้ง และรันซ้ำจาก shell ในหน้าจอเพื่อถ่ายภาพ

| ไฟล์ | คืออะไร |
|---|---|
| `container-setup/ab-claude.sh`, `ab-codex.sh`, `ab-driver.sh` | สคริปต์รันประโยคทดสอบซ้ำและเก็บ JSON/JSONL |
| `prompt-step3.txt`, `prompt-step4.txt` | ประโยคทดสอบฝั่ง Claude และฝั่ง Codex |
| `ab/noskill.summary.jsonl`, `ab/noskill-*`, `ab/ab-noskill-*-session.txt` | ไม่มี skill · shell ฝั่งละ 2 ครั้ง (JSON ของ `claude -p`, JSONL ของ `codex exec --json`, บันทึก session) |
| `11-noskill-claude-tui-session.txt`, `12-noskill-codex-tui-rollout.txt` | ไม่มี skill · หน้าสนทนา (สำเนาจาก LAB 004) |
| `ab/skill.summary.jsonl`, `ab/skill-*`, `ab/ab-skill-*-session.txt` | มี skill · shell ฝั่งละ 2 ครั้ง |
| `08-skill-claude-tui-session.txt`, `08b-skill-claude-shell-session.txt` | มี skill · Claude หน้าสนทนา และ shell ที่ถ่ายภาพ |
| `09-skill-codex-tui-rollout.txt` | มี skill · Codex หน้าสนทนา (`$yolo`) |
| `13-session-durations.txt` | ระยะเวลาทุก session ในคอนเทนเนอร์ (จาก timestamp แรก–สุดท้าย) |

ภาพหน้าจอใน `../img/` ถ่ายจากหน้า ttyd ของคอนเทนเนอร์ผ่าน Playwright (1324×820)
