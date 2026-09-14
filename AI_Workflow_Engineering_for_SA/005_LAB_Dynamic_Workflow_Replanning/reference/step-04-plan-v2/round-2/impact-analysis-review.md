# ตรวจยืนยัน impact-analysis-v2 — รอบ 2

คำตัดสิน: **PASS เฉพาะการยืนยันผลวิเคราะห์ระดับแผน**; ไม่พบเหตุให้เปลี่ยนแผนหรือข้อสรุป impact เดิมจากพารามิเตอร์ที่แทนค่าครบ
S = `../../session`; B = `../../step-00-input/baseline-filtered-v2`; R = `../../step-03-reveal-1/reveal-1.md` (อ้างจากโฟลเดอร์ไฟล์นี้)
PREV_PLAN = S/plan-v1.json; CURRENT_PLAN = S/plan-v2.json; REVEAL_FILE = R; อ่าน Markdown คู่กันและหลักฐาน Evaluator เดิมตาม hash
ยืนยัน v1 → v2 ต่อเนื่อง; JSON #/version,#/trigger และ S/plan-v2.md:4–6 ระบุ reveal-1 พร้อม F-01 เดิม; ไม่มี placeholder ในพารามิเตอร์รอบนี้

## หลักฐานและ reuse/hash
SHA-256 S/plan-v1.json: `4bd023624fb2cb5c1ec9975528e8ffbcb6ac830cd40f9b61c5db28523ae25cfe`; .md: `10f2d1da058fafe1a6ed75047ad157ab0694cb7ee40ddd89c91874fa4d3310ae`
SHA-256 S/plan-v2.json: `8682dcba597fd36cadcf0a4724a9a75bd866f551b337281c663ee419c059c828`; .md: `75c5e9b06c7e26fbf7174295d165fbae64be57ea8ff807b4d96884898296ea2c`
SHA-256 R: `1fde792db1fdcf211be4a171fd88c61184ce892720832023fcaefad6a67f8917`; S/impact-analysis-v2.md: `b4b5dcfbe1d03d1e31d59758b2a9476cecf00b65b0226914ac29f199894ecfb3`
SHA-256 S/evaluations/plan-v2-review.md: `470d9248beca3760f63b1df7b54b5bcc24fc18cce5c1994ab3adebcf8403cd0e` ตรงตาราง output ใน ../evaluation/evaluator.md
SHA-256 S/evaluations/plan-v2/plan-v2-review-evidence.json: `66711881302f8d765012d237d9ffca437816b5e7ac6f25ec58c7cf90d72d1e8a` ตรงรายงาน Evaluator
คำนวณ input hashes ตรง 29/29 และ input-set hash ตรง evidence; reuse ใน JSON #/reuse ตรง 15/15; นี่คือการตรวจ bytes ไม่ใช่ทดสอบระบบ
ใช้ซ้ำตามรุ่น/hash ใน S/plan-v2.md:66–80: baseline-filtered-v2 ของ 18 US/AC, shell/role/reset/selector และ audit plan-v1 เป็นฐาน; ไม่โอนผล PASS ไปเป้าหมายใหม่
FR/Flow/state/structure/UI ส่วน upstream เปลี่ยนเป็น replace; contract/outline เป็น recheck (= needs_recheck ตาม P:63); เหตุคือ reveal-1/F-01 และยอด/สถานะ/เวลารอที่เชื่อมต่อ

## ผลกระทบโดยตรง
ตารางหลัก S/impact-analysis-v2.md:21–31 ครบ **11/11 แถว**: US-09/14/21/05/07/08/11/12/15/19/25; ทุกแถวมี task id และ locator ที่ผูก Hxx พร้อมแยกยืนยัน/อนุมาน/รอคำตอบ
R:12–14 ตรงสำเนา I:15–17 ทั้ง 3 แถวทุกคอลัมน์; เป็นข้อมูลจากต้นฉบับที่เพิ่งเปิด ไม่ใช่ข้อกำหนดร้านที่ผู้วิเคราะห์เพิ่ม
US-09/14 (I:21–22): FR/NFR เวลา → event/state รายการ → ข้อมูลรายการ/ยอด → ลูกค้า/ครัว/หน้าร้าน → งานตรวจ; คง 10 วินาทีบน LAN และผ่าน 5 จาก 5 กรณีของแต่ละ US
US-21 (I:23): FR → ช่วงเวลา/จำนวนยืนยัน/หน้าต่าง 15 นาทีเริ่ม 00/15/30/45 → ผู้จัดการ/ก่อนยืนยันลูกค้า → boundary/threshold; คง N=5 ผ่าน 3 จาก 3 รอบ; ไม่สรุปห้ามยืนยันเอง

