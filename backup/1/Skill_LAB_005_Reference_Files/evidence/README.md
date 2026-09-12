# หลักฐานการทดลอง Skill_LAB 005 (2026-09-10)

รันในคอนเทนเนอร์ `devtools-skilllab-2b4a03` (image `tuchsanai/devtools:2569_1`, Ubuntu 24.04, Claude Code 2.1.267, codex-cli 0.154.0) ตั้งค่าตามผลของ LAB 001 (`BASE_PATH=/root/ai-accounts`) ยืมไฟล์ credential ของ `yolo1`, `yolo2`, `cyolo1` ของผู้สอน บัญชีอื่นไม่ได้ล็อกอิน ทุกไฟล์ปิดบังอีเมล/ชื่อองค์กรเป็น `<email>`/`<ORG>` คอนเทนเนอร์ถูกลบหลังจบชุด

## รูปแบบไฟล์ (ชื่อไฟล์ = `<เงื่อนไข>-<ประโยค>-<cli>-<รอบ>`)

| ไฟล์ | คืออะไร |
|---|---|
| `*.summary.jsonl` | สรุปต่อครั้ง 1 บรรทัด (เวลา, turn/คำสั่ง, ต้นทุน/โทเคน, เครื่องมือ, skill ที่เรียก, คำตอบ 400 ตัวอักษรแรก) |
| `*-claude-*.json` | ผลเต็มของ `yoloN -p --output-format json` (`result`, `modelUsage`, `total_cost_usd`, `num_turns`) |
| `*-claude-*.session.jsonl` / `.transcript.txt` | session log ของ Claude Code และฉบับอ่านง่าย (USER / TOOL / ASSISTANT) |
| `*-codex-*.jsonl` / `.out` / `.rollout.jsonl` | event stream ของ `cyoloN exec --json`, คำตอบสุดท้าย (`-o`), และ rollout ของ session |
| `prompts/` | ประโยคทดสอบที่ใช้จริง |
| `*.err` | stderr ของแต่ละครั้ง |

| `shop-rules-*` | แยกไฟล์ references/ (skill เล็ก) |
| `shop-rules-mono-*` | ไฟล์เดียว (skill เล็ก) |
| `partB/` | ฉบับใหญ่ ~17,000 ตัวอักษร (`shop-rules-big-*` แยกไฟล์, `shop-rules-mono-big-*` ไฟล์เดียว) |

สคริปต์ที่ใช้รันและแปลง log อยู่ใน `../../Skill_LAB_001_Hello_Skill/evidence/common/` (`run-claude.sh`, `run-codex.sh`, `claude-transcript.py`, `codex-transcript.py`)
