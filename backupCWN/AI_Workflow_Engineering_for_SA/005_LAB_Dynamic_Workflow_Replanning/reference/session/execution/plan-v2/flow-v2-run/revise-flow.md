# Executor — revise-flow

TASK_ID: revise-flow; RUN_ID: flow-v2-run; PLAN: plan-v2; UTC: 2026-09-14T13:21:31.591323Z
**STATUS: EXECUTED — ทำเอกสารเสร็จ รอ Evaluator verify-flow; ไม่ใช่ PASS**.

## Gate และ dependency ที่ตรวจจริง

ตรวจรายชื่อ plan-v* เฉพาะ session ก่อนทำและก่อนเขียน: เลขสูงสุด 2 คู่ JSON/Markdown ครบ ไม่มีรุ่นใหม่ค้าง. ตรวจ duplicate JSON keys, Draft7Validator+FormatChecker, task ID ไม่ซ้ำ, dependency มีจริง ไม่ self/cycle/cancelled. พบ revise-flow หนึ่งรายการ kind=revise/status=planned; outputs ทั้งสามตรง plan. ใช้ผล Evaluator ที่ hash คู่แผนยังตรงสำหรับความสอดคล้อง JSON/Markdown เต็ม ไม่ประเมิน PLAN_READY เอง.

- verify-plan: S/evaluations/plan-v2-review.md PLAN_READY / verify-plan PASS เอกสาร/offline mock; hash plan JSON/Markdown/impact/schema ตรงปัจจุบัน จึงผ่าน l-plan-gate สำหรับงานนี้.
- revise-fr: S/execution/plan-v2/fr-v2-run/revise-fr.md ระบุ EXECUTED และมี S/fr-nfr-v2.md จริง. verify-fr: S/evaluations/fr-v2-check.md PASS เอกสารและอนุญาต revise-flow. ตรวจ binding ของทั้ง 15 input/target/execution ในผล verify-fr กับ bytes ปัจจุบันตรงครบ 15/15 รวม FR target/hash และหลักฐาน producer. ผลนี้รองรับ dependency ทั้งสอง ไม่ใช้ status planned ใน snapshot เป็นเหตุเดาว่าเสร็จ.
- task inputs ครบ 9/9; hash baseline Flow/state/structure/UI contract ตรง provenance 4/4. disposition ของเอกสารสามไฟล์เป็น replace; reuse เฉพาะข้อความ/โครง/ข้อค้างตาม registry และ path/hash ไม่ reuse verdict FAIL เป็น PASS. F-01 เดิมยังต้องให้ verify-flow ตรวจปิด; test-outline v1 BLOCKED ไม่ถูกปลดในรอบนี้.
- l-check-gates ผ่านเฉพาะ FR v2 → revise-flow; downstream ยังรอ verify-flow PASS. l-real-scope และ l-q-status/eta/payment/mapping/operations/environment/refund/capacity ยังบล็อกการยืนยันกฎ/ระบบจริง แต่อนุญาตเอกสารที่ติดป้ายข้อค้างตามแผน. ไม่มี approval ที่ห้ามเอกสารนี้ค้าง. ไม่แก้ limit หรือ snapshot.

S=reference/session; B=reference/step-00-input/baseline-filtered-v2; path ในรายงานอ้างจากราก LAB 005.

## งานที่ทำ

สร้าง flow-v2.md, state-machine-v2.md, structure-v2.md ขอบเขต 21 US โดยใช้ FR v2 เป็น authority. คง MRG-01–MRG-30 ผ่าน registry/path/hash พร้อมส่วนแก้ และเพิ่ม MRG-31–MRG-35 ครอบแจ้งทำไม่ได้/เปลี่ยนเมนู/คืนรายการ/ตั้งช่วง-N/ข้อความก่อนยืนยัน. Mapping F-01 US-11/FR-11/MRG-05 → MOD-06/SCR-08 พร้อม Order.order_state/OrderEvent แยกสถานะเงินตรงทั้งสามเอกสาร; ไม่ปิด F-01 แทน Evaluator.

เก็บ snapshot เดิม รายการคืน/แทน ยอดก่อน/ปรับ และ payment log เดิม; ตัวเลขเงินตัวอย่างและ X=10 เป็น fixture มีป้ายสมมติฐาน. หน้าต่าง 00/15/30/45 และข้อความก่อนยืนยันครบ; ไม่เพิ่มกฎปฏิเสธเมื่อเต็ม. แยก item/order/payment/table/AI task; ขอบหน้าต่าง/aggregate/คืนเงินจริง/ส่วนต่าง/สิทธิ์ไม่ชัดยังรอยืนยัน. คงข้อค้าง ก./ค./ช. และ US-20 อ้าง US-14.

