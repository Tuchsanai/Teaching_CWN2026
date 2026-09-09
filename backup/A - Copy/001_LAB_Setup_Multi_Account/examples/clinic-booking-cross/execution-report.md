# ผลรัน Fable → Astra

Fable high สร้าง plan-v1; Astra high พบผังงานข้ามเงื่อนไขความตกลงของลูกค้า จึง NOT READY; Fable high แก้ plan-v2; Astra high ตรวจซ้ำเป็น READY จากนั้นสรุป solution และตรวจ A–C ได้ PASS ทั้งหมด

รัน CLI แยกขั้นผ่าน SSH บน 5090 ส่งเนื้อหาไฟล์ input ให้โมเดล บันทึก output ตามจริง เป็นการส่งงานข้ามค่ายที่จัดลำดับคำสั่งโดยผู้ทดลอง ไม่ใช่หลักฐานว่า Fable เรียก Astra โดยอัตโนมัติ ผลเป็นการตรวจเอกสาร ไม่ใช่การรันซอฟต์แวร์คลินิก

| Output | ผู้สร้าง | Input |
|---|---|---|
| [plan-v1.md](plan-v1.md) | Fable high | case.txt |
| [review-1.md](review-1.md) | Astra high | case.txt, plan-v1.md |
| [plan-v2.md](plan-v2.md) | Fable high | case.txt, plan-v1.md, review-1.md |
| [review-2.md](review-2.md) | Astra high | case.txt, plan-v2.md |
| [solution.md](solution.md) | Astra high | case.txt, review-final.md, plan-v2.md |
| [scenario-results.md](scenario-results.md) | Astra high | case.txt, plan-v2.md, solution.md |

[review-final.md](review-final.md) เป็นสำเนา review-2.md ตรงตัว [execution.json](execution.json) เก็บรุ่นโมเดลที่ runtime รายงานรวม helper หากมี

Container `devtools-booking-cross-839d78` · port 2224 · ลบพร้อมสำเนาข้อมูลล็อกอินแล้ว
