# yolo2 · Learning design · บท 03 สบายใจ สปา (เว็บจากพรอมต์ล้วน → Playwright)

> ผู้เขียน: Learning-experience designer · อ้างอิง BRIEF.md + README บท 01/02 + รูป 02/img/concept-02, 11, intro-04
> สไตล์ที่ต้องคงไว้จากบท 02: รูปการ์ตูนนำทุกหัวข้อ · ตารางแทนย่อหน้า · 💬 พรอมต์ในกรอบ text · ✅ ผลจริง · 👀 สังเกต 2 ข้อ · ข้อความสั้นมาก

---

## ส่วนที่ 1 · โครง README บทนี้

```text
# สร้างเว็บสปาจากพรอมต์ล้วน แล้วทดสอบด้วย Playwright
(2 บรรทัดนำ) บทนี้ "ไม่มีโค้ดให้" มีแค่รูป → เราคุยกับเจ้าของร้าน แล้วให้ Claude สร้างเว็บ + ทดสอบให้ทั้งหมด
```

### 1.1 ส่วนนำ · เข้าใจด้วยรูป (5 รูป ข้อความใต้รูปไม่เกิน 2 บรรทัด)

| ลำดับ | รูป | หัวข้อในหน้า | ข้อความใต้รูป (สั้น) |
|---|---|---|---|
| 1 | intro-01-sabai-spa.jpg | สบายใจ สปา คือเว็บอะไร? | เว็บสปาที่มี "AI" แนะนำ จองคิว สมาชิก และทัวร์ 360° |
| 2 | intro-02-from-scratch.jpg | บทนี้ต่างจากบท 02 ยังไง? | บท 02 มีเว็บให้ · บทนี้ **เริ่มจากโฟลเดอร์ว่าง** |
| 3 | intro-03-pro-flow.jpg | ทำงานแบบมืออาชีพ 8 สถานี | คุย → เขียนความต้องการ → พรอมต์ → เว็บ → ทดสอบ |
| 4 | intro-04-fake-ai.jpg | "AI" ในเว็บนี้ไม่ใช่ AI จริง | ใช้ **กฎตายตัว** ถามเหมือนเดิม ได้คำตอบเดิม → ทดสอบได้ |
| 5 | intro-05-bug-hunt-spa.jpg | ตอนจบได้อะไร? | GIF + MP4 + รายงาน และฝึกจับบั๊ก 3 ตัว |

ตาม intro-05 ด้วยตาราง "✅ เรียนจบได้อะไร" 5 แถว (เหมือนบท 02) และ "📂 ในโฟลเดอร์มีอะไร" (README / img / assets → จบบทจะมีไฟล์อะไรเพิ่ม)

```text
03_sabai-spa-from-prompt/
├─ README.md   📖 บทเรียน
├─ img/        🖼️ รูปประกอบบทเรียน
└─ assets/     🌸 รูปที่เว็บจะใช้ (ทำไว้ให้แล้ว)
— หลังทำครบทุก LAB จะมีเพิ่ม —
INTERVIEW.md → USER-STORIES.md → REQUIREMENTS.md → BUILD-PROMPT.md → sabai-spa/ → TEST-PLAN.md → e2e/
```

### 1.2 ความรู้พื้นฐาน (อ่าน 7 นาที · 1 หัวข้อ = 1 รูป + 1 ตารางเล็ก)

| # | หัวข้อ | รูป | เนื้อหาย่อ (ตาราง/1–2 บรรทัด) |
|---|---|---|---|
| 1 | ฟังก่อนสร้าง: สัมภาษณ์ | concept-01-interview.jpg | เจ้าของบอก "กฎร้าน" · ลูกค้าบอก "อยากได้อะไร" |
| 2 | User Story คืออะไร | concept-02-user-story.jpg | สูตร **ในฐานะ… ฉันอยาก… เพื่อ…** + ตัวอย่าง 2 ข้อ |
| 3 | เกณฑ์ยอมรับ (Acceptance) | concept-03-acceptance.jpg | "ต้องเห็นอะไร ถึงเรียกว่าเสร็จ" → กลายเป็น test ได้ทันที |
| 4 | FR / BR / NFR | concept-04-fr-br-nfr.jpg | ตาราง 3 แถว: ทำอะไร / กฎร้าน (มีตัวเลข) / ดีแค่ไหน (วัดได้) |
| 5 | ทำอะไรก่อน (Must/Should/Could) | concept-05-must-should.jpg | ฟีเจอร์เยอะ เวลาน้อย → ทำ Must ให้ครบก่อน |
| 6 | พรอมต์ที่เขียนพรอมต์ | concept-06-meta-prompt.jpg | เรา → Claude เขียน BUILD-PROMPT.md → เราอ่าน → copy ไปวาง |
| 7 | BUILD-PROMPT ที่ดีต้องมีอะไร | concept-07-build-prompt-checklist.jpg | เช็กลิสต์ 5 ช่อง (ดูส่วนที่ 2) |
| 8 | เว็บ 2 กล่อง: web + db | concept-08-two-containers.jpg | web = หน้าร้าน (Next.js :3000) · db = สมุดบัญชี (PostgreSQL) |
| 9 | ทำให้ "ทดสอบได้" | concept-10-testid.jpg, concept-09-reset-seed.jpg, concept-11-fixed-time.jpg | ป้ายชื่อปุ่ม · ปุ่มรีเซ็ต · ล็อกวันที่ |

ตัวอย่างตาราง FR/BR/NFR ที่ใส่ใน README (ใช้ตัวเลขจาก yolo3 เมื่อได้ข้อสรุป):

| ชนิด | ถามว่า | ตัวอย่างสปา |
|---|---|---|
| **FR** ความต้องการด้านฟังก์ชัน | เว็บต้อง **ทำอะไร**ได้? | จองคิว เลือกบริการ นักบำบัด เวลา |
| **BR** กฎธุรกิจ | ร้านมี **กฎ** อะไร? (มีตัวเลข) | จองล่วงหน้าได้ไม่เกิน 30 วัน · ห้ามจองซ้อน |
| **NFR** ความต้องการด้านคุณภาพ | ต้อง **ดีแค่ไหน**? (วัดได้) | ใช้บนมือถือ 375px ได้ · 3 ภาษา · เพลงไม่เล่นเอง |

### 1.3 รายการ LAB (9 LAB · ทำตามลำดับ เพราะแต่ละ LAB ใช้ไฟล์จาก LAB ก่อนหน้า)

> ไม่มี "พรอมต์รวมจบในพรอมต์เดียว" แบบบท 02 เพราะการสร้างเว็บใช้เวลานานและต้องให้นักศึกษาอ่าน/ตัดสินใจระหว่างทาง
> ทุก LAB มีรูป `labN-paste.png` (ภาพหน้าจอจริง วางพรอมต์ในช่อง กรอบแดง) เหมือนบท 02

