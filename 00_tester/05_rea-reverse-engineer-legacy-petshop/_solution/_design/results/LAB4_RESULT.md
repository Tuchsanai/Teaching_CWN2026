# LAB 4_RESULT · ล็อกพฤติกรรมเดิมก่อนแตะโค้ด

| หัวข้อ | ค่า |
|---|---|
| เวลาเริ่ม · จบ · ใช้ไป | 2026-10-12 09:51 · 10:02 · 11 นาที (เครื่อง ~4 = Playwright 5 รอบ + สำรวจ headless 4 รอบ · agent ~7) |
| cwd ของเซสชัน / settings มีผลไหม | runner เป็น Agent-tool session cwd ≠ `w/` → `w/CLAUDE.md` + `w/.claude/settings.json` **ไม่ได้ถูกบังคับโดย harness · ทำตามเอง (self-enforced)** · ทุกคำสั่งรันจาก `C:/t/work/run05/w` |
| ไฟล์ที่สร้าง/แก้ | `BASELINE.md` (81 บรรทัด) · `e2e-legacy/tests/new/char-money.spec.ts` (187 บรรทัด · 7 test) · `e2e-legacy/tests/new/golden/products.json` (40,276 B) · `golden/coupons-validate.json` (16,199 B · 30 กรณี) |
| สคริปต์ชั่วคราว | `rea\scratch\lab4-probe.mjs` (40 บรรทัด · API probe) · `rea\scratch\lab4-explore.mjs` (53 · headless อ่านเงิน 4 จุด) · `rea\scratch\lab4-golden.mjs` (34 · บันทึก golden) · `../tools/lab4/count.mjs` (นับผล list reporter) · `../tools/lab4/shots.mjs` (ภาพ README) · log ทั้งหมดใน `../tools/lab4/*.txt` |
| โหมดการรัน · shell ที่ agent ใช้จริง | A · PowerShell tool (Windows PowerShell 5.1) สำหรับคำสั่งในพรอมต์ · Git Bash เฉพาะงานของ runner (นับผล/grep log ใน `../tools/lab4`) |
| timeout / รันซ้ำ | `npm run test:all` ตั้ง timeout 10 นาที (รันจริง 61 s และ 82 s) · ไม่มีการสั่งซ้ำระหว่างรอ · รัน SHIP-03 เพิ่ม 1 รอบด้วย `--reporter=json` เพื่อดูว่า expected-fail ล้มตรงจุดที่ตั้งใจ |
| สถานะเว็บ | pawpantry05 healthy (Up ~40 นาที · container created 02:21Z · ไม่ได้ rebuild ใน LAB นี้) |
| ข้อมูลทดสอบ | reset 6 ครั้งโดย `global-setup.ts` (ทุกรอบ playwright) + 1 ครั้งมือ (runner เทียบ `/api/products` ก่อน/หลัง reset ว่าต่างแค่ stock) · ผู้ใช้: สุ่มอีเมลใหม่ทุก test/สคริปต์ (`registerByApi` / `@test.dev`) · ไม่ใช้บัญชี demo |

## ข้อห้ามที่ทำตาม (และที่พลาด ถ้ามี)

