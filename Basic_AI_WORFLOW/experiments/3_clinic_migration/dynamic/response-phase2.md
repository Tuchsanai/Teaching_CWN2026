## 1. บันทึกเวอร์ชันแผน

| เวอร์ชัน | เหตุผล | สิ่งที่เปลี่ยน | ผลกระทบ | Reuse |
|---|---|---|---|---|
| v1 | เริ่มงานตาม INPUT | สร้าง T1–T6 | ครอบคลุมผลงานเดิมทั้งหมด | ไม่มี |
| v2 | พบข้อมูลกำกวมที่ต้องตัดสินจากหลักฐาน | เพิ่ม T2a และปรับ Dependency ของ T3 | เพิ่ม review/quarantine ในการออกแบบและย้ายข้อมูล | เก็บ T1/T2 |
| v3 | NEW INFORMATION: ความยินยอมตาม PDPA และคนไข้จองเองผ่าน LINE OA | เพิ่มงานส่วนต่าง T7–T11; กำหนดทั้งสองข้อเป็น P0 | ปรับขอบเขต Findings, To-Be, Model, Mapping, Migration และ Roll-out | คง As-Is และใช้ผลตรวจ CSV/กติกาข้อมูลเดิมต่อ |

ใช้ Re-plan สะสม **2/3 ครั้ง** ไม่มีงาน DROPPED แก้งานเดิมเฉพาะส่วนที่ระบุใน Impact analysis ของ v3

## 2. บันทึกการทำงานของเฟสนี้

| ขั้นตอน | งาน | ผลลัพธ์ | การตัดสินของ EVALUATOR |
|---|---|---|---|
| 8 | T7 | ออกแบบ consent แยกวัตถุประสงค์ หลักฐาน เวอร์ชัน และการถอน; เพิ่ม review gates | แผนยังเหมาะสม: ใช่ |
| 9 | T8 | ปรับ LINE OA self-booking และ Data Model รองรับ consent/สิทธิ์เข้าถึง | แผนยังเหมาะสม: ใช่ |
| 10 | T9 | ปรับ Mapping, account linking และ Migration/rollback ที่ไม่คืนสิทธิ์ซึ่งถอนไปแล้ว | แผนยังเหมาะสม: ใช่ |
| 11 | T10 | ปรับ Gap/Roll-out พร้อม UAT 18 สถานการณ์; self-service เป็นข้อบังคับก่อนเปิดใช้ | แผนยังเหมาะสม: ใช่ |
| 12 | T11 | ตรวจเอกสาร Mermaid เชิงโครงสร้าง และการรักษาประวัติเดิม | แผนยังเหมาะสม: ใช่ — บรรลุเป้าหมายด้านเอกสาร |

## 3. ผลงานส่งมอบสุดท้าย

- [output.md](/root/workspace/CWN/Teaching/Basic_AI_WORFLOW/experiments/3_clinic_migration/dynamic/output.md) — ฉบับสมบูรณ์ที่ปรับในไฟล์เดิม ทุกส่วนที่เปลี่ยนมี `(updated: change request)`
- [trace.md](/root/workspace/CWN/Teaching/Basic_AI_WORFLOW/experiments/3_clinic_migration/dynamic/trace.md) — เพิ่ม Plan v3 และผลแต่ละงานท้ายไฟล์ โดยคงบันทึกเดิมครบ
- [response-phase2.md](/root/workspace/CWN/Teaching/Basic_AI_WORFLOW/experiments/3_clinic_migration/dynamic/response-phase2.md) — ข้อความตอบเฟสนี้

งานเฟสนี้ **DONE ทั้ง 5 งาน** รวมกับงานเดิมเป็น 12 งาน DONE ตรวจยืนยันว่า As-Is และประวัติ trace เดิมไม่เปลี่ยน

เอกสารกำหนดให้คนไข้จองเองจนได้รับเลขนัด และให้ consent มีหลักฐานตรวจย้อนหลัง/ถอนได้ ข้อมูลเดิมที่ไม่มีหลักฐานยังเป็น `unknown` การส่งมอบนี้ยังไม่ใช่การย้ายระบบหรือเก็บ consent จริง

ตรวจ Mermaid เชิงโครงสร้างแล้ว แต่ไม่ได้ render หรือใช้ parser; ไม่ใช้เครือข่ายหรือติดตั้งแพ็กเกจ การตรวจ PDPA ล่าสุดและทดสอบ LINE OA จริงถูกกำหนดเป็นเกณฑ์ก่อนเปิดใช้งาน