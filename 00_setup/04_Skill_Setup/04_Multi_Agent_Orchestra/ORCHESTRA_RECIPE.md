# ORCHESTRA_RECIPE — คุมวง multi-agent ข้ามหลายบัญชี (สร้าง BuildMart จากแผน DAG)

> ไฟล์นี้เขียนให้ **AI ที่เป็น orchestrator อ่านแล้วทำตามเอง** (ใช้ skill `yolo` · `cyolo` ที่ติดตั้งไว้แล้ว)
> นักศึกษาไม่ต้องรันคำสั่งเอง — แค่วางพรอมต์ใน readme
> "มือ" ของ orchestrator คือ `tools/orch.py` (อยู่ข้างไฟล์นี้ · อัลกอริทึม KC-QUEST ตัวเดียวกับ `tools/planner.py`) ทำงานที่ต้องแม่นและไม่ควรเปลือง token: วัดโควตา จับคู่งาน เปิด worker ดูโทเคน สลับบัญชี merge
> "สมอง" คือคุณ: อ่านโจทย์ + แผน เขียน prompt ของแต่ละงาน ตรวจผล ตัดสินใจเมื่อมีปัญหา

## 0) ค่าที่ผู้ใช้ระบุในพรอมต์ (ไม่ระบุ = ค่าเริ่มต้น)

| ค่า | ค่าเริ่มต้น | ความหมาย |
|---|---|---|
| `PROBLEM` | `BUILDMART.md` (ข้างไฟล์นี้) | requirement |
| `PLAN` | `out/buildmart` (ข้างไฟล์นี้) | แผน DAG จาก `tools/planner.py` (พรอมต์ ① ②) — มี `tasks.json` อยู่แล้ว **ใช้แผนนี้เป็นจุดเริ่ม ไม่ต้องแตกงานใหม่** · ไม่มีโฟลเดอร์นี้ = แตกงานเองตามข้อ 2 |
| `RUN` | `/root/runs/buildmart` | โฟลเดอร์ทำงานใน container (ไม่อยู่ใน `/workspace` เพราะ `node_modules` หลายชุดบน bind mount ของ Windows ช้ามาก) |
| `OUT` | `my_buildmart/` (ข้างไฟล์นี้) | ที่ export ผลลัพธ์กลับเข้า repo ตอนจบ |
| `MAX_AGENTS` | `12` | worker ที่รัน **พร้อมกัน** สูงสุด — **ไม่นับงาน image ของ cyolo** (image พร้อมกันได้อีก ≤ 5) |
| `BACKEND` | `mock` | `mock` = แชทบอทใช้ `mock-llm` ตอนสร้าง/ทดสอบ (ไม่เสียเงิน · ขั้น "เปิด AI บน Vast" เป็นพรอมต์แยกใน readme) · `vast` = ให้ทีมเช่า RTX 5090 เองระหว่างสร้าง (งาน VAST ในแผน) |
| `BUDGET` | ไม่จำกัด | งบต่อบัญชีเป็น % ของโควตาสัปดาห์ เช่น `yolo3=3` → เขียนลง `RUN/accounts.json` เป็น `{"yolo3":{"budget_pct":3}}` |
| `EXPIRES` | – | วันหมดแพลนของบัญชี เช่น `yolo2=2026-10-30` → `{"yolo2":{"plan_expires":"2026-10-30"}}` |

ตั้งตัวแปรก่อนทุกขั้น: `O="python3 <โฟลเดอร์ของไฟล์นี้>/tools/orch.py --run $RUN"`

**ห้ามเปิดดูโฟลเดอร์ `_solution/`** (เป็นเฉลยของผู้สอน) — ทีมต้องสร้างเองจาก requirement

## 1) สำรวจบัญชี + เลือกตัวคุมวง

```bash
$O init --problem <PROBLEM> --max-agents <MAX_AGENTS> --mirror <OUT>   # BOARD.md ถูก copy ไป <OUT>/ ให้ผู้ใช้เปิดดูสดใน JupyterLab
# ถ้ามี BUDGET / EXPIRES → เขียน $RUN/accounts.json ก่อนขั้นถัดไป
$O quota
```

- แสดงตาราง `quota` ให้ผู้ใช้ดู และอธิบายสั้น ๆ ว่าบัญชีไหน "ควรใช้ก่อน" (ใกล้รีเซ็ต/หมดอายุแต่ยังเหลือเยอะ) และบัญชีไหนเป็น orchestrator
- **orchestrator ต้องเป็นบัญชีที่ headroom มากที่สุด** (ฝั่ง yolo ได้แต้มต่อ +5 เพราะตอบเร็วกว่า) — ถ้า `whoami` ไม่ใช่บัญชีนั้นและ headroom ต่างกันเกิน 10% → รัน `$O handover --to <บัญชีนั้น>` แล้ว**จบงานของคุณ** บอกผู้ใช้ให้ดูความคืบหน้าที่ `<OUT>/BOARD.md`
- ห้ามเปิดดู `.credentials.json` / `auth.json` / ค่าใน `.env`

