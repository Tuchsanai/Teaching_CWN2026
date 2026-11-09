# รูปแบบกราฟทั้งหมด

ทุกกราฟคือ `{"goal": "...", "nodes": [ ... ]}`

## relay

```json
{"nodes":[
 {"id":"a","account":"yolo","difficulty":1,"expect":"number","prompt":"7*6 = เท่าไร"},
 {"id":"b","account":"cyolo","difficulty":1,"expect":"number","prompt":"{{a}}+100 = เท่าไร"},
 {"id":"c","account":"yolo","difficulty":1,"expect":"number","prompt":"{{b}}*3 = เท่าไร"}
]}
```

## fan-out / fan-in

งานย่อยไม่มี `depends_on` ต่อกัน งานรวมใส่ `depends_on` ทุกตัว อ้างผลด้วย `{{file:x}}`

## graph (DAG)

ใช้ `depends_on` กี่ตัวก็ได้ งานที่พร้อมรันพร้อมกันตามเพดาน `--max-total` / `--max-per-account`

## review loop

```json
{"id":"essay","type":"review","max_rounds":3,"difficulty":1,
 "worker":{"account":"yolo","prompt":"เขียนคำขวัญ 1 บรรทัดเรื่องการอ่าน"},
 "reviewer":{"account":"cyolo","prompt":"ตรวจว่าเป็นภาษาไทย 1 บรรทัด ตอบ APPROVED ถ้าผ่าน"}}
```

ผลล่าสุดอยู่ `out/essay.md` แต่ละรอบอยู่ `out/essay.r1.work.md` · `out/essay.r1.review.md` ไม่ APPROVED ภายใน `max_rounds` = ล้ม

## board

ใส่ `"board": true` ใน node หรือสั่งใน prompt ให้เขียนบรรทัด `BOARD: <ข้อเท็จจริง>` ระบบจะเพิ่มลง `board.md` พร้อมผู้เขียนและเวลา แล้วใส่ให้ agent ตัวถัดไปอัตโนมัติ เพิ่มเองได้ด้วย `team.py board --run <id> --add "..."`

## debate

```json
{"id":"d","type":"debate","prompt":"โจทย์","sides":["yolo","cyolo"],"judge":"yolo","difficulty":1}
```

ผล: `out/d__a.md`, `out/d__b.md`, คำตัดสิน `out/d.md` (`WINNER:` `ANSWER:` `REASON:`) ใช้ต่อเป็น `{{d}}`

## best-of-N + judge

```json
{"id":"b","type":"best_of","prompt":"โจทย์","accounts":["yolo1","yolo2","cyolo1"],"criteria":"ถูกต้องและกระชับ","judge":"yolo","difficulty":1}
```

ผู้ตัดสินตอบ `SCORES:` `WINNER: <เลข>` `REASON:` ผลชนะคัดลอกไป `out/b.winner.md`

## router และ failover

`account: any` → ภาพ/ตรวจโค้ด ไป Codex, เอกสารยาว ไป Claude, นอกนั้นบัญชีที่โควตาเหลือมากสุด งานที่ล้มเพราะโควตา/rate limit/ล็อกอินหมดอายุ ย้ายไปบัญชีอื่นฝั่งเดียวกันก่อน แล้วค่อยข้ามฝั่งถ้าไม่ผูก CLI งานที่ระบุบัญชีเองไม่ย้าย ทุกการย้ายบันทึกใน `state.json`, `board.md`, ledger (`event: worker_switch`)

จำลองความล้มเหลวโดยไม่เผาโควตา: `MA_SIMULATE_LIMIT=yolo1 team.py run ...` หรือ `--simulate-limit yolo1`

## human gate

ใส่ `"approve": true` งานจะรอ `team.py approve <run> <node>` (สร้าง `approvals/<node>.ok`) รอนานสุด `--gate-timeout` วินาที ครบแล้ว exit 3 แล้ว `--resume` ทำต่อได้

## งบและโควตา

`--worker-token-budget N` หยุดรับงานเมื่อบัญชีนั้นใช้ครบ (นับรวม cache) งานที่รันอยู่จบตามปกติ งานในคิวย้ายไปบัญชีอื่น `--quota-stop 80` หยุดรับงานเมื่อโควตาใช้เกิน % สถานะ: พร้อม / ใกล้หมด (≥60%) / หยุดรับงาน / ใช้ไม่ได้ `prefer` ใช้กำหนดบัญชีที่อยากให้รับงานก่อนโดยยังย้ายได้

## หัวหน้าทีม (`lead`)

หัวหน้าใช้คำสั่งเหล่านี้ระหว่างรอบ (อยู่ใน prompt ให้แล้ว): `dispatch`, `wait`, `assemble`, `checkpoint`, `finish`

งบหัวหน้าตรวจทันทีหลังทุก `dispatch`/`checkpoint`: เกินแล้วจะตอบ `BUDGET_EXCEEDED` ให้ checkpoint แล้วจบรอบ ลำดับผู้สืบทอด: `--succession` หรืออัตโนมัติ (บัญชีพร้อม โควตาเหลือมาก ฝั่งเดียวกันก่อน) `--forbid` ห้ามบางบัญชี หัวหน้าคนสุดท้ายไม่ถูกจำกัดงบเพื่อให้งานจบ
