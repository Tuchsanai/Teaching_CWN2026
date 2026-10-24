# LAB 10_RESULT · ฝึกเดี่ยวครบวงจร PR-1 (เพิ่มลงตะกร้าเกินสต็อก แต่ขึ้นข้อความสำเร็จ)
| หัวข้อ | ค่า |
|---|---|
| เวลาเริ่ม · จบ · ใช้ไป | 2026-10-12 10:54 · 11:10 · ~16 นาที (เครื่อง ~8: test:all 4.8 นาที + รายเบราว์เซอร์ 2.4 + build 10 วิ + อื่น ๆ · agent ~8) |
| cwd ของเซสชัน / settings มีผลไหม | runner cwd ไม่ใช่ `w/` → `w/CLAUDE.md` + `w/.claude/settings.json` **ไม่ได้ถูกบังคับ** · runner ทำตามเอง (คำสั่งทุกตัวรันจาก `w/` ด้วย PowerShell tool) |
| ไฟล์ที่สร้าง/แก้ | แก้ `petshop/components/ProductCard.tsx` (+5 −2) · สร้าง `e2e-legacy/tests/new/pr1-add-to-cart.spec.ts` (81 บรรทัด · 4 test) · แก้ `CHANGE-REPORT.md` (เพิ่มคอลัมน์ PR-1 ใน 10 แถวของตารางหัวข้อ 1 + หมายเหตุ 1 บรรทัด) |
| สคริปต์ชั่วคราว | `rea\scratch\pr1-repro.mjs` · `rea\scratch\pr1-toast-probe.mjs` · `../tools/lab10/add-pr1-col.mjs` (แก้ตาราง UTF-8) · `../tools/lab10/shot.mjs` `shot2.mjs` (ภาพ) · log ยาวทั้งหมดใน `../tools/lab10/*.txt` |
| โหมดการรัน · shell ที่ agent ใช้จริง | A · PowerShell tool (Windows PowerShell 5.1) · Git Bash ใช้เฉพาะอ่าน/grep log |
| timeout / รันซ้ำ | build / test:all / รายเบราว์เซอร์ ตั้ง timeout 15–20 นาที (foreground) · ไม่มีการสั่งซ้ำระหว่างรอ |
| สถานะเว็บ | build ใหม่ 10:57:26 (exit 0 · 9.7 วิ · `next build` รันจริง ไม่ cached) → healthy · **จบ LAB: `docker compose down` ใน `w/petshop` (project pawpantry05 · container + network ถูกลบ · พอร์ต 4000 ว่าง)** · image `rea-lab:6.4.0` ไม่แตะ |
| ข้อมูลทดสอบ | reset 4 ครั้งโดยสคริปต์ (`pr1-repro` `pr1-toast-probe` `shot` ×2) + global-setup ทุกรอบ Playwright · ไม่ล็อกอิน (ตะกร้าอยู่ใน localStorage) |

## ข้อห้ามที่ทำตาม (และที่พลาด ถ้ามี)
- ทำซ้ำแบบ black-box ก่อนเปิดโค้ด: เขียน spec และได้ผลแดงก่อน แล้วจึง grep/อ่าน `petshop/components/ProductCard.tsx` `ShopProvider.tsx` (อ่าน CODEBASE-MAP/TEST-DATA เท่านั้นก่อนหน้านั้น)
- ไม่แตะไฟล์เดิมใน `e2e-legacy/` / `TEST-DATA.md` ทั้งเครื่องมือและ shell · `git diff --stat -- e2e-legacy TEST-DATA.md` = ว่าง (ตรวจหลังแก้และก่อนจบ)
- ไม่แก้ test เดิม · test ใหม่อยู่ใน `tests/new/` · แก้โค้ด 1 ไฟล์ที่ helper กลางตามที่ "ร้าน" อนุมัติ · ไม่ refactor
- ไม่เปิด `_solution/` · ไม่ใช้ Playwright MCP (ทุกอย่าง headless) · ไม่ใช้ git เปลี่ยนสถานะ · ไม่แตะ container บทอื่น (`sabai06-*` `exref-*` ยังรันอยู่ตามเดิม)
- ไม่เลี่ยง deny ผ่าน shell · CHANGE-REPORT แก้ด้วย node (UTF-8) ไม่ใช้ `Set-Content`/`>` ตามคำเตือน CLAUDE.md

