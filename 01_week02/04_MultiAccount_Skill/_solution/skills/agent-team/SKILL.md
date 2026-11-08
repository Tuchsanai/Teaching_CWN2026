---
name: agent-team
description: ให้หลายบัญชี Claude (yoloN) และ Codex (cyoloN) ทำงานร่วมกันแบบ multi-agent ทั้งใน CLI เดียวกันและข้าม CLI — relay ส่งต่องาน, fan-out/fan-in, กราฟ DAG, review loop, กระดานความรู้กลาง, debate/ตรวจไขว้, best-of-N + ผู้ตัดสิน, router เลือกฝั่งอัตโนมัติ, กระจายโหลดตามโควตา + failover, human gate, บริหารโทเค็นลูกทีม, สลับหัวหน้าทีมเมื่อโควตาหมด และสรุปสถิติทั้งทีม ใช้เมื่อผู้ใช้ขอ "แบ่งงานหลายบัญชี", "ส่งต่องานระหว่าง agent", "ให้ Claude กับ Codex ตรวจกันเอง", "รันขนาน", "ทีม agent", "สถิติโทเค็นแต่ละบัญชี", "โควตาทุกบัญชี" · Multi-account teamwork across Claude Code and Codex: task graphs, handoffs, shared board, review/debate/best-of-N, quota-aware routing with failover, human gates, worker token budgets, leader handoff, team-wide token stats.
---

# agent-team — ทีม agent หลายบัญชี

`T=/root/ai-accounts/.Claude/shared/skills/agent-team/scripts/team.py` (ต้องติดตั้งคู่กับสกิล yolo และ cyolo)

| ต้องการ | คำสั่ง |
|---|---|
| บัญชีไหนใช้ได้ (เรียกจริง, แคช 10 นาที) | `python3 $T check` (`--recheck` บังคับตรวจใหม่) |
| โควตาทุกบัญชี + เวลาของข้อมูล | `python3 $T quota` (`--fresh` อ่านใหม่) |
| รันกราฟงานจนจบ | `python3 $T run graph.json` (หรือ `run - < graph.json`) |
| รันเบื้องหลัง (มี human gate) | `python3 $T run graph.json --detach` แล้ว `status` / `wait` |
| ดูภาพรวมทีม | `python3 $T status --run <id>` |
| อนุมัติ human gate | `python3 $T approve <node> --run <id>` |
| สถิติตามบัญชี/รุ่น/run | `python3 $T stats [--run <id>] [--json]` |
| หัวหน้าทีมที่สลับตัวเองได้ | `python3 $T lead --goal "<เป้าหมาย>" [--succession yolo2,cyolo1] [--lead-token-budget N]` |
| จำกัดงบลูกทีม | `--worker-token-budget 50000` หรือ `yolo1=20000,cyolo2=30000` |

ทุก run อยู่ที่ `/workspace/.agent-team/<run_id>/`: `graph.json` `state.json` `board.md` `handoff.md` `msgs/<จาก>__<ถึง>.md` `out/<node>.md` `ledger.jsonl` (+ ledger รวม `/workspace/.agent-team/ledger.jsonl`)

## กราฟงานแบบสั้น

```json
{"goal": "relay ข้าม CLI", "defaults": {"difficulty": 1},
 "nodes": [
  {"id": "a", "account": "cyolo", "prompt": "7*6 = ?", "expect": "int"},
  {"id": "b", "account": "yolo",  "prompt": "นำ {{a}} บวก 100", "expect": "int"},
  {"id": "c", "account": "cyolo1", "prompt": "นำ {{b}} คูณ 3", "expect": "int"}]}
```

| รูปแบบ | ทำอย่างไร |
|---|---|
| relay | `{{id}}` ใน prompt (ค่าสั้น ≤ 2000 ตัวอักษร) — เพิ่ม `depends_on` ให้เอง |
| ข้อมูลยาว | `{{file:id}}` = path ของ `out/id.md` ให้ผู้รับอ่านเอง (ห้ามยัดข้อความยาวลง prompt) |
| fan-out / fan-in | หลาย node ไม่มี dependency (รันพร้อมกัน) + node รวมที่อ้าง `{{file:x}}` ทุกตัว |
| review loop | `"type": "review"`, `account` = ผู้ทำ, `reviewer`, `criteria`, `max_rounds` |
| debate / ตรวจไขว้ | `"type": "debate"`, `candidates: ["yolo","cyolo"]`, `judge` |
| best-of-N | `"type": "best_of"`, `candidates: [...]` หรือ `n`, `criteria`, `judge` |
| router | `"account": "any"` (ภาพ → cyolo · ตรวจโค้ด → Codex · เอกสารยาว → Claude · อื่น ๆ → ฝั่งโควตาเหลือมาก) |
| human gate | `"approve": true` หยุดรอไฟล์ `approvals/<id>.ok` |
| board | ทุก agent ได้ข้อค้นพบใน `board.md` ก่อนเริ่ม · บรรทัด `BOARD: …` ในคำตอบถูกเพิ่มลงกระดาน |
| ภาพ | `"image": "/workspace/x.png"` (ไป cyolo เสมอ ตรวจ PNG) |

