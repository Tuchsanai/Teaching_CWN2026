# หลักฐานการทดลอง LAB 004 (2026-09-09)

รันในคอนเทนเนอร์ `tuchsanai/devtools:2569_1` (Ubuntu 24.04) ชื่อ `devtools-lab004-ab-00c090` ผ่านสกิล devtools-lab แล้วลบทิ้งหลังจบ Claude Code 2.1.266, codex-cli 0.153.4, `BASE_PATH=/root/ai-accounts` บัญชี `yolo1` (Claude Max), `yolo2` (Claude Team), `cyolo1` (ChatGPT) ใช้ credential ของผู้สอน บัญชีอื่นไม่ได้ล็อกอิน ทุกไฟล์ปิดบังอีเมลและชื่อองค์กรเป็น `<email>` / `<ORG>`

| ไฟล์ | คืออะไร |
|---|---|
| `01-lab001-layout.txt` | โครงสร้างโฟลเดอร์ `$BASE_PATH` หลังตั้งค่าตาม LAB 001 |
| `02-versions.txt` | `yoloN --version; cyoloN --version` |
| `03-auth-status.txt` | สถานะล็อกอินทั้ง 10 บัญชี (ขั้นที่ 4.2) |
| `04-smoke-test.txt` | ทดสอบเรียก `yolo1` และ `cyolo1` ก่อนเริ่ม รวมกรณี `gpt-5.4-mini` ที่บัญชี ChatGPT ใช้ไม่ได้ |
| `prompt-step3.txt`, `prompt-step4.txt` | ประโยคทดสอบฝั่ง Claude และฝั่ง Codex (ขั้นที่ 4.3) |
| `11-noskill-claude-tui-session.txt` | บันทึก session ของ `yolo1` ก่อนมี skill (เห็น `ListAgents`, `SendMessage`) |
| `12-noskill-codex-tui-rollout.txt` | rollout ของ `cyolo1` ก่อนมี skill |

บันทึกของการทดลองซ้ำเงื่อนไข "ไม่มี skill" อีกฝั่งละ 2 ครั้งผ่าน shell อยู่ใน [LAB 006 evidence/ab/](../../006_LAB_Use_Skill_Compare/evidence/ab/) ภาพหน้าจอใน `../img/` ถ่ายจากหน้า ttyd ของคอนเทนเนอร์ผ่าน Playwright (1324×820) แผนภาพวาดด้วย Excalidraw ต้นฉบับใน `../img/src/`
