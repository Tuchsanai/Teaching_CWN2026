# ผลตรวจ UAT — ระบบจอง “ออกแบบบริการด้วย AI”

> **SIMULATION** — ตรวจด้วย CLI เดียวในขั้นนี้ ข้อมูลผู้เรียนทั้งหมดเป็นรหัสจำลอง `<LEARNER_A>`–`<LEARNER_D>`
>
> วันที่ตรวจ: 2026-09-07 (UTC)  
> ขอบเขต: browser เดียว, ไม่มี backend หรือ production  
> เป้าหมาย browser: `http://172.17.0.3:8080/` (`HTTP 200`, `text/html`)  
> เครื่องมือ browser: Playwright 1.63.0 + Chromium, viewport ปกติและ 375 × 812 px  
> ข้อกำหนดการแก้ไข: ไม่ได้แก้ `index.html` และไม่ได้อ่าน/ค้นหา README ของ LAB

## สรุป

| กลุ่ม | PASS | FAIL | SKIP | สรุป |
|---|---:|---:|---:|---|
| ตรวจเอกสาร B01–B09 | 9 | 0 | 0 | `requirements.md` และ `index.html` ครบ B01–B09 |
| ทดสอบ browser UAT-01–09 | 9 | 0 | 0 | ผ่านทุกเคสจากผลที่สังเกตจริง |
| Console/page errors | 1 | 0 | 0 | `console.error` = 0, `pageerror` = 0, failed request = 0 |

## A. ผลตรวจเอกสาร

| ID | ทำจริง | Expected | Actual | ผล | หลักฐาน |
|---|---|---|---|---|---|
| DOC-B01 | อ่านข้อกำหนดและตรวจชื่อ/จำนวนที่นั่ง/สถานะเริ่มต้นใน HTML | ชื่อ “ออกแบบบริการด้วย AI”, 3 ที่, เริ่ม 0 รายการ/เหลือ 3 | ระบุครบ และ HTML กำหนด `WORKSHOP_NAME`, `TOTAL_SEATS = 3`, state เริ่มว่าง | **PASS** | `requirements.md` §4 B01 และ UAT-01; `index.html` มีหัวเรื่อง ตัวเลข 3/0/3 และ state `{ bookings: [] }` |
| DOC-B02 | ตรวจรหัสที่อนุญาตและช่องข้อมูล | รับเฉพาะ `<LEARNER_A>`–`<LEARNER_D>`; ไม่มีชื่อจริง อีเมล โทรศัพท์ | เอกสารระบุรหัสจำลอง 4 ค่า; HTML มี input รหัสเพียงช่องเดียวและ `ALLOWED_CODES` ตรงทั้ง 4 ค่า | **PASS** | `requirements.md` §4 B02; `index.html` ตัวแปร `ALLOWED_CODES` และ `#learner-code` |
| DOC-B03 | ตรวจ validation และการเปลี่ยนจำนวน | ว่าง/space/ซ้ำไม่รับ; สำเร็จแล้วรายการ +1 ที่เหลือ −1 ทันที | เอกสารมีเกณฑ์ครบ; HTML normalize/trim, ตรวจซ้ำ และ render ทันทีหลังเพิ่ม | **PASS** | `requirements.md` §4 B03 และ UAT-01–03; ฟังก์ชัน `normalizeCode`, `indexOfCode`, `book`, `render` |
| DOC-B04 | ตรวจเงื่อนไขเต็ม 3 ที่ | ครบ 3 ไม่รับ D และเหลือ 0 | เอกสารกำหนดรายการคง 3/เหลือ 0 พร้อมข้อความไทย; HTML ปฏิเสธเมื่อ `left <= 0` | **PASS** | `requirements.md` §4 B04 และ UAT-04–05; ข้อความ “ที่นั่งเต็มแล้ว คงเหลือ 0 ที่นั่ง” |
| DOC-B05 | ตรวจ flow ยกเลิก B แล้วรับ D | ยกเลิกแล้วคืนที่ทันที และรับ D ได้ | เอกสารระบุ A/B/C → A/C → A/C/D; HTML splice, save และ render ก่อนรับรายการใหม่ | **PASS** | `requirements.md` §4 B05 และ UAT-06; ฟังก์ชัน `cancel` และ `book` |
| DOC-B06 | ตรวจ persistence | refresh แล้วยังมีข้อมูลเดิม | เอกสารกำหนด `localStorage`; HTML save/load ด้วยคีย์ `aiDesignWorkshop.bookings.v1` | **PASS** | `requirements.md` §3–4 B06 และ UAT-07; ฟังก์ชัน `save`, `load` |
| DOC-B07 | ตรวจ “เริ่มใหม่” | ล้างเป็น 0 รายการ/เหลือ 3 และ refresh แล้วยังคงว่าง | เอกสารมีขั้นตอนและตัวเลขครบ; HTML ล้าง state และ remove app key | **PASS** | `requirements.md` §4 B07 และ UAT-07; ฟังก์ชัน `resetAll` |
| DOC-B08 | ตรวจ responsive และ accessibility | 375px ไม่ล้น; keyboard เข้าถึง; focus ชัด | เอกสารมีค่า `scrollWidth − clientWidth = 0` และลำดับ keyboard; HTML ใช้ native input/button และ outline 3px | **PASS** | `requirements.md` §4 B08 และ UAT-08–09; CSS `:focus`/`:focus-visible` |
| DOC-B09 | ตรวจข้อความสถานะไทย | ผลจอง/ปฏิเสธ/ยกเลิกสื่อด้วยข้อความไทย ไม่ใช้สีอย่างเดียว | เอกสารระบุครบ; HTML ใส่ข้อความสถานะไทยทุกเหตุการณ์พร้อม `role=status` | **PASS** | `requirements.md` §4 B09; ฟังก์ชัน `setStatus`, `book`, `cancel` |

