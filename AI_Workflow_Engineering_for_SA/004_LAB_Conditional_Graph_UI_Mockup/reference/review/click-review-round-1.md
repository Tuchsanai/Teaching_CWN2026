**บันทึกลำดับคลิกจริง — รอบ 1**

ตรวจเมื่อ 2026-09-14T12:16:53.232505+00:00 · [ผลเทียบ Flow/Structure](review.md)

ตรวจ HTML SHA-256 `d2b7bfa0cff5700d3ca07f611c03cfa0304c54eafb51387f125e95edd11f7803` ซึ่งเป็นสำเนา reference เปิดผ่าน file:// ด้วย Python Playwright / Chromium 151.0.7922.34 headless หลัง Browser MCP ปฏิเสธ file:// นี่คือการรันจริงของผู้ตรวจบนสำเนา ไม่ใช่หลักฐานการสร้าง UI ของนักศึกษา

เรียกฟังก์ชัน check เดิมจาก tests/ui-check.py โดยไม่แก้ assertions ใช้ context ใหม่และกดresetก่อนแต่ละcheck ไม่resetกลางการส่งต่องานเดียวกัน; หนึ่งแท็บแชร์ข้อมูล3บทบาท เข้าบัญชีใหม่ทุกครั้งที่เลือกแท็บเจ้าหน้าที่/ผู้จัดการ เก็บการคลิก/กรอก/selectและอ่านข้อความDOMหลังactionในสคริปต์ชั่วคราว ผลด้านล่างมาจากการรัน browser ไม่อนุมานจากโค้ด

**ผลการคลิก19checksตามตารางREADME ทั้งสองขนาดจอ**

D=1280×900 และ M=390×844 ทั้ง19รายการผ่านทั้งD/M รวม38executions ไม่มี pageerror ที่บันทึกใน38รายการ คอลัมน์READMEบอกลำดับที่ครอบคลุม; บางกรณีแบ่งหลายcheckและใช้โต๊ะ01แทน02ตามที่ระบุ ภาพเป็นสถานะปลายทางของcheck จึงใช้คู่กับลำดับและข้อความที่อ่านระหว่างคลิก ไม่ใช่หลักฐานทุกขั้นในภาพเดียว

