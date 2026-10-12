# IMAGES-REVIEW-05 · ตรวจภาพประกอบบท 05

> ผู้ตรวจ VI5 · 12 ต.ค. 2026 · ภาพใหม่ 18 ภาพ (`C:/t/orch/q05.json`, IMG S5_0–S5_17 จบครบ exit=0) + ภาพแนวคิดเดิม 9 ภาพ (T1–T9) + ไดอะแกรม PNG 3 ภาพ
> เกณฑ์: (1) ข้อความไทยตรงตามพรอมต์ทุกตัวอักษร/วรรณยุกต์ มีหัวเรื่อง ไม่มีตัวอักษรเพี้ยน (2) ตัวละครตรงสไตล์ (เด็กชายผมน้ำตาลยุ่ง ฮู้ดสีน้ำเงิน · หุ่นยนต์กลมสีขาว จอดำ ตาฟ้า เสาอากาศลูกบอลฟ้า ไม่มีโลโก้/ตราบนตัว · แมวส้ม + ลูกหมาน้ำตาล · ร้าน PawPantry) (3) ไม่เฉลย BUG-01 (ยอด ฿1,049 · ไฟล์ `lib/orders.ts` · สาเหตุ) และคำตอบใน `CR-DESIGN.md` (4) ขนาด ≤ 400 KB
> วิธีแก้ข้อความ: เรนเดอร์ข้อความด้วย headless Chromium (ฟอนต์ Leelawadee UI / Segoe UI ตัวหนา, สีพื้นตรงกับป้าย) แล้ววางทับ · ไม่วาดอักษรไทยด้วย PIL · ตรวจซ้ำด้วยการครอปขยาย · ต้นฉบับก่อนแก้เก็บไว้ที่ `C:/t/work/vi5/*.orig.*`

## สรุป

| ผล | จำนวน |
|---|---|
| OK | 27 (ใหม่ 16 · เดิม 9 · ไดอะแกรม 2) |
| fixed-overlay | 2 (`concept-07`, `concept-24`) |
| re-rendered | 1 (`rea-architecture.png`) |
| regenerate | 0 |

ทุกไฟล์ใน `img/` ≤ 400 KB (ใหญ่สุด `rea-architecture.png` 345 KB)

## ภาพใหม่ 18 ภาพ

