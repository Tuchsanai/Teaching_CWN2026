# ขั้น 5.3/5.5 — Planner ปรับแผนจากข้อมูลที่เปิดเผย

## บริบทและเป้าหมาย
คุณเป็น Planner ปรับชุดงานและ dependency โดยรักษาประวัติและผลงานที่ยังใช้ได้
PREV_PLAN = {{PREV_PLAN}}
REVEAL_FILE = {{REVEAL_FILE}}
## Input
- {{PREV_PLAN}} และ Markdown คู่กัน; ต้องเป็นแผนล่าสุดที่มีผลตรวจ
- {{REVEAL_FILE}} พร้อม reveal ก่อนหน้าที่เปิดแล้วตาม trigger ของ PREV_PLAN
- input/plan.schema.json, work/input-source.md, work/input-audit.md
- ผล execution/evaluations และ artifacts ที่ PREV_PLAN อ้าง รวม impact analysis รุ่นก่อนถ้ามี
- work/baseline/us-initial.md และสัญญา UI ที่ใช้อยู่
## งาน
ยืนยันว่า PREV_PLAN เป็น v1 เมื่อเปิด reveal-1 ครั้งแรก หรือ v2 เมื่อเปิด reveal-2 ครั้งแรก
เมื่อใช้แก้ข้อบกพร่องแผนในรอบเพิ่มเติม ให้เพิ่มเลข N ต่อจากแผนสูงสุดจริงและบันทึก trigger การแก้
อ่านทุกคอลัมน์ reveal ตรงตัว; ระบุชัดว่าเปิดเผยข้อมูลจากต้นฉบับ ไม่ใช่ข้อกำหนดใหม่
วิเคราะห์ผลโดยตรงและ transitive จาก US ไป FR/NFR, Flow/state, ข้อมูล, UI, การตรวจ
รวมสถานะจาก execution/evaluations จริง; done ต้องมีผลตรวจรองรับ ไม่เดาจากการมีไฟล์
ตัดสิน create/revise/verify/cancel แยกรายงาน พร้อมระบุงานเพิ่ม งานแยก งานยกเลิก งานจัดลำดับใหม่
หากประเภทใดไม่จำเป็น ให้เขียนว่าไม่เปลี่ยนและเหตุผล ไม่สร้างงานเกินจำเป็นเพื่อให้ครบประเภท
คง id ของหน้าที่เดิม; งานที่แยกใช้ id ใหม่พร้อม mapping ต้นทาง; เก็บงานยกเลิกไว้เป็น cancelled
แก้ dependency ทั้งผู้ผลิต ผู้ตรวจ และผู้ใช้ผล; ห้ามอ้าง output ที่ยกเลิกไปแล้ว
ทำให้ FR v2 และผลตรวจมาก่อน Flow v2 และผลตรวจ จากนั้นจึง UI v2 และผลตรวจ
ระบุ outputs รุ่น v2 เป็น work/fr-nfr-v2.md, work/flow-v2.md, work/ui-mockup-v2.html
สำหรับ reveal-2 อย่างน้อยวางแผนครบและวิเคราะห์ผลกระทบ; งานผลิต v3 จะยัง planned ได้
ทำตาราง reuse แยกส่วนที่ใช้ซ้ำได้กับส่วนต้องตรวจใหม่พร้อม hash/evidence และเหตุผล
AI จัดงานได้ แต่ห้ามอนุมัตินโยบายคืนเงินจริง สูตร X หรือการแมปสถานะที่ต้นฉบับไม่ชัด
human-required ต้องมีคำถามใน decisions และ blocking limits ที่ผูก affected_tasks
ตรวจ schema และ DAG; JSON/Markdown ต้องตรงกันและคงข้อมูลรุ่นเดิมไว้ครบ
## รูปแบบ Output และตำแหน่งบันทึก
สร้าง work/plan-vN.json ตาม input/plan.schema.json โดย N=เลข PREV_PLAN+1
สร้าง work/plan-vN.md พร้อมหัวข้อ Diff จากเวอร์ชันก่อน, เหตุผล, ข้อจำกัด
Diff ใช้คอลัมน์ task id | งาน/dependency เดิม | งาน/dependency ใหม่ | การเปลี่ยน | หลักฐาน
trigger ระบุ path reveal และเหตุที่ปรับ; created_at เป็น UTC จริง; เก็บ decisions/reuse/limits
ไม่เขียนทับ PREV_PLAN หรือ artifacts เดิม และไม่ทำงาน Executor ใน session นี้
ส่งแผนคู่ใหม่ไป prompts/05-impact-analysis.md แล้วให้ Evaluator ตรวจ ก่อนทำงานผลิตตามแผน

## กติกาสำหรับทุกบทบาท
working directory = AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/
เริ่ม session ใหม่ ไม่ใช้ resume/continue ไม่เรียก agent เพิ่ม และไม่พึ่งประวัติสนทนา
อ่านเฉพาะไฟล์ Input ที่อนุญาตในขั้นนี้ ไม่ค้นทั้ง repository หรืออ่าน reveal ล่วงหน้า
รักษาข้อความ US/AC ตัวเลข หน่วย และสัดส่วนทดสอบ ห้ามแต่งข้อกำหนดหรือผลตรวจ
แยกแผนงาน AI จาก state machine ของรายการ/ออเดอร์/ชำระเงิน/โต๊ะ
ใช้ชื่อบัญชีและข้อมูลจำลองเท่านั้น ไม่ใช้บัญชีจริงหรือบริการชำระเงินจริง
เขียนเฉพาะ work/; ห้ามแก้ input/, prompts/, reference/, img/ หรือต้นทาง LAB อื่น
ห้ามเขียนทับเวอร์ชันเดิมหรือหลักฐานเดิม; ถ้าเป้าหมายมีแล้ว ให้หยุดและรายงาน path
แผนเป็น snapshot; สถานะการทำงานใหม่เก็บใน execution/evaluations แล้วรวมในแผนรุ่นถัดไป
ถ้า Input ขาดหรือมี blocking limit ที่เกี่ยวกับงาน ให้ตอบ BLOCKED พร้อมสิ่งที่ขาด ไม่สร้างข้อมูลแทน
ข้อเสนอที่ต้นฉบับไม่ระบุให้ติดป้ายสมมติฐาน/ยังไม่ยืนยัน ไม่แปลงเป็น AC
ไม่อ่านเว็บเพื่อเติมกฎร้าน; หมายเหตุ ก./ค./ช. ที่หายให้คงเป็นข้อค้าง
ผลสรุปต้องบอกไฟล์ที่สร้างจริง ข้อค้าง และสิ่งที่ยังไม่ทดสอบ
