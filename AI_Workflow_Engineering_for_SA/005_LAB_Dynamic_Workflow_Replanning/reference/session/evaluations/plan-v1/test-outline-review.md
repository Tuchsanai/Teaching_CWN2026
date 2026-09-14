# verify-test-outline — ตรวจหลักฐานและ dependency

REVIEW_MODE: artifacts; TASK_ID: draft-test-outline; VERIFY_TASK: verify-test-outline; RUN_ID: test-outline-review; plan-v1; UTC: 2026-09-14T12:58:42.155553Z.
ผลรวม **BLOCKED**: verify-fr PASS เอกสาร แต่ verify-flow FAIL F-01; l-check-gates/depends_on ยังไม่ผ่าน (evaluations/flow-v1-check.md:4,35–40).
ตารางด้านล่างเป็นข้อค้นพบตรวจร่างครบ 18 US เพื่อส่ง Planner ไม่ใช่การปลด gate หรือ PASS ของ verify-test-outline; Mock-up runtime/ระบบจริง NOT_TESTED ทุกข้อ.
Path ย่อ: S=reference/session; B=reference/step-00-input/baseline-filtered-v2; O=S/test-outline-v1.md; U=B/us-initial.md; R=B/fr-nfr.md; F=B/flow.md; T=B/structure.md; H=B/ui-mockup.html; C=B/ui-contract.md.
วิธีตรวจจริง: อ่านเอกสารและ HTML source, Python parse ตารางแบบ scoped/เทียบข้อความและ SHA-256; ไม่มี browser/DOM/click/LAN และไม่ได้รัน verify-ui.
PASS ข้อความ: U→audit ตาราง 9 คอลัมน์ ส่วน US เดิม 18×6=108 เซลล์ตรง; O เกณฑ์รับ 18/18 ตรง U และ source locator ถูกต้อง; อีก 5 คอลัมน์อ้างต้นฉบับ ไม่ได้คัดซ้ำใน O.
ตรวจประกอบ: schema draft-07+FormatChecker/UTC ผ่าน; 8 task/20 edges ไม่มีซ้ำ/self/cycle/อ้างหาย/cancel ขัดกัน; JSON 560 string values พบใน Markdown; ไม่ประเมิน PLAN_READY ใหม่.
Hash ผูก verify-fr 10/10, verify-flow 8/8, manifest 10/10, reuse 12/12 และ execution→O ตรง; hash ตรงไม่ทำให้ผล FAIL กลายเป็น PASS; ไม่กำหนดอายุหลักฐานขึ้นเอง.

| US | Locator U → R → O; Flow coverage → UI source | ผลตรวจข้อความ/แผนกรณี (ไม่ปลด gate) | Mock-up / ระบบจริง |
|---|---|---|---|
| US-01 | U:3 → R:20 → O:21; F:42 → H:343–344 | PASS — QR/จุดวัด/ไม่ login | NOT_TESTED / NOT_TESTED |
| US-02 | U:4 → R:21 → O:22; F:43 → H:343,355 | PASS — table_id/20 โต๊ะ ไม่แทนด้วย seed 3 โต๊ะ | NOT_TESTED / NOT_TESTED |
| US-03 | U:5 → R:22 → O:23; F:44 → H:343,354,373 | PASS — ช่วงรับ 15 นาที/ขั้นต่ำ 20 นาที/10 ใบ | NOT_TESTED / NOT_TESTED |
| US-04 | U:6 → R:23 → O:24; F:45 → H:344–345,354 | PASS — ตัวเลือกครบ/ยอดก่อนยืนยัน/19 จาก 20 | NOT_TESTED / NOT_TESTED |
| US-05 | U:7 → R:24 → O:25; F:46 → H:347,354 | PASS — จอลูกค้าไม่รีเฟรช/ชื่อสถานะแยก ETA | NOT_TESTED / NOT_TESTED |
| US-06 | U:8 → R:25 → O:26; F:47 → H:344,354,366–369 | PASS — ป้าย+ปุ่มปิด+ปฏิเสธตะกร้าเก่า | NOT_TESTED / NOT_TESTED |
| US-07 | U:9 → R:26 → O:27; F:48 → H:346 | PASS — สูตร/7 วัน/สองช่วงเร่งด่วน/80% คง; ไม่มี ETA จริง | NOT_TESTED / NOT_TESTED |
| US-08 | U:10 → R:27 → O:28; F:49 → H:347,350,355–356,378 | PASS — สองวิธี/ยอด/3 กรณี/fallback ไม่เท่ากับจ่ายแล้ว | NOT_TESTED / NOT_TESTED |
| US-10 | U:11 → R:28 → O:29; F:50 → H:354,375 | PASS — timestamp/monotonic/30 ใบ×3 รอบ/มือถือ 2 เครื่อง | NOT_TESTED / NOT_TESTED |
| US-11 | U:12 → R:29 → O:30; F:51 → H:354–355 | PASS AC; BLOCKED F-01 — Flow ขาดจอหน้าร้าน | NOT_TESTED / NOT_TESTED |
| US-12 | U:13 → R:30 → O:31; F:52 → H:344–345,354 | PASS — ทั้งจาน/เฉพาะตัวเลือก/5 ชนิด; ไม่กู้ช่องปิด | NOT_TESTED / NOT_TESTED |
| US-13 | U:14 → R:31 → O:32; F:53 → H:320,344–345,354 | PASS — ชุดเปิดคืน/วัตถุดิบซ้อนเป็นสมมติฐาน | NOT_TESTED / NOT_TESTED |
| US-15 | U:15 → R:32 → O:33; F:54 → H:303–304,355,374–376 | PASS — T-001/00:00 แยกเลขออเดอร์; เหตุการณ์เงิน+log | NOT_TESTED / NOT_TESTED |
| US-16 | U:16 → R:33 → O:34; F:55 → H:343,355,366 | PASS — session ใหม่/ปฏิเสธรอบเก่า; ไม่บังคับจ่ายครบ | NOT_TESTED / NOT_TESTED |
| US-19 | U:17 → R:34 → O:35; F:56 → H:344–345,358 | PASS — รูป≤2 MB/0–10 ตัวเลือก/ราคาเดิม5ใบ/ลบแมป | NOT_TESTED / NOT_TESTED |
| US-20 | U:18 → R:35 → O:36; F:57 → H:359 | PASS — เมนูต้องมีอยู่/คง US-14/5 เมนู; mapping ยังรอยืนยัน | NOT_TESTED / NOT_TESTED |
| US-25 | U:19 → R:36 → O:37; F:58 → H:356,360–364 | PASS — บัญชีจำลอง/PIN/ล็อก/3×2 URL; รายงาน placeholder | NOT_TESTED / NOT_TESTED |
| US-26 | U:20 → R:37 → O:38; F:59 → H:305,340,354–355 | PASS — คง 30 นาที/20 ใบ/เก็บในร้าน; ขาดตัวติดตั้งจริง | NOT_TESTED / NOT_TESTED |