| ไฟล์ | ผล | ประเด็น | พรอมต์ใหม่ (ถ้าต้องสร้างใหม่) |
|---|---|---|---|
| intro-01-legacy-handover.jpg | OK | หัวเรื่อง "รับช่วงระบบเดิม" + บับเบิล "เอกสารแค่นี้เหรอ?" ถูกต้อง · แมวอยู่ข้างแล็ปท็อปแทนที่จะนั่งบนเครื่อง (เล็กน้อย) · จุดดำที่อกหุ่นคือมือที่ประสานกัน ไม่ใช่โลโก้ | – |
| intro-02-understand-lock-change-prove.jpg | OK | หัวเรื่องและป้าย 4 ก้อน เข้าใจ/ล็อก/แก้/พิสูจน์ ถูกต้องครบ | – |
| concept-02-static-vs-dynamic.jpg | OK | "static: ดูไม่ต้องรัน", "runtime: ดูตอนรันจริง", "เห็นคนละอย่าง" ถูกต้อง · มีป้ายอังกฤษตกแต่งเกินพรอมต์ (ไม่กระทบ) | – |
| concept-04-rea-or-read.jpg | OK | "อ่าน repo เลย", "ใช้ REA ส่อง", "source ครบ" ถูกต้อง · เด็กชี้ซ้าย | – |
| concept-07-content-digest.jpg | fixed-overlay | **เฉลยรั่ว:** ป้ายกล่องทั้งสองเขียน `orders.ts` = ชื่อไฟล์ต้นเหตุ BUG-01 → วางทับเป็น `page.js` ทั้งสองกล่อง (ความหมาย "ชื่อเดียวกัน ลายนิ้วมือต่าง" ยังอยู่) · ข้อความอื่นถูกต้อง · **หมายเหตุ:** พรอมต์ใน `q05.json` ยังมี "orders.ts" ถ้าจะสร้างใหม่ต้องเปลี่ยนเป็น "page.js" | – |
| concept-11-obligation-ledger.jpg | OK | เจ้าของ/กรณีทดสอบ/ผลตรวจ/unknown ถูกต้อง | – |
| concept-15-characterization-lock.jpg | OK | "พฤติกรรมเดิม", ไม้บรรทัด "[D] ร้าน", บับเบิล "ล็อก ≠ ถูก" ถูกต้อง · มีเต่าทองบนชั้น | – |
| concept-14-rea-limits.jpg | OK | "ร้านอยากได้อะไร?", "บอกไม่ได้", ห้อง "server" ล็อก ถูกต้อง | – |
| concept-17-reserved-ports.jpg | OK | "Windows จองแล้ว" บนช่อง 3000–3002, รถเข้าช่อง 4000 ตรงกับ D5 | – |
| concept-18-agent-reads-repo.jpg | OK | "CODEBASE-MAP", "ไฟล์:บรรทัด", "เดา?" ถูกต้อง · เล็กน้อย: ชื่อไฟล์บนสันหนังสือ/หมุดเป็น `.py` (main.py, app.py:120 ฯลฯ) ขณะที่ PawPantry เป็น Next.js/TypeScript — ไม่เฉลยอะไร ใช้สอนได้ ถ้าอยากให้ตรงขึ้นค่อยสร้างใหม่ด้วยพรอมต์ทางขวา (ไม่บังคับ) | (ไม่บังคับ) ...เหมือนเดิม แต่: "book spines labelled `page.tsx`, `route.ts`, `Header.tsx`, `layout.tsx`; each map pin has a tag `ไฟล์:บรรทัด` with a TypeScript file name such as `page.tsx:42`; code sheets show TypeScript/JSX, not Python; do NOT show `orders.ts` or any `lib/` file" |
| concept-16-legacy-safety-net.jpg | OK | "ชุดเทสต์เดิม เขียวหมด", "test ใหม่", ตาข่ายมีรู ถูกต้อง | – |
| concept-19-customer-ticket.jpg | OK | ใบเสร็จ "฿ ?" กับหน้าจอ "รวมทั้งหมด ฿ ?!" — **ไม่มีตัวเลขจริง** ไม่เฉลย ฿1,049 · ลูกค้าผมบ๊อบเสื้อคาร์ดิแกนเหลือง ตรงพรอมต์ | – |
| concept-20-root-vs-symptom.jpg | OK | "แก้ที่ต้นเหตุ" ✓ / "แก้ปลายเหตุ" ขีดฆ่า ✗ ถูกต้อง · ภาพเป็นนามธรรม ไม่ชี้ไฟล์/สาเหตุ | – |
| concept-21-ask-before-build.jpg | OK | "ก่อนหรือหลังลด?" ถูกต้อง · เจ้าของร้านผ้ากันเปื้อนมีป้ายชื่ออุ้งเท้าแมว · ไม่มีตัวเลขเงื่อนไข CR | – |
| concept-22-red-then-green.jpg | OK | "แดง: ยังไม่มีฟีเจอร์", "เขียว" ถูกต้อง · ไอคอนเบราว์เซอร์เป็นวงกลมสี ไม่มีโลโก้ · ตัวละครซ้ำซ้าย/ขวาเป็นการเล่าก่อน–หลัง ยอมรับได้ | – |
| concept-23-change-proof.jpg | OK | "ตั้งใจแก้", "hash ต่าง", "bundle ต่าง", ตรายาง "ส่งมอบได้" ถูกต้อง (ตรวจครอปแล้ว) | – |
| concept-24-solo-loop.jpg | fixed-overlay | หัวเรื่องสะกดผิด "ครบวงจ**ด**้วยตัวเอง" (ขาด ร) → วางทับเป็น "ครบวงจรด้วยตัวเอง" (ครอบทั้งวรรณยุกต์บน ไม่มีเศษเดิมเหลือ) · ธง "ฝึกเดี่ยว" ถูกต้อง | – |
| outro-01-handover-next.jpg | OK | "CHANGE-REPORT", แฟ้ม "HANDOVER" หนาเป็นระเบียบ, ป้าย "บท 06 →" ถูกต้อง · มีป้าย "สปาไทย" เกินพรอมต์ (สะกดถูก ไม่กระทบ) | – |