## ผลตรวจเบื้องต้นของ Executor

ตรวจในหน่วยความจำก่อนเขียนและ read-back หลัง exclusive create: coverage 21 US ตรง task.us_refs, registry baseline 30 flows, modules 12 และ screens 17 อ้าง ID ที่มีในทะเบียน; mapping ส่วนแก้ของ US-11/09/14/21 เหมือนกันทั้งสามเอกสาร. AC US-09/11/14/21 คัดตรงตัวจาก FR authority; เกณฑ์เดิมทั้งหมดอ้าง FR path/hash โดยไม่เปลี่ยน US/AC/NFR. ตรวจแยกสองจุดวัด 10 วินาทีและสองปลายทาง 5 วินาที, snapshot/payment/state boundary และข้อความเต็มก่อนยืนยันจากเอกสารที่สร้าง.

การตรวจนี้เป็นความครบและความสอดคล้องเบื้องต้นของผู้ผลิต ไม่ใช่ Evaluator PASS หรือผลทดสอบระบบ. ยังไม่ได้ render Mermaid/เปิด browser/รัน application; เอกสารใช้ตารางและลำดับข้อความ. Inputs ที่ใช้ตรวจ hash ซ้ำก่อนเขียนตรงครบ; ผล read-back ตรงเนื้อหาที่เตรียม. ไม่ทับไฟล์เดิม ไม่แก้ plan/input/prompts/baseline/UI/outline. อ่าน input/README.md เฉพาะเป็นสัญญาที่อนุญาต ไม่อ่าน README หลัก LAB; ไม่อ่าน reveal-2/เว็บ/เรียก agent หรือ CLI โมเดลเพิ่ม.

## ข้อค้าง ส่งต่อ และสิ่งที่ยังไม่ทดสอบ

F-01 แก้ในเอกสารแล้วแต่ **รอ verify-flow**; ผลตรวจอิสระ v2 ยังไม่มี. Q เดิม 18 รหัสและ Q-V2-REFUND/STATE/CAPACITY ยัง OPEN. หมายเหตุ ก./ค./ช., เสร็จแล้ว/พร้อมเสิร์ฟ/aggregate/ETA, คืนเงินจริง/ส่วนต่าง/คืนซ้ำ/สิทธิ์ผู้อนุมัติ, สูตร X/ช่วง/เขตเวลา/รอยต่อ/นับคืน/เปลี่ยน N และกฎเมื่อเต็มยังไม่ยืนยัน.

ส่งต่อเป็นไฟล์ให้ Evaluator session ถัดไป: outputs ทั้งสามตาม hashes ด้านล่าง + รายงานนี้ + FR v2/ผล verify-fr/คู่แผน/ผล PLAN_READY/F-01 ตาม input plan; เป้าหมาย verify-flow คือ S/evaluations/flow-v2-check.md. ห้ามปลด draft-test-outline/verify-test-outline/revise-ui/verify-ui/evaluate-handoff ก่อนผลตาม gates. ต้องตรวจต่อ FR-05/07/08/11/12/15/19/20/25, NFR-02/04/07/17/19 และ coverage ทุก US รวมส่วนใช้ซ้ำกับ UI contract/fixture ใหม่. ไม่ได้เรียกหรือได้รับผล Evaluator ในรอบนี้.

ไม่มีการเปลี่ยน dependency/scope จึงไม่ต้องแก้แผน; ถ้าข้อค้างทำให้ต้องเปลี่ยน ส่ง Planner สร้าง snapshot ใหม่. NOT_TESTED: UI v2/selector/DOM/คลิก/responsive, LAN/Wi-Fi/หลายอุปกรณ์/โหลด/การแข่งขัน/สัดส่วน AC จริง, สูตรและความแม่นยำ ETA/ข้อมูล 7 วัน, สูตร X, auth/security/server logs, Ubuntu/ติดตั้ง 30 นาที/ถอดอินเทอร์เน็ต, ระบบเงินจริง. ไม่ใช้บัญชีจริงหรือบริการชำระเงินจริง.

## Hash manifest

Plan JSON SHA-256: `8682dcba597fd36cadcf0a4724a9a75bd866f551b337281c663ee419c059c828`
Plan Markdown SHA-256: `75c5e9b06c7e26fbf7174295d165fbae64be57ea8ff807b4d96884898296ea2c`
Input-set SHA-256: `373b78a27d6b3be1e955b278c7fddc3ebfb7ae93950c20c6342ea1552eb4c5ac` (path จากราก LAB + TAB + SHA256 + LF เรียง path, UTF-8; รวม hash-only dependency ไม่รวม outputs)

