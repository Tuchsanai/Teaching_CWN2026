# LAB 6_RESULT · แก้ BUG-01 ที่ต้นเหตุ

| หัวข้อ | ค่า |
|---|---|
| เวลาเริ่ม · จบ · ใช้ไป | 2026-10-12 10:12 · 10:18 · ~6 นาที (เครื่อง ~2.5: build 12 s · bug01 spec 11 s · char-money 7 s · ทั้งชุด 26 s · bug01.mjs 93 s · agent ~3.5) |
| cwd ของเซสชัน / settings มีผลไหม | runner (Agent tool) cwd ไม่ใช่ `w/` → `w/CLAUDE.md` + `.claude/settings.json` **ไม่ได้ถูกบังคับโดย harness · runner ทำตามเองเคร่งครัด** (ทุกคำสั่งรันจาก `w/` ด้วย path เต็ม) |
| ไฟล์ที่สร้าง/แก้ | `petshop/lib/orders.ts` (+1 −7) · `e2e-legacy/tests/new/char-money.spec.ts` (SHIP-02/03 · `diff` 19 บรรทัดต่าง) · `BUG-01.md` (+ หัวข้อ "แก้แล้ว" · แถวสถานะ · 162 บรรทัด) · `out/bug01-before-fix/` (สำเนาผลก่อนแก้ ก่อนรัน bug01.mjs ทับ) |
| สคริปต์ชั่วคราว | ไม่สร้างใหม่ · ใช้ `rea\scratch\bug01.mjs` ของ LAB 5 · log ยาวใน `../tools/lab6/` (build.txt bug01-after.txt char-before-adjust.txt full-chromium.txt bug01-rerun.txt char-money.before.spec.ts) |
| โหมดการรัน · shell ที่ agent ใช้จริง | A · PowerShell tool (build/playwright/node/git diff --no-index) · Git Bash เฉพาะอ่านไฟล์/grep/append BUG-01.md (heredoc UTF-8) |
| timeout / รันซ้ำ | build timeout 15 นาที (จบใน 12 s เพราะ layer npm ci cached · `next build` รันจริง) · playwright 10–15 นาที · ไม่มีการสั่งซ้ำ |
| สถานะเว็บ | pawpantry05 healthy · build ล่าสุด container created 10:13:05 (+07) |
| ข้อมูลทดสอบ | reset 1 ครั้ง (ใน bug01.mjs) · ผู้ใช้สุ่มใหม่ `bug01-<ts>@test.dev` · test ใช้ผู้ใช้สุ่มต่อ test |

## ข้อห้ามที่ทำตาม (และที่พลาด ถ้ามี)
- ไม่แตะไฟล์เดิมใน `e2e-legacy/` / `TEST-DATA.md` ทั้งเครื่องมือและ shell · `git diff --stat -- e2e-legacy TEST-DATA.md` ว่าง (ตรวจหลังรันทั้งชุดและตอนจบ) · ไม่เลี่ยง deny ผ่าน shell
- ไม่แก้ผลที่คาดหวังใน `tests/new/bug01-shipping.spec.ts` · แก้เฉพาะ test คู่ legacy-quirk/KNOWN-ISSUE ตามข้อยกเว้นข้อ 3 พร้อมเหตุผลอ้าง BUG-01
- ไม่เปิด `_solution/` · ไม่อ่าน LAB อื่น · ไม่ใช้ git เปลี่ยนสถานะ · `git diff --no-index` เป็นรายไฟล์ (ไม่ diff ทั้งโฟลเดอร์)
- ไม่แตะ container `sabai06-*` / `exref-*` / `multi-account-devtool` · Playwright headless เท่านั้น

## คำตอบสรุปที่แสดงในแชท
> | test หรือกรณี | ก่อนแก้ | หลังแก้ |
> |---|---|---|
> | `bug01-shipping.spec.ts` (9 test) | 3 failed · 6 passed | 9 passed |
> | TC-CHAR-SHIP-02 (legacy-quirk ล็อก 1049) | passed | failed → ปรับค่าล็อกเป็น {0, 999} อ้าง BUG-01 → passed |
> | TC-CHAR-SHIP-03 (KNOWN-ISSUE test.fail) | expected-fail | "Expected to fail, but passed" → เอา test.fail() ออก → passed |
> | ชุดเดิม 40 test (chromium) | 40 passed | 40 passed |
> | ทั้งชุด chromium | — | 56 passed · 0 failed · 0 flaky (24.8 s) |
> | ฿999 ส่งธรรมดา (POST /api/orders ship·total) | 50 · 1049 ❌ | 0 · 999 ✅ |
> | ฿998 ส่งธรรมดา | 50 · 1048 | 50 · 1048 |
> | ฿1,000 ส่งธรรมดา | 0 · 1000 | 0 · 1000 |
> | ฿999 + PAW10 | 50 · 950 ❌ (ปุ่ม 900) | 0 · 900 ✅ |
> | ฿999 + FREESHIP | 0 · 999 | 0 · 999 |
> | ฿999 ส่งด่วน | 120 · 1119 | 120 · 1119 |
> | ฿998 + PAW10 | 50 · 949 | 50 · 949 |

