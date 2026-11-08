# รันจริงและรายงาน (`export` · `run` · `report`)

## export → `graph.json`

| บล็อก | node ที่ได้ |
|---|---|
| `yolo` / `cyolo` | `{"account": "yolo"/"cyolo"}` task |
| `image` | `{"account": "cyolo", "image": "/workspace/plans/<แผน>/app/<output>.png", "kind": "image"}` |
| `review` | `{"type": "review", "account": <ฝั่งผู้ทำตามแผน>, "reviewer": <อีกฝั่ง>, "criteria": <done + ไฟล์มีจริง>, "max_rounds": 2}` |
| `debate` | `{"type": "debate", "candidates": ["yolo","cyolo"], "judge": <ฝั่งผู้ตัดสินตามแผน>}` |
| `best_of` | `{"type": "best_of", "candidates": [<ฝั่งของผู้ตอบตามแผน>], "judge": …, "criteria": <done>}` |

ทุก node: `id` = id บล็อก · `depends_on` · `difficulty` (+ `review_difficulty`/`judge_difficulty` เท่ากัน) · `cwd` = `/workspace/plans/<แผน>/app` (agent-team รองรับ `cwd` จริง: `do_call()` ใช้ `n["cwd"]` เป็นโฟลเดอร์ทำงาน) · `timeout` · `expect: text` · เรียง node ตามลำดับ topological (agent-team บังคับประกาศหลัง dependency)

prompt ของ node บอก: เป้าหมายรวม · บล็อกนี้ทำอะไร (`title` + `detail`) · path ไฟล์ผลใน `app/` · เกณฑ์ `done` · path ไฟล์ของบล็อกก่อนหน้า (ไม่ยัดเนื้อหาลง prompt · ผลของ debate/best_of ใช้ `{{file:id}}`) · ห้ามแก้ไฟล์ของบล็อกอื่นยกเว้นบล็อก `exclusive` · ตอบสั้นว่าเขียนไฟล์อะไร · ไม่ใช้ `{{id}}` กับผลยาว

ตรวจก่อนเขียนไฟล์ 2 ชั้น: ① ทุกฟิลด์ต้องอยู่ในตาราง "ฟิลด์ของ node" ของ `agent-team/references/graph.md` (อ่านจากไฟล์จริงทุกครั้ง) ② ส่งทุก node ให้ `team.add_node()` ของจริงตรวจ (id, type, account, image ฝั่ง, depends_on ประกาศก่อน, difficulty) โดยไม่สร้าง run

## ทำไมส่งเป็น "ฝั่ง" ไม่ใช่บัญชีตามแผน

agent-team ไม่มีช่องรับ "บัญชีแนะนำ": `add_node()` ล้างค่า `planned` ทุกครั้ง และ node ที่ระบุบัญชีเจาะจง (`yolo2`) เป็น **pinned = ไม่ย้ายอัตโนมัติ** (ล้มแล้วหยุด) ดังนั้น `export` ใช้ฝั่ง `yolo`/`cyolo` ตามบัญชีที่ KC-QUEST เลือก → failover ของ agent-team ยังทำงาน (โควตา/ล็อกอินล้ม → ย้ายบัญชีในฝั่งเดียวกัน) แลกกับการที่บัญชีจริงอาจไม่ตรงแผน (agent-team เลือกตามโหลด + โควตา/25 + โทเค็นใน run) · `run` ส่ง `--accounts` = บัญชีที่แผนพิจารณา (ที่พร้อมจริง) เพื่อจำกัดวงให้ตรงแผนมากที่สุด · **ความต่างระหว่างแผนกับของจริงคือสิ่งที่ `report` แสดง**

## run

`team.py run /workspace/plans/<แผน>/graph.json --run <แผน>-<YYYYmmdd-HHMMSS> --accounts <บัญชีในแผน> [--detach]` · run_id เก็บใน `/workspace/plans/<แผน>/run.json` (`run_id` + `history`) · ผลของ run อยู่ที่ `/workspace/.agent-team/<run_id>/` · difficulty → รุ่น/effort ตามบท 04 (agent-team เลือกให้) · agent-team **ไม่ retry งานที่เสียโทเค็น** (ล้ม = บล็อกที่ขึ้นด้วย `blocked`) · `--detach` แล้วดูสถานะ `team.py status --run <run_id>`

## report

อ่าน `<run>/state.json` (สถานะ · started/ended · events) + `<run>/ledger.jsonl` (เฉพาะ `event = call` · node ของบล็อก = `B03` หรือ `B03.w1` `B03.r1` `B03.c1` `B03.judge`)

| ไฟล์ | เนื้อหา |
|---|---|
| `gantt-actual.svg/png` | แถว = บัญชีที่เรียกจริง · แท่ง = ts_start–ts_end ของการเรียกในบล็อกนั้น (แยกบทบาท ทำ/ตรวจ/ตอบ/ตัดสิน) · บล็อกหลายบัญชีเชื่อมด้วยเส้นประ |
| `compare.svg/png` | ทุกบล็อก: ซ้าย = ช่วงตามแผน · ขวา = ช่วงจริง (แกนแยกเพราะสเกลต่างกันก่อนปรับ k) |
| `REPORT.md` | ตาราง บล็อก · สกิล · บัญชีแผน/จริง · นาทีแผน/จริง · tokens (in+out) · ครั้ง · สถานะ · ไฟล์ผล + ตรวจว่า tokens รวม = ledger · รายการบล็อกที่บัญชีต่างจากแผน · events (worker_switch ฯลฯ) |
| `/workspace/plans/calib.json` | `k[skill]` = นาทีจริง ÷ นาทีแผน (ก่อนคูณ k) · `history` (เขียนเมื่อ run จบแล้วเท่านั้น) |

tokens = `input_tokens + output_tokens` ต่อการเรียก (นิยามเดียวกับ `macore.tokens_used` ของ agent-team) · การเรียกตรวจความพร้อม (`_check`) ไม่นับเป็นของบล็อก แต่แสดงแยก · debate/best_of: `report` เขียนคำตอบที่ถูก/ชนะ (ค่า `value` ใน state) ลง `app/<output>` เป็นข้อความเท่านั้น (ไม่รันผลลัพธ์)
