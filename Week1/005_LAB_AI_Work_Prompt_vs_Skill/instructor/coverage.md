# ตรวจความครอบคลุมข้อกำหนด

| ข้อกำหนดผู้ใช้ | สินทรัพย์ที่ตรวจได้ |
|---|---|
| 1 Skill สำหรับคนทั่วไป/ไม่ฝึกโมเดลใหม่ | theory.md, setup.md, Skill ทั้งสามใน skills/ |
| 2 System Analysis | labs/lab1/README.md, data/A,B,C; experiments/inputs/lab1-A,B,C.md; instructor/lab1-key.md |
| 3 DevOps 30นาที/ไม่เขียนโค้ด | labctl, labs/lab2/commands.md, instructor/runtime/server.py/control.py; keys แยก |
| 4 ธุรกิจ/นโยบาย/คิว/ส่งคน | labs/lab3/data/A,B,C; instructor/lab3-key.md และ exemplars A/B/C |
| 5 ตัวช่วยทุก Lab | README.md, hints.md สามระดับ, worksheet.md, template.md ในแต่ละ Lab; exemplar ผู้สอนครบ |
| 6 สร้างและปรับ Skill | skill-workshop.md, instructor/demo/known-flaw.md, v1/v2 SKILL.md; เป็นกรณีสร้างขึ้นอย่างชัดเจน |
| 7 เปรียบเทียบยุติธรรม | canonical/lab1–3.md; experiments/README.md สี่กลุ่ม; scores.md/csv; summary.md; prepare_experiment.py |
| 8 พร้อมสอน | README เวลาเรียน/เตรียมแยก; instructor/slides.md; verification.md; progress.md |
| ไม่ให้ผู้เรียนเขียนโค้ด/config | setup/workshop/lab guides ระบุชัด; helper source อยู่ instructor/runtime |
| Lab1 ≥3 conflicts/unknowns + refs | R5–R7 /3, R8–R10 /3, ยืนยัน R1–R4; 26 scoring items; UAT pending ก่อนเจ้าของตัดสิน |
| Lab3 ≥6เคส+order+dated policy+tie | แต่ละชุด6เคส 5ออเดอร์; P00–P07 U01–U04; day0; เงินซ้ำ/ชำรุด/IDขาด/เกินสิทธิ์/ยกเว้น |
| native loading ไม่สับสนกับแนบไฟล์ | setup.md + experiment native gate; syntax verified, actual loading pending |
| canonical body เท่ากัน | check_package.py เทียบทุกไบต์กับ SKILL body; prepare helper ใส่ body เต็มใน P |
| DevOps ความยาก A/B เท่ากัน | basic A/B และ rollback A/B แยก; transfer C ไม่นำมาเป็นคู่หลัก |
| ร้านรัน offline + loopback isolated | socket bind port0 ส่ง fd ที่ยังเปิด; runtime instance เฉพาะสำเนา; ไม่มี pip/Docker |
| เช็กใช้งานจริง/ผิดยังไม่หาย/cleanup | test_runtime.py และ raw evidence/runtime-tests.txt; ทดสอบ generated workspace ด้วย check_package.py |
| ไม่แต่งผล/เวลาเครื่องไม่ใช่คน | scores/summary ว่าง; verification pending; exemplars ติดป้ายสร้างโดยผู้สอน |

เส้นทางในตารางอ้างจากรากแพ็กเกจ ตารางนี้เป็นการตรวจสินทรัพย์ ไม่แทนหลักฐานว่าเรียนแล้วได้ผลจริง ดูผลเชิงหน้าที่และสิ่งที่ยังไม่ทดสอบใน [verification](../verification.md)