| check ID | README | ลำดับที่ทำจริง (หลังreset) | ผลที่เห็น/อ่านจากUIจริง | ผล D/M | ภาพใหม่ D/M |
|---|---|---|---|---|---|
| roles | ลูกค้า1; ผู้จัดการ1 | ลูกค้าเปิดเมนู → demokitchen/0000 → demofront/0000 → demomanager/0000 | พบ3แท็บและหน้าบทบาทตามสิทธิ์; ภาพสุดท้ายอยู่หน้าเมนูผู้จัดการ | ผ่าน/ผ่าน (mock) | [D](manual-shots/round-1/desktop-roles.png) / [M](manual-shots/round-1/mobile-roles.png) |
| table-menu | ลูกค้า1; หน้าร้าน1 | เลือกโต๊ะ02 → เปิดเมนู → ส่งm01 → หน้าร้าน | active-table02; #1ใบหน้าร้าน data-table-id02 ยอด50 | ผ่าน/ผ่าน (mock) | [D](manual-shots/round-1/desktop-table-menu.png) / [M](manual-shots/round-1/mobile-table-menu.png) |
| option-price | ลูกค้า2–4; ครัว2 | เปิดโต๊ะ01 → m01 → เพิ่มไข่ → เพิ่มตะกร้า → ส่ง → ครัว | 50→60; ตะกร้า60; ใบครัวมีเพิ่มไข่ดาว60 | ผ่าน/ผ่าน (mock) | [D](manual-shots/round-1/desktop-option-price.png) / [M](manual-shots/round-1/mobile-option-price.png) |
| queue-order | ครัว1 | โต๊ะ01 ส่งm01 แล้วm02 ขณะนาฬิกาค้าง → ครัว | #1,#2 เวลา12:00:00+07:00เท่ากัน เรียงเลข1,2 | ผ่าน/ผ่าน (mock) | [D](manual-shots/round-1/desktop-queue-order.png) / [M](manual-shots/round-1/mobile-queue-order.png) |
| status-sync | ลูกค้า5; ครัว3 | ส่งm01 → ครัวกดถัดไป → ลูกค้า → หน้าร้าน → ทำอีกครั้ง | รับออเดอร์→กำลังทำ→เสร็จแล้วตรง3หน้าจอ ไม่มีreload | ผ่าน/ผ่าน (mock) | [D](manual-shots/round-1/desktop-status-sync.png) / [M](manual-shots/round-1/mobile-status-sync.png) |
| stock-whole | ครัว4–5 | เพิ่มm01ยังไม่ส่ง → ครัวchickenหมด → ลูกค้า → ส่งตะกร้าเดิม → ครัว | m01 disabled; ข้อความหมด; ไม่มีใบครัวเพิ่ม (0) | ผ่าน/ผ่าน (mock) | [D](manual-shots/round-1/desktop-stock-whole.png) / [M](manual-shots/round-1/mobile-stock-whole.png) |
| stock-option | ครัว7–8ส่วนปฏิเสธ | เพิ่มm01+ไข่ → ครัวeggหมด → ลูกค้าเปิดm01 → ส่ง → ครัว | m01ยังเปิด ไข่เพิ่มdisabled; ปฏิเสธตะกร้าเดิม คิว0 | ผ่าน/ผ่าน (mock) | [D](manual-shots/round-1/desktop-stock-option.png) / [M](manual-shots/round-1/mobile-stock-option.png) |
| restock | ครัว6,8ส่วนเติม | chickenหมด→เติม → eggหมด→เติม → เลือกไข่ → ส่ง → ครัว | เมนู/ไข่เปิดคืน และมีใบครัวเพิ่มไข่1ใบ | ผ่าน/ผ่าน (mock) | [D](manual-shots/round-1/desktop-restock.png) / [M](manual-shots/round-1/mobile-restock.png) |
| promptpay-slip | ลูกค้า6–7 | ส่งm01+ไข่ → PromptPay → หน้าร้านอ่าน60 → ยืนยันสลิป → ลูกค้า | ยังไม่จ่าย→ค้างจ่าย→จ่ายแล้ว; log demofront/ISO/order ID | ผ่าน/ผ่าน (mock) | [D](manual-shots/round-1/desktop-promptpay-slip.png) / [M](manual-shots/round-1/mobile-promptpay-slip.png) |
| promptpay-disabled | ลูกค้า9 | ส่งm01 → ผู้จัดการปิดPromptPay → ลูกค้า | cash-messageมีเงินสด; ไม่จ่ายแล้วแม้เวลาเดิม | ผ่าน/ผ่าน (mock) | [D](manual-shots/round-1/desktop-promptpay-disabled.png) / [M](manual-shots/round-1/mobile-promptpay-disabled.png) |
| promptpay-timeout-cash | ลูกค้า8; หน้าร้าน2–3บางส่วน | ส่งm01 → PromptPay → +10นาที → เงินสด → หน้าร้านรับเงิน → ลูกค้า | ครบ10นาทียังค้างจ่ายและแจ้งเงินสด; ยืนยันหน้าร้านแล้วจ่ายแล้ว | ผ่าน/ผ่าน (mock) | [D](manual-shots/round-1/desktop-promptpay-timeout-cash.png) / [M](manual-shots/round-1/mobile-promptpay-timeout-cash.png) |
| takeaway-slot | ลูกค้า10–11; หน้าร้าน1บางส่วน | กลับบ้าน → เลือก12:30–12:45 → ส่ง → ครัว/หน้าร้าน → ลูกค้าส่งm02 | ช่วง15นาทีเริ่ม≥20นาที; T-001แล้วT-002; ครัวมีป้าย/ช่วงรับ | ผ่าน/ผ่าน (mock) | [D](manual-shots/round-1/desktop-takeaway-slot.png) / [M](manual-shots/round-1/mobile-takeaway-slot.png) |
| close-table | หน้าร้าน5–6 (โต๊ะ02ตรวจเพิ่มด้านล่าง) | โต๊ะ01ส่งm01 → หน้าร้านรับเงิน → ปิด01 → ลูกค้าเปิด01 → ส่งm02 | S-0001→S-0002; ก่อนส่งใหม่order-idว่าง/cart0/ยังไม่จ่าย; ใบใหม่55 | ผ่าน/ผ่าน (mock) | [D](manual-shots/round-1/desktop-close-table.png) / [M](manual-shots/round-1/mobile-close-table.png) |
| menu-management | ผู้จัดการ1–3; ลบเมนูไม่มีแมป | ส่งm01 → managerแก้50→65 → ลูกค้า/หน้าร้าน → สร้างm09ราคา70ตัวเลือก5 → ลบm09 | ราคาใหม่65แต่ใบเดิม50; m09สร้าง/ลบได้; ไม่ครอบคลุมรูปและ10ตัวเลือก | ผ่าน/ผ่าน (mock) | [D](manual-shots/round-1/desktop-menu-management.png) / [M](manual-shots/round-1/mobile-menu-management.png) |
| ingredient-mapping | ผู้จัดการ5–7 | managerแมปm02 whole milk → ครัวmilkหมด/เติม → แมปm01 option extra-egg milk → ทำหมด | m02ปิด/เปิดคืน; m01ยังเปิดแต่ไข่disabled; seed menu IDsครบ | ผ่าน/ผ่าน (mock) | [D](manual-shots/round-1/desktop-ingredient-mapping.png) / [M](manual-shots/round-1/mobile-ingredient-mapping.png) |
| pin-lock | ผู้จัดการ11–12 | demokitchen PIN9999×5 → PIN0000ระหว่างล็อก → +10นาที → PIN0000 | ระหว่างล็อกปฏิเสธ; +10นาทีเข้าได้; ภาพปลายทางไม่ได้แสดงล็อก | ผ่าน/ผ่าน (mock) | [D](manual-shots/round-1/desktop-pin-lock.png) / [M](manual-shots/round-1/mobile-pin-lock.png) |
| permission-denied | หน้าร้าน7 | login kitchen/front → เปลี่ยนURL hash /manager/menu และ /manager/reports → managerเข้าเมนู | 2บัญชี×2หน้า denied และไม่แสดงsection; managerเข้าได้; ภาพปลายทางเป็นmanager | ผ่าน/ผ่าน (mock) | [D](manual-shots/round-1/desktop-permission-denied.png) / [M](manual-shots/round-1/mobile-permission-denied.png) |
| account-create | ผู้จัดการ9–10 | manager → ab/123/front บันทึก → demonew/1234 บันทึก → loginใหม่ → /manager/menu | ข้อมูลสั้นถูกปฏิเสธ; demonewเข้าfrontได้แต่manager/menuไม่ได้ | ผ่าน/ผ่าน (mock) | [D](manual-shots/round-1/desktop-account-create.png) / [M](manual-shots/round-1/mobile-account-create.png) |
| reset | วิธีรีเซ็ต; ไม่ครอบคลุมทุกชนิดข้อมูลเพิ่มพร้อมกัน | ส่งm01 → chickenหมด → ปิดPromptPay → +10นาที → reset → ตรวจลูกค้า/ครัว/manager | เวลา12:00 คิวว่าง cart0 ยังไม่จ่าย m01เปิด PromptPayเปิด | ผ่าน/ผ่าน (mock) | [D](manual-shots/round-1/desktop-reset.png) / [M](manual-shots/round-1/mobile-reset.png) |

