# Evaluator — verify-flow plan-v2
REVIEW_MODE: artifacts; TASK_ID: revise-flow; VERIFY_TASK: verify-flow; RUN_ID: flow-v2-review.
UTC: 2026-09-14T13:25:05.429873Z; ตรวจ v2 ครั้งที่ 1; แก้ artifacts 0 รอบ; F-01 เป็นผลตรวจหลังแก้เอกสารรอบแรก.
ผล: **PASS เฉพาะเอกสาร Flow/state/structure v2; F-01 closed ระดับ traceability เอกสาร**. Mock runtime / AC ระบบจริง: **NOT_TESTED**; กฎที่รอมนุษย์: **BLOCKED**.
Path จากราก LAB: S=reference/session; B=reference/step-00-input/baseline-filtered-v2; V=S/fr-nfr-v2.md; F=S/flow-v2.md; M=S/state-machine-v2.md; T=S/structure-v2.md; R=reference/step-03-reveal-1/reveal-1.md.
วิธีจริง: อ่าน delta ทั้งสามไฟล์และผลกระทบ; Python SHA-256, draft-07/FormatChecker/DAG, เทียบ mapping/AC/registry/references. ไม่รัน browser/UI/LAN และไม่ audit baseline ทุกแถวซ้ำ.
Gate PASS: plan-v2 เป็นเลขล่าสุด; hash คู่แผน/impact/schema ตรงผล verify-plan; FR v2 PASS ผูก hash ตรง 15/15 bindings; outputs/รายงาน Executor มีจริง. Snapshot planned/needs_recheck ไม่ใช่สถานะธุรกิจ.
Reuse PASS จำกัดขอบเขต: flow-v1-check bindings 8/8 และ Executor inputs/outputs ที่อนุญาต 25/25 ตรง; ไม่อ่านหรือ hash README. ใช้ผลเดิม 18 US/ทุกคอลัมน์/AC ตาม fr-v2-check; ไม่รับ FAIL เดิมเป็น PASS ใหม่.
PASS โครงสร้าง: coverage 21/21 US; MRG-01–30 locator ตรง 30/30; modules 12/screens 17 มีปลายทางจริง; refs เดิมของ 11 modules/16 screens ไม่หาย; mapping delta 4 แถวตรงกันทั้งสามไฟล์.
PASS authority: R:12–14 → V:30,35,40 ทั้ง 18 เซลล์ตรง; AC US-09/11/14/21 ที่ F:158–161 ตรง US authority. ชื่อ I-V2/C-V2/MOD-12/SCR-17 เป็นชื่อออกแบบที่ trace ครบ ไม่ใช้ความต่างชื่อเป็นเหตุ FAIL.

