# REPORT · sitesafe

**run:** `sitesafe-20261119-062515` · `/workspace/.agent-team/sitesafe-20261119-062515` · โจทย์: สร้างระบบ SiteSafe Inspect ตาม docs/REQUIREMENTS.md และ docs/DESIGN.md (ข้อมูลทดสอบอยู่ที่ docs/TEST-DATA.md): ฝั่งเว็บรันด้วย docker compose (web Next.js + dispatcher + PostgreSQL + volume photos + mock-gateway) และฝั่ง AI บนเครื่อง GPU 1 ใบ (API gateway + RabbitMQ + GPU Worker YOLO) หัวหน้างานอัปโหลดรูปหน้างาน ระบบนับคนไม่ใส่หมวก (H) และคนไม่ใส่เสื้อสะท้อนแสง (V) ตัดสินผล ผ่าน / เตือน / ไม่ผ่าน ตาม BR-01 ถึง BR-07 แก้ผลได้พร้อมร่องรอย มีรายงานรายวันต่อไซต์ และรูปห้ามหาย

## ตารางบล็อก (แผน vs จริง)

| บล็อก | สกิล | บัญชีแผน | บัญชีจริง | นาทีแผน | นาทีจริง | tokens (ไม่รวม cache read) | ครั้ง | สถานะ | ไฟล์ผล |
|---|---|---|---|---|---|---|---|---|---|
| **B01** | ⚙️ cyolo | cyolo1(ทำ) | cyolo1(ทำ) | 7.50 | 0.77 | 36,019 | 1 | ok | ✅ docker-compose.yml |
| **B02** | ⚙️ cyolo | cyolo1(ทำ) | cyolo1(ทำ) | 18.75 | 3.03 | 39,832 | 1 | ok | ✅ web/db/schema.sql |
| **B03** | 🔍 review | yolo2(ทำ), cyolo1(ตรวจ) | yolo3(ทำ), cyolo1(ตรวจ), yolo2(ทำ) | 36.25 | 35.38 | 803,710 | 4 | bad_output — ไม่ได้ APPROVED ภายใน max_rounds=2 | ✅ web/lib/rules.ts |
| B04 | ⚙️ cyolo | cyolo1(ทำ) | cyolo1 | 18.75 | - | 0 | 0 | blocked — งานที่ต้องรอ B03 ล้ม/ไม่ผ่าน จึงไม่รัน | ❌ web/dispatcher/index.ts |
| B05 | 🧠 yolo | yolo2(ทำ) | yolo2(ทำ) | 25.00 | 19.48 | 276,396 | 1 | ok | ✅ ai/gateway/main.py |
| B06 | ⚙️ cyolo | cyolo1(ทำ) | cyolo1(ทำ) | 18.75 | 5.75 | 67,811 | 1 | ok | ✅ ai/worker/worker.py |
| B07 | ⚙️ cyolo | cyolo1(ทำ) | cyolo1(ทำ) | 18.75 | 5.88 | 92,969 | 1 | ok | ✅ ai/train/evaluate.py |
| **B08** | 🧠 yolo | yolo2(ทำ) | yolo2 | 25.00 | - | 0 | 0 | blocked — งานที่ต้องรอ B03 ล้ม/ไม่ผ่าน จึงไม่รัน | ❌ web/app/login/page.tsx |
| B09 | 🖼️ image | cyolo1(ทำ) | cyolo1(ทำ) | 7.50 | 0.55 | 16,971 | 1 | ok | ✅ logo.png |
| **B10** | 🧠 yolo | yolo2(ทำ) | yolo3 | 25.00 | - | 0 | 0 | blocked — งานที่ต้องรอ B04,B08 ล้ม/ไม่ผ่าน จึงไม่รัน | ❌ TEST.md |

- tokens รวมของบล็อก **1,333,708** = ผลรวมจาก ledger ของ run (10 การเรียก) **1,333,708** ✅ ตรงกัน
- การเรียกที่ไม่ใช่บล็อก (ตรวจความพร้อม ฯลฯ): 0 ครั้ง · 0 tokens (ไม่นับในตาราง)
- เวลารวม: แผน 112.5 นาที · จริง 39.2 นาที
- บล็อกเสร็จ 6/10

## ภาพ

![Gantt จริง](gantt-actual.png)

![แผน vs จริง](compare.png)

## ความต่างระหว่างแผนกับของจริง

- B03: แผน yolo2(ทำ), cyolo1(ตรวจ) → จริง yolo3(ทำ), cyolo1(ตรวจ), yolo2(ทำ)
- B10: แผน yolo2(ทำ) → จริง yolo3
- (export ส่งเป็นฝั่ง yolo/cyolo ไม่ผูกบัญชี เพื่อให้ failover ของ agent-team ทำงาน → agent-team เลือกบัญชีในฝั่งเองตามโหลด/โควตา ดู references/run.md)

## ตัวปรับเวลา k (calib.json)

`/workspace/plans/calib.json`: {"cyolo": 0.2421, "yolo": 0.7793, "image": 0.0733}

k = นาทีจริง ÷ นาทีแผน (ก่อนคูณ k) แยกตามสกิล · `plan` ครั้งถัดไปคูณเวลาแต่ละบล็อกด้วย k ของสกิลนั้น
