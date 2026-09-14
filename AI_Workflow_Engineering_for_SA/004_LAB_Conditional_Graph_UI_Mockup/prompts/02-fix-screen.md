# ขั้น 4.3 — แก้เฉพาะหน้าจอที่ตก

## บริบทและ Input
คุณเป็นผู้แก้ UI ของครัวคุณยาย เริ่ม session ใหม่จากโฟลเดอร์ LAB 004
อ่าน work/ui-mockup.html, work/current-round.txt, JSON รอบก่อนใน work/, input/ui-contract.md, input/mock-data.json และ work/upstream/
รายการจากตัวตรวจที่ต้องแก้ (แทนช่องนี้ด้วย JSON จริงก่อนรัน):
{{FAILED_CHECKS}}
## งาน
จับคู่ check ID → US → หน้าจอ → สาเหตุจาก detail และ screenshot ของรอบก่อน
แก้เฉพาะหน้าจอ/ฟังก์ชันที่ทำให้ข้อในรายการตก ห้ามแตะส่วนที่ผ่าน ห้ามจัดหน้าใหม่ทั้งไฟล์
หากปัญหาอยู่ใน shared state ให้ระบุผลกระทบต่อหน้าจอที่ผ่านก่อน; ถ้าซ่อมแบบจำกัดขอบเขตไม่ได้ ให้รายงาน BLOCKED แทนขยายงานเอง
เก็บ data-testid, mock seed และกฎธุรกิจเดิมทุกข้อ; ห้าม hardcode ให้ผ่านตาม check โดยไม่ทำพฤติกรรม
## ข้อจำกัด
ห้ามแก้ tests/, input/, prompts/, work/upstream/, reference/ หรือ img/ และห้ามลบหลักฐานก่อนแก้
ไม่แก้ถ้า JSON ก่อนหน้า edge=cancel หรือ pass; ถ้าแก้ครบ 3 รอบแล้วให้หยุดและรายงานยกเลิก
ไม่ข้ามข้อที่เคยผ่านในการตรวจซ้ำ; ห้ามเปลี่ยน failed เป็น passed เองหรือสรุปผลก่อนรัน
## Output และตำแหน่งบันทึก
แก้ work/ui-mockup.html หลังตรวจว่ามี snapshot work/ui-before-round-N.html แล้ว โดย N อ่านจาก work/current-round.txt
เขียน work/fix-report-round-N.md: check ID, หน้าจอ, สาเหตุ, จุดแก้, ส่วนที่คงไว้, regression ที่ต้องตรวจ และข้อค้าง
หาก placeholder ยังไม่แทนหรือไม่มี snapshot ให้หยุดพร้อมเหตุ; ให้ผู้เรียนรัน tests/ui-check.py ทั้งชุดเป็นผู้ตัดสิน
