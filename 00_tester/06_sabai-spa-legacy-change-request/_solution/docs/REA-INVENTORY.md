# REA-INVENTORY · สบายใจ สปา มองแบบ black-box (LAB 2)

> ขั้นนี้ไม่ได้เปิดโค้ดใน `web/` `db/` · ทุกข้อเท็จจริงมาจาก Evidence ของ REA (rea-lab:6.4.0) และไฟล์ใน `rea-out/` เท่านั้น
> ป้าย: **static** = เห็นในโค้ดที่ส่งถึงเบราว์เซอร์ (ไม่ได้รัน) · **runtime** = เห็นคำขอจริงตอนใช้งาน (HAR / scenario) · **inference** = อนุมานจากหลักฐานหลายก้อน ยังไม่ได้พิสูจน์ · **unknown** = หลักฐานนี้ไม่พอจะบอก
> `[E ev_xxxxxxxx]` = evidence_id 8 ตัวแรกของ Evidence ที่เห็นแถวนั้น

## 1. Evidence ที่ใช้ (ขนาด · เวลา · evidence_id)

| ก้อน | คำสั่ง REA | ไฟล์ | ขนาด | เวลา | evidence_id ย่อ |
|---|---|---|---|---|---|
| static bundle (`.next/static` 79 ไฟล์ 1.15 MB จาก `sabai06-web`) | `analyze-javascript-application` | `rea-out/static-v1.json` | 34,083,464 B (~33 MB) | 48.1 วิ | `ev_11d475e1` |
| สรุป static | `inspect-analysis-view` (summary) | `rea-out/summary-v1.json` | 16,686 B | 6.6 วิ | `ev_24390574` (parent = `ev_11d475e1`) |
| HAR เส้นทางใช้งานจริง | `record-har.mjs` (Playwright) | `rea-out/journeys.har` | 3,861,694 B (~3.7 MB) · 135 record | 10.1 วิ | — (ไฟล์ดิบ) |
| API จาก HAR | `inspect-web-network-capture` (10 record `/api/*`) | `rea-out/har-api.json` | 59,767 B | 2.1 วิ | `ev_6fbeaec6` |
| REA ขับเบราว์เซอร์ | `capture-browser-scenario` (network `sabai06-net`) | `rea-out/scenario.json` · `rea-out/scenario-final.png` | 247,833 B · 107,054 B | 3.5 วิ (scenario 1,590 ms) | `ev_8dc23d9f` |

statistics (static): relevant_files 54 · parsed_javascript_files 54 · parse_failures 0 · modules 346 · findings 950 · visited_ast_nodes 272,719 · text_bytes_read 884,586
coverage: application **partial** · semantic **partial (truncated)** · ทุก family partial (request 58 relations · data-flow 16,541 · call-flow 132) · limitations 14 ข้อหลัก + 7 ข้อรายไฟล์ (heap/ budget หมดที่ chunks framework, main, webpack, polyfills, 1255, 4bd1b696, `_buildManifest.js`) · REA ระบุเองว่า "Graph coverage is incomplete; unavailable facts remain explicit and must not be read as absence"

## 2. ตาราง endpoint

