---
name: cyolo
description: ควบคุม Codex CLI ทุกบัญชี (cyolo1…cyoloN) เรียกแบบไม่โต้ตอบ เลือกรุ่น/effort จาก models_cache สร้างภาพ ตรวจล็อกอิน โควตา สถิติต่อครั้ง ใช้เมื่อ "ให้ cyolo ตรวจ", "เรียก cyolo1", "สร้างภาพด้วย cyolo", "โควตา Codex", "สถิติโทเค็นแต่ละบัญชี" · Use to run a Codex account non-interactively, pick model/effort, generate images, verify login, read quota, or show per-call token stats.
---

# cyolo — Codex CLI หลายบัญชี

`X=/root/ai-accounts/.Codex/shared/skills/cyolo/scripts/cyolo.py` (ใน container รัน `python3 $X ...` ตรง ๆ ไม่มีคำสั่ง docker) · บน host ดูหัวข้อ "เรียกจาก host"

| ต้องการ | คำสั่ง |
|---|---|
| ถามงานเดียว | `python3 $X ask cyolo1 "ตรวจ ..." --difficulty 2` |
| ระบุรุ่น/effort | `python3 $X ask cyolo1 "..." --model gpt-6-luna --effort low` |
| ได้ JSON + สถิติ | เติม `--json` |
| สร้างภาพ PNG | `python3 $X image cyolo1 "วงกลมสีแดงบนพื้นขาว ขนาดเล็ก" /workspace/a.png` |
| ตรวจล็อกอิน + เรียกจริง | `python3 $X check` |
| โควตา (เวลาของข้อมูลกำกับ) | `python3 $X quota` · ข้อมูลเก่าเติม `--refresh` |
| รุ่นและ effort ที่รองรับ | `python3 $X models` |
| สถิติจาก ledger | `python3 $X stats` |

ความยาก → effort: 1 `low` · 2 `medium` · 3 `high` · 4 `xhigh` · 5 `max` · 6 `ultra` (ไม่ระบุ = `low`) รุ่นเริ่มต้น `gpt-6.1-sol`

## หลักที่ต้องรู้

- ใช้ `--ephemeral` เป็นค่าเริ่มต้น (เร็วกว่า ~3.5 เท่า) · อ่านคำตอบจากไฟล์ `-o` และ `turn.completed` / `turn.failed`
- `input_tokens` ของ Codex รวม cached แล้ว
- effort ที่รุ่นไม่รองรับถูกลดเป็นระดับสูงสุดที่รองรับ และบันทึก `effort_from` ใน ledger
- งาน ephemeral ไม่อัปเดตโควตา ข้อมูลโควตาจึงมาจาก rollout เก่าได้ ดูเวลาของข้อมูลเสมอ `--refresh` เรียกสั้น 1 ครั้งแบบไม่ ephemeral
- สร้างภาพใช้ `low` เสมอ prompt ควรแจกแจงทุกเงื่อนไขเป็นข้อ path ต้องเป็น absolute สคริปต์ตรวจ PNG signature ให้
- ledger: ทุกการเรียกผ่านสคริปต์เพิ่มแถวใน `/workspace/.agent-team/ledger.jsonl` ไม่เก็บ prompt
- ห้ามอ่านหรือส่งต่อ `auth.json` · งานหลายบัญชีร่วมกันใช้สกิล `agent-team`

## เรียกจาก host

อ่านสกิลก่อนเริ่ม แล้วเรียกด้วย `sh -c "..."` (ใช้ได้ทั้ง PowerShell และ Git Bash):

```text
docker exec multi-account sh -c "cat /root/ai-accounts/.Codex/shared/skills/cyolo/SKILL.md"
docker exec -i multi-account sh -c "python3 /root/ai-accounts/.Codex/shared/skills/cyolo/scripts/cyolo.py check"
docker exec -i multi-account sh -c "python3 /root/ai-accounts/.Codex/shared/skills/cyolo/scripts/cyolo.py ask cyolo1 'ตอบ OK' --effort low"
```