## คำตอบสรุปที่แสดงในแชท
> | ขั้น | หลักฐาน (ไฟล์) | ผล |
> |---|---|---|
> | 1 ทำซ้ำ black-box | `rea\scratch\pr1-repro.mjs` · `out\pr1-A-cart.png` | สต็อกหน้าสินค้า "เหลือ 3 ชิ้น" · 2+2 → toast "✅เพิ่ม สูตรลดก้อนขน (1.5 kg) ลงตะกร้าแล้ว 🛒" ทั้งสองรอบ · badge 2 → 3 · ตะกร้า 3 ชิ้น ฿1,560 · 3+1 → "⚠️ไม่สามารถเพิ่ม … สินค้าในสต็อกไม่พอ" · ตัวเลือกจำนวนหยุดที่ 3 (max=3) |
> | 1 ผลที่คาดหวัง | [D] TEST-DATA สต็อก 3 · ข้อความไม่มีใน [D]/[R] → ถาม → [ร้าน] "เพิ่มได้อีกเพียง {n} ชิ้น (สินค้าเหลือ {สต็อก} ชิ้น)" แจ้งเตือน ไม่ใช่สำเร็จ | – |
> | 1 test แดง | `e2e-legacy/tests/new/pr1-add-to-cart.spec.ts` (4 test) | ก่อนแก้ **2 failed · 2 passed** (TC-PR1-01 2+2 · 02 1+3 แดง · guard 03 3+1 · 04 1+2 เขียว) |
> | 2 ต้นเหตุ | `components/ProductCard.tsx:63` `if (added > 0)` ใน `useAddToCart` (:59-71) | `addToCart` (`ShopProvider.tsx:178-198`) clamp ถูกและคืนจำนวนที่เพิ่มจริง แต่ helper เช็กแค่ `> 0` → เพิ่มได้ 1 จาก 2 ก็ขึ้นข้อความสำเร็จ |
> | 2 impact | `useAddToCart` ใช้ที่ `ProductDetail.tsx:238` (qty เลือกได้ → กระทบจริง) · `ProductCard.tsx:142` การ์ดสินค้า · `FinderWizard.tsx:57` (qty 1 เสมอ → ไม่มีกรณีบางส่วน) · ไม่ผ่าน helper: ซื้อคู่กัน `ProductDetail.tsx:79` · โปรด `WishlistView.tsx:18` · test ที่ต้องรันซ้ำ: 03-product (TC-PRD-03) 04-wishlist 05-cart 09-recommend + ทั้งชุด | อนุมัติแก้ที่ helper กลางที่เดียว |
> | 3 แก้ + build | `ProductCard.tsx` +5 −2 · `docker compose up -d --build` exit 0 | เพิ่มได้ไม่ครบ → toast `error` "เพิ่มได้อีกเพียง {added} ชิ้น (สินค้าเหลือ {stockOf} ชิ้น)" |
> | 3 test ใหม่ | `pr1-add-to-cart.spec.ts` | **4 passed** |
> | 3 regression chromium | `npx playwright test` | **81 passed** 27.6 วิ |
> | 3 regression 3 เบราว์เซอร์ | `npm run test:all` | **196 passed · 47 failed** (สต็อกร่วมหมดในรอบเดียว) → รันทีละเบราว์เซอร์: firefox **81/81** 39.9 วิ · webkit **81/81** 1.2 นาที |
> | 4 CHANGE-REPORT | `CHANGE-REPORT.md` หัวข้อ 1 คอลัมน์ PR-1 | re-engineering · +5 −2 · แดง 2/4 → เขียว 4/4 · regression 81×3 |