**LAB 1 · สัมภาษณ์เจ้าของร้านและลูกค้า**
- 🎯 ให้ Claude สรุปบันทึกสัมภาษณ์ (เจ้าของ 1 + ลูกค้า 4) เป็น INTERVIEW.md ที่อ่านง่าย
- รูป: concept-01-interview.jpg (คุณจันทร์ + ลูกค้า พูดใส่สมุดของเด็ก)
- ✅ เห็น: INTERVIEW.md แบ่งหัวข้อ "กฎร้าน (ตัวเลข)" กับ "สิ่งที่ลูกค้าอยากได้" + รายการ "คำถามที่ยังไม่ชัด"
- 👀 ตัวเลขกฎร้าน (เวลาเปิด-ปิด, ยกเลิกก่อนกี่ ชม.) คือ "ค่าขอบ" ที่จะทดสอบภายหลัง · Claude ถามกลับเรื่องที่กำกวม = ดี

**LAB 2 · เขียน User Story**
- 🎯 แปลงสิ่งที่ลูกค้าอยากได้เป็น User Story พร้อมเกณฑ์ยอมรับ และจัด Must/Should/Could
- รูป: concept-02-user-story.jpg, concept-03-acceptance.jpg, concept-05-must-should.jpg
- ✅ เห็น: USER-STORIES.md ราว 15 ข้อ รหัส US-01… แต่ละข้อมีเกณฑ์ยอมรับ 1–2 ข้อ และป้าย Must/Should/Could
- 👀 Story พูดภาษา "ลูกค้า" ไม่มีคำว่า database/API · เกณฑ์ยอมรับที่ดีมีตัวเลขหรือข้อความที่ตรวจได้

**LAB 3 · แยก FR / BR / NFR**
- 🎯 ให้ Claude แตก Story เป็น FR, BR, NFR ที่มีรหัสและวัดผลได้
- รูป: concept-04-fr-br-nfr.jpg
- ✅ เห็น: REQUIREMENTS.md 3 ตาราง (FR-xx, BR-xx, NFR-xx) + คอลัมน์ "มาจาก US ไหน"
- 👀 BR ทุกข้อมีตัวเลข · NFR ที่เขียนว่า "เร็ว" หรือ "สวย" เฉย ๆ ใช้ไม่ได้ ต้องวัดได้ (เช่น < 3 วินาที)

**LAB 4 · ให้ Claude เขียนพรอมต์สร้างเว็บ (BUILD-PROMPT.md)**
- 🎯 ใช้พรอมต์ที่ "เขียนพรอมต์" ได้ BUILD-PROMPT.md ที่ครบพอให้ Claude อีกรอบสร้างเว็บได้เอง
- รูป: concept-06-meta-prompt.jpg, concept-07-build-prompt-checklist.jpg
- ✅ เห็น: BUILD-PROMPT.md มีหัวข้อ เทคโนโลยี / หน้าเว็บ / กฎ "AI" / testid / health+reset+seed / BUG_MODE / คำสั่ง Windows
- 👀 อ่านก่อนวางเสมอ ตรงไหนไม่ตรงกับ REQUIREMENTS ให้สั่งแก้ก่อน · พรอมต์นี้เก็บไว้ใช้ซ้ำได้ (สร้างใหม่ได้ทุกเมื่อ)

**LAB 5 · วางพรอมต์ → ได้เว็บ 2 กล่องใน Docker**
- 🎯 เปิด Claude Code **เซสชันใหม่** วาง BUILD-PROMPT.md แล้วได้เว็บที่ http://localhost:3000
- รูป: concept-08-two-containers.jpg + ภาพหน้าจอ lab5-docker.png (`docker compose ps` 2 แถว healthy)
- ✅ เห็น: กล่อง `web` และ `db` ขึ้น **healthy** · `/api/health` ตอบ ok · หน้าแรกสวยด้วยรูปจาก assets/ (site-home.png)
- 👀 ใช้เวลานาน (10–30 นาที) เป็นเรื่องปกติ · เว็บของแต่ละคน "หน้าตาไม่เหมือนกันเป๊ะ" แต่ต้องทำตาม requirement เดียวกัน

**LAB 6 · เดินดูเว็บแบบลูกค้า (Playwright MCP)**
- 🎯 ให้ Playwright MCP พาเดินทุกหน้าหลัก จับภาพ แล้วเทียบกับ REQUIREMENTS ว่าอะไรยังขาด
- รูป: concept-12-site-map.jpg + ตารางภาพหน้าจอ 2 คอลัมน์ (site-quiz, site-booking, site-mood, site-skin, site-wallet, site-tour, site-chatbot, site-mobile)
- ✅ เห็น: ภาพหน้าจอ 8 หน้า + ตาราง "FR ไหน มีแล้ว / ยังไม่มี"
- 👀 ลองกด "จองตามอารมณ์ → เหนื่อย" 2 รอบ ต้องได้ผลเหมือนเดิม (กฎตายตัว) · ปุ่มเพลงต้องกดเองถึงดัง ไม่ใช่บั๊ก

**LAB 7 · เขียนแผนทดสอบ (TEST-PLAN.md)**
- 🎯 ให้ Claude เขียน TEST-PLAN.md ที่โยง test case ทุกข้อกลับไปหา FR/BR พร้อม P1/P2/P3
- รูป: concept-13-req-to-test.jpg, concept-14-test-the-ai.jpg (+ ลิงก์ไป concept 4–5 ของบท 02 เรื่อง 5 คำถาม/P1-P3)
- ✅ เห็น: ~30 test case เป็นตาราง มีคอลัมน์ "มาจาก FR/BR" และเกณฑ์ผ่าน (P1 ผ่านหมด + ≥ 95%)
- 👀 ทุก BR ที่มีตัวเลขต้องมี test ค่าขอบ (ต่ำกว่า 1 · พอดี · เกิน 1) · "AI" ทดสอบได้เพราะรู้คำตอบล่วงหน้า

**LAB 8 · เขียน + รัน test 3 เบราว์เซอร์ ได้ GIF + MP4 + รายงาน**
- 🎯 สร้างโฟลเดอร์ e2e จากศูนย์ รัน Chromium/Firefox/WebKit แล้วได้หลักฐานแบบ tester
- รูป: concept-15-evidence-pack.jpg (+ ใช้ซ้ำ 02/concept-07-cross-browser.jpg ได้) + ภาพหน้าจอ lab8-html-report.png, lab8-test-report.png, gif-TC-BOOK-xx.gif
- ✅ เห็น: "N passed" (≈30 × 3) · GIF/MP4 ใน e2e/test-report · TEST-REPORT.md สรุป "ผ่านเกณฑ์ / ไม่ผ่านเกณฑ์"
- 👀 test ข้อแรกที่ทุกข้อเรียกคือ `/api/test/reset` → ข้อมูลเริ่มเหมือนกันทุกรอบ · ถ้าล้มตั้งแต่แรก ให้ดู GIF ก่อนเสมอ ห้ามแก้ test ให้ผ่าน

