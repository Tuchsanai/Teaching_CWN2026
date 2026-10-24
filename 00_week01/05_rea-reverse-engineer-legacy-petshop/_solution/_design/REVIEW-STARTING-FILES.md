# REVIEW-STARTING-FILES · ตรวจไฟล์ตั้งต้นฝั่งผู้เรียน บท 05 (งาน RS5 · 12 ต.ค. 2026)

> ขอบเขต: `petshop/HANDOVER-NOTES.md` `petshop/README.md` `petshop/docker-compose.yml` `TEST-DATA.md` `rea/README.md` `rea/*.mjs` `rea/rea.ps1` `rea/Dockerfile` `rea/scenario-coupon.json` `e2e-legacy/README-LEGACY.md` `.gitignore` · เทียบกับ `LESSON-PLAN.md` §0 §7 · `PREP-LOG.md` · `CR-DESIGN.md` · `STYLE-GUIDE.md` §3
> วิธีตรวจ: อ่านทุกไฟล์ทั้งไฟล์ + grep (`1,?049|PP-231|orders\.ts|recalc|recompute|FREE_SHIPPING_MIN|STANDARD_SHIPPING|gift|wrap|ห่อ|ค่าส่ง|ส่งฟรี|999|BUG-0|CR-0|toast|bug_?mode|ฝึก`) · ไม่ได้รัน server · ไม่แตะ `C:/t/work/run05` · ไม่ใช้ git ที่เปลี่ยนสถานะ

## 1. สรุป

| เรื่องที่ตรวจ | ผล |
|---|---|
| (1) เฉลยรั่ว BUG-01 / CR-01 / Quiz | ✅ **ไม่พบ** ในไฟล์ผู้เรียน คอมเมนต์ หรือ help text · คำว่า "ห่อ" ใน `rea-input.mjs`/`rea/README.md` = "ห่อผล REA เป็น input" (ไม่เกี่ยว CR-01) · `฿999`/"ส่งฟรี" มีเฉพาะใน `TEST-DATA.md` (= [D] ของร้าน ตั้งใจให้มี) และใน test เดิม `TC-CART-03` (นอกขอบเขต · ตามแผน D3) |
| (2) บันทึกส่งมอบสมจริง + ข้อเท็จจริงเก่า 2 ข้อ | ✅ ครบ 2 ข้อ ตรง §7.5-C ตามตัว · 9 บรรทัด · ไม่ถูกชี้ว่าเก่า (รายละเอียด §3) |
| (3) ภาษาไทย / น้ำเสียงบ้าน | ✅ โดยรวมดี · แก้ถ้อยคำเล็ก 2 จุดใน `README-LEGACY.md` |
| (4) พอร์ต 4000 · `pawpantry05` · `pawpantry05_default` · PowerShell | ✅ ตรงทุกไฟล์ · ไม่มี `localhost:3000` หรือ `host.docker.internal` ในไฟล์ผู้เรียน · `.ps1` เรียกผ่าน `-NoProfile -ExecutionPolicy Bypass` ทุกที่ |

## 2. รายการ (ไฟล์ · ข้อค้นพบ · แก้แล้ว?)

