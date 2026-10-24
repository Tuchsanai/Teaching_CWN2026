# PROMPT-FIX-LOG · บท 05 (หลัง RUN05 · 12 ต.ค. 2026)

ที่มา: `C:/t/orch/PROMPT-FIXES-05.md` + หัวข้อ "ข้อเสนอแก้พรอมต์" ใน `results/LAB*_RESULT.md` (RUN05) · **ไม่ได้รัน LAB ซ้ำ** · helper ทดสอบกับผลจริงของ RUN05 ใน `C:/t/work/run05/w/out/` (อ่านอย่างเดียว · รันจาก `w/` เพื่อให้ `/work/...` ชี้ถูก) และทดสอบ `rea.ps1` ในโฟลเดอร์ scratch แยก (สำเนา `out/v1/.next/static` + HAR)

ไฟล์ที่แก้: `PROMPTS.md` · `README-PART-B.md` (บล็อก ```text ทั้ง 12 บล็อกที่เปลี่ยน คัดจาก PROMPTS.md ด้วยสคริปต์ · ตรวจแล้ว byte-identical 13/13 บล็อก) · `fast_track/README.md` (🅰️ และ 🅱️ แก้ชุดเดียวกัน) · `rea/rea-summarize.mjs` · `rea/rea.ps1` · `rea/README.md`

## 1. แก้ helper (แล้วทำให้พรอมต์สั้นลง)

| ข้อเสนอ (ระดับ · LAB) | แก้อะไร | ผลทดสอบกับผลจริง RUN05 |
|---|---|---|
| M · LAB 2 · progress ของ REA ท่วม context (~490 บรรทัด stderr) | `rea.ps1`: ทุกโหมด (ยกเว้น `-Mcp`) รันผ่าน `sh -c` · stdout → fd 3 (ไฟล์ `-Out` หรือหน้าจอ) · stderr ผ่าน `grep --line-buffered -v rea_progress` · exit code ของ REA เก็บใน `/tmp/rc` · สวิตช์ใหม่ `-Progress` = เห็น progress ตามเดิม · `mkdir` ล้มแล้ว `exit 1` | analyze static `-Out`: exit 0 · 39 s · **stderr 0 บรรทัด** · ไฟล์ 54,410,173 B ไบต์แรก `{` (ไม่มี BOM) · `-Progress`: stderr 34 บรรทัด (ทั้งหมดเป็น rea_progress) · `doctor --filter-output healthy,checks`: exit 1 · stdout 29 บรรทัด **เท่ากับ rea.ps1 เดิมทุกไบต์** · HAR ไม่มีไฟล์: exit 1 · JSON error ใน `-Out` **เท่ากับของเดิม** · คำสั่งผิด: exit 1 + `COMMAND_NOT_FOUND` · จำลอง stderr ปน: บรรทัด `rea_progress` หาย · `real-error` ยังออก stderr · exit 3 ส่งต่อครบ |
| M · LAB 9 · HAR แสดงแค่ key ชั้นบน (`order, id`) มองไม่เห็น `giftWrap` | `rea-summarize.mjs` โหมด HAR: key 2 ชั้น `order{…}` · array of object = `items[]{…}` · หัวตาราง `--md` มี evidence_id_short · records · API | `out\after\har.json` → response `order{id,userId,items,subtotal,discount,shipping,giftWrap,giftWrapFee,total,…}, id` · request `…, address{name,phone,address,province,postcode}, giftWrap` · `out\har.json` (ก่อน CR) ไม่มี giftWrap → เห็นความต่างทันที |
| M · LAB 3 · ขอ "ค่าตัวอย่าง" แต่ตัวย่อไม่แสดงค่า | ตัวเลือกใหม่ `--samples` (HAR + scenario): body ย่อ (array เหลือตัวแรก + `…(+N)` · string > 60 ตัวตัด · ทั้งก้อน ≤ 400 ตัว · อีเมลแทนด้วย `<อีเมล>` · body ที่ REA ปิดยังเป็น `(redacted)`) | `out\har.json --md --samples`: coupon `{"code":"PAW10","items":[{"slug":"lickable-salmon-treat","size":"4 ซอง","qty":3}]}` → `discount 20` · order → `subtotal 207 · discount 20 · shipping 50 · total 237` · login `(redacted)` ทั้ง 2 ฝั่ง |
| m · LAB 3 · a11y เก็บ `฿113` แต่ทิ้งป้าย "ยอดชำระทั้งหมด" | scenario: รวมคู่ `term:` + `definition:` เป็น `ป้าย = ค่า` ก่อนกรอง · ตาราง API ของ scenario มี key 2 ชั้น | `out\scenario.json --md`: `ยอดรวมสินค้า = ฿69` · `ส่วนลด PAW10 = -฿6` · `ค่าจัดส่ง = ฿50` · `ยอดชำระทั้งหมด = ฿113` |
| M · LAB 2 · ไม่บอกไฟล์ของ node `electron-renderer` และ HTTP method ของ endpoint | analyze: ตาราง/ฟิลด์ `electron_renderer` (ไฟล์ HTML · mechanism · จำนวน script) · คอลัมน์ `method (helper อ่าน bundle)` = เปิดไฟล์ bundle ตรงช่วงที่ REA ชี้ (บรรทัดเริ่ม 1 คอลัมน์เริ่ม 0 · ยืนยันด้วยการตัดข้อความจริง) หา `method:"…"` · fetch ไม่ระบุ = GET · ไม่มีไฟล์บนเครื่อง = `-` (REA เองไม่บันทึก method: endpoint props มีแค่ `endpoint_kind value mechanism`) | static: `/api/auth/login|logout|register` `/api/coupons/validate` `/api/orders` = POST · `/api/products` = GET · `a b c` = `-` · server: 6 endpoint `/api/*` (ทุกตัวมาจาก file node) method ตรงกับ static · electron-renderer 2 ตัว = `pages/500.html` (html-script-reference · 8 script) และ `app/_global-error.html` (html-script-entrypoint · 8) |
| regression ของโหมดอื่น | — | `trace-coupon` `s2b-v1src-v2build` `cmp` `v1-src` (`--md`) และ `--s2b-table` 4 ไฟล์: **ผลเท่ากับตัวย่อเดิมทุกไบต์** · `--png` ยังเขียนภาพได้ (182,349 B) · รันเร็ว (<0.1 s ต่อ HAR) |

ทำให้พรอมต์ง่ายลง: ไม่ต้องใส่ `2>$null` ในคำสั่ง REA · LAB 2 ขอ method/electron-renderer จากตัวย่อได้ตรง ๆ · LAB 3 ใช้ `--samples` แทนการให้ agent เขียนสคริปต์อ่าน HAR เอง · LAB 9 ส่วน 2 เห็น key ที่เพิ่มด้วยตัวย่ออย่างเดียว

## 2. แก้พรอมต์ (PROMPTS.md → README-PART-B.md ตรงตัว)

| LAB | ระดับ | ข้อเสนอ | แก้ที่ไหน |
|---|---|---|---|
| 0 | M | doctor ให้ผลสั้น | ข้อ 3 → `rea.ps1 doctor --filter-output healthy,checks` · 🎯 ~30 บรรทัด (ไม่กรอง ~2,800) |
| 0 | M | ExecutionPolicy RemoteSigned / Process=Bypass ปกติ | 🎯 LAB 0 · README-B 👀 LAB 0 |
| 0 | m | ห้าม `Get-Content \| Set-Content` กับ JSON ไทย · `Invoke-RestMethod` ทำชื่อไทยเพี้ยน | PROMPTS ตาราง "ถ้าเจอปัญหา" · FT กติกาข้อ 4 · LAB 4/7 พรอมต์ (อ่าน API ด้วย node fetch) |
| 0 | m | compose ครั้งที่ 2 ใช้ cache | ข้อ 4 "(ครั้งแรกนาน ~3 นาที · ครั้งต่อไป…)" · LAB 6/8/10 "นาน 1–3 นาที" · 🎯 + README-B 👀 |
| 1 | M | ตรวจรั้ว deny เป็น 2 ข้อความแยก | ✔️ LAB 1 (PROMPTS + README-B) พร้อมข้อความที่ใช้และบอกว่าข้อความปฏิเสธพูดว่า "directory" |
| 1 | DECISION | white-box เจอ PP-231 ตั้งแต่ LAB 1 = คงไว้ | บรรทัดท้ายพรอมต์ "เจอโค้ดน่าบั๊ก → สมมติฐานใน ยังไม่รู้" · 👀 PROMPTS + README-B "พบโค้ดน่าสงสัย ≠ หลักฐาน" · FT กติกาข้อ 8 (ทั้ง 2 แบบ) |
| 1 | m | path ของ deny rule | ข้อ 6 "relative เช่น `Edit(e2e-legacy/tests/*.ts)` · ห้าม `**` `//`" · FT ขั้น 1 |
| 1 | m / note | อ่านไฟล์ด้วยเครื่องมืออ่าน/Git Bash ได้ | วงเล็บต้นพรอมต์ LAB 1 · README-B 👀 LAB 0 · PROMPTS ตาราง "ถ้าเจอปัญหา" |
| 2 | M | `2>$null` | แก้ที่ `rea.ps1` (ข้อ 1 ตารางบน) · 🎯 LAB 2 บันทึกว่าไม่ขึ้นแล้ว |
| 2 | M | นิยาม ✅/⚠️/❓ · route.ts จาก source map | ข้อ 5 (นิยาม 3 ป้าย · ชื่อไฟล์อย่างเดียว = ❓ + กำกับ "เห็นชื่อไฟล์") · FT ขั้น 2 |
| 2 | M | electron-renderer + method | helper (ข้อ 1) · ข้อ 2 ขอ `--md` + method + ที่มา + ไฟล์ของ electron-renderer · 🎯 ผลจริง · README-B 👀 (method ไม่ใช่ผลของ REA) |
| 2 | m | grep = grey · HEALTHCHECK = black | ข้อ 5 นิยามตา · FT ขั้น 2 |
| 2 | m | อ้างแนวทาง REA จากไหน | ข้อ 6 (3) → README ของบท หัวข้อ 🎓 "ใช้ REA เมื่อไร เมื่อไรอ่าน repo เฉย ๆ" |
| 2 | m | robocopy exit 1 | ข้อ 1 "เครื่องมืออาจแสดง exit 1 เป็น error ไม่ต้องรันซ้ำ" |
| RFT5 | — | 🎯 LAB 2 ใส่เรื่อง file node | 🎯 LAB 2 (endpoint `/api/*` ของ server ทั้ง 6 มาจาก file node) · ข้อ 2 อธิบายคอลัมน์ "ที่มา" |
| 3 | M | ค่าตัวอย่าง | helper `--samples` · ข้อ 2/3/4 ใช้ `--md --samples` · FT ขั้น 3 |
| 3 | M | รหัส demo อยู่ในคำสั่ง | ข้อ 2 "ถ้าคัดคำสั่งลงเอกสาร เขียน `<รหัส demo>` `<อีเมล demo>`" · README-B 👀 LAB 3 · FT ขั้น 3 |
| 3 | m | ป้าย a11y | helper (คู่ term/definition) · ข้อ 3 บอกรูป "ป้าย = ค่า" · 🎯 |
| 4 | M | สต็อกร่วม 3 เบราว์เซอร์ | ข้อ 3 bullet "สต็อกเป็นของร่วม" · README-B 👀 · FT กติกาข้อ 9 (ใหม่ ทั้ง 2 แบบ) + ขั้น 4 |
| 4 | M | นับ expected-fail | บรรทัดท้ายพรอมต์ (Playwright นับรวมใน passed) · README-B 👀 · FT ขั้น 4 |
| 4 | m | `place-order` · หน้าคำสั่งซื้อ `/orders/PP-…` · NEWCAT50 ไม่มี ฿500 พอดี · อ่าน API ด้วย node | ข้อ 3 |
| 4 | NOTE | characterization + [D] เจอ S1 เอง | 🎯 ผลจริง + 👀 PROMPTS · README-B 👀 "เจอจุดขัดก่อนลูกค้าแจ้ง = test.fail KNOWN-ISSUE ไม่ใช่แก้ทันที" |
| 5 | M | HAR ที่ `127.0.0.1:4000` | ขั้นที่ 1 (เหตุผล: REA ไม่รับ HAR ที่อัดผ่าน localhost) · FT มีอยู่แล้ว |
| 5 | M | HAR 40 MB | ขั้นที่ 1 `recordHar: { path, urlFilter: /\/api\// }` · README-B 👀 · FT ขั้น 5 |
| 5 | m | ที่วาง BUG-01.md | บรรทัดแรก "ที่โฟลเดอร์บท" |
| 5 | m | [D] ไม่พอที่ PAW10 ฿999 | ขั้นที่ 1 ใช้ oracle [R] "ปุ่ม = คำสั่งซื้อ" + จดใน ยังไม่รู้ · ขั้นที่ 2 รับ [D] หรือ [R] · README-B 👀 · FT ขั้น 5 |
| 5 | m | ชามกินช้าสต็อก 18 | ขั้นที่ 1 reset ก่อนรันทุกรอบ · FT ขั้น 5 |
| 5 | m / DECISION | black-box ต้องหาหลักฐานใหม่ | บรรทัดใหม่ "BASELINE/CODEBASE-MAP มีผู้ต้องสงสัย = สมมติฐาน · ต้องได้หลักฐานใหม่" · 👀 PROMPTS + README-B |
| 6 | M | เก็บหลักฐานก่อนแก้ | ข้อ 5 `out\bug01-before-fix\` · 👀 PROMPTS + README-B · FT ขั้น 6 |
| 6 | m | เวลา build · เปลี่ยน tag ของ test คู่ | ข้อ 2 "1–3 นาที" · ข้อ 3 "ทั้งค่าและ tag/annotation" · README-B 👀 · FT ขั้น 6 |
| 7 | M | giftWrap ผิดชนิด ตรวจอะไร | ข้อ 3 "ตรวจทั้งยอดและ field giftWrap=false · giftWrapFee=0" · 🎯 ปรับ (ข้อนี้แดงก่อนมีฟีเจอร์) · README-B 👀 · FT ขั้น 7 |
| 7 | M | timeout สั้น | ข้อ 4 `test.use({ actionTimeout: 3_000 })` + `expect.configure({ timeout: 3_000 })` · ห้ามแก้ config · FT ขั้น 7 |
| 7 | (H จาก LAB 8) | กติกาสต็อก × 3 เบราว์เซอร์ | ข้อ 3 · 🎯 ⚠️ RUN05 · README-B 👀 · FT กติกาข้อ 9 + ขั้น 7 |
| 7 | m | ตะกร้าที่มีจริง · Invoke-RestMethod | ข้อ 1 · วงเล็บต้นพรอมต์ |
| 7 | RUNNER | runner เห็น 🎯 ก่อนคำนวณ | **ไม่แก้ในบทนี้** (เป็นเรื่องของ `RUNNER.md` ไม่ใช่พรอมต์ผู้เรียน) |
| 8 | **H** | `test:all` รอบเดียวล้ม 46/231 เพราะสต็อกหมด | ต้นทาง: กติกาสต็อกใน LAB 4/7 · ข้อ 4 LAB 8 "409 / qty-plus = ข้อมูลทดสอบหมด → รันทีละเบราว์เซอร์ `--project=` · ห้ามแก้ตะกร้า/config" · ✔️ ยอมรับผลรายเบราว์เซอร์ · 🎯 ผลจริง · 👀 test data isolation (PROMPTS + README-B) · FT กติกาข้อ 9 + ขั้น 8 + ตาราง 🆘 · PROMPTS ตาราง "ถ้าเจอปัญหา" |
| 8 | m | diff `lib/orders.ts` รวม BUG-01 | ข้อ 7 "ให้แยกบอก" · FT ขั้น 8 |
| 8 | m | `--reporter=list` | **ไม่ใส่**: config มี reporter `list` อยู่แล้ว และ `npm run … -- --flag` ใน PowerShell 5.1 เสี่ยงโดน `--` ถูกกิน |
| 9 | M~H | `Get-FileHash` ไม่มี `-LiteralPath` นับได้ 5 แทน 6 | ข้อ 1 `-LiteralPath` + เทียบ `git status --short petshop` · 🎯 + 👀 PROMPTS · README-B 👀 · FT ขั้น 9 |
| 9 | M | import-reference-source ไม่มี evidence_id | บรรทัด CHANGE-PROOF → ใช้ `root_sha256_short` · FT ขั้น 9 |
| 9 | M | key ซ้อนใน HAR | helper (ข้อ 1) · ส่วน 2 ข้อ 2 บอกว่าตัวย่อแสดง 2 ชั้น · 🎯 · FT ขั้น 9 |
| 9 | m | หลักฐาน obligation ใช้ผลเดิมได้ · `--s2b-table` แสดงแค่แถวที่ต่าง | ข้อ 5 · ข้อ 3 · FT ขั้น 9 |
| 10 | M | `test:all` 409 | ข้อ 3 · ✔️ · 🎯 · 👀 PROMPTS + README-B |
| 10 | M | "เพิ่มแถว" กับตารางแนวตั้ง | ข้อ 4 "เพิ่ม PR-1 ในตารางสรุป (แถวหรือคอลัมน์ตามรูปแบบเดิม)" · ✔️ · README-B 👀 |
| 10 | m | ชนิดของแจ้งเตือน · สต็อกน้อย · toast flaky | ข้อ 1 (ข้อความและชนิดแจ้งเตือนต้องมี [D]/[R] · reset ก่อนทำซ้ำ) · 🎯 (toast ~2.8 วิ) |

## 3. ตรวจหลังแก้

- บล็อก ```text ของ `PROMPTS.md` 13 บล็อก = บล็อก 0–12 ของ `README-PART-B.md` ทุกไบต์ (สคริปต์ดึงบล็อกด้วย regex แล้วเทียบ bytes · 12 บล็อกเปลี่ยน · บล็อก MCP ไม่เปลี่ยน)
- `fast_track/README.md`: ทุกการแทนที่ assert จำนวนครั้ง (ส่วนที่ใช้ร่วม = 2 ครั้ง คือ 🅰️ และ 🅱️) · 🅱️ ใช้ถ้อยคำทั่วไป ไม่เติมเบาะแสเฉพาะ PawPantry (ยกเว้นข้อความ error 409 ที่เห็นได้จากระบบเอง)
- `rea.ps1` ยังเป็น UTF-8 มี BOM (PowerShell 5.1 อ่านภาษาไทยในคอมเมนต์ได้) · line ending LF เหมือนเดิม
- ยังไม่ได้ทดสอบ: `recordHar.urlFilter` กับ REA `inspect-web-network-capture` (LAB 5 ไม่ส่ง HAR นี้เข้า REA) · กติกาสต็อกใหม่ยังไม่มีรอบ RUN ยืนยันว่า `test:all` รอบเดียวเขียว (ห้ามรัน LAB ซ้ำในงานนี้)
