# Evaluator — plan-v1

ผลรวม: **PLAN_READY เฉพาะแผนงานเอกสารและ offline mock ตาม gate**; verdict สำหรับ `verify-plan`: **PASS ในขอบเขตดังกล่าว**. การรับรองกฎร้านและระบบจริงเป็น **PLAN_NOT_READY / BLOCKED** และอยู่นอก tasks ของแผนนี้. ผลนี้ไม่ใช่ PASS ของชิ้นงาน downstream หรือ AC ระบบจริง.

- REVIEW_MODE: `plan`
- TASK_ID: `all`
- RUN_ID: `plan-review`
- Plan: `plan-v1`; created_at: `2026-09-14T12:35:53.783903Z`
- Evaluated at (UTC): `2026-09-14T12:39:37.247070Z`
- ตรวจครั้งที่ 1 ในกิจกรรมนี้; แก้แผน 0 รอบ; ไม่เปลี่ยน snapshot
- ขอบเขตอ่าน: คู่ plan-v1, Schema, Planner validation ที่แผนอ้าง, input-audit/provenance และ 10 ไฟล์ใน manifest ของ baseline-filtered-v2 เท่านั้น

ทุก path แบบย่อในรายงานอ้างจาก `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning`. `baseline/` ด้านล่างหมายถึง `reference/step-00-input/baseline-filtered-v2/` และ `plan.md` หมายถึง `reference/session/plan-v1.md`.

## ผลรายขอบเขตและการเดินงาน

| ขอบเขต | ผลตรวจแผน | สถานะการปฏิบัติ/ข้อจำกัด |
|---|---|---|
| คู่แผนและ verify-plan | PLAN_READY / PASS | ผ่านการตรวจรอบนี้ โดยผูก hash ของทั้งสองไฟล์; รายงานตาม outputs ถูกสร้างแยกจาก snapshot |
| audit-fr-baseline → verify-fr | PLAN_READY | เริ่มรายงาน audit ได้หลังมีรายงานนี้; verify-fr ต้องรอ audit จริง ไม่ใช่ผล upstream 108/108 |
| verify-flow | PLAN_READY | รอ audit-fr-baseline และ verify-fr PASS; งานนี้ยังไม่ได้รัน คง MC-01–MC-03 |
| draft-test-outline | PLAN_READY | รอ audit-fr-baseline และ verify-fr PASS; ไม่ต้องรอ verify-flow เพราะยังไม่ใช้ Flow เป็นฐานตัดสินในช่วงร่าง |
| verify-test-outline | PLAN_READY | รอร่างจริงและ verify-fr/verify-flow PASS เพื่อเทียบข้ามเอกสาร |
| verify-ui ใน offline mock | PLAN_READY เฉพาะรูปแบบและขอบเขตงาน | NOT_TESTED ในรอบนี้; รอ upstream และตรวจความพร้อม browser ตาม l-browser ก่อนรัน หากทำไม่ได้ให้ BLOCKED เฉพาะสายนี้ |
| evaluate-handoff | PLAN_READY เฉพาะแผนการตรวจส่งต่อ | ยังส่งมอบชุดงานไม่ได้ ต้องมี outputs และผล PASS ตาม dependency ทุกเส้น |
| ยืนยันกฎร้าน/ระบบจริง | PLAN_NOT_READY / BLOCKED | ไม่มี task ระบบจริงในแผน; l-real-scope ยัง blocking=true ต้องได้คำตอบและหลักฐานระบบตามขอบเขตใหม่ |

คำถามธุรกิจไม่บล็อกการเขียน audit หรือ test outline ที่คงคำถามเดิม ตามข้อกำหนดเฉพาะรอบอ้างอิงของผู้ใช้. การขาด outputs ของงานอนาคตไม่ใช่ input หายของ verify-plan; ทุกไฟล์ดังกล่าวมีผู้ผลิตและ dependency รองรับ.

## วิธีตรวจและหลักฐาน