## ตัวเลขสำคัญ (นับจากไฟล์จริง พร้อมคำสั่งที่ใช้นับ)
- diff โค้ด: `git diff --no-index --numstat out\v1\lib\orders.ts petshop\lib\orders.ts` → `1 7` (exit 1) · `git status --short petshop` → ไฟล์เดียว ` M petshop/lib/orders.ts`
- ไฟล์ที่แตะ = ตาราง impact แถว A ใน BUG-01.md (`lib/orders.ts:4-5` + `:63-67`) ไม่เกินตาราง
- ทั้งชุด: `grep -E "^\s+ok " full-chromium.txt` → 56 · ใน `tests\new`: bug01 9 · char-money 7 → เดิม 40
- bug01.mjs ใหม่: 7 กรณี ปุ่ม = server total = /account ทุกกรณี (บรรทัดผลใน `../tools/lab6/bug01-rerun.txt`)

## คำสั่งที่รัน
| คำสั่ง (จาก `w/`) | exit | เวลา | ผล |
|---|---|---|---|
| `cd petshop; docker compose up -d --build` | 0 | 12 s (+ healthy 2 s) | `next build` ✓ Compiled successfully in 1842ms · ส่วนใหญ่ CACHED |
| `npx playwright test tests/new/bug01-shipping.spec.ts --project=chromium --reporter=list` | 0 | 11 s | 9 passed (9.5 s) |
| `npx playwright test tests/new/char-money.spec.ts --project=chromium` (ก่อนปรับ test) | 1 | 7 s | 2 failed (SHIP-02 ค่า 50/1049 ≠ 0/999 · SHIP-03 Expected to fail, but passed) · 5 passed |
| `npx playwright test --project=chromium --reporter=list` (หลังปรับ) | 0 | 26 s | 56 passed (24.8 s) |
| `node rea\scratch\bug01.mjs` | 0 | 93 s | 7 กรณี · ทับ `out\bug01-blackbox.json` `out\bug01.har` (สำเนาก่อนแก้ใน `out\bug01-before-fix\`) |
| `git diff --no-index out\v1\lib\orders.ts petshop\lib\orders.ts` | 1 | — | +1 −7 |

## ตัวอย่างแถวเด่น 3–6 แถว (สำหรับ README)
- ฿999 ส่งธรรมดา: server ก่อน `{shipping 50, total 1049}` → หลัง `{shipping 0, total 999}` · /account ฿1,049 → ฿999
- ฿999 + PAW10: ปุ่ม ฿900 แต่คำสั่งซื้อ ฿950 → ทั้งคู่ ฿900
- diff ทั้งหมดคือ "ลบ" 7 บรรทัด (2 import + คอมเมนต์ PP-231 + บล็อก if 4 บรรทัด) เพิ่มคอมเมนต์ 1 บรรทัด
- test คู่ characterization พลิกตามคาด: legacy-quirk แดง + KNOWN-ISSUE "Expected to fail, but passed" = สัญญาณว่าพฤติกรรมเปลี่ยนจริง

## ตัดสินแทนผู้เรียน
| คำถาม | คำตอบ | ที่มา | เหตุผล |
|---|---|---|---|
| ก่อนเริ่ม: จะใช้วิธีไหน (BUG-01.md แนะนำ **A · ลบบล็อกซ้ำ** · มี B `>`→`>=` และ C ให้เลือก) | "ใช้วิธีที่ทำให้กฎเงินอยู่ที่เดียว (ลบการคำนวณค่าส่งซ้ำ) ไม่ใช่แค่เปลี่ยนเครื่องหมาย" → A | 🧑 | BUG-01.md แนะนำ A อยู่แล้ว → ผู้เรียนเห็นด้วย ไม่มีความขัดแย้งให้จด · agent **ไม่ได้** แก้แบบเปลี่ยนเครื่องหมายอย่างเดียว |
| คอมเมนต์ใหม่แทนบล็อก PP-231 ใส่ไหม | ใส่ 1 บรรทัดอ้าง BUG-01 | ตัดสินเอง | ให้คนถัดไปรู้ว่าทำไมไม่มีการคำนวณซ้ำ (+1 บรรทัด) |
| SHIP-02 (legacy-quirk) ปรับอย่างไร | เปลี่ยนค่าที่ล็อกเป็นค่าหลังแก้ + tag `@bug01-fixed` + annotation `changed-by-BUG-01` (ไม่ลบ test) | ตัดสินเอง ตามข้อยกเว้นข้อ 3 | ยังเป็น golden master ของ server ที่ ฿999 · ซ้ำกับ SHIP-03 บ้างแต่เก็บประวัติไว้ |
| SHIP-03 (KNOWN-ISSUE) | เอา `test.fail()` ออก · ค่าคาดเดิม | ตัดสินเอง (ตรงกับที่ BUG-01.md ข้อ 5 เขียนไว้) | ค่าตาม TEST-DATA ไม่เปลี่ยน |
| ข้อ 5 "ยิง API ซ้ำ" ใช้อะไร | รัน `rea\scratch\bug01.mjs` เดิม (ยิง POST /api/orders ผ่าน UI ทุกกรณี + อ่านหน้าคำสั่งซื้อ//account) หลังสำรองผลก่อนแก้ไป `out\bug01-before-fix\` | ตัดสินเอง | ได้ทุกคอลัมน์ของตารางเดิม และไม่ทำหลักฐานก่อนแก้หาย |

## ข้อสังเกต 👀
- เพราะ LAB 4 วางคู่ legacy-quirk + KNOWN-ISSUE ไว้ การแก้ทำให้ 2 ข้อพลิก "พร้อมกัน" ในทิศที่คาด — เป็นภาพสอนที่ดีว่า characterization test ไม่ได้ "ผิด" แต่เป็นเสียงเตือนว่าพฤติกรรมเปลี่ยน และต้องตัดสินใจอย่างมีเอกสาร
- build เร็วมาก (12 s) เพราะแก้แค่ไฟล์ใน lib → layer `npm ci` cached · ข้อความ "นาน ~3 นาที" ในพรอมต์เป็นกรณีแย่สุด
- `bug01.mjs` เขียนทับ `out\bug01.har`/`blackbox.json`/ภาพของ LAB 5 — ถ้าไม่สำรองก่อน หลักฐาน "ก่อนแก้" ที่ BUG-01.md อ้างจะหาย
- PAW10 ที่ ฿999 หลังแก้ = ฿900 (ฟรีค่าส่ง นับก่อนส่วนลด) — ยังเป็นคำถามธุรกิจ ("ยังไม่รู้" ข้อ 2) ไม่ใช่ข้อยุติ

## ปัญหา / วิธีแก้
- ไม่มีปัญหาขวาง · `git diff --no-index` exit 1 ตามที่พรอมต์เตือน

## ข้อเสนอแก้พรอมต์
- M: ข้อ 5 ไม่บอกว่าต้องเก็บผลก่อนแก้ไว้ — ถ้าใช้สคริปต์ LAB 5 ซ้ำจะเขียนทับหลักฐาน · เสนอเพิ่ม "ถ้าสคริปต์เขียนทับไฟล์ใน out\ ให้คัดผลเดิมไป out\bug01-before-fix\ ก่อน"
- m: "(นาน ~3 นาที)" → "(ครั้งแรกนาน ~3 นาที · แก้ไฟล์เดียวมักไม่ถึงนาที)"
- m: ข้อ 3 อาจระบุว่าการปรับ test คู่ควรเปลี่ยน tag/annotation ด้วย (ไม่ใช่แค่ค่า) เพื่อไม่ให้ยังเรียกตัวเองว่า legacy-quirk

## ภาพที่ควรใช้ใน README
- `../design/shots/lab6-c999-order-before.png` — หน้าคำสั่งซื้อ ฿999 ก่อนแก้: ค่าส่ง ฿50 ยอด ฿1,049 (ภาพจาก LAB 5 · 1280×800 viewport)
- `../design/shots/lab6-c999-order-after.png` — หน้าคำสั่งซื้อเดียวกันหลังแก้: ค่าส่ง ฟรี ยอด ฿999
