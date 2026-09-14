# Executor — draft-test-outline

TASK_ID: draft-test-outline; RUN_ID: outline-v2-run; PLAN: plan-v2; UTC: 2026-09-14T13:29:21.921268Z
STATUS: **EXECUTED — รอ Evaluator; ไม่ใช่ PASS**.

สร้างจริงเพียง 2 ไฟล์ใน reference/step-05-execute-v2/draft-test-outline/: test-outline-v2.md และ execution.md นี้. ใช้ข้อกำหนดเฉพาะรันอ้างอิงที่ระบุ “ใช้แทนข้อกำหนด path ด้านบน”; จึงไม่สร้าง S/test-outline-v2.md หรือ S/execution/plan-v2/outline-v2-run/draft-test-outline.md. ส่งตำแหน่งจริงให้ Evaluator ใช้แทน path output ใน snapshot รอบนี้; ไม่มีการแก้ plan JSON/Markdown หรือหลักฐานเดิม.

## Gates และหลักฐาน

- ตรวจรายชื่อเฉพาะ S/plan-v*: สูงสุด v2 คู่ JSON/Markdown ครบ ไม่มีรุ่นใหม่ค้าง; JSON duplicate-key parser, Draft7Validator+FormatChecker ผ่าน; 11 task ID ไม่ซ้ำ dependency มีจริง/ไม่ชี้ตัวเอง/ไม่รอ cancelled และ DAG ไม่มีวงจร. พบ draft-test-outline หนึ่งรายการ kind=revise/status=needs_recheck ไม่ใช่ cancel/verify/reused.
- PLAN_READY/verify-plan PASS จาก S/evaluations/plan-v2-review.md. คำนวณ SHA-256 ผูก manifest review-evidence ตรง 29/29 รวมคู่แผน/impact/schema; ใช้ผลผู้ตรวจเดิมสำหรับความสอดคล้องคู่แผนเต็ม ไม่อ้างประเมินแผนใหม่.
- depends_on verify-fr: S/evaluations/fr-v2-check.md PASS เฉพาะเอกสาร; input/target bindings ตรง 15/15. revise-fr EXECUTED มี output FR v2 และ hash ตรงรายงาน producer.
- depends_on verify-flow: S/evaluations/flow-v2-check.md และ plan-v2/flow-v2-review-evidence.json PASS_DOCUMENTS_ONLY, F-01=closed_document_traceability_only; manifest ตรง 26/26. Flow/state/structure v2 มีจริงและ hash ตรง producer EXECUTED ครบ 3 ไฟล์ รวม FR เป็น 4/4. ผลตรวจปลด gate เอกสารสำหรับงานนี้โดยตรง; ไม่ใช้ PASS v1 แทน v2.
- Reuse hash ของร่าง v1/ผลตรวจ v1, US ตั้งต้น, reveal-1 และ C ตรงแผน/หลักฐาน. ร่าง v1 และ C disposition=recheck; ใช้ AC/fixture เป็นฐานแล้วแทน mapping F* ด้วย F/M/T v2. ไม่ถือว่า v1 BLOCKED กลายเป็นผ่าน และไม่อ้างว่ารัน HTML.
- l-plan-gate/l-check-gates ปลดเฉพาะร่างเอกสารตามผลข้างต้น; l-real-scope/l-q-status/eta/payment/mapping/operations/environment/refund/capacity ยังบล็อกกฎหรือระบบจริง แต่อนุญาตเอกสารติดป้ายสมมติฐาน. l-browser ไม่ผูก draft-test-outline. ไม่มี upstream/approval ค้างที่บล็อกงานนี้ในขอบเขตที่ทำ.

## งานที่ทำและผลตรวจเบื้องต้น

ปรับร่างเป็น 21 US; คง AC 18 เดิม เพิ่ม AC ของ US-09/14/21 จาก reveal ที่ trigger อนุญาต. แก้ F-01 ครัว→OrderEvent/order_state→MOD-06/SCR-08 สถานะอาหารแยกเงิน; เพิ่มทำไม่ได้→แจ้ง→เปลี่ยน/คืน→ครัว/ยอดหน้าร้าน และคืนซ้ำไม่หักซ้ำแบบสมมติฐาน mock. คง snapshot ราคาเดิม/ชุด 5 ใบ; N=5 มีแผน 3 รอบและรอยต่อ 00/15/30/45 แสดงก่อนยืนยัน ไม่เพิ่มกฎห้ามสั่ง. แยก item/order/payment/table/capacity จาก AI task status.

