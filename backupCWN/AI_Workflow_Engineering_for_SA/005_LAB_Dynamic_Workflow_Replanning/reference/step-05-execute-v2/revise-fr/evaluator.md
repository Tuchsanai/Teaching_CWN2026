# Evaluator — verify-fr plan-v2
REVIEW_MODE: artifacts; TASK_ID: revise-fr; VERIFY_TASK: verify-fr; RUN_ID: fr-v2-review.
UTC: 2026-09-14T13:14:42.983103Z; ตรวจครั้งที่ 1; แก้ชิ้นงาน/แผน 0 รอบ.
ผล: **PASS เฉพาะเอกสาร FR/NFR v2**; Mock-up runtime / AC ระบบจริง: **NOT_TESTED**; การยืนยันกฎที่ขาด: **BLOCKED**.
Path จากราก LAB: S=reference/session; B=reference/step-00-input/baseline-filtered-v2; V=S/fr-nfr-v2.md; R=reference/step-03-reveal-1/reveal-1.md.
วิธีตรวจจริง: Python แยกตารางเทียบ 21×6=126 เซลล์และบรรทัด US ตรงตัว; difflib เทียบ baseline→V; SHA-256 จาก bytes; อ่าน FR ใหม่/NFR/ผลกระทบ/คำถาม. ไม่ทำ audit ตั้งต้นเต็มซ้ำ.
Gate PASS: hash คู่แผน+impact+schema ตรง verify-plan; audit v1 ตรง fr-v1-check; target ตรง execution:63; ตรวจ schema draft-07/FormatChecker/UTC และ DAG 11 tasks ผ่าน. ใช้ผลแผนเดิมที่ hash ตรงสำหรับ JSON/Markdown/diff/human limits เต็ม.

| US | Source → V:US / V:FR | ผลเอกสารและหลักฐาน | Mock / ระบบจริง |
|---|---|---|---|
| US-01 | B/us-initial.md:3 → 22 / 50 | PASS — 6 เซลล์ตรงต้นทาง; FR ทั้งแถวตรง baseline | NOT_TESTED / NOT_TESTED |
| US-02 | B/us-initial.md:4 → 23 / 51 | PASS — 6 เซลล์ตรงต้นทาง; FR ทั้งแถวตรง baseline | NOT_TESTED / NOT_TESTED |
| US-03 | B/us-initial.md:5 → 24 / 52 | PASS — 6 เซลล์ตรงต้นทาง; FR ทั้งแถวตรง baseline | NOT_TESTED / NOT_TESTED |
| US-04 | B/us-initial.md:6 → 25 / 53 | PASS — 6 เซลล์ตรงต้นทาง; FR ทั้งแถวตรง baseline | NOT_TESTED / NOT_TESTED |
| US-05 | B/us-initial.md:7 → 26 / 54 | PASS — 6 เซลล์ตรงต้นทาง; FR ทั้งแถวตรง baseline; ผลต่อสถานะและ 5 วินาที/18 จาก 20 คงเดิม V:197 | NOT_TESTED / NOT_TESTED |
| US-06 | B/us-initial.md:8 → 27 / 55 | PASS — 6 เซลล์ตรงต้นทาง; FR ทั้งแถวตรง baseline | NOT_TESTED / NOT_TESTED |
| US-07 | B/us-initial.md:9 → 28 / 56 | PASS — 6 เซลล์ตรงต้นทาง; FR ทั้งแถวตรง baseline; สูตร/7 วัน/สองช่วงเดิม/10 นาที/80% คงเดิม V:201; X ไม่ใช่ ETA | NOT_TESTED / NOT_TESTED |
| US-08 | B/us-initial.md:10 → 29 / 57 | PASS — 6 เซลล์ตรงต้นทาง; FR ทั้งแถวตรง baseline; ยอดตรงกัน/วิธีจ่ายเดิม คง payment state V:198 | NOT_TESTED / NOT_TESTED |
| US-09 | R:12 → 30 / 127 | PASS — 6 เซลล์/AC ตรง; ครัวกด→แจ้งลูกค้า 10 วินาที LAN, สองปุ่ม/ลดยอด, 5 จาก 5; NFR V:137 | NOT_TESTED / NOT_TESTED |
| US-10 | B/us-initial.md:11 → 31 / 58 | PASS — 6 เซลล์ตรงต้นทาง; FR ทั้งแถวตรง baseline | NOT_TESTED / NOT_TESTED |
| US-11 | B/us-initial.md:12 → 32 / 59 | PASS — 6 เซลล์ตรงต้นทาง; FR ทั้งแถวตรง baseline; สถานะอาหารถึงหน้าร้านแยกจากเงิน V:197,204; F-01 OPEN | NOT_TESTED / NOT_TESTED |
| US-12 | B/us-initial.md:13 → 33 / 60 | PASS — 6 เซลล์ตรงต้นทาง; FR ทั้งแถวตรง baseline; ทั้งจาน/ตัวเลือกแยกจากรายการในคิว V:200; ช่องเพื่อยังปิด | NOT_TESTED / NOT_TESTED |
| US-13 | B/us-initial.md:14 → 34 / 61 | PASS — 6 เซลล์ตรงต้นทาง; FR ทั้งแถวตรง baseline | NOT_TESTED / NOT_TESTED |
| US-14 | R:13 → 35 / 128 | PASS — 6 เซลล์/AC ตรง; item รอลูกค้าตัดสินใจ; ลูกค้าเลือก→ครัวอัปเดต/ลบ 10 วินาที LAN, 5 จาก 5; NFR V:138 | NOT_TESTED / NOT_TESTED |
| US-15 | B/us-initial.md:15 → 36 / 62 | PASS — 6 เซลล์ตรงต้นทาง; FR ทั้งแถวตรง baseline; log ชื่อผู้ใช้/เวลาและสถานะเงินเดิม V:198 | NOT_TESTED / NOT_TESTED |
| US-16 | B/us-initial.md:16 → 37 / 63 | PASS — 6 เซลล์ตรงต้นทาง; FR ทั้งแถวตรง baseline | NOT_TESTED / NOT_TESTED |
| US-19 | B/us-initial.md:17 → 38 / 64 | PASS — 6 เซลล์ตรงต้นทาง; FR ทั้งแถวตรง baseline; ราคา ณ สั่งและ 5 จาก 5 เดิม V:199 | NOT_TESTED / NOT_TESTED |
| US-20 | B/us-initial.md:18 → 39 / 65 | PASS — 6 เซลล์ตรงต้นทาง; FR ทั้งแถวตรง baseline; คงรหัสอ้าง US-14; Q-20 ยังเปิด V:159,187 | NOT_TESTED / NOT_TESTED |
| US-21 | R:14 → 40 / 129 | PASS — 6 เซลล์/AC ตรง; 15 นาที 00/15/30/45, ยืนยันถึง N, ข้อความก่อนยืนยัน, N=5, 3 จาก 3; ไม่เพิ่ม SLA/สูตร X | NOT_TESTED / NOT_TESTED |
| US-25 | B/us-initial.md:19 → 41 / 66 | PASS — 6 เซลล์ตรงต้นทาง; FR ทั้งแถวตรง baseline | NOT_TESTED / NOT_TESTED |
| US-26 | B/us-initial.md:20 → 42 / 67 | PASS — 6 เซลล์ตรงต้นทาง; FR ทั้งแถวตรง baseline | NOT_TESTED / NOT_TESTED |

