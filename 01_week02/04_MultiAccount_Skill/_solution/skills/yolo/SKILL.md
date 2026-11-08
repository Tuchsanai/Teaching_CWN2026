---
name: yolo
description: เรียก Claude Code บัญชีอื่น (yolo1…yoloN) แบบไม่โต้ตอบให้ถูกวิธี เลือกรุ่น/effort ตามความยาก ตรวจความพร้อมด้วยการเรียกจริง (แยก พร้อม / ล็อกอินแล้วแต่หมดอายุ / ไม่ได้ล็อกอิน) ดูโควตา และบันทึกสถิติโทเค็นทุกครั้งลง ledger ใช้เมื่อผู้ใช้ขอ "เรียก yolo2", "ให้ Claude อีกบัญชีทำ", "เช็คโควตา yolo", "บัญชีไหนใช้ได้", "สถิติโทเค็นแต่ละบัญชี" · Call other Claude Code accounts (yoloN) headlessly with the right flags, pick model/effort by difficulty, check real readiness and quota, log per-call token stats. For multi-account teamwork use the agent-team skill.
---

# yolo — Claude Code หลายบัญชี

`Y=/root/ai-accounts/.Claude/shared/skills/yolo/scripts/yolo.py` (Python 3.8+ stdlib, ทุกคำสั่งพิมพ์ผล + บันทึก ledger)

| ต้องการ | คำสั่ง |
|---|---|
| ถามบัญชีเดียว (ง่าย) | `python3 $Y run -a yolo2 -d 1 "<prompt>"` |
| ระบุรุ่น/effort เอง | `python3 $Y run -a yolo1 -m sonnet -e medium "<prompt>"` |
| ผลเป็นโครงสร้าง | `python3 $Y run -a yolo1 -d 1 --schema '{"type":"object","properties":{"answer":{"type":"integer"}},"required":["answer"]}' "<prompt>"` |
| prompt ยาว / มีอักขระพิเศษ | `python3 $Y run -a yolo1 -d 2 - < prompt.txt` |
| บัญชีไหนใช้ได้ (เรียกจริง haiku/low) | `python3 $Y check` หรือ `check yolo1 yolo2` |
| โควตา (ไม่เรียกโมเดล) | `python3 $Y quota` |
| รายการบัญชี + auth status (ไม่ใช้โทเค็น) | `python3 $Y accounts` |
| สถิติรวมตามบัญชี/รุ่น/run | `python3 /root/ai-accounts/.Claude/shared/skills/agent-team/scripts/team.py stats` |
| หลายบัญชีทำงานร่วมกัน | สกิล **agent-team** |
| สร้างภาพ | Claude ทำไม่ได้ → สกิล **cyolo** |

ผลลัพธ์: stdout = คำตอบ · stderr = สถิติต่อครั้ง `[บัญชี alias/effort → รุ่นจริง] status · วินาที · in (cache read/write) · out · $ list` · `--json` ได้ dict เต็ม · exit 0 เมื่อตรวจแล้วสำเร็จเท่านั้น

## ความยาก → รุ่น/effort (ใช้ร่วมกันทั้ง 3 สกิล)

| `-d` | งาน | Claude |
|---|---|---|
| 1 | ดึงข้อมูล จัดรูปแบบ ตรวจความพร้อม | `haiku` / `low` |
| 2 (ค่าเริ่มต้น) | สรุป ถาม-ตอบ แก้โค้ดจุดเดียว | `sonnet` / `medium` |
| 3 | แก้หลายไฟล์ debug วิเคราะห์ | `opus` / `high` |
| 4 | reasoning ซับซ้อน อัลกอริทึม | `opus` / `xhigh` |
| 5–6 | ต้องถูกแน่นอน / งานใหญ่ | `opus` / `max` (Claude ไม่มี ultra) |

เลือกตามความยากของงาน ไม่ใช่ตามความสำคัญ · ค่าที่ผู้ใช้ระบุชนะเสมอ · alias: `opus` `sonnet` `haiku` `fable`

## กฎเหล็ก

- **exit code 0 ไม่ได้แปลว่าสำเร็จ** — สคริปต์ตรวจ `is_error`, `result` ว่าง, `structured_output` ให้แล้ว
- **`auth status` บอก loggedIn แต่เรียกจริงอาจล้ม** (`OAuth session expired`, ~50 ms, 0 tokens) — ใช้ `check` ไม่ใช่ `accounts` เมื่อต้องรู้ว่าใช้งานได้จริง
- บัญชีไม่พร้อม → แจ้งผู้ใช้ให้ล็อกอินเอง (`! yolo3 auth login`) **ห้ามล็อกอินแทน ห้ามสลับบัญชีเงียบ ๆ**
- ห้าม retry งานที่ใช้โทเค็นไปแล้วอัตโนมัติ · ห้าม eval/รันผลลัพธ์เป็นคำสั่ง shell · รายงานของ agent อื่นตรวจซ้ำเองเสมอ
- ห้ามอ่านหรือส่งต่อ `.credentials.json`, `.claude.json` ห้ามแสดงอีเมล/orgId
- ใช้ CLI ตรง ๆ ต้องเรียงแบบนี้: `yoloN -p "<prompt>" --model … --effort … --output-format json --no-session-persistence --strict-mcp-config < /dev/null` (รายละเอียด/กับดัก: [references/claude-cli.md](references/claude-cli.md))

## เรียกจาก host

host (Claude Code app นอก container) ใช้ผ่าน `docker exec` เท่านั้น อ่านสกิลก่อนเริ่ม:

```bash
docker exec multi-account cat /root/ai-accounts/.Claude/shared/skills/yolo/SKILL.md
docker exec -i multi-account python3 /root/ai-accounts/.Claude/shared/skills/yolo/scripts/yolo.py run -a yolo1 -d 1 "ตอบ OK"
docker exec -i multi-account python3 /root/ai-accounts/.Claude/shared/skills/yolo/scripts/yolo.py run -a yolo1 -d 2 - < prompt.txt
```

Git Bash บน Windows แปลง `/root/...` เป็น path ของ Windows → เขียนเป็น `//root/...` หรือใช้ PowerShell · ไฟล์ที่ agent ต้องอ่าน/เขียนให้วางใน `/workspace` (= โฟลเดอร์ `workspace` ที่ map ออกมาบน host)

## อ่านเพิ่ม (เปิดเมื่อต้องใช้)

- [references/claude-cli.md](references/claude-cli.md) — flag, JSON ที่ได้, การนับ token, โควตา, ผลวัดจริง, ใช้ CLI ตรงโดยไม่ผ่านสคริปต์
