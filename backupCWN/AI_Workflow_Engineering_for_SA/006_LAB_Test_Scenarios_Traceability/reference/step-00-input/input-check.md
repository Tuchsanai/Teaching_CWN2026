# ตรวจ Input และที่มา — ขั้น 6.0

เวลาตรวจ (UTC): 2026-09-14T14:25:05+00:00

**ผลตรวจ Input: ครบ 9/9 ไฟล์ อ่านได้ และ snapshot v2 3/3 ไฟล์มี SHA-256 ตรงกับ provenance และต้นทางที่อ้างจริง** ไม่มี Input จำเป็นขาดสำหรับขั้น 6.0; ใช้เตรียมการออกแบบ scenario ต่อได้โดยคงข้อค้างด้านล่าง การรับรองพฤติกรรม UI/US/AC ทั้งหมดเป็น **NOT_TESTED** รอบนี้ตรวจไฟล์และอ่าน HTML เท่านั้น ไม่เปิด browser ไม่คลิก ไม่รัน JavaScript ของ UI และไม่เรียกผู้ช่วยเพิ่ม

**ใช้ผลอ้างอิง ไม่ใช่ผลที่นักศึกษารันเอง** ใช้ผล LAB 005 เพื่อกำหนด snapshot ที่ทำซ้ำได้ ไม่ถือผลตรวจหรือข้อความ PASS ของต้นทางเป็นผลรัน LAB นี้ ไม่สร้าง UI หรือผล LAB 005 แทน

ก่อนเริ่มตรวจไม่พบ `input-check.md` และ `scenario-set-round-0.json` จึงสร้างใหม่ด้วยโหมดไม่เขียนทับ หากพบ Output เดิมในการเรียกครั้งถัดไป ต้องหยุดและขอ path รุ่นใหม่ในบันทึกการสนทนา ห้ามแก้หรือเขียนทับหลักฐานเดิม

## ฐาน path และการใช้ Input

path ในตาราง Input ต่อไปนี้ relative จากโฟลเดอร์ขั้นนี้ ส่วน path ต้นทางที่ถอดจาก provenance และค่าทุกตัวใน manifest relative จากราก LAB ซึ่งอยู่ที่ `../..` ตาม prompt นี้ คำสั่งจัดเก็บใน README/สัญญาต้นแบบไม่ได้ใช้แทนขอบเขต Output ของรอบนี้

| Input ที่อ่านจริง (relative จากขั้นนี้) | รุ่น/สถานะต้นทาง | การใช้ผลอ้างอิง |
|---|---|---|
| `provenance.md` | ไม่ระบุเลขรุ่น; provenance ของ snapshot รอบนี้ | ที่มา snapshot และฐาน path ของ manifest |
| `fr-nfr-v2.md` | v2; ส่วนเอกสารระบุ EXECUTED และรอตรวจ | FR/NFR, US/AC และข้อค้างของ v2 |
| `flow-v2.md` | v2; ส่วนเอกสารระบุ EXECUTED และรอตรวจ | Flow และ mapping ที่เอกสารออกแบบไว้ |
| `ui-mockup-v2.html` | UI v2; offline mock จำลอง | ตรวจ markup, template, seed และ event handler แบบ static |
| `../../../docs/case-study-source.md` | ไม่ระบุเลขรุ่น; วันที่ตรวจในเอกสาร 2026-09-14 | ฐาน US/AC ต้นฉบับ 26 รายการและบริบท |
| `../../../docs/data-issues.md` | ไม่ระบุเลขรุ่น; วันที่ตรวจในเอกสาร 2026-09-14 | ทะเบียน DI-01–DI-09 และ A-01–A-06 ที่ยังไม่ยืนยัน |
| `../../input/README.md` | Input LAB 006; ไม่ระบุเลขรุ่น | กติกา Input, runner และขอบเขตหลักฐาน |
| `../../input/ui-v2-test-contract.md` | fixture เพิ่ม UI v2 | selector ที่คาดหวังเพิ่ม 9 รายการและ precondition fixture |
| `../../../004_LAB_Conditional_Graph_UI_Mockup/input/ui-contract.md` | fixture เดิม LAB 004; ไม่ระบุเลขรุ่น | selector เดิม 81 รายการและข้อสมมติ fixture |

SHA-256 คำนวณจาก bytes ทั้งไฟล์ ไม่ปรับ newline หรือ encoding ก่อน hash:

| Input | bytes | SHA-256 ที่ตรวจจริง |
|---|---:|---|
| `provenance.md` | 2913 | `34eab044de41842a66208e06b292c0e9c67a2657f151165c688c06c99c05edd1` |
| `fr-nfr-v2.md` | 150751 | `2cbdde11bb3fd5e62f338a1ea74f65d11112f3ea56e8a10ed9d24b08a1dcf0bb` |
| `flow-v2.md` | 41286 | `8fe7983eb45a7222424c7fafe34adf78874da75e7e7cf3ab013d4955d1159f9c` |
| `ui-mockup-v2.html` | 80956 | `249b98c493f4c1347efe36f8be059095ede9d3b23b76ada3b022cfc416c2a1cc` |
| `../../../docs/case-study-source.md` | 30948 | `23294c6b1b6fa1ac76f83b2c60a21c4d2cdf6efa5b6b777d4d9224d7e5e0af3d` |
| `../../../docs/data-issues.md` | 10788 | `62ebb252784ab3bb39da13fca0010f68c223e1aab5914ff9545112175ff9702a` |
| `../../input/README.md` | 4771 | `6cfd51d498ed545b84a71c436d7358d39dc4c4effa8e21bc308540256e1632d6` |
| `../../input/ui-v2-test-contract.md` | 4319 | `208a8cfd8d607b006c3d1151747dde8cead20ec716b8f6c6b70fba34d19eeaf2` |
| `../../../004_LAB_Conditional_Graph_UI_Mockup/input/ui-contract.md` | 17734 | `294b660d2e39b3745344f225400eee57c02c25b6efb108a3a7ecce7cdd060e68` |

## ตรวจ provenance กับต้นทาง

| ต้นทาง (relative จากราก LAB) | snapshot ในขั้นนี้ | ผลเทียบ SHA-256 |
|---|---|---|
| `../005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/fr-nfr-v2.md` | `fr-nfr-v2.md` | MATCH: snapshot = hash ใน provenance = bytes ต้นทาง |
| `../005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/flow-v2.md` | `flow-v2.md` | MATCH: snapshot = hash ใน provenance = bytes ต้นทาง |
| `../005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/ui-mockup-v2.html` | `ui-mockup-v2.html` | MATCH: snapshot = hash ใน provenance = bytes ต้นทาง |

provenance ยังอ้าง `ui-contract-v2.md`, `test-outline-v2.md`, `state-machine-v2.md` และ `structure-v2.md` ในชุดต้นทางเดียวกัน รอบนี้อ่านเพียงรายการและ hash ที่ provenance ระบุ ไม่ได้เปิดหรือตรวจ hash ของไฟล์ประกอบทั้งสี่ จึงไม่รับรองเนื้อหา/ผลตรวจของไฟล์เหล่านั้น ไม่ใช่ Input จำเป็นที่ขาดตามรายการ prompt นี้ หากขั้นถัดไปจำเป็นต้องใช้รายละเอียดดังกล่าว ต้องอ่านและตรวจไฟล์จริงก่อน ไม่สร้างเนื้อหาที่ขาดแทน

สถานะใน FR/Flow เป็นข้อความตามเวลาที่ผลิตเอกสาร: FR ยังกล่าวถึง Flow/UI ที่รอผลิต ส่วน Flow อ้างผลตรวจ FR และยังกล่าวถึง UI ที่รอผลิต รอบนี้มี HTML v2 จริงและตรวจ bytes แล้ว จึงใช้ HTML เป็นหลักฐานว่ามีโค้ดส่วนใดอยู่ โดยไม่แก้สถานะเก่าและไม่อนุมานว่า Evaluator หรือ runtime ผ่านแล้ว

## ความครบและความคงเดิมของ US/AC

ตารางกรณีศึกษามี 26 US; ตาราง US/AC ของ FR v2 มี 21 US ได้แก่ US-01–US-16, US-19–US-21 และ US-25–US-26 ผลเทียบข้อความแต่ละเซลล์จากไฟล์จริง: AC ทั้ง 21 ข้อตรงกับกรณีศึกษาแบบ exact text จึงคงตัวเลข หน่วย สูตร จำนวนตัวอย่าง สัดส่วนสำเร็จ จุดวัด และข้อความอ้างหมายเหตุไว้ทุกข้อ ไม่ใช้ข้อความย่อในรายงานนี้แทน AC เต็มใน Input

พบความต่าง 1 เซลล์ในตาราง US: ช่อง “เพื่อ” ของ US-12 ใน FR v2 เป็น `[ปิดรายละเอียดนอกขอบเขตตั้งต้น; เก็บต้นฉบับไว้ในสำเนาก่อนกรอง]` ขณะที่กรณีศึกษาเป็น `ลูกค้าไม่สั่งเมนูที่ทำไม่ได้` ความต่างนี้มีอยู่ใน Input เดิม; ไม่เติมหรือแก้ snapshot ส่วน AC ของ US-12 ตรงกัน

