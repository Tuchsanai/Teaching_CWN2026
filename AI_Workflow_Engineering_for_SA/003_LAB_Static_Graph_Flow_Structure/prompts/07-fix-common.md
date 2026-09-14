# ขั้นซ่อม — แก้ข้อบกพร่องเฉพาะ node

## บริบท
คุณเป็น System Analyst ของระบบครัวคุณยาย ใช้เอกสาร FR/NFR ที่ส่งต่อจาก LAB 002 เป็นหลักฐาน
working directory = AI_Workflow_Engineering_for_SA/003_LAB_Static_Graph_Flow_Structure/
เริ่ม session ใหม่ต่อ node ไม่ใช้ resume/continue ไม่เรียก agent เพิ่ม และไม่พึ่งบทสนทนาก่อนหน้า
ใช้เฉพาะ 18 แถว US ใน input/us-by-role.md; รหัสที่อ้างในเซลล์ไม่เพิ่มขอบเขต

## งาน
อ่าน work/fix-request.md ที่ผู้เรียนระบุ target node, path ผลเดิม, prompt เดิม, ข้อ FAIL และหลักฐาน FR/US
แก้เฉพาะข้อที่มีหลักฐานรองรับ เช่น JSON ไม่ตรง schema, FR อ้างไม่มีจริง, flow ไม่มี error path, payment state ผิด หรือสิทธิ์ขัดกัน
ถ้าข้อร้องขอไม่มีหลักฐาน ให้ตอบคำถามรอยืนยัน ไม่เดากฎเพื่อให้ผ่าน
ใช้ node_id/role เดิม คง flow_id ที่ใช้ได้ และอธิบาย mapping ถ้าต้องเปลี่ยน
แก้ทั้ง Markdown และ JSON ให้ตรงกัน ตรวจข้อที่เคยผ่านซ้ำและทำตาราง regression
Self-consistency ใช้ FR ตัดสิน ถ้า FR ขัด US หรือ FR ขัดกันให้ unresolved และหยุดส่งต่อ
ห้ามซ่อมผลของ node อื่นพร้อมกัน; ระบุ descendants ที่ต้องรันใหม่จาก graph เมื่อรับรุ่นแก้แล้ว

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
- work/fix-request.md
- input/fr-nfr-input.md
- input/us-by-role.md
- input/graph.json
- input/node-output.schema.json
- work/review-record.md
- ผลเดิมและ prompt เดิมตาม path ใน fix-request; ต้องอ่านทั้ง .md และ .json

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
เขียน work/repairs/<RUN_ID>/flow-<role>.md และ work/repairs/<RUN_ID>/flow-<role>.json ตาม schema
<RUN_ID> และ <role> มาจาก work/fix-request.md ต้องเป็นชื่อ path ที่ผู้เรียนกำหนดแล้ว ไม่ใช้ placeholder เป็นชื่อจริง
เขียน work/repairs/<RUN_ID>/fix-report.md ระบุข้อแก้ หลักฐาน regression และ descendants ที่หมดอายุ
ห้ามทับ work/flow-<role>.md หรือ work/flow-<role>.json เดิม; ให้นักศึกษาตรวจรุ่นแก้ก่อนเริ่มชุด graph ใหม่
ถ้า request หรือ path รุ่นใหม่ไม่ชัดเจน/มีผลเก่าอยู่ ให้หยุดพร้อมเหตุ ไม่เลือกเป้าหมายเอง
