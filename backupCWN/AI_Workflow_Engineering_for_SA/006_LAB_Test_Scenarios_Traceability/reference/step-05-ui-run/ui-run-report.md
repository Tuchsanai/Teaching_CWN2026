# รายงานตรวจผลรัน UI v2 — ขั้น 6.5

ผลจาก `ui-test-results.json`: **passed 12 / failed 2 / skipped 0 รวม 14 fixture** ตรงกับการนับสมาชิก `results` ด้วย TestID ไม่ใช้ตำแหน่งแถว ผลล้มเหลวทั้งสองรายการคงเป็น **UI_FAIL**; ไม่มีผลรันใหม่ในขั้นนี้ และไม่มีการรัน browser หรือเรียกผู้ช่วย/AI เพิ่ม

## แหล่งหลักฐานและการตรวจความสอดคล้อง

| Input | ใช้ตรวจ |
|---|---|
| [ui-test-results.json](ui-test-results.json) | ผลจริง สถานะ เหตุผล และ screenshot ต่อ TestID |
| [../../input/ui-scenarios.json](../../input/ui-scenarios.json) | ชื่อ/US/steps ของ 14 fixture; เป็นสัญญาการทดสอบ ไม่ใช่ผลรัน |
| [../step-03-merge/traceability.csv](../step-03-merge/traceability.csv) | header, mapping และ Status ก่อนรัน |
| [../step-03-merge/test-scenarios.md](../step-03-merge/test-scenarios.md) | 114 scenario เชิงออกแบบ, automation, precondition และข้อจำกัด fixture |
| [../step-04-nfr-split/nfr-split.md](../step-04-nfr-split/nfr-split.md) | ขอบเขต functional/ระบบจริง, NFR และ US/AC ต้นฉบับ |
| [../step-00-input/provenance.md](../step-00-input/provenance.md) | ที่มา snapshot อ้างอิง LAB 005 และฐาน path |
| [../step-00-input/input-check.md](../step-00-input/input-check.md) | ข้อค้นพบ selector/setup/fixture mismatch แบบ static |
| [runner/log.jsonl](runner/log.jsonl) | ผลดิบก่อน normalize, ยอด stdout, เวลาและ exit code |

Path ใน manifest และค่า `html`/`screenshot` ของผลรันอ้างจากราก LAB `../..`; ลิงก์ในรายงานนี้อ้างจากโฟลเดอร์รายงาน ตาม provenance ข้อมูลต้นทางเป็นผลอ้างอิง LAB 005 ไม่ใช่ผลของนักศึกษา และไม่ใช้ผลตรวจต้นทางแทนผลรันครั้งนี้

บันทึก runner เริ่ม `2026-09-14T15:08:37.463423+00:00` จบ `2026-09-14T15:08:50.762850+00:00` ใช้เวลา `13.299 s`; `browser=launch`, `launch_fallback_reason=null`, `scope=offline mock UI`. ระยะเวลารวมของ runner ไม่ใช่เวลา LAN หรือเวลาแต่ละ AC; ไม่มีข้อมูล version ของ browser/viewport หรือผลจับเวลาราย AC ใน JSON

ตรวจ `runner.report.raw_json` กับ JSON แล้วต่างกันเฉพาะ top-level `html` ซึ่ง normalize เป็น `reference/step-00-input/ui-mockup-v2.html` และชี้ snapshot เดียวกัน; `results` ทั้งชุด รวมสถานะ เหตุผล และ screenshot ตลอดจนยอดรวมและ metadata อื่นตรงกัน ไม่คัด path เครื่องจากผลดิบลงรายงาน `runner.stdout` ยืนยันยอด 12/2/0; stderr ว่าง และ `exit_code=0` มาพร้อม `--allow-fail` จึงไม่แปลว่า fixture ผ่านทั้งหมด

พบ 14 TestID ไม่ซ้ำใน fixture และ 14 TestID ไม่ซ้ำใน results; ชุด ID ตรงกันครบ ไม่มีผลเกินหรือ fixture ขาดผล; US ของแต่ละ ID ตรงกับ fixture และทุกแถวที่เกี่ยวข้องใน traceability ตรวจพบไฟล์ screenshot ที่ JSON ระบุครบ 14/14 ไฟล์ โดยตรวจการมีอยู่เท่านั้น **ไม่ได้เปิดดูภาพ**

## ผลทุก fixture scenario

`UI_PASS` หมายถึง assertions ที่ runner รายงานผ่านใน Mock-up เท่านั้น ไม่ใช่ PASS ของ US/AC เต็มหรือ NFR ระบบจริง คอลัมน์เหตุผลคัดข้อความ JSON; กรณี F01 แสดงส่วน error/call log ในตารางและเก็บ reason เต็มตาม JSON ในภาคผนวก ลำดับชื่อไฟล์ภาพไม่ใช้จับคู่ผล

| TestID / US | Fixture scenario ตาม input | ผล JSON → Status | เหตุผลตาม JSON | ภาพที่มีจริง |
|---|---|---|---|---|
| TS-US-01-101 / US-01 | เปิดเมนูโดยไม่ล็อกอิน; ไม่วัด QR/Wi-Fi | pass → UI_PASS | All assertions observed; mock UI only | [shots/000-TS-US-01-101.png](shots/000-TS-US-01-101.png) |
| TS-US-02-101 / US-02 | ผูกโต๊ะ 02 ใน UI จำลอง | pass → UI_PASS | All assertions observed; mock UI only | [shots/001-TS-US-02-101.png](shots/001-TS-US-02-101.png) |
| TS-US-03-101 / US-03 | กลับบ้านและช่วงรับจำลอง | pass → UI_PASS | All assertions observed; mock UI only | [shots/002-TS-US-03-101.png](shots/002-TS-US-03-101.png) |
| TS-US-04-101 / US-04 | ตัวเลือกไข่รวมราคาและส่งใบครัว | pass → UI_PASS | All assertions observed; mock UI only | [shots/003-TS-US-04-101.png](shots/003-TS-US-04-101.png) |
| TS-US-05-101 / US-05 | ลูกค้าเห็นสถานะใหม่ในแท็บเดียว | pass → UI_PASS | All assertions observed; mock UI only | [shots/004-TS-US-05-101.png](shots/004-TS-US-05-101.png) |
| TS-US-06-101 / US-06 | ตะกร้าเก่าถูกปฏิเสธหลัง chicken หมด | pass → UI_PASS | All assertions observed; mock UI only | [shots/005-TS-US-06-101.png](shots/005-TS-US-06-101.png) |
| TS-US-08-101 / US-08 | PromptPay ค้างยืนยันและ fallback 10 นาทีจำลอง | pass → UI_PASS | All assertions observed; mock UI only | [shots/006-TS-US-08-101.png](shots/006-TS-US-08-101.png) |
| TS-US-08-102 / US-08 | เงินสดต้องให้หน้าร้านยืนยัน | pass → UI_PASS | All assertions observed; mock UI only | [shots/007-TS-US-08-102.png](shots/007-TS-US-08-102.png) |
| TS-US-09-101 / US-09 | แจ้งทำไม่ได้และลูกค้าคืนรายการ; ไม่ใช่คืนเงินจริง | fail → UI_FAIL | Step 18: AssertionError: Locator expected to be visible<br>Actual value: None<br>Error: element(s) not found <br>Call log:<br>  - Expect "to_be_visible" with timeout 2500ms<br>  - waiting for get_by_test_id("payment-summary-total") | [shots/008-TS-US-09-101.png](shots/008-TS-US-09-101.png) |
| TS-US-11-101 / US-11 | ครัวหนึ่งแตะเปลี่ยนสถานะถึงหน้าร้าน | pass → UI_PASS | All assertions observed; mock UI only | [shots/009-TS-US-11-101.png](shots/009-TS-US-11-101.png) |
| TS-US-12-101 / US-12 | egg หมดปิดเฉพาะตัวเลือก m01 ยังสั่งได้ | pass → UI_PASS | All assertions observed; mock UI only | [shots/010-TS-US-12-101.png](shots/010-TS-US-12-101.png) |
| TS-US-14-101 / US-14 | ทำไม่ได้ย้ายรายการไปรอลูกค้าตัดสินใจ | pass → UI_PASS | All assertions observed; mock UI only | [shots/011-TS-US-14-101.png](shots/011-TS-US-14-101.png) |
| TS-US-21-101 / US-21 | N=5 แสดงครัวเต็มก่อนยืนยันใบถัดไป | fail → UI_FAIL | Step 6: TimeoutError: Locator.evaluate: Timeout 2500ms exceeded.<br>Call log:<br>  - waiting for get_by_test_id("rush-start") | [shots/012-TS-US-21-101.png](shots/012-TS-US-21-101.png) |
| TS-US-25-101 / US-25 | PIN ผิดปฏิเสธเข้า manager | pass → UI_PASS | All assertions observed; mock UI only | [shots/013-TS-US-25-101.png](shots/013-TS-US-25-101.png) |

รอบนี้ `screenshot=null` จำนวน 0 รายการ; หากเป็น null ต้องรายงาน “ไม่มีภาพ” พร้อม reason ตาม JSON ไม่สร้าง path ทดแทน ไฟล์ภาพที่มีอยู่ยังไม่มีผล visual review: ผู้ตรวจ/เวลาที่เปิดตรวจ/ความถูกต้องของ layout/ความสวยงาม **ไม่มีข้อมูล** ต้องให้ผู้ตรวจเปิดภาพจริงและบันทึกผลแยกในรุ่นใหม่ ไม่อนุมานจากชื่อไฟล์ ภาพ หรือข้อความ Aria ที่ยังไม่ได้ตรวจด้วยสายตา

## แยกประเภทความล้มเหลวและ skip

| ประเภท | จำนวน / TestID | ข้อวินิจฉัยตามหลักฐาน |
|---|---|---|
| Assertion failure | 1 — TS-US-09-101 | Step 18: expect_text ที่ payment-summary-total คาด 0 บาท แต่ AssertionError ระบุไม่พบ element ขณะรอ visibility ภายใน 2500ms; ไม่ใช่หลักฐานว่าได้ยอดผิดเป็นตัวเลขอื่น |
| Setup/infrastructure | setup 1 — TS-US-21-101; infrastructure 0 ที่พบในผล | Step 6: fill rush-start ล้มเหลวด้วย Locator.evaluate timeout 2500ms ก่อนตั้งค่าความจุ/สร้างชุดออเดอร์; เป็น setup ของ fixture ไม่ใช่หลักฐาน browser launch หรือเครือข่ายล่ม |
| Fixture mismatch | 2 — F01/TS-US-09-101 และ F02/TS-US-21-101 | input-check ระบุ payment-summary-total, rush-start, rush-end ไม่ตรงชื่อใน snapshot และ fixture ความจุขาด nav-capacity; เป็นการจำแนกสาเหตุของสอง failure ข้างต้น ไม่บวกเป็น failure อีกสองรายการ |
| Skip | 0 | ไม่มี status=skip ใน results; manual/mock-not-testable/ไม่มีผลจริงไม่ถูกเปลี่ยนเป็น SKIP และไม่ย้าย failure ไปเป็น skip |

## รายการข้อบกพร่องและคำแนะนำตรวจซ้ำรุ่นใหม่

### F01 — TS-US-09-101: selector ของยอดหลังคืนไม่ตรง fixture

ผลจริง **fail / UI_FAIL** ที่ Step 18 ซึ่งเป็นขั้นสุดท้ายของ fixture: `expect_text(payment-summary-total, "0 บาท")` ล้มเหลวเพราะไม่พบ element ตาม reason. `input-check.md` ระบุว่าไม่พบชื่อนี้ และพบ `customer-adjusted-total` ซึ่งเป็นยอดออเดอร์ล่าสุดของ session ไม่ใช่ยอดรวมหลายออเดอร์ทั้ง session; ยังมี `resolution-order-total` ใน `customer-resolution-order[data-order-id]` ที่มี scope ระดับออเดอร์

Aria snapshot ใน reason บันทึกข้อความคืนรายการและยอด 0 บาทหลังคืนจานเดิม 50 บาทไว้ แต่เป็นข้อความประกอบ error ไม่ใช่การเปิดตรวจ screenshot และไม่ทำให้ assertion ที่ล้มเหลวกลับเป็น pass. ผล runtime ของ selector ทดแทนยังไม่มีข้อมูล และยังไม่ยืนยันการคืนเงินจริง