## ตัวเลขสำคัญ (นับจากไฟล์จริง พร้อมคำสั่งที่ใช้นับ)
- diff: `git diff --no-index --stat out\v1\components\ProductCard.tsx petshop\components\ProductCard.tsx` → `1 file changed, 5 insertions(+), 2 deletions(-)` · ก่อนแก้ SHA-256 ของ `petshop\…\ProductCard.tsx` = `out\v1\…` (Get-FileHash เทียบ → True) · รวม 3 งาน `git diff --stat -- petshop` = 7 files, 66 insertions, 17 deletions
- 81 test ต่อเบราว์เซอร์ = เดิม 40 + bug01/char-money 16 + cr01 21 + pr1 4
- `test:all` 47 failed (จาก `../tools/lab10/all.txt` แยกด้วย awk ตามบล็อก): firefox 15 (cr01 14 · pr1 1) · webkit 32 (05-cart 1 · 06-coupon 1 · 09-recommend 2 · bug01 4 · char-money 5 · cr01 19) · สาเหตุ: มี `409`/"สินค้าไม่พอ: ลูกแมว สูตรแซลมอน" 21 บล็อก · click timeout บนปุ่มที่ disabled (`qty-plus` "element is not enabled") 21 · assertion อื่น 5 (09-recommend 2 · bug01 2 · TC-PR1-03 firefox ไม่เห็น toast 1) · ทั้ง 47 ข้อผ่านเมื่อรันทีละเบราว์เซอร์
- firefox `pr1-add-to-cart.spec.ts --repeat-each=3` → 12 passed 17.3 วิ (ไม่ flaky เมื่อรันลำพัง)

## คำสั่งที่รัน (REA/docker/playwright: คำสั่ง | exit | เวลา | ขนาดผล)
| คำสั่ง | exit | เวลา | ผล |
|---|---|---|---|
| `node rea\scratch\pr1-repro.mjs` | 0 | 4.4 วิ | 3 สถานการณ์ (2+2 · 3+1 · 4) |
| `node rea\scratch\pr1-toast-probe.mjs` | 0 | – | class `toast-success` vs `toast-error` · qty-input max=3 |
| `npx playwright test tests/new/pr1-add-to-cart.spec.ts` (ก่อนแก้ รอบ 1) | 1 | 11.5 วิ | 4 failed (2 ข้อ guard แดงเพราะ spec ผิด: `item-qty` เป็น input ต้อง `toHaveValue`) → แก้ spec |
| เหมือนกัน (ก่อนแก้ รอบ 2) | 1 | 11.5 วิ | **2 failed · 2 passed** |
| `cd petshop; docker compose up -d --build` | 0 | 9.7 วิ | image pawpantry05:latest · Recreated |
| `npx playwright test tests/new/pr1-add-to-cart.spec.ts` (หลังแก้) | 0 | 3.3 วิ | 4 passed |
| `npx playwright test` (chromium) | 0 | 28.9 วิ | 81 passed |
| `npm run test:all` | 1 | 288.7 วิ | 196 passed · 47 failed |
| `npx playwright test --project=firefox` | 0 | 41.1 วิ | 81 passed |
| `npx playwright test --project=webkit` | 0 | 72 วิ | 81 passed |
| `npx playwright test tests/new/pr1-add-to-cart.spec.ts --project=firefox --repeat-each=3` | 0 | 18.6 วิ | 12 passed |
| `docker compose down` (w/petshop) | 0 | – | container + network pawpantry05_default removed |

## ตัวอย่างแถวเด่น 3–6 แถว (สำหรับ README)
- black-box: `[A] round 2: asked 2 → toast: ✅เพิ่ม สูตรลดก้อนขน (1.5 kg) ลงตะกร้าแล้ว 🛒 badge ["3"]` · `pp-cart=[{"slug":"hairball-control-dry","size":"1.5 kg","qty":3}]`
- test แดง: `Expected substring: "เพิ่มได้อีกเพียง 1 ชิ้น (สินค้าเหลือ 3 ชิ้น)"` · `unexpected value "✅เพิ่ม สูตรลดก้อนขน (1.5 kg) ลงตะกร้าแล้ว 🛒"`
- ต้นเหตุ: `ProductCard.tsx:63` `if (added > 0) {` → แก้เป็น `if (added > 0 && added < Math.max(1, Math.floor(qty))) { … "เพิ่มได้อีกเพียง ${added} ชิ้น (สินค้าเหลือ ${stockOf(product.slug)} ชิ้น)", "error" } else if (added > 0) {`
- หลังแก้ (shot): `round 2: ⚠️เพิ่มได้อีกเพียง 1 ชิ้น (สินค้าเหลือ 3 ชิ้น)`
- regression: chromium 81/81 · firefox 81/81 · webkit 81/81 (ทีละเบราว์เซอร์) · test:all รอบเดียว 196/243

