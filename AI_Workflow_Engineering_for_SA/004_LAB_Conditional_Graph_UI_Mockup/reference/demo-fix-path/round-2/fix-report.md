# รายงานแก้ชุดสาธิต

สถานะ: **รอตรวจซ้ำ**

ตัวนับ `round-2/current-round.txt` มีค่า 1 จึงเป็นการแก้ครั้งแรก โดย `round-1` เป็น baseline และ `round-2` เป็นผลหลังแก้ ไม่ใช่การแก้ครั้งที่สอง รอบก่อนมี `edge=fix` ผ่าน 17 ข้อและตก 2 ข้อ ตัวเลขนี้เป็นผลก่อนแก้เท่านั้น

ข้อบกพร่องถูกฉีดโดยผู้จัดทำเพื่อสาธิต edge=fix ไม่ใช่ผลของลูปหลัก ใช้ `../seed/ui-mockup-broken.html` เป็นทั้ง HTML ตั้งต้นและ snapshot ก่อนแก้ คงต้นฉบับและหลักฐานรอบก่อนไว้ ใช้ข้อมูลจำลองเดิมทั้งหมด

อ่านข้อกำหนดจาก `input/ui-contract.md`, `input/mock-data.json`, โครงสร้างและ flow ใน `reference/step-00-input/` และอ่านขั้นตอนใน `tests/ui-check.py` โดยไม่รันตัวตรวจ ใช้คำสั่งที่แทนรายการตกด้วย JSON จริงแล้วสำหรับการรันนี้ ไม่แก้ไฟล์แม่แบบ

## การจับคู่และจุดแก้

| Check ID | US | หน้าจอ | สาเหตุและหลักฐาน | จุดแก้ |
|---|---|---|---|---|
| option-price | US-04 | SCR-03 ลูกค้า: รายละเอียดจานและตัวเลือก (`customerHTML`) | detail ระบุคาดหวัง 60 แต่ `item-total` เป็น 50 บาท; ภาพ `../round-1/shots/option-price.png` แสดงติ๊กเพิ่มไข่ดาว +10 บาทแล้ว แต่ยอดยัง 50 บาท โค้ดแสดงเฉพาะ `m.price` แม้มีรายการ `selected` อยู่แล้ว | เปลี่ยนนิพจน์ยอดจานให้รวมราคาฐานกับราคาตัวเลือกทั้งหมดที่เลือก ใช้ `cents` และ `money` เดิมให้สอดคล้องกับ `addItem` และ `submitOrder` รองรับเลือก/ยกเลิกและราคาจากข้อมูล ไม่ใส่ยอด 60 ตายตัว |
| promptpay-slip | US-08, US-15 | SCR-09 หน้าร้าน: ยืนยันชำระเงิน (`frontHTML`); ผลเชื่อมไป SCR-05 ลูกค้า | detail ระบุปุ่ม `btn-confirm-slip` disabled จนคลิกหมดเวลา; ภาพ `../round-1/shots/promptpay-slip.png` แสดงยอด 60 บาท สถานะค้างจ่าย เลือก PromptPay แล้ว แต่ปุ่มยืนยันเป็นสีเทา โค้ดกำหนด disabled ตายตัว | เปลี่ยนเงื่อนไข disabled ให้ตรงกับ guard ใน `confirmPayment`: ปิดเมื่อจ่ายแล้วหรือยังไม่มีคำขอ PromptPay (`requested_at === null`) เมื่อเข้าเงื่อนไขจึงกดยืนยันผ่าน handler เดิมได้ |

## ขอบเขตและผลต่อ state ร่วม

สาเหตุทั้งสองอยู่ที่การแสดงผล จึงแก้เฉพาะสองนิพจน์ใน HTML ที่คัดลอกจาก seed ไม่แก้โครงสร้างหรือฟังก์ชันที่เขียน shared state

ยอดรายละเอียดอ่านรายการตัวเลือกที่เลือกอยู่ ส่วนตะกร้า ยอด snapshot ตอนส่ง ใบครัว และยอดหน้าร้านใช้การคำนวณเดิม การเปิดปุ่มสลิปทำให้เรียก `confirmPayment` เดิม ซึ่งตรวจสิทธิ์ front/manager แล้วเปลี่ยนสถานะเงินและเพิ่มเหตุการณ์ที่มีผู้ใช้จำลอง เวลา ISO และเลขออเดอร์ หน้าลูกค้าและหน้าร้านอ่านผลจาก state เดิม จึงต้องตรวจการซิงก์สถานะและบันทึกเหตุการณ์ซ้ำร่วมด้วย