ข้อเสนอสำหรับผู้ดูแล fixture ในรุ่นใหม่: กำหนดขอบเขตยอดที่จะตรวจให้ชัดตามหนึ่งออเดอร์/หนึ่งจานของ fixture แล้วใช้ mapping ที่ input-check พบจริงพร้อม scope order/item; ไม่ใช้ cart-total หรือ snapshot front-total แทนยอดหลังคืน ตรวจการแสดงรายการก่อนคืน การคืนเฉพาะรายการ และยอดคาด 0 บาทจาก m01=50 บาทของชุดจำลอง โดยคงคำถามยอดหลายออเดอร์ ราคา/ส่วนต่าง และนโยบายเงินจริงเป็น BLOCKED จนมีข้อมูล ทำผลรันใหม่พร้อม reason/ภาพ และเก็บ fail ครั้งนี้ไว้อ้างเทียบ

### F02 — TS-US-21-101: ตั้งค่าความจุไม่ได้ก่อนถึง assertion

ผลจริง **fail / UI_FAIL** ที่ Step 6: `fill(rush-start, "11:30")`; reason เป็น `TimeoutError: Locator.evaluate: Timeout 2500ms exceeded.` ขณะรอ `rush-start`. input-check ระบุชื่อจริง `capacity-start` และ `capacity-end` แทน `rush-start`/`rush-end` และต้องเข้าหน้าความจุผ่าน `nav-capacity` หลัง login ผู้จัดการ ซึ่งไม่มีใน steps ของ fixture นี้

ยังไม่ถึง Step 7–31 รวมการตั้ง `capacity-limit=5`, บันทึกค่า, ยืนยัน 5 ออเดอร์ และ assertions ที่ `capacity-message` ของใบถัดไป จึงไม่มีหลักฐานว่าระบบเตือนความจุทำงานผิดหรือผ่าน; rush-end เป็น mismatch ที่ทราบจาก static check ไม่ใช่ timeout ครั้งที่สองที่รันพบแล้ว

ข้อเสนอสำหรับผู้ดูแล fixture ในรุ่นใหม่: เพิ่มทางเข้าหน้าที่พบจริงและปรับชื่อ input ตาม mapping ที่ตรวจแล้ว ตั้งช่วง 11:30–13:30 และ N=5 อย่างชัดเจน ส่ง 5 ออเดอร์ในหน้าต่าง 15 นาทีเดียวกัน แล้วเตรียมใบที่ 6 เพื่อยืนยันว่าข้อความ “ครัวเต็ม”/“รอประมาณ” เกิดก่อนยืนยัน ไม่เพิ่ม expected ว่าต้องห้ามส่งใบที่ 6 เก็บครบ 3 จาก 3 รอบตาม US-21 เมื่อตรวจ AC; รอบ smoke เดียวไม่แทนสามรอบ คง X=10 นาที/เขตเวลา +07:00/ขอบหน้าต่างจาก seed เป็นสมมติฐาน fixture; ไม่ยืมเป็นสูตร ETA ของ US-07 และไม่ถือเป็น Load test

### ขอบเขต assertion และข้อค้างที่ยังเปิด

ตารางต่อไปคงข้อความขอบเขตจากส่วน “เชื่อม fixture สงวน 14 ID / 13 US” ใน test-scenarios.md ตรงตัว เป็นข้อจำกัดของการออกแบบเดิม ไม่ใช่ผลรันที่เพิ่มขึ้น; F01/F02 ที่ต้นทางระบุ BLOCKED มีผลรัน fail จริงแล้วในรอบนี้ และยังต้องแก้ความเข้ากันได้ในรุ่นใหม่

| Fixture TestID | ขอบเขต/ข้อค้างเดิม |
|---|---|
| TS-US-01-101 | เพียง menu-list; ไม่ assert รายการแรก/QR/3 วินาที/20 ครั้ง |
| TS-US-02-101 | ข้อความ 02 ใน front-orders ใบเดียว; ไม่ตรวจ URL/20 โต๊ะ/การผูกอัตโนมัติ |
| TS-US-03-101 | กลับบ้านใบเดียวและ 12:30; ไม่ครบช่วงจบ/ทุก slot/ขอบ 20 นาที/10 ใบ |
| TS-US-04-101 | item-total มี 60 และใบครัวมีไข่; ไม่ครบ configuration/ยอดตะกร้า/20 ใบ |
| TS-US-05-101 | กำลังทำในแท็บเดียวหลังสลับบทบาท; ไม่พิสูจน์จอเปิดค้าง/ไม่รีเฟรช/5 วินาที LAN/20 ครั้ง |
| TS-US-06-101 | order-message มีหมด; ยังขาดป้ายพร้อม disabled/no-new-order/10 ครั้ง LAN |
| TS-US-08-101 | +10 นาทีแล้วมีข้อความเงินสด; ไม่ใช่เกิน 10 นาที/ไม่มีปลายทางยืนยัน/ไม่ครบสามกรณี |
| TS-US-08-102 | เงินสดยังไม่จ่ายจนหน้าร้านรับเงิน; เชื่อมวิธีเงินสด US-08 และยืนยันสถานะ US-15 ข้ามบทบาท; ไม่ครบ 20 ใบ/เงินจริง |
| TS-US-09-101 | F01: BLOCKED — payment-summary-total MISSING; ไม่ตรวจเปลี่ยนเมนู/LAN/5 กรณี |
| TS-US-11-101 | หนึ่งใบ/หนึ่งแตะแล้ว front-orders มีกำลังทำ; ไม่ตรวจเสร็จแล้ว/5 วินาที/18 จาก 20 |
| TS-US-12-101 | ปิด egg แล้วส่ง m01 ได้; ไม่มี assertion extra-egg disabled/วัตถุดิบ 5 ชนิด |
| TS-US-14-101 | ตรวจเพียงรอลูกค้าตัดสินใจ; ยังไม่ตรวจผลเปลี่ยน/คืน/10 วินาที LAN/5 กรณี |
| TS-US-21-101 | F02: BLOCKED — rush-start/rush-end MISSING และขาด nav-capacity; หนึ่งรอบไม่แทน 3 จาก 3 |
| TS-US-25-101 | PIN ผิดหนึ่งครั้ง; ไม่แทน 5 ครั้ง/5 นาที/3 บัญชี × 2 หน้า/ความปลอดภัยฝั่ง server |

ก่อนตรวจซ้ำให้จัด fixture/contract และ Output เป็นรุ่นใหม่ คง snapshot/ผลเก่าและ TestID สำหรับการเปรียบเทียบ ระบุสิ่งที่แก้จริงในรุ่นใหม่ รันซ้ำทั้งสอง failure และ regression ของ fixture ที่เกี่ยวข้องเมื่อได้รับงานรันในขั้นถัดไป เก็บ failures/skips ตามที่เกิดจริง ห้ามเปลี่ยนผลเก่านี้เพื่อให้ยอดผ่านเพิ่ม ขั้นนี้ไม่ได้แก้ selector, fixture, HTML, input หรือรันตรวจซ้ำ

## รายการ scenario ที่ mock-up ทดสอบไม่ได้

รายการด้านล่างเป็น **63 TestID เชิงออกแบบ แยกจาก 14 fixture**: mock-not-testable 57 และ manual 6 ตาม test-scenarios.md จับคู่กับสถานะใน traceability.csv. ทั้งหมดไม่มีผลจริงใน JSON จึงไม่ใช่ skipped ของ runner และคง Status เดิม; manual หมายถึงต้องมีผู้ตรวจคนเพิ่มเพื่อยืนยัน ไม่ได้หมายความว่าหน้าจอ mock ทุกส่วนใช้งานไม่ได้ ส่วน precondition อ้างอักษรย่อและชุดข้อมูลตามบล็อกต้นทางที่ลิงก์ไว้

### mock-not-testable — 57 รายการ