## 2) วางแผน — เริ่มจากแผน DAG

**มี `PLAN/tasks.json`** (ปกติ): copy เป็น `$RUN/tasks.json` แล้วเติมให้ครบสำหรับรันจริง — คง `id` `title` `size` `depends_on` `only` `exclusive` ตามแผนเดิม (ให้ตรงกับ DAG/Gantt ที่นักศึกษาเห็น) และเติม:
- `owns` ของทุกงาน (ไฟล์/โฟลเดอร์ที่เป็นเจ้าของ ไม่ทับกันมากที่สุด) · `status: "todo"`
- `BACKEND=mock` → งาน VAST (ถ้ามี) ใส่ `status: "done"` + `note: "ข้าม — เปิด AI บน Vast เป็นพรอมต์แยก"` และงานที่รอ VAST ไม่ต้องรอ
- ปรับได้เฉพาะเมื่อจำเป็น (เช่นงานใหญ่เกิน L ต้องแบ่ง) และจดเหตุผลใน `$RUN/NOTES.md`

**ไม่มีแผน**: แตกเอง 14–22 งาน ขนาด `S`/`M`/`L` (~0.6/1.5/3 ล้านโทเคน · งานต้องปิดได้ด้วยโทเคนที่บัญชีเหลือ) · งานแรก = โครงโปรเจกต์ + compose + DB + RabbitMQ · งานรูป `area: image` ให้ cyolo · งานสุดท้าย `exclusive: true`

จากนั้นเขียน:
1. `$RUN/tasks/_shared.md` — **สัญญากลาง** ที่ทุก worker ต้องยึด (ใส่ไว้หัว prompt ของทุกงาน): โครงโฟลเดอร์ + เจ้าของไฟล์ · service ใน compose + port · ตาราง DB (รวม `doc_chunks vector(384)`) · ชื่อคิว/exchange RabbitMQ + รูปแบบข้อความ JSON (ข้อ 4.2 ของ BUILDMART) · API + JSON · ฟังก์ชันคำนวณที่ใช้ร่วม · env · `data-testid` ทุกตัว · ล็อกเวอร์ชัน `@playwright/test` ให้ตรงกับ Chromium ที่มีใน container (`/ms-playwright` · ตรวจเองว่าเวอร์ชันไหนตรง) — เขียนให้ละเอียดพอที่งานขนานจะต่อกันได้โดยไม่ต้องคุยกัน
2. `$RUN/tasks/<ID>.md` ทีละงาน: เป้าหมาย · ไฟล์ที่เป็นของงานนี้ · ขั้นตอนย่อย (checklist) · **เกณฑ์ผ่าน** ที่ worker รันตรวจเองได้ (`npm run build`, `curl`, script ทดสอบคิว, Playwright ฯลฯ) อ้างเลขเคสใน BUILDMART ข้อ 7

กติกาของ prompt งาน:
- dev infra ที่ใช้ร่วมกันทั้งทีม (เปิดด้วย `$O infra up`): Postgres+pgvector (ฐานข้อมูลแยกต่องาน) · RabbitMQ (`AMQP_URL` ใน prompt ของ worker) · embedder (`EMBED_URL`) — worker ทดสอบคิว/RAG ได้โดยไม่ต้องรัน compose
- **ชื่อคิวต้องไม่ชนกันระหว่างงานที่ทดสอบพร้อมกัน** บน RabbitMQ dev กลาง → ให้แต่ละงานใช้ vhost หรือ prefix ชื่อคิวจาก env (`MQ_PREFIX=<id>_`) ตอนทดสอบ
- `docker compose` ทั้งระบบรันได้เฉพาะงาน `exclusive` — compose รันบน Docker **ใน container นี้** → เว็บอยู่ที่ `http://localhost:3400` · RabbitMQ UI `http://localhost:15672` · Playwright ใช้ Chromium ที่ `/ms-playwright` (ห้าม `npx playwright install`)
- งานทดสอบรวมสุดท้าย: `docker compose --profile mock --profile tts up -d --build` → รัน Playwright ทุกเคสในข้อ 7 ของ BUILDMART (วิดีโอช้าพอให้คนดูทัน · เคส T ต้องได้ MP4 มีเสียง) → `test-gifs/` `test-videos/` `TEST_REPORT.md` แล้ว commit ลง main

```bash
$O check        # ต้องได้ OK ก่อนไปต่อ
$O infra up     # Postgres+pgvector · RabbitMQ · embedder สำหรับ dev
```

## 3) คุมวง — loop จนเสร็จ

