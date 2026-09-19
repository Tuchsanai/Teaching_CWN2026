# สัญญา UI สำหรับ Conditional Graph

สัญญานี้เป็น fixture สำหรับ Mock-up ไม่ใช่ข้อกำหนดร้านที่เพิ่มจากต้นฉบับ
ใช้ HTML native button/select/input เพื่อให้ผู้เรียนและ Playwright ทำสิ่งเดียวกันได้
เปิด HTML ผ่าน file:// ไม่ fetch JSON, ไม่ CDN, ไม่โหลดรูป/ฟอนต์/สคริปต์จากเครือข่าย
ข้อมูลจาก mock-data.json ต้องฝังในไฟล์ HTML; state ใช้หน่วยความจำของแท็บหรือ localStorage ชื่อเฉพาะแอป
หนึ่งแท็บแชร์ state ระหว่างบทบาท; แต่ละ check เปิด browser context ใหม่และกดรีเซ็ตก่อนเริ่ม
มีแถบ 3 บทบาทเท่านั้น: ลูกค้า / ครัวและหน้าร้าน / ผู้จัดการ; บัญชี kitchen/front แยกสิทธิ์ในแท็บพนักงาน
เลือกแท็บพนักงานหรือผู้จัดการใหม่ให้แสดงฟอร์ม login ทุกครั้ง ไม่สืบทอดสิทธิ์จากผู้ใช้ก่อน
selector ทั่วไปต้อง unique และมองเห็นเมื่อเปิดหน้าที่เกี่ยวข้อง; รายการซ้ำต้อง scope ใน container ที่ระบุ
ปุ่มรีเซ็ต, sim-clock, btn-advance-10m อยู่ส่วนกลางให้ทุกบทบาทเห็น และติดป้าย “จำลอง”
ชื่อ demo และ PIN 0000 เป็น placeholder สาธารณะเพื่อทดสอบ ไม่ใช่บัญชีจริงและไม่ใช่ระบบยืนยันตัวตนจริง