| US | V:US/FR → F:coverage | ผลเอกสาร / mapping / locator | Mock / ระบบจริง |
|---|---|---|---|
| US-01 | 22/50 → 34 | PASS — MRG-01/12 → MOD-01/SCR-01; reuse | NOT_TESTED / NOT_TESTED |
| US-02 | 23/51 → 35 | PASS — MRG-01/04/12/13 → MOD-01/02/06; โต๊ะเดิม | NOT_TESTED / NOT_TESTED |
| US-03 | 24/52 → 36 | PASS — MRG-02/04/14 → SCR-02/03/06/08; ช่วงรับแยก capacity | NOT_TESTED / NOT_TESTED |
| US-04 | 25/53 → 37 | PASS — MRG-03/04/32/33; ตัวเลือก/ราคา snapshot → T:61,85,87 | NOT_TESTED / NOT_TESTED |
| US-05 | 26/54 → 38 | PASS — MRG-05 → SCR-04; ครัว→ลูกค้าไม่รีเฟรช 5 วินาที/18 จาก 20; F:163 | NOT_TESTED / NOT_TESTED |
| US-06 | 27/55 → 39 | PASS — MRG-08/09/18; ปิด catalog แยก item → M:68,81 | NOT_TESTED / NOT_TESTED |
| US-07 | 28/56 → 40 | PASS — MRG-03/04 → MOD-03/SCR-03; สูตร/7 วัน/ช่วงเดิม/10 นาที/80% → F:163,T:94; X ไม่ใช่ ETA | NOT_TESTED / NOT_TESTED |
| US-08 | 29/57 → 41 | PASS — MRG-32/33 เพิ่มยอดปรับเดียวกันลูกค้า/หน้าร้าน → F:122,130,165; payment เดิม M:69–72 | NOT_TESTED / NOT_TESTED |
| US-09 | 30/127 → 42 | PASS — MRG-31/32/33 → I-V2-01/02/03 → SCR-06→04/03; สองปุ่ม/ลดรวม/10 วินาที/5 จาก 5 → F:110–132,M:52–54,T:87–89 | NOT_TESTED / NOT_TESTED |
| US-10 | 31/58 → 43 | PASS — MRG-04 → SCR-06; timestamp/monotonic เดิม ไม่ใช้ item count → F:144,M:65 | NOT_TESTED / NOT_TESTED |
| US-11 | 32/59 → 44 | PASS — F-01 closed: MRG-05→O-02/03→MOD-04→06→SCR-06→08; F:104–106,M:66,79,T:46,67,86,105 | NOT_TESTED / NOT_TESTED |
| US-12 | 33/60 → 45 | PASS — MRG-08/18/19 → MOD-05/SCR-07; ทั้งจาน/เฉพาะตัวเลือกแยกคิวเดิม → F:78,88–89,M:81 | NOT_TESTED / NOT_TESTED |
| US-13 | 34/61 → 46 | PASS — MRG-09/20; เปิด catalog ไม่ตอบแทนลูกค้า → F:79,90,T:90 | NOT_TESTED / NOT_TESTED |
| US-14 | 35/128 → 47 | PASS — MRG-31/32/33 → I-V2; รอลูกค้าตัดสินใจ; ลูกค้าเลือก→ครัวอัปเดต/ลบ 10 วินาที/5 จาก 5 → F:118–132,M:52–59 | NOT_TESTED / NOT_TESTED |
| US-15 | 36/62 → 48 | PASS — P-01–08/log/table-id/T-001 เดิม; คืนรายการไม่สร้างยืนยันเงิน → F:122,130,165,M:69–74,T:89,91 | NOT_TESTED / NOT_TESTED |
| US-16 | 37/63 → 49 | PASS — MRG-12–17; table/session แยก item/order/payment → M:33,73–74,T:84,119 | NOT_TESTED / NOT_TESTED |
| US-19 | 38/64 → 50 | PASS — MRG-21–25/32/33; original snapshot/5 จาก 5 คงเดิม; ยอดปรับแยก → F:150–152,165,T:85,88–90 | NOT_TESTED / NOT_TESTED |
| US-20 | 39/65 → 51 | PASS — MRG-23/25 → MOD-08/09; คง US-14/Q-20 → F:95,169,T:70–71,90 | NOT_TESTED / NOT_TESTED |
| US-21 | 40/129 → 52 | PASS — MRG-34/35→C-V2-01–03→MOD-12/SCR-17→03; 15 นาที/00/15/30/45/N=5/3 จาก 3; ก่อนยืนยัน → F:136–146,M:55–57,T:76,92–93,106 | NOT_TESTED / NOT_TESTED |
| US-25 | 41/66 → 53 | PASS — MRG-26–28 → MOD-10/SCR-13–15; permission เดิม/Unknown คงอยู่ → T:103–110 | NOT_TESTED / NOT_TESTED |
| US-26 | 42/67 → 54 | PASS — MRG-29/30 → MOD-07/11; ไม่มีหน้าติดตั้งใน mock → T:78; reuse เอกสารเท่านั้น | NOT_TESTED / NOT_TESTED |

