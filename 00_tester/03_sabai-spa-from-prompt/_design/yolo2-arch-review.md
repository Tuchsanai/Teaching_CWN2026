# ตรวจแผนภาพสถาปัตยกรรม: concept-29 / concept-30

ผู้ตรวจ: yolo2 · วันที่ 2026-10-08 · อ่านโค้ดอย่างเดียว ไม่ได้รัน docker

## ตัวเลขที่นับได้จากโค้ด

| เรื่อง | ค่าจริง | หลักฐาน |
|---|---|---|
| หน้าเว็บ (`page.tsx`) | **17** หน้า: `/` `/account` `/book` `/gift-cards` `/login` `/mood` `/packages/bangkok-relax` `/privacy` `/quiz` `/register` `/rooms` `/rooms/couple-suite` `/services` `/services/[slug]` `/skin` `/therapists` `/wallet` (ไม่นับ `not-found.tsx`) | `find spa/app -name page.tsx` |
| API (`route.ts`) | **22** ไฟล์ route = **24** endpoint (`/api/bookings` มี GET+POST, `/api/test/reset` มี GET+POST) · ในจำนวนนี้มี 2 path สำหรับทดสอบ (`/api/test/reset`, `/api/test/user`) | `find spa/app/api -name route.ts` · `spa/app/api/bookings/route.ts` · `spa/app/api/test/reset/route.ts` |
| ตาราง DB (`CREATE TABLE`) | **14** ตาราง: settings, users, sessions, services, therapists, reviews, rooms, hotels, courses, waist_measurements, body_photos, gift_cards, bookings, booking_resources | `spa/lib/server/schema.ts:2,7,21,27,40,47,56,65,72,83,90,98,114,152` |
| เวอร์ชัน PostgreSQL | **16** (`postgres:16-alpine`) | `spa/docker-compose.yml:3` |
| container | `db` → `sabai-db`, `web` → `sabai-web` พอร์ต `3000:3000` · db ไม่เปิดพอร์ตออก host | `spa/docker-compose.yml:2-4,19-25` |
| ข้อมูลถาวร | named volume `sabai-db-data` | `spa/docker-compose.yml:10-11,44-45` |
| web image | Node 20 alpine, Next.js standalone, `node server.js` :3000 | `spa/Dockerfile:4,19,27,30-31` |

## AI ทำงานที่ไหน

| ฟีเจอร์ | ทำงานที่ | หลักฐาน |
|---|---|---|
| วิเคราะห์ผิว | **เบราว์เซอร์** เฉลี่ยสีด้วย `<canvas>` แล้วใช้ `classifySkin` ไม่อัปโหลดรูป | `spa/app/skin/page.tsx:1,16-38,76` · `spa/lib/recommend.ts:81` |
| แนะนำตามอารมณ์ / แบบทดสอบ | **เบราว์เซอร์** (`recommendForMood`, `quizResult`) | `spa/app/mood/page.tsx:1,7` · `spa/app/quiz/page.tsx:1,8` · `spa/lib/recommend.ts:21,47` |
| แชตบอต | **ผสม**: แยกภาษา/เจตนาในเบราว์เซอร์ แต่ราคา รอบว่าง และการจองต้องเรียก API ฝั่ง server | `spa/components/ChatBot.tsx:1,6,59,89,121,248` · `spa/lib/chatbot.ts:1-20` · ฝังทุกหน้าผ่าน `spa/app/layout.tsx:49` |
| กฎราคา / ส่วนลด / แต้ม | **server** (`buildQuote` → `computeQuote`) ไฟล์ `lib/rules.ts` ใช้ได้ทั้งสองฝั่ง แต่ยอดจริงคิดที่ API | `spa/lib/rules.ts:117` · `spa/lib/server/booking.ts:11,187,238` |
| ทุกตัวเป็น "AI" ปลอม | กฎตายตัว ไม่สุ่ม ไม่เรียก API ภายนอก (NFR-12) | `spa/lib/recommend.ts:1` · `spa/lib/chatbot.ts:1` · `REQUIREMENTS.md:98` |