| endpoint | เห็นจาก static | เห็นจาก HAR / scenario (method · query · body keys · status) | ป้าย | แหล่ง |
|---|---|---|---|---|
| `/api/price` | fetch @ `app/book/page` | POST · — · type, serviceCode, people, date, time, therapists, contactName, contactPhone, redeemBlocks, useBirthday, giftCardCode, hotelCode, distanceKm, coursePurchaseId · 200 (2 ครั้ง) · scenario ก็ยิง POST | static + runtime | [E ev_11d475e1] [E ev_6fbeaec6] [E ev_8dc23d9f] |
| `/api/bookings` | fetch @ `app/book/page` | POST · — · คีย์เดียวกับ price + `quotedTotal` · **201** (1 ครั้ง · ได้ B14) | static + runtime | [E ev_11d475e1] [E ev_6fbeaec6] |
| `/api/auth/login` | fetch @ `app/login/page` | POST · — · body ถูก REA ปิดทั้งก้อน (มีค่า sensitive) · 200 (2 ครั้ง) · response `ok, user` + cookie `sabai_session` | static + runtime | [E ev_11d475e1] [E ev_6fbeaec6] |
| `/api/auth/logout` | fetch @ `app/layout` | POST · — · — · 200 (1 ครั้ง) | static + runtime | [E ev_11d475e1] [E ev_6fbeaec6] |
| `/api/slots` | route file เท่านั้น (ไม่อยู่ในรายการ fetch) | GET · service, date, type, people · — · 200 (1 ครั้ง) · scenario ก็ยิง `?service=S01&date=2026-10-12&type=single&people=1` | runtime (static ไม่เห็น call) | [E ev_6fbeaec6] [E ev_8dc23d9f] |
| `/api/bookings/{id}/cancel` | route file `bookings/[id]/cancel` เท่านั้น | POST · — · — · 200 (1 ครั้ง · B05 ยกเลิกแล้ว) | runtime (static ไม่เห็น call) | [E ev_6fbeaec6] |
| `/api/admin/bookings` | route file เท่านั้น | GET · date · — · 200 (2 ครั้ง) | runtime (static ไม่เห็น call) | [E ev_6fbeaec6] |
| `/api/test/reset` | fetch @ `app/admin/page` | ไม่อยู่ใน 10 record ที่เลือก (record-har เรียก reset ผ่าน API context ตอนเริ่ม · log `reset 200`) | static | [E ev_11d475e1] |
| `/api/chat` | fetch @ `app/chat/page` | ไม่เห็น | static | [E ev_11d475e1] |
| `/api/courses` | fetch @ `app/wallet/page` | ไม่เห็น | static | [E ev_11d475e1] |
| `/api/quiz` | fetch @ `app/quiz/page` | ไม่เห็น | static | [E ev_11d475e1] |
| `/api/giftcards` | fetch @ `app/giftcard/page` | ไม่เห็น | static | [E ev_11d475e1] |
| `/api/admin/bookings/[id]/complete` | route file เท่านั้น | ไม่เห็น | static (ชื่อไฟล์) · การใช้งาน unknown | [E ev_11d475e1] |
| `/api/giftcards/[code]` | route file เท่านั้น | ไม่เห็น | static (ชื่อไฟล์) · unknown | [E ev_11d475e1] |
| `/api/health` | route file เท่านั้น | ไม่เห็น | static (ชื่อไฟล์) · unknown | [E ev_11d475e1] |
| `/api/hotels` | route file เท่านั้น | ไม่เห็น | static (ชื่อไฟล์) · unknown | [E ev_11d475e1] |
| `/api/me` | route file เท่านั้น | ไม่เห็น (ทั้งที่ journey ล็อกอินแล้วเปิด /account) | static (ชื่อไฟล์) · unknown | [E ev_11d475e1] [E ev_6fbeaec6] |
| `/api/me/bookings` | route file เท่านั้น | ไม่เห็น (ทั้งที่ /account แสดง 8 นัด) | static (ชื่อไฟล์) · inference: หน้า account ได้ข้อมูลทางอื่น | [E ev_11d475e1] [E ev_6fbeaec6] |
| `/api/mood` | route file เท่านั้น | ไม่เห็น | static (ชื่อไฟล์) · unknown | [E ev_11d475e1] |
| `/api/photos/[id]` | route file เท่านั้น | ไม่เห็น | static (ชื่อไฟล์) · unknown | [E ev_11d475e1] |
| `/api/services` | route file เท่านั้น | ไม่เห็น (ทั้งที่ /services แสดงรายการบริการ) | static (ชื่อไฟล์) · inference: หน้า services ได้ข้อมูลทางอื่น | [E ev_11d475e1] [E ev_6fbeaec6] |
| `/api/test/today` | route file เท่านั้น | ไม่เห็น | static (ชื่อไฟล์) · unknown | [E ev_11d475e1] |
| `/api/therapists` | route file เท่านั้น | ไม่เห็น | static (ชื่อไฟล์) · unknown | [E ev_11d475e1] |
| `/api/transport` | route file เท่านั้น | ไม่เห็น | static (ชื่อไฟล์) · unknown | [E ev_11d475e1] |
| `/api/wallet` | route file เท่านั้น | ไม่เห็น | static (ชื่อไฟล์) · unknown | [E ev_11d475e1] |

