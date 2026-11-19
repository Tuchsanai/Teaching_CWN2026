# REPORT · receiptdesk

**run:** `receiptdesk-20261119-115927` · `/workspace/.agent-team/receiptdesk-20261119-115927` · โจทย์: สร้างระบบ ReceiptDesk ตาม docs/REQUIREMENTS.md และ docs/DESIGN.md (ข้อมูลทดสอบ docs/TEST-DATA.md · ต้นฉบับอยู่ที่ /workspace/e2e_lab/receiptdesk/docs): ฝั่งเว็บรันด้วย docker compose (web Next.js + dispatcher + PostgreSQL + volume uploads) และฝั่ง AI บนเครื่อง GPU 2 ใบ (API gateway FastAPI + RabbitMQ คิว urgent/normal/dlq + GPU Worker 2 ตัว + NGINX + vLLM 2 ตัว) อ่านใบเสร็จเป็น 5 ช่อง ติดธงตาม BR-04/BR-05 ให้พนักงานตรวจแก้และยืนยัน งานด่วนแซงคิวแบบ 4:1 คิวเต็มแจ้งนาทีลองใหม่ ใบที่อ่านไม่ได้ไป Dead-letter Queue และมีโค้ด Training LoRA + Evaluation ของโมเดล Vision-Language

## ตารางบล็อก (แผน vs จริง)

| บล็อก | สกิล | บัญชีแผน | บัญชีจริง | นาทีแผน | นาทีจริง | tokens (ไม่รวม cache read) | ครั้ง | สถานะ | ไฟล์ผล |
|---|---|---|---|---|---|---|---|---|---|
| **B01** | ⚙️ cyolo | cyolo1(ทำ) | cyolo1(ทำ) | 2.27 | 0.83 | 39,038 | 1 | ok | ✅ docker-compose.yml |
| **B02** | ⚙️ cyolo | cyolo1(ทำ) | cyolo1(ทำ) | 5.67 | 3.38 | 45,473 | 1 | ok | ✅ web/db/schema.sql |
| B03 | 🔍 review | yolo2(ทำ), cyolo1(ตรวจ) | yolo2(ทำ), cyolo1(ตรวจ), yolo3(ทำ), yolo1(ทำ) | 10.84 | 6.53 | 842,669 | 12 | bad_output — ไม่ได้ APPROVED ภายใน max_rounds=3 | ✅ web/lib/rules.ts |
| **B04** | 🧠 yolo | yolo2(ทำ) | yolo1 | 18.34 | - | 0 | 0 | blocked — งานที่ต้องรอ B03 ล้ม/ไม่ผ่าน จึงไม่รัน | ❌ web/app/api/README.md |
| B05 | ⚙️ cyolo | cyolo1(ทำ) | cyolo1(ทำ) | 5.67 | 9.32 | 102,558 | 1 | ok | ✅ web/dispatcher/index.ts |
| B06 | ⚖️ debate | yolo2(ตอบ), cyolo1(ตอบ), yolo3(ตัดสิน) | cyolo1(ตอบ), yolo1(ตอบ), yolo2(ตัดสิน) | 4.57 | 11.45 | 320,224 | 3 | ok | ✅ docs/urgent-policy.md |
| B07 | ⚙️ cyolo | cyolo1(ทำ) | cyolo1(ทำ) | 5.67 | 3.73 | 64,952 | 1 | ok | ✅ ai/queue/topology.py |
| B08 | 🧠 yolo | yolo1(ทำ) | yolo2(ทำ) | 9.17 | 9.03 | 188,570 | 1 | ok | ✅ ai/gateway/main.py |
| B09 | 🧠 yolo | yolo1(ทำ) | yolo1(ทำ) | 9.17 | 10.37 | 184,726 | 1 | ok | ✅ ai/worker/worker.py |
| B10 | 🧠 yolo | yolo3(ทำ) | yolo1(ทำ) | 18.34 | 13.62 | 248,830 | 1 | ok | ✅ ai/train/train_lora.py |
| **B11** | 🧠 yolo | yolo2(ทำ) | yolo3 | 18.34 | - | 0 | 0 | blocked — งานที่ต้องรอ B04 ล้ม/ไม่ผ่าน จึงไม่รัน | ❌ web/app/pages.md |
| B12 | 🏆 best_of | cyolo1(ตอบ), yolo3(ตอบ), yolo1(ตัดสิน) | - | 11.42 | - | 0 | 0 | blocked — งานที่ต้องรอ B04 ล้ม/ไม่ผ่าน จึงไม่รัน | ❌ web/app/review/page.tsx |
| B13 | 🖼️ image | cyolo1(ทำ) | cyolo1(ทำ) | 0.55 | 0.55 | 21,044 | 1 | ok | ✅ web/public/logo.png |
| **B14** | 🧠 yolo | yolo2(ทำ) | yolo2 | 9.17 | - | 0 | 0 | blocked — งานที่ต้องรอ B11,B12 ล้ม/ไม่ผ่าน จึงไม่รัน | ❌ TEST.md |

- tokens รวมของบล็อก **2,058,084** = ผลรวมจาก ledger ของ run (23 การเรียก) **2,058,084** ✅ ตรงกัน
- การเรียกที่ไม่ใช่บล็อก (ตรวจความพร้อม ฯลฯ): 0 ครั้ง · 0 tokens (ไม่นับในตาราง)
- เวลารวม: แผน 63.5 นาที · จริง 45.6 นาที
- บล็อกเสร็จ 9/14

## ภาพ

![Gantt จริง](gantt-actual.png)

![แผน vs จริง](compare.png)

## ความต่างระหว่างแผนกับของจริง

- B03: แผน yolo2(ทำ), cyolo1(ตรวจ) → จริง yolo2(ทำ), cyolo1(ตรวจ), yolo3(ทำ), yolo1(ทำ)
- B04: แผน yolo2(ทำ) → จริง yolo1
- B06: แผน yolo2(ตอบ), cyolo1(ตอบ), yolo3(ตัดสิน) → จริง cyolo1(ตอบ), yolo1(ตอบ), yolo2(ตัดสิน)
- B08: แผน yolo1(ทำ) → จริง yolo2(ทำ)
- B10: แผน yolo3(ทำ) → จริง yolo1(ทำ)
- B11: แผน yolo2(ทำ) → จริง yolo3
- B12: แผน cyolo1(ตอบ), yolo3(ตอบ), yolo1(ตัดสิน) → จริง -
- (export ส่งเป็นฝั่ง yolo/cyolo ไม่ผูกบัญชี เพื่อให้ failover ของ agent-team ทำงาน → agent-team เลือกบัญชีในฝั่งเองตามโหลด/โควตา ดู references/run.md)

## ตัวปรับเวลา k (calib.json)

`/workspace/plans/calib.json`: {"cyolo": 0.2708, "debate": 1.2722, "yolo": 0.6604, "image": 0.0733}

k = นาทีจริง ÷ นาทีแผน (ก่อนคูณ k) แยกตามสกิล · `plan` ครั้งถัดไปคูณเวลาแต่ละบล็อกด้วย k ของสกิลนั้น