**LAB 9 · จับบั๊ก (BUG_MODE=1) + test ใหม่จากภาษาคน**
- 🎯 เปิดโหมดฝังบั๊ก ดูว่า test จับได้ครบ 3 ตัวไหม แล้วเขียนรายงานบั๊ก + เพิ่ม test 2 ข้อจากภาษาไทย
- รูป: intro-05-bug-hunt-spa.jpg, concept-17-bug-or-requirement.jpg (+ ใช้ซ้ำ 02/concept-15, 18)
- ✅ เห็น: ผ่าน N−3 · ล้ม 3 · ตาราง บั๊ก/test ที่จับ/คาดหวัง/จริง + GIF ของข้อที่ล้ม 3 ไฟล์ · รายงาน "ไม่ผ่านเกณฑ์"
- 👀 test ล้ม = เจอบั๊กก่อนลูกค้า 🎉 · บางครั้ง "ผิด" เพราะ requirement กำกวม → กลับไปแก้ REQUIREMENTS ไม่ใช่แค่โค้ด

**ท้ายบท** (เหมือนบท 02): "ถ้าเจอปัญหา: คัดลอกพรอมต์นี้" (concept-18-stuck-help.jpg) · 📖 คำศัพท์ · ไฟล์ในบทนี้หลังจบ

---

## ส่วนที่ 2 · รายการรูปการ์ตูนที่ต้องสร้าง (23 รูป · ทุกรูป 3:2 · 1536×1024 · .jpg)

### 2.0 บล็อกที่ต้องแปะ "ก่อน" prompt ทุกรูป

**[STYLE]**
`Cute anime cartoon illustration, thick clean dark-navy outlines, bright pastel colors, soft cel shading, rounded white speech boxes and rounded pastel label cards with numbered circle badges, like a friendly Thai classroom poster. Landscape 3:2 (1536x1024), uncluttered, lots of breathing room, very large readable text. Spa mood palette: sage green, cream, soft pink, warm gold accents, with lotus flowers, candles and bamboo as light decoration. Render ALL Thai text EXACTLY as written inside the quotes, in a bold rounded Thai font (like Kanit Bold or Prompt Bold), correct spelling with all vowels and tone marks, no extra words, no gibberish text, no watermark.`

**[CAST]** (ใส่เฉพาะตัวที่ปรากฏในรูปนั้น)
- BOY = `a Thai student boy, messy brown hair, big brown eyes, rosy cheeks, royal-blue hoodie with white drawstrings`
- ROBOT = `a small round white robot (Claude helper) with a dark glossy screen face showing cyan smiling eyes, light-blue ear pieces and a short antenna with a blue ball`
- OWNER = `"Khun Jan", a kind Thai spa owner woman in her 40s, dark hair in a neat bun with a white orchid, sage-green Thai-style spa blouse, gentle warm smile`
- LOTUS = `"Nong Bua", a chibi pink lotus flower mascot with a round happy face, tiny arms and a leaf-green collar`

> ตัวละครคงที่: BOY = นักศึกษา/tester · ROBOT = Claude · OWNER = เจ้าของร้าน · LOTUS = มาสคอตแชตบอต/ตัวแทน "AI" ของเว็บ

### 2.1 ส่วนนำ (5)

**1. img/intro-01-sabai-spa.jpg** · ตัวละคร: OWNER, LOTUS, BOY, ROBOT
- ข้อความ: หัว "สบายใจ สปา" · ① "AI แนะนำผิว" · ② "จองคิวทันที" · ③ "สมาชิก + แต้ม" · ④ "ทัวร์ห้อง 360°"
- ภาพ: หน้าจอแล็ปท็อปใหญ่กลางภาพเป็นเว็บสปาสวย (ห้องสปา ดอกบัว) มีป้ายฟีเจอร์ 4 ป้ายลอยรอบจอ OWNER ผายมือต้อนรับ BOY กับ ROBOT ทำหน้าตื่นเต้น
- Prompt: `[STYLE][CAST] A big laptop in the center shows a beautiful wellness spa website with a lotus pond hero image. Khun Jan stands left, welcoming with an open palm; Nong Bua floats near the screen waving. The boy and the robot on the right look amazed. Top title banner: "สบายใจ สปา". Four rounded feature cards around the laptop with icons (face scan, calendar, gold star card, 360 arrow): "AI แนะนำผิว", "จองคิวทันที", "สมาชิก + แต้ม", "ทัวร์ห้อง 360°".`

**2. img/intro-02-from-scratch.jpg** · ตัวละคร: BOY, ROBOT
- ข้อความ: หัว "เริ่มจากโฟลเดอร์ว่าง" · ซ้าย "บท 02: มีเว็บให้" · ขวา "บทนี้: มีแค่รูป" · ล่าง "พรอมต์ → เว็บทั้งเว็บ"
- ภาพ: แบ่งซ้าย-ขวา ซ้ายกล่องของขวัญมีเว็บร้านสัตว์เลี้ยงสำเร็จรูป ขวาโฟลเดอร์เกือบว่าง มีแค่ไอคอนรูปภาพ BOY ถือกระดาษพรอมต์ ROBOT ประกอบตัวต่อเป็นเว็บสปาจากกระดาษนั้น
- Prompt: `[STYLE][CAST] Split comparison poster. Left half (muted): an open gift box containing a ready-made pet shop website, label "บท 02: มีเว็บให้". Right half (bright): an almost empty folder with only a few picture icons, label "บทนี้: มีแค่รูป". The boy holds a glowing prompt paper; the robot builds a spa website out of toy blocks from that paper. Title: "เริ่มจากโฟลเดอร์ว่าง". Bottom ribbon: "พรอมต์ → เว็บทั้งเว็บ".`

