# Structure v2 — modules / data / screens / permissions

TASK_ID: revise-flow; RUN_ID: flow-v2-run; PLAN: plan-v2; UTC: 2026-09-14T13:21:31.591323Z
STATUS: **EXECUTED — รอ Evaluator verify-flow; ไม่ใช่ PASS**. F-01: แก้ในเอกสารแล้ว รอ Evaluator ตรวจปิด.
Plan JSON SHA-256: `8682dcba597fd36cadcf0a4724a9a75bd866f551b337281c663ee419c059c828`

Path จากราก LAB 005: S=`reference/session`; B=`reference/step-00-input/baseline-filtered-v2`; R=`reference/step-03-reveal-1/reveal-1.md`.
Authority คือ [FR/NFR v2](fr-nfr-v2.md) ตาม hash นี้; verify-fr ใน `S/evaluations/fr-v2-check.md` PASS เอกสารและอนุญาต revise-flow. PLAN_READY จาก `S/evaluations/plan-v2-review.md` ใช้เฉพาะเอกสาร/offline mock. ไม่แก้ snapshot.

| Source | SHA-256 | ขอบเขตหลักฐาน |
|---|---|---|
| S/fr-nfr-v2.md | 2cbdde11bb3fd5e62f338a1ea74f65d11112f3ea56e8a10ed9d24b08a1dcf0bb | authority; verify-fr PASS เอกสาร |
| B/flow.md | d0a5fcd029f4f315a02fcd2c057a44907bdf7362fbce17b8664a75b82773595d | ใช้ผลอ้างอิง; reuse เฉพาะส่วนที่ระบุ |
| B/state-machine.md | b4bc79de9e95f1526ca05326211a6025981b0420f3681b574e37189319f35adf | ใช้ผลอ้างอิง; ไม่รับรอง mapping เดิม |
| B/structure.md | fc8facf9088ad320d8dc3a7157edc14b337c1cb7081c3b098bcf91ceab08c560 | ใช้ผลอ้างอิง; โครงสร้างเสนอ |
| B/ui-contract.md | 294b660d2e39b3745344f225400eee57c02c25b6efb108a3a7ecce7cdd060e68 | fixture/selector เดิม; runtime ยังไม่ตรวจ |

ขอบเขต 21 US: US-01–US-16, US-19–US-21, US-25–US-26. FR/US/AC/NFR เต็มทุกคำใช้ S/fr-nfr-v2.md ตาราง US/AC, FR, NFR และ Traceability; ไม่คัดตารางประวัติซ้ำ. ข้อความที่อ้างเกณฑ์เป็นข้อกำหนดสำหรับตรวจภายหลัง ไม่ใช่ผลทดสอบ. ไม่กู้ช่องเพื่อ US-12 ที่ปิดไว้.

เมื่ออ่านร่วม baseline ให้ใช้ FR v2 เป็น authority ตามด้วยส่วนแก้ v2 นี้ แล้วจึงใช้ส่วนเดิมที่ระบุ reuse. หัว scope/สถานะผ่าน/ข้อห้ามเปิดข้อมูลในเอกสารเก่าเป็นประวัติ ไม่ใช้แทน scope v2; ข้อเสนอที่ยังไม่ยืนยันคงเป็นข้อเสนอ. ลิงก์ node/JSON/ต้นทางนอกสำเนาไม่ถูกเปิดหรืออ้างว่าอ่านแล้ว.

## ขอบเขตใช้ซ้ำและรุ่นของชื่อ

ใช้ entity/key/relation เดิมที่ B/structure.md:30–57 และ B/flow.md:413–438, permission เดิม B/structure.md:84–121 และข้อค้าง:145–202 ตาม hash. ชื่อ entity/key/cardinality และสิทธิ์ Unknown ยังคงเป็นแบบเสนอ; ไม่มีการสร้างฐานข้อมูลจริง. ใช้ MRG ID จาก B/flow.md เป็นชื่อกลางแทนชื่อ node ใน B/structure.md; mapping ประวัติอยู่ B/flow.md:98–217 ไม่คัดซ้ำ.