ตรวจเอกสารด้วย Python ก่อนเขียน: source US→ตาราง US ใน FR v2 ตรง 21×6=126 เซลล์; AC ร่าง v1 ตรง source 18/18; AC ร่าง v2 ตรง source 21/21 เซลล์และ scope ตรง task; Flow coverage 21/21 ใช้รหัส/หน้าจอจาก F; ตาราง N=5 มี 3 รอบและผล NOT_TESTED. ตรวจอ่าน mapping M/T และป้ายสมมติฐาน/ข้อค้าง; เป็น preliminary checks ของ Executor ไม่ใช่ผล PASS ของ verify-test-outline. ตรวจ input hashes ซ้ำก่อนเขียนตรงครบ; ปลายทางสองไฟล์ยังไม่มี ใช้ exclusive create ไม่เขียนทับ.

## ข้อค้างและส่งต่อ

ยังค้าง ก./ค./ช., Q เดิม 18 ข้อและ Q-V2-REFUND/STATE/CAPACITY, MC-01–03, mapping เสร็จแล้ว/พร้อมเสิร์ฟ/aggregate, คืนเงินจริง/ส่วนต่าง/ผู้อนุมัติ/ซ้ำ, สูตร X/หน้าต่าง/นับคืน/เปลี่ยน N, US-20 อ้าง US-14 และ UI v2/selector ใหม่ที่ยังไม่ผลิต. รายละเอียดใน outline และ V:170–189,216–218; ไม่มีคำยืนยันธุรกิจใหม่.

NOT_TESTED: mock/browser/DOM/คลิก/roles/reset/responsive ทุกกรณี; LAN/Wi-Fi/QR/มือถือหลายเครื่อง/เวลา/โหลด/concurrency/สัดส่วนทุก AC; ETA/server log/security; Ubuntu/ติดตั้ง/เก็บข้อมูล/ถอดอินเทอร์เน็ต; เงินจริง. ไม่ใช้บัญชีจริง/บริการเงินจริง. ไม่เปิด reveal-2, README หลัก LAB, เว็บ หรือแหล่ง source นอกชุด; อ่าน input/README.md ที่ระบุใน inputs เท่านั้น. หลักฐาน transitive นอก task อ่านเฉพาะ bytes เพื่อ hash ไม่ใช้เติมกฎ.

จัดชุดส่งต่อให้ Evaluator verify-test-outline: output จริงด้านล่าง + report นี้ + task inputs/hash manifest. ต้องตรวจเป็น session แยกและออก S/evaluations/test-outline-v2-check.md; รอบนี้ไม่เรียก agent/AI CLI/ผู้ตรวจเพิ่มและไม่รับรองตนเอง. Downstream revise-ui → verify-ui → evaluate-handoff ยังรอ gates; UI ต้องผูก selectors ใหม่กับ contract v2 ตรวจ regression เดิม/ยอด/สถานะ/ความจุ และจำนวนตัวอย่างจริงยังไม่ทดสอบ. ไม่พบเหตุเปลี่ยน dependency/scope; หากพบภายหลังให้ Planner สร้าง snapshot รุ่นใหม่.

## Output และ hashes

| ไฟล์จริง | SHA-256 |
|---|---|
| reference/step-05-execute-v2/draft-test-outline/test-outline-v2.md | `50b3c1a7e68a5ca3a56cff2939f55cd591ae2c60c63bd3577625bc442dd2b763` |
| reference/step-05-execute-v2/draft-test-outline/execution.md | ไม่ใส่ self-hash ที่วนกลับ; คำนวณหลังเขียนในผลเครื่องมือ |

