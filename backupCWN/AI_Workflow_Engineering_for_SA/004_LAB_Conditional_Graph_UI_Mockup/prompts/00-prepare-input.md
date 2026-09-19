# ขั้น 4.0 — เตรียม Input

## บริบท
คุณเป็น SA ของครัวคุณยาย ทำงานจากโฟลเดอร์ LAB 004 ใน session ใหม่
อ่าน input/README.md, input/mock-data.json, input/ui-contract.md และ ../docs/case-study-source.md
## งาน
สำรวจ ../003_LAB_Static_Graph_Flow_Structure/work/ และ lab004-handoff.md ก่อน
หากไม่มีผลของนักศึกษา ใช้ชุดที่มี manifest ครบใน ../003_LAB_Static_Graph_Flow_Structure/reference/ พร้อมบันทึกว่าใช้ผลอ้างอิง
เลือก snapshot เดียว ตรวจ flow-customer.md, flow-kitchen-front.md, flow-manager.md, state-machine.md, structure.md, flow-merge.md
อ่าน JSON คู่กันและ merge-report.md เมื่อมี; เปรียบเทียบฉบับรวมกับ state/structure และข้อค้าง
คัดลอกชุดที่ตรวจแล้วไป work/upstream/ และคำนวณ SHA-256 จากไฟล์จริง
## ข้อจำกัด
ไม่แก้ต้นทาง ไม่เขียน reference/ หรือ img/ ไม่สร้าง flow แทนไฟล์ที่ขาด ไม่อ้างผลอ้างอิงเป็นผลตนเอง
คงข้อสงสัย A-02, DI-04/A-03 และ DI-07/A-05; ถ้าขาด Input หรือขัดแย้งจนสร้าง UI ไม่ได้ ให้บันทึก MISSING/BLOCKED และหยุด
ไม่ใส่บัญชีจริง ข้อมูลบุคคล token หรือ PIN จริง; ขอบเขต UI มีเฉพาะ 16 US ใน README
## Output และตำแหน่งบันทึก
เขียน work/input-source.md ตารางต้นทาง/รุ่น/hash/SELF หรือ REFERENCE และ work/input-audit.md สถานะ READY/MISSING/BLOCKED พร้อมเหตุ
เขียน work/session-plan.md ระบุเงื่อนไขหยุด: baseline รอบ 0 แล้วแก้ได้รอบ 1–3, ชุดข้อที่ตกซ้ำสองรอบติดให้ยกเลิก
ช่องเพดานเวลา/งบให้ผู้เรียนกำหนดก่อนรันจริง; ข้อมูลที่ไม่ได้วัดใช้ ไม่มีข้อมูล
หากปลายทางมีหลักฐานเดิมให้หยุดและรายงาน path ที่ต้องเก็บเป็นชุดใหม่ ห้ามทับ