รวม: fetch ที่ REA กู้ได้จาก static = **9** endpoint จริง (+ ค่าเศษ `[[...]]` `[]` `[...]` จาก `children.get` และ `/_next/image` 2 ครั้ง ใน `chunks/main` ซึ่งไม่ใช่ API ของร้าน) · ชื่อไฟล์ route `chunks/app/api/**/route-*.js` = **25** · HAR = **7 endpoint / 10 ครั้ง** (จาก 135 record) · scenario = 2 endpoint (`GET /api/slots` · `POST /api/price`)

## 3. หน้า (route) ที่เห็นจากชื่อไฟล์ใน bundle

| route | ไฟล์ใน `chunks/app/` | API ที่ static เห็นในไฟล์นั้น | เห็นตอน runtime |
|---|---|---|---|
| `/` | `page-2f4537628f4a6913.js` | — | — |
| `/services` | `services/page-…` | — | ✔ HAR + scenario |
| `/book` | `book/page-…` | `/api/price` `/api/bookings` | ✔ HAR + scenario (`?service=S01`) |
| `/login` | `login/page-…` | `/api/auth/login` | ✔ HAR (`?next=/account`) |
| `/account` | `account/page-…` | — | ✔ HAR (8 นัด · ยกเลิก B05) |
| `/admin` | `admin/page-…` | `/api/test/reset` | ✔ HAR (2 แถววันที่ 12 ต.ค.) |
| `/chat` | `chat/page-…` | `/api/chat` | — |
| `/giftcard` | `giftcard/page-…` | `/api/giftcards` | — |
| `/package` | `package/page-…` | — | — |
| `/quiz` | `quiz/page-…` | `/api/quiz` | — |
| `/skin` | `skin/page-…` | — | — |
| `/therapists` | `therapists/page-…` | — | — |
| `/transport` | `transport/page-…` | — | — |
| `/wallet` | `wallet/page-…` | `/api/courses` | — |
| (`_not-found`) | `_not-found/page-…` | — | — |
| (layout ร่วม) | `layout-a97cb37b93e372f4.js` | `/api/auth/logout` | ✔ HAR |

= **14 หน้า** + `_not-found` + layout ร่วม 1 ไฟล์ · ป้าย static ทั้งหมด [E ev_11d475e1]

## 4. สิ่งที่ REA ไม่เห็น