F-01 ยืนยันจาก F:51,406,447,449,451 และ T:22,69,71,73,223: US-11/MRG-05 มีครัวกับลูกค้า แต่จอ/module หน้าร้านไม่มี FR-11; F:71/R:29 ระบุผู้รับหน้าร้านอยู่จริง.
O:30 วาง expected หน้าร้านถูก AC; C:67 และ H:355 มีข้อความสถานะครัวใน source แต่ไม่ใช่หลักฐานคลิกและไม่แก้ traceability ใน F/T. O:17,40 ยังใช้ F* / NEEDS_RECHECK ถูกเปิดไว้.
แก้เฉพาะจุด F-01: ส่ง Planner วาง producer/outputs รุ่นใหม่เชื่อม US-11/FR-11/MRG-05 กับจอรับสถานะหน้าร้านและ module/coverage ให้ F/T ตรงกัน แล้ว verify-flow ใหม่; ห้ามแก้ baseline/ทับ O หรือข้าม dependency.
ผลกระทบ: US-05/07 ใช้สถานะครัวร่วม US-11 แต่จุดรับลูกค้าและจุดจบ ETA ต่างกัน; ไม่รับรอง เสร็จแล้ว=พร้อมเสิร์ฟ (O:25,27,30; state-machine.md:40,51–53).
ผลกระทบต่อเนื่อง: US-12/13/19/20 → US-06/04 → US-08/15 ผ่านเมนู/ตัวเลือก/ราคา snapshot; ปิดโต๊ะ US-16 ไม่ทำให้จ่ายแล้ว และไม่ย้อนเปลี่ยนออเดอร์เดิมเอง (O:26,28,31–36; F:74–91).
PASS การแยกขอบเขต: รายการไม่เพิ่ม transition ที่ปิดไว้; ออเดอร์/ชำระเงิน/โต๊ะ/table session แยกกัน และ AI planned/EXECUTED ไม่ใช่ state ธุรกิจ (O:4,17,42; state-machine.md:40–54).
PASS แผนตรวจ fixture: O:13–15,21–38 ครอบ role/reset/scoped selectors/template/stock/cash/slip/ราคา/session/direct route/รูป/ตัวเลือก/ข้ามวัน/stock ซ้อน/viewport; C:7–117 รองรับฐาน fixture; H hash คงเดิม. DOM uniqueness/คลิก/พฤติกรรมจริง NOT_TESTED.
ข้อค้าง BLOCKED เฉพาะรับรองกฎจริง: หมายเหตุ ก./ค./ช., Q 18 รหัส, MC-01–03, Unknown permissions และสภาพติดตั้ง; O:42 คงสมมติฐาน ไม่สร้าง AC ใหม่. US-07 ไม่มี implementation ETA; US-26 ไม่มีตัวติดตั้ง/ผล offline จริง.
Downstream BLOCKED: verify-test-outline → verify-ui → evaluate-handoff; draft-test-outline ยังผลิตได้จาก verify-fr ตาม snapshot. เมื่อ Flow PASS และ hash เปลี่ยนให้ตรวจ O ข้ามเอกสารใหม่ตามแผนรุ่นถัดไป.
ข้อบกพร่องใหม่ในข้อความ O: ไม่พบจากการตรวจนี้; F-01 เป็นข้อบกพร่อง upstream ที่ยังเปิด. ตรวจครั้งที่ 1 แก้ 0 รอบ; จำกัดแก้ไม่เกิน 2 รอบต่อปัญหาเป็นข้อตกลงการเรียน ไม่ใช่ AC ร้าน.
NOT_TESTED: browser/responsive/QR/LAN/Wi-Fi/โหลด/สัดส่วน AC/server log/ETA/security/Ubuntu/ตัดอินเทอร์เน็ต/ชำระเงินจริง; ผลเก่า upstream ไม่ใช่ผลรันนี้. ไม่เปิด README/reveal/เว็บ ไม่เรียก agent/CLI เพิ่ม.

