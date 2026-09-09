# หลักฐานการทดลอง LAB 004 (2026-09-09)

การทดลองรันในคอนเทนเนอร์ `tuchsanai/devtools:2569_1` (Ubuntu 24.04) ชื่อ `devtools-lab004-ab-00c090` ผ่านสกิล devtools-lab แล้วลบทิ้งหลังจบ

| รายการ | ค่า |
|---|---|
| Claude Code | 2.1.266 (ติดตั้งด้วย `curl -fsSL https://claude.ai/install.sh \| bash`) |
| Codex CLI | 0.153.4 (`npm install -g @openai/codex`) |
| BASE_PATH | `/root/ai-accounts` (= `$HOME/ai-accounts` ตาม LAB 001) |
| บัญชีที่ใช้ | `yolo1` (Claude Max), `yolo2` (Claude Team), `cyolo1` (ChatGPT) — คัดลอกเฉพาะไฟล์ credential ของผู้สอนเข้าไป ไม่ล็อกอินใหม่ |
| บัญชีอื่น | `yolo3`–`yolo5`, `cyolo2`–`cyolo5` ไม่ได้ล็อกอิน (SKIP) |
| โมเดล | ผู้เรียก: yolo1 = Opus · high, cyolo1 = gpt-6-astra · medium (ค่าเริ่มต้นของ CLI) · ค่าเริ่มต้นในสกิล: yolo = opus/high, cyolo = gpt-6-astra/medium |
| ขั้นที่ 2 | `yolo1 -p --model opus --effort high` · 358 s · 29 turns · list price $1.39 · PASS 9 / SKIP 8 / FAIL 0 |

ทุกไฟล์ปิดบังอีเมลและชื่อองค์กรเป็น `<email>` / `<ORG>` แล้ว ไม่มี token หรือ credential

## ลำดับการทดลอง

1. ติดตั้ง CLI และสร้างโครงสร้างตาม LAB 001 (`container-setup/`)
2. **ไม่มี skill**: รันประโยคทดสอบ 6 ครั้ง (`ab-driver.sh noskill` = Claude `-p` ×2 + Codex `exec` ×2, แล้วหน้าสนทนาอีกฝั่งละ 1)
3. ขั้นที่ 2: ให้ yolo1 สร้าง skill ด้วยพรอมต์ `prompt-step2.txt`
4. **มี skill**: รันประโยคทดสอบ 6 ครั้งแบบเดียวกัน (`ab-driver.sh skill` + หน้าสนทนา) และรันซ้ำจาก shell ในหน้าจอเพื่อถ่ายภาพ

## ไฟล์

| ไฟล์ | คืออะไร |
|---|---|
| `container-setup/00-bootstrap.sh` | ติดตั้ง Claude Code + Codex CLI ในคอนเทนเนอร์ (ตาม LAB 001 ขั้นที่ 1–2) |
| `container-setup/01-lab001-result.sh` | สร้างโครงสร้าง `$BASE_PATH` และ wrapper `yolo1–5`, `cyolo1–5` ให้เท่ากับผลลัพธ์ของ LAB 001 |
| `container-setup/ab-claude.sh`, `ab-codex.sh`, `ab-driver.sh` | สคริปต์รันประโยคทดสอบซ้ำและเก็บ JSON/JSONL |
| `01-lab001-layout.txt`, `02-versions.txt`, `03-auth-status.txt`, `04-smoke-test.txt` | โครงสร้าง เวอร์ชัน สถานะล็อกอิน และการทดสอบเรียกก่อนเริ่ม |
| `prompt-step2.txt`, `prompt-step3.txt`, `prompt-step4.txt` | พรอมต์ที่ใช้จริง (ตรงกับกรอบใน README) |
| `11-noskill-claude-tui-session.txt` | ไม่มี skill · Claude หน้าสนทนา (เห็น `ListAgents`, `SendMessage`) |
| `12-noskill-codex-tui-rollout.txt` | ไม่มี skill · Codex หน้าสนทนา |
| `ab/noskill.summary.jsonl`, `ab/noskill-*` | ไม่มี skill · shell ฝั่งละ 2 ครั้ง (JSON ของ `claude -p`, JSONL ของ `codex exec --json`, บันทึก session) |
| `05-step2-result.md`, `05-step2-stats.json` | ขั้นที่ 2: ข้อความสรุปที่ Claude ตอบ และเวลา/รอบ/โทเคน |
| `06-skill-report.md` | `skill-report.md` ที่ AI เขียน |
| `07-step2-toolcalls.txt`, `07b-step2-session-full.txt` | ลำดับเครื่องมือที่ Claude เรียกในขั้นที่ 2 (ย่อ / เต็ม) |
| `generated-skills/yolo/SKILL.md`, `generated-skills/cyolo/SKILL.md` | SKILL.md ที่ AI สร้าง (ฉบับ Claude สำเนาฝั่ง Codex เหมือนกันทุกไบต์) |
| `08-skill-claude-tui-session.txt`, `08b-skill-claude-shell-session.txt` | มี skill · Claude หน้าสนทนา และ shell ที่ถ่ายภาพ |
| `09-skill-codex-tui-rollout.txt` | มี skill · Codex หน้าสนทนา (`$yolo`) |
| `ab/skill.summary.jsonl`, `ab/skill-*` | มี skill · shell ฝั่งละ 2 ครั้ง |
| `13-session-durations.txt` | ระยะเวลาทุก session ในคอนเทนเนอร์ (จาก timestamp แรก–สุดท้าย) |
| `previous-fable-medium/` | การทดลองรอบแรกในวันเดียวกัน (ค่าเริ่มต้นสกิล fable/medium, ผู้เรียก Fable · medium) ผ่านทั้งหมดเช่นกัน เก็บไว้เทียบ |

ภาพหน้าจอใน `../img/` ถ่ายจากหน้า ttyd ของคอนเทนเนอร์ผ่าน Playwright (ขนาด 1324×820) แผนภาพ `overview.png` และ `what-is-skill.png` วาดด้วย Excalidraw ไฟล์ต้นฉบับอยู่ใน `../img/src/`
