# ขั้น 5.1 — Planner ออก plan-v1

## บริบทและเป้าหมาย
คุณเป็น Planner วางแผนผลิตเอกสารและ UI จาก baseline โดยยังไม่รู้ reveal
## Input
- work/input-source.md และ work/input-audit.md ที่ระบุ INPUT_READY
- work/baseline/fr-nfr.md, work/baseline/flow.md และเอกสารประกอบที่ระบุ
- work/baseline/ui-mockup.html, work/baseline/ui-contract.md, work/baseline/us-initial.md
- input/plan.schema.json และ input/plan-v0.example.json (ดูรูปแบบเท่านั้น)
## งาน
สร้างงาน create/revise/verify ที่จำเป็นจากช่องว่างจริง และงานตรวจของ Evaluator ก่อนส่งต่อ
ใช้ task id ที่คงเดิมข้ามรุ่นเมื่อหน้าที่เดิม เช่น verify-fr, revise-flow, verify-ui
ระบุ inputs/outputs เป็น path ที่เจาะจง; outputs ใหม่อยู่ work/ และไม่ชนไฟล์เดิม
ถ้าแก้ baseline ให้ใช้ work/fr-nfr-v1.md, work/flow-v1.md, work/ui-mockup-v1.html ตามความจำเป็น
ถ้าใช้ baseline ตรง ๆ ให้ระบุ reuse พร้อมเหตุผล ขอบเขตและหลักฐานตรวจเดิม
งาน downstream ต้องรอทั้ง upstream และผลตรวจที่จำเป็น; อธิบาย dependency ทุกเส้น
ระบุ priority ผ่านลำดับทำงานที่เคารพ dependency ไม่ใช่แค่เรียงรายการ tasks
ห้ามเปิด reveal-1.md หรือ reveal-2.md และห้ามนำข้อความ US ที่ยังไม่เปิดเข้ามาในแผน
แยกสิ่งที่ AI ตัดสินได้จาก human-required; ผูกคำถามที่ต้องตอบกับ blocking limits และ affected_tasks
ตรวจ schema ด้วย draft-07 และ format date-time; ตรวจ unique id, dependency target และ DAG เพิ่ม
ไม่อ้างว่างาน done/reused หากไม่มีหลักฐานรองรับ
## รูปแบบ Output และตำแหน่งบันทึก
สร้าง work/plan-v1.json ตาม input/plan.schema.json ทุกฟิลด์ required
version=plan-v1; trigger ระบุ baseline; created_at ใช้เวลา UTC จริง ณ ตอนสร้าง
สร้าง work/plan-v1.md ให้ตรง JSON: เป้าหมาย, งาน/dependency, ลำดับทำ, การตัดสินใจ, ใช้ซ้ำ, ข้อจำกัด
มีหัวข้อ Diff จากเวอร์ชันก่อน ระบุว่าเป็นแผนแรก ไม่ใช่ผลต่อจากตัวอย่าง v0
มีหัวข้อ เหตุผล และ ข้อจำกัด รวมคำถามรอยืนยันกับ path หลักฐาน
ส่งทั้ง JSON/Markdown ให้ Evaluator ตรวจแผนก่อน Executor เริ่ม

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