## ผลกระทบต่อเนื่อง
US-05/07 (I:24–25; B/us-initial.md:7,9): mapping รายการ→ออเดอร์และข้อมูลคิว→ETA ต้องตรวจใหม่; คง AC เดิม; ไม่เทียบ “เสร็จแล้ว” กับ “พร้อมเสิร์ฟ” เอง
US-08/15/19 (I:26,29–30; B/us-initial.md:10,15,17): คืนรายการ→ยอดลูกค้า/หน้าร้าน→เหตุการณ์จ่ายและ log; คงราคาที่เก็บกับออเดอร์ ไม่คำนวณยอดเก่าจากราคา catalog และไม่ reset จ่ายแล้วเอง
US-12 (I:28; B/us-initial.md:13–14,18): availability เมนู/ตัวเลือกกับรายการรับเข้าคิวเป็นคนละเหตุการณ์; ตรวจ US-06/13/20 ต่อเนื่อง; ไม่ยกเลิกรายการในคิวจากการปิดขายเอง
US-11/F-01 (I:27; S/evaluations/flow-v1-check.md:35–40): แผนมี revise-flow เชื่อม FR-11/MRG-05 ถึง module/screen หน้าร้านและตรวจ coverage ทั้ง Flow/state/structure; คงเป็นข้อบกพร่องเดิมที่ต้องตรวจปิดตาม gate
US-25/รายงาน (I:31; B/ui-contract.md:113): ผลยอดคืนต่อการนับรายงานเป็นข้ออนุมานที่รอคำตอบ; ใช้ซ้ำสิทธิ์/placeholder และตรวจ regression; ไม่เพิ่ม AC หรือ producer รายงานจริง
JSON #/tasks และ P:13–39: คง 8 task id เดิม เพิ่ม revise-fr/revise-flow/revise-ui รวม 11 งาน; ตรวจ DAG ได้ลำดับ verify-plan → revise-fr → verify-fr → revise-flow → verify-flow → draft-test-outline → verify-test-outline → revise-ui → verify-ui → evaluate-handoff โดย revise-fr รอ audit-fr-baseline ด้วย
สถานะ audit done มี verify-fr v1 PASS รองรับ; Flow FAIL/outline BLOCKED ทำให้ needs_recheck; AI planned/done แยกจากสถานะรายการ/ออเดอร์/ชำระเงิน/โต๊ะ; ผลแผน PASS ไม่ปิด F-01 หรือรับรองชิ้นงาน

## คำถามรอคำตอบ
คง 8 กลุ่ม d-human-status/eta/payment/mapping/operations/environment/refund/capacity และ l-q-* ตาม P:51–58,92–99: หมายเหตุ ก./ค./ช., mapping, ช่อง US-12, US-20 อ้าง US-14, การปฏิบัติงานและสภาพทดสอบยังไม่ยืนยัน
ยอดรวมลดตามคืนยืนยันจาก US-09; ผู้อนุมัติ/วิธีคืนเงินจริง/ส่วนต่าง/คืนซ้ำ/วันนับรายงานยังค้าง; X ไม่ใช่ ETA ที่ยืนยัน และช่วง US-21 เช่น 11:30–13:30 ไม่แทน US-07 11:30–13:00 และ 17:30–19:30
งานรับรองกฎ/expected outcome จริงตลอด revise-fr ถึง evaluate-handoff ยัง BLOCKED ตามเรื่อง; หลังได้คำตอบให้ผูก source/hash แล้วตรวจ FR→Flow/state/data→UI→ยอดก่อน–หลัง/สถานะ/log/ขอบหน้าต่าง/N/X และ regression ใหม่

## ข้อจำกัด
ตรวจเอกสารและ hash เท่านั้น; ไม่ audit baseline ทุกเซลล์หรือรัน schema suite ของ Evaluator ซ้ำ; ไม่ทดสอบระบบ/browser/LAN/ETA/สัดส่วน AC/เงินจริง และไม่ประเมินชิ้นงานหรือผลตรวจที่ผลิตหลัง Evaluator แผนเดิม
ไม่อ่าน reveal-2/README/เว็บ ไม่เรียก agent หรือ CLI โมเดลเพิ่ม; ข้อความ “ยังไม่ผลิต v2/ไม่มี Evaluator v2” ใน impact เดิมเป็นสถานะ ณ เวลาเขียน ไม่แก้ย้อนหลังให้เป็นสถานะปัจจุบัน
ข้อสังเกต locator เล็กน้อย: I:21 ชี้ราคา snapshot ไป B/ui-contract.md:102; ข้อความ snapshot อยู่ :103 ใน hash H10 เดียวกัน (:102 เป็นราคา fixture); ไม่เปลี่ยนข้อสรุปหรือบังคับแก้ snapshot

## งานถัดไปและผลว่าต้องแก้หรือไม่
ไม่ต้องแก้แผนหรือ impact เดิมเพื่อแก้ความกำกวมของ template; บันทึก locator ที่แม่นยำไว้ใน review นี้แล้ว; ไม่พบแผนตกหล่นใหม่ที่ต้องส่ง Planner และคงงาน F-01/ข้อค้างธุรกิจตามเดิม
สร้างเฉพาะ `impact-analysis-review.md` นี้แบบ exclusive create; S/impact-analysis.md มี section v2 ตรง bytes กับฉบับแยกหลังหัวประวัติ 27 bytes และคงทุกไฟล์เดิม; ไม่มีการเพิ่ม section ซ้ำ
