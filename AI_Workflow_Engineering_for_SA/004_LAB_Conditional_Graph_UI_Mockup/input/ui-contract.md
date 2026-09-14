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
