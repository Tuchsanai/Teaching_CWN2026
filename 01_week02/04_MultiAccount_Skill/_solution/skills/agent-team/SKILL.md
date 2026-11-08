---
name: agent-team
description: ให้หลายบัญชี (yoloN = Claude Code, cyoloN = Codex) ทำงานร่วมกันแบบ multi-agent ทั้งใน CLI เดียวกันและข้าม CLI — relay ส่งต่องาน, fan-out/fan-in, DAG, review loop, board แชร์ความรู้, debate, best-of-N + judge, router, failover ตามโควตา, human gate, งบโทเค็นลูกทีม, สลับหัวหน้าทีม และตารางสถิติ + โควตาทั้งทีม ใช้เมื่อ "แบ่งงานหลายบัญชี", "ส่งต่องานระหว่าง agent", "ให้ yolo ทำแล้ว cyolo ตรวจ", "ทำขนานแล้วรวมผล", "สถิติโทเค็นแต่ละบัญชี", "สาธิตสลับหัวหน้าทีม" · Use for multi-account multi-agent work: relay, fan-out, DAG, review, debate, best-of-N, routing, failover, leader handoff, team token stats.
---

# agent-team — หลายบัญชีทำงานเป็นทีม

container `multi-account` · `T` = `/root/ai-accounts/.Claude/shared/skills/agent-team/scripts/team.py` (สำเนาใน `.Codex/shared/skills/` ด้วย) · ใช้สกิล `yolo`/`cyolo` ข้างเคียง · run อยู่ที่ `/workspace/.agent-team/<run_id>/`

| ต้องการ | คำสั่ง |
|---|---|
| บัญชีไหนพร้อม (เรียกจริง) | `python3 T check` |
| โควตาทุกบัญชี + เวลาของข้อมูล | `python3 T quota` |
| รันกราฟงาน → จบด้วยตาราง + โควตา | `python3 T run graph.json` (`--json` ให้โปรแกรมอ่าน) |
| รันต่อเฉพาะงานที่ล้ม/ถูกบล็อก | `python3 T run --resume <run_id> [กราฟที่แก้.json] [--set <งาน>.expect=text]` |
| ภาพรวมทีม (บทบาท คิว tokens โควตา สถานะ) | `python3 T status [--run <id>]` |
| สถิติจาก ledger ตามบัญชี/รุ่น/run | `python3 T stats [--run <id>]` |
| อนุมัติงาน `"approve": true` | `python3 T approve --run <id> <งาน>` แล้ว `run --resume <id>` |
| หัวหน้าทีม + สลับหัวหน้าอัตโนมัติ | `python3 T lead --goal "<เป้าหมาย>"` |
| สาธิตสลับหัวหน้า/ย้ายงานในคำสั่งเดียว | `python3 T lead --demo --lead-model haiku [--goal "<เป้าหมาย>"]` |

exit: 0 = คำสั่งสำเร็จ (แม้บางบัญชีไม่พร้อม/รออนุมัติ) · 1 = มีงานล้ม · 2 = กราฟ/argument ผิด

## กราฟงาน (JSON)

```json
{"goal": "…", "defaults": {"difficulty": 1},
 "nodes": [
  {"id": "a", "account": "yolo",  "prompt": "คำนวณ 7*6", "expect": "int"},
  {"id": "b", "account": "cyolo", "prompt": "นำ {{a}} บวก 100", "expect": "int"},
  {"id": "c", "account": "any",   "prompt": "สรุปไฟล์ {{file:b}}"}
 ]}
```