| data-testid | ความหมาย/พฤติกรรม |
|---|---|
| `data-testid="role-customer"` | button: แท็บลูกค้า ไม่ต้องล็อกอิน |
| `data-testid="role-staff"` | button: แท็บครัว/หน้าร้าน แสดงฟอร์มเข้าใช้ |
| `data-testid="role-manager"` | button: แท็บผู้จัดการ แสดงฟอร์มเข้าใช้ |
| `data-testid="screen-customer"` | section ลูกค้า |
| `data-testid="screen-staff"` | section พนักงาน |
| `data-testid="screen-manager"` | section ผู้จัดการ แสดงหลังอนุญาตเท่านั้น |
| `data-testid="staff-user"` | select value=demokitchen, demofront, demomanager และบัญชีที่สร้างใหม่ |
| `data-testid="staff-pin"` | input password; PIN จำลอง 0000 |
| `data-testid="btn-login"` | button ยืนยันชื่อผู้ใช้และ PIN |
| `data-testid="auth-message"` | ข้อความปฏิเสธ/ล็อก/ผลเข้าใช้ แสดงให้เห็น |
| `data-testid="nav-kitchen"` | button เปิดครัว เฉพาะ kitchen/manager |
| `data-testid="nav-front"` | button เปิดหน้าร้าน เฉพาะ front/manager |
| `data-testid="nav-menu-admin"` | button/ลิงก์ไป #/manager/menu ตรวจสิทธิ์เมื่อเข้าโดยตรงด้วย |
| `data-testid="nav-mapping"` | button ไปหน้าแมป เฉพาะ manager |
| `data-testid="nav-accounts"` | button ไปหน้าบัญชี เฉพาะ manager |
| `data-testid="menu-admin"` | section จัดการเมนู |
| `data-testid="report-screen"` | section รายงาน #/manager/reports เฉพาะ manager; เป็น placeholder ตรวจสิทธิ์ ไม่มีรายงานนอกขอบเขต |
| `data-testid="table-select"` | select value=01,02,03 แทนสแกน QR ที่มี table_id |
| `data-testid="btn-open-menu"` | button เริ่ม/เปิด session โต๊ะที่เลือก |
| `data-testid="active-table"` | ข้อความโต๊ะที่ active |
| `data-testid="session-id"` | ข้อความ session ID เปลี่ยนเมื่อปิดโต๊ะแล้วเปิดใหม่ |
| `data-testid="menu-list"` | section รายการเมนู |
| `data-testid="menu-item-m01"` | button เมนู m01; แม่แบบ menu-item-<id> ทุกเมนู ปิดด้วย disabled เมื่อทั้งจานหมด |
| `data-testid="menu-item-m02"` | button เมนู m02 ตามแม่แบบเดียวกัน |
| `data-testid="menu-item-m09"` | button เมนูใหม่ที่สร้างในชุดตรวจ ใช้ตัวนับ m09 หลัง reset |
| `data-testid="option-extra-egg"` | checkbox ตัวเลือกไข่ของ m01; แม่แบบ option-<id> ภายในรายละเอียดจานที่เลือก |
| `data-testid="item-total"` | ยอดจานที่เลือก แสดงเลขและหน่วยบาท |
| `data-testid="btn-add-item"` | button เพิ่มจานลงตะกร้า |
| `data-testid="cart-count"` | จำนวนจานในตะกร้า แสดงเลขล้วน |
| `data-testid="cart-total"` | ยอดตะกร้า |
| `data-testid="btn-submit-order"` | button ส่งตะกร้า; ต้องยอมให้กดเพื่อตรวจปฏิเสธตะกร้าที่วัตถุดิบเพิ่งหมด |
| `data-testid="order-message"` | ข้อความส่งแล้วหรือปฏิเสธ มีคำว่า หมด เมื่อวัตถุดิบไม่พอ |
| `data-testid="order-id"` | เลขออเดอร์ล่าสุดของ session ลูกค้า เป็นเลขเพิ่มทีละหนึ่ง |
| `data-testid="customer-order-status"` | สถานะออเดอร์ล่าสุด รับออเดอร์ → กำลังทำ → เสร็จแล้ว |
| `data-testid="kitchen-queue"` | container ใบครัว เรียง timestamp วินาที แล้วเลขออเดอร์; แสดงตัวเลือกและป้ายกลับบ้าน |
| `data-testid="kitchen-order"` | article ซ้ำได้ใน kitchen-queue; มี data-order-id, data-received-at เป็น ISO พร้อม timezone |
| `data-testid="btn-status-next"` | button ซ้ำได้ใน kitchen-order; คลิกหนึ่งครั้งเปลี่ยนหนึ่งสถานะ |
| `data-testid="ingredient-select"` | select ในครัว value=รหัสวัตถุดิบ |
| `data-testid="btn-out-of-stock"` | button ทำวัตถุดิบที่เลือกหมด |
| `data-testid="btn-restock"` | button ทำวัตถุดิบที่เลือกกลับมามี |
| `data-testid="ingredient-status"` | ข้อความชื่อ/สถานะวัตถุดิบที่เลือก |
| `data-testid="pay-cash"` | button ลูกค้าเลือกเงินสด ยังไม่เปลี่ยนเป็นจ่ายแล้ว |
| `data-testid="pay-promptpay"` | button ลูกค้าเลือก PromptPay แสดง QR จำลองและค้างจ่าย |
| `data-testid="payment-status"` | ข้อความสถานะลูกค้า ยังไม่จ่าย / ค้างจ่าย / จ่ายแล้ว |
| `data-testid="cash-message"` | ข้อความแนะนำ เงินสด เมื่อปิด PromptPay หรือค้างยืนยันถึง 10 นาที |
| `data-testid="toggle-promptpay"` | checkbox ตั้งค่าเปิด/ปิด PromptPay เฉพาะผู้จัดการ |
| `data-testid="btn-advance-10m"` | button ส่วนจำลองเวลา เพิ่ม 10 นาที ไม่ต้องรอจริง |
| `data-testid="sim-clock"` | ข้อความ ISO ของเวลาจำลองพร้อม timezone |
| `data-testid="order-mode"` | select dine-in หรือ takeaway |
| `data-testid="pickup-slot"` | select ค่า HH:MM-HH:MM ช่วง 15 นาที เริ่มอย่างน้อย 20 นาทีจาก sim-clock |
| `data-testid="takeaway-id"` | ข้อความ T-001 ของออเดอร์กลับบ้านแรก |
| `data-testid="front-orders"` | container ใบหน้าร้านมีโต๊ะ/หมายเลขกลับบ้าน/สถานะครัว/ยอด |
| `data-testid="front-order"` | article ซ้ำได้ใน front-orders มี data-order-id และ data-table-id; กลับบ้านใช้ data-table-id=takeaway |
| `data-testid="front-payment-status"` | ข้อความสถานะจ่ายภายใน front-order |
| `data-testid="front-total"` | ยอด snapshot ภายใน front-order |
| `data-testid="btn-confirm-slip"` | button ภายใน front-order ยืนยันสลิปได้เฉพาะ front/manager |
| `data-testid="btn-receive-cash"` | button ภายใน front-order รับเงินสดได้เฉพาะ front/manager |
| `data-testid="payment-log"` | ข้อความรายการเหตุการณ์ชื่อผู้ใช้จำลอง+เวลา ISO+order ID |
| `data-testid="front-table-select"` | select value=01,02,03 |
| `data-testid="btn-close-table"` | button ปิด session โต๊ะ selected; เก็บออเดอร์เก่าในประวัติ ไม่ปน session ใหม่ |
| `data-testid="admin-menu-select"` | select existing menu IDs หรือ new |
| `data-testid="admin-menu-name"` | input ชื่อเมนู |
| `data-testid="admin-menu-price"` | input number ราคา >=0 |
| `data-testid="admin-menu-image"` | input file รับ jpg/png <=2 MB แปลง data URI ไม่มี URL ภายนอก |
| `data-testid="admin-option-name"` | input ชื่อตัวเลือกใหม่; UI เพิ่ม/ลบได้ 0–10 ตัวเลือก |
| `data-testid="admin-option-price"` | input number ราคาเพิ่ม >=0 |
| `data-testid="btn-save-menu"` | button บันทึกเมนู รวมตัวเลือกที่กรอก |
| `data-testid="btn-delete-menu"` | button ลบเมนู พร้อม confirm แจ้งลบแมปถ้ามี |
| `data-testid="admin-message"` | ข้อความผลจัดการเมนู |
| `data-testid="mapping-menu"` | select เฉพาะเมนูที่มีอยู่ |
| `data-testid="mapping-scope"` | select whole หรือ option |
| `data-testid="mapping-option"` | select รหัสตัวเลือกของเมนูที่เลือก ใช้เมื่อ scope=option |
| `data-testid="mapping-ingredient"` | select รหัสวัตถุดิบ |
| `data-testid="btn-save-mapping"` | button เพิ่มความสัมพันธ์ ไม่ลบแมปอื่น |
| `data-testid="mapping-list"` | รายการแมปพร้อมรหัสเมนู วัตถุดิบ scope และ option |
| `data-testid="account-username"` | input ชื่อผู้ใช้ 3–20 ตัวอักษร/ตัวเลข |
| `data-testid="account-pin"` | input password PIN 4–6 หลัก |
| `data-testid="account-role"` | select kitchen/front/manager |
| `data-testid="btn-save-account"` | button สร้างบัญชีจำลอง |
| `data-testid="account-message"` | ข้อความผลสร้างหรือปฏิเสธบัญชี |
| `data-testid="btn-reset"` | button ส่วนกลาง รีเซ็ตข้อมูลทั้งหมดกลับ seed และเวลาเริ่มต้นพร้อมออกจากระบบ |