ตาราง modules/screens ด้านล่างเป็นทะเบียนปัจจุบันแทน B/flow.md:397–459 และ B/structure.md:13–81; เก็บ ID เดิม เพิ่ม MOD-12/SCR-17 เฉพาะ FR-21 และขยายส่วน US-09/14/F-01. Coverage 21 US เต็มใช้ [flow-v2.md](flow-v2.md) ตาราง Coverage; ไม่ใช้ coverage 18 แถวเก่าเป็นผล v2. [state-machine-v2.md](state-machine-v2.md) ใช้ event/data/ปลายทางเดียวกัน.

## Mapping ส่วนแก้ที่ตรงกันทั้งสามเอกสาร

| US / FR / NFR | Flow / event-transition | Module | Screen / direction | Data / state |
|---|---|---|---|---|
| US-11 / FR-11 / NFR-07 | MRG-05; O-02/O-03 | MOD-04 → MOD-06 | SCR-06 → SCR-08; SCR-04 รับผลตาม FR-05 | Order.order_state / OrderEvent; แยก PaymentSummary.payment_state |
| US-09 / FR-09 / NFR-V2-09 | MRG-31/32/33; I-V2-01/02/03 | MOD-04, MOD-02, MOD-07, MOD-06 | SCR-06 → SCR-04; เลือกผ่าน SCR-03/04; ยอด SCR-05/08/09 | OrderItem, ItemDecision, OrderAdjustment, snapshot เดิม/ยอดปรับ |
| US-14 / FR-14 / NFR-V2-14 | MRG-31/32/33; I-V2-01/02/03 | MOD-04, MOD-02 | SCR-06 ↔ SCR-04; เปลี่ยนผ่าน SCR-03 | item_state รอลูกค้าตัดสินใจ; ไม่ใช่ order/payment/table state |
| US-21 / FR-21 | MRG-34/35; C-V2-01/02/03 | MOD-12, MOD-02 | SCR-17 → SCR-03 | CapacitySetting, CapacityWindow; confirmed_order_count/N; X จำลอง |

ชื่อ MOD-12/SCR-17 และ ItemDecision/OrderAdjustment/CapacitySetting/CapacityWindow รวม I-V2/C-V2 เป็นชื่อออกแบบใหม่ในชุดเอกสารนี้ ไม่ใช่ข้อกำหนดร้านเพิ่ม. การเลือก MOD-06/SCR-08 เป็นปลายทาง F-01 เป็นข้อเสนอการจัดวางที่รองรับผู้รับตาม FR-11. UI v2 ยังไม่ได้ผลิต; ตารางนี้เป็น mapping ของเอกสารจริง ไม่ใช่ผลคลิก.

## Modules ปัจจุบัน

