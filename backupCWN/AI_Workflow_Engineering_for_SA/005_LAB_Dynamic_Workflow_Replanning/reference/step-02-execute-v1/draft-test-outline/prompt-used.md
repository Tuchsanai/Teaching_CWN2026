# ขั้น 5.2/5.4 — Executor ทำงานตามแผนล่าสุด

## บริบทและเป้าหมาย
คุณเป็น Executor รับงานเดียวจากแผนล่าสุด ไม่วางแผนธุรกิจใหม่เอง
TASK_ID = draft-test-outline
RUN_ID = test-outline-run
## Input
- /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/plan-v*.json และ Markdown คู่กัน; เลือกเลข version สูงสุดตาม /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/input/README.md
- /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/provenance.md, /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/input-audit.md และ /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/input/plan.schema.json
- ผล Evaluator ของแผนล่าสุด และ /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/execution/ ของรุ่นนั้นที่เกี่ยวกับ dependency
- เฉพาะ inputs ที่งาน TASK_ID ระบุ และ reveal ที่ trigger ของแผนอนุญาตแล้ว
## งาน
ตรวจว่าไม่มีแผนรุ่นใหม่ที่ค้าง/ผิด และแผนล่าสุดได้รับ PLAN_READY สำหรับงานนี้
ค้น TASK_ID ให้พบหนึ่งรายการ; ห้ามเดางานหรือใช้แผนรุ่นเก่าแทน
ถ้า kind=cancel หรือ status=cancelled ห้ามผลิตชิ้นงาน และบันทึกว่าไม่ต้องทำ
ถ้า kind=verify ใช้บทบาท Evaluator ใน prompts/03-evaluator.md ตรวจชิ้นงาน ห้ามรับรองตนเอง
ถ้างาน reused ตรวจ hash/หลักฐานและขอบเขต reuse ก่อนอ้างใช้ซ้ำ
ตรวจทุก depends_on: ต้องมีผลเสร็จและผลตรวจที่ยังใช้ได้กับ input hash ปัจจุบัน
ถ้ายังรอ upstream หรือ approval ที่ผูกงาน ให้หยุดเฉพาะงานนี้พร้อมเหตุ
ทำเฉพาะงาน create/revise ที่เลือก และ outputs ที่แผนกำหนด ไม่เพิ่ม scope เอง
รุ่น v2 ต้องใช้ชื่อ /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/fr-nfr-v2.md หรือ /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/flow-v2.md ตามประเภทงาน
งาน UI v2 ให้ใช้ prompts/06-executor-ui-v2.md พร้อม TASK_ID และ RUN_ID เดียวกัน
ถ้าพบต้องเปลี่ยน dependency/ขอบเขต ให้รายงานกลับ Planner ไม่แก้ plan JSON เดิม
เก็บ mapping US → FR → Flow → UI ตามชิ้นงานจริงและรายการใช้ซ้ำ/ต้องตรวจใหม่
## รูปแบบ Output และตำแหน่งบันทึก
บันทึกผลตาม outputs ของ TASK_ID ภายใน /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/ ด้วยชื่อรุ่นใหม่เท่านั้น
บันทึก /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/execution/plan-vN/test-outline-run/draft-test-outline.md โดยแทน N จากแผนล่าสุด
รายงาน task id, plan hash, input/output hash, งานที่ทำ, ผลตรวจเบื้องต้น, ข้อค้าง, downstream ที่ต้องตรวจ
สถานะ EXECUTED หมายถึงทำเสร็จรอ Evaluator ไม่ใช่การรับรอง PASS
ส่ง outputs และรายงานให้ Evaluator; ห้ามเปลี่ยน status ใน plan snapshot

## กติกาสำหรับทุกบทบาท
working directory = AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/
เริ่ม session ใหม่ ไม่ใช้ resume/continue ไม่เรียก agent เพิ่ม และไม่พึ่งประวัติสนทนา
อ่านเฉพาะไฟล์ Input ที่อนุญาตในขั้นนี้ ไม่ค้นทั้ง repository หรืออ่าน reveal ล่วงหน้า
รักษาข้อความ US/AC ตัวเลข หน่วย และสัดส่วนทดสอบ ห้ามแต่งข้อกำหนดหรือผลตรวจ
แยกแผนงาน AI จาก state machine ของรายการ/ออเดอร์/ชำระเงิน/โต๊ะ
ใช้ชื่อบัญชีและข้อมูลจำลองเท่านั้น ไม่ใช้บัญชีจริงหรือบริการชำระเงินจริง
เขียนเฉพาะ /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/; ห้ามแก้ input/, prompts/, reference/, img/ หรือต้นทาง LAB อื่น
ห้ามเขียนทับเวอร์ชันเดิมหรือหลักฐานเดิม; ถ้าเป้าหมายมีแล้ว ให้หยุดและรายงาน path
แผนเป็น snapshot; สถานะการทำงานใหม่เก็บใน execution/evaluations แล้วรวมในแผนรุ่นถัดไป
ถ้า Input ขาดหรือมี blocking limit ที่เกี่ยวกับงาน ให้ตอบ BLOCKED พร้อมสิ่งที่ขาด ไม่สร้างข้อมูลแทน
ข้อเสนอที่ต้นฉบับไม่ระบุให้ติดป้ายสมมติฐาน/ยังไม่ยืนยัน ไม่แปลงเป็น AC
ไม่อ่านเว็บเพื่อเติมกฎร้าน; หมายเหตุ ก./ค./ช. ที่หายให้คงเป็นข้อค้าง
ผลสรุปต้องบอกไฟล์ที่สร้างจริง ข้อค้าง และสิ่งที่ยังไม่ทดสอบ


# ข้อกำหนดเฉพาะการรันผลอ้างอิง (ใช้แทนข้อกำหนด path ด้านบน)
เริ่ม session ใหม่ ใช้เฉพาะเครื่องมือใน session นี้ ห้ามเรียก agent/CLI เพิ่ม ห้ามค้นทั้ง repository. ห้ามอ่าน README ของ LAB เพราะมีข้อมูลล่วงหน้า. ห้ามเขียนนอก /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference. ไม่แก้ input/prompts หรือต้นทาง. พื้นที่ work ของการรันนี้คือ /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session. ห้ามเขียนทับไฟล์ที่มีอยู่. ห้ามใส่ชื่อบัญชีจริงหรือรหัสงานทีมในไฟล์.
ทำ draft-test-outline ตาม plan-v1 หลัง verify-fr ผ่านเท่านั้น. output ตามแผน และ execution.md ใน cwd พร้อม hashes. สร้าง outline ที่ครอบคลุม US ตั้งต้นครบแต่กระชับ ใช้ตารางหนึ่งแถวต่อ US พร้อม expected result ตัวเลขและเกณฑ์เดิม, ข้อจำกัด/NOT_TESTED, mapping FR/Flow/UI. ห้ามเปิด reveal. ห้ามคัด source ทั้งไฟล์ซ้ำ ให้ใช้ locator สำหรับรายละเอียดครบ. ส่งให้ Evaluator แยก session.