## ตัดสินแทนผู้เรียน (คำถาม | คำตอบ | ที่มา 🧑/ตัดสินเอง | เหตุผล)
| คำถาม | คำตอบ | ที่มา | เหตุผล |
|---|---|---|---|
| ข้อ 1: ข้อความที่ถูกเมื่อเพิ่มได้ไม่ครบคืออะไร ([D]/[R] ไม่มี) | แจ้งเตือน "เพิ่มได้อีกเพียง {จำนวนที่เพิ่มได้} ชิ้น (สินค้าเหลือ {สต็อก} ชิ้น)" · เพิ่มไม่ได้เลย/ครบ = ข้อความเดิม | 🧑 | TEST-DATA บอกแค่สต็อก 3 |
| ข้อ 2: อนุมัติแก้ไหม | อนุมัติ แก้ที่ `useAddToCart` ที่เดียว | 🧑 | ตรงกับต้นเหตุที่หาได้ |
| "แจ้งเตือน" ใช้ toast ชนิดไหน (มีแค่ success/info/error) | `error` (ไอคอน ⚠️ เหมือนข้อความสต็อกไม่พอเดิม) | ตัดสินเอง | `info` ใช้ 🐾 ดูไม่เป็นคำเตือน · ไม่เพิ่มชนิดใหม่เพื่อแก้ให้เล็กที่สุด |
| {สต็อก} มาจากไหน | `stockOf(slug)` (สต็อกรวมทุกขนาดฝั่ง browser · ตรงกับ "เหลือ 3 ชิ้น" บนหน้า) | ตัดสินเอง | ตัวอย่างของร้าน "สินค้าเหลือ 3 ชิ้น" = สต็อกทั้งหมด ไม่ใช่ที่เหลือหลังหักตะกร้า |
| เพิ่มได้บางส่วนยังให้ลูกบอลบินเข้าตะกร้าไหม | ยังบิน (มีของลงตะกร้าจริง) | ตัดสินเอง | ไม่เปลี่ยนพฤติกรรมเกินที่ร้านขอ |
| `test:all` ล้ม 47 ข้อ | ไม่แก้โค้ด/test · รันทีละเบราว์เซอร์แล้วจดเหตุ | ตัดสินเอง (ตามที่ผู้สั่งงานแจ้งไว้) | อาการสต็อกร่วมหมดซ้ำกับ LAB 8 · รายเบราว์เซอร์ 81/81 ทั้งหมด |

## ข้อสังเกต 👀 (บทเรียนจากรอบจริง ไม่ใช่สรุปผลซ้ำ)
- test แดงรอบแรกแดง "ผิดเหตุ" 2 ข้อ (`item-qty` เป็น `<input>` ต้องใช้ `toHaveValue`) → guard ที่ควรเขียวก่อนแก้ช่วยจับ spec ผิดได้ทันที เป็นตัวอย่างดีว่าทำไม test แดงต้องดู **ข้อความ error** ไม่ใช่แค่ว่าแดง
- ตัวเลือกจำนวนบนหน้าสินค้า clamp ที่สต็อกรวม (3) แต่ไม่หักของที่อยู่ในตะกร้าแล้ว → ลูกค้าเลือก 2 ได้ทั้งที่เหลือให้เพิ่มแค่ 1 นี่คือที่มาของอาการ (UI ไม่กันก่อนกด) · ร้านเลือกแก้ที่ข้อความ ไม่ได้แก้ตัวเลือกจำนวน
- หน้าสินค้ายังขึ้น "เหลือ 3 ชิ้น" หลังของ 3 ชิ้นอยู่ในตะกร้าแล้ว (สต็อก server ไม่ลดจนกว่าจะสั่งซื้อ) — ไม่อยู่ในขอบเขต PR-1 แต่ควรถามร้าน
- การ์ดสินค้า/Finder ใช้ helper เดียวกันแต่ส่ง qty 1 เสมอ → ตาราง impact "หลายหน้า" แต่กระทบจริงแค่หน้าสินค้า (ต้องอ่านผู้เรียกด้วย ไม่ใช่นับจาก grep อย่างเดียว)
- `test:all` รอบเดียว: นอกจาก 409 ยังมี TC-PR1-03 firefox ที่ toast ไม่โผล่ภายใน 8 วิ (toast หายเองใน 2.8 วิ · เครื่องโหลดหนัก 3 เบราว์เซอร์ × 4 workers) — รันลำพัง repeat ×3 ผ่าน → นับเป็นผลข้างเคียงของรอบหนัก ไม่ใช่บั๊ก