| field | ค่า |
|---|---|
| `account` | **แนะนำ** `yolo` / `cyolo` / `any` (ระบบเลือกบัญชีที่พร้อม งานน้อย โควตาเหลือมาก และย้ายงานเมื่อบัญชีล้ม) · `any` = router: ภาพ → cyolo, `kind: code_review` → Codex, `kind: doc` → Claude · บัญชีเจาะจง `yolo2` ใช้เฉพาะบัญชีที่ `check` ว่าพร้อม (ไม่พร้อม = `run` ไม่เริ่มและบอกบัญชีที่พร้อม · ระหว่างรันไม่ย้ายอัตโนมัติ) |
| `prompt` | `{{a}}` ค่าสั้นของงาน a (ยาว > 1500 ตัวอักษรกลายเป็น path ให้เอง) · `{{file:a}}` path ของ `out/a.md` · `{{account:a}}` · `{{run_dir}}` · placeholder สร้าง `depends_on` ให้ |
| `depends_on` | id ที่ต้องเสร็จก่อน (ลำดับโดยไม่ส่งค่า) งานที่พร้อมรันพร้อมกันเอง |
| `expect` | `text` (ค่าเริ่มต้น ใช้กับความเรียง) · `int`/`number` (รับ `42` หรือ `50 - 8 = 42`) · `json` · `regex:<pat>` · `contains:<คำ>` · `png` |
| `difficulty` 1–6 | 1 = haiku/low · Codex low, 2 = sonnet/medium (ค่าเริ่มต้น), 3 = opus/high … (หรือ `model`/`effort`) |
| `cwd` | โฟลเดอร์ทำงาน absolute (งานแก้โค้ดพร้อมกันให้แยกโฟลเดอร์) |
| `kind` / อื่น ๆ | `image` (ผล `out/<id>.png`) · `code_review` · `doc` · `approve: true` = human gate · `timeout` (600 s) |

ชนิดพิเศษ: `"type": "review"` + `reviewer`, `review_prompt`, `max_rounds` (วนจนผู้ตรวจตอบ `APPROVED`) · `"type": "debate"` + `accounts` (ค่าเริ่มต้น `["yolo","cyolo"]`), `judge` · `"type": "best_of"` + `n`, `accounts`, `criteria`, `judge` — ผู้ตัดสินตอบ JSON พร้อม `reason` ผลงานที่ชนะอยู่ `out/<id>.best.md`

ผลผิด `expect` เก็บไว้ใน `out/` พร้อมเหตุผล (resume ที่แก้แค่ `expect` ตรวจใหม่โดยไม่เรียกซ้ำ) · งานล้ม → งานที่ขึ้นกับมันถูกบล็อก ไม่ retry อัตโนมัติ · บรรทัด `BOARD: …` ในคำตอบถูกบันทึกลง `board.md` ให้งานถัดไปเห็น

### ตัวอย่างพร้อมดัดแปลง: ทำขนานหลายบัญชี → อีกบัญชีตรวจ → แก้และทดสอบ

```json
{"goal": "slugify + ทดสอบ", "defaults": {"difficulty": 1},
 "nodes": [
  {"id": "impl_a", "account": "yolo", "cwd": "/workspace/proj/a",
   "prompt": "เขียน /workspace/proj/a/slug.py ฟังก์ชัน slugify(s): ตัวเล็ก เว้นวรรคเป็น - ตัดอักขระพิเศษ ตอบสรุป 1 บรรทัด"},
  {"id": "impl_b", "account": "cyolo", "cwd": "/workspace/proj/b",
   "prompt": "เขียน /workspace/proj/b/slug.py ฟังก์ชัน slugify(s) สเปกเดียวกัน ตอบสรุป 1 บรรทัด"},
  {"id": "review", "account": "cyolo", "kind": "code_review", "depends_on": ["impl_a", "impl_b"],
   "prompt": "ตรวจโค้ด /workspace/proj/a/slug.py และ /workspace/proj/b/slug.py เลือกฉบับที่ดีกว่า บอกบั๊กเป็นข้อ ๆ"},
  {"id": "fix", "account": "yolo", "cwd": "/workspace/proj/final",
   "prompt": "อ่านผลตรวจ {{file:review}} เขียน /workspace/proj/final/slug.py ฉบับแก้ + test_slug.py รัน python3 -m unittest จริง บรรทัดสุดท้ายตอบ PASS หรือ FAIL",
   "expect": "regex:(PASS)"}
 ]}
```

ดัดแปลง: fan-out/fan-in = งานอิสระหลายตัว + งานรวมที่อ้าง `{{x}}`/`{{file:x}}` ทุกตัว · review loop = `{"id":"essay","type":"review","account":"yolo","reviewer":"cyolo","prompt":"…","review_prompt":"เกณฑ์ …","max_rounds":3}` · ผสม = `{"id":"q","type":"debate","prompt":"…"}` + `{"id":"pic","account":"any","kind":"image","prompt":"เงื่อนไขภาพเป็นข้อ ๆ"}` ในกราฟเดียว · งานคำนวณสั่ง "ใช้เชลล์คำนวณ" และตรวจผลอิสระเสมอ

ตัวเลือก `run` (ดู `--help`): `--per-account 3` `--max-parallel 8` `--timeout 600` `--worker-token-budget N|บัญชี=N` `--quota-threshold 80` `--exclude` `--wait-approval S`