Playwright (`e2e/playwright.config.ts`) รันบนเครื่องผู้เรียน ยิงไปที่ `baseURL` `http://localhost:3000` (บรรทัด 31) ใช้ 3 เบราว์เซอร์ chromium/firefox/webkit (บรรทัด 41-48) และมี project `time-travel` (บรรทัด 49-54) นอกจากเปิดหน้าเว็บแล้วยังเรียก API ตรงด้วย เช่น `e2e/global-setup.ts:22` (`/api/test/reset`), `e2e/tests/fixtures.ts:94` (`/api/test/user`) และ `e2e/tests/02-api.spec.ts`

---

## รูปที่ 1: `img/concept-29-architecture.jpg` ("ระบบของเว็บสปา")

| องค์ประกอบในรูป | ของจริงในโค้ด | ผล | ข้อเสนอแก้ |
|---|---|---|---|
| หัวเรื่อง "ระบบของเว็บสปา" | — | ถูก | คงไว้ |
| ① "คอมพิวเตอร์ของเรา (Windows)" | Playwright รันบน host ยิงไปที่ `localhost:3000` (`e2e/playwright.config.ts:31`) · คำสั่งใน CLAUDE.md เป็น PowerShell | ถูก | คงไว้ |
| "เบราว์เซอร์" | ผู้ใช้/Playwright เปิดผ่านเบราว์เซอร์ | ถูก | ใส่ให้ชัดขึ้นเป็น "เบราว์เซอร์ → localhost:3000" |
| "Playwright หุ่นยนต์ทดสอบ" | `e2e/playwright.config.ts:39-55` | ถูกแต่ไม่ครบ | "Playwright หุ่นยนต์ทดสอบ (Chromium · Firefox · WebKit)" |
| ลูกศร "เปิดเว็บ / จองคิว" → web | `ports: "3000:3000"` (`spa/docker-compose.yml:24-25`) | ถูก | "เปิดเว็บ / จองคิว ผ่าน http://localhost:3000" |
| ② "web: Next.js :3000" | service `web` / container `sabai-web` / พอร์ต 3000 (`spa/docker-compose.yml:19-25`, `spa/Dockerfile:30-31`) | ถูก | "web (sabai-web): Next.js :3000" |
| ป้าย "หน้าเว็บ" + "API" ใน container web | 17 `page.tsx` + 22 `route.ts` อยู่ใน image เดียวกัน | ถูก | คงไว้ หรือเติม "หน้าเว็บ 17 · API 22" |
| ลูกศร "อ่าน-เขียนข้อมูล" web ↔ db | `DATABASE_URL: postgres://spa:spa@db:5432/spa` (`spa/docker-compose.yml:27`) | ถูก | คงไว้ |
| ③ "db: PostgreSQL" | `postgres:16-alpine` container `sabai-db` (`spa/docker-compose.yml:2-4`) | ถูก | "db (sabai-db): PostgreSQL 16" |
| ถัง "เก็บข้อมูลถาวร" | volume `sabai-db-data` (`spa/docker-compose.yml:10-11,44-45`) | ถูก แต่วาดไว้ในตัว container | "volume sabai-db-data: ข้อมูลยังอยู่หลัง docker compose down" |
| วาฬ "docker" แบกทั้ง 2 container | docker compose 2 services (`spa/docker-compose.yml:1-42`) | ถูก | "docker compose: 2 container" |
| ④ "AI = กฎในเบราว์เซอร์" | ผิว/อารมณ์/ควิซ อยู่ในเบราว์เซอร์จริง แต่แชตบอตเรียก `/api/services` `/api/availability` `/api/quote` `/api/bookings` (`spa/components/ChatBot.tsx:59,89,121,248`) | **ทำให้เข้าใจผิด** ผู้เรียนจะคิดว่าแชตบอตไม่แตะ server และคิดว่ามี AI จริง | "AI = กฎตายตัว ไม่สุ่ม · ผิว/อารมณ์/ควิซ คิดในเบราว์เซอร์ · แชตบอตถามราคา-คิว-จอง ผ่าน API" |
| ป้ายซ้ายบน "สปา ใจดี ♥ ชีวิตดีขึ้น" | ชื่อร้านคือ "สบายใจ สปา" (`spa/lib/i18n.ts:15`) | **ผิด** (ชื่อร้านผิด) | "สบายใจ สปา" หรือลบทิ้ง |
| จอโน้ตบุ๊ก "สปส / สปา ใจดี / จองคิว" | ชื่อร้าน "สบายใจ สปา" | **ผิด** ("สปส" เป็นตัวอักษรเพี้ยน ชื่อร้านผิด) | "สบายใจ สปา" + ปุ่ม "จองคิว" |
| ป้ายขวาบน "ผ่อนคลายด้วยเทคโนโลยี สู่สุขภาพที่ดีในทุกวัน" | — | ตกแต่ง ไม่ผิด แต่ทำให้รก | ลบ |
| ป้ายซ้ายล่าง "นวดกาย สบายใจ โค้ดก็สบายขึ้น ♥" | — | ตกแต่ง ไม่ผิด | ลบ หรือคงไว้ 1 ป้ายเท่านั้น |
| ป้ายไม้ล่าง "เทคโนโลยีที่ดูแล...เหมือนสปาที่ใส่ใจ ♥" | — | ตกแต่ง ไม่ผิด | ลบ |
| หินขวาล่าง "สุขภาพดี เริ่มได้จากวันนี้" | — | ตกแต่ง ไม่ผิด | ลบ |