## ภาพแนวคิดเดิม 9 ภาพ (T1–T9)

| ไฟล์ | ผล | ประเด็น |
|---|---|---|
| concept-01-reverse-engineering.jpg (T1) | OK | หัวเรื่อง + Forward/Reverse + การ์ด หน้าเว็บ/API/โมดูล/กฎธุรกิจ ถูกต้อง · ป้ายไทยตกแต่งเกินพรอมต์ 2 ป้าย สะกดถูก (ตรวจครอปแล้ว) |
| concept-03-black-white-grey-box.jpg (T2) | OK | ป้าย Grey-box ถูกวางทับไว้แล้วรอบก่อน ข้อความถูก · ตัวละครซ้ำตามฉาก 3 กล่อง |
| concept-05-evidence-not-opinion.jpg (T3) | OK | SHA-256 + แท็ก 4 สี, "น่าจะ..." ✗, "ไม่เจอ ≠ ไม่มี" ถูกต้อง |
| concept-06-missing-not-absent.jpg (T4) | OK | `/api/products` `/api/orders` ในแสง, `/api/recommendations` + a b c ในเงา, ป้าย "หาไม่เจอ ≠ ไม่มี" ถูกต้อง |
| concept-08-version-compare.jpg (T6) | OK | v1/v2, เหมือนเดิม/เปลี่ยน/ไม่รู้, "ต้องทดสอบซ้ำ" ถูกต้อง |
| concept-09-feature-trace.jpg (T5) | OK | สถานี chunk/endpoint/localStorage/หน้าตะกร้า + `/api/coupons/validate` + "seed → trace" ถูกต้อง (คูปองเป็นเรื่องบท 03 ไม่เกี่ยว BUG-01) |
| concept-10-passive-driven-har.jpg (T7) | OK | 3 แผง Passive/Driven/HAR + กล่อง "ความลับ" ถูกต้อง |
| concept-12-evidence-badge-e.jpg (T8) | OK | ป้าย [D]/[R]/[E]/[A]/[O], ตาชั่ง ควรทำ/ทำอยู่, "ผลที่คาดหวัง" ถูกต้อง |
| concept-13-ethics-permission.jpg (T9) | OK | ระบบของเรา/ระบบคนอื่น, "ต้องได้รับอนุญาต", "password / cookie" ถูกต้อง |

## ไดอะแกรม PNG

| ไฟล์ | ผล | ประเด็น |
|---|---|---|
| rea-architecture.png | re-rendered | แก้ `diagrams/rea-architecture.html`: `localhost:3000` → `localhost:4000` (เบราว์เซอร์ / Playwright บนเครื่อง) + เพิ่ม `http://petshop:3000` (REA ใน container ผ่าน network `pawpantry05_default`, ตาม D7) · ตัด provider `inspect-web-page` (ไม่ได้ทดสอบ) เหลือ 3 ตัว (HAR reader ขยายเต็มแถว) · เรนเดอร์ด้วย `tools/render-png.mjs` → 2560×2016 · 345 KB · อัปเดตตาราง + alt text ใน `IMAGES-NOTES.md` แล้ว |
| re-taxonomy.png | OK | ไม่มี 3000 / inspect-web-page ใน HTML ต้นทาง |
| three-eyes.png | OK | ไม่มี 3000 / inspect-web-page ใน HTML ต้นทาง |

## ตรวจการเฉลยรั่ว (ทั้ง 30 ภาพ)

- ไม่มีภาพใดแสดง ฿1,049 / ฿999 / ฿50 / `>` vs `>=` / `lib/orders.ts` (หลังแก้ concept-07)
- concept-19 ใช้ "฿ ?" และ "฿ ?!" เท่านั้น · concept-20 เป็นภาพวัชพืชนามธรรม · concept-21/22 แสดงกล่องของขวัญแต่ไม่มีราคา/เงื่อนไขของ CR-01
