# รายงานการสร้างและทดสอบ LAB 006

วันที่ทดสอบ: 7 กันยายน 2026 (UTC)  
ผลรวม: **PASS** — พรอมท์ตรง README 4/4, browser UAT ผ่าน 9/9, จุดตรวจ B02-X ผ่าน, container และพื้นที่ชั่วคราวถูกลบแล้ว

## 1. สิ่งที่เปลี่ยนจาก README เดิม

- เลิกพรอมท์ก้อนเดียวที่ให้ AI ทำหลายบทบาทต่อเนื่อง แยกเป็น 4 ขั้นและหยุดทุกขั้น
- ใช้ลำดับหน้าต่าง A `yolo1` → B `qyolo1` → C `cyolo1` → B หรือ A
- คงกรณีศึกษา กฎ B01–B09, UAT-01–09, ตัวเลข 3 ที่นั่ง และรหัสอ้างอิงเดิม
- เพิ่ม 6 ส่วนในทุกขั้น: เป้าหมาย, ข้อมูลตั้งต้น, พรอมท์, Expected Output, จุดตรวจ และวิธีแก้เมื่อผลไม่ตรง
- เพิ่มทางลัดไปยังไฟล์พรอมท์, template บันทึก UAT ทีละข้อ และภาพผังใต้หัวเรื่อง
- ใช้ภาษาไทยประโยคสั้น ไม่มีคำสั่ง shell ให้ผู้เรียนพิมพ์ README มีขนาด 20,465 ไบต์ หรือประมาณ 19.99 KiB

## 2. ผล live test ด้วย AI จริงบน host

ใช้ข้อความจากไฟล์พรอมท์ตรงตามตัวอักษร บัญชี Claude ใช้ `yolo3` ตามสเปกข้อ 9.6 แม้ README สำหรับผู้เรียนยังระบุ `yolo1` รายละเอียดเวลา รุ่น effort และ exit code อยู่ใน [run-metadata.json](live/run-metadata.json)

| ขั้น | wrapper / รุ่น | Expected Output | ผลจริงและหลักฐาน |
|---|---|---|---|
| 1 | `yolo3` / Claude Opus 5 / medium | `requirements.md` มี B01–B09 และ UAT-01–09 แล้วแสดงเนื้อหาและหยุด | รอบแรกจับคู่ UAT-01/03 ผิด จึงล็อกรหัสในพรอมท์ รอบ 2 ตรงและหยุดหลังขั้นเดียว: [รอบแรก](live/step-01-yolo3-attempt-1.md), [รอบสุดท้าย](live/step-01-yolo3.md) |
| 2 | `qyolo1` / qwen3.8-max / high | `index.html`, `preview.md`, URL; server ทำงานเบื้องหลัง; ไม่สร้าง UAT | รอบ 1 TIMEOUT เพราะ server อยู่ foreground; รอบ 2 ทำเกินขอบเขต; รอบ 3 ตรงสาระ แสดงเนื้อหาและหยุด: [TIMEOUT](live/step-02-qyolo1-attempt-1.md), [รอบ 2](live/step-02-qyolo1-attempt-2.md), [รอบสุดท้าย](live/step-02-qyolo1.md) |
| 3 | `cyolo1` / gpt-5.6-sol / medium | ตรวจเอกสารและรัน Playwright ถ้ามี สร้าง `uat-results.md` โดยไม่แก้เว็บ | รอบแรก UAT หลัก 9/9 แต่ตรวจเอกสารพบ B02-X จึง FAIL; หลังส่งกลับผู้สร้าง รอบสุดท้าย B01–B09 และ UAT 9/9 PASS ไม่แก้เว็บและหยุด: [ก่อนแก้](live/step-03-cyolo1-attempt-1.md), [หลังแก้](live/step-03-cyolo1.md) |
| 4 | `yolo3` / Claude Opus 5 / medium | ถ้าแทน template แล้วให้บันทึกผลจริง; ถ้ายังไม่แทนให้ SKIP | รัน template ตรงไฟล์โดยยังมี placeholder จึงบันทึก SKIP ไม่เดาผล ไม่แก้เว็บ และหยุด: [ผลขั้น 4](live/step-04-yolo3.md) |

รูปแบบคำสั่งที่ใช้ตรงตามโจทย์: Claude ส่งด้วย `-p` และบันทึก stdout/stderr, Qwen ส่งด้วย `-p`, Codex ใช้ `exec --skip-git-repo-check -m gpt-5.6-sol` และ effort medium ทุกขั้นมีเพดาน 15 นาที

การเทียบ Expected Output:

- ขั้น 1 ตรงหลังแก้พรอมท์ 1 รอบ
- ขั้น 2 ตรงหลังแก้พรอมท์ 2 รอบ ซึ่งไม่เกินเพดาน
- ขั้น 3 ตรงหลังแก้เว็บด้วย feedback 1 รอบจากเพดาน 2 รอบ
- ขั้น 4 ตรงเงื่อนไข SKIP เพราะยังไม่ได้แทน placeholder

## 3. การแก้ defect และผลก่อน/หลัง

ผู้ตรวจ `cyolo1` พบว่าเว็บรับ `<LEARNER_X>` ทั้งที่ B02 อนุญาตเฉพาะ A–D จึงตัดสิน FAIL โดยไม่แก้เว็บ จากนั้นส่ง feedback ที่กรอกแล้วให้ `qyolo1` เก็บผลก่อนแก้ แก้เฉพาะ validation และทดสอบซ้ำ ผล B02-X เปลี่ยนจาก FAIL เป็น PASS ใช้ 1 รอบ หลักฐานอยู่ใน [step-04-feedback-qyolo1.md](live/step-04-feedback-qyolo1.md) และสคริปต์ที่ AI สร้างอยู่ใน [uat-b02x-retest.py](live/uat-b02x-retest.py)

ไม่ได้ลดเกณฑ์ B01–B09 และไม่ได้เปลี่ยนกฎธุรกิจ หลังแก้ hash ของ `index.html` บน host และใน container ตรงกันที่ `7c69727156a903c89edc23dfe55d01612583253edb0b8ecc47e1a41c14988b03`

## 4. ผลทดสอบ browser

ใช้ Chromium ที่เปิดร่วมผ่าน `pw-up` CDP `127.0.0.1:9222` เข้า URL ของ container โดยตรง

| รายการ | ผล |
|---|---|
| UAT-01–09 | PASS 9, FAIL 0 |
| B02-X เพิ่มเติม | PASS 1, FAIL 0 |
| console / page / request errors | 0 |
| desktop | [desktop-1440.png](desktop-1440.png) |
| mobile | [mobile-375.png](mobile-375.png), overflow 0 px |
| ผลแบบเครื่องอ่าน | [uat-auto.json](uat-auto.json) |
| สคริปต์ทดสอบ | [run-uat.js](run-uat.js) |

ระหว่างสร้างหลักฐานซ้ำ ตัวตรวจเคยจับข้อความ UAT-03 เฉพาะคำติดกันว่า “จองแล้ว” แต่หน้าเว็บใช้ “จองไว้แล้ว” สถานะ 1/2 และรายการไม่ซ้ำถูกต้อง จึงแก้เฉพาะ pattern ของตัวตรวจเป็นข้อความที่ความหมายเดียวกันแล้วรันใหม่ ไม่ได้แก้เว็บหรือผ่อนเกณฑ์

## 5. Container และการตรวจทางลัด

| รายการ | ผล |
|---|---|
| ชื่อ / image | `devtools-lab006-38ddc3` / `tuchsanai/devtools:2569_1` |
| สิทธิ์ / ports | privileged; `2286:22`, `8086:8080` |
| IP และ URL ที่ browser ใช้ | `172.17.0.3`; `http://172.17.0.3:8080/` ตอบ 200 |
| วิธีเข้า container | ใช้ `docker exec -i` เพราะ host ไม่มี `sshpass`; ไม่เขียนรหัสผ่านในเอกสารผู้เรียน |
| คัดลอก LAB | `/root/workspace/sa-labs/006_LAB_Prototype_and_UAT/` |
| ตรวจทางลัด | `README.md` และ `prompts/step-01.md` ถึง `step-04.md` มีจริงทุก path; hash พรอมท์ host/container ตรงทุกไฟล์ |
| cleanup | ลบ exact name/ID แล้ว; `docker ps -a --filter name=devtools-lab006` เหลือ 0 |

รายละเอียดเครื่องอ่านอยู่ใน [container-checks.json](container-checks.json) ก่อนสร้างพบ container LAB 001 และไม่ได้แตะต้อง ภายหลัง container นั้นหายไปจาก final listing โดยไม่ใช่คำสั่งของกระบวนการนี้

## 6. ความตรงของพรอมท์และความปลอดภัย

[check-prompts.py](check-prompts.py) ดึงกรอบพรอมท์ทั้ง 4 จาก README แล้วเทียบ byte ต่อ byte กับไฟล์ `prompts/step-01.md` ถึง `step-04.md` ผล **MATCH 4/4** ดู [prompt-diff.txt](prompt-diff.txt) ทุกไฟล์ขึ้นต้นด้วย path มาตรฐาน จบด้วยคำสั่งแสดงเนื้อหา หยุดรอ และไม่ทำขั้นถัดไป