| # | ไฟล์ | ข้อค้นพบ | แก้แล้ว? |
|---|---|---|---|
| 1 | `e2e-legacy/README-LEGACY.md` บรรทัด 21 | "เว็บอื่น: `$env:BASE_URL="http://localhost:4000"`" ตัวอย่างชี้ค่าเดียวกับค่าเริ่มต้น จึงไม่ได้สอนอะไร · และ `$env:` ค้างทั้งหน้าต่าง PowerShell (รอบหลังจะยิงพอร์ตเดิมโดยไม่รู้ตัว) | ✅ เปลี่ยนเป็น `http://localhost:<พอร์ต>` + บอกค่าเริ่มต้น 4000 + `Remove-Item Env:BASE_URL` |
| 2 | `e2e-legacy/README-LEGACY.md` บรรทัด 22 | "(container ต้องตั้ง `ALLOW_TEST_RESET=1` ไว้แล้วใน compose)" ประโยคกำกวม ("ต้อง…ไว้แล้ว") | ✅ เป็น "(ใช้ได้เพราะ compose ตั้ง `ALLOW_TEST_RESET=1` ไว้ให้แล้ว)" ให้ตรงกับ `petshop/README.md` |
| 3 | `rea/record-har.mjs` บรรทัด 78 | ชื่อ step `"04 add to cart (x3 ให้ยอดถึงเงื่อนไขคูปอง)"` **ไม่จริง**: `PAW10` ไม่มียอดขั้นต่ำ (`lib/pricing.ts` · `TEST-DATA.md`) · agent ที่อ่าน repo ใน LAB 1 อาจจดลง `CODEBASE-MAP.md` ว่า "PAW10 มีขั้นต่ำ" = ปนเปื้อนแผนที่ · แต่ชื่อนี้ถูกพิมพ์ลง `har-steps.json`/console (เป็น output) และ §7.8 สั่ง "ตามตัว" | ❌ **ไม่แก้ (เปลี่ยน output)** · เสนอ: เปลี่ยนเป็น `"04 add to cart (x3)"` ทั้ง `rea/` และ `rea-probe/` แล้วเช็กว่า README/RESULT ไม่ได้อ้างชื่อ step เดิม |
| 4 | `TEST-DATA.md` บรรทัด 3 | "ข้อมูลชุดนี้คือ **สิ่งเดียวที่ทีมพัฒนาให้มา**" ขัดเรื่องเล่าบท 05 (มี repo + `HANDOVER-NOTES.md` + `e2e-legacy/` ด้วย) · §7 #6 บังคับ `cmp` เท่าบท 03 | ❌ **ไม่แก้ (ผิดแผน #6)** · เสนอ: ปล่อยไว้แล้วให้ README บท (🧭/📦) บอกว่า TEST-DATA เป็นเอกสารเก่าจากบท 03 หรือใช้เป็นตัวอย่างเพิ่มของ "เอกสารบอก ≠ ความจริง" · ถ้าจะแก้ ต้องแก้ตรวจรับ #6 ด้วย |
| 5 | `petshop/HANDOVER-NOTES.md` | ข้อเท็จจริงเก่า 2 ข้อมีครบและสมจริง (ดู §3) · ไม่มีคำ `ค่าส่ง ส่งฟรี shipping 999 PP-231 orders.ts` · "tracker เดิมปิดไปแล้ว" เข้ากับคอมเมนต์ `PP-231` ในโค้ดที่ตามต่อไม่ได้ | — (ไม่ต้องแก้) |
| 6 | `petshop/HANDOVER-NOTES.md` | (ทางเลือก) บันทึกจริงมักมีชื่อคน/วันที่ส่งมอบ เช่น `> ส่งมอบ ส.ค. 2026 · ทีม contractor เดิม` จะช่วยให้ "ใช้ได้ถึงสิ้นปี" มีปีอ้างอิง · แต่ §7.5-C สั่ง "ตามตัว" และ PREP ตรวจรับ 9 บรรทัดแล้ว | ❌ ไม่แก้ (ข้อเสนอ ไม่จำเป็น) |
| 7 | `petshop/README.md` | ตรง §7.5-B ตามตัว · `Invoke-RestMethod -Method Post http://localhost:4000/api/test/reset` ใช้ได้ใน PS 5.1 · ไม่มีคำว่า "ฝึก"/BUG_MODE | — |
| 8 | `petshop/docker-compose.yml` | ตรง §7.5-A: `name: pawpantry05` · `container_name: pawpantry05` · `image: pawpantry05:latest` · `"${WEB_PORT:-4000}:3000"` · service `petshop` (= DNS ใน `pawpantry05_default`) · ไม่มี BUG_MODE | — |
| 9 | `.gitignore` | ตรง §7.5-G ตามตัว · ไม่ ignore `.claude/` `CLAUDE.md` (ถูก · ผู้เรียนต้อง commit ใน LAB 1) | — |
| 10 | `rea/README.md` | ตรง §7.5-F · 15 บรรทัด · บอก `-Network pawpantry05_default` · เตือน `.har` มีรหัสผ่าน/cookie · ไม่มีเฉลย | — |
| 11 | `rea/rea.ps1` | หัวไฟล์ตรง §7.5-D · UTF-8 มี BOM (PS 5.1 อ่านไทยถูก) · ตัวอย่างใช้ `pawpantry05_default` และ `/work/...` · ไม่มี `host.docker.internal` | — |
| 12 | `rea/rea-input.mjs` | usage/ข้อความ error เป็นกลาง (trace/s2b/compare/view) · ไม่มี seed ตัวอย่างที่ชี้ BUG-01 | — |
| 13 | `rea/rea-summarize.mjs` | คอมเมนต์อธิบายกลไก REA เท่านั้น (เพดานผลลัพธ์ · `--sensitive-value` ลบ body) · ไม่มีชื่อไฟล์แอป/ตัวเลขเฉลย/`ev_` ฝังตายตัว | — |
| 14 | `rea/record-har.mjs` | ค่าเริ่มต้น `http://127.0.0.1:4000` + แปลง `localhost` อัตโนมัติ ต่างจาก §7.8 (`localhost:4000`) แต่ตรง D7 ("HAR ใช้ `127.0.0.1:4000`") และ PREP-LOG 3.2 อธิบายไว้ · คอมเมนต์อธิบายเหตุผล IPv6 ชัด · เส้นทางสั่งซื้อไม่ได้ทำยอด ฿999 | — (แจ้ง: §7.8 ควรแก้ให้ตรงไฟล์จริง) |
| 15 | `rea/scenario-coupon.json` · `rea/Dockerfile` | `start_url` = `http://petshop:3000/` · ไม่มีข้อความเฉลย · Dockerfile คอมเมนต์ไทยเป็นกลาง | — |
| 16 | `e2e-legacy/README-LEGACY.md` | ตัวเลข "ผลรันล่าสุด" 40 passed ~13 วินาที · 120 passed ~1 นาที ตรง PREP-LOG #7 (12.9 s · 58.2 s) · ไม่พูดถึง `tests/new/` (ถูก · เป็นเอกสารทีมเดิม) | — |
| 17 | บท 06 (นอกขอบเขต) | `06/e2e-legacy/README-LEGACY.md` บรรทัด 27 มีประโยค "เว็บอื่น: …localhost:4000" แบบเดียวกับข้อ 1 | ❌ ไม่แก้ (นอกขอบเขต RS5) · แจ้งผู้ตรวจบท 06 |