**3. img/intro-03-pro-flow.jpg** · ตัวละคร: BOY, ROBOT, OWNER (เล็ก)
- ข้อความ: หัว "ทางเดินแบบมืออาชีพ" · ① "คุยกับร้าน" · ② "เขียนความต้องการ" · ③ "พรอมต์สร้างเว็บ" · ④ "ทดสอบ + จับบั๊ก"
- ภาพ: เส้นทางเกมกระดานคดเคี้ยว 4 จุดพัก (ไมโครโฟน, สมุดจด, กระดาษพรอมต์, แว่นขยาย+แมลง) BOY กับ ROBOT เดินตามทาง ปลายทางคือสปาที่มี OWNER ยืนรอ
- Prompt: `[STYLE][CAST] A winding board-game path with 4 big numbered stops: a microphone, a notebook with checklist, a glowing prompt scroll, a magnifying glass over a tiny cartoon bug. The boy and robot walk along the path; at the far end a small Thai spa building with Khun Jan waving. Title: "ทางเดินแบบมืออาชีพ". Stop labels: "คุยกับร้าน", "เขียนความต้องการ", "พรอมต์สร้างเว็บ", "ทดสอบ + จับบั๊ก".`

**4. img/intro-04-fake-ai.jpg** · ตัวละคร: LOTUS, ROBOT, BOY
- ข้อความ: หัว "AI ในเว็บนี้ = กฎตายตัว" · ① "เหนื่อย → นวดไทย" · ② "ถามซ้ำ ได้คำตอบเดิม" · ③ "ไม่ต้องใช้ API key" · ROBOT พูด "จึงทดสอบได้!"
- ภาพ: LOTUS ใส่หมวกนักมายากลแต่ด้านหลังมีสมุดกฎเปิดอยู่ (ถ้า…แล้ว…) BOY ถามคำถามเดิม 2 ครั้งได้การ์ดคำตอบเหมือนกัน 2 ใบ ROBOT ชูนิ้วโป้ง
- Prompt: `[STYLE][CAST] Nong Bua wears a tiny magician hat but secretly reads from an open rule book with if-then arrows behind its back. The boy asks twice and receives two identical answer cards. Title: "AI ในเว็บนี้ = กฎตายตัว". Cards: "เหนื่อย → นวดไทย", "ถามซ้ำ ได้คำตอบเดิม", "ไม่ต้องใช้ API key". The robot gives a thumbs up with speech bubble: "จึงทดสอบได้!".`

**5. img/intro-05-bug-hunt-spa.jpg** · ตัวละคร: ROBOT, BOY, LOTUS
- ข้อความ: หัว "ตามล่าบั๊ก 3 ตัว" · ① "ส่วนลดสมาชิกผิด" · ② "จองซ้อนได้" · ③ "คอร์สไม่ลดครั้ง" · ล่าง "test ล้ม = เจอบั๊ก"
- ภาพ: ROBOT ถือแว่นขยายส่องหน้าเว็บสปา เจอแมลงการ์ตูน 3 ตัวซ่อนในตะกร้าดอกไม้/ปฏิทิน/บัตรคอร์ส BOY ถือคลิปบอร์ดจด LOTUS ตกใจ (ชื่อบั๊กปรับตามที่ yolo1 เลือกจริง)
- Prompt: `[STYLE][CAST] The robot holds a big magnifying glass over a spa website and finds 3 cute cartoon bugs hiding: one on a member discount price tag, one on a calendar with two overlapping bookings, one on a course card. Each bug has a label card: "ส่วนลดสมาชิกผิด", "จองซ้อนได้", "คอร์สไม่ลดครั้ง". The boy writes on a clipboard, Nong Bua looks surprised. Title: "ตามล่าบั๊ก 3 ตัว". Bottom ribbon: "test ล้ม = เจอบั๊ก".`

### 2.2 ความรู้พื้นฐาน + LAB (18)

**6. img/concept-01-interview.jpg** · OWNER, BOY, ROBOT + ลูกค้า 2 คน (ตัวประกอบ)
- ข้อความ: หัว "ฟังก่อนสร้าง" · OWNER: "ยกเลิกก่อน 24 ชม. ฟรี" · ลูกค้า: "เครียดมาก อยากจองง่าย ๆ" · สมุด: "กฎร้าน · สิ่งที่อยากได้"
- ภาพ: โต๊ะในล็อบบี้สปา OWNER กับลูกค้าสาวออฟฟิศพูด BOY จดสมุดที่แบ่ง 2 คอลัมน์ ROBOT อัดเสียงด้วยไมค์เล็ก
- Prompt: `[STYLE][CAST] Cozy spa lobby table. Khun Jan speaks with bubble "ยกเลิกก่อน 24 ชม. ฟรี". A tired office-worker woman customer speaks with bubble "เครียดมาก อยากจองง่าย ๆ". The boy writes in a notebook split into two columns, header "กฎร้าน · สิ่งที่อยากได้". The robot holds a tiny microphone. Title: "ฟังก่อนสร้าง".`

**7. img/concept-02-user-story.jpg** · BOY, ROBOT
- ข้อความ: หัว "User Story = 3 ช่อง" · ① "ในฐานะ: คนทำงานที่เครียด" · ② "ฉันอยาก: จองตามอารมณ์" · ③ "เพื่อ: ได้ทรีตเมนต์ที่ใช่"
- ภาพ: เลียนแบบ concept-02 บท 02 — BOY ชี้การ์ดใหญ่ 3 แถบสี (ฟ้า เขียว ส้ม) ROBOT มุมขวาล่างโบกมือ
- Prompt: `[STYLE][CAST] The boy peeks from the left pointing at a big card with 3 colored numbered rows (blue, green, orange): "ในฐานะ: คนทำงานที่เครียด", "ฉันอยาก: จองตามอารมณ์", "เพื่อ: ได้ทรีตเมนต์ที่ใช่". Title banner: "User Story = 3 ช่อง". The robot waves at the bottom right.`

**8. img/concept-03-acceptance.jpg** · BOY, ROBOT
- ข้อความ: หัว "เสร็จแล้ว ดูยังไง?" · ① "กด 'เหนื่อย'" · ② "เห็นนวดไทยอันดับ 1" · ROBOT: "ตรวจได้ = เป็น test ได้"
- ภาพ: เช็กลิสต์บนกระดาน 2 ข้อมีติ๊กเขียว ลูกศรจากเช็กลิสต์ไปยังป้าย "TC" สีม่วง
- Prompt: `[STYLE][CAST] A pastel checklist board with two green-ticked lines: "กด 'เหนื่อย'" and "เห็นนวดไทยอันดับ 1". An arrow goes from the checklist to a purple tag shaped like a test card. The boy scratches his head thinking, the robot explains with speech bubble "ตรวจได้ = เป็น test ได้". Title: "เสร็จแล้ว ดูยังไง?".`

