# PLAN · receiptdesk

**โจทย์:** สร้างระบบ ReceiptDesk ตาม docs/REQUIREMENTS.md และ docs/DESIGN.md (ข้อมูลทดสอบ docs/TEST-DATA.md · ต้นฉบับอยู่ที่ /workspace/e2e_lab/receiptdesk/docs): ฝั่งเว็บรันด้วย docker compose (web Next.js + dispatcher + PostgreSQL + volume uploads) และฝั่ง AI บนเครื่อง GPU 2 ใบ (API gateway FastAPI + RabbitMQ คิว urgent/normal/dlq + GPU Worker 2 ตัว + NGINX + vLLM 2 ตัว) อ่านใบเสร็จเป็น 5 ช่อง ติดธงตาม BR-04/BR-05 ให้พนักงานตรวจแก้และยืนยัน งานด่วนแซงคิวแบบ 4:1 คิวเต็มแจ้งนาทีลองใหม่ ใบที่อ่านไม่ได้ไป Dead-letter Queue และมีโค้ด Training LoRA + Evaluation ของโมเดล Vision-Language

วางแผนเมื่อ 19/11/2026 11:57 · MAX_AGENTS 4 · บัญชี yolo1, yolo2, yolo3 · ตัวปรับเวลา k {"cyolo": 0.3022, "yolo": 0.7335, "image": 0.0733, "*": 0.5077, "review": 0.5981}

> แผนนี้ยังไม่ได้รันจริง — KC-QUEST เลือกบัญชีจากโควตา แล้วจำลองเวลาตาม dependency

## 1) โควตาของแต่ละบัญชี

| บัญชี | แพลน | ใช้ไป 5 ชม. | ใช้ไปสัปดาห์ | headroom | รีเซ็ต/หมดอายุ (ชม.) | U | slot | ที่มา |
|---|---|---|---|---|---|---|---|---|
| yolo1 | default | 0% | 2% | **98%** | 162.0 | 0.129 | 3 | team.py quota |
| yolo2 | default | 0% | 18% | **82%** | 97.0 | 0.198 | 3 | team.py quota |
| yolo3 | default | 6% | 27% | **73%** | 121.0 | 0.165 | 3 | team.py quota |


## 2) DAG + สกิล + บัญชี

![DAG](dag.png)

**สายวิกฤต:** B01 → B02 → B04 → B11 → B14 · ยาว 9.6M tok

## 3) ตารางแจกงาน (เหตุผล KC-QUEST ทุกบล็อก)

| บล็อก | สกิล | ชื่อ | ขนาด · c | รอ | rank | บัญชี (บทบาท) | เริ่ม–จบ (นาที) | เหตุผล KC-QUEST |
|---|---|---|---|---|---|---|---|---|
| **B01** | ⚙️ cyolo | โครงโปรเจกต์ + docker compose | S · 0.6 | – | 9.6 | ❌ | unassigned | ไม่มีบัญชีชุดไหนปิดบล็อกนี้ได้ (แบ่งให้เล็กลง / เพิ่มบัญชี / ลด n) |
| **B02** | ⚙️ cyolo | ฐานข้อมูล 11 ตาราง + ข้อมูลตั้งต้น | M · 1.5 | B01 | 9 | ❌ | blocked | รอบล็อกที่ไม่มีบัญชีรับ |
| B03 | 🔍 review | โมดูลกติกา Business Rule | M · 1.5 | B01 | 9 | ❌ | blocked | รอบล็อกที่ไม่มีบัญชีรับ |
| **B04** | 🧠 yolo | สิทธิ์ 4 บทบาท + API ของเว็บ 23 เส้น | L · 3 | B02, B03 | 7.5 | ❌ | blocked | รอบล็อกที่ไม่มีบัญชีรับ |
| B06 | ⚖️ debate | ออกแบบกติกาการแซงคิวของงานด่วน | S · 0.6 | B01 | 6.6 | ❌ | blocked | รอบล็อกที่ไม่มีบัญชีรับ |
| B07 | ⚙️ cyolo | คิว RabbitMQ: Priority · Backpressure · DLQ | M · 1.5 | B06 | 6 | ❌ | blocked | รอบล็อกที่ไม่มีบัญชีรับ |
| B08 | 🧠 yolo | API gateway (FastAPI + SQLite) | M · 1.5 | B07 | 4.5 | ❌ | blocked | รอบล็อกที่ไม่มีบัญชีรับ |
| B10 | 🧠 yolo | โค้ด Training LoRA (1 และ 2 GPU) + Evaluation | L · 3 | B01 | 4.5 | ❌ | blocked | รอบล็อกที่ไม่มีบัญชีรับ |
| **B11** | 🧠 yolo | หน้าเว็บตามบทบาท (ยกเว้นหน้าตรวจแก้) | L · 3 | B04 | 4.5 | ❌ | blocked | รอบล็อกที่ไม่มีบัญชีรับ |
| B05 | ⚙️ cyolo | dispatcher (Outbox) + ตัวอ่านจำลอง | M · 1.5 | B02 | 3 | ❌ | blocked | รอบล็อกที่ไม่มีบัญชีรับ |
| B09 | 🧠 yolo | GPU Worker + NGINX ไป vLLM 2 ตัว | M · 1.5 | B07, B08 | 3 | ❌ | blocked | รอบล็อกที่ไม่มีบัญชีรับ |
| B12 | 🏆 best_of | หน้าจอตรวจแก้ใบเสร็จ | M · 1.5 | B04 | 3 | ❌ | blocked | รอบล็อกที่ไม่มีบัญชีรับ |
| B13 | 🖼️ image | โลโก้ ReceiptDesk | S · 0.6 | – | 2.1 | ❌ | unassigned | ไม่มีบัญชีชุดไหนปิดบล็อกนี้ได้ (แบ่งให้เล็กลง / เพิ่มบัญชี / ลด n) |
| **B14** | 🧠 yolo | รวมระบบ + ทดสอบเบื้องต้น | M · 1.5 | B05, B09, B10, B11, B12, B13 | 1.5 | ❌ | blocked | รอบล็อกที่ไม่มีบัญชีรับ |

## 4) Gantt แผน

![Gantt](gantt-plan.png)

## 5) รอบแจกงาน

| นาทีที่ | บล็อกที่เริ่ม |
|---|---|

## 6) สรุป

- บล็อก 14 · แจกได้ 0 · agent พร้อมกันสูงสุด 0/4
- เวลาประมาณ 0.0 นาที (แท่ง Gantt) · ไฟล์ผลของทีม: `/workspace/plans/receiptdesk-nocodex/app/`
- ⚠ บล็อกที่ไม่มีบัญชีรับ: B01, B13, B02, B03, B04, B05, B06, B07, B08, B09, B10, B11, B12, B14 → แบ่งให้เล็กลง / เพิ่มบัญชี / ลด n

ต่อไป: `dagplan.py export receiptdesk-nocodex` → `dagplan.py run receiptdesk-nocodex` → `dagplan.py report receiptdesk-nocodex`