## ปัญหา / วิธีแก้
- `npm run test:all` 47 failed เพราะสต็อกร่วม (`kitten-salmon-dry` ฯลฯ) หมดเมื่อ 3 เบราว์เซอร์สั่งซื้อในรอบเดียว (reset แค่ครั้งเดียวต่อรอบ) → รัน `--project=firefox` / `--project=webkit` แยก (global-setup reset ให้ทุกรอบ) ได้ 81/81 ทั้งคู่
- รันสคริปต์ครั้งแรกด้วย `Out-File` ไปโฟลเดอร์ `../tools/lab10/` ที่ยังไม่มี → error `DirectoryNotFoundException` → สร้างโฟลเดอร์แล้วรันใหม่ (สคริปต์ยังไม่ได้รัน ไม่กระทบข้อมูล)

## ข้อเสนอแก้พรอมต์ (ระดับ H = ทำต่อไม่ได้/ผลผิด · M = ได้ผลแต่สับสน · m = ถ้อยคำ)
- **M** ข้อ 3 `npm run test:all` ล้มแน่นอนในรอบเดียว (สต็อกร่วมหมด · ซ้ำกับ LAB 8) → เพิ่มในพรอมต์: "ถ้าล้มด้วย 409 'สินค้าไม่พอ' ให้รันทีละเบราว์เซอร์ `npx playwright test --project=firefox` แล้ว `--project=webkit`" หรือแก้ที่ต้นทาง (reset ต่อ project) ก่อนแจกบท
- **M** ข้อ 4 "เพิ่มแถว PR-1" แต่ตาราง CHANGE-REPORT (จาก LAB 9) เป็นตารางแนวตั้ง (หัวข้อเป็นแถว งานเป็นคอลัมน์) → ผู้เรียนต้องตีความเป็น "เพิ่มคอลัมน์" · เสนอเขียน "เพิ่ม PR-1 ในตารางสรุปของ CHANGE-REPORT.md (แถวหรือคอลัมน์ตามรูปแบบเดิม)"
- **m** ข้อ 1 ควรบอกว่า "แจ้งเตือน" ใช้ toast แบบไหน หรือให้ถามด้วย (เว็บมีแค่ success/info/error) · ข้อ 1 "ทำซ้ำแบบ black-box" ควรบอกว่าตัวเลือกจำนวนหยุดที่สต็อก (ผู้เรียนที่ลอง 4 ชิ้นจะงง)
- **m** (ไม่ใช่พรอมต์) test ที่ตรวจ toast ไวต่อเครื่องช้าเพราะ toast หายใน 2.8 วิ — ถ้าเจอ flaky ใน `test:all` ให้ README อธิบาย

## ภาพที่ควรใช้ใน README (../design/shots/labN-*.png 1280×800 + คำอธิบาย 1 บรรทัด)
- `../design/shots/lab10-pr1-cart-before.png` — ตะกร้าหลังกด 2+2 (ก่อนแก้): มีแค่ 3 ชิ้น ฿1,560 ทั้งที่ toast บอกสำเร็จทั้งสองรอบ (คัดจาก `w/out/pr1-A-cart.png`)
- `../design/shots/lab10-pr1-toast-after.png` — หน้าสินค้าหลังแก้ รอบสอง (qty 2): toast ⚠️ "เพิ่มได้อีกเพียง 1 ชิ้น (สินค้าเหลือ 3 ชิ้น)" · badge ตะกร้า 3