**9. img/concept-04-fr-br-nfr.jpg** · BOY, ROBOT, OWNER
- ข้อความ: หัว "ความต้องการ 3 แบบ" · FR "ทำอะไรได้: จองคิว" · BR "กฎร้าน: จองล่วงหน้า ≤ 30 วัน" · NFR "ดีแค่ไหน: โหลด < 3 วิ"
- ภาพ: 3 กล่องเรียงกัน สีฟ้า/ชมพู/เขียว ไอคอน ปุ่มจอง / หนังสือกฎที่ OWNER ถือ / นาฬิกาจับเวลา+มือถือ
- Prompt: `[STYLE][CAST] Three big rounded boxes side by side. Blue box with a booking button icon: "FR" and "ทำอะไรได้: จองคิว". Pink box where Khun Jan holds a rule book: "BR" and "กฎร้าน: จองล่วงหน้า ≤ 30 วัน". Green box with a stopwatch and a phone: "NFR" and "ดีแค่ไหน: โหลด < 3 วิ". The boy and robot stand below pointing. Title: "ความต้องการ 3 แบบ".`

**10. img/concept-05-must-should.jpg** · BOY, ROBOT
- ข้อความ: หัว "ทำอะไรก่อน?" · "Must: ต้องมี" · "Should: ควรมี" · "Could: มีก็ดี" · BOY: "Must ให้ครบก่อน!"
- ภาพ: ตะกร้าปิกนิก 3 ใบขนาดใหญ่-กลาง-เล็ก ใส่การ์ดฟีเจอร์ (ปฏิทินจอง, ควิซ, ทัวร์ 360) ROBOT ใส่การ์ดลงตะกร้าใหญ่ก่อน
- Prompt: `[STYLE][CAST] Three picnic baskets, large red, medium yellow, small green, labeled "Must: ต้องมี", "Should: ควรมี", "Could: มีก็ดี". Feature cards (calendar, quiz, 360 view icons) are sorted into them; the robot puts a calendar card into the large basket first. The boy cheers with bubble "Must ให้ครบก่อน!". Title: "ทำอะไรก่อน?".`

**11. img/concept-06-meta-prompt.jpg** · BOY, ROBOT ×2
- ข้อความ: หัว "พรอมต์ที่เขียนพรอมต์" · ① "สั่ง: ช่วยเขียนพรอมต์" · ② "ได้ BUILD-PROMPT.md" · ③ "อ่าน แล้ว Copy" · ④ "วางในเซสชันใหม่ → เว็บ"
- ภาพ: วงจร 4 ขั้นแบบ intro-04 บท 02 ROBOT ตัวแรกเขียนกระดาษยาว BOY อ่านด้วยแว่นขยาย ROBOT ตัวที่สองรับกระดาษไปสร้างเว็บ
- Prompt: `[STYLE][CAST] A left-to-right 4-step flow with numbered badges inside a big laptop frame. Step 1: the boy types, label "สั่ง: ช่วยเขียนพรอมต์". Step 2: the robot writes a long scroll, label "ได้ BUILD-PROMPT.md". Step 3: the boy reads it with a magnifier, label "อ่าน แล้ว Copy". Step 4: a second identical robot builds a spa website from the scroll, label "วางในเซสชันใหม่ → เว็บ". Title: "พรอมต์ที่เขียนพรอมต์".`

**12. img/concept-07-build-prompt-checklist.jpg** · ROBOT, BOY
- ข้อความ: หัว "BUILD-PROMPT ต้องมี" · ① "Next.js + PostgreSQL" · ② "รูปจาก assets/" · ③ "ป้าย data-testid" · ④ "health · reset · seed" · ⑤ "BUG_MODE + คำสั่ง Windows"
- ภาพ: ม้วนกระดาษยาวที่ ROBOT ถือ มีช่องติ๊ก 5 ช่องสีพาสเทล BOY ติ๊กด้วยดินสอยักษ์
- Prompt: `[STYLE][CAST] The robot holds open a long scroll with 5 pastel checkbox rows, the boy ticks them with a giant pencil: "Next.js + PostgreSQL", "รูปจาก assets/", "ป้าย data-testid", "health · reset · seed", "BUG_MODE + คำสั่ง Windows". Title: "BUILD-PROMPT ต้องมี".`

**13. img/concept-08-two-containers.jpg** · BOY, ROBOT, LOTUS
- ข้อความ: หัว "เว็บ 2 กล่อง" · กล่อง1 "web: หน้าร้าน :3000" · กล่อง2 "db: สมุดบัญชี" · ลูกศร "จอง → บันทึก" · ล่าง "docker compose up"
- ภาพ: ตู้คอนเทนเนอร์การ์ตูน 2 ใบบนหลังวาฬ Docker ซ้ายเป็นหน้าร้านสปามี LOTUS ต้อนรับ ขวาเป็นตู้เก็บสมุดช้างสีฟ้า (PostgreSQL) BOY เปิดเบราว์เซอร์ localhost:3000
- Prompt: `[STYLE][CAST] A friendly blue whale carries two cartoon shipping containers. Left container is a cute spa storefront with Nong Bua at the door, label "web: หน้าร้าน :3000". Right container is a filing cabinet with a small blue elephant and ledger books, label "db: สมุดบัญชี". A pipe arrow between them labeled "จอง → บันทึก". The boy uses a browser, the robot types the command shown on a ribbon "docker compose up". Title: "เว็บ 2 กล่อง".`

**14. img/concept-09-reset-seed.jpg** · ROBOT, BOY
- ข้อความ: หัว "ก่อนทดสอบ กดรีเซ็ต" · ① "ข้อมูลรก" · ② "/api/test/reset" · ③ "กลับเป็นข้อมูลตัวอย่าง" · ROBOT: "ทุกรอบเริ่มเหมือนกัน"
- ภาพ: ซ้ายห้องสปาที่ผ้าขนหนู/การ์ดจองกระจัดกระจาย กลางปุ่มแดงใหญ่ ขวาห้องเดียวกันเรียบร้อย ROBOT กดปุ่ม
- Prompt: `[STYLE][CAST] Three panels left to right. Panel 1: a messy spa room with scattered towels and booking cards, label "ข้อมูลรก". Panel 2: the robot presses a big round red button, label "/api/test/reset". Panel 3: the same room perfectly tidy, label "กลับเป็นข้อมูลตัวอย่าง". The robot speech bubble: "ทุกรอบเริ่มเหมือนกัน". Title: "ก่อนทดสอบ กดรีเซ็ต".`