- **ไม่พบ `/api/slots` `/api/admin/bookings` `/api/bookings/{id}/cancel` ในรายการ fetch ของ static** ทั้งที่ HAR เห็นว่าถูกเรียกจริง เพราะ REA กู้เฉพาะ URL ที่เป็นค่าคงที่ในโค้ด (limitation: "Static paths and relationships may remain unresolved when expressions are dynamic") · URL ที่ต่อ query หรือแทรก id (เช่น template literal `/api/bookings/${id}/cancel`) จึงหลุด — เป็น inference ยังไม่ได้ยืนยันจากโค้ด
- **ไม่พบการเรียก `/api/me` `/api/me/bookings` `/api/services` ในหลักฐานนี้** ทั้งที่ journey เปิด `/account` (เห็น 8 นัด) และ `/services` (เห็นบริการ) · เป็นไปได้ว่าหน้าเหล่านี้ดึงข้อมูลฝั่งเซิร์ฟเวอร์ (render เสร็จก่อนส่งถึงเบราว์เซอร์) ซึ่ง HAR และ static ของเบราว์เซอร์มองไม่เห็น — inference ต้องยืนยันจากโค้ด
- **route อีก 13 ไฟล์ (`hotels` `therapists` `transport` `wallet` `mood` `photos/[id]` `giftcards/[code]` `test/today` `health` `admin/bookings/[id]/complete` ฯลฯ) ไม่พบผู้เรียกในหลักฐานนี้** เพราะ coverage ของ static เป็น partial (semantic truncated) และ HAR เดินแค่เส้นทางเดียว (บริการ → จอง → บัญชี → ยกเลิก → หลังร้าน) ไม่ได้แตะหน้าเหล่านั้น → ห้ามสรุปว่าไม่มีใครใช้
- **ไม่เห็นกฎธุรกิจฝั่งเซิร์ฟเวอร์** (คำนวณราคา ส่วนลด ช่วงเวลาว่าง การชนของนัด สิทธิ์ผู้ใช้) เพราะ static วิเคราะห์เฉพาะ bundle ฝั่งเบราว์เซอร์ และ HAR เห็นแค่ input/output ของ 10 ครั้ง
- **ไม่เห็น body ของ `/api/auth/login`** เพราะ REA ตัด `postData.text` ทิ้งทั้งก้อนเมื่อมีค่า `--sensitive-value` (ตั้งใจ) และไม่เก็บค่า cookie `sabai_session`
- **7 ไฟล์วิเคราะห์ไม่ครบ** (unknown 8 รายการจาก `endpoints`: polyfills ×2, framework, 4bd1b696, webpack, 1255, `_buildManifest.js`, main) เพราะ worker heap/budget หมด · ข้อเท็จจริงที่อยู่ในไฟล์เหล่านั้นอาจหายไป
- **ไม่เห็นฐานข้อมูล** (ตาราง ข้อมูล seed) และไม่เห็นว่าเว็บรันจริงด้วยเวอร์ชันไหนนอกจาก build id `jZbQKIWK8AqDc8R_yqfn0`
- REA ระบุเองว่า static "does not prove runtime execution" · scenario/HAR "receipt order does not prove causality"

## 5. คำถามที่ต้องไปหาคำตอบจากโค้ดหรือฐานข้อมูล

1. `/api/slots` `/api/bookings/{id}/cancel` `/api/admin/bookings` ถูกเรียกจากไฟล์ไหน และสร้าง URL แบบไหน (ทำไม static ไม่เห็น)
2. หน้า `/account` `/services` ได้ข้อมูลจากไหน — อ่าน DB ตรงฝั่งเซิร์ฟเวอร์ หรือเรียก `/api/me/bookings` `/api/services` จริง · ถ้าไม่มีใครเรียก route เหล่านี้ยังต้องเก็บไหม
3. `/api/price` คำนวณยอดอย่างไร (ราคาเต็ม × คน · ส่วนลด discountKind/discountPct · แต้ม · บัตรของขวัญ · ค่ารถตาม distanceKm/vehicles) และ `/api/bookings` ใช้สูตรเดียวกันหรือไม่ (`quotedTotal` ที่ส่งไปถูกตรวจกับยอดฝั่งเซิร์ฟเวอร์ไหม)
4. ช่องเวลาใน `/api/slots` (min/max/slots) มาจากตาราง/กฎอะไร · มีการกันนัดซ้ำ/ช่างชนกันตอน `POST /api/bookings` หรือไม่
5. กติกาการยกเลิก: ทำไม B06 ปุ่มยกเลิกถูกปิดแต่ B05 ยกเลิกได้ · ฝั่งเซิร์ฟเวอร์ตรวจเงื่อนไขเดียวกันหรือแค่หน้าเว็บ
6. `/api/test/reset` และ `/api/test/today` เปิดอยู่ในเวอร์ชันที่ส่งมอบ · ถูกป้องกันด้วยอะไร (env/สิทธิ์) และหน้า `/admin` ใครเข้าได้
7. `/api/admin/bookings/[id]/complete` `/api/mood` `/api/photos/[id]` `/api/test/today` ใช้ทำอะไร มีหน้าไหนเรียก
8. session `sabai_session` อายุ 7 วัน (expires 2026-10-19) · logout ทำให้ session เดิมใช้ไม่ได้ฝั่งเซิร์ฟเวอร์จริงไหม

