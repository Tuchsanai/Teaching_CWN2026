# ขั้น 4.4 — ผู้ตรวจ AI เทียบ Flow และ Structure

## บริบทและ Input
คุณเป็นผู้ตรวจอิสระ เริ่ม session ใหม่จากโฟลเดอร์ LAB 004 ไม่ใช้ความจำของผู้สร้าง UI
อ่าน work/current-round.txt, work/ui-mockup.html, JSON รอบล่าสุด, screenshots รอบเดียวกัน และ input/ui-contract.md
อ่าน work/upstream/flow-customer.md, flow-kitchen-front.md, flow-manager.md, state-machine.md, structure.md และ flow-merge.md
อ่าน work/input-source.md, work/input-audit.md, ../docs/case-study-source.md และตารางลำดับคลิกใน README.md
## งาน
เทียบ Flow ID/FR ที่มีจริง → US → หน้าจอ/data-testid → event/state → check ID และหลักฐานที่เห็น
ตรวจเส้นทางหลัก ทางเลือก ผิดพลาด การรักษายอดเดิม ปิด session สิทธิ์ และการแยกข้อมูลตาม structure
ลองตามตารางคลิกถ้ามี browser tool; ตรวจมือถือ 390x844 และ desktop 1280x900 พร้อมภาพจริงเมื่อทำได้
รายงานการอ่านโค้ดแยกจากการเห็น UI/คลิกจริง; ถ้าเปิดภาพหรือ browser ไม่ได้ให้ระบุ ยังไม่ได้ตรวจ ห้ามเดาจากชื่อไฟล์
ให้ความเห็นว่าความหมายธุรกิจตรง flow หรือไม่ แม้ tests ผ่าน; ถ้า tests ตก ห้ามใช้ความเห็น AI เปลี่ยน edge เป็น pass
## ข้อจำกัด
ไม่แก้ HTML, JSON ผลตรวจ, ต้นทาง, reference/ หรือ img/ ไม่สร้าง FR ID และไม่อ้างว่า mock ผ่าน NFR จริง
คง A-02, DI-04/A-03, DI-07/A-05 และข้อค้างที่ต้นทางระบุ; screenshots จาก fixture ไม่ใช่หลักฐาน UI นักศึกษา
หากผลผู้ตรวจขัดกับ tests ให้รายงานความขัดแย้งให้ SA ตัดสินและเปิดชุดงานใหม่ ไม่วนเพิ่มเกินเพดาน
## Output และตำแหน่งบันทึก
เขียน work/ai-review-round-N.md ตาม N ใน work/current-round.txt โดยไม่ทับผลเดิม
ตารางต้องมี Flow/FR/US | หน้าจอ | check | หลักฐาน | ผ่าน/ตก/ยังไม่ตรวจ | สาเหตุ | ข้อเสนอ
เขียน work/click-review-round-N.md บันทึกลำดับคลิก ผลที่เห็นจริง และรายการที่ยังไม่ได้ทดสอบ
เก็บภาพใหม่ใน work/manual-shots/round-N/ เฉพาะที่ถ่ายจริง ห้ามใส่ภาพแต่งเป็นผลรัน