**คลิกตรวจเพิ่มจาก README และจุดที่ tests ไม่ครอบคลุม — desktop1280×900**

แต่ละกลุ่มเริ่มcontextใหม่/reset; ภายในกลุ่มรักษาข้อมูลส่งต่อ บัญชีเป็นplaceholderเท่านั้น ชื่อกลุ่มด้านล่างเป็นชื่อการตรวจของผู้ตรวจ ไม่ใช่ check ID ใหม่ในJSON

| กลุ่ม / README | ลำดับคลิก/ข้อมูลที่ทำจริง | ผลที่เห็นจริง | ผลและหลักฐาน |
|---|---|---|---|
| วัตถุดิบ5ชนิด / ครัว9–10 | เปิดเมนู → ครัวเลือก rice/chicken/pork/egg/milk ทีละตัว ทำหมด → ลูกค้าอ่านdisabled → เติมก่อนตัวถัดไป | riceปิดm01,m02,m03,m05,m06; chickenปิดm01,m04,m06; porkปิดm02,m05; eggปิดm03,m07และไข่เพิ่ม แต่m01เปิด; milkปิดm08; เติมแล้วเปิดคืน | ผ่านmock; อ่านDOMจริงทุกชุด |
| หมดซ้อนและปิดขาย / ครัว9 | chickenหมด+basilหมด → เติมchickenอย่างเดียว → ลูกค้า; เติมbasil → ผู้จัดการปิดขายm01 → chickenหมด/เติม | m01ยังปิดเมื่อbasilหมด; เมื่อไม่มีเหตุหมดเปิดได้; ปิดขายmanagerยังคงปิดหลังเติม | ผ่านcontract mock; [ภาพ](manual-shots/round-1/extra-stock-overlap.png); ไม่ปิดQ-12/Q-13 |
| ราคาและยอดเดิม5ใบ / ผู้จัดการ1–2 | ลูกค้าส่งm01จำนวน5ใบ สลับไม่ไข่/ไข่ → managerแก้จาน65 ไข่20 → หน้าร้านอ่านยอดทุกใบ | [50,60,50,60,50] ก่อนและหลังเท่ากันทั้ง5ใบ | ผ่านmock; [ภาพที่ถ่าย](manual-shots/round-1/extra-snapshot-five.png); หลักฐานยอดมาจากDOMทั้ง5ใบ ภาพนี้ยังไม่ได้เปิดตรวจรายละเอียดทุกใบ |
| ลบเมนูมีแมป / ผู้จัดการ8 ใช้m01แทนm02 | managerเลือกm01 → ลบ → อ่านdialogและCancel → หน้าแมป → กลับเมนูลบและAccept → หน้าแมป/หน้าร้าน | dialogเตือนลบแมปทั้งหมดของเมนู/ตัวเลือก; Cancelยังมีm01; Acceptลบm01ทั้งwhole/optionแต่m02อยู่; ใบเก่า5ใบยังคงยอด/ชื่อ | ผ่านmock; [ภาพแมปหลังลบ](manual-shots/round-1/extra-delete-mapping.png); dialogอ่านจริงแต่ไม่มีภาพnative dialog |
| ไฟล์รูป / ผู้จัดการ4 | กรอกเมนู70 → อัปโหลดPNG/JPG4×4ที่สร้างเป็นtest inputใน/tmp → PNG2,000,000ไบต์ → บันทึก → PNG2,000,001ไบต์/ไฟล์txt/PNGsignatureปลอม → บันทึก → เลือกPNGถูกต้องใหม่ | ไฟล์ปกติและ2,000,000รับ; เกินขนาด/txt/signatureปลอมปฏิเสธ; เมื่อรูปผิดกันบันทึก; กลับเลือกรูปถูกต้องได้ | ผ่านนโยบายmock; [ภาพปฏิเสธ](manual-shots/round-1/extra-retry-image-rejected.png); test inputไม่ใช่ภาพผลรันและไม่เก็บในmanual-shots; Q-19นิยามMBยังเปิด |
| ตัวเลือก0–10 / ผู้จัดการ3–4 | เมนูm09ราคา70 → เพิ่มตัวเลือก1–10ราคา5ทุกตัว → บันทึก → ลองตัวเลือก11 → ลูกค้าเปิดm09 → managerลบตัวเลือกทั้งหมดแล้วบันทึก | บันทึก10ได้; ข้อความปฏิเสธ11และจำนวนคง10; ลูกค้ามีรูปและ10checkbox; ลบทั้งหมดกลับ0ได้ | ผ่านmock; [ภาพ10/10และปฏิเสธ11](manual-shots/round-1/extra-retry-options-limit.png) |
| เลขรับข้ามวัน / ลูกค้า10–11 | กลับบ้านส่ง2ใบ → +1วัน → ส่งใบ3 → หน้าร้าน | T-001,T-002→วันใหม่T-001; order-id3; ใบแสดงวัน01/02แยกกัน | ผ่านmock; [ภาพ](manual-shots/round-1/extra-day-identifiers.png) |
| ขอบเที่ยงคืน / ขยายลูกค้า10–11 | reset → กลับบ้าน → +10นาที71ครั้งถึง23:50 → ส่ง2ใบ → +10นาทีถึง00:00 → ส่งใบ3 → หน้าร้าน | 23:50ช่วงแรก00:15–00:30วันถัดไป; ใบ1/2 T-001/T-002; 00:00ใบ3 T-001 ช่วง00:30–00:45 เลขorderไม่รีเซ็ต | ผ่านmock; [ภาพเที่ยงคืน](manual-shots/round-1/extra-midnight.png); อิง+07:00จำลอง ไม่อนุมัติtimezoneธุรกิจ |
| ช่วงรับเดิมเก่า / ขยายลูกค้า10 | resetเวลา12:00 → กลับบ้านเลือก12:30–12:45 → ใส่m01ตะกร้า → +10นาที2ครั้ง → อ่านselect → ส่ง → ครัว | selectเปลี่ยนเองเป็น12:45–13:00; ไม่มีข้อความขอให้ยืนยันช่วงใหม่; ใบครัวใช้12:45–13:00 | พบข้อเสนอให้SAตัดสินด้านUX แม้ขั้นต่ำ20นาทียังถูก; [ภาพ](manual-shots/round-1/extra-slot-reselected.png) |
| หน้าร้านสองช่องทาง / หน้าร้าน1–4 | โต๊ะ02ส่งm01→เงินสด → กลับบ้านส่งm02→PromptPay → demofrontรับเงินสดใบ1/ยืนยันสลิปใบ2 | table_id02กับtakeawayแยกกัน;50/55; เลือกเงินสดยังไม่จ่าย; ยืนยันแล้วทั้ง2จ่ายแล้วพร้อมlog | ผ่านmock; [ภาพ](manual-shots/round-1/extra-front-two-channels.png) |
| ปิดsession/เปิดใหม่ / หน้าร้าน5–6 | หลังกลุ่มก่อนปิดโต๊ะ02 → ลูกค้าสลับกลับdine-in → ก่อนเปิดใหม่ตรวจไม่มีปุ่มส่ง → เปิด02 → ส่งm02 → หน้าร้าน; เปิดโต๊ะ03จากหน้าร้านแล้วลูกค้าเปิด03 | sessionเดิมไม่มีปุ่มส่ง; sessionใหม่ต่างเดิม/order-idว่าง/ยังไม่จ่าย; ใบ3ยอด55ไม่รวมเก่า; หน้าร้านใบ1มีป้ายประวัติ; โต๊ะ03เปิดได้ | ผ่านUI mock; [ภาพที่ถ่าย](manual-shots/round-1/extra-session-history.png); ยังไม่ส่งstale payloadโดยตรง |
| สิทธิ์6กรณี / หน้าร้าน7และผู้จัดการ10 | สร้างdemonew/1234/front → loginทีละdemokitchen,demofront,demonew → เปลี่ยนhashไป /manager/menu และ /manager/reports | ทุกคู่รวม6ครั้ง auth-messageมีปฏิเสธ; menu-admin/report-screenไม่แสดง | ผ่านmock; [ภาพการปฏิเสธ](manual-shots/round-1/extra-permissions-six.png); ใช้hashnavigationในแท็บ ไม่ใช่ยิงbackend |
| ไม่สืบทอดสิทธิ์และล็อก / ผู้จัดการ11–12 | managerเข้าได้→กดแท็บmanagerใหม่ → ตรวจlogin → kitchen PIN9999×5 → +1นาที4ครั้ง→0000 → +1นาที→0000 | กดแท็บใหม่ต้องlogin; ผิด5ครั้งล็อกถึง12:05; นาที4 PINถูกยังล็อก นาที5เข้าได้ | ผ่านmock; [ภาพล็อก](manual-shots/round-1/extra-pin-locked.png) |
| สลิปหลังfallback / ลูกค้า6–9 | ส่งm01+ไข่→PromptPay→+10นาที→managerปิดPromptPay→frontยืนยันสลิป→ลูกค้า→+10นาที | เริ่มค้างจ่ายและQRจำลอง; timeoutไม่จ่ายเอง; แม้ปิดช่องทางยังยืนยันสลิปเดิมได้; จ่ายแล้วไม่ย้อนและcash-messageว่างหลังเพิ่มเวลา | ผ่านmock; อ่านDOMจริง; ภาพที่ถ่าย [ค้างจ่าย](manual-shots/round-1/extra-promptpay-pending.png), [หลังยืนยัน](manual-shots/round-1/extra-slip-after-fallback.png) ยังไม่ได้เปิดดูสองภาพนี้ |