Plan JSON SHA-256: `8682dcba597fd36cadcf0a4724a9a75bd866f551b337281c663ee419c059c828`
Plan Markdown SHA-256: `75c5e9b06c7e26fbf7174295d165fbae64be57ea8ff807b4d96884898296ea2c`
Input-set SHA-256: `ea067c464f864d5f4374166e9b69699ccd015fcf4de3e70d1f90c896670a1cac` = UTF-8 ของ relative path + TAB + SHA256 + LF เรียง path ของตารางต่อไป; รวมไฟล์อ่านจริงและ hash-only สำหรับผูก dependency. ไม่ได้ตรวจเนื้อหาประวัติทุกไฟล์ซ้ำ.

| Input path จากราก LAB | SHA-256 | การใช้ |
|---|---|---|
| input/README.md | `eca3997d869894c7244c3ebea2320e688832aa4e670598feed84a36058e6eaf1` | task input / gate content |
| input/plan.schema.json | `cea51a142b808b2c3045994baa68a45d98d280f9d9c5a55962c2015de365431c` | task input / gate content |
| reference/session/evaluations/flow-v1-check.md | `43cd1d0cf505bb509d9453f060503c82ed300332324c9893168eb74f05a70141` | hash-only dependency |
| reference/session/evaluations/flow-v2-check.md | `8eb49dba6953c6d63a3eb833f54a67c74bad9b42978a83ea97408d21e18f8c1d` | task input / gate content |
| reference/session/evaluations/fr-v1-check.md | `b533a2d6b8618f590d3de91bdc4250172ad8d987df6060860f16e0a672403c5a` | hash-only dependency |
| reference/session/evaluations/fr-v2-check.md | `b21ee2b862656cf871d69117c44d2d5168154360da088c929bf87e033151819b` | task input / gate content |
| reference/session/evaluations/plan-v1-review.md | `f2facd03b3cd1f74969c110bfc336226b7d331f65042e51b036b5995166b3eb1` | hash-only dependency |
| reference/session/evaluations/plan-v1-validation.json | `a93dde889286710ef1217a542ab365b4fa27db3ca9e5473f9ed6dc57b83c5b1d` | hash-only dependency |
| reference/session/evaluations/plan-v2-review.md | `470d9248beca3760f63b1df7b54b5bcc24fc18cce5c1994ab3adebcf8403cd0e` | task input / gate content |
| reference/session/evaluations/plan-v2-validation.json | `a5b468a83cb2dde8ac5489f0c53214d28c68d41350cdd20e91e6a5c310bb25f3` | hash-only dependency |
| reference/session/evaluations/plan-v2/flow-v2-review-evidence.json | `b88498fd4c385582fbe9c52a3746e9d948944c3bb772fc880c6c9b9c88702f14` | task input / gate content |
| reference/session/evaluations/plan-v2/plan-v2-review-evidence.json | `66711881302f8d765012d237d9ffca437816b5e7ac6f25ec58c7cf90d72d1e8a` | task input / gate content |
| reference/session/evaluations/test-outline-v1-check.md | `ea6c1f13c350bd5103493061d8b14fba8115cba46a8b900df42ec0445a1aa9a2` | task input / gate content |
| reference/session/execution/fr-baseline-audit-v1.md | `78f8ce610526fdaa3e7911b3765fbff8246ea223d9772611e370bb42d5374175` | hash-only dependency |
| reference/session/execution/plan-v1/audit-fr-baseline-run/audit-fr-baseline.md | `42318bb248f2a2e4b675cbdd5104f2bc70ea401ebd4d83aa29076b65113c77b8` | hash-only dependency |
| reference/session/execution/plan-v1/test-outline-run/draft-test-outline.md | `6ac65ca1a2cd45d5034c299677eab8b8545dcb6ac2257aada1c27cc0643814f8` | hash-only dependency |
| reference/session/execution/plan-v2/flow-v2-run/revise-flow.md | `860a4f6b24b83172708864633dba4368771d76473c3f8dc11e7d975e9f84f0a7` | task input / gate content |
| reference/session/execution/plan-v2/fr-v2-run/revise-fr.md | `571c4226e328461c807411303a66737876618d768bcbc19d261b76a32dfd745b` | task input / gate content |
| reference/session/flow-v2.md | `8fe7983eb45a7222424c7fafe34adf78874da75e7e7cf3ab013d4955d1159f9c` | task input / gate content |
| reference/session/fr-nfr-v2.md | `2cbdde11bb3fd5e62f338a1ea74f65d11112f3ea56e8a10ed9d24b08a1dcf0bb` | task input / gate content |
| reference/session/impact-analysis-v2.md | `b4b5dcfbe1d03d1e31d59758b2a9476cecf00b65b0226914ac29f199894ecfb3` | hash-only dependency |
| reference/session/plan-v1.json | `4bd023624fb2cb5c1ec9975528e8ffbcb6ac830cd40f9b61c5db28523ae25cfe` | hash-only dependency |
| reference/session/plan-v1.md | `10f2d1da058fafe1a6ed75047ad157ab0694cb7ee40ddd89c91874fa4d3310ae` | hash-only dependency |
| reference/session/plan-v2.json | `8682dcba597fd36cadcf0a4724a9a75bd866f551b337281c663ee419c059c828` | task input / gate content |
| reference/session/plan-v2.md | `75c5e9b06c7e26fbf7174295d165fbae64be57ea8ff807b4d96884898296ea2c` | task input / gate content |
| reference/session/state-machine-v2.md | `efe13a4cbb843c056884478fa8e5a0ab201c9641a579ae355cedb07867218d0a` | task input / gate content |
| reference/session/structure-v2.md | `f1a935fc0cf2779d225ce050a12b5df108c53a149fa0885ac7ce78828ae2290d` | task input / gate content |
| reference/session/test-outline-v1.md | `6bdeccb7cf14fcdf03f0fa56578e1595c1ec3ea2dda67c3f74d4bba4c07ae18c` | task input / gate content |
| reference/step-00-input/baseline-filtered-v2/flow-check.json | `3be4ccd3d045951e7c69e523e6ce2dfab052d45ece39d453741f310435d1c700` | hash-only dependency |
| reference/step-00-input/baseline-filtered-v2/flow.md | `d0a5fcd029f4f315a02fcd2c057a44907bdf7362fbce17b8664a75b82773595d` | hash-only dependency |
| reference/step-00-input/baseline-filtered-v2/fr-check.json | `1b0c604da9288ce926ba4c98eb258107b130f309f85b1ee96403e02ba0d0f98c` | hash-only dependency |
| reference/step-00-input/baseline-filtered-v2/fr-nfr.md | `da31640e540b825d4fec555627ea098f092daf4243d5d304fd4c32ae6db734cd` | hash-only dependency |
| reference/step-00-input/baseline-filtered-v2/input-audit.md | `d4100680ed1f31ea3351144f202f85343fb47a23acfa0305116731ab8bb1bbd8` | task input / gate content |
| reference/step-00-input/baseline-filtered-v2/provenance.md | `8059b1b47647d690ed7a73e6b4b9751e209edb3905868a4729269fb79330739a` | task input / gate content |
| reference/step-00-input/baseline-filtered-v2/state-machine.md | `b4bc79de9e95f1526ca05326211a6025981b0420f3681b574e37189319f35adf` | hash-only dependency |
| reference/step-00-input/baseline-filtered-v2/structure.md | `fc8facf9088ad320d8dc3a7157edc14b337c1cb7081c3b098bcf91ceab08c560` | hash-only dependency |
| reference/step-00-input/baseline-filtered-v2/ui-check.json | `c09bf23c92abf0cd9c570f71ff890c1b572f8846c4d2ff8f5d2c3323be448af7` | hash-only dependency |
| reference/step-00-input/baseline-filtered-v2/ui-contract.md | `294b660d2e39b3745344f225400eee57c02c25b6efb108a3a7ecce7cdd060e68` | task input / gate content |
| reference/step-00-input/baseline-filtered-v2/ui-mockup.html | `d2b7bfa0cff5700d3ca07f611c03cfa0304c54eafb51387f125e95edd11f7803` | hash-only dependency |
| reference/step-00-input/baseline-filtered-v2/us-initial.md | `56a439f6e22f4a8d17f552b023c3c8fe61556f5bd31f1f1e9b70c1f9da6049d2` | task input / gate content |
| reference/step-03-reveal-1/reveal-1.md | `1fde792db1fdcf211be4a171fd88c61184ce892720832023fcaefad6a67f8917` | task input / gate content |