US-17, US-18, US-22, US-23 และ US-24 มีในกรณีศึกษา แต่ไม่มีแถว FR/US ที่ active ใน v2 ห้ามสร้าง FR หรือ Flow ให้ทั้งห้าข้อขึ้นเอง การออกแบบ coverage ภายหลังต้องแสดงช่องว่างนี้อย่างเปิดเผย ไม่ลดฐาน 26 US ให้เหลือเฉพาะสิ่งที่ mock ทำได้

## วิธีตรวจ selector เดิม

อ่าน `data-testid` ใน markup และ template รวมอาร์กิวเมนต์ของ `button(testid, ...)` ซึ่งสร้าง attribute จริงที่ `ui-mockup-v2.html:324` แล้วตาม seed, ตัวนับ และเงื่อนไข render สำหรับชื่อที่ประกอบแบบ dynamic ไม่ถือเพียงการพบคำในโค้ดเรียก selector ว่าเป็น element ที่สร้างแล้ว

ตรวจชื่อเดิมครบ 81 รายการ: 77 รายการพบชื่อใน markup/template หรืออาร์กิวเมนต์สร้างปุ่ม อีก 4 รายการพบเส้นทางสร้างจาก template และ seed/ตัวนับ ยังไม่ยืนยัน DOM ที่ render, visibility, uniqueness หรือการคลิกของรายการใด สถานะทุกแถวคือ **STATIC_FOUND / runtime NOT_TESTED** ยกเว้นแถวที่ระบุว่าเป็น conditional template

เลขบรรทัดทั้งหมดในตาราง selector อ้าง `ui-mockup-v2.html`:

| data-testid ตามสัญญาเดิม | หลักฐานบรรทัด | ผลตรวจชื่อ/เงื่อนไขจาก source |
|---|---|---|
| `role-customer` | 20 | พบชื่อเดิมในโค้ดสร้าง element |
| `role-staff` | 20 | พบชื่อเดิมในโค้ดสร้าง element |
| `role-manager` | 20 | พบชื่อเดิมในโค้ดสร้าง element |
| `screen-customer` | 345 | พบชื่อเดิมในโค้ดสร้าง element |
| `screen-staff` | 364 | พบชื่อเดิมในโค้ดสร้าง element |
| `screen-manager` | 367 | พบชื่อเดิมในโค้ดสร้าง element |
| `staff-user` | 341 | พบชื่อเดิมในโค้ดสร้าง element |
| `staff-pin` | 341 | พบชื่อเดิมในโค้ดสร้าง element |
| `btn-login` | 341 | พบชื่อเดิมในโค้ดสร้าง element |
| `auth-message` | 23 | พบชื่อเดิมในโค้ดสร้าง element |
| `nav-kitchen` | 363 | พบชื่อเดิมในโค้ดสร้าง element |
| `nav-front` | 363 | พบชื่อเดิมในโค้ดสร้าง element |
| `nav-menu-admin` | 367 | พบชื่อเดิมในโค้ดสร้าง element |
| `nav-mapping` | 367 | พบชื่อเดิมในโค้ดสร้าง element |
| `nav-accounts` | 367 | พบชื่อเดิมในโค้ดสร้าง element |
| `menu-admin` | 369 | พบชื่อเดิมในโค้ดสร้าง element |
| `report-screen` | 367 | พบ placeholder ตรวจสิทธิ์; ไม่มีรายงานยอดขาย |
| `table-select` | 345 | พบชื่อเดิมในโค้ดสร้าง element |
| `btn-open-menu` | 345 | พบชื่อเดิมในโค้ดสร้าง element |
| `active-table` | 345 | พบชื่อเดิมในโค้ดสร้าง element |
| `session-id` | 345 | พบชื่อเดิมในโค้ดสร้าง element |
| `menu-list` | 346 | พบชื่อเดิมในโค้ดสร้าง element |
| `menu-item-m01` | 38–48, 346 | template `menu-item-${esc(m.id)}` + seed m01; ต้องเปิดเมนู |
| `menu-item-m02` | 52–57, 346 | template เดียวกัน + seed m02; ต้องเปิดเมนู |
| `menu-item-m09` | 308, 346, 394–395 | conditional template: seed ยังไม่มี m09; `nextMenu:9` และ saveMenu สร้าง m09 เมื่อบันทึกเมนูใหม่สำเร็จหลัง reset; ยังไม่ได้สร้างจริง |
| `option-extra-egg` | 44–48, 347 | template `option-${esc(x.id)}` + option ของ m01; ต้องเลือกจานที่มีตัวเลือก |
| `item-total` | 347 | พบชื่อเดิมในโค้ดสร้าง element |
| `btn-add-item` | 347 | พบชื่อเดิมในโค้ดสร้าง element |
| `cart-count` | 348 | พบชื่อเดิมในโค้ดสร้าง element |
| `cart-total` | 348 | พบชื่อเดิมในโค้ดสร้าง element |
| `btn-submit-order` | 348 | พบชื่อเดิมในโค้ดสร้าง element |
| `order-message` | 348 | พบชื่อเดิมในโค้ดสร้าง element |
| `order-id` | 349 | พบชื่อเดิมในโค้ดสร้าง element |
| `customer-order-status` | 349 | พบชื่อเดิมในโค้ดสร้าง element |
| `kitchen-queue` | 365 | พบชื่อเดิมในโค้ดสร้าง element |
| `kitchen-order` | 365 | ซ้ำตามออเดอร์; scope ใน kitchen-queue และ data-order-id |
| `btn-status-next` | 365 | ซ้ำตามออเดอร์; scope ใน kitchen-queue และ data-order-id |
| `ingredient-select` | 365 | พบชื่อเดิมในโค้ดสร้าง element |
| `btn-out-of-stock` | 365 | พบชื่อเดิมในโค้ดสร้าง element |
| `btn-restock` | 365 | พบชื่อเดิมในโค้ดสร้าง element |
| `ingredient-status` | 365 | พบชื่อเดิมในโค้ดสร้าง element |
| `pay-cash` | 349 | พบชื่อเดิมในโค้ดสร้าง element |
| `pay-promptpay` | 349 | พบชื่อเดิมในโค้ดสร้าง element |
| `payment-status` | 349 | พบชื่อเดิมในโค้ดสร้าง element |
| `cash-message` | 349 | พบชื่อเดิมในโค้ดสร้าง element |
| `toggle-promptpay` | 367 | พบชื่อเดิมในโค้ดสร้าง element |
| `btn-advance-10m` | 18 | พบชื่อเดิมในโค้ดสร้าง element |
| `sim-clock` | 18 | พบชื่อเดิมในโค้ดสร้าง element |
| `order-mode` | 345 | พบชื่อเดิมในโค้ดสร้าง element |
| `pickup-slot` | 345 | พบชื่อเดิมในโค้ดสร้าง element |
| `takeaway-id` | 349 | พบชื่อเดิมในโค้ดสร้าง element |
| `front-orders` | 366 | พบชื่อเดิมในโค้ดสร้าง element |
| `front-order` | 366 | ซ้ำตามออเดอร์; scope ใน front-orders / front-order และ data-order-id |
| `front-payment-status` | 366 | ซ้ำตามออเดอร์; scope ใน front-orders / front-order และ data-order-id |
| `front-total` | 366 | ซ้ำตามออเดอร์; scope ใน front-orders / front-order และ data-order-id; เป็นยอด snapshot เดิม ไม่ใช่ยอดหลังคืน |
| `btn-confirm-slip` | 366 | ซ้ำตามออเดอร์; scope ใน front-orders / front-order และ data-order-id |
| `btn-receive-cash` | 366 | ซ้ำตามออเดอร์; scope ใน front-orders / front-order และ data-order-id |
| `payment-log` | 366 | พบชื่อเดิมในโค้ดสร้าง element |
| `front-table-select` | 366 | พบชื่อเดิมในโค้ดสร้าง element |
| `btn-close-table` | 366 | พบชื่อเดิมในโค้ดสร้าง element |
| `admin-menu-select` | 369 | พบชื่อเดิมในโค้ดสร้าง element |
| `admin-menu-name` | 369 | พบชื่อเดิมในโค้ดสร้าง element |
| `admin-menu-price` | 369 | พบชื่อเดิมในโค้ดสร้าง element |
| `admin-menu-image` | 369 | พบชื่อเดิมในโค้ดสร้าง element |
| `admin-option-name` | 369 | พบชื่อเดิมในโค้ดสร้าง element |
| `admin-option-price` | 369 | พบชื่อเดิมในโค้ดสร้าง element |
| `btn-save-menu` | 369 | พบชื่อเดิมในโค้ดสร้าง element |
| `btn-delete-menu` | 369 | พบชื่อเดิมในโค้ดสร้าง element |
| `admin-message` | 369 | พบชื่อเดิมในโค้ดสร้าง element |
| `mapping-menu` | 370 | พบชื่อเดิมในโค้ดสร้าง element |
| `mapping-scope` | 370 | พบชื่อเดิมในโค้ดสร้าง element |
| `mapping-option` | 370 | พบชื่อเดิมในโค้ดสร้าง element |
| `mapping-ingredient` | 370 | พบชื่อเดิมในโค้ดสร้าง element |
| `btn-save-mapping` | 370 | พบชื่อเดิมในโค้ดสร้าง element |
| `mapping-list` | 370 | พบชื่อเดิมในโค้ดสร้าง element |
| `account-username` | 371 | พบชื่อเดิมในโค้ดสร้าง element |
| `account-pin` | 371 | พบชื่อเดิมในโค้ดสร้าง element |
| `account-role` | 371 | พบชื่อเดิมในโค้ดสร้าง element |
| `btn-save-account` | 371 | พบชื่อเดิมในโค้ดสร้าง element |
| `account-message` | 371 | พบชื่อเดิมในโค้ดสร้าง element |
| `btn-reset` | 18 | พบชื่อเดิมในโค้ดสร้าง element |

