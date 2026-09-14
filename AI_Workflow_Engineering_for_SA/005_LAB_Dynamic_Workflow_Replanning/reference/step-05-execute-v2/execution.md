# revise-ui — execution summary

STATUS: **EXECUTED — รอ Evaluator verify-ui; ไม่ใช่ PASS**. TASK_ID: revise-ui; RUN_ID: ui-v2-run; plan-v2; UTC: 2026-09-14T13:44:04.140341Z.

Gates: PLAN_READY และ FR/Flow/outline v2 PASS เอกสารที่ hash ตรง; F-01 closed ระดับเอกสาร. Baseline copy เท่ากับ hash ที่แผนอ้าง. รายละเอียด mapping 21 US → FR → Flow → UI, input hashes และ scope อยู่รายงานด้านล่าง.

| ไฟล์ที่สร้างจริง | SHA-256 |
|---|---|
| [ui-mockup-v2.html](/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/ui-mockup-v2.html) — 80,956 bytes | `249b98c493f4c1347efe36f8be059095ede9d3b23b76ada3b022cfc416c2a1cc` |
| [ui-contract-v2.md](/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/ui-contract-v2.md) | `40ad0ff84c423a225b1675bbc2a627390446b9ecfcbcbb4496a6f0605e675888` |
| [revise-ui.md](/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/execution/plan-v2/ui-v2-run/revise-ui.md) | `96cff4720cc3abc20467f760f2a826ff74f7ba6346b415f7dca0c170ea7d03ee` |

ไฟล์ที่สี่คือ summary นี้: /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/execution.md; ไม่มี self-hash. Plan JSON SHA-256 `8682dcba597fd36cadcf0a4724a9a75bd866f551b337281c663ee419c059c828`; plan Markdown `75c5e9b06c7e26fbf7174295d165fbae64be57ea8ff807b4d96884898296ea2c`. Input-set `70b0f1d8630f3f4eead1a7e75bbb26453483945e037113ec1104ee892d06a4f7`; full manifest อยู่ execution report.

เพิ่มทำไม่ได้รายรายการ → แจ้งลูกค้า/เปลี่ยนเมนู/คืนรายการ; คิวและยอดหลังปรับอ่าน snapshot/decision ชุดเดียวกัน. front-total คง snapshot เดิม; ใช้ front-adjusted-total/customer-adjusted-total/resolution-order-total สำหรับยอดใหม่. ปุ่มใหม่ใช้ data-id/data-item-id และ scope outer article[data-order-id] เท่านั้น ไม่เพิ่ม data-order-id ซ้ำใน kitchen-queue/front-orders.

Locators หลัก: btn-item-unavailable, customer-unavailable-alert, item-resolution, replacement-menu, btn-change-menu, btn-return-item, nav-capacity, capacity-start, capacity-end, capacity-limit, capacity-wait-minutes, btn-save-capacity, capacity-message. Contract รวม locators เพิ่มอื่น/ยอดปรับ/ประวัติ/ตัวเลือกและ payload/scope ครบ.

ความจุใช้ sim-clock +07:00 ตามคำสั่งรัน, seed เวลา 12:00 อยู่ในช่วง 11:30–13:30, N=5 ต่อ 15 นาทีเริ่ม 00/15/30/45. X=10 ค่าเริ่มจำลองปรับได้ มีป้ายชัดก่อนปุ่มยืนยัน และยังยืนยันได้; ไม่เพิ่มสูตร X/ETA. เก็บ CSS/seed และ business handlers เดิม; static selector inventory 77 literal selectors คงครบ; node --check ผ่าน syntax เท่านั้น.

NOT_RUN: browser/regression 19 checks, V2-A–F/5 จาก 5/US-21 N=5 สามรอบ, DOM/คลิก/ภาพ/responsive. ไม่มีภาพที่สร้าง. LAN/ระบบจริง/การชำระหรือโอนคืนเงินจริงยัง NOT_TESTED. กฎคืนเงินจริง/ส่วนต่าง/สูตร X/เขตเวลา/หมายเหตุ ก./ค./ช./สถานะ aggregate และ Q เดิมยังค้าง; สมมติฐาน fixture ไม่ใช่ AC. รายงานนี้ส่งต่อผู้ตรวจ ไม่รับรอง UI ผ่านและไม่แก้ plan snapshot/baseline.
