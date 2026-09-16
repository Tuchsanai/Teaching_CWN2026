# 1. Execution trace ของการรันซ้ำครั้งนี้ (updated: change request)

## ตารางการรันซ้ำ (updated: change request)

| Node | รันซ้ำหรือไม่? (yes/no) | เหตุผล |
|---|---|---|
| N1 | yes | INPUT เพิ่ม PDPA consent และ LINE OA self-booking แม้ CSV ไม่เปลี่ยน จึงมี completeness findings ใหม่ |
| N1b | yes | ผล N1 เปลี่ยน ต้องตรวจใหม่; หลักฐานของค่ากำกวมเดิมไม่เปลี่ยน ผลลัพธ์จึงเท่าเดิมทุกประการ |
| N2 | yes | Dependency N1 เปลี่ยน ต้องประเมิน As-Is ใหม่; requirement อนาคตไม่เปลี่ยนหลักฐาน As-Is จึงคงผลเดิมทุกประการ |
| N3 | yes | Dependency N1 เปลี่ยน ต้องเพิ่มกระบวนการและ model ของ consent/LINE self-booking |
| N4 | yes | Dependency N1 เปลี่ยน ต้องเพิ่ม mapping/migration/rollback ของข้อมูลใหม่ |
| N5 | yes | ผล N3/N4 เปลี่ยน จึงรวมใหม่ตาม MERGE RULES หลังทุก dependency DONE |

ไม่มี Node ที่เข้าเงื่อนไข no ในรอบนี้: N1 เพิ่มช่องว่างความครบถ้วนที่มีผลต่อปลายทาง จึงทำให้ dependency ของ N2–N4 เปลี่ยนจริง การรันแล้วได้ผลเดิม (N1b/N2) แยกจากการ reuse โดยไม่รัน ไม่ได้แก้ผลเดิมเพื่อทำให้ดูเหมือนมีการเปลี่ยนแปลง

| Node | สถานะ | หมายเหตุ |
|---|---|---|
| N1 | DONE | ผลเปลี่ยน: เพิ่มข้อค้นพบที่มีที่มาจาก requirement ใหม่; findings CSV เดิมคงอยู่ |
| N1b | DONE | ประเมินหลัง N1 DONE; contract เท่าผลเดิมทุกไบต์ ไม่มีหลักฐานใหม่เลือกค่ากำกวม |
| N2 | DONE | รันหลัง N1/N1b DONE อย่างอิสระ; contract เท่าผลเดิมทุกไบต์ |
| N3 | DONE | รันหลัง N1/N1b DONE โดยไม่เห็น N2/N4; เพิ่ม consent/LINE flows และ model |
| N4 | DONE | รันหลัง N1/N1b DONE โดยไม่เห็น N2/N3; เพิ่ม mapping/onboarding/migration |
| N5 | DONE | รับเฉพาะ DONE contracts หลัง N2–N4 ครบ; รวมความต่าง ตรวจแผนภาพ และคงส่วนเดิมที่ไม่เปลี่ยน |

ไม่พบ Node FAILED และไม่ต้อง retry; ไม่มีผลงานขาด หยุดเมื่อ N5 DONE ข้อมูลหรือ policy ที่ยังรอยืนยันไม่ใช่ความล้มเหลวของ Node ในการจัดทำแผน ผลรันเดิมและ trace เดิมคงอยู่; เพิ่มบันทึกเฟส 2 ต่อท้ายเท่านั้น