ไม่พบชื่อเดิมที่ต้องเปลี่ยน mapping จากการตรวจ source นี้ แต่การเกิด element ตามเงื่อนไขยัง NOT_TESTED โดยเฉพาะ `menu-item-m09` ไม่ได้มีอยู่ใน seed หลัง reset ส่วน role tabs ใช้ `role-staff` สำหรับบทบาท kitchen-front ใน manifest และให้บัญชีจำลองครัว/หน้าร้านแยกสิทธิ์กัน ไม่มี `role-kitchen-front` ในสัญญาที่ใช้

## ส่วนขยาย v2 และ mapping ที่พบจริง

สัญญาเพิ่มมี 9 selector: 6 ชื่อพบตรง อีก 3 ชื่อไม่พบตามที่สัญญาระบุ ตารางนี้บันทึก mapping เท่านั้น ไม่แก้ HTML, สัญญา หรือชุด scenario เดิม

| selector ที่สัญญาคาดหวัง | ชื่อที่พบจริง/หลักฐาน | ขอบเขตและข้อค้าง |
|---|---|---|
| `btn-item-unavailable` | ชื่อเดิม; 358, 442–448, 523 | ปุ่มทำไม่ได้ต่อรายการภายใน kitchen-order; หลายจานทำให้ซ้ำ ต้อง scope data-order-id และ data-item-id |
| `item-resolution` | ชื่อเดิม; 427–438 | container ต่อรายการ มี “วัตถุดิบหมด” ในลูก `customer-unavailable-alert` เมื่อ state=pending; ไม่ใช่ข้อความแจ้งเดี่ยวที่ unique เสมอ |
| `btn-return-item` | ชื่อเดิม; 435, 450–471, 524 | แสดงเมื่อรายการ pending; resolveItem ปรับ state และยอดจำลอง; ยังไม่เคยกด |
| `capacity-message` | ชื่อเดิม; 348, 480–485 | แทรกก่อน btn-submit-order เมื่ออยู่ช่วงเร่งด่วนและ count >= N; ไม่มีการปฏิเสธเพราะถึง N ใน submitOrder |
| `capacity-limit` | ชื่อเดิม; 493, 503–509 | input number ที่หน้า capacity; ต้องไป nav-capacity หลัง login ผู้จัดการ |
| `rush-start` | **ไม่พบชื่อเดิม → `capacity-start`**; 491, 503 | input time เริ่มช่วง; saveCapacity อ่านค่าจากชื่อนี้จริง |
| `rush-end` | **ไม่พบชื่อเดิม → `capacity-end`**; 492, 503 | input time สิ้นสุดช่วง; saveCapacity อ่านค่าจากชื่อนี้จริง |
| `btn-save-capacity` | ชื่อเดิม; 495, 501–509, 525 | ปุ่มผูก save-capacity ไป saveCapacity; เป็นการตรวจ wiring ใน source เท่านั้น |
| `payment-summary-total` | **ไม่พบชื่อเดิม**; พบ `customer-adjusted-total` ผ่าน context ที่ 349, 407–410 | mapping แบบจำกัด: ยอดปรับของออเดอร์ล่าสุดของ session ตาม latest() ไม่ใช่ยอดรวมหลายออเดอร์ทั้ง session; ใช้เทียบ fixture หนึ่งออเดอร์/หนึ่งจานได้ในเชิง source แต่ runtime ยัง NOT_TESTED |

