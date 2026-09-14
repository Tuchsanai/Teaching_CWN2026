# Evaluator — plan-v2
REVIEW_MODE: plan; TASK_ID: all; VERIFY_TASK: verify-plan; RUN_ID: plan-v2-review.
UTC: 2026-09-14T13:06:34.239659Z; ตรวจครั้งที่ 1; แก้แผน/ชิ้นงาน 0 รอบ.
ผล: **PLAN_READY เฉพาะแผนงานเอกสาร/offline mock ตาม gates; verify-plan = PASS**.
การยืนยันกฎร้าน/ระบบจริง: **BLOCKED**; ผลนี้ไม่ใช่ PASS ของชิ้นงาน v2 หรือ AC ระบบจริง.
Path จากราก LAB; S=reference/session; B=reference/step-00-input/baseline-filtered-v2; R=reference/step-03-reveal-1/reveal-1.md; P=S/plan-v2.md; I=S/impact-analysis-v2.md.

วิธีตรวจจริง: Python jsonschema Draft7Validator+FormatChecker, duplicate-key parser, UTC, graphlib DAG, producer/ancestor, scoped Markdown tables, SHA-256 จาก bytes และอ่านเหตุผล/ขอบเขต/หลักฐาน.
ใช้ verify-fr v1 ตาม hash; ไม่ audit baseline ทุกเซลล์ซ้ำ. ตรวจเนื้อหาที่อนุญาตและ hash dependency; ไม่เปิด README/reveal-2/เว็บ/ต้นทางนอกชุด ไม่เรียก agent/CLI เพิ่ม.
หลักฐานละเอียด: S/evaluations/plan-v2/plan-v2-review-evidence.json (checks และ input hashes 29 ไฟล์); ตรวจ input hashes ซ้ำก่อนเขียนตรงครบ.

| รายการ | ผล | หลักฐาน / locator และขอบเขต |
|---|---|---|
| รุ่น/schema/UTC | PASS | plan-v2 เป็นรุ่นเลขสูงสุดใน session; draft-07+date-time ผ่าน ไม่มี duplicate key; created_at ลงท้าย Z/offset 00:00 |
| Unique IDs / DAG | PASS | tasks 11, decisions 15, limits 14 ไม่ซ้ำ; 25 edges ไม่มี target หาย/self/cycle; JSON #/tasks, #/limits |
| Producer/consumer | PASS | inputs ที่ผลิตในแผนมี producer ใน ancestor; external inputs มีครบ; 16 outputs ไม่ซ้ำ มีอยู่เดิมเฉพาะ audit v1 ที่ใช้ประวัติ done; P:29–39 |
| JSON/Markdown/diff | PASS | เทียบ title/kind/status/input/output/dependency/US/reason ทุก task, decision/authority, reuse/hash/evidence และ limits/boolean/targets; P:13–99; metadata ตรง |
| เพิ่ม/แยก/จัดลำดับ | PASS | เพิ่ม revise-fr/flow/ui จาก reveal-1 และ F-01; draft-test-outline create→revise; คง 8 ID เดิม ถอน audit→verify-plan เพราะ gate v1 จบแล้ว; P:13–23,48,50 |
| Cancel consistency | PASS | ไม่มี kind=cancel หรือ status=cancelled; ไม่มี active task รอ cancelled; ไม่จำเป็นต้องยกเลิกงานเดิมที่ยังต้องทำ |
| Reveal/US/AC | PASS | R:12–14 → I:15–17 ตรงทั้ง 3 แถว × 6 คอลัมน์; tasks อ้างเฉพาะ 21 US ที่เปิด; 10 วินาที/LAN/5 จาก 5 และ 15 นาที/00/15/30/45/N=5/3 จาก 3 คงเดิม |
| ผลกระทบต่อเนื่อง | PASS | I:24–31,35–40 ครอบ US-05/07/08/12/15/19 และ US-11/06/13/20/25 เท่าที่เกี่ยว; แยกคืนรายการจากปิดขาย และราคาเดิมจากราคา catalog |
| Reuse / อายุหลักฐาน | PASS จำกัดขอบเขต | manifest 10/10, reuse 15/15, bindings รายงานเดิม 55/55 และ Planner ที่เกี่ยว 25/25 ตรง; P:66–80; ไม่ตั้ง TTL เองและไม่ยก PASS v1 เป็น PASS v2 |
| สถานะจากผลจริง | PASS | fr-v1-check.md:4 PASS → audit done; flow-v1-check.md:4 FAIL และ test-outline-v1-check.md:4 BLOCKED → needs_recheck; P:50; EXECUTED ไม่เท่ากับ PASS |
| F-01 แผนแก้ | PASS ระดับแผน; F-01 OPEN | flow-v1-check.md:35–40 → P:17–20,105 / I:27,37; producer แก้ US-11/FR-11/MRG-05→module/screen หน้าร้านและ coverage ให้ Flow/state/structure ตรง |
| Gates | PASS ระดับแผน | P:47,86–89; รอ artifact+PASS ผูก hash; F-01 ต้องปิดโดย verify-flow ก่อน outline/UI; ยังไม่ปลด l-check-gates/l-browser |
| แยกสถานะ | PASS ระดับแผน | P:49 / I:38–39; รายการ/ออเดอร์/ชำระเงิน/โต๊ะ แยกจาก AI task status; ไม่เปลี่ยนจ่ายแล้วเป็นค้างจ่ายเอง |
| UI contract / วิธีตรวจ | PASS ระดับแผน; runtime NOT_TESTED | P:37–38,71–72,89; คง data-testid/fixture เดิม เพิ่ม contract v2; รัน browser/network off/reset/roles/scoped selectors/responsive ใน verify-ui ภายหลัง |
| ระบบจริง | BLOCKED / NOT_TESTED | P:88,91–99 / I:65–68; ข้อค้างธุรกิจยังบล็อกการรับรองจริง และไม่มีการรันระบบจริงในรอบนี้ |