## รูปที่ 2: `img/concept-30-architecture-detail.jpg` ("ระบบมีกี่ชั้น?")

| องค์ประกอบในรูป | ของจริงในโค้ด | ผล | ข้อเสนอแก้ |
|---|---|---|---|
| หัวเรื่อง "ระบบมีกี่ชั้น?" | — | ถูก | คงไว้ |
| ① "หน้าเว็บ 17 หน้า" | 17 `page.tsx` (ดูตารางนับด้านบน) | ถูก | คงไว้ |
| ป้าย "จองคิว" | `spa/app/book/page.tsx` | ถูก | คงไว้ |
| ป้าย "AI ผิว" | `spa/app/skin/page.tsx` | ถูก | คงไว้ |
| ป้าย "แชตบอต" | เป็น component ลอยอยู่ทุกหน้า ไม่ใช่หน้าแยก (`spa/app/layout.tsx:49`) | เกือบถูก | "แชตบอต (ทุกหน้า)" |
| ป้าย "Wallet" | `spa/app/wallet/page.tsx` | ถูก | คงไว้ |
| ② "API 22 เส้น" | 22 ไฟล์ `route.ts` = 24 endpoint (มี 2 path สำหรับ test) | ถูกถ้านับเป็น path · คลุมเครือ | "API 22 path (24 endpoint รวม /api/test/*)" |
| ③ "กฎร้าน: ราคา ส่วนลด แต้ม" ใต้ API | `computeQuote` `spa/lib/rules.ts:117` ถูกเรียกจาก `spa/lib/server/booking.ts:238` | ถูก | "กฎร้าน (คิดที่ server): ราคา ส่วนลด แต้ม" |
| วงเล็บ "sabai-web" ครอบชั้น 1–3 | container `sabai-web` (`spa/docker-compose.yml:23`) | ถูก | คงไว้ |
| ④ "PostgreSQL 15 ตาราง" | **14** ตาราง (`spa/lib/server/schema.ts`) และเวอร์ชันคือ **16** (`spa/docker-compose.yml:3`) | **ผิด** จำนวนตารางผิด และอ่านได้ว่าเป็น "PostgreSQL เวอร์ชัน 15" | "PostgreSQL 16 · 14 ตาราง" |
| วงเล็บ "sabai-db" ครอบชั้น 4 | container `sabai-db` (`spa/docker-compose.yml:4`) | ถูก | คงไว้ |
| ลูกศรไหล 1→2→3→4 | page เรียก API → server ใช้กฎ → query DB | ถูก | คงไว้ |
| หุ่นยนต์ "Playwright ทดสอบตรงนี้" ชี้ชั้น 1 อย่างเดียว | Playwright เรียก API ตรงด้วย (`e2e/global-setup.ts:22`, `e2e/tests/fixtures.ts:94`, `e2e/tests/02-api.spec.ts`) | **ทำให้เข้าใจผิด** (ผู้เรียนจะคิดว่าทดสอบผ่าน UI อย่างเดียว) | ลูกศร 2 เส้นไปชั้น 1 และ 2: "Playwright ทดสอบหน้าเว็บ + เรียก API ตรง" |
| ไม่ได้บอกว่าชั้น 1 รันในเบราว์เซอร์ | ทุก `page.tsx` เป็น `"use client"` · ผิว/อารมณ์/ควิซ คิดในเบราว์เซอร์ | ขาดข้อมูล | ใต้ชั้น 1 เติม "รันในเบราว์เซอร์ · AI ผิว/อารมณ์ = กฎตายตัว" |
| ป้าย "สวย สบาย ด้วยเทคโนโลยี ♡" | — | ตกแต่ง ไม่ผิด | ลบ |
| ป้าย "เล็ก แต่สวย ทำได้จริง ♡" | — | ตกแต่ง ไม่ผิด | ลบ |
| ป้าย "เทคโนโลยีเพื่อความงามที่ยั่งยืน ♡" | — | ตกแต่ง ไม่ตรงเนื้อหา | ลบ |
| หิน "ระบบดี ชีวิตสบาย ♡" | — | ตกแต่ง ไม่ผิด | ลบ |

