# ผลตรวจแผน v3 และ impact

REVIEW_MODE: plan; TASK_ID: all; VERIFY_TASK: verify-plan; RUN_ID: plan-v3-review.
UTC: 2026-09-14T14:13:08.159143Z. ตรวจครั้งที่ 1; ไม่แก้แผนหรือ impact; แก้ปัญหาชิ้นงาน 0 รอบ.

**PLAN_READY — เฉพาะแผนงานเอกสารวิเคราะห์และการเตรียม mock ที่ระบุสมมติฐาน ภายใต้ผลตรวจแต่ละขั้น.** ไม่พบข้อบกพร่องที่บังคับแก้ก่อนรับแผนในขอบเขตนี้. กฎธุรกิจที่ยังไม่มีคำตอบ **BLOCKED**; ชิ้นงานและการทดสอบ v3 **NOT_TESTED**. รอบนี้ตรวจแผนและ impact เท่านั้น ไม่เริ่ม execute v3.

Path จากราก LAB: S=reference/session; C=reference/step-07-plan-v3; B=reference/step-00-input/baseline-filtered-v2; R1=reference/step-03-reveal-1/reveal-1.md; R2=reference/step-06-reveal-2/reveal-2.md. Locator JSON ใช้ชื่อ collection และ id เพื่อค้นรายการ เช่น tasks[id=verify-plan].

วิธีตรวจจริง: อ่านคู่แผน v3/v2, impact v3, audit/provenance, reveal ที่เปิดแล้วสองชุด และรายงาน v2 ของ plan/FR/Flow/outline/UI/handoff; ตรวจจุดข้อมูลและสัญญา v2 ที่ impact อ้าง. ใช้ Python ใน session นี้ตรวจ Draft7Validator พร้อม FormatChecker, UTC, IDs, DAG, input/output, diff และเทียบทุกฟิลด์ JSON กับตาราง Markdown หลังแทน path alias/อักขระตาราง. คำนวณ SHA-256 จาก bytes เทียบหลักฐานเดิม; ไม่ยึด PASS_STRUCTURAL ของ Planner เป็นผล Evaluator.

ใช้ผลตรวจ 126 เซลล์ของ FR v2 ที่ผูก hash ตรง ไม่ตรวจ 126 เซลล์ซ้ำ. ตรวจการยก 21 แถวเดิมเข้า snapshot ใหม่ตรงทั้งบรรทัด และ 5 แถว R2 ตรงทุกคอลัมน์ใน decisions[id=d-source-rows] กับ impact:9–13; ไม่มีการเพิ่มเกณฑ์รับ. ไม่อ่าน README/ต้นฉบับนอกชุด/เว็บ ไม่เรียก agent หรือ AI CLI เพิ่ม ไม่รัน browser และไม่อ้างเปิดดูภาพรอบนี้.

