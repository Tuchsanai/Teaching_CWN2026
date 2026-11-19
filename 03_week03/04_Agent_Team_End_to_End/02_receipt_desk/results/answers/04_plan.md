วางแผน **receiptdesk** ด้วยสกิล dag-planner ใน container `multi-account` เสร็จแล้ว ยังไม่ได้รันทีมจริง

- แตกงานเป็น **14 บล็อก** ครบทุกหัวข้อที่โจทย์กำหนด สคริปต์ `dag` ตรวจผ่าน ไม่มี ERROR
- ใช้ครบ **6 สกิล**
  - B03 กติกา Business Rule ใช้ review: yolo2 ทำ cyolo1 ตรวจ (คนละ CLI) ตั้งรอบตรวจไว้ 3 รอบ
  - B06 กติกาแซงคิวของงานด่วนใช้ debate
  - B12 หน้าจอตรวจแก้ใบเสร็จใช้ best_of (n=2)
  - บล็อกอื่นใช้ yolo, cyolo หรือ image
- ตั้งเวลาทำงานต่อบล็อก (`timeout`) ตามขนาด: S 900 วินาที (15 นาที) · M 1800 วินาที (30 นาที) · L 2700 วินาที (45 นาที)
- จัดบัญชีด้วย KC-QUEST จากโควตาจริงของ **yolo1, yolo2, yolo3, cyolo1 เท่านั้น** agent พร้อมกันไม่เกิน 4 (`--max-agents 4`) และใช้ตัวปรับเวลา k จาก `calib.json`
- คัดลอกเอกสารไปไว้ในสำเนาทำงาน `/workspace/e2e_lab/receiptdesk/docs` แผนอยู่ที่ `/workspace/plans/receiptdesk`
- คัดลอกไฟล์มาไว้ที่ `./plan` แล้ว:
  - `blocks.json` (ไฟล์บล็อก)
  - `dag.png` (ภาพ DAG) และ `gantt-plan.png` (ภาพ Gantt)
  - `PLAN.md`, `plan.json`, `dag.json` (ไฟล์แผน)

| บล็อก | สกิล | ขนาด | รอบล็อกใด | บัญชี | เริ่ม–จบ (นาที) |
|---|---|---|---|---|---|
| B01 โครงโปรเจกต์ + docker compose | cyolo | S | – | cyolo1 | 0.0–2.3 |
| B02 ฐานข้อมูล 11 ตาราง + ข้อมูลตั้งต้น | cyolo | M | B01 | cyolo1 | 2.3–7.9 |
| B03 โมดูลกติกา Business Rule | review | M | B01 | yolo2 (ทำ) · cyolo1 (ตรวจ) | 6.8–17.7 |
| B04 สิทธิ์ 4 บทบาท + API ของเว็บ 23 เส้น | yolo | L | B02, B03 | yolo2 | 17.7–36.0 |
| B05 dispatcher (Outbox) + ตัวอ่านจำลอง | cyolo | M | B02 | cyolo1 | 7.9–13.6 |
| B06 ออกแบบกติกาการแซงคิวของงานด่วน | debate | S | B01 | yolo2, cyolo1 (ตอบ) · yolo3 (ตัดสิน) | 2.3–6.8 |
| B07 คิว RabbitMQ: Priority · Backpressure · DLQ | cyolo | M | B06 | cyolo1 | 6.8–12.5 |
| B08 API gateway (FastAPI + SQLite) | yolo | M | B07 | yolo1 | 13.6–22.8 |
| B09 GPU Worker + NGINX ไป vLLM 2 ตัว | yolo | M | B07, B08 | yolo1 | 22.8–31.9 |
| B10 โค้ด Training LoRA (1 และ 2 GPU) + Evaluation | yolo | L | B01 | yolo3 | 12.5–30.8 |
| B11 หน้าเว็บตามบทบาท | yolo | L | B04 | yolo2 | 36.0–54.4 |
| B12 หน้าจอตรวจแก้ใบเสร็จ | best_of | M | B04 | cyolo1, yolo3 (ตอบ) · yolo1 (ตัดสิน) | 36.0–47.4 |
| B13 โลโก้ ReceiptDesk | image | S | – | cyolo1 | 0.0–0.5 |
| B14 รวมระบบ + ทดสอบเบื้องต้น | yolo | M | B05, B09, B10, B11, B12, B13 | yolo2 | 54.4–63.5 |

**Critical Path:** B01 → B02 → B04 → B11 → B14 (ยาว 9.6 ล้านโทเคน)
**เวลารวมของแผน:** ≈ 63.5 นาที

เวลาที่ใช้: ~3 นาที
