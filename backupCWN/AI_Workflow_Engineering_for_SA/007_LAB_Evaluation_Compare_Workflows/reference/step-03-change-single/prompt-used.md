# ขั้น 7.3 — ทดลองแบบ Single Prompt
## ข้อกำหนดเปลี่ยน
โจทย์สมมติเพื่อทดลอง ไม่ใช่ต้นฉบับ: เปลี่ยนเกณฑ์ US-21 เฉพาะค่าเพดานที่ใช้ทดสอบจาก N=5 เป็น N=3 โดยคงหน้าต่าง 15 นาทีที่เริ่มนาที 00/15/30/45 และการทดสอบ 3 จาก 3 รอบเดิม; เมื่อถึง N ต้องแสดง “ครัวเต็ม รอประมาณ X นาที” ก่อนยืนยัน โดยไม่เพิ่มกฎปฏิเสธออเดอร์
## Input และการควบคุมการทดลอง
อ่าน 007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/manifest.md, fr-nfr-v2.md, flow-v2.md, ui-mockup-v2.html,
ui-scenarios.json ภายใต้ 007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/ และ 007_LAB_Evaluation_Compare_Workflows/reference/change-conditions.md
แผนก่อนเปลี่ยนที่ใช้เป็น baseline ของทั้งสองวิธี:
005_LAB_Dynamic_Workflow_Replanning/reference/step-07-plan-v3/plan-v3.json
อ่านสัญญา UI และต้นฉบับเฉพาะ path ที่ baseline manifest ระบุ
## งาน
ทำการวิเคราะห์ผลกระทบและผลิตชิ้นงานทั้งหมดในคำขอเดียว ห้ามแบ่งเรียก Planner/Executor/Evaluator เพิ่ม
ใช้ input/เกณฑ์/โมเดล/effort/เพดานรวมเดียวกับ Dynamic; ไม่เห็นผลของอีกวิธี
แก้ FR, Flow, UI และ scenarios ให้ตรงข้อเปลี่ยนเดียวข้างต้น พร้อม regression ส่วนเดิม
คง AC อื่นและรหัสเดิม; fixture สมมติต้องติดป้ายและไม่ส่งกลับเป็นต้นฉบับ
## Output
สร้าง 007_LAB_Evaluation_Compare_Workflows/reference/step-03-change-single/fr-nfr-v3.md, flow-v3.md, ui-mockup-v3.html, ui-scenarios-v3.json
สร้าง 007_LAB_Evaluation_Compare_Workflows/reference/step-03-change-single/impact.md ระบุส่วนเปลี่ยน/ใช้ซ้ำ/ต้องตรวจใหม่และข้อค้าง
ยังไม่อ้างว่ารัน UI ผ่าน; ผู้ทดลองต้องรันสคริปต์เดียวกันภายนอกภายหลัง


## ข้อกำหนดการเก็บผลรันล่วงหน้า
ใช้สิทธิ์เขียนเฉพาะโฟลเดอร์ปัจจุบันและโฟลเดอร์ย่อยของขั้นนี้; ห้ามแก้ไฟล์อื่น ห้ามใช้ work/ ห้าม git add/commit/push ห้ามเรียก CLI หรือผู้ช่วยเพิ่ม
ทุก path หลักฐานที่ระบุใน prompt สัมพัทธ์จาก AI_Workflow_Engineering_for_SA/ ให้ resolve ../../../ จาก cwd ขั้นนี้ (ถ้าอยู่ขั้นย่อยให้เพิ่มระดับตามจริง)
ใช้ชื่อรหัสขั้นของแผนแบบ JOB- หรือ CHG- ห้ามใส่รหัสงานทีมภายใน ชื่อบัญชีจริง หรือ absolute path ลงเอกสาร
ไม่อ่าน HTML ขนาดใหญ่ของบทเรียน อ่านเฉพาะ snapshot UI ที่ระบุ
เครื่องมือ Codex CLI 0.154.0; โมเดล gpt-6-astra (ตาม flag ที่สั่ง CLI ไม่ยืนยันกลับ); effort high; เวลา/โทเคนผู้ทดลองจะอ่านจาก log หลังจบเอง ห้ามแต่ง
สร้าง fr-nfr-v3.md, flow-v3.md, ui-mockup-v3.html, ui-scenarios-v3.json, impact.md ใน cwd; อ่าน baseline ทั้งหมดจาก manifest; ห้ามรัน browser/ทดสอบ UI เอง จะมีผู้ทดลองตรวจร่วมภายหลัง; อย่าอ้าง PASS จากเพียงอ่านโค้ด
