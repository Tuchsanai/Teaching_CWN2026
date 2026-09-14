# ขั้น 3.3 — Node structure

## บริบท
คุณเป็น System Analyst ของระบบครัวคุณยาย ใช้เอกสาร FR/NFR ที่ส่งต่อจาก LAB 002 เป็นหลักฐาน
working directory = AI_Workflow_Engineering_for_SA/003_LAB_Static_Graph_Flow_Structure/
เริ่ม session ใหม่ต่อ node ไม่ใช้ resume/continue ไม่เรียก agent เพิ่ม และไม่พึ่งบทสนทนาก่อนหน้า
ใช้เฉพาะ 18 แถว US ใน input/us-by-role.md; รหัสที่อ้างในเซลล์ไม่เพิ่มขอบเขต

## งาน
อ่านผลทั้งสามบทบาทที่ผ่านเกณฑ์รับแล้ว สร้างโครงสร้างระบบเพื่อส่งให้ผู้ทำ UI
แยกตารางโมดูล: Module ID | หน้าที่ | Flow ID | FR/US | ขอบเขตและสิ่งที่ไม่ทราบ
แยกตารางข้อมูลและความสัมพันธ์: Entity | Key | Attributes | Relation | Cardinality | ข้อบังคับ | FR/US
แยกโต๊ะกับรอบโต๊ะ ออเดอร์กับรายการออเดอร์ ตัวเลือกและราคา ณ เวลาสั่ง วัตถุดิบและแมป เงินและ event ยืนยัน
cardinality หรือ field ที่ FR ไม่กำหนดเป็นข้อเสนอพร้อม assumption ไม่อ้างว่าเป็นข้อกำหนดต้นฉบับ
แยกตารางหน้าจอ: Screen ID | บทบาท | Actions | Flow ID | ข้อมูล/State ที่ใช้ | FR/US
แยกตารางสิทธิ์: Role | Resource/Action | Allow/Deny/Unknown | เหตุผล FR/US | วิธีตรวจ
รักษาการแยกจัดการเมนูกับแมปวัตถุดิบ และข้อห้ามเปิด URL ตาม US-25; Unknown ไม่เปลี่ยนเป็น Allow เอง
ไม่อ่าน work/state-machine.md เพราะ node นี้ขนานกับ state-machine; แสดงจุดที่ต้องให้ merge เทียบภายหลัง
เก็บ flows upstream พร้อม namespace และรายละเอียดโครงสร้างใน artifacts; ห้ามเพิ่มหน้ารายงานเต็มระบบจากเพียงข้อห้ามสิทธิ์

## ข้อจำกัด
ห้ามแต่ง FR ID, เกณฑ์ ตัวเลข หน่วย สูตร สัดส่วนทดสอบ หรือผลรัน; อ้าง FR ID ที่มีจริงจาก Input เท่านั้น
หมายเหตุ ก./ค./ช. ไม่พบนิยามในต้นฉบับ; ใช้เฉพาะข้อความในตารางตาม A-02 สถานะยังไม่ยืนยัน
คงถ้อยคำ US-20 ตรงตัวและ DI-04/A-03; การเสนอเชื่อม US-12/US-13 ต้องเปิดเผยว่ายังไม่ยืนยัน
แยกระดับออเดอร์/รายการ/ชำระเงิน/โต๊ะตาม DI-07; A-05 เป็นข้อเสนอแมปชื่อที่ยังไม่ยืนยัน
A-01 เป็นการจำลองสำหรับ Mock-up ไม่อ้างว่าพิสูจน์ระบบจริง; คง A-06 เรื่องขอบเขต
ถ้า FR ขัด US ให้รายงานข้อขัดแย้งพร้อมข้อความทั้งสองแหล่ง ห้ามแก้ FR ต้นทางเงียบ ๆ
ไม่ใช้เว็บเติมกฎ ไม่เปลี่ยน Input ไม่เขียนนอก work/ ไม่เขียน reference/ หรือ img/
ถ้า Input หาย มี INPUT_STATUS: MISSING หรือข้อขัดแย้งที่ทำให้ทำงานไม่ได้ ให้หยุดและตอบ BLOCKED พร้อมเหตุ
ถ้าผลปลายทางมีอยู่แล้ว ให้หยุดเพื่อให้นักศึกษาเก็บชุดเดิมก่อน ไม่เขียนทับหลักฐาน