| ข้อค้นพบ | ผล / ระดับ block | หลักฐานและ locator | การแก้หรือผลต่อ downstream |
|---|---|---|---|
| Schema/UTC/IDs/DAG | PASS — แผน | Draft-07 ไม่มี error; created_at ลงท้าย Z และ offset 0; 13 tasks, 19 decisions, 17 limits มี id ไม่ซ้ำ; 37 dependency edges ไม่มีปลายทางหาย/self-edge/วงจร; P3 tasks/created_at | ไม่ต้องแก้โครงสร้าง |
| Producer → consumer / binding inputs | PASS — แผน | ตรวจ 78 input references ที่เป็น output ของ task ในแผน ทุก producer อยู่ใน ancestors ของ consumer; external inputs มีจริง; outputs ไม่ชนกัน. ก่อนตรวจมี output เดิมเฉพาะ audit ที่ done | output v3 ที่ยังไม่มีเป็นงานอนาคตที่มี producer; downstream ต้องรอไฟล์จริงและ PASS ของ hash รุ่นนั้นตาม l-check-gates |
| JSON/Markdown และ canonical | PASS — แผน | ตารางตรงครบ tasks 13/13, decisions 19/19, reuse 24/24, limits 17/17; version/trigger/UTC ตรง. C กับ S ตรงทุก byte ทั้ง JSON, Markdown และ impact | รายงานนี้ผูก hash คู่แผนและ impact ตามตารางท้าย |
| Diff เพิ่ม/แยก/ยกเลิก/ลำดับ | PASS — แผน | S/plan-v3.md:9–21; d-reuse-no-revise; impact:23–27,53. คง 11 task IDs เดิม; เพิ่ม define-data-contract จาก revise-flow และ verify-data-contract จาก verify-flow; audit เดิมไม่เปลี่ยน; ไม่ลบ/ยกเลิกงาน | ไม่มี cancel task และไม่มี status cancelled จึงไม่มี active task รอ cancelled. ไม่ต้องสร้างการยกเลิกเทียม |
| ความใหม่ของหลักฐาน reuse | PASS — ประวัติเท่านั้น | Hash inputs เดิม 44/44 ตรง manifest; history prefix เดิม 35,875 bytes ตรงแยกต่างหาก. Bindings v2 ของ plan/FR/Flow/outline 12/12 ตรงรายงานจริง; UI/contract/observations/evidence ตรง ui-v2-check | สถานะ v3 คือ done 1 งาน audit, needs_recheck 10 งาน, planned 2 งานใหม่. ไม่ใช้ v2 PASS ปลด gates v3 |
| อำนาจตัดสินใจและข้อรอมนุษย์ | PASS การผูกข้อจำกัด; BLOCKED การยืนยันกฎ | human-required 11/11 ข้อมี l-q-* blocking=true อ้างกลับ decision และครอบคลุม 11 งาน FR/data/Flow/outline/UI/handoff; ไม่มี affected task หาย; S/plan-v3.md:47–57,91–107 | คงหมายเหตุ ก./ค./ช., สถานะ/ETA, payment/refund, mapping, operations/environment, capacity/X และคำถามใหม่เรื่องบิล/รายงาน/คิว/toggle/history; คำตอบต้องมีหลักฐานก่อนแก้รุ่นถัดไป |
| แยกสถานะและยอด | PASS — แผน | impact:35–41; tasks[id=define-data-contract,verify-flow,revise-ui]; S/structure-v2.md:84–97, state-machine-v2.md:65–83, ui-contract-v2.md:175–181 | แยกรายการ/ออเดอร์/เงิน/โต๊ะจาก AI task; original snapshot แยก adjusted; คืนรายการไม่ยืนยันคืนเงินจริง ไม่ทำ paid กลับเป็นค้างจ่ายเอง |
| สัญญา UI และผลรันเดิม | PASS การวางงานตรวจ; v3 NOT_TESTED | tasks[id=revise-ui,verify-ui]; ui-v2-check:20–22,49–50,58–64. คง data-testid/roles/reset และความหมาย front-total เดิม; verify-ui ระบุ browser file:// ปิด network พร้อม script/hash/UTC/actual | 19/19 และ 8/8 เป็น mock เดิม; 8 executions = 6 สถานการณ์ไม่ซ้ำ โดย N=5 ซ้ำ 3 context ที่ 12:00. ไม่แทน full outline หรือระบบจริง |
| สายที่มานอกสำเนา | ข้อจำกัดไม่บล็อกแผน | B/input-audit.md; B/provenance.md; limits[id=l-provenance]. Hash baseline 10/10 อยู่ใน manifest ที่ตรง แต่รายงาน upstream มีข้อจำกัด target/ก่อนกรอง | ไม่รับรอง provenance ภายนอกชุด และไม่ตามลิงก์เพื่อเติมข้อมูลที่หาย |

