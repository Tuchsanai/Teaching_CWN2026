# ขั้น 7.3 — ทดลองแบบ Dynamic Workflow
## ข้อกำหนดเปลี่ยน
โจทย์สมมติเพื่อทดลอง ไม่ใช่ต้นฉบับ: เปลี่ยนเกณฑ์ US-21 เฉพาะค่าเพดานที่ใช้ทดสอบจาก N=5 เป็น N=3 โดยคงหน้าต่าง 15 นาทีที่เริ่มนาที 00/15/30/45 และการทดสอบ 3 จาก 3 รอบเดิม; เมื่อถึง N ต้องแสดง “ครัวเต็ม รอประมาณ X นาที” ก่อนยืนยัน โดยไม่เพิ่มกฎปฏิเสธออเดอร์
## Input และการควบคุมการทดลอง
อ่าน work/change/baseline/manifest.md, fr-nfr-v2.md, flow-v2.md, ui-mockup-v2.html,
ui-scenarios.json ภายใต้ work/change/baseline/ และ work/change/conditions.md
แผนก่อนเปลี่ยนที่ใช้เป็น baseline ของทั้งสองวิธี:
{{PREV_PLAN}}
PHASE = {{PHASE}}; ROUND = {{ROUND}}
อ่านผลก่อนหน้าจาก work/change/dynamic/ ตาม dependency ของ PHASE เท่านั้น ไม่อ่านผล single
## งาน
PHASE=plan: สร้าง plan-round-<ROUND>.md มี task id, dependency, inputs, outputs, owner, state และ stop rule
แสดงแผนเดิม -> ข้อมูลใหม่ -> งานเพิ่ม/แยก/ยกเลิก/จัดลำดับ -> ชิ้นงานกระทบ -> ส่วนใช้ซ้ำ/ตรวจใหม่
รอบ 0 วางแผนจากข้อเปลี่ยน; รอบ 1/2 ใช้ผล evaluate ก่อนหน้าเป็น feedback และบันทึก diff แผน
PHASE=execute: อ่านแผนรอบนี้ แล้วผลิต fr-nfr-v3.md, flow-v3.md, ui-mockup-v3.html,
ui-scenarios-v3.json ใน work/change/dynamic/round-<ROUND>/ พร้อม execution.md ตาม dependency
PHASE=evaluate: อ่านแผน/ผล execute/ผลสคริปต์ tests.json ของรอบนี้ ตรวจข้อเปลี่ยนเดียวและ regression
เขียน evaluation-round-<ROUND>.md ระบุ COMPLETE, REPLAN หรือ STOP_WITH_GAPS พร้อมหลักฐาน
หนึ่งการเรียกทำหนึ่ง PHASE เท่านั้น; ผู้ทดลองเป็นผู้เรียก phase ถัดไป ไม่ให้โมเดลเรียกตัวเอง
REPLAN เมื่อพบข้อบกพร่องที่แก้ได้; หยุดเมื่อครบเกณฑ์ เพดานแก้ 2 รอบ งบหมด หรือข้อเดิมไม่คืบ
## Output
เขียนไฟล์ใหม่ภายใต้ work/change/dynamic/ ตาม PHASE/ROUND ไม่ทับแผน/ผลก่อนหน้า
รักษา AC อื่นและรหัสเดิม; เปลี่ยนแผน AI ไม่ใช่เปลี่ยนสถานะออเดอร์
นับทุกการเรียกของ plan/execute/evaluate/แก้ในต้นทุนรวม ไม่ซ่อนค่า orchestration

## กติกา
Working directory: AI_Workflow_Engineering_for_SA/007_LAB_Evaluation_Compare_Workflows/
เริ่ม session ใหม่ ใช้ input จากไฟล์ ไม่ resume ไม่เรียกผู้ช่วยหรือ CLI เพิ่ม
เขียนเฉพาะ work/ และ output รุ่นใหม่ หากมีไฟล์แล้วให้หยุดโดยคงหลักฐานเดิม
ห้ามแก้ reference/, img/, prompts/, ต้นทาง LAB อื่น หรือต้นฉบับข้อกำหนดร้าน
ใช้ข้อมูลจำลองและ placeholder เท่านั้น ไม่ใช้ข้อมูลบัญชีจริง
ตัวเลขเวลา/รอบ/โทเคนมาจาก log ที่มีจริง; ไม่มีให้เขียนไม่มีข้อมูล
ข้อประมาณต้องมีสูตร ที่มา และสมมติฐานแยกจากค่าจริง ไม่ใช้ 0 แทนข้อมูลที่ขาด
ห้ามสรุปว่า workflow ซับซ้อนกว่าดีกว่าเสมอ; ตัดสินตามขอบเขต คุณภาพ และทรัพยากร
