# Execution — draft-test-outline

TASK_ID: `draft-test-outline`; RUN_ID: `test-outline-run`; Plan: `plan-v1`; UTC: `2026-09-14T12:55:42.047005Z`.
สถานะ: **EXECUTED — ทำเสร็จรอ Evaluator แยก session ไม่ใช่ PASS**.
Plan JSON SHA-256: `4bd023624fb2cb5c1ec9975528e8ffbcb6ac830cd40f9b61c5db28523ae25cfe`
Plan Markdown SHA-256: `10f2d1da058fafe1a6ed75047ad157ab0694cb7ee40ddd89c91874fa4d3310ae`
Input-set SHA-256: `257814459b92ee16a2b25e6bc86fa581f3f388f21faa42e82ccdaf1cf363b557`

งานที่ทำ: สร้าง `reference/session/test-outline-v1.md` ตาม output เดียวของ task; ตารางหนึ่งแถวต่อ US รวม 18 แถว มี locator US/FR/NFR/Q, AC เดิมตรงตัว, fixture/การกระทำ/expected mock, หลักฐานที่จะเก็บ, Flow mapping ระดับ artifact ที่ต้องตรวจต่อ และ UI source/selector. เพิ่มเงื่อนไขร่วม role/reset/selector scope/template และ responsive ตามเหตุผล task ไม่เพิ่มกฎธุรกิจ.

Gate ที่ตรวจจริง: พบเฉพาะคู่ plan-v1; schema Draft7 + date-time, unique task ID, dependency มีจริง/ไม่มีวงจร และ strings ของ JSON อยู่ใน Markdown ครบ. TASK_ID มีหนึ่ง create/planned; ไม่ใช่ reused/cancel/verify. PLAN_READY/PASS ผูก hashes ที่เทียบได้ 16/16 แถว; verify-fr PASS เฉพาะเอกสารผูก hashes 10/10 แถว; audit output hash ตรงทั้งรายงาน execution และ verify-fr. Manifest baseline bytes ตรง 10/10; input reuse ที่เกี่ยวข้อง 6/6 ตรง source_version. ไม่ตั้ง TTL ที่ไม่มีหลักฐาน; scope ผลตรวจยังเป็นเอกสาร. l-plan-gate/l-check-gates ปลดสำหรับ dependency audit-fr-baseline/verify-fr ของงานนี้เท่านั้น; ข้อค้างธุรกิจไม่บล็อกร่างตาม PLAN_READY. ไม่ใช้ verify-flow เป็นฐานตัดสินหรืออ้าง PASS ของงานนั้นในรอบนี้.

ผลตรวจเบื้องต้น Executor: coverage US 18/18 ไม่ซ้ำตรง task, AC เซลล์ตรงตัว 18/18, FR/source locators ตรงรหัส; source selectors/template อ้างจาก HTML/contract; output ใหม่ไม่มีไฟล์ก่อนสร้าง. การตรวจเหล่านี้ไม่ใช่ Evaluator PASS หรือผล runtime. ตรวจ input hashes ก่อนเขียนและหลังเขียนอีกครั้ง.

Output: `reference/session/test-outline-v1.md`
Output SHA-256: `6bdeccb7cf14fcdf03f0fa56578e1595c1ec3ea2dda67c3f74d4bba4c07ae18c`

ข้อค้าง: Q 18 รหัสตาม FR, หมายเหตุ ก./ค./ช., MC-01–MC-03, เสร็จแล้ว/พร้อมเสิร์ฟ, สูตร ETA/ประชากร, PromptPay ปิดกับสองวิธี, วัตถุดิบซ้อน/แมปเปลี่ยน/US-20 อ้าง US-14, session/เลขข้ามวัน/หน่วย MB/สิทธิ์/สภาพติดตั้ง. คง OPEN/HUMAN_REQUIRED ไม่เติมคำตอบ. Flow mapping เป็น F* ระดับ artifact จาก audit ต้องตรวจใหม่; UI mapping ยังไม่ผ่าน DOM/browser. ไม่พบเหตุให้เปลี่ยน scope/dependency; หากพบภายหลังส่ง Planner ไม่แก้ snapshot.

NOT_TESTED: browser/selector/click/edge/responsive, Flow/state/structure เชิงเนื้อหา, LAN/Wi-Fi/QR/โหลด/เวลาและสัดส่วนจริงทุก AC, server log/ETA/ข้อมูล 7 วัน, security/log/การชำระเงินจริง, Ubuntu/ตัวติดตั้ง/ออฟไลน์ระบบจริง. ทุกกรณีใน outline เป็น NOT_TESTED (NOT_RUN). ผล UI upstream 19/19 เป็นประวัติเท่านั้น. ไม่เปิด reveal/README หลักของ LAB/เว็บ ไม่เรียก agent/CLI เพิ่ม. อ่าน input/README.md ตาม Input ที่อนุญาตเพื่อกฎเลือกแผน ไม่ตามลิงก์.

Downstream: จัดชุดส่ง `verify-test-outline` ให้ Evaluator แยก session พร้อมร่าง/รายงานนี้และ inputs ตาม task; ผู้ตรวจต้องตรวจ verify-fr/verify-flow และ hashes ปัจจุบันก่อนผลตรวจ. ต่อด้วย verify-ui และ evaluate-handoff ตามทุก dependency. ไม่สร้างผล Evaluator และไม่แก้ status ใน plan-v1.

Input hashes (path จากราก LAB; input-set = SHA-256 ของ UTF-8 แต่ละบรรทัด path + TAB + sha256 + LF เรียง path; ไม่รวม outputs):

