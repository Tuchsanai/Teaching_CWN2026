# Evaluator — ผลสองงาน

REVIEW_MODE: artifacts; TASK_ID: audit-fr-baseline; RUN_ID: audit-fr-review; plan-v1.
**verify-fr: PASS เฉพาะเอกสาร** — US 18 แถว/108 เซลล์ตรงต้นทาง, NFR 15 ข้อและ Q 18 รหัสครบ พร้อม locator และ hash; ไม่ใช่ผล checker upstream หรือระบบจริง.
**verify-flow: FAIL เฉพาะเอกสาร F-01 (US-11)** — FR-11/Flow ระบุจอหน้าร้านรับสถานะใหม่ แต่ coverage เชื่อมเฉพาะจอลูกค้า SCR-04 และจอครัว SCR-06; ไม่มีจอหน้าร้านที่อ้าง FR-11/MRG-05.
หลักฐาน F-01: baseline-filtered-v2/fr-nfr.md:29; flow.md:51,71,406,447,449,451; structure.md:22,69,71,73,223. ตารางอื่นคง AC/ข้อค้างเดิม; พบ 30 flows และ 17 transitions ที่เทียบกับ FR/สำเนา.
แก้เฉพาะจุดโดยสร้างฉบับใหม่ให้ screen/module/coverage เชื่อมจอหน้าร้านกับ FR-11/US-11 และ MRG-05 พร้อมเกณฑ์เดิม. ส่ง Planner วาง producer/outputs/dependency recheck เพราะ plan-v1 ไม่มีงาน revise และห้ามทับ baseline.
Downstream: verify-test-outline, verify-ui, evaluate-handoff BLOCKED รอ verify-flow PASS; draft-test-outline ทำต่อจาก FR ได้ตาม dependency. ไม่แก้ snapshot/artifacts; ตรวจครั้งแรก แก้ 0 รอบ เพดาน 2 รอบต่อปัญหาเป็นข้อตกลงการเรียน.
ข้อค้าง: MC-01–MC-03, Q/หมายเหตุ ก./ค./ช., เสร็จแล้ว–พร้อมเสิร์ฟ, PromptPay/เวลาเริ่ม, US-14/แมปซ้อน, initial/terminal/สิทธิ์/ติดตั้ง ยังไม่ยืนยัน; BLOCKED สำหรับรับรองกฎจริง.
Mock-up/ระบบจริง: NOT_TESTED — ไม่รัน browser, DOM/data-testid/click, LAN/โหลด/เวลา/ETA/สัดส่วน AC, security/log, Ubuntu/offline หรือชำระเงินจริง; UI อ่าน hash-only. ไม่อ่าน README/reveal/เว็บและไม่เรียก agent/CLI เพิ่ม.

Path ในตารางอ้างจากราก LAB; SHA-256 จาก bytes จริง. Hash ตัวรายงานนี้ตรวจหลังเขียน ไม่ฝัง self-hash.

| Plan / output ที่สร้างจริง | SHA-256 |
|---|---|
| reference/session/plan-v1.json (input) | `4bd023624fb2cb5c1ec9975528e8ffbcb6ac830cd40f9b61c5db28523ae25cfe` |
| reference/session/plan-v1.md (input) | `10f2d1da058fafe1a6ed75047ad157ab0694cb7ee40ddd89c91874fa4d3310ae` |
| reference/session/evaluations/fr-v1-check.md | `b533a2d6b8618f590d3de91bdc4250172ad8d987df6060860f16e0a672403c5a` |
| reference/session/evaluations/flow-v1-check.md | `43cd1d0cf505bb509d9453f060503c82ed300332324c9893168eb74f05a70141` |
| reference/session/evaluations/plan-v1/audit-fr-review-evidence.json | `c36f6c42ef89292bcd8cb4fa461bdd13c3331ad8215f9ef1624007cb040bfd1c` |
| reference/session/evaluations/plan-v1/audit-fr-review.md | `881d66a4ce0cffe9add96d75a2b9c1ce479c948a00c96e7639a710b84ed910ad` |

ไฟล์ที่ 5 ที่สร้างจริงคือ evaluator.md นี้ใน cwd ของการรัน. รายงานหลัก 51 บรรทัดและ evidence JSON มี input hashes ครบ 19 ไฟล์/ผลรายข้อ; hash ของ inputs คงเดิมหลังตรวจ. ไม่คัด source ทั้งชุดซ้ำหรือทับไฟล์เดิม.