```bash
$O dispatch            # เปิด worker ให้งานที่พร้อม (เลือกบัญชีด้วย KC-QUEST + เช็คว่าโทเคนพอปิดงาน)
$O wait --timeout 540  # เฝ้าดูจนมี event (≤ 9 นาที) · ระหว่างนั้นเปิดงานใหม่ + สลับบัญชีให้อัตโนมัติ
```

ทำซ้ำ 2 คำสั่งนี้ แล้วตอบสนองตาม event ที่ได้ (JSON):

| event | orch.py ทำให้แล้ว | คุณ (สมอง) ทำ |
|---|---|---|
| `DONE` | merge `task/<ID>` เข้า main | ดู `git -C $RUN/app log --stat -1` สั้น ๆ · จดสรุป 1 บรรทัดลง `$RUN/NOTES.md` |
| `HANDOFF` | หยุด worker · commit WIP · เขียนบันทึกส่งต่อ · ให้บัญชีอื่นทำต่อ | แจ้งผู้ใช้ 1 บรรทัด (บัญชีไหน → ไหน เพราะอะไร) |
| `LIMIT_HANDOFF` | เหมือน HANDOFF (โควตาหมดจริงกลางงาน) | แจ้งผู้ใช้ · ถ้าเกิดบ่อย ลด `max_agents` ใน `$RUN/config.json` |
| `MERGE_CONFLICT` | คืนงานเข้าคิว พร้อมคำสั่งให้ `git merge main` แล้วแก้ conflict | ไม่ต้องทำอะไร (ถ้าเกิดซ้ำกับงานเดิม → แก้ `_shared.md`/แบ่งงานใหม่) |
| `INCOMPLETE` | คืนงานเข้าคิวให้ทำต่อ | อ่าน `tail` ของ log + progress · ถ้าติดเรื่องเดิมซ้ำ → `$O retry --task <ID> --note "<วิธีแก้>"` หรือแบ่งงาน |
| `FAILED` | หยุดลองแล้ว (ครบ 4 รอบ) | วิเคราะห์ แก้ prompt/แบ่งงานใหม่ใน `tasks.json` + `tasks/*.md` แล้ว `$O check` |
| `WARN_NO_TARGET` | – | ไม่มีบัญชีไหนรับต่อไหว → ปล่อยรันต่อ หรือแบ่งงานให้เล็กลง |
| `ORCH_LOW` | – | **บัญชีของคุณเหลือน้อย** → เขียนสถานะ/สิ่งที่ต้องทำต่อลง `$RUN/NOTES.md` แล้ว `$O handover` และ**จบงานทันที** |
| `STUCK` | – | ไม่มีงานรันและไม่มีงานที่พร้อม → ตรวจ dependency/งาน failed |
| `ALL_DONE` | – | ไปขั้นที่ 4 |

กติกา:
- **คุณไม่เขียนโค้ดเอง** (นอกจากแก้เล็กมาก) — มอบงานผ่าน `tasks/*.md` เท่านั้น ความจำของคุณคือ `NOTES.md` + `BOARD.md` (orchestrator คนถัดไปอ่านต่อได้)
- ทุกครั้งที่ตื่น ให้รายงานผู้ใช้สั้น ๆ: เสร็จกี่งาน/รันกี่ตัว/บัญชีที่ใช้ + event สำคัญ
- งานใช้เวลานานได้ ให้วน `dispatch`/`wait` ไปเรื่อย ๆ **ห้ามจบไปก่อนแล้วบอกว่าจะกลับมาดู**
- เพิ่มงานกลางทางได้ (เพิ่มใน `tasks.json` + `tasks/<ID>.md` แล้ว `$O check`)
- อย่าเปิด worker ซ้ำซ้อนด้วย `yoloN -p` เอง ให้ผ่าน `$O dispatch`/`$O start` เท่านั้น (orch.py ต้องรู้ทุก process เพื่อเฝ้าโทเคน)

## 4) ปิดงาน

```bash
$O report                                   # REPORT.md: งาน × บัญชี × โทเคน × การสลับ
$O export --to <OUT>                        # copy โค้ด + ผลทดสอบ (GIF/MP4/TEST_REPORT) + board/report กลับเข้า repo
$O infra down                               # ปิด dev infra
```

ตรวจว่า `<OUT>` ไม่มี `.env` / `.env.vast` / key ติดไป (ดูชื่อไฟล์ ห้ามพิมพ์ค่า) · เปิดเว็บทิ้งไว้แบบ mock ให้ผู้ใช้ลอง (`docker compose --profile mock up -d` ใน `$RUN/app`)

สรุปให้ผู้ใช้เป็นตารางภาษาไทย: งานทั้งหมด (บัญชีที่ทำ, รอบ, โทเคน) เทียบกับแผน Gantt (`PLAN/plan.json`: นาทีที่ประเมิน vs เวลาจริง) · การสลับบัญชี/orchestrator · ผลทดสอบ (ผ่านกี่เคสต่อกลุ่ม) · โฟลเดอร์ผลลัพธ์ `<OUT>/app`