| ID | หน้าที่ | Flow | FR | US |
|---|---|---|---|---|
| MOD-01 | เข้าระบบสั่งผ่าน QR และแยกโต๊ะ/รอบโต๊ะ | MRG-01, MRG-12, MRG-15, MRG-16, MRG-17 | FR-01, FR-02, FR-16 | US-01, US-02, US-16 |
| MOD-02 | เลือกอาหาร/ตัวเลือก/ช่วงรับ/ยืนยัน และเมนูแทน; แสดงข้อความความจุก่อนยืนยัน | MRG-02, MRG-03, MRG-04, MRG-08, MRG-09, MRG-32, MRG-35 | FR-02, FR-03, FR-04, FR-06, FR-07, FR-08, FR-09, FR-10, FR-13, FR-14, FR-15, FR-19, FR-21 | US-02, US-03, US-04, US-06, US-07, US-08, US-09, US-10, US-13, US-14, US-15, US-19, US-21 |
| MOD-03 | คำนวณและแสดง ETA ก่อนยืนยัน | MRG-03, MRG-04 | FR-07 | US-07 |
| MOD-04 | คิวครัว สถานะอาหาร ส่งเหตุการณ์ และรายการรอลูกค้าตัดสินใจ | MRG-04, MRG-05, MRG-31, MRG-32, MRG-33 | FR-03, FR-04, FR-05, FR-09, FR-10, FR-11, FR-14, FR-15 | US-03, US-04, US-05, US-09, US-10, US-11, US-14, US-15 |
| MOD-05 | วัตถุดิบหมด/กลับมามีและผลปิดเมนู/ตัวเลือก | MRG-08, MRG-09, MRG-18, MRG-19, MRG-20 | FR-06, FR-12, FR-13 | US-06, US-12, US-13 |
| MOD-06 | จอหน้าร้าน แยกโต๊ะ/เลขรับ; รับสถานะอาหาร US-11/FR-11/MRG-05 ที่ SCR-08 แยกสถานะเงิน; อ่านยอดปรับ | MRG-04, MRG-05, MRG-13, MRG-14, MRG-32, MRG-33 | FR-02, FR-03, FR-08, FR-09, FR-10, FR-11, FR-15, FR-16 | US-02, US-03, US-08, US-09, US-10, US-11, US-15, US-16 |
| MOD-07 | สรุปยอดเดิม/ยอดปรับ วิธีชำระ fallback และยืนยันพร้อม log; ไม่คืนเงินจริง | MRG-06, MRG-07, MRG-10, MRG-11, MRG-32, MRG-33 | FR-08, FR-09, FR-15, FR-19, FR-26 | US-08, US-09, US-15, US-19, US-26 |
| MOD-08 | จัดการเมนู ราคา รูป และตัวเลือก | MRG-21, MRG-22, MRG-23, MRG-24 | FR-19, FR-20 | US-19, US-20 |
| MOD-09 | แมปวัตถุดิบกับเมนู/ตัวเลือกที่มีแล้ว | MRG-23, MRG-25 | FR-19, FR-20 | US-19, US-20 |
| MOD-10 | บัญชี PIN และการตรวจสิทธิ์ URL | MRG-26, MRG-27, MRG-28 | FR-25 | US-25 |
| MOD-11 | ติดตั้งและจัดเก็บ/บริการภายในร้าน | MRG-29, MRG-30 | FR-26 | US-26 |
| MOD-12 | ตั้งช่วงเร่งด่วน/N และอ่านจำนวนออเดอร์ยืนยันต่อหน้าต่าง 00/15/30/45 เพื่อข้อความก่อนยืนยัน | MRG-34, MRG-35 | FR-21 | US-21 |

## Screens ปัจจุบัน

