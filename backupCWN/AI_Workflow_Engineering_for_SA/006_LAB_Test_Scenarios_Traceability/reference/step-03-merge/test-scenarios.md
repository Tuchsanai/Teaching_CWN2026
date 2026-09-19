# Test Scenarios รวมสามบทบาท

ผลออกแบบขั้นต่ำ **26/26 US**, 114 scenario เชิงออกแบบ (customer 35, kitchen-front 42, manager 37); ทุก US มีอย่างน้อยสอง scenario รวมสำเร็จและผิดพลาด/ข้อยกเว้น. ผลผู้ตรวจที่เลือกยังเป็น **GAPS / STOP_WITH_GAPS**; ไม่ประกาศ COVERED. COVERED หมายถึงเอกสารออกแบบครบ ไม่ใช่ PASS. Actual และหลักฐานผลรัน: **ไม่มีข้อมูล**.

ใช้ [selected-set.md](../step-02-coverage/selected-set.md), [manifest](../step-02-coverage/fix-1/scenario-set-round-1.json), [Coverage รอบที่เลือก](../step-02-coverage/round-2/coverage-round-2.md) และ [ผลแก้](../step-02-coverage/fix-1/coverage-fixes-round-1.md). ค่าภายใน manifest รวมข้อความ reference/... ที่คัดมา relative จากราก LAB ../.. เท่านั้น. Path อื่นปรับให้ relative จากโฟลเดอร์นี้ และใช้ได้เมื่อวาง Output ทั้งสามใน ../final/ ซึ่งอยู่ระดับเดียวกัน.

Authority ข้อความ US/AC คือ [case-study-source.md](../../../docs/case-study-source.md); mapping ใช้ [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md) และ [flow-v2.md](../step-00-input/flow-v2.md); ตรวจ [ui-mockup-v2.html](../step-00-input/ui-mockup-v2.html) แบบ static เท่านั้น. ไม่ถือเสียงส่วนใหญ่แทนหลักฐาน. ข้อมูลและบัญชีทั้งหมดเป็น fixture จำลองสาธารณะ; สมมติฐานไม่ใช่ข้อกำหนดร้าน.

## วิธีอ่านสถานะและต้นฉบับ

[traceability.csv](traceability.csv) ใช้ auto → NOT_RUN, manual → MANUAL_PENDING, mock-not-testable → MOCK_NOT_TESTABLE. ต้นฉบับด้านล่างคง Status/จำนวนรุ่นเดิมเพื่อรักษาหลักฐาน จึงพบ NOT_TESTABLE หรือ manual ที่เป็น NOT_RUN ได้; เป็นประวัติ ไม่ใช่สถานะการรันใหม่. ไม่แก้ automation, AC, ID, ขั้นตอน, expected หรือข้อค้าง. BLOCKED/MISSING อยู่ในเหตุผลและ [traceability-notes.md](traceability-notes.md); NOT_RUN ไม่รับรองความพร้อม fixture.

CSV แจกแจงขอบเขต mapping ระดับ US ตามทะเบียน; จำนวนแถวไม่ใช่จำนวน scenario/assertions และไม่รับรองว่าแต่ละ Flow เรียกทุก Screen. ดูความหมายการแตกแถวใน notes. NFR คงในบล็อก/ทะเบียน ไม่ยัดลงช่อง FR. ขั้น 6.5 จึงผูกผล UI จาก JSON โดย TestID ของ fixture; ไม่กระจายผลผ่านไปทุก scenario ที่เชื่อมกัน.

## ดัชนีครบ 26 US

| US | บทบาท | สำเร็จ | ผิดพลาด/ข้อยกเว้น | จำนวนออกแบบ | Mapping ที่ค้าง |
|---|---|---|---|---|---|
| US-01 | customer | [TS-US-01-1](#design-ts-us-01-1); [TS-US-01-2](#design-ts-us-01-2) | [TS-US-01-3](#design-ts-us-01-3) | 3 | มีทะเบียนระดับ US; ไม่ยืนยัน runtime |
| US-02 | customer | [TS-US-02-1](#design-ts-us-02-1); [TS-US-02-2](#design-ts-us-02-2) | [TS-US-02-3](#design-ts-us-02-3) | 3 | มีทะเบียนระดับ US; ไม่ยืนยัน runtime |
| US-03 | customer | [TS-US-03-1](#design-ts-us-03-1) | [TS-US-03-2](#design-ts-us-03-2); [TS-US-03-3](#design-ts-us-03-3) | 3 | มีทะเบียนระดับ US; ไม่ยืนยัน runtime |
| US-04 | customer | [TS-US-04-1](#design-ts-us-04-1); [TS-US-04-2](#design-ts-us-04-2) | [TS-US-04-3](#design-ts-us-04-3); [TS-US-04-4](#design-ts-us-04-4) | 4 | มีทะเบียนระดับ US; ไม่ยืนยัน runtime |
| US-05 | customer | [TS-US-05-1](#design-ts-us-05-1); [TS-US-05-2](#design-ts-us-05-2) | [TS-US-05-3](#design-ts-us-05-3); [TS-US-05-4](#design-ts-us-05-4) | 4 | มีทะเบียนระดับ US; ไม่ยืนยัน runtime |
| US-06 | customer | [TS-US-06-1](#design-ts-us-06-1); [TS-US-06-3](#design-ts-us-06-3) | [TS-US-06-2](#design-ts-us-06-2) | 3 | มีทะเบียนระดับ US; ไม่ยืนยัน runtime |
| US-07 | customer | [TS-US-07-1](#design-ts-us-07-1); [TS-US-07-2](#design-ts-us-07-2) | [TS-US-07-3](#design-ts-us-07-3); [TS-US-07-4](#design-ts-us-07-4) | 4 | มีทะเบียนระดับ US; ไม่ยืนยัน runtime |
| US-08 | customer | [TS-US-08-1](#design-ts-us-08-1); [TS-US-08-2](#design-ts-us-08-2); [TS-US-08-5](#design-ts-us-08-5) | [TS-US-08-3](#design-ts-us-08-3); [TS-US-08-4](#design-ts-us-08-4) | 5 | มีทะเบียนระดับ US; ไม่ยืนยัน runtime |
| US-09 | customer | [TS-US-09-1](#design-ts-us-09-1); [TS-US-09-6](#design-ts-us-09-6) | [TS-US-09-3](#design-ts-us-09-3); [TS-US-09-4](#design-ts-us-09-4); [TS-US-09-5](#design-ts-us-09-5) | 6 | มีทะเบียนระดับ US; ไม่ยืนยัน runtime |
| US-10 | kitchen-front | [TS-US-10-1](#design-ts-us-10-1); [TS-US-10-3](#design-ts-us-10-3) | [TS-US-10-4](#design-ts-us-10-4); [TS-US-10-5](#design-ts-us-10-5) | 5 | มีทะเบียนระดับ US; ไม่ยืนยัน runtime |
| US-11 | kitchen-front | [TS-US-11-1](#design-ts-us-11-1); [TS-US-11-4](#design-ts-us-11-4) | [TS-US-11-3](#design-ts-us-11-3); [TS-US-11-5](#design-ts-us-11-5) | 5 | มีทะเบียนระดับ US; ไม่ยืนยัน runtime |
| US-12 | kitchen-front | [TS-US-12-1](#design-ts-us-12-1); [TS-US-12-3](#design-ts-us-12-3) | [TS-US-12-4](#design-ts-us-12-4); [TS-US-12-5](#design-ts-us-12-5) | 5 | มีทะเบียนระดับ US; ไม่ยืนยัน runtime |
| US-13 | kitchen-front | [TS-US-13-1](#design-ts-us-13-1); [TS-US-13-3](#design-ts-us-13-3) | [TS-US-13-4](#design-ts-us-13-4) | 4 | มีทะเบียนระดับ US; ไม่ยืนยัน runtime |
| US-14 | kitchen-front | [TS-US-14-1](#design-ts-us-14-1); [TS-US-14-5](#design-ts-us-14-5) | [TS-US-14-4](#design-ts-us-14-4); [TS-US-14-6](#design-ts-us-14-6) | 6 | มีทะเบียนระดับ US; ไม่ยืนยัน runtime |
| US-15 | kitchen-front | [TS-US-15-1](#design-ts-us-15-1); [TS-US-15-3](#design-ts-us-15-3); [TS-US-15-6](#design-ts-us-15-6) | [TS-US-15-5](#design-ts-us-15-5); [TS-US-15-7](#design-ts-us-15-7) | 7 | มีทะเบียนระดับ US; ไม่ยืนยัน runtime |
| US-16 | kitchen-front | [TS-US-16-1](#design-ts-us-16-1); [TS-US-16-3](#design-ts-us-16-3) | [TS-US-16-2](#design-ts-us-16-2); [TS-US-16-4](#design-ts-us-16-4) | 4 | มีทะเบียนระดับ US; ไม่ยืนยัน runtime |
| US-17 | kitchen-front | [TS-US-17-1](#design-ts-us-17-1) | [TS-US-17-2](#design-ts-us-17-2); [TS-US-17-3](#design-ts-us-17-3) | 3 | FR/Flow/Screen MISSING |
| US-18 | kitchen-front | [TS-US-18-1](#design-ts-us-18-1) | [TS-US-18-2](#design-ts-us-18-2); [TS-US-18-3](#design-ts-us-18-3) | 3 | FR/Flow/Screen MISSING |
| US-19 | manager | [TS-US-19-1](#design-ts-us-19-1); [TS-US-19-2](#design-ts-us-19-2); [TS-US-19-6](#design-ts-us-19-6); [TS-US-19-8](#design-ts-us-19-8) | [TS-US-19-3](#design-ts-us-19-3); [TS-US-19-5](#design-ts-us-19-5); [TS-US-19-7](#design-ts-us-19-7) | 8 | มีทะเบียนระดับ US; ไม่ยืนยัน runtime |
| US-20 | manager | [TS-US-20-1](#design-ts-us-20-1); [TS-US-20-4](#design-ts-us-20-4) | [TS-US-20-3](#design-ts-us-20-3) | 4 | มีทะเบียนระดับ US; ไม่ยืนยัน runtime |
| US-21 | manager | [TS-US-21-1](#design-ts-us-21-1); [TS-US-21-6](#design-ts-us-21-6) | [TS-US-21-2](#design-ts-us-21-2); [TS-US-21-4](#design-ts-us-21-4); [TS-US-21-5](#design-ts-us-21-5) | 6 | มีทะเบียนระดับ US; ไม่ยืนยัน runtime |
| US-22 | manager | [TS-US-22-1](#design-ts-us-22-1) | [TS-US-22-2](#design-ts-us-22-2); [TS-US-22-4](#design-ts-us-22-4) | 4 | FR/Flow/Screen MISSING |
| US-23 | manager | [TS-US-23-1](#design-ts-us-23-1) | [TS-US-23-3](#design-ts-us-23-3); [TS-US-23-4](#design-ts-us-23-4) | 4 | FR/Flow/Screen MISSING |
| US-24 | manager | [TS-US-24-1](#design-ts-us-24-1) | [TS-US-24-2](#design-ts-us-24-2); [TS-US-24-3](#design-ts-us-24-3) | 3 | FR/Flow/Screen MISSING |
| US-25 | manager | [TS-US-25-1](#design-ts-us-25-1); [TS-US-25-5](#design-ts-us-25-5) | [TS-US-25-2](#design-ts-us-25-2); [TS-US-25-3](#design-ts-us-25-3); [TS-US-25-4](#design-ts-us-25-4); [TS-US-25-6](#design-ts-us-25-6) | 6 | มีทะเบียนระดับ US; ไม่ยืนยัน runtime |
| US-26 | manager | [TS-US-26-1](#design-ts-us-26-1) | [TS-US-26-2](#design-ts-us-26-2) | 2 | Screen MISSING — งานติดตั้ง/เครือข่าย |

## เชื่อม fixture สงวน 14 ID / 13 US

อ้าง [ui-scenarios.json](../../input/ui-scenarios.json) ตาม ID เดิม; ไม่สร้าง steps/selector ทดแทน. ทั้งหมดเป็น auto / NOT_RUN และ smoke บาง clause เท่านั้น ไม่ถือว่าครบ AC. TS-US-08-102 เชื่อมวิธีเงินสดใน TS-US-08-1 และยืนยันสถานะใน TS-US-15-1 โดยไม่ย้ายเจ้าของหรือแก้เนื้อหาเดิม.

| Fixture | US | เชื่อม scenario เชิงออกแบบ | ขอบเขต/ข้อค้าง | Status เริ่ม |
|---|---|---|---|---|
| TS-US-01-101 | US-01 | [TS-US-01-1](#design-ts-us-01-1); [TS-US-01-2](#design-ts-us-01-2) | เพียง menu-list; ไม่ assert รายการแรก/QR/3 วินาที/20 ครั้ง | NOT_RUN |
| TS-US-02-101 | US-02 | [TS-US-02-1](#design-ts-us-02-1); [TS-US-02-2](#design-ts-us-02-2) | ข้อความ 02 ใน front-orders ใบเดียว; ไม่ตรวจ URL/20 โต๊ะ/การผูกอัตโนมัติ | NOT_RUN |
| TS-US-03-101 | US-03 | [TS-US-03-1](#design-ts-us-03-1); [TS-US-03-2](#design-ts-us-03-2) | กลับบ้านใบเดียวและ 12:30; ไม่ครบช่วงจบ/ทุก slot/ขอบ 20 นาที/10 ใบ | NOT_RUN |
| TS-US-04-101 | US-04 | [TS-US-04-1](#design-ts-us-04-1); [TS-US-04-2](#design-ts-us-04-2) | item-total มี 60 และใบครัวมีไข่; ไม่ครบ configuration/ยอดตะกร้า/20 ใบ | NOT_RUN |
| TS-US-05-101 | US-05 | [TS-US-05-1](#design-ts-us-05-1); [TS-US-05-2](#design-ts-us-05-2) | กำลังทำในแท็บเดียวหลังสลับบทบาท; ไม่พิสูจน์จอเปิดค้าง/ไม่รีเฟรช/5 วินาที LAN/20 ครั้ง | NOT_RUN |
| TS-US-06-101 | US-06 | [TS-US-06-1](#design-ts-us-06-1); [TS-US-06-2](#design-ts-us-06-2); [TS-US-06-3](#design-ts-us-06-3) | order-message มีหมด; ยังขาดป้ายพร้อม disabled/no-new-order/10 ครั้ง LAN | NOT_RUN |
| TS-US-08-101 | US-08 | [TS-US-08-2](#design-ts-us-08-2); [TS-US-08-4](#design-ts-us-08-4); [TS-US-08-5](#design-ts-us-08-5) | +10 นาทีแล้วมีข้อความเงินสด; ไม่ใช่เกิน 10 นาที/ไม่มีปลายทางยืนยัน/ไม่ครบสามกรณี | NOT_RUN |
| TS-US-08-102 | US-08 | [TS-US-08-1](#design-ts-us-08-1); [TS-US-15-1](#design-ts-us-15-1) | เงินสดยังไม่จ่ายจนหน้าร้านรับเงิน; เชื่อมวิธีเงินสด US-08 และยืนยันสถานะ US-15 ข้ามบทบาท; ไม่ครบ 20 ใบ/เงินจริง | NOT_RUN |
| TS-US-09-101 | US-09 | [TS-US-09-1](#design-ts-us-09-1); [TS-US-09-6](#design-ts-us-09-6) | F01: BLOCKED — payment-summary-total MISSING; ไม่ตรวจเปลี่ยนเมนู/LAN/5 กรณี | NOT_RUN |
| TS-US-11-101 | US-11 | [TS-US-11-1](#design-ts-us-11-1); [TS-US-11-2](#design-ts-us-11-2); [TS-US-11-4](#design-ts-us-11-4) | หนึ่งใบ/หนึ่งแตะแล้ว front-orders มีกำลังทำ; ไม่ตรวจเสร็จแล้ว/5 วินาที/18 จาก 20 | NOT_RUN |
| TS-US-12-101 | US-12 | [TS-US-12-2](#design-ts-us-12-2); [TS-US-12-3](#design-ts-us-12-3) | ปิด egg แล้วส่ง m01 ได้; ไม่มี assertion extra-egg disabled/วัตถุดิบ 5 ชนิด | NOT_RUN |
| TS-US-14-101 | US-14 | [TS-US-14-1](#design-ts-us-14-1); [TS-US-14-2](#design-ts-us-14-2); [TS-US-14-3](#design-ts-us-14-3); [TS-US-14-5](#design-ts-us-14-5) | ตรวจเพียงรอลูกค้าตัดสินใจ; ยังไม่ตรวจผลเปลี่ยน/คืน/10 วินาที LAN/5 กรณี | NOT_RUN |
| TS-US-21-101 | US-21 | [TS-US-21-1](#design-ts-us-21-1); [TS-US-21-6](#design-ts-us-21-6) | F02: BLOCKED — rush-start/rush-end MISSING และขาด nav-capacity; หนึ่งรอบไม่แทน 3 จาก 3 | NOT_RUN |
| TS-US-25-101 | US-25 | [TS-US-25-3](#design-ts-us-25-3); [TS-US-25-5](#design-ts-us-25-5) | PIN ผิดหนึ่งครั้ง; ไม่แทน 5 ครั้ง/5 นาที/3 บัญชี × 2 หน้า/ความปลอดภัยฝั่ง server | NOT_RUN |


---

## ต้นฉบับฉบับเต็ม — customer

Source: [scenarios-customer-round-1.md](../step-02-coverage/fix-1/scenarios-customer-round-1.md). คัดทั้งไฟล์; ปรับเฉพาะฐาน path/ลิงก์และเพิ่มจุดนำทางก่อนหัวข้อ.

# Scenarios บทบาทลูกค้า — US-01 ถึง US-09

## บันทึกรอบแก้ coverage — ROUND 1

คัดส่วนเดิมจาก [scenarios-customer.md](../step-01-fanout/customer/scenarios-customer.md) แล้วเพิ่มเฉพาะ TS-US-04-4, TS-US-05-4, TS-US-07-4 ตาม D01, D02, D03; รวม 35 TestID. นิยามเดิม 32 รายการคงข้อความทุกบล็อก; ปรับเฉพาะดัชนี/ข้อมูลรุ่น/ฐาน path ที่จำเป็นนอกบล็อก. รายการใหม่ทั้งหมดใช้ mock-not-testable และ Status MOCK_NOT_TESTABLE ตาม template; Status NOT_TESTABLE ในรายการเดิมเก็บตามต้นทาง. ข้อความจำนวนและสถานะในหัวข้อบันทึกต้นทางเป็นข้อมูลก่อนแก้

manifest ต้นทาง: [scenario-set-round-0.json](../step-00-input/scenario-set-round-0.json) resolve ค่าจากโฟลเดอร์ manifest; manifest รอบนี้: [scenario-set-round-1.json](../step-02-coverage/fix-1/scenario-set-round-1.json) resolve ทุกค่าจากราก LAB ../.. ตาม P01. รายละเอียดการแก้และ regression อยู่ที่ [coverage-fixes-round-1.md](../step-02-coverage/fix-1/coverage-fixes-round-1.md). ส่งผู้ตรวจรอบเดียวกัน ยังไม่ประกาศ COVERED; Actual/หลักฐานไม่มีข้อมูล


เจ้าของทุก scenario: **customer**. ออกแบบจากข้อความ US/AC ก่อนจับคู่ UI; การใช้ครัว หน้าร้าน หรือผู้จัดการเป็น setup/ตรวจปลายทางไม่เปลี่ยนเจ้าของ US. เอกสารนี้เป็นการออกแบบและตรวจไฟล์เท่านั้น ยังไม่ได้รัน Mock-up หรือระบบจริง

สถานะเริ่มใช้ **NOT_RUN** สำหรับ auto/manual และ **NOT_TESTABLE** สำหรับ mock-not-testable ตามคำสั่งงาน ซึ่งมีลำดับเหนือค่าตัวอย่าง MANUAL_PENDING/MOCK_NOT_TESTABLE ใน template. ข้อมูลธุรกิจหรือเครื่องมือขาดใช้ BLOCKED ในเหตุผล/ข้อค้าง; Actual result และหลักฐานผลรันทุกรายการเป็น ไม่มีข้อมูล. ไม่ยกผลของไฟล์อ้างอิงเป็นผลรันใหม่

## แหล่งอ้างอิงและขอบเขต

Path ในเอกสารนี้ relative จากโฟลเดอร์นี้; manifest ต้นทาง resolve จาก ../step-00-input ตามข้อแก้ P01; manifest รอบแก้ใหม่ resolve จากราก LAB ที่ ../..; ไม่แก้ manifest ต้นทาง

| แหล่ง | ใช้เพื่อ |
|---|---|
| [case-study-source.md](../../../docs/case-study-source.md) | US/AC เต็มตรงตัวเป็น authority |
| [data-issues.md](../../../docs/data-issues.md) | DI-01–DI-09 และ A-01–A-06; ไม่คัดประวัติหรือข้อมูลสภาพแวดล้อม |
| [input-check.md](../step-00-input/input-check.md) | ความครบ Input, static selector mapping และข้อจำกัด |
| [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md) | FR/NFR และคำถาม Q; อ้างหัวข้อ FR, Traceability และคำถามรอยืนยัน |
| [flow-v2.md](../step-00-input/flow-v2.md) | หัวข้อ Coverage, ทะเบียนส่วนเดิมที่ใช้ซ้ำ, MRG-31/32/33 |
| [ui-mockup-v2.html](../step-00-input/ui-mockup-v2.html) | ตรวจ seed, markup, template และ handler แบบ static เท่านั้น |
| [scenario-template.md](../../input/scenario-template.md) | ช่องข้อมูลหนึ่งชุดต่อ TestID |
| [coverage-criteria.md](../../input/coverage-criteria.md) | ความครบต่อ US/clause/ทางเลือกและข้อค้าง |
| [ui-scenarios.json](../../input/ui-scenarios.json) | อ้าง ID fixture ที่สงวน n≥101 ไม่สร้างหรือเปลี่ยน fixture |
| [ui-v2-test-contract.md](../../input/ui-v2-test-contract.md) | สมมติฐาน suite เพิ่มและชื่อ selector ที่ต้องเทียบ HTML |
| [ui-contract.md](../../../004_LAB_Conditional_Graph_UI_Mockup/input/ui-contract.md) | สัญญาเดิมสำหรับบทบาท/seed/reset/selector |
| [ui-contract-v2.md](../step-00-input/ui-contract-v2.md) | selector ใหม่, scope order/item, ยอดเดิม/ยอดปรับ |
| [test-outline-v2.md](../step-00-input/test-outline-v2.md) | แนวแยกจุดวัดและชุดห้ากรณี; ไม่รับผลหรือข้อความประวัติการทำงานมาเป็นหลักฐาน |

ตาราง coverage ในไฟล์นี้มี 9 แถวเฉพาะเจ้าของ customer; เกณฑ์รวม 26 แถว/อย่างน้อย 52 scenario เป็นงานรวมทุกบทบาท ยังไม่รับรองจากไฟล์นี้. คง ID หลังเผยแพร่; n ของรายการออกแบบต่ำกว่า 101 และไม่ซ้ำภายใน US. การรันในอนาคตต้องเก็บผลในรุ่นใหม่ ไม่เขียนทับหลักฐานนี้

## ข้อความ US และ AC ต้นฉบับเต็ม ก่อนแยก assertions

ตารางนี้คัดทั้งแถวจาก case-study-source.md โดยไม่แก้คำ ตัวเลข หน่วย สูตร จำนวนตัวอย่าง หรือหมายเหตุ; AC เต็มยังคัดซ้ำในแต่ละ scenario ตาม template

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

## แยก functional assertions กับ NFR และจำนวนตัวอย่าง

รหัส F/N ต่อไปนี้เป็นป้าย clause ในเอกสารนี้เท่านั้น ไม่ใช่ FR/NFR ใหม่. สัดส่วนความตรงและกฎเวลาในธุรกิจยังเก็บใน FR แม้ไม่ได้จัดหมวด NFR แยก; AC เต็มด้านบนมีอำนาจเหนือคำย่อ

| US | Functional assertions | NFR/เกณฑ์เวลาและประชากร | Scenario เชิงออกแบบ |
|---|---|---|---|
| US-01 | F01 เข้าถึงเมนูจาก QR โดยไม่ login (ข้อความ US); ปลายทางรายการแรก | NFR-01: กล้องอ่าน QR สำเร็จ→รายการแรก ≤3 วินาที Wi‑Fi ร้าน ≥18/20 ครั้ง | TS-US-01-1, TS-US-01-2, TS-US-01-3 |
| US-02 | F02 URL มี table_id เช่น /t/07; ผูกโดยไม่กรอกโต๊ะ; หน้าร้านตรงป้าย | ไม่มี NFR แยก; 20 โต๊ะ อย่างน้อย 19/20 ใบตรงป้าย; URL แต่ละโต๊ะต้องมี table_id | TS-US-02-1, TS-US-02-2, TS-US-02-3 |
| US-03 | F03a ช่วงรับละ 15 นาที เริ่มอย่างน้อย 20 นาทีหลังเวลาสั่ง; F03b ป้ายสั่งกลับบ้านและช่วงรับตรงครัว | ไม่มี NFR แยก; กฎ 15/20 นาทีเป็นธุรกิจ ไม่ใช่ latency; ชุด 10 ใบต้องครบ 10/10 | TS-US-03-1, TS-US-03-2, TS-US-03-3 |
| US-04 | F04a ตัวเลือกครบตามที่ตั้ง; F04b รวมราคาเพิ่มก่อนยืนยัน; F04c ตัวเลือกตรงใบครัว | ไม่มี NFR แยก; F04c ≥19/20 ใบ; F04a/F04b ต้องตรวจครบแยก ไม่ใช้สัดส่วนลดความครบ | TS-US-04-1, TS-US-04-2, TS-US-04-3, TS-US-04-4 |
| US-05 | F05 ลูกค้าเห็นสถานะใหม่โดยไม่ refresh; คงสามชื่อตาม US | NFR-02: ครัวกด→ลูกค้าแสดงสถานะ ≤5 วินาที LAN ≥18/20 ครั้ง | TS-US-05-1, TS-US-05-2, TS-US-05-3, TS-US-05-4 |
| US-06 | F06a มีทั้งป้ายหมดและปุ่มปิด; F06b สั่งเมนูปิดต้องปฏิเสธพร้อมข้อความ | NFR-03: ครัวกดหมด→มีผลทั้งสอง ≤10 วินาที LAN ≥9/10 ครั้ง; การปฏิเสธตรวจแยก | TS-US-06-1, TS-US-06-2, TS-US-06-3 |
| US-07 | F07a ETA ทุกออเดอร์ก่อนยืนยันตามสูตรเต็ม; F07b log เริ่มยืนยันสั่งถึงครัวพร้อมเสิร์ฟ | NFR-04: 7 วันล่าสุดในสูตร; ช่วง 11:30–13:00/17:30–19:30 ของ 1 วัน; คลาดเคลื่อน ≤10 นาที ≥80%; UI ยังไม่รองรับ | TS-US-07-1, TS-US-07-2, TS-US-07-3, TS-US-07-4 |
| US-08 | F08a ยอดลูกค้า/หน้าร้าน; F08b เงินสด/PromptPay ทุกใบ; F08c ค้างจ่ายจนยืนยัน; F08d ปิดหรือ timeout แจ้งเงินสด; F08e รับเงินสด/ยืนยันสลิป→จ่ายแล้ว | NFR-17 อ้างทางออกชำระ; ยอด ≥19/20 ใบ, สองวิธีทุกใบ; timeout 10 นาทีเป็นกฎธุรกิจ; 3 กรณีต้อง 3/3 | TS-US-08-1, TS-US-08-2, TS-US-08-3, TS-US-08-4, TS-US-08-5; ทางเลือกเงินสดปกติเชื่อม fixture TS-US-08-102 |
| US-09 | F09a แจ้งพร้อมเปลี่ยนเมนู/คืนรายการ; F09b ลดตามรายการคืน | NFR-V2-09: ครัวกดทำไม่ได้→ลูกค้าแจ้งพร้อมสองปุ่ม ≤10 วินาที LAN; ชุด 5/5 ทั้งทางเลือกตามแผน | TS-US-09-1, TS-US-09-2, TS-US-09-3, TS-US-09-4, TS-US-09-5, TS-US-09-6 |

## Precondition และ scope ที่ใช้ซ้ำ

- **R0:** เปิด `../step-00-input/ui-mockup-v2.html` ใน browser context ใหม่ แล้วกด `btn-reset`; seed วันที่ `2026-01-01T12:00:00+07:00`, ลูกค้าโต๊ะ 01/dine-in, ยังไม่เปิดเมนู, ไม่ login, คิว/ตะกร้า/การจ่าย/การปรับว่าง, stock มี, PromptPay เปิด. แต่ละ scenario เริ่มใหม่ เว้นขั้นที่ระบุคงหลายออเดอร์. เวลา/เขตเวลา/ราคา/จำนวนจานเป็น fixture ไม่ใช่นโยบายร้าน
- **O (สร้างออเดอร์):** `role-customer` → `table-select` ตามข้อมูล → `btn-open-menu` → `menu-item-m01` หรือ `menu-item-m02` → เลือก `option-extra-egg` ถ้าระบุ → `btn-add-item` ต่อจาน → อ่าน `cart-total` ก่อน `btn-submit-order` → จด `order-id` จริงหลังส่ง. ถ้าเปิด session แล้วและต้องเพิ่มใบ ให้คง session และเริ่มที่เลือกเมนู. จานละ 1 ตาม fixture; ไม่กำหนด API เพิ่มจำนวนที่ไม่มี
- **K0/F0/M0:** เข้า `role-staff` สำหรับครัว/หน้าร้าน หรือ `role-manager` สำหรับผู้จัดการ ทุกครั้งเลือก `staff-user` เป็น `demokitchen`/`demofront`/`demomanager` ตามบทบาท กรอก `staff-pin=0000` แล้ว `btn-login`; เข้า `nav-kitchen`/`nav-front`/`nav-menu-admin` เมื่อเกี่ยวข้อง. ทั้งหมดเป็นบัญชีทดสอบสาธารณะตามสัญญา; ไม่มีบัญชีจริง. กลับลูกค้าใช้ `role-customer`; ไม่ reset หรือ reload เพื่ออ้างว่าสถานะอัปเดตเอง
- **G:** ส่วนกลางระดับหน้า: `btn-reset`, `role-customer`, `role-staff`, `role-manager`, `sim-clock`, `btn-advance-10m`; ฟอร์ม login อยู่ระดับหน้า ไม่อยู่ใน screen-manager ก่อน login
- **C:** `[data-testid="screen-customer"]`; ใช้ selector ลูกค้าภายใน C; `menu-item-m01/m02` อยู่ใน `menu-list`; `item-total`/`option-extra-egg` อยู่รายละเอียดจานที่เลือก; `order-id`/`customer-order-status`/`customer-adjusted-total`/`payment-status` คือออเดอร์ล่าสุด ต้องตรวจ ID ก่อนอ่านทุกครั้ง
- **K(order ID):** `[data-testid="kitchen-queue"] [data-testid="kitchen-order"][data-order-id="<ID ที่จด>"]` ภายใน `screen-staff`; `btn-status-next` scope K; ทำไม่ได้ต่อจานใช้ `K [data-testid="btn-item-unavailable"][data-item-id="<item ID>"]`
- **F(order ID):** `[data-testid="front-orders"] [data-testid="front-order"][data-order-id="<ID ที่จด>"]` ภายใน `screen-staff`; `front-total`, `front-adjusted-total`, `front-payment-status`, `btn-confirm-slip`, `btn-receive-cash` ต้องอยู่ F ของใบเป้าหมาย
- **R(order ID):** `C [data-testid="customer-item-resolutions"] [data-testid="customer-resolution-order"][data-order-id="<ID ที่จด>"]`; **I(item ID):** `R [data-testid="item-resolution"][data-item-id="<item ID>"]`; ปุ่มเปลี่ยน/คืนและ replacement controls อยู่ I. `resolution-message` อยู่ใน customer-item-resolutions, `resolution-order-total` อยู่ R. จด item ID จาก `K li[data-item-id]` ของชื่อจาน/ตัวเลือกที่ตั้งไว้; ถ้าพบหลายรายการเหมือนกันให้ตั้ง fixture แยกก่อน ห้ามเลือกตัวแรกโดยเดา
- **M:** `screen-manager` หลัง login; ฟอร์มเมนูอยู่ `menu-admin`. selector ทุกตัวพบจากสัญญาและโค้ดสร้าง HTML แบบ static เท่านั้น ยังไม่ยืนยัน runtime visibility/uniqueness. ถ้า runtime element ไม่เกิดตาม precondition ให้บันทึกปัญหา ไม่ใส่ผลผ่าน

auto หมายถึงมีทางทำ action/assertion บน Mock-up ที่ส่งมาได้; ยังไม่มีสคริปต์หรือผลรันในงานนี้ และอาจพบ defect ตอนรัน. manual มีขั้นตรวจคนจริงบน mock; mock-not-testable ต้องพึ่งระบบจริงหรือสิ่งที่ UI/ข้อมูลยังไม่มี. การรันหลายใบในหน่วยความจำเดียวไม่พิสูจน์เกณฑ์ระบบจริง

<a id="design-ts-us-01-1"></a>

## TS-US-01-1 — เปิดรายการแรกโดยไม่ล็อกอินครบโต๊ะใน seed

- US: US-01
- เจ้าของ: customer
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: นับจากกล้องมือถืออ่าน QR สำเร็จ จนถึงหน้าเมนูแสดงรายการแรก ภายใน 3 วินาทีบน Wi‑Fi ร้าน ในอย่างน้อย 18 จาก 20 ครั้งของชุดทดสอบ
- clause ที่ตรวจ: F01: สแกนแล้วเข้าถึงเมนูโดยไม่ล็อกอินในข้อความ US; ตรวจเฉพาะปลายทางรายการแรกของ AC
- FR / Flow / Screen: FR-01; NFR-01 → MRG-01, MRG-12 → SCR-01; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: auto ตรวจเฉพาะพฤติกรรมจำลองผ่าน UI/DOM; ไม่พิสูจน์ QR, LAN/Wi‑Fi, Security, Load, Availability, server log หรือการชำระเงินจริง
- Precondition/reset: R0 แยก context ใหม่ต่อโต๊ะ; ยังไม่ login และ menu-list ยังไม่แสดง
- Test data: โต๊ะ 01, 02, 03 ตาม seed; m01 กะเพราไก่ 50 บาท
- data-testid และ scope: G: btn-reset, role-customer; C: table-select, btn-open-menu, active-table, menu-list > menu-item-m01; ฟอร์ม staff-user/staff-pin ตรวจระดับหน้า; คำย่อ G/C/K/F/R/I/M และขั้น O/K0/F0/M0 ตามส่วน Precondition และ scope ที่ใช้ซ้ำ
- ขั้นตอน:

  1. ทำ R0 แล้วเลือกโต๊ะแต่ละค่าผ่าน table-select โดยไม่กรอกข้อมูลเข้าใช้
  2. กด btn-open-menu; ตรวจ active-table และรายการ m01 ภายใน menu-list
  3. ตรวจว่าไม่ต้องผ่านฟอร์ม login เพื่อเห็นรายการแรก; ทำซ้ำใน context ใหม่ให้ครบ 3 โต๊ะ

- Expected result: แต่ละโต๊ะเปิด menu-list และ menu-item-m01 ที่มองเห็นได้ พร้อมหมายเลขโต๊ะที่เลือก โดยไม่ต้อง login; fixture TS-US-01-101 ตรวจเพียง menu-list จึงยังไม่แทน assertion รายการแรกและหลายโต๊ะนี้
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงข้อความ AC ต้นฉบับเต็มของ US-01 ในรายการนี้ทุกตัวเลข/สูตร/หน่วย/สัดส่วน; ตารางแยก assertions ระบุประชากรที่ต้องเก็บ. ชุดย่อยหรือจำนวน fixture ใน Test data ไม่ใช้แทนประชากรนั้น; assertion เฉพาะข้อผิดพลาดที่ไม่มีกลุ่มตัวอย่างใน AC ไม่เพิ่มเกณฑ์จำนวนเอง. ทุกเกณฑ์ระบบจริงยังไม่ได้ทดสอบ
- สมมติฐาน/ข้อค้าง: table-select เป็นตัวแทน QR เท่านั้น; การสแกนจริงและเวลาแยก TS-US-01-2
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-01-2"></a>

## TS-US-01-2 — สแกน QR จริงและวัดการแสดงรายการแรก 20 ครั้ง

- US: US-01
- เจ้าของ: customer
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: นับจากกล้องมือถืออ่าน QR สำเร็จ จนถึงหน้าเมนูแสดงรายการแรก ภายใน 3 วินาทีบน Wi‑Fi ร้าน ในอย่างน้อย 18 จาก 20 ครั้งของชุดทดสอบ
- clause ที่ตรวจ: F01 + N01: เปิดเมนูโดยไม่ล็อกอิน; จากกล้องอ่าน QR สำเร็จถึงรายการแรก ≤3 วินาทีบน Wi‑Fi ร้าน อย่างน้อย 18 จาก 20 ครั้ง
- FR / Flow / Screen: FR-01; NFR-01 → MRG-01, MRG-12 → SCR-01; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: mock-not-testable: UI/ข้อมูลหรือระบบจริงที่จำเป็นยังไม่มีตาม precondition; ไม่ใช้การอ่าน source หรือคลิก mock แทน AC ระบบจริง
- Precondition/reset: BLOCKED: ไม่มีระบบจริง/QR เชื่อมระบบ/มือถือบน Wi‑Fi ร้าน; ต้องกำหนดสภาพทดสอบตาม Q-01 ก่อนรัน
- Test data: ป้าย QR โต๊ะจำลอง 01; ชุด 20 ครั้ง ระบุรุ่นมือถือ เบราว์เซอร์ จำนวนเมนู และภาระ Wi‑Fi ในหลักฐานภายหลัง
- data-testid และ scope: Mock อ้าง C: menu-list, menu-item-m01 ได้เฉพาะปลายทาง; selector กล้อง/ระบบจริง MISSING ไม่แต่งชื่อ; คำย่อ G/C/K/F/R/I/M และขั้น O/K0/F0/M0 ตามส่วน Precondition และ scope ที่ใช้ซ้ำ
- ขั้นตอน:

  1. เตรียมมือถือที่ไม่ login และเชื่อม Wi‑Fi ร้าน บันทึกเงื่อนไข cache/เครือข่ายที่ตกลง
  2. แต่ละครั้งบันทึก t0 เมื่อกล้องอ่าน QR สำเร็จ และ t1 เมื่อหน้าเมนูแสดงรายการแรก พร้อมภาพ/วิดีโอระบุครั้ง
  3. คำนวณ t1−t0 ทั้ง 20 ครั้ง นับครั้ง ≤3 วินาที; การเปิดไม่ได้หรือไม่มีหลักฐานต้องรายงาน ไม่แทนด้วยค่า 0

- Expected result: เปิดได้โดยไม่ล็อกอิน; อย่างน้อย 18 จาก 20 ครั้งใช้เวลาไม่เกิน 3 วินาทีบน Wi‑Fi ร้าน; ไม่มีค่าเวลาให้ตัดสินในรอบนี้
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงข้อความ AC ต้นฉบับเต็มของ US-01 ในรายการนี้ทุกตัวเลข/สูตร/หน่วย/สัดส่วน; ตารางแยก assertions ระบุประชากรที่ต้องเก็บ. ชุดย่อยหรือจำนวน fixture ใน Test data ไม่ใช้แทนประชากรนั้น; assertion เฉพาะข้อผิดพลาดที่ไม่มีกลุ่มตัวอย่างใน AC ไม่เพิ่มเกณฑ์จำนวนเอง. ทุกเกณฑ์ระบบจริงยังไม่ได้ทดสอบ
- สมมติฐาน/ข้อค้าง: Q-01; ต้องใช้จุดเริ่มกล้องอ่านสำเร็จ ไม่ใช้เริ่มเปิดไฟล์ HTML
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-01-3"></a>

## TS-US-01-3 — QR อ่านไม่ได้หรือปลายทางเมนูเปิดไม่ได้

- US: US-01
- เจ้าของ: customer
- ประเภท: ข้อยกเว้น
- AC ต้นฉบับเต็ม: นับจากกล้องมือถืออ่าน QR สำเร็จ จนถึงหน้าเมนูแสดงรายการแรก ภายใน 3 วินาทีบน Wi‑Fi ร้าน ในอย่างน้อย 18 จาก 20 ครั้งของชุดทดสอบ
- clause ที่ตรวจ: ข้อยกเว้นของ F01/N01; AC ไม่ระบุวิธีแจ้งข้อผิดพลาดหรือ retry
- FR / Flow / Screen: FR-01; NFR-01 → MRG-01, MRG-12 → SCR-01; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: mock-not-testable: UI/ข้อมูลหรือระบบจริงที่จำเป็นยังไม่มีตาม precondition; ไม่ใช้การอ่าน source หรือคลิก mock แทน AC ระบบจริง
- Precondition/reset: BLOCKED: ต้องมี QR/ระบบจริงและคำตอบเกี่ยวกับ fallback; แยกจากชุดปกติ 20 ครั้ง
- Test data: QR จำลองเสียหายหนึ่งรูป และ QR ถูกต้องที่ปลายทางไม่พร้อมหนึ่งกรณี; ไม่มีข้อมูลลูกค้าจริง
- data-testid และ scope: MISSING: ไม่มี selector สำหรับกล้องอ่าน QR ล้มเหลวหรือเครือข่ายจริงใน mock; คำย่อ G/C/K/F/R/I/M และขั้น O/K0/F0/M0 ตามส่วน Precondition และ scope ที่ใช้ซ้ำ
- ขั้นตอน:

  1. ลองอ่าน QR จำลองเสียหายแล้วบันทึกผลที่กล้องและหน้าเว็บ
  2. อีกกรณีให้กล้องอ่าน QR สำเร็จแต่เมนูปลายทางไม่ตอบ; บันทึกจุดเริ่มและข้อความที่เกิดจริง
  3. เทียบพฤติกรรม fallback กับคำตอบเจ้าของข้อกำหนดเมื่อมี

- Expected result: ถ้ากล้องยังอ่านไม่สำเร็จยังไม่เริ่มจับเวลา AC; ถ้าอ่านสำเร็จแต่รายการแรกไม่ขึ้นภายใน 3 วินาที ให้บันทึกว่าเกินเกณฑ์ของครั้งนั้น; ข้อความ/จำนวน retry/ทางออกยังไม่มี oracle จึง BLOCKED
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงข้อความ AC ต้นฉบับเต็มของ US-01 ในรายการนี้ทุกตัวเลข/สูตร/หน่วย/สัดส่วน; ตารางแยก assertions ระบุประชากรที่ต้องเก็บ. ชุดย่อยหรือจำนวน fixture ใน Test data ไม่ใช้แทนประชากรนั้น; assertion เฉพาะข้อผิดพลาดที่ไม่มีกลุ่มตัวอย่างใน AC ไม่เพิ่มเกณฑ์จำนวนเอง. ทุกเกณฑ์ระบบจริงยังไม่ได้ทดสอบ
- สมมติฐาน/ข้อค้าง: สมมติฐานรอยืนยัน Q-01 และประเด็น QR เสีย: ไม่กำหนดว่าต้อง retry กี่ครั้งหรือแสดงข้อความใด
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-02-1"></a>

## TS-US-02-1 — ตรวจโต๊ะสามใบแยกตาม order ID

- US: US-02
- เจ้าของ: customer
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: QR แต่ละโต๊ะมี URL ที่มี table_id (เช่น `/t/07`) และออเดอร์ที่สร้างจาก QR โต๊ะทดสอบ 20 โต๊ะ มี table_id ตรงกับป้ายโต๊ะอย่างน้อย 19 จาก 20 ใบ โดยตรวจจากหน้าจอหน้าร้าน
- clause ที่ตรวจ: F02: ออเดอร์ผูกโต๊ะและแสดงบนหน้าร้าน; เป็น projection ของ AC โดยยังไม่ผ่าน QR URL จริง
- FR / Flow / Screen: FR-02; —; AC ใน FR → MRG-01, MRG-04, MRG-12, MRG-13 → SCR-01, SCR-03, SCR-08; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: auto ตรวจเฉพาะพฤติกรรมจำลองผ่าน UI/DOM; ไม่พิสูจน์ QR, LAN/Wi‑Fi, Security, Load, Availability, server log หรือการชำระเงินจริง
- Precondition/reset: R0 ครั้งเดียว; คงออเดอร์ไว้ครบสามโต๊ะเพื่อทดสอบ scope
- Test data: โต๊ะ 01 สั่ง m01=50; โต๊ะ 02 สั่ง m02=55; โต๊ะ 03 สั่ง m01+extra-egg=60 บาท
- data-testid และ scope: G และ C ตาม R0/O; C: active-table, order-id; F(order ID): front-order, attribute data-table-id และข้อความป้ายโต๊ะ; คำย่อ G/C/K/F/R/I/M และขั้น O/K0/F0/M0 ตามส่วน Precondition และ scope ที่ใช้ซ้ำ
- ขั้นตอน:

  1. เปิดเมนูโต๊ะ 01 สั่งตามข้อมูลผ่าน O และจด order-id
  2. ทำโต๊ะ 02 และ 03 โดยเลือก table-select และเปิดเมนูใหม่ ไม่ reset ระหว่างสามใบ; จด ID แยก
  3. เข้า F0 ตรวจ F ของแต่ละ ID เทียบเลขโต๊ะกับข้อมูลก่อนสั่ง และตรวจไม่มีการชี้ใบเดียวซ้ำ

- Expected result: ทั้งสามใบใน mock ผูก 01/02/03 ตามลำดับที่สั่งและตรง data-table-id/ป้ายใน F ของ ID นั้น; ไม่ใช้ข้อความ 02 ที่พบที่ใดก็ได้ใน front-orders เป็นหลักฐาน; เชื่อม TS-US-02-101 ซึ่งเป็น smoke ใบเดียว
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงข้อความ AC ต้นฉบับเต็มของ US-02 ในรายการนี้ทุกตัวเลข/สูตร/หน่วย/สัดส่วน; ตารางแยก assertions ระบุประชากรที่ต้องเก็บ. ชุดย่อยหรือจำนวน fixture ใน Test data ไม่ใช้แทนประชากรนั้น; assertion เฉพาะข้อผิดพลาดที่ไม่มีกลุ่มตัวอย่างใน AC ไม่เพิ่มเกณฑ์จำนวนเอง. ทุกเกณฑ์ระบบจริงยังไม่ได้ทดสอบ
- สมมติฐาน/ข้อค้าง: seed มี 3 โต๊ะ ไม่แทน 20 โต๊ะตาม AC; การพิมพ์/เลือก table-select ไม่พิสูจน์ผูกจาก QR อัตโนมัติ
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-02-2"></a>

## TS-US-02-2 — QR URL และป้ายโต๊ะตรงกันในชุด 20 โต๊ะ

- US: US-02
- เจ้าของ: customer
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: QR แต่ละโต๊ะมี URL ที่มี table_id (เช่น `/t/07`) และออเดอร์ที่สร้างจาก QR โต๊ะทดสอบ 20 โต๊ะ มี table_id ตรงกับป้ายโต๊ะอย่างน้อย 19 จาก 20 ใบ โดยตรวจจากหน้าจอหน้าร้าน
- clause ที่ตรวจ: F02: URL มี table_id เช่น /t/07; ออเดอร์จาก 20 โต๊ะตรงป้ายอย่างน้อย 19 จาก 20 ใบ
- FR / Flow / Screen: FR-02; —; AC ใน FR → MRG-01, MRG-04, MRG-12, MRG-13 → SCR-01, SCR-03, SCR-08; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: mock-not-testable: UI/ข้อมูลหรือระบบจริงที่จำเป็นยังไม่มีตาม precondition; ไม่ใช้การอ่าน source หรือคลิก mock แทน AC ระบบจริง
- Precondition/reset: BLOCKED: ไม่มี QR route/backend และ 20 โต๊ะใน mock; เตรียมป้ายจำลอง 20 โต๊ะบนระบบทดสอบจริง
- Test data: โต๊ะจำลอง 01–20 โต๊ะละ 1 ออเดอร์; ตัวอย่าง URL /t/07; m01 จำนวน 1 ต่อใบ
- data-testid และ scope: ระบบจริง MISSING; F(order ID) เป็นเพียง selector เทียบเคียงของ mock; คำย่อ G/C/K/F/R/I/M และขั้น O/K0/F0/M0 ตามส่วน Precondition และ scope ที่ใช้ซ้ำ
- ขั้นตอน:

  1. ตรวจ URL ที่ QR ของทุกโต๊ะถอดได้ ว่ามี table_id และบันทึกคู่ป้าย/URL
  2. สแกนแต่ละโต๊ะและสร้างออเดอร์โดยไม่กรอกเลขโต๊ะเอง จด order ID
  3. เปิดจอหน้าร้านและเทียบ table_id กับป้ายตาม ID ให้ครบ 20 ใบ; บันทึกทุกใบที่ไม่ตรง

- Expected result: QR แต่ละโต๊ะมี URL ที่มี table_id และหน้าร้านตรงกับป้ายอย่างน้อย 19 จาก 20 ใบ; ไม่ใช้เกณฑ์ 19/20 อนุญาตให้บาง QR ไม่มี table_id
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงข้อความ AC ต้นฉบับเต็มของ US-02 ในรายการนี้ทุกตัวเลข/สูตร/หน่วย/สัดส่วน; ตารางแยก assertions ระบุประชากรที่ต้องเก็บ. ชุดย่อยหรือจำนวน fixture ใน Test data ไม่ใช้แทนประชากรนั้น; assertion เฉพาะข้อผิดพลาดที่ไม่มีกลุ่มตัวอย่างใน AC ไม่เพิ่มเกณฑ์จำนวนเอง. ทุกเกณฑ์ระบบจริงยังไม่ได้ทดสอบ
- สมมติฐาน/ข้อค้าง: Q-02 ผู้สร้าง/เปลี่ยน QR และจำนวนโต๊ะจริงยังไม่กำหนด; 20 โต๊ะเป็นชุดทดสอบตาม AC
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-02-3"></a>

## TS-US-02-3 — table_id หาย ไม่มีอยู่ หรือถูกเปลี่ยน

- US: US-02
- เจ้าของ: customer
- ประเภท: ผิดพลาด
- AC ต้นฉบับเต็ม: QR แต่ละโต๊ะมี URL ที่มี table_id (เช่น `/t/07`) และออเดอร์ที่สร้างจาก QR โต๊ะทดสอบ 20 โต๊ะ มี table_id ตรงกับป้ายโต๊ะอย่างน้อย 19 จาก 20 ใบ โดยตรวจจากหน้าจอหน้าร้าน
- clause ที่ตรวจ: ข้อผิดพลาดของ F02; ต้นฉบับไม่กำหนดผลเมื่อ table_id ไม่ถูกต้อง
- FR / Flow / Screen: FR-02; —; AC ใน FR → MRG-01, MRG-04, MRG-12, MRG-13 → SCR-01, SCR-03, SCR-08; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: mock-not-testable: UI/ข้อมูลหรือระบบจริงที่จำเป็นยังไม่มีตาม precondition; ไม่ใช้การอ่าน source หรือคลิก mock แทน AC ระบบจริง
- Precondition/reset: BLOCKED: รอ Q-02 และ route ระบบจริง; ไม่ดัดแปลง HTML หรือ input
- Test data: URL จำลอง /t/ โดยไม่มีค่า, /t/99 เมื่อไม่มีโต๊ะ 99, QR ป้าย 07 แต่ URL /t/08
- data-testid และ scope: MISSING: route/table_id validation ไม่อยู่ใน mock; ห้ามสร้าง selector ข้อผิดพลาดเอง; คำย่อ G/C/K/F/R/I/M และขั้น O/K0/F0/M0 ตามส่วน Precondition และ scope ที่ใช้ซ้ำ
- ขั้นตอน:

  1. อ่าน URL ทั้งสามแบบและบันทึกค่า table_id ที่ได้รับ
  2. ลองเปิดเมนูและส่งคำสั่งในระบบทดสอบเมื่อพร้อม จดผลและหมายเลขโต๊ะที่แสดง
  3. กรณีสร้างออเดอร์สำเร็จเทียบหน้าร้านกับป้าย; แยกการ mismatch ออกจากนโยบายแจ้ง invalid

- Expected result: URL ไม่มี table_id ไม่เป็นไปตามเงื่อนไข URL ของ AC; ออเดอร์ผูกต่างจากป้ายเป็น mismatch; ผลตอบรับ invalid เช่น reject/เลือกโต๊ะใหม่ และข้อความแจ้งยัง BLOCKED รอยืนยัน
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงข้อความ AC ต้นฉบับเต็มของ US-02 ในรายการนี้ทุกตัวเลข/สูตร/หน่วย/สัดส่วน; ตารางแยก assertions ระบุประชากรที่ต้องเก็บ. ชุดย่อยหรือจำนวน fixture ใน Test data ไม่ใช้แทนประชากรนั้น; assertion เฉพาะข้อผิดพลาดที่ไม่มีกลุ่มตัวอย่างใน AC ไม่เพิ่มเกณฑ์จำนวนเอง. ทุกเกณฑ์ระบบจริงยังไม่ได้ทดสอบ
- สมมติฐาน/ข้อค้าง: Q-02: ไม่ตั้งกฎให้ default โต๊ะหรือปฏิเสธ HTTP status ใดเอง
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-03-1"></a>

## TS-US-03-1 — ช่วงรับและป้ายครัวครบ 10 ออเดอร์กลับบ้าน

- US: US-03
- เจ้าของ: customer
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: เลือกเวลารับได้จากรายการช่วงเวลาละ 15 นาที (เช่น 12:00–12:15, 12:15–12:30) ที่เริ่มอย่างน้อย 20 นาทีหลังเวลาสั่ง และออเดอร์สั่งกลับบ้านทดสอบ 10 ใบ แสดงป้าย “สั่งกลับบ้าน” พร้อมช่วงเวลารับบนจอครัวครบทั้ง 10 ใบ
- clause ที่ตรวจ: F03a: ช่วงละ 15 นาที เริ่มอย่างน้อย 20 นาที; F03b: ครัวมีป้ายและช่วงรับครบ 10 จาก 10 ใบ
- FR / Flow / Screen: FR-03; —; AC ใน FR → MRG-02, MRG-04, MRG-14 → SCR-02, SCR-03, SCR-06, SCR-08; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: auto ตรวจเฉพาะพฤติกรรมจำลองผ่าน UI/DOM; ไม่พิสูจน์ QR, LAN/Wi‑Fi, Security, Load, Availability, server log หรือการชำระเงินจริง
- Precondition/reset: R0; เวลา 12:00; โหมด takeaway; คง 10 ออเดอร์ใน context เดียวและไม่เลื่อนเวลา
- Test data: m01 จำนวน 1 ต่อใบ; 10 ใบสลับ slot 12:30-12:45 และ 12:45-13:00 อย่างละ 5; เป็นการแจกแจง fixture
- data-testid และ scope: G/C ตาม R0/O; C: order-mode, pickup-slot, order-id; K(order ID): kitchen-order อ่านป้ายและช่วงรับจากข้อความภายในใบ; คำย่อ G/C/K/F/R/I/M และขั้น O/K0/F0/M0 ตามส่วน Precondition และ scope ที่ใช้ซ้ำ
- ขั้นตอน:

  1. เลือก order-mode=takeaway; อ่านรายการ option ของ pickup-slot ตรวจความยาวทุกช่วง 15 นาที และเวลาเริ่ม−sim-clock ≥20 นาที
  2. เลือกช่วงตามข้อมูล เพิ่ม m01 และยืนยัน; เก็บ order-id/ช่วงรับทุกใบ ทำครบ 10 ใบ
  3. เข้า K0 ตรวจ K แต่ละ ID ว่ามีป้าย สั่งกลับบ้าน และช่วงเริ่ม–จบตรงที่เลือกครบ 10 ใบ

- Expected result: ช่วงที่เสนอทุกช่วงยาว 15 นาทีและไม่เริ่มก่อนขั้นต่ำ 20 นาที; ทั้ง 10 ใบใน mock มีป้ายและช่วงรับตรงกัน; TS-US-03-101 เป็น smoke ใบเดียว ไม่แทนชุดนี้
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงข้อความ AC ต้นฉบับเต็มของ US-03 ในรายการนี้ทุกตัวเลข/สูตร/หน่วย/สัดส่วน; ตารางแยก assertions ระบุประชากรที่ต้องเก็บ. ชุดย่อยหรือจำนวน fixture ใน Test data ไม่ใช้แทนประชากรนั้น; assertion เฉพาะข้อผิดพลาดที่ไม่มีกลุ่มตัวอย่างใน AC ไม่เพิ่มเกณฑ์จำนวนเอง. ทุกเกณฑ์ระบบจริงยังไม่ได้ทดสอบ
- สมมติฐาน/ข้อค้าง: Q-03: ปัดขึ้นขอบ 15 นาทีและจำนวนช่วงใน UI เป็น fixture; เวลาเริ่ม 12:00 → ช่วงแรก 12:30-12:45 ไม่ใช่กฎเพิ่มของร้าน
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-03-2"></a>

## TS-US-03-2 — ขอบขั้นต่ำ 20 นาทีและช่วงที่เร็วเกินไป

- US: US-03
- เจ้าของ: customer
- ประเภท: ผิดพลาด
- AC ต้นฉบับเต็ม: เลือกเวลารับได้จากรายการช่วงเวลาละ 15 นาที (เช่น 12:00–12:15, 12:15–12:30) ที่เริ่มอย่างน้อย 20 นาทีหลังเวลาสั่ง และออเดอร์สั่งกลับบ้านทดสอบ 10 ใบ แสดงป้าย “สั่งกลับบ้าน” พร้อมช่วงเวลารับบนจอครัวครบทั้ง 10 ใบ
- clause ที่ตรวจ: F03a: ไม่เสนอช่วงเริ่มน้อยกว่า 20 นาที; ขอบเท่ากับ 20 นาทีเป็นค่าที่ยอมรับได้
- FR / Flow / Screen: FR-03; —; AC ใน FR → MRG-02, MRG-04, MRG-14 → SCR-02, SCR-03, SCR-06, SCR-08; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: auto ตรวจเฉพาะพฤติกรรมจำลองผ่าน UI/DOM; ไม่พิสูจน์ QR, LAN/Wi‑Fi, Security, Load, Availability, server log หรือการชำระเงินจริง
- Precondition/reset: R0; ใช้ปุ่มเวลาเพื่อเปิดรายการช่วงรับใหม่ในแต่ละจุด; ไม่มีการ inject option ที่ UI ไม่สร้าง
- Test data: 12:00 → 12:15 ห่าง 15 นาที; 12:10 → 12:30 ห่าง 20 นาที; 12:20 → 12:30 ห่าง 10 นาที และ 12:45 ห่าง 25 นาที
- data-testid และ scope: G: btn-reset, btn-advance-10m, sim-clock; C: order-mode, pickup-slot; คำย่อ G/C/K/F/R/I/M และขั้น O/K0/F0/M0 ตามส่วน Precondition และ scope ที่ใช้ซ้ำ
- ขั้นตอน:

  1. ที่ 12:00 เลือก takeaway ตรวจว่า 12:15-12:30 ไม่ใช่ช่วงที่เลือกได้ และช่วงแรกจำลอง 12:30-12:45
  2. เลื่อน 10 นาที ตรวจ sim-clock=12:10 และช่วง 12:30-12:45 ยังเลือกได้ที่ขอบ 20 นาที
  3. เลื่อนอีก 10 นาที ตรวจเวลา 12:20; ช่วง 12:30-12:45 ต้องไม่เลือกได้ และช่วงแรกจำลอง 12:45-13:00; ตรวจทุกช่วงยาว 15 นาที

- Expected result: ไม่ยอมให้เลือกช่วงเริ่มต่ำกว่า 20 นาทีทั้งสองจุด; ขอบ 20 นาทีที่ 12:10 เลือกได้ใน fixture; ไม่สรุปว่าต้องมีทุก slot ที่ผ่านขั้นต่ำในระบบจริง
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงข้อความ AC ต้นฉบับเต็มของ US-03 ในรายการนี้ทุกตัวเลข/สูตร/หน่วย/สัดส่วน; ตารางแยก assertions ระบุประชากรที่ต้องเก็บ. ชุดย่อยหรือจำนวน fixture ใน Test data ไม่ใช้แทนประชากรนั้น; assertion เฉพาะข้อผิดพลาดที่ไม่มีกลุ่มตัวอย่างใน AC ไม่เพิ่มเกณฑ์จำนวนเอง. ทุกเกณฑ์ระบบจริงยังไม่ได้ทดสอบ
- สมมติฐาน/ข้อค้าง: Q-03: เวลาสั่งจริงยังไม่ชัด; ผล submit ของ slot เก่าหรือข้อความเมื่อหมดช่วงยังไม่กำหนด ดู TS-US-03-3
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-03-3"></a>

## TS-US-03-3 — เลือกช่วงรับแล้วค้างหน้าจอจนต่ำกว่าขั้นต่ำ

- US: US-03
- เจ้าของ: customer
- ประเภท: ข้อยกเว้น
- AC ต้นฉบับเต็ม: เลือกเวลารับได้จากรายการช่วงเวลาละ 15 นาที (เช่น 12:00–12:15, 12:15–12:30) ที่เริ่มอย่างน้อย 20 นาทีหลังเวลาสั่ง และออเดอร์สั่งกลับบ้านทดสอบ 10 ใบ แสดงป้าย “สั่งกลับบ้าน” พร้อมช่วงเวลารับบนจอครัวครบทั้ง 10 ใบ
- clause ที่ตรวจ: F03a/F03b เมื่อเวลาระหว่างเลือกและยืนยันเปลี่ยน; ผล stale slot ไม่ระบุใน AC
- FR / Flow / Screen: FR-03; —; AC ใน FR → MRG-02, MRG-04, MRG-14 → SCR-02, SCR-03, SCR-06, SCR-08; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: mock-not-testable: UI/ข้อมูลหรือระบบจริงที่จำเป็นยังไม่มีตาม precondition; ไม่ใช้การอ่าน source หรือคลิก mock แทน AC ระบบจริง
- Precondition/reset: BLOCKED: รอ Q-03 นิยามเวลาสั่ง/การเลื่อนช่วงอัตโนมัติ และระบบจริง; mock render อาจเลือกช่วงใหม่เองจึงไม่แทนคำสั่งเก่าจริง
- Test data: เลือก 12:30–12:45 เมื่อเวลา 12:00 แล้วกดยืนยันที่ 12:20; m01 จำนวน 1
- data-testid และ scope: C: pickup-slot, btn-submit-order, order-message เป็นจุดเทียบเคียง; selector/clock ระบบจริง MISSING; คำย่อ G/C/K/F/R/I/M และขั้น O/K0/F0/M0 ตามส่วน Precondition และ scope ที่ใช้ซ้ำ
- ขั้นตอน:

  1. เลือกช่วงที่ถูกต้องในตอนเปิดหน้าตามข้อมูลและบันทึกเวลานั้น
  2. รอจน 12:20 แล้วบันทึกว่ารายการช่วงรับที่ UI แสดงเปลี่ยนหรือยังเดิม จากนั้นยืนยัน
  3. เมื่อมีคำตอบนิยามเวลาสั่งให้คำนวณ start−เวลาสั่ง; ถ้าสร้างออเดอร์ให้เทียบช่วงรับที่ลูกค้าเห็นและใบครัว

- Expected result: เมื่อกำหนดจุดเวลาสั่งแล้ว ช่วงที่ยอมรับต้องยาว 15 นาทีและเริ่มอย่างน้อย 20 นาทีหลังจุดนั้น; การแจ้งเตือน/บังคับเลือกใหม่/เปลี่ยนอัตโนมัติยังไม่มี oracle และไม่กำหนดเอง
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงข้อความ AC ต้นฉบับเต็มของ US-03 ในรายการนี้ทุกตัวเลข/สูตร/หน่วย/สัดส่วน; ตารางแยก assertions ระบุประชากรที่ต้องเก็บ. ชุดย่อยหรือจำนวน fixture ใน Test data ไม่ใช้แทนประชากรนั้น; assertion เฉพาะข้อผิดพลาดที่ไม่มีกลุ่มตัวอย่างใน AC ไม่เพิ่มเกณฑ์จำนวนเอง. ทุกเกณฑ์ระบบจริงยังไม่ได้ทดสอบ
- สมมติฐาน/ข้อค้าง: Q-03; ไม่อ้าง stale rejection จากการอ่าน handler ว่าเป็นกฎร้านหรือผลรัน
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-04-1"></a>

## TS-US-04-1 — ตัวเลือกที่ตั้ง ราคาเพิ่ม และใบครัวชุด 20 ใบ

- US: US-04
- เจ้าของ: customer
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: เมนูที่ผู้จัดการตั้งตัวเลือกไว้แสดงตัวเลือกครบตามที่ตั้ง ราคาเพิ่มรวมในยอดก่อนกดยืนยัน และตัวเลือกที่เลือกปรากฏในใบครัวอย่างน้อย 19 จาก 20 ใบของชุดทดสอบ
- clause ที่ตรวจ: F04a: ตัวเลือกครบตามที่ตั้ง; F04b: รวมราคาเพิ่มก่อนยืนยัน; F04c: ตัวเลือกบนใบครัวอย่างน้อย 19 จาก 20 ใบ
- FR / Flow / Screen: FR-04; —; AC ใน FR → MRG-03, MRG-04, MRG-32, MRG-33 → SCR-03, SCR-06, SCR-04; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: auto ตรวจเฉพาะพฤติกรรมจำลองผ่าน UI/DOM; ไม่พิสูจน์ QR, LAN/Wi‑Fi, Security, Load, Availability, server log หรือการชำระเงินจริง
- Precondition/reset: R0; seed m01 มี extra-egg หนึ่งตัว; ไม่เปลี่ยนราคา/stock ระหว่างชุด
- Test data: 20 ใบสลับ m01 ไม่เลือกเพิ่ม=50 บาท กับ m01+extra-egg=60 บาท อย่างละ 10; ตัวเลขจาก seed และการแจกแจงเป็น fixture
- data-testid และ scope: C: menu-item-m01, option-extra-egg, item-total, cart-total, btn-add-item, btn-submit-order, order-id; K(order ID) อ่านชื่อรายการ/ตัวเลือก; คำย่อ G/C/K/F/R/I/M และขั้น O/K0/F0/M0 ตามส่วน Precondition และ scope ที่ใช้ซ้ำ
- ขั้นตอน:

  1. เปิด m01 ตรวจตัวเลือกที่แสดงเทียบ seed ว่ามี เพิ่มไข่ดาว +10 ครบและไม่มีตัวเลือกที่ไม่ได้ตั้ง
  2. แต่ละใบตรวจ item-total ก่อนเพิ่ม และ cart-total ก่อนยืนยันให้ได้ 50 หรือ 60 ตามข้อมูล; เก็บ option/ยอด/order-id
  3. เข้า K0 หลังครบ 20 ใบ เทียบรายการ/ตัวเลือกภายใน K แต่ละ ID กับข้อมูลก่อนยืนยัน รวมกรณีไม่เลือกที่ต้องไม่เพิ่มไข่เอง

- Expected result: ตัวเลือกตรง configuration และยอดก่อนยืนยันถูกทุกใบใน mock; บันทึกจำนวนใบครัวที่ตรงทั้งหมด 20 ใบและเปรียบเทียบเกณฑ์อย่างน้อย 19 จาก 20; ไม่ใช้สัดส่วนนี้ลดเกณฑ์ความครบ/ยอดก่อนยืนยัน; TS-US-04-101 ตรวจเพียงไข่หนึ่งใบ
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงข้อความ AC ต้นฉบับเต็มของ US-04 ในรายการนี้ทุกตัวเลข/สูตร/หน่วย/สัดส่วน; ตารางแยก assertions ระบุประชากรที่ต้องเก็บ. ชุดย่อยหรือจำนวน fixture ใน Test data ไม่ใช้แทนประชากรนั้น; assertion เฉพาะข้อผิดพลาดที่ไม่มีกลุ่มตัวอย่างใน AC ไม่เพิ่มเกณฑ์จำนวนเอง. ทุกเกณฑ์ระบบจริงยังไม่ได้ทดสอบ
- สมมติฐาน/ข้อค้าง: seed มีเพียงไข่ ไม่แปลว่าร้านไม่ต้องรองรับระดับเผ็ด/ไม่ใส่ผักชี; เพิ่มตรวจ TS-US-04-2; Q-04
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-04-2"></a>

## TS-US-04-2 — ตัวเลือกหลายชนิดที่ผู้จัดการตั้งแสดงครบและอ่านได้

- US: US-04
- เจ้าของ: customer
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: เมนูที่ผู้จัดการตั้งตัวเลือกไว้แสดงตัวเลือกครบตามที่ตั้ง ราคาเพิ่มรวมในยอดก่อนกดยืนยัน และตัวเลือกที่เลือกปรากฏในใบครัวอย่างน้อย 19 จาก 20 ใบของชุดทดสอบ
- clause ที่ตรวจ: F04a/F04b: ครบทุกตัวเลือกที่ตั้งและราคาเพิ่มก่อนยืนยัน; คงตัวอย่างระดับเผ็ด ไม่ใส่ผักชี เพิ่มไข่ดาวใน US
- FR / Flow / Screen: FR-04; —; AC ใน FR → MRG-03, MRG-04, MRG-32, MRG-33 → SCR-03, SCR-06, SCR-04; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: manual
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: manual เพราะมีขั้นตรวจ label/การผูกตัวเลือกกับจานด้วยคนบน mock; ไม่ต้องใช้ธุรกรรมจริงและไม่มีผลตรวจในรอบนี้
- Precondition/reset: R0; เข้า M0 หน้าจัดการเมนู; ใช้ผู้ตรวจคนอ่าน label/ความสัมพันธ์กับจานและเปรียบเทียบ configuration
- Test data: m01 เดิมมีเพิ่มไข่ดาว +10; เพิ่มชื่อ ระดับเผ็ด (จำลอง) +0 และ ไม่ใส่ผักชี (จำลอง) +0 ผ่านหน้าผู้จัดการทีละตัว; ราคา m01=50
- data-testid และ scope: M: nav-menu-admin, admin-menu-select, admin-option-name, admin-option-price, btn-save-menu, admin-message; C: menu-item-m01, option-extra-egg, item-total, cart-total; testid ของตัวเลือกเพิ่มเกิด dynamic จึงอ่าน label ด้วยคน ไม่ตั้งชื่อคาดเดา; คำย่อ G/C/K/F/R/I/M และขั้น O/K0/F0/M0 ตามส่วน Precondition และ scope ที่ใช้ซ้ำ
- ขั้นตอน:

  1. ผู้จัดการเลือก m01 เพิ่มตัวเลือกจำลองหนึ่งตัวและบันทึก แล้วเพิ่มอีกตัวและบันทึก; จดรายการชื่อ/ราคา configuration ทั้งสาม
  2. ลูกค้าเปิด m01 ผู้ตรวจเทียบ label ทั้งสามกับที่ตั้ง อ่านได้และระบุว่าเป็นของจานนี้
  3. เลือกแต่ละตัวและเลือกทั้งสามเพื่อดูราคา 50 หรือ 60 ตามผลรวม; ตรวจ item-total และ cart-total ก่อนกดยืนยัน

- Expected result: แสดงชื่อ/ราคาเพิ่มครบสามตัวตามที่ตั้ง ผู้ตรวจอ่านได้และผูกกับจาน m01; ทั้งสามรวมแล้ว 60 บาทก่อนยืนยันตาม fixture; ไม่อ้างว่ารองรับการเลือกเผ็ดหลายระดับตามกฎจริงแล้ว
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงข้อความ AC ต้นฉบับเต็มของ US-04 ในรายการนี้ทุกตัวเลข/สูตร/หน่วย/สัดส่วน; ตารางแยก assertions ระบุประชากรที่ต้องเก็บ. ชุดย่อยหรือจำนวน fixture ใน Test data ไม่ใช้แทนประชากรนั้น; assertion เฉพาะข้อผิดพลาดที่ไม่มีกลุ่มตัวอย่างใน AC ไม่เพิ่มเกณฑ์จำนวนเอง. ทุกเกณฑ์ระบบจริงยังไม่ได้ทดสอบ
- สมมติฐาน/ข้อค้าง: Q-04: จำนวนค่าที่เลือกได้ การบังคับเลือก และตัวเลือกขัดกันยังไม่กำหนด; ชื่อและราคา 0 เป็นข้อมูลจำลอง ไม่รับรองการป้องกันสารก่อแพ้
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-04-3"></a>

## TS-US-04-3 — ตัวเลือกขัดกันหรือไม่ได้เลือกตัวที่อาจบังคับ

- US: US-04
- เจ้าของ: customer
- ประเภท: ผิดพลาด
- AC ต้นฉบับเต็ม: เมนูที่ผู้จัดการตั้งตัวเลือกไว้แสดงตัวเลือกครบตามที่ตั้ง ราคาเพิ่มรวมในยอดก่อนกดยืนยัน และตัวเลือกที่เลือกปรากฏในใบครัวอย่างน้อย 19 จาก 20 ใบของชุดทดสอบ
- clause ที่ตรวจ: ข้อผิดพลาดของ F04a/F04b; ไม่มีนิยามความเข้ากันได้หรือ required ใน AC
- FR / Flow / Screen: FR-04; —; AC ใน FR → MRG-03, MRG-04, MRG-32, MRG-33 → SCR-03, SCR-06, SCR-04; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: mock-not-testable: UI/ข้อมูลหรือระบบจริงที่จำเป็นยังไม่มีตาม precondition; ไม่ใช้การอ่าน source หรือคลิก mock แทน AC ระบบจริง
- Precondition/reset: BLOCKED: รอ Q-04 และ configuration ที่ระบุว่าใดบังคับ/ขัดกัน; mock ไม่มีสัญญารองรับกฎนี้
- Test data: ชุดสมมติ เผ็ดน้อย+เผ็ดมาก ในจานเดียว และไม่เลือกตัวที่เจ้าของระบบจะระบุว่าบังคับ; ยังไม่มีรายการคู่ขัดกันที่ยืนยัน
- data-testid และ scope: MISSING: selector กฎ required/conflict ใน v2; ไม่แต่ง option ID; คำย่อ G/C/K/F/R/I/M และขั้น O/K0/F0/M0 ตามส่วน Precondition และ scope ที่ใช้ซ้ำ
- ขั้นตอน:

  1. ขอรายการกฎที่ยืนยันแล้วและตั้งในระบบทดสอบเมื่อรองรับ
  2. ทดลองเลือกคู่ขัดกัน และอีกครั้งเว้นตัวที่บังคับแล้วพยายามยืนยัน
  3. เก็บตัวเลือกที่ส่ง ยอดก่อนยืนยัน ข้อความและใบครัวถ้ามี แล้วเทียบกฎที่อนุมัติ

- Expected result: ยังไม่มี oracle ว่าต้องปฏิเสธ ยกเลิกค่าก่อนหน้า หรือยอมรับ; ให้ BLOCKED/ไม่มีข้อมูลจนยืนยัน Q-04; กฎราคาและการส่งตัวเลือกที่ยอมรับยังต้องตรง AC
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงข้อความ AC ต้นฉบับเต็มของ US-04 ในรายการนี้ทุกตัวเลข/สูตร/หน่วย/สัดส่วน; ตารางแยก assertions ระบุประชากรที่ต้องเก็บ. ชุดย่อยหรือจำนวน fixture ใน Test data ไม่ใช้แทนประชากรนั้น; assertion เฉพาะข้อผิดพลาดที่ไม่มีกลุ่มตัวอย่างใน AC ไม่เพิ่มเกณฑ์จำนวนเอง. ทุกเกณฑ์ระบบจริงยังไม่ได้ทดสอบ
- สมมติฐาน/ข้อค้าง: Q-04; ห้ามถือว่าลูกค้าแพ้อาหารทำให้ต้องมีระบบรับรองสารก่อแพ้โดยอัตโนมัติ
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-04-4"></a>

## TS-US-04-4 — จับตัวเลือกผิดจานและราคาเพิ่มตกหล่นด้วย fixture สองจาน

- US: US-04
- เจ้าของ: customer
- ประเภท: ผิดพลาด
- AC ต้นฉบับเต็ม: เมนูที่ผู้จัดการตั้งตัวเลือกไว้แสดงตัวเลือกครบตามที่ตั้ง ราคาเพิ่มรวมในยอดก่อนกดยืนยัน และตัวเลือกที่เลือกปรากฏในใบครัวอย่างน้อย 19 จาก 20 ใบของชุดทดสอบ
- clause ที่ตรวจ: ตัวเลือกครบตาม configuration; ราคาเพิ่มรวมก่อนยืนยัน; ตัวเลือกที่เลือกตรงใบครัว
- FR / Flow / Screen: FR-04; —; AC ใน FR → MRG-03, MRG-04, MRG-32, MRG-33 → SCR-03, SCR-06, SCR-04; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: แก้ D01 เชิงออกแบบ; ต้องมีระบบ/จุดแทรก fault และจุดสังเกตตาม Precondition ซึ่งยังไม่มี จึง BLOCKED การรัน. เป็นแผนตรวจจับผลผิดด้วย oracle อิสระ ไม่ใช่การเปลี่ยนชื่อ happy path; ยังไม่ได้ทำ fault หรือรันทดสอบ
- Precondition/reset: BLOCKED การรัน: ต้องมีระบบทดสอบและตัวแทรกข้อมูลทดสอบที่จุดสร้างยอด/ข้อมูลใบครัว ซึ่ง Input ยังไม่มี; ผู้จัดระบบต้องเปิดให้ตรวจข้อมูลก่อนและหลังแทรกได้ แยกแต่ละกรณีและคืน snapshot เดิมทุกครั้ง
- Test data: fixture เมนู A ราคา 50 มี ไข่ดาว +10; เมนู B ราคา 55 มี ไม่ใส่ผักชี +0 เท่านั้น; ออเดอร์หนึ่งใบมีรายการ a=A+ไข่ดาว จำนวน 1 และ b=B+ไม่ใส่ผักชี จำนวน 1. บัญชีอ้างอิงอิสระ: a=60, b=55, รวม 115 บาท; option ต่อจานต้องตรงคู่เดิม. ชื่อ A/B/a/b เป็นป้ายข้อมูลจำลอง ไม่ใช่ selector

- data-testid และ scope: MISSING: จุดแทรก fault/selector ระบบทดสอบ; ใช้ order ID และ item ID ที่ระบบออกให้จับคู่กับ a/b ในสมุดข้อมูล ไม่คาดเดา API หรือชื่อ data-testid
- ขั้นตอน:

  1. บันทึก configuration ชื่อ/ราคา/รายการตัวเลือกของสองเมนู และคำนวณ 50+10+55+0=115 ด้วยเครื่องคิดเลขก่อนใช้ระบบ; สั่งเลือกตาม a/b โดยยังไม่ยืนยันและเก็บหน้ารายละเอียดจาน/ยอดตะกร้า
  2. control: ปิดตัวแทรก ตรวจตัวเลือกตาม configuration และยอด 60/55/115 ก่อนยืนยัน แล้วส่งและจับคู่ใบครัวตาม order/item ID กับข้อมูลที่เลือก
  3. fault A: reset แล้วใช้ตัวแทรกที่จุดคำนวณยอดก่อนยืนยัน ตัดราคาเพิ่มไข่ดาวของ a จาก 10 เป็น 0 เฉพาะข้อมูลเข้าตัวคำนวณ โดยไม่แก้ configuration หรือรายการเลือกที่บันทึกไว้; เก็บ input ก่อน/หลังและยอด UI แล้วเทียบ 115 ไม่ใช้ยอดผิดเป็น oracle
  4. fault B: reset แล้วคงยอดก่อนยืนยัน 115; หลังส่งให้ตัวแทรกสลับชุดตัวเลือก a กับ b เฉพาะข้อมูลส่งไปแสดงใบครัว โดยคง order/item ID เดิม; อ่านชื่อเมนู/ตัวเลือกทีละจานบนใบครัวและเทียบสมุดข้อมูล
  5. ปิดตัวแทรกและทำ control ซ้ำ; การสร้างเครื่องมือ/ดำเนินการ fault นี้เป็นแผนในระบบทดสอบอนาคต ไม่แก้ HTML/fixture/Input รอบนี้

- Expected result: oracle จาก configuration: A ต้องแสดงเฉพาะไข่ดาว +10 และ B เฉพาะไม่ใส่ผักชี +0; a=60, b=55, รวมก่อนยืนยัน=115; ใบครัว a มีไข่ดาวและ b มีไม่ใส่ผักชี. Fault A ถ้าแสดง 105 ให้ระบุส่วนต่าง −10 และผิด clause ราคา; fault B ต้องตรวจพบคู่ตัวเลือกผิดทั้งสองจาน แม้ยอดรวมยัง 115. ระบบที่ให้ผลผิดเหล่านี้ไม่ผ่าน assertion นั้น; การตรวจจับ fault เป็นผลของตัวตรวจ ไม่ใช่ผลระบบผ่าน
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงใบครัวอย่างน้อย 19 จาก 20 ใบตาม AC ใน TS-US-04-1; ชุด fault สองจานแยกจาก 20 ใบและไม่ใช้แทนสัดส่วนดังกล่าว. ความครบ configuration และราคาเพิ่มก่อนยืนยันตรวจแยกตาม AC
- สมมติฐาน/ข้อค้าง: คง Q-04 และ TS-US-04-3: required/conflict/จำนวนค่าที่เลือกได้ไม่มี oracle; customer ส่งเจ้าของข้อกำหนดตัดสิน. คู่เมนูและราคาเป็น fixture ไม่มีการตั้งกฎ required หรือการรับรองสารก่อแพ้
- Status: MOCK_NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-05-1"></a>

## TS-US-05-1 — รับออเดอร์ กำลังทำ และเสร็จแล้วใน mock ใบเดียวกัน

- US: US-05
- เจ้าของ: customer
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: นับจากพนักงานครัวกดปุ่มเปลี่ยนสถานะ จนถึงหน้าจอลูกค้าที่โต๊ะแสดงสถานะใหม่โดยไม่รีเฟรช ภายใน 5 วินาทีบน LAN ในร้าน ในอย่างน้อย 18 จาก 20 ครั้งของชุดทดสอบ
- clause ที่ตรวจ: F05: แสดงสถานะใหม่ของออเดอร์; ส่วนไร้การรีเฟรชข้ามอุปกรณ์แยก N02
- FR / Flow / Screen: FR-05; NFR-02 → MRG-05 → SCR-04, SCR-06; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: auto ตรวจเฉพาะพฤติกรรมจำลองผ่าน UI/DOM; ไม่พิสูจน์ QR, LAN/Wi‑Fi, Security, Load, Availability, server log หรือการชำระเงินจริง
- Precondition/reset: R0 แล้ว O m01 หนึ่งใบ; จด order ID; ไม่มีการ reload ระหว่างบทบาท
- Test data: โต๊ะ 01; m01=50; ลำดับ รับออเดอร์ → กำลังทำ → เสร็จแล้ว เป็น fixture
- data-testid และ scope: C: order-id, customer-order-status; K(order ID): btn-status-next; G/K0 ตามส่วนตั้งต้น; คำย่อ G/C/K/F/R/I/M และขั้น O/K0/F0/M0 ตามส่วน Precondition และ scope ที่ใช้ซ้ำ
- ขั้นตอน:

  1. หลัง O ตรวจ customer-order-status=รับออเดอร์
  2. เข้า K0 กด btn-status-next ใน K ของ ID นั้นครั้งเดียว กลับ C ตรวจ กำลังทำ
  3. เข้า K0 ใหม่ กดอีกครั้งเฉพาะใบเดิม กลับ C ตรวจ เสร็จแล้ว; ตลอดขั้นไม่ reload

- Expected result: ลูกค้าเห็นทั้งสามชื่อและ order-id เดิมตาม fixture; ต่อจาก TS-US-05-101 ที่ตรวจเพียงกำลังทำ; การกลับแท็บลูกค้าเป็นการ render ในหน่วยความจำเดียว ไม่พิสูจน์รับ event บนหน้าที่เปิดค้าง
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงข้อความ AC ต้นฉบับเต็มของ US-05 ในรายการนี้ทุกตัวเลข/สูตร/หน่วย/สัดส่วน; ตารางแยก assertions ระบุประชากรที่ต้องเก็บ. ชุดย่อยหรือจำนวน fixture ใน Test data ไม่ใช้แทนประชากรนั้น; assertion เฉพาะข้อผิดพลาดที่ไม่มีกลุ่มตัวอย่างใน AC ไม่เพิ่มเกณฑ์จำนวนเอง. ทุกเกณฑ์ระบบจริงยังไม่ได้ทดสอบ
- สมมติฐาน/ข้อค้าง: Q-05/DI-07: ไม่แมป เสร็จแล้ว เป็น พร้อมเสิร์ฟ ให้ US-07 เอง
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-05-2"></a>

## TS-US-05-2 — หน้าลูกค้าเปิดค้างรับสถานะบน LAN 20 ครั้ง

- US: US-05
- เจ้าของ: customer
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: นับจากพนักงานครัวกดปุ่มเปลี่ยนสถานะ จนถึงหน้าจอลูกค้าที่โต๊ะแสดงสถานะใหม่โดยไม่รีเฟรช ภายใน 5 วินาทีบน LAN ในร้าน ในอย่างน้อย 18 จาก 20 ครั้งของชุดทดสอบ
- clause ที่ตรวจ: F05 + N02: ไม่รีเฟรช; ครัวกดถึงลูกค้าแสดงสถานะใหม่ ≤5 วินาที อย่างน้อย 18 จาก 20 ครั้ง
- FR / Flow / Screen: FR-05; NFR-02 → MRG-05 → SCR-04, SCR-06; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: mock-not-testable: UI/ข้อมูลหรือระบบจริงที่จำเป็นยังไม่มีตาม precondition; ไม่ใช้การอ่าน source หรือคลิก mock แทน AC ระบบจริง
- Precondition/reset: BLOCKED: ต้องมีระบบจริงและอุปกรณ์ครัว/ลูกค้าแยกกันบน LAN ร้าน พร้อมหลักฐานเวลาสองปลายทาง
- Test data: ออเดอร์ทดสอบ 10 ใบ ใบละ 2 ครั้งเปลี่ยนสถานะ รวม 20 ครั้ง; การแจกแจงนี้เป็นแผนชุดข้อมูล ไม่เพิ่ม AC
- data-testid และ scope: C: customer-order-status และ K(order ID): btn-status-next เป็น mock counterparts; selector ระบบจริง MISSING; คำย่อ G/C/K/F/R/I/M และขั้น O/K0/F0/M0 ตามส่วน Precondition และ scope ที่ใช้ซ้ำ
- ขั้นตอน:

  1. ให้ลูกค้าเปิดออเดอร์เป้าหมายค้างไว้ ไม่เปลี่ยนบทบาท ไม่ refresh และไม่เปิดหน้าใหม่
  2. ครัวกดเปลี่ยนสถานะ บันทึก t0 และ t1 ที่หน้าลูกค้าแสดงสถานะใหม่ของ ID เดียวกัน ทำครบ 20 ครั้ง
  3. นับครั้งที่สถานะตรงโดยไม่ refresh และ t1−t0 ≤5 วินาที; เก็บครั้งที่ไม่อัปเดตไว้ด้วย

- Expected result: อย่างน้อย 18 จาก 20 ครั้งแสดงสถานะใหม่ภายใน 5 วินาทีบน LAN โดยไม่รีเฟรช; การสลับบทบาทใน mock ไม่ใช่หลักฐานของชุดนี้
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงข้อความ AC ต้นฉบับเต็มของ US-05 ในรายการนี้ทุกตัวเลข/สูตร/หน่วย/สัดส่วน; ตารางแยก assertions ระบุประชากรที่ต้องเก็บ. ชุดย่อยหรือจำนวน fixture ใน Test data ไม่ใช้แทนประชากรนั้น; assertion เฉพาะข้อผิดพลาดที่ไม่มีกลุ่มตัวอย่างใน AC ไม่เพิ่มเกณฑ์จำนวนเอง. ทุกเกณฑ์ระบบจริงยังไม่ได้ทดสอบ
- สมมติฐาน/ข้อค้าง: Q-05: ชื่อสถานะยังคงตาม US-05; ไม่ใช้สถานะเงินแทนสถานะอาหาร
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-05-3"></a>

## TS-US-05-3 — เครือข่ายขาดขณะครัวเปลี่ยนสถานะ

- US: US-05
- เจ้าของ: customer
- ประเภท: ข้อยกเว้น
- AC ต้นฉบับเต็ม: นับจากพนักงานครัวกดปุ่มเปลี่ยนสถานะ จนถึงหน้าจอลูกค้าที่โต๊ะแสดงสถานะใหม่โดยไม่รีเฟรช ภายใน 5 วินาทีบน LAN ในร้าน ในอย่างน้อย 18 จาก 20 ครั้งของชุดทดสอบ
- clause ที่ตรวจ: ข้อยกเว้น F05/N02; การแจ้ง disconnected และ resync ไม่ระบุใน AC
- FR / Flow / Screen: FR-05; NFR-02 → MRG-05 → SCR-04, SCR-06; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: mock-not-testable: UI/ข้อมูลหรือระบบจริงที่จำเป็นยังไม่มีตาม precondition; ไม่ใช้การอ่าน source หรือคลิก mock แทน AC ระบบจริง
- Precondition/reset: BLOCKED: รอข้อตกลง recovery และระบบจริงหลายอุปกรณ์; แยกชุด fault injection ออกจาก LAN ปกติ 20 ครั้ง
- Test data: ออเดอร์จำลองหนึ่งใบ; ตัดเฉพาะการเชื่อมต่อหน้าลูกค้าระหว่างเปลี่ยนเป็นกำลังทำ แล้วเชื่อมใหม่
- data-testid และ scope: MISSING: selector connection/recovery; customer-order-status เป็นเพียงจุดสังเกต mock; คำย่อ G/C/K/F/R/I/M และขั้น O/K0/F0/M0 ตามส่วน Precondition และ scope ที่ใช้ซ้ำ
- ขั้นตอน:

  1. จดสถานะและ order ID ก่อนตัดการเชื่อมต่อหน้าลูกค้า
  2. ให้ครัวเปลี่ยนสถานะและเก็บเวลาที่เกิด event
  3. เชื่อมกลับและบันทึกข้อความ/สถานะ/ต้องรีเฟรชหรือไม่ แล้วเทียบข้อตกลง recovery เมื่อมี

- Expected result: เก็บสถานะที่สังเกตจริงและเวลาที่ขาดการเชื่อมต่อ; ไม่มี oracle สำหรับ retry/resync/offline message จึง BLOCKED; ไม่ประกาศผ่าน 5 วินาทีจาก mock
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงข้อความ AC ต้นฉบับเต็มของ US-05 ในรายการนี้ทุกตัวเลข/สูตร/หน่วย/สัดส่วน; ตารางแยก assertions ระบุประชากรที่ต้องเก็บ. ชุดย่อยหรือจำนวน fixture ใน Test data ไม่ใช้แทนประชากรนั้น; assertion เฉพาะข้อผิดพลาดที่ไม่มีกลุ่มตัวอย่างใน AC ไม่เพิ่มเกณฑ์จำนวนเอง. ทุกเกณฑ์ระบบจริงยังไม่ได้ทดสอบ
- สมมติฐาน/ข้อค้าง: สมมติฐาน recovery รอยืนยันร่วม Q-05; ไม่ตั้ง SLA หลังเชื่อมกลับเพิ่ม
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-05-4"></a>

## TS-US-05-4 — ตรวจสถานะค้างเมื่อระบบส่งอัปเดตช้าเกิน 5 วินาทีบน LAN

- US: US-05
- เจ้าของ: customer
- ประเภท: ข้อยกเว้น
- AC ต้นฉบับเต็ม: นับจากพนักงานครัวกดปุ่มเปลี่ยนสถานะ จนถึงหน้าจอลูกค้าที่โต๊ะแสดงสถานะใหม่โดยไม่รีเฟรช ภายใน 5 วินาทีบน LAN ในร้าน ในอย่างน้อย 18 จาก 20 ครั้งของชุดทดสอบ
- clause ที่ตรวจ: จุดเริ่มครัวกดถึงหน้าลูกค้าแสดงสถานะใหม่โดยไม่รีเฟรช ภายใน 5 วินาที อย่างน้อย 18 จาก 20 ครั้ง
- FR / Flow / Screen: FR-05; NFR-02 → MRG-05 → SCR-04, SCR-06; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: แก้ D02 เชิงออกแบบ; ต้องมีระบบ/จุดแทรก fault และจุดสังเกตตาม Precondition ซึ่งยังไม่มี จึง BLOCKED การรัน. เป็นแผนตรวจจับผลผิดด้วย oracle อิสระ ไม่ใช่การเปลี่ยนชื่อ happy path; ยังไม่ได้ทำ fault หรือรันทดสอบ
- Precondition/reset: BLOCKED การรัน: ต้องมีระบบหลายอุปกรณ์บน LAN ร้านและตัวหน่วงที่ส่วนส่งสถานะของระบบ ไม่ตัดเครือข่าย; ต้องมีการบันทึกภาพครัว/ลูกค้าและนาฬิกาอ้างอิงเดียวกัน พร้อมตรวจว่าตัวหน่วงรับเหตุการณ์ ID ที่ต้องการจริง
- Test data: 10 ออเดอร์จำลอง ใบละ 2 การเปลี่ยนสถานะ รวม 20 ครั้ง ตาม TS-US-05-2; ลำดับรับออเดอร์→กำลังทำ→เสร็จแล้วใช้เฉพาะ fixture. ระบุหมายเลขการกด 1–20 และ order ID ก่อนเริ่ม; หน่วงเฉพาะครั้ง 1, 3, 5 จน t0+6 วินาที

- data-testid และ scope: MISSING: selector และจุดหน่วงระบบจริง; customer-order-status/btn-status-next เป็น counterparts ของ mock เท่านั้น; จุดสังเกตคือหน้าลูกค้าออเดอร์เดียวกันที่เปิดค้าง
- ขั้นตอน:

  1. ทำ control 20 ครั้งโดยไม่หน่วง เก็บ t0 ขณะครัวกดและ t1 เฟรมแรกที่ลูกค้าเห็นสถานะใหม่ของ ID เดียวกัน; หน้าลูกค้าค้างตลอด ไม่ refresh ไม่สลับบทบาท
  2. reset แล้วทำชุด fault 20 ครั้ง: ตัวหน่วงพักการเผยแพร่สถานะของครั้ง 1/3/5 จน t0+6 วินาที รวมทาง push/poll ที่อาจส่งสถานะเดียวกัน; LAN ยังเชื่อมและหน้าลูกค้าเปิดค้าง เก็บร่องรอยรับ/ปล่อยเหตุการณ์เพื่อตรวจว่า fault ถูกกระตุ้น
  3. บันทึกสถานะที่ t0+5 วินาที และต่อเนื่องจนเห็นสถานะใหม่ จับ t1−t0; ถ้ายังเก่าเมื่อเกิน 5 วินาทีให้นับครั้งนั้นไม่เข้าเกณฑ์ แม้ภายหลังจะอัปเดต
  4. นับจากทั้ง 20 ครั้งโดยไม่ตัดสามครั้งที่หน่วงออก; ถ้าตัวหน่วงไม่เกิดผลให้รายงาน setup ไม่สำเร็จและไม่อ้างว่าจับ fault ได้; ปิดตัวหน่วงแล้วทำ control ใหม่

- Expected result: แต่ละครั้งที่เข้าเกณฑ์ต้องเห็นสถานะใหม่ของ order ID เดียวกันโดยไม่รีเฟรชและ t1−t0≤5 วินาที; ถ้าหน่วงได้ตามแผน สามครั้งแรกที่ระบุจะยังเก่าเกินเกณฑ์และแม้อีก 17 ครั้งเข้าเกณฑ์ทั้งหมดก็ได้สูงสุด 17/20 ซึ่งต่ำกว่า 18/20. ค่า 6 วินาทีใช้สร้างเหตุผิดปกติ ไม่ใช่ SLA ใหม่; ไม่เรียกผลจับ delay ว่าระบบผ่าน AC
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: ชุด control และชุด fault แยกกัน ชุดละ 20 ครั้ง; AC เดิมอย่างน้อย 18 จาก 20 ครั้ง ภายใน 5 วินาทีบน LAN. ยังไม่มีผลวัดจริงทั้งสองชุด
- สมมติฐาน/ข้อค้าง: คง TS-US-05-3 และ Q-05 เรื่องเครือข่ายขาด/retry/resync; customer กับเจ้าของข้อกำหนดตัดสิน recovery; ผู้จัดระบบเตรียมจุดหน่วง/หลักฐานเวลา. ไม่เพิ่ม SLA หลัง reconnect และไม่เทียบเสร็จแล้วกับพร้อมเสิร์ฟ
- Status: MOCK_NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-06-1"></a>

## TS-US-06-1 — วัตถุดิบหมดทำให้มีทั้งป้ายและปุ่มปิด

- US: US-06
- เจ้าของ: customer
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: นับจากพนักงานครัวกด “วัตถุดิบหมด” จนถึงหน้าลูกค้าแสดงป้าย “หมด” และปุ่มสั่งถูกปิด ภายใน 10 วินาทีบน LAN ในร้าน ในอย่างน้อย 9 จาก 10 ครั้ง และเมื่อพยายามสั่งเมนูที่ปิดแล้ว ระบบปฏิเสธพร้อมข้อความแจ้ง
- clause ที่ตรวจ: F06a: แสดงป้าย หมด และปุ่มสั่งถูกปิดทั้งสองอย่าง
- FR / Flow / Screen: FR-06; NFR-03 → MRG-08, MRG-09, MRG-18 → SCR-01, SCR-07; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: auto ตรวจเฉพาะพฤติกรรมจำลองผ่าน UI/DOM; ไม่พิสูจน์ QR, LAN/Wi‑Fi, Security, Load, Availability, server log หรือการชำระเงินจริง
- Precondition/reset: R0; เปิด m01 ให้เห็นว่าสั่งได้ก่อนทำ stock change; mapping chicken ใช้ทั้งจานตาม seed
- Test data: ingredient chicken; เมนู m01 กะเพราไก่ 50 บาท
- data-testid และ scope: C: menu-list > menu-item-m01, btn-add-item เมื่อรายละเอียด m01 เปิด; K0: ingredient-select, btn-out-of-stock, ingredient-status; คำย่อ G/C/K/F/R/I/M และขั้น O/K0/F0/M0 ตามส่วน Precondition และ scope ที่ใช้ซ้ำ
- ขั้นตอน:

  1. เปิดเมนูและเลือก m01 ตรวจปุ่มเมนูและ btn-add-item ใช้งานได้ก่อน
  2. เข้า K0 เลือก ingredient-select=chicken กด btn-out-of-stock
  3. กลับ C ตรวจ menu-item-m01 มีคำว่า หมด และ disabled; ถ้ารายละเอียด m01 ยังแสดงตรวจ btn-add-item disabled ด้วย

- Expected result: ป้าย หมด และปุ่มเลือกสั่ง m01 ถูกปิดร่วมกัน; ไม่ยอมให้ผ่านจากป้ายอย่างเดียวหรือ disabled อย่างเดียว; ไม่มีการวัด 10 วินาที LAN ใน scenario นี้
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงข้อความ AC ต้นฉบับเต็มของ US-06 ในรายการนี้ทุกตัวเลข/สูตร/หน่วย/สัดส่วน; ตารางแยก assertions ระบุประชากรที่ต้องเก็บ. ชุดย่อยหรือจำนวน fixture ใน Test data ไม่ใช้แทนประชากรนั้น; assertion เฉพาะข้อผิดพลาดที่ไม่มีกลุ่มตัวอย่างใน AC ไม่เพิ่มเกณฑ์จำนวนเอง. ทุกเกณฑ์ระบบจริงยังไม่ได้ทดสอบ
- สมมติฐาน/ข้อค้าง: แมป seed เป็น fixture; หมายเหตุ ค. ยังขาด (DI-02); ไม่เหมารวมตัวเลือกอย่าง egg ว่าต้องปิดทั้ง m01
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-06-2"></a>

## TS-US-06-2 — ปฏิเสธตะกร้าเก่าที่มีจานหมดโดยไม่เพิ่มใบครัว

- US: US-06
- เจ้าของ: customer
- ประเภท: ผิดพลาด
- AC ต้นฉบับเต็ม: นับจากพนักงานครัวกด “วัตถุดิบหมด” จนถึงหน้าลูกค้าแสดงป้าย “หมด” และปุ่มสั่งถูกปิด ภายใน 10 วินาทีบน LAN ในร้าน ในอย่างน้อย 9 จาก 10 ครั้ง และเมื่อพยายามสั่งเมนูที่ปิดแล้ว ระบบปฏิเสธพร้อมข้อความแจ้ง
- clause ที่ตรวจ: F06b: พยายามสั่งเมนูที่ปิดแล้วต้องปฏิเสธพร้อมข้อความ
- FR / Flow / Screen: FR-06; NFR-03 → MRG-08, MRG-09, MRG-18 → SCR-01, SCR-07; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: auto ตรวจเฉพาะพฤติกรรมจำลองผ่าน UI/DOM; ไม่พิสูจน์ QR, LAN/Wi‑Fi, Security, Load, Availability, server log หรือการชำระเงินจริง
- Precondition/reset: R0; ตะกร้ามี m01 และ m02 ก่อนครัวกดหมด; ยังไม่มีออเดอร์ในคิว
- Test data: m01=50 + m02=55 รวม 105 บาท; จากนั้น chicken หมด; m02 ยังสั่งได้
- data-testid และ scope: C: menu-item-m01, menu-item-m02, btn-add-item, cart-count, cart-total, btn-submit-order, order-message, order-id; K: kitchen-queue และ kitchen-order ทุกใบก่อน/หลัง; K0 stock controls; คำย่อ G/C/K/F/R/I/M และขั้น O/K0/F0/M0 ตามส่วน Precondition และ scope ที่ใช้ซ้ำ
- ขั้นตอน:

  1. เพิ่มทั้งสองจานยังไม่ยืนยัน และจดตะกร้า/คิวเริ่มต้น
  2. เข้า K0 กด chicken หมด; กลับลูกค้ากด btn-submit-order หลังปิดแล้ว
  3. ตรวจ order-message มีการปฏิเสธ/หมด; เข้า K0 เปรียบเทียบจำนวน kitchen-order ก่อนหลัง; ตรวจไม่มีออเดอร์ย่อยของ m02 ถูกเพิ่มเอง

- Expected result: ปฏิเสธคำสั่งที่มี m01 ที่ปิดพร้อมข้อความ; mock คิวว่างและไม่มี order ID ใหม่/ไม่ส่งบางส่วน เป็นข้อกำหนด fixture; TS-US-06-101 ตรวจข้อความในตะกร้าจานเดียว ไม่ตรวจ no-new-order และตะกร้าผสมนี้
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงข้อความ AC ต้นฉบับเต็มของ US-06 ในรายการนี้ทุกตัวเลข/สูตร/หน่วย/สัดส่วน; ตารางแยก assertions ระบุประชากรที่ต้องเก็บ. ชุดย่อยหรือจำนวน fixture ใน Test data ไม่ใช้แทนประชากรนั้น; assertion เฉพาะข้อผิดพลาดที่ไม่มีกลุ่มตัวอย่างใน AC ไม่เพิ่มเกณฑ์จำนวนเอง. ทุกเกณฑ์ระบบจริงยังไม่ได้ทดสอบ
- สมมติฐาน/ข้อค้าง: Q-06: AC ระบุการปฏิเสธเมนูปิด แต่การเก็บตะกร้า/atomic ทั้งตะกร้า/คำพูดเต็ม/เหตุการณ์ชนกันยังรอยืนยัน; ไม่สรุปนโยบายตะกร้าผสมของร้านจาก fixture
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-06-3"></a>

## TS-US-06-3 — เผยแพร่หมดบน LAN และปฏิเสธคำสั่งจริง

- US: US-06
- เจ้าของ: customer
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: นับจากพนักงานครัวกด “วัตถุดิบหมด” จนถึงหน้าลูกค้าแสดงป้าย “หมด” และปุ่มสั่งถูกปิด ภายใน 10 วินาทีบน LAN ในร้าน ในอย่างน้อย 9 จาก 10 ครั้ง และเมื่อพยายามสั่งเมนูที่ปิดแล้ว ระบบปฏิเสธพร้อมข้อความแจ้ง
- clause ที่ตรวจ: F06a/N03: ≤10 วินาทีอย่างน้อย 9 จาก 10 ครั้ง; F06b: ปฏิเสธพร้อมข้อความ
- FR / Flow / Screen: FR-06; NFR-03 → MRG-08, MRG-09, MRG-18 → SCR-01, SCR-07; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: mock-not-testable: UI/ข้อมูลหรือระบบจริงที่จำเป็นยังไม่มีตาม precondition; ไม่ใช้การอ่าน source หรือคลิก mock แทน AC ระบบจริง
- Precondition/reset: BLOCKED: ต้องมีระบบจริงสองอุปกรณ์บน LAN และวิธีส่งคำสั่งทดสอบที่ยืนยันว่าเกิดหลังปิดแล้ว
- Test data: 10 เหตุการณ์ stock change; คืน chicken เป็นมีและตรวจ m01 สั่งได้ก่อนทุกครั้ง; คำสั่งเก่าทดสอบใช้ m01 หนึ่งจาน
- data-testid และ scope: C/K ของ TS-US-06-1/2 เป็น counterparts; endpoint และ selector ระบบจริง MISSING; คำย่อ G/C/K/F/R/I/M และขั้น O/K0/F0/M0 ตามส่วน Precondition และ scope ที่ใช้ซ้ำ
- ขั้นตอน:

  1. แต่ละครั้งเตรียม stock เป็นมีและลูกค้าเห็น m01 สั่งได้
  2. ครัวกดหมดจด t0; จด t1 เมื่อหน้าลูกค้ามีทั้งป้าย หมด และปุ่มปิด; ทำครบ 10 ครั้ง
  3. ส่งคำสั่งของเมนูที่ยืนยันว่าปิดแล้ว ตรวจผลปฏิเสธและข้อความจากระบบ; เก็บ order log ประกอบ ไม่อ้างปุ่ม disabled แทนการปฏิเสธ

- Expected result: อย่างน้อย 9 จาก 10 ครั้ง t1−t0 ≤10 วินาทีบน LAN และคำสั่งเมนูปิดถูกปฏิเสธพร้อมข้อความ; ตัวหาร 10 ครั้งใช้กับการเผยแพร่ ไม่ใช้ลดข้อปฏิเสธ
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงข้อความ AC ต้นฉบับเต็มของ US-06 ในรายการนี้ทุกตัวเลข/สูตร/หน่วย/สัดส่วน; ตารางแยก assertions ระบุประชากรที่ต้องเก็บ. ชุดย่อยหรือจำนวน fixture ใน Test data ไม่ใช้แทนประชากรนั้น; assertion เฉพาะข้อผิดพลาดที่ไม่มีกลุ่มตัวอย่างใน AC ไม่เพิ่มเกณฑ์จำนวนเอง. ทุกเกณฑ์ระบบจริงยังไม่ได้ทดสอบ
- สมมติฐาน/ข้อค้าง: Q-06: ไม่รวมคำสั่งชนพร้อม stock เป็นผลที่ตัดสินได้จนกำหนดลำดับเหตุการณ์
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-07-1"></a>

## TS-US-07-1 — สูตรเวลารอก่อนยืนยันทุกออเดอร์

- US: US-07
- เจ้าของ: customer
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: หน้ายืนยันสั่งแสดงเวลารอโดยประมาณทุกออเดอร์ คำนวณจากสูตร: (จำนวนออเดอร์ค้างในคิวครัวที่ยังไม่ “พร้อมเสิร์ฟ” × เวลาเฉลี่ยต่อออเดอร์ 7 วันล่าสุด) + เวลาเฉลี่ยต่อเมนูของเมนูที่นานที่สุดในตะกร้า · เวลาจริงวัดจากจุดเริ่ม “ลูกค้ากดยืนยันสั่ง” ถึงจุดจบ “ครัวกดสถานะพร้อมเสิร์ฟ” (log ฝั่งเซิร์ฟเวอร์) · ช่วงเร่งด่วนนิยามเป็น 11:30–13:00 และ 17:30–19:30 · ในออเดอร์ช่วงเร่งด่วนของ 1 วันทดสอบ ค่าประมาณคลาดเคลื่อนจากเวลาจริงไม่เกิน 10 นาทีในอย่างน้อย 80% ของออเดอร์ (ดูหมายเหตุ ช.)
- clause ที่ตรวจ: F07a: แสดงทุกออเดอร์ก่อนยืนยัน; คูณจำนวนคิวที่ยังไม่พร้อมเสิร์ฟด้วยค่าเฉลี่ยต่อออเดอร์ 7 วันล่าสุด แล้วบวกค่าเฉลี่ยเมนูที่นานที่สุด
- FR / Flow / Screen: FR-07; NFR-04 → MRG-03, MRG-04 → SCR-03; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: mock-not-testable: UI/ข้อมูลหรือระบบจริงที่จำเป็นยังไม่มีตาม precondition; ไม่ใช้การอ่าน source หรือคลิก mock แทน AC ระบบจริง
- Precondition/reset: BLOCKED: UI v2 มีเพียง ยังประมาณไม่ได้ ไม่มี ETA selector/ข้อมูล 7 วัน/ตัวคำนวณ; ต้องมีระบบรองรับและนิยามค่าเฉลี่ยตาม Q-07
- Test data: ข้อมูลจำลองสำหรับตรวจ arithmetic: ค่าเฉลี่ยต่อออเดอร์ 7 วันล่าสุด=4 นาที; ค่าเฉลี่ย m01=6, m02=9 นาที; คิวค้าง 0/1/3 ใบ และมีใบพร้อมเสิร์ฟอีก 2 ใบที่ต้องไม่นับ; ตะกร้า m01+m02
- data-testid และ scope: MISSING: data-testid สำหรับ ETA และค่าปัจจัย; SCR-03 มีในแบบแต่ HTML แสดงข้อความ placeholder; ห้ามใช้ capacity-message แทน ETA; คำย่อ G/C/K/F/R/I/M และขั้น O/K0/F0/M0 ตามส่วน Precondition และ scope ที่ใช้ซ้ำ
- ขั้นตอน:

  1. เมื่อระบบรองรับ ให้โหลดข้อมูลประวัติจำลองครบ 7 วันตามวิธีเฉลี่ยที่ยืนยัน และยืนยันค่าปัจจัย 4/6/9 ที่ใช้
  2. สร้างคิว 0, 1, 3 ใบที่ยังไม่พร้อมเสิร์ฟ รวมใบพร้อมเสิร์ฟ 2 ใบ; เปิดหน้ายืนยันแต่ละออเดอร์ด้วยตะกร้าสองเมนู
  3. ก่อนกดยืนยันบันทึกจำนวนคิว ค่าเฉลี่ย และ ETA; คำนวณอิสระแล้วเทียบค่าแสดงทุกออเดอร์ รวมตอนเปลี่ยนตะกร้าเหลือ m01

- Expected result: สำหรับตะกร้า m01+m02 ต้องได้ 9, 13, 21 นาทีตาม 0×4+9, 1×4+9, 3×4+9; ใบพร้อมเสิร์ฟไม่นับ; ตะกร้า m01 กับคิว 3 ได้ 18 นาที; ทุกออเดอร์ต้องมี ETA ก่อนยืนยันเมื่อข้อมูลครบ; เป็น expected ข้อมูลจำลอง ไม่ใช่ผลรัน
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงข้อความ AC ต้นฉบับเต็มของ US-07 ในรายการนี้ทุกตัวเลข/สูตร/หน่วย/สัดส่วน; ตารางแยก assertions ระบุประชากรที่ต้องเก็บ. ชุดย่อยหรือจำนวน fixture ใน Test data ไม่ใช้แทนประชากรนั้น; assertion เฉพาะข้อผิดพลาดที่ไม่มีกลุ่มตัวอย่างใน AC ไม่เพิ่มเกณฑ์จำนวนเอง. ทุกเกณฑ์ระบบจริงยังไม่ได้ทดสอบ
- สมมติฐาน/ข้อค้าง: Q-07/DI-03/DI-07: ไม่มีหมายเหตุ ช., วิธีสร้างค่าเฉลี่ย/ปัดเศษ/การเลือกเมนูนานที่สุด; ค่าเฉลี่ยที่กำหนดใช้ตรวจสูตร ไม่รับรองวิธีคำนวณจาก raw history
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-07-2"></a>

## TS-US-07-2 — ความแม่นยำช่วงเร่งด่วนครบหนึ่งวันจาก log เซิร์ฟเวอร์

- US: US-07
- เจ้าของ: customer
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: หน้ายืนยันสั่งแสดงเวลารอโดยประมาณทุกออเดอร์ คำนวณจากสูตร: (จำนวนออเดอร์ค้างในคิวครัวที่ยังไม่ “พร้อมเสิร์ฟ” × เวลาเฉลี่ยต่อออเดอร์ 7 วันล่าสุด) + เวลาเฉลี่ยต่อเมนูของเมนูที่นานที่สุดในตะกร้า · เวลาจริงวัดจากจุดเริ่ม “ลูกค้ากดยืนยันสั่ง” ถึงจุดจบ “ครัวกดสถานะพร้อมเสิร์ฟ” (log ฝั่งเซิร์ฟเวอร์) · ช่วงเร่งด่วนนิยามเป็น 11:30–13:00 และ 17:30–19:30 · ในออเดอร์ช่วงเร่งด่วนของ 1 วันทดสอบ ค่าประมาณคลาดเคลื่อนจากเวลาจริงไม่เกิน 10 นาทีในอย่างน้อย 80% ของออเดอร์ (ดูหมายเหตุ ช.)
- clause ที่ตรวจ: F07b/N04: จุดเริ่ม–จบ log; ช่วง 11:30–13:00 และ 17:30–19:30; 1 วัน; คลาดเคลื่อนไม่เกิน 10 นาทีอย่างน้อย 80%
- FR / Flow / Screen: FR-07; NFR-04 → MRG-03, MRG-04 → SCR-03; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: mock-not-testable: UI/ข้อมูลหรือระบบจริงที่จำเป็นยังไม่มีตาม precondition; ไม่ใช้การอ่าน source หรือคลิก mock แทน AC ระบบจริง
- Precondition/reset: BLOCKED: ไม่มี server log/ระบบ ETA/ข้อมูล 7 วัน; ต้องตอบ Q-05/Q-07 เรื่องพร้อมเสิร์ฟ ประชากร และขอบช่วงก่อนรับรอง
- Test data: ใช้ทุกออเดอร์จำลองในช่วงเร่งด่วนของวันทดสอบเดียว วันที่จะกำหนดเมื่อมีระบบ; จำนวนออเดอร์ D ยังไม่มีข้อมูล ไม่กำหนดตัวหาร 20 เอง
- data-testid และ scope: MISSING: ETA selector/server log interface; capacity-message และ customer-order-status ไม่ใช้แทน log พร้อมเสิร์ฟ; คำย่อ G/C/K/F/R/I/M และขั้น O/K0/F0/M0 ตามส่วน Precondition และ scope ที่ใช้ซ้ำ
- ขั้นตอน:

  1. บันทึก ETA และปัจจัยก่อนยืนยันของทุกออเดอร์ พร้อมเวลา/ID โดยไม่คัดเฉพาะใบที่สะดวก
  2. เก็บ log ฝั่งเซิร์ฟเวอร์เมื่อลูกค้ากดยืนยันและเมื่อครัวกดพร้อมเสิร์ฟ จับคู่ ID แล้วคำนวณเวลาจริง
  3. จัดประชากรช่วง 11:30–13:00 และ 17:30–19:30 ใน 1 วันตามนิยามที่ยืนยัน ตรวจรายการที่ขอบช่วงด้วย
  4. คำนวณ abs(ETA−เวลาจริง) ต่อใบ; นับ K ที่ ≤10 นาที; คำนวณ 100×K/D และเทียบ ≥80%; บันทึกใบไม่จบ/ไม่มี log ไม่ลบทิ้ง

- Expected result: เวลาจริงมาจากสอง event ฝั่งเซิร์ฟเวอร์ตาม AC; สัดส่วนความคลาดเคลื่อนไม่เกิน 10 นาทีต้องอย่างน้อย 80% ของทุกออเดอร์ในช่วงของ 1 วัน; D=0 หรือ log ไม่ครบให้ BLOCKED/ประเมินไม่ได้
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงข้อความ AC ต้นฉบับเต็มของ US-07 ในรายการนี้ทุกตัวเลข/สูตร/หน่วย/สัดส่วน; ตารางแยก assertions ระบุประชากรที่ต้องเก็บ. ชุดย่อยหรือจำนวน fixture ใน Test data ไม่ใช้แทนประชากรนั้น; assertion เฉพาะข้อผิดพลาดที่ไม่มีกลุ่มตัวอย่างใน AC ไม่เพิ่มเกณฑ์จำนวนเอง. ทุกเกณฑ์ระบบจริงยังไม่ได้ทดสอบ
- สมมติฐาน/ข้อค้าง: Q-07: ไม่มีข้อมูลวัน/จำนวนออเดอร์/นโยบายใบไม่จบ; DI-06 ห้ามแทนช่วงนี้ด้วย 11:30–13:30 ของ US-21; DI-07 ห้ามสมมติ เสร็จแล้ว=พร้อมเสิร์ฟ
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-07-3"></a>

## TS-US-07-3 — ไม่มีประวัติ 7 วันหรือไม่มีค่าเฉลี่ยของเมนู

- US: US-07
- เจ้าของ: customer
- ประเภท: ข้อยกเว้น
- AC ต้นฉบับเต็ม: หน้ายืนยันสั่งแสดงเวลารอโดยประมาณทุกออเดอร์ คำนวณจากสูตร: (จำนวนออเดอร์ค้างในคิวครัวที่ยังไม่ “พร้อมเสิร์ฟ” × เวลาเฉลี่ยต่อออเดอร์ 7 วันล่าสุด) + เวลาเฉลี่ยต่อเมนูของเมนูที่นานที่สุดในตะกร้า · เวลาจริงวัดจากจุดเริ่ม “ลูกค้ากดยืนยันสั่ง” ถึงจุดจบ “ครัวกดสถานะพร้อมเสิร์ฟ” (log ฝั่งเซิร์ฟเวอร์) · ช่วงเร่งด่วนนิยามเป็น 11:30–13:00 และ 17:30–19:30 · ในออเดอร์ช่วงเร่งด่วนของ 1 วันทดสอบ ค่าประมาณคลาดเคลื่อนจากเวลาจริงไม่เกิน 10 นาทีในอย่างน้อย 80% ของออเดอร์ (ดูหมายเหตุ ช.)
- clause ที่ตรวจ: ข้อยกเว้น F07a/N04 เมื่อปัจจัยในสูตรขาด; ต้นฉบับไม่กำหนด fallback
- FR / Flow / Screen: FR-07; NFR-04 → MRG-03, MRG-04 → SCR-03; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: mock-not-testable: UI/ข้อมูลหรือระบบจริงที่จำเป็นยังไม่มีตาม precondition; ไม่ใช้การอ่าน source หรือคลิก mock แทน AC ระบบจริง
- Precondition/reset: BLOCKED: ต้องตอบ Q-07 และมีระบบ ETA; ไม่เติมค่าจำลองลง input เดิม
- Test data: กรณีประวัติ 7 วันว่าง และอีกกรณีมีค่าเฉลี่ยต่อออเดอร์แต่ไม่มีค่าเฉลี่ย m02; ตะกร้า m02 จำนวน 1
- data-testid และ scope: MISSING: selector สูตร/กรณีข้อมูลขาด; ข้อความ ยังประมาณไม่ได้ ใน C เป็นข้อจำกัด mock เท่านั้น; คำย่อ G/C/K/F/R/I/M และขั้น O/K0/F0/M0 ตามส่วน Precondition และ scope ที่ใช้ซ้ำ
- ขั้นตอน:

  1. เตรียมแต่ละชุดข้อมูลขาดบนระบบทดสอบเมื่อรองรับ
  2. เปิดก่อนยืนยันแล้วเก็บค่า/ข้อความที่แสดงและการยอมให้สั่ง
  3. เมื่อมีคำตอบเทียบวิธี fallback กับนโยบายที่ยืนยัน; ตรวจว่าไม่ได้แอบแทนข้อมูล 7 วันด้วย X ความจุ

- Expected result: ยังไม่มี oracle ว่าต้องแจ้งข้อความใด/ใช้ค่า default/ห้ามสั่ง จึง BLOCKED; ถ้าแสดงตัวเลขต้องอธิบายแหล่งปัจจัยตามนโยบายที่ยืนยัน; ไม่ถือ placeholder ของ mock ว่าผ่าน AC แสดง ETA ทุกออเดอร์
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงข้อความ AC ต้นฉบับเต็มของ US-07 ในรายการนี้ทุกตัวเลข/สูตร/หน่วย/สัดส่วน; ตารางแยก assertions ระบุประชากรที่ต้องเก็บ. ชุดย่อยหรือจำนวน fixture ใน Test data ไม่ใช้แทนประชากรนั้น; assertion เฉพาะข้อผิดพลาดที่ไม่มีกลุ่มตัวอย่างใน AC ไม่เพิ่มเกณฑ์จำนวนเอง. ทุกเกณฑ์ระบบจริงยังไม่ได้ทดสอบ
- สมมติฐาน/ข้อค้าง: Q-07/หมายเหตุ ช. ขาด; ไม่กำหนดเวลารอ 0 หรือ 10 นาทีเอง
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-07-4"></a>

## TS-US-07-4 — จับ ETA ที่นับใบพร้อมเสิร์ฟรวมในคิวจากประวัติครบ 7 วัน

- US: US-07
- เจ้าของ: customer
- ประเภท: ผิดพลาด
- AC ต้นฉบับเต็ม: หน้ายืนยันสั่งแสดงเวลารอโดยประมาณทุกออเดอร์ คำนวณจากสูตร: (จำนวนออเดอร์ค้างในคิวครัวที่ยังไม่ “พร้อมเสิร์ฟ” × เวลาเฉลี่ยต่อออเดอร์ 7 วันล่าสุด) + เวลาเฉลี่ยต่อเมนูของเมนูที่นานที่สุดในตะกร้า · เวลาจริงวัดจากจุดเริ่ม “ลูกค้ากดยืนยันสั่ง” ถึงจุดจบ “ครัวกดสถานะพร้อมเสิร์ฟ” (log ฝั่งเซิร์ฟเวอร์) · ช่วงเร่งด่วนนิยามเป็น 11:30–13:00 และ 17:30–19:30 · ในออเดอร์ช่วงเร่งด่วนของ 1 วันทดสอบ ค่าประมาณคลาดเคลื่อนจากเวลาจริงไม่เกิน 10 นาทีในอย่างน้อย 80% ของออเดอร์ (ดูหมายเหตุ ช.)
- clause ที่ตรวจ: ETA ก่อนยืนยันทุกออเดอร์; จำนวนคิวที่ยังไม่พร้อมเสิร์ฟ × ค่าเฉลี่ยต่อออเดอร์ 7 วันล่าสุด + ค่าเฉลี่ยเมนูนานที่สุดในตะกร้า
- FR / Flow / Screen: FR-07; NFR-04 → MRG-03, MRG-04 → SCR-03; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: แก้ D03 เชิงออกแบบ; ต้องมีระบบ/จุดแทรก fault และจุดสังเกตตาม Precondition ซึ่งยังไม่มี จึง BLOCKED การรัน. เป็นแผนตรวจจับผลผิดด้วย oracle อิสระ ไม่ใช่การเปลี่ยนชื่อ happy path; ยังไม่ได้ทำ fault หรือรันทดสอบ
- Precondition/reset: BLOCKED การรัน: ไม่มี ETA/ประวัติ/ตัวคำนวณหรือจุดแทรกค่าคิวใน Input; ต้องเตรียมระบบทดสอบที่อ่าน snapshot ปัจจัยและแทรกค่าจำนวนคิวก่อนคำนวณได้. ระบบทดสอบใช้วิธีเฉลี่ย fixture ที่เปิดเผยด้านล่าง ไม่มีข้อมูลขาด
- Test data: วันคำนวณจำลอง 2026-01-08 เวลา 12:00 +07:00; ประวัติ 2026-01-01 ถึง 2026-01-07 ทุกวันมี 2 ออเดอร์ (รวม 14): ใบ A ยืนยัน 12:00 พร้อมเสิร์ฟ 12:10 และเตรียมเมนู A 4 นาที; ใบ B ยืนยัน 12:20 พร้อมเสิร์ฟ 12:30 และเตรียมเมนู B 6 นาที. ใช้ค่าเฉลี่ยเลขคณิตไม่ถ่วงน้ำหนักเป็น fixture: ออเดอร์ 140/14=10 นาที, A=28/7=4 นาที, B=42/7=6 นาที. คิว snapshot มี q1/q2 ยังไม่พร้อมเสิร์ฟ และ q3/q4/q5 พร้อมเสิร์ฟแล้ว; ตะกร้า A+B อย่างละ 1. ป้าย q ไม่ใช่ ID API

- data-testid และ scope: MISSING: selector ETA, ประวัติ และจุดแทรกตัวกรองคิว; ต้องผูก q1–q5 กับ ID จริงของระบบทดสอบ; ไม่ใช้ capacity-message หรือ X แทน ETA
- ขั้นตอน:

  1. เตรียมประวัติทุกวันตามตารางสร้างข้อมูลข้างต้น ตรวจ log เริ่ม/จบและข้อมูลเวลาเมนูครบ 14 ใบ; คำนวณค่าเฉลี่ย 10/4/6 อิสระและยืนยัน snapshot ปัจจัยตรงก่อนเริ่ม
  2. control: สร้าง snapshot คิวห้าใบตามสถานะที่ระบุ เปิดก่อนยืนยัน A+B และจด ETA เทียบ 2×10+max(4,6)=26 นาที; เปลี่ยนตะกร้าเหลือ A เพื่อเทียบ 24 นาที โดยไม่ยืนยันให้คิวเพิ่ม
  3. fault: reset snapshot เดิม ให้ตัวแทรกที่จุดส่งผลตัวกรองคิวไปยังตัวคำนวณเปลี่ยนจำนวน 2 เป็น 5 ด้วยการรวม q3/q4/q5 โดยคงสถานะต้นทางและค่าเฉลี่ยเดิม; เก็บ input ก่อน/หลังและ ETA ที่แสดงบนหน้ายืนยัน A+B
  4. เทียบ ETA ที่แสดงกับ 26 จากสมุดคำนวณ ไม่คำนวณ oracle จากค่าคิวผิด 5; ปิดตัวแทรก เปิด snapshot เดิมใหม่เพื่อตรวจ control; ถ้ายังตรวจปัจจัยหรือสภาพแทรกไม่ได้ให้ BLOCKED การรัน

- Expected result: oracle fixture A+B=26 นาที และ A อย่างเดียว=24 นาที; ใบพร้อมเสิร์ฟสามใบต้องไม่เพิ่ม ETA. ถ้าส่งค่าคิวผิด 5 แล้วแสดง 56 นาที ตัวตรวจต้องชี้ส่วนต่าง +30 นาทีและการรวม q3/q4/q5 ผิด clause. ต้องแสดง ETA ก่อนยืนยันในทุกตะกร้าที่ตรวจเมื่อข้อมูลครบ; การตรวจสูตรนี้ไม่รับรองนโยบายเฉลี่ยจาก raw history ของร้าน
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: ประวัติครบ 7 วันตาม AC; fixture 14 ใบและ snapshot ย่อยไม่แทนทุกออเดอร์ช่วง 11:30–13:00 และ 17:30–19:30 ของ 1 วันทดสอบ หรือเกณฑ์คลาดเคลื่อนไม่เกิน 10 นาทีอย่างน้อย 80% ใน TS-US-07-2; คงจุดเริ่ม/จบ log เซิร์ฟเวอร์ตาม AC
- สมมติฐาน/ข้อค้าง: คง TS-US-07-3/Q-07/หมายเหตุ ช. และ Q-05: ไม่มีข้อมูล fallback วิธีเฉลี่ยจริง ปัดเศษ/ประชากร/สถานะ. customer ส่งเจ้าของข้อกำหนดตัดสิน; วิธีเฉลี่ยและ +07:00 นี้เป็น fixture เท่านั้น ไม่แมปเสร็จแล้ว=พร้อมเสิร์ฟ
- Status: MOCK_NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-08-1"></a>

## TS-US-08-1 — สรุปยอดและตัวเลือกวิธีจ่ายครบ 20 ใบ

- US: US-08
- เจ้าของ: customer
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: ยอดรวมบนหน้าสรุปของลูกค้าตรงกับยอดบนจอหน้าร้านในอย่างน้อย 19 จาก 20 ใบของชุดทดสอบ และเลือกวิธีจ่ายได้ 2 แบบทุกออเดอร์ · เมื่อเลือก PromptPay ออเดอร์อยู่สถานะ “ค้างจ่าย” จนพนักงานหน้าร้านยืนยันสลิป · ถ้าสลิปยังไม่ยืนยันภายใน 10 นาที หรือผู้จัดการร้านตั้งค่า “PromptPay ปิดใช้งาน” หน้าลูกค้าแสดงข้อความให้ชำระเงินสดที่หน้าร้าน และพนักงานหน้าร้านกด “รับเงินสด” หรือ “ยืนยันสลิป” เพื่อเปลี่ยนเป็น “จ่ายแล้ว” ได้ · ทดสอบ 3 กรณี (PromptPay ปกติ / ปิดใช้งาน / สลิปไม่ยืนยันเกิน 10 นาที) ผ่าน 3 จาก 3 (ดูหมายเหตุ ก.)
- clause ที่ตรวจ: F08a: ยอดลูกค้าตรงหน้าร้านอย่างน้อย 19 จาก 20 ใบ; F08b: เลือกวิธีจ่าย 2 แบบทุกออเดอร์
- FR / Flow / Screen: FR-08; NFR-17 → MRG-03, MRG-04, MRG-06, MRG-07, MRG-10, MRG-11, MRG-32, MRG-33 → SCR-03, SCR-05, SCR-09, SCR-16, SCR-08; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: auto ตรวจเฉพาะพฤติกรรมจำลองผ่าน UI/DOM; ไม่พิสูจน์ QR, LAN/Wi‑Fi, Security, Load, Availability, server log หรือการชำระเงินจริง
- Precondition/reset: R0; PromptPay เปิด; ไม่ยืนยันรับเงินจนเก็บค่าทั้งสองวิธีของแต่ละใบเสร็จ; สร้างทีละใบและเก็บก่อนใบถัดไปเพราะ C แสดงออเดอร์ล่าสุด
- Test data: 20 ใบวนชุด m01=50, m02=55, m01+ไข่=60, m01+ไข่และ m02=115 อย่างละ 5 ใบ
- data-testid และ scope: C: order-id, customer-adjusted-total, pay-cash, pay-promptpay, payment-status และข้อความรายการในส่วนติดตามล่าสุด; F(order ID): front-total, front-adjusted-total; G/F0/O; คำย่อ G/C/K/F/R/I/M และขั้น O/K0/F0/M0 ตามส่วน Precondition และ scope ที่ใช้ซ้ำ
- ขั้นตอน:

  1. แต่ละใบสร้างผ่าน O ตามข้อมูล ตรวจรายการ/ยอดก่อนยืนยันและจด order-id หลังยืนยัน
  2. ตรวจ customer-adjusted-total เทียบยอดที่คำนวณ เลือก pay-cash และ pay-promptpay ให้เห็นว่าทั้งสองเลือกได้ก่อนรับเงิน; เก็บสถานะ
  3. เข้า F0 ตรวจยอด F ของ ID เดียวกับลูกค้าและเทียบรายการ; เก็บผลก่อนสร้างใบถัดไป ทำครบ 20 ใบ

- Expected result: บันทึกผลยอดตรงทีละใบและเทียบอย่างน้อย 19 จาก 20; วิธีจ่ายสองแบบต้องเลือกได้ทุกใบทั้ง 20 ไม่ใช้ 19/20 ลดเกณฑ์นี้; ยังไม่มี adjustment จึงยอดเดิมและยอดปรับเท่ากัน; ไม่ใช้ cart-total หลังส่งแทนบิล
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงข้อความ AC ต้นฉบับเต็มของ US-08 ในรายการนี้ทุกตัวเลข/สูตร/หน่วย/สัดส่วน; ตารางแยก assertions ระบุประชากรที่ต้องเก็บ. ชุดย่อยหรือจำนวน fixture ใน Test data ไม่ใช้แทนประชากรนั้น; assertion เฉพาะข้อผิดพลาดที่ไม่มีกลุ่มตัวอย่างใน AC ไม่เพิ่มเกณฑ์จำนวนเอง. ทุกเกณฑ์ระบบจริงยังไม่ได้ทดสอบ
- สมมติฐาน/ข้อค้าง: Q-08: การเลือกสองแบบเมื่อ PromptPay ปิดยังรอคำตอบ; scenario นี้ระบุเปิดชัดเจน; mock ยอดล่าสุดระดับออเดอร์ไม่ยืนยันการรวมหลายออเดอร์ทั้ง session
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-08-2"></a>

## TS-US-08-2 — PromptPay ปกติค้างจ่ายจนหน้าร้านยืนยันสลิป

- US: US-08
- เจ้าของ: customer
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: ยอดรวมบนหน้าสรุปของลูกค้าตรงกับยอดบนจอหน้าร้านในอย่างน้อย 19 จาก 20 ใบของชุดทดสอบ และเลือกวิธีจ่ายได้ 2 แบบทุกออเดอร์ · เมื่อเลือก PromptPay ออเดอร์อยู่สถานะ “ค้างจ่าย” จนพนักงานหน้าร้านยืนยันสลิป · ถ้าสลิปยังไม่ยืนยันภายใน 10 นาที หรือผู้จัดการร้านตั้งค่า “PromptPay ปิดใช้งาน” หน้าลูกค้าแสดงข้อความให้ชำระเงินสดที่หน้าร้าน และพนักงานหน้าร้านกด “รับเงินสด” หรือ “ยืนยันสลิป” เพื่อเปลี่ยนเป็น “จ่ายแล้ว” ได้ · ทดสอบ 3 กรณี (PromptPay ปกติ / ปิดใช้งาน / สลิปไม่ยืนยันเกิน 10 นาที) ผ่าน 3 จาก 3 (ดูหมายเหตุ ก.)
- clause ที่ตรวจ: F08c: ค้างจ่ายจนยืนยันสลิป; F08e: ยืนยันสลิปทำให้จ่ายแล้ว; กรณีปกติในชุด 3 กรณี
- FR / Flow / Screen: FR-08; NFR-17 → MRG-03, MRG-04, MRG-06, MRG-07, MRG-10, MRG-11, MRG-32, MRG-33 → SCR-03, SCR-05, SCR-09, SCR-16, SCR-08; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: auto ตรวจเฉพาะพฤติกรรมจำลองผ่าน UI/DOM; ไม่พิสูจน์ QR, LAN/Wi‑Fi, Security, Load, Availability, server log หรือการชำระเงินจริง
- Precondition/reset: R0 แล้ว O สองใบ m01 และ m02; ใช้ใบล่าสุด m02 เป็นเป้าหมายและเก็บ ID ทั้งสอง; PromptPay เปิด
- Test data: สองออเดอร์ 50 และ 55 บาท; ภาพ QR และการยืนยันสลิปเป็น mock ไม่มีไฟล์สลิปจริงหรือการโอน
- data-testid และ scope: C: order-id, pay-promptpay, payment-status; F(order ID): btn-confirm-slip, front-payment-status, front-adjusted-total; F0; คำย่อ G/C/K/F/R/I/M และขั้น O/K0/F0/M0 ตามส่วน Precondition และ scope ที่ใช้ซ้ำ
- ขั้นตอน:

  1. เลือก pay-promptpay ของใบล่าสุด ตรวจ payment-status=ค้างจ่าย ก่อนมีการยืนยันใด
  2. เข้า F0 ตรวจทั้งสอง ID; กด btn-confirm-slip เฉพาะใบ 55 บาท
  3. กลับ C ตรวจจ่ายแล้ว และกลับ F ตรวจอีกใบยังไม่ถูกยืนยันโดยผลของการกดใบเป้าหมาย

- Expected result: ก่อนยืนยันใบเป้าหมายค้างจ่าย หลังยืนยันสลิปเป็นจ่ายแล้วทั้งลูกค้าและหน้าร้าน; อีกใบไม่เปลี่ยนตาม; เพิ่มปลายทางยืนยันและ scope จาก TS-US-08-101 ซึ่งจบเพียง fallback
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงข้อความ AC ต้นฉบับเต็มของ US-08 ในรายการนี้ทุกตัวเลข/สูตร/หน่วย/สัดส่วน; ตารางแยก assertions ระบุประชากรที่ต้องเก็บ. ชุดย่อยหรือจำนวน fixture ใน Test data ไม่ใช้แทนประชากรนั้น; assertion เฉพาะข้อผิดพลาดที่ไม่มีกลุ่มตัวอย่างใน AC ไม่เพิ่มเกณฑ์จำนวนเอง. ทุกเกณฑ์ระบบจริงยังไม่ได้ทดสอบ
- สมมติฐาน/ข้อค้าง: Q-08/DI-01: วิธีส่งและตรวจสลิปจริง/หมายเหตุ ก. ยังขาด; QR ของ mock ไม่ชำระจริง; ไม่ถือผลคลิกเป็นยืนยันโอน
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-08-3"></a>

## TS-US-08-3 — PromptPay ปิดใช้งานแล้วแจ้งและรับเงินสด

- US: US-08
- เจ้าของ: customer
- ประเภท: ข้อยกเว้น
- AC ต้นฉบับเต็ม: ยอดรวมบนหน้าสรุปของลูกค้าตรงกับยอดบนจอหน้าร้านในอย่างน้อย 19 จาก 20 ใบของชุดทดสอบ และเลือกวิธีจ่ายได้ 2 แบบทุกออเดอร์ · เมื่อเลือก PromptPay ออเดอร์อยู่สถานะ “ค้างจ่าย” จนพนักงานหน้าร้านยืนยันสลิป · ถ้าสลิปยังไม่ยืนยันภายใน 10 นาที หรือผู้จัดการร้านตั้งค่า “PromptPay ปิดใช้งาน” หน้าลูกค้าแสดงข้อความให้ชำระเงินสดที่หน้าร้าน และพนักงานหน้าร้านกด “รับเงินสด” หรือ “ยืนยันสลิป” เพื่อเปลี่ยนเป็น “จ่ายแล้ว” ได้ · ทดสอบ 3 กรณี (PromptPay ปกติ / ปิดใช้งาน / สลิปไม่ยืนยันเกิน 10 นาที) ผ่าน 3 จาก 3 (ดูหมายเหตุ ก.)
- clause ที่ตรวจ: F08d/F08e: ผู้จัดการปิด PromptPay แล้วแจ้งเงินสดที่หน้าร้าน; รับเงินสดเปลี่ยนเป็นจ่ายแล้ว
- FR / Flow / Screen: FR-08; NFR-17 → MRG-03, MRG-04, MRG-06, MRG-07, MRG-10, MRG-11, MRG-32, MRG-33 → SCR-03, SCR-05, SCR-09, SCR-16, SCR-08; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: auto ตรวจเฉพาะพฤติกรรมจำลองผ่าน UI/DOM; ไม่พิสูจน์ QR, LAN/Wi‑Fi, Security, Load, Availability, server log หรือการชำระเงินจริง
- Precondition/reset: R0 แล้ว O m01; เข้า M0 เพื่อปิด PromptPay; ไม่เปลี่ยนข้อมูล order อื่น
- Test data: m01=50 บาท; toggle-promptpay=false; การรับเงินสดจำลองเท่านั้น
- data-testid และ scope: M: toggle-promptpay; C: pay-cash, pay-promptpay, cash-message, payment-status; F(order ID): btn-receive-cash, front-payment-status; คำย่อ G/C/K/F/R/I/M และขั้น O/K0/F0/M0 ตามส่วน Precondition และ scope ที่ใช้ซ้ำ
- ขั้นตอน:

  1. ผู้จัดการยกเลิกเลือก toggle-promptpay; กลับ C ตรวจข้อความ cash-message บอกให้ชำระเงินสดที่หน้าร้าน
  2. ตรวจว่าทั้ง pay-cash และ pay-promptpay ยังอยู่ใน mock; ทดลองเลือก PromptPay แล้วบันทึกว่าการเลือกไม่เริ่มการชำระใน fixture
  3. เลือก pay-cash แล้วเข้า F0 กด btn-receive-cash เฉพาะ ID เป้าหมาย; กลับ C ตรวจสถานะ

- Expected result: มีข้อความให้ชำระเงินสดที่หน้าร้านและกดรับเงินสดแล้วเป็นจ่ายแล้ว; fixture ยังคงปุ่มสองแบบแต่เลือก PromptPay ขณะปิดไม่เปลี่ยน state เป็นข้อจำกัดการตีความ ไม่ใช่หลักฐานว่าผ่าน เลือกได้ 2 แบบทุกออเดอร์ ขณะปิด
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงข้อความ AC ต้นฉบับเต็มของ US-08 ในรายการนี้ทุกตัวเลข/สูตร/หน่วย/สัดส่วน; ตารางแยก assertions ระบุประชากรที่ต้องเก็บ. ชุดย่อยหรือจำนวน fixture ใน Test data ไม่ใช้แทนประชากรนั้น; assertion เฉพาะข้อผิดพลาดที่ไม่มีกลุ่มตัวอย่างใน AC ไม่เพิ่มเกณฑ์จำนวนเอง. ทุกเกณฑ์ระบบจริงยังไม่ได้ทดสอบ
- สมมติฐาน/ข้อค้าง: Q-08: ความสัมพันธ์เลือกได้สองแบบกับปิด PromptPay ยัง BLOCKED; ไม่ซ่อนความขัดแย้งด้วยการนับว่าปุ่มมีอยู่เท่ากับเลือกได้; เงินสดปกติอ้าง TS-US-08-102 ไม่สร้างนิยาม fixture ซ้ำ
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-08-4"></a>

## TS-US-08-4 — สลิปไม่ยืนยันเกิน 10 นาทีแล้วรับเงินสดหรือยืนยันสลิปภายหลัง

- US: US-08
- เจ้าของ: customer
- ประเภท: ข้อยกเว้น
- AC ต้นฉบับเต็ม: ยอดรวมบนหน้าสรุปของลูกค้าตรงกับยอดบนจอหน้าร้านในอย่างน้อย 19 จาก 20 ใบของชุดทดสอบ และเลือกวิธีจ่ายได้ 2 แบบทุกออเดอร์ · เมื่อเลือก PromptPay ออเดอร์อยู่สถานะ “ค้างจ่าย” จนพนักงานหน้าร้านยืนยันสลิป · ถ้าสลิปยังไม่ยืนยันภายใน 10 นาที หรือผู้จัดการร้านตั้งค่า “PromptPay ปิดใช้งาน” หน้าลูกค้าแสดงข้อความให้ชำระเงินสดที่หน้าร้าน และพนักงานหน้าร้านกด “รับเงินสด” หรือ “ยืนยันสลิป” เพื่อเปลี่ยนเป็น “จ่ายแล้ว” ได้ · ทดสอบ 3 กรณี (PromptPay ปกติ / ปิดใช้งาน / สลิปไม่ยืนยันเกิน 10 นาที) ผ่าน 3 จาก 3 (ดูหมายเหตุ ก.)
- clause ที่ตรวจ: F08d/F08e: fallback เมื่อยังไม่ยืนยันภายใน 10 นาที และมีทั้งทางรับเงินสด/ยืนยันสลิป; กรณีเกิน 10 นาทีในชุด 3 กรณี
- FR / Flow / Screen: FR-08; NFR-17 → MRG-03, MRG-04, MRG-06, MRG-07, MRG-10, MRG-11, MRG-32, MRG-33 → SCR-03, SCR-05, SCR-09, SCR-16, SCR-08; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: auto ตรวจเฉพาะพฤติกรรมจำลองผ่าน UI/DOM; ไม่พิสูจน์ QR, LAN/Wi‑Fi, Security, Load, Availability, server log หรือการชำระเงินจริง
- Precondition/reset: R0 แยกใหม่ต่อทางออกสองทาง; O m01 แล้วเลือก PromptPay ที่ 12:00; ไม่ยืนยันก่อนเวลา
- Test data: m01=50; sim-clock 12:00 →12:10 →12:20; รอบ A รับเงินสด รอบ B ยืนยันสลิป; เป็นชุดย่อย fixture ของกรณี timeout เดียว
- data-testid และ scope: G: sim-clock, btn-advance-10m; C: pay-promptpay, payment-status, cash-message; F(order ID): btn-receive-cash หรือ btn-confirm-slip, front-payment-status; คำย่อ G/C/K/F/R/I/M และขั้น O/K0/F0/M0 ตามส่วน Precondition และ scope ที่ใช้ซ้ำ
- ขั้นตอน:

  1. เลือก PromptPay ตรวจค้างจ่าย จดเวลาจำลองเริ่มและ ID
  2. กด btn-advance-10m ครั้งแรกจดผลตรง 10 นาที; กดอีกครั้งจน 20 นาทีเพื่อให้เกิน 10 นาทีจริงในนาฬิกาจำลอง; ตรวจข้อความเงินสดและยังไม่จ่ายแล้วเอง
  3. รอบ A เข้า F0 กดรับเงินสด; รอบ B เริ่มใหม่เหมือนกันแล้วกดยืนยันสลิป; กลับลูกค้าตรวจสถานะของ ID เดิม

- Expected result: หลัง 20 นาทีที่ยังไม่ยืนยันต้องแจ้งเงินสดที่หน้าร้านและยังค้างจ่าย; ทั้งสองทางออกทำให้จ่ายแล้วใน mock; บันทึกผลตรง 10 นาทีแยกและไม่ใช้การขยับเวลาแทน timer จริง; TS-US-08-101 จบที่ +10 นาทีและยังไม่ยืนยันทางออก
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงข้อความ AC ต้นฉบับเต็มของ US-08 ในรายการนี้ทุกตัวเลข/สูตร/หน่วย/สัดส่วน; ตารางแยก assertions ระบุประชากรที่ต้องเก็บ. ชุดย่อยหรือจำนวน fixture ใน Test data ไม่ใช้แทนประชากรนั้น; assertion เฉพาะข้อผิดพลาดที่ไม่มีกลุ่มตัวอย่างใน AC ไม่เพิ่มเกณฑ์จำนวนเอง. ทุกเกณฑ์ระบบจริงยังไม่ได้ทดสอบ
- สมมติฐาน/ข้อค้าง: Q-08: จุดเริ่มนับและความหมายตรงขอบ 10 นาทียังต้องยืนยัน; เลือก PromptPay เป็น t0 ของ fixture ไม่ใช่การตัดสินต้นฉบับ
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-08-5"></a>

## TS-US-08-5 — ตรวจชุดชำระสามกรณีและเวลา timeout บนระบบจริง

- US: US-08
- เจ้าของ: customer
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: ยอดรวมบนหน้าสรุปของลูกค้าตรงกับยอดบนจอหน้าร้านในอย่างน้อย 19 จาก 20 ใบของชุดทดสอบ และเลือกวิธีจ่ายได้ 2 แบบทุกออเดอร์ · เมื่อเลือก PromptPay ออเดอร์อยู่สถานะ “ค้างจ่าย” จนพนักงานหน้าร้านยืนยันสลิป · ถ้าสลิปยังไม่ยืนยันภายใน 10 นาที หรือผู้จัดการร้านตั้งค่า “PromptPay ปิดใช้งาน” หน้าลูกค้าแสดงข้อความให้ชำระเงินสดที่หน้าร้าน และพนักงานหน้าร้านกด “รับเงินสด” หรือ “ยืนยันสลิป” เพื่อเปลี่ยนเป็น “จ่ายแล้ว” ได้ · ทดสอบ 3 กรณี (PromptPay ปกติ / ปิดใช้งาน / สลิปไม่ยืนยันเกิน 10 นาที) ผ่าน 3 จาก 3 (ดูหมายเหตุ ก.)
- clause ที่ตรวจ: F08c/d/e และ NFR-17: PromptPay ปกติ / ปิดใช้งาน / สลิปไม่ยืนยันเกิน 10 นาที ผ่าน 3 จาก 3
- FR / Flow / Screen: FR-08; NFR-17 → MRG-03, MRG-04, MRG-06, MRG-07, MRG-10, MRG-11, MRG-32, MRG-33 → SCR-03, SCR-05, SCR-09, SCR-16, SCR-08; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: mock-not-testable: UI/ข้อมูลหรือระบบจริงที่จำเป็นยังไม่มีตาม precondition; ไม่ใช้การอ่าน source หรือคลิก mock แทน AC ระบบจริง
- Precondition/reset: BLOCKED: ต้องมีระบบจริงในสภาพทดสอบที่ใช้ข้อมูล/สลิปจำลอง ไม่โอนเงินจริง และคำตอบ Q-08; ไม่มี service/timer จริงใน HTML
- Test data: 3 ออเดอร์หลักหนึ่งใบต่อกรณี; ทุกใบ m01=50; timeout มีชุดย่อยรับเงินสด/ยืนยันสลิป; จุดรอยต่อ 9:59, 10:00, 10:01 นาทีเป็นแผน boundary ไม่ใช่เวลา observed
- data-testid และ scope: MISSING: real timer/slip interface; ใช้หน้าลูกค้า/หน้าร้านตาม SCR-05/08/09/16 ไม่แต่ง endpoint หรือ selector; คำย่อ G/C/K/F/R/I/M และขั้น O/K0/F0/M0 ตามส่วน Precondition และ scope ที่ใช้ซ้ำ
- ขั้นตอน:

  1. เตรียมกรณีปกติ เลือก PromptPay แล้วตรวจค้างจ่ายจนพนักงานตรวจสลิปจำลองและกดยืนยัน
  2. เตรียมกรณีผู้จัดการปิด ตรวจข้อความให้จ่ายเงินสดที่หน้าร้านและยืนยันรับเงินสด รวมบันทึกตัวเลือกสองแบบตาม Q-08
  3. เตรียมกรณีไม่ยืนยันสลิป วัดเวลาจริงจาก event ที่ตกลง เก็บผลก่อน/ตรง/หลัง 10 นาที และตรวจ fallback; ครอบคลุมรับเงินสดกับยืนยันสลิปในชุดย่อย
  4. สรุปสามกรณีหลักแยกผลทุก assertion และหลักฐานเวลา ไม่ใช้จำนวน screenshots แทนจำนวนกรณี

- Expected result: ทั้ง 3 กรณีต้องผ่าน 3 จาก 3 ตาม AC; ไม่มีการเปลี่ยนเป็นจ่ายแล้วจาก timeout เอง; ยอด/วิธีจ่ายชุด 20 ใบยังต้องตรวจแยกตาม TS-US-08-1 บนระบบจริง ไม่ใช้สามใบแทน 20
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงข้อความ AC ต้นฉบับเต็มของ US-08 ในรายการนี้ทุกตัวเลข/สูตร/หน่วย/สัดส่วน; ตารางแยก assertions ระบุประชากรที่ต้องเก็บ. ชุดย่อยหรือจำนวน fixture ใน Test data ไม่ใช้แทนประชากรนั้น; assertion เฉพาะข้อผิดพลาดที่ไม่มีกลุ่มตัวอย่างใน AC ไม่เพิ่มเกณฑ์จำนวนเอง. ทุกเกณฑ์ระบบจริงยังไม่ได้ทดสอบ
- สมมติฐาน/ข้อค้าง: Q-08/DI-01: ยังไม่กำหนด oracle ที่ 9:59/10:00 จนตอบจุดเริ่ม/ขอบ; การผ่านสภาพทดสอบยังไม่ใช่การโอนเงินจริงหรือยืนยันสลิปจากธนาคารจริง
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-09-1"></a>

## TS-US-09-1 — แจ้งทั้งสองทางเลือกและคืนเฉพาะรายการในบิลหลายจาน

- US: US-09
- เจ้าของ: customer
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: เมื่อครัวกด “ทำไม่ได้-วัตถุดิบหมด” ที่รายการในคิว หน้าลูกค้าแสดงแจ้งเตือนภายใน 10 วินาทีบน LAN พร้อมปุ่ม “เปลี่ยนเมนู” และ “คืนรายการ” และยอดรวมปรับลดตามรายการที่คืน ทดสอบผ่าน 5 จาก 5 กรณี
- clause ที่ตรวจ: F09a: แจ้งและมีปุ่มเปลี่ยน/คืน; F09b: ยอดลดตามรายการที่คืน
- FR / Flow / Screen: FR-09; NFR-V2-09 → MRG-31, MRG-32, MRG-33 → SCR-03, SCR-04, SCR-05, SCR-06, SCR-08, SCR-09; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: auto ตรวจเฉพาะพฤติกรรมจำลองผ่าน UI/DOM; ไม่พิสูจน์ QR, LAN/Wi‑Fi, Security, Load, Availability, server log หรือการชำระเงินจริง
- Precondition/reset: R0; O ใบเดียวสองจาน m01+ไข่ และ m02; จด order ID และ item ID จาน 60 จากใบครัวก่อนกดทำไม่ได้
- Test data: m01+extra-egg=60, m02=55 รวม 115 บาท; คืนจาน 60 แล้วยอดปรับ 55 เป็น fixture ของ Flow v2
- data-testid และ scope: K(order ID): btn-item-unavailable[data-item-id=I]; R(order ID)/I(item ID): customer-unavailable-alert, item-state, btn-change-menu, btn-return-item; R: resolution-order-total; C: customer-adjusted-total; F: front-total, front-adjusted-total; คำย่อ G/C/K/F/R/I/M และขั้น O/K0/F0/M0 ตามส่วน Precondition และ scope ที่ใช้ซ้ำ
- ขั้นตอน:

  1. สร้างสองจานในใบเดียวและยืนยันยอด 115; เข้า K0 ระบุ item ID ของ m01+ไข่ กดทำไม่ได้เฉพาะรายการนั้น
  2. กลับ C ตรวจ alert มีวัตถุดิบหมด พร้อม btn-change-menu และ btn-return-item ภายใน I เดียวกัน ก่อนคลิกทางออก
  3. กดคืนรายการใน I; ตรวจ resolution-order-total และ customer-adjusted-total=55; เข้า F0 ตรวจ front-adjusted-total=55 แต่ front-total เดิม=115
  4. เข้า K0 ตรวจจาน 60 ไม่อยู่ในรายการที่ต้องทำและ m02 ยังอยู่; หลักฐานยอดต้องเทียบ order ID เดิม

- Expected result: ก่อนตัดสินใจแจ้งวัตถุดิบหมดและมีทั้งสองปุ่ม; คืนเฉพาะจาน 60 แล้วบิลปรับเหลือ 55 โดยไม่หัก m02; ข้อมูล snapshot 115 คงใน mock; TS-US-09-101 เป็น fixture ใบเดียวจานเดียวซึ่งติด selector mismatch ไม่ใช่ scenario นี้
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงข้อความ AC ต้นฉบับเต็มของ US-09 ในรายการนี้ทุกตัวเลข/สูตร/หน่วย/สัดส่วน; ตารางแยก assertions ระบุประชากรที่ต้องเก็บ. ชุดย่อยหรือจำนวน fixture ใน Test data ไม่ใช้แทนประชากรนั้น; assertion เฉพาะข้อผิดพลาดที่ไม่มีกลุ่มตัวอย่างใน AC ไม่เพิ่มเกณฑ์จำนวนเอง. ทุกเกณฑ์ระบบจริงยังไม่ได้ทดสอบ
- สมมติฐาน/ข้อค้าง: Q-V2-REFUND/STATE: ตัวเลข/จำนวนจานละ 1/เก็บ snapshot เป็น fixture; ลดบิลไม่ยืนยันคืนเงินจริง; ไม่ใช้ cart-total หรือ front-total เป็นยอดหลังคืน
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-09-2"></a>

## TS-US-09-2 — เปลี่ยนเมนูและตัวเลือกก่อนยืนยันทางออก

- US: US-09
- เจ้าของ: customer
- ประเภท: ทางเลือก
- AC ต้นฉบับเต็ม: เมื่อครัวกด “ทำไม่ได้-วัตถุดิบหมด” ที่รายการในคิว หน้าลูกค้าแสดงแจ้งเตือนภายใน 10 วินาทีบน LAN พร้อมปุ่ม “เปลี่ยนเมนู” และ “คืนรายการ” และยอดรวมปรับลดตามรายการที่คืน ทดสอบผ่าน 5 จาก 5 กรณี
- clause ที่ตรวจ: F09a: ทางเลือกเปลี่ยนเมนู; ยอด/เมนูแทนตาม MRG-32 เป็น fixture ที่ต้องแยกจากนโยบายส่วนต่างจริง
- FR / Flow / Screen: FR-09; NFR-V2-09 → MRG-31, MRG-32, MRG-33 → SCR-03, SCR-04, SCR-05, SCR-06, SCR-08, SCR-09; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: auto ตรวจเฉพาะพฤติกรรมจำลองผ่าน UI/DOM; ไม่พิสูจน์ QR, LAN/Wi‑Fi, Security, Load, Availability, server log หรือการชำระเงินจริง
- Precondition/reset: R0; O m02 ใบเดียว; K0 กดทำไม่ได้ที่ item ID ของ m02; catalog m01/ไข่ยังมี
- Test data: เดิม m02=55; แทน m01+extra-egg=60; ส่วนต่าง +5 และยอดปรับ 60 เป็น arithmetic fixture
- data-testid และ scope: K(order ID)/I(item ID); I: replacement-menu, replacement-option-extra-egg, replacement-preview, btn-change-menu, btn-return-item, item-state; R: resolution-order-total; C: customer-adjusted-total; F: front-total, front-adjusted-total; คำย่อ G/C/K/F/R/I/M และขั้น O/K0/F0/M0 ตามส่วน Precondition และ scope ที่ใช้ซ้ำ
- ขั้นตอน:

  1. กลับ C ตรวจ alert และสองทางเลือกของ I; เลือก replacement-menu=m01 และ replacement-option-extra-egg
  2. ก่อนกดเปลี่ยน ตรวจ replacement-preview แสดงจาน/ไข่/60 และ I ยังรอลูกค้าตัดสินใจ; บิลยัง 55
  3. กด btn-change-menu; ตรวจยอดปรับ 60 และรายการแทน แล้วเข้า K0 ตรวจ m01+ไข่ใน K ของ ID เดิม
  4. เข้า F0 ตรวจ front-adjusted-total=60, front-total เดิม=55; ไม่มีการยืนยันรับเงินเอง

- Expected result: เลือก draft อย่างเดียวไม่ถือว่าตัดสินใจ; เมื่อยืนยันทางเลือก mock แสดงรายการแทนพร้อมไข่และยอด 60; เปลี่ยนได้เป็นทางออกตาม AC แต่ราคาแทน/ส่วนต่างยังเป็นสมมติฐาน; เวลาอัปเดตครัวของ US-14 ไม่รับรองในงานเจ้าของ US-09 นี้
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงข้อความ AC ต้นฉบับเต็มของ US-09 ในรายการนี้ทุกตัวเลข/สูตร/หน่วย/สัดส่วน; ตารางแยก assertions ระบุประชากรที่ต้องเก็บ. ชุดย่อยหรือจำนวน fixture ใน Test data ไม่ใช้แทนประชากรนั้น; assertion เฉพาะข้อผิดพลาดที่ไม่มีกลุ่มตัวอย่างใน AC ไม่เพิ่มเกณฑ์จำนวนเอง. ทุกเกณฑ์ระบบจริงยังไม่ได้ทดสอบ
- สมมติฐาน/ข้อค้าง: Q-V2-REFUND/STATE: วิธีใช้ราคาปัจจุบัน การเก็บ order/item ID และ payment เดิมเป็น fixture ไม่ใช่กฎร้าน; US-14 ส่งต่อ kitchen-front
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-09-3"></a>

## TS-US-09-3 — กดเปลี่ยนเมนูโดยยังไม่เลือกเมนูแทน

- US: US-09
- เจ้าของ: customer
- ประเภท: ผิดพลาด
- AC ต้นฉบับเต็ม: เมื่อครัวกด “ทำไม่ได้-วัตถุดิบหมด” ที่รายการในคิว หน้าลูกค้าแสดงแจ้งเตือนภายใน 10 วินาทีบน LAN พร้อมปุ่ม “เปลี่ยนเมนู” และ “คืนรายการ” และยอดรวมปรับลดตามรายการที่คืน ทดสอบผ่าน 5 จาก 5 กรณี
- clause ที่ตรวจ: ข้อผิดพลาดของทางเลือก F09a; MRG-32/contract v2 เสนอให้ยังรอเมื่อตัวเลือกไม่ครบ
- FR / Flow / Screen: FR-09; NFR-V2-09 → MRG-31, MRG-32, MRG-33 → SCR-03, SCR-04, SCR-05, SCR-06, SCR-08, SCR-09; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: auto ตรวจเฉพาะพฤติกรรมจำลองผ่าน UI/DOM; ไม่พิสูจน์ QR, LAN/Wi‑Fi, Security, Load, Availability, server log หรือการชำระเงินจริง
- Precondition/reset: R0; O m01 หนึ่งจานแล้วครัวกดทำไม่ได้; replacement-menu ยัง value ว่าง
- Test data: m01=50; ไม่มีเมนูแทน; จด order/item ID ของรายการ pending
- data-testid และ scope: I: replacement-menu, btn-change-menu, btn-return-item, item-state; R: resolution-order-total; C: resolution-message ใน customer-item-resolutions; คำย่อ G/C/K/F/R/I/M และขั้น O/K0/F0/M0 ตามส่วน Precondition และ scope ที่ใช้ซ้ำ
- ขั้นตอน:

  1. ตรวจ precondition ว่ารายการ pending มีทั้งสองปุ่มและ replacement-menu ว่าง
  2. กด btn-change-menu โดยไม่เลือกเมนู
  3. ตรวจ resolution-message บอกให้เลือกเมนูแทน; ตรวจ I ยังรอลูกค้าตัดสินใจและมีปุ่มคืน; ยอดยัง 50

- Expected result: expected เฉพาะ fixture: แจ้งให้เลือกเมนูแทน คง pending ยอดไม่เปลี่ยน และคืนรายการยังเป็นทางออกได้; ไม่เกิดรายการแทนสำเร็จจาก draft ว่าง
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงข้อความ AC ต้นฉบับเต็มของ US-09 ในรายการนี้ทุกตัวเลข/สูตร/หน่วย/สัดส่วน; ตารางแยก assertions ระบุประชากรที่ต้องเก็บ. ชุดย่อยหรือจำนวน fixture ใน Test data ไม่ใช้แทนประชากรนั้น; assertion เฉพาะข้อผิดพลาดที่ไม่มีกลุ่มตัวอย่างใน AC ไม่เพิ่มเกณฑ์จำนวนเอง. ทุกเกณฑ์ระบบจริงยังไม่ได้ทดสอบ
- สมมติฐาน/ข้อค้าง: สมมติฐานรอยืนยัน Q-V2-STATE/REFUND: AC ไม่กำหนดข้อความหรือ flow เมื่อกรอกไม่ครบ; ผล mock ไม่ยืนยันนโยบายร้าน
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-09-4"></a>

## TS-US-09-4 — เมนูแทนหมดหลังเลือก draft แต่ก่อนยืนยัน

- US: US-09
- เจ้าของ: customer
- ประเภท: ผิดพลาด
- AC ต้นฉบับเต็ม: เมื่อครัวกด “ทำไม่ได้-วัตถุดิบหมด” ที่รายการในคิว หน้าลูกค้าแสดงแจ้งเตือนภายใน 10 วินาทีบน LAN พร้อมปุ่ม “เปลี่ยนเมนู” และ “คืนรายการ” และยอดรวมปรับลดตามรายการที่คืน ทดสอบผ่าน 5 จาก 5 กรณี
- clause ที่ตรวจ: F09a เปลี่ยนเมนูร่วม FR-06: เมนูที่ปิดแล้วต้องถูกปฏิเสธพร้อมข้อความ
- FR / Flow / Screen: FR-09; NFR-V2-09 → MRG-31, MRG-32, MRG-33 → SCR-03, SCR-04, SCR-05, SCR-06, SCR-08, SCR-09; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: auto ตรวจเฉพาะพฤติกรรมจำลองผ่าน UI/DOM; ไม่พิสูจน์ QR, LAN/Wi‑Fi, Security, Load, Availability, server log หรือการชำระเงินจริง
- Precondition/reset: R0; O m02 แล้วครัวกดทำไม่ได้; ลูกค้าเลือก m01 เป็น draft ขณะ chicken ยังมี
- Test data: เดิม m02=55; draft m01=50; จากนั้นปิด chicken ก่อนกดเปลี่ยนเมนู
- data-testid และ scope: I: replacement-menu, btn-change-menu, item-state, btn-return-item; C: resolution-message; R: resolution-order-total; K0: ingredient-select, btn-out-of-stock; K(order ID); คำย่อ G/C/K/F/R/I/M และขั้น O/K0/F0/M0 ตามส่วน Precondition และ scope ที่ใช้ซ้ำ
- ขั้นตอน:

  1. เลือก replacement-menu=m01 แต่ยังไม่กด btn-change-menu
  2. เข้า K0 ปิด chicken; กลับ C ตรวจ draft เดิมและเมนูที่ปิดในรายการเลือก
  3. กด btn-change-menu ของ I เดิม ตรวจข้อความปฏิเสธและคงรอ; ตรวจยอดยัง 55 และไม่มี m01 เป็นรายการแทนสำเร็จบนใบครัว

- Expected result: ปฏิเสธเมนูที่ปิดพร้อมข้อความ; fixture คงรอลูกค้าตัดสินใจและยอดเดิม 55 พร้อมปุ่มคืนรายการ; ไม่ถือปุ่มเมนู disabled อย่างเดียวเป็นการตรวจคำสั่ง draft เก่า
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงข้อความ AC ต้นฉบับเต็มของ US-09 ในรายการนี้ทุกตัวเลข/สูตร/หน่วย/สัดส่วน; ตารางแยก assertions ระบุประชากรที่ต้องเก็บ. ชุดย่อยหรือจำนวน fixture ใน Test data ไม่ใช้แทนประชากรนั้น; assertion เฉพาะข้อผิดพลาดที่ไม่มีกลุ่มตัวอย่างใน AC ไม่เพิ่มเกณฑ์จำนวนเอง. ทุกเกณฑ์ระบบจริงยังไม่ได้ทดสอบ
- สมมติฐาน/ข้อค้าง: Q-06/Q-V2-STATE: ต้นฉบับไม่กำหนดลำดับเหตุการณ์ที่เกิดพร้อมกัน; scenario นี้ปิดเสร็จก่อนยืนยัน ไม่ทดสอบ race
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-09-5"></a>

## TS-US-09-5 — หลังคืนแล้วไม่เสนอคืนซ้ำในหน้าจอ

- US: US-09
- เจ้าของ: customer
- ประเภท: ข้อยกเว้น
- AC ต้นฉบับเต็ม: เมื่อครัวกด “ทำไม่ได้-วัตถุดิบหมด” ที่รายการในคิว หน้าลูกค้าแสดงแจ้งเตือนภายใน 10 วินาทีบน LAN พร้อมปุ่ม “เปลี่ยนเมนู” และ “คืนรายการ” และยอดรวมปรับลดตามรายการที่คืน ทดสอบผ่าน 5 จาก 5 กรณี
- clause ที่ตรวจ: ข้อยกเว้น F09b: ผลคืนซ้ำยังไม่กำหนดใน AC; contract v2 เสนอ no-op และซ่อนปุ่ม
- FR / Flow / Screen: FR-09; NFR-V2-09 → MRG-31, MRG-32, MRG-33 → SCR-03, SCR-04, SCR-05, SCR-06, SCR-08, SCR-09; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: auto ตรวจเฉพาะพฤติกรรมจำลองผ่าน UI/DOM; ไม่พิสูจน์ QR, LAN/Wi‑Fi, Security, Load, Availability, server log หรือการชำระเงินจริง
- Precondition/reset: R0 แล้วทำ setup/คืนของ TS-US-09-1 จน item เดียวกัน returned จริงก่อนตรวจปุ่มหาย; ไม่เรียก handler ภายใน
- Test data: บิลเดิม 115 คืนรายการ 60 เหลือ 55; order/item ID เดิม
- data-testid และ scope: I: btn-return-item, item-state; R: resolution-order-total; F(order ID): front-adjusted-total; ปุ่มซ้ำต้องจำกัด I ที่คืนจริง; คำย่อ G/C/K/F/R/I/M และขั้น O/K0/F0/M0 ตามส่วน Precondition และ scope ที่ใช้ซ้ำ
- ขั้นตอน:

  1. ยืนยัน precondition ว่า I เคยมี btn-return-item และกดคืนสำเร็จเชิง fixture แล้ว
  2. ตรวจว่า I ไม่มีปุ่มคืนที่ใช้งานได้ และยอดยัง 55
  3. สลับไป F0 แล้วกลับ C เปิดรายการเดิมตาม ID ตรวจยอดไม่ลดอีกจากการเปิดหน้า/สลับบทบาท

- Expected result: expected fixture: UI ไม่เสนอคืนรายการเดิมซ้ำและยอดคง 55; ไม่อ้างทดสอบ no-op handler, ส่งคำสั่งซ้ำ, idempotency หรือการแข่งขันจริงจากปุ่มหาย
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงข้อความ AC ต้นฉบับเต็มของ US-09 ในรายการนี้ทุกตัวเลข/สูตร/หน่วย/สัดส่วน; ตารางแยก assertions ระบุประชากรที่ต้องเก็บ. ชุดย่อยหรือจำนวน fixture ใน Test data ไม่ใช้แทนประชากรนั้น; assertion เฉพาะข้อผิดพลาดที่ไม่มีกลุ่มตัวอย่างใน AC ไม่เพิ่มเกณฑ์จำนวนเอง. ทุกเกณฑ์ระบบจริงยังไม่ได้ทดสอบ
- สมมติฐาน/ข้อค้าง: Q-V2-REFUND/STATE: การคืนซ้ำและคืนชนเปลี่ยนยัง BLOCKED สำหรับระบบจริง; กรณี duplicate request ต้องออกแบบต่อเมื่อมีนโยบายและ interface
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-09-6"></a>

## TS-US-09-6 — แจ้งรายการทำไม่ได้บน LAN ครบห้ากรณี

- US: US-09
- เจ้าของ: customer
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: เมื่อครัวกด “ทำไม่ได้-วัตถุดิบหมด” ที่รายการในคิว หน้าลูกค้าแสดงแจ้งเตือนภายใน 10 วินาทีบน LAN พร้อมปุ่ม “เปลี่ยนเมนู” และ “คืนรายการ” และยอดรวมปรับลดตามรายการที่คืน ทดสอบผ่าน 5 จาก 5 กรณี
- clause ที่ตรวจ: F09a/F09b + NFR-V2-09: ครัวกดถึงแจ้งพร้อมสองปุ่ม ≤10 วินาทีบน LAN; ยอดลดตามรายการคืน; 5 จาก 5 กรณี
- FR / Flow / Screen: FR-09; NFR-V2-09 → MRG-31, MRG-32, MRG-33 → SCR-03, SCR-04, SCR-05, SCR-06, SCR-08, SCR-09; [FR/NFR — Traceability](../step-00-input/fr-nfr-v2.md), [Flow — Coverage/ทะเบียนส่วนเดิม/ส่วน MRG v2](../step-00-input/flow-v2.md); Screen เป็นรหัสออกแบบ ไม่ใช่ data-testid
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: mock-not-testable: UI/ข้อมูลหรือระบบจริงที่จำเป็นยังไม่มีตาม precondition; ไม่ใช้การอ่าน source หรือคลิก mock แทน AC ระบบจริง
- Precondition/reset: BLOCKED: ต้องมีลูกค้า/ครัวแยกอุปกรณ์บน LAN ระบบจริงและนโยบาย Q-V2-REFUND/STATE; ไม่ทำการโอนหรือคืนเงินจริง
- Test data: 5 กรณีจำลอง: (1) m01 50 คืนทั้งหมด→0; (2) m01+ไข่ 60 กับ m02 55 คืนจาน 60→55; (3) ชุดเดียวกันคืน m02 55→60; (4) m01 50 เปลี่ยน m02 55; (5) m02 55 เปลี่ยน m01+ไข่ 60; การแบ่งคืน 3/เปลี่ยน 2 และยอดเปลี่ยนเป็น fixture ไม่ใช่สัดส่วน/สูตรที่ร้านกำหนด
- data-testid และ scope: K/R/I/F จาก TS-US-09-1/2 เป็น counterparts; selector และเวลาระบบจริง MISSING; คำย่อ G/C/K/F/R/I/M และขั้น O/K0/F0/M0 ตามส่วน Precondition และ scope ที่ใช้ซ้ำ
- ขั้นตอน:

  1. แต่ละกรณีสร้างข้อมูลเริ่มต้นใหม่ จด order/item ID ยอด และสถานะเงินก่อนทำไม่ได้; เปิดหน้าลูกค้าค้าง
  2. ครัวกดทำไม่ได้ที่รายการเป้าหมายจด t0; จด t1 เมื่อลูกค้าเห็นแจ้งเตือนพร้อมทั้งเปลี่ยนเมนูและคืนรายการโดยไม่เปิดหน้าทดแทน
  3. ดำเนินทางออกของแต่ละกรณี; ตรวจยอดลดตามรายการคืน ส่วนเปลี่ยนตรวจว่าลูกค้าเลือกและเกิดรายการแทนตามนโยบายที่ยืนยัน
  4. สรุปผล 5 กรณีแยกกัน เก็บ t1−t0 และยอด/ID; ถ้าตรวจครัวอัปเดตต่อ ให้ส่งหลักฐานแยก US-14 ด้วยจุดเริ่มลูกค้าตัดสินใจ

- Expected result: ทั้ง 5 กรณีต้องแจ้งพร้อมสองปุ่มภายใน 10 วินาทีบน LAN และผ่านทางออก/ยอดที่เกี่ยวข้องครบ 5 จาก 5; ไม่เฉลี่ยกลบกรณีช้า; การคืนทั้งจานไม่ใช่ยืนยันโอนคืนเงินจริง
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงข้อความ AC ต้นฉบับเต็มของ US-09 ในรายการนี้ทุกตัวเลข/สูตร/หน่วย/สัดส่วน; ตารางแยก assertions ระบุประชากรที่ต้องเก็บ. ชุดย่อยหรือจำนวน fixture ใน Test data ไม่ใช้แทนประชากรนั้น; assertion เฉพาะข้อผิดพลาดที่ไม่มีกลุ่มตัวอย่างใน AC ไม่เพิ่มเกณฑ์จำนวนเอง. ทุกเกณฑ์ระบบจริงยังไม่ได้ทดสอบ
- สมมติฐาน/ข้อค้าง: Q-V2-REFUND/STATE: ส่วนต่างเมนู/สถานะรวม/จ่ายแล้วคืนอย่างไรยังขาด; การแบ่งชุดนี้เป็นข้อเสนอทดสอบ ไม่ใช้เพิ่ม AC และไม่แทนชุด 5 จาก 5 ของ US-14
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

## ดัชนี US → TestID และประเภท

ช่อง N/A ระบุเหตุผลเมื่อ AC ไม่มีทางเลือกหรือแยกชนิดนั้น; ช่องข้อยกเว้นที่ไม่มี scenario เฉพาะไม่ใช่การอ้างว่าทดสอบแล้ว. ทุก US มีอย่างน้อยหนึ่งสำเร็จและหนึ่งผิดพลาด/ข้อยกเว้นเชิงออกแบบ แม้ oracle ของบางข้อยัง BLOCKED. คำว่าออกแบบไม่เท่ากับ COVERED/ผ่านระบบจริง

| US | สำเร็จ — ออกแบบ | ทางเลือก — ออกแบบ/อ้าง fixture | ผิดพลาด — ออกแบบ | ข้อยกเว้น — ออกแบบ | Fixture อ้างแยก |
|---|---|---|---|---|---|
| US-01 | TS-US-01-1, TS-US-01-2 | N/A — AC ไม่มีทางเลือกธุรกิจแยก | N/A — ใช้ข้อยกเว้นในคอลัมน์ถัดไปตามเกณฑ์ขั้นต่ำ | TS-US-01-3 | TS-US-01-101 |
| US-02 | TS-US-02-1, TS-US-02-2 | N/A — AC ไม่มีทางเลือกธุรกิจแยก | TS-US-02-3 | N/A — มีกรณีผิดพลาดแล้ว; ไม่มีข้อยกเว้นที่มี oracle เพิ่มใน AC | TS-US-02-101 |
| US-03 | TS-US-03-1 | N/A — AC ไม่มีทางเลือกธุรกิจแยก | TS-US-03-2 | TS-US-03-3 | TS-US-03-101 |
| US-04 | TS-US-04-1, TS-US-04-2 | N/A — AC ไม่มีทางเลือกธุรกิจแยก; ตัวเลือกต่อจานครอบคลุม TS-US-04-1/2 | TS-US-04-3 (oracle เดิมยัง BLOCKED), TS-US-04-4 | N/A — มีกรณีผิดพลาดแล้ว; ไม่มีข้อยกเว้นที่มี oracle เพิ่มใน AC | TS-US-04-101 |
| US-05 | TS-US-05-1, TS-US-05-2 | N/A — AC ไม่มีทางเลือกธุรกิจแยก | N/A — ใช้ข้อยกเว้นในคอลัมน์ถัดไปตามเกณฑ์ขั้นต่ำ | TS-US-05-3 (oracle เดิมยัง BLOCKED), TS-US-05-4 | TS-US-05-101 |
| US-06 | TS-US-06-1, TS-US-06-3 | N/A — AC ไม่มีทางเลือกธุรกิจแยก | TS-US-06-2 | N/A — มีกรณีผิดพลาดแล้ว; ไม่มีข้อยกเว้นที่มี oracle เพิ่มใน AC | TS-US-06-101 |
| US-07 | TS-US-07-1, TS-US-07-2 | N/A — AC ไม่มีทางเลือกธุรกิจแยก | TS-US-07-4 | TS-US-07-3 | ไม่มี fixture — US-07 ไม่รองรับใน v2 |
| US-08 | TS-US-08-1, TS-US-08-2, TS-US-08-5 | TS-US-08-102 (fixture เงินสด); TS-US-08-2/3/4 ตรวจสลิปและทางออก | N/A — ใช้ข้อยกเว้นในคอลัมน์ถัดไปตามเกณฑ์ขั้นต่ำ | TS-US-08-3, TS-US-08-4 | TS-US-08-101, TS-US-08-102 |
| US-09 | TS-US-09-1, TS-US-09-6 | TS-US-09-2 | TS-US-09-3, TS-US-09-4 | TS-US-09-5 | TS-US-09-101 |

## การเชื่อม fixture ที่สงวน ID

ไม่คัดชุด steps ของ fixture มาสร้างเป็น scenario n≥101 ในไฟล์นี้ และไม่เปลี่ยน JSON. Scenario n<101 ข้างต้นขยาย assertion/ประชากร/ข้อยกเว้นจาก AC; การเริ่มจาก action ใกล้กันไม่ใช้ fixture แทน oracle ของ AC. สถานะอ้างอิงทั้งหมด NOT_RUN; ไม่รับรอง suite เดิมเข้ากันได้จนตรวจ runtime

| Fixture จาก ui-scenarios.json | สิ่งที่ fixture ตรวจจริงตาม steps | เชื่อมงานออกแบบ/สิ่งที่ยังไม่พิสูจน์ |
|---|---|---|
| TS-US-01-101 | เปิด menu-list โดยไม่ login | TS-US-01-1/2; ยังไม่ assert รายการแรก/QR/3 วินาที/20 ครั้ง |
| TS-US-02-101 | พบข้อความ 02 ใน front-orders ใบเดียว | TS-US-02-1/2; ยังไม่ตรวจ URL, 20 โต๊ะ, ผูกอัตโนมัติ; ถ้ามีหลายใบห้ามใช้ global text |
| TS-US-03-101 | สั่งกลับบ้านใบเดียวและครัวมี 12:30 | TS-US-03-1/2; ยังไม่ assert ช่วงจบ/ทุก slot/ขอบ 20 นาที/10 ใบ |
| TS-US-04-101 | ไข่ทำให้ item-total มี 60 และครัวมีไข่ | TS-US-04-1/2; ยังไม่ครบ configuration หลายตัวเลือก/ยอดตะกร้าก่อนยืนยัน/20 ใบ |
| TS-US-05-101 | สลับบทบาทแล้วลูกค้าเห็นกำลังทำในแท็บเดียว | TS-US-05-1/2; ไม่พิสูจน์จอเปิดค้างไร้ refresh/5 วินาที LAN/20 ครั้ง |
| TS-US-06-101 | ตะกร้าเดิมกดส่งแล้ว order-message มีหมด | TS-US-06-1/2/3; ต้องเพิ่มป้ายพร้อม disabled/no-new-order/10 ครั้ง LAN |
| TS-US-08-101 | ค้างจ่ายแล้วเลื่อนนาฬิกา +10 นาทีเห็นเงินสด | TS-US-08-2/4/5; ไม่ใช่เกิน 10 นาที, ไม่มีการยืนยันสลิปปลายทาง/ระบบจริง |
| TS-US-08-102 | เงินสดยังไม่จ่ายจนหน้าร้านรับเงิน | ทางเลือกเงินสดปกติของ US-08; อ้างโดยไม่สร้าง steps ซ้ำ; scope ใบเดียวตาม reset; ไม่ทดสอบรับเงินจริง |
| TS-US-09-101 | ทำไม่ได้/มีคืนรายการ/คืนหนึ่งจาน แล้วคาดยอด 0 | TS-US-09-1/6; BLOCKED ด้าน selector เพราะ payment-summary-total ไม่มีใน HTML; ไม่ตรวจปุ่มเปลี่ยนหรือ LAN; item-resolution และปุ่มต่าง ๆ unique ได้เฉพาะหนึ่งใบหนึ่งจานตาม fixture |

การแก้ mapping สำหรับการรันในอนาคตต้องทำในรุ่นใหม่ที่ได้รับขอบเขตงานนั้น: `payment-summary-total` → `customer-adjusted-total` ใช้แทนได้เฉพาะยอด **ออเดอร์ล่าสุดหนึ่งใบ** ใน fixture ไม่ใช่ยอดรวม session. บิลก่อนหน้าที่มี resolution ใช้ `resolution-order-total` scope order ID; หน้าร้านใช้ `front-adjusted-total`. `front-total` คือ snapshot เดิม, `cart-total` คือตะกร้า ไม่ใช้เป็นยอดหลังคืน

อีกสองชื่อในสัญญาเสริมที่ไม่ตรง HTML คือ `rush-start` → `capacity-start` และ `rush-end` → `capacity-end` และต้องเข้า `nav-capacity` ก่อนตั้ง; เป็นข้อส่งต่อ US-21 ไม่เพิ่ม scenario ของบทบาทอื่น. ชื่อ m09 ยังไม่มีหลัง reset จนสร้างเมนูใหม่ จึงไม่ใช้โดยสมมติว่ามี seed

## ข้อบกพร่อง ข้อค้าง และการส่งต่อ

| ประเด็น | ผลกระทบ/Scenario | สิ่งที่ขาดและงานถัดไป |
|---|---|---|
| UI-US07 | TS-US-07-1/2/3: NOT_TESTABLE | HTML แสดงยังประมาณไม่ได้; ไม่มี ETA selector/ข้อมูลเฉลี่ย 7 วัน/ต่อเมนู/การคำนวณ; capacity-message/X ไม่ทดแทนสูตร; ต้องมีระบบและข้อมูลก่อนรัน |
| UI-FIXTURE-V2 | TS-US-09-101: NOT_RUN แต่การรัน JSON เดิม BLOCKED | ไม่พบ payment-summary-total; ชื่อ rush-start/rush-end ก็ไม่ตรง HTML; งานนี้บันทึก mapping เท่านั้น ไม่แก้ input และไม่แปลงเป็น skip |
| UI-SCOPE | US-02/03/04/05/08/09 | selector ต่อออเดอร์/รายการซ้ำ; ต้องใช้ order/item ID หรือ fixture ใบเดียว; ยอดล่าสุดไม่ใช่ยอดทั้ง session; ไม่มีผล runtime ตรวจ uniqueness |
| QR/NETWORK | TS-US-01-2/3, TS-US-02-2/3, TS-US-05-2/3, TS-US-06-3, TS-US-09-6 | Mock มี 3 โต๊ะและตัวเลือกแทน QR, state หนึ่งแท็บ ไม่มี LAN จริง; สภาพเครื่อง/ปริมาณข้อมูลและเครื่องมือวัดยังไม่มีข้อมูล |
| Q-01/Q-02 | US-01/02 ข้อยกเว้น QR และชุดจริง | สภาพทดสอบสแกน/ผู้สร้าง QR/QR ผิด/โต๊ะไม่พบ/ปลายทางล่ม/ทางออกยังรอยืนยัน; ไม่เพิ่ม redirect/default table/ข้อความเอง |
| Q-03 | US-03 | เวลาสั่งอิง event ใด, slot แรก/ปัดขึ้น/ชั่วโมงเปิดรับ/ความจุ/กรณีเลือกแล้วค้างยังไม่มีข้อมูล; fixture 12:00→12:30 ไม่ใช่นโยบายร้าน |
| Q-04 | US-04 | required/จำนวนต่อจาน/คู่ขัดกัน/การเลือกหลายค่า/สารก่อแพ้ยังไม่มี oracle; TS-US-04-3 BLOCKED; ตัวเลือกหลายชื่อของ manual เป็นข้อมูลจำลอง |
| Q-05/DI-07 และ Q-V2-STATE | US-05/07/09 | เสร็จแล้ว/พร้อมเสิร์ฟยังไม่แมป; item/order/payment/table ต้องแยก; aggregate หลังคืนหมดและ recovery เครือข่ายยังไม่กำหนด |
| Q-06 และ DI-02/หมายเหตุ ค. | US-06 และ setup US-04/09 | ข้อความเต็ม การเก็บตะกร้า การส่งบางส่วนและ race ยังไม่กำหนด; กฎเมนูปิดปฏิเสธชัด ส่วน atomic ตะกร้าผสมเป็น fixture; ขาดรายละเอียดแมปเสริม |
| Q-07/DI-03/หมายเหตุ ช. | US-07 | วิธีเฉลี่ย/ปัดเศษ/ไม่มีประวัติ/ประชากรช่วงเร่งด่วน/ขอบช่วง/ใบยังไม่จบ/เวลา server ยังไม่ยืนยัน; ต้องเก็บทุกใบของวัน ไม่คัดใบผิดออก |
| DI-06/Q-V2-CAPACITY | US-07 และ setup ที่เกี่ยวกับ US-21 | คง 11:30–13:00 และ 17:30–19:30 สำหรับ ETA; ช่วง 11:30–13:30 และ X=10 เป็นอีก fixture; ความสัมพันธ์/เขตเวลายังไม่ยืนยัน |
| Q-08/DI-01/หมายเหตุ ก. | US-08 | จุดเริ่ม/ขอบ 10 นาที วิธีส่ง/ตรวจสลิป และเลือกได้สองแบบขณะปิดยังขาด; พบ static ว่าปุ่ม PromptPay ยังอยู่แต่ handler ไม่เริ่มจ่ายขณะปิด; ไม่รับรอง clause สองแบบด้วยการเห็นปุ่ม |
| Q-V2-REFUND/STATE | US-09 และผลต่อ US-08 | สูตรส่วนต่าง/ตัวเลือก/จำนวน/ปัดเศษ/ผู้อนุมัติ/คืนเงินจริงหลังจ่าย/คืนซ้ำ/คืนชนเปลี่ยน/สถานะรวมยังไม่มีข้อมูล; UI ป้องกันคืนซ้ำไม่พิสูจน์ idempotency backend |
| DI-04/Q-20 | ส่งต่อ manager/kitchen-front | US-20 ต้นฉบับยังอ้าง US-14 สำหรับกฎปิด/เปิด; เสนอเชื่อม US-12/US-13 ได้แต่ยังไม่ยืนยัน; ไม่แก้รหัสอ้างในหลักฐาน |
| DI-08/DI-09 | ทุก US | ผลเก่าไม่ใช่ผลรันนี้; mock ไม่รับรอง LAN/Wi‑Fi/Security/Load/Availability/ติดตั้งหรือเงินจริง |

ออกแบบครบทั้ง 9 US ในเชิงมีรายการทดสอบ แต่ความครบที่ตัดสินได้ยังมี **GAPS** จาก oracle/ข้อมูลและข้อจำกัดที่ระบุ ไม่ประกาศ COVERED หรือรับรอง AC ระบบจริง. รอบนี้แก้ตาม D01–D07 เป็นรอบแก้ที่ 1 จากเพดาน 2; ไม่มีการเรียกผู้ช่วยเพิ่ม

## บันทึกสิ่งที่สร้างในต้นทางก่อนแก้และสิ่งที่ยังไม่ได้ทดสอบ

ต้นทางสร้างเฉพาะ `../step-01-fanout/customer/scenarios-customer.md` ในขั้น fanout; ไม่สร้างสคริปต์รัน ไม่แก้ input, manifest, HTML หรือผลเดิม. ตรวจความครบช่อง template/ID/ข้อความ AC จากไฟล์ได้ในระดับเอกสารเท่านั้น

ยังไม่ได้ทดสอบ browser/DOM/คลิก/visibility/uniqueness/responsive, auto/manual ทุก scenario, fixture ทุก ID, จำนวนตัวอย่างและสัดส่วน AC, QR/กล้อง/Wi‑Fi/LAN/หลายอุปกรณ์/การวัดเวลา/การรีเฟรชจริง, สูตรและความแม่นยำ ETA/log 1 วัน/ข้อมูลเฉลี่ย 7 วัน, Security/Load/Availability/ระบบติดตั้ง, ส่งสลิป/ชำระ/คืนเงินจริง. ผลรันและหลักฐานทั้งหมด: **ไม่มีข้อมูล**


---

## ต้นฉบับฉบับเต็ม — kitchen-front

Source: [scenarios-kitchen-front-round-1.md](../step-02-coverage/fix-1/scenarios-kitchen-front-round-1.md). คัดทั้งไฟล์; ปรับเฉพาะฐาน path/ลิงก์และเพิ่มจุดนำทางก่อนหัวข้อ.

# Scenarios ครัวและหน้าร้าน — ขั้น 6.1

## บันทึกรอบแก้ coverage — ROUND 1

คัดส่วนเดิมจาก [scenarios-kitchen-front.md](../step-01-fanout/kitchen-front/scenarios-kitchen-front.md) แล้วเพิ่มเฉพาะ TS-US-11-5, TS-US-17-3 ตาม D04, D05; รวม 42 TestID. นิยามเดิม 40 รายการคงข้อความทุกบล็อก; ปรับเฉพาะดัชนี/ข้อมูลรุ่น/ฐาน path ที่จำเป็นนอกบล็อก. รายการใหม่ทั้งหมดใช้ mock-not-testable และ Status MOCK_NOT_TESTABLE ตาม template; Status NOT_TESTABLE ในรายการเดิมเก็บตามต้นทาง. ข้อความจำนวนและสถานะในหัวข้อบันทึกต้นทางเป็นข้อมูลก่อนแก้

manifest ต้นทาง: [scenario-set-round-0.json](../step-00-input/scenario-set-round-0.json) resolve ค่าจากโฟลเดอร์ manifest; manifest รอบนี้: [scenario-set-round-1.json](../step-02-coverage/fix-1/scenario-set-round-1.json) resolve ทุกค่าจากราก LAB ../.. ตาม P01. รายละเอียดการแก้และ regression อยู่ที่ [coverage-fixes-round-1.md](../step-02-coverage/fix-1/coverage-fixes-round-1.md). ส่งผู้ตรวจรอบเดียวกัน ยังไม่ประกาศ COVERED; Actual/หลักฐานไม่มีข้อมูล


วันที่ออกแบบ: 2026-09-14 • เจ้าของทุก scenario: kitchen-front • ขอบเขต US-10–US-18

ต้นทางก่อนแก้มีเอกสารออกแบบ 40 scenarios จาก clause ของ AC ก่อนพิจารณา UI มีทั้งสำเร็จและผิดพลาด/ข้อยกเว้นทุก US แต่ **ยังมีข้อค้าง (GAPS)** จึงไม่รับรองว่า coverage ระบบครบหรือผ่านแล้ว ไม่มีการเปิด browser คลิก Mock-up หรือรันระบบจริงในขั้นนี้ ทุก Actual result และหลักฐานเป็น “ไม่มีข้อมูล”

สถานะเริ่มใช้ **NOT_RUN / NOT_TESTABLE ตามคำสั่งงาน** แทน MANUAL_PENDING / MOCK_NOT_TESTABLE ในช่อง Status ของแม่แบบ: auto/manual ที่ออกแบบให้ทำกับ mock ได้เป็น NOT_RUN; mock-not-testable เป็น NOT_TESTABLE และระบุสาเหตุ BLOCKED แยกไว้ รหัส automation ยังคง auto/manual/mock-not-testable ตามแม่แบบ

auto หมายถึงออกแบบให้รันกับ Mock-up นี้ได้ ไม่ใช่ผลผ่านของ AC ระบบจริง; manual มีขั้นตรวจด้วยคน; mock-not-testable ต้องมีระบบจริงหรือฟีเจอร์/ข้อมูลที่ยังขาด แม้ภายในแผนระบบจริงจะมีขั้นให้คนตรวจด้วยก็ตาม รหัส n<101 เป็นแบบทดสอบใหม่ รหัส n>=101 อ้าง fixture เดิมเท่านั้น ห้ามเปลี่ยน ID หลังเผยแพร่หรือใช้ ID เดิมแทนพฤติกรรมใหม่

## Input และฐานอ้างอิง

อ่านไฟล์ต่อไปนี้ใน session นี้เพื่อออกแบบและตรวจ source ของ selectors; ใช้ผลอ้างอิง upstream โดยไม่ยกสถานะหรือผลรันเดิมมาเป็นผลรอบนี้ ทุก path ด้านล่าง relative จากโฟลเดอร์ขั้นนี้:

- [../../../docs/case-study-source.md](../../../docs/case-study-source.md)
- [../../../docs/data-issues.md](../../../docs/data-issues.md)
- [../step-00-input/input-check.md](../step-00-input/input-check.md)
- [../step-00-input/fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md)
- [../step-00-input/flow-v2.md](../step-00-input/flow-v2.md)
- [../step-00-input/ui-mockup-v2.html](../step-00-input/ui-mockup-v2.html)
- [../../input/scenario-template.md](../../input/scenario-template.md)
- [../../input/coverage-criteria.md](../../input/coverage-criteria.md)
- [../../input/ui-scenarios.json](../../input/ui-scenarios.json)
- [../../input/ui-v2-test-contract.md](../../input/ui-v2-test-contract.md)
- [../../../004_LAB_Conditional_Graph_UI_Mockup/input/ui-contract.md](../../../004_LAB_Conditional_Graph_UI_Mockup/input/ui-contract.md)
- [../step-00-input/ui-contract-v2.md](../step-00-input/ui-contract-v2.md)
- [../step-00-input/test-outline-v2.md](../step-00-input/test-outline-v2.md)

manifest ต้นทาง resolve จาก ../step-00-input ตาม P01; manifest ใหม่ scenario-set-round-1.json ใช้ path จากราก LAB ที่ ../..; ไม่แก้ Input/ผลเดิม

## US/AC ต้นฉบับครบก่อนแยก assertions

คัดทั้งหกคอลัมน์จาก case-study-source.md ตรงตัว ใช้เป็นฐานแทนข้อความ “เพื่อ” ของ US-12 ที่ถูกปิดไว้ใน FR snapshot; ไม่แก้ snapshot

| ID | บทบาท | ในฐานะ | ฉันต้องการ | เพื่อ | เกณฑ์รับ |
|---|---|---|---|---|---|
| US-10 | พนักงานครัว/หน้าร้าน | พนักงานครัว | เห็นออเดอร์ใหม่บนจอครัวเรียงตามลำดับที่สั่งอย่างคงที่ | ไม่พลาดออเดอร์ในช่วงเร่งด่วน | นับจากลูกค้ากดยืนยันสั่ง จนถึงจอครัวแสดงออเดอร์ใหม่ ภายใน 3 วินาทีบน LAN ในร้าน ในอย่างน้อย 18 จาก 20 ใบของชุดทดสอบ · กฎเรียงลำดับ: เรียงตาม timestamp ฝั่งเซิร์ฟเวอร์ที่รับคำสั่ง (ความละเอียดวินาที) จากน้อยไปมาก และเมื่อ timestamp เท่ากันหรือออเดอร์เข้าพร้อมกัน ให้เรียงตามเลขออเดอร์ที่ระบบออกให้แบบ monotonic (เพิ่มขึ้นทีละ 1 ไม่ซ้ำ ไม่ย้อนกลับ) · ทดสอบยิง 30 ออเดอร์ต่อเนื่องจากมือถือ 2 เครื่องพร้อมกัน ลำดับบนจอครัวต้องตรงกับลำดับเลขออเดอร์ 30 จาก 30 ใบ และรันซ้ำ 3 รอบต้องได้ผลเดิมทุกรอบ (ไม่ยอมรับการสลับคู่) |
| US-11 | พนักงานครัว/หน้าร้าน | พนักงานครัว | กดเปลี่ยนสถานะออเดอร์ (กำลังทำ / เสร็จแล้ว) ด้วยปุ่มเดียว | ให้ลูกค้าและหน้าร้านรู้สถานะโดยไม่ต้องตะโกน | เปลี่ยนสถานะได้ใน 1 แตะ และนับจากกดปุ่มบนจอครัว จนถึงจอหน้าร้านแสดงสถานะใหม่ ภายใน 5 วินาทีบน LAN ในร้าน ในอย่างน้อย 18 จาก 20 ครั้งของชุดทดสอบ |
| US-12 | พนักงานครัว/หน้าร้าน | พนักงานครัว | กด “วัตถุดิบหมด” ที่วัตถุดิบ แล้วระบบปิดเมนูและตัวเลือกที่ใช้วัตถุดิบนั้นตามกติกาแมป | ลูกค้าไม่สั่งเมนูที่ทำไม่ได้ | ผู้จัดการแมปวัตถุดิบ→เมนู/ตัวเลือกไว้ล่วงหน้า (ดูหมายเหตุ ค.) เมื่อกดหมด 1 ครั้ง เมนูที่ใช้วัตถุดิบนั้นทั้งจานปิดทั้งเมนู ส่วนตัวเลือกเพิ่มที่ใช้เฉพาะตัวเลือกถูกปิดเฉพาะตัวเลือกโดยเมนูหลักยังสั่งได้ ทดสอบด้วยวัตถุดิบ 5 ชนิด ผลตรงกติกาอย่างน้อย 5 จาก 5 |
| US-13 | พนักงานครัว/หน้าร้าน | พนักงานครัว | กด “กลับมามี” เพื่อเปิดเมนูและตัวเลือกที่ปิดไปคืน | ขายต่อได้ทันทีเมื่อเติมวัตถุดิบ | นับจากกด “กลับมามี” จนถึงหน้าลูกค้าเปิดปุ่มสั่งคืน ภายใน 10 วินาทีบน LAN ในร้าน ในอย่างน้อย 9 จาก 10 ครั้ง และเมนู/ตัวเลือกที่กลับมาตรงกับชุดที่ถูกปิดจากวัตถุดิบนั้น |
| US-14 | พนักงานครัว/หน้าร้าน | พนักงานครัว | จัดการรายการในคิวที่ทำไม่ได้เพราะวัตถุดิบหมด (กด “ทำไม่ได้” แล้วส่งให้ลูกค้าเลือกทางออก) | ไม่มีออเดอร์ค้างคิวโดยไม่มีข้อสรุป | รายการที่กด “ทำไม่ได้” ย้ายไปสถานะ “รอลูกค้าตัดสินใจ” และเมื่อลูกค้าเปลี่ยนเมนูหรือคืนรายการ จอครัวอัปเดตรายการใหม่หรือลบรายการภายใน 10 วินาทีบน LAN ทดสอบผ่าน 5 จาก 5 กรณี |
| US-15 | พนักงานครัว/หน้าร้าน | พนักงานหน้าร้าน | เห็นออเดอร์แยกตามโต๊ะและตามสั่งกลับบ้าน พร้อมสถานะจ่ายเงินที่ระบบคำนวณเอง | เสิร์ฟถูกโต๊ะและส่งถุงสั่งกลับบ้านถูกคน | จอหน้าร้านแสดงหมายเลขโต๊ะ (จาก table_id ของ QR) สำหรับออเดอร์หน้าร้าน และหมายเลขรับสั่งกลับบ้านรูปแบบ T-001, T-002, … ที่ระบบสร้างอัตโนมัติ เรียงต่อเนื่อง และรีเซ็ตเป็น T-001 เมื่อเริ่มวันใหม่ (00:00) ครบทุกออเดอร์ 20 จาก 20 ใบของชุดทดสอบ · เกณฑ์ระบบ: สถานะ “จ่ายแล้ว/ยังไม่จ่าย/ค้างจ่าย” บนจอเปลี่ยนตามเหตุการณ์ในระบบ (ออเดอร์ใหม่ = ยังไม่จ่าย · เลือก PromptPay = ค้างจ่าย · กด “รับเงินสด” หรือ “ยืนยันสลิป” = จ่ายแล้ว) ถูกต้อง 20 จาก 20 ใบเมื่อเทียบกับ log เหตุการณ์ · เกณฑ์การยืนยันด้วยมือ: การกดของพนักงานหน้าร้านต้องระบุชื่อผู้ใช้และเวลาไว้ใน log ทุกครั้ง 20 จาก 20 ใบ |
| US-16 | พนักงานครัว/หน้าร้าน | พนักงานหน้าร้าน | เปิดโต๊ะและปิดโต๊ะ โดยปิดแล้ว QR โต๊ะนั้นสั่งต่อจากรอบเดิมไม่ได้ | ปล่อยโต๊ะให้ลูกค้าคนต่อไปโดยบิลไม่ปนกัน | เมื่อกดปิดโต๊ะ การสแกน QR โต๊ะเดิมเริ่มรอบสั่งใหม่ (session ใหม่) และรายการรอบเดิมไม่ปรากฏ ทดสอบ 5 โต๊ะ ผ่านอย่างน้อย 5 จาก 5 |
| US-17 | พนักงานครัว/หน้าร้าน | พนักงานหน้าร้าน | รวมบิลหลายรอบสั่งของโต๊ะเดียวกันเป็นยอดเดียว | เก็บเงินได้ครบในครั้งเดียว | โต๊ะที่สั่ง 3 รอบ ยอดรวมบิลเท่ากับผลรวมของทุกรายการ (ตรวจด้วยเครื่องคิดเลข) ในอย่างน้อย 9 จาก 10 โต๊ะทดสอบ และบิลรวมแสดงรายการแยกตามรอบ |
| US-18 | พนักงานครัว/หน้าร้าน | พนักงานครัวในช่วงเร่งด่วน | เห็นจำนวนออเดอร์ค้างและออเดอร์ที่ค้างนานสุดบนจอครัว | จัดคิวและรู้ว่าต้องเร่งจานไหน | จอครัวแสดงตัวนับออเดอร์ค้าง และออเดอร์ที่ค้างเกิน 15 นาที (นับจากเวลาลูกค้ากดยืนยันสั่ง) เปลี่ยนเป็นสีแดง ทดสอบ 10 ออเดอร์ที่ปล่อยเกินเวลา ผ่านอย่างน้อย 9 จาก 10 |

## แยก functional assertions / NFR

F10-a เป็นต้นเป็นชื่อ clause ภายในเอกสารนี้ ไม่ใช่ FR หรือรหัสข้อกำหนดใหม่ ตัวเลขในคอลัมน์เชื่อมโยงหมายถึง n ของ TestID ของ US แถวนั้น; อ่าน ID เต็มในดัชนีถัดไป

| US | Functional assertions | NFR / เกณฑ์ที่ต้องแยกหลักฐาน | เชื่อม scenario / ข้อค้าง |
|---|---|---|---|
| US-10 | F10-a แสดงใบใหม่; F10-b เรียง timestamp เซิร์ฟเวอร์ระดับวินาที; F10-c tie-break monotonic +1 ไม่ซ้ำไม่ย้อน | N10-a 3 วินาที/18 จาก 20; N10-b 2 มือถือพร้อมกัน 30 ใบ/30 จาก 30 × 3 รอบ ไม่สลับคู่ | 1,2,3,4; ขอบส่งซ้ำ/รีสตาร์ต→5 |
| US-11 | F11-a 1 แตะต่อการเปลี่ยน; F11-b หน้าร้านเห็นสถานะอาหาร กำลังทำ/เสร็จแล้วตามข้อความ US | N11 ครัว→หน้าร้าน 5 วินาที/18 จาก 20 | 1,2,4; transition ซ้ำ/ย้อน→3 |
| US-12 | F12-a แมปล่วงหน้า; F12-b กดหมด1ครั้งปิด whole; F12-c ปิด option แต่เมนูหลักยังสั่งได้; 5 ชนิด/5 จาก 5 เป็นเกณฑ์ functional | ไม่มี NFR เฉพาะ; ไม่ยืม 10 วินาทีของ US-06 มาเพิ่ม | 1,2,3; stale cart→4; กฎซ้อน/หมายเหตุ ค.→5 และข้อค้าง |
| US-13 | F13-a เปิดปุ่มคืน; F13-b ชุดเปิดตรงชุดปิดทั้งเมนูและตัวเลือก | N13 10 วินาที/9 จาก 10 บน LAN | 1,2,3; เหตุซ้อน/เปลี่ยนแมป→4 |
| US-14 | F14-a pending; F14-b เปลี่ยนแล้วอัปเดต; F14-c คืนแล้วลบ | N14 ลูกค้าเลือกสำเร็จ→ครัว 10 วินาที/5 จาก 5 บน LAN | 1,2,3,5; เมนูแทนหมด→4; คำสั่งซ้อน/ซ้ำ→6 |
| US-15 | F15-a table_id; F15-b T-001,T-002,… ต่อเนื่อง/รีเซ็ต00:00; F15-c ใหม่/PromptPay/รับสด/ยืนยันสลิป เปลี่ยนสถานะตามเหตุการณ์ | N15-log ชื่อผู้ใช้+เวลา/สถานะเทียบ log; ทั้งสามเกณฑ์ 20 จาก 20 แยกกัน | 1,2,3,4,5,6; กดยืนยันซ้ำ→7 |
| US-16 | F16-a เปิด/ปิด; F16-b QRเดิม sessionใหม่ ไม่แสดงรายการเก่า; F16-c สั่งต่อรอบปิดไม่ได้; 5โต๊ะ/5จาก5 | NFR-21 แยกรอบฝั่งระบบจริง ไม่ได้เพิ่มตัวเลขใหม่ | 1,2,3; ค้างทำ/ค้างจ่ายขณะปิด→4 |
| US-17 | F17-a รวมทุกรายการ3รอบและเครื่องคิดเลข/9จาก10โต๊ะ; F17-b รายการแยกตามรอบ | ไม่มี NFR mapping; ไม่ตั้งรหัสใหม่ | 1; ผลผิดปกติ/ขอบเขตรอบ→2; FR/Flow/UI MISSING |
| US-18 | F18-a counterค้าง; F18-b เกิน15นาทีจากกดยืนยันเป็นสีแดง/9จาก10; ข้อความ US ต้องเห็นค้างนานสุด | 15นาทีเป็น threshold ธุรกิจ ไม่ใช่ SLA ส่งข้อมูล; ไม่มี NFR mapping | 1,2; นิยามค้าง/สถานะรวม→3; FR/Flow/UI MISSING |

## Precondition และ scope ที่ใช้ร่วมกัน

คำย่อด้านล่างเป็นส่วนหนึ่งของทุก scenario ที่อ้าง ต้องขยายเป็นขั้นตอนจริงเมื่อนำไปสร้าง runner; ไม่ใช่การสั่งให้รันในขั้นนี้

- **R0:** เปิด `../step-00-input/ui-mockup-v2.html` ใน browser context ใหม่ แล้วกด `btn-reset` ก่อนเริ่มแต่ละ scenario เว้นแต่ระบุ reset ต่อกรณีย่อย คืนเวลา `2026-01-01T12:00:00+07:00`, โต๊ะ01, dine-in, stockมี, PromptPayเปิด, คิว/ตะกร้า/เหตุการณ์ว่าง และออกจากระบบ สลับบทบาทระหว่าง scenario เดียวกันต้องไม่ reset/reload
- **C0:** กด `role-customer`; เลือก `table-select` ตาม Test data แล้ว `btn-open-menu` เพื่อเริ่ม/เปิด session เดิม หากกลับจากบทบาทอื่นให้รักษาโต๊ะ/session เดิม การส่งแต่ละใบ: เลือก `menu-item-<id>`, ติ๊ก `option-<id>` เฉพาะที่ระบุ, กด `btn-add-item` ต่อจาน แล้ว `btn-submit-order`; จด `order-id` ของใบที่เพิ่งสร้าง จำนวนจานใน fixture หมายถึงเพิ่มแยกครั้ง ไม่สมมติว่ามีช่อง quantity
- **K0/F0:** กด `role-staff` ทุกครั้งที่สลับเข้า เลือก `staff-user` เป็น `demokitchen` / `demofront`, กรอก `staff-pin=0000`, กด `btn-login` แล้ว `nav-kitchen` / `nav-front` ตามบทบาท เป็นบัญชีทดสอบสาธารณะในสัญญา ไม่ใช่บัญชีจริง
- **M0:** กด `role-manager`, เลือก `demomanager` กับ PIN `0000`, กด `btn-login` แล้วเข้า `nav-mapping` เมื่อต้องดูแมป ใช้ข้ามบทบาทเพื่อ setup เท่านั้น เจ้าของ US ไม่เปลี่ยน
- **SCOPE:** `K(o) = [data-testid="kitchen-queue"] [data-testid="kitchen-order"][data-order-id="<o>"]`; `F(o) = [data-testid="front-orders"] [data-testid="front-order"][data-order-id="<o>"]`; `R(o,i) = [data-testid="customer-item-resolutions"] [data-testid="customer-resolution-order"][data-order-id="<o>"] [data-testid="item-resolution"][data-item-id="<i>"]` โดยแทน o/i ด้วย ID ที่อ่านจริง ไม่ใช้ตัวแรกอัตโนมัติ
- **รายการ:** ใน K(o)/F(o) ใช้ `li[data-item-id="<i>"]` เพราะ attribute เดียวกันมีที่ปุ่มด้วย; ปุ่มทำไม่ได้ใช้ `K(o) [data-testid="btn-item-unavailable"][data-item-id="<i>"]` (descendant ไม่ใช่ direct child) จด item ID จาก li ที่ชื่อ/ตัวเลือกตรง Test data ก่อนกระทำ ตรวจพบหนึ่งรายการเป้าหมายก่อนคลิก
- **Scope ทั่วไป:** selector ลูกค้าอยู่ใน `screen-customer`, ครัว/หน้าร้านใน `screen-staff`, ผู้จัดการใน `screen-manager`; role/reset/sim-clock/เพิ่มเวลาอยู่ส่วนกลาง และ staff-user/staff-pin/btn-login อยู่ฟอร์ม login ที่แสดง ห้าม scope ฟอร์ม login ใต้ screen-staff ที่ไม่มีฟอร์มนั้น รายการ menu ใช้ `menu-list` กับ menu-item-ID; option อยู่ในรายละเอียดจานที่เลือก
- **สถานะอาหาร:** ไม่มี data-testid เฉพาะสถานะอาหารหน้าร้าน ให้อ่านข้อความ กำลังทำ/เสร็จแล้วภายใน F(o) ใบเป้าหมาย ไม่ใช้ `front-payment-status` แทน ไม่ถือ เสร็จแล้ว เท่ากับ พร้อมเสิร์ฟ โดยอัตโนมัติ
- **หลักฐานที่ต้องเก็บเมื่อรันภายหลัง:** TestID, hash Input, reset/เวลา/ข้อมูลจำลอง, order/item/session IDs, ผลทุก assertion, Actual result และภาพที่แสดงผลจริง; ระบบจริงเพิ่มเหตุการณ์ต้น–ปลายและ log แยกต่อใบ/รอบ UI ที่เปิดไม่ได้เป็นปัญหา infrastructure ตาม coverage-criteria ไม่ใช่เหตุเปลี่ยน auto เป็น skip เพื่อซ่อนปัญหา

## ดัชนี US → TestID และ coverage ของบทบาทนี้

ตารางนี้มี 9 US ตามขอบเขตครัว/หน้าร้าน ตารางรวม 26 US ตาม coverage-criteria เป็นงานผู้รวมผล ต้องรวมกับอีกสองบทบาท; ไม่สร้าง/อ้าง coverage นอกขอบเขตนี้ และไม่ถือขั้นต่ำ 52 scenarios ของทั้งระบบเป็นจำนวนที่ต้องสร้างในไฟล์บทบาทเดียว

| US | สำเร็จ | ทางเลือก | ผิดพลาด | ข้อยกเว้น | fixture ของ US นี้ (อ้างเท่านั้น) |
|---|---|---|---|---|---|
| US-10 | TS-US-10-1, TS-US-10-3 | TS-US-10-2 | TS-US-10-5 | TS-US-10-4 | ไม่มี fixture ของ US นี้ใน JSON |
| US-11 | TS-US-11-1, TS-US-11-4 | TS-US-11-2 | TS-US-11-3 (oracle เดิมยัง BLOCKED), TS-US-11-5 | N/A — ใช้อีกประเภทผิดพลาด/ข้อยกเว้นตามเกณฑ์ OR | TS-US-11-101 |
| US-12 | TS-US-12-1, TS-US-12-3 | TS-US-12-2 | TS-US-12-4 | TS-US-12-5 | TS-US-12-101 |
| US-13 | TS-US-13-1, TS-US-13-3 | TS-US-13-2 | N/A — ใช้อีกประเภทผิดพลาด/ข้อยกเว้นตามเกณฑ์ OR | TS-US-13-4 | ไม่มี fixture ของ US นี้ใน JSON |
| US-14 | TS-US-14-1, TS-US-14-5 | TS-US-14-2, TS-US-14-3 | TS-US-14-4 | TS-US-14-6 | TS-US-14-101 |
| US-15 | TS-US-15-1, TS-US-15-3, TS-US-15-6 | TS-US-15-2, TS-US-15-4 | TS-US-15-7 | TS-US-15-5 | ไม่มี fixture ของ US นี้ใน JSON |
| US-16 | TS-US-16-1, TS-US-16-3 | N/A — AC ไม่ระบุทางเลือกแยก; ขอบ/ข้อผิดพลาดมีช่องอื่น | TS-US-16-4 | TS-US-16-2 | ไม่มี fixture ของ US นี้ใน JSON |
| US-17 | TS-US-17-1 | N/A — AC ไม่ระบุทางเลือกแยก; ขอบ/ข้อผิดพลาดมีช่องอื่น | TS-US-17-2 (oracle เดิมยัง BLOCKED), TS-US-17-3 | N/A — ใช้อีกประเภทผิดพลาด/ข้อยกเว้นตามเกณฑ์ OR | ไม่มี fixture ของ US นี้ใน JSON |
| US-18 | TS-US-18-1 | N/A — AC ไม่ระบุทางเลือกแยก; ขอบ/ข้อผิดพลาดมีช่องอื่น | TS-US-18-3 | TS-US-18-2 | ไม่มี fixture ของ US นี้ใน JSON |

N/A ไม่ได้ใช้แทน clause ที่ข้อมูลขาด: ข้อที่ยังไม่มีข้อมูลระบุ BLOCKED/MISSING ใน scenario และทะเบียนข้อค้าง ทุก US มีแบบสำเร็จและผิดพลาดหรือข้อยกเว้น แต่บาง oracle รอคำตอบ จึงยังไม่ประกาศ COVERED

## การอ้าง fixture สงวน (ไม่สร้างซ้ำ)

ทั้งหมดอยู่ใน `../../input/ui-scenarios.json`; สถานะการรันรอบนี้ **NOT_RUN** ไม่มี Actual/หลักฐาน

| fixture | เชื่อมแบบออกแบบ | assertion ที่ fixture มีจริง / สิ่งที่ยังขาด |
|---|---|---|
| TS-US-11-101 | TS-US-11-1, TS-US-11-2, TS-US-11-4 | สร้างหนึ่งใบ กดสถานะหนึ่งครั้งแล้ว expect กำลังทำใน front-orders; ปุ่มซ้ำไม่กำกวมเพราะมีใบเดียว; ไม่ตรวจเสร็จแล้ว ไม่วัด5วินาที/18จาก20 |
| TS-US-12-101 | TS-US-12-2, TS-US-12-3 | ปิดeggแล้วส่งm01ไม่ใส่ไข่และexpectรับออเดอร์; ยังไม่มีassertion extra-egg disabled และไม่ครบ5ชนิด |
| TS-US-14-101 | TS-US-14-1, TS-US-14-2, TS-US-14-3, TS-US-14-5 | หนึ่งใบ/หนึ่งจาน กดทำไม่ได้แล้วexpectรอลูกค้าตัดสินใจในkitchen-queue; ไม่ตรวจเปลี่ยน/คืนหรือ10วินาที/5จาก5 |
| TS-US-06-101 (เจ้าของลูกค้า) | TS-US-12-4 | สนับสนุนตะกร้าค้างถูกปฏิเสธเมื่อchickenหมด ไม่สร้างใหม่ในช่วงสงวน |
| TS-US-08-102 (เจ้าของลูกค้า) | TS-US-15-3 | เลือกสดยังไม่จ่าย แล้วหน้าร้านรับสด ลูกค้าเห็นจ่ายแล้ว; ยังไม่assert logชื่อผู้ใช้/เวลา |
| TS-US-08-101 (เจ้าของลูกค้า) | setup ที่เกี่ยวสถานะ US-15 | ตรวจค้างจ่ายและข้อความเงินสดเมื่อเพิ่มเวลา10นาที; ไม่ใช่ผลตรวจ20ใบหรือเงินเข้า |
| TS-US-09-101 (เจ้าของลูกค้า) | TS-US-14-3 | หนึ่งใบm01=50 คืนแล้วexpect payment-summary-total=0บาท; ชื่อนี้ไม่มีในHTMLv2 จึงติดข้อค้างความเข้ากันได้ ห้ามอ้างรันผ่านหรือแก้JSONในงานนี้ |

สำหรับ TS-US-09-101 ชื่อที่พบจริง `customer-adjusted-total` ใช้ได้เฉพาะออเดอร์ล่าสุดของ fixture ใบเดียว; ไม่ใช่ยอดทั้งsession ถ้าหลายใบให้ใช้ `resolution-order-total` ตาม order ID และ `front-adjusted-total` ใน F(o) อย่าใช้ `cart-total` หรือ `front-total` เป็นยอดบิลหลังคืน ส่วนสัญญา capacity ที่เกี่ยว setup มี rush-start/rush-end ต่างจาก capacity-start/capacity-end ใน HTML; ไม่ได้แก้ fixture หรือเพิ่ม scenario US-21 ในขอบเขตนี้

## Scenario ตามแม่แบบ

<a id="design-ts-us-10-1"></a>

## TS-US-10-1 — ออเดอร์ใหม่ปรากฏและเรียงตามเวลารับ

- US: US-10
- เจ้าของ: kitchen-front
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: นับจากลูกค้ากดยืนยันสั่ง จนถึงจอครัวแสดงออเดอร์ใหม่ ภายใน 3 วินาทีบน LAN ในร้าน ในอย่างน้อย 18 จาก 20 ใบของชุดทดสอบ · กฎเรียงลำดับ: เรียงตาม timestamp ฝั่งเซิร์ฟเวอร์ที่รับคำสั่ง (ความละเอียดวินาที) จากน้อยไปมาก และเมื่อ timestamp เท่ากันหรือออเดอร์เข้าพร้อมกัน ให้เรียงตามเลขออเดอร์ที่ระบบออกให้แบบ monotonic (เพิ่มขึ้นทีละ 1 ไม่ซ้ำ ไม่ย้อนกลับ) · ทดสอบยิง 30 ออเดอร์ต่อเนื่องจากมือถือ 2 เครื่องพร้อมกัน ลำดับบนจอครัวต้องตรงกับลำดับเลขออเดอร์ 30 จาก 30 ใบ และรันซ้ำ 3 รอบต้องได้ผลเดิมทุกรอบ (ไม่ยอมรับการสลับคู่)
- clause ที่ตรวจ: F10-a: แสดงออเดอร์ใหม่; F10-b: timestamp ระดับวินาทีเรียงน้อยไปมาก
- FR / Flow / Screen: FR-10; NFR-06 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-04 → SCR-03 / SCR-06 / SCR-08 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: ตรวจการแสดงและเรียงข้อมูลจำลองได้; server timestamp และเวลา LAN ต้องตรวจ TS-US-10-3/4
- Precondition/reset: R0; เปิดโต๊ะ 01 ตาม C0; คิวว่าง
- Test data: m01=50 บาท รายการละ 1; 3 ออเดอร์ที่เวลาจำลอง 12:00, 12:10, 12:20 (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: C0, K0; kitchen-queue > kitchen-order ทั้งชุดเพื่ออ่านลำดับ; K(o) สำหรับแต่ละใบ; sim-clock, btn-advance-10m ส่วนกลาง; ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. C0 ส่งใบแรก จด order-id
  2. กด btn-advance-10m แล้วส่งใบที่สอง
  3. เพิ่มเวลาอีก 10 นาทีแล้วส่งใบที่สาม
  4. K0 อ่าน kitchen-order ทุกใบและ data-received-at
  5. สลับลูกค้าแล้วกลับ K0 ตรวจลำดับซ้ำ
- Expected result: ใบครัวครบ 3 ใบ ตรง order ID ที่จด; timestamp ISO มีความละเอียดวินาทีและเรียงน้อยไปมาก; เลขออเดอร์เพิ่มทีละ 1 ไม่ซ้ำไม่ย้อน; ลำดับเดิมหลังสลับบทบาท
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: 3 วินาทีบน LAN ในร้าน อย่างน้อย 18 จาก 20 ใบ; เรียง timestamp ฝั่งเซิร์ฟเวอร์ความละเอียดวินาทีและเลข monotonic เพิ่มขึ้นทีละ 1 ไม่ซ้ำ ไม่ย้อนกลับ; มือถือ 2 เครื่องพร้อมกัน 30 ออเดอร์ ต้องตรง 30 จาก 30 ใบ รันซ้ำ 3 รอบได้ผลเดิมทุกรอบ ไม่ยอมรับการสลับคู่; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: ช่วงเวลาและ 3 ใบเป็น fixture ไม่แทน 20 ใบหรือ 30 ใบ × 3 รอบ
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-10-2"></a>

## TS-US-10-2 — เวลารับเท่ากันใช้เลขออเดอร์ตัดสินลำดับ

- US: US-10
- เจ้าของ: kitchen-front
- ประเภท: ทางเลือก
- AC ต้นฉบับเต็ม: นับจากลูกค้ากดยืนยันสั่ง จนถึงจอครัวแสดงออเดอร์ใหม่ ภายใน 3 วินาทีบน LAN ในร้าน ในอย่างน้อย 18 จาก 20 ใบของชุดทดสอบ · กฎเรียงลำดับ: เรียงตาม timestamp ฝั่งเซิร์ฟเวอร์ที่รับคำสั่ง (ความละเอียดวินาที) จากน้อยไปมาก และเมื่อ timestamp เท่ากันหรือออเดอร์เข้าพร้อมกัน ให้เรียงตามเลขออเดอร์ที่ระบบออกให้แบบ monotonic (เพิ่มขึ้นทีละ 1 ไม่ซ้ำ ไม่ย้อนกลับ) · ทดสอบยิง 30 ออเดอร์ต่อเนื่องจากมือถือ 2 เครื่องพร้อมกัน ลำดับบนจอครัวต้องตรงกับลำดับเลขออเดอร์ 30 จาก 30 ใบ และรันซ้ำ 3 รอบต้องได้ผลเดิมทุกรอบ (ไม่ยอมรับการสลับคู่)
- clause ที่ตรวจ: F10-c: timestamp เท่ากันให้เรียงเลข monotonic เพิ่มทีละ 1 ไม่ซ้ำ ไม่ย้อนกลับ
- FR / Flow / Screen: FR-10; NFR-06 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-04 → SCR-03 / SCR-06 / SCR-08 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: ตรวจ tie-break จำลองในแท็บเดียว; ไม่ใช่การรับพร้อมกันจากมือถือ 2 เครื่อง
- Precondition/reset: R0; C0; ไม่ขยับ sim-clock ระหว่างส่ง
- Test data: m01=50 บาท × 3 ออเดอร์ ณ 12:00:00+07:00 (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: C0, K0; kitchen-queue > kitchen-order ทั้งชุด, K(o); sim-clock; ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. C0 ส่ง 3 ครั้งแยกตะกร้าโดยไม่ขยับเวลา จด ID ทุกครั้ง
  2. K0 อ่าน attribute ของทุกใบ
  3. สลับบทบาทแล้วกลับครัวอ่านซ้ำ
- Expected result: ทั้ง 3 ใบมี data-received-at เท่ากัน เรียงเลขเพิ่มทีละ 1 ไม่ซ้ำไม่ย้อนและไม่สลับคู่หลังแสดงใหม่
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: 3 วินาทีบน LAN ในร้าน อย่างน้อย 18 จาก 20 ใบ; เรียง timestamp ฝั่งเซิร์ฟเวอร์ความละเอียดวินาทีและเลข monotonic เพิ่มขึ้นทีละ 1 ไม่ซ้ำ ไม่ย้อนกลับ; มือถือ 2 เครื่องพร้อมกัน 30 ออเดอร์ ต้องตรง 30 จาก 30 ใบ รันซ้ำ 3 รอบได้ผลเดิมทุกรอบ ไม่ยอมรับการสลับคู่; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: การยิงพร้อมกันจริงใช้ TS-US-10-4; ขอบเขตเลขข้ามวันยัง Q-10
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-10-3"></a>

## TS-US-10-3 — เวลายืนยันสั่งถึงจอครัวบน LAN

- US: US-10
- เจ้าของ: kitchen-front
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: นับจากลูกค้ากดยืนยันสั่ง จนถึงจอครัวแสดงออเดอร์ใหม่ ภายใน 3 วินาทีบน LAN ในร้าน ในอย่างน้อย 18 จาก 20 ใบของชุดทดสอบ · กฎเรียงลำดับ: เรียงตาม timestamp ฝั่งเซิร์ฟเวอร์ที่รับคำสั่ง (ความละเอียดวินาที) จากน้อยไปมาก และเมื่อ timestamp เท่ากันหรือออเดอร์เข้าพร้อมกัน ให้เรียงตามเลขออเดอร์ที่ระบบออกให้แบบ monotonic (เพิ่มขึ้นทีละ 1 ไม่ซ้ำ ไม่ย้อนกลับ) · ทดสอบยิง 30 ออเดอร์ต่อเนื่องจากมือถือ 2 เครื่องพร้อมกัน ลำดับบนจอครัวต้องตรงกับลำดับเลขออเดอร์ 30 จาก 30 ใบ และรันซ้ำ 3 รอบต้องได้ผลเดิมทุกรอบ (ไม่ยอมรับการสลับคู่)
- clause ที่ตรวจ: N10-a: 3 วินาทีบน LAN อย่างน้อย 18 จาก 20 ใบ
- FR / Flow / Screen: FR-10; NFR-06 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-04 → SCR-03 / SCR-06 / SCR-08 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: จำเป็นต้องมีเครือข่ายและอุปกรณ์จริง; นาฬิกาจำลองไม่เป็นหลักฐาน SLA
- Precondition/reset: ระบบจริงสำหรับทดสอบบน LAN ร้านพร้อมมือถือและจอครัว; ขณะนี้ไม่มีระบบและ log
- Test data: 20 ออเดอร์จำลอง รายการ m01 จำนวน 1 ต่อใบ; จด order ID และเวลาต้น–ปลายรายใบ (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: Mock มี btn-submit-order, K(o); selector ของระบบจริง MISSING ต้องตรวจเมื่อมีระบบ; ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. บนระบบจริงให้ลูกค้ากดยืนยันทีละใบ
  2. บันทึก t0 ขณะกดยืนยันและ t1 เมื่อจอครัวแสดงใบตรง ID
  3. ทำครบ 20 ใบ
  4. คำนวณ t1−t0 และจำนวนใบที่ไม่เกิน 3 วินาที
- Expected result: จอครัวแสดงออเดอร์ตรง ID; t1−t0 ≤3 วินาทีอย่างน้อย 18 จาก 20 ใบ; รายงานแต่ละใบแยกจากค่าเฉลี่ย
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: 3 วินาทีบน LAN ในร้าน อย่างน้อย 18 จาก 20 ใบ; เรียง timestamp ฝั่งเซิร์ฟเวอร์ความละเอียดวินาทีและเลข monotonic เพิ่มขึ้นทีละ 1 ไม่ซ้ำ ไม่ย้อนกลับ; มือถือ 2 เครื่องพร้อมกัน 30 ออเดอร์ ต้องตรง 30 จาก 30 ใบ รันซ้ำ 3 รอบได้ผลเดิมทุกรอบ ไม่ยอมรับการสลับคู่; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: BLOCKED: ไม่มีระบบ LAN/หลักฐานเวลา; วิธีจับเวลาและความคลาดเคลื่อนเครื่องมือรอยืนยัน
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-10-4"></a>

## TS-US-10-4 — รับคำสั่งจากสองมือถือพร้อมกันโดยไม่สลับคู่

- US: US-10
- เจ้าของ: kitchen-front
- ประเภท: ข้อยกเว้น
- AC ต้นฉบับเต็ม: นับจากลูกค้ากดยืนยันสั่ง จนถึงจอครัวแสดงออเดอร์ใหม่ ภายใน 3 วินาทีบน LAN ในร้าน ในอย่างน้อย 18 จาก 20 ใบของชุดทดสอบ · กฎเรียงลำดับ: เรียงตาม timestamp ฝั่งเซิร์ฟเวอร์ที่รับคำสั่ง (ความละเอียดวินาที) จากน้อยไปมาก และเมื่อ timestamp เท่ากันหรือออเดอร์เข้าพร้อมกัน ให้เรียงตามเลขออเดอร์ที่ระบบออกให้แบบ monotonic (เพิ่มขึ้นทีละ 1 ไม่ซ้ำ ไม่ย้อนกลับ) · ทดสอบยิง 30 ออเดอร์ต่อเนื่องจากมือถือ 2 เครื่องพร้อมกัน ลำดับบนจอครัวต้องตรงกับลำดับเลขออเดอร์ 30 จาก 30 ใบ และรันซ้ำ 3 รอบต้องได้ผลเดิมทุกรอบ (ไม่ยอมรับการสลับคู่)
- clause ที่ตรวจ: F10-b/c และ N10-b: concurrent 30 ใบจากมือถือ 2 เครื่อง, 30 จาก 30, รันซ้ำ 3 รอบ
- FR / Flow / Screen: FR-10; NFR-06 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-04 → SCR-03 / SCR-06 / SCR-08 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: ต้องมีการรับคำสั่งพร้อมกันจริงและ log เซิร์ฟเวอร์; sequential mock ไม่พิสูจน์ concurrency
- Precondition/reset: ระบบทดสอบจริงบน LAN; มือถือ 2 เครื่องและจอครัว; เปิดรอบทดสอบที่แยกหลักฐานได้
- Test data: รอบละ 30 ออเดอร์จำลอง รวม 3 รอบ; แบ่งมือถือเครื่องละ 15 เป็นวิธีจัด fixture; ครอบคลุมเวลารับระดับวินาทีที่เท่ากัน (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: Mock อ้าง K(o), kitchen-queue; selector/API server และเครื่องมือ concurrent จริง MISSING; ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. สั่งต่อเนื่องจากทั้งสองเครื่องพร้อมกัน
  2. เก็บ server received timestamp ระดับวินาที, ID และลำดับหน้าจอทั้ง 30 ใบ
  3. เทียบลำดับ timestamp แล้ว ID และเลขต่อเนื่อง
  4. ทำซ้ำครบ 3 รอบด้วยรูปแบบเดียวกัน
- Expected result: แต่ละรอบ ID เพิ่มทีละ 1 ไม่ซ้ำไม่ย้อน; จอครัวตรงลำดับเลขออเดอร์ 30 จาก 30 ใบ; ทุก 3 รอบได้ผลการเรียงตามกฎเดียวกัน ไม่ยอมรับการสลับคู่แม้คู่เดียว; เก็บเลขจริงแต่ละรอบโดยไม่บังคับรีเซ็ตเลข
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: 3 วินาทีบน LAN ในร้าน อย่างน้อย 18 จาก 20 ใบ; เรียง timestamp ฝั่งเซิร์ฟเวอร์ความละเอียดวินาทีและเลข monotonic เพิ่มขึ้นทีละ 1 ไม่ซ้ำ ไม่ย้อนกลับ; มือถือ 2 เครื่องพร้อมกัน 30 ออเดอร์ ต้องตรง 30 จาก 30 ใบ รันซ้ำ 3 รอบได้ผลเดิมทุกรอบ ไม่ยอมรับการสลับคู่; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: BLOCKED: ไม่มีระบบและ log; ไม่เฉลี่ยข้ามรอบและไม่สมมติว่าทุกรอบต้องเริ่มเลข 1
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-10-5"></a>

## TS-US-10-5 — ส่งซ้ำหรือเริ่มระบบใหม่ระหว่างออกเลข

- US: US-10
- เจ้าของ: kitchen-front
- ประเภท: ผิดพลาด
- AC ต้นฉบับเต็ม: นับจากลูกค้ากดยืนยันสั่ง จนถึงจอครัวแสดงออเดอร์ใหม่ ภายใน 3 วินาทีบน LAN ในร้าน ในอย่างน้อย 18 จาก 20 ใบของชุดทดสอบ · กฎเรียงลำดับ: เรียงตาม timestamp ฝั่งเซิร์ฟเวอร์ที่รับคำสั่ง (ความละเอียดวินาที) จากน้อยไปมาก และเมื่อ timestamp เท่ากันหรือออเดอร์เข้าพร้อมกัน ให้เรียงตามเลขออเดอร์ที่ระบบออกให้แบบ monotonic (เพิ่มขึ้นทีละ 1 ไม่ซ้ำ ไม่ย้อนกลับ) · ทดสอบยิง 30 ออเดอร์ต่อเนื่องจากมือถือ 2 เครื่องพร้อมกัน ลำดับบนจอครัวต้องตรงกับลำดับเลขออเดอร์ 30 จาก 30 ใบ และรันซ้ำ 3 รอบต้องได้ผลเดิมทุกรอบ (ไม่ยอมรับการสลับคู่)
- clause ที่ตรวจ: ข้อค้างของ F10-c: ขอบเขต monotonic เมื่อส่งซ้ำ/รีสตาร์ต
- FR / Flow / Screen: FR-10; NFR-06 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-04 → SCR-03 / SCR-06 / SCR-08 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: ต้องมีระบบจริงและคำตอบธุรกิจ; ไม่ใช้ btn-reset เป็นการรีสตาร์ต server
- Precondition/reset: สภาพทดสอบแยกจากข้อมูลจริง; ต้องมีระบบและนโยบาย Q-10 ก่อนรัน
- Test data: คำสั่งจำลองหนึ่งใบและสำเนาคำสั่งเดิม; เก็บเลขก่อนรีสตาร์ต (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: MISSING: ไม่มี selector/ช่องส่งซ้ำหรือรีสตาร์ตระบบจริงใน UI v2; ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. เมื่อยืนยันนโยบายแล้ว ส่งคำสั่งเดิมซ้ำ
  2. ทดลองรีสตาร์ตระบบทดสอบและส่งคำสั่งถัดไป
  3. เก็บ log การรับ/สร้างเลข
- Expected result: BLOCKED/ไม่มีข้อมูลสำหรับตัดสินว่าคำสั่งซ้ำเป็นใบเดิมหรือใหม่และเลขต่อหลังรีสตาร์ตอย่างไร; กฎ monotonic ใน AC ยังคงเดิม ต้องได้ขอบเขตก่อนกำหนด oracle
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: 3 วินาทีบน LAN ในร้าน อย่างน้อย 18 จาก 20 ใบ; เรียง timestamp ฝั่งเซิร์ฟเวอร์ความละเอียดวินาทีและเลข monotonic เพิ่มขึ้นทีละ 1 ไม่ซ้ำ ไม่ย้อนกลับ; มือถือ 2 เครื่องพร้อมกัน 30 ออเดอร์ ต้องตรง 30 จาก 30 ใบ รันซ้ำ 3 รอบได้ผลเดิมทุกรอบ ไม่ยอมรับการสลับคู่; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: รอยืนยัน Q-10; ไม่เพิ่มกฎ idempotency หรือรีเซ็ตเลขเอง
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-11-1"></a>

## TS-US-11-1 — หนึ่งแตะเปลี่ยนเป็นกำลังทำและหน้าร้านเห็น

- US: US-11
- เจ้าของ: kitchen-front
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: เปลี่ยนสถานะได้ใน 1 แตะ และนับจากกดปุ่มบนจอครัว จนถึงจอหน้าร้านแสดงสถานะใหม่ ภายใน 5 วินาทีบน LAN ในร้าน ในอย่างน้อย 18 จาก 20 ครั้งของชุดทดสอบ
- clause ที่ตรวจ: F11-a: เปลี่ยนสถานะได้ใน 1 แตะ; F11-b: หน้าร้านแสดงสถานะใหม่
- FR / Flow / Screen: FR-11; NFR-07 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-05 → SCR-04 / SCR-06 / SCR-08 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: รันจำลองได้; การสลับบทบาทไม่วัดส่งข้ามเครื่อง; เชื่อม fixture TS-US-11-101 ซึ่งตรวจเฉพาะกำลังทำ
- Precondition/reset: R0; C0 สร้าง 1 ใบ แล้ว K0; สถานะ fixture รับออเดอร์
- Test data: m01=50 บาท 1 จาน; จด o จาก order-id (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: C0, K0, F0; K(o) > btn-status-next; อ่าน F(o) ข้อความสถานะอาหาร (ไม่มี testid เฉพาะสถานะอาหาร); ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. คลิก K(o) > btn-status-next เพียง 1 ครั้ง
  2. อ่านสถานะครัว
  3. F0 ตรวจสถานะอาหารใน F(o)
  4. ไม่กดเปลี่ยนอีกระหว่างตรวจ
- Expected result: ครัวและหน้าร้านใบ o แสดง กำลังทำ หลังแตะครั้งเดียว; ใช้ข้อความสถานะอาหาร ไม่ใช้ front-payment-status เป็นคำตอบ
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: เปลี่ยนได้ใน 1 แตะ; ครัวกด→หน้าร้านแสดงใหม่ภายใน 5 วินาทีบน LAN ในร้าน อย่างน้อย 18 จาก 20 ครั้ง; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: ลำดับ รับออเดอร์→กำลังทำ เป็น fixture ตาม A-05/Q-11 ไม่ใช่การยืนยัน transition ทั้งระบบ
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-11-2"></a>

## TS-US-11-2 — หนึ่งแตะจากกำลังทำเป็นเสร็จแล้ว

- US: US-11
- เจ้าของ: kitchen-front
- ประเภท: ทางเลือก
- AC ต้นฉบับเต็ม: เปลี่ยนสถานะได้ใน 1 แตะ และนับจากกดปุ่มบนจอครัว จนถึงจอหน้าร้านแสดงสถานะใหม่ ภายใน 5 วินาทีบน LAN ในร้าน ในอย่างน้อย 18 จาก 20 ครั้งของชุดทดสอบ
- clause ที่ตรวจ: F11-a/b: ปลายทางเสร็จแล้วใน US และ 1 แตะต่อการเปลี่ยน
- FR / Flow / Screen: FR-11; NFR-07 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-05 → SCR-04 / SCR-06 / SCR-08 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: ตรวจปลายทางที่ fixture TS-US-11-101 ยังไม่ได้ตรวจ; ไม่พิสูจน์ LAN
- Precondition/reset: R0; สร้างหนึ่งใบ; K0 กด 1 ครั้งเป็นกำลังทำเป็น setup
- Test data: m01=50 บาท 1 จาน; o เดิม (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: C0, K0, F0; K(o) > btn-status-next; F(o); ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. บันทึกสถานะก่อนตรวจว่ากำลังทำ
  2. คลิก K(o) > btn-status-next 1 ครั้ง
  3. F0 อ่านสถานะอาหารใบเดิม
- Expected result: ใบ o แสดง เสร็จแล้ว ทั้งครัวและหน้าร้านหลังการแตะที่ตรวจ 1 ครั้ง; นับ setup แยกจากการแตะครั้งนี้
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: เปลี่ยนได้ใน 1 แตะ; ครัวกด→หน้าร้านแสดงใหม่ภายใน 5 วินาทีบน LAN ในร้าน อย่างน้อย 18 จาก 20 ครั้ง; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: ไม่ตีความ เสร็จแล้ว=พร้อมเสิร์ฟ เพื่อรับรอง ETA; DI-07/A-05 และ Q-05/11 เปิด
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-11-3"></a>

## TS-US-11-3 — กดสถานะซ้ำหลังเสร็จแล้วหรือขอย้อนสถานะ

- US: US-11
- เจ้าของ: kitchen-front
- ประเภท: ผิดพลาด
- AC ต้นฉบับเต็ม: เปลี่ยนสถานะได้ใน 1 แตะ และนับจากกดปุ่มบนจอครัว จนถึงจอหน้าร้านแสดงสถานะใหม่ ภายใน 5 วินาทีบน LAN ในร้าน ในอย่างน้อย 18 จาก 20 ครั้งของชุดทดสอบ
- clause ที่ตรวจ: ข้อค้าง transition/กดซ้ำของ F11-a
- FR / Flow / Screen: FR-11; NFR-07 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-05 → SCR-04 / SCR-06 / SCR-08 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: ปุ่มที่ปิดใน mock ไม่พิสูจน์การจัดการคำสั่งซ้ำของระบบจริง
- Precondition/reset: ต้องมี transition ที่ยืนยันและระบบทดสอบ; เตรียมใบเสร็จแล้ว
- Test data: ออเดอร์จำลอง 1 ใบ; คำสั่งเปลี่ยนซ้ำหรือขอย้อนรายการเดิม (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: Mock มี K(o) > btn-status-next ซึ่ง disabled เมื่อเสร็จแล้ว; ช่องคำสั่งย้อน/ซ้ำระบบจริง MISSING; ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. หลังยืนยันนโยบาย ทดลองกดหรือส่งคำสั่งซ้ำหลังเสร็จแล้วและขอย้อน
  2. เก็บสถานะก่อนหลังและ log
- Expected result: BLOCKED/ไม่มีข้อมูลว่าจะต้องคงเดิม ปฏิเสธ หรืออนุญาตย้อน; ไม่เพิ่มลำดับสถานะหรือข้อความผิดพลาดเอง
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: เปลี่ยนได้ใน 1 แตะ; ครัวกด→หน้าร้านแสดงใหม่ภายใน 5 วินาทีบน LAN ในร้าน อย่างน้อย 18 จาก 20 ครั้ง; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: Q-11 และ Q-05/DI-07; ปุ่ม disabled เป็นข้อกำหนด fixture เท่านั้น
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-11-4"></a>

## TS-US-11-4 — ครัวหนึ่งแตะส่งสถานะถึงหน้าร้านครบชุด LAN

- US: US-11
- เจ้าของ: kitchen-front
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: เปลี่ยนสถานะได้ใน 1 แตะ และนับจากกดปุ่มบนจอครัว จนถึงจอหน้าร้านแสดงสถานะใหม่ ภายใน 5 วินาทีบน LAN ในร้าน ในอย่างน้อย 18 จาก 20 ครั้งของชุดทดสอบ
- clause ที่ตรวจ: N11: 5 วินาทีบน LAN อย่างน้อย 18 จาก 20 ครั้ง; F11: 1 แตะ
- FR / Flow / Screen: FR-11; NFR-07 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-05 → SCR-04 / SCR-06 / SCR-08 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: ต้องมีการส่งสถานะข้ามจอบน LAN จริง; ไม่วัดจอลูกค้าแทนหน้าร้าน
- Precondition/reset: จอครัวและหน้าร้านแยกอุปกรณ์บน LAN ระบบทดสอบจริง; ไม่มีใน Input
- Test data: 10 ออเดอร์จำลอง เปลี่ยนเป็นกำลังทำและเสร็จแล้วใบละ 2 ครั้ง รวม 20 ครั้ง เป็นการจัด fixture (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: Mock อ้าง K(o) > btn-status-next และ F(o); selector ระบบจริง MISSING; ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. บันทึก ID และสถานะต้นทาง
  2. เปลี่ยนทีละสถานะด้วย 1 แตะ
  3. จับ t0 ที่ครัวกดถึง t1 ที่หน้าร้านแสดงสถานะอาหารใหม่
  4. ทำครบ 20 ครั้งและเก็บแต่ละครั้ง
- Expected result: ทุกการเปลี่ยนใช้ 1 แตะ; หน้าร้านแสดงสถานะอาหารตรงกัน; เวลา ≤5 วินาทีอย่างน้อย 18 จาก 20 ครั้ง
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: เปลี่ยนได้ใน 1 แตะ; ครัวกด→หน้าร้านแสดงใหม่ภายใน 5 วินาทีบน LAN ในร้าน อย่างน้อย 18 จาก 20 ครั้ง; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: BLOCKED ระบบ/หลักฐาน; mapping transition ของ fixture รอ Q-11 แต่คงชื่อกำลังทำ/เสร็จแล้ว
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-11-5"></a>

## TS-US-11-5 — จับการส่งสถานะอาหารไปผิดออเดอร์หลังครัวแตะครั้งเดียว

- US: US-11
- เจ้าของ: kitchen-front
- ประเภท: ผิดพลาด
- AC ต้นฉบับเต็ม: เปลี่ยนสถานะได้ใน 1 แตะ และนับจากกดปุ่มบนจอครัว จนถึงจอหน้าร้านแสดงสถานะใหม่ ภายใน 5 วินาทีบน LAN ในร้าน ในอย่างน้อย 18 จาก 20 ครั้งของชุดทดสอบ
- clause ที่ตรวจ: หนึ่งแตะเปลี่ยนสถานะและหน้าร้านเห็นสถานะอาหารใหม่ของออเดอร์นั้น ภายใน 5 วินาทีบน LAN
- FR / Flow / Screen: FR-11; NFR-07 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-05 → SCR-04 / SCR-06 / SCR-08 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: แก้ D04 เชิงออกแบบ; ต้องมีระบบ/จุดแทรก fault และจุดสังเกตตาม Precondition ซึ่งยังไม่มี จึง BLOCKED การรัน. เป็นแผนตรวจจับผลผิดด้วย oracle อิสระ ไม่ใช่การเปลี่ยนชื่อ happy path; ยังไม่ได้ทำ fault หรือรันทดสอบ
- Precondition/reset: BLOCKED การรัน: ต้องมีครัว/หน้าร้านบนอุปกรณ์แยก LAN และตัวแทรกปลายทางสถานะสำหรับหน้าร้าน; Input ไม่มีเครื่องมือดังกล่าว. คืน snapshot สองใบก่อนแต่ละกรณีและเก็บภาพสองหน้าพร้อมเวลาอ้างอิงเดียวกัน
- Test data: ออเดอร์จำลอง A โต๊ะ 01 และ B โต๊ะ 02 อย่างละเมนู 50 บาท; ทั้งคู่รับออเดอร์. จด ID ที่ระบบออกให้ทั้งสองใบ; fixture เปลี่ยน A จากรับออเดอร์เป็นกำลังทำด้วยหนึ่งแตะ B ไม่มีคำสั่งเปลี่ยน

- data-testid และ scope: Mock มี K(o)>btn-status-next และ F(o) ตาม Precondition/SCOPE เดิม; selector/ตัวแทรกของระบบจริง MISSING. อ่านสถานะอาหารในออเดอร์หน้าร้านตาม ID ไม่ใช้ front-payment-status
- ขั้นตอน:

  1. control: กดที่ A หนึ่งแตะ จด t0, สถานะครัว A และ t1 ที่หน้าร้าน A แสดงกำลังทำ; อ่าน B ควบคู่เพื่อยืนยันไม่ได้จับผิดใบ
  2. fault: reset ทั้งสองใบ ให้ตัวแทรกเปลี่ยน ID ปลายทางจาก A เป็น B เฉพาะข้อมูลเผยแพร่สถานะอาหารไปหน้าร้านหลังครัวกด A หนึ่งแตะ โดยไม่เปลี่ยน ID ต้นทาง/คำสั่ง/ข้อมูลในครัว; บันทึกเหตุการณ์ก่อนและหลังแทรก
  3. เฝ้าหน้าร้าน A/B แยกกันต่อเนื่องผ่าน t0+5 วินาที; จดสถานะทั้งสองและ t1 ของ A เมื่อเห็นค่าตรงจริง; การที่ B แสดงกำลังทำไม่นับเป็น t1 ของ A
  4. เทียบสมุดคำสั่งกับแต่ละ ID แล้วปิดตัวแทรก ทำ control ซ้ำ; ถ้าตรวจผลการสลับ ID ไม่ได้ให้ BLOCKED การกระตุ้น fault

- Expected result: oracle: A ต้องเป็นกำลังทำหลังหนึ่งแตะและวัดถึงหน้าร้าน A ภายใน 5 วินาที; B คงรับออเดอร์ตาม fixture ที่ไม่มีคำสั่ง. ถ้า A ยังเก่าเกิน 5 วินาทีแต่ B เปลี่ยน ต้องระบุผิด ID และครั้งของ A ไม่เข้าเกณฑ์เวลา; ห้ามนับความเร็วการแสดงที่ B เป็นความสำเร็จของ A
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: fault สองใบเป็นการตรวจผิด scope เพิ่ม ไม่แทนชุด 20 ครั้ง ภายใน 5 วินาทีอย่างน้อย 18 จาก 20 ใน TS-US-11-4; ยังคงตรวจหนึ่งแตะต่อการเปลี่ยนและบันทึกทุกครั้งในชุด AC
- สมมติฐาน/ข้อค้าง: คง TS-US-11-3/Q-11/DI-07 เรื่องกดซ้ำ ย้อน และลำดับสถานะจริง; kitchen-front ร่วมเจ้าของข้อกำหนดตัดสิน. ไม่เพิ่มกฎสถานะเงิน/พร้อมเสิร์ฟ
- Status: MOCK_NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-12-1"></a>

## TS-US-12-1 — หมดหนึ่งครั้งปิดเมนูที่ใช้วัตถุดิบทั้งจาน

- US: US-12
- เจ้าของ: kitchen-front
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: ผู้จัดการแมปวัตถุดิบ→เมนู/ตัวเลือกไว้ล่วงหน้า (ดูหมายเหตุ ค.) เมื่อกดหมด 1 ครั้ง เมนูที่ใช้วัตถุดิบนั้นทั้งจานปิดทั้งเมนู ส่วนตัวเลือกเพิ่มที่ใช้เฉพาะตัวเลือกถูกปิดเฉพาะตัวเลือกโดยเมนูหลักยังสั่งได้ ทดสอบด้วยวัตถุดิบ 5 ชนิด ผลตรงกติกาอย่างน้อย 5 จาก 5
- clause ที่ตรวจ: F12-a: แมปล่วงหน้า; F12-b: กดหมด 1 ครั้งปิดทั้งเมนู
- FR / Flow / Screen: FR-12; ไม่มี NFR เฉพาะ US นี้ใน v2 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-08 / MRG-18 / MRG-19 → SCR-01 / SCR-07 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: ตรวจแมปและปุ่มจำลองได้; 1 ชนิดไม่แทนชุด 5 ชนิด
- Precondition/reset: R0; M0 เปิด nav-mapping ยืนยันแมป seed; C0 เปิดเมนูไม่ส่ง; K0
- Test data: chicken→whole m01,m04,m06; เมนูอื่นเป็นชุดควบคุม (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: M0: nav-mapping, mapping-list; K0: ingredient-select, btn-out-of-stock, ingredient-status; C0: menu-list > menu-item-<id> ตาม seed; ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. อ่าน mapping-list ยืนยันแมป chicken ก่อน
  2. K0 เลือก ingredient-select=chicken และกด btn-out-of-stock 1 ครั้ง
  3. C0 กลับหน้าเมนูแล้วอ่านป้าย/disabled ทุกเมนู
- Expected result: m01,m04,m06 หมดและปิดปุ่มทั้งเมนู; เมนูที่ไม่มี chicken ไม่ถูกปิดจากการกดนี้; เทียบชุดที่ปิดกับแมปล่วงหน้า
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: แมปล่วงหน้าและกดหมด 1 ครั้ง; วัตถุดิบ 5 ชนิด ผลตรงกติกาอย่างน้อย 5 จาก 5; หมายเหตุ ค. ไม่มีข้อมูล; ไม่เพิ่ม SLA เวลาให้ US-12; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: หมายเหตุ ค. ไม่มีข้อมูล (DI-02/A-02); US-20 ที่อ้าง US-14 ยัง Q-20
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-12-2"></a>

## TS-US-12-2 — หมดเฉพาะตัวเลือกโดยเมนูหลักยังสั่งได้

- US: US-12
- เจ้าของ: kitchen-front
- ประเภท: ทางเลือก
- AC ต้นฉบับเต็ม: ผู้จัดการแมปวัตถุดิบ→เมนู/ตัวเลือกไว้ล่วงหน้า (ดูหมายเหตุ ค.) เมื่อกดหมด 1 ครั้ง เมนูที่ใช้วัตถุดิบนั้นทั้งจานปิดทั้งเมนู ส่วนตัวเลือกเพิ่มที่ใช้เฉพาะตัวเลือกถูกปิดเฉพาะตัวเลือกโดยเมนูหลักยังสั่งได้ ทดสอบด้วยวัตถุดิบ 5 ชนิด ผลตรงกติกาอย่างน้อย 5 จาก 5
- clause ที่ตรวจ: F12-c: ปิดเฉพาะตัวเลือกเพิ่ม; เมนูหลักยังสั่งได้
- FR / Flow / Screen: FR-12; ไม่มี NFR เฉพาะ US นี้ใน v2 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-08 / MRG-18 / MRG-19 → SCR-01 / SCR-07 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: เพิ่ม assertion ปิดตัวเลือกที่ fixture TS-US-12-101 ยังไม่ได้ assert โดยตรง; ตรวจเฉพาะ mock
- Precondition/reset: R0; M0 ยืนยันแมป egg ก่อน; C0 เปิดโต๊ะ 01; stock อื่นมี
- Test data: egg→option extra-egg ของ m01 และ whole m03,m07 (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: M0: mapping-list; K0: ingredient-select, btn-out-of-stock; C0: menu-item-m01/m03/m07, option-extra-egg, btn-add-item, btn-submit-order; K(o); ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. K0 เลือก egg แล้วกดหมด 1 ครั้ง
  2. C0 ตรวจ m03,m07 disabled
  3. เลือก m01 ตรวจ option-extra-egg disabled
  4. เพิ่ม m01 ไม่ใส่ไข่และส่ง
  5. K0 ตรวจใบที่สร้าง
- Expected result: m01 ยังเลือกและส่งได้; extra-egg ถูกปิด; ใบครัวมี m01 ไม่มีไข่; m03,m07 ถูกปิดทั้งเมนูตามแมป
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: แมปล่วงหน้าและกดหมด 1 ครั้ง; วัตถุดิบ 5 ชนิด ผลตรงกติกาอย่างน้อย 5 จาก 5; หมายเหตุ ค. ไม่มีข้อมูล; ไม่เพิ่ม SLA เวลาให้ US-12; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: แมป/ราคาเป็น fixture; หมายเหตุ ค. ยังขาด
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-12-3"></a>

## TS-US-12-3 — ผลปิดตรงแมปครบวัตถุดิบ 5 ชนิด

- US: US-12
- เจ้าของ: kitchen-front
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: ผู้จัดการแมปวัตถุดิบ→เมนู/ตัวเลือกไว้ล่วงหน้า (ดูหมายเหตุ ค.) เมื่อกดหมด 1 ครั้ง เมนูที่ใช้วัตถุดิบนั้นทั้งจานปิดทั้งเมนู ส่วนตัวเลือกเพิ่มที่ใช้เฉพาะตัวเลือกถูกปิดเฉพาะตัวเลือกโดยเมนูหลักยังสั่งได้ ทดสอบด้วยวัตถุดิบ 5 ชนิด ผลตรงกติกาอย่างน้อย 5 จาก 5
- clause ที่ตรวจ: F12-a/b/c และเกณฑ์อย่างน้อย 5 จาก 5 ชนิด
- FR / Flow / Screen: FR-12; ไม่มี NFR เฉพาะ US นี้ใน v2 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-08 / MRG-18 / MRG-19 → SCR-01 / SCR-07 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: จำนวนครบเกณฑ์ในแบบจำลองได้ แต่ยังไม่ยืนยันการแมป/การปิดในระบบร้านจริง
- Precondition/reset: R0 ใหม่แยกแต่ละชนิด; M0 อ่านแมปล่วงหน้า; stock ทุกชนิดมีตอนเริ่มแต่ละกรณี
- Test data: 5 ชนิด: chicken→whole m01,m04,m06; pork→whole m02,m05; egg→whole m03,m07 และ option extra-egg ของ m01; noodle→whole m04,m07; milk→whole m08 (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: M0: nav-mapping, mapping-list; K0: ingredient-select, btn-out-of-stock; C0: menu-item-<id> ใน menu-list, option-extra-egg, btn-add-item, btn-submit-order; K(o); ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. ทำครบทั้ง 5 แถวโดย reset แยก
  2. ตรวจแมปก่อนกด
  3. K0 กดหมด 1 ครั้งต่อชนิด
  4. C0 เทียบเซตเมนูและตัวเลือกที่ disabled กับแมปทั้งชุด
  5. กรณี egg ส่ง m01 ไม่ใส่ไข่เพื่อยืนยันว่ายังสั่งได้
- Expected result: แต่ละชนิดปิดชุดตรงแมป ไม่มีขาดหรือเกิน; กรณีเฉพาะตัวเลือกเมนูหลักส่งได้; บันทึกผลแยก 5 ชนิด เป้าหมายอย่างน้อย 5 จาก 5
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: แมปล่วงหน้าและกดหมด 1 ครั้ง; วัตถุดิบ 5 ชนิด ผลตรงกติกาอย่างน้อย 5 จาก 5; หมายเหตุ ค. ไม่มีข้อมูล; ไม่เพิ่ม SLA เวลาให้ US-12; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: ข้อมูล 5 ชนิดนี้มาจาก seed เท่านั้น ไม่ใช่ชุดวัตถุดิบร้านที่ยืนยัน; DI-02/Q-12
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-12-4"></a>

## TS-US-12-4 — ตะกร้าที่เตรียมไว้ก่อนวัตถุดิบหมดส่งไม่ได้

- US: US-12
- เจ้าของ: kitchen-front
- ประเภท: ผิดพลาด
- AC ต้นฉบับเต็ม: ผู้จัดการแมปวัตถุดิบ→เมนู/ตัวเลือกไว้ล่วงหน้า (ดูหมายเหตุ ค.) เมื่อกดหมด 1 ครั้ง เมนูที่ใช้วัตถุดิบนั้นทั้งจานปิดทั้งเมนู ส่วนตัวเลือกเพิ่มที่ใช้เฉพาะตัวเลือกถูกปิดเฉพาะตัวเลือกโดยเมนูหลักยังสั่งได้ ทดสอบด้วยวัตถุดิบ 5 ชนิด ผลตรงกติกาอย่างน้อย 5 จาก 5
- clause ที่ตรวจ: ตรวจผล F12-b ต่อการสั่ง; expected ปฏิเสธอ้าง AC US-06/FR-06 เพิ่มเป็น dependency
- FR / Flow / Screen: FR-12; ไม่มี NFR เฉพาะ US นี้ใน v2 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-08 / MRG-18 / MRG-19 → SCR-01 / SCR-07 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen; dependency FR-06/US-06 สำหรับผลปฏิเสธ
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: ตรวจตะกร้าค้างใน mock ได้; อ้าง fixture ข้ามบทบาท TS-US-06-101 โดยไม่เปลี่ยนเจ้าของ US-12
- Precondition/reset: R0; C0 เพิ่ม m01 ลงตะกร้าแล้ว ยังไม่ส่ง
- Test data: m01=50 บาท 1 จาน; chicken มีตอนเพิ่มและหมดก่อนส่ง (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: C0: btn-submit-order, order-message; K0: ingredient-select, btn-out-of-stock, kitchen-queue; ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. K0 เลือก chicken กดหมด 1 ครั้ง
  2. กลับลูกค้า กด btn-submit-order บนตะกร้าเดิม
  3. อ่าน order-message
  4. K0 ตรวจจำนวนใบครัว
- Expected result: แสดงข้อความปฏิเสธมีคำว่า หมด และไม่เพิ่มใบครัว; คำละเอียดไม่ตรึงเกิน AC US-06
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: แมปล่วงหน้าและกดหมด 1 ครั้ง; วัตถุดิบ 5 ชนิด ผลตรงกติกาอย่างน้อย 5 จาก 5; หมายเหตุ ค. ไม่มีข้อมูล; ไม่เพิ่ม SLA เวลาให้ US-12; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: การชนเวลา submit/หมดจริงยัง Q-06; ไม่เพิ่ม SLA US-06 ให้เป็น AC US-12
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-12-5"></a>

## TS-US-12-5 — กดหมดซ้ำหรือวัตถุดิบหลายชนิดหมดซ้อน

- US: US-12
- เจ้าของ: kitchen-front
- ประเภท: ข้อยกเว้น
- AC ต้นฉบับเต็ม: ผู้จัดการแมปวัตถุดิบ→เมนู/ตัวเลือกไว้ล่วงหน้า (ดูหมายเหตุ ค.) เมื่อกดหมด 1 ครั้ง เมนูที่ใช้วัตถุดิบนั้นทั้งจานปิดทั้งเมนู ส่วนตัวเลือกเพิ่มที่ใช้เฉพาะตัวเลือกถูกปิดเฉพาะตัวเลือกโดยเมนูหลักยังสั่งได้ ทดสอบด้วยวัตถุดิบ 5 ชนิด ผลตรงกติกาอย่างน้อย 5 จาก 5
- clause ที่ตรวจ: ข้อค้างขอบเขตกฎแมป F12-b/c
- FR / Flow / Screen: FR-12; ไม่มี NFR เฉพาะ US นี้ใน v2 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-08 / MRG-18 / MRG-19 → SCR-01 / SCR-07 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: ต้องตรวจเหตุปิดซ้อนในระบบจริงหลังได้กติกา; โค้ด mock ไม่เป็นนโยบายร้าน
- Precondition/reset: ระบบทดสอบจริงและคำตอบ Q-12; เตรียม m01 ผูก chicken และ rice
- Test data: chicken,rice สองชนิดจำลอง; m01 และ extra-egg (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: Mock มี ingredient-select, btn-out-of-stock, menu-item-m01, option-extra-egg; selector/log ระบบจริง MISSING; ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. กด chicken หมด แล้ว rice หมด
  2. กด chicken หมดซ้ำ
  3. เก็บแมปและสถานะเมนู/ตัวเลือก/เหตุการณ์ทุกครั้ง
- Expected result: BLOCKED/ไม่มีข้อมูลด้านผลกดซ้ำและการรวมเหตุปิด; กฎ whole/option ที่ชัดยังต้องคง แต่ oracle ของกรณีซ้อนรอหมายเหตุ ค. และ Q-12
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: แมปล่วงหน้าและกดหมด 1 ครั้ง; วัตถุดิบ 5 ชนิด ผลตรงกติกาอย่างน้อย 5 จาก 5; หมายเหตุ ค. ไม่มีข้อมูล; ไม่เพิ่ม SLA เวลาให้ US-12; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: DI-02, Q-12; ไม่กำหนดกฎนับเหตุปิดหรือผลกดซ้ำเอง
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-13-1"></a>

## TS-US-13-1 — กลับมามีเปิดเมนูทั้งชุดที่ปิดคืน

- US: US-13
- เจ้าของ: kitchen-front
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: นับจากกด “กลับมามี” จนถึงหน้าลูกค้าเปิดปุ่มสั่งคืน ภายใน 10 วินาทีบน LAN ในร้าน ในอย่างน้อย 9 จาก 10 ครั้ง และเมนู/ตัวเลือกที่กลับมาตรงกับชุดที่ถูกปิดจากวัตถุดิบนั้น
- clause ที่ตรวจ: F13-a: เปิดปุ่มสั่งคืน; F13-b: ชุดเปิดตรงชุดที่ปิด
- FR / Flow / Screen: FR-13; NFR-08 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-09 / MRG-20 → SCR-01 / SCR-07 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: ตรวจเปิดคืนและเทียบเซตจำลอง; ไม่วัด 10 วินาที LAN
- Precondition/reset: R0; C0; K0 ปิด chicken ก่อนและบันทึกชุดที่ปิดจริง; ไม่มีวัตถุดิบอื่นหมด
- Test data: chicken→m01,m04,m06; เมนูอื่นใช้เป็นชุดควบคุม (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: C0: menu-list > menu-item-<id>, btn-add-item, btn-submit-order; K0: ingredient-select, btn-out-of-stock, btn-restock, ingredient-status; K(o); ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. C0 ตรวจและเก็บว่าปุ่ม m01,m04,m06 ปิดก่อน
  2. K0 เลือก chicken กด btn-restock
  3. C0 ตรวจ enabled ของเมนูทุกตัว
  4. ส่ง m01 หนึ่งจาน
- Expected result: m01,m04,m06 เปิดปุ่มคืนตรงชุดที่ปิดไม่มีขาดหรือเกิน; ส่ง m01 ได้; สถานะเมนูอื่นไม่เปลี่ยนเพราะ restock นี้
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: กดกลับมามี→ลูกค้าเปิดปุ่มสั่งคืนภายใน 10 วินาทีบน LAN ในร้าน อย่างน้อย 9 จาก 10 ครั้ง; ชุดที่กลับมาตรงชุดที่ถูกปิด แยกเกณฑ์ความตรงชุดจากเกณฑ์เวลา; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: Q-13 สำหรับ stock ซ้อนและแมปเปลี่ยน; เกณฑ์เวลา/10 ครั้งใช้ TS-US-13-3
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-13-2"></a>

## TS-US-13-2 — กลับมามีเปิดตัวเลือกและเมนูที่ใช้ไข่คืน

- US: US-13
- เจ้าของ: kitchen-front
- ประเภท: ทางเลือก
- AC ต้นฉบับเต็ม: นับจากกด “กลับมามี” จนถึงหน้าลูกค้าเปิดปุ่มสั่งคืน ภายใน 10 วินาทีบน LAN ในร้าน ในอย่างน้อย 9 จาก 10 ครั้ง และเมนู/ตัวเลือกที่กลับมาตรงกับชุดที่ถูกปิดจากวัตถุดิบนั้น
- clause ที่ตรวจ: F13-b: ชุดเมนู/ตัวเลือกเปิดคืนตรงชุดที่ถูกปิด
- FR / Flow / Screen: FR-13; NFR-08 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-09 / MRG-20 → SCR-01 / SCR-07 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: ตรวจทางเลือกของการเปิดคืนใน mock; ไม่มีผล LAN
- Precondition/reset: R0; ปิด egg แล้ว C0 ยืนยัน m03,m07 และ extra-egg ปิดจริงก่อน
- Test data: egg→whole m03,m07 และ option extra-egg ของ m01; m01=50+ไข่10=60 บาท (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: K0: ingredient-select, btn-out-of-stock, btn-restock; C0: menu-item-m01/m03/m07, option-extra-egg, btn-add-item, btn-submit-order; K(o); ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. K0 กด btn-restock สำหรับ egg
  2. C0 ตรวจ m03,m07 เปิด
  3. เลือก m01 ติ๊ก option-extra-egg เพิ่มแล้วส่ง
  4. K0 ตรวจตัวเลือกในใบ o
- Expected result: ชุดเปิดคืนประกอบด้วย m03,m07 และ extra-egg ตรงชุดปิด; m01 ยังสั่งได้และใบครัวมีเพิ่มไข่ดาว
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: กดกลับมามี→ลูกค้าเปิดปุ่มสั่งคืนภายใน 10 วินาทีบน LAN ในร้าน อย่างน้อย 9 จาก 10 ครั้ง; ชุดที่กลับมาตรงชุดที่ถูกปิด แยกเกณฑ์ความตรงชุดจากเกณฑ์เวลา; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: ข้อมูลราคา/แมปเป็น fixture; หมายเหตุ ค. และ Q-13 ยังเปิด
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-13-3"></a>

## TS-US-13-3 — เปิดคืนภายในเวลาบน LAN และชุดไม่ขาดเกิน

- US: US-13
- เจ้าของ: kitchen-front
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: นับจากกด “กลับมามี” จนถึงหน้าลูกค้าเปิดปุ่มสั่งคืน ภายใน 10 วินาทีบน LAN ในร้าน ในอย่างน้อย 9 จาก 10 ครั้ง และเมนู/ตัวเลือกที่กลับมาตรงกับชุดที่ถูกปิดจากวัตถุดิบนั้น
- clause ที่ตรวจ: N13: 10 วินาทีอย่างน้อย 9 จาก 10 ครั้ง; F13-b แยกตรวจความตรงชุด
- FR / Flow / Screen: FR-13; NFR-08 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-09 / MRG-20 → SCR-01 / SCR-07 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: ต้องมี LAN และสถานะข้อมูลจริง; ยังไม่มีหลักฐานการส่งข้ามจอ
- Precondition/reset: ระบบจริงบน LAN จอครัวและลูกค้าแยก; บันทึกแมปและชุดที่ปิดก่อนทุกครั้ง
- Test data: 10 ครั้งจำลอง: สลับ chicken และ egg อย่างละ 5 เป็นการจัด fixture ไม่ใช่สัดส่วนร้าน (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: Mock มี ingredient-select, btn-restock และ menu-item-<id>/option-extra-egg; selector ระบบจริง MISSING; ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. เตรียมให้ชนิดเป้าหมายหมดและชนิดอื่นมีทุกครั้ง
  2. เก็บชุดปิด
  3. ครัวกดกลับมามีเริ่ม t0
  4. จบ t1 เมื่อปุ่มสั่งคืนบนลูกค้า
  5. เทียบชุดเปิดกับชุดปิด
  6. ทำครบ 10 ครั้ง
- Expected result: เวลา ≤10 วินาทีอย่างน้อย 9 จาก 10 ครั้ง; ชุดเมนูและตัวเลือกที่เปิดตรงกับชุดที่ปิดจากวัตถุดิบนั้น; ไม่ใช้ผลเวลาปกปิดชุดผิด
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: กดกลับมามี→ลูกค้าเปิดปุ่มสั่งคืนภายใน 10 วินาทีบน LAN ในร้าน อย่างน้อย 9 จาก 10 ครั้ง; ชุดที่กลับมาตรงชุดที่ถูกปิด แยกเกณฑ์ความตรงชุดจากเกณฑ์เวลา; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: BLOCKED ระบบและหลักฐาน; กรณีแมปไม่ซ้อนเพื่อไม่เติมคำตอบ Q-13
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-13-4"></a>

## TS-US-13-4 — เติมชนิดเดียวขณะอีกชนิดยังหมดหรือมีการแก้แมป

- US: US-13
- เจ้าของ: kitchen-front
- ประเภท: ข้อยกเว้น
- AC ต้นฉบับเต็ม: นับจากกด “กลับมามี” จนถึงหน้าลูกค้าเปิดปุ่มสั่งคืน ภายใน 10 วินาทีบน LAN ในร้าน ในอย่างน้อย 9 จาก 10 ครั้ง และเมนู/ตัวเลือกที่กลับมาตรงกับชุดที่ถูกปิดจากวัตถุดิบนั้น
- clause ที่ตรวจ: ข้อค้าง F13-b: ชุดที่ต้องเปิดคืนเมื่อเหตุปิดเปลี่ยน
- FR / Flow / Screen: FR-13; NFR-08 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-09 / MRG-20 → SCR-01 / SCR-07 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: ต้องมีข้อมูลเหตุปิด/การเปลี่ยนแมปในระบบจริงพร้อมนโยบายยืนยัน
- Precondition/reset: ระบบจริงและคำตอบ Q-13; เตรียม m01 ปิดจาก chicken และ rice
- Test data: กรณี A: chicken,rice หมดแล้วคืน chicken; กรณี B: ปิด chicken แล้วผู้จัดการแก้แมปก่อนคืน (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: Mock มี ingredient-select, btn-restock, mapping-list, menu-item-m01; selector/log ระบบจริง MISSING; ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. บันทึกแมปขณะปิด
  2. ทำกรณี A และ B แยกชุด
  3. กดกลับมามี
  4. เก็บชุดเปิด/ปิดและแมปล่าสุดเทียบกับก่อนปิด
- Expected result: BLOCKED/ไม่มีข้อมูลว่าต้องยึดแมปขณะใดและเปิดชุดใด; fixture เสนอคงปิดเมื่ออีกชนิดยังหมด แต่ยังไม่เป็นเกณฑ์ระบบจริง
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: กดกลับมามี→ลูกค้าเปิดปุ่มสั่งคืนภายใน 10 วินาทีบน LAN ในร้าน อย่างน้อย 9 จาก 10 ครั้ง; ชุดที่กลับมาตรงชุดที่ถูกปิด แยกเกณฑ์ความตรงชุดจากเกณฑ์เวลา; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: Q-13, Q-12, DI-02; ไม่สรุปว่าเปิดทั้งหมดหรือคงปิดตาม fixture เป็น AC
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-14-1"></a>

## TS-US-14-1 — ทำไม่ได้เปลี่ยนเฉพาะรายการเป็นรอลูกค้าตัดสินใจ

- US: US-14
- เจ้าของ: kitchen-front
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: รายการที่กด “ทำไม่ได้” ย้ายไปสถานะ “รอลูกค้าตัดสินใจ” และเมื่อลูกค้าเปลี่ยนเมนูหรือคืนรายการ จอครัวอัปเดตรายการใหม่หรือลบรายการภายใน 10 วินาทีบน LAN ทดสอบผ่าน 5 จาก 5 กรณี
- clause ที่ตรวจ: F14-a: รายการที่กดทำไม่ได้ย้ายเป็นรอลูกค้าตัดสินใจ
- FR / Flow / Screen: FR-14; NFR-V2-14 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-31 / MRG-32 / MRG-33 → SCR-03 / SCR-04 / SCR-06 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: ตรวจ item state จำลองและ scope หลายรายการ; อ้าง TS-US-14-101 ซึ่งใช้ใบเดียว/จานเดียว
- Precondition/reset: R0; C0 ส่งหนึ่งออเดอร์มี 2 รายการ แล้ว K0
- Test data: m01 และ m02 อย่างละ 1; จด o และ item IDs i,j จาก li; ไม่มี catalog หมดเป็นเงื่อนไขบังคับ (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: K0: K(o) li[data-item-id=i] [data-testid=item-state] และ K(o) descendant btn-item-unavailable[data-item-id=i] โดยใช้ descendant ตาม SCOPE; C0: R(o,i) > item-state; ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. ยืนยัน K(o) มี i และ j ก่อน
  2. กด btn-item-unavailable ของ i
  3. อ่าน item-state ของ i
  4. ตรวจ j ยังเป็นรายการเดิม
  5. กลับลูกค้าอ่าน R(o,i) และยังไม่เลือกทางออก
  6. กลับครัวตรวจ i
- Expected result: i แสดง รอลูกค้าตัดสินใจ ในใบครัวและลูกค้า; j ไม่ถูกทำไม่ได้ตามไป; i ยังรอเมื่อเพียงดูหน้าจอ
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: รายการเป็นรอลูกค้าตัดสินใจ; ลูกค้าเปลี่ยน/คืน→ครัวอัปเดต/ลบภายใน 10 วินาทีบน LAN ผ่าน 5 จาก 5 กรณี; ชุดครอบคลุมสองทางโดยไม่เพิ่มสัดส่วน AC; ไม่ใช้จุดเริ่มแจ้งของ US-09; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: แยก item state จาก order/payment; ผลรวมสถานะทั้งออเดอร์ยัง Q-V2-STATE
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-14-2"></a>

## TS-US-14-2 — ลูกค้าเปลี่ยนเมนูแล้วครัวแสดงรายการแทน

- US: US-14
- เจ้าของ: kitchen-front
- ประเภท: ทางเลือก
- AC ต้นฉบับเต็ม: รายการที่กด “ทำไม่ได้” ย้ายไปสถานะ “รอลูกค้าตัดสินใจ” และเมื่อลูกค้าเปลี่ยนเมนูหรือคืนรายการ จอครัวอัปเดตรายการใหม่หรือลบรายการภายใน 10 วินาทีบน LAN ทดสอบผ่าน 5 จาก 5 กรณี
- clause ที่ตรวจ: F14-b: เปลี่ยนเมนูแล้วจอครัวอัปเดตรายการใหม่
- FR / Flow / Screen: FR-14; NFR-V2-14 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-31 / MRG-32 / MRG-33 → SCR-03 / SCR-04 / SCR-06 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: ตรวจการเปลี่ยนรายการจำลองได้; ระยะเวลา LAN ใช้ TS-US-14-5
- Precondition/reset: R0; C0 ส่ง m01+m02; K0 ทำไม่ได้เฉพาะ item m01; C0 กลับหน้าลูกค้า
- Test data: o มี i=m01, j=m02; เลือกเมนูแทน m03=40 บาท 1 จานตาม seed (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: C0: R(o,i) > replacement-menu, replacement-preview, btn-change-menu, item-state; K0: K(o) li[data-item-id=i] และ li[data-item-id=j]; ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. ใน R(o,i) เลือก replacement-menu=m03
  2. ตรวจ replacement-preview และ item-state ยังรอ
  3. กด btn-change-menu
  4. K0 อ่าน li เป้าหมายและรายการ j
- Expected result: ก่อนยืนยันยังรอลูกค้าตัดสินใจ; หลังยืนยันครัวแสดงข้าวไข่เจียวแทน m01 ในรายการเป้าหมาย; j ยังคง m02; ไม่ใช้การมีข้อความสำเร็จอย่างเดียวแทนตรวจใบครัว
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: รายการเป็นรอลูกค้าตัดสินใจ; ลูกค้าเปลี่ยน/คืน→ครัวอัปเดต/ลบภายใน 10 วินาทีบน LAN ผ่าน 5 จาก 5 กรณี; ชุดครอบคลุมสองทางโดยไม่เพิ่มสัดส่วน AC; ไม่ใช้จุดเริ่มแจ้งของ US-09; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: การคง order/item ID และราคาแทนเป็น fixture; ส่วนต่าง/aggregate ไม่ใช้เป็น oracle AC US-14; Q-V2-REFUND/STATE
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-14-3"></a>

## TS-US-14-3 — ลูกค้าคืนรายการแล้วครัวลบเฉพาะรายการนั้น

- US: US-14
- เจ้าของ: kitchen-front
- ประเภท: ทางเลือก
- AC ต้นฉบับเต็ม: รายการที่กด “ทำไม่ได้” ย้ายไปสถานะ “รอลูกค้าตัดสินใจ” และเมื่อลูกค้าเปลี่ยนเมนูหรือคืนรายการ จอครัวอัปเดตรายการใหม่หรือลบรายการภายใน 10 วินาทีบน LAN ทดสอบผ่าน 5 จาก 5 กรณี
- clause ที่ตรวจ: F14-c: คืนรายการแล้วจอครัวลบรายการ
- FR / Flow / Screen: FR-14; NFR-V2-14 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-31 / MRG-32 / MRG-33 → SCR-03 / SCR-04 / SCR-06 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: ตรวจรายการคืนที่ไม่ใช่ใบล่าสุดได้; ห้ามใช้ customer-adjusted-total ซึ่งอ่านล่าสุดแทนยอดใบ A
- Precondition/reset: R0; C0 ส่งสองออเดอร์ที่โต๊ะ 01; ทำไม่ได้รายการหนึ่งของใบแรกซึ่งไม่ใช่ใบล่าสุด
- Test data: ใบ A: m01+extra-egg=60 และ m02=55 รวม115; ใบ B: m02=55; รายการละ1; จด oA,iA,jA,oB (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: C0: R(oA,iA) > btn-return-item; customer-resolution-order[data-order-id=oA] > resolution-order-total; K0: K(oA)/K(oB) และ li[data-item-id]; F0: F(oA) > front-adjusted-total, front-total; ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. K0 ยืนยันรายการ iA ปรากฏจริงและกดทำไม่ได้
  2. C0 ใช้ R(oA,iA) กด btn-return-item
  3. K0 ตรวจไม่พบ li iA ใน K(oA) แต่ jA ยังอยู่และใบ B ไม่เปลี่ยน
  4. F0 ดูยอดหลังปรับใบ A
- Expected result: ครัวลบเฉพาะ iA ออกจากรายการที่ต้องทำ; jA และใบ B ยังคงเดิม; assertion สนับสนุน fixture: resolution-order-total ใบ A และ front-adjusted-total ใบ A =55 บาท ส่วน front-total snapshot=115; ไม่ยืนยันคืนเงินจริง
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: รายการเป็นรอลูกค้าตัดสินใจ; ลูกค้าเปลี่ยน/คืน→ครัวอัปเดต/ลบภายใน 10 วินาทีบน LAN ผ่าน 5 จาก 5 กรณี; ชุดครอบคลุมสองทางโดยไม่เพิ่มสัดส่วน AC; ไม่ใช้จุดเริ่มแจ้งของ US-09; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: ต้อง assert ว่า li มีอยู่ก่อนคืนก่อนใช้ absence; ยอดเป็น fixture เชื่อม US-09 ไม่เพิ่ม AC US-14; Q-V2-REFUND/STATE
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-14-4"></a>

## TS-US-14-4 — เมนูแทนที่เลือกไว้หมดก่อนยืนยัน

- US: US-14
- เจ้าของ: kitchen-front
- ประเภท: ผิดพลาด
- AC ต้นฉบับเต็ม: รายการที่กด “ทำไม่ได้” ย้ายไปสถานะ “รอลูกค้าตัดสินใจ” และเมื่อลูกค้าเปลี่ยนเมนูหรือคืนรายการ จอครัวอัปเดตรายการใหม่หรือลบรายการภายใน 10 วินาทีบน LAN ทดสอบผ่าน 5 จาก 5 กรณี
- clause ที่ตรวจ: ข้อผิดพลาดของ F14-b; การปฏิเสธเมนูหมดอ้าง FR-06 และ MRG-32
- FR / Flow / Screen: FR-14; NFR-V2-14 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-31 / MRG-32 / MRG-33 → SCR-03 / SCR-04 / SCR-06 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: fixture จำลองเก็บ draft ข้ามบทบาทและตรวจ stock อีกครั้ง; ไม่พิสูจน์ stock race ของระบบจริง
- Precondition/reset: R0; C0 ส่ง m01 1 จาน; K0 ทำไม่ได้; C0 เลือก replacement-menu=m02 แต่ยังไม่กดเปลี่ยน
- Test data: i=m01 เดิม; เมนูแทน m02 มีตอนเลือก จากนั้น pork หมด (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: C0: R(o,i) > replacement-menu, btn-change-menu, item-state; customer-item-resolutions > resolution-message; K0: ingredient-select, btn-out-of-stock, K(o) li[data-item-id=i]; ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. K0 เลือก ingredient-select=pork กดหมด
  2. C0 กลับ R(o,i) แล้วกด btn-change-menu สำหรับ draft ที่ค้าง
  3. อ่าน resolution-message และ item-state
  4. K0 ตรวจรายการเดิม
- Expected result: resolution-message มีการปฏิเสธ/หมด; รายการยังรอลูกค้าตัดสินใจและยังไม่เปลี่ยนเป็น m02; ไม่มีผลเปลี่ยนสำเร็จ
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: รายการเป็นรอลูกค้าตัดสินใจ; ลูกค้าเปลี่ยน/คืน→ครัวอัปเดต/ลบภายใน 10 วินาทีบน LAN ผ่าน 5 จาก 5 กรณี; ชุดครอบคลุมสองทางโดยไม่เพิ่มสัดส่วน AC; ไม่ใช้จุดเริ่มแจ้งของ US-09; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: การคง pending ตาม Flow/fixture; การรับคำสั่งพร้อมกันจริงยัง Q-V2-STATE; ไม่สร้างกฎแก้รายการอัตโนมัติ
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-14-5"></a>

## TS-US-14-5 — เปลี่ยนหรือคืนส่งผลถึงครัวภายใน 10 วินาทีครบ 5 กรณี

- US: US-14
- เจ้าของ: kitchen-front
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: รายการที่กด “ทำไม่ได้” ย้ายไปสถานะ “รอลูกค้าตัดสินใจ” และเมื่อลูกค้าเปลี่ยนเมนูหรือคืนรายการ จอครัวอัปเดตรายการใหม่หรือลบรายการภายใน 10 วินาทีบน LAN ทดสอบผ่าน 5 จาก 5 กรณี
- clause ที่ตรวจ: F14-a/b/c และ N14: ภายใน 10 วินาทีบน LAN ผ่าน 5 จาก 5 กรณี
- FR / Flow / Screen: FR-14; NFR-V2-14 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-31 / MRG-32 / MRG-33 → SCR-03 / SCR-04 / SCR-06 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: ต้องมี LAN และเหตุการณ์จากสองจอ; ชุด 5 กรณีของ US-14 แยกการรับรองจาก US-09
- Precondition/reset: ระบบทดสอบจริง LAN ลูกค้าและครัวแยก; ยืนยันการเลือกทางออกได้; ไม่มีใน Input
- Test data: 5 กรณีจำลอง: (1) m01→m02 (2) คืน m01 ใบเดียว (3) คืน m01+ไข่ในใบ115เหลือ m02 (4) m02→m01+ไข่ (5) คืนรายการใบที่ไม่ใช่ล่าสุด; การจัด 2 เปลี่ยน/3 คืนเป็น fixture ไม่ใช่สัดส่วน AC (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: Mock อ้าง K(o), R(o,i), btn-item-unavailable, btn-change-menu, btn-return-item; selector/เครื่องมือจับเวลาในระบบจริง MISSING; ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. แต่ละกรณีครัวกดทำไม่ได้และตรวจ pending
  2. ลูกค้าเลือกเปลี่ยนหรือคืนสำเร็จเริ่ม t0
  3. จบ t1 เมื่อครัวอัปเดตเมนู/ตัวเลือกใหม่หรือลบรายการตรง ID
  4. เก็บผลรายกรณีครบ 5
- Expected result: ทั้ง 5 กรณีเปลี่ยนเป็นรอลูกค้าตัดสินใจก่อน; ผลทางออกตรงการเลือกและครัวอัปเดต/ลบภายใน10 วินาทีบน LAN ผ่าน5 จาก5; ไม่ใช้เวลาครัวกด→ลูกค้าแจ้งของ US-09 แทนจุดเริ่มนี้
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: รายการเป็นรอลูกค้าตัดสินใจ; ลูกค้าเปลี่ยน/คืน→ครัวอัปเดต/ลบภายใน 10 วินาทีบน LAN ผ่าน 5 จาก 5 กรณี; ชุดครอบคลุมสองทางโดยไม่เพิ่มสัดส่วน AC; ไม่ใช้จุดเริ่มแจ้งของ US-09; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: BLOCKED ระบบ/หลักฐาน; ราคาแทน/คืนเงินและ aggregate รอ Q-V2-REFUND/STATE แต่คงเกณฑ์อัปเดตครัวเดิม
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-14-6"></a>

## TS-US-14-6 — คืนซ้ำหรือคืนชนกับเปลี่ยนรายการเดียวกัน

- US: US-14
- เจ้าของ: kitchen-front
- ประเภท: ข้อยกเว้น
- AC ต้นฉบับเต็ม: รายการที่กด “ทำไม่ได้” ย้ายไปสถานะ “รอลูกค้าตัดสินใจ” และเมื่อลูกค้าเปลี่ยนเมนูหรือคืนรายการ จอครัวอัปเดตรายการใหม่หรือลบรายการภายใน 10 วินาทีบน LAN ทดสอบผ่าน 5 จาก 5 กรณี
- clause ที่ตรวจ: ข้อค้างของ F14-b/c เมื่อมีคำตัดสินซ้ำ/พร้อมกัน
- FR / Flow / Screen: FR-14; NFR-V2-14 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-31 / MRG-32 / MRG-33 → SCR-03 / SCR-04 / SCR-06 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: การไม่แสดงปุ่มใน mock ไม่ตรวจ idempotency ฝั่ง server
- Precondition/reset: ระบบทดสอบและคำตอบ Q-V2-REFUND/STATE; รายการหนึ่ง pending และมีทางส่งคำสั่งที่บันทึกได้
- Test data: คำสั่งคืนสองครั้ง และคู่คืน/เปลี่ยนสำหรับ order/item เดียวกัน แยก fixture (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: Mock R(o,i) มี btn-return-item เฉพาะ pending; ช่องส่งซ้ำหลังปุ่มหาย/คำสั่ง concurrent จริง MISSING; ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. หลังได้คำตอบ ให้ส่งคำสั่งคืนซ้ำและคู่คำสั่งชนกัน
  2. เก็บลำดับเหตุการณ์ การตัดสินใจ รายการครัว และการปรับยอด
- Expected result: BLOCKED/ไม่มีข้อมูลว่าจะให้คำสั่งใดชนะหรือจัดการซ้ำอย่างไร; ไม่กำหนด expected no-op/หักครั้งเดียวเป็น AC ที่ยืนยัน
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: รายการเป็นรอลูกค้าตัดสินใจ; ลูกค้าเปลี่ยน/คืน→ครัวอัปเดต/ลบภายใน 10 วินาทีบน LAN ผ่าน 5 จาก 5 กรณี; ชุดครอบคลุมสองทางโดยไม่เพิ่มสัดส่วน AC; ไม่ใช้จุดเริ่มแจ้งของ US-09; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: Q-V2-REFUND/STATE; ไม่เพิ่มการยกเลิกออเดอร์ ปิดโต๊ะ หรือคืนเงินจริงเมื่อคืนทุกจาน
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-15-1"></a>

## TS-US-15-1 — หน้าร้านแสดงโต๊ะจาก table_id

- US: US-15
- เจ้าของ: kitchen-front
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: จอหน้าร้านแสดงหมายเลขโต๊ะ (จาก table_id ของ QR) สำหรับออเดอร์หน้าร้าน และหมายเลขรับสั่งกลับบ้านรูปแบบ T-001, T-002, … ที่ระบบสร้างอัตโนมัติ เรียงต่อเนื่อง และรีเซ็ตเป็น T-001 เมื่อเริ่มวันใหม่ (00:00) ครบทุกออเดอร์ 20 จาก 20 ใบของชุดทดสอบ · เกณฑ์ระบบ: สถานะ “จ่ายแล้ว/ยังไม่จ่าย/ค้างจ่าย” บนจอเปลี่ยนตามเหตุการณ์ในระบบ (ออเดอร์ใหม่ = ยังไม่จ่าย · เลือก PromptPay = ค้างจ่าย · กด “รับเงินสด” หรือ “ยืนยันสลิป” = จ่ายแล้ว) ถูกต้อง 20 จาก 20 ใบเมื่อเทียบกับ log เหตุการณ์ · เกณฑ์การยืนยันด้วยมือ: การกดของพนักงานหน้าร้านต้องระบุชื่อผู้ใช้และเวลาไว้ใน log ทุกครั้ง 20 จาก 20 ใบ
- clause ที่ตรวจ: F15-a: หมายเลขโต๊ะจาก table_id ของ QR
- FR / Flow / Screen: FR-15; NFR-19 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-04 / MRG-06 / MRG-07 / MRG-10 / MRG-11 / MRG-13 / MRG-14 / MRG-32 / MRG-33 → SCR-03 / SCR-05 / SCR-06 / SCR-08 / SCR-09 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: ตรวจการผูกโต๊ะจำลอง; QR จริงและชุด20 ใบใช้ TS-US-15-6
- Precondition/reset: R0; ใช้โต๊ะจำลอง 01,02,03; สร้างคนละออเดอร์
- Test data: โต๊ะละ m01 1 จาน; จด mapping โต๊ะ→order ID (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: C0: table-select, btn-open-menu, order-id; F0: front-orders > F(o) และ data-table-id; ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. C0 เลือกแต่ละโต๊ะ เปิดเมนูและส่ง
  2. F0 ตรวจข้อความหมายเลขโต๊ะและ data-table-id ใน F(o) ทุกใบ
- Expected result: ทั้งสามใบแสดงโต๊ะตรงกับที่เลือกและ data-table-id ตรงกัน; ไม่ใช้เลขออเดอร์แทนเลขโต๊ะ
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: โต๊ะจาก table_id / เลขรับ T-001, T-002, … ต่อเนื่องและรีเซ็ต T-001 เมื่อวันใหม่ 00:00 ครบ 20 จาก 20 ใบ; สถานะเทียบ log ถูก 20 จาก 20 ใบ; ทุกการกดยืนยันด้วยมือมีชื่อผู้ใช้และเวลาใน log 20 จาก 20 ใบ; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: seed3 โต๊ะไม่แทน20 ใบ; ไม่มีการสแกน QR จริง
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-15-2"></a>

## TS-US-15-2 — กลับบ้านออกหมายเลขรับต่อเนื่อง

- US: US-15
- เจ้าของ: kitchen-front
- ประเภท: ทางเลือก
- AC ต้นฉบับเต็ม: จอหน้าร้านแสดงหมายเลขโต๊ะ (จาก table_id ของ QR) สำหรับออเดอร์หน้าร้าน และหมายเลขรับสั่งกลับบ้านรูปแบบ T-001, T-002, … ที่ระบบสร้างอัตโนมัติ เรียงต่อเนื่อง และรีเซ็ตเป็น T-001 เมื่อเริ่มวันใหม่ (00:00) ครบทุกออเดอร์ 20 จาก 20 ใบของชุดทดสอบ · เกณฑ์ระบบ: สถานะ “จ่ายแล้ว/ยังไม่จ่าย/ค้างจ่าย” บนจอเปลี่ยนตามเหตุการณ์ในระบบ (ออเดอร์ใหม่ = ยังไม่จ่าย · เลือก PromptPay = ค้างจ่าย · กด “รับเงินสด” หรือ “ยืนยันสลิป” = จ่ายแล้ว) ถูกต้อง 20 จาก 20 ใบเมื่อเทียบกับ log เหตุการณ์ · เกณฑ์การยืนยันด้วยมือ: การกดของพนักงานหน้าร้านต้องระบุชื่อผู้ใช้และเวลาไว้ใน log ทุกครั้ง 20 จาก 20 ใบ
- clause ที่ตรวจ: F15-b: T-001,T-002,… อัตโนมัติต่อเนื่อง
- FR / Flow / Screen: FR-15; NFR-19 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-04 / MRG-06 / MRG-07 / MRG-10 / MRG-11 / MRG-13 / MRG-14 / MRG-32 / MRG-33 → SCR-03 / SCR-05 / SCR-06 / SCR-08 / SCR-09 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: ตรวจเลขรับจำลองในวันเดียว; ขอบ00:00แยก TS-US-15-5
- Precondition/reset: R0; C0 เลือก order-mode=takeaway; sim-clock12:00; ไม่ reset ระหว่างส่ง
- Test data: m01 จำนวน1 ต่อออเดอร์กลับบ้าน2 ใบ; pickup-slot=12:30-12:45 เป็น fixture (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: C0: order-mode, pickup-slot, btn-open-menu, order-id, takeaway-id; F0: F(o), data-table-id=takeaway; ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. เลือก takeaway/slot แล้วส่งใบแรก จด order-id/takeaway-id
  2. สลับบทบาทดูหน้าร้านแล้วกลับลูกค้า
  3. ส่งใบที่สอง
  4. F0 เทียบเลขรับทั้งสองใบ
- Expected result: เลขรับเป็น T-001 แล้ว T-002 โดยผู้ใช้ไม่กรอกเอง; ใบหน้าร้านมีป้ายสั่งกลับบ้านและเลขรับตรงใบ; สลับบทบาทไม่เริ่มเลขใหม่
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: โต๊ะจาก table_id / เลขรับ T-001, T-002, … ต่อเนื่องและรีเซ็ต T-001 เมื่อวันใหม่ 00:00 ครบ 20 จาก 20 ใบ; สถานะเทียบ log ถูก 20 จาก 20 ใบ; ทุกการกดยืนยันด้วยมือมีชื่อผู้ใช้และเวลาใน log 20 จาก 20 ใบ; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: ช่วงรับมาจาก fixture US-03; เลขรับกลับบ้านแยกจาก monotonic order ID ของ US-10
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-15-3"></a>

## TS-US-15-3 — ออเดอร์ใหม่และยืนยันรับเงินสด

- US: US-15
- เจ้าของ: kitchen-front
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: จอหน้าร้านแสดงหมายเลขโต๊ะ (จาก table_id ของ QR) สำหรับออเดอร์หน้าร้าน และหมายเลขรับสั่งกลับบ้านรูปแบบ T-001, T-002, … ที่ระบบสร้างอัตโนมัติ เรียงต่อเนื่อง และรีเซ็ตเป็น T-001 เมื่อเริ่มวันใหม่ (00:00) ครบทุกออเดอร์ 20 จาก 20 ใบของชุดทดสอบ · เกณฑ์ระบบ: สถานะ “จ่ายแล้ว/ยังไม่จ่าย/ค้างจ่าย” บนจอเปลี่ยนตามเหตุการณ์ในระบบ (ออเดอร์ใหม่ = ยังไม่จ่าย · เลือก PromptPay = ค้างจ่าย · กด “รับเงินสด” หรือ “ยืนยันสลิป” = จ่ายแล้ว) ถูกต้อง 20 จาก 20 ใบเมื่อเทียบกับ log เหตุการณ์ · เกณฑ์การยืนยันด้วยมือ: การกดของพนักงานหน้าร้านต้องระบุชื่อผู้ใช้และเวลาไว้ใน log ทุกครั้ง 20 จาก 20 ใบ
- clause ที่ตรวจ: F15-c: ใหม่=ยังไม่จ่าย; รับเงินสด=จ่ายแล้ว; N15-log: ผู้ใช้และเวลาในการกด
- FR / Flow / Screen: FR-15; NFR-19 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-04 / MRG-06 / MRG-07 / MRG-10 / MRG-11 / MRG-13 / MRG-14 / MRG-32 / MRG-33 → SCR-03 / SCR-05 / SCR-06 / SCR-08 / SCR-09 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: ตรวจ event/log จำลองได้; ไม่ยืนยัน audit log server หรือการรับเงินจริง; เชื่อม TS-US-08-102
- Precondition/reset: R0; C0 ส่ง1 ใบ; ยังไม่ยืนยันเงิน; F0 ตรวจสถานะแรกแล้วกลับลูกค้า
- Test data: m01=50 บาท; demofront/PIN0000 เป็นบัญชีทดสอบสาธารณะ; sim-clockเริ่ม12:00 (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: C0: pay-cash; F0: F(o)>front-payment-status, btn-receive-cash; payment-log unique ในหน้าร้านแต่กรองแถวด้วย order ID+action; sim-clock ส่วนกลาง; ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. อ่าน F(o)>front-payment-status ว่ายังไม่จ่าย
  2. C0 กด pay-cash
  3. F0 ตรวจยังไม่จ่าย
  4. จด sim-clock และกด btn-receive-cash ในใบ o
  5. อ่านสถานะและ payment-log แถวที่มี order ID และ action รับเงินสด
- Expected result: เปลี่ยนเป็นจ่ายแล้วเมื่อหน้าร้านกด; log จำลองมี order ID, demofront และเวลา ISO ตรง sim-clock ที่กด; ลูกค้าเลือกเงินสดอย่างเดียวไม่ใช่รับเงินแล้ว
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: โต๊ะจาก table_id / เลขรับ T-001, T-002, … ต่อเนื่องและรีเซ็ต T-001 เมื่อวันใหม่ 00:00 ครบ 20 จาก 20 ใบ; สถานะเทียบ log ถูก 20 จาก 20 ใบ; ทุกการกดยืนยันด้วยมือมีชื่อผู้ใช้และเวลาใน log 20 จาก 20 ใบ; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: 20 จาก20 และชื่อผู้ใช้ทุกการกดต้องตรวจระบบจริง TS-US-15-6; Q-15 เรื่อง log
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-15-4"></a>

## TS-US-15-4 — PromptPay ค้างจ่ายจนหน้าร้านยืนยันสลิป

- US: US-15
- เจ้าของ: kitchen-front
- ประเภท: ทางเลือก
- AC ต้นฉบับเต็ม: จอหน้าร้านแสดงหมายเลขโต๊ะ (จาก table_id ของ QR) สำหรับออเดอร์หน้าร้าน และหมายเลขรับสั่งกลับบ้านรูปแบบ T-001, T-002, … ที่ระบบสร้างอัตโนมัติ เรียงต่อเนื่อง และรีเซ็ตเป็น T-001 เมื่อเริ่มวันใหม่ (00:00) ครบทุกออเดอร์ 20 จาก 20 ใบของชุดทดสอบ · เกณฑ์ระบบ: สถานะ “จ่ายแล้ว/ยังไม่จ่าย/ค้างจ่าย” บนจอเปลี่ยนตามเหตุการณ์ในระบบ (ออเดอร์ใหม่ = ยังไม่จ่าย · เลือก PromptPay = ค้างจ่าย · กด “รับเงินสด” หรือ “ยืนยันสลิป” = จ่ายแล้ว) ถูกต้อง 20 จาก 20 ใบเมื่อเทียบกับ log เหตุการณ์ · เกณฑ์การยืนยันด้วยมือ: การกดของพนักงานหน้าร้านต้องระบุชื่อผู้ใช้และเวลาไว้ใน log ทุกครั้ง 20 จาก 20 ใบ
- clause ที่ตรวจ: F15-c: เลือก PromptPay=ค้างจ่าย; ยืนยันสลิป=จ่ายแล้ว; N15-log
- FR / Flow / Screen: FR-15; NFR-19 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-04 / MRG-06 / MRG-07 / MRG-10 / MRG-11 / MRG-13 / MRG-14 / MRG-32 / MRG-33 → SCR-03 / SCR-05 / SCR-06 / SCR-08 / SCR-09 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: ตรวจสถานะและข้อความ log จำลอง ไม่ตรวจสลิป/ยอดโอนจริง
- Precondition/reset: R0; C0 ส่ง1 ใบ; PromptPayเปิดตาม reset; ไม่มีธุรกรรมจริง
- Test data: m02=55 บาท1 จาน; demofront/PIN0000; ไม่ใช้สลิปหรือข้อมูลบัญชีจริง (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: C0: pay-promptpay, payment-status; F0: F(o)>front-payment-status, btn-confirm-slip; payment-log กรอง order ID+action; sim-clock; ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. C0 กด pay-promptpay
  2. F0 ตรวจค้างจ่ายใน F(o)
  3. จด sim-clock
  4. กด btn-confirm-slip ใบ o
  5. อ่านสถานะและ log action ยืนยันสลิป
- Expected result: ก่อนยืนยันค้างจ่าย; หลังหน้าร้านกดจ่ายแล้ว; log จำลองระบุผู้ใช้และเวลาการกดตรงใบ o
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: โต๊ะจาก table_id / เลขรับ T-001, T-002, … ต่อเนื่องและรีเซ็ต T-001 เมื่อวันใหม่ 00:00 ครบ 20 จาก 20 ใบ; สถานะเทียบ log ถูก 20 จาก 20 ใบ; ทุกการกดยืนยันด้วยมือมีชื่อผู้ใช้และเวลาใน log 20 จาก 20 ใบ; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: หมายเหตุ ก. ไม่มีข้อมูลเมื่อ setup เกี่ยว fallback; 20 จาก20 ต้องตรวจ TS-US-15-6
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-15-5"></a>

## TS-US-15-5 — เลขรับกลับบ้านรีเซ็ตเมื่อเริ่มวันใหม่ 00:00

- US: US-15
- เจ้าของ: kitchen-front
- ประเภท: ข้อยกเว้น
- AC ต้นฉบับเต็ม: จอหน้าร้านแสดงหมายเลขโต๊ะ (จาก table_id ของ QR) สำหรับออเดอร์หน้าร้าน และหมายเลขรับสั่งกลับบ้านรูปแบบ T-001, T-002, … ที่ระบบสร้างอัตโนมัติ เรียงต่อเนื่อง และรีเซ็ตเป็น T-001 เมื่อเริ่มวันใหม่ (00:00) ครบทุกออเดอร์ 20 จาก 20 ใบของชุดทดสอบ · เกณฑ์ระบบ: สถานะ “จ่ายแล้ว/ยังไม่จ่าย/ค้างจ่าย” บนจอเปลี่ยนตามเหตุการณ์ในระบบ (ออเดอร์ใหม่ = ยังไม่จ่าย · เลือก PromptPay = ค้างจ่าย · กด “รับเงินสด” หรือ “ยืนยันสลิป” = จ่ายแล้ว) ถูกต้อง 20 จาก 20 ใบเมื่อเทียบกับ log เหตุการณ์ · เกณฑ์การยืนยันด้วยมือ: การกดของพนักงานหน้าร้านต้องระบุชื่อผู้ใช้และเวลาไว้ใน log ทุกครั้ง 20 จาก 20 ใบ
- clause ที่ตรวจ: F15-b: ขอบวันใหม่รีเซ็ต T-001 เวลา00:00
- FR / Flow / Screen: FR-15; NFR-19 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-04 / MRG-06 / MRG-07 / MRG-10 / MRG-11 / MRG-13 / MRG-14 / MRG-32 / MRG-33 → SCR-03 / SCR-05 / SCR-06 / SCR-08 / SCR-09 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: มีปุ่มถึง00:00พอดีใน mock ได้; ไม่ใช้ +1วันตอนเที่ยงแทน boundary และไม่พิสูจน์ timezone ระบบจริง
- Precondition/reset: R0; sim-clock=2026-01-01T12:00:00+07:00; ใช้ปุ่มเวลาเดิม ไม่ reset ข้ามวัน
- Test data: กลับบ้านก่อนเที่ยงคืน2 ใบและหลังเที่ยงคืน2 ใบ; m01 รายการละ1; +07:00 เป็นเขตเวลา fixture (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: C0: order-mode, pickup-slot, btn-submit-order, takeaway-id, order-id; F0: F(o); sim-clock, btn-advance-10m ส่วนกลาง; ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. กด btn-advance-10m 71 ครั้งตรวจ sim-clock=23:50
  2. C0 เลือก takeaway และ slot ที่มีอยู่จริง ณ ตอนนั้น ส่ง2 ใบ จด T-001/T-002
  3. กดเพิ่ม10 นาที1 ครั้งตรวจ00:00วันใหม่
  4. เลือก slot ใหม่ที่ UIเสนอ ส่ง2 ใบ
  5. F0 ตรวจทั้ง4 ใบและวันที่
- Expected result: ก่อนข้ามวัน T-001,T-002; ออเดอร์แรกหลัง00:00เป็นT-001 และใบถัดไปT-002; เก็บวันที่คู่เลขรับเพื่อแยกสองวัน; order ID ยังคงคนละเลข ไม่ถือเลขรับซ้ำข้ามวันเป็น order ID ซ้ำ
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: โต๊ะจาก table_id / เลขรับ T-001, T-002, … ต่อเนื่องและรีเซ็ต T-001 เมื่อวันใหม่ 00:00 ครบ 20 จาก 20 ใบ; สถานะเทียบ log ถูก 20 จาก 20 ใบ; ทุกการกดยืนยันด้วยมือมีชื่อผู้ใช้และเวลาใน log 20 จาก 20 ใบ; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: เขตเวลาร้านและวิธีแยกเลขรับซ้ำข้ามวันยัง Q-15; การเลือก slot หลังขยับเวลาต้องอ่านค่าจริงไม่เดา
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-15-6"></a>

## TS-US-15-6 — ตรวจโต๊ะ เลขรับ สถานะและ log ครบ20 ใบในระบบจริง

- US: US-15
- เจ้าของ: kitchen-front
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: จอหน้าร้านแสดงหมายเลขโต๊ะ (จาก table_id ของ QR) สำหรับออเดอร์หน้าร้าน และหมายเลขรับสั่งกลับบ้านรูปแบบ T-001, T-002, … ที่ระบบสร้างอัตโนมัติ เรียงต่อเนื่อง และรีเซ็ตเป็น T-001 เมื่อเริ่มวันใหม่ (00:00) ครบทุกออเดอร์ 20 จาก 20 ใบของชุดทดสอบ · เกณฑ์ระบบ: สถานะ “จ่ายแล้ว/ยังไม่จ่าย/ค้างจ่าย” บนจอเปลี่ยนตามเหตุการณ์ในระบบ (ออเดอร์ใหม่ = ยังไม่จ่าย · เลือก PromptPay = ค้างจ่าย · กด “รับเงินสด” หรือ “ยืนยันสลิป” = จ่ายแล้ว) ถูกต้อง 20 จาก 20 ใบเมื่อเทียบกับ log เหตุการณ์ · เกณฑ์การยืนยันด้วยมือ: การกดของพนักงานหน้าร้านต้องระบุชื่อผู้ใช้และเวลาไว้ใน log ทุกครั้ง 20 จาก 20 ใบ
- clause ที่ตรวจ: F15-a/b/c และ N15-log: เกณฑ์แต่ละส่วน20 จาก20 ใบ
- FR / Flow / Screen: FR-15; NFR-19 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-04 / MRG-06 / MRG-07 / MRG-10 / MRG-11 / MRG-13 / MRG-14 / MRG-32 / MRG-33 → SCR-03 / SCR-05 / SCR-06 / SCR-08 / SCR-09 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: ต้องมี log ระบบจริง; มีขั้นผู้ตรวจด้วยคนบันทึกผู้ใช้/เวลากด แต่ automationหลักเป็นmock-not-testable เพราะหลักฐาน serverไม่มี
- Precondition/reset: ระบบทดสอบจริงและ log เหตุการณ์; ได้คำตอบเขตเวลาของ00:00; ผู้ตรวจทราบผู้ใช้จำลองและเวลากด
- Test data: 20 ใบจำลอง: dine-in10 ใบและtakeaway10 ใบ; แต่ละกลุ่มใช้เงินสด5/สลิป5; กลับบ้าน5 ก่อนและ5 หลัง00:00; เป็นการแบ่ง fixture ไม่เพิ่มสัดส่วน AC (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: Mock มี F(o), front-payment-status, btn-receive-cash, btn-confirm-slip, payment-log; selectorและที่อ่านlogจริง MISSING; ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. สร้างออเดอร์จาก QR โต๊ะหรือเลือกกลับบ้าน
  2. เก็บ ID,table_id/เลขรับและวัน
  3. เก็บเหตุการณ์ใหม่และสถานะยังไม่จ่ายทุกใบ
  4. ใบPromptPayเลือกแล้วเทียบค้างจ่าย
  5. ผู้ตรวจสังเกตหน้าร้านกดรับเงินสด/ยืนยันสลิปและจดผู้ใช้เวลา
  6. เทียบ log กับสถานะจ่ายแล้วและผู้กดทุกครั้ง
  7. ตรวจต่อเลขและรีเซ็ต00:00
- Expected result: โต๊ะ/เลขรับอัตโนมัติและวันใหม่ถูก20 จาก20 ใบ; สถานะตามเหตุการณ์ถูก20 จาก20 ใบเทียบ log; ทุกการกดยืนยันมีชื่อผู้ใช้และเวลาในlogครบ20 จาก20 ใบ; รายงานทั้ง3 เกณฑ์แยกกัน
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: โต๊ะจาก table_id / เลขรับ T-001, T-002, … ต่อเนื่องและรีเซ็ต T-001 เมื่อวันใหม่ 00:00 ครบ 20 จาก 20 ใบ; สถานะเทียบ log ถูก 20 จาก 20 ใบ; ทุกการกดยืนยันด้วยมือมีชื่อผู้ใช้และเวลาใน log 20 จาก 20 ใบ; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: BLOCKED ระบบ/log/timezone Q-15; ไม่รับรองความถูกต้องของสลิปจากแค่ log
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-15-7"></a>

## TS-US-15-7 — กดยืนยันเงินซ้ำหรือทั้งสองวิธีชนกัน

- US: US-15
- เจ้าของ: kitchen-front
- ประเภท: ผิดพลาด
- AC ต้นฉบับเต็ม: จอหน้าร้านแสดงหมายเลขโต๊ะ (จาก table_id ของ QR) สำหรับออเดอร์หน้าร้าน และหมายเลขรับสั่งกลับบ้านรูปแบบ T-001, T-002, … ที่ระบบสร้างอัตโนมัติ เรียงต่อเนื่อง และรีเซ็ตเป็น T-001 เมื่อเริ่มวันใหม่ (00:00) ครบทุกออเดอร์ 20 จาก 20 ใบของชุดทดสอบ · เกณฑ์ระบบ: สถานะ “จ่ายแล้ว/ยังไม่จ่าย/ค้างจ่าย” บนจอเปลี่ยนตามเหตุการณ์ในระบบ (ออเดอร์ใหม่ = ยังไม่จ่าย · เลือก PromptPay = ค้างจ่าย · กด “รับเงินสด” หรือ “ยืนยันสลิป” = จ่ายแล้ว) ถูกต้อง 20 จาก 20 ใบเมื่อเทียบกับ log เหตุการณ์ · เกณฑ์การยืนยันด้วยมือ: การกดของพนักงานหน้าร้านต้องระบุชื่อผู้ใช้และเวลาไว้ใน log ทุกครั้ง 20 จาก 20 ใบ
- clause ที่ตรวจ: ข้อค้างการกดยืนยันซ้ำของ F15-c/N15-log
- FR / Flow / Screen: FR-15; NFR-19 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-04 / MRG-06 / MRG-07 / MRG-10 / MRG-11 / MRG-13 / MRG-14 / MRG-32 / MRG-33 → SCR-03 / SCR-05 / SCR-06 / SCR-08 / SCR-09 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: ปุ่มdisabledในmockไม่เป็นหลักฐานการป้องกันรับเงินซ้ำหรือกติกาlogจริง
- Precondition/reset: ระบบทดสอบจริงและนโยบายการกดซ้ำที่ยืนยัน; ออเดอร์จำลองหนึ่งใบค้างจ่าย
- Test data: คู่คำสั่งรับเงินสด/ยืนยันสลิปสำหรับใบเดียว และคำสั่งเดิมซ้ำ (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: Mock F(o)>btn-receive-cash/btn-confirm-slip disabledหลังจ่ายแล้ว; ช่องส่งซ้ำระบบจริง MISSING; ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. หลังได้คำตอบ ส่งคำสั่งซ้ำหรือสองคำสั่งชนกันในระบบทดสอบ
  2. เทียบสถานะสุดท้าย ผู้กด เวลา และ log ทุกเหตุการณ์
- Expected result: BLOCKED/ไม่มีข้อมูลสำหรับเกณฑ์รับ/ปฏิเสธการกดซ้ำและจำนวน log ที่ต้องเกิด; เกณฑ์บันทึกผู้ใช้และเวลาทุกการกดยืนยันที่ ACกำหนดยังคงเดิม
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: โต๊ะจาก table_id / เลขรับ T-001, T-002, … ต่อเนื่องและรีเซ็ต T-001 เมื่อวันใหม่ 00:00 ครบ 20 จาก 20 ใบ; สถานะเทียบ log ถูก 20 จาก 20 ใบ; ทุกการกดยืนยันด้วยมือมีชื่อผู้ใช้และเวลาใน log 20 จาก 20 ใบ; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: ข้อค้างเพิ่มจากACที่ไม่กำหนดผลซ้ำ; ไม่ใช้no-opในโค้ดเป็นกฎร้าน
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-16-1"></a>

## TS-US-16-1 — หน้าร้านเปิด–ปิดโต๊ะแล้วเปิดรอบใหม่ไม่ปนรายการเดิม

- US: US-16
- เจ้าของ: kitchen-front
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: เมื่อกดปิดโต๊ะ การสแกน QR โต๊ะเดิมเริ่มรอบสั่งใหม่ (session ใหม่) และรายการรอบเดิมไม่ปรากฏ ทดสอบ 5 โต๊ะ ผ่านอย่างน้อย 5 จาก 5
- clause ที่ตรวจ: F16-a: เปิด/ปิดโต๊ะ; F16-b: QRเดิมเริ่มsessionใหม่และไม่มีรายการเดิม
- FR / Flow / Screen: FR-16; NFR-21 (การแยก session) ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-12 / MRG-13 / MRG-15 / MRG-16 / MRG-17 → SCR-01 / SCR-08 / SCR-10 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: manual
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: manualเพราะให้คนตรวจการเปิดโต๊ะและรายการทั้งรอบที่ไม่มีtestidเฉพาะ; ใช้UIจำลองได้ ไม่พิสูจน์QRจริงหรือsessionฝั่งserver
- Precondition/reset: R0; ไม่มีรอบเปิดที่โต๊ะ01; ผู้ตรวจใช้บัญชีหน้าร้านจำลอง
- Test data: โต๊ะ01; รอบเดิมm01=50บาท1จาน; รอบใหม่m02=55บาท1จาน (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: F0: front-table-select, btn-close-table; ปุ่มเปิดโต๊ะไม่มีdata-testid (MISSING เฉพาะtestid) แต่มีbuttonชื่อ เปิดรอบโต๊ะจำลอง และdata-action=front-open ในHTML; C0: table-select,btn-open-menu,session-id,customer-order-status,order-id; รายละเอียดออเดอร์ทั้งหมดในรอบนี้ไม่มีtestid ใช้ผู้ตรวจอ่าน; ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. F0 เลือก front-table-select=01 แล้วผู้ตรวจกดปุ่มชื่อ เปิดรอบโต๊ะจำลอง
  2. C0 เปิดโต๊ะ01 จดsession-id=S_old ส่งm01
  3. F0 ปิดโต๊ะ01ด้วยbtn-close-table
  4. C0เลือก01และbtn-open-menu จดS_new
  5. ผู้ตรวจอ่านหน้ารอบใหม่และประวัติ
  6. ส่งm02ตรวจใบใหม่
- Expected result: S_newต่างจากS_old; รอบใหม่ไม่มีm01และไม่มีออเดอร์เก่าในรายละเอียดออเดอร์ทั้งหมดในรอบนี้; ใบใหม่มีm02ผูกS_new; ประวัติรอบปิดในหน้าร้านคงอยู่ได้ โดยไม่ถือเป็นรายการปนในรอบลูกค้าใหม่
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: ปิดโต๊ะแล้ว QR เดิมเริ่ม session ใหม่ รายการเก่าไม่ปรากฏ และสั่งต่อรอบเดิมไม่ได้; 5 โต๊ะ อย่างน้อย 5 จาก 5; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: 1โต๊ะไม่แทน5โต๊ะ; ไม่เพิ่มเงื่อนไขจ่ายครบก่อนปิด Q-16; ข้อบกพร่องtestidไม่ใช่ฟีเจอร์เปิดโต๊ะหาย
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-16-2"></a>

## TS-US-16-2 — คำสั่งที่ผูกรอบปิดแล้วสั่งต่อรอบเดิมไม่ได้

- US: US-16
- เจ้าของ: kitchen-front
- ประเภท: ข้อยกเว้น
- AC ต้นฉบับเต็ม: เมื่อกดปิดโต๊ะ การสแกน QR โต๊ะเดิมเริ่มรอบสั่งใหม่ (session ใหม่) และรายการรอบเดิมไม่ปรากฏ ทดสอบ 5 โต๊ะ ผ่านอย่างน้อย 5 จาก 5
- clause ที่ตรวจ: F16-c: QRโต๊ะนั้นสั่งต่อจากรอบเดิมไม่ได้
- FR / Flow / Screen: FR-16; NFR-21 (การแยก session) ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-12 / MRG-13 / MRG-15 / MRG-16 / MRG-17 → SCR-01 / SCR-08 / SCR-10 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: จำเป็นต้องทดสอบsessionและคำสั่งจริง; ไม่ใช้DOMที่ซ่อนเป็นการพิสูจน์serverป้องกันคำสั่ง
- Precondition/reset: ระบบทดสอบจริง; เปิดหน้าลูกค้าค้างและเก็บsessionเก่าก่อนปิด; หน้าร้านมีสิทธิ์ปิดโต๊ะ
- Test data: 5โต๊ะจำลอง01–05; โต๊ะละsessionเก่าและคำสั่งm01ที่ยังไม่ส่ง (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: Mock มีbtn-close-table,session-id,btn-submit-orderแต่ปิดแล้วซ่อนฟอร์ม; ช่องส่งคำสั่งS_oldและselectorระบบจริงMISSING; ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. หน้าร้านปิดแต่ละโต๊ะ
  2. ใช้หน้าค้าง/คำสั่งที่ยังอ้างS_oldพยายามส่ง
  3. ตรวจการรับคำสั่งและlog
  4. สแกนQRเดิมเริ่มS_newและส่งm02เป็นชุดควบคุม
- Expected result: คำสั่งเก่าไม่เพิ่มออเดอร์ในS_old; สแกนใหม่ได้S_newและไม่ปนรายการเก่า; ครบอย่างน้อย5จาก5โต๊ะ; ข้อความผิดพลาด/การนำหน้าไปที่ใดBLOCKEDรอQ-16
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: ปิดโต๊ะแล้ว QR เดิมเริ่ม session ใหม่ รายการเก่าไม่ปรากฏ และสั่งต่อรอบเดิมไม่ได้; 5 โต๊ะ อย่างน้อย 5 จาก 5; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: Q-16: พฤติกรรมหน้าเดิมไม่มีข้อมูล แต่ข้อห้ามสั่งต่อรอบเดิมชัดเจน; seed3โต๊ะไม่ใช้แทน5
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-16-3"></a>

## TS-US-16-3 — ปิดแล้วสแกนใหม่แยกรอบครบ5โต๊ะ

- US: US-16
- เจ้าของ: kitchen-front
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: เมื่อกดปิดโต๊ะ การสแกน QR โต๊ะเดิมเริ่มรอบสั่งใหม่ (session ใหม่) และรายการรอบเดิมไม่ปรากฏ ทดสอบ 5 โต๊ะ ผ่านอย่างน้อย 5 จาก 5
- clause ที่ตรวจ: F16-a/b และNFR-21: sessionใหม่ไม่ปนเดิมครบ5โต๊ะ
- FR / Flow / Screen: FR-16; NFR-21 (การแยก session) ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-12 / MRG-13 / MRG-15 / MRG-16 / MRG-17 → SCR-01 / SCR-08 / SCR-10 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: ต้องมีระบบจริง5โต๊ะและหลักฐานแยกsession; ไม่สร้างโต๊ะเพิ่มในInputเพื่อให้mockดูครอบคลุม
- Precondition/reset: ระบบทดสอบจริงมีQRและโต๊ะจำลอง5โต๊ะ; มีสิทธิ์หน้าร้านและตรวจsessionได้
- Test data: โต๊ะ01–05; แต่ละโต๊ะรอบเดิมm01และรอบใหม่m02อย่างละ1จาน; จำนวนนี้เป็นfixture (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: Mockมีtable-select,btn-open-menu,session-id,front-table-select,btn-close-table; ไม่มีQRจริง/โต๊ะ04–05ในseed; selectorระบบจริงMISSING; ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. หน้าร้านเปิดโต๊ะ
  2. สแกนQRเดิมสร้างรอบและส่งm01
  3. จดsession/order
  4. ปิดโต๊ะแล้วสแกนQRเดียวกันอีกครั้ง
  5. เทียบsessionใหม่และรายการ
  6. ส่งm02และตรวจผูกsessionใหม่
  7. ทำครบ5โต๊ะพร้อมตรวจคำสั่งเก่าตามTS-US-16-2
- Expected result: sessionใหม่ต่างเดิมและรายการเดิมไม่ปรากฏในรอบใหม่; คำสั่งเก่าใช้ต่อไม่ได้; เงื่อนไขครบอย่างน้อย5จาก5โต๊ะ แยกหลักฐานรายโต๊ะ
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: ปิดโต๊ะแล้ว QR เดิมเริ่ม session ใหม่ รายการเก่าไม่ปรากฏ และสั่งต่อรอบเดิมไม่ได้; 5 โต๊ะ อย่างน้อย 5 จาก 5; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: BLOCKED ระบบ/QR/5โต๊ะ; ขั้นเปิดและเงื่อนไขปิดค้างรอQ-16
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-16-4"></a>

## TS-US-16-4 — ขอปิดโต๊ะขณะยังค้างทำหรือค้างจ่าย

- US: US-16
- เจ้าของ: kitchen-front
- ประเภท: ผิดพลาด
- AC ต้นฉบับเต็ม: เมื่อกดปิดโต๊ะ การสแกน QR โต๊ะเดิมเริ่มรอบสั่งใหม่ (session ใหม่) และรายการรอบเดิมไม่ปรากฏ ทดสอบ 5 โต๊ะ ผ่านอย่างน้อย 5 จาก 5
- clause ที่ตรวจ: ข้อค้างเงื่อนไขการปิดโต๊ะของF16-a
- FR / Flow / Screen: FR-16; NFR-21 (การแยก session) ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MRG-12 / MRG-13 / MRG-15 / MRG-16 / MRG-17 → SCR-01 / SCR-08 / SCR-10 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: ต้องมีผลธุรกิจที่ยืนยันและระบบจริง; การยอมปิดของmockเป็นสมมติฐาน
- Precondition/reset: ระบบจริงสำหรับทดสอบและคำตอบQ-16
- Test data: กรณีA: อาหารกำลังทำ; กรณีB: PromptPayค้างจ่าย; แยกโต๊ะจำลองคนละชุด (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: MockมีF(o),front-payment-status,front-table-select,btn-close-table; selector/logระบบจริงMISSING; ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. สร้างstateตามกรณี
  2. หน้าร้านขอปิดโต๊ะ
  3. บันทึกผลปุ่ม session รายการครัว และสถานะเงิน
  4. เทียบกับนโยบายที่ได้รับ
- Expected result: BLOCKED/ไม่มีข้อมูลว่าควรอนุญาต ปฏิเสธ หรือเตือน; ถ้าปิดสำเร็จแล้วข้อกำหนดsessionใหม่ยังต้องเป็นตามAC; ไม่กำหนดต้องจ่ายครบก่อนปิด
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: ปิดโต๊ะแล้ว QR เดิมเริ่ม session ใหม่ รายการเก่าไม่ปรากฏ และสั่งต่อรอบเดิมไม่ได้; 5 โต๊ะ อย่างน้อย 5 จาก 5; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: Q-16 และQ-V2-STATE; ไม่อนุมานว่าปิดโต๊ะแล้วอาหารหรือเงินถูกยกเลิก
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-17-1"></a>

## TS-US-17-1 — รวมบิล3รอบพร้อมตรวจเครื่องคิดเลขครบ10โต๊ะ

- US: US-17
- เจ้าของ: kitchen-front
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: โต๊ะที่สั่ง 3 รอบ ยอดรวมบิลเท่ากับผลรวมของทุกรายการ (ตรวจด้วยเครื่องคิดเลข) ในอย่างน้อย 9 จาก 10 โต๊ะทดสอบ และบิลรวมแสดงรายการแยกตามรอบ
- clause ที่ตรวจ: F17-a: รวมทุกรายการ; F17-b: แสดงแยกตามรอบ; เกณฑ์9จาก10โต๊ะ
- FR / Flow / Screen: MISSING — ไม่มี FR/NFR ของ US-17 ใน v2 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MISSING — ไม่มี Flow ของ US-17 ใน v2 → MISSING — ไม่มี Screen/ฟังก์ชันรวมบิลใน UI v2 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: ต้องมีระบบรวมบิลจริง; มีขั้นตรวจด้วยคนและเครื่องคิดเลขตามAC แต่ยังทำไม่ได้กับmockนี้
- Precondition/reset: BLOCKED: UIv2ไม่มีรวมบิลหลายรอบ ไม่มีFR/Flow/ScreenสำหรับUS-17; ต้องมีระบบที่รองรับก่อน; ผู้ตรวจเตรียมเครื่องคิดเลข
- Test data: 10โต๊ะจำลอง01–10 โต๊ะละ3รอบ; โต๊ะk (1–10): รอบ1รายการ50+10และ55 =115; รอบ2จำนวนkรายการที่40 =40×k; รอบ3ราคา30หนึ่งรายการ; expected 145+40×k คือ185,225,265,305,345,385,425,465,505,545บาท; ราคา/จำนวนเป็นfixture (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: MISSING: ไม่มีdata-testidรวมบิล/รายละเอียดแยกรอบ; front-totalและcustomer-adjusted-totalเป็นยอดต่อออเดอร์ใช้แทนไม่ได้; ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. เมื่อมีระบบ เปิดแต่ละโต๊ะในsessionเดียว
  2. สั่งตามชุด3รอบและเก็บรายการ/ราคา ณสั่ง
  3. ขอรวมบิล
  4. ผู้ตรวจบวกทุกรายการด้วยเครื่องคิดเลขทีละโต๊ะและเทียบยอด
  5. ตรวจรายละเอียดบิลว่ารอบ1/2/3แยกชัดและทุกรายการครบ
- Expected result: ยอดรวมเท่าผลรวมทุกรายการจากเครื่องคิดเลขอย่างน้อย9จาก10โต๊ะ; บิลรวมแสดงรายการแยกตามรอบ ไม่ยอมรับยอดตรงแต่รายละเอียดหาย; ไม่สร้างสูตรภาษี/ส่วนลด/ค่าบริการเพิ่มเติม
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: โต๊ะสั่ง 3 รอบ ยอดรวมเท่าผลรวมทุกรายการ ตรวจด้วยเครื่องคิดเลข อย่างน้อย 9 จาก 10 โต๊ะทดสอบ และบิลรวมแยกรายการตามรอบ; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: BLOCKED FR/Flow/Screen/UI; ขอบเขตยอดเมื่อคืนหรือเปลี่ยน/ปัดเศษยังไม่มีข้อมูล; ชุดนี้ใช้รายการปกติไม่มีส่วนลดและไม่มีการคืน
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-17-2"></a>

## TS-US-17-2 — รวมบิลซ้ำหรือคำสั่งบางรอบยังไม่ยืนยัน

- US: US-17
- เจ้าของ: kitchen-front
- ประเภท: ผิดพลาด
- AC ต้นฉบับเต็ม: โต๊ะที่สั่ง 3 รอบ ยอดรวมบิลเท่ากับผลรวมของทุกรายการ (ตรวจด้วยเครื่องคิดเลข) ในอย่างน้อย 9 จาก 10 โต๊ะทดสอบ และบิลรวมแสดงรายการแยกตามรอบ
- clause ที่ตรวจ: ข้อค้างขอบเขตทุกรายการ/รอบสั่งของF17-a/b
- FR / Flow / Screen: MISSING — ไม่มี FR/NFR ของ US-17 ใน v2 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MISSING — ไม่มี Flow ของ US-17 ใน v2 → MISSING — ไม่มี Screen/ฟังก์ชันรวมบิลใน UI v2 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: UIv2ไม่มีฟังก์ชันและไม่มีoracleกรณีผิดพลาด ต้องมีระบบ/คำตอบก่อน
- Precondition/reset: BLOCKED: ไม่มีระบบรวมบิลและนโยบายกรณีผิดพลาด; เตรียมโต๊ะจำลอง3รอบเมื่อมีระบบ
- Test data: โต๊ะ01: รอบ1=115 รอบ2=40 รอบ3=30บาท; กรณีAขอรวมซ้ำ; กรณีBรอบ3ยังเป็นตะกร้าไม่ยืนยัน (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: MISSING: UI/selectorรวมบิลและรอบที่รวม; ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. ทำกรณีA/Bแยกชุดหลังคำตอบธุรกิจ
  2. บันทึกสถานะรอบและรายการก่อนขอรวม
  3. กดรวมซ้ำหรือรวมขณะรอบ3ไม่ยืนยัน
  4. เก็บบิล/ข้อความ/รายการจริงเทียบกับขอบเขตที่ยืนยัน
- Expected result: BLOCKED/ไม่มีข้อมูลว่าจะปฏิเสธ สร้างบิลเดิม/ใหม่ หรือนับรอบที่ยังไม่ยืนยันอย่างไร; หลักยอดเท่าทุกรายการที่อยู่ในขอบเขตบิลยังต้องคง; ไม่เพิ่มexpectedไม่คิดซ้ำเป็นกฎที่อนุมัติ
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: โต๊ะสั่ง 3 รอบ ยอดรวมเท่าผลรวมทุกรายการ ตรวจด้วยเครื่องคิดเลข อย่างน้อย 9 จาก 10 โต๊ะทดสอบ และบิลรวมแยกรายการตามรอบ; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: ข้อค้างUS-17: นิยามรอบที่รวม การรวมซ้ำ การแก้/คืนรายการระหว่างรวม; ไม่สร้างFR-17หรือFlowขึ้นเอง
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-17-3"></a>

## TS-US-17-3 — ตรวจบิลรายการขาด ซ้ำ และข้ามโต๊ะโดยทั้งสามรอบยืนยันแล้ว

- US: US-17
- เจ้าของ: kitchen-front
- ประเภท: ผิดพลาด
- AC ต้นฉบับเต็ม: โต๊ะที่สั่ง 3 รอบ ยอดรวมบิลเท่ากับผลรวมของทุกรายการ (ตรวจด้วยเครื่องคิดเลข) ในอย่างน้อย 9 จาก 10 โต๊ะทดสอบ และบิลรวมแสดงรายการแยกตามรอบ
- clause ที่ตรวจ: รวมทุกรายการจาก 3 รอบของโต๊ะเดียวกัน เทียบเครื่องคิดเลข และแสดงแยกรอบ
- FR / Flow / Screen: MISSING — ไม่มี FR/NFR ของ US-17 ใน v2 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MISSING — ไม่มี Flow ของ US-17 ใน v2 → MISSING — ไม่มี Screen/ฟังก์ชันรวมบิลใน UI v2 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: แก้ D05 เชิงออกแบบ; ต้องมีระบบ/จุดแทรก fault และจุดสังเกตตาม Precondition ซึ่งยังไม่มี จึง BLOCKED การรัน. เป็นแผนตรวจจับผลผิดด้วย oracle อิสระ ไม่ใช่การเปลี่ยนชื่อ happy path; ยังไม่ได้ทำ fault หรือรันทดสอบ
- Precondition/reset: BLOCKED การรัน: U17 ไม่มี FR/Flow/Screen/ฟังก์ชันรวมบิล; ต้องมีระบบและจุดแทรกชุดรายการก่อนสร้างบิล. เตรียมตารางอ้างอิงอิสระและเครื่องคิดเลข; ทั้งสามรอบยืนยันครบ ไม่มี draft/คืน/เปลี่ยน/ภาษี/ส่วนลดใน fixture
- Test data: ใช้ 10 โต๊ะ k=1–10 ตาม TS-US-17-1: รอบ 1 จาน 50+ตัวเลือก10 และจาน55 รวม115; รอบ2 จาน40 จำนวนk รวม40k; รอบ3 จาน30 จำนวน1. ยอดโต๊ะ01–10=185,225,265,305,345,385,425,465,505,545 บาท. จด table/session/order/round/item ID ทุกแถวแยกจากผลรวมระบบ; รอบ3 โต๊ะ01 และ02 แม้ราคา30เท่ากันเป็นคนละรายการ

- data-testid และ scope: MISSING: selector บิลรวม/แยกรอบ/จุดแทรก; front-total เป็นรายออเดอร์ใช้แทนไม่ได้. จับคู่ข้อมูลจริงด้วย table/session/round/item ID; ไม่สร้าง FR-17 หรือ API
- ขั้นตอน:

  1. ยืนยันสามรอบครบทั้ง 10 โต๊ะแล้วบันทึกสำเนารายการอ้างอิง; คำนวณยอดแต่ละรอบ/โต๊ะด้วยเครื่องคิดเลขโดยไม่อ่านยอดจากบิลระบบเป็น oracle
  2. control: รวมบิลทั้ง 10 โต๊ะ อ่านยอดและรายละเอียดแยกรอบเทียบสำเนาอิสระ; เก็บทุกโต๊ะเพื่อนับอย่างน้อย 9 จาก 10 ตาม AC
  3. fault A: reset แล้วให้ตัวแทรกชุดรายการขาเข้าตัวสร้างบิลโต๊ะ01 ลบรายการรอบ3 ราคา30 โดยไม่แก้ออเดอร์ยืนยันต้นทาง; fault B ทำแยกหลัง reset โดยเพิ่มสำเนารายการเดียวกันซ้ำอีก1รายการ. ทุกครั้งเปิดบิลและเทียบจำนวน/ID/รอบ/ยอดกับสำเนาต้นทาง
  4. fault C: reset แล้วแทนรายการ30บาทรอบ3ของโต๊ะ01ด้วยรายการ30บาทรอบ3ของโต๊ะ02ในข้อมูลสร้างบิลเท่านั้น โดยคงยอด; ตรวจ table/session/item ID คู่รายละเอียดและยอด เพื่อจับการข้ามโต๊ะแม้ยอดตรง
  5. ปิดตัวแทรก คืนข้อมูลสามรอบเดิม และทำ control; เก็บ fault แยกจากผลชุด 10 โต๊ะ ไม่ใช้รายการ fault เพิ่มเป็นรอบสั่งใหม่

- Expected result: โต๊ะ01 ต้องมีรอบ1=115 รอบ2=40 รอบ3=30 รวม185 และทุกรายการเป็นของโต๊ะ01/sessionนั้น. Fault A อาจได้155 (ขาด30) และ fault B 215 (เกิน30): ต้องชี้รายการและรอบผิดด้วย ไม่ตรวจเพียงตัวเลข. Fault C แม้ได้185 ต้องจับว่า item ID ของโต๊ะ02 ปนและของโต๊ะ01หาย. เกณฑ์อย่างน้อย9จาก10ไม่ทำให้มองข้ามความผิดที่พบใน fixture รายโต๊ะ
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงชุด 10 โต๊ะ โต๊ะละ 3 รอบ และผลรวมตรงเครื่องคิดเลขอย่างน้อย 9 จาก 10 รวมรายละเอียดแยกรอบตาม AC. Fault A/B/C แยกชุดจาก control ไม่แทนหรือลดจำนวนโต๊ะ
- สมมติฐาน/ข้อค้าง: คง U17=MISSING; kitchen-front กับผู้ดูแล FR/Flow/UI จัด upstream รุ่นใหม่. เจ้าของข้อกำหนดตัดสินรวมซ้ำ/draft/คืนใน TS-US-17-2; การซ้ำของข้อมูลบิลที่แทรกนี้ไม่ใช่การกำหนดนโยบายกดรวมบิลซ้ำ
- Status: MOCK_NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-18-1"></a>

## TS-US-18-1 — ตัวนับคิวและสีแดงเมื่อค้างเกิน15นาทีครบ10ใบ

- US: US-18
- เจ้าของ: kitchen-front
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: จอครัวแสดงตัวนับออเดอร์ค้าง และออเดอร์ที่ค้างเกิน 15 นาที (นับจากเวลาลูกค้ากดยืนยันสั่ง) เปลี่ยนเป็นสีแดง ทดสอบ 10 ออเดอร์ที่ปล่อยเกินเวลา ผ่านอย่างน้อย 9 จาก 10
- clause ที่ตรวจ: F18-a: ตัวนับค้าง; F18-b: สีแดงเมื่อเกิน15นาทีจากลูกค้ายืนยัน; เป้าหมาย9จาก10; USกล่าวถึงค้างนานสุด
- FR / Flow / Screen: MISSING — ไม่มี FR/NFR ของ US-18 ใน v2 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MISSING — ไม่มี Flow ของ US-18 ใน v2 → MISSING — ไม่มี Screen/counter/สีเตือนค้างของ US-18 ใน UI v2 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: ต้องมีระบบรองรับอายุคิวและเวลาเหตุการณ์จริง; ต้องให้คนตรวจสีที่มองเห็นด้วย; btn-advance-10mไม่สร้างฟีเจอร์ที่ขาด
- Precondition/reset: BLOCKED: UIv2ไม่มีcounter/สีเตือนUS-18 ไม่มีFR/Flow/Screen; ต้องมีระบบรองรับและยืนยันนิยามค้าง
- Test data: 10ออเดอร์จำลองรายการละm01หนึ่งจาน; เวลาลูกค้ายืนยัน12:00ถึง12:09ห่างใบละ1นาที; ปล่อยค้างทุกใบ ไม่กดสถานะ (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: มีkitchen-queue/kitchen-orderในmockแต่ไม่มีdata-testidcounter/คำเตือนอายุและฟังก์ชันสีแดงตามUS-18; MISSING selectorระบบจริง; ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. เมื่อมีระบบ สร้าง10ใบและบันทึกเวลาลูกค้ากดยืนยัน
  2. เปิดจอครัวอ่านตัวนับ
  3. ตรวจตอน12:25ซึ่งทุกใบค้าง16–25นาที
  4. ผู้ตรวจดูสีแดงรายใบและตรวจว่าระบุใบค้างนานสุดได้จากข้อมูลที่แสดง
- Expected result: ตัวนับแสดง10ออเดอร์ค้างในfixtureนี้; ออเดอร์เกิน15นาทีเปลี่ยนสีแดงอย่างน้อย9จาก10; ใบ12:00ค้างนานสุดตามข้อความUS แต่รูปแบบการเน้น/จัดวางยังไม่มีข้อมูล; จุดเริ่มไม่ใช้เวลาได้รับบนserverแทนเวลากดยืนยัน
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: ตัวนับออเดอร์ค้าง; เกิน 15 นาทีจากเวลาลูกค้ากดยืนยันสั่งเปลี่ยนสีแดง; ทดสอบ 10 ออเดอร์ที่ปล่อยเกินเวลา อย่างน้อย 9 จาก 10; ไม่เพิ่ม SLA รอบ refresh; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: BLOCKED FR/Flow/Screen/UI; นิยามค้าง ผลpending/returnedและการบอกค้างนานสุดรอยืนยัน; ไม่ยืมcapacity counterของUS-21
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-18-2"></a>

## TS-US-18-2 — ขอบก่อน/เท่ากับ/เกิน15นาที

- US: US-18
- เจ้าของ: kitchen-front
- ประเภท: ข้อยกเว้น
- AC ต้นฉบับเต็ม: จอครัวแสดงตัวนับออเดอร์ค้าง และออเดอร์ที่ค้างเกิน 15 นาที (นับจากเวลาลูกค้ากดยืนยันสั่ง) เปลี่ยนเป็นสีแดง ทดสอบ 10 ออเดอร์ที่ปล่อยเกินเวลา ผ่านอย่างน้อย 9 จาก 10
- clause ที่ตรวจ: F18-b: คำว่าเกิน15นาที ไม่ใช่ตั้งแต่15นาที
- FR / Flow / Screen: MISSING — ไม่มี FR/NFR ของ US-18 ใน v2 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MISSING — ไม่มี Flow ของ US-18 ใน v2 → MISSING — ไม่มี Screen/counter/สีเตือนค้างของ US-18 ใน UI v2 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: ต้องมีฟีเจอร์และเวลาเหตุการณ์จริง; กรณีนี้แยกboundaryเพิ่มจากชุด10ใบไม่ลดจำนวนAC
- Precondition/reset: ระบบทดสอบที่ควบคุมเวลาเหตุการณ์ระดับวินาทีได้; ไม่มีในUIv2; หนึ่งออเดอร์ยังค้าง
- Test data: ออเดอร์จำลองยืนยัน12:00:00; ตรวจ12:14:59,12:15:00,12:15:01 (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: MISSING: counter/age/สีเตือนและตัวควบคุมวินาที; kitchen-orderหรือปุ่มเพิ่ม10นาทีใช้แทนboundaryระดับวินาทีไม่ได้; ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. บันทึกเวลากดยืนยันเดิม
  2. ตรวจอายุและการเตือนที่ทั้ง3จุดตามลำดับ
  3. เก็บภาพสีและค่าเวลาทุกจุด
- Expected result: 14:59และ15:00ยังไม่เข้าเงื่อนไขเกิน15นาที; 15:01เข้าเงื่อนไขและต้องมีการเปลี่ยนสีแดงตามAC; รูปแบบสีปกติ/รอบrefreshและความละเอียดเวลาที่ระบบใช้ยังรอยืนยัน ไม่เพิ่มSLAแจ้งภายใน1วินาที
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: ตัวนับออเดอร์ค้าง; เกิน 15 นาทีจากเวลาลูกค้ากดยืนยันสั่งเปลี่ยนสีแดง; ทดสอบ 10 ออเดอร์ที่ปล่อยเกินเวลา อย่างน้อย 9 จาก 10; ไม่เพิ่ม SLA รอบ refresh; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: BLOCKED UIและวิธีวัด; ขอข้อกำหนดrefresh/ความละเอียดเวลาเพื่อกำหนดเวลาที่สังเกต โดยไม่เปลี่ยนเกณฑ์เกิน15นาที
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-18-3"></a>

## TS-US-18-3 — การนับค้างเมื่อรายการรอลูกค้าหรือคืนทั้งหมด

- US: US-18
- เจ้าของ: kitchen-front
- ประเภท: ผิดพลาด
- AC ต้นฉบับเต็ม: จอครัวแสดงตัวนับออเดอร์ค้าง และออเดอร์ที่ค้างเกิน 15 นาที (นับจากเวลาลูกค้ากดยืนยันสั่ง) เปลี่ยนเป็นสีแดง ทดสอบ 10 ออเดอร์ที่ปล่อยเกินเวลา ผ่านอย่างน้อย 9 จาก 10
- clause ที่ตรวจ: ข้อค้างนิยามออเดอร์ค้างและค้างนานสุดของF18-a/US
- FR / Flow / Screen: MISSING — ไม่มี FR/NFR ของ US-18 ใน v2 ใน [fr-nfr-v2.md](../step-00-input/fr-nfr-v2.md); MISSING — ไม่มี Flow ของ US-18 ใน v2 → MISSING — ไม่มี Screen/counter/สีเตือนค้างของ US-18 ใน UI v2 ใน [flow-v2.md](../step-00-input/flow-v2.md) หัวข้อ Coverage US → FR/NFR → Flow → module → screen
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: ไม่มีUIcounterและกฎaggregateที่ยืนยัน ต้องมีระบบและคำตอบก่อน
- Precondition/reset: ระบบที่มีcounterUS-18และคำตอบเรื่องสถานะ; เตรียมออเดอร์ค้าง3ใบ
- Test data: ใบAรับออเดอร์; ใบBมีรายการรอลูกค้าตัดสินใจ; ใบCคืนทุกรายการ; เวลายืนยัน12:00,12:01,12:02 (ข้อมูลจำลองเท่านั้น; seed/สัญญา UI หรือชุดออกแบบที่ระบุ ไม่ใช่กฎร้าน)
- data-testid และ scope: MISSING: counter/oldest indicatorUS-18; item-stateของUS-14ใช้เป็นข้อมูลsetupเท่านั้น; ขยายคำย่อตามส่วน Precondition และ SCOPE
- ขั้นตอน:
  1. เตรียมสถานะจำลองผ่านครัว/ลูกค้า
  2. อ่านตัวนับและใบค้างนานสุดก่อนและหลังคืน
  3. บันทึกสถานะระดับitem/orderคู่กับอายุ
  4. เทียบกับนิยามที่ผู้รับผิดชอบยืนยัน
- Expected result: BLOCKED/ไม่มีข้อมูลว่ารายการpending/คืนหมดต้องถูกนับเป็นออเดอร์ค้างหรือไม่และผลต่อค้างนานสุด; ไม่อนุมานว่าเสร็จแล้ว=พร้อมเสิร์ฟ หรือคืนหมด=ยกเลิก
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: ตัวนับออเดอร์ค้าง; เกิน 15 นาทีจากเวลาลูกค้ากดยืนยันสั่งเปลี่ยนสีแดง; ทดสอบ 10 ออเดอร์ที่ปล่อยเกินเวลา อย่างน้อย 9 จาก 10; ไม่เพิ่ม SLA รอบ refresh; scenario นี้ตรวจเฉพาะ clause ที่ระบุ ส่วนที่เหลือเชื่อมในดัชนี ไม่ใช้จำนวน smoke ลดเกณฑ์ต้นฉบับ
- สมมติฐาน/ข้อค้าง: DI-07/A-05,Q-V2-STATE; ไม่ใช้จำนวนออเดอร์ทั้งหมดในkitchen-queueเป็นค้างโดยอัตโนมัติ
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

## ข้อบกพร่องจาก Input / source และข้อค้างส่งต่อ

ข้อค้นพบต่อไปนี้มาจากการอ่านไฟล์ ไม่ใช่ runtime failure ของรอบนี้ ผู้รับข้อค้างธุรกิจคือผู้รับผิดชอบข้อกำหนดร่วมกับเจ้าของ US; ผู้รับข้อค้าง UI/ระบบคือผู้พัฒนาหรือผู้จัดสภาพทดสอบ ไม่มีการส่งข้อความถึงบุคคลอื่นในขั้นนี้

| ประเด็น / US | หลักฐานและผลต่อ scenario | สถานะ / สิ่งที่ต้องได้ก่อนปิด |
|---|---|---|
| US-10 | FR-10/NFR-06 และ Q-10; mock ใช้เวลาหนึ่งแท็บ ไม่มี server concurrency; TS-US-10-3/4/5 | BLOCKED ระบบ LAN, มือถือ2เครื่อง, log และคำตอบขอบเขตเลข/คำสั่งซ้ำ; คง30จาก30×3รอบ |
| US-11 | Q-05/Q-11 และ DI-07; ไม่มี testid สถานะอาหารเฉพาะแต่มีข้อความใน F(o); TS-US-11-1–4 | oracle mock มีสำหรับสอง transition; ระบบจริง/5วินาทีและกดซ้ำ/ย้อนยัง BLOCKED; ต้องยืนยัน transition โดยไม่ใช้สถานะเงินแทน |
| US-12/13 | หมายเหตุ ค. ไม่มีนิยาม; Q-12/Q-13 วัตถุดิบซ้อน/แมปเปลี่ยน; US-12 ช่อง “เพื่อ” ใน snapshot ถูกปิดแต่ source มีต้นฉบับ | ใช้ข้อความ source เต็มในเอกสาร; ผล whole/option ปกติออกแบบได้; ผลซ้อน/เปิดคืนและหมายเหตุ BLOCKED รอคำตอบ |
| US-14 | Q-V2-STATE/REFUND; รายการ pending เป็นคนละระดับกับorder/payment; TS-US-14-5/6 | ต้องมีLAN/5กรณีและกฎซ้ำ/ชน; ห้ามถือคืนหมดเป็นปิดโต๊ะหรือคืนเงินจริง; ราคาหรือส่วนต่างที่ใช้จำลองไม่ใช่นโยบายอนุมัติ |
| US-15 | Q-15; audit logในHTMLเป็นข้อความในหน่วยความจำ; timezoneร้านไม่มีข้อมูล; TS-US-15-5/6/7 | boundaryจำลองใช้+07:00ที่ระบุ แต่วันจริง/20ใบ/logผู้ใช้เวลายังBLOCKED; ห้ามแทนชื่อพนักงานจริงในfixture |
| US-16 | UIมีปุ่มเปิดโต๊ะแต่ไม่มีdata-testidเฉพาะ; seedมี3โต๊ะ; Q-16; TS-US-16-1–4 | manualตรวจปุ่มและหน้ารอบใหม่ได้; sessionฝั่งserver/QR/5โต๊ะและนโยบายค้างทำ/ค้างจ่ายยังBLOCKED |
| US-17 | ไม่มีFR/Flow/Screen/รวมบิลในsnapshotv2; front-totalเป็นยอดแต่ละออเดอร์; TS-US-17-1/2 | MISSING mapping/implementation; ต้องรองรับ3รอบและเครื่องคิดเลข9จาก10โต๊ะ; คำตอบรอบที่ยังไม่ยืนยัน/รวมซ้ำยังBLOCKED |
| US-18 | ไม่มีFR/Flow/Screen/counter/สีแดงตามอายุในsnapshotv2; TS-US-18-1–3 | MISSING mapping/implementation; ต้องมี10ใบเกิน15นาทีและนิยามค้าง/ค้างนานสุด/ความละเอียดเวลา; ไม่ใช้capacityหรือจำนวนใบทั้งหมดแทน |
| Selectorสัญญาv2ไม่ตรงHTML | input-check และHTML: rush-start→capacity-start; rush-end→capacity-end; payment-summary-totalไม่มีชื่อเดิม | ยังไม่แก้Input; TS-US-09-101ติดความเข้ากันได้ก่อนรัน ส่วนscenarioออกแบบนี้ใช้ชื่อที่พบจริงพร้อมขอบเขตยอด |
| US-20 อ้าง US-14 | DI-04/A-03 และQ-20; การเปิดFR-14ในv2ไม่ได้แก้การอ้างกฎปิด/เปิดในUS-20 | OPEN: คงรหัสUS-14ของต้นฉบับ การเสนอเชื่อมUS-12/13ยังไม่ยืนยัน; ไม่เพิ่มscenarioเจ้าของผู้จัดการในไฟล์นี้ |
| หมายเหตุ ก./ช. และบริบทข้ามบทบาท | DI-01/03; การจ่าย/ETAใช้setupหรือผลต่อเนื่อง แต่ไม่มีนิยามหมายเหตุ | OPEN: รอเนื้อหาต้นฉบับ ไม่แต่งรายละเอียด; สูตรUS-07และช่วง11:30–13:00/17:30–19:30ไม่ถูกแทนด้วยค่าcapacity11:30–13:30หรือXจำลอง |
| ขอบเขตหลักฐานระบบจริง | DI-09 และ A-01–A-06 ยังไม่ยืนยัน; seedหนึ่งแท็บไม่มีระบบเครือข่าย/การเก็บถาวร | BLOCKED การรับรองLAN, Security, Load, Availability และเงินจริง; การคลิกmockในอนาคตก็ไม่ปิดข้อเหล่านี้ |

ชื่อ F/N แบบ clause ในเอกสารนี้ไม่ใช่รหัส FR/NFR ที่เพิ่มขึ้น ส่วน MRG/SCR ที่อ้างใช้เฉพาะทะเบียนใน flow-v2.md; รายละเอียด baseline ที่อยู่นอก Input ไม่ถูกแต่งเติมเพื่ออ้างผลทดสอบ US-17/18 ยังคง MISSING ไม่สร้าง FR-17/FR-18 หรือ Screen แทน

## ผลตรวจเอกสารต้นทางก่อนแก้และสิ่งที่ยังไม่ได้ทดสอบ

- แบบออกแบบใหม่ 40 TestID ไม่ซ้ำ ใช้ n=1–7 ภายในแต่ละ US และไม่มีนิยาม scenario ใหม่ในช่วง n>=101
- ครอบคลุมการออกแบบ US-10–US-18 ทั้ง9US มีสำเร็จอย่างน้อย1และผิดพลาด/ข้อยกเว้นอย่างน้อย1ต่อUS; บางกรณีรอoracle/mappingตามทะเบียน จึงยังเป็น GAPS
- คัด US ต้นฉบับ9แถวและ AC เต็มต่อscenarioเทียบกับcase-study-source.md; functional/NFR, sample count, จุดเวลาและทางเลือกมีการเชื่อมดัชนี; ไม่ลดเกณฑ์เพื่อให้พอดีseed
- automation: auto19 / manual1 / mock-not-testable20; Status: NOT_RUN20 / NOT_TESTABLE20; Actual resultและหลักฐาน “ไม่มีข้อมูล” ทั้ง40
- **ยังไม่ทดสอบ:** browser/DOM runtime/visibility/selector uniqueness/click/สี/responsive, fixture smokeทั้งหมด, จำนวนตัวอย่างและสัดส่วนจริง, QR, LAN/Wi-Fi/หลายอุปกรณ์/concurrency/Load, server timestamps/log/session isolation/Security, Availability/Ubuntu/ตัดอินเทอร์เน็ต, ETA/ข้อมูล7วัน และการรับเงิน/ตรวจสลิป/โอนหรือคืนเงินจริง
- เกณฑ์หยุดของรอบออกแบบนี้: ส่งต่อเอกสารพร้อมข้อค้างที่ระบุได้ ไม่สร้างผลผ่านจากsourceหรือแทนข้อมูลที่ขาดด้วยการเดา การรันและบันทึกผลในอนาคตต้องใช้pathรุ่นใหม่พร้อมคงTestIDเดิม ไม่เขียนทับหลักฐานไฟล์นี้

Output ของขั้น fanout เดิมมีเฉพาะ [scenarios-kitchen-front.md](../step-01-fanout/kitchen-front/scenarios-kitchen-front.md) ไม่มีไฟล์ผลรัน log screenshot หรือผลแก้Inputจากขั้นนี้



---

## ต้นฉบับฉบับเต็ม — manager

Source: [scenarios-manager-round-1.md](../step-02-coverage/fix-1/scenarios-manager-round-1.md). คัดทั้งไฟล์; ปรับเฉพาะฐาน path/ลิงก์และเพิ่มจุดนำทางก่อนหัวข้อ.

# Scenario บทบาทผู้จัดการร้าน — US-19 ถึง US-26

## บันทึกรอบแก้ coverage — ROUND 1

คัดส่วนเดิมจาก [scenarios-manager.md](../step-01-fanout/manager/scenarios-manager.md) แล้วเพิ่มเฉพาะ TS-US-22-4, TS-US-24-3 ตาม D06, D07; รวม 37 TestID. นิยามเดิม 35 รายการคงข้อความทุกบล็อก; ปรับเฉพาะดัชนี/ข้อมูลรุ่น/ฐาน path ที่จำเป็นนอกบล็อก. รายการใหม่ทั้งหมดใช้ mock-not-testable และ Status MOCK_NOT_TESTABLE ตาม template; Status NOT_TESTABLE ในรายการเดิมเก็บตามต้นทาง. ข้อความจำนวนและสถานะในหัวข้อบันทึกต้นทางเป็นข้อมูลก่อนแก้

manifest ต้นทาง: [scenario-set-round-0.json](../step-00-input/scenario-set-round-0.json) resolve ค่าจากโฟลเดอร์ manifest; manifest รอบนี้: [scenario-set-round-1.json](../step-02-coverage/fix-1/scenario-set-round-1.json) resolve ทุกค่าจากราก LAB ../.. ตาม P01. รายละเอียดการแก้และ regression อยู่ที่ [coverage-fixes-round-1.md](../step-02-coverage/fix-1/coverage-fixes-round-1.md). ส่งผู้ตรวจรอบเดียวกัน ยังไม่ประกาศ COVERED; Actual/หลักฐานไม่มีข้อมูล


ต้นทางก่อนแก้ออกแบบจาก Input ใช้ข้อมูลจำลองเท่านั้น มี Scenario 35 รายการ: auto 15, manual 4, mock-not-testable 16 รายการ ไม่มีการรัน browser หรือระบบจริง สถานะการออกแบบ **GAPS** เพราะ FR/Flow/หน้าจอบาง US และคำตอบธุรกิจยังขาด ไม่ใช่การรับรอง coverage สมบูรณ์หรือผลทดสอบผ่าน

เจ้าของทุก TestID เชิงออกแบบในไฟล์นี้คือ manager การทำขั้นตอนลูกค้า/ครัว/หน้าร้านใช้ setup และตรวจผลของ US ผู้จัดการ ไม่เปลี่ยนเจ้าของ US

ใช้ Status เริ่มต้น NOT_RUN สำหรับ auto/manual และ NOT_TESTABLE สำหรับ mock-not-testable ตาม prompt รอบนี้ ซึ่งเจาะจงกว่า enum MANUAL_PENDING/MOCK_NOT_TESTABLE ใน template; ค่า automation ยังคงตาม template ทุกกรณี Actual result/หลักฐาน = ไม่มีข้อมูล ไม่ยกผลเก่ามาเป็นผลรันใหม่

## Input และฐาน path

path ทั้งหมดในเอกสารนี้ relative จากโฟลเดอร์ขั้นนี้ ยกเว้นข้อความที่ระบุว่า “จากราก LAB” ซึ่งมีฐานอยู่ที่ ../.. ไม่เขียนหรือแก้ manifest รอบนี้

- [US/AC ต้นฉบับ](../../../docs/case-study-source.md)
- [ปัญหาข้อมูลและสมมติฐาน](../../../docs/data-issues.md)
- [ผลตรวจ Input](../step-00-input/input-check.md)
- [FR/NFR v2](../step-00-input/fr-nfr-v2.md)
- [Flow v2](../step-00-input/flow-v2.md)
- [HTML v2 ที่อ่านโค้ด](../step-00-input/ui-mockup-v2.html)
- [แม่แบบ Scenario](../../input/scenario-template.md)
- [เกณฑ์ Coverage](../../input/coverage-criteria.md)
- [Fixture JSON](../../input/ui-scenarios.json)
- [สัญญา fixture เพิ่ม v2](../../input/ui-v2-test-contract.md)
- [สัญญา UI เดิม](../../../004_LAB_Conditional_Graph_UI_Mockup/input/ui-contract.md)
- [Snapshot สัญญา UI v2](../step-00-input/ui-contract-v2.md)
- [Snapshot แนวทดสอบ v2](../step-00-input/test-outline-v2.md)

คัด US/AC จาก case-study-source.md เป็นฐานก่อนแตก clause; FR/Flow ใช้เชื่อมเฉพาะรหัสที่พบจริง HTML และสัญญา UI ใช้ระบุวิธีทดสอบ ไม่ใช้สร้างข้อกำหนดร้านจากสิ่งที่หน้าจอทำได้

## US และ AC ต้นฉบับครบก่อนแยก assertions

ตารางต่อไปนี้คัดทั้งแถวตรงตัว ไม่แก้ข้อความ “US-14” ใน US-20 ไม่เติมนิยามหมายเหตุ ค. และไม่แทน AC ด้วยข้อความย่อจาก FR

| ID | บทบาท | ในฐานะ | ฉันต้องการ | เพื่อ | เกณฑ์รับ |
|---|---|---|---|---|---|
| US-19 | ผู้จัดการร้าน | ผู้จัดการร้าน | เพิ่ม/แก้/ลบเมนู ราคา รูปเมนู และตัวเลือกเพิ่มต่อเมนู (ชื่อ ราคาเพิ่ม) ผ่านหน้า “จัดการเมนู” | ปรับเมนูตามฤดูกาลและต้นทุนโดยไม่ต้องจ้างคนแก้ระบบ | ขอบเขต: หน้า “จัดการเมนู” เท่านั้น ไม่มีการแมปวัตถุดิบ (แยกไป US-20) · รูปเมนูรับไฟล์ jpg/png ขนาดไม่เกิน 2 MB ต่อรูป · ตัวเลือกเพิ่มระบุชื่อและราคาเพิ่มได้ 0–10 ตัวเลือกต่อเมนู · นับจากกดบันทึก จนถึงเมนูและตัวเลือกเพิ่มใหม่ปรากฏบนหน้าลูกค้าเมื่อรีเฟรช ภายใน 1 นาที · การแก้ราคาไม่เปลี่ยนยอดของออเดอร์ที่สั่งไปแล้ว (ตรวจ 5 ออเดอร์เดิม ผ่าน 5 จาก 5) · ลบเมนูที่มีการแมปวัตถุดิบอยู่ ระบบต้องเตือนและลบการแมปนั้นด้วย |
| US-20 | ผู้จัดการร้าน | ผู้จัดการร้าน | แมปวัตถุดิบกับเมนูและตัวเลือกเพิ่มที่มีอยู่แล้ว ผ่านหน้า “แมปวัตถุดิบ” | ให้ระบบปิดเมนูอัตโนมัติถูกต้องเมื่อวัตถุดิบหมด | ขอบเขต: หน้า “แมปวัตถุดิบ” เท่านั้น ไม่มีการเพิ่ม/แก้เมนูหรือราคา · dependency: เลือกได้เฉพาะเมนูและตัวเลือกเพิ่มที่ถูกสร้างไว้แล้วใน US-19 (ต้องมีเมนูก่อนจึงแมปวัตถุดิบได้ และเมนูที่ยังไม่มีในระบบไม่ปรากฏให้เลือก) · ระบุต่อเมนูว่าใช้วัตถุดิบใด “ทั้งจาน” และต่อตัวเลือกเพิ่มว่าใช้วัตถุดิบใด “เฉพาะตัวเลือก” · บันทึกแล้วมีผลกับกฎปิด/เปิดเมนูอัตโนมัติ (US-14) และแสดงบนหน้าลูกค้าเมื่อรีเฟรชภายใน 1 นาที ทดสอบ 5 เมนู ผ่าน 5 จาก 5 (ดูหมายเหตุ ค.) |
| US-21 | ผู้จัดการร้าน | ผู้จัดการร้าน | ตั้งช่วงเวลาเร่งด่วนและเพดานจำนวนออเดอร์ต่อ 15 นาที | ครัวไม่ล้นและลูกค้าในร้านได้อาหารทัน | ตั้งเวลาเริ่ม–สิ้นสุดช่วงเร่งด่วน (เช่น 11:30–13:30) และเพดาน N ออเดอร์ต่อหน้าต่างเวลา 15 นาทีที่นับจากนาทีที่ 00/15/30/45 เมื่อจำนวนออเดอร์ที่ยืนยันในหน้าต่างนั้นถึง N ลูกค้าใหม่เห็นข้อความ “ครัวเต็ม รอประมาณ X นาที” ก่อนยืนยัน ทดสอบด้วย N=5 ผ่าน 3 จาก 3 รอบ |
| US-22 | ผู้จัดการร้าน | ผู้จัดการร้าน | เปิด/ปิดรับสั่งกลับบ้านชั่วคราวด้วยสวิตช์เดียว | ลดภาระครัวช่วงเร่งด่วนโดยไม่ปิดหน้าร้าน | นับจากผู้จัดการกดปิดรับสั่งกลับบ้าน จนถึงหน้าลูกค้าซ่อนโหมด “สั่งกลับบ้าน” เมื่อโหลดหน้าใหม่ ภายใน 10 วินาทีบน LAN ในร้าน ในอย่างน้อย 9 จาก 10 ครั้ง และการสั่งหน้าร้านผ่าน QR ยังทำได้ตามปกติ |
| US-23 | ผู้จัดการร้าน | ผู้จัดการร้าน | ดูรายงานยอดขายรายวัน แยกตามเมนู ช่องทาง (หน้าร้าน/สั่งกลับบ้าน) และช่วงเวลา พร้อมส่งออก CSV | วางแผนสั่งวัตถุดิบและกำลังคน | เลือกช่วงวันที่แล้วรายงานแสดงภายใน 5 วินาที (นับจากกด “ดูรายงาน” จนตารางแสดงบนเครื่อง Ubuntu ในร้าน) ยอดรวมตรงกับผลรวมออเดอร์สถานะ “จ่ายแล้ว” ที่นับมือจาก 20 ใบของชุดทดสอบ (คลาดเคลื่อน 0 บาท) และดาวน์โหลด CSV เปิดด้วย LibreOffice ได้ |
| US-24 | ผู้จัดการร้าน | ผู้จัดการร้าน | ดูประวัติวัตถุดิบ/เมนูที่ถูกกดหมดพร้อมเวลาและความถี่ | รู้ว่าวัตถุดิบไหนควรสั่งเพิ่มหรือปรับเมนู | เมื่อครัวกด “วัตถุดิบหมด” ระบบบันทึกชื่อวัตถุดิบ เวลา และผู้กด และหน้าประวัติแสดงจำนวนครั้งต่อสัปดาห์ ตรวจสอบกับการกดทดสอบ 10 ครั้ง พบรายการอย่างน้อย 9 จาก 10 |
| US-25 | ผู้จัดการร้าน | ผู้จัดการร้าน | จัดการบัญชีพนักงานและสิทธิ์ (ครัว/หน้าร้าน/ผู้จัดการ) ด้วยชื่อผู้ใช้และ PIN โดยไม่ต้องใช้อีเมล | ข้อมูลยอดขายและการแก้เมนูเข้าถึงได้เฉพาะคนที่ควร | สร้างบัญชีด้วยชื่อผู้ใช้ (ตัวอักษร/ตัวเลข 3–20 ตัว) และ PIN ตัวเลข 4–6 หลัก เข้าสู่ระบบด้วยชื่อผู้ใช้+PIN ใส่ PIN ผิด 5 ครั้งติดถูกล็อก 5 นาที และบัญชีสิทธิ์ครัว/หน้าร้านเปิด URL หน้ารายงานและหน้าจัดการเมนูแล้วถูกปฏิเสธ ทดสอบ 3 บัญชี × 2 หน้า ผ่าน 6 จาก 6 |
| US-26 | ผู้จัดการร้าน | ผู้จัดการร้านที่งบต่ำ | ติดตั้งระบบบนเครื่อง Ubuntu เครื่องเดียวในร้าน ใช้งานผ่าน Wi‑Fi ร้านได้แม้เน็ตภายนอกหลุด | ไม่ต้องจ่ายค่าคลาวด์รายเดือนและร้านไม่หยุดเมื่อเน็ตล่ม | ติดตั้งบน Ubuntu ด้วยสคริปต์เดียว เสร็จภายใน 30 นาที (นับจากรันสคริปต์จนเปิดหน้าเมนูจากมือถือในร้านได้) เก็บข้อมูลบนเครื่องในร้าน และเมื่อถอดสายอินเทอร์เน็ตภายนอก ยังสั่ง/เปลี่ยนสถานะ/ปิดโต๊ะได้ครบ 20 ใบของชุดทดสอบ (ยกเว้นการตรวจสอบยอดโอน PromptPay ซึ่งพนักงานยืนยันด้วยตา) |

## ข้อตกลงการเตรียมและ scope

ทุก shorthand ต่อไปนี้หมายถึงขั้นตอนที่ต้องทำจริงในการรันภายหลัง ไม่ถือว่าได้ทำแล้วในรอบออกแบบนี้

- R0: เปิด HTML v2 ใน browser context ใหม่ กด btn-reset ตรวจ sim-clock = 2026-01-01T12:00:00+07:00, role-customer, โต๊ะ 01, dine-in, คิวและตะกร้าว่าง, stock มี, บัญชี/เมนู/แมปคืน seed; ไม่มี m09 จนบันทึกเมนูใหม่สำเร็จ ห้าม reset กลางกรณีที่ต้องเก็บข้อมูลก่อน–หลัง
- M: กด role-manager เลือก demomanager ใน staff-user กรอก staff-pin=0000 กด btn-login แล้วเปิด nav ของงานที่ระบุ
- K: กด role-staff เลือก demokitchen/PIN0000 กด btn-login และ nav-kitchen
- F: กด role-staff เลือก demofront/PIN0000 กด btn-login และ nav-front
- C: กด role-customer เลือก table-select=01, order-mode=dine-in และ btn-open-menu เว้นแต่กรณีระบุโต๊ะอื่น; จาน m01=50 และ extra-egg=10 เป็นราคา seed จำลอง
- เปลี่ยนบทบาทต้อง login ใหม่ แต่ state ออเดอร์/เมนูในแท็บยังอยู่ การ reload HTML เรียก reset และล้าง state จึงไม่แทนการรีเฟรชระบบจริงเพื่อวัดเกณฑ์ 1 นาที
- ใช้ selectOption สำหรับ select เช่น staff-user, table-select, mapping-menu และ account-role; fill สำหรับช่องกรอก ไม่คัด action fill ใน JSON มาใช้กับ select โดยไม่ดูชนิด element
- ทุกครั้งที่ส่งออเดอร์ให้บันทึก order-id ที่แสดงจริง แล้วเลือกใบตาม ID ห้ามเลือก first/nth แทนตัวตนออเดอร์ เมื่อสร้างหลายใบให้จับคู่ ID กับข้อมูลอ้างอิงก่อนตรวจ
- รูป/CSV/อุปกรณ์/ระบบจริงที่ระบุเป็นข้อมูลเตรียมสำหรับการรันในอนาคต รอบนี้ไม่สร้างไฟล์ fixture หรือหลักฐานเพิ่ม ชื่อบัญชี demo และชื่อสังเคราะห์ในกรณีเป็นข้อมูลทดสอบ ไม่ใช่บัญชีจริง

| ชุดอ้างอิง selector | data-testid ที่พบจริงและ scope |
|---|---|
| S-L | ส่วนกลาง role-customer, role-staff, role-manager, btn-reset, sim-clock, btn-advance-10m, auth-message; form#login-form: staff-user, staff-pin, btn-login; selector login ใช้เมื่อแบบฟอร์มปรากฏเท่านั้น |
| S-M | screen-manager > menu-admin: admin-menu-select, admin-menu-name, admin-menu-price, admin-menu-image, admin-option-name, admin-option-price, btn-save-menu, btn-delete-menu, admin-message; nav-menu-admin อยู่นอก menu-admin ใน screen-manager |
| S-P | screen-manager หน้า nav-mapping: mapping-menu, mapping-scope, mapping-option, mapping-ingredient, btn-save-mapping, mapping-list; section ที่มี mapping-menu ไม่มี data-testid section โดยเฉพาะ |
| S-U | screen-manager หน้า nav-accounts: account-username, account-pin, account-role, btn-save-account, account-message; ไม่มีฟีเจอร์แก้/ลบบัญชีใน source ที่อ่าน |
| S-A | screen-manager > capacity-settings หลัง nav-capacity: capacity-start, capacity-end, capacity-limit, capacity-wait-minutes, btn-save-capacity, capacity-setting-message, capacity-window; capacity-message อยู่ screen-customer ก่อน btn-submit-order |
| S-C | screen-customer: table-select, order-mode, pickup-slot, btn-open-menu, menu-list, menu-item-m01/m02; menu-item-m09 และ menu-item-<id> เกิดหลังสร้าง; section รายละเอียดจานที่เลือกมี option-extra-egg หรือ option-<id>, item-total, btn-add-item; cart-count, cart-total, btn-submit-order, order-message, order-id, customer-order-status, payment-status |
| S-K | screen-staff (หรือ screen-manager เมื่อใช้ผู้จัดการเข้าครัว): nav-kitchen, ingredient-select, ingredient-status, btn-out-of-stock, btn-restock; kitchen-queue > kitchen-order[data-order-id="<ID>"] > btn-status-next; btn-item-unavailable เพิ่ม scope data-item-id หากมีหลายจาน |
| S-F | screen-staff หน้า nav-front: front-orders > front-order[data-order-id="<ID>"] แล้วจึงเลือก front-total, front-adjusted-total, front-payment-status, btn-receive-cash, btn-confirm-slip; front-table-select/btn-close-table ใช้โต๊ะที่ระบุและ session ที่กำลังเปิด; payment-log เป็น log เงิน ไม่ใช่ประวัติ stock |

เครื่องหมาย / ในชื่อย่อ เช่น admin-menu-select/name/price หมายถึงชื่อเต็มใน S-M ไม่ใช่ selector literal ตัวเดียว ชื่อ dynamic อ่าน ID จากเมนู/ตัวเลือกที่บันทึกจริงก่อนใช้ หลักฐาน selector เป็นเพียง static source ไม่รับรอง visibility/uniqueness/runtime

selector ที่ไม่มี data-testid ใช้เฉพาะ CSS/attribute ที่พบจริงใน HTML:369 (ตัวเลือก/รูป), HTML:18 (ปุ่มเวลา) หรือ browser dialog event ไม่สร้างชื่อ data-testid ใหม่ หาก DOM ไม่ตรงให้เก็บข้อบกพร่องในการรันรุ่นใหม่

## ดัชนี US → TestID และประเภท

ตาราง 26 แถวเพื่อส่งต่อผู้ตรวจรวม แต่รับผิดชอบออกแบบเฉพาะ US-19–26 แถวบทบาทอื่นระบุ OUT_OF_SCOPE ไม่ใช่การยืนยันว่ามีหรือขาด coverage ของผู้อื่น ช่อง N/A ในขอบเขตนี้หมายถึงไม่มีทางเลือก/ประเภทนั้นเพิ่มเติมตามข้อความ AC; ทุก US ในขอบเขตมีสำเร็จและผิดพลาดหรือข้อยกเว้นอย่างน้อยหนึ่งรายการ

| US | เจ้าของ | สำเร็จ | ทางเลือก | ผิดพลาด | ข้อยกเว้น | Fixture อ้างเชื่อม (ไม่ใช่รายการออกแบบใหม่) |
|---|---|---|---|---|---|---|
| US-01 | customer | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | ไม่ตรวจในไฟล์นี้ |
| US-02 | customer | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | ไม่ตรวจในไฟล์นี้ |
| US-03 | customer | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | ไม่ตรวจในไฟล์นี้ |
| US-04 | customer | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | ไม่ตรวจในไฟล์นี้ |
| US-05 | customer | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | ไม่ตรวจในไฟล์นี้ |
| US-06 | customer | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | ไม่ตรวจในไฟล์นี้ |
| US-07 | customer | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | ไม่ตรวจในไฟล์นี้ |
| US-08 | customer | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | ไม่ตรวจในไฟล์นี้ |
| US-09 | customer | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | ไม่ตรวจในไฟล์นี้ |
| US-10 | kitchen-front | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | ไม่ตรวจในไฟล์นี้ |
| US-11 | kitchen-front | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | ไม่ตรวจในไฟล์นี้ |
| US-12 | kitchen-front | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | ไม่ตรวจในไฟล์นี้ |
| US-13 | kitchen-front | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | ไม่ตรวจในไฟล์นี้ |
| US-14 | kitchen-front | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | ไม่ตรวจในไฟล์นี้ |
| US-15 | kitchen-front | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | ไม่ตรวจในไฟล์นี้ |
| US-16 | kitchen-front | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | ไม่ตรวจในไฟล์นี้ |
| US-17 | kitchen-front | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | ไม่ตรวจในไฟล์นี้ |
| US-18 | kitchen-front | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | ไม่ตรวจในไฟล์นี้ |
| US-19 | manager | TS-US-19-1, TS-US-19-2, TS-US-19-6, TS-US-19-8 | TS-US-19-4 | TS-US-19-3, TS-US-19-5 | TS-US-19-7 | ไม่มี fixture ของ US นี้ใน JSON |
| US-20 | manager | TS-US-20-1, TS-US-20-4 | TS-US-20-2 | TS-US-20-3 | N/A — ไม่มีกรณีประเภทนี้เพิ่มตาม AC | ไม่มี fixture ของ US นี้ใน JSON |
| US-21 | manager | TS-US-21-1, TS-US-21-6 | TS-US-21-3 | TS-US-21-5 | TS-US-21-2, TS-US-21-4 | TS-US-21-101 |
| US-22 | manager | TS-US-22-1 | TS-US-22-3 | N/A — ไม่มีกรณีประเภทนี้เพิ่มตาม AC | TS-US-22-2 (oracle เดิมยัง BLOCKED), TS-US-22-4 | ไม่มี fixture ของ US นี้ใน JSON |
| US-23 | manager | TS-US-23-1 | TS-US-23-2 | TS-US-23-4 | TS-US-23-3 | ไม่มี fixture ของ US นี้ใน JSON |
| US-24 | manager | TS-US-24-1 | N/A — ไม่มีกรณีประเภทนี้เพิ่มตาม AC | N/A — ไม่มีกรณีประเภทนี้เพิ่มตาม AC | TS-US-24-2 (oracle เดิมยัง BLOCKED), TS-US-24-3 | ไม่มี fixture ของ US นี้ใน JSON |
| US-25 | manager | TS-US-25-1, TS-US-25-5 | N/A — ไม่มีกรณีประเภทนี้เพิ่มตาม AC | TS-US-25-2, TS-US-25-3 | TS-US-25-4, TS-US-25-6 | TS-US-25-101 |
| US-26 | manager | TS-US-26-1 | N/A — ไม่มีกรณีประเภทนี้เพิ่มตาม AC | N/A — ไม่มีกรณีประเภทนี้เพิ่มตาม AC | TS-US-26-2 | ไม่มี fixture ของ US นี้ใน JSON |

## การเชื่อม fixture เดิม

ID ช่วง n≥101 สงวนให้ JSON ไม่สร้าง Scenario ซ้ำ ไม่เปลี่ยน ID หลังเผยแพร่ หากรันหรือแก้เอกสารในอนาคตต้องใช้ path รุ่นใหม่เพื่อคงหลักฐาน

| Fixture ใน ../../input/ui-scenarios.json | เชื่อมแบบออกแบบ | ตรวจได้เพียง | ช่องว่างก่อนนำไปรัน / สถานะ |
|---|---|---|---|
| TS-US-21-101 | TS-US-21-1, TS-US-21-6 | เตรียม 5 ใบและดูคำเตือนก่อนยืนยันใบถัดไปในหนึ่งรอบ | JSON ขาด nav-capacity และใช้ rush-start/rush-end ซึ่งไม่มีใน v2; ชื่อจริง capacity-start/capacity-end. ต้องจัดรุ่น fixture ที่อนุมัติในขั้นถัดไป; ไม่แก้ JSON รอบนี้. NOT_RUN; BLOCKED ความเข้ากันได้ |
| TS-US-25-101 | TS-US-25-3, TS-US-25-5 | PIN ผิดหนึ่งครั้ง แสดงปฏิเสธและไม่แสดง screen-manager | ไม่ได้ตรวจผิดติด 5 ครั้ง/ล็อกครบ 5 นาที/3 บัญชี×2 หน้า และไม่พิสูจน์ server security. NOT_RUN |

fixture อื่นใน JSON เป็นบทบาทอื่น ไม่ย้ายเจ้าของมานับ manager. หากใช้ขั้นคืนรายการร่วมในอนาคต ชื่อ payment-summary-total ไม่พบใน HTML; customer-adjusted-total ใช้ได้เฉพาะออเดอร์ล่าสุด ส่วน front-total คือ snapshot เดิม ไม่ใช่ยอดหลังปรับหรือบิลรวมหลายรอบ

## แตก clause เชิงหน้าที่และ NFR

การจัดกลุ่มนี้เป็นป้ายในเอกสารออกแบบ ไม่ใช่ FR/Flow ID ใหม่ จำนวนตัวอย่างคงอยู่กับ clause ที่ต้นฉบับกำหนด

| US / clause | Functional assertions | NFR / ขอบเขตระบบจริง | TestID / ข้อค้าง |
|---|---|---|---|
| US-19 ขอบเขตและ CRUD | เพิ่ม/แก้/ลบเมนู ชื่อ ราคา รูป ตัวเลือก; ไม่มีแมปในหน้าจัดการเมนู | ไม่มี SLA แยก CRUD | TS-US-19-1/2/4/7 |
| US-19 รูป | jpg/png ไม่เกิน 2 MB ต่อรูป | หน่วย MB รอ Q-19 | TS-US-19-2/3 |
| US-19 ตัวเลือก | ชื่อ/ราคาเพิ่ม 0–10; ค่าเกินขอบไม่รับ | ไม่กำหนดนโยบายราคาเพิ่มเติม | TS-US-19-4/5 |
| US-19 เผยแพร่ | ข้อมูลใหม่ปรากฏเมื่อลูกค้ารีเฟรช | NFR-11 ภายใน 1 นาที | TS-US-19-8; auto 1/4 ไม่แทน reload |
| US-19 ราคาเดิม | แก้ราคาแล้วออเดอร์เดิมคงยอด 5 จาก 5 | mock ไม่พิสูจน์ persistence | TS-US-19-6 |
| US-19 ลบมีแมป | เตือนและลบแมปตาม | ผลออเดอร์ค้างรอ Q-19 | TS-US-19-7 |
| US-20 ขอบเขต/dependency | หน้าแมปไม่มี CRUD เมนู/ราคา; ต้องมีเมนู/ตัวเลือกก่อน; ของที่ยังไม่มีไม่แสดง | ไม่มี NFR ใหม่ | TS-US-20-1/3 |
| US-20 ประเภทแมป | ทั้งจาน/เฉพาะตัวเลือกและผลปิด/เปิด 5 เมนู 5 จาก 5 | Q-20, DI-02/04 อ้าง US-14/หมายเหตุ ค. | TS-US-20-2 |
| US-20 เผยแพร่ | ผลแมปแสดงเมื่อลูกค้ารีเฟรช | NFR-12 ภายใน 1 นาทีครบ 5 เมนู | TS-US-20-4 |
| US-21 ตั้งค่า | เริ่ม–สิ้นสุด เช่น 11:30–13:30 และ N | ไม่มี NFR เฉพาะ | TS-US-21-1/5; ผลค่าผิดรอยืนยัน |
| US-21 หน้าต่าง | 15 นาทีเริ่ม 00/15/30/45 | เขตเวลา/ขอบวินาทีรอคำตอบ | TS-US-21-3/4 |
| US-21 การนับ/เตือน | ออเดอร์ยืนยันถึง N แจ้งครัวเต็มก่อนยืนยันลูกค้าใหม่ | N=5 ผ่าน 3 จาก 3 รอบเป็น functional; X ไม่มีสูตรให้รับรอง | TS-US-21-1/2/6, TS-US-21-101; Q-V2-CAPACITY |
| US-22 สวิตช์ | ปิดรับซ่อนโหมดเมื่อโหลดใหม่; หน้าร้าน QR ยังสั่งได้; เปิดรับคืนตาม US | LAN≤10วินาที อย่างน้อย9จาก10; ทางเปิดไม่มี SLA | TS-US-22-1/3; FR/Flow/UI MISSING |
| US-22 หน้าเดิม | ผล submit เมื่อปิดรับยังไม่ระบุ | ไม่มี oracle | TS-US-22-2 |
| US-23 มิติ/ยอด | รายวัน เมนู ช่องทางหน้าร้าน/กลับบ้าน ช่วงเวลา; รวมจ่ายแล้วจาก20ใบคลาดเคลื่อน0บาท | กดดูรายงาน→ตารางบนUbuntu≤5วินาที | TS-US-23-1/3; FR/Flow/UI MISSING |
| US-23 ส่งออก | ดาวน์โหลด CSV เปิด LibreOffice ได้ | ต้องมีไฟล์จริงและคนเปิดตรวจ | TS-US-23-2 |
| US-23 ค่าผิด | ช่วงกลับด้าน/ข้อมูลว่างไม่มีผลระบุ | รอ oracle | TS-US-23-4 |
| US-24 บันทึก | ชื่อวัตถุดิบ เวลา ผู้กด; ประวัติความถี่ต่อสัปดาห์ | 10ครั้ง พบอย่างน้อย9จาก10; ไม่มี SLA เวลาใหม่ | TS-US-24-1; FR/Flow/UI MISSING |
| US-24 ข้อยกเว้น | กดซ้ำ/ขอบสัปดาห์ยังไม่ระบุ | รอ oracle | TS-US-24-2; Q-M24 |
| US-25 บัญชี/login | ชื่ออักษร/เลข3–20 PINเลข4–6 ไม่ใช้อีเมล และบทบาท | NFR-18 ต้องมีระบบจริง | TS-US-25-1/2/5/6 |
| US-25 ล็อก | ผิด5ครั้งติด ล็อก5นาที | mock clock ไม่แทนเวลาจริง | TS-US-25-3/5, TS-US-25-101 บางส่วน |
| US-25 URL | ครัว/หน้าร้าน3บัญชี×2หน้า ปฏิเสธ6จาก6 | NFR-18 ตรวจสิทธิ์/ข้อมูล server | TS-US-25-4/5 |
| US-26 ติดตั้ง/ข้อมูล | Ubuntuเครื่องเดียว สคริปต์เดียว ข้อมูลอยู่ในร้าน มือถือWi-Fiเข้าได้ | NFR-22 รันสคริปต์→มือถือเปิดเมนู≤30นาที | TS-US-26-1 |
| US-26 เน็ตภายนอกหลุด | สั่ง/สถานะ/ปิดโต๊ะ20ใบครบ; PromptPayพนักงานตรวจด้วยตา | NFR-16 ต้องถอดWANจริงโดยLANยังทำงาน | TS-US-26-2 |

## Scenario ตาม template

<a id="design-ts-us-19-1"></a>

## TS-US-19-1 — เพิ่มและแก้เมนูในขอบเขตหน้าจัดการเมนู

- US: US-19
- เจ้าของ: manager
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: ขอบเขต: หน้า “จัดการเมนู” เท่านั้น ไม่มีการแมปวัตถุดิบ (แยกไป US-20) · รูปเมนูรับไฟล์ jpg/png ขนาดไม่เกิน 2 MB ต่อรูป · ตัวเลือกเพิ่มระบุชื่อและราคาเพิ่มได้ 0–10 ตัวเลือกต่อเมนู · นับจากกดบันทึก จนถึงเมนูและตัวเลือกเพิ่มใหม่ปรากฏบนหน้าลูกค้าเมื่อรีเฟรช ภายใน 1 นาที · การแก้ราคาไม่เปลี่ยนยอดของออเดอร์ที่สั่งไปแล้ว (ตรวจ 5 ออเดอร์เดิม ผ่าน 5 จาก 5) · ลบเมนูที่มีการแมปวัตถุดิบอยู่ ระบบต้องเตือนและลบการแมปนั้นด้วย
- clause ที่ตรวจ: หน้า “จัดการเมนู” เท่านั้น ไม่มีการแมปวัตถุดิบ; เพิ่ม/แก้ชื่อและราคา; การปรากฏบนลูกค้าตรวจเฉพาะ state ในแท็บ
- Functional assertions: ชื่อ/ราคาใหม่ตรงค่าที่บันทึกและเมนูเลือกสั่งได้; หน้าจัดการเมนูไม่มีงานแมป; ไม่สรุปเกณฑ์รีเฟรชหรือ 1 นาที
- NFR ที่แยกจาก functional: NFR-11: กดบันทึก→ข้อมูลเมนูและตัวเลือกปรากฏเมื่อลูกค้ารีเฟรช ภายใน 1 นาที; ตรวจจริง TS-US-19-8
- FR / Flow / Screen: FR-19 / NFR-11 ใน ../step-00-input/fr-nfr-v2.md; MRG-21/22/23/24 ใน ../step-00-input/flow-v2.md; SCR-11 (menu-admin), SCR-03 ลูกค้า; MRG-25/SCR-12 สำหรับ setup แมป
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: มี controls/handler ใน HTML v2 ให้รัน assertion ใน Mock-up ได้; คำว่า auto ไม่ใช่ผลรัน ไม่ยืนยัน AC ระบบจริงหรือ NFR
- Precondition/reset: R0 → M → nav-menu-admin; ไม่มีเมนูใหม่หลัง reset; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: เมนูจำลอง “อาหารทดสอบ” ราคา 70; แก้ชื่อเป็น “อาหารทดสอบใหม่” ราคา 75; ไม่ใส่ตัวเลือก
- data-testid และ scope: menu-admin: admin-menu-select/name/price, btn-save-menu, admin-message (ชื่อเต็มตามทะเบียน S-M); ลูกค้า: menu-list > menu-item-m09; ตรวจ mapping-menu/mapping-scope ภายใน menu-admin ว่าไม่มี
- ขั้นตอน:

  1. เลือก admin-menu-select=new กรอกชื่อและราคา 70 กดบันทึก; ตรวจมี m09 ในรายการจัดการ
  2. ไป C เปิดเมนู ตรวจ m09 ชื่อและราคา 70
  3. กลับ M เลือก m09 แก้ชื่อ/ราคา 75 บันทึก กลับ C ตรวจชื่อและราคาใหม่
  4. เปิด nav-menu-admin ตรวจไม่มีฟอร์มเลือกวัตถุดิบภายใน menu-admin; ลิงก์ nav-mapping ที่อยู่นอก section ไม่ถือเป็นฟอร์มแมป

- Expected result: ชื่อ/ราคาใหม่ตรงค่าที่บันทึกและเมนูเลือกสั่งได้; หน้าจัดการเมนูไม่มีงานแมป; ไม่สรุปเกณฑ์รีเฟรชหรือ 1 นาที
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: รูป jpg/png ไม่เกิน 2 MB ต่อรูป; 0–10 ตัวเลือก; เผยแพร่ภายใน 1 นาที; ราคาออเดอร์เดิม 5 ออเดอร์ ผ่าน 5 จาก 5. ใช้เกณฑ์เฉพาะ clause ของแต่ละกรณี ไม่ลดหรือแทนด้วย smoke; จำนวนทดลองรูป/ตัวเลือกเป็น fixture ไม่ใช่จำนวนบังคับเพิ่ม
- สมมติฐาน/ข้อค้าง: การสลับบทบาทไม่แทน browser reload; เกณฑ์รีเฟรชจริงแยก TS-US-19-8
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-19-2"></a>

## TS-US-19-2 — รูป jpg/png ที่ขนาดขอบเขตและการแสดงรูป

- US: US-19
- เจ้าของ: manager
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: ขอบเขต: หน้า “จัดการเมนู” เท่านั้น ไม่มีการแมปวัตถุดิบ (แยกไป US-20) · รูปเมนูรับไฟล์ jpg/png ขนาดไม่เกิน 2 MB ต่อรูป · ตัวเลือกเพิ่มระบุชื่อและราคาเพิ่มได้ 0–10 ตัวเลือกต่อเมนู · นับจากกดบันทึก จนถึงเมนูและตัวเลือกเพิ่มใหม่ปรากฏบนหน้าลูกค้าเมื่อรีเฟรช ภายใน 1 นาที · การแก้ราคาไม่เปลี่ยนยอดของออเดอร์ที่สั่งไปแล้ว (ตรวจ 5 ออเดอร์เดิม ผ่าน 5 จาก 5) · ลบเมนูที่มีการแมปวัตถุดิบอยู่ ระบบต้องเตือนและลบการแมปนั้นด้วย
- clause ที่ตรวจ: รูปเมนูรับไฟล์ jpg/png ขนาดไม่เกิน 2 MB ต่อรูป
- Functional assertions: ทั้ง jpg และ png ที่ขอบ fixture รับและแสดงรูปตรงต้นแบบ ไม่มีข้อความปฏิเสธรูป; การตรวจด้วยตาเป็นขั้น manual
- NFR ที่แยกจาก functional: NFR-11: กดบันทึก→ข้อมูลเมนูและตัวเลือกปรากฏเมื่อลูกค้ารีเฟรช ภายใน 1 นาที; ตรวจจริง TS-US-19-8
- FR / Flow / Screen: FR-19 / NFR-11 ใน ../step-00-input/fr-nfr-v2.md; MRG-21/22/23/24 ใน ../step-00-input/flow-v2.md; SCR-11 (menu-admin), SCR-03 ลูกค้า; MRG-25/SCR-12 สำหรับ setup แมป
- automation: manual
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: มีขั้นตรวจภาพ/ข้อความ/ขอบเขตด้วยคนตามขั้นตอน; ยังไม่ได้ตรวจ ไม่มีผล manual และไม่ใช้ความเห็นแทนคำตอบธุรกิจที่ขาด
- Precondition/reset: R0 → M → nav-menu-admin; ผู้ตรวจมีภาพสังเคราะห์ที่เปิดได้จริง ไม่ใช้รูปบุคคลจริง; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: ภาพสังเคราะห์ jpg และ png อย่างละ 2 ขนาด: 1,999,999 และ 2,000,000 ไบต์; ทดสอบแยก 4 ชุด; 2 MB=2,000,000 ไบต์เป็นนิยาม mock เท่านั้น
- data-testid และ scope: S-M: admin-menu-image, admin-menu-select, admin-menu-name, admin-menu-price, btn-save-menu; img ภายใน menu-admin และ menu-item-m09 ไม่มี data-testid รูปโดยเฉพาะ ใช้ขอบเขต parent
- ขั้นตอน:

  1. เริ่ม R0 ใหม่ต่อไฟล์ สร้างเมนูจำลองราคา 70 เลือกภาพผ่าน admin-menu-image และรออ่านรูปเสร็จ
  2. ให้ผู้ตรวจเทียบภาพ preview กับภาพต้นแบบ แล้วกดบันทึก
  3. ไป C เปิด m09 ให้ผู้ตรวจเทียบรูปที่แสดงกับภาพเดิมและบันทึกจำนวนไบต์/ชนิดของแต่ละไฟล์

- Expected result: ทั้ง jpg และ png ที่ขอบ fixture รับและแสดงรูปตรงต้นแบบ ไม่มีข้อความปฏิเสธรูป; การตรวจด้วยตาเป็นขั้น manual
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: รูป jpg/png ไม่เกิน 2 MB ต่อรูป; 0–10 ตัวเลือก; เผยแพร่ภายใน 1 นาที; ราคาออเดอร์เดิม 5 ออเดอร์ ผ่าน 5 จาก 5. ใช้เกณฑ์เฉพาะ clause ของแต่ละกรณี ไม่ลดหรือแทนด้วย smoke; จำนวนทดลองรูป/ตัวเลือกเป็น fixture ไม่ใช่จำนวนบังคับเพิ่ม
- สมมติฐาน/ข้อค้าง: Q-19: นิยาม MB ระบบจริงยังไม่ยืนยัน; ที่ 2,097,152 ไบต์ต้องรอหน่วยก่อนตัดสิน AC; ยังไม่มีไฟล์ภาพ/หลักฐานการตรวจรอบนี้
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-19-3"></a>

## TS-US-19-3 — รูปผิดชนิดหรือเกินขนาด

- US: US-19
- เจ้าของ: manager
- ประเภท: ผิดพลาด
- AC ต้นฉบับเต็ม: ขอบเขต: หน้า “จัดการเมนู” เท่านั้น ไม่มีการแมปวัตถุดิบ (แยกไป US-20) · รูปเมนูรับไฟล์ jpg/png ขนาดไม่เกิน 2 MB ต่อรูป · ตัวเลือกเพิ่มระบุชื่อและราคาเพิ่มได้ 0–10 ตัวเลือกต่อเมนู · นับจากกดบันทึก จนถึงเมนูและตัวเลือกเพิ่มใหม่ปรากฏบนหน้าลูกค้าเมื่อรีเฟรช ภายใน 1 นาที · การแก้ราคาไม่เปลี่ยนยอดของออเดอร์ที่สั่งไปแล้ว (ตรวจ 5 ออเดอร์เดิม ผ่าน 5 จาก 5) · ลบเมนูที่มีการแมปวัตถุดิบอยู่ ระบบต้องเตือนและลบการแมปนั้นด้วย
- clause ที่ตรวจ: ขอบเขตชนิด jpg/png และไม่เกิน 2 MB ต่อรูป
- Functional assertions: ต้องไม่รับไฟล์นอกชนิดหรือเกินขนาดที่ยืนยันเป็นรูปเมนู; mock คาดการปฏิเสธตามข้อจำกัด 2,000,000 ไบต์; ผลขอบ 2,000,001 ไบต์ต่อ AC ระบบจริงยัง BLOCKED รอ Q-19
- NFR ที่แยกจาก functional: NFR-11: กดบันทึก→ข้อมูลเมนูและตัวเลือกปรากฏเมื่อลูกค้ารีเฟรช ภายใน 1 นาที; ตรวจจริง TS-US-19-8
- FR / Flow / Screen: FR-19 / NFR-11 ใน ../step-00-input/fr-nfr-v2.md; MRG-21/22/23/24 ใน ../step-00-input/flow-v2.md; SCR-11 (menu-admin), SCR-03 ลูกค้า; MRG-25/SCR-12 สำหรับ setup แมป
- automation: manual
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: มีขั้นตรวจภาพ/ข้อความ/ขอบเขตด้วยคนตามขั้นตอน; ยังไม่ได้ตรวจ ไม่มีผล manual และไม่ใช้ความเห็นแทนคำตอบธุรกิจที่ขาด
- Precondition/reset: R0 → M → nav-menu-admin; ตั้งเมนู/รูปที่ถูกต้องเป็นค่าฐานก่อนทุกกรณี; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: ภาพสังเคราะห์ gif 1,000 ไบต์; jpg และ png ที่เปิดได้แต่ขนาด 2,000,001 และ 2,097,153 ไบต์; ตัวหลังเกินทั้งสองนิยามหน่วยที่เป็นข้อค้าง
- data-testid และ scope: S-M: admin-menu-image, btn-save-menu, admin-message; ข้อความรูป role=status ภายใน menu-admin ไม่มี testid เฉพาะ
- ขั้นตอน:

  1. เลือกไฟล์ผิดทีละชนิด/ขนาด อ่านข้อความด้วยคนแล้วลองบันทึก
  2. ตรวจรูป/ค่าที่หน้าลูกค้าและกลับมาอ่านเมนูเดิม เปรียบเทียบว่ารูปที่อยู่นอกขอบเขตไม่ได้รับเป็นรูปที่ใช้ได้
  3. บันทึกข้อความจริงโดยไม่กำหนดถ้อยคำ error ของร้าน

- Expected result: ต้องไม่รับไฟล์นอกชนิดหรือเกินขนาดที่ยืนยันเป็นรูปเมนู; mock คาดการปฏิเสธตามข้อจำกัด 2,000,000 ไบต์; ผลขอบ 2,000,001 ไบต์ต่อ AC ระบบจริงยัง BLOCKED รอ Q-19
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: รูป jpg/png ไม่เกิน 2 MB ต่อรูป; 0–10 ตัวเลือก; เผยแพร่ภายใน 1 นาที; ราคาออเดอร์เดิม 5 ออเดอร์ ผ่าน 5 จาก 5. ใช้เกณฑ์เฉพาะ clause ของแต่ละกรณี ไม่ลดหรือแทนด้วย smoke; จำนวนทดลองรูป/ตัวเลือกเป็น fixture ไม่ใช่จำนวนบังคับเพิ่ม
- สมมติฐาน/ข้อค้าง: ต้นฉบับไม่ระบุข้อความ error/การคง draft/transaction rollback; ตรวจเฉพาะขอบการรับไฟล์ ไม่ตั้งกฎพฤติกรรมส่วนที่ไม่ระบุ
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-19-4"></a>

## TS-US-19-4 — ตัวเลือก 0 และ 10 รายการ รวมแก้และลบตัวเลือก

- US: US-19
- เจ้าของ: manager
- ประเภท: ทางเลือก
- AC ต้นฉบับเต็ม: ขอบเขต: หน้า “จัดการเมนู” เท่านั้น ไม่มีการแมปวัตถุดิบ (แยกไป US-20) · รูปเมนูรับไฟล์ jpg/png ขนาดไม่เกิน 2 MB ต่อรูป · ตัวเลือกเพิ่มระบุชื่อและราคาเพิ่มได้ 0–10 ตัวเลือกต่อเมนู · นับจากกดบันทึก จนถึงเมนูและตัวเลือกเพิ่มใหม่ปรากฏบนหน้าลูกค้าเมื่อรีเฟรช ภายใน 1 นาที · การแก้ราคาไม่เปลี่ยนยอดของออเดอร์ที่สั่งไปแล้ว (ตรวจ 5 ออเดอร์เดิม ผ่าน 5 จาก 5) · ลบเมนูที่มีการแมปวัตถุดิบอยู่ ระบบต้องเตือนและลบการแมปนั้นด้วย
- clause ที่ตรวจ: ตัวเลือกเพิ่มระบุชื่อและราคาเพิ่มได้ 0–10 ตัวเลือกต่อเมนู; รองรับแก้/ลบตาม US
- Functional assertions: อ่านชื่อและราคาเพิ่มที่บันทึกได้ครบทั้ง 0/10; แก้และลบตัวเลือกสะท้อนใน state ลูกค้า; ไม่รวมเกณฑ์ reload 1 นาที
- NFR ที่แยกจาก functional: NFR-11: กดบันทึก→ข้อมูลเมนูและตัวเลือกปรากฏเมื่อลูกค้ารีเฟรช ภายใน 1 นาที; ตรวจจริง TS-US-19-8
- FR / Flow / Screen: FR-19 / NFR-11 ใน ../step-00-input/fr-nfr-v2.md; MRG-21/22/23/24 ใน ../step-00-input/flow-v2.md; SCR-11 (menu-admin), SCR-03 ลูกค้า; MRG-25/SCR-12 สำหรับ setup แมป
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: มี controls/handler ใน HTML v2 ให้รัน assertion ใน Mock-up ได้; คำว่า auto ไม่ใช่ผลรัน ไม่ยืนยัน AC ระบบจริงหรือ NFR
- Precondition/reset: R0 → M → nav-menu-admin; เมนูใหม่ไม่มีตัวเลือก; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: m09 ชื่อ “ชุดตัวเลือกจำลอง” ราคา 70; ชื่อตัวเลือก “เพิ่มจำลอง01” ถึง “เพิ่มจำลอง10” ราคาเพิ่ม 1 ถึง 10; เปลี่ยนตัวเลือกแรกเป็น “แก้จำลอง01” ราคา 12
- data-testid และ scope: S-M; ปุ่มเพิ่มไม่มี testid: menu-admin button[data-action=add-option]; แถว div.option-row ใช้ input[data-draft-option="0"][data-field=name/price] และ button[data-action=remove-option][data-id="0"]; ลูกค้า section[aria-label="รายละเอียดจานที่เลือก"]
- ขั้นตอน:

  1. บันทึกเมนูที่มี 0 ตัวเลือก ไป C เลือก m09 ตรวจว่าไม่มี checkbox ตัวเลือก
  2. กลับ M เลือก m09; กรอก admin-option-name/price แล้วกดปุ่มเพิ่มทีละรายการจนครบ 10 จากนั้นบันทึก
  3. ไป C เลือก m09 อ่าน label ชื่อ/ราคาเพิ่มครบ 10; ไม่ใช้ตัวนับหัวหน้าแทนตรวจเนื้อหาทั้งสิบ
  4. กลับ M แก้ชื่อ/ราคาของแถวแรกตามข้อมูล บันทึกและเทียบที่ C
  5. กลับ M ลบแถวแรกทีละครั้งจนครบ 10 บันทึก แล้ว C ต้องไม่แสดงตัวเลือก

- Expected result: อ่านชื่อและราคาเพิ่มที่บันทึกได้ครบทั้ง 0/10; แก้และลบตัวเลือกสะท้อนใน state ลูกค้า; ไม่รวมเกณฑ์ reload 1 นาที
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: รูป jpg/png ไม่เกิน 2 MB ต่อรูป; 0–10 ตัวเลือก; เผยแพร่ภายใน 1 นาที; ราคาออเดอร์เดิม 5 ออเดอร์ ผ่าน 5 จาก 5. ใช้เกณฑ์เฉพาะ clause ของแต่ละกรณี ไม่ลดหรือแทนด้วย smoke; จำนวนทดลองรูป/ตัวเลือกเป็น fixture ไม่ใช่จำนวนบังคับเพิ่ม
- สมมติฐาน/ข้อค้าง: selector ที่ไม่มี data-testid อ้างจาก adminHTML ใน HTML:369; opt ID ให้บันทึกจาก DOM หลังสร้าง ไม่เดารหัส; ราคาเพิ่มตัวอย่างไม่ใช่ข้อกำหนดราคา
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-19-5"></a>

## TS-US-19-5 — ป้องกันตัวเลือกเกิน 10

- US: US-19
- เจ้าของ: manager
- ประเภท: ผิดพลาด
- AC ต้นฉบับเต็ม: ขอบเขต: หน้า “จัดการเมนู” เท่านั้น ไม่มีการแมปวัตถุดิบ (แยกไป US-20) · รูปเมนูรับไฟล์ jpg/png ขนาดไม่เกิน 2 MB ต่อรูป · ตัวเลือกเพิ่มระบุชื่อและราคาเพิ่มได้ 0–10 ตัวเลือกต่อเมนู · นับจากกดบันทึก จนถึงเมนูและตัวเลือกเพิ่มใหม่ปรากฏบนหน้าลูกค้าเมื่อรีเฟรช ภายใน 1 นาที · การแก้ราคาไม่เปลี่ยนยอดของออเดอร์ที่สั่งไปแล้ว (ตรวจ 5 ออเดอร์เดิม ผ่าน 5 จาก 5) · ลบเมนูที่มีการแมปวัตถุดิบอยู่ ระบบต้องเตือนและลบการแมปนั้นด้วย
- clause ที่ตรวจ: ตัวเลือกเพิ่มได้ 0–10 ตัวเลือกต่อเมนู
- Functional assertions: เมนูที่บันทึกไม่มีตัวเลือกที่ 11 และยังอยู่ในขอบ 0–10; mock แสดงข้อความปฏิเสธ แต่ไม่ตรึงข้อความร้านหรือวิธีจัดการ draft
- NFR ที่แยกจาก functional: NFR-11: กดบันทึก→ข้อมูลเมนูและตัวเลือกปรากฏเมื่อลูกค้ารีเฟรช ภายใน 1 นาที; ตรวจจริง TS-US-19-8
- FR / Flow / Screen: FR-19 / NFR-11 ใน ../step-00-input/fr-nfr-v2.md; MRG-21/22/23/24 ใน ../step-00-input/flow-v2.md; SCR-11 (menu-admin), SCR-03 ลูกค้า; MRG-25/SCR-12 สำหรับ setup แมป
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: มี controls/handler ใน HTML v2 ให้รัน assertion ใน Mock-up ได้; คำว่า auto ไม่ใช่ผลรัน ไม่ยืนยัน AC ระบบจริงหรือ NFR
- Precondition/reset: R0 → M; สร้าง m09 พร้อมตัวเลือก 10 ตามขั้นเพิ่มใน TS-US-19-4 โดยไม่พึ่งผลรันก่อนหน้า; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: ตัวเลือกที่ 11 ชื่อ “ส่วนเกินจำลอง” ราคาเพิ่ม 11
- data-testid และ scope: S-M; menu-admin button[data-action=add-option] และ div.option-row; C รายละเอียด m09
- ขั้นตอน:

  1. เติมชื่อ/ราคาตัวเลือกที่ 11 แล้วกดเพิ่มและกดบันทึก
  2. อ่านข้อความ admin-message กลับลูกค้าเปิด m09 นับและเทียบรายการตัวเลือก

- Expected result: เมนูที่บันทึกไม่มีตัวเลือกที่ 11 และยังอยู่ในขอบ 0–10; mock แสดงข้อความปฏิเสธ แต่ไม่ตรึงข้อความร้านหรือวิธีจัดการ draft
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: รูป jpg/png ไม่เกิน 2 MB ต่อรูป; 0–10 ตัวเลือก; เผยแพร่ภายใน 1 นาที; ราคาออเดอร์เดิม 5 ออเดอร์ ผ่าน 5 จาก 5. ใช้เกณฑ์เฉพาะ clause ของแต่ละกรณี ไม่ลดหรือแทนด้วย smoke; จำนวนทดลองรูป/ตัวเลือกเป็น fixture ไม่ใช่จำนวนบังคับเพิ่ม
- สมมติฐาน/ข้อค้าง: AC ไม่กำหนดว่าจะปิดปุ่มหรือแจ้งเตือนแบบใด; จำนวนเกิน 10 ต้องไม่ถูกยอมรับเท่านั้น
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-19-6"></a>

## TS-US-19-6 — แก้ราคาแล้วออเดอร์เดิม 5 ใบคงยอด

- US: US-19
- เจ้าของ: manager
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: ขอบเขต: หน้า “จัดการเมนู” เท่านั้น ไม่มีการแมปวัตถุดิบ (แยกไป US-20) · รูปเมนูรับไฟล์ jpg/png ขนาดไม่เกิน 2 MB ต่อรูป · ตัวเลือกเพิ่มระบุชื่อและราคาเพิ่มได้ 0–10 ตัวเลือกต่อเมนู · นับจากกดบันทึก จนถึงเมนูและตัวเลือกเพิ่มใหม่ปรากฏบนหน้าลูกค้าเมื่อรีเฟรช ภายใน 1 นาที · การแก้ราคาไม่เปลี่ยนยอดของออเดอร์ที่สั่งไปแล้ว (ตรวจ 5 ออเดอร์เดิม ผ่าน 5 จาก 5) · ลบเมนูที่มีการแมปวัตถุดิบอยู่ ระบบต้องเตือนและลบการแมปนั้นด้วย
- clause ที่ตรวจ: การแก้ราคาไม่เปลี่ยนยอดของออเดอร์ที่สั่งไปแล้ว (ตรวจ 5 ออเดอร์เดิม ผ่าน 5 จาก 5)
- Functional assertions: ออเดอร์เดิม 5 ใบยังคง 60 บาททุกใบ 5 จาก 5; ใบใหม่ใช้ราคาตัวอย่างใหม่; ผลที่ออกแบบเป็น snapshot ใน mock เท่านั้น
- NFR ที่แยกจาก functional: NFR-11: กดบันทึก→ข้อมูลเมนูและตัวเลือกปรากฏเมื่อลูกค้ารีเฟรช ภายใน 1 นาที; ตรวจจริง TS-US-19-8
- FR / Flow / Screen: FR-19 / NFR-11 ใน ../step-00-input/fr-nfr-v2.md; MRG-21/22/23/24 ใน ../step-00-input/flow-v2.md; SCR-11 (menu-admin), SCR-03 ลูกค้า; MRG-25/SCR-12 สำหรับ setup แมป
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: มี controls/handler ใน HTML v2 ให้รัน assertion ใน Mock-up ได้; คำว่า auto ไม่ใช่ผลรัน ไม่ยืนยัน AC ระบบจริงหรือ NFR
- Precondition/reset: R0 → C โต๊ะ 01; สร้าง 5 ออเดอร์ก่อนแก้ราคาโดยไม่ reset ระหว่างใบ; ไม่มีคืน/เปลี่ยนรายการ; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: แต่ละใบ m01 ราคา 50 + extra-egg 10 = 60 บาท; บันทึก order ID ทั้ง 5; แก้ m01 เป็น 80 และราคา extra-egg เป็น 15; ออเดอร์ใหม่ควรเป็น 95 บาทตาม fixture
- data-testid และ scope: S-C, S-M, S-F; front-orders > front-order[data-order-id="<IDที่บันทึก>"] > front-total และ front-adjusted-total; editor extra-egg ใช้ input[data-draft-option="0"][data-field=price] ภายใน menu-admin
- ขั้นตอน:

  1. สั่ง m01 พร้อมไข่ 5 ครั้ง จด order-id และยอด 60 แต่ละใบ
  2. ไป F อ่าน front-total ของ ID ทั้งห้าเป็นค่าฐาน
  3. ไป M แก้ราคาเมนู/ตัวเลือกและบันทึก แล้วกลับ F เทียบยอดทั้งห้าทีละ ID
  4. ไป C สั่งจานเดิมอีกหนึ่งใบ แล้ว F ตรวจใบใหม่ยอด 95; ห้ามนำใบใหม่มารวม denominator ของห้าใบเดิม

- Expected result: ออเดอร์เดิม 5 ใบยังคง 60 บาททุกใบ 5 จาก 5; ใบใหม่ใช้ราคาตัวอย่างใหม่; ผลที่ออกแบบเป็น snapshot ใน mock เท่านั้น
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: รูป jpg/png ไม่เกิน 2 MB ต่อรูป; 0–10 ตัวเลือก; เผยแพร่ภายใน 1 นาที; ราคาออเดอร์เดิม 5 ออเดอร์ ผ่าน 5 จาก 5. ใช้เกณฑ์เฉพาะ clause ของแต่ละกรณี ไม่ลดหรือแทนด้วย smoke; จำนวนทดลองรูป/ตัวเลือกเป็น fixture ไม่ใช่จำนวนบังคับเพิ่ม
- สมมติฐาน/ข้อค้าง: จำนวน 5 จาก 5 คงเดิม แต่ยังไม่มีผลรัน; persistence และระบบจริงยังไม่พิสูจน์
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-19-7"></a>

## TS-US-19-7 — ลบเมนูที่มีแมปต้องเตือนและลบแมปตาม

- US: US-19
- เจ้าของ: manager
- ประเภท: ข้อยกเว้น
- AC ต้นฉบับเต็ม: ขอบเขต: หน้า “จัดการเมนู” เท่านั้น ไม่มีการแมปวัตถุดิบ (แยกไป US-20) · รูปเมนูรับไฟล์ jpg/png ขนาดไม่เกิน 2 MB ต่อรูป · ตัวเลือกเพิ่มระบุชื่อและราคาเพิ่มได้ 0–10 ตัวเลือกต่อเมนู · นับจากกดบันทึก จนถึงเมนูและตัวเลือกเพิ่มใหม่ปรากฏบนหน้าลูกค้าเมื่อรีเฟรช ภายใน 1 นาที · การแก้ราคาไม่เปลี่ยนยอดของออเดอร์ที่สั่งไปแล้ว (ตรวจ 5 ออเดอร์เดิม ผ่าน 5 จาก 5) · ลบเมนูที่มีการแมปวัตถุดิบอยู่ ระบบต้องเตือนและลบการแมปนั้นด้วย
- clause ที่ตรวจ: ลบเมนูที่มีการแมปวัตถุดิบอยู่ ระบบต้องเตือนและลบการแมปนั้นด้วย
- Functional assertions: มีคำเตือนก่อนยืนยันและไม่มีแมปของเมนูที่ลบหลงเหลือ; ไม่ใช้ข้อความ admin-message อย่างเดียวแทนตรวจ mapping-list
- NFR ที่แยกจาก functional: NFR-11: กดบันทึก→ข้อมูลเมนูและตัวเลือกปรากฏเมื่อลูกค้ารีเฟรช ภายใน 1 นาที; ตรวจจริง TS-US-19-8
- FR / Flow / Screen: FR-19 / NFR-11 ใน ../step-00-input/fr-nfr-v2.md; MRG-21/22/23/24 ใน ../step-00-input/flow-v2.md; SCR-11 (menu-admin), SCR-03 ลูกค้า; MRG-25/SCR-12 สำหรับ setup แมป
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: มี controls/handler ใน HTML v2 ให้รัน assertion ใน Mock-up ได้; คำว่า auto ไม่ใช่ผลรัน ไม่ยืนยัน AC ระบบจริงหรือ NFR
- Precondition/reset: R0 → M; m01 มีแมป rice/chicken/basil ทั้งจานและ egg เฉพาะ extra-egg ตาม seed; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: ลบ m01; ใช้แมป m02 เป็นข้อมูลเปรียบเทียบข้างเคียง; ไม่มีออเดอร์ค้าง
- data-testid และ scope: S-M และ S-P; dialog browser ไม่มี data-testid ใช้ dialog event; ลูกค้า menu-list > menu-item-m01
- ขั้นตอน:

  1. เปิด nav-mapping บันทึกรายการแมปของ m01
  2. กลับ nav-menu-admin เลือก m01 และกด btn-delete-menu; ดัก dialog และตรวจว่ามีคำเตือนเรื่องลบการแมป
  3. ยืนยัน dialog แล้วตรวจ m01 ไม่อยู่ใน admin-menu-select, mapping-menu และ menu-list; mapping-list ไม่มีความสัมพันธ์ที่ menu_id=m01 ทั้ง whole/option

- Expected result: มีคำเตือนก่อนยืนยันและไม่มีแมปของเมนูที่ลบหลงเหลือ; ไม่ใช้ข้อความ admin-message อย่างเดียวแทนตรวจ mapping-list
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: รูป jpg/png ไม่เกิน 2 MB ต่อรูป; 0–10 ตัวเลือก; เผยแพร่ภายใน 1 นาที; ราคาออเดอร์เดิม 5 ออเดอร์ ผ่าน 5 จาก 5. ใช้เกณฑ์เฉพาะ clause ของแต่ละกรณี ไม่ลดหรือแทนด้วย smoke; จำนวนทดลองรูป/ตัวเลือกเป็น fixture ไม่ใช่จำนวนบังคับเพิ่ม
- สมมติฐาน/ข้อค้าง: การยืนยันด้วย dialog เป็นวิธีของ mock; ลบขณะออเดอร์ค้างและผลต่อรายการเดิมรอ Q-19; ไม่ใช้กรณีนี้ตอบนโยบายนั้น
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-19-8"></a>

## TS-US-19-8 — เผยแพร่เมนูและตัวเลือกเมื่อรีเฟรชภายใน 1 นาที

- US: US-19
- เจ้าของ: manager
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: ขอบเขต: หน้า “จัดการเมนู” เท่านั้น ไม่มีการแมปวัตถุดิบ (แยกไป US-20) · รูปเมนูรับไฟล์ jpg/png ขนาดไม่เกิน 2 MB ต่อรูป · ตัวเลือกเพิ่มระบุชื่อและราคาเพิ่มได้ 0–10 ตัวเลือกต่อเมนู · นับจากกดบันทึก จนถึงเมนูและตัวเลือกเพิ่มใหม่ปรากฏบนหน้าลูกค้าเมื่อรีเฟรช ภายใน 1 นาที · การแก้ราคาไม่เปลี่ยนยอดของออเดอร์ที่สั่งไปแล้ว (ตรวจ 5 ออเดอร์เดิม ผ่าน 5 จาก 5) · ลบเมนูที่มีการแมปวัตถุดิบอยู่ ระบบต้องเตือนและลบการแมปนั้นด้วย
- clause ที่ตรวจ: นับจากกดบันทึก จนถึงเมนูและตัวเลือกเพิ่มใหม่ปรากฏบนหน้าลูกค้าเมื่อรีเฟรช ภายใน 1 นาที
- Functional assertions: เมนูและตัวเลือกใหม่ตรงค่าบันทึกหลังลูกค้ารีเฟรช; แยกการจับเวลาไป NFR-11
- NFR ที่แยกจาก functional: NFR-11: กดบันทึก→ข้อมูลเมนูและตัวเลือกปรากฏเมื่อลูกค้ารีเฟรช ภายใน 1 นาที; ตรวจจริง TS-US-19-8
- FR / Flow / Screen: FR-19 / NFR-11 ใน ../step-00-input/fr-nfr-v2.md; MRG-21/22/23/24 ใน ../step-00-input/flow-v2.md; SCR-11 (menu-admin), SCR-03 ลูกค้า; MRG-25/SCR-12 สำหรับ setup แมป
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: จำเป็นต้องมีระบบจริงหรือฟีเจอร์/ข้อมูลที่ Input ยังไม่มี; BLOCKED ตาม Precondition และข้อค้าง ไม่ใช้คลิก Mock-up แทน
- Precondition/reset: BLOCKED: ต้องมีระบบบันทึกจริงและอุปกรณ์ลูกค้าแยก; HTML reload เรียก reset และล้าง state; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: เมนู/ชื่อ/ราคา/รูป/ตัวเลือกชุดจำลองใหม่และชุดแก้ไขจาก TS-US-19-1/2/4; ไม่ใช้บัญชีหรือคำสั่งซื้อจริง
- data-testid และ scope: selector ระบบจริง MISSING; S-M/S-C ใช้เตรียมแบบจำลองได้ แต่ไม่ใช้เป็นหลักฐานของ reload จริง
- ขั้นตอน:

  1. เตรียมระบบจริงที่ได้รับอนุญาตพร้อมหน้าลูกค้าเปิดอยู่
  2. บันทึกเวลา t0 ตอนกดบันทึกเมนูและตัวเลือก
  3. รีเฟรชหน้าลูกค้าบนอุปกรณ์นั้น บันทึก t1 เมื่อข้อมูลใหม่ครบตรงกับที่บันทึก
  4. เปรียบเทียบ t1−t0 แยกต่อชุดใหม่และชุดแก้ไข

- Expected result: เมนูและตัวเลือกใหม่ตรงค่าบันทึกหลังรีเฟรช และ t1−t0 ≤ 1 นาที; ห้ามใช้เวลาสลับบทบาทในแท็บเดียวตัดสิน
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: รูป jpg/png ไม่เกิน 2 MB ต่อรูป; 0–10 ตัวเลือก; เผยแพร่ภายใน 1 นาที; ราคาออเดอร์เดิม 5 ออเดอร์ ผ่าน 5 จาก 5. ใช้เกณฑ์เฉพาะ clause ของแต่ละกรณี ไม่ลดหรือแทนด้วย smoke; จำนวนทดลองรูป/ตัวเลือกเป็น fixture ไม่ใช่จำนวนบังคับเพิ่ม
- สมมติฐาน/ข้อค้าง: Q-19: จำนวนครั้ง/สัดส่วนของเกณฑ์ 1 นาทีไม่มีข้อมูล; สองชุดเป็นข้อเสนอ fixture ไม่เพิ่มจำนวนบังคับ; รูปขอบ 2 MB ยังรอหน่วย
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-20-1"></a>

## TS-US-20-1 — แยกหน้าแมปและเลือกเฉพาะรายการที่สร้างแล้ว

- US: US-20
- เจ้าของ: manager
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: ขอบเขต: หน้า “แมปวัตถุดิบ” เท่านั้น ไม่มีการเพิ่ม/แก้เมนูหรือราคา · dependency: เลือกได้เฉพาะเมนูและตัวเลือกเพิ่มที่ถูกสร้างไว้แล้วใน US-19 (ต้องมีเมนูก่อนจึงแมปวัตถุดิบได้ และเมนูที่ยังไม่มีในระบบไม่ปรากฏให้เลือก) · ระบุต่อเมนูว่าใช้วัตถุดิบใด “ทั้งจาน” และต่อตัวเลือกเพิ่มว่าใช้วัตถุดิบใด “เฉพาะตัวเลือก” · บันทึกแล้วมีผลกับกฎปิด/เปิดเมนูอัตโนมัติ (US-14) และแสดงบนหน้าลูกค้าเมื่อรีเฟรชภายใน 1 นาที ทดสอบ 5 เมนู ผ่าน 5 จาก 5 (ดูหมายเหตุ ค.)
- clause ที่ตรวจ: หน้า “แมปวัตถุดิบ” เท่านั้น ไม่มีเพิ่ม/แก้เมนูหรือราคา; dependency US-19 เมนู/ตัวเลือกต้องถูกสร้างแล้ว
- Functional assertions: เลือกได้เฉพาะเมนูและตัวเลือกที่บันทึกแล้ว; ฟอร์มแมปไม่มีความสามารถเพิ่ม/แก้เมนูหรือราคาในหน้านี้
- NFR ที่แยกจาก functional: NFR-12: บันทึกแมป→ลูกค้ารีเฟรชเห็นผลภายใน 1 นาที ครบ 5 เมนู 5 จาก 5; ตรวจจริง TS-US-20-4
- FR / Flow / Screen: FR-20 / NFR-12 ใน ../step-00-input/fr-nfr-v2.md; MRG-25 (MRG-23 กรณีลบแมป) ใน ../step-00-input/flow-v2.md; SCR-12 หน้าแมป, SCR-11 ใช้สร้างก่อน; SCR-01 ลูกค้า/SCR-07 ครัวเป็น setup
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: มี controls/handler ใน HTML v2 ให้รัน assertion ใน Mock-up ได้; คำว่า auto ไม่ใช่ผลรัน ไม่ยืนยัน AC ระบบจริงหรือ NFR
- Precondition/reset: R0 → M; seed m01 และ extra-egg มีแล้ว; ไม่มี m09; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: เมนูใหม่ m09 “เมนูแมปจำลอง” ราคา 70 ตัวเลือก “เสริมจำลอง” ราคา 5
- data-testid และ scope: S-M/S-P; mapping-menu และ mapping-option อ่าน option[value]; admin-menu-name/price และ btn-save-menu ต้องไม่มีภายใน section ของหน้าแมป (หา section ที่มี mapping-menu)
- ขั้นตอน:

  1. เปิด nav-mapping ตรวจ m01/extra-egg ปรากฏและ m09 ไม่ปรากฏ
  2. ตรวจ section หน้าแมปไม่มีช่องแก้ชื่อ/ราคาและปุ่มบันทึกเมนู
  3. ไป nav-menu-admin สร้าง m09 พร้อมตัวเลือกและบันทึก แล้ว nav-mapping เลือก m09/scope=option
  4. อ่านรหัสตัวเลือกที่สร้างจาก mapping-option และเทียบชื่อกับค่าที่สร้าง

- Expected result: เลือกได้เฉพาะเมนูและตัวเลือกที่บันทึกแล้ว; ฟอร์มแมปไม่มีความสามารถเพิ่ม/แก้เมนูหรือราคาในหน้านี้
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: ทดสอบ 5 เมนู ผ่าน 5 จาก 5; บันทึกแล้วลูกค้ารีเฟรชเห็นผลภายใน 1 นาที. หมายเหตุ ค. ไม่มีนิยาม และคงข้อความอ้าง US-14; ไม่ย้าย denominator เป็นจำนวนวัตถุดิบ
- สมมติฐาน/ข้อค้าง: เส้นทาง nav-menu-admin ที่อยู่นอก section เป็นการไปหน้าคนละงาน ไม่ถือเป็นการแก้ราคาในหน้าแมป
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-20-2"></a>

## TS-US-20-2 — ผลแมปทั้งจานและเฉพาะตัวเลือกครบ 5 เมนู

- US: US-20
- เจ้าของ: manager
- ประเภท: ทางเลือก
- AC ต้นฉบับเต็ม: ขอบเขต: หน้า “แมปวัตถุดิบ” เท่านั้น ไม่มีการเพิ่ม/แก้เมนูหรือราคา · dependency: เลือกได้เฉพาะเมนูและตัวเลือกเพิ่มที่ถูกสร้างไว้แล้วใน US-19 (ต้องมีเมนูก่อนจึงแมปวัตถุดิบได้ และเมนูที่ยังไม่มีในระบบไม่ปรากฏให้เลือก) · ระบุต่อเมนูว่าใช้วัตถุดิบใด “ทั้งจาน” และต่อตัวเลือกเพิ่มว่าใช้วัตถุดิบใด “เฉพาะตัวเลือก” · บันทึกแล้วมีผลกับกฎปิด/เปิดเมนูอัตโนมัติ (US-14) และแสดงบนหน้าลูกค้าเมื่อรีเฟรชภายใน 1 นาที ทดสอบ 5 เมนู ผ่าน 5 จาก 5 (ดูหมายเหตุ ค.)
- clause ที่ตรวจ: ระบุวัตถุดิบทั้งจาน/เฉพาะตัวเลือก; ผลต่อกฎปิด/เปิดและชุด 5 เมนู 5 จาก 5; ตรวจเฉพาะ functional mock
- Functional assertions: ผล mock ตรงแมปทั้งสองทางทุกเมนู 5 จาก 5; เมนูหลักกรณี option ยังสั่งได้; ไม่อ้าง reload หรือเวลา 1 นาที
- NFR ที่แยกจาก functional: NFR-12: บันทึกแมป→ลูกค้ารีเฟรชเห็นผลภายใน 1 นาที ครบ 5 เมนู 5 จาก 5; ตรวจจริง TS-US-20-4
- FR / Flow / Screen: FR-20 / NFR-12 ใน ../step-00-input/fr-nfr-v2.md; MRG-25 (MRG-23 กรณีลบแมป) ใน ../step-00-input/flow-v2.md; SCR-12 หน้าแมป, SCR-11 ใช้สร้างก่อน; SCR-01 ลูกค้า/SCR-07 ครัวเป็น setup
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: มี controls/handler ใน HTML v2 ให้รัน assertion ใน Mock-up ได้; คำว่า auto ไม่ใช่ผลรัน ไม่ยืนยัน AC ระบบจริงหรือ NFR
- Precondition/reset: R0 → M สร้าง 5 เมนูใหม่ m09–m13 ทีละเมนู ทุกเมนูมีตัวเลือก “เสริมจำลอง” หนึ่งตัว; ทุกวัตถุดิบมี; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: m09/chicken/whole; m10/egg/option; m11/pork/whole; m12/rice/option; m13/basil/whole; ทุกเมนูราคา 70 ตัวเลือก 5; จับคู่ option ID ที่อ่านจริงของแต่ละเมนู
- data-testid และ scope: S-M/S-P/S-K/S-C; menu-item-m09 ถึง menu-item-m13 ตาม template menu-item-<id>; option-<idที่อ่านจริง> ภายในรายละเอียดจานที่เลือก
- ขั้นตอน:

  1. สร้างและบันทึก 5 เมนูให้เสร็จก่อนแมป แล้วใช้ mapping-menu/scope/option/ingredient กด btn-save-mapping ทีละคู่
  2. อ่าน mapping-list เทียบ menu ID, ingredient, whole/option และ option ID ครบ 5
  3. สำหรับแต่ละคู่ ไป K เลือกวัตถุดิบกดหมด จากนั้น C เปิดเมนู: whole ตรวจเมนู disabled; option ตรวจเมนู enabled และเฉพาะตัวเลือก mapped disabled
  4. กลับ K กดกลับมามี แล้ว C ตรวจเมนู/ตัวเลือกเป้าหมายเปิดคืน ก่อนเริ่มคู่ถัดไป

- Expected result: ผล mock ตรงแมปทั้งสองทางทุกเมนู 5 จาก 5; เมนูหลักกรณี option ยังสั่งได้; ไม่อ้าง reload หรือเวลา 1 นาที
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: ทดสอบ 5 เมนู ผ่าน 5 จาก 5; บันทึกแล้วลูกค้ารีเฟรชเห็นผลภายใน 1 นาที. หมายเหตุ ค. ไม่มีนิยาม และคงข้อความอ้าง US-14; ไม่ย้าย denominator เป็นจำนวนวัตถุดิบ
- สมมติฐาน/ข้อค้าง: DI-02/DI-04, A-02/A-03 และ Q-20 ยังเปิด: คงอ้าง US-14 ต้นฉบับ; การใช้ US-12/US-13 setup เป็นข้อเสนอรอยืนยัน ไม่ใช่การแก้ dependency
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-20-3"></a>

## TS-US-20-3 — เมนูที่ยังไม่สร้างต้องไม่ปรากฏให้แมป

- US: US-20
- เจ้าของ: manager
- ประเภท: ผิดพลาด
- AC ต้นฉบับเต็ม: ขอบเขต: หน้า “แมปวัตถุดิบ” เท่านั้น ไม่มีการเพิ่ม/แก้เมนูหรือราคา · dependency: เลือกได้เฉพาะเมนูและตัวเลือกเพิ่มที่ถูกสร้างไว้แล้วใน US-19 (ต้องมีเมนูก่อนจึงแมปวัตถุดิบได้ และเมนูที่ยังไม่มีในระบบไม่ปรากฏให้เลือก) · ระบุต่อเมนูว่าใช้วัตถุดิบใด “ทั้งจาน” และต่อตัวเลือกเพิ่มว่าใช้วัตถุดิบใด “เฉพาะตัวเลือก” · บันทึกแล้วมีผลกับกฎปิด/เปิดเมนูอัตโนมัติ (US-14) และแสดงบนหน้าลูกค้าเมื่อรีเฟรชภายใน 1 นาที ทดสอบ 5 เมนู ผ่าน 5 จาก 5 (ดูหมายเหตุ ค.)
- clause ที่ตรวจ: ต้องมีเมนูก่อนจึงแมปวัตถุดิบได้ และเมนูที่ยังไม่มีในระบบไม่ปรากฏให้เลือก
- Functional assertions: ไม่สามารถเลือกแมปรายการที่ยังไม่ได้สร้างผ่านรายการเลือก; ไม่มีเมนูหรือ option draft หลุดเข้ารายการ
- NFR ที่แยกจาก functional: NFR-12: บันทึกแมป→ลูกค้ารีเฟรชเห็นผลภายใน 1 นาที ครบ 5 เมนู 5 จาก 5; ตรวจจริง TS-US-20-4
- FR / Flow / Screen: FR-20 / NFR-12 ใน ../step-00-input/fr-nfr-v2.md; MRG-25 (MRG-23 กรณีลบแมป) ใน ../step-00-input/flow-v2.md; SCR-12 หน้าแมป, SCR-11 ใช้สร้างก่อน; SCR-01 ลูกค้า/SCR-07 ครัวเป็น setup
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: มี controls/handler ใน HTML v2 ให้รัน assertion ใน Mock-up ได้; คำว่า auto ไม่ใช่ผลรัน ไม่ยืนยัน AC ระบบจริงหรือ NFR
- Precondition/reset: R0 → M; ไม่มี m09; สร้าง draft เมนูแต่ยังไม่บันทึก; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: draft “ยังไม่บันทึกจำลอง” ราคา 70 พร้อมชื่อ option draft; m99 เป็น ID จำลองที่ไม่มี
- data-testid และ scope: S-M/S-P; mapping-menu option และ mapping-option option; ไม่มีการ inject ID ที่ไม่มีลง DOM
- ขั้นตอน:

  1. เปิดหน้าแมปอ่านรายการค่าที่มีอยู่ ยืนยันว่า m09/m99 ไม่มี
  2. กลับจัดการเมนูกรอก draft ใหม่แต่ไม่กดบันทึก แล้วกลับหน้าแมป
  3. ตรวจไม่พบชื่อ draft/ID ใหม่และไม่มี option draft ให้เลือก

- Expected result: ไม่สามารถเลือกแมปรายการที่ยังไม่ได้สร้างผ่านรายการเลือก; ไม่มีเมนูหรือ option draft หลุดเข้ารายการ
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: ทดสอบ 5 เมนู ผ่าน 5 จาก 5; บันทึกแล้วลูกค้ารีเฟรชเห็นผลภายใน 1 นาที. หมายเหตุ ค. ไม่มีนิยาม และคงข้อความอ้าง US-14; ไม่ย้าย denominator เป็นจำนวนวัตถุดิบ
- สมมติฐาน/ข้อค้าง: การเรียก API ด้วย ID ปลอมหรือถูกลบพร้อมกัน: ผล/ข้อความ/HTTP code ไม่มีข้อมูล ไม่กำหนดเองและไม่ได้ทดสอบ
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-20-4"></a>

## TS-US-20-4 — ผลแมปเมื่อรีเฟรชภายใน 1 นาทีครบ 5 เมนู

- US: US-20
- เจ้าของ: manager
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: ขอบเขต: หน้า “แมปวัตถุดิบ” เท่านั้น ไม่มีการเพิ่ม/แก้เมนูหรือราคา · dependency: เลือกได้เฉพาะเมนูและตัวเลือกเพิ่มที่ถูกสร้างไว้แล้วใน US-19 (ต้องมีเมนูก่อนจึงแมปวัตถุดิบได้ และเมนูที่ยังไม่มีในระบบไม่ปรากฏให้เลือก) · ระบุต่อเมนูว่าใช้วัตถุดิบใด “ทั้งจาน” และต่อตัวเลือกเพิ่มว่าใช้วัตถุดิบใด “เฉพาะตัวเลือก” · บันทึกแล้วมีผลกับกฎปิด/เปิดเมนูอัตโนมัติ (US-14) และแสดงบนหน้าลูกค้าเมื่อรีเฟรชภายใน 1 นาที ทดสอบ 5 เมนู ผ่าน 5 จาก 5 (ดูหมายเหตุ ค.)
- clause ที่ตรวจ: บันทึกแล้วมีผลกับกฎปิด/เปิดเมนูอัตโนมัติ (US-14) และแสดงบนหน้าลูกค้าเมื่อรีเฟรชภายใน 1 นาที ทดสอบ 5 เมนู ผ่าน 5 จาก 5 (ดูหมายเหตุ ค.)
- Functional assertions: ผลแมป whole/option ตรง 5 เมนูเมื่อรีเฟรช; คง US-14 และหมายเหตุ ค. เป็นข้อค้าง; แยกเวลาการเผยแพร่ไป NFR-12
- NFR ที่แยกจาก functional: NFR-12: บันทึกแมป→ลูกค้ารีเฟรชเห็นผลภายใน 1 นาที ครบ 5 เมนู 5 จาก 5; ตรวจจริง TS-US-20-4
- FR / Flow / Screen: FR-20 / NFR-12 ใน ../step-00-input/fr-nfr-v2.md; MRG-25 (MRG-23 กรณีลบแมป) ใน ../step-00-input/flow-v2.md; SCR-12 หน้าแมป, SCR-11 ใช้สร้างก่อน; SCR-01 ลูกค้า/SCR-07 ครัวเป็น setup
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: จำเป็นต้องมีระบบจริงหรือฟีเจอร์/ข้อมูลที่ Input ยังไม่มี; BLOCKED ตาม Precondition และข้อค้าง ไม่ใช้คลิก Mock-up แทน
- Precondition/reset: BLOCKED: ระบบบันทึก/อ่านข้ามอุปกรณ์และหมายเหตุ ค. ไม่มีข้อมูล; ไม่ใช้ reload HTML ที่ล้าง state; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: 5 เมนูและความสัมพันธ์จำลองตาม TS-US-20-2; ตั้งสถานะหมด/มีให้รู้ก่อนแต่ละชุดเพื่อแยกผลบันทึกแมปจากเวลาครัวกด
- data-testid และ scope: ระบบจริง MISSING; S-P/S-K/S-C เป็น mapping อ้างอิง UI เท่านั้น
- ขั้นตอน:

  1. สร้างเมนู/ตัวเลือกในระบบทดสอบจริงและเตรียมสถานะวัตถุดิบที่กำหนด
  2. บันทึกแมปพร้อม t0 ต่อเมนู; รีเฟรชหน้าลูกค้าและเก็บ t1 เมื่อเห็นผล whole/option
  3. ทดลองหมด/กลับมามีให้ผลตรงแมป ครอบคลุม 5 เมนู; บันทึกเวลาเผยแพร่แมปแยกจากเวลาเหตุการณ์ครัว
  4. เทียบผลและ t1−t0 ทีละเมนู ไม่รวมเวลา US-12/US-13 มาทดแทน

- Expected result: ผลแมปปรากฏหลัง refresh ภายใน 1 นาทีและถูกต้อง 5 จาก 5 เมนู; การรับรองส่วนหมายเหตุและรหัสอ้างยัง BLOCKED
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: ทดสอบ 5 เมนู ผ่าน 5 จาก 5; บันทึกแล้วลูกค้ารีเฟรชเห็นผลภายใน 1 นาที. หมายเหตุ ค. ไม่มีนิยาม และคงข้อความอ้าง US-14; ไม่ย้าย denominator เป็นจำนวนวัตถุดิบ
- สมมติฐาน/ข้อค้าง: DI-02/DI-04, Q-20; ห้ามสรุปว่า US-14 ถูกแก้เป็น US-12/13; หน่วยเวลาเดิมไม่ลดเป็นความเร็ว render mock
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-21-1"></a>

## TS-US-21-1 — ตั้งช่วงและ N=5 เตือนก่อนยืนยันครบ 3 รอบ

- US: US-21
- เจ้าของ: manager
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: ตั้งเวลาเริ่ม–สิ้นสุดช่วงเร่งด่วน (เช่น 11:30–13:30) และเพดาน N ออเดอร์ต่อหน้าต่างเวลา 15 นาทีที่นับจากนาทีที่ 00/15/30/45 เมื่อจำนวนออเดอร์ที่ยืนยันในหน้าต่างนั้นถึง N ลูกค้าใหม่เห็นข้อความ “ครัวเต็ม รอประมาณ X นาที” ก่อนยืนยัน ทดสอบด้วย N=5 ผ่าน 3 จาก 3 รอบ
- clause ที่ตรวจ: ตั้งเริ่ม–สิ้นสุดและ N; หน้าต่าง 15 นาที; ถึง N แสดง “ครัวเต็ม รอประมาณ X นาที” ก่อนยืนยัน; N=5 ผ่าน 3 จาก 3 รอบ
- Functional assertions: ทั้ง 3 รอบมีข้อความ “ครัวเต็ม รอประมาณ 10 นาที” พร้อมป้าย X จำลองก่อนลูกค้าใหม่ยืนยัน เมื่อ count=5; ไม่ตีความว่าต้องปิดหรือเปิดรับออเดอร์ที่ 6 ตามกฎร้าน
- NFR ที่แยกจาก functional: ไม่มี NFR เฉพาะ US-21 ใน FR v2; 15 นาที/00/15/30/45/N เป็นกฎ functional ไม่ใช่ SLA; ไม่สร้างสูตร X หรือเกณฑ์ load
- FR / Flow / Screen: FR-21 ใน ../step-00-input/fr-nfr-v2.md; MRG-34/35 ใน ../step-00-input/flow-v2.md; SCR-17 (capacity-settings) และ SCR-03 ลูกค้าก่อนยืนยัน
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: มี controls/handler ใน HTML v2 ให้รัน assertion ใน Mock-up ได้; คำว่า auto ไม่ใช่ผลรัน ไม่ยืนยัน AC ระบบจริงหรือ NFR
- Precondition/reset: R0 ใหม่ทุกหนึ่งรอบ → M → nav-capacity; ตั้งค่าครบเองทุกครั้ง ไม่อาศัย default; รอบ 1 เวลา 12:00, รอบ 2 เวลา 12:15, รอบ 3 เวลา 12:30; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: ช่วง 11:30–13:30; N=5; X=10 นาทีเป็น fixture ไม่ใช่สูตรร้าน; รอบละ 5 ออเดอร์ m01 จานละ 50 แล้วเตรียมใบที่ 6
- data-testid และ scope: S-C/S-A; +5 นาทีไม่มี data-testid ใช้ button[data-action=advance][data-minutes="5"] ส่วนกลาง; +10 ใช้ btn-advance-10m
- ขั้นตอน:

  1. ต่อรอบ reset แล้วเลื่อนเวลารอบ 2 ด้วย +10,+5 นาที; รอบ 3 ด้วย +10 สามครั้ง; ตรวจ sim-clock มี +07:00
  2. เข้า M → nav-capacity กรอก capacity-start=11:30, capacity-end=13:30, capacity-limit=5, capacity-wait-minutes=10 และบันทึก; อ่านค่ากลับ
  3. ไป C โต๊ะ 01 สั่ง m01 หนึ่งจานและยืนยัน 4 ใบ; เตรียมใบที่ 5 ตรวจไม่พบ capacity-message ก่อนถึง N
  4. ยืนยันใบที่ 5 แล้วสลับเป็นลูกค้าใหม่โต๊ะ 02 เปิดเมนูและเพิ่ม m01 เตรียมใบที่ 6 แต่ยังไม่ส่ง
  5. ตรวจ capacity-message เต็มข้อความและป้าย X จำลองอยู่ก่อนปุ่ม btn-submit-order; กลับ M อ่าน capacity-window ยังยืนยันแล้ว 5; กลับลูกค้าตรวจออเดอร์ใหม่ยังไม่ถูกสร้าง
  6. บันทึกหลักฐานแยกทั้ง 3 รอบพร้อมจำนวน/เวลา/ข้อความ

- Expected result: ทั้ง 3 รอบมีข้อความ “ครัวเต็ม รอประมาณ 10 นาที” พร้อมป้าย X จำลองก่อนลูกค้าใหม่ยืนยัน เมื่อ count=5; ไม่ตีความว่าต้องปิดหรือเปิดรับออเดอร์ที่ 6 ตามกฎร้าน
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: ช่วงตัวอย่าง 11:30–13:30; หน้าต่าง 15 นาทีเริ่ม 00/15/30/45; N=5 ผ่าน 3 จาก 3 รอบ. สามรอบหลัก TS-US-21-1/6; boundary/ค่าผิดเพิ่มเติมไม่นำมานับแทนสามรอบ
- สมมติฐาน/ข้อค้าง: อ้าง fixture TS-US-21-101 โดยไม่คัดสร้าง ID ซ้ำ; แบบนี้เพิ่ม 3 รอบและ selector v2 ที่พบจริง; +07:00/[start,end) เป็น fixture ต่างจากข้อเสนอ UTC ใน Flow; สูตร X ยัง Q-V2-CAPACITY
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-21-2"></a>

## TS-US-21-2 — ตะกร้าและคำสั่งที่ยังไม่ยืนยันไม่ทำให้เต็ม

- US: US-21
- เจ้าของ: manager
- ประเภท: ข้อยกเว้น
- AC ต้นฉบับเต็ม: ตั้งเวลาเริ่ม–สิ้นสุดช่วงเร่งด่วน (เช่น 11:30–13:30) และเพดาน N ออเดอร์ต่อหน้าต่างเวลา 15 นาทีที่นับจากนาทีที่ 00/15/30/45 เมื่อจำนวนออเดอร์ที่ยืนยันในหน้าต่างนั้นถึง N ลูกค้าใหม่เห็นข้อความ “ครัวเต็ม รอประมาณ X นาที” ก่อนยืนยัน ทดสอบด้วย N=5 ผ่าน 3 จาก 3 รอบ
- clause ที่ตรวจ: นับจำนวนออเดอร์ที่ยืนยันในหน้าต่าง ไม่ใช่จำนวนจานหรือตะกร้า
- Functional assertions: จำนวนยืนยันเป็น 4 ตลอดแม้มีหลายจาน/เปิดหน้าซ้ำ/ตะกร้าถูกปฏิเสธ; ไม่แสดงคำเตือนถึง N ก่อนยืนยันสำเร็จใบที่ 5
- NFR ที่แยกจาก functional: ไม่มี NFR เฉพาะ US-21 ใน FR v2; 15 นาที/00/15/30/45/N เป็นกฎ functional ไม่ใช่ SLA; ไม่สร้างสูตร X หรือเกณฑ์ load
- FR / Flow / Screen: FR-21 ใน ../step-00-input/fr-nfr-v2.md; MRG-34/35 ใน ../step-00-input/flow-v2.md; SCR-17 (capacity-settings) และ SCR-03 ลูกค้าก่อนยืนยัน
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: มี controls/handler ใน HTML v2 ให้รัน assertion ใน Mock-up ได้; คำว่า auto ไม่ใช่ผลรัน ไม่ยืนยัน AC ระบบจริงหรือ NFR
- Precondition/reset: R0 → ตั้ง S-A ช่วง 11:30–13:30, N=5, X=10; เวลา 12:00 คงเดิม; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: ส่งสำเร็จ 4 ใบ: ใบแรก m01 จำนวน 3 จานในออเดอร์เดียว อีก 3 ใบจานละ 1; ตะกร้าถัดไปเพิ่ม m01 จำนวน 6 จานแต่ไม่ส่ง
- data-testid และ scope: S-C/S-A/S-K; cart-count, order-id, capacity-window, capacity-message; stock ใช้ ingredient-select=chicken
- ขั้นตอน:

  1. ยืนยัน 4 ออเดอร์โดยใบแรกมีหลายจาน ตรวจ M capacity-window ระบุยืนยันแล้ว 4
  2. กลับ C เติม 6 จาน เปิดเมนูซ้ำและสลับบทบาท แล้วกลับ M ตรวจ count ยัง 4
  3. ไป K กด chicken หมดแล้วกลับ C พยายามส่งตะกร้าเก่า ตรวจ order-message มีการปฏิเสธและไม่มี order ID ใหม่
  4. กลับ M ตรวจยัง 4 ออเดอร์ กลับ C ตรวจไม่มีคำเตือนเต็มเพราะยังไม่ถึง N

- Expected result: จำนวนยืนยันเป็น 4 ตลอดแม้มีหลายจาน/เปิดหน้าซ้ำ/ตะกร้าถูกปฏิเสธ; ไม่แสดงคำเตือนถึง N ก่อนยืนยันสำเร็จใบที่ 5
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: ช่วงตัวอย่าง 11:30–13:30; หน้าต่าง 15 นาทีเริ่ม 00/15/30/45; N=5 ผ่าน 3 จาก 3 รอบ. สามรอบหลัก TS-US-21-1/6; boundary/ค่าผิดเพิ่มเติมไม่นำมานับแทนสามรอบ
- สมมติฐาน/ข้อค้าง: กติกาปฏิเสธ stock มาจาก US-06 ใช้ setup เท่านั้น เจ้าของการตรวจจำนวนยัง US-21; ไม่กำหนดผลจำนวนของการคืน/เปลี่ยนรายการที่ยืนยันแล้ว
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-21-3"></a>

## TS-US-21-3 — หน้าต่างเริ่มนาที 00/15/30/45

- US: US-21
- เจ้าของ: manager
- ประเภท: ทางเลือก
- AC ต้นฉบับเต็ม: ตั้งเวลาเริ่ม–สิ้นสุดช่วงเร่งด่วน (เช่น 11:30–13:30) และเพดาน N ออเดอร์ต่อหน้าต่างเวลา 15 นาทีที่นับจากนาทีที่ 00/15/30/45 เมื่อจำนวนออเดอร์ที่ยืนยันในหน้าต่างนั้นถึง N ลูกค้าใหม่เห็นข้อความ “ครัวเต็ม รอประมาณ X นาที” ก่อนยืนยัน ทดสอบด้วย N=5 ผ่าน 3 จาก 3 รอบ
- clause ที่ตรวจ: หน้าต่างเวลา 15 นาทีที่นับจากนาทีที่ 00/15/30/45
- Functional assertions: เริ่มหน้าต่างตรง 00/15/30/45 และไม่รวมใบหน้าต่างก่อนใน fixture; สี่ชุดนี้เป็น boundary เพิ่ม ไม่แทนสามรอบ TS-US-21-1
- NFR ที่แยกจาก functional: ไม่มี NFR เฉพาะ US-21 ใน FR v2; 15 นาที/00/15/30/45/N เป็นกฎ functional ไม่ใช่ SLA; ไม่สร้างสูตร X หรือเกณฑ์ load
- FR / Flow / Screen: FR-21 ใน ../step-00-input/fr-nfr-v2.md; MRG-34/35 ใน ../step-00-input/flow-v2.md; SCR-17 (capacity-settings) และ SCR-03 ลูกค้าก่อนยืนยัน
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: มี controls/handler ใน HTML v2 ให้รัน assertion ใน Mock-up ได้; คำว่า auto ไม่ใช่ผลรัน ไม่ยืนยัน AC ระบบจริงหรือ NFR
- Precondition/reset: R0 → S-A ตั้ง 11:30–13:30,N=5,X=10; ทุกช่วงมีคิวใหม่ในหน้าต่างนั้น; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: เวลา 12:00,12:15,12:30,12:45 และ 13:00 (+07:00 จำลอง); ช่วงครึ่งเปิดเป็น fixture
- data-testid และ scope: S-A/S-C; ปุ่ม +5 นาทีใช้ CSS จริงตาม TS-US-21-1; อ่าน capacity-window และ sim-clock
- ขั้นตอน:

  1. เริ่ม 12:00 ยืนยัน 5 ออเดอร์แล้วตรวจเต็ม
  2. เลื่อน +10,+5 เป็น 12:15 ตรวจ start/end เป็น 12:15–12:30 และ count=0 ก่อนส่งชุดใหม่
  3. ยืนยัน 5 ใบในช่วงใหม่นี้ ทำซ้ำที่ 12:30 และ 12:45 พร้อมตรวจเตือน
  4. เลื่อนถึง 13:00 ตรวจหน้าต่าง 13:00–13:15 และ count=0; เก็บจำนวน/เวลาทุกช่วง

- Expected result: เริ่มหน้าต่างตรง 00/15/30/45 และไม่รวมใบหน้าต่างก่อนใน fixture; สี่ชุดนี้เป็น boundary เพิ่ม ไม่แทนสามรอบ TS-US-21-1
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: ช่วงตัวอย่าง 11:30–13:30; หน้าต่าง 15 นาทีเริ่ม 00/15/30/45; N=5 ผ่าน 3 จาก 3 รอบ. สามรอบหลัก TS-US-21-1/6; boundary/ค่าผิดเพิ่มเติมไม่นำมานับแทนสามรอบ
- สมมติฐาน/ข้อค้าง: การเป็นช่วง [start,end) และเขตเวลา +07:00 ยังเป็นสมมติฐาน; ไม่อ้างว่าทดสอบก่อนขอบหนึ่งวินาทีด้วยปุ่มขยับเป็นนาที
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-21-4"></a>

## TS-US-21-4 — ขอบหนึ่งวินาที เขตเวลา และสูตร X

- US: US-21
- เจ้าของ: manager
- ประเภท: ข้อยกเว้น
- AC ต้นฉบับเต็ม: ตั้งเวลาเริ่ม–สิ้นสุดช่วงเร่งด่วน (เช่น 11:30–13:30) และเพดาน N ออเดอร์ต่อหน้าต่างเวลา 15 นาทีที่นับจากนาทีที่ 00/15/30/45 เมื่อจำนวนออเดอร์ที่ยืนยันในหน้าต่างนั้นถึง N ลูกค้าใหม่เห็นข้อความ “ครัวเต็ม รอประมาณ X นาที” ก่อนยืนยัน ทดสอบด้วย N=5 ผ่าน 3 จาก 3 รอบ
- clause ที่ตรวจ: การจัดออเดอร์ลงหน้าต่าง 00/15/30/45 และค่า X ก่อนยืนยัน
- Functional assertions: ยังไม่มี expected สำหรับการตัดขอบ, คืน/เปลี่ยน, เปลี่ยน N, นอกช่วง และสูตร X; ผลตัดสิน BLOCKED จนได้ oracle; ข้อบังคับที่ทราบคือถึง N ต้องแจ้งก่อนยืนยัน
- NFR ที่แยกจาก functional: ไม่มี NFR เฉพาะ US-21 ใน FR v2; 15 นาที/00/15/30/45/N เป็นกฎ functional ไม่ใช่ SLA; ไม่สร้างสูตร X หรือเกณฑ์ load
- FR / Flow / Screen: FR-21 ใน ../step-00-input/fr-nfr-v2.md; MRG-34/35 ใน ../step-00-input/flow-v2.md; SCR-17 (capacity-settings) และ SCR-03 ลูกค้าก่อนยืนยัน
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: จำเป็นต้องมีระบบจริงหรือฟีเจอร์/ข้อมูลที่ Input ยังไม่มี; BLOCKED ตาม Precondition และข้อค้าง ไม่ใช้คลิก Mock-up แทน
- Precondition/reset: BLOCKED: ไม่มีนิยามเขตเวลา/ขอบหน้าต่าง/สูตร X ที่อนุมัติและไม่มีเครื่องมือ UI ขยับทีละวินาที; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: ยืนยันที่ 11:59:59→12:00:00,12:14:59→12:15:00,12:29:59→12:30:00,12:44:59→12:45:00; ก่อน/ตรง 11:30 และ 13:30; N=5
- data-testid และ scope: S-A มีเฉพาะหน้าจำลอง; timestamp server/เครื่องมือวินาที/selector ระบบจริง MISSING
- ขั้นตอน:

  1. รับคำยืนยันขอบช่วงและเขตเวลาจากเจ้าของข้อกำหนดก่อนกำหนด oracle
  2. ในระบบทดสอบสร้างเหตุการณ์ยืนยันที่ก่อน/ตรงขอบทุกค่าข้างต้น เก็บ server timestamp และจำนวนที่นับ
  3. ทดสอบคืน/เปลี่ยนหลังยืนยันและเปลี่ยน N กลางช่วงโดยบันทึกผลจริง; เทียบกับคำตอบที่อนุมัติ
  4. ตรวจ X ตามสูตร/ข้อมูลที่ได้รับการยืนยันก่อนเปรียบเทียบตัวเลข

- Expected result: ยังไม่มี expected สำหรับการตัดขอบ, คืน/เปลี่ยน, เปลี่ยน N, นอกช่วง และสูตร X; ผลตัดสิน BLOCKED จนได้ oracle; ข้อบังคับที่ทราบคือถึง N ต้องแจ้งก่อนยืนยัน
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: ช่วงตัวอย่าง 11:30–13:30; หน้าต่าง 15 นาทีเริ่ม 00/15/30/45; N=5 ผ่าน 3 จาก 3 รอบ. สามรอบหลัก TS-US-21-1/6; boundary/ค่าผิดเพิ่มเติมไม่นำมานับแทนสามรอบ
- สมมติฐาน/ข้อค้าง: Q-V2-CAPACITY และ DI-06/A-04; US-21 ตัวอย่าง 11:30–13:30 ไม่แก้ US-07 ที่ 11:30–13:00 และ 17:30–19:30; ไม่ยืมสูตร ETA แทน X
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-21-5"></a>

## TS-US-21-5 — ค่าตั้งความจุไม่ครบหรือช่วงกลับด้าน

- US: US-21
- เจ้าของ: manager
- ประเภท: ผิดพลาด
- AC ต้นฉบับเต็ม: ตั้งเวลาเริ่ม–สิ้นสุดช่วงเร่งด่วน (เช่น 11:30–13:30) และเพดาน N ออเดอร์ต่อหน้าต่างเวลา 15 นาทีที่นับจากนาทีที่ 00/15/30/45 เมื่อจำนวนออเดอร์ที่ยืนยันในหน้าต่างนั้นถึง N ลูกค้าใหม่เห็นข้อความ “ครัวเต็ม รอประมาณ X นาที” ก่อนยืนยัน ทดสอบด้วย N=5 ผ่าน 3 จาก 3 รอบ
- clause ที่ตรวจ: การตั้งเริ่ม–สิ้นสุดและ N; ต้นฉบับไม่กำหนดผลค่าผิด
- Functional assertions: oracle ร้าน MISSING; ไม่ตัดสินว่า AC ผ่าน/ไม่ผ่านจากค่าผิดที่ยังไม่มีนโยบาย; mock คาดข้อความ “บันทึกไม่ได้ใน fixture” ตามข้อจำกัดฟอร์ม แต่เป็นข้อสังเกตจำลองเท่านั้น
- NFR ที่แยกจาก functional: ไม่มี NFR เฉพาะ US-21 ใน FR v2; 15 นาที/00/15/30/45/N เป็นกฎ functional ไม่ใช่ SLA; ไม่สร้างสูตร X หรือเกณฑ์ load
- FR / Flow / Screen: FR-21 ใน ../step-00-input/fr-nfr-v2.md; MRG-34/35 ใน ../step-00-input/flow-v2.md; SCR-17 (capacity-settings) และ SCR-03 ลูกค้าก่อนยืนยัน
- automation: manual
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: มีขั้นตรวจภาพ/ข้อความ/ขอบเขตด้วยคนตามขั้นตอน; ยังไม่ได้ตรวจ ไม่มีผล manual และไม่ใช้ความเห็นแทนคำตอบธุรกิจที่ขาด
- Precondition/reset: R0 → M → nav-capacity; บันทึกค่าฐาน 11:30–13:30,N=5,X=10 ก่อนแต่ละกรณี; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: เริ่มว่าง; เริ่ม13:30/สิ้นสุด11:30; N ว่าง/0/−1/1.5 ทีละกรณี
- data-testid และ scope: S-A: capacity-start/end/limit, btn-save-capacity, capacity-setting-message และ capacity-window
- ขั้นตอน:

  1. กรอกค่าผิดหนึ่งตัวต่อครั้ง กดบันทึก ให้ผู้ตรวจอ่านและจดข้อความ/ค่าที่แสดง
  2. เปิดหน้าความจุใหม่อ่านค่าที่คงไว้ แล้วคืนค่าฐานก่อนกรณีถัดไป
  3. แยกผลสังเกต mock ออกจากคำถามส่งเจ้าของข้อกำหนด

- Expected result: oracle ร้าน MISSING; ไม่ตัดสินว่า AC ผ่าน/ไม่ผ่านจากค่าผิดที่ยังไม่มีนโยบาย; mock คาดข้อความ “บันทึกไม่ได้ใน fixture” ตามข้อจำกัดฟอร์ม แต่เป็นข้อสังเกตจำลองเท่านั้น
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: ช่วงตัวอย่าง 11:30–13:30; หน้าต่าง 15 นาทีเริ่ม 00/15/30/45; N=5 ผ่าน 3 จาก 3 รอบ. สามรอบหลัก TS-US-21-1/6; boundary/ค่าผิดเพิ่มเติมไม่นำมานับแทนสามรอบ
- สมมติฐาน/ข้อค้าง: Q-V2-CAPACITY: ช่วงข้ามวัน/ค่า N ที่ยอมรับ/การคงค่าเดิม/ข้อความผิดยังรอยืนยัน; manual เพราะมีขั้นอ่านและทบทวนผลโดยคน; ช่องเกณฑ์ธุรกิจ BLOCKED
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-21-6"></a>

## TS-US-21-6 — ยืนยัน threshold สามรอบด้วยเหตุการณ์ระบบจริง

- US: US-21
- เจ้าของ: manager
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: ตั้งเวลาเริ่ม–สิ้นสุดช่วงเร่งด่วน (เช่น 11:30–13:30) และเพดาน N ออเดอร์ต่อหน้าต่างเวลา 15 นาทีที่นับจากนาทีที่ 00/15/30/45 เมื่อจำนวนออเดอร์ที่ยืนยันในหน้าต่างนั้นถึง N ลูกค้าใหม่เห็นข้อความ “ครัวเต็ม รอประมาณ X นาที” ก่อนยืนยัน ทดสอบด้วย N=5 ผ่าน 3 จาก 3 รอบ
- clause ที่ตรวจ: ออเดอร์ยืนยันในหน้าต่างถึง N แสดงข้อความก่อนยืนยัน N=5 ผ่าน 3 จาก 3 รอบ
- Functional assertions: threshold/ลำดับข้อความผ่าน 3 จาก 3 รอบเมื่อรันจริงตาม AC; สูตร X ยังไม่อาจรับรองและไม่มี SLA/เกณฑ์ load ใหม่
- NFR ที่แยกจาก functional: ไม่มี NFR เฉพาะ US-21 ใน FR v2; 15 นาที/00/15/30/45/N เป็นกฎ functional ไม่ใช่ SLA; ไม่สร้างสูตร X หรือเกณฑ์ load
- FR / Flow / Screen: FR-21 ใน ../step-00-input/fr-nfr-v2.md; MRG-34/35 ใน ../step-00-input/flow-v2.md; SCR-17 (capacity-settings) และ SCR-03 ลูกค้าก่อนยืนยัน
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: จำเป็นต้องมีระบบจริงหรือฟีเจอร์/ข้อมูลที่ Input ยังไม่มี; BLOCKED ตาม Precondition และข้อค้าง ไม่ใช้คลิก Mock-up แทน
- Precondition/reset: BLOCKED: ไม่มีระบบจริง/เหตุการณ์ server และ oracle สูตร X; ต้องตั้งช่วงเวลาที่ตกลงและลูกค้าหลายหน้าจอ; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: สามรอบอิสระตาม TS-US-21-1, N=5; ใช้เฉพาะออเดอร์จำลอง; เวลาเริ่มแต่ละรอบบันทึกตามเขตเวลาที่ได้รับคำยืนยัน
- data-testid และ scope: selector/endpoint ระบบจริง MISSING; S-A/S-C เป็นเพียงจุดอ้างอิง
- ขั้นตอน:

  1. ตั้งช่วง/N แล้วเก็บข้อมูลการตั้งค่าจริง
  2. ยืนยัน 4→5 ออเดอร์ในหน้าต่างเดียว เก็บ server events แยกจากจำนวนรายการ
  3. เปิดก่อนยืนยันของลูกค้าใหม่ เก็บข้อความและพิสูจน์ว่ายังไม่มีเหตุการณ์ยืนยันของใบใหม่
  4. ทำครบ 3 รอบเทียบ count,ช่วงและข้อความทุกครั้ง; ถ้าจะตรวจตัวเลข X ต้องได้สูตรก่อน

- Expected result: threshold/ลำดับข้อความผ่าน 3 จาก 3 รอบเมื่อรันจริงตาม AC; สูตร X ยังไม่อาจรับรองและไม่มี SLA/เกณฑ์ load ใหม่
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: ช่วงตัวอย่าง 11:30–13:30; หน้าต่าง 15 นาทีเริ่ม 00/15/30/45; N=5 ผ่าน 3 จาก 3 รอบ. สามรอบหลัก TS-US-21-1/6; boundary/ค่าผิดเพิ่มเติมไม่นำมานับแทนสามรอบ
- สมมติฐาน/ข้อค้าง: การรัน mock สามรอบไม่รับรอง concurrency หรือ server count; ไม่อนุมานนโยบายปฏิเสธเมื่อเต็ม
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-22-1"></a>

## TS-US-22-1 — ปิดรับกลับบ้านแต่ QR หน้าร้านยังสั่งได้

- US: US-22
- เจ้าของ: manager
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: นับจากผู้จัดการกดปิดรับสั่งกลับบ้าน จนถึงหน้าลูกค้าซ่อนโหมด “สั่งกลับบ้าน” เมื่อโหลดหน้าใหม่ ภายใน 10 วินาทีบน LAN ในร้าน ในอย่างน้อย 9 จาก 10 ครั้ง และการสั่งหน้าร้านผ่าน QR ยังทำได้ตามปกติ
- clause ที่ตรวจ: ปิดรับ→ลูกค้าซ่อนโหมดเมื่อโหลดหน้าใหม่ภายใน 10 วินาที LAN อย่างน้อย 9 จาก 10; หน้าร้านยังสั่งได้
- Functional assertions: สวิตช์ปิดรับทำให้โหมดกลับบ้านหายเมื่อโหลดใหม่ และลูกค้ายังสั่งหน้าร้านผ่าน QR ได้; แยกเกณฑ์เวลา LAN ด้านล่าง
- NFR ที่แยกจาก functional: รหัส NFR=MISSING; เกณฑ์จาก AC คือปิดรับ→ซ่อนโหมดเมื่อโหลดใหม่ ภายใน 10 วินาทีบน LAN อย่างน้อย 9 จาก 10; ไม่แต่งรหัส NFR
- FR / Flow / Screen: FR=MISSING / Flow=MISSING / Screen สวิตช์=MISSING: US-22 ไม่อยู่ในขอบเขต FR/Flow v2; ออกแบบจาก ../../../docs/case-study-source.md; order-mode ใน HTML มีเฉพาะฝั่งลูกค้า
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: จำเป็นต้องมีระบบจริงหรือฟีเจอร์/ข้อมูลที่ Input ยังไม่มี; BLOCKED ตาม Precondition และข้อค้าง ไม่ใช้คลิก Mock-up แทน
- Precondition/reset: BLOCKED: US-22 ไม่มี FR/Flow/สวิตช์ใน UI v2; ต้องมีระบบ LAN จริงและเริ่มเปิดรับกลับบ้าน; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: 10 รอบทดลองอิสระ; QR โต๊ะจำลอง 01; เมนูจำลอง 50 บาท; เปิดรับก่อนทุกหนึ่งรอบ
- data-testid และ scope: สวิตช์รับกลับบ้าน MISSING; order-mode มีใน screen-customer แต่ไม่มี control ปิดรับ; toggle-promptpay เป็นคนละงาน ห้ามใช้แทน
- ขั้นตอน:

  1. ก่อนแต่ละรอบเปิดรับกลับบ้านและตรวจว่าโหมดปรากฏบนลูกค้า
  2. กดสวิตช์ปิดรับหนึ่งครั้งพร้อม t0; ลูกค้าโหลดหน้าใหม่บน LAN จับ t1 เมื่อไม่มีโหมดกลับบ้าน
  3. สแกน QR โต๊ะจำลองและยืนยันออเดอร์หน้าร้านหนึ่งใบ ตรวจระบบรับและผูกโต๊ะได้
  4. ทำครบ 10 ครั้งโดยคืน precondition ก่อนทุกครั้ง และเก็บเวลารายครั้ง

- Expected result: โหมดกลับบ้านหายหลังโหลดใหม่ภายใน 10 วินาทีอย่างน้อย 9 จาก 10 ครั้ง; การสั่งผ่าน QR หน้าร้านยังทำได้ตาม AC
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: ทดสอบปิดรับ 10 ครั้ง ภายใน 10 วินาทีบน LAN อย่างน้อย 9 จาก 10; สั่งหน้าร้านผ่าน QR ยังทำได้; เกณฑ์เวลา/จำนวนครั้งตอนเปิดและหน้าเก่าไม่มีข้อมูล
- สมมติฐาน/ข้อค้าง: ขอบเขตสวิตช์เดียวมาจาก US; ไม่ใช้ข้อยกเว้นเวลาหนึ่งครั้งยอมรับให้การสั่งหน้าร้านเสีย; ยังไม่มี runtime
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-22-2"></a>

## TS-US-22-2 — หน้ากลับบ้านค้างอยู่ก่อนผู้จัดการปิดรับ

- US: US-22
- เจ้าของ: manager
- ประเภท: ข้อยกเว้น
- AC ต้นฉบับเต็ม: นับจากผู้จัดการกดปิดรับสั่งกลับบ้าน จนถึงหน้าลูกค้าซ่อนโหมด “สั่งกลับบ้าน” เมื่อโหลดหน้าใหม่ ภายใน 10 วินาทีบน LAN ในร้าน ในอย่างน้อย 9 จาก 10 ครั้ง และการสั่งหน้าร้านผ่าน QR ยังทำได้ตามปกติ
- clause ที่ตรวจ: การปิดรับชั่วคราว; ต้นฉบับกำหนดเฉพาะลูกค้าที่โหลดหน้าใหม่
- Functional assertions: สำหรับ B ต้องซ่อนโหมดตามเกณฑ์ US-22; สำหรับ A การรับ/ปฏิเสธ/ข้อความ/ช่วงรับใหม่ไม่มีข้อมูล จึง BLOCKED ไม่เพิ่มกฎอัตโนมัติ
- NFR ที่แยกจาก functional: รหัส NFR=MISSING; เกณฑ์จาก AC คือปิดรับ→ซ่อนโหมดเมื่อโหลดใหม่ ภายใน 10 วินาทีบน LAN อย่างน้อย 9 จาก 10; ไม่แต่งรหัส NFR
- FR / Flow / Screen: FR=MISSING / Flow=MISSING / Screen สวิตช์=MISSING: US-22 ไม่อยู่ในขอบเขต FR/Flow v2; ออกแบบจาก ../../../docs/case-study-source.md; order-mode ใน HTML มีเฉพาะฝั่งลูกค้า
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: จำเป็นต้องมีระบบจริงหรือฟีเจอร์/ข้อมูลที่ Input ยังไม่มี; BLOCKED ตาม Precondition และข้อค้าง ไม่ใช้คลิก Mock-up แทน
- Precondition/reset: BLOCKED: ไม่มี UI ปิดรับและไม่กำหนดผล submit จากหน้าเดิม; ระบบจริงต้องพร้อมก่อนทดลอง; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: ลูกค้า A เปิดหน้ากลับบ้านและมีตะกร้าก่อนปิด; ลูกค้า B โหลดใหม่หลังปิด
- data-testid และ scope: สวิตช์และ route จริง MISSING; order-mode/pickup-slot/btn-submit-order อ้าง UI จำลองเท่านั้น
- ขั้นตอน:

  1. A เตรียมตะกร้ากลับบ้านไว้ ผู้จัดการปิดรับ
  2. B โหลดใหม่เพื่อยืนยันส่วนที่ AC ระบุว่าซ่อนโหมด
  3. A พยายามยืนยันจากหน้าเก่า เก็บผลและเหตุการณ์ไว้พิจารณาตามนโยบายที่ขอคำยืนยัน

- Expected result: สำหรับ B ต้องซ่อนโหมดตามเกณฑ์ US-22; สำหรับ A การรับ/ปฏิเสธ/ข้อความ/ช่วงรับใหม่ไม่มีข้อมูล จึง BLOCKED ไม่เพิ่มกฎอัตโนมัติ
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: ทดสอบปิดรับ 10 ครั้ง ภายใน 10 วินาทีบน LAN อย่างน้อย 9 จาก 10; สั่งหน้าร้านผ่าน QR ยังทำได้; เกณฑ์เวลา/จำนวนครั้งตอนเปิดและหน้าเก่าไม่มีข้อมูล
- สมมติฐาน/ข้อค้าง: ขอเจ้าของข้อกำหนดยืนยันผลต่อหน้าเก่าและออเดอร์กลับบ้านที่ยืนยันแล้ว
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-22-3"></a>

## TS-US-22-3 — เปิดรับกลับบ้านคืนด้วยสวิตช์เดียว

- US: US-22
- เจ้าของ: manager
- ประเภท: ทางเลือก
- AC ต้นฉบับเต็ม: นับจากผู้จัดการกดปิดรับสั่งกลับบ้าน จนถึงหน้าลูกค้าซ่อนโหมด “สั่งกลับบ้าน” เมื่อโหลดหน้าใหม่ ภายใน 10 วินาทีบน LAN ในร้าน ในอย่างน้อย 9 จาก 10 ครั้ง และการสั่งหน้าร้านผ่าน QR ยังทำได้ตามปกติ
- clause ที่ตรวจ: ความต้องการ US เปิด/ปิดรับสั่งกลับบ้านชั่วคราวด้วยสวิตช์เดียว; AC ให้เวลาเฉพาะปิด
- Functional assertions: กลับมารับสั่งกลับบ้านได้ตามความต้องการ US; ไม่ยืม SLA 10 วินาที/9 จาก 10 สำหรับทางเปิดเพราะ AC ไม่ระบุ
- NFR ที่แยกจาก functional: รหัส NFR=MISSING; เกณฑ์จาก AC คือปิดรับ→ซ่อนโหมดเมื่อโหลดใหม่ ภายใน 10 วินาทีบน LAN อย่างน้อย 9 จาก 10; ไม่แต่งรหัส NFR
- FR / Flow / Screen: FR=MISSING / Flow=MISSING / Screen สวิตช์=MISSING: US-22 ไม่อยู่ในขอบเขต FR/Flow v2; ออกแบบจาก ../../../docs/case-study-source.md; order-mode ใน HTML มีเฉพาะฝั่งลูกค้า
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: จำเป็นต้องมีระบบจริงหรือฟีเจอร์/ข้อมูลที่ Input ยังไม่มี; BLOCKED ตาม Precondition และข้อค้าง ไม่ใช้คลิก Mock-up แทน
- Precondition/reset: BLOCKED: ฟีเจอร์เปิด/ปิดไม่อยู่ใน UI v2; ระบบเริ่มปิดรับและหน้าร้านยังเปิด; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: เมนูจำลองและช่วงรับที่ถูกต้องตามเวลาทดสอบ; ไม่มีคำสั่งจริง
- data-testid และ scope: สวิตช์เปิดรับ MISSING; ไม่สร้างชื่อ selector ขึ้นใหม่
- ขั้นตอน:

  1. กดสวิตช์เปิดหนึ่งครั้ง โหลดหน้าลูกค้าใหม่
  2. ตรวจเลือกกลับบ้านและส่งออเดอร์ทดสอบได้; ตรวจโหมดหน้าร้านยังใช้งาน

- Expected result: กลับมารับสั่งกลับบ้านได้ตามความต้องการ US; ไม่ยืม SLA 10 วินาที/9 จาก 10 สำหรับทางเปิดเพราะ AC ไม่ระบุ
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: ทดสอบปิดรับ 10 ครั้ง ภายใน 10 วินาทีบน LAN อย่างน้อย 9 จาก 10; สั่งหน้าร้านผ่าน QR ยังทำได้; เกณฑ์เวลา/จำนวนครั้งตอนเปิดและหน้าเก่าไม่มีข้อมูล
- สมมติฐาน/ข้อค้าง: เกณฑ์เวลา/จำนวนตัวอย่างตอนเปิดไม่มีข้อมูล; ชุดหนึ่งครั้งเป็นข้อเสนอ ไม่ใช่เกณฑ์ใหม่
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-22-4"></a>

## TS-US-22-4 — จับการปิดรับกลับบ้านที่ปิดการสั่งผ่าน QR หน้าร้านผิดขอบเขต

- US: US-22
- เจ้าของ: manager
- ประเภท: ข้อยกเว้น
- AC ต้นฉบับเต็ม: นับจากผู้จัดการกดปิดรับสั่งกลับบ้าน จนถึงหน้าลูกค้าซ่อนโหมด “สั่งกลับบ้าน” เมื่อโหลดหน้าใหม่ ภายใน 10 วินาทีบน LAN ในร้าน ในอย่างน้อย 9 จาก 10 ครั้ง และการสั่งหน้าร้านผ่าน QR ยังทำได้ตามปกติ
- clause ที่ตรวจ: หลังปิดรับกลับบ้าน โหลดใหม่ซ่อนโหมดตามเวลา AC และการสั่งหน้าร้านผ่าน QR ยังทำได้ตามปกติ
- FR / Flow / Screen: FR=MISSING / Flow=MISSING / Screen สวิตช์=MISSING: US-22 ไม่อยู่ในขอบเขต FR/Flow v2; ออกแบบจาก ../../../docs/case-study-source.md; order-mode ใน HTML มีเฉพาะฝั่งลูกค้า
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: แก้ D06 เชิงออกแบบ; ต้องมีระบบ/จุดแทรก fault และจุดสังเกตตาม Precondition ซึ่งยังไม่มี จึง BLOCKED การรัน. เป็นแผนตรวจจับผลผิดด้วย oracle อิสระ ไม่ใช่การเปลี่ยนชื่อ happy path; ยังไม่ได้ทำ fault หรือรันทดสอบ
- Precondition/reset: BLOCKED การรัน: U22 ไม่มี mapping/สวิตช์รับกลับบ้านและระบบ QR จริง; ต้องมีระบบทดสอบพร้อมตัวแทรกขอบเขตช่องทางที่ตรวจการรับออเดอร์ก่อนยืนยัน. ยังไม่มีจุดแทรกหรือ selector ใน Input; ไม่ใช้ toggle-promptpay
- Test data: fixture โต๊ะ01 เปิด session อยู่ เมนูจำลอง50บาท stockมี; ก่อนปิดรับกลับบ้านสั่งหน้าร้านผ่าน QR ได้. ปิดรับกลับบ้านด้วยสวิตช์จริงในระบบทดสอบ; ลูกค้าใหม่สแกน QR โต๊ะ01หลังปิด ไม่ใช้หน้ากลับบ้านเก่า

- data-testid และ scope: MISSING: สวิตช์/QR route ระบบจริง/จุดแทรก; ใช้ table/session/order ID ที่ได้จริงและอ่านรายการบนจอครัว/หน้าร้านเพื่อยืนยันรับคำสั่ง ไม่แต่ง selector
- ขั้นตอน:

  1. control: เริ่มเปิดรับทั้งสองช่องทางและยืนยันว่าจาน/โต๊ะพร้อมสั่ง แล้วผู้จัดการกดปิดรับกลับบ้านจด t0; ลูกค้าโหลดใหม่ จด t1 เมื่อโหมดกลับบ้านซ่อน ตรวจ t1−t0≤10 วินาที
  2. หลังปิด ลูกค้าใหม่สแกน QR หน้าร้าน เลือกเมนู50บาทและกดยืนยัน เก็บ order ID และตรวจรายการ/โต๊ะบนครัวกับหน้าร้านเพื่อยืนยันว่ายังสั่งได้
  3. fault: reset แล้วใช้ตัวแทรกที่จุดตรวจรับคำสั่งของระบบ เปลี่ยนขอบเขตผลของสวิตช์ปิดจากเฉพาะกลับบ้านให้ครอบคลุมทั้งกลับบ้านและหน้าร้าน โดยคงโต๊ะเปิด/stockมี/QRถูกต้อง; เก็บขอบเขตก่อนและหลังแทรกเป็นหลักฐาน setup
  4. ผู้จัดการปิดรับกลับบ้านแล้วทำขั้นสแกน QR ใหม่และยืนยันเมนูเดิม; เก็บผลการส่ง ข้อความถ้ามี และรายการปลายทาง โดยไม่คาดเดาข้อความปฏิเสธเฉพาะ
  5. ตรวจสถานะคำสั่งจากหลักฐานการประมวลผล: ถ้ายังไม่มีผลตอบหรือไม่มีจุดสังเกตพอ ให้ BLOCKED/ไม่มีข้อมูล ไม่ตั้ง timeout การสั่งเพิ่ม; ปิดตัวแทรกแล้วทำ control ซ้ำ

- Expected result: หลังปิดรับกลับบ้าน การยืนยันจาก QR หน้าร้านยังต้องสร้างออเดอร์ของโต๊ะ/sessionนั้นที่ตรวจรายการได้ตามปกติ. ถ้า fault ทำให้ปฏิเสธหรือปิดทางยืนยันเพราะสวิตช์กลับบ้าน ให้ระบุผิดขอบเขตตาม AC แม้โหลดใหม่ซ่อนโหมดกลับบ้านภายใน10วินาทีแล้ว. การไม่มีหลักฐานจบคำสั่งอย่างเดียวไม่อนุมานสาเหตุปฏิเสธ
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: คงปิดรับ 10 ครั้ง ซ่อนโหมดเมื่อโหลดใหม่ภายใน 10 วินาทีบน LAN อย่างน้อย 9 จาก 10 ตาม TS-US-22-1 พร้อมตรวจ QR หน้าร้าน; fault แยกต่างหาก ไม่เพิ่ม SLA รับคำสั่งหรือกฎหน้าเก่า
- สมมติฐาน/ข้อค้าง: U22 ยัง MISSING; manager/ผู้ดูแล FR/Flow/UI เตรียมระบบและ mapping. เจ้าของข้อกำหนดตัดสินการรับ/ปฏิเสธหน้าเก่าใน TS-US-22-2; ไม่ยืม control โหลดใหม่มาเป็น oracle ของหน้าเก่า
- Status: MOCK_NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-23-1"></a>

## TS-US-23-1 — รายงานช่วงวันที่และยอดจ่ายแล้วจาก 20 ใบ

- US: US-23
- เจ้าของ: manager
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: เลือกช่วงวันที่แล้วรายงานแสดงภายใน 5 วินาที (นับจากกด “ดูรายงาน” จนตารางแสดงบนเครื่อง Ubuntu ในร้าน) ยอดรวมตรงกับผลรวมออเดอร์สถานะ “จ่ายแล้ว” ที่นับมือจาก 20 ใบของชุดทดสอบ (คลาดเคลื่อน 0 บาท) และดาวน์โหลด CSV เปิดด้วย LibreOffice ได้
- clause ที่ตรวจ: US ต้องรายงานรายวันแยกเมนู/ช่องทาง/ช่วงเวลา; AC เลือกช่วงวันที่ ตารางภายใน 5 วินาที Ubuntu ยอดรวมจ่ายแล้วคลาดเคลื่อน 0 บาท
- Functional assertions: เลือกช่วงวันที่และแสดงรายงานแยกรายวัน/เมนู/ช่องทาง/ช่วงเวลา; ยอดรวมเฉพาะจ่ายแล้วจากชุด20ใบตรง840บาท คลาดเคลื่อน0บาท; แยกการแสดงตารางภายใน5วินาทีไปเกณฑ์คุณภาพ
- NFR ที่แยกจาก functional: รหัส NFR=MISSING; AC มี 5 วินาทีจากกดดูรายงานจนตารางแสดงบน Ubuntu; ความตรงของยอด 0 บาทจาก 20 ใบและ CSV ต้องแยกตรวจ; ไม่สร้างรหัสใหม่
- FR / Flow / Screen: FR=MISSING / Flow=MISSING / Screen รายงานทำงานจริง=MISSING: US-23 ไม่อยู่ใน FR/Flow v2; report-screen (SCR-15 สำหรับตรวจสิทธิ์ US-25) เป็น placeholder ไม่ใช่รายงาน US-23; ฐาน AC ../../../docs/case-study-source.md
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: จำเป็นต้องมีระบบจริงหรือฟีเจอร์/ข้อมูลที่ Input ยังไม่มี; BLOCKED ตาม Precondition และข้อค้าง ไม่ใช้คลิก Mock-up แทน
- Precondition/reset: BLOCKED: report-screen เป็น placeholder; ไม่มี FR/Flow/ตารางรายงานใน v2; ต้องมีระบบจริงบน Ubuntu และผู้ตรวจนับมือ; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: ชุด D23 รวม 20 ใบ: วันที่ 2026-01-05 สิบใบ และ 2026-01-06 สิบใบ; ต่อวัน ใบ1–8 จ่ายแล้ว ราคา 50,55 สลับกัน รวม 420; ใบ9 ยังไม่จ่าย 50, ใบ10 ค้างจ่าย 55; ต่อวันใบ1–4 หน้าร้านช่วง12:00,ใบ5–8 กลับบ้านช่วง18:00; เมนู A=50/B=55 จานละ1; รวมจ่ายแล้วสองวัน840 บาท
- data-testid และ scope: report-screen ใช้ยืนยันช่องว่างเท่านั้น; ตัวเลือกช่วงวันที่/ปุ่มดูรายงาน/ตารางและ selector จริง MISSING
- ขั้นตอน:

  1. เตรียม D23 ในระบบทดสอบ ตรวจสถานะ/วันที่/เมนู/ช่องทาง/เวลารับรู้ด้วยข้อมูลอ้างอิงและนับมือ 20 ใบ
  2. เลือก 2026-01-05 ถึง 2026-01-06 กดดูรายงานพร้อม t0 และจับ t1 เมื่อตารางแสดงบนเครื่อง Ubuntu
  3. เทียบยอดรวม840 รายวัน420 แต่ละวัน; เมนู A รวม400/Bรวม440; ช่องทางหน้าร้าน420/กลับบ้าน420; ตรวจการแยกช่วงเวลาจากข้อมูล
  4. เลือกวันเดียวที่ระบบรองรับและตรวจยอดอ้างอิง420 โดยบันทึกนิยามขอบวันที่และช่วงเวลาที่ได้รับคำยืนยันก่อนตัดสิน

- Expected result: ตารางแสดง t1−t0 ≤5 วินาที; ยอดจ่ายแล้วจาก20ใบตรง840 คลาดเคลื่อน0บาท; แยกมิติได้ตาม US; การตีความขอบวันที่/ช่วงเวลารอคำตอบ
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: 20 ใบของชุดทดสอบ เทียบผลรวมเฉพาะสถานะ “จ่ายแล้ว” คลาดเคลื่อน 0 บาท; ตารางแสดงภายใน 5 วินาทีบน Ubuntu; CSV เปิดด้วย LibreOffice ได้
- สมมติฐาน/ข้อค้าง: Q-M23: วันนับยอด/เขตเวลา/ช่วงเวลา/คืนหรือเปลี่ยนหลังจ่ายไม่มีข้อมูล; fixture มีเฉพาะจ่ายแล้วไม่คืน ลดความกำกวมแต่ไม่ตอบนโยบายทั้งหมด
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-23-2"></a>

## TS-US-23-2 — ส่งออก CSV และเปิดด้วย LibreOffice

- US: US-23
- เจ้าของ: manager
- ประเภท: ทางเลือก
- AC ต้นฉบับเต็ม: เลือกช่วงวันที่แล้วรายงานแสดงภายใน 5 วินาที (นับจากกด “ดูรายงาน” จนตารางแสดงบนเครื่อง Ubuntu ในร้าน) ยอดรวมตรงกับผลรวมออเดอร์สถานะ “จ่ายแล้ว” ที่นับมือจาก 20 ใบของชุดทดสอบ (คลาดเคลื่อน 0 บาท) และดาวน์โหลด CSV เปิดด้วย LibreOffice ได้
- clause ที่ตรวจ: ดาวน์โหลด CSV เปิดด้วย LibreOffice ได้
- Functional assertions: ดาวน์โหลดได้และ LibreOffice เปิดได้; ไม่กำหนดชื่อไฟล์/encoding/delimiter/ลำดับคอลัมน์เอง; ความตรงกับรายงานใช้เป็นการตรวจประกอบ
- NFR ที่แยกจาก functional: รหัส NFR=MISSING; AC มี 5 วินาทีจากกดดูรายงานจนตารางแสดงบน Ubuntu; ความตรงของยอด 0 บาทจาก 20 ใบและ CSV ต้องแยกตรวจ; ไม่สร้างรหัสใหม่
- FR / Flow / Screen: FR=MISSING / Flow=MISSING / Screen รายงานทำงานจริง=MISSING: US-23 ไม่อยู่ใน FR/Flow v2; report-screen (SCR-15 สำหรับตรวจสิทธิ์ US-25) เป็น placeholder ไม่ใช่รายงาน US-23; ฐาน AC ../../../docs/case-study-source.md
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: จำเป็นต้องมีระบบจริงหรือฟีเจอร์/ข้อมูลที่ Input ยังไม่มี; BLOCKED ตาม Precondition และข้อค้าง ไม่ใช้คลิก Mock-up แทน
- Precondition/reset: BLOCKED: ไม่มีปุ่ม export หรือ CSV จริงใน UI v2; ต้องมีรายงานระบบจริงและ LibreOffice ให้คนตรวจ; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: ข้อมูล D23 เดียวกับ TS-US-23-1; ชื่อเมนูจำลองภาษาไทย; CSV ที่ระบบสร้างจากรายงานนั้น ไม่มีไฟล์ให้เปิดในรอบนี้
- data-testid และ scope: report-screen เป็น placeholder; ปุ่ม/ลิงก์ดาวน์โหลด CSV MISSING; LibreOffice ไม่มี data-testid ของเว็บ
- ขั้นตอน:

  1. สร้างรายงาน D23 และกดส่งออกเมื่อระบบรองรับ
  2. เก็บไฟล์ดาวน์โหลดจริง เปิดด้วย LibreOffice
  3. ให้ผู้ตรวจยืนยันว่าเปิดอ่านคอลัมน์/รายการได้ และเทียบข้อมูลกับรายงาน โดยจดการตั้งค่า import จริง

- Expected result: ดาวน์โหลดได้และ LibreOffice เปิดได้; ไม่กำหนดชื่อไฟล์/encoding/delimiter/ลำดับคอลัมน์เอง; ความตรงกับรายงานใช้เป็นการตรวจประกอบ
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: 20 ใบของชุดทดสอบ เทียบผลรวมเฉพาะสถานะ “จ่ายแล้ว” คลาดเคลื่อน 0 บาท; ตารางแสดงภายใน 5 วินาทีบน Ubuntu; CSV เปิดด้วย LibreOffice ได้
- สมมติฐาน/ข้อค้าง: ต้องใช้ระบบจริงเพื่อได้ export จึง automation=mock-not-testable แม้ขั้นสุดท้ายต้องใช้คน; ไม่มีผล manual หรือไฟล์ CSV รอบนี้
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-23-3"></a>

## TS-US-23-3 — ออเดอร์ยังไม่จ่ายหรือค้างจ่ายไม่รวมยอดรายงาน

- US: US-23
- เจ้าของ: manager
- ประเภท: ข้อยกเว้น
- AC ต้นฉบับเต็ม: เลือกช่วงวันที่แล้วรายงานแสดงภายใน 5 วินาที (นับจากกด “ดูรายงาน” จนตารางแสดงบนเครื่อง Ubuntu ในร้าน) ยอดรวมตรงกับผลรวมออเดอร์สถานะ “จ่ายแล้ว” ที่นับมือจาก 20 ใบของชุดทดสอบ (คลาดเคลื่อน 0 บาท) และดาวน์โหลด CSV เปิดด้วย LibreOffice ได้
- clause ที่ตรวจ: ยอดรวมตรงผลรวมออเดอร์สถานะ “จ่ายแล้ว” จาก 20 ใบ คลาดเคลื่อน 0 บาท
- Functional assertions: ยอดรายงานเป็น840 ไม่ใช่1,050; คลาดเคลื่อน0บาทจากผลรวมเฉพาะจ่ายแล้ว; เป็นผลที่อนุมานตรงจากตัวกรองสถานะ AC
- NFR ที่แยกจาก functional: รหัส NFR=MISSING; AC มี 5 วินาทีจากกดดูรายงานจนตารางแสดงบน Ubuntu; ความตรงของยอด 0 บาทจาก 20 ใบและ CSV ต้องแยกตรวจ; ไม่สร้างรหัสใหม่
- FR / Flow / Screen: FR=MISSING / Flow=MISSING / Screen รายงานทำงานจริง=MISSING: US-23 ไม่อยู่ใน FR/Flow v2; report-screen (SCR-15 สำหรับตรวจสิทธิ์ US-25) เป็น placeholder ไม่ใช่รายงาน US-23; ฐาน AC ../../../docs/case-study-source.md
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: จำเป็นต้องมีระบบจริงหรือฟีเจอร์/ข้อมูลที่ Input ยังไม่มี; BLOCKED ตาม Precondition และข้อค้าง ไม่ใช้คลิก Mock-up แทน
- Precondition/reset: BLOCKED: ไม่มีระบบรายงาน; เตรียม D23 20 ใบรวมสถานะต่างกันตาม TS-US-23-1; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: จ่ายแล้ว16ใบ=840; ยังไม่จ่าย2ใบ=100; ค้างจ่าย2ใบ=110; ผลรวมทั้ง20ใบ=1,050 เป็นค่าล่อให้ตรวจนับผิด
- data-testid และ scope: ตัวกรองและตารางรายงาน MISSING; front-payment-status ใช้ดูสถานะ mock แต่ไม่แทนตารางจริง
- ขั้นตอน:

  1. นับมือแยกจ่ายแล้ว/ยังไม่จ่าย/ค้างจ่ายครบ20ใบ
  2. เลือกช่วงรายงานเดียวกับ D23 แล้วเทียบยอดกับ840และยอดรวมทุกสถานะ1,050
  3. หากพบการนำใบไม่จ่ายเข้ายอด บันทึก ID และส่วนต่างที่ผิด

- Expected result: ยอดรายงานเป็น840 ไม่ใช่1,050; คลาดเคลื่อน0บาทจากผลรวมเฉพาะจ่ายแล้ว; เป็นผลที่อนุมานตรงจากตัวกรองสถานะ AC
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: 20 ใบของชุดทดสอบ เทียบผลรวมเฉพาะสถานะ “จ่ายแล้ว” คลาดเคลื่อน 0 บาท; ตารางแสดงภายใน 5 วินาทีบน Ubuntu; CSV เปิดด้วย LibreOffice ได้
- สมมติฐาน/ข้อค้าง: การเปลี่ยนสถานะย้อนหลังและคืนเงินจริงยังรอยืนยัน ไม่รวมใน fixture นี้
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-23-4"></a>

## TS-US-23-4 — ช่วงวันที่ไม่ถูกต้องหรือไม่มีรายการ

- US: US-23
- เจ้าของ: manager
- ประเภท: ผิดพลาด
- AC ต้นฉบับเต็ม: เลือกช่วงวันที่แล้วรายงานแสดงภายใน 5 วินาที (นับจากกด “ดูรายงาน” จนตารางแสดงบนเครื่อง Ubuntu ในร้าน) ยอดรวมตรงกับผลรวมออเดอร์สถานะ “จ่ายแล้ว” ที่นับมือจาก 20 ใบของชุดทดสอบ (คลาดเคลื่อน 0 บาท) และดาวน์โหลด CSV เปิดด้วย LibreOffice ได้
- clause ที่ตรวจ: เลือกช่วงวันที่เพื่อดูรายงาน; ต้นฉบับไม่กำหนดผลช่วงผิดหรือว่าง
- Functional assertions: ไม่มีข้อมูลว่าต้องปฏิเสธ สลับวัน แสดงศูนย์ หรือตารางว่าง; BLOCKED ไม่กำหนดผลขึ้นเอง
- NFR ที่แยกจาก functional: รหัส NFR=MISSING; AC มี 5 วินาทีจากกดดูรายงานจนตารางแสดงบน Ubuntu; ความตรงของยอด 0 บาทจาก 20 ใบและ CSV ต้องแยกตรวจ; ไม่สร้างรหัสใหม่
- FR / Flow / Screen: FR=MISSING / Flow=MISSING / Screen รายงานทำงานจริง=MISSING: US-23 ไม่อยู่ใน FR/Flow v2; report-screen (SCR-15 สำหรับตรวจสิทธิ์ US-25) เป็น placeholder ไม่ใช่รายงาน US-23; ฐาน AC ../../../docs/case-study-source.md
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: จำเป็นต้องมีระบบจริงหรือฟีเจอร์/ข้อมูลที่ Input ยังไม่มี; BLOCKED ตาม Precondition และข้อค้าง ไม่ใช้คลิก Mock-up แทน
- Precondition/reset: BLOCKED: ไม่มีฟอร์มรายงาน/นโยบาย validation; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: เริ่ม2026-01-06 สิ้นสุด2026-01-05; ช่วงว่าง2026-01-07 ที่ไม่มี D23
- data-testid และ scope: selector วันที่และข้อความผล MISSING
- ขั้นตอน:

  1. ในระบบที่พร้อมทดลองกรอกช่วงกลับด้าน แล้วช่วงที่ไม่มีรายการแยกกัน
  2. เก็บผลหน้าจอ/ไฟล์ export ถ้ามีและส่งเจ้าของข้อกำหนดยืนยันก่อนตั้งเกณฑ์

- Expected result: ไม่มีข้อมูลว่าต้องปฏิเสธ สลับวัน แสดงศูนย์ หรือตารางว่าง; BLOCKED ไม่กำหนดผลขึ้นเอง
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: 20 ใบของชุดทดสอบ เทียบผลรวมเฉพาะสถานะ “จ่ายแล้ว” คลาดเคลื่อน 0 บาท; ตารางแสดงภายใน 5 วินาทีบน Ubuntu; CSV เปิดด้วย LibreOffice ได้
- สมมติฐาน/ข้อค้าง: Q-M23: ขอรูปแบบผลค่าผิด/ไม่มีรายการ รวมพฤติกรรม export กรณีว่าง
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-24-1"></a>

## TS-US-24-1 — ประวัติชื่อวัตถุดิบ เวลา ผู้กด และจำนวนรายสัปดาห์

- US: US-24
- เจ้าของ: manager
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: เมื่อครัวกด “วัตถุดิบหมด” ระบบบันทึกชื่อวัตถุดิบ เวลา และผู้กด และหน้าประวัติแสดงจำนวนครั้งต่อสัปดาห์ ตรวจสอบกับการกดทดสอบ 10 ครั้ง พบรายการอย่างน้อย 9 จาก 10
- clause ที่ตรวจ: กดวัตถุดิบหมด→บันทึกชื่อ เวลา ผู้กด; หน้าประวัติแสดงจำนวนครั้งต่อสัปดาห์;10ครั้ง พบอย่างน้อย9จาก10
- Functional assertions: พบรายการตรงชื่อวัตถุดิบ/เวลา/ผู้กดอย่างน้อย9จาก10; หน้าประวัติแสดงความถี่รายสัปดาห์เทียบการกดจริง chicken5/egg3/rice2; ถ้าขาดเหตุการณ์ต้องรายงานจำนวนที่ขาดและส่วนต่าง ไม่ลด expected count เพื่อให้ผ่าน
- NFR ที่แยกจาก functional: รหัส NFR=MISSING; AC มีข้อมูลตรวจสอบย้อนกลับชื่อวัตถุดิบ/เวลา/ผู้กดและความครบอย่างน้อย 9 จาก 10; ไม่มี SLA เวลาแสดงผลหรือระยะเก็บ log
- FR / Flow / Screen: FR=MISSING / Flow=MISSING / Screen ประวัติ=MISSING: US-24 ไม่อยู่ใน FR/Flow v2; ฐาน ../../../docs/case-study-source.md; SCR-07/ปุ่ม stock ใช้ setup เท่านั้น ไม่แทนระบบประวัติ
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: จำเป็นต้องมีระบบจริงหรือฟีเจอร์/ข้อมูลที่ Input ยังไม่มี; BLOCKED ตาม Precondition และข้อค้าง ไม่ใช้คลิก Mock-up แทน
- Precondition/reset: BLOCKED: ไม่มี FR/Flow/หน้าประวัติหรือ stock audit log ใน v2; ระบบจริงและนิยามสัปดาห์ต้องพร้อม; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: 10เหตุการณ์ในสัปดาห์ทดสอบที่ยืนยันขอบแล้ว: chicken5,egg3,rice2; เวลา2026-01-06 12:00 ถึง12:09 ห่างครั้งละ1นาที; ผู้กดบัญชีสังเคราะห์ kit01/kit02 สลับ; คืนสถานะมีทุกครั้งก่อนกดหมดครั้งถัดไป
- data-testid และ scope: S-K: ingredient-select/btn-out-of-stock/btn-restock ใช้ setup mock เท่านั้น; หน้าประวัติ/ตัวนับรายสัปดาห์/selector log MISSING; payment-log ไม่ใช่ stock log
- ขั้นตอน:

  1. บันทึกตารางคาดการณ์10เหตุการณ์ ชื่อวัตถุดิบ เวลา ผู้กด
  2. ให้ครัวกดหมด10ครั้งตามลำดับและคืนสถานะมีระหว่างเหตุการณ์
  3. ผู้จัดการเปิดประวัติ เทียบแต่ละรายการกับตารางอ้างอิงและนับจำนวนต่อสัปดาห์
  4. ตรวจมุมมองประวัติเมนูที่ถูกปิดตามแมปตามความต้องการ US โดยระบุหากไม่มีรายละเอียดเชื่อมโยง

- Expected result: พบรายการตรงชื่อวัตถุดิบ/เวลา/ผู้กดอย่างน้อย9จาก10; หน้าประวัติแสดงความถี่รายสัปดาห์เทียบการกดจริง chicken5/egg3/rice2; ถ้าขาดเหตุการณ์ต้องรายงานจำนวนที่ขาดและส่วนต่าง ไม่ลด expected count เพื่อให้ผ่าน
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: กดทดสอบ 10 ครั้ง พบรายการอย่างน้อย 9 จาก 10; หน้าประวัติแสดงจำนวนครั้งต่อสัปดาห์; ชุดกดซ้ำแยกจากสิบครั้งหลัก
- สมมติฐาน/ข้อค้าง: Q-M24: นิยามสัปดาห์/เขตเวลา/ความละเอียดเวลา/การเชื่อมประวัติเมนูไม่มีข้อมูล; ACไม่ได้กำหนด tolerance ความถี่แยก จึงรายงานผลดิบและขอคำยืนยันเมื่อ log ขาด
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-24-2"></a>

## TS-US-24-2 — กดหมดซ้ำขณะวัตถุดิบยังหมด

- US: US-24
- เจ้าของ: manager
- ประเภท: ข้อยกเว้น
- AC ต้นฉบับเต็ม: เมื่อครัวกด “วัตถุดิบหมด” ระบบบันทึกชื่อวัตถุดิบ เวลา และผู้กด และหน้าประวัติแสดงจำนวนครั้งต่อสัปดาห์ ตรวจสอบกับการกดทดสอบ 10 ครั้ง พบรายการอย่างน้อย 9 จาก 10
- clause ที่ตรวจ: จำนวนครั้งต่อสัปดาห์และการบันทึกเมื่อกดหมด; ไม่ระบุการกดซ้ำ
- Functional assertions: จำนวนคาดหมายกรณีซ้ำไม่มีข้อมูล; ไม่ฟันธงเป็น1หรือ3และไม่รับรอง deduplication; BLOCKED
- NFR ที่แยกจาก functional: รหัส NFR=MISSING; AC มีข้อมูลตรวจสอบย้อนกลับชื่อวัตถุดิบ/เวลา/ผู้กดและความครบอย่างน้อย 9 จาก 10; ไม่มี SLA เวลาแสดงผลหรือระยะเก็บ log
- FR / Flow / Screen: FR=MISSING / Flow=MISSING / Screen ประวัติ=MISSING: US-24 ไม่อยู่ใน FR/Flow v2; ฐาน ../../../docs/case-study-source.md; SCR-07/ปุ่ม stock ใช้ setup เท่านั้น ไม่แทนระบบประวัติ
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: จำเป็นต้องมีระบบจริงหรือฟีเจอร์/ข้อมูลที่ Input ยังไม่มี; BLOCKED ตาม Precondition และข้อค้าง ไม่ใช้คลิก Mock-up แทน
- Precondition/reset: BLOCKED: ไม่มีประวัติจริงและนโยบายเหตุการณ์ซ้ำ; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: chicken ตั้งมีแล้วกดหมดครั้งแรก ต่อด้วยกดหมดซ้ำ2ครั้งโดยไม่ restock; เวลาและบัญชีจำลองเดิม; แยกจากชุด10ครั้งหลัก
- data-testid และ scope: S-K สำหรับปุ่ม setup; history/count/log MISSING
- ขั้นตอน:

  1. กดหมดครั้งแรกบันทึก t0 แล้วกดซ้ำอีก2ครั้ง
  2. เปิดประวัติและนับเหตุการณ์/จำนวนรายสัปดาห์
  3. ส่งผลที่สังเกตให้เจ้าของข้อกำหนดยืนยันว่าการกดหรือ transition เป็นสิ่งที่นับ

- Expected result: จำนวนคาดหมายกรณีซ้ำไม่มีข้อมูล; ไม่ฟันธงเป็น1หรือ3และไม่รับรอง deduplication; BLOCKED
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: กดทดสอบ 10 ครั้ง พบรายการอย่างน้อย 9 จาก 10; หน้าประวัติแสดงจำนวนครั้งต่อสัปดาห์; ชุดกดซ้ำแยกจากสิบครั้งหลัก
- สมมติฐาน/ข้อค้าง: Q-M24: ต้องยืนยันการนับซ้ำและกรณีข้ามสัปดาห์ก่อนตัดสินผล
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-24-3"></a>

## TS-US-24-3 — จับประวัติผิดผู้กดและความถี่ผิดจากสิบเหตุการณ์ที่ restock ก่อนทุกครั้ง

- US: US-24
- เจ้าของ: manager
- ประเภท: ข้อยกเว้น
- AC ต้นฉบับเต็ม: เมื่อครัวกด “วัตถุดิบหมด” ระบบบันทึกชื่อวัตถุดิบ เวลา และผู้กด และหน้าประวัติแสดงจำนวนครั้งต่อสัปดาห์ ตรวจสอบกับการกดทดสอบ 10 ครั้ง พบรายการอย่างน้อย 9 จาก 10
- clause ที่ตรวจ: บันทึกชื่อวัตถุดิบ เวลา ผู้กด และจำนวนครั้งต่อสัปดาห์ เทียบชุดกด 10 ครั้งอย่างน้อย 9 จาก 10
- FR / Flow / Screen: FR=MISSING / Flow=MISSING / Screen ประวัติ=MISSING: US-24 ไม่อยู่ใน FR/Flow v2; ฐาน ../../../docs/case-study-source.md; SCR-07/ปุ่ม stock ใช้ setup เท่านั้น ไม่แทนระบบประวัติ
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: แก้ D07 เชิงออกแบบ; ต้องมีระบบ/จุดแทรก fault และจุดสังเกตตาม Precondition ซึ่งยังไม่มี จึง BLOCKED การรัน. เป็นแผนตรวจจับผลผิดด้วย oracle อิสระ ไม่ใช่การเปลี่ยนชื่อ happy path; ยังไม่ได้ทำ fault หรือรันทดสอบ
- Precondition/reset: BLOCKED การรัน: U24 ไม่มี stock history/log/หน้าประวัติและตัวแทรกข้อมูลแสดงผล; ต้องมีระบบทดสอบและบันทึกเหตุการณ์อิสระจากหน้าประวัติ. ใช้สัปดาห์ fixture 2026-01-05 00:00 ถึงก่อน 2026-01-12 00:00 +07:00; ทุกเหตุการณ์อยู่กลางช่วง ไม่ใช้ตัดสินขอบสัปดาห์จริง
- Test data: ข้อมูลสังเคราะห์วันที่2026-01-06 ตามตารางอ้างอิงด้านล่าง; kit01/kit02 เป็นผู้ใช้จำลอง. ทุกครั้งตั้งวัตถุดิบให้มีและตรวจว่ามีก่อนกดหมด1ครั้ง; รวม chicken5/egg3/rice2. ตารางนี้สร้างก่อนทดสอบ ไม่ดึงจากประวัติที่กำลังตรวจ

| แถว | เวลาในวันที่ 2026-01-06 (+07:00) | วัตถุดิบ | ผู้กดจำลอง |
|---|---|---|---|
| 1 | 12:00 | chicken | kit01 |
| 2 | 12:01 | chicken | kit02 |
| 3 | 12:02 | chicken | kit01 |
| 4 | 12:03 | chicken | kit02 |
| 5 | 12:04 | chicken | kit01 |
| 6 | 12:05 | egg | kit02 |
| 7 | 12:06 | egg | kit01 |
| 8 | 12:07 | egg | kit02 |
| 9 | 12:08 | rice | kit01 |
| 10 | 12:09 | rice | kit02 |

- data-testid และ scope: MISSING: stock history/count/ตัวแทรกข้อมูลจริง; ingredient-select/btn-out-of-stock/btn-restock เป็น setup mock เท่านั้น และ payment-log ไม่ใช่ stock audit; ผูกเลขแถวอ้างอิงกับ event ID ที่ได้จริง
- ขั้นตอน:

  1. เตรียมผู้ใช้จำลองและนาฬิกา fixture; ทำครบสิบแถวตามตาราง โดย restock วัตถุดิบและยืนยันมีทุกครั้งก่อนกดหมดครั้งเดียว; เก็บผู้กด/ชื่อ/เวลาจากการกระทำและเหตุการณ์ต้นทางที่แยกจากตัวอ่านประวัติ
  2. control: เปิดประวัติและจับคู่สิบแถวกับตารางอิสระตาม event ID/การกระทำ; ตรวจชื่อ/เวลา/ผู้กดและจำนวนต่อสัปดาห์ 5/3/2. เวลาอ้างอิงในตารางเป็นระดับนาทีของ fixture; หากรูปแบบเวลาระบบยังแปลงเทียบไม่ได้ให้ BLOCKED ด้านเวลา ไม่กำหนด tolerance ของร้าน
  3. fault A: reset ชุดประวัติสิบเหตุการณ์เดิม ให้ตัวแทรกที่ข้อมูลส่งไปแสดงประวัติสลับผู้กดเฉพาะแถว1กับ2 (kit01↔kit02) โดยคง event ID ชื่อ เวลา และ log ต้นทาง; เปิดประวัติใหม่ เทียบทุกแถวกับตาราง ไม่ยอมให้จับคู่ข้ามเหตุการณ์เพียงเพราะชื่อผู้ใช้มีอยู่ในชุด
  4. fault B: reset แล้วคงรายละเอียดสิบเหตุการณ์เดิมครบ แต่เปลี่ยนค่ารวมรายสัปดาห์ที่ส่งไปแสดงจาก chicken5/egg3/rice2 เป็น chicken4/egg4/rice2; เปิดประวัติและนับอิสระทั้งชื่อวัตถุดิบและยอดรวมเพื่อจับแม้ผลรวมยัง10
  5. เก็บ input ก่อน/หลังแทรกและผลแสดงจริง แยก fault A/B จาก control; ปิดตัวแทรก คืน snapshot แล้วตรวจ control อีกครั้ง

- Expected result: control ตาม fixture ต้องเทียบชื่อ/เวลา/ผู้กดกับตาราง พบอย่างน้อย9จาก10 และตรวจความถี่กับ chicken5/egg3/rice2. Fault A ถ้าแสดงตามข้อมูลผิดจะเหลือผู้กดตรง8จาก10 ต้องชี้แถว1/2 และไม่เข้าเกณฑ์9จาก10. Fault B แม้ชื่อ/เวลา/ผู้กดครบ10และผลรวมความถี่ยัง10 ต้องตรวจพบ chicken−1 และ egg+1 เทียบรายการอิสระ. ไม่เปลี่ยน expected เป็น4/4/2เพื่อให้ตรงผลผิด
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: กดหมด 10 ครั้งอย่างน้อย 9 จาก 10 ตาม AC; restock เป็น setup ไม่นับเป็นการกดหมด. Fault A/B เป็นสำเนาชุดสิบเหตุการณ์สำหรับตรวจ oracle ไม่ใช่ผลการกดซ้ำขณะยังหมด; รายงานความถี่ผิดแยกจากสัดส่วนพบรายการ
- สมมติฐาน/ข้อค้าง: U24=MISSING; manager/ผู้ดูแล FR/Flow/UI เตรียมระบบประวัติ. เจ้าของข้อกำหนดตอบ Q-M24 เรื่องกดซ้ำ/สัปดาห์/timezone/ความละเอียดเวลาและประวัติเมนู; TS-US-24-2 ยัง BLOCKED ไม่มีจำนวนคาดหมายใหม่ของการกดซ้ำ
- Status: MOCK_NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-25-1"></a>

## TS-US-25-1 — สร้างบัญชีขอบเขตที่รับได้และเข้าใช้โดยไม่ใช้อีเมล

- US: US-25
- เจ้าของ: manager
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: สร้างบัญชีด้วยชื่อผู้ใช้ (ตัวอักษร/ตัวเลข 3–20 ตัว) และ PIN ตัวเลข 4–6 หลัก เข้าสู่ระบบด้วยชื่อผู้ใช้+PIN ใส่ PIN ผิด 5 ครั้งติดถูกล็อก 5 นาที และบัญชีสิทธิ์ครัว/หน้าร้านเปิด URL หน้ารายงานและหน้าจัดการเมนูแล้วถูกปฏิเสธ ทดสอบ 3 บัญชี × 2 หน้า ผ่าน 6 จาก 6
- clause ที่ตรวจ: ชื่อผู้ใช้ตัวอักษร/ตัวเลข3–20ตัว; PINตัวเลข4–6หลัก; เข้าระบบชื่อผู้ใช้+PIN ไม่ใช้อีเมล; บทบาทครัว/หน้าร้าน/ผู้จัดการ
- Functional assertions: รับชื่อขอบ3/20ตัวและPIN4/5/6หลักได้; loginด้วยชื่อและPINโดยไม่ใช้อีเมล; ตรงบทบาทที่เลือกในmock
- NFR ที่แยกจาก functional: NFR-18: ความปลอดภัยข้อมูลบัญชี/ล็อก 5 นาที/ปฏิเสธ URL; auto ตรวจเพียงการจำลอง UI; server authentication/authorization จริงแยก TS-US-25-5
- FR / Flow / Screen: FR-25 / NFR-18 ใน ../step-00-input/fr-nfr-v2.md; MRG-26/27/28 ใน ../step-00-input/flow-v2.md; SCR-13/14/15, login/accounts/menu-admin/report-screen
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: มี controls/handler ใน HTML v2 ให้รัน assertion ใน Mock-up ได้; คำว่า auto ไม่ใช่ผลรัน ไม่ยืนยัน AC ระบบจริงหรือ NFR
- Precondition/reset: R0 → M → nav-accounts; ใช้ข้อมูลสังเคราะห์ทั้งหมด; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: บัญชี a01 / PIN1234 / kitchen; b0123456789012345678 (20ตัว) / PIN123456 / front; mgr01 / PIN12345 / manager
- data-testid และ scope: S-U และ S-L; nav-kitchen/nav-front/screen-manager; อ่านรายการบัญชีภายใน section ที่มี account-username
- ขั้นตอน:

  1. สร้างทีละบัญชีด้วย account-username,account-pin,account-role กด btn-save-account โดยไม่กรอกอีเมล
  2. ตรวจ account-message และรายการบัญชีชื่อ/สิทธิ์ตรงข้อมูล
  3. ออกด้วยการเลือก role ใหม่: ครัว/หน้าร้านใช้ role-staff ผู้จัดการใช้ role-manager; เลือกชื่อใน staff-user กรอก PINถูกแล้ว btn-login
  4. ตรวจเข้าสู่หน้าของสิทธิ์ที่กำหนดได้; ทำครบทั้ง3บัญชีโดยไม่resetระหว่างการสร้างกับlogin

- Expected result: รับชื่อขอบ3/20ตัวและPIN4/5/6หลักได้; loginด้วยชื่อและPINโดยไม่ใช้อีเมล; ตรงบทบาทที่เลือกในmock
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: ชื่อผู้ใช้ตัวอักษร/ตัวเลข 3–20 ตัว; PIN ตัวเลข 4–6 หลัก; ผิด 5 ครั้งติดล็อก 5 นาที; บัญชีครัว/หน้าร้าน 3 บัญชี × 2 หน้า ผ่าน 6 จาก 6; ไม่มีอีเมล
- สมมติฐาน/ข้อค้าง: ASCIIเป็นชุดตัวอย่างที่ไม่กำกวม; ไม่สรุปชุดUnicode/ความปลอดภัยจากmock; ชุด3บัญชีนี้เป็นขอบเขตข้อมูล ไม่แทน3บัญชีครัว/หน้าร้านในTS-US-25-4
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-25-2"></a>

## TS-US-25-2 — ปฏิเสธชื่อหรือ PIN นอกขอบเขต

- US: US-25
- เจ้าของ: manager
- ประเภท: ผิดพลาด
- AC ต้นฉบับเต็ม: สร้างบัญชีด้วยชื่อผู้ใช้ (ตัวอักษร/ตัวเลข 3–20 ตัว) และ PIN ตัวเลข 4–6 หลัก เข้าสู่ระบบด้วยชื่อผู้ใช้+PIN ใส่ PIN ผิด 5 ครั้งติดถูกล็อก 5 นาที และบัญชีสิทธิ์ครัว/หน้าร้านเปิด URL หน้ารายงานและหน้าจัดการเมนูแล้วถูกปฏิเสธ ทดสอบ 3 บัญชี × 2 หน้า ผ่าน 6 จาก 6
- clause ที่ตรวจ: ชื่อผู้ใช้ตัวอักษร/ตัวเลข3–20ตัว และPINตัวเลข4–6หลัก
- Functional assertions: ไม่สร้างบัญชีที่ชื่อนอกช่วงหรือมีอักขระไม่ใช่ตัวอักษร/ตัวเลข หรือPINนอกช่วง/ไม่ใช่ตัวเลข; mockคาดข้อความปฏิเสธ
- NFR ที่แยกจาก functional: NFR-18: ความปลอดภัยข้อมูลบัญชี/ล็อก 5 นาที/ปฏิเสธ URL; auto ตรวจเพียงการจำลอง UI; server authentication/authorization จริงแยก TS-US-25-5
- FR / Flow / Screen: FR-25 / NFR-18 ใน ../step-00-input/fr-nfr-v2.md; MRG-26/27/28 ใน ../step-00-input/flow-v2.md; SCR-13/14/15, login/accounts/menu-admin/report-screen
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: มี controls/handler ใน HTML v2 ให้รัน assertion ใน Mock-up ได้; คำว่า auto ไม่ใช่ผลรัน ไม่ยืนยัน AC ระบบจริงหรือ NFR
- Precondition/reset: R0 → M → nav-accounts; reset ใหม่ต่อแถวเพื่อไม่ให้ผลชื่อซ้ำปน; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: ชื่อ: a1 (2ตัว), a01234567890123456789 (21ตัว), ab!, ว่าง โดยPIN1234; PIN:123 (3หลัก),1234567 (7หลัก),12a4,ว่าง โดยชื่อ valid01; role=kitchen
- data-testid และ scope: S-U: account-username/pin/role, btn-save-account, account-message; S-L staff-user options ตรวจไม่มีบัญชีที่ถูกปฏิเสธ
- ขั้นตอน:

  1. กรอกค่าที่ผิดหนึ่งช่องต่อแถวพร้อมค่าถูกช่องอื่น แล้วกดสร้าง
  2. อ่านข้อความและตรวจไม่เพิ่มบัญชีในรายการชื่อ; เปิดloginตรวจไม่มีบัญชีใหม่จากแถวนั้น
  3. ทำทั้ง8แถวแยกกันและบันทึกค่าขอบ/ผลที่พบ

- Expected result: ไม่สร้างบัญชีที่ชื่อนอกช่วงหรือมีอักขระไม่ใช่ตัวอักษร/ตัวเลข หรือPINนอกช่วง/ไม่ใช่ตัวเลข; mockคาดข้อความปฏิเสธ
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: ชื่อผู้ใช้ตัวอักษร/ตัวเลข 3–20 ตัว; PIN ตัวเลข 4–6 หลัก; ผิด 5 ครั้งติดล็อก 5 นาที; บัญชีครัว/หน้าร้าน 3 บัญชี × 2 หน้า ผ่าน 6 จาก 6; ไม่มีอีเมล
- สมมติฐาน/ข้อค้าง: ACไม่กำหนดถ้อยคำerrorหรือชุดอักขระUnicodeที่อนุญาต; 8แถวเป็นfixture ไม่เพิ่มจำนวนบังคับในAC
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-25-3"></a>

## TS-US-25-3 — PIN ผิดติดกัน 5 ครั้ง ล็อก 5 นาทีจำลอง

- US: US-25
- เจ้าของ: manager
- ประเภท: ผิดพลาด
- AC ต้นฉบับเต็ม: สร้างบัญชีด้วยชื่อผู้ใช้ (ตัวอักษร/ตัวเลข 3–20 ตัว) และ PIN ตัวเลข 4–6 หลัก เข้าสู่ระบบด้วยชื่อผู้ใช้+PIN ใส่ PIN ผิด 5 ครั้งติดถูกล็อก 5 นาที และบัญชีสิทธิ์ครัว/หน้าร้านเปิด URL หน้ารายงานและหน้าจัดการเมนูแล้วถูกปฏิเสธ ทดสอบ 3 บัญชี × 2 หน้า ผ่าน 6 จาก 6
- clause ที่ตรวจ: ใส่ PIN ผิด 5 ครั้งติดถูกล็อก 5 นาที
- Functional assertions: เส้นทาง login ปฏิเสธ PIN ผิด เข้าสถานะล็อก และปฏิเสธ PIN ถูกระหว่างล็อก; จำนวนครั้งและระยะล็อกต้องตรวจแยกทั้ง clock จำลองและ NFR-18 จริง
- NFR ที่แยกจาก functional: NFR-18: ความปลอดภัยข้อมูลบัญชี/ล็อก 5 นาที/ปฏิเสธ URL; auto ตรวจเพียงการจำลอง UI; server authentication/authorization จริงแยก TS-US-25-5
- FR / Flow / Screen: FR-25 / NFR-18 ใน ../step-00-input/fr-nfr-v2.md; MRG-26/27/28 ใน ../step-00-input/flow-v2.md; SCR-13/14/15, login/accounts/menu-admin/report-screen
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: มี controls/handler ใน HTML v2 ให้รัน assertion ใน Mock-up ได้; คำว่า auto ไม่ใช่ผลรัน ไม่ยืนยัน AC ระบบจริงหรือ NFR
- Precondition/reset: R0 → role-manager; เลือก demomanager; ยังไม่ล็อก; เวลาเริ่ม12:00+07:00; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: PINผิด9999ห้าครั้งต่อเนื่อง; PINถูก0000; เวลา12:04ยังอยู่ในล็อกและ12:05ครบ5นาที
- data-testid และ scope: S-L: staff-user,staff-pin,btn-login,auth-message,screen-manager; sim-clock; ปุ่ม+1นาทีไม่มีtestid ใช้ button[data-action=advance][data-minutes="1"] ส่วนกลาง
- ขั้นตอน:

  1. เลือกบัญชีและเติมPINผิดใหม่ทุกครั้งแล้วกดloginรวม5ครั้งโดยไม่resetหรือคั่นด้วยPINถูก
  2. ตรวจครั้งที่5มีข้อความล็อก5นาที; ทันทีหลังล็อกใส่PINถูกต้องยังถูกปฏิเสธ
  3. กด+1นาที4ครั้งตรวจเวลา12:04 แล้วใส่PINถูกต้องยังถูกปฏิเสธ
  4. กด+1นาทีอีกครั้งตรวจเวลา12:05 ใส่PINถูกและตรวจเข้าใช้ได้ในfixture

- Expected result: ล็อกหลังผิด5ครั้งติดและยังเข้าไม่ได้ในช่วง5นาที; mockเข้าได้เมื่อครบ5นาที; ไม่ใช้btn-advance-10mอ้างขอบ5นาที
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: ชื่อผู้ใช้ตัวอักษร/ตัวเลข 3–20 ตัว; PIN ตัวเลข 4–6 หลัก; ผิด 5 ครั้งติดล็อก 5 นาที; บัญชีครัว/หน้าร้าน 3 บัญชี × 2 หน้า ผ่าน 6 จาก 6; ไม่มีอีเมล
- สมมติฐาน/ข้อค้าง: TS-US-25-101ตรวจPINผิดครั้งเดียวเท่านั้น จึงไม่แทนกรณีนี้; ขอบวินาที/นาฬิกาserver/ขอบเขตล็อกจริงรอQ-25และTS-US-25-5
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-25-4"></a>

## TS-US-25-4 — ครัว/หน้าร้านถูกปฏิเสธ URL สองหน้าครบ 6 กรณี

- US: US-25
- เจ้าของ: manager
- ประเภท: ข้อยกเว้น
- AC ต้นฉบับเต็ม: สร้างบัญชีด้วยชื่อผู้ใช้ (ตัวอักษร/ตัวเลข 3–20 ตัว) และ PIN ตัวเลข 4–6 หลัก เข้าสู่ระบบด้วยชื่อผู้ใช้+PIN ใส่ PIN ผิด 5 ครั้งติดถูกล็อก 5 นาที และบัญชีสิทธิ์ครัว/หน้าร้านเปิด URL หน้ารายงานและหน้าจัดการเมนูแล้วถูกปฏิเสธ ทดสอบ 3 บัญชี × 2 หน้า ผ่าน 6 จาก 6
- clause ที่ตรวจ: บัญชีครัว/หน้าร้านเปิด URL รายงานและจัดการเมนูถูกปฏิเสธ3บัญชี×2หน้า ผ่าน6จาก6
- Functional assertions: routeที่ถูกห้ามถูกปฏิเสธ6จาก6ในmock; ไม่ใช้การซ่อนnavเป็นหลักฐาน; report-screenใช้ตรวจสิทธิ์เท่านั้นไม่พิสูจน์US-23
- NFR ที่แยกจาก functional: NFR-18: ความปลอดภัยข้อมูลบัญชี/ล็อก 5 นาที/ปฏิเสธ URL; auto ตรวจเพียงการจำลอง UI; server authentication/authorization จริงแยก TS-US-25-5
- FR / Flow / Screen: FR-25 / NFR-18 ใน ../step-00-input/fr-nfr-v2.md; MRG-26/27/28 ใน ../step-00-input/flow-v2.md; SCR-13/14/15, login/accounts/menu-admin/report-screen
- automation: auto
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: มี controls/handler ใน HTML v2 ให้รัน assertion ใน Mock-up ได้; คำว่า auto ไม่ใช่ผลรัน ไม่ยืนยัน AC ระบบจริงหรือ NFR
- Precondition/reset: R0 → M สร้างบัญชีตามข้อมูล; แยก login ใหม่ต่อบัญชี; ก่อนเริ่มตรวจ manager เปิดสองrouteได้เพื่อไม่ให้ assertion hidden ผ่านเพราะหน้าไม่เคยมี; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: kit01/kitchen,kit02/kitchen,front01/front ทุกบัญชีPIN1234; สัดส่วน2ครัว+1หน้าร้านเป็นfixture; routes #/manager/menu และ #/manager/reports
- data-testid และ scope: S-U/S-L; auth-message,menu-admin,report-screen,screen-manager; เปิดhash URLตรงในแท็บเดิมโดยไม่reloadไฟล์
- ขั้นตอน:

  1. ผู้จัดการเปิดแต่ละrouteตรง ตรวจmenu-admin/report-screenแสดงได้ แล้วสร้าง3บัญชี
  2. เลือกrole-staff loginบัญชีแรกให้สำเร็จ แล้วตั้งhashเป็น#/manager/menuโดยตรง
  3. ตรวจauth-messageมีคำว่าปฏิเสธและไม่แสดงmenu-admin; ทดสอบ#/manager/reportsและไม่แสดงreport-screen
  4. ทำซ้ำสำหรับอีก2บัญชี เก็บตาราง6ช่อง account×routeพร้อมactual/ภาพเมื่อมีการรัน

- Expected result: routeที่ถูกห้ามถูกปฏิเสธ6จาก6ในmock; ไม่ใช้การซ่อนnavเป็นหลักฐาน; report-screenใช้ตรวจสิทธิ์เท่านั้นไม่พิสูจน์US-23
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: ชื่อผู้ใช้ตัวอักษร/ตัวเลข 3–20 ตัว; PIN ตัวเลข 4–6 หลัก; ผิด 5 ครั้งติดล็อก 5 นาที; บัญชีครัว/หน้าร้าน 3 บัญชี × 2 หน้า ผ่าน 6 จาก 6; ไม่มีอีเมล
- สมมติฐาน/ข้อค้าง: ไม่มีserver/APIจริงในHTML จึงไม่รับรองauthorizationจริง; นโยบายสิทธิ์หน้าอื่นไม่เพิ่ม; สัดส่วนบัญชีจริงรอQ-25
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-25-5"></a>

## TS-US-25-5 — ตรวจบัญชี ล็อก และสิทธิ์ URL ที่ระบบจริง

- US: US-25
- เจ้าของ: manager
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: สร้างบัญชีด้วยชื่อผู้ใช้ (ตัวอักษร/ตัวเลข 3–20 ตัว) และ PIN ตัวเลข 4–6 หลัก เข้าสู่ระบบด้วยชื่อผู้ใช้+PIN ใส่ PIN ผิด 5 ครั้งติดถูกล็อก 5 นาที และบัญชีสิทธิ์ครัว/หน้าร้านเปิด URL หน้ารายงานและหน้าจัดการเมนูแล้วถูกปฏิเสธ ทดสอบ 3 บัญชี × 2 หน้า ผ่าน 6 จาก 6
- clause ที่ตรวจ: ACทั้งชุดข้อมูลบัญชี/login/ล็อก5ครั้ง5นาที/ปฏิเสธURL3×2=6จาก6
- Functional assertions: ระบบสร้างบัญชีและ login ตามชื่อ/PIN โดยไม่ใช้อีเมล; ตรวจค่าขอบบัญชี; การล็อกและปฏิเสธ URL ด้วยสิทธิ์ต้องมีหลักฐานระบบจริงตาม NFR-18
- NFR ที่แยกจาก functional: NFR-18: ความปลอดภัยข้อมูลบัญชี/ล็อก 5 นาที/ปฏิเสธ URL; auto ตรวจเพียงการจำลอง UI; server authentication/authorization จริงแยก TS-US-25-5
- FR / Flow / Screen: FR-25 / NFR-18 ใน ../step-00-input/fr-nfr-v2.md; MRG-26/27/28 ใน ../step-00-input/flow-v2.md; SCR-13/14/15, login/accounts/menu-admin/report-screen
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: จำเป็นต้องมีระบบจริงหรือฟีเจอร์/ข้อมูลที่ Input ยังไม่มี; BLOCKED ตาม Precondition และข้อค้าง ไม่ใช้คลิก Mock-up แทน
- Precondition/reset: BLOCKED: ไม่มีbackend/บัญชีระบบทดสอบ/นาฬิกาserver; ใช้เฉพาะบัญชีสังเคราะห์บนระบบที่ได้รับอนุญาต; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: ชุดค่าถูกและผิดตามTS-US-25-1/2; PINผิด5ครั้ง; เวลา299วินาทีและ300วินาทีหลังเริ่มล็อกเป็นจุดตรวจเสนอ; 3บัญชีสิทธิ์ครัว/หน้าร้านตามTS-US-25-4
- data-testid และ scope: URLจริง/endpoint/selectorระบบจริง MISSING; hash routesของmockไม่ใช่URLหลักฐานserver
- ขั้นตอน:

  1. สร้างและloginข้อมูลถูกโดยไม่ใช้อีเมล ตรวจค่าผิดไม่สร้างบัญชี
  2. ทำPINผิด5ครั้งติดและจับเวลาจริง; ทดลองPINถูกระหว่างล็อกและเมื่อครบ5นาที เก็บเหตุการณ์server
  3. login3บัญชีครัว/หน้าร้านแล้วเปิดURLรายงานและจัดการเมนูโดยตรงครบ6กรณี
  4. ตรวจresponseและข้อมูลที่ส่งกลับว่าถูกปฏิเสธตามสิทธิ์ ไม่อาศัยเพียงDOMที่ซ่อน

- Expected result: ชื่อ/PINอยู่ในเกณฑ์และloginได้; ล็อก5นาทีหลังผิด5ครั้ง; ปฏิเสธสองหน้า6จาก6บนระบบจริงเมื่อมีผลรัน
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: ชื่อผู้ใช้ตัวอักษร/ตัวเลข 3–20 ตัว; PIN ตัวเลข 4–6 หลัก; ผิด 5 ครั้งติดล็อก 5 นาที; บัญชีครัว/หน้าร้าน 3 บัญชี × 2 หน้า ผ่าน 6 จาก 6; ไม่มีอีเมล
- สมมติฐาน/ข้อค้าง: Q-25: ขอบเขตตัวนับล็อก/ข้ามอุปกรณ์/ชุดอักขระและสิทธิ์อื่นยังไม่มีข้อมูล; ไม่กำหนดHTTP status/การเก็บPIN/กู้บัญชีเอง
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-25-6"></a>

## TS-US-25-6 — ชื่อบัญชีซ้ำและขอบเขตการจัดการบัญชี

- US: US-25
- เจ้าของ: manager
- ประเภท: ข้อยกเว้น
- AC ต้นฉบับเต็ม: สร้างบัญชีด้วยชื่อผู้ใช้ (ตัวอักษร/ตัวเลข 3–20 ตัว) และ PIN ตัวเลข 4–6 หลัก เข้าสู่ระบบด้วยชื่อผู้ใช้+PIN ใส่ PIN ผิด 5 ครั้งติดถูกล็อก 5 นาที และบัญชีสิทธิ์ครัว/หน้าร้านเปิด URL หน้ารายงานและหน้าจัดการเมนูแล้วถูกปฏิเสธ ทดสอบ 3 บัญชี × 2 หน้า ผ่าน 6 จาก 6
- clause ที่ตรวจ: USจัดการบัญชีพนักงาน; ACระบุสร้างและloginแต่ไม่ระบุชื่อซ้ำหรือแก้/ลบบัญชี
- Functional assertions: ผลร้านสำหรับชื่อซ้ำ/ตัวพิมพ์และแก้/ลบบัญชีไม่มีข้อมูล; mockอาจปฏิเสธชื่อซ้ำตามโค้ดแต่ไม่ใช่oracleธุรกิจ; ประเด็นนี้BLOCKED
- NFR ที่แยกจาก functional: NFR-18: ความปลอดภัยข้อมูลบัญชี/ล็อก 5 นาที/ปฏิเสธ URL; auto ตรวจเพียงการจำลอง UI; server authentication/authorization จริงแยก TS-US-25-5
- FR / Flow / Screen: FR-25 / NFR-18 ใน ../step-00-input/fr-nfr-v2.md; MRG-26/27/28 ใน ../step-00-input/flow-v2.md; SCR-13/14/15, login/accounts/menu-admin/report-screen
- automation: manual
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: มีขั้นตรวจภาพ/ข้อความ/ขอบเขตด้วยคนตามขั้นตอน; ยังไม่ได้ตรวจ ไม่มีผล manual และไม่ใช้ความเห็นแทนคำตอบธุรกิจที่ขาด
- Precondition/reset: R0 → M → nav-accounts; สร้าง dup01/PIN1234/kitchenหนึ่งบัญชีก่อน; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: สร้างdup01ซ้ำ แล้ว DUP01; ทดลองสังเกตเครื่องมือแก้สิทธิ์/ลบที่มีอยู่โดยไม่เพิ่มselectorเอง
- data-testid และ scope: S-U; account-message; ปุ่มแก้/ลบบัญชี MISSING ในUI v2
- ขั้นตอน:

  1. ลองสร้างชื่อซ้ำตรงตัวและต่างตัวพิมพ์ทีละกรณี
  2. ให้ผู้ตรวจบันทึกข้อความและจำนวนบัญชี แล้วเทียบกับคำถามเรื่องชื่อซ้ำ
  3. บันทึกว่าหน้านี้มีเฉพาะสร้างบัญชี ไม่มีUIแก้/ลบ โดยไม่อ้างว่าเป็นACที่ต้องมีรูปแบบใด

- Expected result: ผลร้านสำหรับชื่อซ้ำ/ตัวพิมพ์และแก้/ลบบัญชีไม่มีข้อมูล; mockอาจปฏิเสธชื่อซ้ำตามโค้ดแต่ไม่ใช่oracleธุรกิจ; ประเด็นนี้BLOCKED
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: ชื่อผู้ใช้ตัวอักษร/ตัวเลข 3–20 ตัว; PIN ตัวเลข 4–6 หลัก; ผิด 5 ครั้งติดล็อก 5 นาที; บัญชีครัว/หน้าร้าน 3 บัญชี × 2 หน้า ผ่าน 6 จาก 6; ไม่มีอีเมล
- สมมติฐาน/ข้อค้าง: Q-25: รอคำตอบก่อนกำหนดผลและสิทธิ์เปลี่ยนบัญชี; manualมีขั้นตรวจขอบเขตด้วยคน
- Status: NOT_RUN
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-26-1"></a>

## TS-US-26-1 — ติดตั้งด้วยสคริปต์เดียวและเก็บข้อมูลในร้าน

- US: US-26
- เจ้าของ: manager
- ประเภท: สำเร็จ
- AC ต้นฉบับเต็ม: ติดตั้งบน Ubuntu ด้วยสคริปต์เดียว เสร็จภายใน 30 นาที (นับจากรันสคริปต์จนเปิดหน้าเมนูจากมือถือในร้านได้) เก็บข้อมูลบนเครื่องในร้าน และเมื่อถอดสายอินเทอร์เน็ตภายนอก ยังสั่ง/เปลี่ยนสถานะ/ปิดโต๊ะได้ครบ 20 ใบของชุดทดสอบ (ยกเว้นการตรวจสอบยอดโอน PromptPay ซึ่งพนักงานยืนยันด้วยตา)
- clause ที่ตรวจ: Ubuntuเครื่องเดียว; สคริปต์เดียวเสร็จภายใน30นาทีจากรันจนมือถือเปิดเมนูได้; ข้อมูลเก็บในร้าน
- Functional assertions: สคริปต์เดียวติดตั้งระบบบนUbuntuเครื่องเดียวได้ มือถือบนWi-Fiร้านเปิดเมนูได้ และข้อมูลอยู่บนเครื่องในร้าน; ระยะเวลาติดตั้งแยก NFR-22
- NFR ที่แยกจาก functional: NFR-22: สคริปต์เดียวติดตั้ง Ubuntu ภายใน 30 นาที; NFR-16: ข้อมูลในร้าน/WAN ขาดแล้วยังทำงานครบ 20 ใบ; การเปิด file:// ไม่พิสูจน์ทั้งสอง
- FR / Flow / Screen: FR-26 / NFR-16,NFR-22 ใน ../step-00-input/fr-nfr-v2.md; MRG-29/30 ใน ../step-00-input/flow-v2.md; Screen ติดตั้ง=MISSING (ไม่มีใน mock)
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: จำเป็นต้องมีระบบจริงหรือฟีเจอร์/ข้อมูลที่ Input ยังไม่มี; BLOCKED ตาม Precondition และข้อค้าง ไม่ใช้คลิก Mock-up แทน
- Precondition/reset: BLOCKED: ไม่มีสคริปต์ติดตั้ง/ระบบจริงหรือข้อมูลรุ่นUbuntuและเครื่องทดสอบ; ต้องได้สภาพเริ่มต้นที่ยืนยันก่อนวัด; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: Ubuntuเครื่องทดสอบหนึ่งเครื่อง มือถือหนึ่งเครื่องบนWi-Fiทดสอบของร้านและเมนู/ออเดอร์สังเคราะห์; ไม่ใส่ชื่อเครื่องหรือpathจริงในเอกสารนี้
- data-testid และ scope: สคริปต์/URLเมนูจริง/ตำแหน่งจัดเก็บ MISSING; ไม่มีscreenติดตั้งในmock; btn-open-menuไม่แทนการเปิดผ่านมือถือ
- ขั้นตอน:

  1. บันทึกสภาพเครื่องUbuntu/แพ็กเกจ/สิทธิ์/เครือข่ายเริ่มต้นตามที่ตกลง
  2. เริ่มจับt0พร้อมรันสคริปต์เดียว เก็บlogติดตั้งจริง
  3. ใช้มือถือบนWi-Fiร้านเปิดหน้าเมนู บันทึกt1เมื่อเปิดได้
  4. สร้างข้อมูลจำลองหนึ่งรายการ ตรวจการตั้งค่าและข้อมูลจริงว่าอยู่บนเครื่องในร้าน พร้อมหลักฐานที่ปกปิดข้อมูลเครื่องก่อนส่งต่อ

- Expected result: t1−t0≤30นาทีโดยใช้สคริปต์เดียว; มือถือเปิดเมนูได้และข้อมูลเก็บบนเครื่องในร้าน; ไม่ใช้เวลาเปิดHTMLแทน
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: ติดตั้งด้วยสคริปต์เดียวบน Ubuntu ภายใน 30 นาที จากเริ่มรันจนมือถือเปิดเมนูได้; เก็บข้อมูลในร้าน; ถอดอินเทอร์เน็ตภายนอกแล้วสั่ง/เปลี่ยนสถานะ/ปิดโต๊ะครบ 20 ใบ ยกเว้นตรวจยอดโอน PromptPay ที่พนักงานยืนยันด้วยตา
- สมมติฐาน/ข้อค้าง: Q-26: รุ่นUbuntuฮาร์ดแวร์/สิทธิ์/แพ็กเกจ/อินเทอร์เน็ตระหว่างติดตั้งไม่มีข้อมูล; จำนวนการติดตั้งซ้ำไม่มีเกณฑ์ในAC; ไม่แต่งงบ/uptime/backup
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

<a id="design-ts-us-26-2"></a>

## TS-US-26-2 — อินเทอร์เน็ตภายนอกหลุดยังทำงานครบ 20 ใบ

- US: US-26
- เจ้าของ: manager
- ประเภท: ข้อยกเว้น
- AC ต้นฉบับเต็ม: ติดตั้งบน Ubuntu ด้วยสคริปต์เดียว เสร็จภายใน 30 นาที (นับจากรันสคริปต์จนเปิดหน้าเมนูจากมือถือในร้านได้) เก็บข้อมูลบนเครื่องในร้าน และเมื่อถอดสายอินเทอร์เน็ตภายนอก ยังสั่ง/เปลี่ยนสถานะ/ปิดโต๊ะได้ครบ 20 ใบของชุดทดสอบ (ยกเว้นการตรวจสอบยอดโอน PromptPay ซึ่งพนักงานยืนยันด้วยตา)
- clause ที่ตรวจ: ถอดอินเทอร์เน็ตภายนอกยังสั่ง/เปลี่ยนสถานะ/ปิดโต๊ะครบ20ใบ; ยกเว้นตรวจยอดโอนPromptPayที่พนักงานยืนยันด้วยตา
- Functional assertions: ทำเส้นทางสั่ง/เปลี่ยนสถานะ/ปิดโต๊ะครบทุกใบในชุด20ใบและเก็บข้อมูลในร้าน; ขั้นดูสลิปด้วยคนแยกจากตรวจโอนอัตโนมัติ; เงื่อนไขWANขาดแยก NFR-16
- NFR ที่แยกจาก functional: NFR-22: สคริปต์เดียวติดตั้ง Ubuntu ภายใน 30 นาที; NFR-16: ข้อมูลในร้าน/WAN ขาดแล้วยังทำงานครบ 20 ใบ; การเปิด file:// ไม่พิสูจน์ทั้งสอง
- FR / Flow / Screen: FR-26 / NFR-16,NFR-22 ใน ../step-00-input/fr-nfr-v2.md; MRG-29/30 ใน ../step-00-input/flow-v2.md; Screen ติดตั้ง=MISSING (ไม่มีใน mock)
- automation: mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: จำเป็นต้องมีระบบจริงหรือฟีเจอร์/ข้อมูลที่ Input ยังไม่มี; BLOCKED ตาม Precondition และข้อค้าง ไม่ใช้คลิก Mock-up แทน
- Precondition/reset: BLOCKED: ต้องติดตั้งระบบจริงบนUbuntuและLAN/Wi-Fiยังทำงาน; ไม่มีระบบดังกล่าวในInput; ใช้เครือข่ายทดลองที่ได้รับอนุญาต; ใช้ขั้นตอนร่วมที่ระบุโดยไม่พึ่ง Scenario อื่นเคยรันผ่าน
- Test data: 20ออเดอร์จำลองเรียงลำดับทดสอบ; โต๊ะ01ใช้sessionใหม่ต่อใบหลังปิด; เมนูm01ราคา50; fixtureเสนอ19ใบใช้เงินสดจำลอง และ1ใบมีสลิปสังเคราะห์ติดป้ายเพื่อให้คนตรวจขั้นตอน ไม่ใช่เงินโอนจริง
- data-testid และ scope: ระบบจริง selector/URL MISSING; S-C/S-K/S-Fเป็นจุดเชื่อมเชิงออกแบบเท่านั้น; หลักฐานWAN/ที่เก็บข้อมูลไม่ใช่data-testid
- ขั้นตอน:

  1. ยืนยันระบบบนUbuntuและLAN/Wi-Fiพร้อม แล้วถอดเฉพาะการเชื่อมต่ออินเทอร์เน็ตภายนอก เก็บหลักฐานว่ายังต่อถึงUbuntuได้
  2. ระหว่างWANขาด สร้างออเดอร์แต่ละใบจากมือถือ เก็บID แล้วครัวเปลี่ยนสถานะและหน้าร้านปิดโต๊ะของsessionนั้น
  3. ทำทั้งสามการกระทำครบทุกใบทั้ง20โดยไม่คืนWANระหว่างชุด; ตรวจข้อมูล/logอยู่บนเครื่องในร้าน
  4. แยกขั้นพนักงานดูสลิปสังเคราะห์และยืนยันด้วยตาจากความสามารถตรวจยอดโอนอัตโนมัติ; เก็บผล manual ตามที่เกิดจริง
  5. จบชุดคืนการเชื่อมต่อทดสอบและสรุปผลรายID

- Expected result: ครบทั้งสั่ง/เปลี่ยนสถานะ/ปิดโต๊ะ20จาก20ใบขณะWANขาดและข้อมูลอยู่ในร้าน; ข้อยกเว้นPromptPayต้องอาศัยคน ไม่อ้างตรวจยอดโอนออนไลน์หรือชำระจริง
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: ติดตั้งด้วยสคริปต์เดียวบน Ubuntu ภายใน 30 นาที จากเริ่มรันจนมือถือเปิดเมนูได้; เก็บข้อมูลในร้าน; ถอดอินเทอร์เน็ตภายนอกแล้วสั่ง/เปลี่ยนสถานะ/ปิดโต๊ะครบ 20 ใบ ยกเว้นตรวจยอดโอน PromptPay ที่พนักงานยืนยันด้วยตา
- สมมติฐาน/ข้อค้าง: สัดส่วน19/1และการใช้โต๊ะซ้ำเป็นfixture ไม่ใช่เกณฑ์ใหม่; ไม่มีACเรื่องLANล่ม/ไฟดับ/กู้คืน/availability%; ไม่ทำเงินจริงในชุดทดสอบ
- Status: NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

## ข้อบกพร่องจาก Input/โค้ด และข้อค้างส่งต่อ

รายการนี้เป็นผลอ่านไฟล์ ไม่ใช่ runtime failure และไม่มีผลคลิกยืนยัน ข้อคำถาม Q-M23/Q-M24 และประเด็น US-22 ด้านล่างเป็นรหัสข้อค้างในเอกสารนี้ ไม่ใช่รหัส FR/Flow ที่สร้างเพิ่ม

| ประเด็น | หลักฐาน/ผลกระทบ | ผู้รับผิดชอบตอบหรือแก้ในขั้นถัดไป | TestID ที่เกี่ยวข้อง |
|---|---|---|---|
| US-22 ไม่มีฟีเจอร์ | input-check หัวข้อแยกสิ่งที่มีจริง และ HTML customerHTML มีโหมดกลับบ้านแต่ไม่มีสวิตช์ผู้จัดการ; FR/Flow ไม่มี US นี้ | ผู้ดูแล requirement/FR/Flow/UI ต้องจัดรุ่นใหม่; เจ้าของร้านยืนยันหน้าเก่า/เปิดรับคืน | TS-US-22-1, TS-US-22-2, TS-US-22-3 |
| US-23 ยังเป็น placeholder | HTML managerHTML แสดง report-screen เพื่อทดสอบสิทธิ์ ไม่มีตาราง/ตัวกรอง/export CSV; ไม่มี FR/Flow ของ US-23 | ผู้ดูแล FR/Flow/UI; เจ้าของร้านตอบ Q-M23 เรื่องวันนับยอด เขตเวลา ช่วงเวลา ค่าผิด/ข้อมูลว่างและคืนหลังจ่าย | TS-US-23-1, TS-US-23-2, TS-US-23-3, TS-US-23-4 |
| US-24 ไม่มีประวัติ | handler stock เปลี่ยน available แต่ไม่มี stock audit/history รายสัปดาห์; payment-log ใช้เงินเท่านั้น | ผู้ดูแล FR/Flow/UI; เจ้าของร้านตอบ Q-M24 เรื่องสัปดาห์ เวลา กดซ้ำ และประวัติเมนู | TS-US-24-1, TS-US-24-2 |
| Reload ไม่เก็บ state | HTML reset สร้าง state จาก seed เมื่อเริ่มไฟล์ใหม่; ไม่มี persistence ข้าม reload | ผู้พัฒนาระบบจริง/ผู้ทดสอบ NFR; ห้ามใช้สลับบทบาทแทน refresh | TS-US-19-8, TS-US-20-4 |
| ชื่อ selector v2 ไม่ตรง fixture | rush-start/rush-end ไม่พบ; capacity-start/capacity-end พบจริง และต้องผ่าน nav-capacity; payment-summary-total ไม่พบ | ผู้ดูแลชุดรันจัด fixture รุ่นใหม่ตาม source โดยคง ID และ history; รอบนี้ไม่แก้ Input | TS-US-21-101, TS-US-21-1; ผลกระทบข้ามบทบาท TS-US-09-101 |
| ขอบรูป 2 MB | uploadImage ใช้ 2,000,000 ไบต์ใน mock; ต้นฉบับไม่ระบุ MB ฐานใด | เจ้าของข้อกำหนด Q-19; ค่า/ความละเอียดราคากับลบขณะออเดอร์ค้างยังรอยืนยัน | TS-US-19-2, TS-US-19-3, TS-US-19-7 |
| US-20 อ้าง US-14/หมายเหตุ ค. | คงข้อความเดิมตาม DI-02/DI-04; A-02/A-03 ยังไม่ยืนยัน; US-12/13 เป็นเพียงการเชื่อมที่เสนอ | เจ้าของข้อกำหนดตอบ Q-20 ก่อนปิด coverage dependency/หมายเหตุ | TS-US-20-1, TS-US-20-2, TS-US-20-3, TS-US-20-4 |
| ความจุ/X | สูตร X, เขตเวลา, รอยต่อ, คืน/เปลี่ยน, เปลี่ยน N กลางช่วง, ผลนอกช่วง/ค่าไม่ถูกต้อง ไม่มีคำตอบ; ปุ่มเวลาไม่มีระดับวินาที | เจ้าของข้อกำหนดตอบ Q-V2-CAPACITY; ผู้ทดสอบเตรียมเหตุการณ์และเวลาระบบจริง | TS-US-21-4, TS-US-21-5, TS-US-21-6 |
| PIN/สิทธิ์จริง | HTML เป็นบัญชีและ hash route จำลอง; ไม่ใช่ server authentication/authorization | เจ้าของข้อกำหนด Q-25 และผู้พัฒนาระบบ; รอชุดอักขระ/ล็อก/ชื่อซ้ำ/แก้ลบบัญชี/สิทธิ์เพิ่มเติม | TS-US-25-5, TS-US-25-6 |
| Ubuntu/ข้อมูล/ออฟไลน์ | ไม่มีสคริปต์/เครื่องจริง/ข้อมูล deployment; การอ่าน HTML ไม่พิสูจน์ติดตั้งหรืองานขณะ WAN ขาด | เจ้าของข้อกำหนด Q-26 และผู้ทดสอบ infrastructure เตรียมสภาพเริ่มต้นที่ตกลง | TS-US-26-1, TS-US-26-2 |
| หมายเหตุและข้อมูลข้ามบทบาท | หมายเหตุ ก./ค./ช. ไม่มีนิยาม; DI-06 แยกช่วง US-07/21; DI-07/A-05 สถานะยังไม่ยืนยัน; Q-V2-REFUND/STATE เรื่องคืน/เปลี่ยนยังเปิด | เจ้าของข้อกำหนด; ไม่ยืมข้อสมมติ fixture มาเป็นกฎการเงิน/สถานะ/เวลา | ข้อจำกัด setup และยอด/เวลาในชุดผู้จัดการ; เจ้าของ US อื่นคงตามเดิม |
| การรวม manifest / P01 | manifest ต้นทาง resolve จาก ../step-00-input; manifest ใหม่ resolve จากราก LAB ../.. | ผู้ตรวจอ่าน scenario-set-round-1.json; ไฟล์นี้ใช้ reference/step-02-coverage/fix-1/scenarios-manager-round-1.md | ทั้งไฟล์; ไม่แก้ manifest ต้นทาง |

A-01–A-06 จาก data-issues ยังคงเป็นสมมติฐานที่ยังไม่ยืนยัน ไม่ใช้ข้อมูลประวัติหรือสถานะผลเก่ามาแทนผลใหม่ ข้อค้างที่ต้นฉบับไม่ระบุผลจะไม่ถูกบังคับเป็น expected ว่าระบบต้องปฏิเสธ/ยอมรับเอง

## บันทึกสิ่งที่สร้างในต้นทางก่อนแก้และสิ่งที่ยังไม่ได้ทดสอบ

ต้นทางสร้างเฉพาะ [scenarios-manager.md](../step-01-fanout/manager/scenarios-manager.md) ในโฟลเดอร์ขั้นนี้: 35 Scenario เชิงออกแบบ พร้อม US/AC ตรงต้นฉบับ ดัชนีประเภท การเชื่อม fixture เดิม 2 ID และข้อค้าง ไม่สร้างหรือแก้ Input, manifest, HTML, script, fixture, ภาพ หรือผลเก่า

ตรวจเอกสารก่อนบันทึก: ID เชิงออกแบบไม่ซ้ำและต่ำกว่า 101, ทุก US-19–26 มีสำเร็จและผิดพลาด/ข้อยกเว้น, AC ทุก Scenario คัดตรงแถวต้นฉบับ, ชื่อบัญชีขอบเขตนับจำนวนอักขระ, ช่อง template ครบ และไม่มี Status ผลผ่าน การตรวจโครงสร้างนี้ไม่ใช่การรันทดสอบระบบ

ยังไม่ได้ทดสอบทั้งหมด: browser/DOM/selector visibility และ uniqueness/คลิก/ภาพ/CSV/LibreOffice, smoke fixture, ผล 3/5/6/10/20 ตัวอย่างตาม AC, refresh/persistence, LAN/Wi-Fi/เวลาจริง, หลายอุปกรณ์/concurrency/Load, Security และ server log, การติดตั้ง Ubuntu/ที่เก็บข้อมูลจริง/Availability เมื่อถอดอินเทอร์เน็ต, การชำระหรือคืนเงินจริง

สถานะเริ่มต้นของ 19 Scenario ที่เป็น auto/manual คือ NOT_RUN และ 16 Scenario ที่ต้องระบบจริง/ฟีเจอร์ที่ขาดคือ NOT_TESTABLE; กรณี oracle ธุรกิจขาดระบุ BLOCKED ในข้อค้างแม้สามารถสังเกต Mock-up ได้ ไม่มีข้อมูลจำนวนผ่าน/ไม่ผ่านจาก runtime ต้องเก็บ Actual/หลักฐานในเอกสารรุ่นใหม่เมื่อมีการรันจริง