## กติกาที่ตัวตรวจใช้

- reset: เลือกแท็บลูกค้า, โต๊ะ 01, dine-in; ยังไม่เปิดเมนู; ตะกร้า/คิว/การจ่าย/ประวัติ/บัญชีเพิ่ม/แมปเพิ่มว่าง; เมนู/แมป seed คืนเดิม; วัตถุดิบทั้งหมดมี; PromptPay เปิด; เวลาเริ่มตาม seed
- เปิดโต๊ะใหม่แล้ว customer-order-status/payment-status แสดงสถานะว่าง/ยังไม่จ่าย และไม่แสดงรายการ session เก่า
- เมนู m01 ราคา 50 + extra-egg 10 = 60 บาท; m02 ราคา 55 บาท; ทุกการส่งสำเร็จล้างตะกร้าและเพิ่มเลขออเดอร์หนึ่ง
- ยอดออเดอร์เก็บ snapshot รวมตัวเลือก ณ เวลาส่ง; แก้ราคาในผู้จัดการไม่เปลี่ยนยอดเก่า
- เปลี่ยนบทบาทหรือเปิดเมนูของโต๊ะ active อีกครั้งไม่ล้างตะกร้าหรือสถานะ; ห้ามบังคับ reload หลังเปลี่ยนสถานะ
- ปิด chicken ทำให้ m01 ทั้งจานหมด; ปิด egg ทำให้ m01 ยังสั่งได้แต่ extra-egg disabled; m03 ทั้งจานหมด
- ตรวจ stock ซ้ำตอน submit เสมอ; ตะกร้าที่เพิ่มไว้ก่อน stock หมดต้องถูกปฏิเสธ พร้อมข้อความ หมด และห้ามเพิ่มใบครัว
- กลับมามีเปิดคืนเฉพาะรายการที่ไม่มีวัตถุดิบอื่นหมดค้างอยู่; การปิดขายด้วยผู้จัดการเป็นคนละเหตุ
- ก่อนยืนยันชำระเงิน front-total ต้องเท่าลูกค้า; เงินสดที่ลูกค้าเลือกยังเป็น ยังไม่จ่าย; front เป็นผู้ยืนยัน
- สถานะลูกค้า/ครัวใช้ รับออเดอร์ → กำลังทำ → เสร็จแล้ว; เป็นชื่อสำหรับ fixture ตาม A-05 ยังรอยืนยัน mapping upstream
- คิวเรียง timestamp ของนาฬิกาจำลองปัดลงวินาที แล้วเลขออเดอร์; ไม่อ้างว่าแทนนาฬิกา server จริง
- takeaway ครั้งแรกได้ T-001 ต่อไป T-002; ขึ้นวันใหม่ของนาฬิกาจำลองรีเซ็ตลำดับ; ห้ามรีเซ็ตระหว่างวันด้วยการสลับบทบาท
- เวลาเริ่ม 12:00: slot แรก 12:30-12:45 (ปัดขึ้นขอบ 15 นาทีหลังขั้นต่ำ 20 นาที), แล้ว 12:45-13:00; วันอ้างอิงจาก sim-clock
- ข้ามไป #/manager/menu หรือ #/manager/reports โดยบัญชี kitchen/front ต้องแสดง ปฏิเสธ ใน auth-message และไม่แสดง section ที่ป้องกัน
- PIN ผิด 5 ครั้งติดล็อก 5 นาทีตามเวลาจำลอง; ใส่ PIN ถูกระหว่างล็อกต้องยังถูกปฏิเสธ; reset ล้างสถานะล็อก
- US-20 ต้นฉบับอ้างกฎปิด/เปิดเป็น US-14; คงข้อสงสัย DI-04 และเสนอสัมพันธ์กับ US-12/US-13 ตาม A-03 ซึ่งยังไม่ยืนยัน
- ตัวตรวจเป็น smoke checks ของพฤติกรรม ไม่ทดแทนจำนวนตัวอย่าง/สัดส่วนสำเร็จ/เกณฑ์วินาทีบน LAN ตามต้นฉบับ
- ฟิลด์รูป/ตัวเลือกหลายรายการ/วันเปลี่ยน/หลายวัตถุดิบค้างหมด และขนาดจอ ต้องตรวจเพิ่มด้วยสคริปต์คลิกและผู้ตรวจ AI