---

## สรุป

| รูป | ผล | เหตุผลหลัก |
|---|---|---|
| concept-29-architecture.jpg | **ต้องสร้างใหม่** (โครงถูกแล้ว แก้ข้อความ) | ข้อ ④ "AI = กฎในเบราว์เซอร์" ทำให้เข้าใจผิดเรื่องแชตบอต · ชื่อร้านผิดเป็น "สปา ใจดี" และมีตัวอักษรเพี้ยน "สปส" บนจอ |
| concept-30-architecture-detail.jpg | **ต้องสร้างใหม่** | "PostgreSQL 15 ตาราง" ผิด (จริง 14 ตาราง เวอร์ชัน 16) · Playwright ชี้แค่ชั้นหน้าเว็บ |

### ข้อความทั้งหมดที่รูปใหม่ concept-29 ควรมี

- หัวเรื่อง: **ระบบของเว็บสปา**
- ① **คอมพิวเตอร์ของเรา (Windows)**
  - **เบราว์เซอร์** (จอแสดง "สบายใจ สปา" + ปุ่ม "จองคิว")
  - **Playwright หุ่นยนต์ทดสอบ (Chromium · Firefox · WebKit)**
- ลูกศร: **เปิดเว็บ / จองคิว → http://localhost:3000**
- วาฬ: **docker compose: 2 container**
- ② **web (sabai-web): Next.js :3000** ข้างในมีป้าย **หน้าเว็บ** และ **API**
- ลูกศร web ↔ db: **อ่าน-เขียนข้อมูล**
- ③ **db (sabai-db): PostgreSQL 16**
- ถัง: **volume sabai-db-data: ข้อมูลยังอยู่หลัง docker compose down**
- ④ **AI = กฎตายตัว ไม่สุ่ม** · บรรทัดรอง **ผิว/อารมณ์/ควิซ คิดในเบราว์เซอร์ · แชตบอตถามราคา-คิว-จอง ผ่าน API**
- ข้อความตกแต่ง: ไม่ใส่ หรือใส่แค่ **สบายใจ สปา** 1 ป้าย (ห้ามมี "สปา ใจดี", "สปส", สโลแกนอื่น)

### ข้อความทั้งหมดที่รูปใหม่ concept-30 ควรมี

- หัวเรื่อง: **ระบบมีกี่ชั้น?**
- วงเล็บซ้ายครอบชั้น 1–3: **sabai-web**
- ① **หน้าเว็บ 17 หน้า** · ป้าย **จองคิว** **AI ผิว** **แชตบอต (ทุกหน้า)** **Wallet** · บรรทัดรอง **รันในเบราว์เซอร์**
- ② **API 22 path (24 endpoint รวม /api/test/*)**
- ③ **กฎร้าน (คิดที่ server): ราคา ส่วนลด แต้ม**
- วงเล็บซ้ายครอบชั้น 4: **sabai-db**
- ④ **PostgreSQL 16 · 14 ตาราง**
- ลูกศรลงระหว่างชั้น 1→2→3→4 (ไม่มีข้อความ)
- หุ่นยนต์: **Playwright ทดสอบหน้าเว็บ + เรียก API ตรง** ลูกศรชี้ทั้งชั้น 1 และชั้น 2
- ข้อความตกแต่ง: ไม่ใส่ (ลบ "สวย สบาย ด้วยเทคโนโลยี", "เล็ก แต่สวย ทำได้จริง", "เทคโนโลยีเพื่อความงามที่ยั่งยืน", "ระบบดี ชีวิตสบาย")