Input-set SHA-256: `1eaf964db38015d5461e6e2edd102f75aeea73e2f0b4fe494f12417ae3e24159` = UTF-8 path+TAB+sha256+LF เรียง path ของตารางนี้ (รวมแผน/target O; ไม่รวมรายงานที่สร้าง).
| Input (path จากราก LAB; B/S ตามนิยาม) | SHA-256 |
|---|---|
| input/plan.schema.json | `cea51a142b808b2c3045994baa68a45d98d280f9d9c5a55962c2015de365431c` |
| S/evaluations/flow-v1-check.md | `43cd1d0cf505bb509d9453f060503c82ed300332324c9893168eb74f05a70141` |
| S/evaluations/fr-v1-check.md | `b533a2d6b8618f590d3de91bdc4250172ad8d987df6060860f16e0a672403c5a` |
| S/evaluations/plan-v1-review.md | `f2facd03b3cd1f74969c110bfc336226b7d331f65042e51b036b5995166b3eb1` |
| S/execution/fr-baseline-audit-v1.md | `78f8ce610526fdaa3e7911b3765fbff8246ea223d9772611e370bb42d5374175` |
| S/execution/plan-v1/test-outline-run/draft-test-outline.md | `6ac65ca1a2cd45d5034c299677eab8b8545dcb6ac2257aada1c27cc0643814f8` |
| S/plan-v1.json | `4bd023624fb2cb5c1ec9975528e8ffbcb6ac830cd40f9b61c5db28523ae25cfe` |
| S/plan-v1.md | `10f2d1da058fafe1a6ed75047ad157ab0694cb7ee40ddd89c91874fa4d3310ae` |
| S/test-outline-v1.md | `6bdeccb7cf14fcdf03f0fa56578e1595c1ec3ea2dda67c3f74d4bba4c07ae18c` |
| B/flow-check.json | `3be4ccd3d045951e7c69e523e6ce2dfab052d45ece39d453741f310435d1c700` |
| B/flow.md | `d0a5fcd029f4f315a02fcd2c057a44907bdf7362fbce17b8664a75b82773595d` |
| B/fr-check.json | `1b0c604da9288ce926ba4c98eb258107b130f309f85b1ee96403e02ba0d0f98c` |
| B/fr-nfr.md | `da31640e540b825d4fec555627ea098f092daf4243d5d304fd4c32ae6db734cd` |
| B/input-audit.md | `d4100680ed1f31ea3351144f202f85343fb47a23acfa0305116731ab8bb1bbd8` |
| B/provenance.md | `8059b1b47647d690ed7a73e6b4b9751e209edb3905868a4729269fb79330739a` |
| B/state-machine.md | `b4bc79de9e95f1526ca05326211a6025981b0420f3681b574e37189319f35adf` |
| B/structure.md | `fc8facf9088ad320d8dc3a7157edc14b337c1cb7081c3b098bcf91ceab08c560` |
| B/ui-check.json | `c09bf23c92abf0cd9c570f71ff890c1b572f8846c4d2ff8f5d2c3323be448af7` |
| B/ui-contract.md | `294b660d2e39b3745344f225400eee57c02c25b6efb108a3a7ecce7cdd060e68` |
| B/ui-mockup.html | `d2b7bfa0cff5700d3ca07f611c03cfa0304c54eafb51387f125e95edd11f7803` |
| B/us-initial.md | `56a439f6e22f4a8d17f552b023c3c8fe61556f5bd31f1f1e9b70c1f9da6049d2` |

ไฟล์ผลตามแผน: S/evaluations/test-outline-v1-check.md; รายงานรัน: S/evaluations/plan-v1/test-outline-review.md; สรุปและ output hashes: evaluator.md ใน cwd. ไม่ใส่ self-hash ที่วนกลับ.
Output SHA-256 ของ S/evaluations/test-outline-v1-check.md: `ea6c1f13c350bd5103493061d8b14fba8115cba46a8b900df42ec0445a1aa9a2`.
