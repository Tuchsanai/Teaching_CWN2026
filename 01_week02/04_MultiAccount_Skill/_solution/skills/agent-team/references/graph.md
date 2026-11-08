# กราฟงาน (graph.json)

```json
{"goal": "<ข้อความ>", "defaults": {"difficulty": 1, "timeout": 300}, "nodes": [ {…}, … ]}
```

`defaults` ถูกเติมให้ทุก node ที่ไม่ได้ระบุเอง · node ต้องประกาศหลัง node ที่มันขึ้นด้วย

## ฟิลด์ของ node

| ฟิลด์ | ค่า | หมายเหตุ |
|---|---|---|
| `id` | `[A-Za-z0-9_.-]+` | ชื่อไฟล์ผล `out/<id>.md` |
| `prompt` | ข้อความ | ใช้ `{{id}}` / `{{file:id}}` ได้ |
| `type` | `task` (ค่าเริ่มต้น) · `review` · `debate` · `best_of` | |
| `account` | `yoloN` · `cyoloN` · `yolo` · `cyolo` · `any` (ค่าเริ่มต้น) | บัญชีเจาะจง = pinned ไม่ย้ายอัตโนมัติ |
| `depends_on` | `["a","b"]` | template เพิ่มให้เอง |
| `difficulty` | 1–6 | ตารางความยาก (ค่าเริ่มต้น 2) |
| `model`, `effort` | ระบุตรง | `model` ของ Claude ใช้เฉพาะเมื่อได้บัญชี yolo และกลับกัน |
| `expect` | `int` `number` `json` `text` `regex:<pattern>` | ตรวจก่อนส่งต่อ ไม่ผ่าน = งานล้ม |
| `schema` | JSON schema | ผลแบบมีโครงสร้าง (Claude `--json-schema`, Codex `--output-schema` แบบ strict) |
| `image` | absolute path `.png` | ไป cyolo เสมอ ตรวจ PNG signature |
| `kind` | `image` `code_review` `long_doc` | คำใบ้ให้ router (ไม่ใส่ = เดาจาก prompt) |
| `approve` | `true` | human gate |
| `progress` | `true` | สั่งให้เขียนความคืบหน้าลง `msgs/<id>__progress.md` (อัตโนมัติเมื่อ difficulty ≥ 3) |
| `cwd`, `timeout` | path, วินาที | ค่าเริ่มต้น cwd = `<run>/work` |
| review | `reviewer`, `criteria`, `max_rounds` (3), `review_difficulty` | `account` = ผู้ทำ |
| debate | `candidates` (`["yolo","cyolo"]`), `judge` (`any`), `judge_difficulty` | |
| best_of | `candidates` หรือ `n` + `candidate_account`, `criteria`, `judge` | |

ค่าที่ส่งต่อ (`{{id}}`): `task` = ผลที่ผ่าน `expect` · `debate` = คำตอบที่ผู้ตัดสินสรุป · `best_of` = ผลของผู้ชนะ · `review` = ฉบับที่ APPROVED

## รูปแบบ

### relay ข้าม CLI (A → B → C)

```json
{"defaults": {"difficulty": 1}, "nodes": [
 {"id": "a", "account": "cyolo", "prompt": "คำนวณ 7*6", "expect": "int"},
 {"id": "b", "account": "yolo",  "prompt": "นำ {{a}} บวก 100", "expect": "int"},
 {"id": "c", "account": "cyolo", "prompt": "นำ {{b}} คูณ 3", "expect": "int"}]}
```

ทุกทอดเขียน `msgs/a__b.md`, `msgs/b__c.md` · ผู้เรียกต้องตรวจทุกทอดด้วยการคำนวณอิสระเสมอ

### fan-out / fan-in

```json
{"nodes": [
 {"id": "p1", "account": "yolo1",  "prompt": "สรุปข้อดีของ X 3 ข้อ"},
 {"id": "p2", "account": "yolo2",  "prompt": "สรุปข้อเสียของ X 3 ข้อ"},
 {"id": "p3", "account": "cyolo1", "prompt": "ยกตัวอย่างการใช้ X 3 ข้อ"},
 {"id": "merge", "account": "any", "prompt": "รวมไฟล์ {{file:p1}} {{file:p2}} {{file:p3}} เป็นรายงานเดียว"}]}
```

