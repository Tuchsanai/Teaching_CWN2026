---
name: yolo
description: เรียก Claude Code ของบัญชี yolo1…yoloN แบบไม่โต้ตอบให้ถูกวิธี — เลือกรุ่น/effort ตามความยาก, ตรวจล็อกอินด้วยการเรียกจริง (แยก พร้อม / ล็อกอินแล้วแต่หมดอายุ / ไม่ได้ล็อกอิน), อ่านโควตา /usage และบันทึกสถิติโทเค็นทุกครั้งลง ledger ใช้เมื่อ "เรียก yolo2", "ให้ yolo1 ตอบ", "ตรวจว่า yolo บัญชีไหนใช้ได้", "โควตา yolo", "สถิติโทเค็นแต่ละบัญชี" · Use to call Claude Code accounts (yoloN) non-interactively with the right model/effort, check real login status, read quota and per-call token stats.
---

# yolo — Claude Code หลายบัญชี (`yolo1`…`yoloN`)

สคริปต์: `/root/ai-accounts/.Claude/shared/skills/yolo/scripts/yolo.py` (ใน container `multi-account`) เรียกสั้น ๆ ว่า `Y`

| ต้องการ | คำสั่ง |
|---|---|
| ถามงานเดียว (เลือกรุ่นตามความยาก) | `python3 Y ask yolo2 "<prompt>" --difficulty 1` |
| ระบุรุ่น/effort เอง | `python3 Y ask yolo1 "<prompt>" --model sonnet --effort medium` |
| ผล + สถิติเป็น JSON | `python3 Y ask yolo1 "<prompt>" --json` |
| ผลแบบมีโครงสร้าง | `python3 Y ask yolo1 "<prompt>" --json-schema '{"type":"object",...}' --json` → `structured_output` |
| ตรวจความพร้อมทุกบัญชี (เรียกจริง haiku/low) | `python3 Y check` |
| โควตา (ไม่เสียโทเค็น) | `python3 Y quota` |
| ดูรุ่น/effort ของความยาก N | `python3 Y pick --difficulty 3` |
| สถิติรวมทุกบัญชี | `python3 /root/ai-accounts/.Claude/shared/skills/agent-team/scripts/team.py stats` |

`ask` พิมพ์คำตอบทาง stdout และบรรทัดสถิติ `[yolo1 haiku/low 3.2s in=27684 out=3 $0.0029 ok]` ทาง stderr · exit 0 = สำเร็จจริง, 1 = ล้ม (ข้อความผิดพลาดอยู่ในบรรทัดสถิติ)

## ความยาก → รุ่น / effort (ตารางเดียวกับ cyolo และ agent-team)

| difficulty | งาน | Claude |
|---|---|---|
| 1 | ดึงข้อมูล จัดรูปแบบ ตรวจความพร้อม | `haiku` / `low` |
| 2 | สรุป ถาม-ตอบ แก้โค้ดจุดเดียว (ค่าเริ่มต้น) | `sonnet` / `medium` |
| 3 | แก้โค้ดหลายไฟล์ debug วิเคราะห์ | `opus` / `high` |
| 4 | reasoning ซับซ้อน อัลกอริทึม | `opus` / `xhigh` |
| 5–6 | ต้องถูกแน่นอน / งานใหญ่ | `opus` / `max` |

alias: `opus`→claude-opus-5-5 · `sonnet`→claude-sonnet-5-5 · `haiku`→claude-haiku-5-5 · `fable`→claude-fable-5-1 · effort: `low` `medium` `high` `xhigh` `max`

## กฎที่สคริปต์ทำให้แล้ว (ถ้าเรียก `yoloN` เองต้องทำเหมือนกัน)

- `yoloN -p "<prompt>" --model M --effort E --output-format json --no-session-persistence --strict-mcp-config < /dev/null`
- ปิด stdin เสมอ · prompt อยู่ติด `-p` ก่อน flag ที่รับหลายค่า (`--allowedTools`, `--add-dir`, `--mcp-config`) ไม่งั้น prompt ถูกกลืน
- **exit 0 ไม่ได้แปลว่าสำเร็จ** ตัดสินจาก `is_error` + `result`
- `auth status` บอก `loggedIn: true` แต่เรียกจริงอาจได้ `OAuth session expired` (~50 ms, tokens 0) → `check` จึงเรียกจริงเสมอ
- บัญชีเดียวรันพร้อมกันได้หลายงานเมื่อใส่ `--no-session-persistence` (โควตาใช้ร่วมกันทั้งบัญชี)
- `/usage` เป็นคำสั่งในตัว ไม่เรียกโมเดล ให้บรรทัด `Current session` / `Current week (…)` เป็น % ที่ใช้ไปแล้ว บางบัญชีไม่มีบรรทัด session — ไม่มีข้อมูลก็รายงานว่าไม่มี
- ทุกการเรียกเพิ่ม 1 แถวใน `/workspace/.agent-team/ledger.jsonl` (ไม่เก็บ prompt/secret) · `MA_SIMULATE_LIMIT=yolo1` ทำให้บัญชีนั้นล้มเหมือนโควตาหมด (ทดสอบ failover)
- ห้ามอ่าน/ส่งต่อ `.credentials.json`, `.claude.json` · ห้ามแสดงอีเมลหรือ orgId · ห้ามล็อกอินแทนผู้ใช้

รายละเอียด JSON ที่ได้ ข้อผิดพลาดที่พบ และฟิลด์ ledger: [`references/claude-cli.md`](references/claude-cli.md)

## เรียกจาก host (Claude Code app บน Windows · ใช้ได้ทั้ง PowerShell และ Git Bash)

ห่อด้วย `sh -c "…"` เสมอ (Git Bash จะแปลง `/root/...` ที่เป็น argument เดี่ยวเป็น path Windows) ข้อความใน prompt ใช้ `'…'` ข้างใน

```
docker exec multi-account sh -c "cat /root/ai-accounts/.Claude/shared/skills/yolo/SKILL.md"
docker exec multi-account sh -c "python3 /root/ai-accounts/.Claude/shared/skills/yolo/scripts/yolo.py check"
docker exec multi-account sh -c "python3 /root/ai-accounts/.Claude/shared/skills/yolo/scripts/yolo.py ask yolo1 'ตอบ OK' --difficulty 1"
docker exec multi-account sh -c "python3 /root/ai-accounts/.Claude/shared/skills/yolo/scripts/yolo.py quota"
```

งานหลายบัญชี/ส่งต่องาน ใช้สกิล `agent-team`