# ส่วนเพิ่มสัญญา UI v2 — offline fixture

ไฟล์เป้าหมาย: `ui-mockup-v2.html` ใน directory เดียวกัน. ส่วน baseline ด้านบนคัดตรงทุกตัวอักษร; selectors เดิมและ payload เดิมคงความหมาย. ส่วนนี้เพิ่มพฤติกรรม US-09/14/21 ตาม FR/Flow v2 และคำสั่งรัน revise-ui. สัญญาไม่ใช่ผลทดสอบ: **EXECUTED; browser/regression NOT_RUN; AC ระบบจริง NOT_TESTED**.

## Authority และขอบเขต

FR authority: `fr-nfr-v2.md`; Flow: `flow-v2.md` MRG-31–35; state: `state-machine-v2.md` I-V2-01–03/C-V2-01–03; data: `structure-v2.md` แถว 85–94; แผนตรวจ `test-outline-v2.md` V2-A–F และ US-21 สามรอบ. ใช้คำสั่งผู้ใช้รอบนี้สำหรับนาฬิกา +07:00 และช่องกรอก X จำลอง: ต่างจากข้อเสนอ clock UTC ใน Flow/outline แต่ไม่แก้เอกสารต้นฉบับและไม่ประกาศเขตเวลาธุรกิจใหม่. ช่อง X ตั้งค่าตัวเลข fixture เท่านั้น ไม่ใช่เครื่องมือตั้งสูตร X หรือ ETA.

`front-total` ยังคง **ยอด snapshot ณ ส่งออเดอร์**; `cart-total` ยังเป็นยอดตะกร้าก่อนส่ง. ห้ามเปลี่ยน test เดิมให้ใช้ snapshot เป็นยอดหลังปรับ: v2 เพิ่ม `front-adjusted-total` และ `customer-adjusted-total` สำหรับยอดปัจจุบันจาก decision ชุดเดียวกัน. ทั้งสองเท่ากับยอดเดิมเมื่อยังไม่มี adjustment; ลูกค้า/หน้าร้านแสดงป้ายแยกยอดชัดเจน. `customer-order-status`, `front-payment-status`, `payment-status`, `btn-status-next`, `btn-confirm-slip`, `btn-receive-cash` คงความหมาย/สิทธิ์เดิม.

## Selectors เพิ่มและ scope ที่บังคับ