คง data-testid, mock seed, หน้าตาและ CSS, สิทธิ์เข้าใช้, ตะกร้าและการส่งออเดอร์, กฎ stock, ยอดออเดอร์เก่า, timeout PromptPay, การรับเงินสด, คิว, รอบโต๊ะ และกฎธุรกิจอื่นทั้งหมด ไม่เพิ่ม guard ใหม่เรื่อง timeout หรือการปิด PromptPay ไม่แตะไฟล์ผู้เรียนหรือหลักฐานผลตรวจ

## Regression ที่รอตรวจ

ผู้จัดทำต้องรัน `tests/ui-check.py` ทั้งชุดกับ HTML หลังแก้ พร้อม `--prev` อ้างอิง `../round-1/ui-check.json` โดยไม่ข้ามข้อที่เคยผ่าน:

- สองข้อที่ตก: `option-price`, `promptpay-slip`
- 17 ข้อที่เคยผ่าน: `roles`, `table-menu`, `queue-order`, `status-sync`, `stock-whole`, `stock-option`, `restock`, `promptpay-disabled`, `promptpay-timeout-cash`, `takeaway-slot`, `close-table`, `menu-management`, `ingredient-mapping`, `pin-lock`, `permission-denied`, `account-create`, `reset`

จุดที่ต้องสังเกต: เลือก/ยกเลิกตัวเลือกแล้วราคาปรับตามข้อมูล ยอดตรงกับตะกร้าและใบหน้าร้าน ตัวเลือกยังไปใบครัว ยอด snapshot ไม่เปลี่ยนตามราคาเมนูใหม่; สลิปยังค้างจ่ายก่อนยืนยัน ผู้มีสิทธิ์ยืนยันแล้วทั้งสองหน้าจอเป็นจ่ายแล้วพร้อม log ปุ่มปิดเมื่อยังไม่เคยขอ PromptPay หรือจ่ายแล้ว; กรณีปิด PromptPay และเกิน 10 นาทียังมีทางรับเงินสดตามเดิม

## ข้อค้างและการตรวจใน session นี้

ตรวจความต่างของไฟล์แบบอ่านอย่างเดียวเพื่อยืนยันขอบเขตสองจุดและการคง seed ไม่ได้รันตัวตรวจ ไม่ได้เปิดเบราว์เซอร์ทดสอบ และไม่ได้สร้างหรือแก้ JSON ผลตรวจ ภาพ หรือ log ใหม่ จึงยังไม่ประกาศว่าข้อใดผ่านหลังแก้ สถานะทั้งหมดหลังแก้คือ **รอตรวจซ้ำ** โดยผู้จัดทำเป็นผู้รันทั้งชุดพร้อม `--prev` และตัดสินผล

## JSON รายการตกจริงจาก baseline

เก็บครบทั้ง `detail` และ `us` โดยคง `passed: false` ตามผลก่อนแก้:

```json
[
  {
    "id": "option-price",
    "us": [
      "US-04"
    ],
    "passed": false,
    "detail": "AssertionError: Locator expected to contain text '60'\nActual value: 50 บาท \nCall log:\n  - Expect \"to_contain_text\" with timeout 2500ms\n  - waiting for get_by_test_id(\"item-total\")\n    9 × locator resolved to <strong class=\"amount\" data-testid=\"item-total\">50 บาท</strong>\n      - unexpected value \"50 บาท\"\n\nAria snapshot:\n- strong: 50 บาท"
  },
  {
    "id": "promptpay-slip",
    "us": [
      "US-08",
      "US-15"
    ],
    "passed": false,
    "detail": "TimeoutError: Locator.click: Timeout 2500ms exceeded.\nCall log:\n  - waiting for get_by_test_id(\"front-orders\").locator(\"[data-order-id=\\\"1\\\"]\").get_by_test_id(\"btn-confirm-slip\")\n    - locator resolved to <button disabled data-id=\"1\" data-action=\"confirm-slip\" data-testid=\"btn-confirm-slip\">ยืนยันสลิปจำลอง</button>\n  - attempting click action\n    2 × waiting for element to be visible, enabled and stable\n      - element is not enabled\n    - retrying click action\n    - waiting 20ms\n    2 × waiting for element to be visible, enabled and stable\n      - element is not enabled\n    - retrying click action\n      - waiting 100ms\n    5 × waiting for element to be visible, enabled and stable\n      - element is not enabled\n    - retrying click action\n      - waiting 500ms\n"
  }
]
```