## B. ผลทดสอบ browser จริง

ทุกเคสรันใน browser context เดียวตามลำดับ UAT-01 → UAT-09 โดยล้าง `localStorage` เฉพาะตอนตั้งต้น และใช้ปุ่ม “เริ่มใหม่” ตามขั้นตอนที่กำหนด

| ID | ทำจริง | Expected | Actual | ผล | หลักฐาน |
|---|---|---|---|---|---|
| UAT-01 | ล้าง `localStorage`, reload, คลิกจองเมื่อว่าง แล้วกรอก space 3 ตัวและคลิกอีกครั้ง | ทั้งสองครั้งไม่รับ; 0 รายการ; เหลือ 3; แจ้งไทย | ทั้ง empty และ spaces ได้ `booked=0`, `left=3`, codes ว่าง; ข้อความ “ยังไม่ได้กรอกรหัสผู้เรียน…” | **PASS** | ชื่อจริงบนหน้า = “ออกแบบบริการด้วย AI”; total=3; ตัวเลขคง 0/3 ทั้งสองครั้ง |
| UAT-02 | กรอก A แล้วคลิกจอง | A 1 รายการ; เหลือ 2; สำเร็จทันที | `codes=[A]`, `booked=1`, `left=2`; ข้อความไทยขึ้นต้น “สำเร็จ” | **PASS** | อ่าน DOM หลังคลิกโดยไม่ reload ได้ 1/2 |
| UAT-03 | กรอก A ซ้ำแล้วคลิกจอง | ไม่เพิ่มซ้ำ; 1 รายการ; เหลือ 2 | `codes=[A]`, `booked=1`, `left=2`; ข้อความ “จองไว้แล้ว” | **PASS** | นับ `.row-code` ได้ A เพียงแถวเดียว |
| UAT-04 | จาก A จอง B แล้ว C และอ่านค่าหลังแต่ละคลิก | หลัง B = A/B, 2 รายการ, เหลือ 1; หลัง C = A/B/C, 3 รายการ, เหลือ 0 | หลัง B ได้ `[A,B]`, 2/1; หลัง C ได้ `[A,B,C]`, 3/0 | **PASS** | **ยืนยัน A/B/C ครบ 3 รายการและเหลือ 0**; ทั้งสองครั้งมีข้อความไทยสำเร็จ |
| UAT-05 | ที่สถานะเต็ม กรอก D และคลิกจอง | ปฏิเสธ D; คง A/B/C, 3 รายการ, เหลือ 0; แจ้งเต็มและเลข 0 | ได้ `[A,B,C]`, `booked=3`, `left=0`; ข้อความ “ที่นั่งเต็มแล้ว คงเหลือ 0 ที่นั่ง…ไม่สามารถรับ D” | **PASS** | **ยืนยัน D ถูกปฏิเสธ** และไม่มีแถว D |
| UAT-06 | คลิกยกเลิก B แล้วกรอก D และคลิกจอง | หลังยกเลิก = A/C, 2 รายการ, เหลือ 1; หลังจอง = A/C/D, 3 รายการ, เหลือ 0 | หลังยกเลิก `[A,C]`, 2/1; หลังรับ D `[A,C,D]`, 3/0 | **PASS** | **ยืนยันผลสุดท้าย A/C/D**; มีข้อความไทยยกเลิกและจองสำเร็จ |
| UAT-07 | reload ที่ A/C/D; ตรวจ app key; คลิก “เริ่มใหม่”; reload อีกครั้ง | refresh แรกยัง A/C/D, 3/0; หลังเริ่มใหม่และ refresh เป็น 0/3 | refresh แรก `[A,C,D]`, 3/0; app key มี JSON ของ A/C/D; หลัง reset = 0/3; reload ซ้ำ = 0/3; app key เป็น `null` | **PASS** | **ยืนยัน refresh แล้วยัง A/C/D** และ “เริ่มใหม่” ล้างถาวรใน browser นี้ |
| UAT-08 | ใช้ Tab ไป input/book/cancel/reset; ใช้ Enter จอง A และ Space ยกเลิก | เข้าถึงทุก control; focus ชัด; Enter ทำ 0/3 → 1/2; Space ทำ 1/2 → 0/3 | focus ตามลำดับ `learner-code` → `book-btn` → `cancel:A` → `reset-btn`; ทุกจุด outline solid 3px; Enter ได้ 1/2; Space ได้ 0/3 | **PASS** | computed outline ทุกจุด = `rgb(11, 78, 162) solid 3px` |
| UAT-09 | ตั้ง viewport 375×812; มี A 1 รายการ; วัด width/ตรวจ control; สังเกตข้อความจอง/ปฏิเสธ/ยกเลิก | `scrollWidth ≤ clientWidth`; ไม่มี control ถูกตัด; ทั้งสามเหตุการณ์มีข้อความไทย | `scrollWidth=375`, `clientWidth=375`, difference=0; clipped controls=[]; final `[A]`, 1/2; ทั้ง 3 ข้อความมีอักษรไทยและยาวกว่า 0 | **PASS** | **ยืนยัน `scrollWidth ≤ clientWidth` เป็น `375 ≤ 375` ที่ 375px** |

> หมายเหตุรหัสในตาราง browser: A/B/C/D หมายถึง `<LEARNER_A>`/`<LEARNER_B>`/`<LEARNER_C>`/`<LEARNER_D>` ตามลำดับ

## C. Console และ page errors

| รายการที่ดักระหว่าง UAT-01–09 | Actual | ผล | หลักฐาน |
|---|---:|---|---|
| `console.error` | 0 | **PASS** | listener ของ Playwright ไม่ได้รับ error message |
| `pageerror` | 0 | **PASS** | listener ของ Playwright ไม่ได้รับ uncaught page exception |
| `requestfailed` | 0 | **PASS** | listener ของ Playwright ไม่ได้รับ failed request |

## ข้อสรุปส่งกลับ

- เอกสาร `requirements.md` และ implementation ใน `index.html` ครบ B01–B09 จากการตรวจเนื้อหา
- Browser UAT ผ่าน **9/9**, ไม่มี FAIL หรือ SKIP
- ไม่พบ console/page errors ระหว่างการรัน
- ไม่ได้แก้ `index.html`