รายการยังขาดตามชื่อสัญญา: `rush-start`, `rush-end`, `payment-summary-total` การนำ suite เดิมไปรันโดยไม่ปรับชื่อ/ทางเข้าหน้าความจุยัง **BLOCKED ด้านความเข้ากันได้ของ selector** ต้องคงข้อค้าง ไม่แปลงการไม่พบฟีเจอร์เป็น skip เพื่อซ่อนปัญหา รอบนี้ไม่มีผล fail/pass จากการรัน suite

สำหรับยอดคืน พบ `resolution-order-total` ใน `customer-resolution-order[data-order-id]` ที่บรรทัด 439 และ `front-adjusted-total` ใน `front-order[data-order-id]` ผ่านบรรทัด 366, 409–410 รวมทั้ง `history-adjusted-total` ผ่านบรรทัด 350, 409–410 ทุกตัวอ่าน adjustedTotal เดียวกัน แต่ scope/เงื่อนไขต่างกัน จึงไม่ใช้แทนกันแบบ global ส่วน `cart-total` เป็นตะกร้าและ `front-total` เป็น snapshot เดิม ไม่ใช้เป็นหลักฐานยอดหลังคืน

selector ประกอบ v2 ที่พบเพิ่มเติมและมีประโยชน์ในการออกแบบ:

| กลุ่ม | selector/หลักฐานจาก HTML |
|---|---|
| ทางเข้าผู้จัดการ | `nav-capacity` ที่ 367; navigate รองรับ capacity ที่ 373 และ managerHTML เลือก capacityHTML |
| ฟอร์มความจุ | `capacity-settings`, `capacity-wait-minutes`, `capacity-setting-message`, `capacity-window` ที่ 488–497 |
| ลูกค้าตัดสินใจ | `customer-item-resolutions`, `customer-resolution-order`, `resolution-message`, `item-state`, `customer-unavailable-alert` ที่ 419–430; `item-state` ยังสร้างในใบรายการที่ 357 |
| เปลี่ยนเมนู | `replacement-menu`, template `replacement-option-${esc(x.id)}`, `replacement-preview`, `btn-change-menu` ที่ 431–434; handler ที่ 450–471, 515–524 |
| ยอดและประวัติ | `customer-adjusted-total`, `front-adjusted-total`, `history-adjusted-total`, `resolution-order-total`, `refund-policy-note`, `item-adjustment-event` ที่ 407–439 |

ต้อง scope รายการซ้ำด้วย order/item ID และสร้าง precondition ให้ชัดก่อนตรวจ expect_hidden เพราะ element ที่ไม่เคยเกิดก็อาจให้ผล hidden ได้ สัญญา runner ไม่เลือกตัวแรกให้อัตโนมัติ การพบ selector จาก source จึงไม่ยืนยันว่า smoke ที่ใช้ global selector จะทำงานได้

## Fixture ที่พบจริงและขอบเขตการตีความ

- Seed เริ่ม `2026-01-01T12:00:00+07:00`, โต๊ะ `01`/`02`/`03`, m01=50 บาท, extra-egg=10 บาท, m02=55 บาท; reset คืนค่าและออกจากระบบ (HTML:27–119, 305–311) ใช้เฉพาะข้อมูลและบัญชีจำลองในสัญญา ไม่ใช่ข้อมูลร้าน
- Capacity seed คือ 11:30–13:30, N=5, X=10 นาที (HTML:305) แม้มี default ตรง fixture ก็ต้องตั้งช่วง/N ชัดเจนใน scenario ตามสัญญา: ส่ง 5 ออเดอร์ในเวลาจำลองเดียว แล้วเตรียมใบที่ 6 เพื่อดูข้อความก่อนยืนยัน ไม่สร้าง expected ว่าต้องห้ามใบที่ 6
- capacityWindow นับ confirmed_at เป็นออเดอร์ในหน้าต่าง 15 นาทีที่ 00/15/30/45 โดยใช้ [เริ่ม, สิ้นสุด) และ +07:00 (HTML:472–479) ต่างจากตัวอย่าง UTC ใน Flow; เป็นความต่างของ fixture ไม่ใช่คำยืนยันเขตเวลาร้าน คืน/เปลี่ยนรายการไม่ลบออเดอร์ออกจากตัวนับตาม source
- Flow อธิบายหน้าตั้งช่วง/N โดยไม่เพิ่มตั้งค่าสูตร X แต่ HTML มี input X จำลอง `capacity-wait-minutes` ค่านี้ไม่ใช่สูตร ETA หรือ AC ใหม่ (HTML:494, 500) ห้ามใช้ X=10 แทนสูตร US-07 หรือเปลี่ยนช่วง US-07 11:30–13:00 และ 17:30–19:30 ให้เป็นช่วง fixture US-21
- Fixture คืน m01 ราคา 50 เพียงจานเดียว: โค้ด adjustedTotal ตัดรายการ returned ออกจากผลรวม จึงมีผลคาดหวังจาก source ว่าเหลือ 0 บาท ต้องพิสูจน์ด้วยการรันภายหลัง ไม่ใช่ผลคลิกที่ผ่านแล้ว ไม่ใช้ตะกร้าแทนบิล และการลดบิลไม่ยืนยันการคืนเงินจริง
- การเปลี่ยน/คืนรายการแยก item state จาก order/payment/table; resolveItem ไม่เขียนสถานะชำระและไม่ลบ snapshot เดิม ข้อสมมติเรื่องกดซ้ำ/เมนูแทน/ราคา/aggregate ยังไม่ใช่กฎร้านที่อนุมัติ (HTML:401–471)
- จำนวนโต๊ะ seed 3 โต๊ะ, fixture หนึ่งจาน และ smoke หนึ่งกรณีไม่แทนจำนวนตัวอย่างของ AC ใด ไม่ลดจำนวนตัวอย่างหรือสัดส่วนเดิมเพื่อให้พอดีกับ mock

