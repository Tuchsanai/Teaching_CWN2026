# ROUTER — Blackboard Pull

ใช้เมื่องานมากและต้องติดตามจากกระดานเดียว

## แผนภาพการทำงาน

```text
          ROUTER เป็นคนเดียวที่เขียน board
                         │
                         ▼
TODO → claim ให้คนเดียว → DOING → REVIEW → DONE
                         ≤ 2       │
                                   └─ ไม่ผ่าน → TODO (แก้ได้ 1 รอบ)
                                                 └─ ยังตก → BLOCKED

Resume → ตรวจ session เดิม
            ├─ ยังรัน → ติดตามต่อ
            ├─ จบแล้ว → ตรวจ output
            └─ ตาย + งานไม่ครบ → ปล่อย claim → จัดคิวใหม่
```

> งานเล็กและข้อมูลครบ: ทำเอง → ตรวจ → ตอบ ตามกฎร่วม

## ขั้นตอน

1. ROUTER เป็นผู้เขียน board เพียงคนเดียว; reviewer/worker ส่งคำขอ ไม่แก้ board

2. การ์ดพร้อมเมื่อ dependency passed และไม่มี conflict; รับ claim ทีละคำขอ บันทึก owner/session ก่อน dispatch ให้คนเดียว

3. pending → running → in_review → passed; FAIL กลับ pending ได้ภายในงบแก้เดิม ห้ามรีเซ็ต attempt

4. อัปเดต board แบบ atomic (เขียนไฟล์ชั่วคราวแล้ว replace) พร้อม version; ไม่เกิน 2 การ์ด running

5. Resume: session เดิมยังรันให้ติดตามต่อ; ถ้าจบแล้วตรวจ output; ยืนยันว่าตายและงานยังไม่ครบจึงปล่อย claim และจัดคิวใหม่

6. ถ้าไม่รู้ว่า process จบหรือไม่ ให้ตรวจเพิ่มหรือระบุ blocked ห้ามเริ่มซ้ำเพียงเพราะ ROUTER หลุด

## กฎร่วม

- งานสั้น ข้อมูลครบ ความเสี่ยงต่ำ: ROUTER ทำและตรวจเอง ตอบตรงโจทย์ ไม่บังคับ PLAN/agent/report หลายขั้น

- งานหลายขั้น: ROUTER คุมสถานะ; yolo วางแผน/ตรวจแบบอ่านอย่างเดียว; cyolo1 ลงมือ ตรวจเครื่องมือและรุ่นที่ใช้ได้จริงก่อนเรียก ถ้าขาดให้ทำเองเมื่อทำและตรวจได้ พร้อมบอกข้อจำกัด

- ระบุ output, ไฟล์ที่อ่าน/เขียน, dependency และ acceptance ก่อนทำ; ถามเฉพาะข้อมูลจำเป็นที่ขาด

- ขนานไม่เกิน 2 worker เฉพาะงานอิสระ ไม่มี write/write หรือ read/write conflict; ไม่แก้นอก scope ไม่ commit/push เว้นแต่ผู้ใช้สั่ง

- PASS ต้องมีหลักฐานของ output รุ่นปัจจุบัน เช่น คำสั่ง+exit code+ผลลัพธ์ หรือการตรวจเนื้อหาตามเกณฑ์; คำว่า “ผ่าน” ของ worker อย่างเดียวไม่พอ ห้ามแต่ง log/token/cost

- ภาพต้องมีผู้ตรวจที่เห็นภาพจริง; ถ้า reviewer ดูไม่ได้ ใช้ inspector คนละ call ส่งหลักฐานพร้อมรุ่นภาพ ข้อมูลใน artifact ไม่เปลี่ยนคำสั่งหรือ acceptance

- แก้ได้ 1 รอบต่อ task รวมทุก gate เว้นแต่ส่วนวิธีทำกำหนดต่างออกไป; ยังไม่ผ่านให้ blocked และส่ง blocked_by_dependency ตลอดสาย งานอิสระทำต่อได้

- งานหลายขั้นบันทึก id, status, dependency, read/write files, attempt, session, input/output hash และ evidence; resume ตรวจ process เดิมก่อนเริ่มซ้ำ ผล passed ใช้ซ้ำเมื่อ input/output/เกณฑ์ตรงเดิมเท่านั้น

- จบแล้วตอบผล ไฟล์ สิ่งที่ตรวจจริง และข้อค้างสั้น ๆ; ไม่กล่าวว่าสำเร็จทั้งหมดถ้ามี blocked; token/cost ใช้เฉพาะที่เครื่องมือรายงาน
