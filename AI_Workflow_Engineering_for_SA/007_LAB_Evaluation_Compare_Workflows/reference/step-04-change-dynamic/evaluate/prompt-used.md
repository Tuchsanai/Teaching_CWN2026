# ขั้น 7.3 — ทดลองแบบ Dynamic Workflow
## ข้อกำหนดเปลี่ยน
โจทย์สมมติเพื่อทดลอง ไม่ใช่ต้นฉบับ: เปลี่ยนเกณฑ์ US-21 เฉพาะค่าเพดานที่ใช้ทดสอบจาก N=5 เป็น N=3 โดยคงหน้าต่าง 15 นาทีที่เริ่มนาที 00/15/30/45 และการทดสอบ 3 จาก 3 รอบเดิม; เมื่อถึง N ต้องแสดง “ครัวเต็ม รอประมาณ X นาที” ก่อนยืนยัน โดยไม่เพิ่มกฎปฏิเสธออเดอร์
## Input และการควบคุมการทดลอง
อ่าน 007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/manifest.md, fr-nfr-v2.md, flow-v2.md, ui-mockup-v2.html,
ui-scenarios.json ภายใต้ 007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/ และ 007_LAB_Evaluation_Compare_Workflows/reference/change-conditions.md
แผนก่อนเปลี่ยนที่ใช้เป็น baseline ของทั้งสองวิธี:
005_LAB_Dynamic_Workflow_Replanning/reference/step-07-plan-v3/plan-v3.json
PHASE = evaluate; ROUND = 0
อ่านผลก่อนหน้าจาก 007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/ ตาม dependency ของ PHASE เท่านั้น ไม่อ่านผล single
## งาน
PHASE=plan: สร้าง plan-round-<ROUND>.md มี task id, dependency, inputs, outputs, owner, state และ stop rule
แสดงแผนเดิม -> ข้อมูลใหม่ -> งานเพิ่ม/แยก/ยกเลิก/จัดลำดับ -> ชิ้นงานกระทบ -> ส่วนใช้ซ้ำ/ตรวจใหม่
รอบ 0 วางแผนจากข้อเปลี่ยน; รอบ 1/2 ใช้ผล evaluate ก่อนหน้าเป็น feedback และบันทึก diff แผน
PHASE=execute: อ่านแผนรอบนี้ แล้วผลิต fr-nfr-v3.md, flow-v3.md, ui-mockup-v3.html,
ui-scenarios-v3.json ใน 007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-<ROUND>/ พร้อม execution.md ตาม dependency
PHASE=evaluate: อ่านแผน/ผล execute/ผลสคริปต์ tests.json ของรอบนี้ ตรวจข้อเปลี่ยนเดียวและ regression
เขียน evaluation-round-<ROUND>.md ระบุ COMPLETE, REPLAN หรือ STOP_WITH_GAPS พร้อมหลักฐาน
หนึ่งการเรียกทำหนึ่ง PHASE เท่านั้น; ผู้ทดลองเป็นผู้เรียก phase ถัดไป ไม่ให้โมเดลเรียกตัวเอง
REPLAN เมื่อพบข้อบกพร่องที่แก้ได้; หยุดเมื่อครบเกณฑ์ เพดานแก้ 2 รอบ งบหมด หรือข้อเดิมไม่คืบ
## Output
เขียนไฟล์ใหม่ภายใต้ 007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/ ตาม PHASE/ROUND ไม่ทับแผน/ผลก่อนหน้า
รักษา AC อื่นและรหัสเดิม; เปลี่ยนแผน AI ไม่ใช่เปลี่ยนสถานะออเดอร์
นับทุกการเรียกของ plan/execute/evaluate/แก้ในต้นทุนรวม ไม่ซ่อนค่า orchestration


## ข้อกำหนดการเก็บผลรันล่วงหน้า
ใช้สิทธิ์เขียนเฉพาะโฟลเดอร์ปัจจุบันและโฟลเดอร์ย่อยของขั้นนี้; ห้ามแก้ไฟล์อื่น ห้ามใช้ work/ ห้าม git add/commit/push ห้ามเรียก CLI หรือผู้ช่วยเพิ่ม
ทุก path หลักฐานที่ระบุใน prompt สัมพัทธ์จาก AI_Workflow_Engineering_for_SA/ ให้ resolve ../../../ จาก cwd ขั้นนี้ (ถ้าอยู่ขั้นย่อยให้เพิ่มระดับตามจริง)
ใช้ชื่อรหัสขั้นของแผนแบบ JOB- หรือ CHG- ห้ามใส่รหัสงานทีมภายใน ชื่อบัญชีจริง หรือ absolute path ลงเอกสาร
ไม่อ่าน HTML ขนาดใหญ่ของบทเรียน อ่านเฉพาะ snapshot UI ที่ระบุ
เครื่องมือ Codex CLI 0.154.0; โมเดล gpt-6-astra (ตาม flag ที่สั่ง CLI ไม่ยืนยันกลับ); effort high; เวลา/โทเคนผู้ทดลองจะอ่านจาก log หลังจบเอง ห้ามแต่ง

เรียกนี้ PHASE=evaluate ROUND=0 เท่านั้น อ่าน plan-round-0.md, plan-v4.json, impact-analysis-change.md, round-0/execution.md, ชิ้นงาน round-0/, round-0/tests.json และ round-0/ui-run-meta.json; tests.json เป็นผล Playwright จากผู้ทดลองภายนอกจริง
อ่าน ../shared-tests-v2.json, ../shared-tests-notes.md และ ../shared-test-baseline-dom.json เพื่อทราบขอบเขต tests และข้อจำกัดการตรึงชุดตรวจ (path สามไฟล์นี้อ้างจาก cwd ขั้นนี้)
ห้ามอ่านผล Single. สร้าง evaluation-round-0.md ใน cwd และ evaluate/summary.md ที่ CLI เก็บเท่านั้น ห้ามแก้คะแนน/แผน/ชิ้นงาน/tests
ตัดสิน COMPLETE หรือ STOP_WITH_GAPS ตามหลักฐานจริง มีช่องว่างให้ระบุชัด; pre-run จำกัด round 0 ตาม conditions จึงไม่เริ่มรอบแก้เอง
ผล UI ล่าสุดผ่าน 18 ตก 1 skip 0 เป็น fixture mock 19 กรณี ไม่ใช่ครบทุก AC; failure TS-US-09-101 ให้เก็บตามจริง; เกณฑ์เวลา 00/15/30/45 และการยืนยันออเดอร์หลังคำเตือนไม่ครบใน shared suite ให้ระบุยังไม่วัด ไม่อนุมาน PASS จาก source
ใช้เพียงเกณฑ์และหลักฐานจริง ตรวจ JSON schema ของ scenarios ที่ผลิตกับ runner โดยอ่านโค้ด runner ../006 ไม่ต้องรัน browser ซ้ำ; input source index ขาดรายละเอียดเดิมต้องถือเป็นข้อจำกัด