## แยก plan-v3 จากสิ่งที่มีจริงใน UI v2

ไม่ได้รับ plan-v3 เป็น Input และไม่ได้เปิดแผนดังกล่าว จึงไม่มีข้อมูลพอระบุรายการงาน/สถานะการดำเนินการของแผนเป็นรายงานจริง ใช้ข้อกำกับจาก README ว่า plan-v3 ไม่ยืนยันการสร้างฟีเจอร์ และใช้โค้ด HTML ของ snapshot นี้ตรวจสิ่งที่มีอยู่เท่านั้น

| ขอบเขต | สิ่งที่พบจากไฟล์ | สถานะรอบนี้ |
|---|---|---|
| US-09 / US-14 | Flow ออกแบบ MRG-31/32/33; HTML มีปุ่มแจ้งทำไม่ได้ ตัวเลือกลูกค้า handler คืน/เปลี่ยน ยอดปรับ และการกรองรายการคืนออกจากใบครัว | มีโค้ดจำลอง; NOT_TESTED runtime/AC |
| US-21 | Flow ออกแบบ MRG-34/35; HTML มีฟอร์มช่วง/N/X และข้อความก่อนยืนยัน | มีโค้ดจำลอง; NOT_TESTED runtime/AC |
| US-11 | Flow ระบุครัวส่งสถานะอาหารไปหน้าร้าน; HTML:365–366 อ่าน statuses[o.status] ของออเดอร์เดียวกัน และ handler next-status ที่ 529 เปลี่ยนค่าแล้ว render | มีเส้นทางโค้ด; NOT_TESTED; ห้ามใช้ front-payment-status แทนสถานะอาหาร |
| US-07 | HTML:348 ระบุ “ยังประมาณไม่ได้” เพราะไม่มีค่าเฉลี่ย 7 วันและต่อเมนู | BLOCKED ด้านข้อมูล/สูตรที่ยังไม่ทำใน mock; NOT_TESTED |
| US-23 รายงานยอดขาย/CSV | report-screen ที่ HTML:367 เป็น “Placeholder” สำหรับตรวจสิทธิ์ US-25 เท่านั้น ไม่มีตารางรายงาน/ส่งออก CSV ที่ทำงานใน source นี้ | NOT_TESTED; รายงานที่อยู่เพียงในแผนเป็น PLANNED เท่านั้น |
| US-17 / US-18 / US-22 / US-24 | นอก active scope ของ FR/Flow v2; ไม่พบ implementation สำหรับรวมบิลหลายรอบ, counter/เตือนออเดอร์เกินเวลา, สวิตช์กลับบ้าน หรือประวัติวัตถุดิบรายสัปดาห์ตาม US เหล่านี้ใน HTML ที่อ่าน | NOT_TESTED; ไม่มี FR/Flow v2 ให้รับรอง ไม่อนุมานว่าถูกสร้างเพราะแผนรุ่นใหม่ |
| US-25 | มี login/สิทธิ์จำลองและ placeholder หน้ารายงาน | NOT_TESTED ทั้ง runtime และ Security จริง; การมีหน้าตรวจสิทธิ์ไม่ยืนยัน US-23 |
| US-26 / NFR ระบบจริง | HTML เก็บ state ในหน่วยความจำหนึ่งแท็บ ไม่มีหลักฐานระบบติดตั้งจริงหรือเครือข่ายหลายเครื่องในชุด Input นี้ | NOT_TESTED; การรับรองติดตั้ง/LAN/Availability ยัง BLOCKED ด้านหลักฐาน |