PASS การคงเดิม: FR 18/18 แถวและ NFR 15/15 แถวตรง baseline ทั้งบรรทัด รวมวิธีตรวจ; V:50–118. ไม่อ้างว่า FR เก่าทุก AC ตรง US แบบ byte เพราะรูปเขียนเดิม เช่น Wi-Fi/Wi‑Fi ต่างกัน; ใช้ผล audit v1 ตาม hash.
PASS diff: เปลี่ยนหัว/บริบท 18→21 US และประวัติรุ่น; traceability US-20 V:159 กับ Q-20 V:187 ปรับเฉพาะบริบทเปิด FR-14 โดยคงข้อสงสัยรหัสอ้าง. Q เดิม 18 รหัสครบ (17 แถวตรงตัว) และเพิ่ม Q-V2-REFUND/STATE/CAPACITY V:216–218.
PASS ขอบเขต V:197–210: แยกรายการ/ออเดอร์/ชำระเงิน/โต๊ะจาก AI task status; คืนรายการไม่รับรองคืนเงินจริง; ปิด catalog ไม่เปลี่ยนรายการในคิวเอง; X=10 ติดป้าย fixture. ไม่พบเกณฑ์ธุรกิจใหม่ในส่วนที่เพิ่ม.
BLOCKED กฎจริง: หมายเหตุ ก./ค./ช.; mapping เสร็จแล้ว/พร้อมเสิร์ฟ/aggregate/ETA; refund/ส่วนต่าง/คืนซ้ำ/ผู้อนุมัติ; สูตร X/รอยต่อ/นับคืน/เปลี่ยน N/เตือนหรือห้ามยืนยัน; Q เดิมยังเปิดตาม limits ของ plan-v2.
NOT_TESTED Flow/UI v2 และ data-testid/DOM/click/responsive: V:222–246 เป็น mapping ระดับ artifact ที่รอตรวจ; รอบนี้ไม่ได้เปิด browser หรือทดสอบ UI. ไม่รับรองผลคลิกจากการอ่านเอกสาร.
NOT_TESTED ระบบจริง: LAN/Wi-Fi/หลายอุปกรณ์/โหลด/สัดส่วน AC/ETA/7 วัน/log/security/Ubuntu/ติดตั้ง/ถอดอินเทอร์เน็ต/การชำระเงินจริง ทุกข้อ; ไม่มีผลทดสอบจริงให้สรุปผ่าน.
Downstream: อนุญาต revise-flow เฉพาะเอกสาร/offline mock ตาม hash V นี้; verify-flow ต้องตรวจ Flow/state/structure และปิด F-01 ก่อน outline/UI ตามแผน. ไม่ปลด gates ของ verify-ui/handoff หรือกฎ/ระบบจริง; ไม่แก้ snapshot.
FAIL ที่ต้องแก้ใน verify-fr: ไม่พบ; scope/dependency ไม่เปลี่ยน. หากต้องเปลี่ยนส่ง Planner; จำกัดแก้ไม่เกิน 2 รอบต่อปัญหา ไม่คืบหยุดพร้อมหลักฐาน (ข้อตกลงการเรียน ไม่ใช่ AC).
รอบนี้ไม่อ่าน README/reveal-2/เว็บ ไม่เรียก agent หรือ AI CLI เพิ่ม; hash-only ของ impact และ evidence ใช้ผูก gate ไม่อ้างตรวจเนื้อหาใหม่.