ตรวจ transcript และงานที่เก็บใน evidence ด้วยรูปแบบอีเมล คีย์ลับ และข้อมูลรับรองตามโจทย์ พบอีเมลที่ AI เติมใน `requirements.md` 1 จุดและปกปิดเป็น `<REDACTED>` แล้ว ตรวจซ้ำไม่พบค่าจริง งานจาก host ถูกเก็บครบใน [live/work](live/work/) แล้วลบ `/root/workspace/sa-work/006/` และยืนยันว่าไม่มี process ฟังพอร์ต 8080 บน host

## 7. รายการ SKIP และเหตุการณ์หลักฐานเดิม

- การคลิก UAT-01–09 โดยผู้เรียนมนุษย์: **SKIP** เพราะรอบ build นี้ไม่มีผู้เรียนกรอก template; ไม่อ้างผลอัตโนมัติแทนผลคน
- ขั้น 4 ที่ส่ง template ตรงไฟล์: **SKIP ตามกฎ** เพราะ `<UAT_ID>` และช่องอื่นยังไม่ถูกแทน
- API key, login และการติดตั้ง browser ใหม่: **SKIP** เพราะไม่จำเป็นและไม่ร้องขอข้อมูลเจ้าของบัญชี
- Playwright: **ไม่ SKIP** เพราะมีอยู่และรันจริง

ไฟล์หลักฐานเดิมถูกย้ายเข้า `previous/` ก่อนเริ่มตามสเปก แต่โฟลเดอร์ evidence ถูกลบจากภายนอกระหว่าง live test จึงกู้ได้เฉพาะ transcript จาก session ของ wrapper และสร้างหลักฐาน browser ใหม่ รายการที่สูญหายบันทึกอย่างตรงไปตรงมาใน [previous/README.md](previous/README.md)

autosave `.ipynb_checkpoints` เก่าที่ปรากฏใหม่ใต้ LAB ถูกย้ายแบบไม่แก้เนื้อหาไป `previous/lab-checkpoints/` เพื่อไม่ให้ปะปนกับไฟล์ฉบับส่ง

## 8. ตารางตรวจรับตามสเปกข้อ 8

| ข้อ | เกณฑ์ที่ตรวจ | ผล | หลักฐาน |
|---:|---|:---:|---|
| 8.1 | รักษาวัตถุประสงค์ กรณีศึกษา B01–B09, UAT-01–09 และรหัสเดิม | PASS | README และ `live/work/requirements.md` |
| 8.2 | README ใหม่มี 4 ขั้นและ 6 ส่วนทุกขั้น มีภาพใต้หัวเรื่อง ภาษาเหมาะกับ SA | PASS | ตรวจหัวข้อแต่ละชนิดได้ 4 ครั้ง; README 19.99 KiB; ไม่มีคำสั่ง shell ให้ผู้เรียน |
| 8.3 | มี prompt 4 ไฟล์ กรอบ README ตรงไฟล์ และ path ทางลัดใช้ได้ | PASS | `prompt-diff.txt` MATCH 4/4; ตรวจ path ใน container ทีละไฟล์ |
| 8.4 | ลำดับ wrapper ถูกต้อง ทำทีละขั้น แสดงเนื้อหาและหยุด | PASS | transcript ขั้น 1–4; Claude live ใช้ yolo3 ตามข้อ 9.6 |
| 8.5 | รันพรอมท์จริง เทียบ Expected และแก้ได้ไม่เกิน 2 รอบ | PASS | `run-metadata.json`; ขั้น 1 ใช้ 1 รอบแก้ ขั้น 2 ใช้ 2 รอบแก้ |
| 8.6 | Container ถูกชื่อ image ports และคัดลอก LAB/preview ครบ | PASS | `container-checks.json`; HTTP 200; hash ตรง |
| 8.7 | ทดสอบเว็บจริง UAT-01–09, desktop/mobile และ feedback loop | PASS | `uat-auto.json` 9/9, B02-X PASS, ภาพ 2 ขนาด, feedback 1 รอบ |
| 8.8 | รายงานแยก PASS/FAIL/SKIP มี evidence ตรวจข้อมูลลับ และ cleanup | PASS | รายงานนี้, transcript/work, scan หลังปกปิด, host work และ container เหลือ 0 |

**สรุปเกณฑ์ข้อ 8: PASS 8/8, FAIL 0/8**
