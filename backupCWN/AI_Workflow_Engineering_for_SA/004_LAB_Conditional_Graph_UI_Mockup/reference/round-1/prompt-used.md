# ขั้น 4.1 — สร้าง UI Mock-up ที่เล่นได้

## บริบทและ Input
คุณเป็นผู้พัฒนา Mock-up ให้ SA ของครัวคุณยาย เริ่ม session ใหม่จากโฟลเดอร์ LAB 004
อ่าน work/input-source.md, work/input-audit.md, work/session-plan.md และ work/upstream/ ทุกไฟล์ตาม manifest
อ่าน flow-customer.md, flow-kitchen-front.md, flow-manager.md, state-machine.md, structure.md, flow-merge.md จาก snapshot
อ่าน input/mock-data.json, input/ui-contract.md, tests/ui-check.py และ ../docs/case-study-source.md
ถ้า Input ไม่ READY หรือมีข้อขัดแย้งที่ปิดกั้นงาน ให้รายงาน BLOCKED ไม่สร้าง flow/FR ขึ้นเอง
## งาน
สร้าง work/ui-mockup.html ไฟล์เดียว มี HTML/CSS/JavaScript และข้อมูลจำลองจาก input/mock-data.json ฝังในไฟล์
เปิดด้วย file:// ได้โดยไม่ใช้ server, fetch JSON, CDN, web font, รูปหรือทรัพยากรออนไลน์ทุกชนิด
ใช้แถบสลับบทบาท 3 บทบาท: ลูกค้า / ครัวและหน้าร้าน / ผู้จัดการ; แยกสิทธิ์ kitchen กับ front ด้วยฟอร์มชื่อผู้ใช้และ PIN จำลอง
แสดงป้าย “จำลอง” ให้ชัดสำหรับ PromptPay, QR โต๊ะ, การแจ้งเตือน, เวลา, PIN/สิทธิ์ และการสลับบทบาท
ลูกค้าเลือกโต๊ะหรือกลับบ้าน → เมนู → ตัวเลือก → ตะกร้า → ส่งออเดอร์ → ติดตามสถานะ → เงินสด/PromptPay
ครัวเห็นคิวเรียง timestamp วินาที/เลขออเดอร์และเปลี่ยนสถานะทีละขั้น; วัตถุดิบหมด/กลับมามีมีผลตามแมป
หน้าร้านแสดงโต๊ะ/T-001, ยอด snapshot, สถานะจ่าย; ยืนยันสลิป/รับเงินสดพร้อม log ชื่อผู้ใช้สมมติและเวลา; ปิดโต๊ะเริ่ม session ใหม่
ผู้จัดการแยกหน้าจัดการเมนูออกจากแมปวัตถุดิบ มีบัญชี/PIN และตั้งค่า PromptPay
เพิ่ม/แก้/ลบเมนู ราคา รูป jpg/png <=2 MB และตัวเลือก 0–10; ลบเมนูที่แมปแล้วต้องเตือนและลบแมป; ยอดออเดอร์เก่าห้ามเปลี่ยน
หน้าแมปเลือกได้เฉพาะเมนู/ตัวเลือกที่สร้างแล้ว แยกทั้งจานกับเฉพาะตัวเลือกและมีผลต่อการปิด/เปิดจริง
ตรวจ stock ซ้ำตอนส่ง ปฏิเสธตะกร้าที่เพิ่มไว้ก่อนวัตถุดิบหมด; ห้ามเพิ่มใบครัวเมื่อปฏิเสธ
PromptPay ค้างจ่ายจนหน้าร้านยืนยัน; เมื่อปิดบริการหรือไม่ยืนยันถึง 10 นาทีแสดงเงินสด; กดเลือกเงินสดไม่เท่ากับรับเงิน
กลับบ้านเลือก slot 15 นาทีเริ่มอย่างน้อย 20 นาทีจากเวลาจำลอง; T-001 เพิ่มต่อเนื่องและเริ่มใหม่เมื่อวันเปลี่ยน
บัญชีใหม่ใช้ชื่อ 3–20 ตัวอักษร/ตัวเลข PIN 4–6 หลัก; ผิด 5 ครั้งติดล็อก 5 นาทีตามนาฬิกาจำลอง; route ผู้จัดการต้องปฏิเสธ kitchen/front
มีปุ่มรีเซ็ตคืน seed/เวลา/บัญชี/แมป/คิวและออกจากระบบ; บอกวิธีใช้บนหน้า; ใช้ CSS รองรับมือถือและคีย์บอร์ด
## สัญญา data-testid ที่ต้องมีครบ
ใช้ชื่อและชนิด controls ต่อไปนี้ตรงกับ input/ui-contract.md; รายการซ้ำต้องอยู่ใน container ตาม contract
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

## ข้อจำกัดและความถูกต้อง
ห้ามลดเกณฑ์ใน tests หรือ input เพื่อให้ผ่าน ห้ามใช้บัญชีจริง อีเมล token ข้อมูลลูกค้าจริง หรือการโอนเงินจริง
เลือกแท็บพนักงาน/ผู้จัดการใหม่ต้อง login ใหม่; ลูกค้าไม่ต้อง login; ห้ามสืบทอดสิทธิ์บัญชีก่อน
ใช้ native disabled สำหรับเมนู/ตัวเลือกที่หมด แต่ปุ่มส่งตะกร้า stale ต้องให้กดเพื่อแสดงปฏิเสธ
ใช้ state กลางในแท็บ ไม่จำลองด้วยแค่ alert; เก็บแยก order/items/payment/table-session ตาม structure
รักษา A-02 และข้อสงสัย DI-04/A-03 ของ US-20; การแมปชื่อสถานะตาม DI-07/A-05 ต้องเปิดเผยว่ายังไม่ยืนยัน
ไม่กล่าวว่า UI ผ่านเกณฑ์ LAN, หลายเครื่อง, load, authentication หรือจำนวนตัวอย่างจริงของ US
ไม่แก้ work/upstream/, tests/, input/, prompts/, reference/ หรือ img/ ไม่เรียก agent เพิ่ม
## Output และตำแหน่งบันทึก
เขียน work/ui-mockup.html และ work/build-notes.md อธิบาย Flow/FR/US → หน้าจอ, สมมติฐาน และส่วนจำลอง
ถ้ามี work/ui-mockup.html เดิมให้หยุดเพื่อเก็บชุดเดิมก่อน ไม่เขียนทับ; ผู้เรียนต้องตรวจและ snapshot ก่อนแก้รอบต่อไป
อย่าเขียนผลผ่านหรือภาพขึ้นเอง ให้ผู้เรียนรัน tests/ui-check.py เพื่อได้ JSON และ screenshot จริง