| ID | บทบาท | Actions | Flow | Data / state | FR |
|---|---|---|---|---|---|
| SCR-01 | ลูกค้า | สแกน QR เปิดเมนู เลือกเมนู; แสดงหมดและปิดปุ่มตามผลวัตถุดิบ | MRG-01, MRG-08, MRG-09, MRG-12 | DiningTable/TableSession, Menu/MenuOption, AvailabilityEffect; กรณี URL ผิดและหน้าเดิมรอ Q-02/Q-16 | FR-01, FR-02, FR-06, FR-12, FR-13, FR-16 |
| SCR-02 | ลูกค้า | เลือกสั่งกลับบ้านและช่วงรับ | MRG-02 | PickupSelection; นิยามเวลาสั่งและช่วงแรก Q-03; ไม่เพิ่มสวิตช์ปิดรับกลับบ้าน | FR-03 |
| SCR-03 | ลูกค้า | เลือกตัวเลือก/ตรวจยอด/ETA/ข้อความความจุก่อนยืนยัน และเลือกเมนูแทนของรายการรอ | MRG-03, MRG-04, MRG-32, MRG-35 | OrderItem snapshot, ItemDecision, OrderAdjustment (เสนอ); CapacityWindow; X จำลองแยก ETA | FR-02, FR-03, FR-04, FR-07, FR-08, FR-09, FR-10, FR-14, FR-15, FR-19, FR-21 |
| SCR-04 | ลูกค้าที่โต๊ะ | ดูสถานะอาหารไม่รีเฟรช; แจ้งรายการทำไม่ได้พร้อมสองปุ่มเปลี่ยนเมนู/คืนรายการ | MRG-05, MRG-31, MRG-32, MRG-33 | Order.order_state แยก OrderItem.item_state; ItemDecision อ้างรายการ; ไม่ใช่ payment state | FR-04, FR-05, FR-09, FR-11, FR-14 |
| SCR-05 | ลูกค้า | ดูรายการเดิม/คืน/แทนและยอดเดิม/ยอดปรับ; เลือกวิธีจ่าย/fallback เดิม | MRG-06, MRG-07, MRG-10, MRG-11, MRG-32, MRG-33 | PaymentSummary, OrderAdjustment; payment_state เดิม; ข้อค้างเงินจริงแสดงชัด | FR-08, FR-09, FR-15, FR-19 |
| SCR-06 | พนักงานครัว | คิวและ 1 แตะเปลี่ยนสถานะออเดอร์; กดทำไม่ได้ที่รายการ/เห็นรอลูกค้าตัดสินใจ; อัปเดตหรือลบตามลูกค้า | MRG-04, MRG-05, MRG-31, MRG-32, MRG-33 | Order.order_state + OrderEvent; OrderItem.item_state + ItemDecision; timestamp/monotonic เดิม | FR-03, FR-04, FR-05, FR-09, FR-10, FR-11, FR-14, FR-15 |
| SCR-07 | พนักงานครัว | กดวัตถุดิบหมด/กลับมามี ดูผลเมนูและตัวเลือก | MRG-08, MRG-18, MRG-19, MRG-20 | Ingredient, WholeDishMap/OptionIngredientMap, AvailabilityEffect; อ่านแมปเพื่อทำงานไม่ได้แปลว่ามีสิทธิ์เปิดหน้าแมป/แก้แมป; กฎซ้อน Q-12/Q-13 | FR-06, FR-12, FR-13 |
| SCR-08 | พนักงานหน้าร้าน | หน้าร้านดูโต๊ะ/เลขรับและสถานะอาหารใหม่ US-11/FR-11/MRG-05; อ่านสถานะเงินแยกช่องกับยอดปรับ | MRG-04, MRG-05, MRG-13, MRG-14, MRG-32, MRG-33 | Order.order_state + OrderEvent จาก SCR-06/MOD-04 ผ่าน MOD-06; PaymentSummary.payment_state แยก; OrderAdjustment/TakeoutIdentifier/TableSession | FR-02, FR-03, FR-08, FR-09, FR-10, FR-11, FR-15, FR-16 |
| SCR-09 | พนักงานหน้าร้าน | หน้าร้านตรวจยอดเดิม/ปรับ รับเงินสด/ยืนยันสลิปและ log ตามเดิม | MRG-06, MRG-07, MRG-10, MRG-11, MRG-32, MRG-33 | PaymentSummary/OrderAdjustment; PaymentConfirmationEvent ชื่อผู้ใช้/เวลา; ไม่มีปุ่มคืนเงินจริง | FR-08, FR-09, FR-15, FR-19 |
| SCR-10 | พนักงานหน้าร้าน | เปิดโต๊ะ ปิดโต๊ะ; แจ้งรอบเดิมสั่งต่อไม่ได้ตามรูปแบบที่ยังรอยืนยัน | MRG-15, MRG-16, MRG-17 | DiningTable/TableSession; ค้างทำ/ค้างจ่ายและหน้าเดิมรอ Q-16; ไม่ทำรวมบิลหลายรอบ | FR-16 |
| SCR-11 | ผู้จัดการร้าน | เพิ่ม/แก้/ลบเมนู ราคา รูป และตัวเลือก; เตือนเมื่อเมนูมีแมปก่อนลบตาม FR | MRG-21, MRG-22, MRG-23, MRG-24 | Menu/MenuOption; ยอด Order เดิมคงเดิม; รูปแบบคำเตือน/เลือกไฟล์ใหม่เป็น A-MUX; ไม่มีงานแมป | FR-19, FR-20 |
| SCR-12 | ผู้จัดการร้าน | เลือกเมนู/ตัวเลือกที่สร้างแล้ว ระบุวัตถุดิบทั้งจาน/เฉพาะตัวเลือก บันทึกแมป | MRG-25 | Ingredient/WholeDishMap/OptionIngredientMap; ไม่เพิ่ม/แก้เมนู/ราคา; ข้อเสนอเชื่อมปิด/เปิดยัง DI-04/A-03; ทะเบียนวัตถุดิบ Q-20 | FR-19, FR-20 |
| SCR-13 | พนักงานครัว / พนักงานหน้าร้าน / ผู้จัดการร้าน | เข้าสู่ระบบด้วยชื่อผู้ใช้+PIN; แสดงผลล็อก | MRG-26, MRG-27 | StaffAccount/LoginLockContext; บัญชีแรก/ชุดอักขระ/ขอบเขตล็อกรอ Q-25 | FR-25 |
| SCR-14 | ผู้จัดการร้าน | สร้างบัญชีและกำหนดบทบาท; รายละเอียดแก้/ลบ/รีเซ็ตยังไม่ออกแบบ | MRG-26 | StaffAccount/StaffRole; แยกจากหน้าล็อกอิน; การกำหนดจำนวน role ต่อบัญชีเป็นข้อเสนอ | FR-25 |
| SCR-15 | พนักงานครัว / พนักงานหน้าร้าน | แสดงผลปฏิเสธเมื่อเปิด URL รายงานหรือจัดการเมนูโดยตรง | MRG-28 | ผลตรวจ AccessRule; ข้อความและ URL จริงยัง Q-25; เป็นผลปฏิเสธ ไม่มีตารางรายงาน/ยอดขาย/CSV | FR-25 |
| SCR-16 | ผู้จัดการร้าน | ข้อเสนอพื้นที่ตั้ง PromptPay ปิดใช้งาน; ตำแหน่งและการจัดวางยังไม่ยืนยัน A-ST05 | MRG-10, MRG-11 | PaymentAvailabilitySetting; ไม่ซ่อนทางเลือกเอง และไม่สร้างหน้าตั้งค่าทั้งระบบ; รอ Q-08 | FR-08 |
| SCR-17 | ผู้จัดการร้าน | ผู้จัดการตั้งเวลาเริ่ม–สิ้นสุดและ N ต่อ 15 นาที | MRG-34 | CapacitySetting/CapacityWindow; ไม่ตั้งสูตร X หรือช่วง ETA | FR-21 |

