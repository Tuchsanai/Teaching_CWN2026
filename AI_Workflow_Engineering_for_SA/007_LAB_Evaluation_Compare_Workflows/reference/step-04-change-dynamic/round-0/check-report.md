# ผลตรวจชิ้นงานและ UI ร่วม — Dynamic

วันที่ UTC 2026-09-14T15:29:47.218982+00:00
สถานะ: STOP_WITH_GAPS — มีผลผลิตจริงและเกณฑ์บางส่วนผ่าน แต่ยังมี regression ตกและเกณฑ์ที่ไม่ได้รัน

| รายการตรวจ | ผลจริง | หลักฐาน |
|---|---|---|
| Shared UI fixture | ผ่าน 18 / ตก 1 / skip 0 | tests.json |
| N−1/N ใน 3 รอบอิสระ | ผ่าน 6 / 6 fixture | tests.json: TS-US-21-101–106 |
| ชิ้นงานหลักที่เปลี่ยน | 4 ไฟล์จาก 4 | change-artifact-check.json |
| แถว FR/US ที่เปลี่ยน | US-21, FR-21 | change-artifact-check.json |
| แถว US/FR/NFR อื่นคงเดิม | True | เทียบทุกแถวรวม ID ที่ซ้ำใน traceability |
| ค่า default capacitySeed.limit=3 | True | ui-mockup-v3.html |

## ข้อที่ตก

- TS-US-09-101: Step 18: AssertionError: Locator expected to be visible Actual value: None Error: element(s) not found  Call log:   - Expect "to_be_visible" with timeout 2500ms   - waiting for get_by_test_id("payment-summary-total")  Aria snapshot: - link "ข้ามไปเนื้อหา":   - /url: "#main" - banner:   - text: ห้องทดลอง UI v3 • ข้อทดลอง N=3 • ข้อมูลจำลอง   - heading "ครัวคุณยาย" [level=1]   - text: จำลอง • ไม่มีการสั่งหรือโอนเงินจริง   - strong: นาฬิกาจำลอง   - text: 2026-01-01T12:00:00+07:00 เวลา +07:00 เดินเมื

## ขอบเขตและข้อค้าง

- ชุดร่วม 19 fixture ใช้ shared-tests-v2.json และ runner ของ LAB 006 เหมือนกันทุก action/ผลคาดหวัง; 13 regression เดิม + 6 threshold fixture
- ยังไม่รัน clock ที่ขอบ 00/15/30/45 ทั้งหมดหรือยืนยันใบถัดไปหลังคำเตือน; 6 fixture ผ่านไม่เท่ากับครบ AC US-21 ทั้งหมด
- ผลตัวนับ/ข้อความเป็น UI mock ไม่ใช่ผลเวลา server, LAN, security, load, availability หรือเงิน
- baseline scenario index ขาด action array และมี path สัญญาเดิมไม่พบ; รุ่นชุดตรวจแก้ setup หลังเริ่ม AI จาก DOM baseline โดยคงผลคาดหวัง; ไม่ใช่การควบคุม input อย่างสมบูรณ์
- เก็บผลเดิม LAB 006 ผ่าน 12 ตก 2 ไว้; ผลรันใหม่นี้ไม่ทับหรือเปลี่ยนข้อสรุปชุดเดิม
- ไม่มีการรันซ้ำหลังผลชุดร่วมตก; ไม่มีการแก้ UI เพื่อซ่อนข้อผิดพลาด
- ไม่ใช่การรับรองคุณภาพด้วยสายตาจาก screenshot; screenshot เป็นหลักฐานประกอบ runtime ที่ไฟล์มีอยู่จริง

tests.json/ui-mockup-v3.html อ้างจากโฟลเดอร์นี้; change-artifact-check.json/shared-tests-v2.json อ้างจาก reference/ ของ LAB 007
