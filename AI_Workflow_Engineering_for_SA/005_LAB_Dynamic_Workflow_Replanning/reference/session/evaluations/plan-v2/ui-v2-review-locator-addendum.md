# แก้ locator ประกอบ ui-v2-check.md

REVIEW_MODE: artifacts; TASK_ID: revise-ui; RUN_ID: ui-v2-review; plan-v2.
UTC: 2026-09-14T14:01:33.717704Z. แก้ข้อผิดพลาดเลขบรรทัดรายงานรอบ 1; ไม่แก้ UI/แผน/ผลทดสอบหรือไฟล์เดิม.

การตรวจรายงานขั้นสุดท้ายพบ locator สี่ค่าชี้บรรทัดว่างถัดจากหลักฐาน ให้ใช้ตารางนี้แทนทุก occurrence ใน [ui-v2-check.md](../ui-v2-check.md):

| Locator เดิม | Locator ที่ถูกต้องใน reference/session/ui-contract-v2.md | เรื่อง |
|---|---|---|
| C:200 | C:199 | baseline smoke และ contract extras |
| C:202 | C:201 | V2-A–F / หลายรายการ / payment / snapshot |
| C:204 | C:203 | US-09/14 ชุด 5 จาก 5 / LAN |
| C:206 | C:205 | US-21 N=5 สามรอบและขอบหน้าต่าง |

ผลตรวจ/ข้อค้างไม่เปลี่ยน: PASS เฉพาะเอกสารและชุด offline mock 19/19 กับ 8/8; full contract/ระบบจริงยัง NOT_TESTED; กฎที่ขาด BLOCKED. [handoff-v2.md](../handoff-v2.md) ใช้ข้อจำกัดเดิมครบ. ไม่จำเป็นต้องรัน browser ซ้ำหรือส่ง Planner เพราะ scope/dependency ไม่เปลี่ยน.
รายงานเดิม SHA-256 `295ecaad9d2b5673c8b2e585fba2c32ec877b1f98fa8e9e474d6c8deade463cd`; contract SHA-256 `40ad0ff84c423a225b1675bbc2a627390446b9ecfcbcbb4496a6f0605e675888`. สร้างไฟล์ addendum นี้ใหม่เพื่อไม่ทับหลักฐานเดิม.
