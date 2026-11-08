# กราฟงาน — ฟิลด์ทั้งหมดและรูปแบบขั้นสูง

ไฟล์กราฟเป็น object `{"goal", "defaults", "board", "nodes": [...]}` หรือ list ของงานเฉย ๆ · `defaults` ถูกเติมให้ทุกงานที่ไม่ได้ระบุ · `"board": false` ปิดการแทรก board ใน prompt

## ฟิลด์ของงาน

| field | ชนิด | ความหมาย |
|---|---|---|
| `id` | str | ไม่ซ้ำ ใช้ใน placeholder (`a-z0-9_.-`) |
| `prompt` | str | คำสั่งงาน รองรับ `{{id}}` `{{file:id}}` `{{account:id}}` `{{run_dir}}` `{{board}}` |
| `account` | str | `yoloN` / `cyoloN` (pinned) · `yolo`/`claude` · `cyolo`/`codex` · `any` (ค่าเริ่มต้น) |
| `depends_on` | list | id ที่ต้องสำเร็จก่อน (placeholder เพิ่มให้อัตโนมัติ) |
| `expect` | str | `text` · `int` · `number` · `json` · `regex:<pat>` (มี group 1 = ค่าที่ส่งต่อ) · `contains:<s>` · `png` |
| `difficulty` | 1–6 | เลือกรุ่น/effort (ค่าเริ่มต้น 2 หรือ `run --difficulty`) |
| `model`, `effort` | str | ระบุตรง; `model` ผูกงานกับฝั่งของรุ่นนั้น (`haiku` → Claude, `gpt-6.1-sol` → Codex) |
| `kind` | str | `image` · `code_review` · `doc` · `code` (code/difficulty≥3 สั่งให้เขียนความคืบหน้าลง `msgs/`) |
| `cwd` | str | โฟลเดอร์ทำงาน absolute (สร้างให้) และบอกใน prompt |
| `output` | str | path ของภาพ (kind image) ค่าเริ่มต้น `out/<id>.png` |
| `schema` | object | ผลแบบมีโครงสร้าง (Claude `--json-schema`, Codex `--output-schema` ต้อง strict) |
| `timeout` | int | วินาที (ค่าเริ่มต้น 600) |
| `approve` | bool | human gate |

## prompt ที่ worker ได้รับ

```
[ทีม <run> · งาน <id> · บัญชี <acct>]
โฟลเดอร์ทำงาน (absolute path): …          (ถ้ามี cwd)
กระดานความรู้กลาง (…/board.md): …          (ถ้ามีข้อค้นพบ ≤1500 ตัวอักษร ไม่งั้นบอก path)
ถ้าพบข้อเท็จจริงที่งานอื่นควรรู้ ให้เขียนเป็นบรรทัดขึ้นต้นด้วย BOARD:
---
<prompt ที่แทน placeholder แล้ว>
(รูปแบบคำตอบ: จำนวนเต็มอย่างเดียว)          (ตาม expect)
```

บรรทัด `BOARD:` ถูกตัดออกจากคำตอบก่อนตรวจ `expect` และต่อท้าย `board.md` พร้อมผู้เขียน/เวลา

## review loop

```json
{"id": "essay", "type": "review", "account": "yolo", "reviewer": "cyolo", "max_rounds": 3,
 "prompt": "เขียนย่อหน้า 3 ประโยคเรื่อง …",
 "review_prompt": "ตรวจว่า 3 ประโยคพอดีและมีคำว่า X"}
```
รอบละ 2 การเรียก (ผู้ทำ + ผู้ตรวจ) · รอบถัดไปผู้ทำได้ความเห็นผู้ตรวจและ path ของร่างเดิม · ผล: `out/essay.md` (ฉบับสุดท้าย), `out/essay.rN.md`, `out/essay.review.md` · ครบ `max_rounds` โดยไม่ APPROVED = "ไม่ผ่านการตรวจ" · ผู้ตรวจค่าเริ่มต้นคือฝั่งตรงข้ามกับผู้ทำ

## debate / ตรวจไขว้

```json
{"id": "q", "type": "debate", "prompt": "จำนวนเฉพาะระหว่าง 1–100 มีกี่ตัว ใช้เชลล์คำนวณ", "accounts": ["yolo", "cyolo"], "judge": "yolo"}
```
ขยายเป็น `q.1` (yolo), `q.2` (cyolo) รันพร้อมกัน แล้ว `q` = ผู้ตัดสินตอบ JSON `{"final", "winner", "reason"}` (ต้องมี reason) · `{{q}}` ในงานถัดไปได้ JSON นั้น

## best-of-N + judge

```json
{"id": "slogan", "type": "best_of", "n": 3, "accounts": ["yolo1", "yolo2", "cyolo1"],
 "prompt": "คิดสโลแกนสั้นสำหรับ …", "criteria": "สั้น จำง่าย ตรงโจทย์", "judge": "cyolo"}
```
`slogan.1..N` → ผู้ตัดสินตอบ `{"best": "B", "scores": {...}, "reason": "…"}` · ผลงานที่ชนะคัดลอกไป `out/slogan.best.md`

## router (`account: any`)

ลำดับการตัดสิน: `kind: image` หรือ prompt มี "สร้างภาพ/image generation" → cyolo (ผูกฝั่ง) · `kind: code_review` หรือ "ตรวจโค้ด/code review" → Codex · `kind: doc|long|summary|writing` หรือ prompt > 4000 ตัวอักษร → Claude · นอกนั้นเลือกจากทุกบัญชีที่พร้อม: งานในคิวน้อยสุด → โควตาใช้ไปน้อยสุด → tokens ใน run น้อยสุด · เหตุผลอยู่ใน `state.json` (`route`) และบรรทัด `a → yolo1 (…)` ตอนเริ่ม

## failover

งานที่ล้มเพราะโควตาหมด/rate limit/ล็อกอินหมดอายุ (tokens = 0) → บัญชีนั้นถูกตั้ง "ใช้ไม่ได้" งานย้ายไปบัญชีอื่นฝั่งเดียวกันก่อน (ไม่มีจึงข้ามฝั่ง ถ้า `account: any`) · บันทึก `worker_switch` · งานที่ระบุบัญชีเองไม่ย้าย: หยุดและรายงาน · ทดสอบด้วย `MA_SIMULATE_LIMIT=yolo1 python3 team.py run g.json`

## human gate

`"approve": true` → สถานะ "รออนุมัติ" (งานอิสระอื่นรันต่อ) · ถ้าไม่มีอะไรรันแล้ว `run` จบ (exit 0) และบอกคำสั่ง · อนุมัติ: `team.py approve --run <id> <งาน>` (สร้าง `approvals/<งาน>`) แล้ว `team.py run --resume <id>` · หรือรันด้วย `--wait-approval 600` ให้รอไฟล์เอง

## resume

`run --resume <id> [graph.json] [--set id.field=value]` · งานสำเร็จไม่รันซ้ำ (ไม่มีแถวใหม่ใน ledger) · งานล้ม/ถูกบล็อก/รูปแบบไม่ผ่านรันใหม่ · แก้ `prompt`/`expect`/`account`/`difficulty`… ได้จากไฟล์กราฟ (จับคู่ด้วย id) หรือ `--set` · ถ้าแก้แค่ `expect` ของงานที่รูปแบบไม่ผ่าน จะตรวจคำตอบเดิมใหม่โดยไม่เรียกโมเดล