| data-testid | Element / scope / พฤติกรรม |
|---|---|
| `btn-item-unavailable` | button ข้อความ **ทำไม่ได้**; อยู่ใน `kitchen-order` ของแต่ละรายการ ใช้ `data-id=order_id`, `data-item-id=item_id`; ครัว/ผู้จัดการกดให้รายการรอลูกค้า; pending หรือออเดอร์เสร็จแล้ว disabled เป็น fixture |
| `customer-item-resolutions` | section หนึ่งเดียวบนลูกค้าเมื่อ active session มีรายการได้รับการแจ้ง ครอบคลุมออเดอร์เก่ากว่าล่าสุดด้วย; ไม่อยู่ใน details ที่ต้องกางก่อนเห็น |
| `customer-resolution-order` | article ซ้ำภายใน section ข้างบน มี `data-order-id`; อ้างออเดอร์เดียวกับใบครัว/หน้าร้าน |
| `item-resolution` | div ต่อรายการ มี `data-item-id`; scope จาก `customer-resolution-order[data-order-id]`; แสดง snapshot เดิมและสถานะ item ปัจจุบัน |
| `customer-unavailable-alert` | p role=alert ภายใน item-resolution เฉพาะ pending; บอก **วัตถุดิบหมดกลางคิว** และสองทางเลือก |
| `item-state` | span สถานะรายการ; scope ภายใน item-resolution หรือ list li[data-item-id] ของใบครัว/ใบหน้าร้าน; อาจซ้ำในหน้าลูกค้าสรุปล่าสุด/ประวัติ ห้ามใช้ global locator |
| `replacement-menu` | select ใน item-resolution pending; value=menu ID เช่น m02; placeholder value ว่าง; ปิดตัวเลือกเมนูที่หมด/ปิดขาย; มี data-item-id |
| `replacement-option-<option_id>` | checkbox ของเมนูแทนใน item-resolution เช่น replacement-option-extra-egg; แยกจาก option-extra-egg เดิม; มี data-item-id และ data-replacement-option |
| `replacement-preview` | p ใน item-resolution หลังเลือกเมนูแทน แสดงเมนู/ตัวเลือก/ราคาและยอดเสนอหลังเปลี่ยนก่อนกดยืนยัน |
| `btn-change-menu` | button **เปลี่ยนเมนู** ใน item-resolution pending; data-id=order ID + data-item-id; เลือกเมนูแล้วกดเพื่อยืนยัน; หากยังไม่เลือกแสดงข้อความและคง pending |
| `btn-return-item` | button **คืนรายการ** ใน item-resolution pending; payload เดียวกับปุ่มเปลี่ยน; กดแล้วนำรายการออกจากครัว/ยอดปัจจุบัน เก็บ snapshot และประวัติ |
| `resolution-message` | p role=status หนึ่งเดียวใน customer-item-resolutions; แจ้งผลสำเร็จจำลองหรือปฏิเสธเมนูหมด/ยังไม่เลือก |
| `resolution-order-total` | strong ยอดหลังปรับใน customer-resolution-order; scope ด้วย order ID เพื่อเทียบออเดอร์ที่ไม่ใช่ล่าสุด |
| `customer-adjusted-total` | strong ยอดหลังปรับออเดอร์ล่าสุด ในส่วนติดตามล่าสุดลูกค้า; unique เมื่อมีออเดอร์ล่าสุด |
| `history-adjusted-total` | strong ซ้ำใน details ออเดอร์ทั้งหมด; scope article ประวัติ; สำหรับตรวจหลายใบแนะนำ resolution-order-total เมื่อมี resolution |
| `front-adjusted-total` | strong ยอดหลังปรับ ภายใน front-order[data-order-id]; ใช้เทียบลูกค้าและแยกจาก front-total ที่คง snapshot |
| `refund-policy-note` | p ในบล็อกยอดหลังปรับเมื่อมี adjustment; ซ้ำตามสรุป/ประวัติ/ใบหน้าร้าน ให้ scope บล็อกยอดหรือ front-order; ไม่ใช่ payment state |
| `item-adjustment-event` | li ใน details ประวัติปรับรายการจำลองของแต่ละบล็อกยอด; data-item-id, order ID ในข้อความ, actor จำลอง/ISO เวลา/รายการก่อนหลัง/ยอดก่อนหลัง; แยกจาก payment-log |
| `nav-capacity` | button หน้าผู้จัดการไป #/manager/capacity; แสดงหลังล็อกอินผู้จัดการ; direct route ตรวจสิทธิ์ |
| `capacity-settings` | section unique เฉพาะผู้จัดการในหน้า capacity |
| `capacity-start` | input time ค่าเริ่ม 11:30 |
| `capacity-end` | input time ค่าเริ่ม 13:30 |
| `capacity-limit` | input number ค่าเริ่ม N=5 ออเดอร์ต่อ 15 นาที |
| `capacity-wait-minutes` | input number ค่าเริ่ม X=10; label **X นาที — ค่าจำลอง ยังไม่ยืนยันสูตร** |
| `btn-save-capacity` | button บันทึกฟอร์มทั้งสี่ เฉพาะ manager; ไม่เปลี่ยนค่า ETA/pickup/PromptPay |
| `capacity-setting-message` | p role=status unique ใน capacity-settings ผลบันทึก/ข้อจำกัดฟอร์มจำลอง |
| `capacity-window` | p ใน capacity-settings แสดง ISO start/end +07:00 และจำนวนออเดอร์ยืนยัน/อยู่ในช่วงหรือไม่ |
| `capacity-message` | p unique ในตะกร้าลูกค้า **ก่อน** btn-submit-order เมื่ออยู่ในช่วงและจำนวนถึง N; ข้อความ `ครัวเต็ม รอประมาณ X นาที` แทน X ด้วยค่าจำลอง; ป้าย X เป็นค่าจำลอง ยังไม่ยืนยันสูตร อยู่ติดกัน; ไม่ render เมื่อยังไม่ถึงเพดานหรือนอกช่วง |