### graph (DAG) ส่งข้อมูลยาวด้วยไฟล์

node ใดก็ได้มี `depends_on` หลายตัว งานที่พร้อมรันพร้อมกัน · ข้อมูลยาวส่งด้วย `{{file:id}}` แล้วสั่งให้ผู้รับอ่านไฟล์/ใช้เชลล์ประมวลผลเอง (เร็วและถูกกว่าการยัดข้อมูลลง prompt) · `{{id}}` ที่ยาวเกิน 2000 ตัวอักษรถูกปฏิเสธ

### review loop

```json
{"id": "fn", "type": "review", "account": "yolo", "reviewer": "cyolo", "max_rounds": 3,
 "prompt": "เขียนฟังก์ชัน Python add(a, b)", "criteria": "มี type hints และ docstring"}
```

ผู้ทำส่งร่าง → `out/fn.r1.md` → ผู้ตรวจอ่านไฟล์ ตอบ `APPROVED` หรือรายการที่ต้องแก้ → ผู้ทำแก้จากร่างเดิม … จนได้ `APPROVED` หรือครบ `max_rounds` (= งานล้ม) · บทสนทนาอยู่ใน `msgs/fn.worker__fn.reviewer.md` และกลับกัน

### board (แชร์ความรู้)

ทุก prompt ได้ข้อค้นพบบน `board.md` (≤ 3000 ตัวอักษรแทรกให้ ยาวกว่านั้นให้ path) และคำสั่งให้ใส่ `BOARD: <ข้อเท็จจริง>` ท้ายคำตอบ · scheduler ตัดบรรทัดนั้นออกจากผลแล้วต่อท้ายลง board พร้อมผู้เขียนและเวลา · คนเพิ่มเองได้: `team.py note "…" --run <id>`

### debate / ตรวจไขว้

```json
{"id": "q", "type": "debate", "candidates": ["yolo", "cyolo"], "judge": "yolo",
 "prompt": "มีจำนวนเฉพาะกี่ตัวที่น้อยกว่า 100"}
```

ผู้ตอบแต่ละฝั่งเขียน `out/q.c1.md`, `out/q.c2.md` · ผู้ตัดสิน (คนละบัญชีกับผู้ตอบถ้าได้) ตรวจเองแล้วตอบ JSON `{answer, winner, agree, reason}` → `out/q.judge.json`, `out/q.md`

### best-of-N + judge

```json
{"id": "slogan", "type": "best_of", "candidates": ["yolo1", "yolo2", "cyolo1"], "judge": "cyolo2",
 "criteria": "สั้นไม่เกิน 8 คำ จำง่าย ตรงกับสินค้า", "prompt": "คิดสโลแกนร้านกาแฟ 1 ประโยค"}
```

ผู้ตัดสินให้คะแนนทุกคน `{scores:[{candidate,score,note}], best, reason}` ค่าที่ส่งต่อคือผลของผู้ชนะ

### router (`account: "any"`)

| ชนิดงาน | ไปที่ | ตัดสินจาก |
|---|---|---|
| ภาพ | cyolo | `image`, `kind: image`, คำว่า สร้างภาพ/วาดภาพ/.png |
| ตรวจโค้ด | Codex | `kind: code_review`, คำว่า ตรวจโค้ด/review code/หาบั๊ก |
| เอกสารยาว | Claude | `kind: long_doc`, prompt > 4000 ตัวอักษร, อ้างไฟล์ > 20 KB, คำว่า สรุปเอกสาร |
| อื่น ๆ | ฝั่งที่โควตาเหลือมากกว่า | quota.json |

เหตุผลของ router อยู่ใน `state.json` (`nodes.<id>.route`) และ `board.md`

### human gate

```json
{"id": "deploy", "approve": true, "depends_on": ["build"], "prompt": "…"}
```

เมื่อพร้อมรัน → สถานะ `waiting_approval` + `msgs/deploy__human.md` บอกวิธีอนุมัติ · งานอื่นที่ไม่ขึ้นกับมันรันต่อ · อนุมัติ: `team.py approve deploy --run <id>` (หรือสร้าง `approvals/deploy.ok`) · รอเกิน `gate_timeout` (3600 s) → `blocked`