US-26 ไม่มีหน้าจอติดตั้งใน mock; MOD-11 กับ MRG-29/30 คงข้อกำหนดติดตั้ง/ออฟไลน์เดิมโดยยังไม่ทดสอบ. ทุกการจัดวางเป็นข้อเสนอหน้าจอ ไม่อนุมัติสิทธิ์ที่ Unknown. SCR-17 ไม่รวมหน้าตั้งค่าธุรกิจอื่น.

## ข้อมูลเดิมที่ใช้ซ้ำและส่วนขยาย v2

| Entity / ความสัมพันธ์ | Fields หรือผลที่ต้องรักษา | ที่มา / state / ข้อค้าง |
|---|---|---|
| DiningTable → TableSession → Order | table_id จาก QR; session_id แยกรอบ; order_id แยกเลขครัวกับเลขรับ | B/structure.md:36–38; FR-02/16; ปิดแล้วเริ่ม session ใหม่ไม่ปนรายการเดิม |
| Order → OrderItem → SelectedOption | คง order_total_at_order; menu_name_at_order/base_price_at_order/quantity/item_total_at_order; option_name_at_order/extra_price_at_order | B/structure.md:38–40; snapshot เดิมจาก FR-04/19; จำนวน/สูตรเงินยังเสนอ |
| Order / OrderEvent | order_state; server_received_at ระดับวินาที, kitchen_sequence monotonic; client_confirmed_at แยก kitchen_changed_at | B/structure.md:38,52; O-02/O-03 → MOD-06/SCR-08; data สถานะอาหารที่แก้ F-01 |
| OrderItem (ขยาย) → ItemDecision (ใหม่เสนอ) | item_state; decision_id/order_item_ref; unable_at/customer_decided_at; choice=change/return; replacement_ref และ snapshot_ref เดิม | FR-09/14; รอลูกค้าตัดสินใจเป็น state FR; key/ป้ายผล/การเก็บ revision เป็นข้อเสนอ; เก็บของเดิมแม้จอครัวลบ |
| Order → OrderAdjustment (ใหม่เสนอ) | adjustment_id, decision_ref, original_total, before_total, returned_item_refs, replacement_item_refs, adjusted_total, revision | FR-09/08/15/19; ยอดก่อน/หลังชุดเดียวกันส่ง SCR-05/08/09; สูตรส่วนต่าง/ปัดเศษ/คืนซ้ำยัง Q-V2-REFUND |
| PaymentSummary → PaymentEvent → PaymentConfirmationEvent | แยก total_at_order เดิมจากยอดปรับที่อ่านจาก OrderAdjustment; payment_state เดิม; username_at_event/confirmed_at/confirmation_action เดิม | B/structure.md:49–51; FR-08/15; ไม่เขียนทับยอด ณ สั่งหรือ event ยืนยันเดิม; ไม่มี refund-completed state |
| Menu/MenuOption ↔ Ingredient ผ่าน WholeDishMap/OptionIngredientMap/AvailabilityEffect | current_price/current_extra_price แยก snapshot; ทั้งจาน/เฉพาะตัวเลือก; ชุดปิด/เปิดคืน | B/structure.md:41–46; FR-06/12/13/19/20; ปิด catalog ไม่เปลี่ยน item เอง; US-20/Q-20 คงเดิม |
| PickupSelection / TakeoutIdentifier | ช่วงรับและ order_time_reference; T-001 ต่อเนื่อง/รีเซ็ต 00:00 แยก kitchen_sequence | B/structure.md:47–48; FR-03/15; เขตเวลา/จุดเริ่มยังรอยืนยัน; ไม่ใช้แทน CapacityWindow |
| CapacitySetting (ใหม่เสนอ) → CapacityWindow (ใหม่เสนอ) | setting_id/start_time/end_time/N; window_start/window_end/confirmed_order_refs/confirmed_order_count; proposed confirmation observation | FR-21; 15 นาทีเริ่ม 00/15/30/45; C-V2-01/02/03; key/UTC/[start,end)/เปลี่ยน N/นับคืนยังเสนอ |
| Capacity presentation → SCR-03 | X_mock=10 และ is_mock_label เป็นข้อมูลแสดง fixture; ข้อความ “ครัวเต็ม รอประมาณ X นาที” | X ไม่ใช่สูตรที่อนุมัติ ไม่ใช่ ETAObservation; จำนวนถึง N ไม่สร้าง permission-denied/blocked order |
| ETAObservation | queued_not_ready_count, average_order_latest_7_days, longest_menu_average, estimated_wait; จุดวัด log เดิม | B/structure.md:53; FR-07/NFR-04; ไม่มีข้อมูลพอให้บอกยังประมาณไม่ได้ ไม่สร้างค่าจาก X |
| StaffAccount/StaffRole/AccessRule/LoginLockContext/PaymentAvailabilitySetting | username/PIN/role/lock/fallback ตามต้นทาง; ไม่มีชื่อบัญชีจริงหรือข้อมูลธนาคาร | B/structure.md:54–57; FR-25/08; Unknown permissions/วิธีจัดเก็บยังรอยืนยัน |