## ข้อบกพร่อง ข้อค้าง และสิ่งที่ยังไม่ทดสอบ

- ข้อบกพร่อง/ช่องว่างจาก static check: selector v2 ไม่ตรงชื่อ 3 รายการ; ยอดที่พบจริงจำกัดระดับออเดอร์; m09 ต้องสร้างก่อน; ต้องเข้าหน้าความจุผ่าน nav-capacity; รายงานเป็น placeholder; ETA ยังไม่มีข้อมูล ทั้งหมดเป็นข้อค้นพบจากไฟล์ ไม่ใช่ runtime failure
- ข้อค้างข้อมูล DI-01–DI-03: ไม่มีนิยามหมายเหตุ ก./ค./ช.; DI-04: US-20 ยังคงอ้าง US-14 การเชื่อม US-12/US-13 เป็นข้อเสนอ; DI-05 เป็นรูปแบบ Markdown; DI-06 แยกช่วง US-07/US-21; DI-07 ยังไม่ยืนยัน mapping สถานะ; DI-08 ผลเก่า/ข้อมูลบัญชีไม่ใช่หลักฐานใหม่; DI-09 mock ไม่พิสูจน์ระบบจริง คง A-01–A-06 เป็นสมมติฐานที่ยังไม่ยืนยัน
- Q เดิมทั้ง 18 รายการใน FR v2 และ Q-V2-REFUND/STATE/CAPACITY ยังเปิด: ราคา/ส่วนต่าง/ผู้อนุมัติและวิธีคืนเงินจริง, ผลรายการต่อออเดอร์/ETA/โต๊ะ, สูตร X, เขตเวลา/ขอบหน้าต่าง/วิธีนับและผลเมื่อเต็ม ไม่มีคำตอบใหม่ในรอบนี้ การรับรองนโยบายดังกล่าวยัง BLOCKED
- **NOT_TESTED:** browser/DOM/runtime/click/visibility/uniqueness/responsive, smoke scenarios, จำนวนตัวอย่าง/สัดส่วนสำเร็จทุก AC, เวลา LAN/Wi-Fi, หลายอุปกรณ์/concurrency/Load, authentication/authorization/Security ฝั่ง server, logs จริง, Availability/การถอดอินเทอร์เน็ต, การติดตั้ง Ubuntu, สูตรและความแม่นยำ ETA, PromptPay/การชำระ/คืนเงินจริง ไม่มีจำนวน passed/failed/skipped จากการรัน UI ให้รายงาน
- หาก Input จำเป็นขาดหรืออ่านไม่ได้ในขั้นที่พึ่งพา ให้หยุดขั้นนั้นเป็น BLOCKED และบันทึกไม่มีข้อมูล ไม่สร้าง FR, Flow, selector, UI หรือผล LAB 005 แทน รอบนี้หยุดงานที่ขั้น 6.0 ตามขอบเขต ไม่สร้าง scenario รายบทบาทหรือรันขั้นถัดไป

## Output ที่สร้างจริงและความหมายของ manifest

สร้างเฉพาะ `input-check.md` และ `scenario-set-round-0.json` ในโฟลเดอร์ขั้นนี้ ไม่มีการแก้ Input, ต้นทาง หรือผลเก่า manifest เป็น object role → path เท่านั้น มีค่าตาม prompt ตรงตัว:

| role | path ที่คาดหวัง (relative จากราก LAB `../..`) |
|---|---|
| customer | `../step-01-fanout/customer/scenarios-customer.md` |
| kitchen-front | `../step-01-fanout/kitchen-front/scenarios-kitchen-front.md` |
| manager | `../step-01-fanout/manager/scenarios-manager.md` |

**manifest เป็นรายการ Output ที่คาดหวัง ไม่ใช่การรับรองว่าทั้งสามไฟล์มีแล้ว** ไม่ได้ตรวจการมีอยู่หรือสร้างไฟล์ปลายทาง คง `../step-01-fanout/...` ตาม prompt โดยไม่ resolve จากโฟลเดอร์ขั้นนี้หรือแก้ให้เป็นตำแหน่งอื่น ผู้ใช้ manifest ต้อง resolve จากราก LAB ตาม provenance
