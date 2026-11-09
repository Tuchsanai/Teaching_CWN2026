---
name: yolo
description: เรียก Claude Code ทุกบัญชี (yolo1…yoloN) แบบไม่โต้ตอบ เลือกรุ่นและ effort ตรวจล็อกอินจริง ดูโควตา และสถิติต่อครั้ง ใช้เมื่อ "เรียก yolo2", "ให้ yolo ตอบ", "ตรวจล็อกอิน Claude", "โควตา Claude", "สถิติโทเค็นแต่ละบัญชี". Run any Claude Code account non-interactively, choose model/effort, verify real login, read quota and per-call stats. Use for "call yolo2", "ask yolo", "check Claude logins", "Claude quota", "token stats per account".
---

# yolo — Claude Code ทุกบัญชี

สคริปต์: `/root/ai-accounts/.Claude/shared/skills/yolo/scripts/yolo.py` (เรียกว่า `Y` ด้านล่าง)

| ต้องการ | คำสั่ง |
|---|---|
| เรียกงานเดียว | `python3 Y run --account yolo2 --difficulty 1 "ตอบ OK"` |
| ระบุรุ่น/effort เอง | `python3 Y run --account yolo1 --model sonnet --effort medium "..."` |
| ผลเป็น JSON ตาม schema | `python3 Y run --account yolo1 --schema '{"type":"object",...}' "..."` แล้วอ่าน `structured` จาก `--json` |
| prompt จากไฟล์ / stdin | `--prompt-file x.txt` หรือส่ง `-` เป็น prompt |
| ตรวจความพร้อมทุกบัญชี (เรียกจริง) | `python3 Y check` |
| โควตาทุกบัญชี | `python3 Y quota` |
| สถิติตามบัญชี/รุ่น/run | `python3 Y stats` (`--run <id>`, `--json`) |

## ความยาก → รุ่น

`--difficulty 1..6` เลือกให้ตามตาราง และ `--model` / `--effort` ใช้แทนได้

| difficulty | งาน | รุ่น / effort |
|---|---|---|
| 1 | ดึงข้อมูล จัดรูปแบบ ตรวจความพร้อม | haiku / low |
| 2 | สรุป ถาม-ตอบ แก้โค้ดจุดเดียว | sonnet / medium |
| 3 | แก้โค้ดหลายไฟล์ debug วิเคราะห์ | opus / high |
| 4 | reasoning ซับซ้อน อัลกอริทึม | opus / xhigh |
| 5, 6 | ต้องถูกแน่นอน / งานใหญ่ | opus / max |

## กฎสำคัญ (สคริปต์ทำให้แล้ว ถ้าเรียกเองต้องทำตาม)

- ต้องมี `-p` ปิด stdin และวาง prompt ก่อน flag ที่รับหลายค่า
- **exit 0 ไม่ได้แปลว่าสำเร็จ** ดู `is_error` / `result` · `run` คืน non-zero เมื่อ `is_error`
- `auth status` เชื่อไม่ได้ `check` จึงเรียกจริงแล้วแยก พร้อม / ล็อกอินแล้วแต่หมดอายุ / ไม่ได้ล็อกอิน
- `/usage` ไม่เรียกโมเดล บัญชีที่ไม่มีบรรทัด `Current session` ให้ถือว่าไม่มีข้อมูลส่วนนั้น ห้ามเดา
- `total_cost_usd` เป็นราคาตามรายการ ไม่ใช่ยอดจ่ายจริง
- บัญชีเดียวรันพร้อมกันได้เพราะใส่ `--no-session-persistence` แต่ใช้โควตาร่วมกัน
- ทุกครั้งที่สคริปต์เรียกบัญชีจะเพิ่มแถวใน `/workspace/.agent-team/ledger.jsonl` (ไม่เก็บ prompt)
- ห้ามอ่านหรือส่งต่อ `.credentials.json`, `.claude.json` ห้ามแสดงอีเมลหรือ orgId

## เรียกจาก host

อ่านสกิลก่อนเริ่ม แล้วเรียกผ่าน `docker exec` (ใช้ path แบบ `../root/...` ได้ทั้ง PowerShell และ Git Bash โดยไม่ต้องแก้ เพราะ WORKDIR ของ container คือ `/workspace`):

```
docker exec multi-account cat ../root/ai-accounts/.Claude/shared/skills/yolo/SKILL.md
docker exec -i multi-account python3 ../root/ai-accounts/.Claude/shared/skills/yolo/scripts/yolo.py check
docker exec -i multi-account python3 ../root/ai-accounts/.Claude/shared/skills/yolo/scripts/yolo.py quota
docker exec -i multi-account python3 ../root/ai-accounts/.Claude/shared/skills/yolo/scripts/yolo.py stats
docker exec -i multi-account python3 ../root/ai-accounts/.Claude/shared/skills/yolo/scripts/yolo.py run --account yolo1 --difficulty 1 "ตอบ OK"
```