ฟิลด์ทั้งหมดและตัวอย่างทุกรูปแบบ: [references/graph.md](references/graph.md)

## กฎที่ scheduler ทำให้เอง

- ตรวจความพร้อมทุกบัญชีด้วยการเรียกจริงก่อนเริ่ม ข้ามบัญชีที่ใช้ไม่ได้พร้อมแจ้งใน `board.md`
- `account`: บัญชีเจาะจง (`yolo2` = **ไม่ย้ายอัตโนมัติ** ล้มแล้วหยุดและรายงาน) · ฝั่ง (`yolo`/`cyolo`) · `any`
- พร้อมกันสูงสุด 3 งาน/บัญชี และ 8 งานรวม (`--per-account`, `--max`) · timeout ต่องาน 600 s (`--timeout`)
- ผลแต่ละงานตรวจรูปแบบ (`expect`: `int` `number` `json` `text` `regex:…`) ก่อนส่งต่อ · งานล้ม → งานที่ขึ้นกับมัน `blocked` · **ไม่ retry งานที่เสียโทเค็น** · ไม่ eval ผลลัพธ์
- งานที่ล้มเพราะโควตา/ล็อกอินหมดอายุ (ไม่เสียโทเค็น) ย้ายไปบัญชีอื่นฝั่งเดียวกันก่อน แล้วจึงข้ามฝั่งถ้าไม่ผูก CLI · บันทึก `worker_switch` ใน state.json, board.md, ledger
- บัญชีที่โควตา ≥ 80% หรือใช้โทเค็นเกินงบ → **หยุดรับงาน** งานที่รันอยู่ปล่อยให้จบ งานในคิวย้ายไปคนอื่น
- ทุกการเรียกบันทึก ledger (ไม่มีข้อความ prompt/secret) · จำลองโควตาหมด: `MA_SIMULATE_LIMIT=yolo1` (หรือ `yolo1:2` = ล้มตั้งแต่ครั้งที่ 2)

รายละเอียดการบริหารโทเค็น ledger และ status: [references/tokens.md](references/tokens.md)

## หัวหน้าทีม (`lead`)

ผู้ควบคุมเป็นสคริปต์ (ไม่ใช้โทเค็น) รันหัวหน้าเป็นรอบสั้น ๆ หัวหน้าอ่าน `handoff.md` สั่งงานผ่าน `team.py add/dispatch/wait` แล้ว `checkpoint` ก่อนจบรอบ ลูกทีมรันเป็น process แยก หัวหน้าเปลี่ยนตัวแล้วงานไม่หาย · สลับเชิงรุกเมื่อโควตา ≥ 80% หรือเกิน `--lead-token-budget` · สลับเชิงรับเมื่อรอบล้ม/timeout/heartbeat หยุด · ผู้สืบทอดจาก `--succession` หรือเลือกอัตโนมัติ (ฝั่งเดียวกันก่อน) · ห้ามบางบัญชีด้วย `--forbid` · ทดสอบได้ด้วย `MA_SIMULATE_CRASH=lead_after_dispatch`

ขั้นตอนและคำสั่งของหัวหน้า: [references/leader.md](references/leader.md)

## เรียกจาก host

host (Claude Code app นอก container) ใช้ผ่าน `docker exec` เท่านั้น อ่านสกิลก่อนเริ่ม:

```bash
docker exec multi-account cat /root/ai-accounts/.Claude/shared/skills/agent-team/SKILL.md
docker exec -i multi-account python3 /root/ai-accounts/.Claude/shared/skills/agent-team/scripts/team.py run - < graph.json
docker exec multi-account python3 /root/ai-accounts/.Claude/shared/skills/agent-team/scripts/team.py status
```

Git Bash บน Windows แปลง `/root/...` เป็น path ของ Windows → เขียนเป็น `//root/...` หรือใช้ PowerShell · run directory อยู่ใน `/workspace/.agent-team/` = โฟลเดอร์ `workspace/.agent-team` บน host อ่านผลได้ตรง ๆ
