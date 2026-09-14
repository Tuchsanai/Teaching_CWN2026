# วิเคราะห์ผลกระทบและขอบเขตใช้ซ้ำ

## บริบทและเป้าหมาย
คุณเป็นผู้วิเคราะห์ผลกระทบ เปรียบเทียบแผนก่อน–หลังกับข้อมูลที่เปิดเผยจริง
PREV_PLAN = /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/plan-v1.json
CURRENT_PLAN = /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/plan-v2.json
REVEAL_FILE = /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-03-reveal-1/reveal-1.md
## Input
- /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/plan-v1.json และ Markdown คู่กัน
- /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/plan-v2.json และ Markdown คู่กัน
- /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-03-reveal-1/reveal-1.md และ reveal ก่อนหน้าที่เปิดแล้วเท่านั้น
- artifacts, execution/evaluations และ baseline ที่ทั้งสองแผนอ้าง
- /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/impact-analysis.md และ impact-analysis รุ่นก่อนถ้ามี
## งาน
ตรวจว่าแผนสองรุ่นต่อเนื่องและ trigger อ้าง reveal ที่กำหนด; ถ้าไม่ตรงให้หยุด
ติดตาม US → FR/NFR → Flow/state/data → UI → งานตรวจ และ dependency ต่อเนื่องทุกชั้น
แยกการเพิ่มข้อมูลจากต้นฉบับออกจากสมมติฐานของผู้วิเคราะห์
แยกการเปลี่ยนงาน AI ออกจากการเปลี่ยนสถานะออเดอร์; ไม่ใช้สองเรื่องแทนกัน
วิเคราะห์ผลต่อ US-05/07/08/12/15/19 โดยอ้างหลักฐานที่เกี่ยวข้องจริง
ถ้าไม่กระทบข้อใดให้ระบุเหตุผล/หลักฐาน ไม่เว้นว่างจนดูเหมือนไม่ได้ตรวจ
ตรวจยอดคืนรายการ สถานะจ่ายแล้ว ราคาที่เก็บกับออเดอร์ และผลต่อรายงานโดยไม่แต่งนโยบายเงินคืน
ตรวจช่วงเร่งด่วน/เวลารอว่าไม่สรุปเป็นค่าเดียวกันโดยไม่มีคำยืนยัน
ระบุส่วนที่ใช้ซ้ำได้พร้อมรุ่นและ hash; ส่วนที่เปลี่ยน upstream ต้อง needs_recheck หรือ replace พร้อมเหตุ
ระบุคำถามที่ต้องถามมนุษย์ งานที่ติดข้อค้าง และวิธีตรวจหลังมีคำตอบ
สำหรับ reveal-2 ต้องวิเคราะห์ครบทั้งห้า US แม้ยังไม่ผลิต FR/Flow/UI v3
## รูปแบบ Output และตำแหน่งบันทึก
สร้าง /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/impact-analysis-vN.md โดย N จาก CURRENT_PLAN และห้ามเขียนทับ
ตารางหลักใช้คอลัมน์: แผนเดิม | ข้อมูลใหม่ | งาน/dependency ที่เปลี่ยน | ชิ้นงานที่กระทบ | ส่วนที่ใช้ซ้ำ/ตรวจใหม่
ทุกแถวระบุ task id, US และ locator/hash ตามไฟล์ที่อ่านจริง พร้อมสถานะการยืนยัน
มีหัวข้อ ผลกระทบโดยตรง, ผลกระทบต่อเนื่อง, คำถามรอคำตอบ, ข้อจำกัด, งานถัดไป
สร้าง /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/impact-analysis.md ในครั้งแรก; ครั้งต่อไปเพิ่มท้ายทั้ง section รุ่นใหม่เท่านั้น
รักษาเนื้อหา section รุ่นเดิมทุกตัวอักษร ไม่เขียนทับประวัติหรือแก้ผลย้อนหลัง
ถ้ามี section รุ่นนี้แล้ว ให้หยุดเพื่อเลือกการรันใหม่ ไม่เพิ่มผลซ้ำ
ถ้าพบแผนตกหล่นให้รายงานแก่ Planner; ห้ามแก้แผนรุ่นเดิมเอง

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
ตรวจยืนยัน impact-analysis-v2 เดิมด้วยพารามิเตอร์ที่แทนค่าครบใน session ใหม่: ต้นฉบับ prompt รอบแรกมี CURRENT_PLAN เป็น placeholder ใน template แนบท้าย แม้ข้อกำหนดเฉพาะระบุ plan-v2 และผลผ่าน Evaluator แล้ว. รอบนี้ตรวจยืนยันการจับคู่ plan-v1 -> plan-v2 และ reveal-1 โดยไม่มีความกำกวม. ห้ามสร้างแผนใหม่หรือแก้ไฟล์เดิม. ยกเว้น output path ของ template: สร้างเฉพาะ impact-analysis-review.md ใน cwd /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-04-plan-v2/round-2 พร้อมคำตัดสิน ความตรงกับตาราง11แถวเดิม, US-09/14/21 และ transitive, reuse/hash, ข้อจำกัด, และผลว่าต้องแก้หรือไม่. กระชับราว40บรรทัด ไม่คัดแผนหรือตารางเดิมทั้งชุด. อ่านแผน/impact/ผล Evaluator รอบเดิมตามhash ไม่ทดสอบระบบหรืออ่าน reveal-2. เก็บข้อค้างธุรกิจตามเดิมและไม่เขียนทับประวัติ.