ตรวจด้วย Python อ่านไฟล์ที่ระบุเท่านั้น: parse JSON แบบตรวจ duplicate key, `jsonschema.Draft7Validator.check_schema` และ `Draft7Validator(..., format_checker=FormatChecker())`, parse UTC, ตรวจ ID/graph ด้วย DFS, ตรวจ dependency ของ input ที่ผลิตโดย task อื่นรวม transitive dependency, คำนวณ SHA-256 จาก bytes จริง และเทียบ Markdown แบบรายส่วน. อ่านเหตุผล decisions/limits/reuse และหลักฐาน baseline ที่เกี่ยวกับความพร้อม/คำถาม/สัญญา UI. ไม่รันงาน artifact audit เต็มทุกเซลล์ในรอบ plan นี้.

| รายการตรวจ | ผล | หลักฐาน/รายละเอียด |
|---|---|---|
| JSON Schema draft-07 | PASS | Schema ถูกต้อง; plan ไม่มี validation error รวม date-time format; ไม่มี duplicate JSON key |
| UTC | PASS | created_at ลงท้าย Z และ parse offset ได้ 00:00; เวลาแผนก่อนเวลาตรวจนี้ |
| Unique ID | PASS | tasks 8/8, decisions 12/12, limits 12/12; ไม่พบ ID ซ้ำ |
| Dependency target/self/cycle | PASS | 20 เส้น; target มีจริงทุกเส้น; ไม่มี self-reference หรือวงจร |
| เหตุผล dependency | PASS | เหตุผลแต่ละ task ระบุทุกเส้นต้นทาง → ปลายทางครบ 20 เส้น; inputs ที่ผลิตในแผนอยู่ใน ancestor chain |
| ลำดับและ priority | PASS | plan.md:16–18 และ d-schedule ตรง DAG; สองสายหลัง verify-fr รวมที่ verify-test-outline อย่างมีเหตุผล |
| Cancel consistency | PASS — ไม่มีกรณี cancel | ทั้ง 8 task เป็น planned; ไม่มี kind=cancel/status=cancelled และไม่มี active task รอ cancelled task |
| Limit targets | PASS | affected_tasks ทุก ID มีจริง; l-real-scope ว่างโดยตั้งใจเพราะไม่มีงานระบบจริง |
| JSON/Markdown | PASS | เทียบข้อความ field ใน task 8, decision 12, reuse 12, limit 12 ครบ 44 ส่วนตรงกัน รวมลำดับรายการ/boolean; string values 560 รายการมีตรงตัวใน Markdown; version/trigger/UTC ตรงกัน |
| Diff/เพิ่ม/แยก/ยกเลิก | PASS สำหรับแผนแรก | plan.md:12–14, 550–554; ไม่มีแผนก่อนหน้าของการรันนี้ให้ diff. ไม่อ่าน baseline เก่าหรือไฟล์ diff. ตัวอย่าง v0 ที่แผนกล่าวถึงไม่ใช่ snapshot ก่อนหน้าและไม่ได้เปิดอ่านในการประเมินนี้ |
| ขอบเขตข้อมูลที่เปิด | PASS ระดับเนื้อหาแผน | ทุก task อ้าง 18 US ตรงแถว baseline/us-initial.md:3–20; ไม่มี task ใหม่จากรหัสอ้าง US-14 ใน US-20; ไม่กู้เซลล์ US-12 ที่ปิดไว้ |
| เหตุผลงานใหม่ | PASS | baseline/input-audit.md ระบุช่องว่าง FR audit ของ session, Flow หลังกรอง, DOM/browser และ test outline; แผนสร้าง 2 งานและ verify 6 งาน ไม่มีการ revise/cancel โดยไร้หลักฐาน |
| Path/input/output | PASS | input ตั้งต้นของ verify-plan มีครบ; output 10 path ไม่ซ้ำ อยู่ใน session และไม่มีอยู่ก่อนรอบนี้; input ของงานอนาคตมีผู้ผลิตครบ |
| Reuse/hash | PASS แบบจำกัดการใช้ | manifest ตรง 10/10; reuse source_version ตรง 12/12; Planner validation ผูก hash ของคู่แผนตรงกับ bytes ปัจจุบัน |
| รักษา US/AC และสถานะธุรกิจ | PASS ระดับคำสั่งในแผน | audit/verify/test-outline กำหนดคงข้อความ ตัวเลข หน่วย สัดส่วน และแยกสมมติฐาน; d-offline-boundary และ verify-flow แยกรายการ/ออเดอร์/ชำระเงิน/โต๊ะจาก AI task status |
| สัญญา UI/หลักฐานคลิก | PASS ระดับแผน; การคลิก NOT_TESTED | verify-ui ระบุ browser, context/reset, network off, script/observations, hashes และ selector ตาม contract; ไม่แก้ HTML/data-testid เดิม. การอ่าน HTML ไม่ใช่การคลิกผ่าน |