ใน `kitchen-queue` และ `front-orders` มี `data-order-id` เฉพาะ **outer order article หนึ่งตัวต่อออเดอร์**. ลูกภายในใช้ data-id/data-item-id ไม่ซ้ำ data-order-id. `li` รายการและปุ่มอาจมี data-item-id เดียวกัน จึงต้องระบุชนิด element หรือ testid ให้ครบ ห้ามใช้ `[data-item-id]` ลอย ๆ แล้วคาดว่า unique.

ตัวอย่าง locator ที่ต้องใช้ใน Evaluator (ยังไม่รัน):

```text
[data-testid="kitchen-queue"] [data-testid="kitchen-order"][data-order-id="1"] [data-testid="btn-item-unavailable"][data-item-id="1"]
[data-testid="customer-item-resolutions"] [data-testid="customer-resolution-order"][data-order-id="1"] [data-testid="item-resolution"][data-item-id="1"] [data-testid="btn-return-item"]
[data-testid="front-orders"] [data-testid="front-order"][data-order-id="1"] [data-testid="front-adjusted-total"]
```

## State, data และเงินจำลอง

`Order.total`, `OrderItem` (รวม options/price/total), `Payment.total`, order_id/received_at/confirmed_at และ paymentEvents เดิมไม่ถูกเปลี่ยนโดย feature ใหม่นี้. `s.itemResolutions[item_id]` แยก state/revision/current snapshot ของเมนูแทน; `s.adjustments` เก็บก่อน/หลัง/actor/ISO; `s.itemEvents` แยกเหตุรายการ. `adjustedTotal(order)` เป็นมุมมองจากรายการที่ไม่คืนและ effective snapshot ล่าสุด ไม่ใช้ราคา catalog ย้อนหลัง. ไม่มี field AI plan status ปนใน business state.

รายการ queued → pending (**รอลูกค้าตัดสินใจ**) → replaced (**รายการแทนในคิว**) หรือ returned (**คืนรายการแล้ว**). มีเฉพาะ pending ที่เป็นชื่อสถานะจาก FR โดยตรง; ชื่ออื่น/คง item ID เดิมแล้วเพิ่ม revision เป็นข้อเสนอ mock. การแจ้งไม่ต้องปิด catalog ก่อนและไม่เปลี่ยน stock เอง. ครัวแสดงเมนูแทนจริงผ่าน effective snapshot; returned ไม่อยู่ใน list ที่ต้องทำ แต่ original item ยังอยู่ในข้อมูล/ประวัติ. ปุ่มสถานะออเดอร์เดิมยังทำงานอิสระ ไม่รวมสถานะ item เป็น order state อัตโนมัติ.

หลังเลือกเมนูและตัวเลือกยังไม่ถือว่าสำเร็จจนกดเปลี่ยนเมนู; ตรวจ stock/options อีกครั้งเมื่อกด. เมนูหมดหรือถูกลบแสดงปฏิเสธและคง pending. Draft เลือกเมนูไม่ใช้ตะกร้าปกติและไม่เพิ่มเลขออเดอร์. การแก้ catalog ไม่เปลี่ยน snapshot เดิม/เมนูแทนที่ยืนยันแล้ว. จำนวนจำลองจานละ 1 และการใช้ราคา catalog ที่แสดงก่อนยืนยันเมนูแทนเป็นสมมติฐาน ไม่ใช่สูตรส่วนต่างที่อนุมัติ.

