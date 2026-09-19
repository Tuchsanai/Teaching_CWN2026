# ขั้น 5.4 — ปรับ UI v2 ตามแผนล่าสุด

## บริบทและเป้าหมาย
คุณเป็น Executor งาน UI ของระบบครัวคุณยาย เพิ่มการจำลองตาม US-09/14/21
TASK_ID = revise-ui
RUN_ID = ui-v2-run
## Input
- แผนล่าสุด /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/plan-vN.json/md พร้อม PLAN_READY และ inputs/outputs ของ revise-ui
- /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/fr-nfr-v2.md, /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/flow-v2.md และผลตรวจ upstream ที่แผนกำหนด
- UI รุ่นที่แผนอ้าง (baseline หรือ v1), /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-contract.md
- input/reveal-1.md และ /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/impact-analysis-v2.md
- execution/evaluations ของ dependency และ /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/provenance.md
## งาน
ใช้กติกาเลือกแผนล่าสุดและ dependency ตาม prompts/02-executor.md; หยุดหากงาน UI ไม่ได้รับอนุญาต
สร้างไฟล์ HTML เดียว เปิดผ่าน file:// ใช้ข้อมูลจำลอง ฝัง CSS/JS/ข้อมูล ไม่ใช้ CDN/fetch ภายนอก
คง data-testid เดิมทุกตัวที่สัญญากำหนด รวม scope ของ selector ซ้ำและพฤติกรรมเดิม
เพิ่ม selector ใหม่ได้ เช่น btn-item-unavailable, item-resolution, btn-return-item, capacity-message
selector ใหม่เป็นสัญญาทดสอบของ Mock-up ให้บันทึกเพิ่ม ห้ามเปลี่ยนความหมาย selector เดิมเงียบ ๆ
รองรับครัวกดทำไม่ได้ที่รายการ ลูกค้าเห็นแจ้งเตือน เลือกเปลี่ยนเมนู/คืนรายการ และยอดปรับตามต้นฉบับ
แยกสถานะรายการ “รอลูกค้าตัดสินใจ” จากสถานะออเดอร์และสถานะชำระเงิน
คืนรายการไม่ใช่การยืนยันว่าโอนเงินคืนแล้ว; นโยบายเงินจริงที่ยังไม่ชัดให้แสดงเป็นข้อค้าง
รองรับผู้จัดการตั้งช่วงเร่งด่วนและเพดานต่อ 15 นาทีที่เริ่มนาที 00/15/30/45
เมื่อถึงเพดาน แสดง “ครัวเต็ม รอประมาณ X นาที” ก่อนยืนยันตามต้นฉบับ
ห้ามเพิ่มกฎปฏิเสธออเดอร์อัตโนมัติเพียงเพราะข้อความครัวเต็ม ถ้าต้นฉบับไม่ได้สั่ง
ค่า X ต้องอ้าง FR/คำยืนยันจริง; ถ้ายังไม่ชัดใช้ค่าจำลองติดป้ายและจำกัดผลตรวจ ไม่อ้างสูตรใหม่เป็น AC
รักษาการปิดเมนู/ตัวเลือกใหม่แยกจากการจัดการรายการที่อยู่ในคิวแล้ว
ตรวจผลต่อสถานะลูกค้า ยอดชำระ หน้าร้าน และราคา snapshot เดิมตามงานในแผน
ระบุ regression ที่ต้องรันตาม ui-contract; ห้ามบอกผ่านจากการอ่าน HTML เพียงอย่างเดียว
## รูปแบบ Output และตำแหน่งบันทึก
สร้าง /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/ui-mockup-v2.html หรือ output รุ่นแก้ใหม่ที่แผนล่าสุดระบุ โดยไม่ทับไฟล์เก่า
สร้าง /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/execution/plan-vN/ui-v2-run/revise-ui.md พร้อม plan/input/output hash
รายงาน mapping US → FR → Flow → UI, selector ที่เพิ่ม, พฤติกรรมใช้ซ้ำ, รายการต้องตรวจใหม่, ข้อค้าง
สร้างภาพเฉพาะเมื่อมีการเปิดตรวจจริง โดยบันทึกใน /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/ ของรอบนั้น ไม่เขียน img/
ส่ง UI และรายงานให้ Evaluator; LAN และการโอนเงินจริงยัง NOT_TESTED ใน Mock-up

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
ทำ revise-ui ตาม plan-v2 เมื่อ FR/Flow/outline v2 ผ่านตาม gates ทั้งหมด. สร้างเฉพาะ UI รุ่นใหม่ session/ui-mockup-v2.html พร้อม ui-contract-v2.md และ execution report ตามแผน; ห้ามแก้ baseline. ใช้ session/ui-mockup.html ที่คัดตรงจาก LAB 004 final แล้ว (hash เท่ากับ baseline ที่แผนอ้าง) เป็นฐาน. เก็บ CSS/JS/seed และ data-testid/payload/ราคา snapshot/พฤติกรรมเดิมให้คงเดิม; เพิ่ม feature ตาม FR/Flow v2. แนะนำ selectors ใหม่ให้ใช้ชื่อแน่นอนดังนี้: btn-item-unavailable, customer-unavailable-alert, item-resolution, replacement-menu, btn-change-menu, btn-return-item, nav-capacity, capacity-start, capacity-end, capacity-limit, capacity-wait-minutes, btn-save-capacity, capacity-message. ถ้าซ้ำหลายรายการให้ scope ด้วย data-order-id/data-item-id และบันทึกใน contract. ปุ่มครัวต้องแสดงคำ ทำไม่ได้; ลูกค้าเห็นสาเหตุวัตถุดิบหมดกลางคิวพร้อมเปลี่ยนเมนู/คืนรายการ; สถานะรายการรอลูกค้าตัดสินใจไม่ทับสถานะออเดอร์/การจ่าย/โต๊ะ. คืนรายการลดยอดลูกค้า/หน้าร้านและเปลี่ยนเมนูอัปเดตครัวจริงใน mock ไม่ยืนยันโอนเงินคืน. ครัวเต็มแสดง ครัวเต็ม รอประมาณ X นาที โดย X เป็นค่าจำลองที่เห็นป้ายชัดเจนก่อนปุ่มยืนยัน และยังยืนยันได้. ผู้จัดการตั้งช่วง/N/ค่า X จำลองได้; N=5 ใช้ตรวจ 3 รอบ หน้าต่างเริ่มนาที00/15/30/45. ไม่สร้าง UI reveal-2. ทำ HTML offline ไฟล์เดียว >20000 bytes. อ่าน tests/ui-check.py ของ LAB 004 ได้เพื่อรักษา behavior; การรัน regression และภาพจะทำโดยขั้นตรวจภายหลัง ให้สรุปสิ่งที่ยังไม่รันตามจริง. ส่ง execution.md ใน cwd /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2 พร้อม hash และ locator ที่เพิ่ม. ไม่มีการเรียก agent/CLI เพิ่ม.

ตำแหน่งไฟล์ที่ใช้จริงแบบ absolute เพื่อไม่ให้ตีความ cwd ต่างกัน:
- UI baseline อ่านอย่างเดียว: /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/ui-mockup.html
- UI v2 output ตามแผน: /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/ui-mockup-v2.html
- contract v2 output: /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/ui-contract-v2.md
- execution report ตามกติกา: /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/execution/plan-v2/ui-v2-run/revise-ui.md
- summary of execution เพิ่มใน /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/execution.md
ต้องสร้าง outputs ตาม absolute paths ข้างต้นเพื่อให้ Evaluator รับต่อได้ ไม่สร้าง subdirectory session ซ้อนใน cwd ของขั้น.