| US / ผลตรวจแผน | ผลโดยตรงและต่อเนื่องที่ต้องตรวจ | หลักฐาน / ขอบเขตที่ยังบล็อก |
|---|---|---|
| US-17 — PASS | session → รอบสั่ง → order/items/options/snapshot → บิล → US-08/15 → US-23; รวม 3 รอบ แสดงแยกรอบ อย่างน้อย 9 จาก 10 โต๊ะ | R2:12; impact:23,35; data producer + verifier มาก่อน Flow/UI. จ่ายบางรอบ/การผูกรอบ/การนับบิลซ้ำรอ d-human-bill-report |
| US-18 — PASS | confirmed timestamp → อายุและจำนวนออเดอร์ค้าง → ครัว; กระทบ US-05/07/10/11/21. เกิน 15 นาทีจากลูกค้ายืนยัน; 10 ออเดอร์ อย่างน้อย 9 จาก 10 | R2:13; impact:24,28–29,36; แยก client confirmation จาก received timestamp/เลข monotonic, จำนวนจาน และหน้าต่าง capacity; ไม่เปลี่ยนคิวเพียงเพราะสีแดง. นิยามค้าง/พร้อมเสิร์ฟรอมนุษย์ |
| US-22 — PASS | สวิตช์กลับบ้าน → โหลดหน้าใหม่ → ซ่อนโหมด ภายใน 10 วินาทีบน LAN อย่างน้อย 9 จาก 10; QR หน้าร้านยังใช้ได้; ตรวจ US-02/03/04/15/16 ต่อ | R2:14; impact:25,38; รอบโต๊ะ/ตัวเลือก/ช่องทาง/เลขรับต้องคงเดิม. ตะกร้าและออเดอร์ก่อนปิดนอกเกณฑ์รับยังเป็นคำถาม |
| US-23 — PASS | ข้อมูลบิล/snapshot/adjustment/payment → รายงานเฉพาะจ่ายแล้ว → CSV; US-08/09/15/17/19/25. รายงาน 5 วินาที Ubuntu, นับมือ 20 ใบ, คลาดเคลื่อน 0 บาท, CSV เปิด LibreOffice | R2:15; impact:26,30,32–35,40. revise-flow/UI รอ verify-data-contract; ห้ามใช้ placeholder สิทธิ์เดิมเป็นรายงานผ่านแล้ว. ฐาน original/adjusted และวันรับรู้รอมนุษย์ |
| US-24 — PASS | เหตุการณ์กดวัตถุดิบหมดพร้อมชื่อ/เวลา/ผู้กด → จำนวนครั้งต่อสัปดาห์ → ประวัติ; ตรวจ US-06/12/13/14/20/25 ที่เกี่ยว. กดทดสอบ 10 ครั้งพบอย่างน้อย 9 จาก 10 | R2:16; impact:27,31,39; producer event ใน data contract มาก่อน history consumer; ห้ามใช้จำนวนเมนูปิดหรือ item ทำไม่ได้แทนความถี่. กดซ้ำ/ขอบสัปดาห์/เขตเวลารอมนุษย์ |
| US-05/07/08/12/15/19 — PASS การส่งต่อ | impact:28–33 มี regression แยกสถานะอาหาร/ETA/ยอดและวิธีจ่าย/catalog/log/ราคา ณ สั่ง; เก็บสูตร หน่วย ตัวเลขและสัดส่วนเดิม รวม snapshot 5 ใบ | หลักฐาน v2 FR/Flow/outline ตาม hash; ทั้ง 11 งานที่ได้รับผลกระทบมี us_refs 26 รหัส. ผลใหม่ต้องตรวจตามรุ่น ไม่รับรองจาก smoke เดิม |

Downstream: ผลนี้ผ่าน verify-plan เฉพาะขอบเขตเอกสารและสมมติฐานที่ระบุ; เมื่อเริ่มกิจกรรมถัดไป revise-fr จึงใช้รายงานนี้ได้. จากนั้นต้องมีผลจริงตามสาย FR → verify-fr → data contract → verify-data-contract → Flow → verify-flow → outline → verify-test-outline → UI → verify-ui → handoff. ทั้งรายงานเฉพาะจ่ายแล้วและประวัติวัตถุดิบหมดต้องรอข้อมูลและผลตรวจข้อมูลก่อน. รายงานนี้ไม่ปลด l-real-scope, l-q-*, l-browser หรือผลตรวจขั้นถัดไป และไม่เปลี่ยน snapshot เป็น done.

ข้อบกพร่องบังคับแก้: ไม่พบในขอบเขตแผน/impact. ข้อค้างไม่ใช่ FAIL ของระบบที่ยังไม่ได้ทดสอบ. หากคำตอบมนุษย์ทำให้ขอบเขต/dependency เปลี่ยน ให้ส่ง Planner สร้างรุ่นถัดไปพร้อม trigger/diff/หลักฐาน ห้ามแก้ v3 ย้อนหลัง. จำกัดแก้ไม่เกิน 2 รอบต่อปัญหา ไม่คืบให้หยุดพร้อมหลักฐาน; เป็นข้อตกลงการเรียน ไม่ใช่เกณฑ์รับของร้าน. สคริปต์ตรวจชั่วคราวมี syntax error ก่อนทำงานหนึ่งครั้ง แก้แล้วรันสำเร็จ ไม่มีการเปลี่ยนไฟล์หลักฐานหรือเพิ่มรอบแก้แผน.

ยังไม่ทดสอบ: v3 ทุกชิ้นงานและ runtime; v2 full outline, US-09 และ US-14 สองชุด 5/5, N=5 ถึง threshold ที่ 12:15/12:30, หลายรายการ/5 snapshots/คำสั่งซ้ำภายใน/keyboard และช่องว่าง ui-v2-check:58–63; LAN/Wi-Fi/หลายอุปกรณ์, สัดส่วนและเวลาตามเกณฑ์รับระบบจริง, ETA/ประวัติ 7 วัน, Ubuntu install, LibreOffice, ความปลอดภัยจริง และการชำระ/คืนเงินจริง. ไม่ใช้ข้อมูลหรือบัญชีจริง.