**เหตุขัดข้องของเครื่องมือและการตรวจซ้ำ**

การตรวจรูปครั้งแรกดำเนินถึงปฏิเสธไฟล์แล้วติด `Page.wait_for_function: EvalError ... unsafe-eval` จากCSPของหน้า นี่เป็นคำสั่งรอของสคริปต์ผู้ตรวจ ไม่ใช่UI/assertionธุรกิจตก ส่วนตัวเลือกที่ต่อจากนั้นยังไม่ได้รันในครั้งแรก เก็บภาพ extra-image-options-failure.png ไว้ตามที่ถ่ายจริง (ไม่ได้เปิดภาพนี้เพื่อวินิจฉัย ใช้errorlog) เปลี่ยนเฉพาะสคริปต์ชั่วคราวให้รอด้วยlocator assertionแล้วตรวจกลุ่มรูป/ตัวเลือกซ้ำในcontextใหม่ ผลครบตามตาราง ชื่อภาพซ้ำใช้extra-retry-* ไม่ทับครั้งแรก ไม่แก้CSP/HTML/tests/JSONเดิม และไม่นับretryเป็นกรณีใหม่หรือroundใหม่

**ภาพเดิมรอบ1ที่เปิดดูจริงทั้ง19ภาพ**

ภาพอยู่ในshots/round-1 และทุกภาพเหมือนreference จึงใช้บอกได้เฉพาะสิ่งที่ภาพแสดง ไม่รับรองผลงานนักศึกษา: roles/permission-denied/resetเป็นหน้าmanager; table-menuเป็นหน้าร้านโต๊ะ02; option-priceเป็นใบครัวเพิ่มไข่60; queue-orderแสดง2ใบ; status-syncเป็นหน้าร้านเสร็จแล้วแต่ยังไม่จ่าย; stock-whole/stock-optionเป็นครัวว่างและวัตถุดิบหมด; restockมีใบเพิ่มไข่และไข่กลับมามี; promptpay-slip/timeout-cashเป็นลูกค้าจ่ายแล้ว; promptpay-disabledมีข้อความเงินสด; takeaway-slotแสดงT-002; close-tableแสดงประวัติS-0001และใบS-0002; menu-managementแสดงราคาใหม่65กับยอดเดิม50; ingredient-mappingแสดงm02/m08หมดและไข่เพิ่มdisabled; pin-lockเป็นครัวหลังปลดล็อก; account-createเป็นdemonewถูกปฏิเสธหน้าmanager ภาพเหล่านี้ไม่พิสูจน์ทุกขั้นก่อนหน้า