| Input path | SHA-256 |
|---|---|
| input/README.md | eca3997d869894c7244c3ebea2320e688832aa4e670598feed84a36058e6eaf1 |
| input/plan.schema.json | cea51a142b808b2c3045994baa68a45d98d280f9d9c5a55962c2015de365431c |
| reference/session/evaluations/flow-v1-check.md | 43cd1d0cf505bb509d9453f060503c82ed300332324c9893168eb74f05a70141 |
| reference/session/evaluations/fr-v1-check.md | b533a2d6b8618f590d3de91bdc4250172ad8d987df6060860f16e0a672403c5a |
| reference/session/evaluations/fr-v2-check.md | b21ee2b862656cf871d69117c44d2d5168154360da088c929bf87e033151819b |
| reference/session/evaluations/plan-v2-review.md | 470d9248beca3760f63b1df7b54b5bcc24fc18cce5c1994ab3adebcf8403cd0e |
| reference/session/evaluations/plan-v2/plan-v2-review-evidence.json | 66711881302f8d765012d237d9ffca437816b5e7ac6f25ec58c7cf90d72d1e8a |
| reference/session/evaluations/test-outline-v1-check.md | ea6c1f13c350bd5103493061d8b14fba8115cba46a8b900df42ec0445a1aa9a2 |
| reference/session/execution/fr-baseline-audit-v1.md | 78f8ce610526fdaa3e7911b3765fbff8246ea223d9772611e370bb42d5374175 |
| reference/session/execution/plan-v2/fr-v2-run/revise-fr.md | 571c4226e328461c807411303a66737876618d768bcbc19d261b76a32dfd745b |
| reference/session/fr-nfr-v2.md | 2cbdde11bb3fd5e62f338a1ea74f65d11112f3ea56e8a10ed9d24b08a1dcf0bb |
| reference/session/impact-analysis-v2.md | b4b5dcfbe1d03d1e31d59758b2a9476cecf00b65b0226914ac29f199894ecfb3 |
| reference/session/plan-v2.json | 8682dcba597fd36cadcf0a4724a9a75bd866f551b337281c663ee419c059c828 |
| reference/session/plan-v2.md | 75c5e9b06c7e26fbf7174295d165fbae64be57ea8ff807b4d96884898296ea2c |
| reference/step-00-input/baseline-filtered-v2/flow.md | d0a5fcd029f4f315a02fcd2c057a44907bdf7362fbce17b8664a75b82773595d |
| reference/step-00-input/baseline-filtered-v2/fr-nfr.md | da31640e540b825d4fec555627ea098f092daf4243d5d304fd4c32ae6db734cd |
| reference/step-00-input/baseline-filtered-v2/input-audit.md | d4100680ed1f31ea3351144f202f85343fb47a23acfa0305116731ab8bb1bbd8 |
| reference/step-00-input/baseline-filtered-v2/provenance.md | 8059b1b47647d690ed7a73e6b4b9751e209edb3905868a4729269fb79330739a |
| reference/step-00-input/baseline-filtered-v2/state-machine.md | b4bc79de9e95f1526ca05326211a6025981b0420f3681b574e37189319f35adf |
| reference/step-00-input/baseline-filtered-v2/structure.md | fc8facf9088ad320d8dc3a7157edc14b337c1cb7081c3b098bcf91ceab08c560 |
| reference/step-00-input/baseline-filtered-v2/ui-contract.md | 294b660d2e39b3745344f225400eee57c02c25b6efb108a3a7ecce7cdd060e68 |
| reference/step-00-input/baseline-filtered-v2/us-initial.md | 56a439f6e22f4a8d17f552b023c3c8fe61556f5bd31f1f1e9b70c1f9da6049d2 |
| reference/step-03-reveal-1/reveal-1.md | 1fde792db1fdcf211be4a171fd88c61184ce892720832023fcaefad6a67f8917 |

| Output path | SHA-256 | สถานะ |
|---|---|---|
| reference/session/flow-v2.md | 8fe7983eb45a7222424c7fafe34adf78874da75e7e7cf3ab013d4955d1159f9c | EXECUTED; รอ verify-flow |
| reference/session/state-machine-v2.md | efe13a4cbb843c056884478fa8e5a0ab201c9641a579ae355cedb07867218d0a | EXECUTED; รอ verify-flow |
| reference/session/structure-v2.md | f1a935fc0cf2779d225ce050a12b5df108c53a149fa0885ac7ce78828ae2290d | EXECUTED; รอ verify-flow |

ไฟล์ที่สร้างจริง: outputs สามไฟล์ข้างต้น, `reference/session/execution/plan-v2/flow-v2-run/revise-flow.md`, `reference/step-05-execute-v2/revise-flow/execution.md`. รายงาน cwd บันทึก hash execution report หลังสร้าง; ไม่ใส่ self-hash วนกลับ.
