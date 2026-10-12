# IMAGES-REVIEW-06 — ตรวจภาพประกอบบท 06 (VI6)

ตรวจ 26/26 ไฟล์ใน `img/` เทียบพรอมต์ใน `q06.json` · ทุกไฟล์ 1280×853 และ ≤ 340 KB · log มี END ครบ S6_0–S6_25 (exit=0)

เกณฑ์ที่ใช้: (1) สะกดข้อความไทยตรงพรอมต์ทีละตัวอักษร (ซูม 2–8 เท่า) (2) ตัวละครถูกต้อง: เด็กผู้ชายผมน้ำตาลยุ่ง ฮู้ดสีน้ำเงิน · หุ่นยนต์ทรงกลมสีขาว จอหน้าสีดำ ตาฟ้า เสาอากาศลูกบอลฟ้า ไม่มีโลโก้ · คุณจันทร์ · น้องบัว · ฉากสปาไทย (3) ไม่มีเฉลยรั่ว (บั๊ก L1–L8 และ mutant ตาม CR-DESIGN §2, คำตอบใน EXAM-DRAFT) (4) ขนาดไฟล์

สรุป: **OK 23 · fixed-overlay 2 · regenerate 1**

| ไฟล์ | ผล | ปัญหา / หมายเหตุ | พรอมต์ใหม่ (ถ้าต้องสร้างใหม่) |
|---|---|---|---|
| intro-01-legacy-handover.jpg | fixed-overlay | กระดาษโน้ตเขียน "ผ่าาน" (มี า ซ้ำ) → แปะ "ผ่าน" ทับด้วยข้อความที่ Chromium เรนเดอร์ (Leelawadee UI Bold 18px บนพื้นเหลือง #ffe26c) · ข้อความอื่นถูกต้อง หุ่นยนต์ไม่มีโลโก้ | – |
| intro-02-change-desk.jpg | OK | ป้ายชื่อบนโต๊ะเขียน "คุณจันทร์" (ไม่มีในพรอมต์ แต่สะกดถูกตามบท 04) | – |
| concept-01-inherited-system.jpg | OK | การ์ด "จองคิว" ที่เพิ่มมาเองสะกดถูก | – |
| concept-02-cr-lifecycle.jpg | OK | ป้าย 6 สถานีถูกครบ | – |
| concept-03-four-eyes.jpg | OK | มีคุณจันทร์เพิ่มเข้ามาและป้ายอังกฤษ "Thai Spa" ซึ่งไม่เสียหายอะไร | – |
| concept-04-browser-only.jpg | OK | – | – |
| concept-05-outdated-docs.jpg | OK | – | – |
| concept-06-safety-net.jpg | OK | – | – |
| concept-07-lock-not-correct.jpg | fixed-overlay | ชื่อภาพเขียน "บั้ก" (ไม้โท) แทน "บั๊ก" (ไม้ตรี) → แปะ "ล็อกทั้งบั๊ก" ใหม่บนพื้นไม้ (สร้างพื้นจากคอลัมน์ไม้ที่ไม่มีตัวอักษร ตัวอักษรไล่สีทองพร้อมขอบน้ำตาล) · มีป้ายภาษาอังกฤษตกแต่งที่ไม่เสียหาย | – |
| concept-08-test-seam.jpg | OK | ตรวจแล้ว "นาฬิกา" ถูกต้อง: ฬ ในฟอนต์มนแบบไม่มีหัวดูคล้าย พ แต่เส้นขวาสูงเกินแนวบรรทัด · การ์ด "จองวันนี้/จองพรุ่งนี้/จองสัปดาห์หน้า" ที่เพิ่มมาเองสะกดถูก | – |
| concept-09-mutation.jpg | OK | – | – |
| concept-10-impact-ripple.jpg | OK | – | – |
| concept-11-red-first.jpg | OK | – | – |
| concept-12-intended-vs-unintended.jpg | OK | – | – |
| concept-13-live-db-migration.jpg | OK | – | – |
| concept-14-rollback.jpg | OK | – | – |
| concept-15-traceability.jpg | OK | – | – |
| concept-16-audit-signoff.jpg | OK | – | – |
| concept-17-reserved-ports.jpg | OK | มีคุณจันทร์เปิดประตู 4000 เพิ่มมา ไม่เสียหาย | – |
| concept-18-claude-md-fence.jpg | OK | มีป้ายตกแต่งเพิ่ม "พัก / คิด / ทำให้ดี / ไปด้วยกัน :)" สะกดถูก ไม่เกี่ยวกับเนื้อหา (จะลบภายหลังก็ได้) | – |
| concept-19-effective-date.jpg | OK | – | – |
| concept-20-double-tap.jpg | regenerate | "ลูกค้า" ที่กดจองสองครั้งถูกวาดเป็นเด็กผู้ชายคนเดิมซ้ำ 2 ตัว (มุมซ้ายบนกับซ้ายล่าง) จึงดูเหมือนตัวเอกเป็นคนจองซ้ำเอง ซึ่งขัดกับเรื่อง (คุณสมชาย 081-000-0003) · ข้อความไทยถูกทั้งหมด | Spa lobby scene. A middle-aged Thai man customer (short black hair, glasses, striped polo shirt, clearly NOT the boy) sits on a sofa holding a smartphone with a weak Wi-Fi icon and taps the green "จอง" button twice; two identical booking tickets labeled "จอง" fly out. The robot catches the second ticket with a big golden padlock labeled "ล็อกก่อนจอง" and a speech bubble "มีนัดแล้ว". The boy (only ONE boy in the picture) stands at the right holding a card "081-000-0003" and checks it. Title sign "คนเดียวกัน เวลาทับ = ซ้ำ". |
| concept-21-reschedule-self-overlap.jpg | OK | คุณจันทร์ปรากฏ 2 ที่ (บนการ์ดนักบำบัด "คนเดิม" และยืนข้าง ๆ) ไม่เสียหาย | – |
| concept-22-independent-oracle.jpg | OK | มีป้ายตกแต่ง 3 ป้ายที่เพิ่มมาเอง ("ความรู้ ช่วยให้ งานง่ายขึ้น", "งานดี ชีวิตดี สมดุล", "คิด วิเคราะห์ สู่การพัฒนาที่ดีกว่า") สะกดถูก · ตัวเลขบนจอ 1250/320/875/640/2090 เป็นตัวเลขสุ่ม ไม่มีป้ายกำกับ จึงไม่ถือว่าเฉลยรั่ว | – |
| concept-23-version-compare-sabai.jpg | OK | – | – |
| outro-01-signoff-party.jpg | OK | – | – |

## ตรวจเรื่องเฉลยรั่ว
ไม่มีภาพไหนบอกต้นเหตุบั๊ก L2–L8 (ร้านกด "ใช้บริการเสร็จ" ให้นัดล่วงหน้าได้, logout แล้ว cookie ยังใช้ได้, ค่ารถ, Gift Card, owner ยกเลิกนัด, test hooks) หรือ mutant M1–M6 และไม่มีคำตอบข้อสอบ · ตัวเลขที่ปรากฏ (฿3,000→฿2,850, ฿760, 19:00→19:30, 081-000-0003) มาจากหนังสือ CR ที่ผู้เรียนเห็นอยู่แล้ว · ภาพ concept-20 พูดถึงการจองซ้ำ (L1) ซึ่งเป็นเรื่องร้องเรียนใน CR-03 ที่ผู้เรียนเห็นอยู่แล้ว

## วิธีแก้แบบแปะทับ
- ใช้ Playwright Chromium (`--disable-lcd-text`) เรนเดอร์ข้อความไทยด้วยฟอนต์ Leelawadee UI Bold แล้วใช้ PIL แปะทับ (ขอบเฟด 2–3 px) แล้วเซฟเป็น JPEG q90 ได้ intro-01 = 297 KB, concept-07 = 307 KB
- ไฟล์เดิมก่อนแก้สำรองไว้ใน scratchpad ของ VI6 (`vi6/backup/`) ไม่ได้อยู่ใน repo