**ตรวจขนาดจอและการเปิดดูภาพใหม่**

19checksคลิกทั้งdesktop1280×900/mobile390×844 และบันทึกภาพfull-pageหลังแต่ละcheck; scrollWidth=1280/390ตามviewportทุกครั้ง ตรวจเพิ่มกรอบcontrolsแนวนอนในหน้าลูกค้าไม่พบนอกขอบ ไม่ได้ทดสอบtouch/keyboardจริงบนอุปกรณ์มือถือ

เปิดดูภาพใหม่ด้วยview_imageจริง: mobile-option-price, mobile-table-menu, mobile-roles, mobile-promptpay-slip; desktop-viewport-cart, mobile-viewport-top, mobile-viewport-cart; extra-permissions-six, extra-pin-locked, extra-delete-mapping, extra-front-two-channels, extra-retry-image-rejected, extra-retry-options-limit, extra-slot-reselected, extra-day-identifiers, extra-midnight ภาพใหม่อื่นที่ถ่ายไว้ยังไม่ได้เปิดตรวจด้วยสายตาโดยผู้ตรวจ จึงใช้เฉพาะผลคลิก/DOMที่บันทึก ไม่อ้างผลด้านภาพจากชื่อไฟล์

ภาพviewportเพิ่ม [desktop](manual-shots/round-1/desktop-viewport-cart.png) และ [mobile](manual-shots/round-1/mobile-viewport-cart.png) แสดงยอด60และETAยังประมาณไม่ได้ชัดเจน; [mobileหน้าบน](manual-shots/round-1/mobile-viewport-top.png) แสดงว่าส่วนหัวกินพื้นที่มากและยังไม่เห็นเมนูอาหารบนจอแรก แต่เลื่อนและคลิกตามcheckได้ ภาพviewportเหล่านี้มีขนาดพิกเซลตามจอที่ขอ; ภาพfull-pageสูงกว่าviewportโดยตั้งใจ; ภาพelementเป็นการจับsectionจริงจากbrowser ไม่ใช่ภาพตัดต่อ

**รายการยังไม่ได้ทดสอบ / ห้ามนับผ่าน**

