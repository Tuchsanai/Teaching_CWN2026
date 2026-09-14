# verify-fr — ผลตรวจเอกสาร

REVIEW_MODE: artifacts; TASK_ID: audit-fr-baseline; บทบาทงาน: verify-fr; RUN_ID: audit-fr-review; plan-v1.
ตรวจ UTC: 2026-09-14T12:45:46.464876Z; ผล: **PASS เฉพาะความสอดคล้องเอกสาร**; ระบบจริงและ Mock-up runtime: **NOT_TESTED**.
ตรวจครั้งที่ 1; แก้ artifacts 0 รอบ; ไม่แก้ snapshot, ไม่อ่าน README/reveal/เว็บ และไม่เรียก agent/CLI เพิ่ม.
Path ย่อจากราก LAB; B = reference/step-00-input/baseline-filtered-v2; A = reference/session/execution/fr-baseline-audit-v1.md.

วิธีตรวจจริง: Python parse ตารางและเทียบเซลล์ตรงตัว 18 แถว × 6 คอลัมน์ = 108 เซลล์; ตรวจ locator FR/NFR/Q ทุกแถว, SHA-256 จาก bytes; อ่านพฤติกรรม/AC/วิธีตรวจ/ข้อจำกัดเทียบความหมายรายข้อ.
108 เซลล์นี้เป็นการเทียบข้อความครั้งนี้ ไม่ใช่ผล checker upstream 108/108 หรือผลทดสอบ AC; numeric-token check ใช้เสริมการอ่านสูตร/เหตุการณ์/ตัวหารเท่านั้น.
Gate PASS: evaluations/plan-v1-review.md ผูก hash คู่แผนตรง; execution report ผูก A ตรง; manifest 10/10 และ reuse 12/12 ตรง; ไม่มีหลักฐานหมดอายุเพิ่มเติมให้กำหนดเอง.
ตรวจแผนประกอบ: draft-07 + FormatChecker/UTC/duplicate keys ผ่าน; 8 task, 20 dependency ไม่มี self/cycle/target หาย/cancel ขัดกัน; 560 string values พบใน Markdown. ใช้ verdict verify-plan เดิมสำหรับการทบทวนแผนเต็ม.

