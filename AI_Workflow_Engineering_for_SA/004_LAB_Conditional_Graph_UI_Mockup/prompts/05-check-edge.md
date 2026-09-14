# ขั้น 4.2 — อ่านผลตรวจและตัดสิน Edge

## บริบทและ Input
คุณเป็นผู้ตรวจ workflow ของ LAB 004 ใน session ใหม่
อ่าน work/current-round.txt เป็น N, work/ui-check-round-N.json, input/ui-contract.md และ tests/ui-check.py
ถ้า N > 0 อ่าน work/ui-check-round-(N-1).json ด้วย; อ่าน log/ภาพรอบเดียวกันที่มีจริง
## งาน
ยืนยันจำนวน checks, passed และ failed ตรงกัน แสดงรายการข้อที่ตกพร้อม US/detail/หน้าจอ
อธิบาย edge ตาม JSON: failed=0 คือ pass; ชุด failed IDs เท่าเดิมสองรอบติดคือ cancel; นอกนั้น fix
ถ้าเป็นชุดที่เล็กลงจริงหรือเปลี่ยนชุด ยังเป็น fix; อย่าใช้แค่จำนวนตกที่เท่ากันตัดสินว่า cancel
รอบ 0 คือ baseline; รอบ 1–3 คือรอบแก้; ถ้า N=3 แล้วยังตก ให้ workflow ยกเลิกแม้ raw edge เป็น fix
ถ้า runtime/browser ไม่พร้อม แยก environment ออกจากบั๊กหน้าจอและหยุดแก้ UI จนตรวจสาเหตุได้
## ข้อจำกัด
ห้ามแก้ HTML, tests, JSON ผลตรวจ หรือข้ามเงื่อนไขกันวน/เพดาน; ไม่สร้างผลถ้ารายงานยังไม่มี
AI เป็นผู้อธิบายหลักฐาน ไม่ใช่ผู้เปลี่ยน raw edge; เวลา/โทเคนที่ไม่มี log ใช้ ไม่มีข้อมูล
## Output และตำแหน่งบันทึก
เขียน work/ui-check-round-N.md: ผลตรวจจริง, failed IDs, raw edge, workflow decision, เหตุผลหยุด/ส่งต่อ และหลักฐาน
กรณี cancel ให้ระบุสิ่งที่ยังเสียและงานที่ต้องวางแผนใหม่; ไม่ถือว่ายกเลิกเท่ากับผ่าน
หาก Markdown รอบนี้มีอยู่แล้ว ให้หยุดเพื่อใช้ชื่อชุดใหม่ ไม่เขียนทับ