- ETAตามสูตร/ความแม่นยำและserver logพร้อมเสิร์ฟ; การแมปสถานะA-05; ผลภายใต้ประวัติไม่พอรอSA — เห็นplaceholderจริงแต่ยังไม่มีการคำนวณให้ทดสอบ
- QRกล้อง/URL table_idผิด, stale session request/API, การสั่งชนstockหมด/ปิดโต๊ะ, eventซ้ำ/ผิดลำดับ, หลายbrowser/หลายอุปกรณ์และการรักษาข้อมูลหลังrestart
- LAN latency,โหลด,สัดส่วนตัวอย่าง20โต๊ะ/20ใบ,ติดตั้งUbuntu30นาที,เน็ตภายนอกหลุด,ความปลอดภัย/PIN/backend/ข้อมูลถาวร,ตรวจธนาคารหรือชำระเงินจริง
- รูปและ10ตัวเลือกตรวจเพิ่มบนdesktopเท่านั้น; ยังไม่ได้คลิกชุดรูป/10ตัวเลือกบนmobile และยังไม่ได้ตรวจทุกชนิดรูปเสีย/ทุกขอบขนาดJPG/2MiB (นิยามMBต้นทางยังค้าง)
- ลบตัวเลือกที่มีแมปโดยตรง, เปลี่ยนแมประหว่างวัตถุดิบหมด, กดหมดซ้ำ, ทดสอบnoodleเดี่ยว ๆ; ตรวจstock5ชนิดและbasilซ้อนตามที่บันทึกเท่านั้น
- resetล้างบัญชีใหม่/แมปใหม่/history/lockพร้อมกันครบทุกประเภท (อ่านresetในโค้ดแต่ไม่ได้ออกกรณีคลิกครบ); ชื่อบัญชีทุกboundary/Unicode/ซ้ำ และสิทธิ์อื่นที่structureระบุUnknown
- คงตะกร้าระหว่างสลับหลายโต๊ะที่ต่างมีตะกร้า, ทุกปุ่มเลือกจ่ายออเดอร์เก่าในdetails, screenshotใหม่ทุกไฟล์, accessibility/contrastทั้งระบบ
- การรีเฟรชหน้าแล้วเห็นเมนูใหม่ตามACจริง: HTMLใช้memoryและreloadเริ่มseedใหม่ จึงไม่ใช่หลักฐานผ่านพฤติกรรมหลายclient/refreshของระบบจริง

คง A-02, DI-04/A-03, DI-07/A-05, MC-01–MC-03 และข้อค้างต้นทางตามรายงานAI; raw edge JSONยังpass จำนวน19/0 ไม่เปลี่ยน ผลความเห็นETA/ช่วงรับต้องส่งSAตัดสินและเปิดชุดงานใหม่ตามขอบเขตที่ยืนยัน ไม่วนแก้รอบนี้เกินเพดาน

**ทะเบียนภาพใหม่ที่ถ่ายจริง**

รวม 59 ภาพ; SHA-256/ขนาดช่วยระบุไฟล์ ไม่ได้แทนการเปิดดูภาพ รายการเปิดดูจริงอยู่ย่อหน้าก่อนหน้า