## หัวหน้าทีม (lead) และคำสั่งสาธิต

`lead` = ผู้ควบคุม (สคริปต์ ไม่ใช้โทเค็น) รันหัวหน้าเป็นรอบสั้นที่อ่าน `handoff.md` + `state.json` แล้วแจกงาน · ลูกทีมเป็น process แยก หัวหน้าเปลี่ยนตัวงานไม่หาย · รัน foreground (~1 นาทีกับ haiku) จบด้วยตาราง สลับหัวหน้า · ย้ายงาน · ผลแต่ละงาน · สถิติตามบัญชี

```
python3 T lead --demo --lead-model haiku
python3 T lead --demo --lead-model haiku --goal "เขียนคำอธิบายสั้นของ 4 ภาษาโปรแกรม แบ่งให้ลูกทีมคนละภาษา แล้วรวมเป็นไฟล์เดียว"
```

`--demo` ใช้กับเป้าหมายใดก็ได้ (ไม่ใส่ `--goal` = สูตรคูณแม่ 2–9 พร้อมตรวจผลอิสระ) และเกิดครบ 3 เหตุการณ์ในรันเดียว (ต้องมีบัญชีพร้อม ≥ 3):
1. **เชิงรับ** หัวหน้าคนแรกถูก kill หลังแจกงานครั้งแรก (`--simulate-crash <บัญชี>`) → คนใหม่ทำต่อจาก checkpoint + `state.json`
2. **เชิงรุก** หัวหน้าคนที่สองงบ 1 token (`--lead-token-budget <บัญชี>=1`) → checkpoint → ส่งไม้ (ข้ามไป Codex ได้)
3. **ย้ายงานลูกทีม** ลูกทีมหนึ่งคนงบ 1 token (`--worker-token-budget <บัญชี>=1`, `--per-account 1`) → งานในคิวของเขาย้ายบัญชี, `status` แสดง "หยุดรับงาน"

ตั้งเองได้: `--succession yolo1,yolo2,cyolo1` · `--lead-token-budget 200000` · `--simulate-limit cyolo2` (= `MA_SIMULATE_LIMIT`) · `--output <path>` · `--lead-model sonnet` (ค่าเริ่มต้น) — รายละเอียด [`references/leader.md`](references/leader.md)

## เรียกจาก host (Claude Code app บน Windows · ใช้ได้ทั้ง PowerShell และ Git Bash)

ห่อทุกคำสั่งด้วย `sh -c "…"` (Git Bash แปลง `/root/...` ที่เป็น argument เดี่ยว) · ส่งกราฟ: เขียน `graph.json` บน host ด้วยเครื่องมือ Write (ไม่ใช้ heredoc) แล้ว `docker cp` (ปลายทาง `tmp/…` ไม่ขึ้นต้นด้วย `/` จึงไม่ถูกแปลง)

```
docker exec multi-account sh -c "cat /root/ai-accounts/.Claude/shared/skills/agent-team/SKILL.md"
docker exec multi-account sh -c "python3 /root/ai-accounts/.Claude/shared/skills/agent-team/scripts/team.py check"
docker cp graph.json multi-account:tmp/graph.json
docker exec multi-account sh -c "python3 /root/ai-accounts/.Claude/shared/skills/agent-team/scripts/team.py run /tmp/graph.json"
docker exec multi-account sh -c "python3 /root/ai-accounts/.Claude/shared/skills/agent-team/scripts/team.py status"
docker exec multi-account sh -c "python3 /root/ai-accounts/.Claude/shared/skills/agent-team/scripts/team.py stats"
docker exec multi-account sh -c "python3 /root/ai-accounts/.Claude/shared/skills/agent-team/scripts/team.py lead --demo --lead-model haiku"
docker exec multi-account sh -c "ls /workspace/.agent-team/<run_id>/out"
```

(Git Bash ส่ง stdin ได้ด้วย `docker exec -i … run - < graph.json` แต่ PowerShell 5.1 ไม่มี `<` จึงใช้ `docker cp`)

เพิ่มเติม (เปิดเมื่อจำเป็น): [`references/graph.md`](references/graph.md) ฟิลด์ทั้งหมด/รูปแบบขั้นสูง · [`references/leader.md`](references/leader.md) สลับหัวหน้า/งบโทเค็น · [`references/files.md`](references/files.md) ไฟล์ใน run, ledger, สถิติ