ข้อมูล amount/payment/order/item/session/capacity และ AI task เป็นคนละระดับ: ไม่มีฟิลด์เดียวใช้สลับความหมาย. รายการคืน/แทนไม่เขียนทับ original_total หรือ snapshot เดิม; adjusted_total เป็นมุมมองล่าสุดจาก decision เดียวกัน. เก็บ PaymentConfirmationEvent เดิมแม้ adjusted_total ลดและเคยจ่ายแล้ว. ไม่เพิ่มระบบบัญชีคืนเงินจริงหรือเนื้อหารายงาน.

## Permission / บทบาทของส่วนแก้

| บทบาท | Resource / action | Flow / module / screen | ขอบเขตสิทธิ์ |
|---|---|---|---|
| ครัว | เปลี่ยนสถานะอาหาร 1 แตะ; ทำไม่ได้ที่รายการในคิว | MRG-05/31; MOD-04; SCR-06 | ตาม FR-11/14; ไม่ได้สิทธิ์คืนเงินจริง |
| ลูกค้า | เห็นแจ้งเตือน เลือกเปลี่ยนเมนูหรือคืนรายการของตน | MRG-31/32/33; MOD-02/04; SCR-03/04 | ตาม FR-09; วิธีพิสูจน์ ownership/session จริงยังไม่ทดสอบ; ไม่มีสิทธิ์ยืนยันสลิป |
| หน้าร้าน | อ่านสถานะอาหาร/ยอดปรับแยกสถานะเงิน; รับเงินสด/ยืนยันสลิปและ log | MRG-05/32/33/06/07/10/11; MOD-06/07; SCR-08/09 | ตาม FR-11/08/15; ไม่อนุมัติคืนเงินจริงหรือกำหนดส่วนต่างแทนเจ้าของ |
| ผู้จัดการ | ตั้งช่วงเร่งด่วนและ N | MRG-34; MOD-12; SCR-17 | ตาม FR-21; ไม่เพิ่มสิทธิ์ตั้งสูตร X หรือกฎปฏิเสธเต็ม |
| ครัว/หน้าร้าน | URL จัดการเมนูและรายงาน | MRG-28; MOD-10; SCR-15 | คงปฏิเสธตาม FR-25; รายงานเป็น placeholder เท่านั้น |
| บทบาทอื่น / สิทธิ์นอกที่ FR ระบุ | เช่นอนุมัติคืนเงิน แก้ค่า X หรือสิทธิ์ข้ามบทบาทเพิ่มเติม | Unknown ตาม baseline และ Q-25 | ยังไม่ยืนยัน; การมีแท็บรวมพนักงานไม่รวมสิทธิ์ครัวกับหน้าร้าน |