**15. img/concept-10-testid.jpg** · ROBOT, BOY
- ข้อความ: หัว "ป้ายชื่อให้หุ่นยนต์" · ป้าย "data-testid=\"book-btn\"" · BOY: "คนดูสี" · ROBOT: "หุ่นยนต์ดูป้าย"
- ภาพ: ปุ่ม "จองเลย" สีชมพูบนหน้าเว็บ มีป้ายห้อยคอแบบป้ายชื่อพนักงาน ROBOT ส่องป้ายผ่านแว่น BOY มองตัวปุ่ม
- Prompt: `[STYLE][CAST] A big pink website button reading "จองเลย" wears a hanging name badge that reads "data-testid=\"book-btn\"" in monospace. The boy looks at the button colors with bubble "คนดูสี"; the robot scans the badge with a laser magnifier, bubble "หุ่นยนต์ดูป้าย". Title: "ป้ายชื่อให้หุ่นยนต์".`

**16. img/concept-11-fixed-time.jpg** · ROBOT, BOY
- ข้อความ: หัว "ล็อกวันที่ให้ test" · ซ้าย "วันนี้ว่าง พรุ่งนี้เต็ม?" · ขวา "test ส่งวันที่เอง" · ROBOT: "ผลเดิมทุกวัน"
- ภาพ: ซ้าย BOY งงกับปฏิทินที่หน้าเปลี่ยนเองตลอด ขวา ROBOT ตรึงปฏิทินด้วยหมุดทองที่วันที่ตัวอย่าง (ใส่ "พรุ่งนี้ 10:00")
- Prompt: `[STYLE][CAST] Left: the boy looks confused at a calendar whose pages keep flying, bubble "วันนี้ว่าง พรุ่งนี้เต็ม?". Right: the robot pins a calendar page with a big golden pushpin on a slot card reading "พรุ่งนี้ 10:00", label "test ส่งวันที่เอง", robot bubble "ผลเดิมทุกวัน". Title: "ล็อกวันที่ให้ test".`

**17. img/concept-12-site-map.jpg** · LOTUS, BOY, ROBOT
- ข้อความ: หัว "แผนที่เว็บสปา" · "หน้าแรก" · "AI ผิว + ควิซ" · "จองคิว" · "สมาชิก + Wallet" · "ทัวร์ 360°"
- ภาพ: แผนที่สวนสปามุมสูง เกาะ 5 เกาะเชื่อมด้วยสะพานไม้ LOTUS เป็นไกด์ถือธง BOY+ROBOT เดินตาม
- Prompt: `[STYLE][CAST] A top-down cute treasure-map of a spa garden with 5 islands linked by wooden bridges, each island has a sign: "หน้าแรก", "AI ผิว + ควิซ", "จองคิว", "สมาชิก + Wallet", "ทัวร์ 360°". Nong Bua leads as a tour guide with a small flag; the boy and robot follow. Title: "แผนที่เว็บสปา".`

**18. img/concept-13-req-to-test.jpg** · BOY, ROBOT
- ข้อความ: หัว "1 กฎร้าน → 3 test" · กฎ "จองล่วงหน้า ≤ 30 วัน" · "29 วัน → จองได้" · "30 วัน → จองได้" · "31 วัน → ต้องเตือน"
- ภาพ: เลียนแบบ concept-11 บท 02 — ม้วนกระดาษกฎซ้าย, BOY คิด, การ์ด 3 ใบขวา (เขียว เขียว แดง) (ตัวเลขปรับตาม BR จริงจาก yolo3)
- Prompt: `[STYLE][CAST] Left: a parchment scroll reading "จองล่วงหน้า ≤ 30 วัน". Middle: the boy thinking with question marks. Right: three stacked cards: green "29 วัน → จองได้", green "30 วัน → จองได้", red "31 วัน → ต้องเตือน". Yellow arrows connect them; the robot cheers at the bottom. Title: "1 กฎร้าน → 3 test".`

**19. img/concept-14-test-the-ai.jpg** · LOTUS, ROBOT
- ข้อความ: หัว "ทดสอบ AI แบบกฎ" · ใส่ "อารมณ์: เครียด" · คาดหวัง "อโรมา อันดับ 1" · ROBOT: "รู้คำตอบก่อน = ตรวจได้"
- ภาพ: เครื่องกรวยใสแบบ concept-08 บท 02: การ์ดอารมณ์ (แมวดินปั้นเครียด) ใส่ด้านบน ออกมาเป็นการ์ดทรีตเมนต์อโรมา มี LOTUS นั่งในเครื่อง
- Prompt: `[STYLE][CAST] A transparent funnel machine: a card with a stressed clay-cat face labeled "อารมณ์: เครียด" drops in the top; Nong Bua sits inside flipping a rule book; out comes a card with aroma oil bottles labeled "อโรมา อันดับ 1" next to a green check. The robot holds a clipboard, bubble "รู้คำตอบก่อน = ตรวจได้". Title: "ทดสอบ AI แบบกฎ".`

**20. img/concept-15-evidence-pack.jpg** · BOY, ROBOT, OWNER
- ข้อความ: หัว "หลักฐานการทดสอบ" · "3 เบราว์เซอร์" · "GIF + MP4" · "TEST-REPORT.md" · OWNER: "พร้อมเปิดร้านไหม?"
- ภาพ: ROBOT 3 ตัวเล็ก (Chromium/Firefox/WebKit โลโก้แบบการ์ตูน ไม่ใช้โลโก้จริง) วิ่งเข้าเส้นชัย BOY ยื่นแฟ้มรายงาน+ฟิล์มให้ OWNER
- Prompt: `[STYLE][CAST] Left: three mini robots in different colored jerseys cross a finish line, label "3 เบราว์เซอร์" (no real browser logos). Center: a film strip and a play button, label "GIF + MP4". Right: the boy hands a report folder labeled "TEST-REPORT.md" to Khun Jan, who asks with bubble "พร้อมเปิดร้านไหม?". Title: "หลักฐานการทดสอบ".`

**21. img/concept-16-pdpa-selfie.jpg** · BOY, LOTUS
- ข้อความ: หัว "เซลฟี่ไม่ออกจากเครื่อง" · ① "วิเคราะห์ในเบราว์เซอร์" · ② "ไม่อัปโหลด ไม่เก็บ" · LOTUS: "ปลอดภัย PDPA"
- ภาพ: BOY ถือมือถือเซลฟี่ รูปอยู่ในฟองแก้วรอบเครื่อง ลูกศรไปเซิร์ฟเวอร์ถูกขีดฆ่า แม่กุญแจทอง
- Prompt: `[STYLE][CAST] The boy takes a selfie with a phone; the photo stays inside a glowing glass bubble around the phone with a golden padlock, label "วิเคราะห์ในเบราว์เซอร์". An arrow to a cloud server is crossed out with a red X, label "ไม่อัปโหลด ไม่เก็บ". Nong Bua gives a thumbs up, bubble "ปลอดภัย PDPA". Title: "เซลฟี่ไม่ออกจากเครื่อง".`