## 3. ข้อเท็จจริงเก่า 2 ข้อใน `HANDOVER-NOTES.md` (ตรวจกับโค้ด)

| บรรทัด | ข้อความในบันทึก | โค้ดจริง | สมจริง? | ชี้ว่าเก่าไหม |
|---|---|---|---|---|
| 5 | "ทุกหน้าดึงรายการสินค้าผ่าน `GET /api/products` ถ้าจะแก้ข้อมูลสินค้าให้ดูที่ API ก่อน" | `app/page.tsx` `app/products/page.tsx` เรียก `liveProducts()` จาก `lib/store` ตรง (server render) · `/api/products` ใช้แค่ `ShopProvider.tsx:262` (refresh สต็อกฝั่ง client) · ข้อมูลจริงอยู่ `lib/products.ts` | ✅ จริงครึ่งเดียว แบบที่คนเขียนจากความจำมักพลาด | ไม่ชี้ |
| 6 | "SUMMER20 ลด 20% ใช้ได้ถึงสิ้นปี" | `lib/pricing.ts:123` `case "SUMMER20": return fail(expired)` · `TEST-DATA.md` เขียน "หมดอายุ" | ✅ เคยจริงแล้วหมดอายุ · ไม่ระบุปี = สมจริง | ไม่ชี้ (แต่ขัดกับ `TEST-DATA.md` ตรง ๆ → ผู้เรียนจับได้จากเทียบเอกสาร 2 ฉบับ ไม่ต้องอ่านโค้ด · ยอมรับได้) |

ข้อที่เหลือในบันทึก (localStorage ของตะกร้า/รายการโปรด `pp-cart` `pp-wishlist` · คูปอง PAW10/FREESHIP/NEWCAT50 · suite ผ่านครบ · พอร์ต 4000) ตรงโค้ดจริง → มีเรื่องเก่าแค่ 2 ข้อตามแผน ไม่มีข้อที่ 3 โดยไม่ตั้งใจ