ใช้ permission matrix เดิมตาม path/hash สำหรับ actions ที่ไม่เปลี่ยน; ไม่อนุมานว่า manager ทำได้ทุก action. ข้ออนุญาต front/manager ใน ui-contract เดิมเป็น fixture ไม่ใช่การรับรองสิทธิ์ธุรกิจจริง. ชื่อบัญชีจำลองของ mock หากต้องใช้เสนอ kitchenDemo/frontDemo/managerDemo เท่านั้น ไม่เก็บ PIN จริง.

## Mapping ไป UI contract และรายการที่ต้องตรวจใหม่

| US / screen | สิ่งที่มีใน B/ui-contract.md (fixture) | ส่งต่อ UI v2 / ผลตรวจ |
|---|---|---|
| US-01/02/03/04/06/13; SCR-01/02/03/07 | menu-list, menu-item-<id>, option-<id>, item-total, cart-total, btn-submit-order, order-mode, pickup-slot, ingredient-select/btn-out-of-stock/btn-restock | reuse selectors เดิม; ตรวจ stock/cart/options/ช่วงรับ/session หลังเพิ่มรายการแทน; ไม่อ้าง DOM เดิมผ่านใหม่ |
| US-05/10/11/14; SCR-04/06/08 | customer-order-status, kitchen-queue, kitchen-order[data-order-id], btn-status-next, front-orders/front-order[data-order-id] | F-01 ต้องตรวจสถานะอาหารใหม่ใน front-order ใบเดียวกัน; front-payment-status เป็นคนละข้อมูล. US-09/14 ยังไม่มี selector ใหม่ที่สร้างจริง |
| US-08/09/15/19; SCR-05/08/09 | pay-cash/pay-promptpay, payment-status, cash-message, front-total, front-payment-status, btn-confirm-slip/btn-receive-cash, payment-log | เพิ่มแสดง original/adjusted totals และรายการคืน/แทน; front-total ต้องอ้างยอดที่ตกลงแสดงล่าสุดอย่างชัดเจนพร้อมเก็บ snapshot เดิมแยก; ไม่แก้สัญญาเดิมในงานนี้ |
| US-16; SCR-10 | front-table-select, btn-close-table | reuse; ตรวจรอบใหม่ไม่ปนและรายการค้างการตัดสินใจตามข้อค้าง ไม่ให้คืนรายการปิดโต๊ะเอง |
| US-19/20/25; SCR-11/12/13/14/15/16 | admin-*, mapping-*, account-*, toggle-promptpay; URL auth ตาม contract | reuse โดยไม่แต่งสิทธิ์; snapshot เก่าต้องคง; รูป/ตัวเลือก/แมป/ล็อก/ตรง URL ต้อง runtime recheck |
| US-21; SCR-17/03 | sim-clock เป็นเวลา fixture เดิม; ยังไม่มี selector ตั้งช่วง/N/ข้อความใหม่ | revise-ui ต้องกำหนด selectors ใน ui-contract-v2 คู่ HTML จริง; แสดงข้อความก่อนยืนยันและป้าย X จำลอง |
| ทุกหน้าจอ | 3 แท็บ ลูกค้า / ครัวและหน้าร้าน / ผู้จัดการ; btn-reset; login แยก kitchen/front | screen ID เป็นส่วนงานเชิงตรรกะ ไม่เพิ่มแท็บเอง; reset/role/selector scoping/viewport/network off ต้องตรวจใน verify-ui |

