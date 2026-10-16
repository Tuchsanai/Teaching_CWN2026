# ORCHESTRA_RECIPE — คุมวง multi-agent ข้ามหลายบัญชี

> ไฟล์นี้เขียนให้ **AI ที่เป็น orchestrator อ่านแล้วทำตามเอง** (ใช้ skill `yolo` · `cyolo` · `vastai` ที่ติดตั้งไว้แล้ว)
> นักศึกษาไม่ต้องรันคำสั่งเอง — แค่วางพรอมต์ใน README
> "มือ" ของ orchestrator คือ `tools/orch.py` (อยู่ข้างไฟล์นี้) ทำงานที่ต้องแม่นและไม่ควรเปลือง token: วัดโควตา จับคู่งาน เปิด worker ดูโทเคน สลับบัญชี merge
> "สมอง" คือคุณ: อ่านโจทย์ แตกงาน เขียน prompt ของแต่ละงาน ตรวจผล ตัดสินใจเมื่อมีปัญหา

## 0) ค่าที่ผู้ใช้ระบุในพรอมต์ (ไม่ระบุ = ค่าเริ่มต้น)

| ค่า | ค่าเริ่มต้น | ความหมาย |
|---|---|---|
| `PROBLEM` | `BUILDMART.md` (ข้างไฟล์นี้) | โจทย์ |
| `RUN` | `/root/runs/buildmart` | โฟลเดอร์ทำงานใน container (ไม่อยู่ใน `/workspace` เพราะ `node_modules` หลายชุดบน bind mount ของ Windows ช้ามาก) |
| `OUT` | `my_buildmart/` (ข้างไฟล์นี้) | ที่ export ผลลัพธ์กลับเข้า repo ตอนจบ |
| `MAX_AGENTS` | `12` | worker ที่รัน **พร้อมกัน** สูงสุด — **ไม่นับงาน image ของ cyolo** (image พร้อมกันได้อีก ≤ 5) |
| `BACKEND` | `vast` | `vast` = เช่า RTX 5090 เปิด Qwen ตาม `NINFER_RECIPE.md` · `mock` = ไม่เช่า GPU |
| `BUDGET` | ไม่จำกัด | งบต่อบัญชีเป็น % ของโควตาสัปดาห์ เช่น `yolo3=3` → เขียนลง `RUN/accounts.json` เป็น `{"yolo3":{"budget_pct":3}}` |
| `EXPIRES` | – | วันหมดแพลนของบัญชี เช่น `yolo2=2026-10-20` → `{"yolo2":{"plan_expires":"2026-10-20"}}` |

ตั้งตัวแปรก่อนทุกขั้น: `O="python3 <โฟลเดอร์ของไฟล์นี้>/tools/orch.py --run $RUN"`

## 1) สำรวจบัญชี + เลือกตัวคุมวง

```bash
$O init --problem <PROBLEM> --max-agents <MAX_AGENTS> --mirror <OUT>   # BOARD.md ถูก copy ไป <OUT>/ ให้ผู้ใช้เปิดดูสดใน JupyterLab
# ถ้ามี BUDGET / EXPIRES → เขียน $RUN/accounts.json ก่อนขั้นถัดไป
$O quota
```

- แสดงตาราง `quota` ให้ผู้ใช้ดู และอธิบายสั้น ๆ ว่าบัญชีไหน "ควรใช้ก่อน" (โควตาสัปดาห์ที่จะสูญเปล่าต่อชั่วโมงมากสุด = ใกล้รีเซ็ต/หมดอายุแต่ยังเหลือเยอะ) และบัญชีไหนเป็น orchestrator
- **orchestrator ต้องเป็นบัญชีที่ headroom มากที่สุด** (ฝั่ง yolo ได้แต้มต่อ +5 เพราะตอบเร็วกว่า) — ถ้า `whoami` ไม่ใช่บัญชีนั้นและ headroom ต่างกันเกิน 10% → รัน `$O handover --to <บัญชีนั้น>` แล้ว**จบงานของคุณ** บอกผู้ใช้ให้ดูความคืบหน้าที่ `<OUT>/BOARD.md`
- ห้ามเปิดดู `.credentials.json` / `auth.json` / ค่าใน `.env`

## 2) วางแผน — แตกโจทย์เป็นงานย่อย

อ่าน `$RUN/PROBLEM.md` แล้วเขียน 3 อย่าง:

1. `$RUN/tasks/_shared.md` — **สัญญากลาง** ที่ทุก worker ต้องยึด (ใส่ไว้หัว prompt ของทุกงาน): โครงสร้างโฟลเดอร์ ชื่อตาราง/คอลัมน์ ชื่อ API + รูปแบบ JSON ฟังก์ชันคำนวณที่ใช้ร่วม ชื่อ env · เขียนให้ละเอียดพอที่งานขนานจะต่อกันได้โดยไม่ต้องคุยกัน
2. `$RUN/tasks/<ID>.md` ทีละงาน: เป้าหมาย · ไฟล์ที่เป็นของงานนี้ · ขั้นตอนย่อย (เป็น checklist) · **เกณฑ์ผ่าน** ที่ worker รันตรวจเองได้ (`npm run build`, `curl`, Playwright ฯลฯ)
3. `$RUN/tasks.json`:

```json
{"tasks": [
  {"id": "T01", "title": "scaffold + DB schema/seed + mock-llm", "area": "backend", "size": "M",
   "depends_on": [], "owns": ["package.json", "db/", "mock-llm/", "docker-compose.yml"], "status": "todo"},
  {"id": "VAST", "title": "เช่า RTX 5090 + เปิด Qwen", "area": "infra", "size": "M",
   "depends_on": [], "only": "yolo", "no_handoff": true, "status": "todo"},
  {"id": "IMG1", "title": "รูปหมวดสินค้า 11 รูป", "area": "image", "size": "S", "depends_on": ["T01"], "status": "todo"},
  {"id": "T14", "title": "ทดสอบรวม + GIF + TEST_REPORT", "area": "test", "size": "L",
   "depends_on": ["..."], "exclusive": true, "status": "todo"}
]}
```

กติกาการแตกงาน:
- **10–18 งาน** ขนาด `S`/`M`/`L` (ประเมินโทเคน ~0.6/1.5/3 ล้าน) — งานใหญ่กว่า `L` ต้องแบ่ง เพราะ**งานต้องปิดได้ด้วยโทเคนที่บัญชีเหลือ** (`$O check` จะเตือนงานที่ไม่มีบัญชีไหนรับไหว)
- `T01` = โครงโปรเจกต์ + compose + schema/seed + mock-llm + layout หลัก — งานอื่นเกือบทั้งหมด depends on `T01`
- แยก frontend ตามหน้า/ฟีเจอร์ แยก backend ตามกลุ่ม API แยกแชทบอท (backend tag/คำนวณ, UI widget) แยกชุดทดสอบเว็บ/แชทบอท — ให้ `owns` ไม่ทับกันมากที่สุด (ลด merge conflict)
- `BACKEND=vast` → มีงาน `VAST` (`only: yolo`, `no_handoff: true`, ไม่มี dependency เริ่มได้ทันที) prompt: *"ใช้ skill vastai ทำตาม `<โฟลเดอร์ของไฟล์นี้>/NINFER_RECIPE.md` MODEL=qwen3.8-27b-nvfp4 LABEL=bm-ninfer-5090 MAX_DPH=1.20 OUT_ENV=$RUN/.env.vast — ห้ามลบเครื่องเมื่อเสร็จ"* · งานทดสอบด้วย AI จริง depends on `VAST`
- มีงาน `area: image` ได้ (เช่น รูปหมวดสินค้า/แบนเนอร์) → รันด้วย cyolo และ**ไม่นับ**ในเพดาน `MAX_AGENTS`
- งานสุดท้าย `exclusive: true` (รันคนเดียว): `docker compose up` ทั้งระบบ รัน Playwright ทุกเคสทั้ง `MODE=mock` และ `MODE=ai` (ถ้ามี `$RUN/.env.vast`) ทำ GIF + `TEST_REPORT.md` แล้ว commit ลง main
- prompt ของงานทดสอบต้องบอก: Playwright รันใน container นี้ เปิดเว็บที่ `http://host.docker.internal:3400` (compose รันบน Docker ของเครื่อง host ผ่าน docker.sock) · Chromium อยู่ที่ `/ms-playwright`

```bash
$O check        # ต้องได้ OK ก่อนไปต่อ
$O infra up     # Postgres กลางสำหรับ dev (แต่ละงานได้ฐานข้อมูลของตัวเอง)
```

## 3) คุมวง — loop จนเสร็จ

```bash
$O dispatch            # เปิด worker ให้งานที่พร้อม (เลือกบัญชีตามคะแนน + เช็คว่าโทเคนพอปิดงาน)
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
- ทุกครั้งที่ตื่น ให้รายงานผู้ใช้สั้น ๆ: เสร็จกี่งาน/รันกี่ตัว/บัญชีที่ใช้ + event สำคัญ (อ่าน `$RUN/BOARD.md` · ผู้ใช้เปิดดูสดได้ที่ `<OUT>/BOARD.md`)
- เพิ่มงานกลางทางได้ (เพิ่มใน `tasks.json` + `tasks/<ID>.md` แล้ว `$O check`)
- อย่าเปิด worker ซ้ำซ้อนด้วย `yoloN -p` เอง ให้ผ่าน `$O dispatch`/`$O start` เท่านั้น (orch.py ต้องรู้ทุก process เพื่อเฝ้าโทเคน)

## 4) ปิดงาน

```bash
$O report                                   # REPORT.md: งาน × บัญชี × โทเคน × การสลับ
$O export --to <OUT>                        # copy โค้ด + ผลทดสอบ + board/report กลับเข้า repo
```

สรุปให้ผู้ใช้เป็นตารางภาษาไทย: งานทั้งหมด (บัญชีที่ทำ, รอบ, โทเคน) · การสลับบัญชี/orchestrator · ผลทดสอบ (ผ่านกี่เคส ทั้ง mock/ai) · URL เว็บ `http://localhost:3400` · เครื่อง Vast ที่ยังเปิดอยู่ (**ไม่ลบเอง** ผู้ใช้จะสั่งลบในขั้นปิดเครื่อง)