**22. img/concept-17-bug-or-requirement.jpg** · BOY, ROBOT, OWNER
- ข้อความ: หัว "test ล้ม ผิดที่ไหน?" · ① "เว็บผิด → แก้เว็บ" · ② "test ผิด → แก้ test" · ③ "ความต้องการกำกวม → ถามร้าน" · ล่าง "ดู GIF ก่อนเสมอ"
- ภาพ: ทางแยก 3 ทาง ป้ายบอกทาง 3 ป้าย BOY ยืนตรงแยกถือ GIF ฟิล์ม ทางที่ 3 นำไปหา OWNER
- Prompt: `[STYLE][CAST] A crossroads with three wooden signposts: "เว็บผิด → แก้เว็บ", "test ผิด → แก้ test", "ความต้องการกำกวม → ถามร้าน"; the third path leads to Khun Jan holding a notebook. The boy stands at the junction holding a film strip; the robot points to a banner at the bottom "ดู GIF ก่อนเสมอ". Title: "test ล้ม ผิดที่ไหน?".`

**23. img/concept-18-stuck-help.jpg** · BOY, ROBOT
- ข้อความ: หัว "ติดตรงไหน Copy พรอมต์แก้" · ① "port 3000 ไม่ว่าง" · ② "db ยังไม่พร้อม" · ③ "Claude หยุดกลางทาง" · ROBOT: "บอกอาการ ให้ผมช่วย"
- ภาพ: BOY ยืนหน้ากำแพงอิฐ 3 ก้อนที่มีป้ายปัญหา ROBOT ยื่นการ์ดพรอมต์เรืองแสงเหมือนกุญแจ
- Prompt: `[STYLE][CAST] The boy faces a small brick wall with three labeled bricks: "port 3000 ไม่ว่าง", "db ยังไม่พร้อม", "Claude หยุดกลางทาง". The robot offers a glowing prompt card shaped like a key, bubble "บอกอาการ ให้ผมช่วย". Title: "ติดตรงไหน Copy พรอมต์แก้".`

### 2.3 ภาพหน้าจอจริง (ไม่ใช้ image gen · จับหลังรันจริง)
`lab1…lab9-paste.png` · `lab5-docker.png` · `site-home/quiz/skin/booking/mood/wallet/tour/chatbot/mobile.png` · `lab8-html-report.png` · `lab8-test-report.png` · `lab9-bug-report.png` · `gif-TC-*.gif` 4–5 ไฟล์ · `gif-bug-*.gif` 3 ไฟล์ · `video-TC-BOOK-xx.mp4` 1 ไฟล์ — เบลอชื่อผู้ใช้ Windows ทุกภาพ

**เคล็ดลับให้ image gen เขียนไทยถูก:** ข้อความต่อกล่อง ≤ 6–8 คำ · หลีกเลี่ยงสระซ้อนวรรณยุกต์ถี่ ๆ · ใส่ในเครื่องหมายคำพูดตรงตัว · สั่ง "no extra text" · ถ้าเพี้ยน ให้ลดเหลือ 3 กล่องแล้วสร้างใหม่ · ตรวจทุกรูปด้วยตาก่อนใช้

---

## ส่วนที่ 3 · คำแนะนำการเรียบเรียงภาษา

### 3.1 คำศัพท์ที่ต้องอธิบาย (ใส่ตาราง 📖 ท้ายบท · อธิบายด้วยการเปรียบเทียบสปา)

| คำ | อธิบายง่าย ๆ |
|---|---|
| **สัมภาษณ์ (Interview)** | คุยกับเจ้าของและลูกค้าก่อนสร้าง |
| **User Story** | "ในฐานะ… ฉันอยาก… เพื่อ…" ความต้องการ 1 ข้อจากมุมลูกค้า |
| **เกณฑ์ยอมรับ (Acceptance criteria)** | ต้องเห็นอะไรถึงเรียกว่า "เสร็จ" |
| **FR / BR / NFR** | เว็บทำอะไร / กฎของร้าน / ดีแค่ไหน |
| **Must / Should / Could** | ต้องมี / ควรมี / มีก็ดี |
| **พรอมต์ (Prompt) · BUILD-PROMPT** | ข้อความสั่ง AI · พรอมต์ยาวสำหรับสร้างเว็บทั้งเว็บ |
| **เซสชันใหม่** | เปิดหน้าต่าง Claude Code ใหม่ ความจำเริ่มจากศูนย์ |
| **Next.js / PostgreSQL** | ตัวสร้างหน้าเว็บ / ฐานข้อมูล (สมุดบัญชีของร้าน) |
| **docker compose / service** | คำสั่งเปิดหลายกล่องพร้อมกัน / กล่อง 1 ใบ (web, db) |
| **healthy / healthcheck** | กล่องพร้อมใช้จริง / ตัวคอยเช็กทุก 10 วินาที |
| **Rule-based (กฎตายตัว)** | "ถ้า… แล้ว…" ถามเหมือนเดิมได้คำตอบเดิม |
| **seed / reset** | ข้อมูลตัวอย่างตั้งต้น / ปุ่มล้างกลับเป็นข้อมูลตั้งต้น |
| **data-testid** | ป้ายชื่อที่หุ่นยนต์ใช้หาปุ่ม |
| **BUG_MODE** | สวิตช์เปิดบั๊กที่ฝังไว้ เพื่อฝึกจับ |
| **Traceability** | สายโยง: test ข้อนี้มาจาก FR/BR ข้อไหน |
| **PDPA** | กฎหมายคุ้มครองข้อมูลส่วนบุคคล → รูปเซลฟี่ห้ามเก็บ |

คำที่ **ไม่ต้องอธิบาย** (เรียนแล้วในบท 01–02, ลิงก์กลับไปแทน): Test case, P1/P2/P3, Happy/Negative, Boundary, E2E, GIF/MP4, Exit criteria

### 3.2 วิธีลดข้อความ

