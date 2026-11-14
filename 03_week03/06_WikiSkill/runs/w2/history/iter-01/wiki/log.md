# Evolution Log

## Iteration 1 · Training 46.4%

อ่าน Trace 5 ไฟล์ (ล้มทั้งหมด ไม่มีงานที่ผ่านให้เทียบ): t4-cashback-r1, t4-cashback-r3, t3-shipping-fee-r3, t1-cafe-bill-r1, t2-split-bill-r1 รอบนี้ไม่มีสกิล (ไม่มีโฟลเดอร์ ./skills) ที่ trace บางไฟล์ระบุ “อ่านสกิล: ใช่” หมายถึงแค่เคยสั่ง ls ./skills เท่านั้น ไม่มีสกิลให้อ่านจริง และ wiki/skill-impact.md ยังว่าง จึงไม่มีข้อเสนอรอบก่อนให้ประเมิน

พบว่าทุกงานผ่านชุดข้อตรวจพื้นฐานเหมือนกัน (contract, basic, half_up/no_drift, boundary) แต่ตกชุดเดียวกันหมด: (1) reject_value/reject_type เพราะไม่ตรวจอินพุต (2) cli_ok/cli_error เพราะไม่มี __main__ อ่าน stdin (3) tests เพราะไม่มี test_solve.py สามข้อนี้ไม่ได้อยู่ในข้อความโจทย์แต่ตัวตรวจคาดไว้ ผู้ปรับสกิลจึงต้องใส่เป็นข้อกำหนดมาตรฐานของงานประเภทนี้ (4) Agent ไม่รันงานตัวเองอย่างครบ: 2 งานไม่รันเลย อีก 3 งานรันแค่ happy path (5) ข้อ policy ตกใน cashback และ shipping_fee โดยค่าที่ได้ต่างจากที่คาดมาก (300 vs 600, 0 vs 8000) ยังไม่ยืนยันสาเหตุ อาจเป็นการตีความโจทย์ผิดหรือกฎที่โจทย์ไม่ได้เขียน

สิ่งที่ได้ผลแล้ว: การคำนวณเงินด้วยจำนวนเต็ม/Fraction และปัดครึ่งขึ้นครั้งเดียวท้ายสุด ผ่าน half_up, no_drift, boundary ในทุกงานที่มีข้อนั้น

ปัญหาที่ยังเปิดอยู่: ทั้ง 5 pattern ที่เป็นปัญหายังเกิดอยู่ทั้งหมด และ policy ยังไม่ยืนยัน (ต้องดูรายการกรณีที่ตกทั้ง 6 ในรอบถัดไป) ยังไม่มี trace ของงานที่ผ่านครบให้เปรียบเทียบ

แก้ wiki: สร้างหน้าใหม่ 6 หน้า (missing-input-validation, missing-cli-entrypoint, missing-test-file, no-self-verification, policy-mismatch-unconfirmed, integer-math-half-up-works) และเขียน index ใหม่ทั้งไฟล์
