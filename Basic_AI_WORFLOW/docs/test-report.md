# รายงานตรวจสไลด์ AI Workflow Engineering

## คำสั่งที่ใช้ build/test

รันจากรากโปรเจกต์ด้วย Python และ Chromium ของ Playwright; วัดเวลาด้วย Bash `time`

```sh
TIMEFORMAT='BUILD_SECONDS=%R'
time python3 src/build_deck.py --slides src/slides --root . --out AI_Workflow_Engineering.html
TIMEFORMAT='TEST_SECONDS=%R'
time python3 tests/test_slides.py --html AI_Workflow_Engineering.html --out tests/results.json --shots tests/screenshots
```

## เวลาตรวจและสภาพแวดล้อม

เวลาตรวจล่าสุด: **2026-09-16T17:04:44.925750+07:00** แปลงจาก `tests/results.json` → `checked_at` เป็นเวลาไทย +07:00
เปิด deck แบบ `file://` ที่ viewport **1600×900 px**; ตรวจความสูงสไลด์ตามเกณฑ์ **720 px**

เวลา build **25.179 วินาที** และ test **35.474 วินาที** เป็นค่ารอบล่าสุดที่วัดด้วย `time`; test ถ่าย screenshot ใหม่ครบทุกหน้า

## ผลตรวจ

Build, `tests/test_slides.py` เต็มชุด และ `tests/check_links.py` ได้ **exit 0**

| รายการ | ผล |
| --- | --- |
| slides | 107 |
| pages | 107 |
| ok | true |
| overflow | 0 |
| console_errors | 0 |
| copy_ok | true |
| iframes count / loaded | 12 / 12 |
| mermaid_svg | 75 |
| tabs_ok | true |

### จำนวนหน้าต่อบท

นับจาก `pages[].chapter` รวมหน้าสารบัญตามบทที่ระบุในผลตรวจ

| บท | จำนวนหน้า |
| --- | --- |
| 0 บทนำ | 17 |
| 1 Loop Engineering | 23 |
| 2 Graph Engineering | 25 |
| 3 Dynamic Workflow | 24 |
| 4 สรุปและเปรียบเทียบ | 18 |

### data-goto-title ที่ resolve

resolve สำเร็จ **15 รายการ** หลังสร้างสารบัญและกำหนดเลขหน้า ตรวจเทียบ `data-goto` กับ `pages[].index` ตามชื่อหน้า
ผลตรวจรอบก่อน: ทดสอบคลิกลิงก์จริงใน Chromium ครบ **15 รายการ** และตรวจทั้ง hash กับชื่อหน้าปลายทาง ผ่านทั้งหมด; รอบนี้ build และ link-check ตรวจชื่อกับเลขหน้าซ้ำ

| title | หน้า |
| --- | --- |
| ทดลองจริง — โจทย์ 1 จองห้องประชุม × Loop | 25 |
| ทดลองจริง — โจทย์ 1 จองห้องประชุม × Graph | 51 |
| ทดลองจริง — โจทย์ 1 จองห้องประชุม × Dynamic | 74 |
| ทดลองจริง — โจทย์ 2 เบิกค่าใช้จ่าย × Loop | 29 |
| ทดลองจริง — โจทย์ 2 เบิกค่าใช้จ่าย × Graph | 55 |
| ทดลองจริง — โจทย์ 2 เบิกค่าใช้จ่าย × Dynamic | 78 |
| ทดลองจริง — โจทย์ 3 ย้ายระบบนัดหมาย × Loop | 33 |
| ทดลองจริง — โจทย์ 3 ย้ายระบบนัดหมาย × Graph | 59 |
| ทดลองจริง — โจทย์ 3 ย้ายระบบนัดหมาย × Dynamic | 82 |
| โจทย์ 3 × Loop — Change Request (เฟส 2) | 37 |
| โจทย์ 3 × Graph — Change Request (เฟส 2): Node ไหนต้องรันซ้ำ | 63 |
| โจทย์ 3 × Dynamic — Change Request (เฟส 2): NEW INFORMATION → Plan v3 | 86 |
| Loop Prompt Template (ฉบับไทย) | 23 |
| Graph Prompt Template (ฉบับไทย) | 49 |
| Dynamic Workflow Prompt Template (ฉบับไทย) | 72 |