| US | Locator B/us-initial.md → B/fr-nfr.md → A | ผลเอกสาร | Mock-up / ระบบจริง |
|---|---|---|---|
| US-01 | :3 → :20 → :37 | PASS — 6 เซลล์เดิมและ FR/AC/วิธีตรวจสอดคล้อง | NOT_TESTED / NOT_TESTED |
| US-02 | :4 → :21 → :38 | PASS — 6 เซลล์เดิมและ FR/AC/วิธีตรวจสอดคล้อง | NOT_TESTED / NOT_TESTED |
| US-03 | :5 → :22 → :39 | PASS — 6 เซลล์เดิมและ FR/AC/วิธีตรวจสอดคล้อง | NOT_TESTED / NOT_TESTED |
| US-04 | :6 → :23 → :40 | PASS — 6 เซลล์เดิมและ FR/AC/วิธีตรวจสอดคล้อง | NOT_TESTED / NOT_TESTED |
| US-05 | :7 → :24 → :41 | PASS — 6 เซลล์เดิมและ FR/AC/วิธีตรวจสอดคล้อง | NOT_TESTED / NOT_TESTED |
| US-06 | :8 → :25 → :42 | PASS — 6 เซลล์เดิมและ FR/AC/วิธีตรวจสอดคล้อง | NOT_TESTED / NOT_TESTED |
| US-07 | :9 → :26 → :43 | PASS — 6 เซลล์เดิมและ FR/AC/วิธีตรวจสอดคล้อง | NOT_TESTED / NOT_TESTED |
| US-08 | :10 → :27 → :44 | PASS — 6 เซลล์เดิมและ FR/AC/วิธีตรวจสอดคล้อง | NOT_TESTED / NOT_TESTED |
| US-10 | :11 → :28 → :45 | PASS — 6 เซลล์เดิมและ FR/AC/วิธีตรวจสอดคล้อง | NOT_TESTED / NOT_TESTED |
| US-11 | :12 → :29 → :46 | PASS — 6 เซลล์เดิมและ FR/AC/วิธีตรวจสอดคล้อง | NOT_TESTED / NOT_TESTED |
| US-12 | :13 → :30 → :47 | PASS — 6 เซลล์เดิมและ FR/AC/วิธีตรวจสอดคล้อง | NOT_TESTED / NOT_TESTED |
| US-13 | :14 → :31 → :48 | PASS — 6 เซลล์เดิมและ FR/AC/วิธีตรวจสอดคล้อง | NOT_TESTED / NOT_TESTED |
| US-15 | :15 → :32 → :49 | PASS — 6 เซลล์เดิมและ FR/AC/วิธีตรวจสอดคล้อง | NOT_TESTED / NOT_TESTED |
| US-16 | :16 → :33 → :50 | PASS — 6 เซลล์เดิมและ FR/AC/วิธีตรวจสอดคล้อง | NOT_TESTED / NOT_TESTED |
| US-19 | :17 → :34 → :51 | PASS — 6 เซลล์เดิมและ FR/AC/วิธีตรวจสอดคล้อง | NOT_TESTED / NOT_TESTED |
| US-20 | :18 → :35 → :52 | PASS — 6 เซลล์เดิมและ FR/AC/วิธีตรวจสอดคล้อง | NOT_TESTED / NOT_TESTED |
| US-25 | :19 → :36 → :53 | PASS — 6 เซลล์เดิมและ FR/AC/วิธีตรวจสอดคล้อง | NOT_TESTED / NOT_TESTED |
| US-26 | :20 → :37 → :54 | PASS — 6 เซลล์เดิมและ FR/AC/วิธีตรวจสอดคล้อง | NOT_TESTED / NOT_TESTED |