## 6. ค่าที่ล็อกได้เป็น [E]

> [E] = "ระบบทำอยู่" ณ เวลาที่เก็บหลักฐาน · ใช้ล็อกพฤติกรรมเดิม (characterization) ได้ **แต่ไม่ใช่ "ควรทำ"** · ถ้าค่าใดผิดกฎธุรกิจ ต้องมี CR มาเปลี่ยน ไม่ใช่แก้เงียบ

| ค่า | ผลที่เห็น | แหล่ง |
|---|---|---|
| scenario นวดไทย 60 นาที (S01) · เดี่ยว · 1 คน · 12 ต.ค. 2026 15:00–16:00 | 12/12 step `completed` · หน้าสรุป "ยอดสุทธิ: ฿1,000" (`summary-amount-total` data-amount="1000") · ราคาเต็ม ฿1,000 × 1 · ชำระที่ร้าน ฿1,000 | [E ev_8dc23d9f] |
| ยอด quote ใน HAR journey (หลัง reset now 2026-10-10 10:00) | "ยอดสุทธิ: ฿1,000" | [E ev_6fbeaec6] |
| `GET /api/slots` | 200 · query service, date, type, people · keys date, service, durationMin, min, max, slots | [E ev_6fbeaec6] |
| `POST /api/price` | 200 · response 30 คีย์ (service … total, totalLabel, giftcardPaid, otherPaid, pointsToEarn, lines, birthdayAvailable, maxRedeemBlocks, pointsBalance, loggedIn, course, giftCard, giftCardError) | [E ev_6fbeaec6] |
| `POST /api/bookings` | **201** · keys bookingId, code, status, total, totalLabel, therapists, therapistNames, message, detail, quote · ได้รหัส B14 | [E ev_6fbeaec6] |
| `POST /api/auth/login` | 200 · keys ok, user · ตั้ง cookie `sabai_session` httpOnly อายุ 7 วัน | [E ev_6fbeaec6] |
| `POST /api/bookings/{id}/cancel` | 200 · keys ok, bookingId, code, status · B05 → "ยกเลิกแล้ว" | [E ev_6fbeaec6] |
| `POST /api/auth/logout` | 200 · keys ok | [E ev_6fbeaec6] |
| `GET /api/admin/bookings?date=` | 200 · keys date, today, bookings · วันที่ 12 ต.ค. มี 2 แถว | [E ev_6fbeaec6] |

## 7. สรุป

| แหล่ง | endpoint ที่เห็น | เวลา | coverage | evidence_id ย่อ |
|---|---|---|---|---|
| static bundle | fetch 9 (+ เศษ 3 + `/_next/image`) · route file 25 · หน้า 14 | 48.1 วิ + summary 6.6 วิ | partial (semantic truncated · unknown 8) | `ev_11d475e1` / `ev_24390574` |
| HAR (record-har + inspect) | 7 endpoint / 10 ครั้ง | 10.1 วิ + 2.1 วิ | เฉพาะเส้นทางที่ record-har เดิน · runtime_attribution unknown | `ev_6fbeaec6` |
| REA scenario | 2 (`GET /api/slots` · `POST /api/price`) · 12/12 step · ฿1,000 | 3.5 วิ (1,590 ms) | complete (equality_eligible) | `ev_8dc23d9f` |