| Path | SHA-256 | การใช้ |
|---|---|---|
| `input/README.md` | `eca3997d869894c7244c3ebea2320e688832aa4e670598feed84a36058e6eaf1` | อ่านเนื้อหาหรือส่วนที่เกี่ยวข้อง + hash |
| `input/plan.schema.json` | `cea51a142b808b2c3045994baa68a45d98d280f9d9c5a55962c2015de365431c` | อ่านเนื้อหาหรือส่วนที่เกี่ยวข้อง + hash |
| `reference/session/evaluations/fr-v1-check.md` | `b533a2d6b8618f590d3de91bdc4250172ad8d987df6060860f16e0a672403c5a` | อ่านเนื้อหาหรือส่วนที่เกี่ยวข้อง + hash |
| `reference/session/evaluations/plan-v1-review.md` | `f2facd03b3cd1f74969c110bfc336226b7d331f65042e51b036b5995166b3eb1` | อ่านเนื้อหาหรือส่วนที่เกี่ยวข้อง + hash |
| `reference/session/evaluations/plan-v1-validation.json` | `a93dde889286710ef1217a542ab365b4fa27db3ca9e5473f9ed6dc57b83c5b1d` | hash-only: ผูก gate/manifest ไม่ตรวจเนื้อหา |
| `reference/session/execution/fr-baseline-audit-v1.md` | `78f8ce610526fdaa3e7911b3765fbff8246ea223d9772611e370bb42d5374175` | อ่านเนื้อหาหรือส่วนที่เกี่ยวข้อง + hash |
| `reference/session/execution/plan-v1/audit-fr-baseline-run/audit-fr-baseline.md` | `42318bb248f2a2e4b675cbdd5104f2bc70ea401ebd4d83aa29076b65113c77b8` | อ่านเนื้อหาหรือส่วนที่เกี่ยวข้อง + hash |
| `reference/session/plan-v1.json` | `4bd023624fb2cb5c1ec9975528e8ffbcb6ac830cd40f9b61c5db28523ae25cfe` | อ่านเนื้อหาหรือส่วนที่เกี่ยวข้อง + hash |
| `reference/session/plan-v1.md` | `10f2d1da058fafe1a6ed75047ad157ab0694cb7ee40ddd89c91874fa4d3310ae` | อ่านเนื้อหาหรือส่วนที่เกี่ยวข้อง + hash |
| `reference/step-00-input/baseline-filtered-v2/flow-check.json` | `3be4ccd3d045951e7c69e523e6ce2dfab052d45ece39d453741f310435d1c700` | hash-only: ผูก gate/manifest ไม่ตรวจเนื้อหา |
| `reference/step-00-input/baseline-filtered-v2/flow.md` | `d0a5fcd029f4f315a02fcd2c057a44907bdf7362fbce17b8664a75b82773595d` | hash-only: ผูก gate/manifest ไม่ตรวจเนื้อหา |
| `reference/step-00-input/baseline-filtered-v2/fr-check.json` | `1b0c604da9288ce926ba4c98eb258107b130f309f85b1ee96403e02ba0d0f98c` | hash-only: ผูก gate/manifest ไม่ตรวจเนื้อหา |
| `reference/step-00-input/baseline-filtered-v2/fr-nfr.md` | `da31640e540b825d4fec555627ea098f092daf4243d5d304fd4c32ae6db734cd` | อ่านเนื้อหาหรือส่วนที่เกี่ยวข้อง + hash |
| `reference/step-00-input/baseline-filtered-v2/input-audit.md` | `d4100680ed1f31ea3351144f202f85343fb47a23acfa0305116731ab8bb1bbd8` | อ่านเนื้อหาหรือส่วนที่เกี่ยวข้อง + hash |
| `reference/step-00-input/baseline-filtered-v2/provenance.md` | `8059b1b47647d690ed7a73e6b4b9751e209edb3905868a4729269fb79330739a` | อ่านเนื้อหาหรือส่วนที่เกี่ยวข้อง + hash |
| `reference/step-00-input/baseline-filtered-v2/state-machine.md` | `b4bc79de9e95f1526ca05326211a6025981b0420f3681b574e37189319f35adf` | hash-only: ผูก gate/manifest ไม่ตรวจเนื้อหา |
| `reference/step-00-input/baseline-filtered-v2/structure.md` | `fc8facf9088ad320d8dc3a7157edc14b337c1cb7081c3b098bcf91ceab08c560` | hash-only: ผูก gate/manifest ไม่ตรวจเนื้อหา |
| `reference/step-00-input/baseline-filtered-v2/ui-check.json` | `c09bf23c92abf0cd9c570f71ff890c1b572f8846c4d2ff8f5d2c3323be448af7` | อ่านเนื้อหาหรือส่วนที่เกี่ยวข้อง + hash |
| `reference/step-00-input/baseline-filtered-v2/ui-contract.md` | `294b660d2e39b3745344f225400eee57c02c25b6efb108a3a7ecce7cdd060e68` | อ่านเนื้อหาหรือส่วนที่เกี่ยวข้อง + hash |
| `reference/step-00-input/baseline-filtered-v2/ui-mockup.html` | `d2b7bfa0cff5700d3ca07f611c03cfa0304c54eafb51387f125e95edd11f7803` | อ่านเนื้อหาหรือส่วนที่เกี่ยวข้อง + hash |
| `reference/step-00-input/baseline-filtered-v2/us-initial.md` | `56a439f6e22f4a8d17f552b023c3c8fe61556f5bd31f1f1e9b70c1f9da6049d2` | อ่านเนื้อหาหรือส่วนที่เกี่ยวข้อง + hash |

Hash ของรายงาน execution นี้บันทึกหลังสร้างใน `reference/step-02-execute-v1/draft-test-outline/execution.md`; ไม่ใส่ self-hash ที่วนกลับ.