1. **1 หัวข้อ = 1 รูป + ≤ 2 บรรทัด** ถ้าต้องเกิน 3 บรรทัด → เปลี่ยนเป็นตาราง
2. **ตารางแทนย่อหน้า** เสมอ (ผลจริง, คำศัพท์, ปัญหา) คอลัมน์ไม่เกิน 4
3. **ใช้ตัวอย่างเดียววิ่งทั้งบท**: "คนทำงานเครียด → จองตามอารมณ์ → นวด/อโรมา" ใช้ใน User Story, เกณฑ์ยอมรับ, test ของ AI, GIF → นักศึกษาไม่ต้องจำตัวอย่างใหม่
4. **ไม่แปะผลงานยาว ๆ ลง README** (INTERVIEW, REQUIREMENTS, BUILD-PROMPT) → แสดงภาพหน้าจอ 1 ภาพ + ตาราง 3–5 แถว + `<details>` ซ่อนตัวเต็ม
5. **ฟีเจอร์ 15 ข้อของ BRIEF ห้ามลิสต์ซ้ำทุก LAB** → อยู่ในรูป intro-01 และ site map ครั้งเดียว
6. **👀 สังเกต = 2 bullet เท่านั้น** ข้อละ ≤ 1 บรรทัด เริ่มด้วยสิ่งที่ "ตาเห็น"
7. **ตัวเลขจากเว็บที่สร้างจริงต่างกันได้** → เขียน "≈" หรือ "ตัวอย่างจากเครื่องผู้สอน" กำกับทุกตาราง ✅ ผลจริง
8. คำอังกฤษเทคนิคใส่ `code` เฉพาะที่ต้องพิมพ์/ค้นหา (เช่น `BUG_MODE=1`, `/api/test/reset`) ที่เหลือเขียนไทย

### 3.3 จุดที่มือใหม่น่าจะงง/ติด → รูปหรือพรอมต์แก้

| จุดที่ติด | ทำไมงง | แก้ด้วย |
|---|---|---|
| "ทำไมไม่สั่งสร้างเว็บเลย ต้องเขียนพรอมต์ก่อนทำไม" | ดูอ้อม | รูป concept-06 + 1 บรรทัด: "พรอมต์ยาวครบ ตรวจก่อนได้ ใช้ซ้ำได้" |
| ไม่รู้ว่าต้องเปิด **เซสชันใหม่** ตอน LAB 5 | ไม่เข้าใจเรื่องความจำ AI | กล่อง 💡 + ภาพหน้าจอปุ่ม/คำสั่ง `/clear` หรือเปิดหน้าต่างใหม่ |
| สร้างเว็บนาน 10–30 นาที / Claude ถามอนุญาตบ่อย | คิดว่าค้าง | ใส่ ⏱️ เวลาที่คาด + พรอมต์: `ทำต่อจนเสร็จตาม BUILD-PROMPT.md ถ้าติดให้หยุดแล้วบอกว่าติดตรงไหน` |
| Claude หยุดกลางทาง / หน้าต่างเต็ม | context ยาว | พรอมต์: `อ่าน BUILD-PROMPT.md และไฟล์ที่สร้างแล้ว ตรวจว่าขาดอะไร แล้วทำต่อเฉพาะส่วนที่ขาด` |
| เว็บของตัวเองหน้าตาไม่เหมือนในบทเรียน | กลัวทำผิด | 👀 ใน LAB 5: "ไม่เหมือนเป๊ะได้ ขอแค่ทำตาม REQUIREMENTS" |
| พอร์ต 3000 ชน (เว็บ petshop บท 02 ยังเปิดอยู่) | error อ่านไม่ออก | รูป concept-18 + พรอมต์: `เช็กว่าพอร์ต 3000 ถูกใช้โดยอะไร ถ้าเป็น petshop บท 02 ให้ docker compose down ที่โฟลเดอร์นั้น` |
| web ขึ้นก่อน db พร้อม → web ล้ม | ไม่รู้ว่ามี 2 กล่อง | รูป concept-08 + พรอมต์: `ดู docker compose logs db และ web ให้ web รอ db healthy ก่อน (depends_on condition)` |
| สคริปต์ .sh ใน container พังเพราะ Windows (CRLF) | error "not found" งง | พรอมต์: `เช็กว่าไฟล์ .sh เป็น CRLF ไหม แปลงเป็น LF และเพิ่ม .gitattributes` |
| ตั้ง `BUG_MODE=1` ไม่เป็นใน PowerShell | ไวยากรณ์ต่างจาก Linux | ให้ BUILD-PROMPT ทำ `.env` หรือสคริปต์ npm ไว้ → พรอมต์ LAB 9 สั่งผ่าน Claude เท่านั้น |
| รูปในเว็บไม่ขึ้น | assets/ อยู่นอกโปรเจกต์ | BUILD-PROMPT ต้องสั่ง "คัดลอก assets/ ไป public/" + พรอมต์แก้: `รูปไม่ขึ้น ช่วยเช็กว่าคัดลอก assets ไป public แล้วหรือยัง` |
| เพลงไม่ดังเอง / "AI" ตอบเหมือนเดิมทุกครั้ง | คิดว่าเป็นบั๊ก | รูป intro-04 + 👀 ใน LAB 6 "นี่คือสิ่งที่ตั้งใจ" |
| อัปโหลดเซลฟี่ตัวเองไม่ได้/ไม่อยากใช้หน้าตัวเอง | ความเป็นส่วนตัว | ใช้ `assets/skin/sample-face.jpg` เสมอ + รูป concept-16 |
| test ล้มแบบสุ่ม (วันนี้ผ่าน พรุ่งนี้ล้ม) | เวลา/วันที่เปลี่ยน | รูป concept-11 + พรอมต์: `test ล้มเพราะวันที่หรือเปล่า ให้ใช้วันที่ที่ test ส่งเอง ห้ามแก้ expected ให้ผ่าน` |
| test ล้มบางข้อแค่บน WebKit | ไม่รู้ว่าเบราว์เซอร์ต่างกัน | พรอมต์: `ข้อนี้ล้มเฉพาะ WebKit ดู GIF แล้วบอกว่าเป็นบั๊กเว็บบน Safari หรือ test รอไม่พอ` |
| ไม่มี GIF / MP4 | ไม่มี ffmpeg | ใช้พรอมต์เดียวกับบท 02 (ลิงก์กลับ) |
| test ล้มตอน BUG_MODE=0 ก็ล้ม | สับสนบั๊กจริง vs บั๊กฝัง | รูป concept-17 + เน้น: "บั๊กจริงจากการสร้างเว็บ = เจอของจริง เก่งมาก" ให้รายงานแยกจากบั๊กฝัง |
| ลืมปิดโหมดบั๊ก | ผลรอบถัดไปเพี้ยน | บรรทัดสุดท้ายของพรอมต์ LAB 9 สั่งปิดเสมอ + ตารางปัญหา |

### 3.4 น้ำเสียงและรูปแบบ
- พูดกับนักศึกษาด้วย "เรา" · Claude เป็น "ผู้ช่วย" · ให้นักศึกษาเป็น "คนตัดสินใจ" เหมือนบท 01–02
- ทุก LAB เปิดด้วย 🎯 ประโยคเดียวที่บอก "ได้อะไร" ไม่ใช่ "ทำอะไร"
- จบบทด้วยประโยคเชื่อมโลกจริง: "ทีมจริงก็ทำแบบนี้: ฟัง → เขียน → สร้าง → ทดสอบ → วนกลับไปฟัง"