| Plan / input / artifact hash | SHA-256 |
|---|---|
| input/plan.schema.json | `cea51a142b808b2c3045994baa68a45d98d280f9d9c5a55962c2015de365431c` |
| S/plan-v2.json | `8682dcba597fd36cadcf0a4724a9a75bd866f551b337281c663ee419c059c828` |
| S/plan-v2.md | `75c5e9b06c7e26fbf7174295d165fbae64be57ea8ff807b4d96884898296ea2c` |
| S/impact-analysis-v2.md | `b4b5dcfbe1d03d1e31d59758b2a9476cecf00b65b0226914ac29f199894ecfb3` |
| S/evaluations/plan-v2-review.md | `470d9248beca3760f63b1df7b54b5bcc24fc18cce5c1994ab3adebcf8403cd0e` |
| S/evaluations/plan-v2/plan-v2-review-evidence.json | `66711881302f8d765012d237d9ffca437816b5e7ac6f25ec58c7cf90d72d1e8a` |
| S/evaluations/fr-v1-check.md | `b533a2d6b8618f590d3de91bdc4250172ad8d987df6060860f16e0a672403c5a` |
| S/execution/fr-baseline-audit-v1.md | `78f8ce610526fdaa3e7911b3765fbff8246ea223d9772611e370bb42d5374175` |
| S/execution/plan-v2/fr-v2-run/revise-fr.md | `571c4226e328461c807411303a66737876618d768bcbc19d261b76a32dfd745b` |
| S/fr-nfr-v2.md | `2cbdde11bb3fd5e62f338a1ea74f65d11112f3ea56e8a10ed9d24b08a1dcf0bb` |
| B/us-initial.md | `56a439f6e22f4a8d17f552b023c3c8fe61556f5bd31f1f1e9b70c1f9da6049d2` |
| B/fr-nfr.md | `da31640e540b825d4fec555627ea098f092daf4243d5d304fd4c32ae6db734cd` |
| B/input-audit.md | `d4100680ed1f31ea3351144f202f85343fb47a23acfa0305116731ab8bb1bbd8` |
| B/provenance.md | `8059b1b47647d690ed7a73e6b4b9751e209edb3905868a4729269fb79330739a` |
| R | `1fde792db1fdcf211be4a171fd88c61184ce892720832023fcaefad6a67f8917` |
Input-set (15 ไฟล์ด้านบน; path จากราก LAB+TAB+SHA256+LF เรียง path): `e4404c2c35faa001abee13c21c78dc7bfc2a554d4ed60ee9f03703b2cf3ffc3f`.
สร้างจริง: S/evaluations/fr-v2-check.md; S/evaluations/plan-v2/fr-v2-review.md; reference/step-05-execute-v2/revise-fr/evaluation/evaluator.md. Hash รายงานสองไฟล์แรกอยู่ evaluator.md; ไม่ทำ self-hash.

| Output report | SHA-256 |
|---|---|
| reference/session/evaluations/fr-v2-check.md | `b21ee2b862656cf871d69117c44d2d5168154360da088c929bf87e033151819b` |
| reference/session/evaluations/plan-v2/fr-v2-review.md | `b21ee2b862656cf871d69117c44d2d5168154360da088c929bf87e033151819b` |