ลำดับที่ตรวจได้: `verify-plan → audit-fr-baseline → verify-fr → verify-flow → draft-test-outline → verify-test-outline → verify-ui → evaluate-handoff`. นี่เป็นหนึ่ง topological order; verify-flow กับ draft-test-outline ทำเป็นงานอิสระหลัง verify-fr ได้ตามแผน โดยรอบนี้ไม่เรียก agent หรือ CLI เพิ่ม.

## Human-required และ blocking limits

human-required มี 6 กลุ่ม ครอบคลุม Q ที่มีจริงทั้ง 18 รหัสใน baseline/fr-nfr.md:130–147. ไม่พบ human-confirmed หรือคำตัดสินกฎร้านโดย AI. ทุกกลุ่มเชื่อม `l-q-*` สำหรับเก็บข้อค้างของงานเอกสาร/mock และเชื่อม `l-real-scope` ซึ่ง blocking=true สำหรับการยืนยันกฎ/ระบบจริง. การตั้ง l-q-* เป็น false จึงไม่ใช่เหตุ FAIL ภายใต้ข้อกำหนดเฉพาะรอบนี้; ไม่มี task ระบบจริงให้ใส่ใน affected_tasks ของ l-real-scope.

| Decision → limit | หลักฐานที่เปิดแล้ว | งานปัจจุบันที่ต้องคงข้อค้าง |
|---|---|---|
| d-human-status → l-q-status | Q-05/Q-07/Q-11; flow.md:239 MC-01; state-machine.md:104; mapping เสร็จแล้ว/พร้อมเสิร์ฟยังไม่ยืนยัน | verify-flow, draft-test-outline, verify-test-outline, verify-ui, evaluate-handoff |
| d-human-eta → l-q-eta | Q-07, หมายเหตุ ช.; fr-nfr.md:26,136; ui-mockup.html:346 ไม่มีค่า ETA | draft-test-outline, verify-test-outline, verify-ui, evaluate-handoff |
| d-human-payment → l-q-payment | Q-08, หมายเหตุ ก.; fr-nfr.md:27,137; flow.md:240 MC-02 | verify-flow, draft-test-outline, verify-test-outline, verify-ui, evaluate-handoff |
| d-human-mapping → l-q-mapping | Q-12/Q-13/Q-20, หมายเหตุ ค.; flow.md:241 MC-03; us-initial.md:18; ui-contract.md:115 | audit-fr-baseline, verify-fr, verify-flow, draft-test-outline, verify-test-outline, verify-ui, evaluate-handoff |
| d-human-operations → l-q-operations | Q-02/Q-03/Q-04/Q-06/Q-10/Q-11/Q-15/Q-16; fr-nfr.md:131–143 | audit-fr-baseline, verify-fr, verify-flow, draft-test-outline, verify-test-outline, verify-ui, evaluate-handoff |
| d-human-environment → l-q-environment | Q-01/Q-19/Q-25/Q-26; fr-nfr.md:130,144,146–147; structure.md:84 สิทธิ์ | audit-fr-baseline, verify-fr, verify-flow, draft-test-outline, verify-test-outline, verify-ui, evaluate-handoff |

หากเพิ่ม task ที่พัฒนาหรือรับรองกฎจริง ต้องส่ง Planner ทำ snapshot รุ่นถัดไปและผูก blocking limit กับ task นั้นโดยตรงก่อนเริ่ม; รายงานนี้ไม่อนุญาตขยาย scope.

## Reuse และ downstream

US/FR/contract/provenance/audit ใช้เป็น input ตาม hash; FR ยังต้อง audit และ verify ใหม่. Flow/state/structure และ HTML ถูกจัดเป็น recheck ถูกต้อง. fr-check 108/108, flow-check merge 30 flows/unresolved 3 และ ui-check 19/19 เป็นหลักฐาน upstream เท่านั้น. Flow check ก่อนกรองไม่รับรอง hash หลังกรอง; UI check อ้าง HTML upstream; fr-check ไม่มี target hash ภายใน. ไม่มีการถือผลเก่าเป็น PASS ใหม่ และไม่มีหลักฐานวันหมดอายุให้กำหนด TTL ขึ้นเอง. ตรวจได้เฉพาะความตรงของสำเนาและขอบเขตการใช้ตาม provenance; ไม่พิสูจน์สายที่มานอกชุด.