| Plan / input / หลักฐาน | SHA-256 |
|---|---|
| P3 — S/plan-v3.json = C/plan-v3.json | `2cc75857183b0fefd5f2631638442494dce2ff63436b8fa768ad5c2c13420125` |
| M3 — S/plan-v3.md = C/plan-v3.md | `a109d733c6d892c49397246f24928755f344d2fb92f181e141a444f5aa19e83c` |
| Impact — S/impact-analysis-v3.md = C/impact-analysis-v3.md | `beae0c4a4a9263815132134f7d0a2930d6e784b6ea7d57e6419c8a7f6264467e` |
| input/plan.schema.json | `cea51a142b808b2c3045994baa68a45d98d280f9d9c5a55962c2015de365431c` |
| S/evaluations/plan-v3-validation.json | `f4900041348c1fa905c6bc04afbf9c07d8d2a9f9e1953b6f145617c0bae9dcd0` |
| S/plan-v2.json | `8682dcba597fd36cadcf0a4724a9a75bd866f551b337281c663ee419c059c828` |
| S/plan-v2.md | `75c5e9b06c7e26fbf7174295d165fbae64be57ea8ff807b4d96884898296ea2c` |
| B/input-audit.md | `d4100680ed1f31ea3351144f202f85343fb47a23acfa0305116731ab8bb1bbd8` |
| B/provenance.md | `8059b1b47647d690ed7a73e6b4b9751e209edb3905868a4729269fb79330739a` |
| R1 | `1fde792db1fdcf211be4a171fd88c61184ce892720832023fcaefad6a67f8917` |
| R2 | `08fa0611441305ca4e85ad461a8fd68c580ec47c495957b5d10002333ef7c023` |
| S/evaluations/fr-v2-check.md | `b21ee2b862656cf871d69117c44d2d5168154360da088c929bf87e033151819b` |
| S/evaluations/flow-v2-check.md | `8eb49dba6953c6d63a3eb833f54a67c74bad9b42978a83ea97408d21e18f8c1d` |
| S/evaluations/test-outline-v2-check.md | `0f982d0c0d6ee72264eca64f36bc6b0105edcaafab122f2d1654562d43cd3c2f` |
| S/evaluations/ui-v2-check.md | `295ecaad9d2b5673c8b2e585fba2c32ec877b1f98fa8e9e474d6c8deade463cd` |
| S/evaluations/handoff-v2.md | `649defa8112322d99eb7c30c986a6811c7d495236a17ec854e3ae5f6114a349a` |
| S/execution/ui-v2-observations.json | `bf16ddef9c6ab46303702cbb18e5a3f0fe1bb1c0c969bc511b47fba825cec941` |
| S/execution/ui-v2-evaluator-evidence.json | `fe9924ef5c94ca19994d45e78c18bbd436abb4fd934bce72361f32f74c06cb92` |

Input-set ปัจจุบัน 51 ไฟล์: `ee0be316b9449e9ca53466d0286c9ac192e5bdfb8fe9c2dd066a0c7b7edafbc4`. วิธีคำนวณ: path จากราก LAB + TAB + SHA-256 + LF เรียง path; รายการคือ input_hashes_before ใน S/evaluations/plan-v3-validation.json ยกเว้น impact-analysis.md (history) แล้วเพิ่ม S และ C ของ plan-v3.json, plan-v3.md, impact-analysis-v3.md รวม 6 ไฟล์ และ validation JSON อีก 1 ไฟล์. History ตรวจ prefix แยกโดยไม่ใช้ hash ก่อน append มาเทียบทั้งไฟล์; hash history ปัจจุบันตรง history_after. การตรวจ hash ไม่อ้างว่าอ่านเนื้อหาทุกไฟล์ซ้ำ.

สร้างจริง: S/evaluations/plan-v3-review.md (output ของ verify-plan), S/evaluations/plan-v3/plan-v3-review.md (สำเนารายงานเดียวกัน) และ C/evaluation/evaluator.md (สรุปพร้อม output hashes ของรายงานสองสำเนา). ไม่มี self-hash ในรายงาน; ไม่เขียนทับแผน/impact/หลักฐานเดิม.