| TestID | Scenario เดิม | Automation / Status คงเดิม | เหตุผล/เงื่อนไขที่ยังต้องมีตามต้นทาง |
|---|---|---|---|
| [TS-US-01-2](../step-03-merge/test-scenarios.md#design-ts-us-01-2) | สแกน QR จริงและวัดการแสดงรายการแรก 20 ครั้ง | mock-not-testable / MOCK_NOT_TESTABLE | mock-not-testable: UI/ข้อมูลหรือระบบจริงที่จำเป็นยังไม่มีตาม precondition; ไม่ใช้การอ่าน source หรือคลิก mock แทน AC ระบบจริง; Precondition/reset: BLOCKED: ไม่มีระบบจริง/QR เชื่อมระบบ/มือถือบน Wi‑Fi ร้าน; ต้องกำหนดสภาพทดสอบตาม Q-01 ก่อนรัน |
| [TS-US-01-3](../step-03-merge/test-scenarios.md#design-ts-us-01-3) | QR อ่านไม่ได้หรือปลายทางเมนูเปิดไม่ได้ | mock-not-testable / MOCK_NOT_TESTABLE | mock-not-testable: UI/ข้อมูลหรือระบบจริงที่จำเป็นยังไม่มีตาม precondition; ไม่ใช้การอ่าน source หรือคลิก mock แทน AC ระบบจริง; Precondition/reset: BLOCKED: ต้องมี QR/ระบบจริงและคำตอบเกี่ยวกับ fallback; แยกจากชุดปกติ 20 ครั้ง |
| [TS-US-02-2](../step-03-merge/test-scenarios.md#design-ts-us-02-2) | QR URL และป้ายโต๊ะตรงกันในชุด 20 โต๊ะ | mock-not-testable / MOCK_NOT_TESTABLE | mock-not-testable: UI/ข้อมูลหรือระบบจริงที่จำเป็นยังไม่มีตาม precondition; ไม่ใช้การอ่าน source หรือคลิก mock แทน AC ระบบจริง; Precondition/reset: BLOCKED: ไม่มี QR route/backend และ 20 โต๊ะใน mock; เตรียมป้ายจำลอง 20 โต๊ะบนระบบทดสอบจริง |
| [TS-US-02-3](../step-03-merge/test-scenarios.md#design-ts-us-02-3) | table_id หาย ไม่มีอยู่ หรือถูกเปลี่ยน | mock-not-testable / MOCK_NOT_TESTABLE | mock-not-testable: UI/ข้อมูลหรือระบบจริงที่จำเป็นยังไม่มีตาม precondition; ไม่ใช้การอ่าน source หรือคลิก mock แทน AC ระบบจริง; Precondition/reset: BLOCKED: รอ Q-02 และ route ระบบจริง; ไม่ดัดแปลง HTML หรือ input |
| [TS-US-03-3](../step-03-merge/test-scenarios.md#design-ts-us-03-3) | เลือกช่วงรับแล้วค้างหน้าจอจนต่ำกว่าขั้นต่ำ | mock-not-testable / MOCK_NOT_TESTABLE | mock-not-testable: UI/ข้อมูลหรือระบบจริงที่จำเป็นยังไม่มีตาม precondition; ไม่ใช้การอ่าน source หรือคลิก mock แทน AC ระบบจริง; Precondition/reset: BLOCKED: รอ Q-03 นิยามเวลาสั่ง/การเลื่อนช่วงอัตโนมัติ และระบบจริง; mock render อาจเลือกช่วงใหม่เองจึงไม่แทนคำสั่งเก่าจริง |
| [TS-US-04-3](../step-03-merge/test-scenarios.md#design-ts-us-04-3) | ตัวเลือกขัดกันหรือไม่ได้เลือกตัวที่อาจบังคับ | mock-not-testable / MOCK_NOT_TESTABLE | mock-not-testable: UI/ข้อมูลหรือระบบจริงที่จำเป็นยังไม่มีตาม precondition; ไม่ใช้การอ่าน source หรือคลิก mock แทน AC ระบบจริง; Precondition/reset: BLOCKED: รอ Q-04 และ configuration ที่ระบุว่าใดบังคับ/ขัดกัน; mock ไม่มีสัญญารองรับกฎนี้ |
| [TS-US-04-4](../step-03-merge/test-scenarios.md#design-ts-us-04-4) | จับตัวเลือกผิดจานและราคาเพิ่มตกหล่นด้วย fixture สองจาน | mock-not-testable / MOCK_NOT_TESTABLE | แก้ D01 เชิงออกแบบ; ต้องมีระบบ/จุดแทรก fault และจุดสังเกตตาม Precondition ซึ่งยังไม่มี จึง BLOCKED การรัน. เป็นแผนตรวจจับผลผิดด้วย oracle อิสระ ไม่ใช่การเปลี่ยนชื่อ happy path; ยังไม่ได้ทำ fault หรือรันทดสอบ; Precondition/reset: BLOCKED การรัน: ต้องมีระบบทดสอบและตัวแทรกข้อมูลทดสอบที่จุดสร้างยอด/ข้อมูลใบครัว ซึ่ง Input ยังไม่มี; ผู้จัดระบบต้องเปิดให้ตรวจข้อมูลก่อนและหลังแทรกได้ แยกแต่ละกรณีและคืน snapshot เดิมทุกครั้ง |
| [TS-US-05-2](../step-03-merge/test-scenarios.md#design-ts-us-05-2) | หน้าลูกค้าเปิดค้างรับสถานะบน LAN 20 ครั้ง | mock-not-testable / MOCK_NOT_TESTABLE | mock-not-testable: UI/ข้อมูลหรือระบบจริงที่จำเป็นยังไม่มีตาม precondition; ไม่ใช้การอ่าน source หรือคลิก mock แทน AC ระบบจริง; Precondition/reset: BLOCKED: ต้องมีระบบจริงและอุปกรณ์ครัว/ลูกค้าแยกกันบน LAN ร้าน พร้อมหลักฐานเวลาสองปลายทาง |
| [TS-US-05-3](../step-03-merge/test-scenarios.md#design-ts-us-05-3) | เครือข่ายขาดขณะครัวเปลี่ยนสถานะ | mock-not-testable / MOCK_NOT_TESTABLE | mock-not-testable: UI/ข้อมูลหรือระบบจริงที่จำเป็นยังไม่มีตาม precondition; ไม่ใช้การอ่าน source หรือคลิก mock แทน AC ระบบจริง; Precondition/reset: BLOCKED: รอข้อตกลง recovery และระบบจริงหลายอุปกรณ์; แยกชุด fault injection ออกจาก LAN ปกติ 20 ครั้ง |
| [TS-US-05-4](../step-03-merge/test-scenarios.md#design-ts-us-05-4) | ตรวจสถานะค้างเมื่อระบบส่งอัปเดตช้าเกิน 5 วินาทีบน LAN | mock-not-testable / MOCK_NOT_TESTABLE | แก้ D02 เชิงออกแบบ; ต้องมีระบบ/จุดแทรก fault และจุดสังเกตตาม Precondition ซึ่งยังไม่มี จึง BLOCKED การรัน. เป็นแผนตรวจจับผลผิดด้วย oracle อิสระ ไม่ใช่การเปลี่ยนชื่อ happy path; ยังไม่ได้ทำ fault หรือรันทดสอบ; Precondition/reset: BLOCKED การรัน: ต้องมีระบบหลายอุปกรณ์บน LAN ร้านและตัวหน่วงที่ส่วนส่งสถานะของระบบ ไม่ตัดเครือข่าย; ต้องมีการบันทึกภาพครัว/ลูกค้าและนาฬิกาอ้างอิงเดียวกัน พร้อมตรวจว่าตัวหน่วงรับเหตุการณ์ ID ที่ต้องการจริง |
| [TS-US-06-3](../step-03-merge/test-scenarios.md#design-ts-us-06-3) | เผยแพร่หมดบน LAN และปฏิเสธคำสั่งจริง | mock-not-testable / MOCK_NOT_TESTABLE | mock-not-testable: UI/ข้อมูลหรือระบบจริงที่จำเป็นยังไม่มีตาม precondition; ไม่ใช้การอ่าน source หรือคลิก mock แทน AC ระบบจริง; Precondition/reset: BLOCKED: ต้องมีระบบจริงสองอุปกรณ์บน LAN และวิธีส่งคำสั่งทดสอบที่ยืนยันว่าเกิดหลังปิดแล้ว |
| [TS-US-07-1](../step-03-merge/test-scenarios.md#design-ts-us-07-1) | สูตรเวลารอก่อนยืนยันทุกออเดอร์ | mock-not-testable / MOCK_NOT_TESTABLE | mock-not-testable: UI/ข้อมูลหรือระบบจริงที่จำเป็นยังไม่มีตาม precondition; ไม่ใช้การอ่าน source หรือคลิก mock แทน AC ระบบจริง; Precondition/reset: BLOCKED: UI v2 มีเพียง ยังประมาณไม่ได้ ไม่มี ETA selector/ข้อมูล 7 วัน/ตัวคำนวณ; ต้องมีระบบรองรับและนิยามค่าเฉลี่ยตาม Q-07 |
| [TS-US-07-2](../step-03-merge/test-scenarios.md#design-ts-us-07-2) | ความแม่นยำช่วงเร่งด่วนครบหนึ่งวันจาก log เซิร์ฟเวอร์ | mock-not-testable / MOCK_NOT_TESTABLE | mock-not-testable: UI/ข้อมูลหรือระบบจริงที่จำเป็นยังไม่มีตาม precondition; ไม่ใช้การอ่าน source หรือคลิก mock แทน AC ระบบจริง; Precondition/reset: BLOCKED: ไม่มี server log/ระบบ ETA/ข้อมูล 7 วัน; ต้องตอบ Q-05/Q-07 เรื่องพร้อมเสิร์ฟ ประชากร และขอบช่วงก่อนรับรอง |
| [TS-US-07-3](../step-03-merge/test-scenarios.md#design-ts-us-07-3) | ไม่มีประวัติ 7 วันหรือไม่มีค่าเฉลี่ยของเมนู | mock-not-testable / MOCK_NOT_TESTABLE | mock-not-testable: UI/ข้อมูลหรือระบบจริงที่จำเป็นยังไม่มีตาม precondition; ไม่ใช้การอ่าน source หรือคลิก mock แทน AC ระบบจริง; Precondition/reset: BLOCKED: ต้องตอบ Q-07 และมีระบบ ETA; ไม่เติมค่าจำลองลง input เดิม |
| [TS-US-07-4](../step-03-merge/test-scenarios.md#design-ts-us-07-4) | จับ ETA ที่นับใบพร้อมเสิร์ฟรวมในคิวจากประวัติครบ 7 วัน | mock-not-testable / MOCK_NOT_TESTABLE | แก้ D03 เชิงออกแบบ; ต้องมีระบบ/จุดแทรก fault และจุดสังเกตตาม Precondition ซึ่งยังไม่มี จึง BLOCKED การรัน. เป็นแผนตรวจจับผลผิดด้วย oracle อิสระ ไม่ใช่การเปลี่ยนชื่อ happy path; ยังไม่ได้ทำ fault หรือรันทดสอบ; Precondition/reset: BLOCKED การรัน: ไม่มี ETA/ประวัติ/ตัวคำนวณหรือจุดแทรกค่าคิวใน Input; ต้องเตรียมระบบทดสอบที่อ่าน snapshot ปัจจัยและแทรกค่าจำนวนคิวก่อนคำนวณได้. ระบบทดสอบใช้วิธีเฉลี่ย fixture ที่เปิดเผยด้านล่าง ไม่มีข้อมูลขาด |
| [TS-US-08-5](../step-03-merge/test-scenarios.md#design-ts-us-08-5) | ตรวจชุดชำระสามกรณีและเวลา timeout บนระบบจริง | mock-not-testable / MOCK_NOT_TESTABLE | mock-not-testable: UI/ข้อมูลหรือระบบจริงที่จำเป็นยังไม่มีตาม precondition; ไม่ใช้การอ่าน source หรือคลิก mock แทน AC ระบบจริง; Precondition/reset: BLOCKED: ต้องมีระบบจริงในสภาพทดสอบที่ใช้ข้อมูล/สลิปจำลอง ไม่โอนเงินจริง และคำตอบ Q-08; ไม่มี service/timer จริงใน HTML |
| [TS-US-09-6](../step-03-merge/test-scenarios.md#design-ts-us-09-6) | แจ้งรายการทำไม่ได้บน LAN ครบห้ากรณี | mock-not-testable / MOCK_NOT_TESTABLE | mock-not-testable: UI/ข้อมูลหรือระบบจริงที่จำเป็นยังไม่มีตาม precondition; ไม่ใช้การอ่าน source หรือคลิก mock แทน AC ระบบจริง; Precondition/reset: BLOCKED: ต้องมีลูกค้า/ครัวแยกอุปกรณ์บน LAN ระบบจริงและนโยบาย Q-V2-REFUND/STATE; ไม่ทำการโอนหรือคืนเงินจริง |
| [TS-US-10-3](../step-03-merge/test-scenarios.md#design-ts-us-10-3) | เวลายืนยันสั่งถึงจอครัวบน LAN | mock-not-testable / MOCK_NOT_TESTABLE | จำเป็นต้องมีเครือข่ายและอุปกรณ์จริง; นาฬิกาจำลองไม่เป็นหลักฐาน SLA; Precondition/reset: ระบบจริงสำหรับทดสอบบน LAN ร้านพร้อมมือถือและจอครัว; ขณะนี้ไม่มีระบบและ log |
| [TS-US-10-4](../step-03-merge/test-scenarios.md#design-ts-us-10-4) | รับคำสั่งจากสองมือถือพร้อมกันโดยไม่สลับคู่ | mock-not-testable / MOCK_NOT_TESTABLE | ต้องมีการรับคำสั่งพร้อมกันจริงและ log เซิร์ฟเวอร์; sequential mock ไม่พิสูจน์ concurrency; Precondition/reset: ระบบทดสอบจริงบน LAN; มือถือ 2 เครื่องและจอครัว; เปิดรอบทดสอบที่แยกหลักฐานได้ |
| [TS-US-10-5](../step-03-merge/test-scenarios.md#design-ts-us-10-5) | ส่งซ้ำหรือเริ่มระบบใหม่ระหว่างออกเลข | mock-not-testable / MOCK_NOT_TESTABLE | ต้องมีระบบจริงและคำตอบธุรกิจ; ไม่ใช้ btn-reset เป็นการรีสตาร์ต server; Precondition/reset: สภาพทดสอบแยกจากข้อมูลจริง; ต้องมีระบบและนโยบาย Q-10 ก่อนรัน |
| [TS-US-11-3](../step-03-merge/test-scenarios.md#design-ts-us-11-3) | กดสถานะซ้ำหลังเสร็จแล้วหรือขอย้อนสถานะ | mock-not-testable / MOCK_NOT_TESTABLE | ปุ่มที่ปิดใน mock ไม่พิสูจน์การจัดการคำสั่งซ้ำของระบบจริง; Precondition/reset: ต้องมี transition ที่ยืนยันและระบบทดสอบ; เตรียมใบเสร็จแล้ว |
| [TS-US-11-4](../step-03-merge/test-scenarios.md#design-ts-us-11-4) | ครัวหนึ่งแตะส่งสถานะถึงหน้าร้านครบชุด LAN | mock-not-testable / MOCK_NOT_TESTABLE | ต้องมีการส่งสถานะข้ามจอบน LAN จริง; ไม่วัดจอลูกค้าแทนหน้าร้าน; Precondition/reset: จอครัวและหน้าร้านแยกอุปกรณ์บน LAN ระบบทดสอบจริง; ไม่มีใน Input |
| [TS-US-11-5](../step-03-merge/test-scenarios.md#design-ts-us-11-5) | จับการส่งสถานะอาหารไปผิดออเดอร์หลังครัวแตะครั้งเดียว | mock-not-testable / MOCK_NOT_TESTABLE | แก้ D04 เชิงออกแบบ; ต้องมีระบบ/จุดแทรก fault และจุดสังเกตตาม Precondition ซึ่งยังไม่มี จึง BLOCKED การรัน. เป็นแผนตรวจจับผลผิดด้วย oracle อิสระ ไม่ใช่การเปลี่ยนชื่อ happy path; ยังไม่ได้ทำ fault หรือรันทดสอบ; Precondition/reset: BLOCKED การรัน: ต้องมีครัว/หน้าร้านบนอุปกรณ์แยก LAN และตัวแทรกปลายทางสถานะสำหรับหน้าร้าน; Input ไม่มีเครื่องมือดังกล่าว. คืน snapshot สองใบก่อนแต่ละกรณีและเก็บภาพสองหน้าพร้อมเวลาอ้างอิงเดียวกัน |
| [TS-US-12-5](../step-03-merge/test-scenarios.md#design-ts-us-12-5) | กดหมดซ้ำหรือวัตถุดิบหลายชนิดหมดซ้อน | mock-not-testable / MOCK_NOT_TESTABLE | ต้องตรวจเหตุปิดซ้อนในระบบจริงหลังได้กติกา; โค้ด mock ไม่เป็นนโยบายร้าน; Precondition/reset: ระบบทดสอบจริงและคำตอบ Q-12; เตรียม m01 ผูก chicken และ rice |
| [TS-US-13-3](../step-03-merge/test-scenarios.md#design-ts-us-13-3) | เปิดคืนภายในเวลาบน LAN และชุดไม่ขาดเกิน | mock-not-testable / MOCK_NOT_TESTABLE | ต้องมี LAN และสถานะข้อมูลจริง; ยังไม่มีหลักฐานการส่งข้ามจอ; Precondition/reset: ระบบจริงบน LAN จอครัวและลูกค้าแยก; บันทึกแมปและชุดที่ปิดก่อนทุกครั้ง |
| [TS-US-13-4](../step-03-merge/test-scenarios.md#design-ts-us-13-4) | เติมชนิดเดียวขณะอีกชนิดยังหมดหรือมีการแก้แมป | mock-not-testable / MOCK_NOT_TESTABLE | ต้องมีข้อมูลเหตุปิด/การเปลี่ยนแมปในระบบจริงพร้อมนโยบายยืนยัน; Precondition/reset: ระบบจริงและคำตอบ Q-13; เตรียม m01 ปิดจาก chicken และ rice |
| [TS-US-14-5](../step-03-merge/test-scenarios.md#design-ts-us-14-5) | เปลี่ยนหรือคืนส่งผลถึงครัวภายใน 10 วินาทีครบ 5 กรณี | mock-not-testable / MOCK_NOT_TESTABLE | ต้องมี LAN และเหตุการณ์จากสองจอ; ชุด 5 กรณีของ US-14 แยกการรับรองจาก US-09; Precondition/reset: ระบบทดสอบจริง LAN ลูกค้าและครัวแยก; ยืนยันการเลือกทางออกได้; ไม่มีใน Input |
| [TS-US-14-6](../step-03-merge/test-scenarios.md#design-ts-us-14-6) | คืนซ้ำหรือคืนชนกับเปลี่ยนรายการเดียวกัน | mock-not-testable / MOCK_NOT_TESTABLE | การไม่แสดงปุ่มใน mock ไม่ตรวจ idempotency ฝั่ง server; Precondition/reset: ระบบทดสอบและคำตอบ Q-V2-REFUND/STATE; รายการหนึ่ง pending และมีทางส่งคำสั่งที่บันทึกได้ |
| [TS-US-15-6](../step-03-merge/test-scenarios.md#design-ts-us-15-6) | ตรวจโต๊ะ เลขรับ สถานะและ log ครบ20 ใบในระบบจริง | mock-not-testable / MOCK_NOT_TESTABLE | ต้องมี log ระบบจริง; มีขั้นผู้ตรวจด้วยคนบันทึกผู้ใช้/เวลากด แต่ automationหลักเป็นmock-not-testable เพราะหลักฐาน serverไม่มี; Precondition/reset: ระบบทดสอบจริงและ log เหตุการณ์; ได้คำตอบเขตเวลาของ00:00; ผู้ตรวจทราบผู้ใช้จำลองและเวลากด |
| [TS-US-15-7](../step-03-merge/test-scenarios.md#design-ts-us-15-7) | กดยืนยันเงินซ้ำหรือทั้งสองวิธีชนกัน | mock-not-testable / MOCK_NOT_TESTABLE | ปุ่มdisabledในmockไม่เป็นหลักฐานการป้องกันรับเงินซ้ำหรือกติกาlogจริง; Precondition/reset: ระบบทดสอบจริงและนโยบายการกดซ้ำที่ยืนยัน; ออเดอร์จำลองหนึ่งใบค้างจ่าย |
| [TS-US-16-2](../step-03-merge/test-scenarios.md#design-ts-us-16-2) | คำสั่งที่ผูกรอบปิดแล้วสั่งต่อรอบเดิมไม่ได้ | mock-not-testable / MOCK_NOT_TESTABLE | จำเป็นต้องทดสอบsessionและคำสั่งจริง; ไม่ใช้DOMที่ซ่อนเป็นการพิสูจน์serverป้องกันคำสั่ง; Precondition/reset: ระบบทดสอบจริง; เปิดหน้าลูกค้าค้างและเก็บsessionเก่าก่อนปิด; หน้าร้านมีสิทธิ์ปิดโต๊ะ |
| [TS-US-16-3](../step-03-merge/test-scenarios.md#design-ts-us-16-3) | ปิดแล้วสแกนใหม่แยกรอบครบ5โต๊ะ | mock-not-testable / MOCK_NOT_TESTABLE | ต้องมีระบบจริง5โต๊ะและหลักฐานแยกsession; ไม่สร้างโต๊ะเพิ่มในInputเพื่อให้mockดูครอบคลุม; Precondition/reset: ระบบทดสอบจริงมีQRและโต๊ะจำลอง5โต๊ะ; มีสิทธิ์หน้าร้านและตรวจsessionได้ |
| [TS-US-16-4](../step-03-merge/test-scenarios.md#design-ts-us-16-4) | ขอปิดโต๊ะขณะยังค้างทำหรือค้างจ่าย | mock-not-testable / MOCK_NOT_TESTABLE | ต้องมีผลธุรกิจที่ยืนยันและระบบจริง; การยอมปิดของmockเป็นสมมติฐาน; Precondition/reset: ระบบจริงสำหรับทดสอบและคำตอบQ-16 |
| [TS-US-17-1](../step-03-merge/test-scenarios.md#design-ts-us-17-1) | รวมบิล3รอบพร้อมตรวจเครื่องคิดเลขครบ10โต๊ะ | mock-not-testable / MOCK_NOT_TESTABLE | ต้องมีระบบรวมบิลจริง; มีขั้นตรวจด้วยคนและเครื่องคิดเลขตามAC แต่ยังทำไม่ได้กับmockนี้; Precondition/reset: BLOCKED: UIv2ไม่มีรวมบิลหลายรอบ ไม่มีFR/Flow/ScreenสำหรับUS-17; ต้องมีระบบที่รองรับก่อน; ผู้ตรวจเตรียมเครื่องคิดเลข |
| [TS-US-17-2](../step-03-merge/test-scenarios.md#design-ts-us-17-2) | รวมบิลซ้ำหรือคำสั่งบางรอบยังไม่ยืนยัน | mock-not-testable / MOCK_NOT_TESTABLE | UIv2ไม่มีฟังก์ชันและไม่มีoracleกรณีผิดพลาด ต้องมีระบบ/คำตอบก่อน; Precondition/reset: BLOCKED: ไม่มีระบบรวมบิลและนโยบายกรณีผิดพลาด; เตรียมโต๊ะจำลอง3รอบเมื่อมีระบบ |
| [TS-US-17-3](../step-03-merge/test-scenarios.md#design-ts-us-17-3) | ตรวจบิลรายการขาด ซ้ำ และข้ามโต๊ะโดยทั้งสามรอบยืนยันแล้ว | mock-not-testable / MOCK_NOT_TESTABLE | แก้ D05 เชิงออกแบบ; ต้องมีระบบ/จุดแทรก fault และจุดสังเกตตาม Precondition ซึ่งยังไม่มี จึง BLOCKED การรัน. เป็นแผนตรวจจับผลผิดด้วย oracle อิสระ ไม่ใช่การเปลี่ยนชื่อ happy path; ยังไม่ได้ทำ fault หรือรันทดสอบ; Precondition/reset: BLOCKED การรัน: U17 ไม่มี FR/Flow/Screen/ฟังก์ชันรวมบิล; ต้องมีระบบและจุดแทรกชุดรายการก่อนสร้างบิล. เตรียมตารางอ้างอิงอิสระและเครื่องคิดเลข; ทั้งสามรอบยืนยันครบ ไม่มี draft/คืน/เปลี่ยน/ภาษี/ส่วนลดใน fixture |
| [TS-US-18-1](../step-03-merge/test-scenarios.md#design-ts-us-18-1) | ตัวนับคิวและสีแดงเมื่อค้างเกิน15นาทีครบ10ใบ | mock-not-testable / MOCK_NOT_TESTABLE | ต้องมีระบบรองรับอายุคิวและเวลาเหตุการณ์จริง; ต้องให้คนตรวจสีที่มองเห็นด้วย; btn-advance-10mไม่สร้างฟีเจอร์ที่ขาด; Precondition/reset: BLOCKED: UIv2ไม่มีcounter/สีเตือนUS-18 ไม่มีFR/Flow/Screen; ต้องมีระบบรองรับและยืนยันนิยามค้าง |
| [TS-US-18-2](../step-03-merge/test-scenarios.md#design-ts-us-18-2) | ขอบก่อน/เท่ากับ/เกิน15นาที | mock-not-testable / MOCK_NOT_TESTABLE | ต้องมีฟีเจอร์และเวลาเหตุการณ์จริง; กรณีนี้แยกboundaryเพิ่มจากชุด10ใบไม่ลดจำนวนAC; Precondition/reset: ระบบทดสอบที่ควบคุมเวลาเหตุการณ์ระดับวินาทีได้; ไม่มีในUIv2; หนึ่งออเดอร์ยังค้าง |
| [TS-US-18-3](../step-03-merge/test-scenarios.md#design-ts-us-18-3) | การนับค้างเมื่อรายการรอลูกค้าหรือคืนทั้งหมด | mock-not-testable / MOCK_NOT_TESTABLE | ไม่มีUIcounterและกฎaggregateที่ยืนยัน ต้องมีระบบและคำตอบก่อน; Precondition/reset: ระบบที่มีcounterUS-18และคำตอบเรื่องสถานะ; เตรียมออเดอร์ค้าง3ใบ |
| [TS-US-19-8](../step-03-merge/test-scenarios.md#design-ts-us-19-8) | เผยแพร่เมนูและตัวเลือกเมื่อรีเฟรชภายใน 1 นาที | mock-not-testable / MOCK_NOT_TESTABLE | จำเป็นต้องมีระบบจริงหรือฟีเจอร์/ข้อมูลที่ Input ยังไม่มี; BLOCKED ตาม Precondition และข้อค้าง ไม่ใช้คลิก Mock-up แทน; Precondition/reset: BLOCKED: ต้องมีระบบบันทึกจริงและอุปกรณ์ลูกค้าแยก; HTML reload เรียก reset และล้าง state; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน |
| [TS-US-20-4](../step-03-merge/test-scenarios.md#design-ts-us-20-4) | ผลแมปเมื่อรีเฟรชภายใน 1 นาทีครบ 5 เมนู | mock-not-testable / MOCK_NOT_TESTABLE | จำเป็นต้องมีระบบจริงหรือฟีเจอร์/ข้อมูลที่ Input ยังไม่มี; BLOCKED ตาม Precondition และข้อค้าง ไม่ใช้คลิก Mock-up แทน; Precondition/reset: BLOCKED: ระบบบันทึก/อ่านข้ามอุปกรณ์และหมายเหตุ ค. ไม่มีข้อมูล; ไม่ใช้ reload HTML ที่ล้าง state; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน |
| [TS-US-21-4](../step-03-merge/test-scenarios.md#design-ts-us-21-4) | ขอบหนึ่งวินาที เขตเวลา และสูตร X | mock-not-testable / MOCK_NOT_TESTABLE | จำเป็นต้องมีระบบจริงหรือฟีเจอร์/ข้อมูลที่ Input ยังไม่มี; BLOCKED ตาม Precondition และข้อค้าง ไม่ใช้คลิก Mock-up แทน; Precondition/reset: BLOCKED: ไม่มีนิยามเขตเวลา/ขอบหน้าต่าง/สูตร X ที่อนุมัติและไม่มีเครื่องมือ UI ขยับทีละวินาที; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน |
| [TS-US-21-6](../step-03-merge/test-scenarios.md#design-ts-us-21-6) | ยืนยัน threshold สามรอบด้วยเหตุการณ์ระบบจริง | mock-not-testable / MOCK_NOT_TESTABLE | จำเป็นต้องมีระบบจริงหรือฟีเจอร์/ข้อมูลที่ Input ยังไม่มี; BLOCKED ตาม Precondition และข้อค้าง ไม่ใช้คลิก Mock-up แทน; Precondition/reset: BLOCKED: ไม่มีระบบจริง/เหตุการณ์ server และ oracle สูตร X; ต้องตั้งช่วงเวลาที่ตกลงและลูกค้าหลายหน้าจอ; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน |
| [TS-US-22-1](../step-03-merge/test-scenarios.md#design-ts-us-22-1) | ปิดรับกลับบ้านแต่ QR หน้าร้านยังสั่งได้ | mock-not-testable / MOCK_NOT_TESTABLE | จำเป็นต้องมีระบบจริงหรือฟีเจอร์/ข้อมูลที่ Input ยังไม่มี; BLOCKED ตาม Precondition และข้อค้าง ไม่ใช้คลิก Mock-up แทน; Precondition/reset: BLOCKED: US-22 ไม่มี FR/Flow/สวิตช์ใน UI v2; ต้องมีระบบ LAN จริงและเริ่มเปิดรับกลับบ้าน; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน |
| [TS-US-22-2](../step-03-merge/test-scenarios.md#design-ts-us-22-2) | หน้ากลับบ้านค้างอยู่ก่อนผู้จัดการปิดรับ | mock-not-testable / MOCK_NOT_TESTABLE | จำเป็นต้องมีระบบจริงหรือฟีเจอร์/ข้อมูลที่ Input ยังไม่มี; BLOCKED ตาม Precondition และข้อค้าง ไม่ใช้คลิก Mock-up แทน; Precondition/reset: BLOCKED: ไม่มี UI ปิดรับและไม่กำหนดผล submit จากหน้าเดิม; ระบบจริงต้องพร้อมก่อนทดลอง; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน |
| [TS-US-22-3](../step-03-merge/test-scenarios.md#design-ts-us-22-3) | เปิดรับกลับบ้านคืนด้วยสวิตช์เดียว | mock-not-testable / MOCK_NOT_TESTABLE | จำเป็นต้องมีระบบจริงหรือฟีเจอร์/ข้อมูลที่ Input ยังไม่มี; BLOCKED ตาม Precondition และข้อค้าง ไม่ใช้คลิก Mock-up แทน; Precondition/reset: BLOCKED: ฟีเจอร์เปิด/ปิดไม่อยู่ใน UI v2; ระบบเริ่มปิดรับและหน้าร้านยังเปิด; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน |
| [TS-US-22-4](../step-03-merge/test-scenarios.md#design-ts-us-22-4) | จับการปิดรับกลับบ้านที่ปิดการสั่งผ่าน QR หน้าร้านผิดขอบเขต | mock-not-testable / MOCK_NOT_TESTABLE | แก้ D06 เชิงออกแบบ; ต้องมีระบบ/จุดแทรก fault และจุดสังเกตตาม Precondition ซึ่งยังไม่มี จึง BLOCKED การรัน. เป็นแผนตรวจจับผลผิดด้วย oracle อิสระ ไม่ใช่การเปลี่ยนชื่อ happy path; ยังไม่ได้ทำ fault หรือรันทดสอบ; Precondition/reset: BLOCKED การรัน: U22 ไม่มี mapping/สวิตช์รับกลับบ้านและระบบ QR จริง; ต้องมีระบบทดสอบพร้อมตัวแทรกขอบเขตช่องทางที่ตรวจการรับออเดอร์ก่อนยืนยัน. ยังไม่มีจุดแทรกหรือ selector ใน Input; ไม่ใช้ toggle-promptpay |
| [TS-US-23-1](../step-03-merge/test-scenarios.md#design-ts-us-23-1) | รายงานช่วงวันที่และยอดจ่ายแล้วจาก 20 ใบ | mock-not-testable / MOCK_NOT_TESTABLE | จำเป็นต้องมีระบบจริงหรือฟีเจอร์/ข้อมูลที่ Input ยังไม่มี; BLOCKED ตาม Precondition และข้อค้าง ไม่ใช้คลิก Mock-up แทน; Precondition/reset: BLOCKED: report-screen เป็น placeholder; ไม่มี FR/Flow/ตารางรายงานใน v2; ต้องมีระบบจริงบน Ubuntu และผู้ตรวจนับมือ; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน |
| [TS-US-23-2](../step-03-merge/test-scenarios.md#design-ts-us-23-2) | ส่งออก CSV และเปิดด้วย LibreOffice | mock-not-testable / MOCK_NOT_TESTABLE | จำเป็นต้องมีระบบจริงหรือฟีเจอร์/ข้อมูลที่ Input ยังไม่มี; BLOCKED ตาม Precondition และข้อค้าง ไม่ใช้คลิก Mock-up แทน; Precondition/reset: BLOCKED: ไม่มีปุ่ม export หรือ CSV จริงใน UI v2; ต้องมีรายงานระบบจริงและ LibreOffice ให้คนตรวจ; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน |
| [TS-US-23-3](../step-03-merge/test-scenarios.md#design-ts-us-23-3) | ออเดอร์ยังไม่จ่ายหรือค้างจ่ายไม่รวมยอดรายงาน | mock-not-testable / MOCK_NOT_TESTABLE | จำเป็นต้องมีระบบจริงหรือฟีเจอร์/ข้อมูลที่ Input ยังไม่มี; BLOCKED ตาม Precondition และข้อค้าง ไม่ใช้คลิก Mock-up แทน; Precondition/reset: BLOCKED: ไม่มีระบบรายงาน; เตรียม D23 20 ใบรวมสถานะต่างกันตาม TS-US-23-1; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน |
| [TS-US-23-4](../step-03-merge/test-scenarios.md#design-ts-us-23-4) | ช่วงวันที่ไม่ถูกต้องหรือไม่มีรายการ | mock-not-testable / MOCK_NOT_TESTABLE | จำเป็นต้องมีระบบจริงหรือฟีเจอร์/ข้อมูลที่ Input ยังไม่มี; BLOCKED ตาม Precondition และข้อค้าง ไม่ใช้คลิก Mock-up แทน; Precondition/reset: BLOCKED: ไม่มีฟอร์มรายงาน/นโยบาย validation; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน |
| [TS-US-24-1](../step-03-merge/test-scenarios.md#design-ts-us-24-1) | ประวัติชื่อวัตถุดิบ เวลา ผู้กด และจำนวนรายสัปดาห์ | mock-not-testable / MOCK_NOT_TESTABLE | จำเป็นต้องมีระบบจริงหรือฟีเจอร์/ข้อมูลที่ Input ยังไม่มี; BLOCKED ตาม Precondition และข้อค้าง ไม่ใช้คลิก Mock-up แทน; Precondition/reset: BLOCKED: ไม่มี FR/Flow/หน้าประวัติหรือ stock audit log ใน v2; ระบบจริงและนิยามสัปดาห์ต้องพร้อม; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน |
| [TS-US-24-2](../step-03-merge/test-scenarios.md#design-ts-us-24-2) | กดหมดซ้ำขณะวัตถุดิบยังหมด | mock-not-testable / MOCK_NOT_TESTABLE | จำเป็นต้องมีระบบจริงหรือฟีเจอร์/ข้อมูลที่ Input ยังไม่มี; BLOCKED ตาม Precondition และข้อค้าง ไม่ใช้คลิก Mock-up แทน; Precondition/reset: BLOCKED: ไม่มีประวัติจริงและนโยบายเหตุการณ์ซ้ำ; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน |
| [TS-US-24-3](../step-03-merge/test-scenarios.md#design-ts-us-24-3) | จับประวัติผิดผู้กดและความถี่ผิดจากสิบเหตุการณ์ที่ restock ก่อนทุกครั้ง | mock-not-testable / MOCK_NOT_TESTABLE | แก้ D07 เชิงออกแบบ; ต้องมีระบบ/จุดแทรก fault และจุดสังเกตตาม Precondition ซึ่งยังไม่มี จึง BLOCKED การรัน. เป็นแผนตรวจจับผลผิดด้วย oracle อิสระ ไม่ใช่การเปลี่ยนชื่อ happy path; ยังไม่ได้ทำ fault หรือรันทดสอบ; Precondition/reset: BLOCKED การรัน: U24 ไม่มี stock history/log/หน้าประวัติและตัวแทรกข้อมูลแสดงผล; ต้องมีระบบทดสอบและบันทึกเหตุการณ์อิสระจากหน้าประวัติ. ใช้สัปดาห์ fixture 2026-01-05 00:00 ถึงก่อน 2026-01-12 00:00 +07:00; ทุกเหตุการณ์อยู่กลางช่วง ไม่ใช้ตัดสินขอบสัปดาห์จริง |
| [TS-US-25-5](../step-03-merge/test-scenarios.md#design-ts-us-25-5) | ตรวจบัญชี ล็อก และสิทธิ์ URL ที่ระบบจริง | mock-not-testable / MOCK_NOT_TESTABLE | จำเป็นต้องมีระบบจริงหรือฟีเจอร์/ข้อมูลที่ Input ยังไม่มี; BLOCKED ตาม Precondition และข้อค้าง ไม่ใช้คลิก Mock-up แทน; Precondition/reset: BLOCKED: ไม่มีbackend/บัญชีระบบทดสอบ/นาฬิกาserver; ใช้เฉพาะบัญชีสังเคราะห์บนระบบที่ได้รับอนุญาต; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน |
| [TS-US-26-1](../step-03-merge/test-scenarios.md#design-ts-us-26-1) | ติดตั้งด้วยสคริปต์เดียวและเก็บข้อมูลในร้าน | mock-not-testable / MOCK_NOT_TESTABLE | จำเป็นต้องมีระบบจริงหรือฟีเจอร์/ข้อมูลที่ Input ยังไม่มี; BLOCKED ตาม Precondition และข้อค้าง ไม่ใช้คลิก Mock-up แทน; Precondition/reset: BLOCKED: ไม่มีสคริปต์ติดตั้ง/ระบบจริงหรือข้อมูลรุ่นUbuntuและเครื่องทดสอบ; ต้องได้สภาพเริ่มต้นที่ยืนยันก่อนวัด; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน |
| [TS-US-26-2](../step-03-merge/test-scenarios.md#design-ts-us-26-2) | อินเทอร์เน็ตภายนอกหลุดยังทำงานครบ 20 ใบ | mock-not-testable / MOCK_NOT_TESTABLE | จำเป็นต้องมีระบบจริงหรือฟีเจอร์/ข้อมูลที่ Input ยังไม่มี; BLOCKED ตาม Precondition และข้อค้าง ไม่ใช้คลิก Mock-up แทน; Precondition/reset: BLOCKED: ต้องติดตั้งระบบจริงบนUbuntuและLAN/Wi-Fiยังทำงาน; ไม่มีระบบดังกล่าวในInput; ใช้เครือข่ายทดลองที่ได้รับอนุญาต; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน |

### manual — 6 รายการที่ต้องให้คนตรวจ

| TestID | Scenario เดิม | Automation / Status คงเดิม | เหตุผล/เงื่อนไขที่ยังต้องมีตามต้นทาง |
|---|---|---|---|
| [TS-US-04-2](../step-03-merge/test-scenarios.md#design-ts-us-04-2) | ตัวเลือกหลายชนิดที่ผู้จัดการตั้งแสดงครบและอ่านได้ | manual / MANUAL_PENDING | manual เพราะมีขั้นตรวจ label/การผูกตัวเลือกกับจานด้วยคนบน mock; ไม่ต้องใช้ธุรกรรมจริงและไม่มีผลตรวจในรอบนี้; Precondition/reset: R0; เข้า M0 หน้าจัดการเมนู; ใช้ผู้ตรวจคนอ่าน label/ความสัมพันธ์กับจานและเปรียบเทียบ configuration |
| [TS-US-16-1](../step-03-merge/test-scenarios.md#design-ts-us-16-1) | หน้าร้านเปิด–ปิดโต๊ะแล้วเปิดรอบใหม่ไม่ปนรายการเดิม | manual / MANUAL_PENDING | manualเพราะให้คนตรวจการเปิดโต๊ะและรายการทั้งรอบที่ไม่มีtestidเฉพาะ; ใช้UIจำลองได้ ไม่พิสูจน์QRจริงหรือsessionฝั่งserver; Precondition/reset: R0; ไม่มีรอบเปิดที่โต๊ะ01; ผู้ตรวจใช้บัญชีหน้าร้านจำลอง |
| [TS-US-19-2](../step-03-merge/test-scenarios.md#design-ts-us-19-2) | รูป jpg/png ที่ขนาดขอบเขตและการแสดงรูป | manual / MANUAL_PENDING | มีขั้นตรวจภาพ/ข้อความ/ขอบเขตด้วยคนตามขั้นตอน; ยังไม่ได้ตรวจ ไม่มีผล manual และไม่ใช้ความเห็นแทนคำตอบธุรกิจที่ขาด; Precondition/reset: R0 → M → nav-menu-admin; ผู้ตรวจมีภาพสังเคราะห์ที่เปิดได้จริง ไม่ใช้รูปบุคคลจริง; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน |
| [TS-US-19-3](../step-03-merge/test-scenarios.md#design-ts-us-19-3) | รูปผิดชนิดหรือเกินขนาด | manual / MANUAL_PENDING | มีขั้นตรวจภาพ/ข้อความ/ขอบเขตด้วยคนตามขั้นตอน; ยังไม่ได้ตรวจ ไม่มีผล manual และไม่ใช้ความเห็นแทนคำตอบธุรกิจที่ขาด; Precondition/reset: R0 → M → nav-menu-admin; ตั้งเมนู/รูปที่ถูกต้องเป็นค่าฐานก่อนทุกกรณี; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน |
| [TS-US-21-5](../step-03-merge/test-scenarios.md#design-ts-us-21-5) | ค่าตั้งความจุไม่ครบหรือช่วงกลับด้าน | manual / MANUAL_PENDING | มีขั้นตรวจภาพ/ข้อความ/ขอบเขตด้วยคนตามขั้นตอน; ยังไม่ได้ตรวจ ไม่มีผล manual และไม่ใช้ความเห็นแทนคำตอบธุรกิจที่ขาด; Precondition/reset: R0 → M → nav-capacity; บันทึกค่าฐาน 11:30–13:30,N=5,X=10 ก่อนแต่ละกรณี; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน |
| [TS-US-25-6](../step-03-merge/test-scenarios.md#design-ts-us-25-6) | ชื่อบัญชีซ้ำและขอบเขตการจัดการบัญชี | manual / MANUAL_PENDING | มีขั้นตรวจภาพ/ข้อความ/ขอบเขตด้วยคนตามขั้นตอน; ยังไม่ได้ตรวจ ไม่มีผล manual และไม่ใช้ความเห็นแทนคำตอบธุรกิจที่ขาด; Precondition/reset: R0 → M → nav-accounts; สร้าง dup01/PIN1234/kitchenหนึ่งบัญชีก่อน; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน |

Scenario เชิงออกแบบแบบ auto อีก **51 TestID คง NOT_RUN** เพราะไม่มีผลใน JSON แม้จะเชื่อม US หรือ Flow เดียวกับ fixture ที่ผ่าน ไม่กระจาย UI_PASS/UI_FAIL ไปยัง scenario เหล่านี้

## ผลการอัปเดต traceability

สร้าง [traceability-after-ui.csv](traceability-after-ui.csv) โดยคง header เดิม `US,FR,Flow,Screen,TestID,Scenario,Status`, ลำดับแถว และข้อความทุกช่องเดิม เปลี่ยนเฉพาะ Status ของทุกแถวที่ TestID มีผลจริง: pass → UI_PASS, fail → UI_FAIL, skip → SKIP. TestID เดียวอาจมีหลายแถว mapping จึงไม่ใช้จำนวนแถวเป็นจำนวนการทดสอบ

| Status หลังอัปเดต | TestID ไม่ซ้ำ | แถว CSV |
|---|---:|---:|
| UI_PASS | 12 | 153 |
| UI_FAIL | 2 | 22 |
| SKIP | 0 | 0 |
| NOT_RUN | 51 | 856 |
| MANUAL_PENDING | 6 | 110 |
| MOCK_NOT_TESTABLE | 57 | 404 |
| รวม | 128 | 1545 |

เปลี่ยน Status **175 แถวของ 14 fixture TestID**; อีก **1370 แถวของ 114 TestID** คงเดิม ตรวจเทียบรายช่องแล้วไม่มีการเปลี่ยน US, FR, Flow, Screen, TestID หรือ Scenario และ header คงเดิม ไม่เพิ่มหรือลบแถว และไม่แก้ไฟล์ traceability ต้นทาง

## NFR ระบบจริง ข้อค้าง และสิ่งที่ยังไม่ได้ทดสอบ

ผล UI_PASS ทั้ง 12 รายการจำกัดที่ `offline mock UI` เท่านั้น ทุกแถวระบบจริงใน [nfr-split.md](../step-04-nfr-split/nfr-split.md) คง **NOT_TESTED; ความพร้อม BLOCKED; Actual ไม่มีข้อมูล**. ไม่อัปเดตแถว functional ระดับ US ของเอกสารนั้นเป็นผ่านทั้งข้อ และไม่มีการรับรอง NFR ระบบจริงเป็น PASS

- ยังไม่ทดสอบ QR/Wi-Fi/LAN และเวลาระหว่างอุปกรณ์จริง, หน้าจอเปิดค้าง/ไม่รีเฟรช, timestamp/concurrency และการทดสอบแทรกข้อผิดพลาดตามแบบ; elapsed time ของ runner ใช้แทน SLA ไม่ได้
- ยังไม่มีผลสูตร ETA/ประวัติ 7 วัน/ประชากรออเดอร์ช่วงเร่งด่วนครบ 1 วันและ server log, ขอบเวลาระดับวินาที/เขตเวลา/สูตร X หรือสถานะที่อนุมัติ; US-07 ใช้ 11:30–13:00 และ 17:30–19:30 คงเดิม แยกจากช่วงตัวอย่าง 11:30–13:30 ของ US-21
- Security ฝั่ง server ยังไม่มีผล authentication/authorization, PIN/เวลาล็อก, session และ audit log จริง; การใส่ PIN ผิดครั้งเดียวของ fixture ไม่ยืนยันล็อก 5 ครั้ง/5 นาทีหรือ 3 บัญชี × 2 หน้า ผ่าน 6 จาก 6
- Load/Availability ทั่วไปยังไม่มีข้อมูล workload และเกณฑ์ตัวเลข; concurrency เฉพาะ US-10 หรือ capacity N=5 ไม่ยืนยัน Load ส่วน offline HTML ไม่ยืนยัน WAN ขาด, uptime, การกู้คืน หรือ Availability ของระบบติดตั้งจริง
- ยังไม่ทดสอบข้อมูลคงทน/refresh, รวมบิลหลายรอบ, อายุคิว, สวิตช์รับกลับบ้าน, รายงาน/CSV/LibreOffice, ประวัติวัตถุดิบ, Ubuntu/สคริปต์ติดตั้ง/ที่เก็บข้อมูลในร้าน และการทำงานขณะถอด WAN; US-17/18/22/23/24 ยังมี mapping/implementation MISSING ตาม Input ไม่สร้าง FR/Flow/selector ทดแทน
- ไม่มีการชำระหรือคืนเงินจริง; PromptPay/เงินสด/สลิป/ยอดในผลนี้เป็นข้อมูลจำลอง การคลิกหรือแสดงยอด 0 บาทไม่พิสูจน์เงินเข้า/คืนเงินจริง
- visual review/responsive/layout ยังไม่มีผลผู้เปิดตรวจภาพแยกไว้; มีเพียง path ภาพที่ตรวจพบไฟล์เท่านั้น ไม่ใช้ผล assertions สรุปความสวยงามหรือ layout ถูกต้อง

ข้อค้างจาก Input ยังคง: DI-01–03 หมายเหตุ ก./ค./ช. ไม่มีข้อมูล; DI-04 คง US-20 อ้าง US-14 ตามเดิม; DI-06/07 ช่วงเวลา/สถานะยังต้องยืนยัน; Q เดิม 18 รายการและ Q-V2-REFUND/STATE/CAPACITY ยังเปิด; A-01–A-06 และสมมติฐานชุดข้อมูลยังไม่ใช่ข้อกำหนดร้าน รวมถึง oracle การคืน/เปลี่ยน/กดซ้ำ/คำสั่งชน, Q-25/PIN/สิทธิ์ และ Q-26/สภาพติดตั้งต้องมีข้อมูลก่อนรับรอง ตรวจซ้ำในรุ่นใหม่ตามเกณฑ์และจำนวนตัวอย่างเดิมทุกข้อในภาคผนวก ไม่ลดจำนวนตัวอย่างให้เท่ากับ smoke

## ภาคผนวก — reason ของผลล้มเหลวตาม JSON

คัด reason ตรงตัว ไม่ขยายส่วนที่ JSON ไม่ได้เก็บไว้; F01 จบข้อความ Aria ที่ `- s` ตามหลักฐานที่ได้รับ ไม่มีข้อมูลส่วนที่เหลือ และไม่ได้อ่าน screenshot เพื่อเติมข้อความ

### TS-US-09-101

```text
Step 18: AssertionError: Locator expected to be visible
Actual value: None
Error: element(s) not found 
Call log:
  - Expect "to_be_visible" with timeout 2500ms
  - waiting for get_by_test_id("payment-summary-total")

Aria snapshot:
- link "ข้ามไปเนื้อหา":
  - /url: "#main"
- banner:
  - text: ห้องทดลอง UI v2 • ข้อมูลจำลอง
  - heading "ครัวคุณยาย" [level=1]
  - text: จำลอง • ไม่มีการสั่งหรือโอนเงินจริง
  - strong: นาฬิกาจำลอง
  - text: 2026-01-01T12:00:00+07:00 เวลา +07:00 เดินเมื่อกดปุ่มเท่านั้น
  - button "+1 นาที"
  - button "+5 นาที"
  - button "+10 นาที จำลอง"
  - button "+1 วัน"
  - button "รีเซ็ตทั้งหมด / ออกจากระบบ"
  - paragraph: สลับบทบาท จำลอง ข้อมูลร่วมกันเฉพาะในแท็บนี้ • เข้าแท็บพนักงานหรือผู้จัดการใหม่ต้องล็อกอินทุกครั้ง
  - navigation "สลับบทบาทจำลอง":
    - button "ลูกค้า" [pressed]
    - button "ครัวและหน้าร้าน"
    - button "ผู้จัดการ"
- main:
  - group: วิธีเล่นและข้อค้างที่ต้องทบทวน
  - heading "วันนี้รับอะไรดี" [level=2]
  - text: QR โต๊ะ จำลอง รูปแบบการสั่ง
  - combobox "รูปแบบการสั่ง":
    - option "ทานที่ร้าน" [selected]
    - option "สั่งกลับบ้าน"
  - text: เลือกโต๊ะ แทนสแกน QR ที่มี table_id
  - combobox "เลือกโต๊ะ แทนสแกน QR ที่มี table_id":
    - option "โต๊ะ 01" [selected]
    - option "โต๊ะ 02"
    - option "โต๊ะ 03"
  - button "เปิดเมนู / เริ่มรอบสั่ง"
  - strong: โต๊ะ 01
  - text: "Session: S-0001"
  - region "รายการที่ครัวทำไม่ได้":
    - heading "แจ้งจากครัว / ทางเลือกของคุณ" [level=2]
    - paragraph: "จำลอง: จำนวนจานละ 1 · เมนูแทนใช้ราคาและตัวเลือกที่เห็นก่อนยืนยัน · วิธีคิดส่วนต่างยังไม่ยืนยัน ไม่มีการรับหรือคืนเงินจริง"
    - status: คืนรายการแล้ว ลดเฉพาะยอดจำลองและนำออกจากคิวที่ต้องทำ ไม่ใช่การโอนเงินคืน
    - article:
      - 'heading "ออเดอร์ #1" [level=3]'
      - strong: กะเพราไก่
      - text: · คืนรายการแล้ว
      - paragraph: "snapshot เดิม: กะเพราไก่ — 50 บาท"
      - paragraph: ยอดรายการปัจจุบัน 0 บาท · ไม่มีการยืนยันโอนเงินคืน
      - paragraph:
        - text: "ยอดหลังปรับรายการ (จำลอง):"
        - strong: 0 บาท
  - heading "เมนูจากครัว" [level=2]
  - text: 8 เมนู • ราคาจำลอง
  - button "กะเพราไก่ 50 บาท · สั่งได้":
    - strong: กะเพราไก่
    - text: 50 บาท · สั่งได้
  - button "ข้าวหมูทอด 55 บาท · สั่งได้":
    - strong: ข้าวหมูทอด
    - text: 55 บาท · สั่งได้
  - button "ข้าวไข่เจียว 40 บาท · สั่งได้":
    - strong: ข้าวไข่เจียว
    - text: 40 บาท · สั่งได้
  - button "ผัดเส้นไก่ 50 บาท · สั่งได้":
    - s
```

### TS-US-21-101

```text
Step 6: TimeoutError: Locator.evaluate: Timeout 2500ms exceeded.
Call log:
  - waiting for get_by_test_id("rush-start")

```

## ภาคผนวก — US/AC ต้นฉบับครบ 26 รายการ

คัดตารางจากภาคผนวกของ nfr-split.md ตรงตัวเพื่อคงข้อความ US/AC ตัวเลข หน่วย สูตร และจำนวนตัวอย่างเดิมทั้งหมด ตารางนี้เป็นข้อกำหนด ไม่ใช่ผลผ่าน URL ตัวอย่างใน AC เป็นเส้นทางของแอป ไม่ใช่ path เครื่อง

| ID | บทบาท | ในฐานะ | ฉันต้องการ | เพื่อ | เกณฑ์รับ |
|---|---|---|---|---|---|
| US-01 | ลูกค้า | ลูกค้าที่นั่งในร้าน | สแกน QR ที่โต๊ะแล้วเปิดเมนูได้โดยไม่ต้องล็อกอิน | เริ่มสั่งอาหารได้เร็วไม่ต้องรอพนักงาน | นับจากกล้องมือถืออ่าน QR สำเร็จ จนถึงหน้าเมนูแสดงรายการแรก ภายใน 3 วินาทีบน Wi‑Fi ร้าน ในอย่างน้อย 18 จาก 20 ครั้งของชุดทดสอบ |
| US-02 | ลูกค้า | ลูกค้าที่นั่งในร้าน | ให้ออเดอร์ที่สั่งผ่าน QR ผูกกับหมายเลขโต๊ะอัตโนมัติ | ไม่ต้องพิมพ์เลขโต๊ะเองและอาหารมาถูกโต๊ะ | QR แต่ละโต๊ะมี URL ที่มี table_id (เช่น `/t/07`) และออเดอร์ที่สร้างจาก QR โต๊ะทดสอบ 20 โต๊ะ มี table_id ตรงกับป้ายโต๊ะอย่างน้อย 19 จาก 20 ใบ โดยตรวจจากหน้าจอหน้าร้าน |
| US-03 | ลูกค้า | ลูกค้าสั่งกลับบ้าน | เลือกโหมด “สั่งกลับบ้าน” และระบุเวลามารับ | มารับอาหารได้ตรงเวลาไม่ต้องรอที่ร้าน | เลือกเวลารับได้จากรายการช่วงเวลาละ 15 นาที (เช่น 12:00–12:15, 12:15–12:30) ที่เริ่มอย่างน้อย 20 นาทีหลังเวลาสั่ง และออเดอร์สั่งกลับบ้านทดสอบ 10 ใบ แสดงป้าย “สั่งกลับบ้าน” พร้อมช่วงเวลารับบนจอครัวครบทั้ง 10 ใบ |
| US-04 | ลูกค้า | ลูกค้าที่แพ้อาหารหรือชอบรสจัด | เลือกตัวเลือกเพิ่มต่อจาน (ระดับเผ็ด ไม่ใส่ผักชี เพิ่มไข่ดาว) | ได้อาหารตรงตามที่ต้องการ | เมนูที่ผู้จัดการตั้งตัวเลือกไว้แสดงตัวเลือกครบตามที่ตั้ง ราคาเพิ่มรวมในยอดก่อนกดยืนยัน และตัวเลือกที่เลือกปรากฏในใบครัวอย่างน้อย 19 จาก 20 ใบของชุดทดสอบ |
| US-05 | ลูกค้า | ลูกค้าที่สั่งแล้ว | เห็นสถานะออเดอร์แบบเรียลไทม์ (รับออเดอร์ / กำลังทำ / เสร็จแล้ว) | รู้ว่าต้องรออีกนานแค่ไหน | นับจากพนักงานครัวกดปุ่มเปลี่ยนสถานะ จนถึงหน้าจอลูกค้าที่โต๊ะแสดงสถานะใหม่โดยไม่รีเฟรช ภายใน 5 วินาทีบน LAN ในร้าน ในอย่างน้อย 18 จาก 20 ครั้งของชุดทดสอบ |
| US-06 | ลูกค้า | ลูกค้าสั่งช่วงเที่ยง | เห็นเมนูที่วัตถุดิบหมดถูกปิดหรือติดป้าย “หมด” | ไม่เสียเวลาสั่งแล้วถูกยกเลิก | นับจากพนักงานครัวกด “วัตถุดิบหมด” จนถึงหน้าลูกค้าแสดงป้าย “หมด” และปุ่มสั่งถูกปิด ภายใน 10 วินาทีบน LAN ในร้าน ในอย่างน้อย 9 จาก 10 ครั้ง และเมื่อพยายามสั่งเมนูที่ปิดแล้ว ระบบปฏิเสธพร้อมข้อความแจ้ง |
| US-07 | ลูกค้า | ลูกค้าในช่วงเร่งด่วน | เห็นเวลารอโดยประมาณก่อนยืนยันสั่ง | ตัดสินใจได้ว่าจะสั่งหรือเปลี่ยนเมนู | หน้ายืนยันสั่งแสดงเวลารอโดยประมาณทุกออเดอร์ คำนวณจากสูตร: (จำนวนออเดอร์ค้างในคิวครัวที่ยังไม่ “พร้อมเสิร์ฟ” × เวลาเฉลี่ยต่อออเดอร์ 7 วันล่าสุด) + เวลาเฉลี่ยต่อเมนูของเมนูที่นานที่สุดในตะกร้า · เวลาจริงวัดจากจุดเริ่ม “ลูกค้ากดยืนยันสั่ง” ถึงจุดจบ “ครัวกดสถานะพร้อมเสิร์ฟ” (log ฝั่งเซิร์ฟเวอร์) · ช่วงเร่งด่วนนิยามเป็น 11:30–13:00 และ 17:30–19:30 · ในออเดอร์ช่วงเร่งด่วนของ 1 วันทดสอบ ค่าประมาณคลาดเคลื่อนจากเวลาจริงไม่เกิน 10 นาทีในอย่างน้อย 80% ของออเดอร์ (ดูหมายเหตุ ช.) |
| US-08 | ลูกค้า | ลูกค้าที่จ่ายเงิน | เห็นสรุปรายการ ยอดรวม และเลือกวิธีจ่าย (เงินสด หรือโอนผ่าน QR PromptPay) พร้อมทางออกเมื่อ PromptPay ใช้ไม่ได้ | ตรวจสอบยอดก่อนจ่ายและจ่ายได้สะดวกแม้ในกรณีผิดปกติ | ยอดรวมบนหน้าสรุปของลูกค้าตรงกับยอดบนจอหน้าร้านในอย่างน้อย 19 จาก 20 ใบของชุดทดสอบ และเลือกวิธีจ่ายได้ 2 แบบทุกออเดอร์ · เมื่อเลือก PromptPay ออเดอร์อยู่สถานะ “ค้างจ่าย” จนพนักงานหน้าร้านยืนยันสลิป · ถ้าสลิปยังไม่ยืนยันภายใน 10 นาที หรือผู้จัดการร้านตั้งค่า “PromptPay ปิดใช้งาน” หน้าลูกค้าแสดงข้อความให้ชำระเงินสดที่หน้าร้าน และพนักงานหน้าร้านกด “รับเงินสด” หรือ “ยืนยันสลิป” เพื่อเปลี่ยนเป็น “จ่ายแล้ว” ได้ · ทดสอบ 3 กรณี (PromptPay ปกติ / ปิดใช้งาน / สลิปไม่ยืนยันเกิน 10 นาที) ผ่าน 3 จาก 3 (ดูหมายเหตุ ก.) |
| US-09 | ลูกค้า | ลูกค้าที่ออเดอร์ค้างในคิวครัวแล้ววัตถุดิบหมด | ได้รับแจ้งบนหน้าจอและเลือกทางออกได้ (เปลี่ยนเมนู หรือคืนรายการนั้น) | ไม่ต้องรอเปล่าและยอดจ่ายถูกปรับให้ตรง | เมื่อครัวกด “ทำไม่ได้-วัตถุดิบหมด” ที่รายการในคิว หน้าลูกค้าแสดงแจ้งเตือนภายใน 10 วินาทีบน LAN พร้อมปุ่ม “เปลี่ยนเมนู” และ “คืนรายการ” และยอดรวมปรับลดตามรายการที่คืน ทดสอบผ่าน 5 จาก 5 กรณี |
| US-10 | พนักงานครัว/หน้าร้าน | พนักงานครัว | เห็นออเดอร์ใหม่บนจอครัวเรียงตามลำดับที่สั่งอย่างคงที่ | ไม่พลาดออเดอร์ในช่วงเร่งด่วน | นับจากลูกค้ากดยืนยันสั่ง จนถึงจอครัวแสดงออเดอร์ใหม่ ภายใน 3 วินาทีบน LAN ในร้าน ในอย่างน้อย 18 จาก 20 ใบของชุดทดสอบ · กฎเรียงลำดับ: เรียงตาม timestamp ฝั่งเซิร์ฟเวอร์ที่รับคำสั่ง (ความละเอียดวินาที) จากน้อยไปมาก และเมื่อ timestamp เท่ากันหรือออเดอร์เข้าพร้อมกัน ให้เรียงตามเลขออเดอร์ที่ระบบออกให้แบบ monotonic (เพิ่มขึ้นทีละ 1 ไม่ซ้ำ ไม่ย้อนกลับ) · ทดสอบยิง 30 ออเดอร์ต่อเนื่องจากมือถือ 2 เครื่องพร้อมกัน ลำดับบนจอครัวต้องตรงกับลำดับเลขออเดอร์ 30 จาก 30 ใบ และรันซ้ำ 3 รอบต้องได้ผลเดิมทุกรอบ (ไม่ยอมรับการสลับคู่) |
| US-11 | พนักงานครัว/หน้าร้าน | พนักงานครัว | กดเปลี่ยนสถานะออเดอร์ (กำลังทำ / เสร็จแล้ว) ด้วยปุ่มเดียว | ให้ลูกค้าและหน้าร้านรู้สถานะโดยไม่ต้องตะโกน | เปลี่ยนสถานะได้ใน 1 แตะ และนับจากกดปุ่มบนจอครัว จนถึงจอหน้าร้านแสดงสถานะใหม่ ภายใน 5 วินาทีบน LAN ในร้าน ในอย่างน้อย 18 จาก 20 ครั้งของชุดทดสอบ |
| US-12 | พนักงานครัว/หน้าร้าน | พนักงานครัว | กด “วัตถุดิบหมด” ที่วัตถุดิบ แล้วระบบปิดเมนูและตัวเลือกที่ใช้วัตถุดิบนั้นตามกติกาแมป | ลูกค้าไม่สั่งเมนูที่ทำไม่ได้ | ผู้จัดการแมปวัตถุดิบ→เมนู/ตัวเลือกไว้ล่วงหน้า (ดูหมายเหตุ ค.) เมื่อกดหมด 1 ครั้ง เมนูที่ใช้วัตถุดิบนั้นทั้งจานปิดทั้งเมนู ส่วนตัวเลือกเพิ่มที่ใช้เฉพาะตัวเลือกถูกปิดเฉพาะตัวเลือกโดยเมนูหลักยังสั่งได้ ทดสอบด้วยวัตถุดิบ 5 ชนิด ผลตรงกติกาอย่างน้อย 5 จาก 5 |
| US-13 | พนักงานครัว/หน้าร้าน | พนักงานครัว | กด “กลับมามี” เพื่อเปิดเมนูและตัวเลือกที่ปิดไปคืน | ขายต่อได้ทันทีเมื่อเติมวัตถุดิบ | นับจากกด “กลับมามี” จนถึงหน้าลูกค้าเปิดปุ่มสั่งคืน ภายใน 10 วินาทีบน LAN ในร้าน ในอย่างน้อย 9 จาก 10 ครั้ง และเมนู/ตัวเลือกที่กลับมาตรงกับชุดที่ถูกปิดจากวัตถุดิบนั้น |
| US-14 | พนักงานครัว/หน้าร้าน | พนักงานครัว | จัดการรายการในคิวที่ทำไม่ได้เพราะวัตถุดิบหมด (กด “ทำไม่ได้” แล้วส่งให้ลูกค้าเลือกทางออก) | ไม่มีออเดอร์ค้างคิวโดยไม่มีข้อสรุป | รายการที่กด “ทำไม่ได้” ย้ายไปสถานะ “รอลูกค้าตัดสินใจ” และเมื่อลูกค้าเปลี่ยนเมนูหรือคืนรายการ จอครัวอัปเดตรายการใหม่หรือลบรายการภายใน 10 วินาทีบน LAN ทดสอบผ่าน 5 จาก 5 กรณี |
| US-15 | พนักงานครัว/หน้าร้าน | พนักงานหน้าร้าน | เห็นออเดอร์แยกตามโต๊ะและตามสั่งกลับบ้าน พร้อมสถานะจ่ายเงินที่ระบบคำนวณเอง | เสิร์ฟถูกโต๊ะและส่งถุงสั่งกลับบ้านถูกคน | จอหน้าร้านแสดงหมายเลขโต๊ะ (จาก table_id ของ QR) สำหรับออเดอร์หน้าร้าน และหมายเลขรับสั่งกลับบ้านรูปแบบ T-001, T-002, … ที่ระบบสร้างอัตโนมัติ เรียงต่อเนื่อง และรีเซ็ตเป็น T-001 เมื่อเริ่มวันใหม่ (00:00) ครบทุกออเดอร์ 20 จาก 20 ใบของชุดทดสอบ · เกณฑ์ระบบ: สถานะ “จ่ายแล้ว/ยังไม่จ่าย/ค้างจ่าย” บนจอเปลี่ยนตามเหตุการณ์ในระบบ (ออเดอร์ใหม่ = ยังไม่จ่าย · เลือก PromptPay = ค้างจ่าย · กด “รับเงินสด” หรือ “ยืนยันสลิป” = จ่ายแล้ว) ถูกต้อง 20 จาก 20 ใบเมื่อเทียบกับ log เหตุการณ์ · เกณฑ์การยืนยันด้วยมือ: การกดของพนักงานหน้าร้านต้องระบุชื่อผู้ใช้และเวลาไว้ใน log ทุกครั้ง 20 จาก 20 ใบ |
| US-16 | พนักงานครัว/หน้าร้าน | พนักงานหน้าร้าน | เปิดโต๊ะและปิดโต๊ะ โดยปิดแล้ว QR โต๊ะนั้นสั่งต่อจากรอบเดิมไม่ได้ | ปล่อยโต๊ะให้ลูกค้าคนต่อไปโดยบิลไม่ปนกัน | เมื่อกดปิดโต๊ะ การสแกน QR โต๊ะเดิมเริ่มรอบสั่งใหม่ (session ใหม่) และรายการรอบเดิมไม่ปรากฏ ทดสอบ 5 โต๊ะ ผ่านอย่างน้อย 5 จาก 5 |
| US-17 | พนักงานครัว/หน้าร้าน | พนักงานหน้าร้าน | รวมบิลหลายรอบสั่งของโต๊ะเดียวกันเป็นยอดเดียว | เก็บเงินได้ครบในครั้งเดียว | โต๊ะที่สั่ง 3 รอบ ยอดรวมบิลเท่ากับผลรวมของทุกรายการ (ตรวจด้วยเครื่องคิดเลข) ในอย่างน้อย 9 จาก 10 โต๊ะทดสอบ และบิลรวมแสดงรายการแยกตามรอบ |
| US-18 | พนักงานครัว/หน้าร้าน | พนักงานครัวในช่วงเร่งด่วน | เห็นจำนวนออเดอร์ค้างและออเดอร์ที่ค้างนานสุดบนจอครัว | จัดคิวและรู้ว่าต้องเร่งจานไหน | จอครัวแสดงตัวนับออเดอร์ค้าง และออเดอร์ที่ค้างเกิน 15 นาที (นับจากเวลาลูกค้ากดยืนยันสั่ง) เปลี่ยนเป็นสีแดง ทดสอบ 10 ออเดอร์ที่ปล่อยเกินเวลา ผ่านอย่างน้อย 9 จาก 10 |
| US-19 | ผู้จัดการร้าน | ผู้จัดการร้าน | เพิ่ม/แก้/ลบเมนู ราคา รูปเมนู และตัวเลือกเพิ่มต่อเมนู (ชื่อ ราคาเพิ่ม) ผ่านหน้า “จัดการเมนู” | ปรับเมนูตามฤดูกาลและต้นทุนโดยไม่ต้องจ้างคนแก้ระบบ | ขอบเขต: หน้า “จัดการเมนู” เท่านั้น ไม่มีการแมปวัตถุดิบ (แยกไป US-20) · รูปเมนูรับไฟล์ jpg/png ขนาดไม่เกิน 2 MB ต่อรูป · ตัวเลือกเพิ่มระบุชื่อและราคาเพิ่มได้ 0–10 ตัวเลือกต่อเมนู · นับจากกดบันทึก จนถึงเมนูและตัวเลือกเพิ่มใหม่ปรากฏบนหน้าลูกค้าเมื่อรีเฟรช ภายใน 1 นาที · การแก้ราคาไม่เปลี่ยนยอดของออเดอร์ที่สั่งไปแล้ว (ตรวจ 5 ออเดอร์เดิม ผ่าน 5 จาก 5) · ลบเมนูที่มีการแมปวัตถุดิบอยู่ ระบบต้องเตือนและลบการแมปนั้นด้วย |
| US-20 | ผู้จัดการร้าน | ผู้จัดการร้าน | แมปวัตถุดิบกับเมนูและตัวเลือกเพิ่มที่มีอยู่แล้ว ผ่านหน้า “แมปวัตถุดิบ” | ให้ระบบปิดเมนูอัตโนมัติถูกต้องเมื่อวัตถุดิบหมด | ขอบเขต: หน้า “แมปวัตถุดิบ” เท่านั้น ไม่มีการเพิ่ม/แก้เมนูหรือราคา · dependency: เลือกได้เฉพาะเมนูและตัวเลือกเพิ่มที่ถูกสร้างไว้แล้วใน US-19 (ต้องมีเมนูก่อนจึงแมปวัตถุดิบได้ และเมนูที่ยังไม่มีในระบบไม่ปรากฏให้เลือก) · ระบุต่อเมนูว่าใช้วัตถุดิบใด “ทั้งจาน” และต่อตัวเลือกเพิ่มว่าใช้วัตถุดิบใด “เฉพาะตัวเลือก” · บันทึกแล้วมีผลกับกฎปิด/เปิดเมนูอัตโนมัติ (US-14) และแสดงบนหน้าลูกค้าเมื่อรีเฟรชภายใน 1 นาที ทดสอบ 5 เมนู ผ่าน 5 จาก 5 (ดูหมายเหตุ ค.) |
| US-21 | ผู้จัดการร้าน | ผู้จัดการร้าน | ตั้งช่วงเวลาเร่งด่วนและเพดานจำนวนออเดอร์ต่อ 15 นาที | ครัวไม่ล้นและลูกค้าในร้านได้อาหารทัน | ตั้งเวลาเริ่ม–สิ้นสุดช่วงเร่งด่วน (เช่น 11:30–13:30) และเพดาน N ออเดอร์ต่อหน้าต่างเวลา 15 นาทีที่นับจากนาทีที่ 00/15/30/45 เมื่อจำนวนออเดอร์ที่ยืนยันในหน้าต่างนั้นถึง N ลูกค้าใหม่เห็นข้อความ “ครัวเต็ม รอประมาณ X นาที” ก่อนยืนยัน ทดสอบด้วย N=5 ผ่าน 3 จาก 3 รอบ |
| US-22 | ผู้จัดการร้าน | ผู้จัดการร้าน | เปิด/ปิดรับสั่งกลับบ้านชั่วคราวด้วยสวิตช์เดียว | ลดภาระครัวช่วงเร่งด่วนโดยไม่ปิดหน้าร้าน | นับจากผู้จัดการกดปิดรับสั่งกลับบ้าน จนถึงหน้าลูกค้าซ่อนโหมด “สั่งกลับบ้าน” เมื่อโหลดหน้าใหม่ ภายใน 10 วินาทีบน LAN ในร้าน ในอย่างน้อย 9 จาก 10 ครั้ง และการสั่งหน้าร้านผ่าน QR ยังทำได้ตามปกติ |
| US-23 | ผู้จัดการร้าน | ผู้จัดการร้าน | ดูรายงานยอดขายรายวัน แยกตามเมนู ช่องทาง (หน้าร้าน/สั่งกลับบ้าน) และช่วงเวลา พร้อมส่งออก CSV | วางแผนสั่งวัตถุดิบและกำลังคน | เลือกช่วงวันที่แล้วรายงานแสดงภายใน 5 วินาที (นับจากกด “ดูรายงาน” จนตารางแสดงบนเครื่อง Ubuntu ในร้าน) ยอดรวมตรงกับผลรวมออเดอร์สถานะ “จ่ายแล้ว” ที่นับมือจาก 20 ใบของชุดทดสอบ (คลาดเคลื่อน 0 บาท) และดาวน์โหลด CSV เปิดด้วย LibreOffice ได้ |
| US-24 | ผู้จัดการร้าน | ผู้จัดการร้าน | ดูประวัติวัตถุดิบ/เมนูที่ถูกกดหมดพร้อมเวลาและความถี่ | รู้ว่าวัตถุดิบไหนควรสั่งเพิ่มหรือปรับเมนู | เมื่อครัวกด “วัตถุดิบหมด” ระบบบันทึกชื่อวัตถุดิบ เวลา และผู้กด และหน้าประวัติแสดงจำนวนครั้งต่อสัปดาห์ ตรวจสอบกับการกดทดสอบ 10 ครั้ง พบรายการอย่างน้อย 9 จาก 10 |
| US-25 | ผู้จัดการร้าน | ผู้จัดการร้าน | จัดการบัญชีพนักงานและสิทธิ์ (ครัว/หน้าร้าน/ผู้จัดการ) ด้วยชื่อผู้ใช้และ PIN โดยไม่ต้องใช้อีเมล | ข้อมูลยอดขายและการแก้เมนูเข้าถึงได้เฉพาะคนที่ควร | สร้างบัญชีด้วยชื่อผู้ใช้ (ตัวอักษร/ตัวเลข 3–20 ตัว) และ PIN ตัวเลข 4–6 หลัก เข้าสู่ระบบด้วยชื่อผู้ใช้+PIN ใส่ PIN ผิด 5 ครั้งติดถูกล็อก 5 นาที และบัญชีสิทธิ์ครัว/หน้าร้านเปิด URL หน้ารายงานและหน้าจัดการเมนูแล้วถูกปฏิเสธ ทดสอบ 3 บัญชี × 2 หน้า ผ่าน 6 จาก 6 |
| US-26 | ผู้จัดการร้าน | ผู้จัดการร้านที่งบต่ำ | ติดตั้งระบบบนเครื่อง Ubuntu เครื่องเดียวในร้าน ใช้งานผ่าน Wi‑Fi ร้านได้แม้เน็ตภายนอกหลุด | ไม่ต้องจ่ายค่าคลาวด์รายเดือนและร้านไม่หยุดเมื่อเน็ตล่ม | ติดตั้งบน Ubuntu ด้วยสคริปต์เดียว เสร็จภายใน 30 นาที (นับจากรันสคริปต์จนเปิดหน้าเมนูจากมือถือในร้านได้) เก็บข้อมูลบนเครื่องในร้าน และเมื่อถอดสายอินเทอร์เน็ตภายนอก ยังสั่ง/เปลี่ยนสถานะ/ปิดโต๊ะได้ครบ 20 ใบของชุดทดสอบ (ยกเว้นการตรวจสอบยอดโอน PromptPay ซึ่งพนักงานยืนยันด้วยตา) |

## ไฟล์ที่สร้างและการรักษาหลักฐาน

สร้างเฉพาะ [ui-run-report.md](ui-run-report.md) และ [traceability-after-ui.csv](traceability-after-ui.csv) ในโฟลเดอร์ขั้นนี้ ตรวจว่าไม่มี Output เดิมก่อนสร้างและใช้การเปิดไฟล์แบบไม่เขียนทับ หากมี Output อยู่แล้วต้องหยุดและขอ path รุ่นใหม่ในบันทึกก่อนดำเนินการ ไม่สร้างไฟล์อื่นหรือแก้ผลเก่า/Input; ตรวจ SHA-256 ของ Input ทั้งแปดไฟล์ก่อนและหลังสร้างให้ตรงเดิม