| ประเด็นผลกระทบที่เกี่ยวจริง | การส่งต่อที่แผนครอบคลุม |
|---|---|
| US-05/07 และ US-11 | verify-flow แยก mapping สถานะกับจุดจบ ETA; outline คงสูตรและเกณฑ์เดิม; UI ตรวจได้เฉพาะ mock ไม่มีค่า ETA ไม่สรุป AC ผ่าน |
| US-08/15 | คงคำถาม PromptPay/fallback และแยกชำระเงินจากออเดอร์/เลขรับ/โต๊ะ; mock เงินสด/สลิปต้องอ้าง fixture และ log ตามต้นฉบับ |
| US-12/13/19/20 และ US-06 | ตรวจผลทั้งจาน/ตัวเลือกและการแมปที่มีเมนูมาก่อน; คง US-20 อ้าง US-14 เดิม; ตรวจราคา snapshot/รูป/ตัวเลือก/วัตถุดิบซ้อนใน mock โดยไม่ตัดสินกฎที่ค้าง |
| US-16/25/26 | คงข้อค้างปิดโต๊ะและสิทธิ์; mock auth ไม่รับรอง security จริง; HTML ไม่พิสูจน์การติดตั้ง Ubuntu หรือ offline ระบบจริง |

รายงานนี้ปลด l-plan-gate เฉพาะคู่แผน hash ด้านล่างหลังบันทึก outputs สำเร็จ. l-check-gates ยังรอผลจริงทีละสาย. l-browser ยังไม่ถูกปลดจากการตรวจแผน; หาก runtime ไม่พร้อม ให้บันทึก BLOCKED/NOT_TESTED และหยุด verify-ui/handoff โดยไม่หยุด audit/test outline ที่ผ่าน gate แล้ว. ไม่แก้ status planned ทั้ง 8 งานใน snapshot; รวมสถานะจาก evaluations/execution ในรุ่นถัดไป.

## ข้อบกพร่องและข้อสังเกต

ไม่พบข้อบกพร่องที่ต้องแก้ก่อนเริ่มขอบเขตเอกสาร/offline mock; รายการ FAIL ว่าง. ไม่ต้องแก้แผนในรอบนี้.

- Path รายงานของ verify-plan ใน plan.md:47–51 และ l-plan-gate เป็น `session/evaluations/plan-v1-review.md` ต่างจากตำแหน่งสำเนาที่คำสั่งรอบนี้กำหนด `session/evaluations/plan-v1/plan-review.md`. สร้างรายงานเนื้อหาเดียวกันทั้งสอง path และ evaluator.md ตามคำสั่งให้สร้าง outputs ของ verify task ด้วย จึงไม่มี input ขาดของ downstream และไม่ต้องแก้ snapshot.
- แผนใช้คำ NOT_RUN ในร่าง/กรณีเครื่องมือไม่พร้อม. ในการรายงานผล Evaluator ให้ใช้ NOT_TESTED สำหรับสิ่งที่ไม่ได้ทดสอบตามคำสั่งผู้ใช้; อาจระบุ NOT_RUN เป็นเหตุผลประกอบ ไม่แปลงเป็น PASS. นี่เป็นการระบุวิธีรายงาน ไม่ใช่ AC ร้านใหม่.
- ตรวจเนื้อหาและหลักฐานที่อนุญาต ไม่ได้เปิดประวัติ/ตัวอย่าง v0/logs เพื่อพิสูจน์กระบวนการอ่านของผู้สร้าง. จึงไม่รับรองข้อกล่าวอ้างเกี่ยวกับการทำงานที่อยู่นอกหลักฐานชุดนี้.

หากผล artifact ภายหลัง FAIL ให้ระบุ path/locator, expected/actual, ข้อเสนอแก้เฉพาะจุด และ task downstream; ส่ง Planner เมื่อ scope/dependency หรือไฟล์รุ่นเป้าหมายเปลี่ยน. จำกัดแก้ไม่เกิน 2 รอบต่อปัญหาในกิจกรรมนี้ หากไม่คืบให้หยุดพร้อมหลักฐาน. เพดานนี้เป็นข้อตกลงการเรียน ไม่ใช่ AC ร้าน.

