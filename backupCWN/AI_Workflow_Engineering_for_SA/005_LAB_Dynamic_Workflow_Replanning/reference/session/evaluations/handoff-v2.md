# Evaluator — evaluate-handoff / plan-v2

REVIEW_MODE: artifacts; TASK_ID: evaluate-handoff; RUN_ID: ui-v2-review; UTC: 2026-09-14T14:00:55.211785Z.
ผล **PASS — v2 ready for docs/mock เฉพาะขอบเขตการรันครั้งนี้**. Full contract/outline runtime coverage ยังไม่ครบ; AC ระบบจริง **NOT_TESTED**; การยืนยันกฎร้านที่ขาด **BLOCKED**. v3/reveal-2 ยังไม่เปิด.

ตรวจต่อจาก verify-ui ใน Evaluator session เดียว ใช้ outputs จริงครบทุก input ที่ evaluate-handoff ระบุ. ไม่ใช้ planned/needs_recheck ใน snapshot เป็นผลการทำงานปัจจุบัน และไม่เปลี่ยน plan JSON/Markdown.

| Gate | ผลและหลักฐาน |
|---|---|
| verify-plan | PASS/PLAN_READY เอกสารและ offline mock; plan-v2 JSON/Markdown/impact hashes ตรง plan-v2-review.md |
| audit-fr-baseline / verify-fr | PASS reuse audit hash จาก fr-v1-check.md/fr-v2-check.md; FR v2 ตรง target hash; 21×6 เซลล์ตรวจซ้ำตรงในรอบนี้ |
| verify-flow | PASS เอกสาร Flow/state/structure ตาม hash; F-01 closed เอกสาร และ status-sync รอบนี้ผ่าน offline mock |
| verify-test-outline | PASS เอกสาร test-outline-v2.md ตาม hash; เป็นแผนตรวจ ไม่ใช่ผ่านทุกกรณี runtime |
| revise-ui / verify-ui | canonical HTML/contract ตรง; ui-v2-check.md PASS จำกัด scope; wrapper จริง 1 ครั้ง regression 19/19, feature 8/8 = 6 สถานการณ์ N=5 ซ้ำ 3 รอบ |
| gate evidence/current inputs | PASS input hashes 41/41 และ bindings 12/12; แผน/inputs/outputs ไม่เปลี่ยนระหว่างตรวจ; ไม่มี cancelled dependency ที่ active รอ |

ตรวจต่อเนื่อง US-05/07/08/12/15/19 พร้อม US-11/16: คง source/AC/ตัวเลขเดิม; คิว/อาหารแยกเงินและโต๊ะ; front-total label “ยอด snapshot เดิม” แยก front-adjusted-total label “ยอดหลังปรับรายการ (จำลอง)”. คืนรายการไม่แปลว่าคืนเงินจริง; X=10/+07:00/[start,end)/รับใบที่หกเป็น fixture ยังไม่ยืนยันกฎร้าน. ไม่มีการสร้าง AC เพิ่ม.

ข้อค้างที่ต้องส่งด้วย: ui-v2-check.md ตาราง coverage แสดง US-09/14 ชุด 5/5 และ LAN, N=5 threshold ที่ 12:15/12:30 (driver ทั้งสามรอบเริ่ม 12:00), V2-A–F ขั้นละเอียด/หลาย item/5 snapshot/payment ค้างจ่าย/คำสั่งคืนซ้ำ, contract extras/keyboard/capacity direct route ยัง NOT_TESTED. ไม่รวม retry เป็นสถานการณ์ใหม่. ไม่มี FAIL ของ UI ในชุดที่รัน แต่ไม่รับรองส่วนที่ขาด.

กฎ/ระบบจริงยัง BLOCKED ตาม l-real-scope และ l-q-* ทั้งแปด: หมายเหตุ ก./ค./ช., สถานะ/พร้อมเสิร์ฟ/aggregate/ETA, payment/refund/ผู้อนุมัติ/ส่วนต่าง, mapping/Q-20, operations/สิทธิ์/สิ่งแวดล้อม, capacity/X/เขตเวลา/นับคืน/นโยบายเมื่อเต็ม. LAN/Wi-Fi/เงินจริง/ความปลอดภัยจริง/fullETA/ประวัติ 7 วัน/Ubuntu/ติดตั้ง/ถอดอินเทอร์เน็ตระบบจริง NOT_TESTED.

Downstream: ส่งชุด v2 เพื่อทบทวนเอกสารและสาธิต offline mock พร้อมขอบเขตข้างต้นได้ตามคำสั่งการรัน; ยังไม่พร้อมรับรองระบบจริง. ไม่เปิด reveal เพิ่ม ไม่สร้างแผน v3 แทน Planner. หาก scope/dependency เปลี่ยนส่ง Planner; การตรวจส่วนขาดให้ใช้ไฟล์ใหม่และคงหลักฐานนี้. แก้ UI/แผน 0 รอบ; เพดานแก้ไม่เกิน 2 รอบต่อปัญหาคงเดิม ไม่ใช่ AC ร้าน.

| Hash binding | SHA-256 |
|---|---|
| plan-v2.json | `8682dcba597fd36cadcf0a4724a9a75bd866f551b337281c663ee419c059c828` |
| plan-v2.md | `75c5e9b06c7e26fbf7174295d165fbae64be57ea8ff807b4d96884898296ea2c` |
| ui-v2-check.md (output verify-ui) | `295ecaad9d2b5673c8b2e585fba2c32ec877b1f98fa8e9e474d6c8deade463cd` |
| ui-v2-observations.json | `bf16ddef9c6ab46303702cbb18e5a3f0fe1bb1c0c969bc511b47fba825cec941` |
| Input-set 41 files | `c501d66b18468cc6097f4da66ae7aa31771209bc3b76a45dbd0e968afa464020` |
| canonical HTML | `249b98c493f4c1347efe36f8be059095ede9d3b23b76ada3b022cfc416c2a1cc` |
| canonical contract | `40ad0ff84c423a225b1675bbc2a627390446b9ecfcbcbb4496a6f0605e675888` |

สร้างจริง: reference/session/evaluations/handoff-v2.md. Manifest inputs และ runtime outputs อยู่ execution/ui-v2-evaluator-evidence.json และ execution/ui-v2-observations.json; hash รายงานนี้อยู่ reference/step-05-execute-v2/evaluation/evaluator.md.
