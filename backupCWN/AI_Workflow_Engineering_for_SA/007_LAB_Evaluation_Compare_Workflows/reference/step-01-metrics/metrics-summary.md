# สรุปทรัพยากรต่อ LAB

calls = จำนวน event turn.completed + turn.failed; failed เป็นส่วนหนึ่งของ calls
จำนวน event ไม่ยืนยันจำนวน process CLI และไม่ใช่จำนวนรอบสร้าง–ตรวจ–แก้
โทเคนรวมจาก usage ของ terminal events; ขาด key แม้หนึ่งครั้งให้ไม่มีข้อมูล พร้อม subtotal ในข้อสังเกต
cached_input_tokens และ reasoning_tokens แยกแสดง ไม่บวกซ้ำเป็นโทเคนรวม
duration_s ใช้ meta.json ก่อน run-meta.md ในโฟลเดอร์เดียวกับ log เท่านั้น
ผลรวม duration_s เป็นผลรวมเวลาต่อไฟล์ ไม่ใช่เวลา wall ของกราฟที่รันขนาน
แต่ละโฟลเดอร์ log ต้องมี metadata ของการรันนั้นเอง; ไม่กระจายเวลารวมจากโฟลเดอร์แม่
สแกนเฉพาะ reference/; ไม่ครอบคลุม work/ หรือผลทดลอง Single/Dynamic โดยอัตโนมัติ
ไม่มีข้อมูลไม่เท่ากับ 0; ไม่พบ log ไม่ได้หมายความว่าไม่มีการเรียก

| lab | calls | failed | input_tokens | cached_input_tokens | output_tokens | reasoning_tokens | duration_s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 001_LAB_Single_Prompt_Baseline | 3 | 0 | 1512903 | 1342720 | 47163 | 2957 | ไม่มีข้อมูล |
| 002_LAB_Loop_FR_NFR | 5 | 0 | 2341246 | 2087424 | 83388 | 2259 | 1488.91 |
| 003_LAB_Static_Graph_Flow_Structure | 6 | 0 | ไม่มีข้อมูล | ไม่มีข้อมูล | ไม่มีข้อมูล | ไม่มีข้อมูล | ไม่มีข้อมูล |
| 004_LAB_Conditional_Graph_UI_Mockup | 3 | 0 | 4352097 | 4036480 | 54538 | 6260 | ไม่มีข้อมูล |
| 005_LAB_Dynamic_Workflow_Replanning | 22 | 0 | ไม่มีข้อมูล | ไม่มีข้อมูล | ไม่มีข้อมูล | ไม่มีข้อมูล | 5718.442563 |
| 006_LAB_Test_Scenarios_Traceability | 10 | 0 | ไม่มีข้อมูล | ไม่มีข้อมูล | ไม่มีข้อมูล | ไม่มีข้อมูล | 4051.631 |
| 007_LAB_Evaluation_Compare_Workflows | ไม่มีข้อมูล | ไม่มีข้อมูล | ไม่มีข้อมูล | ไม่มีข้อมูล | ไม่มีข้อมูล | ไม่มีข้อมูล | ไม่มีข้อมูล |

## ข้อสังเกต

ไม่พบปัญหารูปแบบจากไฟล์ที่อ่าน; ค่าที่ขาดยังแสดงไม่มีข้อมูล