รายการ selector ข้างต้นอ้างสัญญาเดิมเท่านั้น; ไม่ได้อ่าน HTML มารับรองว่ามี runtime. ชื่อ field ใหม่เป็นข้อเสนอเอกสาร ยังไม่มี ui-contract-v2 หรือ UI v2 ใน outputs งานนี้. เกณฑ์ AC เต็มรักษาใน FR v2 และส่วนเกณฑ์ flow-v2; UI ต้องรักษาตัวเลข/หน่วย/สัดส่วนเดิมและติดป้าย fixture เมื่อยังไม่มีคำตอบ.

## ข้อค้างและขอบเขตที่ยังไม่พิสูจน์

คง Q เดิมทั้ง 18 รหัสตาม S/fr-nfr-v2.md:170–189 และ Q-V2-REFUND/STATE/CAPACITY:216–218; ไม่คัดประวัติสมมติฐานทุกตารางซ้ำ. MC-01–MC-03, A-05/DI-07 (สถานะ), DI-04/A-03 (US-20), หมายเหตุ ก./ค./ช. ยัง OPEN. การเปิด FR-14 ไม่แก้ข้อความ US-20 ที่อ้าง US-14 และไม่ยืนยันว่าหมายถึงกฎเดียวกัน.

- สถานะ: initial/terminal/ข้ามขั้น/ย้อน/กดซ้ำ, เสร็จแล้วกับพร้อมเสิร์ฟ และการรวมสถานะ item → order/ETA/table ยังรอยืนยัน. คืนทุกรายการก็ไม่ประกาศยกเลิกออเดอร์ จ่ายแล้ว หรือปิดโต๊ะเอง.
- เงิน: วิธีคิดส่วนต่างเปลี่ยนเมนู ยอดคืน/ตัวเลือก/จำนวน/ปัดเศษ ผู้อนุมัติ วิธีคืนเงินจริง การคืนซ้ำ/คำสั่งชนกันและวันรายงานยังไม่มีคำตอบ. ไม่ให้สิทธิ์คืนเงินจริงเพิ่ม. หมายเหตุ ก. จุดเริ่ม 10 นาทีและสองวิธีจ่ายขณะ PromptPay ปิดยังคงข้อค้าง.
- ความจุ: สูตร X/ความสัมพันธ์กับ ETA, เขตเวลาและขอบหน้าต่าง, คืน/เปลี่ยน/เปลี่ยน N ระหว่างช่วง, ผลเมื่อเต็มนอกจากข้อความ ยังรอ Q-V2-CAPACITY. ไม่เพิ่มกฎห้ามยืนยันเมื่อเต็ม. ช่วงตัวอย่าง 11:30–13:30 ไม่เปลี่ยนช่วงวัด ETA 11:30–13:00 และ 17:30–19:30.
- เดิม: QR ผิด/เวลาเริ่มสั่ง/ตัวเลือก/เลขออเดอร์ข้ามวัน/วัตถุดิบซ้อน/แมประหว่างปิด/ปิดโต๊ะค้างทำหรือค้างจ่าย/นิยาม 2 MB/Unknown permissions/สภาพติดตั้ง ยังตาม Q เดิม. ไม่เติมกฎเหล่านี้จากเว็บ.

NOT_TESTED: Evaluator verify-flow v2, UI v2/DOM/data-testid/click/responsive, ระบบจริง LAN/Wi-Fi/หลายอุปกรณ์/โหลด/concurrency/สัดส่วน AC, ETA/ข้อมูล 7 วัน/ความแม่นยำ, สูตร X, auth/security/server log, Ubuntu/สคริปต์ติดตั้ง/ถอดอินเทอร์เน็ต และการชำระเงินจริง. ใช้เฉพาะข้อมูลและบัญชีจำลองหากนำแบบไปทำ mock; รอบนี้ไม่รัน mock หรือระบบจริง.

ส่งต่อไฟล์ทั้งสามและ execution report ให้ Evaluator `verify-flow` ตรวจผูก hash ปัจจุบันและ F-01 ก่อนบันทึก `S/evaluations/flow-v2-check.md`. จากนั้น draft-test-outline/verify-test-outline และ revise-ui/verify-ui จึงทำตาม dependency ของแผนได้. ไม่มีการเรียก Evaluator/agent เพิ่มหรือรับรองตนเองในรอบนี้. ถ้าคำตอบธุรกิจทำให้ scope/dependency เปลี่ยน ให้ Planner สร้างแผนรุ่นถัดไป ไม่แก้ plan-v2.
