# PLAN · receiptdesk-skill

**โจทย์:** ReceiptDesk: เว็บรับใบเสร็จเป็นชุดให้สำนักงานบัญชี อ่านด้วย VLM (Qwen3-VL-2B + LoRA) บน GPU เช่า ผ่าน gateway + RabbitMQ (Priority/Backpressure/DLQ) ให้พนักงานตรวจแก้ยืนยัน ลูกค้าร้านดูสรุปรายเดือน ตาม docs/USER-STORIES.md docs/REQUIREMENTS.md docs/DESIGN.md docs/TEST-DATA.md

วางแผนเมื่อ 19/11/2026 18:11 · MAX_AGENTS 4 · บัญชี yolo1, yolo2, yolo3 · ตัวปรับเวลา k {"cyolo": 0.2708, "yolo": 0.6138, "image": 0.0733, "*": 0.4904, "review": 0.0726, "debate": 1.2722, "best_of": 0.6585}

> แผนนี้ยังไม่ได้รันจริง — KC-QUEST เลือกบัญชีจากโควตา แล้วจำลองเวลาตาม dependency

## 1) โควตาของแต่ละบัญชี

| บัญชี | แพลน | ใช้ไป 5 ชม. | ใช้ไปสัปดาห์ | headroom | รีเซ็ต/หมดอายุ (ชม.) | U | slot | ที่มา |
|---|---|---|---|---|---|---|---|---|
| yolo1 | default | 0% | 5% | **95%** | 155.8 | 0.133 | 3 | team.py quota |
| yolo2 | default | 0% | 18% | **82%** | 90.8 | 0.209 | 3 | team.py quota |
| yolo3 | default | 3% | 31% | **69%** | 114.8 | 0.173 | 3 | team.py quota |


## 2) DAG + สกิล + บัญชี

![DAG](dag.png)

**สายวิกฤต:** B01 → B02 → B04 → B11 → B14 · ยาว 9.6M tok

## 3) ตารางแจกงาน (เหตุผล KC-QUEST ทุกบล็อก)

| บล็อก | สกิล | ชื่อ | ขนาด · c | รอ | rank | บัญชี (บทบาท) | เริ่ม–จบ (นาที) | เหตุผล KC-QUEST |
|---|---|---|---|---|---|---|---|---|
| **B01** | ⚙️ cyolo | โครงโปรเจกต์ + compose | S · 0.6 | – | 9.6 | ❌ | unassigned | ไม่มีบัญชีชุดไหนปิดบล็อกนี้ได้ (แบ่งให้เล็กลง / เพิ่มบัญชี / ลด n) |
| **B02** | ⚙️ cyolo | ฐานข้อมูล + seed + reset | M · 1.5 | B01 | 9 | ❌ | blocked | รอบล็อกที่ไม่มีบัญชีรับ |
| **B04** | 🔍 review | กติกา BR + สิทธิ์ + API เว็บ | L · 3 | B02 | 7.5 | ❌ | blocked | รอบล็อกที่ไม่มีบัญชีรับ |
| B03 | ⚖️ debate | ตัดสินกติกาแซงคิว | S · 0.6 | B01 | 6.6 | ❌ | blocked | รอบล็อกที่ไม่มีบัญชีรับ |
| B05 | 🧠 yolo | คิว Priority · Backpressure · DLQ | M · 1.5 | B03 | 6 | ❌ | blocked | รอบล็อกที่ไม่มีบัญชีรับ |
| B07 | ⚙️ cyolo | Gateway บน GPU | M · 1.5 | B05 | 4.5 | ❌ | blocked | รอบล็อกที่ไม่มีบัญชีรับ |
| B09 | 🧠 yolo | Training LoRA 1 และ N GPU | M · 1.5 | B01 | 4.5 | ❌ | blocked | รอบล็อกที่ไม่มีบัญชีรับ |
| **B11** | 🧠 yolo | หน้าเว็บ อัปโหลด สถานะ สรุป | L · 3 | B04 | 4.5 | ❌ | blocked | รอบล็อกที่ไม่มีบัญชีรับ |
| B06 | ⚙️ cyolo | Dispatcher + ตัวอ่านจำลอง | M · 1.5 | B02, B05 | 3 | ❌ | blocked | รอบล็อกที่ไม่มีบัญชีรับ |
| B08 | ⚙️ cyolo | GPU Worker + NGINX + vLLM | M · 1.5 | B07 | 3 | ❌ | blocked | รอบล็อกที่ไม่มีบัญชีรับ |
| B10 | ⚙️ cyolo | Evaluation + ตรึง Threshold | M · 1.5 | B09 | 3 | ❌ | blocked | รอบล็อกที่ไม่มีบัญชีรับ |
| B12 | 🏆 best_of | หน้าจอตรวจแก้ใบเสร็จ | M · 1.5 | B04 | 3 | ❌ | blocked | รอบล็อกที่ไม่มีบัญชีรับ |
| B13 | 🖼️ image | โลโก้ ReceiptDesk | S · 0.6 | – | 2.1 | ❌ | unassigned | ไม่มีบัญชีชุดไหนปิดบล็อกนี้ได้ (แบ่งให้เล็กลง / เพิ่มบัญชี / ลด n) |
| **B14** | 🧠 yolo | รวมระบบ + ทดสอบ | M · 1.5 | B06, B08, B10, B11, B12, B13 | 1.5 | ❌ | blocked | รอบล็อกที่ไม่มีบัญชีรับ |

## 4) Gantt แผน

![Gantt](gantt-plan.png)

## 5) รอบแจกงาน

| นาทีที่ | บล็อกที่เริ่ม |
|---|---|

## 6) สรุป

- บล็อก 14 · แจกได้ 0 · agent พร้อมกันสูงสุด 0/4
- เวลาประมาณ 0.0 นาที (แท่ง Gantt) · ไฟล์ผลของทีม: `/workspace/plans/receiptdesk-skill-nocodex/app/`
- ⚠ บล็อกที่ไม่มีบัญชีรับ: B01, B13, B02, B03, B04, B05, B06, B07, B08, B09, B10, B11, B12, B14 → แบ่งให้เล็กลง / เพิ่มบัญชี / ลด n

ต่อไป: `dagplan.py export receiptdesk-skill-nocodex` → `dagplan.py run receiptdesk-skill-nocodex` → `dagplan.py report receiptdesk-skill-nocodex`
