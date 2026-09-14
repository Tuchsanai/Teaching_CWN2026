# ขั้น 5.0 — ตรวจ Input ก่อนเปิด reveal

## บริบทและเป้าหมาย
คุณเป็นผู้ตรวจความพร้อมของงานวิเคราะห์ระบบครัวคุณยาย
ตรวจไฟล์ตั้งต้นที่นักศึกษาคัดลอกตาม /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/input/README.md แล้ว ห้ามสร้าง FR หรือ Flow ทดแทน
## Input
- /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/input/README.md เฉพาะวิธีเตรียม input และสัญญาแผน
- /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/provenance.md
- /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/fr-nfr.md
- /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/flow.md และเอกสารประกอบที่ระบุใน input-source.md
- /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/ui-mockup.html และ /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/ui-contract.md
- /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/us-initial.md พร้อมผลตรวจ upstream ที่คัดไว้
## งาน
ตรวจความครบ ที่มา รุ่น SHA-256 และหลักฐานการตรวจของทั้งสามชิ้นงาน
บันทึกคำว่า ใช้ผลอ้างอิง ตามที่มาจริง; ไม่ถือว่ารุ่นเลขสูงสุดคือรุ่นที่ผ่าน
หากผลตรวจ upstream ไม่มี ให้ระบุยังไม่ตรวจและหยุดส่งต่อการผลิตงาน
ตรวจว่า baseline ไม่ครอบคลุมเนื้อหา US ที่กันไว้; ถ้าหลุดให้บันทึกจุดที่พบและหยุดก่อน plan-v1
อ่านเฉพาะ US ตั้งต้น 18 แถว; รหัสที่ถูกอ้างในเซลล์ไม่ขยายขอบเขต
ตรวจ FR/Flow/UI ว่าใช้รุ่นสอดคล้องกัน พร้อมระบุ UI ส่วนที่ยังไม่มีจาก LAB ก่อน
แยกข้อค้างด้านธุรกิจจากไฟล์หาย ไม่แก้ข้อกำหนดเอง
## รูปแบบ Output และตำแหน่งบันทึก
สร้าง /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/input-audit.md เป็นตาราง ชิ้นงาน | ที่มา | hash | ผลตรวจ | ข้อค้าง | พร้อมส่งต่อ
สรุป INPUT_READY หรือ BLOCKED พร้อมเหตุผลและรายการหลักฐานที่ใช้
ห้ามเขียนว่า INPUT_READY หากหลักฐานจำเป็นขาดหรือข้อมูลที่กันไว้หลุด
ส่งต่อเฉพาะ input-audit และ baseline ที่พร้อมให้ Planner

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
อ่าน baseline ที่คัดไว้และ provenance.md พร้อม fr-check.json flow-check.json ui-check.json. สร้าง input-audit.md ใน cwd นี้โดยตรง (แทน path output ด้านบน). ตรวจที่มาและเนื้อหาเปิดเผยก่อนเวลา: การอ้าง US-14 ในเซลล์ US-20 กับรายการ excluded ไม่ใช่เนื้อหา reveal. ไม่มีไฟล์ต้องอ่านอื่นนอก input ที่กำหนด. ถ้าพร้อมสำหรับงานวิเคราะห์/mock เขียน INPUT_READY พร้อมแยกข้อค้างธุรกิจจาก file blocker. ไม่อ่าน reveal ใด ๆ.