- ไม่แก้ `petshop/` · ไม่แก้ไฟล์เดิมใน `e2e-legacy/` (เพิ่มเฉพาะใน `tests/new/`) · ไม่เปิด `_solution/` · `git diff --stat -- e2e-legacy TEST-DATA.md petshop` = ว่าง · ไม่มีการเขียนไฟล์ต้องห้ามผ่าน shell
- ไม่เรียก `/api/test/reset` ในเทสต์ · ไม่ล็อกเลขคำสั่งซื้อ (ตรวจแค่ `/^PP-\d{6}$/`) และสต็อก · ใช้ `toEqual` ไม่ใช้ `toMatchSnapshot` · ไม่แก้ fixtures.ts
- ไฟล์ JSON/ภาษาไทยเขียนด้วย node (`writeFileSync utf8`) ไม่ใช้ `Set-Content`/`>` · มีครั้งเดียวที่ใช้ `[IO.File]::WriteAllText` (UTF-8 ไม่มี BOM) แก้สคริปต์ของตัวเองใน `rea\scratch\`
- ไม่ใช้ Playwright MCP · ไม่ git ที่เปลี่ยนสถานะ · ไม่แตะ `sabai06-*` / `exref-*`
- พลาดเล็กน้อย: runner ยิง `POST /api/test/reset` เอง 1 ครั้ง (นอกเทสต์ · CLAUDE.md อนุญาต) เพื่อพิสูจน์ว่าฟิลด์อื่นนอกจาก `stock` ไม่เปลี่ยน — ตอนนั้นไม่มีชุดเทสต์อื่นรันอยู่

## คำตอบสรุปที่แสดงในแชท

> | ชุด | เบราว์เซอร์ | ผ่าน | ล้ม | expected-fail |
> |---|---|---|---|---|
> | ชุดเดิม (40 test) | chromium | 40 | 0 | 0 |
> | | firefox | 40 | 0 | 0 |
> | | webkit | 40 | 0 | 0 |
> | ใหม่ `char-money` (7 test) | chromium (2 รอบ) | 6 | 0 | 1 |
> | | firefox | 6 | 0 | 1 |
> | | webkit | 6 | 0 | 1 |
>
> ผู้ต้องสงสัย S1: ตะกร้า ฿999 พอดี (ส่งปกติ) หน้าตะกร้า/ปุ่มยืนยันบอก "ฟรี ฿999" แต่ server บันทึกค่าส่ง ฿50 ยอด ฿1,049 → ขัด TEST-DATA "ฟรีเมื่อซื้อครบ ฿999" · ล็อกเป็นคู่ TC-CHAR-SHIP-02 (legacy-quirk) + TC-CHAR-SHIP-03 (`test.fail` KNOWN-ISSUE)

## ตัวเลขสำคัญ (นับจากไฟล์จริง พร้อมคำสั่งที่ใช้นับ)

ผล Playwright แยกเบราว์เซอร์ (reporter `list` · นับด้วย `node ../tools/lab4/count.mjs <log>` = นับบรรทัด `ok`/`x` ต่อ `[browser]` + รวมเวลาต่อ test)

| รอบ | เบราว์เซอร์ | passed | failed | expected-fail | flaky | เวลารวมทั้งรอบ (สรุปท้าย list) | ผลรวมเวลา test ในเบราว์เซอร์ |
|---|---|---|---|---|---|---|---|
| 1 · `npx playwright test` (ชุดเดิม) | chromium | 40 | 0 | 0 | 0 | 13.0 s (wall 14.4 s) | 45.7 s |
| 2 · `npm run test:all` (ชุดเดิม) | chromium | 40 | 0 | 0 | 0 | 59.9 s (wall 60.7 s) | 46.0 s |
| | firefox | 40 | 0 | 0 | 0 | | 62.0 s |
| | webkit | 40 | 0 | 0 | 0 | | 112.7 s |
| 3 · `npx playwright test tests/new` รอบ 1 | chromium | 6 | 0 | 1 | 0 | 4.1 s | 11.0 s |
| 4 · `npx playwright test tests/new` รอบ 2 | chromium | 6 | 0 | 1 | 0 | 4.0 s | 10.4 s |
| 5 · `npm run test:all` (เดิม + ใหม่) | chromium | 46 (เดิม 40 + ใหม่ 6) | 0 | 1 | 0 | 1.4 m = "141 passed" (wall 82 s) | 52.9 s (ใหม่ 9.0) |
| | firefox | 46 | 0 | 1 | 0 | | 84.1 s (ใหม่ 19.8) |
| | webkit | 46 | 0 | 1 | 0 | | 164.2 s (ใหม่ 29.1) |

- reporter `list` แสดง expected-fail เป็น `x` แต่สรุปท้ายนับรวมใน "passed" (141 = 120 + 21) · HTML report ก็แสดงเป็น ✓ Passed 141 · Failed 0 · Flaky 0
- ไม่มี flaky → ไม่ได้รัน `--repeat-each=3`
- ยืนยัน expected-fail ล้มที่จุดที่ตั้งใจ (`--reporter=json` · `expectedStatus failed · status expected`): diff `shipping 0 → 50` · `total 999 → 1049` ที่ response `POST /api/orders`
- golden: `products.json` 28 รายการ (ตัด `stock`) · `coupons-validate.json` 30 กรณี (`node -e` อ่าน `cases.length`) · `/api/products` ก่อน/หลัง reset เทียบแล้ว: เท่ากันเมื่อตัด stock (`equal-without-stock true`)

## คำสั่งที่รัน (playwright/สำรวจ: คำสั่ง | exit | เวลา | ขนาดผล)

| คำสั่ง (จาก `w/` หรือ `w/e2e-legacy`) | exit | เวลา | ผล |
|---|---|---|---|
| `npx playwright test` | 0 | 14.4 s | 40 passed · log `../tools/lab4/run1-chromium.txt` |
| `npm run test:all` | 0 | 60.7 s | 120 passed · `run1-all.txt` |
| `node rea\scratch\lab4-probe.mjs --order` | 0 | ~2 s | 36 กรณี validate + 5 ออเดอร์ (998/999 × standard/express + 999+PAW10) |
| `node rea\scratch\lab4-explore.mjs s999` · `s998` · `s999 express` · `s998 coupon=NEWCAT50` · `t999` | 0 ×5 | ~4 s/ครั้ง | เงิน 4 จุดต่อตะกร้า (ตารางด้านล่าง) |
| `node rea\scratch\lab4-golden.mjs` | 0 | ~1 s | products 28 · coupon cases 30 |
| `npx playwright test tests/new` ×2 | 0 · 0 | 5 s · 5 s | 7 passed (6 + 1 expected-fail) ทั้งสองรอบ |
| `npx playwright test tests/new -g "SHIP-03" --reporter=json` | 0 | ~5 s | ยืนยันจุดที่ expected-fail ล้ม |
| `npm run test:all` | 0 | 82 s | 141 passed (1.4m) · `run2-all.txt` |
| `node ../tools/lab4/shots.mjs` | 0 | ~6 s | ภาพ 4 ไฟล์ใน `../design/shots/` |

ผลสำรวจเงิน 4 จุด [E] (`lab4-explore.mjs`):

| ตะกร้า | ① ตะกร้า (ย่อย/ส่ง/รวม) | ② ปุ่ม | ③ response `{subtotal,discount,shipping,total}` | ④ หน้าคำสั่งซื้อ |
|---|---|---|---|---|
| ฿998 ปกติ | 998 / ฿50 / ฿1,048 | ฿1,048 | 998, 0, 50, 1048 | ฿50 · ฿1,048 |
| ฿999 ปกติ (2 ตะกร้า) | 999 / ฟรี / ฿999 | ฿999 | 999, 0, **50**, **1049** | **฿50 · ฿1,049** |
| ฿999 ด่วน | 999 / ฟรี / ฿999 (ยังไม่เลือกด่วน) | ฿1,119 | 999, 0, 120, 1119 | ฿120 · ฿1,119 |
| ฿998 + NEWCAT50 | 998 / −฿50 / ฿50 / ฿998 | ฿998 | 998, 50, 50, 998 | ฿998 |
| (API เท่านั้น) ฿999 + PAW10 | – | – | 999, 99, 50, 950 | – (ไม่ได้ล็อก · ไม่มีกฎใน [D] ว่าส่งฟรีคิดก่อน/หลังส่วนลด) |

## ตัวอย่างแถวเด่น 3–6 แถว (สำหรับ README)

| จาก | แถว |
|---|---|
| ตารางช่องว่าง | TC-CART-03 **ชื่อ** "ซื้อครบ ฿999 ได้ส่งฟรี" แต่ตัว test ตรวจที่ ฿790 กับ ฿2,680 ในหน้าตะกร้าเท่านั้น → ไม่มีข้อไหนใช้ยอด ฿999 พอดี |
| ตารางช่องว่าง | กฎเงินเกือบทั้งหมดตรวจแค่หน้าตะกร้า · มีแค่ TC-CHK-03 (FREESHIP ฿378) ที่ดูยอดบนคำสั่งซื้อที่ server บันทึก · ไม่มี test อ่าน response `POST /api/orders` · ส่งด่วน ฿120 ไม่มี test เลย |
| test ใหม่ | TC-CHAR-SHIP-02 (legacy-quirk) ฿999: ตะกร้า ฟรี ฿999 · ปุ่ม ฿999 · response `{999,0,50,1049}` · หน้าคำสั่งซื้อ ฿1,049 — [E] |
| test ใหม่ | TC-CHAR-SHIP-03 (KNOWN-ISSUE `test.fail`) ตาม [D] ฿999 ต้องฟรีทุกจุด → ล้มที่ ③ (shipping 50) |
| golden | PAW10 ปัดลง ฿69→6 · ฿999→99 · NEWCAT50 อาหารแมว ฿499 ไม่ผ่าน / ฿520 ผ่าน |
| ผลรัน | 3 เบราว์เซอร์: 141 passed = เดิม 120 + ใหม่ 21 (มี expected-fail 3 ที่ reporter นับเป็น passed) |

## ตัดสินแทนผู้เรียน (คำถาม | คำตอบ | ที่มา 🧑/ตัดสินเอง | เหตุผล)

| คำถาม | คำตอบที่ใช้ | ที่มา | เหตุผล |
|---|---|---|---|
| ข้อ 1 "ถ้ามีข้อล้มให้หยุดบอกผมก่อน" | ไม่ต้องถาม (ไม่มีข้อล้ม: 40/40 · 120/120) | – | เงื่อนไขไม่เกิด · ถ้าเกิดจะใช้ 🧑 "จดไว้ใน BASELINE.md ว่าเป็นของเดิม แล้วทำต่อ" |
| เลือกตะกร้าค่าขอบไหน | ฿998 / ฿999 (ปกติ · ด่วน) + NEWCAT50 บน ฿998 + golden คูปอง ฿499/฿520 | ตัดสินเอง | ค่าขอบของ "ครบ ฿999" คือ 998/999 · หา ฿500 อาหารแมวพอดีไม่ได้ (brute force ราคาอาหารแมวแห้ง/เปียกไม่มีชุดที่รวม 500) จึงใช้ 499/520 |
| ตะกร้า ฿999 ใช้ชามกินช้า ×3 ซ้ำ 3 test ได้ไหม | แยกเป็น 2 ตะกร้า (คู่ quirk/known-issue ใช้ ไม้ตกแมว + ทูน่าแพ็ค ×2 + แกะบด ×2 · ส่งด่วนใช้ชามกินช้า) | ตัดสินเอง | ชามกินช้า stock 18 · 3 test × 3 ใบ × 3 เบราว์เซอร์ = 27 > 18 → ออเดอร์จะล้มเพราะสต็อก (เทสต์รันขนาน reset แค่ต้นรอบ) |
| [E] ≠ [D] ที่ ฿999 | test คู่ legacy-quirk + `test.fail()` KNOWN-ISSUE + "ผู้ต้องสงสัย" ใน BASELINE.md | พรอมต์ข้อ 4 | ห้ามล็อกค่าที่ขัด [D] เป็นผลคาดหวังเดี่ยว ๆ |
| PAW10 ปัดลง (฿999 → 99) ขัด [D] ไหม | ไม่ขัด (บันทึกเป็น [E] ใน golden) | ตัดสินเอง | [D] บอกแค่ "ลด 10%" ไม่บอกวิธีปัด |
| PAW10 + ยอดใกล้เส้น (ส่งฟรีคิดจากยอดก่อน/หลังส่วนลด) | ไม่ล็อก · จดใน BASELINE "ยังไม่ได้ล็อก ต้องถามเจ้าของร้าน" | ตัดสินเอง | CLAUDE.md "ไม่แน่ใจกฎธุรกิจ ให้ถาม อย่าเดา" และพัวพันกับ S1 |

## ข้อสังเกต 👀 (บทเรียนจากรอบจริง ไม่ใช่สรุปผลซ้ำ)

- ชุดเดิมเขียว 120/120 บน build ที่มีบั๊กเงิน → "regression ผ่าน" ไม่ได้แปลว่ากฎเงินถูก เพราะชุดเดิมดูเงินแทบทั้งหมดแค่หน้าตะกร้า (ซึ่งตรง [D])
- ชื่อ test ≠ สิ่งที่ test ตรวจ: TC-CART-03 ชื่อพูดถึง ฿999 แต่ไม่เคยใช้ ฿999 ต้องอ่านตัว test
- การตรวจ "ตะกร้าเดียวกัน 4 จุด" คือสิ่งที่เปิดผู้ต้องสงสัย: ตะกร้า + ปุ่มตรงกัน แต่ response + หน้าคำสั่งซื้อไม่ตรง → ถ้าตรวจจุดเดียว (เช่นตะกร้า) จะไม่เห็น
- ที่ ฿998 และส่งด่วน ฿999 ทุกจุดตรงกัน → ปัญหาอยู่เฉพาะเส้น "ครบ ฿999" ของส่งปกติ (ค่าขอบตัวเดียว)
- `test.fail()` ในรายงาน list แสดงเป็น `x` แต่สรุปท้ายรวมใน "passed" และ HTML report แสดง ✓ — ผู้เรียนที่ดูแค่ "141 passed" จะไม่รู้ว่ามี KNOWN-ISSUE ต้องดู annotation/tag `@known-issue`
- golden ต้องตัดฟิลด์ที่เปลี่ยนเอง: เทียบ `/api/products` ก่อน/หลัง reset แล้วต่างแค่ `stock` (ไม่ใช่เดาเอา)
- สต็อกเป็นทรัพยากรร่วมของเทสต์ขนาน: ต้องคำนวณ "ชิ้นต่อ test × เบราว์เซอร์" ไม่ให้เกินสต็อก seed (ชามกินช้า 18) และหลีกสินค้าที่ชุดเดิมพึ่งสต็อก (`hairball-control-dry` 3 ใน TC-PRD-03 · สินค้าของ TC-CHK-04) — golden คูปองใช้ hairball ได้เพราะ validate ไม่ตัดสต็อก

## ปัญหา / วิธีแก้

| ปัญหา | วิธีแก้ |
|---|---|
| `Invoke-RestMethod` (PS 5.1) แสดงชื่อสินค้าภาษาไทยเป็น mojibake | อ่าน API ด้วย node `fetch` แทน |
| นับผลจาก log list reporter ด้วย `Select-String` ได้ 0 (เลขลำดับถูก pad ด้วยช่องว่าง `ok   4 [chromium]`) | เขียน `../tools/lab4/count.mjs` ใช้ regex `\s+\d+` |
| `npm run ... *> file` ใน PowerShell ใส่ NativeCommandError ของ stderr (`npm notice`) ไว้ต้น log | ไม่กระทบผล · exit code 0 ทุกรอบ |
| ไม่มีชุดอาหารแมวที่รวม ฿500 พอดี | ใช้ ฿499 (ไม่ผ่าน) กับ ฿520 (ผ่าน) ใน golden |

## ข้อเสนอแก้พรอมต์ (ระดับ H = ทำต่อไม่ได้/ผลผิด · M = ได้ผลแต่สับสน · m = ถ้อยคำ)

- **H:** ไม่มี
- **M:** ข้อ 3 ควรเตือนเรื่องสต็อกร่วมของเทสต์ขนาน 3 เบราว์เซอร์ (เช่น "ตะกร้าที่สั่งซื้อจริงต้องไม่ทำให้สต็อก seed หมดเมื่อรัน 3 เบราว์เซอร์ และอย่าใช้สินค้าที่ TC-PRD-03/TC-CHK-04 ใช้") — ถ้าเลือก ชามกินช้า ×3 ใน 3 test จะเจอออเดอร์ล้มแบบสุ่มเฉพาะ `test:all`
- **M:** ตารางสรุปท้ายพรอมต์ควรบอกว่า expected-fail จะถูก reporter นับรวมใน "passed" (เช่น "ดู `x` ใน list หรือนับจาก tag `@known-issue`") ไม่งั้นผู้เรียนจะกรอก expected-fail = 0 จากบรรทัดสรุป
- **m:** "ปุ่มยืนยันสั่งซื้อ" → ระบุ testid `place-order` (ข้อความ "ยืนยันสั่งซื้อ ฿…") และ "หน้าคำสั่งซื้อ" = `/orders/PP-…` หลังกดสั่ง
- **m:** ข้อ 3 "ค่าขอบของคูปอง" — NEWCAT50 ไม่มีชุดสินค้าที่รวม ฿500 พอดี บอกได้ว่าใช้ค่าใกล้ที่สุดสองฝั่งได้

## ภาพที่ควรใช้ใน README (../design/shots/labN-*.png 1280×800 + คำอธิบาย 1 บรรทัด)

| ไฟล์ | คำอธิบาย |
|---|---|
| `lab4-cart-999-free.png` | หน้าตะกร้า ฿999 (ไม้ตกแมว + ทูน่าแพ็ค ×2 + แกะบด ×2) ขึ้น "ได้ส่งฟรีแล้ว!" ค่าจัดส่ง ฟรี ยอด ฿999 |
| `lab4-checkout-button-999.png` | หน้า checkout ปุ่ม "ยืนยันสั่งซื้อ ฿999" |
| `lab4-order-1049.png` | หน้าคำสั่งซื้อหลังกดยืนยัน: ค่าจัดส่ง ฿50 ยอดชำระ ฿1,049 (ตะกร้าเดียวกัน) |
| `lab4-report-char-money.png` | HTML report กรอง `char-money`: 141 Passed · Failed 0 · TC-CHAR-SHIP-03 (`known-issue`) แสดงเป็น ✓ |