## Plan/input hashes

SHA-256 คำนวณจาก bytes ของไฟล์จริงก่อนสร้างรายงาน และตรวจไม่เปลี่ยนหลังเขียน. ตารางครอบคลุม input ที่อ่านในการประเมินนี้ทั้งหมด; ไม่รวม reveal, diff, baseline เก่า หรือ reference ภายนอกสำเนา.

| Input path | SHA-256 |
|---|---|
| `reference/session/plan-v1.json` | `4bd023624fb2cb5c1ec9975528e8ffbcb6ac830cd40f9b61c5db28523ae25cfe` |
| `reference/session/plan-v1.md` | `10f2d1da058fafe1a6ed75047ad157ab0694cb7ee40ddd89c91874fa4d3310ae` |
| `input/plan.schema.json` | `cea51a142b808b2c3045994baa68a45d98d280f9d9c5a55962c2015de365431c` |
| `reference/session/evaluations/plan-v1-validation.json` | `a93dde889286710ef1217a542ab365b4fa27db3ca9e5473f9ed6dc57b83c5b1d` |
| `reference/step-00-input/baseline-filtered-v2/input-audit.md` | `d4100680ed1f31ea3351144f202f85343fb47a23acfa0305116731ab8bb1bbd8` |
| `reference/step-00-input/baseline-filtered-v2/provenance.md` | `8059b1b47647d690ed7a73e6b4b9751e209edb3905868a4729269fb79330739a` |
| `reference/step-00-input/baseline-filtered-v2/fr-nfr.md` | `da31640e540b825d4fec555627ea098f092daf4243d5d304fd4c32ae6db734cd` |
| `reference/step-00-input/baseline-filtered-v2/flow.md` | `d0a5fcd029f4f315a02fcd2c057a44907bdf7362fbce17b8664a75b82773595d` |
| `reference/step-00-input/baseline-filtered-v2/state-machine.md` | `b4bc79de9e95f1526ca05326211a6025981b0420f3681b574e37189319f35adf` |
| `reference/step-00-input/baseline-filtered-v2/structure.md` | `fc8facf9088ad320d8dc3a7157edc14b337c1cb7081c3b098bcf91ceab08c560` |
| `reference/step-00-input/baseline-filtered-v2/ui-mockup.html` | `d2b7bfa0cff5700d3ca07f611c03cfa0304c54eafb51387f125e95edd11f7803` |
| `reference/step-00-input/baseline-filtered-v2/ui-contract.md` | `294b660d2e39b3745344f225400eee57c02c25b6efb108a3a7ecce7cdd060e68` |
| `reference/step-00-input/baseline-filtered-v2/us-initial.md` | `56a439f6e22f4a8d17f552b023c3c8fe61556f5bd31f1f1e9b70c1f9da6049d2` |
| `reference/step-00-input/baseline-filtered-v2/fr-check.json` | `1b0c604da9288ce926ba4c98eb258107b130f309f85b1ee96403e02ba0d0f98c` |
| `reference/step-00-input/baseline-filtered-v2/flow-check.json` | `3be4ccd3d045951e7c69e523e6ce2dfab052d45ece39d453741f310435d1c700` |
| `reference/step-00-input/baseline-filtered-v2/ui-check.json` | `c09bf23c92abf0cd9c570f71ff890c1b572f8846c4d2ff8f5d2c3323be448af7` |

Input-set SHA-256: `6f546be9e203d432721300a6b535f595106273ce01b55e32ab8232e51ef4289d`. วิธีคำนวณ: เรียง relative path ในตารางแบบ lexicographic แล้วต่อ UTF-8 `path + TAB + sha256 + LF` ทุกแถว ก่อนทำ SHA-256. ค่านี้เป็น hash ของ manifest รายการ input ไม่ใช่ hash ของ ZIP หรือโฟลเดอร์.

## Output hashes และไฟล์ที่สร้างจริง

รายงานเนื้อหาเดียวกัน 3 ไฟล์:

- `reference/step-01-plan-v1/evaluation/evaluator.md`
- `reference/session/evaluations/plan-v1/plan-review.md`
- `reference/session/evaluations/plan-v1-review.md`

