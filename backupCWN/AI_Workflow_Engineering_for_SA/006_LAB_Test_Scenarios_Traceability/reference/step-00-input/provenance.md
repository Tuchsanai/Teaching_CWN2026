# ที่มาของ Input

ใช้ผลอ้างอิงจาก LAB 005 ไม่ใช่ผลของนักศึกษา และไม่ถือผลตรวจต้นทางเป็นผลรัน UI ใน LAB นี้

| ไฟล์ต้นทาง (relative จาก LAB) | SHA-256 |
|---|---|
| ../005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/fr-nfr-v2.md | 2cbdde11bb3fd5e62f338a1ea74f65d11112f3ea56e8a10ed9d24b08a1dcf0bb |
| ../005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/flow-v2.md | 8fe7983eb45a7222424c7fafe34adf78874da75e7e7cf3ab013d4955d1159f9c |
| ../005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/ui-mockup-v2.html | 249b98c493f4c1347efe36f8be059095ede9d3b23b76ada3b022cfc416c2a1cc |
| ../005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/ui-contract-v2.md | 40ad0ff84c423a225b1675bbc2a627390446b9ecfcbcbb4496a6f0605e675888 |
| ../005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/test-outline-v2.md | 50b3c1a7e68a5ca3a56cff2939f55cd591ae2c60c63bd3577625bc442dd2b763 |
| ../005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/state-machine-v2.md | efe13a4cbb843c056884478fa8e5a0ab201c9641a579ae355cedb07867218d0a |
| ../005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/structure-v2.md | f1a935fc0cf2779d225ce050a12b5df108c53a149fa0885ac7ce78828ae2290d |

## ข้อตกลงการจัดเก็บ

เก็บ snapshot ต้นทางตามโครงส่งมอบที่กำหนด แม้ข้อความทั่วไปอีกส่วนระบุไม่ให้วางสำเนา input ใน reference
ปรับ path ของ prompt ที่ใช้จริงให้เขียนผลตรงโฟลเดอร์ขั้นใน reference เพื่อรักษาขอบเขตไฟล์ที่อนุญาต; ไม่แก้ prompts/, input/, tests/ หรือ work/
เวลาใน meta เป็น wall time ที่จับก่อนและหลัง process; โทเคนอ่านจาก turn.completed.usage เท่านั้น
ผล AI เก็บตามที่สร้าง ไม่ปรับเนื้อหาด้วยมือ; การรวมและแก้ coverage ส่งกลับให้ AI ตาม prompt
รอบตรวจครั้งแรกใช้ชื่อ round-1 เทียบกับ round-0 ในบทเรียน; รอบแก้แยก fix-1/fix-2 และตรวจซ้ำตามเพดาน
ทุก path ใน manifest อ้างจากโฟลเดอร์ LAB; คำสั่งอ่านไฟล์ของ AI ใช้ path สัมพันธ์กับ cwd ที่ระบุใน prompt