| Human-required → blocking limit | ขอบเขตที่ยังไม่ยืนยัน |
|---|---|
| d-human-status → l-q-status | mapping เสร็จแล้ว/พร้อมเสิร์ฟ, aggregate และ transition |
| d-human-eta → l-q-eta | หมายเหตุ ช., ค่าเฉลี่ย/ประชากร/ปัดเศษ/ไม่มีประวัติ |
| d-human-payment → l-q-payment | หมายเหตุ ก., สองวิธีจ่าย/PromptPay ปิด/จุดเริ่ม 10 นาที |
| d-human-mapping → l-q-mapping | หมายเหตุ ค., วัตถุดิบซ้อน และ US-20 อ้าง US-14 |
| d-human-operations → l-q-operations | QR/เลข/ข้ามวัน/log/ปิดโต๊ะ/คำสั่งชนกัน |
| d-human-environment → l-q-environment | ชุดทดสอบ/MB/สิทธิ์ Unknown/Ubuntu |
| d-human-refund → l-q-refund | คืนเงินจริง/ผู้อนุมัติ/ส่วนต่าง/คืนซ้ำ/การนับรายงาน |
| d-human-capacity → l-q-capacity | สูตร X/ช่วงเวลา/นับคืน/เปลี่ยน N/เตือนหรือห้ามยืนยัน |
ทั้ง 8 กลุ่มมี blocking=true และ affected_tasks ครบสาย revise-fr ถึง evaluate-handoff; JSON #/decisions, #/limits; P:51–58,92–99.
ข้อค้างเหล่านี้ไม่บล็อกเอกสาร/offline mock ที่ติดป้ายสมมติฐานตาม l-real-scope; ไม่พบการตัดสินกฎร้านแทนมนุษย์; ช่องเพื่อ US-12 ยังคงปิด.

Downstream: หลังบันทึกผลนี้ ปลดเฉพาะ l-plan-gate ให้ revise-fr เริ่มได้โดยใช้ audit v1 ที่ผ่านตาม hash.
ลำดับต่อ: revise-fr → verify-fr → revise-flow → verify-flow (ปิด F-01) → draft-test-outline → verify-test-outline → revise-ui → verify-ui → evaluate-handoff.
งานหลัง revise-fr ยังรอ inputs/PASS ของรุ่น v2; ห้ามส่งมอบก่อนผลครบ. ไม่แก้ snapshot JSON/Markdown หรือปิด F-01 ด้วยผลตรวจแผน.
ข้อบกพร่องแผนที่ต้องแก้ก่อนเริ่ม: ไม่พบ. F-01 เดิมให้แก้ module/screen/coverage ใน outputs v2 แล้วตรวจใหม่ตาม flow-v1-check.md:38; ไม่ใช้สถานะเงินแทนสถานะอาหาร.
หาก scope/dependency เปลี่ยน ส่ง Planner สร้างรุ่นใหม่; จำกัดแก้ไม่เกิน 2 รอบต่อปัญหา ไม่คืบให้หยุดพร้อมหลักฐาน; เป็นข้อตกลงการเรียน ไม่ใช่ AC ร้าน.
NOT_TESTED: ชิ้นงาน v2, browser/DOM/click/responsive, LAN/Wi-Fi/โหลด/สัดส่วน AC/ETA/security/log/Ubuntu/ติดตั้ง/ถอดอินเทอร์เน็ต/เงินจริง; ไม่มี browser run ในการตรวจแผน.
สร้างจริง: S/evaluations/plan-v2-review.md (output verify-plan), S/evaluations/plan-v2/plan-v2-review.md (รายงานรัน), evidence JSON ที่ระบุข้างต้น และ reference/step-04-plan-v2/evaluation/evaluator.md; ไม่ทับไฟล์เดิม.

| Plan / input hash | SHA-256 |
|---|---|
| S/plan-v2.json | 8682dcba597fd36cadcf0a4724a9a75bd866f551b337281c663ee419c059c828 |
| S/plan-v2.md | 75c5e9b06c7e26fbf7174295d165fbae64be57ea8ff807b4d96884898296ea2c |
| S/impact-analysis-v2.md | b4b5dcfbe1d03d1e31d59758b2a9476cecf00b65b0226914ac29f199894ecfb3 |
| input/plan.schema.json | cea51a142b808b2c3045994baa68a45d98d280f9d9c5a55962c2015de365431c |
| Input-set: path+TAB+SHA256+LF เรียง path ของ 29 ไฟล์ใน evidence | 486f14df5d3d1267a537d7f470241aadcee748e92ebb094b8b29740608f07e8c |
| Output evidence JSON | 66711881302f8d765012d237d9ffca437816b5e7ac6f25ec58c7cf90d72d1e8a |
Output hashes ของรายงาน Markdown อยู่ evaluator.md หลังเขียน; ไม่ใส่ self-hash ที่วนกลับ.

| Output Markdown | SHA-256 |
|---|---|
| reference/session/evaluations/plan-v2-review.md | 470d9248beca3760f63b1df7b54b5bcc24fc18cce5c1994ab3adebcf8403cd0e |
| reference/session/evaluations/plan-v2/plan-v2-review.md | 470d9248beca3760f63b1df7b54b5bcc24fc18cce5c1994ab3adebcf8403cd0e |