| ไฟล์ | ขนาดพิกเซล | SHA-256 |
|---|---|---|
| [desktop-account-create.png](manual-shots/round-1/desktop-account-create.png) | 1280×900 | `32bef3ffbee5f1b17c2004af25bfc70b4a49f62b552e2f313b08435a3ec609f9` |
| [desktop-close-table.png](manual-shots/round-1/desktop-close-table.png) | 1280×2121 | `4c91b246ebe069c583b50d683985000b491adfbf4383fda3d9eafda0fe0b8f9a` |
| [desktop-ingredient-mapping.png](manual-shots/round-1/desktop-ingredient-mapping.png) | 1280×1969 | `9f7fb1b960bf6856c5c098ed0d411e770413fa553720588d99dd7df5af146425` |
| [desktop-menu-management.png](manual-shots/round-1/desktop-menu-management.png) | 1280×1992 | `7407e8d1c334564e8999f258fcf6d0b2e35454fc99d56a312194eeb5a74f9805` |
| [desktop-option-price.png](manual-shots/round-1/desktop-option-price.png) | 1280×1187 | `e868969d8f9a3ae0a39180d13b56f5ba9eef55570e9179c510d377bfdc5231f1` |
| [desktop-permission-denied.png](manual-shots/round-1/desktop-permission-denied.png) | 1280×1568 | `5863e78b9e3853d028260e2cdac481d17edef1daad3635216622cdf2ccf9d5c2` |
| [desktop-pin-lock.png](manual-shots/round-1/desktop-pin-lock.png) | 1280×1187 | `0572b6543461c572c2b2433652dd99ab71018e2239976be9b0e3f64203562241` |
| [desktop-promptpay-disabled.png](manual-shots/round-1/desktop-promptpay-disabled.png) | 1280×2064 | `54426d005601076fd4093d855dcf0f25ea85a9006e4d34ad1dd8e4739026b88f` |
| [desktop-promptpay-slip.png](manual-shots/round-1/desktop-promptpay-slip.png) | 1280×1992 | `be9c8df4e7a9c01a0a70b02cb8c4ed8ffd3b8e90e9a513202e0fcf1b899ed11a` |
| [desktop-promptpay-timeout-cash.png](manual-shots/round-1/desktop-promptpay-timeout-cash.png) | 1280×1992 | `2e7fb161f1937370c8dd2b71619c1eaba380f1693af0029d2109129247cdd9de` |
| [desktop-queue-order.png](manual-shots/round-1/desktop-queue-order.png) | 1280×1355 | `73a9331892f30b5a4ffd71962724d1f9ff805a03573c44b940aaf659fe74867d` |
| [desktop-reset.png](manual-shots/round-1/desktop-reset.png) | 1280×1568 | `073bc326c8bb97fb04e510265e2a772a17f32a8a285cdf85cffa3e21e1a61d39` |
| [desktop-restock.png](manual-shots/round-1/desktop-restock.png) | 1280×1187 | `6db52168a7e8db2ea17236678d1c11100dd223af2af80d49349677e1f980307f` |
| [desktop-roles.png](manual-shots/round-1/desktop-roles.png) | 1280×1568 | `5863e78b9e3853d028260e2cdac481d17edef1daad3635216622cdf2ccf9d5c2` |
| [desktop-status-sync.png](manual-shots/round-1/desktop-status-sync.png) | 1280×1698 | `429ba4f8101d5c7d2a7feb5ad5aafd1ce995b3be84f0b7ecd41d884ac72ddf2a` |
| [desktop-stock-option.png](manual-shots/round-1/desktop-stock-option.png) | 1280×1187 | `5428bf63a11608c1fc8e35926a0a08233db5f8e20ef58302f401c2e1cc1d62c0` |
| [desktop-stock-whole.png](manual-shots/round-1/desktop-stock-whole.png) | 1280×1187 | `cfb5561e6ae56813e587c69960cfd5124799916d62cc0e1ce96fd0883ed27992` |
| [desktop-table-menu.png](manual-shots/round-1/desktop-table-menu.png) | 1280×1698 | `ab0044c6f302fea45fcb0c8673f1c4343fadbc06f2c4e628f35d0d6e0668eeab` |
| [desktop-takeaway-slot.png](manual-shots/round-1/desktop-takeaway-slot.png) | 1280×1992 | `bb163eaf7fda6270ab87707910a50d3235919aa29ce612fa484c5bf6137b13b7` |
| [desktop-viewport-cart.png](manual-shots/round-1/desktop-viewport-cart.png) | 1280×900 | `d17eb6dcde5bb64fd0e040a7897f16bd6e87e2a69fcf72ad6c2dfd6dfa60f324` |
| [desktop-viewport-top.png](manual-shots/round-1/desktop-viewport-top.png) | 1280×900 | `f19e1f0b94564e8c50f9547c60e52be9331a74389381dc0adb90071d3aece4f3` |
| [extra-day-identifiers.png](manual-shots/round-1/extra-day-identifiers.png) | 1280×2386 | `fc762c2b3781b2a5aa8e74830f9d2e2da7ea9164cfe00de9cce48b3f8e9141ee` |
| [extra-delete-mapping.png](manual-shots/round-1/extra-delete-mapping.png) | 1280×1878 | `6a49aa69204af1f9f3d6da95d64c1c50ce447e5a713b851bbb163d762d73845f` |
| [extra-front-two-channels.png](manual-shots/round-1/extra-front-two-channels.png) | 1280×2212 | `73cfd45bd52996c1f7702459035c608d98b3fd8b4d26868a6dde133870283350` |
| [extra-image-options-failure.png](manual-shots/round-1/extra-image-options-failure.png) | 1280×1694 | `d78e33bf70df03a99ac534b234301a698226fa5ef7222fd5ce30c29f61ad2c3c` |
| [extra-image-rejected.png](manual-shots/round-1/extra-image-rejected.png) | 1136×799 | `e256ac266ee70c770c93c890b2f1240f940b6fda2c7b79063ed9719408fe706c` |
| [extra-midnight.png](manual-shots/round-1/extra-midnight.png) | 1280×2386 | `44ae0aebeedfc84eb01428f26b3293ac47be7e6c296160b152d9abe45c22e55c` |
| [extra-permissions-six.png](manual-shots/round-1/extra-permissions-six.png) | 1280×900 | `ec76fec8bed1d0996ed80bfbb9bbcab0819a4b4233a4ee42b3459eb13abaff9e` |
| [extra-pin-locked.png](manual-shots/round-1/extra-pin-locked.png) | 1280×1010 | `c79b861228d9d998924b94772d0ffca4ed168f31e5710b39f76ebe97f726dd80` |
| [extra-promptpay-pending.png](manual-shots/round-1/extra-promptpay-pending.png) | 1136×1649 | `2472ebc6fb34aae410cc1fbc4cf9a6be96aac27098d8075b1a29ad460cdcd35e` |
| [extra-retry-image-options-customer.png](manual-shots/round-1/extra-retry-image-options-customer.png) | 1280×2397 | `8895d1b3df927a49b1b32daedecbf5157ea30b6f805dc07c4d6ec04b535a858f` |
| [extra-retry-image-rejected.png](manual-shots/round-1/extra-retry-image-rejected.png) | 1136×799 | `43f4c53ce2b5adcb57b9ed3aee9b250c8debf384f05fefedf17d6224992a2bb4` |
| [extra-retry-options-limit.png](manual-shots/round-1/extra-retry-options-limit.png) | 1136×1634 | `8a141ab854cdda8c7ac7fbbe3898bd00d6ef6556c240afb4d48d00ec73c6a6ce` |
| [extra-session-history.png](manual-shots/round-1/extra-session-history.png) | 1280×2592 | `718325df9fc1c74d7a1c8096f2a7809fd0495084bba112cc07938ae7895e92be` |
| [extra-slip-after-fallback.png](manual-shots/round-1/extra-slip-after-fallback.png) | 1280×1992 | `3e9eb93e09162b8d525533cf9e0bbdd32720b358db461265774140bc4e1e9217` |
| [extra-slot-reselected.png](manual-shots/round-1/extra-slot-reselected.png) | 1136×1386 | `8d75e097b68040adef1998be4c5250cd7519cd73008ad3093a3b87b8b9410268` |
| [extra-snapshot-five.png](manual-shots/round-1/extra-snapshot-five.png) | 1280×3075 | `3e4b0119fbc838749eb8f9574875d8b5b0317890b95eb01aeca929e41060576c` |
| [extra-stock-overlap.png](manual-shots/round-1/extra-stock-overlap.png) | 1280×1969 | `84b633ccba8930f6d5ddd9dfd4ba8ec4129381d9f66aba5d26dacdf6ae5116ef` |
| [mobile-account-create.png](manual-shots/round-1/mobile-account-create.png) | 390×862 | `2fcae294cce29acfdb8dd77491b37c3ed0700440cff6f6431c8aaa0a71a281e4` |
| [mobile-close-table.png](manual-shots/round-1/mobile-close-table.png) | 390×2552 | `f5af788900c7a7fee9c44f65553e3a4bc228844e8e27ce43ffe5eb77edc3131f` |
| [mobile-ingredient-mapping.png](manual-shots/round-1/mobile-ingredient-mapping.png) | 390×2976 | `03af85a8dd2fb6707e7c8f8db78d3def22ef44616f0c2b2f753003152f3b2790` |
| [mobile-menu-management.png](manual-shots/round-1/mobile-menu-management.png) | 390×3028 | `53afa9bf664790b9b9cb9b5a29547b85429f1eae4634e9388d440a7e57cb6058` |
| [mobile-option-price.png](manual-shots/round-1/mobile-option-price.png) | 390×1712 | `e5cdba46bdf3a95c432dce6dfcee6df4bdefdb9692d63e0d400013d90a1e86a1` |
| [mobile-permission-denied.png](manual-shots/round-1/mobile-permission-denied.png) | 390×2069 | `e02d6a9b4e3a82f33313e848f2f1e00fe47abb40c55654bd630cf0065b4eae60` |
| [mobile-pin-lock.png](manual-shots/round-1/mobile-pin-lock.png) | 390×1578 | `9d1ccd0c23e6a5178eaa67f93ce901c38061b6882b9eee8321ebac97bf29f766` |
| [mobile-promptpay-disabled.png](manual-shots/round-1/mobile-promptpay-disabled.png) | 390×3188 | `5c1d3619900c153647d4118a3390f96915171427abd6500fe9a8cb12c7c9c147` |
| [mobile-promptpay-slip.png](manual-shots/round-1/mobile-promptpay-slip.png) | 390×3115 | `a16569062654fc551855bd6add6ef7e1dc1e5f5f15079370d5d667c32e9b6fd7` |
| [mobile-promptpay-timeout-cash.png](manual-shots/round-1/mobile-promptpay-timeout-cash.png) | 390×3115 | `5b5175b6459e30250cfff6d9e3293a2b09071411f652c6240426162bc42ece3d` |
| [mobile-queue-order.png](manual-shots/round-1/mobile-queue-order.png) | 390×1936 | `3787261667f14fbe6ee56b4915c935982c64fc350a6130010b8405e3c39f7a70` |
| [mobile-reset.png](manual-shots/round-1/mobile-reset.png) | 390×2069 | `6d3b7217a681e52e0c9d45915b4b1f32701b6d89e820722273a63c364aec3007` |
| [mobile-restock.png](manual-shots/round-1/mobile-restock.png) | 390×1712 | `ca192d8bc93d18602c60c65c5ba8bd65e8c37760358f92aa70d79e1deac2d86f` |
| [mobile-roles.png](manual-shots/round-1/mobile-roles.png) | 390×2069 | `e02d6a9b4e3a82f33313e848f2f1e00fe47abb40c55654bd630cf0065b4eae60` |
| [mobile-status-sync.png](manual-shots/round-1/mobile-status-sync.png) | 390×1941 | `5eac24db4223816ca103d10a03ef5f2f935746933af25154c6b474005d266e66` |
| [mobile-stock-option.png](manual-shots/round-1/mobile-stock-option.png) | 390×1578 | `54c76b7f7f88817da3975506e0fbbe2dbbba1c29dce455b1be8c0e41f5377d92` |
| [mobile-stock-whole.png](manual-shots/round-1/mobile-stock-whole.png) | 390×1578 | `4e6eb7b026be4258b29b1cd262a5dc5a66006d761812b8434cca921dc4f2dae3` |
| [mobile-table-menu.png](manual-shots/round-1/mobile-table-menu.png) | 390×1941 | `0ec3da5c76e4bd9ccdb88714da998a84857113620f8d9f16a2d156284b23f4e9` |
| [mobile-takeaway-slot.png](manual-shots/round-1/mobile-takeaway-slot.png) | 390×3117 | `92b464871d006ae64cf33537eccc2ae9b0933467b234b653071088480bfd0841` |
| [mobile-viewport-cart.png](manual-shots/round-1/mobile-viewport-cart.png) | 390×844 | `40c2b501c961d76833b5ab427fe6d8bc265a30e614292b7a93a239456635c6d8` |
| [mobile-viewport-top.png](manual-shots/round-1/mobile-viewport-top.png) | 390×844 | `a8a5c68a513c6f13175b625eb3de12f28faf16d22112bcbdad4af578b84ecae0` |