SHA-256 ของ bytes เต็มของรายงานทั้ง 3 ไฟล์บันทึกใน `reference/session/evaluations/plan-v1/plan-review.sha256` ซึ่งสร้างใหม่ในรอบนี้ด้วย. แยก checksum จากตัวรายงานเพื่อไม่ใส่ self-referential hash; manifest นี้ไม่รวม hash ของตัวมันเอง. รายงานทั้งสามต้องมี hash เดียวกัน.

| Task output ตาม snapshot | สถานะ/hash รอบนี้ |
|---|---|
| `reference/session/evaluations/plan-v1-review.md` | CREATED — รายงานประเมินนี้; hash เต็มอยู่ใน plan-review.sha256 |
| `reference/session/execution/fr-baseline-audit-v1.md` | NOT_CREATED — ยังไม่มี output จึงไม่มี hash; ไม่ใช่ผล FAIL ของแผน |
| `reference/session/evaluations/fr-v1-check.md` | NOT_CREATED — ยังไม่มี output จึงไม่มี hash; ไม่ใช่ผล FAIL ของแผน |
| `reference/session/evaluations/flow-v1-check.md` | NOT_CREATED — ยังไม่มี output จึงไม่มี hash; ไม่ใช่ผล FAIL ของแผน |
| `reference/session/test-outline-v1.md` | NOT_CREATED — ยังไม่มี output จึงไม่มี hash; ไม่ใช่ผล FAIL ของแผน |
| `reference/session/evaluations/test-outline-v1-check.md` | NOT_CREATED — ยังไม่มี output จึงไม่มี hash; ไม่ใช่ผล FAIL ของแผน |
| `reference/session/execution/ui-checks-v1.spec.js` | NOT_CREATED — ยังไม่มี output จึงไม่มี hash; ไม่ใช่ผล FAIL ของแผน |
| `reference/session/execution/ui-v1-observations.json` | NOT_CREATED — ยังไม่มี output จึงไม่มี hash; ไม่ใช่ผล FAIL ของแผน |
| `reference/session/evaluations/ui-v1-check.md` | NOT_CREATED — ยังไม่มี output จึงไม่มี hash; ไม่ใช่ผล FAIL ของแผน |
| `reference/session/evaluations/handoff-v1.md` | NOT_CREATED — ยังไม่มี output จึงไม่มี hash; ไม่ใช่ผล FAIL ของแผน |

## สิ่งที่ยังไม่ทดสอบ

| รายการ | ผลรอบนี้ |
|---|---|
| FR/US audit ทุกคอลัมน์และค่าเดิมครบ matrix; checker FR รอบใหม่ | NOT_TESTED — เป็นงาน audit-fr-baseline/verify-fr ถัดไป |
| Flow/state/structure หลังกรองครบทุก mapping/guard/transition | NOT_TESTED — ตรวจเพียงหลักฐานความพร้อมและความเหมาะสมของแผน ไม่ใช่ verify-flow |
| DOM, selector uniqueness, คลิก smoke/edge, responsive ของ HTML สำเนานี้ | NOT_TESTED — ไม่เปิด browser และไม่อนุมานผ่านจาก HTML |
| LAN/Wi-Fi หลายอุปกรณ์, เวลา/โหลดและสัดส่วนตัวอย่างจริง | NOT_TESTED |
| สูตร ETA/ความแม่นยำ/ข้อมูล 7 วันและช่วงเร่งด่วนระบบจริง | NOT_TESTED; ข้อค้าง human-required ยัง BLOCKED สำหรับการยืนยันกฎ |
| ระบบ auth/security จริง, การชำระเงินจริง | NOT_TESTED — ไม่มีบัญชีจริงหรือบริการชำระเงินจริง |
| ติดตั้ง Ubuntu/ตัดอินเทอร์เน็ตภายนอกและใช้งานระบบจริง | NOT_TESTED |

สร้างเฉพาะรายงาน 3 สำเนาและ checksum 1 ไฟล์ตามรายการ; ไม่แก้แผน baseline หรือหลักฐานเดิม. หมายเหตุ ก./ค./ช., Q ทั้ง 18 รหัส, MC-01–MC-03 และหลักฐาน runtime ยังค้างตามขอบเขตที่ระบุ.