Fixture ตาม Flow: m01+extra-egg=60 และ m02=55 รวม 115 บาท; คืนจาน 60 แล้วยอดหลังปรับ 55 บาท; เปลี่ยนจาน 60 เป็น m02=55 แล้วยอดหลังปรับ 110 บาท. ตัวเลขเหล่านี้เป็น expected fixture **ยังไม่ได้รันทดสอบ**. front-total คง 115 ในทั้งสองกรณี; front-adjusted-total เท่ากับ customer-adjusted-total หรือ resolution-order-total ของออเดอร์เดียวกัน.

คืนหรือเปลี่ยนไม่แก้ `payment.state`, `paymentEvents`, `order.status`, TableSession.state; จ่ายแล้วคงจ่ายแล้วพร้อมข้อค้างส่วนต่าง/คืนเงินจริง. ทั้งสองวิธีชำระ/fallback และสิทธิ์ยืนยันใช้ handler เดิม; ยอดปัจจุบันใช้บล็อกยอดหลังปรับ ก่อนหน้าร้านยืนยันจำลอง. ไม่บันทึก refund-completed/ไม่สร้าง payment log ปลอม. คืนหมดทุกจานก็ไม่ปิดโต๊ะ/ยกเลิกออเดอร์เอง. การคืนซ้ำหลัง state returned เป็น no-op ใน handler และปุ่มไม่แสดง เป็นสมมติฐาน mock เท่านั้น; concurrency/idempotency ระบบจริงยังไม่รับรอง.

## ความจุและนาฬิกาจำลอง

reset คง seed เดิม 2026-01-01T12:00:00+07:00, ทุกบัญชี demo, ทุกเมนู/แมป และคิวว่าง; เพิ่ม reset resolutions/events/adjustments/drafts เป็นว่างและ CapacitySetting=11:30–13:30, N=5, X=10. สลับบทบาทไม่ reset ข้อมูล. ไม่มีการอ่าน timezone เครื่องมาเทียบเวลา local โดยตรง: `capacityWindow()` ใช้ `iso()` เดิมที่ +07:00, ปัดนาทีลง 00/15/30/45 และ parse start พร้อม offset.

ช่วงใช้ [start,end) วันเดียว และ window [start,start+15 นาที) เป็น fixture. นับจาก `Order.confirmed_at` เฉพาะออเดอร์ที่ submit สำเร็จในหน้าต่าง รวม dine-in/takeaway; จำนวนจาน/ตะกร้า/เปิดหน้า/สลับบทบาทไม่เพิ่มจำนวน. การคืน/เปลี่ยนไม่ลดยอดนับ ไม่ reset ขณะเปลี่ยน N เป็นสมมติฐานรอ Q-V2-CAPACITY. ช่วงรับกลับบ้านยัง 15 นาที เริ่มอย่างน้อย 20 นาทีจากนาฬิกา ตามสัญญาเดิม.

ครัวเต็ม: count≥N และอยู่ในช่วง แสดงข้อความก่อนปุ่มยืนยันพร้อมป้าย X; ปุ่มยังยืนยันได้และ handler submit เดิมไม่มีกฎปฏิเสธจาก capacity. X ไม่ใช้สูตร ETA; US-07 ยังคง “ยังประมาณไม่ได้” เพราะไม่มีค่าเฉลี่ย 7 วัน/ต่อเมนูและหมายเหตุ ช. การตั้ง X เป็นตัวอย่างตามคำสั่งรัน ไม่อ้างเป็น AC ใหม่.

ฟอร์ม mock รองรับ start<end วันเดียว, N จำนวนเต็มบวก, X จำนวนเต็มไม่ติดลบเท่านั้น; error ระบุข้อจำกัด fixture. ข้ามวัน/นโยบายค่า invalid/ผลเปลี่ยนค่าระหว่างช่วงจริงยังไม่ยืนยัน. เครื่องมือเวลาเดิมขยับ +1/+5/+10 นาที/+1 วัน; ไม่มีปุ่มขยับ 1 วินาที จึงยังไม่อ้างตรวจ 12:14:59 → 12:15:00 ด้วยปุ่ม.

## ชุดตรวจที่ส่งต่อ — ยัง NOT_RUN

Evaluator ต้องเปิด file:// ใน browser context ใหม่ ปิด network ตั้ง profile/cache/temp ภายใน session รีเซ็ตทุกกรณี บันทึก browser/UTC/script/hash/actual และภาพเฉพาะที่เปิดจริง. ไม่ใช้ source inventory/syntax หรือผล baseline 19/19 เป็น PASS ของ UI v2.

