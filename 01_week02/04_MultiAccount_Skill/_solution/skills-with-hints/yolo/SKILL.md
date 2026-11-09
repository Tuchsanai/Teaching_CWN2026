---
name: yolo
description: ควบคุม Claude Code ทุกบัญชี (yolo1…yoloN) เรียกแบบไม่โต้ตอบให้ถูกวิธี เลือกรุ่น/effort ตรวจล็อกอินจริง โควตา สถิติต่อครั้ง ใช้เมื่อ "เรียก yolo2", "ให้ yolo ตอบ", "เช็กบัญชี Claude", "โควตา Claude", "สถิติโทเค็นแต่ละบัญชี" · Use to run a Claude Code account non-interactively, choose model/effort, verify real login, read quota, or show per-call token stats.
---

# yolo — Claude Code หลายบัญชี

`Y=/root/ai-accounts/.Claude/shared/skills/yolo/scripts/yolo.py` (ใน container รัน `python3 $Y ...` ตรง ๆ ไม่มีคำสั่ง docker) · บน host ดูหัวข้อ "เรียกจาก host"

| ต้องการ | คำสั่ง |
|---|---|
| ถามงานเดียว | `python3 $Y ask yolo2 "สรุป ..." --difficulty 2` |
| ระบุรุ่น/effort | `python3 $Y ask yolo2 "..." --model haiku --effort low` |
| ได้ JSON + สถิติ | เติม `--json` |
| ผลแบบมีโครงสร้าง | เติม `--json-schema '<schema>'` แล้วอ่าน `structured` จาก `--json` |
| ตรวจความพร้อมจริง | `python3 $Y check` (หรือ `check yolo1 yolo2`) |
| โควตา | `python3 $Y quota` |
| สถิติจาก ledger | `python3 $Y stats` (`--run <id>` `--json`) |
| รุ่นและตารางความยาก | `python3 $Y models` |

ความยาก → รุ่น/effort: 1 `haiku/low` · 2 `sonnet/medium` · 3 `opus/high` · 4 `opus/xhigh` · 5–6 `opus/max` (ไม่ระบุ = `haiku/low`)

## หลักที่ต้องรู้

- สคริปต์เรียกแบบถูกต้องให้แล้ว: `-p` + `--no-session-persistence` + stdin ปิด · exit 0 ของ CLI ไม่ได้แปลว่าสำเร็จ สคริปต์ดู `is_error`
- `check` เรียกจริงด้วย `haiku/low` เพราะ `auth status` เชื่อไม่ได้ แยกสถานะ: พร้อม / ล็อกอินแล้วแต่หมดอายุ / ไม่ได้ล็อกอิน
- บัญชีเดียวรันพร้อมกันหลายงานได้ แต่โควตาใช้ร่วมกัน · `quota` อ่าน `/usage` (ไม่เสียโทเค็น) เป็น % ที่ใช้ไปแล้ว บางบัญชีไม่มีบรรทัด session
- ledger: ทุกการเรียกผ่านสคริปต์เพิ่มแถวใน `/workspace/.agent-team/ledger.jsonl` ไม่เก็บ prompt
- ห้ามอ่านหรือส่งต่อ `.credentials.json` และ `.claude.json` ห้ามแสดงอีเมลหรือ orgId
- งานหลายบัญชีร่วมกันใช้สกิล `agent-team`

## เรียกจาก host

อ่านสกิลก่อนเริ่ม แล้วเรียกด้วย `sh -c "..."` (ใช้ได้ทั้ง PowerShell และ Git Bash):

```text
docker exec multi-account sh -c "cat /root/ai-accounts/.Claude/shared/skills/yolo/SKILL.md"
docker exec -i multi-account sh -c "python3 /root/ai-accounts/.Claude/shared/skills/yolo/scripts/yolo.py check"
docker exec -i multi-account sh -c "python3 /root/ai-accounts/.Claude/shared/skills/yolo/scripts/yolo.py ask yolo1 'ตอบ OK' --model haiku --effort low"
```