PASS: NFR ทั้ง 15 แถว หมวด/US/locator ตรง B/fr-nfr.md:45–88 และ A:62–76; วิธีตรวจเป็นข้อเสนอ ไม่เป็น AC ใหม่. Q ครบ 18 รหัส/US/locator ตาม B/fr-nfr.md:130–147 และ A:84–101 ยัง OPEN/HUMAN_REQUIRED.
PASS: US-01/02/03/04 คงจุดวัด QR, table_id, ช่วงรับและความครบตัวเลือก/ยอดก่อนยืนยัน; ไม่ลดกฎความครบเป็นสัดส่วนชุดใบครัว (A:37–40).
PASS: US-05/07/11 คงชื่อสถานะคนละคำและจุดวัดเดิม; สูตรคิว × เฉลี่ยต่อออเดอร์ 7 วัน + เฉลี่ยต่อเมนูนานที่สุด, สองช่วงเร่งด่วน, server log, 1 วัน/10 นาที/80% คงครบ (A:41,43,46; B/fr-nfr.md:24,26,29,58).
PASS: US-08/15 คง 19/20 กับสองวิธีทุกออเดอร์แยกกัน, 10 นาทีและ 3/3, เหตุการณ์ยังไม่จ่าย/ค้างจ่าย/จ่ายแล้วกับ log ทุกครั้ง 20/20; ไม่รวมสถานะครัวหรือเงื่อนไขปิดโต๊ะ (A:44,49–50).
PASS: US-06/12/13/19/20 คงทั้งจาน/เฉพาะตัวเลือก, ป้ายและปุ่ม, ชุดเปิดคืน, ราคาออเดอร์เดิม, jpg/png ≤2 MB, 0–10 ตัวเลือก, รีเฟรช 1 นาทีและ 5/5; ไม่แก้ US-20 อ้าง US-14 หรือกู้เซลล์ US-12 (A:42,47–48,51–52).
PASS: US-10 คง 30/30, มือถือ 2 เครื่องพร้อมกัน, รันซ้ำ 3 รอบ ไม่สลับคู่; เลข monotonic แยก T-001/00:00 ของ US-15. US-16 คง session ใหม่และปฏิเสธรอบเดิม 5/5 (A:45,49–50).
PASS: US-25/26 คงชื่อผู้ใช้/PIN/ล็อก/URL 6/6; Ubuntu เครื่องเดียว/สคริปต์เดียว 30 นาที/งานออฟไลน์ครบ 20 ใบและข้อยกเว้นยืนยันยอดโอนด้วยตา (A:53–54).
BLOCKED เฉพาะการยืนยันกฎจริง: หมายเหตุ ก./ค./ช., Q ทุกข้อ, mapping เสร็จแล้ว/พร้อมเสิร์ฟ, PromptPay ปิดกับสองวิธี, วัตถุดิบซ้อน, US-14, สิทธิ์ Unknown และสภาพติดตั้ง; ไม่ขัด PASS ของการคงข้อค้างในเอกสาร.
NOT_TESTED: Flow mapping ใน A:111–136 ยังเป็น mapping ระดับ artifact จาก input-audit; ต้องทำ verify-flow ต่อ. UI/selector/data-testid/click/response/LAN/โหลด/ETA/security/log/Ubuntu/offline/ชำระเงินจริงไม่ได้รัน.
Downstream: ปลด verify-fr gate ให้ verify-flow และ draft-test-outline ตาม dependency เฉพาะ hash นี้; ยังไม่ปลด verify-test-outline/verify-ui/handoff. ไม่เปลี่ยน status planned ใน snapshot.
ข้อบกพร่อง FAIL: ไม่พบในขอบเขต verify-fr; ไม่ต้องแก้ artifact. หากภายหลังต้องเปลี่ยน scope/dependency/รุ่น output ส่ง Planner; จำกัดแก้ 2 รอบต่อปัญหาตามข้อตกลงการเรียน.

| หลักฐาน | SHA-256 |
|---|---|
| reference/session/plan-v1.json | `4bd023624fb2cb5c1ec9975528e8ffbcb6ac830cd40f9b61c5db28523ae25cfe` |
| reference/session/plan-v1.md | `10f2d1da058fafe1a6ed75047ad157ab0694cb7ee40ddd89c91874fa4d3310ae` |
| reference/session/evaluations/plan-v1-review.md | `f2facd03b3cd1f74969c110bfc336226b7d331f65042e51b036b5995166b3eb1` |
| reference/session/execution/fr-baseline-audit-v1.md | `78f8ce610526fdaa3e7911b3765fbff8246ea223d9772611e370bb42d5374175` |
| reference/session/execution/plan-v1/audit-fr-baseline-run/audit-fr-baseline.md | `42318bb248f2a2e4b675cbdd5104f2bc70ea401ebd4d83aa29076b65113c77b8` |
| B/us-initial.md | `56a439f6e22f4a8d17f552b023c3c8fe61556f5bd31f1f1e9b70c1f9da6049d2` |
| B/fr-nfr.md | `da31640e540b825d4fec555627ea098f092daf4243d5d304fd4c32ae6db734cd` |
| B/input-audit.md | `d4100680ed1f31ea3351144f202f85343fb47a23acfa0305116731ab8bb1bbd8` |
| B/provenance.md | `8059b1b47647d690ed7a73e6b4b9751e209edb3905868a4729269fb79330739a` |
| B/fr-check.json | `1b0c604da9288ce926ba4c98eb258107b130f309f85b1ee96403e02ba0d0f98c` |

สร้างจริง: reference/session/evaluations/fr-v1-check.md. Output hash บันทึกในรายงานหลักและ evaluator.md หลังเขียน; input hashes/check details รวมใน plan-v1/audit-fr-review-evidence.json เมื่อจบสองงาน.