F-01 closed: F:60/M:41/T:31 มีเส้นทางเดียวกัน; T:46 MOD-06 และ T:67 SCR-08 มี FR-11/MRG-05/actions/data/บทบาทผู้รับครบ. F:159 คง 1 แตะ/5 วินาทีบน LAN/อย่างน้อย 18 จาก 20; M:66 รองรับปลายทางหน้าร้าน.
F-01 ไม่ได้ปิดจากชื่อ screen หรือสถานะเงิน: ใช้ OrderEvent/Order.order_state → front-order ใบเดียวกันตาม data-order-id; B/ui-contract.md:67–69 รองรับความหมาย; T:117 แยก front-payment-status. ยังไม่มีหลักฐานคลิก.
PASS reuse/precedence: F:18–26,71–100; M:24; T:24–26 ระบุ FR v2 → delta → baseline ที่ hash ตรง. Entity/key/cardinality/permission/EP/INV และข้อค้างเดิมใช้ซ้ำตาม locator; ไม่กู้ข้อความปิดหรือสรุปผล upstream เป็นผล v2.
PASS state/data: M:30–35,78–83 แยก item/order/payment/table/AI; F:122,130,150–152 และ T:85–97 เก็บราคาเดิมกับยอดปรับและ log; คืนรายการไม่แปลว่าคืนเงินจริง/ยกเลิกออเดอร์/ปิดโต๊ะ.
PASS ขอบเขตสมมติฐาน: F:138,144–146,150,169–174 คง X=10/UTC/[start,end)/ส่วนต่าง/นับคืนเป็น fixture ยังไม่ยืนยัน; ไม่เพิ่มสูตร X, SLA US-21 หรือกฎห้ามยืนยันเมื่อเต็ม.
BLOCKED เฉพาะรับรองกฎจริง: ก./ค./ช., เสร็จแล้ว↔พร้อมเสิร์ฟ/aggregate/ETA, refund/ส่วนต่าง/ซ้ำ/ผู้อนุมัติ, X/รอยต่อ/เปลี่ยน N/นับคืน, Q-20/Unknown/คำถามเดิม; ตาม l-real-scope และ l-q-* ไม่บล็อกเอกสารนี้.
NOT_TESTED UI: อ่านสัญญาและ mapping เท่านั้น; data-testid เดิมต้องรักษาใน revise-ui (T:116–124). ไม่ตรวจ HTML/DOM/คลิก/responsive/reset/roles หรือ mock behavior และไม่ใช้ผล UI upstream แทน.
NOT_TESTED ระบบจริงทุก AC: LAN/Wi-Fi/QR/หลายอุปกรณ์/เวลา/โหลด/สัดส่วนตัวอย่าง/ETA 7 วัน/log/security/Ubuntu/ติดตั้ง/ถอดอินเทอร์เน็ต/การชำระเงินจริง.
Downstream: ปลดเฉพาะ gate verify-flow เอกสารให้ draft-test-outline v2 เริ่มตาม FR+Flow hashes นี้; ต้องสร้าง/ตรวจ outline v2 ก่อน revise-ui และตรวจ UI v2 ก่อน handoff. ไม่เปลี่ยนผล BLOCKED ของ outline v1 หรือ snapshot.
ข้อบกพร่องที่ต้องแก้ใน artifacts รอบนี้: ไม่พบ; F-01 เอกสารปิดแล้ว. หากคำตอบมนุษย์เปลี่ยน scope/dependency ให้ส่ง Planner; จำกัดแก้ไม่เกิน 2 รอบต่อปัญหา ไม่คืบหยุดพร้อมหลักฐาน (ข้อตกลงการเรียน ไม่ใช่ AC ร้าน).

| Plan / input / target hash | SHA-256 |
|---|---|
| S/plan-v2.json | `8682dcba597fd36cadcf0a4724a9a75bd866f551b337281c663ee419c059c828` |
| S/plan-v2.md | `75c5e9b06c7e26fbf7174295d165fbae64be57ea8ff807b4d96884898296ea2c` |
| V | `2cbdde11bb3fd5e62f338a1ea74f65d11112f3ea56e8a10ed9d24b08a1dcf0bb` |
| S/evaluations/fr-v2-check.md | `b21ee2b862656cf871d69117c44d2d5168154360da088c929bf87e033151819b` |
| S/evaluations/flow-v1-check.md | `43cd1d0cf505bb509d9453f060503c82ed300332324c9893168eb74f05a70141` |
| F | `8fe7983eb45a7222424c7fafe34adf78874da75e7e7cf3ab013d4955d1159f9c` |
| M | `efe13a4cbb843c056884478fa8e5a0ab201c9641a579ae355cedb07867218d0a` |
| T | `f1a935fc0cf2779d225ce050a12b5df108c53a149fa0885ac7ce78828ae2290d` |
| S/execution/plan-v2/flow-v2-run/revise-flow.md | `860a4f6b24b83172708864633dba4368771d76473c3f8dc11e7d975e9f84f0a7` |
Input-set 26 ไฟล์ (path จากราก LAB+TAB+SHA256+LF เรียง path): `6d0ae0c75f32c26e61f70903da19f415604282637b75e3ddafcf8d1be6a1897c`; manifest/checks ใน S/evaluations/plan-v2/flow-v2-review-evidence.json.
สร้างจริง: S/evaluations/flow-v2-check.md; S/evaluations/plan-v2/flow-v2-review.md; evidence JSON ที่ระบุ; reference/step-05-execute-v2/revise-flow/evaluation/evaluator.md. Output hashes อยู่ evaluator.md; ไม่ทำ self-hash.
ไม่เปิด README/reveal-2/เว็บ ไม่เรียก agent/AI CLI เพิ่ม ไม่แก้ Executor/baseline/input/prompts/แผน และไม่ใช้ข้อมูลบัญชีจริง.