รัน baseline smoke ทั้ง 19 checks จาก LAB 004: roles, table-menu, option-price, queue-order, status-sync, stock-whole, stock-option, restock, promptpay-slip, promptpay-disabled, promptpay-timeout-cash, takeaway-slot, close-table, menu-management, ingredient-mapping, pin-lock, permission-denied, account-create, reset. รวมตรวจเพิ่มตาม baseline contract: รูป jpg/png และ 2 MB, 0–10 options/ลบตัวเลือกและแมป, วันเปลี่ยน T-001, วัตถุดิบหมดซ้อน, manager ปิดขาย, reset/role/direct route, keyboard/มือถือ/desktop/overflow. tests/ui-check.py อ่านเพื่อรักษาพฤติกรรมเท่านั้น รอบนี้ไม่ได้รัน.

V2-A–F: ทำไม่ได้→แจ้งพร้อมสองปุ่ม→คง pending จนเลือก→เปลี่ยนเมนู/ตัวเลือกหรือคืน; หลาย item/หลาย order/ออเดอร์ไม่ล่าสุดต้อง scope ไม่ผิดใบ; ปฏิเสธ replacement ที่หมด; snapshot+ยอดหลังปรับลูกค้าเท่าหน้าร้าน; ราคา catalog เปลี่ยนไม่กระทบเดิม; คืนซ้ำ/คืนหมด; สถานะยังไม่จ่าย/ค้างจ่าย/จ่ายแล้วและ log เดิม; catalog ปิด/เปิดไม่ตัดสินใจแทนรายการ pending; F-01 ครัว→สถานะอาหารหน้าร้านแยก payment; ทดลองคืนเมนูแทนต่อด้วยและตรวจ revision.

US-09 และ US-14 ต้องจัดชุด **5 จาก 5 กรณีแยกแต่ละ US** ครอบเปลี่ยนและคืน ไม่กำหนดสัดส่วนใหม่. จุดวัด US-09 ครัวกด→ลูกค้าเห็นแจ้งพร้อมปุ่ม **10 วินาทีบน LAN**; US-14 ลูกค้าเลือกสำเร็จ→ครัวอัปเดต/ลบ **10 วินาทีบน LAN**. สลับบทบาทในแท็บเดียวพิสูจน์ได้เพียง mock ไม่แทน LAN.

US-21 ต้อง **N=5 ผ่าน 3 จาก 3 รอบ**: context ใหม่แต่ละรอบ ตั้ง 11:30–13:30; รอบ 1 เวลา 12:00, รอบ 2 +10m/+5m ถึง 12:15, รอบ 3 +10m สามครั้งถึง 12:30. แต่ละรอบส่ง 4→5 ออเดอร์แล้วลูกค้าใหม่เห็นคำเตือนก่อนยืนยัน; หลายจานนับหนึ่งออเดอร์; สลับบทบาทไม่เพิ่มจำนวน; ยืนยันใบถัดไปยังได้; บันทึก count/confirmed_at/ข้อความ/ปุ่มก่อนและหลัง. เพิ่ม boundary 00/15/30/45, นอกช่วง/ตรงสิ้นสุด, เปลี่ยน N/X, คืน/เปลี่ยนการนับ และสิทธิ์เข้าหน้า capacity ทั้ง login/direct URL. ก่อนขอบหนึ่งวินาทียัง NOT_TESTED จนมีวิธีที่เก็บหลักฐานจริงได้. ไม่อ้างสามภาพแทนสามรอบ.

เกณฑ์ regression จริงตาม FR/outline คงเดิมทั้งหมด เช่น US-05/11 **5 วินาที / อย่างน้อย 18 จาก 20**, US-08 **อย่างน้อย 19 จาก 20** และ fallback **3 จาก 3**, US-19 snapshot **5 จาก 5**; smoke ไม่มีสิทธิ์ลดสัดส่วน. LAN/Wi-Fi/หลายอุปกรณ์/โหลด/concurrency/เงินจริง/ETA 7 วัน/server log/auth-security/Ubuntu/ติดตั้ง/ถอดอินเทอร์เน็ตจริงยัง **NOT_TESTED**.

## ข้อค้าง

หมายเหตุ ก./ค./ช., Q เดิม/Q-V2-REFUND/STATE/CAPACITY, mapping เสร็จแล้ว↔พร้อมเสิร์ฟ, aggregate/ETA, วิธีคืน/ผู้อนุมัติ/ส่วนต่าง/คืนซ้ำ, สูตร X/เขตเวลา/รอยต่อ/เปลี่ยน N/นับคืน, Q-20 ที่ยังอ้าง US-14 และ Unknown permissions ยังคงเปิด. ไม่อ่าน reveal-2 และไม่เพิ่มหน้ารายงานใหม่. การยืนยันกฎร้านจริง BLOCKED ตาม limits; offline mock ที่ติดป้ายสมมติฐานทำได้. สถานะ EXECUTED ของงาน AI ไม่ใช่สถานะ item/order/payment/table และไม่ใช่ Evaluator PASS.
