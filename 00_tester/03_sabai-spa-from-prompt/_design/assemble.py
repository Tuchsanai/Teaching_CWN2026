"""Merge readme-part1 + readme-part2 and fill result placeholders -> ../README.md"""
import os, re
D = os.path.dirname(os.path.abspath(__file__))
p1 = open(os.path.join(D, 'readme-part1.md'), encoding='utf-8').read()
p2 = open(os.path.join(D, 'readme-part2.md'), encoding='utf-8').read()
md = p1.rstrip() + '\n\n' + p2.lstrip()

def fill(key, text):
    global md
    md = md.replace('{{' + key + '}}', text.strip())

fill('LAB4_RESULT', '''
Claude ทำครบ **12 ขั้น (0–11)** ใช้เวลาประมาณ **50 นาที** และตรวจกฎร้านผ่าน API เอง **79 ข้อ ผ่านทั้งหมด**

![PowerShell แสดง docker compose ps กล่อง sabai-db และ sabai-web ขึ้น healthy ทั้งคู่ และ /api/health ตอบ ok true db true วงสีแดงไว้](img/lab4-docker.png)

| ขั้น | ผล |
|---|---|
| Docker 2 กล่อง | ✅ `sabai-db` (postgres:16-alpine) + `sabai-web` (Next.js) ขึ้น **healthy** |
| `/api/health` | ✅ `{"ok":true,"db":true}` |
| รูปจาก `assets/` | ✅ คัดลอกครบ 35 รูป ไม่มีรูปจากเน็ต |
| ฟีเจอร์ | ✅ จองเดี่ยว/คู่/กลุ่ม · อารมณ์ · ควิซ · วิเคราะห์ผิว · ก่อน/หลัง · chatbot 3 ภาษา · Wallet · Gift Card · ทัวร์ 360° · เพลง |
| สำหรับ test | ✅ `data-testid` ทุกปุ่ม · ปุ่มรีเซ็ต + ล็อกวันที่ · ผู้ใช้ตัวอย่าง 3 คน (`nida@sabai.test` / `Sabai1234!`) |
| เอกสาร | ✅ `spa/SPEC.md` (testid, ข้อความ error, API) · `spa/BUGS.md` (เฉลยบั๊ก) |
''')

fill('LAB4_SCREENSHOTS', '''
แล้วเปิด http://localhost:3000 ได้เว็บนี้ 🎉 (รูปทุกรูปมาจาก `assets/`)

![หน้าแรกเว็บสบายใจ สปา หัวข้อ กลับมาสบายใจในทุกสัมผัส ภาพศาลาสปาริมสระบัวยามเย็น ปุ่มจองคิวเลย](img/site-home.jpg)

| 💆 บริการและทรีตเมนต์ | 👩 นักบำบัด + คะแนนรีวิว |
|---|---|
| ![หน้าบริการ การ์ดนวดไทย ฿800 ประคบสมุนไพร ฿900 นวดเท้า ฿600](img/site-services.jpg) | ![หน้านักบำบัด รูปนักบำบัดในชุดสปา คะแนน 4.9 4.5 4.4 และตัวกรอง 4.5 ดาวขึ้นไป](img/site-therapists.jpg) |
| 🎁 **Gift Card 3 ลาย** | 🛏️ **ทัวร์ห้อง 360°** |
| ![หน้า Gift Card บัตรลายทองสีเขียว ฿2,000 เลือกมูลค่าและลาย ส่งทาง LINE หรืออีเมล](img/site-gift.jpg) | ![หน้า Couple Suite ทัวร์ 360 องศา ภาพห้องสปาคู่ ลากเพื่อหมุน](img/site-tour.jpg) |
| 🚐 **แพ็กเกจนักท่องเที่ยว + รถรับส่ง** | 📱 **มือถือ** |
| ![หน้าแพ็กเกจ Bangkok Relax คนขับเปิดประตูรถตู้ให้คู่นักท่องเที่ยว ราคา ฿2,900](img/site-package.jpg) | ![หน้าแรกบนจอมือถือ](img/site-mobile-home.jpg) |
''')