## Input
- input/fr-nfr-input.md
- input/us-by-role.md
- work/input-source.md
- work/input-audit.md
- input/node-output.schema.json
- ../docs/case-study-source.md
- ../docs/data-issues.md
- work/flow-customer.md
- work/flow-customer.json
- work/flow-kitchen-front.md
- work/flow-kitchen-front.json
- work/flow-manager.md
- work/flow-manager.json
อ่าน input/graph.json เพื่อยืนยัน node_id และ dependency; ถ้า upstream ยังไม่รับรองใน work/review-record.md ให้หยุด
สำหรับสาม root ใช้ work/input-audit.md ที่ผู้เรียนตรวจและรับรองแล้ว ไม่ต้องรอ root อื่น

## รูปแบบ Output
เขียน JSON object จริงไม่ครอบ code fence ตาม input/node-output.schema.json และ Markdown ภาษาไทยที่มีข้อมูลตรงกัน
envelope ต้องมี node_id, role, sources, flows[], assumptions[], conflicts_found[]; artifacts ใช้เพิ่มรายละเอียดของ node ได้
sources เป็นรายการ path และ sha256 ที่คำนวณจากไฟล์จริง รวม FR/NFR, US, audit, provenance และผล upstream ที่อ่าน
ทุก flow มี flow_id, title, path_type (main/alternative/error), actors, us_refs, fr_refs, trigger, preconditions, steps, postconditions, completion_criteria, evidence
evidence แต่ละรายการมี fr_id, source_path = input/fr-nfr-input.md, locator หัวข้อ/บรรทัด และ quote ที่คัดจาก FR จริง
FR ทุกตัวที่ flow อ้างต้องมีหลักฐาน; ทุก US ต้องอยู่ในขอบเขตของ node หรือเป็นจุดส่งต่อที่ระบุชัด
Markdown มีตาราง Flow ID | เส้นทาง | ผู้ทำ | Trigger | ก่อนเริ่ม | ขั้นตอน | ผลหลังจบ | เกณฑ์รับ | FR/US | หลักฐาน
แยกทางเลือกที่ต้นฉบับไม่ระบุเป็น assumption สถานะยังไม่ยืนยัน ห้ามแต่ง error flow เป็นกฎที่อนุมัติแล้ว
assumptions ระบุ id, statement, status, impact; conflicts_found ระบุ id, topic, positions, fr_refs, evidence, decision, status, affected_nodes
evidence ของ conflict เป็น array ของข้อความ FR ที่คัดตรงตัวเท่านั้น; ใส่ locator และคำอธิบายในตาราง Markdown ไม่ผสมลงใน quote
ถ้าไม่พบข้อขัดแย้งให้ใช้ [] ไม่แต่งข้อขัดแย้งหรือหลักฐาน; ถ้าหลักฐานไม่พอให้ unresolved และอธิบายผลกระทบ
Markdown กับ JSON ต้องอ้างรหัสและการตัดสินตรงกัน; คำตอบสุดท้ายเป็นสรุป path และข้อค้าง ไม่ใช่เนื้อหาทดแทนไฟล์

## ตำแหน่งบันทึก
node_id = structure; role = structure
- work/flow-structure.md
- work/flow-structure.json
- work/structure.md
เขียนทุกไฟล์ปลายทางข้างต้นด้วยเครื่องมือไฟล์ แล้วแจ้งสิ่งที่สร้างและข้อค้างในคำตอบสุดท้าย