ผลตรวจ resolver จากรอบก่อน (ไม่ได้รัน sample ซ้ำในรอบแก้ข้อความนี้): ทดสอบบนสำเนา sample deck ชั่วคราวและลบสำเนาหลังตรวจ โดยคง sample ต้นฉบับ:
เขียนทับเลข fallback และเติมเลขเมื่อไม่มี `data-goto` ได้ (exit 0), ชื่อ `สารบัญ` อ้างถึงสารบัญอัตโนมัติได้,
ชื่อไม่พบหรือชื่อปลายทางซ้ำหลายหน้าให้ exit 4 พร้อมรายการใน stderr
ตรวจว่า asset ผิดพลาดยังให้ exit 2 และ URL ภายนอกยังให้ exit 3; เลขหน้าและส่วนท้ายยังครบ
ชื่อซ้ำที่ไม่มีลิงก์อ้างถึงไม่ทำให้การ build ล้มเหลว

## ขนาดไฟล์และหลักฐานภาพ

`AI_Workflow_Engineering.html` มีขนาด **18427760 bytes** หรือ **18.427760 MB** (หน่วยฐานสิบ)

ผลตรวจ: `tests/results.json`
ภาพครบทุกหน้า: `tests/screenshots/slide-NNN.png` โดย path ของแต่ละหน้าอยู่ใน `pages[].screenshot`
ภาพรวม: `tests/screenshots/overview.png`

รอบนี้เปิดดูภาพหน้า 27 (Iteration Log และข้อสังเกต “取消”) แล้ว
ข้อความไทย ส่วนท้าย และกล่องเนื้อหาปรากฏในพื้นที่สไลด์; เนื้อหายาวอ่านต่อด้วยการเลื่อนภายในกล่อง

## การตรวจ URL ภายนอก

parse DOM ด้วย BeautifulSoup แล้วตัด attribute `srcdoc` ออกจาก iframe ก่อนตรวจ `src`, `href`, `xlink:href`, `srcset`
ตรวจ HTTP(S) ที่ต้นค่า attribute และทุกตำแหน่งของ `srcset` รวมถึง URL แบบละ protocol ใน attribute ทั่วไป
ผล **0 รายการ** นอก `srcdoc`; build ยังตรวจ CSS URL และ import ตามพฤติกรรมเดิม

## ผล link-check

`tests/link-report.json`: `ok=true`, ตรวจ 22 ไฟล์ / 222 ลิงก์, broken 0 และ violations 0
มี warning 7 รายการ: ภาพ output ขนาดเกิน 1 MB จำนวน 6 ไฟล์ และข้อยกเว้นการตรวจหลักฐานดิบ 1 รายการ; ไม่บล็อกผลตรวจ

## ข้อจำกัดที่พบ

ไฟล์ใหญ่เพราะฝัง trace/output ดิบและภาพ SVG รวมไว้ใน HTML เพื่อเปิดอ่านแบบไฟล์เดียว
`response-phase2.md` ของ AI มี absolute path เป็นหลักฐานดิบ จึงแสดงตามต้นฉบับผ่าน directive โดยไม่แก้หลักฐาน

การตรวจ iframe ยืนยันว่า document โหลดครบและมีเนื้อหา ไม่ใช่การรับรองทุกฟังก์ชันของเว็บที่ฝัง
test runner ตรวจ Copy กล่องแรกที่พบและสลับแท็บคู่แรกในแต่ละชุด; ภาพหน้าจอเก็บสถานะเริ่มต้นของแต่ละหน้า
ผลไม่มี URL ภายนอกนี้ครอบคลุม DOM นอก `srcdoc` ตามเกณฑ์ ไม่ได้สแกน JavaScript ทุกเส้นทางการทำงาน

## รายการ fragment ที่แก้และ diff

แก้ข้อความบรรยายใน `src/slides/00-intro.html` 2 จุด และ `src/slides/10-loop.html` 1 จุด เป็น “ช่อง REQUIREMENT” โดยคง placeholder ในกล่อง Template
เติมข้อสังเกตคำจีน “取消” ในหน้า “โจทย์ 1 × Loop — Iteration Log” และหัวข้อเดียวกันใน `readme.md`
ชื่อและลำดับหน้าคงเดิมครบ 107 หน้า ไม่มีการแบ่งหน้าหรือแก้ไฟล์หลักฐานดิบ; ตรวจ SHA-256 ของ trace ก่อนและหลังแล้วตรงกัน
build ผ่านโดยไม่ต้องเปลี่ยน `data-md` เป็น `data-file` และไม่ต้องแก้ชื่อปลายทางในบทสรุป

## ข้อสังเกตจากหลักฐานดิบ

[trace ของโจทย์จองห้องประชุมแบบ Loop](../experiments/1_meeting_room/loop/trace.md) มีคำจีน “取消” หลุดจากผลของโมเดล สไลด์แสดง trace ผ่าน directive ตามต้นฉบับ จึงคงข้อความนี้ไว้โดยไม่แก้หลักฐานดิบ