fill('LAB5_RESULT', '''
Claude เดินครบ 5 ขั้น เก็บภาพไว้ใน `screenshots/` **16 รูป** และไม่มี error ใน console

| 😩 เลือก "เครียด" → อโรมา · ประคบ · ขัดผิว | ⭐ รีวิวนักบำบัด |
|---|---|
| ![หน้าเลือกอารมณ์ กดเครียด แนะนำนวดน้ำมันอโรมา ฿1,500 ประคบสมุนไพร ฿900 ขัดผิวข้าวมะพร้าว ฿1,400](img/site-mood-stressed.jpg) | ![การ์ดนักบำบัดมาลี 4.9 ดาว 10 รีวิว เปิดรายการรีวิวของลูกค้า](img/site-therapist-reviews.jpg) |
| 📅 **จองคิว: รอบเต็มกดไม่ได้** | 🔍 **วิเคราะห์ผิวในเครื่อง** |
| ![หน้าจองคิว ตารางรอบเวลา 14:30 15:00 15:30 ขึ้นเต็ม สรุปราคานวดไทย ฿800](img/site-book-summary.jpg) | ![ผลวิเคราะห์ผิวรูปตัวอย่าง ผิวสมดุล ค่าเฉลี่ย R170 G140 B124 แนะนำทรีตเมนต์หน้าขมิ้นและอโรมา](img/site-skin-result.jpg) |
| ✨ **ภาพจำลองก่อน/หลัง** | 💬 **Chatbot ตอบราคา** |
| ![ภาพจำลองก่อนหลังทำทรีตเมนต์ ใบหน้าครึ่งซ้ายก่อน ครึ่งขวาหลัง มีแถบเลื่อนเปรียบเทียบ ป้ายภาพจำลองเท่านั้น](img/site-skin-before-after.jpg) | ![หน้าต่างแชทผู้ช่วยสบายใจ ถามนวดไทยราคาเท่าไหร่ ตอบรายการราคาทุกบริการ](img/site-chatbot-price.jpg) |
| 🏅 **บัญชีคุณนิดา: Gold 124 แต้ม** | 🎟️ **Wallet: เหลือ 7 จาก 11 ครั้ง** |
| ![หน้าบัญชีคุณนิดา ระดับ Gold แต้ม 124 ยอดสะสม ฿12,400 อีก ฿17,600 ถึง Platinum](img/site-account.jpg) | ![หน้า Wallet คอร์สกระชับสัดส่วนเหลือ 7 จาก 11 ครั้ง หมดอายุ 5 ก.พ. 2027](img/site-wallet.jpg) |

ตารางที่ Claude สรุป (ย่อ)

| หน้า | สิ่งที่ควรทดสอบ | ความเสี่ยง |
|---|---|---|
| จองคิว `/book` | จองซ้อน · ช่วงวันที่ +1 ถึง +30 · ราคาทุกบรรทัด | 🔴 สูง |
| บัญชี / Wallet | ระดับสมาชิก ฿10,000 · ยกเลิก 24 ชม. · คอร์สลดครั้ง | 🔴 สูง |
| เข้าสู่ระบบ | รหัสผิดต้องเตือน · เข้า `/wallet` โดยไม่ login | 🔴 สูง |
| อารมณ์ / ผิว / Chatbot | ผลต้องเหมือนเดิมทุกครั้ง · ตอบตามภาษาที่ถาม | 🟡 กลาง |
| หน้าแรก | เมนู ปุ่มจอง สลับภาษา มือถือ | 🟢 ต่ำ |

💡 **Playwright MCP ไม่ขยับ?** ตอนเปิดแท็บครั้งแรก ปลั๊กอินใน Chrome จะ **ขอให้กดอนุญาต** (เหมือนบท 01 LAB 6) ถ้าไม่กด Claude จะรอไปเรื่อย ๆ
''')

fill('LAB6_RESULT', '''
ได้ `TEST-PLAN.md` **33 test case** โยงกลับ FR/BR ครบ และมีหัวข้อ **"ต้องถาม" 15 ข้อ** (ค่าที่ SPEC ไม่ได้บอก Claude ไม่เดาเอง)

| โมดูล | จำนวน | P1 | P2 | P3 |
|---|---|---|---|---|
| BOOK จองคิว | 8 | 8 | – | – |
| MEM สมาชิก / แต้ม | 4 | 4 | – | – |
| WAL คอร์ส | 3 | 3 | – | – |
| อื่น ๆ (HOME MOOD THER AI CHAT GIFT DASH EXP MOB API) | 18 | 4 | 11 | 3 |
| **รวม** | **33** | **19** | **11** | **3** |

ตัวอย่างจากไฟล์จริง

| ID | สิ่งที่ทดสอบ | มาจาก | ระดับ |
|---|---|---|---|
| TC-BOOK-01 | **E2E** จองคิวเดี่ยวจนจบ: บริการ → วัน → รอบ → ยืนยัน | FR-01, FR-06 | P1 |
| TC-BOOK-03 | ปฏิทินกดได้แค่ +1 ถึง +30 วัน (ข้ามเดือนด้วย) | BR-05 | P1 |
| TC-MEM-01 | ค่าขอบระดับ ฿9,999 / ฿10,000 / ฿29,999 / ฿30,000 | BR-13 | P1 |
| TC-WAL-01 | จองด้วยคอร์สแล้ว **7 → 6 ครั้ง** ยกเลิกแล้วคืน | BR-16 | P1 |
| TC-MOOD-01 | เลือกอารมณ์ 10 รอบ ต้องได้คำแนะนำเดิมทุกรอบ | BR-23 | P2 |
| TC-API-01 | เรียก API ที่ต้อง login โดยไม่ login → **401** | FR-07 | P2 |

เกณฑ์ผ่าน: P1 ผ่านครบ **19/19** และผ่านรวม ≥ 95% (อย่างน้อย **32 จาก 33**)
''')

# LAB 7 prompt: reset only once (fix found by yolo1 code review)
md = md.replace(
    '3. global-setup.ts: เช็ก /api/health ถ้าเว็บยังไม่เปิดให้ error ภาษาไทยบอกวิธีเปิด แล้ว POST /api/test/reset พร้อม now ที่ล็อกไว้\n',
    '3. global-setup.ts: เช็ก /api/health ถ้าเว็บยังไม่เปิดให้ error ภาษาไทยบอกวิธีเปิด แล้ว POST /api/test/reset พร้อม now ที่ล็อกไว้\n'
    '   (reset แค่ครั้งเดียวตรงนี้ ห้าม reset ใน test เพราะ 3 เบราว์เซอร์รันพร้อมกัน)\n')

for k in ['LAB7_RESULT', 'LAB8_RESULT', 'LAB9_RESULT']:
    p = os.path.join(D, f'{k}.md')
    if os.path.exists(p): fill(k, open(p, encoding='utf-8').read())

open(os.path.join(D, '..', 'README.md'), 'w', encoding='utf-8').write(md)
left = re.findall(r'\{\{\w+\}\}', md)
imgs = set(re.findall(r'\]\((img/[^)]+)\)', md))
missing = [i for i in imgs if not os.path.exists(os.path.join(D, '..', i))]
print('placeholders left:', left)
print('images referenced:', len(imgs), 'missing:', missing)
