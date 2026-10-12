# 🔑 เกณฑ์ตรวจผู้สอน · บท 05 รับช่วงระบบเดิม PawPantry (REA + legacy)

> ⚠️ **สำหรับผู้สอนเท่านั้น · ห้ามคัดลง README** · README แสดงเฉพาะรูบริก 20 ข้อ (ข้อ 2 ของไฟล์นี้ ข้อความเดียวกัน) ส่วนหมายเหตุผู้ตรวจ เฉลย BUG-01 / CR-01 และผลที่คาดหวังของ REA อยู่ที่นี่ที่เดียว
> ที่มา: `_design/LESSON-PLAN.md` §2 §4 §4.1 · `_design/PROMPTS.md` (🎯 ทุก LAB) · `_design/CR-DESIGN.md` (BUG-01 · CR-01 · PR-1 · **A5 รันจริงบน prototype**) · `_design/CODEBASE-NOTES.md` · `_design/REA-THEORY.md` · `_design/REA-FEASIBILITY.md` + `_design/rea-probe/evidence/` (**A1 รันจริง**) · `_design/REVIEW-PLAN-V1.md`
> เลขบรรทัดอ้างไฟล์ใน `petshop/` ตอนเริ่มบท (มี BUG-01 อบอยู่ · ไม่มี BUG_MODE · ตรวจกับไฟล์จริง 12 ต.ค. 2026) · ตัวเลขผลจริงของรอบถ่ายทำอยู่ใน [README.md](README.md) ข้อ 2 และ `_design/results/LAB*_RESULT.md` · ค่าในไฟล์นี้เป็น **ผลที่ต้องได้** (จากการรันของ A1/A5) ใช้เทียบกับงานผู้เรียน

## สารบัญ

1. [วิธีให้คะแนน](#1-วิธีให้คะแนน)
2. [รูบริก 20 ข้อ (ข้อความเดียวกับ README) + วิธีตรวจ](#2-รูบริก-20-ข้อ-ข้อความเดียวกับ-readme--วิธีตรวจ)
3. [ตรวจทีละ LAB](#3-ตรวจทีละ-lab)
4. [เฉลย BUG-01: ต้นเหตุ · วิธีแก้ที่ถูก · กับดัก](#4-เฉลย-bug-01-ต้นเหตุ--วิธีแก้ที่ถูก--กับดัก)
5. [เฉลย CR-01: คำถามร้าน · impact · ค่าขอบ](#5-เฉลย-cr-01-คำถามร้าน--impact--ค่าขอบ)
6. [เฉลย PR-1 (LAB 10)](#6-เฉลย-pr-1-lab-10)
7. [ผลที่คาดหวังจาก REA + ป้าย authority](#7-ผลที่คาดหวังจาก-rea--ป้าย-authority)
8. [หมายเหตุผู้ตรวจ (LESSON-PLAN §4.1)](#8-หมายเหตุผู้ตรวจ-lesson-plan-41)

---

## 1. วิธีให้คะแนน

| เรื่อง | กติกา |
|---|---|
| คะแนนเต็ม | 20 ข้อ ข้อละ 1 · **ดีมาก ≥ 18 · ใช้ได้ 14–17 · ต้องแก้ < 14** |
| หลักฐาน | ให้คะแนนจาก **ไฟล์ในโฟลเดอร์บทของผู้เรียน** (`*.md` · `e2e-legacy/tests/new/` · `petshop/` · `out/`) ไม่ใช่จากคำพูดในแชท · ไม่มีหลักฐานในไฟล์ = 0 |
| ครึ่งคะแนน | ไม่มี · ก้ำกึ่งให้ดูว่า "ข้อห้าม" ในคอลัมน์ "ได้ 0 ถ้า" เกิดขึ้นไหม ถ้าไม่เกิดให้ 1 |
| LAB 0 | ไม่มีคะแนน แต่เป็นเงื่อนไขก่อนตรวจ: ไม่มี `rea-lab:6.4.0` / เว็บ :4000 ไม่ healthy = LAB 2 3 9 ไม่มีหลักฐาน REA → ข้อ 4 5 17 18 = 0 |
| ธงแดง (ตัดทันที) | อบ ฿1,049 เป็นผลที่คาดหวัง → ข้อ 8 = 0 (และมักลามข้อ 10) · แก้ไฟล์เดิมใน `e2e-legacy/` หรือรัน `-u` → ข้อ 19 = 0 และผล regression ข้อ 16 ใช้ไม่ได้ · มีรหัสผ่าน/cookie ในไฟล์ `.md` หรือ commit `.har` → ข้อ 5 = 0 · แก้ BUG-01 ด้วย `>`→`>=` อย่างเดียวและไม่ย้อนแก้ → ข้อ 12 = 0 (ดูข้อ 4.4) |
| AI ไม่ deterministic | ตัวเลขนับ (จำนวน endpoint · ตัวนับ s2b · เวลา) ต่างจากตารางนี้เล็กน้อยได้ · ที่ **ต้องตรงเป๊ะ** คือยอดเงินทุกกรณีในข้อ 4 และ 5 (คำนวณจากราคาจริงใน `lib/products.ts`) |

---

## 2. รูบริก 20 ข้อ (ข้อความเดียวกับ README) + วิธีตรวจ

**A. เข้าใจระบบ (LAB 1–3)** 1. ทุกแถวใน CODEBASE-MAP มี "ยืนยันจาก" ไฟล์:บรรทัด และแถว "เดา" ≤ 10% · 2. ตาราง "เอกสารบอก ≠ โค้ดทำ" เจอเรื่องเก่าใน HANDOVER-NOTES ครบ 2 ข้อ และไม่ตัดสินเอง · 3. CLAUDE.md ≤ 60 บรรทัด มีคำสั่งรัน พอร์ต 4000 ห้ามแตะ กติกาการแก้ และ settings.json กันไฟล์เดิมได้จริง · 4. SYSTEM-MAP ติดป้าย 🔵🟢🟡⚪ ทุกแถว ไม่มีข้อ "ไม่เจอ" ที่สรุปว่า "ไม่มี" · 5. API-INVENTORY ไม่มีรหัสผ่าน/cookie และอธิบาย 3 วิธีดูระบบได้
**B. ล็อก (LAB 4)** 6. รัน suite เดิม 3 เบราว์เซอร์ก่อนแตะโค้ด · 7. golden master ตรวจเงินครบ 4 จุดของตะกร้าเดียวกัน · 8. ค่าที่ [E] ขัด [D] ไม่ถูกอบเป็นผลที่คาดหวัง
**C. BUG-01 (LAB 5–6)** 9. ทำซ้ำแบบ black-box และหาขอบเขตอาการ (กรณีข้างเคียง) ก่อนเปิดโค้ด · 10. test แดงก่อนแก้ ด้วยผลที่คาดหวัง [D] · 11. ต้นเหตุระบุไฟล์:บรรทัด และตรวจคอมเมนต์ในโค้ดตรงนั้นกับหลักฐาน HAR (ไม่เชื่อคอมเมนต์ทันที) · 12. แก้ที่ต้นเหตุ ไม่ใช่ปลายเหตุ และอธิบายได้ว่าทำไมวิธีที่เลือกเป็นต้นเหตุ
**D. CR-01 (LAB 7–8)** 13. ถามร้านก่อน ≥ 2 เรื่อง พร้อมตัวเลขที่ต่างกัน · 14. impact ครอบทุกจุดที่คำนวณ **และแสดง** เงิน (หน้าและ API) โดยตรวจด้วยการค้นโค้ด ไม่ใช่เดาจากชื่อไฟล์ · 15. TC มีค่าขอบ ±1 บาท + API ส่ง giftWrap ผิดชนิด · 16. TC-GIFT แดงก่อน → เขียวหลัง และ regression 3 เบราว์เซอร์ไม่มีข้อเดิมล้ม
**E. พิสูจน์ส่งมอบ (LAB 9–10)** 17. รายการไฟล์ที่ตั้งใจแก้ = ไฟล์ที่ hash ต่าง = ไฟล์ที่ REA บอกว่า bundle ต่าง (หรืออธิบายส่วนเกิน) · 18. CHANGE-REPORT ทุกตัวเลขอ้างไฟล์ผล + มี evidence_id + rollback · 19. ไม่มีการรัน `-u` หรือแก้ test เดิมให้ผ่าน · 20. PR-1 ทำครบวงจรในพรอมต์เดียว (แดง → ถามก่อนแก้ → เขียว → regression)

คำสั่งตรวจรันจาก **รากบทของผู้เรียน** ด้วย Git Bash (หรือแปลงเป็น `Select-String` ใน PowerShell)

| ข้อ | ไฟล์หลักฐาน | ได้ 1 เมื่อ | ได้ 0 ถ้า | ตรวจเร็ว |
|---|---|---|---|---|
| ข้อ 1 | `CODEBASE-MAP.md` | ส่วน A–F ทุกแถวมีคอลัมน์ "ยืนยันจาก" เป็น `ไฟล์:บรรทัด` · แถว "เดา" ≤ 10% ของทั้งหมด | ไม่มีคอลัมน์ · อ้างแค่ชื่อไฟล์ไม่มีบรรทัด · เดา > 10% | `grep -c "เดา" CODEBASE-MAP.md` เทียบจำนวนแถว · สุ่มเปิด 3 แถวดูว่าบรรทัดตรงจริง |
| ข้อ 2 | `CODEBASE-MAP.md` ส่วน G | มีทั้ง **SUMMER20** และ **"ทุกหน้าดึงผ่าน `/api/products`"** เป็น ⚠️/❌ และเขียนเป็นคำถามถึงร้าน | ขาดข้อใด · เขียนว่า "เอกสารผิด แก้แล้ว" (ตัดสินเอง) | `grep -n "SUMMER20\|api/products" CODEBASE-MAP.md` |
| ข้อ 3 | `CLAUDE.md` · `.claude/settings.json` | ≤ 60 บรรทัด · มี `4000` · คำสั่งรัน/เทสต์/REA · ห้ามแตะ (ทั้งเครื่องมือแก้ไฟล์และ shell) · กติกาการแก้ · `permissions.deny` แบบ `Edit(...)` ที่ลองแก้ไฟล์เดิมแล้วถูกปฏิเสธ และสร้างไฟล์ใน `tests/new/` ได้ | ใช้ `@CODEBASE-MAP.md` (โหลดทุกเซสชัน ทำให้ LAB 5 ไม่ black-box) · deny ด้วย `Write(...)` อย่างเดียว · glob กัน `tests/new/` ไปด้วย | `wc -l < CLAUDE.md` · `grep -c "@CODEBASE-MAP" CLAUDE.md` = 0 · `grep -n "Edit(" .claude/settings.json` |
| ข้อ 4 | `SYSTEM-MAP.md` | ทุกแถวส่วน A B มีป้ายหนึ่งใน 🔵🟢🟡⚪ · แถว ❓ ไม่เจอ มีเหตุผลที่เป็นไปได้ · มี `evidence_id` | มีประโยค "ไม่มี API นี้" / "ไม่ได้ใช้" จากผล static | `grep -n "ไม่มี" SYSTEM-MAP.md` แล้วอ่านบริบท |
| ข้อ 5 | `API-INVENTORY.md` | ไม่มี `Paw12345` / ค่า cookie / อีเมลจริง · ส่วน D อธิบาย analyze build · HAR · scenario (ใครคุมเบราว์เซอร์ · มีผลกับข้อมูลไหม · บอกอะไรได้/ไม่ได้) · 2 บรรทัดว่าทำไม HAR ห้ามส่งต่อ | มีค่าลับในไฟล์ `.md` ใด ๆ · `.har` ถูก track ใน git | `grep -rln "Paw12345\|pp_session=" --include=*.md .` = ว่าง · `git ls-files "*.har"` = ว่าง |
| ข้อ 6 | `BASELINE.md` | ผล `npx playwright test` + `npm run test:all` แยกเบราว์เซอร์ **ก่อน** LAB 6 แก้โค้ด | รันแค่ chromium · รันหลังแก้โค้ดแล้ว | เวลาใน BASELINE เทียบเวลาแก้ `petshop/lib/orders.ts` |
| ข้อ 7 | `e2e-legacy/tests/new/char-money.spec.ts` | ตะกร้า **เดียวกัน** ตรวจเงิน 4 จุด: หน้าตะกร้า · ปุ่มยืนยัน · response POST `/api/orders` · หน้าคำสั่งซื้อ | ตรวจแค่หน้าตะกร้า/แค่ API · คนละตะกร้าในแต่ละจุด | อ่าน spec หา 4 assertion ต่อเคส |
| ข้อ 8 | spec ข้อ 7 + `BASELINE.md` "ผู้ต้องสงสัย" | ค่าที่ขัด [D] เป็น test คู่ `legacy-quirk` + `test.fail` `KNOWN-ISSUE` (ดู [ข้อ 8](#8-หมายเหตุผู้ตรวจ-lesson-plan-41) แถว 8) · ถ้าไม่ได้เลือกตะกร้า ฿999 เลย = ไม่มีค่าที่ขัด → ได้ 1 ถ้าไม่มีค่าใดอบบั๊ก | `expect(...).toBe(1049)` หรือ `toContainText("1,049")` เป็นผลที่คาดหวังเดี่ยว ๆ | `grep -rn "1049\|1,049" e2e-legacy/tests/new/` แล้วดูว่ามี `test.fail`/annotation คู่ |
| ข้อ 9 | `BUG-01.md` (อาการ · ขั้นตอนทำซ้ำ · ตารางกรณี) · `out/bug01.har` | ทำซ้ำบน `localhost:4000` ก่อนเปิดโค้ด · ตารางกรณีข้างเคียง ≥ 4 (฿998 · ฿999+PAW10 · ฿999+FREESHIP · ฿999 ด่วน) และสรุปว่าผิดเฉพาะกรณีไหน | อ้างต้นเหตุในโค้ดก่อนมีผลทำซ้ำ · ไม่มีกรณีข้างเคียง | ลำดับหัวข้อใน BUG-01.md · `ls out/bug01.har` |
| ข้อ 10 | `e2e-legacy/tests/new/bug01-shipping.spec.ts` + ผลรันก่อนแก้ | ชื่อขึ้นต้น `BUG-01` · คาด ฿999 / `shipping: 0` ตาม [D] · มีข้อ "เงินบนปุ่ม = เงินในคำสั่งซื้อ" · แดงด้วยเหตุผลเรื่องเงิน (ไม่ใช่ timeout/locator) | ผลที่คาดหวังลอกจากเว็บ · แดงเพราะหา element ไม่เจอ | ผลรันใน BUG-01.md "ก่อน/หลัง" |
| ข้อ 11 | `BUG-01.md` ต้นเหตุ | ชี้ `lib/orders.ts` บล็อก `// PP-231` (`:63-67`) + กฎจริง `lib/pricing.ts` `shippingCost()` (`:130-133`) · **ตรวจคอมเมนต์กับ HAR**: body POST `/api/orders` ไม่มีค่าส่ง/ยอด → คอมเมนต์ไม่ตรงความจริง | บอกแค่ "เครื่องหมาย `>` ผิด" ไม่พูดถึงการคำนวณซ้ำ/เขียนทับ · เชื่อคอมเมนต์ว่าเป็นการกันโกงที่ต้องคงไว้ | ดูข้อ 4.2–4.3 |
| ข้อ 12 | `BUG-01.md` impact + "แก้แล้ว" · `petshop/lib/orders.ts` | ลบบล็อกคำนวณซ้ำ + import ที่ไม่ใช้ · ให้เหตุผลว่ากฎเงินต้องอยู่ที่เดียว (`computeTotals`) และวิธี `>=` ปิดแค่อาการ | เหลือโค้ดใน `orders.ts` ที่เขียน `totals.shipping`/`totals.total` หลัง `computeTotals` | `grep -n "FREE_SHIPPING_MIN\|totals\.total =\|totals\.shipping =" petshop/lib/orders.ts` = ว่าง |
| ข้อ 13 | `CR-01.md` คำถาม + คำตอบ | ≥ 2 เรื่องจาก [ข้อ 5.1](#51-คำถามที่ควรถามร้าน--คำตอบร้าน) แต่ละเรื่องมีตะกร้าตัวอย่างที่ยอดต่างกันตามการตีความ · จดคำตอบร้านก่อนเขียน TC | ถามโดยไม่มีตัวเลข · ตอบเองโดยไม่ถาม | — |
| ข้อ 14 | `CR-01.md` impact | มีครบ 6 ไฟล์ใน [ข้อ 5.2](#52-impact-ที่ต้องได้) โดยเฉพาะ `app/orders/[id]/page.tsx` · มีรายการ "ไม่ต้องแตะแต่ตรวจแล้ว" (`app/api/orders/route.ts` · `app/account/page.tsx`) · คอลัมน์ "ใครเรียกใช้" เป็นผลค้นหา (grep) | ขาดหน้า `/orders/[id]` · อ้างแค่ชื่อไฟล์ไม่มีผลค้นหา | `grep -n "orders/\[id\]" CR-01.md` |
| ข้อ 15 | `CR-01.md` TC + `cr01-giftwrap.spec.ts` | มีคู่ ฿1,499 / ฿1,500 · มี `giftWrap: "true"` และ/หรือ `1` ผ่าน API ที่ต้องได้ ฿239 | ขอบไกลกว่า ±1 · ไม่มีกรณีผิดชนิด | ดูข้อ 5.3 |
| ข้อ 16 | `CR-01.md` "ผลรอบแรก" + "ทำแล้ว" | รอบแรกแดงเพราะ "ยังไม่มีฟีเจอร์" (หา `gift-wrap` ไม่เจอ · ไม่มี field `giftWrap`) · หลังทำเขียวทุกข้อ · `npm run test:all` ไม่มีข้อเดิมล้ม | ไม่มีผลรอบแรก · ข้อเดิมล้มแต่ส่งงาน · regression แค่ chromium | ตาราง 3 เบราว์เซอร์ใน CR-01.md |
| ข้อ 17 | `CHANGE-PROOF.md` | ตาราง 3 รายการ (ตั้งใจแก้ · SHA-256 ต่าง · REA บอกต่าง) ตรงกัน หรือส่วนเกินมีคำอธิบาย (เช่นไฟล์ที่ `next build` เขียนเอง) · ตัวนับ s2b ครบ 7 คลาสทุกคู่ | มีไฟล์ต่างที่อธิบายไม่ได้ · ใช้ unknown = "ไฟล์หาย" | ดูข้อ 7 แถว s2b |
| ข้อ 18 | `CHANGE-REPORT.md` | ทุกตัวเลขอ้างไฟล์ผล · มี `evidence_id` (8 ตัวแรกพอ) · มีวิธี rollback · มี "สิ่งที่หลักฐานยังพิสูจน์ไม่ได้" | ตัวเลขลอย ไม่มีที่มา · ไม่มี rollback | — |
| ข้อ 19 | `e2e-legacy/` ทั้งโฟลเดอร์ | ไฟล์เดิม (10 spec + `fixtures.ts` + config) ไม่เปลี่ยน · ไม่มี `-u`/`--update-snapshots` · ข้อยกเว้นเดียว: ปรับ test **คู่** ใน `tests/new/` หลังแก้ BUG-01 พร้อมเหตุผลอ้าง BUG-01 | ไฟล์เดิมเปลี่ยน · แก้ผลที่คาดหวังใน `bug01-*`/`cr01-*` ให้ผ่าน | `git diff --stat -- e2e-legacy/tests/*.ts e2e-legacy/*.ts e2e-legacy/package.json TEST-DATA.md` = ว่าง |
| ข้อ 20 | `tests/new/pr1-*.spec.ts` · แถว PR-1 ใน `CHANGE-REPORT.md` | ในพรอมต์ LAB 10 เดียว: test แดงก่อน → ถามก่อนแก้ (มีบันทึกคำถาม) → เขียว → chromium + 3 เบราว์เซอร์ | แก้ก่อนเขียน test · ไม่ถามก่อนแก้ · ไม่มี regression | ดูข้อ 6 |

---

## 3. ตรวจทีละ LAB

### LAB 0 · เช็กเครื่อง (ไม่มีคะแนน)

| ตรวจ | ต้องได้ | ผิดบ่อย |
|---|---|---|
| พอร์ต | อธิบายได้ว่า 3000 อยู่ในช่วงที่ Windows/WinNAT จอง (`netsh … excludedportrange`) จึงใช้ 4000 | สั่งปิด/เปลี่ยน winnat เอง · ไปใช้ 3000 |
| `rea.ps1 doctor` | รันผ่าน `-ExecutionPolicy Bypass -File` · exit 1 ได้ (hopper/ghidra/ida = `missing_analysis_engine` · `skill:identity` = `config_drift`) และสรุปว่า **ไม่กระทบงานเว็บ** | เห็น exit 1 แล้วหยุด/พยายามติดตั้ง Ghidra · เปลี่ยน ExecutionPolicy ของเครื่อง |
| เว็บ + network | container `pawpantry05` healthy · `localhost:4000/api/health` = `{"ok":true}` · probe ใน `pawpantry05_default` ไปที่ `http://petshop:3000` = `{"ok":true}` | สับสน 2 ที่อยู่ (`localhost:4000` = เรา · `petshop:3000` = REA ใน network) · ไป recreate container ของบท 02/03 |

### LAB 1 · CODEBASE-MAP + CLAUDE.md (รูบริก 1 2 3)

| ส่วน | ข้อเท็จจริงที่ต้องเห็น (ตรวจกับโค้ดได้) | ผิดบ่อย |
|---|---|---|
| A | Next.js App Router · ข้อมูล server อยู่ใน RAM (`globalThis.__pawpantryStore` ใน `lib/store.ts`) · browser: localStorage `pp-cart` `pp-wishlist` `pp-recent` `pp-coupon` · ไม่มี DB | บอกว่ามีฐานข้อมูล · ลืม `pp-recent`/`pp-coupon` |
| B C | 11 หน้า + not-found · **12 API route** (`app/api/**/route.ts`) · `/api/orders` ต้อง login (401) · `/api/test/reset` ขึ้นกับ `ALLOW_TEST_RESET` | นับ route ขาด `products/[slug]` `orders/[id]` `test/reset` |
| D | กฎเงินอยู่ `lib/pricing.ts` (`shippingCost` `:130-133` · `computeTotals` `:135-`) · ข้อความ "฿50/฿120/ส่งฟรี" ฮาร์ดโค้ดในหลาย component · หน้า `/orders/[id]` เขียนสรุปเงินเอง · (ถ้าเจอบล็อก `PP-231` ใน `lib/orders.ts` ก็ **ถูก** = ค้นพบแบบ white-box ไม่หักคะแนน) | เขียนว่า "กฎเงินอยู่ที่เดียว" โดยไม่เห็น `orders.ts` ก็ไม่ผิด แต่ต้องไม่สรุปว่า "ไม่มีที่อื่น" |
| F | ชุดเดิมตรวจเงินที่หน้าตะกร้าเป็นหลัก · ไม่มีข้อที่สั่งซื้อจนจบที่ ฿999 (ถ้าเห็นตอนนี้ = ดีมาก) | เชื่อชื่อ test TC-CART-03 ว่าตรวจ ฿999 |
| G | ดู [ข้อ 3.1](#31-เรื่องเก่าใน-handover-notesmd-รูบริกข้อ-2) | — |
| I | A B C E F = redocumentation · D G = design recovery · ตาที่ใช้ = white-box ทั้งหมด · H = สิ่งที่ต้องใช้ black/grey-box · ยังไม่ใช่ re-engineering เพราะยังไม่เปลี่ยนระบบ | จัด LAB 1 เป็น re-engineering |

#### 3.1 เรื่องเก่าใน `HANDOVER-NOTES.md` (รูบริกข้อ 2)

| บรรทัดใน HANDOVER-NOTES | โค้ดทำ | ป้าย | คำถามถึงร้านที่ดี |
|---|---|---|---|
| **"คูปองที่ใช้อยู่: … SUMMER20 ลด 20% ใช้ได้ถึงสิ้นปี"** (ต้องเจอ) | `lib/pricing.ts:123-124` `case "SUMMER20": return fail(COUPON_MESSAGES.expired)` · TEST-DATA [D] ก็บอก "หมดอายุ" | ❌ | "SUMMER20 ยังต้องใช้ได้ไหม ถ้าใช้ได้ ลดเท่าไรและถึงวันไหน" |
| **"ทุกหน้าดึงรายการสินค้าผ่าน `GET /api/products`"** (ต้องเจอ) | หน้า `/` `/products` `/products/[slug]` เป็น server component เรียก `lib/` ตรง · `fetch("/api/products")` มีที่เดียว `components/ShopProvider.tsx:262` (`refreshStock` หลังสั่งซื้อ) | ❌ / ⚠️ | "ถ้าจะแก้ข้อมูลสินค้า ต้องแก้ที่ `lib/products.ts` ไม่ใช่ API — ยืนยันได้ไหมว่าไม่มีระบบอื่นเรียก API นี้" |
| "ตะกร้าและรายการโปรดเก็บใน localStorage" (โบนัส) | ถูก แต่ไม่ครบ: มี `pp-recent` `pp-coupon` ด้วย | ⚠️ | — |
| "ชุดเทสต์ … ผ่านครบทุกข้อก่อน deploy" (โบนัส) | จริง (ชุดเดิมเขียว) แต่ไม่มีข้อที่ตรวจคำสั่งซื้อ ฿999 → **เขียว ≠ ไม่มีบั๊ก** | ⚠️ | — |
| "งานค้าง: ไม่มี" (โบนัส · มักเห็นหลัง LAB 10) | มีบั๊ก toast เพิ่มลงตะกร้า (PR-1) อยู่ในโค้ด | ⚠️ | — |
| คอมเมนต์ `// PP-231: server must not trust the shipping fee shown in the browser` (โบนัส · ถ้าเจอใน LAB 1) | `CheckoutForm.tsx:76` ส่งแค่ `{ items, coupon, shipping, payment, address }` ไม่มีค่าส่ง → คอมเมนต์อ้างสิ่งที่ไม่เกิด | ⚠️ (ยืนยันด้วย HAR ใน LAB 5) | — |

ได้ 0 ถ้า: แก้ HANDOVER-NOTES เอง · ตัดสินว่า "เอกสารผิด" โดยไม่มีคำถามถึงร้าน

### LAB 2 · REA ส่อง build → SYSTEM-MAP (รูบริก 4)

ตรวจกับ [ข้อ 7](#7-ผลที่คาดหวังจาก-rea--ป้าย-authority) · สิ่งที่ต้องมี: `out\v1\.next\` (build สำเร็จ) · digest ของ static/server · ส่วน B แถวละ "ยืนยันด้วยตา" · ส่วน C 5 ข้อ (ข้อ 3 อ้าง skill ของ REA "Skip REA for ordinary source-repository architecture analysis" · ข้อ 5 นับแถว 2 ตา/ตาเดียว)

ผิดบ่อย: เปิดไฟล์ JSON ~54 MB ตรง ๆ จน context เต็ม (พรอมต์ห้าม · ให้ใช้ `rea-summarize.mjs`) · สรุป "ไม่มี `/api/recommendations`" · บอกว่า PawPantry เป็น Electron เพราะเห็น `electron-renderer` · แก้ `out\v1` ทีหลัง (ต้องเก็บไว้เทียบใน LAB 6 8 9)

### LAB 3 · HAR + scenario → API-INVENTORY (รูบริก 5)

| ตรวจ | ต้องได้ (A1 รันจริง) | ผิดบ่อย |
|---|---|---|
| ส่วน A | API 4 ตัวจาก HAR: POST `/api/coupons/validate` 200 (`code, items` → `ok, code, discount, freeShipping, message`) · POST `/api/auth/login` 200 · POST `/api/orders` 201 (`items, coupon, shipping, payment, address` → `order, id`) · GET `/api/products` 200 | ใส่ค่า body ของ login ลงตาราง |
| ส่วน B | storage key จาก scenario: `pp-recent` `pp-cart` `pp-coupon` → เปลี่ยน ⚪ เป็น 🟢 พร้อมไฟล์ `out\scenario.json` | เปลี่ยนเป็น 🟢 โดยอ้างโค้ด (นั่นคือ white-box ไม่ใช่ runtime) |
| ส่วน C | API ที่ไม่เห็นรอบนี้ (`/api/recommendations` `/api/orders/[id]` `/api/auth/me` …) = "ไม่ได้ถูกเรียกในรอบนี้" + วิธีเก็บเพิ่ม | "API นี้ไม่ได้ใช้งาน" |
| ส่วน D | analyze build = ไม่มีใครคุมเบราว์เซอร์ ไม่มีผลกับข้อมูล · HAR = คน/สคริปต์คุม (บันทึกย้อนหลัง · REA ไม่ยิงซ้ำ) · scenario = REA คุม Playwright · มีผลข้างเคียง (ตะกร้า/คูปอง) | บอกว่า HAR ยิง request ใหม่ |
| ความลับ | `Paw12345` ไม่อยู่ใน `out\har.json` แต่อยู่ใน `.har` ต้นฉบับ · `.gitignore` กัน `out/` `*.har` | ลบ `--sensitive-value` เพราะคิดว่า REA ตัดให้หมด |
| 👀 | URL ในผล scenario เป็น `petshop:3000` เพราะ REA อยู่ใน docker network เดียวกับเว็บ | คิดว่า REA ส่องเว็บคนละตัว |

### LAB 4 · characterization (รูบริก 6 7 8)

- ชุดเดิม: ค่าอ้างอิง `e2e-legacy/README-LEGACY.md` = chromium 40 passed · 3 เบราว์เซอร์ 120 passed (ผลรอบถ่ายทำดู README ข้อ 2) · ถ้าผู้เรียนเจอข้อล้ม ต้องหยุดถามก่อน (พรอมต์ข้อ 1)
- ตารางช่องว่างที่ดี: TC-CART-03 ชื่อ "ซื้อครบ ฿999 ได้ส่งฟรี" แต่ตรวจ ฿790 / ฿2,680 ที่หน้าตะกร้า (`05-cart.spec.ts`) · TC-CHK-03 สั่งซื้อจริงที่ ฿378 + FREESHIP (`08-checkout.spec.ts`) · **ไม่มีข้อสั่งซื้อจริงที่ ฿999 พอดี** · ไม่มีข้อเทียบปุ่มกับคำสั่งซื้อ
- golden: `/api/products` 28 รายการ (ตัด `stock`) · `/api/coupons/validate` PAW10 / FREESHIP / NEWCAT50 / SUMMER20 / โค้ดมั่ว · เทียบด้วย `toEqual` ไม่ใช่ `toMatchSnapshot`
- ถ้าเลือกตะกร้า ฿999 → เจอ ฿1,049 → ต้องเป็น test คู่ (ข้อ 8 ของ [หมายเหตุผู้ตรวจ](#8-หมายเหตุผู้ตรวจ-lesson-plan-41)) · ถ้าไม่เลือก ไม่หักคะแนน แต่ควรมี 👀 "golden master ล็อกแค่ที่เราเลือกดู"
- ผิดบ่อย: เรียก `/api/test/reset` ในเทสต์ใหม่ (ชุดเดิมรันขนาน 4 workers) · ล็อกเลขคำสั่งซื้อ/สต็อกตรง ๆ (flaky) · รัน `tests/new` รอบเดียว (พรอมต์ให้ 2 รอบดูความนิ่ง)

### LAB 5 · BUG-01 ทำซ้ำ → แดง → ต้นเหตุ (รูบริก 9 10 11)

ตารางกรณีที่ต้องได้ → [ข้อ 4.1](#41-อาการและขอบเขต-black-box) · ต้นเหตุ → [ข้อ 4.2](#42-ต้นเหตุ-white-box) · impact 2 วิธี → [ข้อ 4.4](#44-วิธีแก้-2-แบบ-และกับดักของ-) · ผิดบ่อย: ไปหาเลขคำสั่งซื้อของลูกค้าในเครื่องทดสอบ (เลขแรกหลัง reset เป็นของสคริปต์ HAR ไม่ใช่ลูกค้า) · test แดงเพราะ locator · เปิด CODEBASE-MAP ส่วน D ก่อนทำซ้ำ (ขั้นที่ 1 ห้าม)

### LAB 6 · แก้ BUG-01 (รูบริก 12)

ต้องได้: แตะ `petshop/lib/orders.ts` ไฟล์เดียว · ลบ import `FREE_SHIPPING_MIN` `STANDARD_SHIPPING` + บล็อก `:63-67` (−12/+1 บรรทัดโดยประมาณ) · build ผ่าน · `bug01-shipping` เขียว · ชุดเดิม chromium ไม่มีข้อล้ม · test คู่ของ LAB 4 ปรับพร้อมเหตุผลอ้าง BUG-01 · ยิง API ซ้ำ: ฿999 → 999 · ฿999+PAW10 → 900 · ที่เหลือเท่าเดิม · `git diff --no-index` exit 1 = มีความต่าง (ไม่ใช่ error)

### LAB 7 · CR-01 ถาม → impact → test แดง (รูบริก 13 14 15)

→ [ข้อ 5](#5-เฉลย-cr-01-คำถามร้าน--impact--ค่าขอบ) · รอบแรกที่ถูก: test UI แดงเพราะหา `gift-wrap` ไม่เจอ · test API แดงเพราะไม่มี field `giftWrap`/`giftWrapFee` · ข้อ "ส่งผิดชนิดแล้วยอด ฿239" **เขียวได้ตั้งแต่ตอนนี้** = guard ที่ถูก (ผู้เรียนต้องอธิบายว่าเขียวเพราะอะไร ไม่ใช่ลบทิ้ง)

### LAB 8 · ทำ CR-01 + regression (รูบริก 14 16)

ต้องได้: 6 ไฟล์ ~+60/−9 (prototype ของ A5) · กฎค่าห่ออยู่ `lib/pricing.ts` ฟังก์ชันเดียวใช้ทั้ง browser/server · server รับแค่ `giftWrap === true` · TC-GIFT เขียวทุกข้อ · `npm run test:all` ไม่มีข้อเดิมล้ม · ยิง API ตรงตาราง W1–W10 · ภาพ `out\shots\lab8-checkout-giftwrap.png` · ถ้าเจอ "หน้า ฿269 แต่คำสั่งซื้อ ฿239" = ผลของกับดัก [ข้อ 4.4](#44-วิธีแก้-2-แบบ-และกับดักของ-) ต้องแก้ที่ `lib/orders.ts` ไม่ใช่เพิ่มค่าห่อเข้าไปในบล็อกซ้ำ

### LAB 9 · พิสูจน์ + CHANGE-REPORT (รูบริก 17 18)

→ [ข้อ 7](#7-ผลที่คาดหวังจาก-rea--ป้าย-authority) แถว SHA-256 / s2b / compare / HAR ใหม่ · obligation ledger ที่ดี: positive = PAW10 floor 10% · FREESHIP · ส่งด่วน ฿120 · ส่งฟรีที่ ฿999 (ตอนนี้ทั้งหน้าและคำสั่งซื้อ) · negative = SUMMER20 / โค้ดมั่วยังถูกปฏิเสธ · malformed = `giftWrap: "true"` ไม่คิดค่าห่อ · ข้อที่ไม่มี test = ⚪ (ห้ามเดาว่าผ่าน) · ชนิดงาน: CR-01 = re-engineering · BUG-01 = re-engineering (เปลี่ยนยอดคำสั่งซื้อ) หรือ restructuring ถ้าให้เหตุผลได้ (ดู QUIZ ข้อ 1)

### LAB 10 · PR-1 (รูบริก 19 20)

→ [ข้อ 6](#6-เฉลย-pr-1-lab-10)

---

## 4. เฉลย BUG-01: ต้นเหตุ · วิธีแก้ที่ถูก · กับดัก

ข้อความลูกค้า: ไม้ตกแมว 1 + ชามกินช้า 3 · ตะกร้า "ได้ส่งฟรีแล้ว!" · ปุ่ม "ยืนยันสั่งซื้อ ฿999" · หน้าคำสั่งซื้อ/บัญชี **฿1,049** · เก็บเงินปลายทาง

### 4.1 อาการและขอบเขต (black-box)

ตะกร้า ฿999 = ไม้ตกแมว ขนนก ฿129 ×1 + ชามกินช้า ฿290 ×3 · ค่า [D] จาก TEST-DATA "ปกติ ฿50 (ฟรีเมื่อซื้อครบ ฿999) · ด่วน ฿120" · ค่าจริง: A5 รันจริง (`CR-DESIGN` §2.4) + สคริปต์ตรวจรับ `LESSON-PLAN` §7.4

| กรณี | คิดเองจาก [D] | ตะกร้า / ปุ่ม | คำสั่งซื้อ (response · หน้าคำสั่งซื้อ · `/account`) | ถูก? |
|---|---|---|---|---|
| ฿999 ส่งธรรมดา | 999 + 0 = **999** | ฿999 ส่งฟรี | **฿1,049** (`shipping: 50`) | ❌ |
| ฿999 + PAW10 | ลด floor(99.9) = 99 → 900 + 0 = **900** | ฿900 | **฿950** | ❌ |
| ฿998 ส่งธรรมดา | 998 + 50 = **1,048** | ฿1,048 | ฿1,048 | ✅ |
| ฿999 + FREESHIP | **999** | ฿999 | ฿999 | ✅ |
| ฿999 ส่งด่วน | 999 + 120 = **1,119** | ฿1,119 | ฿1,119 | ✅ |
| ≥ ฿1,000 ส่งธรรมดา (เช่น ฿1,560) | ส่งฟรี | ส่งฟรี | ส่งฟรี | ✅ |

**ขอบเขต:** ผิดเฉพาะ **ยอดสินค้าก่อนหักส่วนลด = ฿999 พอดี + ส่งธรรมดา + ไม่ใช้ FREESHIP** และผิดเฉพาะ **ฝั่ง server** (หน้าเว็บแสดงถูกตาม [D]) → ลูกค้าบอก "ยอดพันกว่าบาทไม่เคยเป็น" ตรงกับขอบเขตนี้

### 4.2 ต้นเหตุ (white-box)

| ที่ | โค้ด | ทำอะไร |
|---|---|---|
| `petshop/lib/pricing.ts:39` · `:130-133` | `FREE_SHIPPING_MIN = 999` · `shippingCost()` คืน `subtotal >= FREE_SHIPPING_MIN ? 0 : STANDARD_SHIPPING` | **กฎจริง** ใช้ทั้ง browser (`useCartTotals` → `SummaryRows`) และ server (`computeTotals` ใน `createOrder`) |
| `petshop/lib/orders.ts:62` | `const totals = computeTotals({ lines, couponCode, shipping });` | ได้ยอดถูก (฿999 ส่งฟรี) |
| `petshop/lib/orders.ts:63-67` | `// PP-231: server must not trust the shipping fee shown in the browser — recompute it here.` → `if (shipping === "standard" && !totals.coupon?.freeShipping) { totals.shipping = totals.subtotal > FREE_SHIPPING_MIN ? 0 : STANDARD_SHIPPING; totals.total = Math.max(0, totals.subtotal - totals.discount + totals.shipping); }` | **กฎชุดที่ 2** คำนวณค่าส่งซ้ำด้วย `>` (฿999 ไม่ถือว่าครบ) แล้ว **เขียนทับ `totals.total` เอง** |
| `petshop/lib/orders.ts:3-10` | import `FREE_SHIPPING_MIN` `STANDARD_SHIPPING` | ใช้เฉพาะในบล็อกซ้ำ |

**สรุปต้นเหตุ:** กฎเงินถูกเขียนสองที่ (client/server divergence) · ที่ server ใช้ `>` แทน `>=` และคำนวณยอดรวมใหม่เองโดยไม่ผ่าน `computeTotals()` · ต้นเหตุคือ **การมีกฎชุดที่สอง** ไม่ใช่แค่เครื่องหมาย

### 4.3 ตรวจคอมเมนต์กับหลักฐาน (รูบริกข้อ 11)

- คอมเมนต์อ้างว่า "server ต้องไม่เชื่อค่าส่งที่ browser แสดง" → ฟังมีเหตุผล แต่ **browser ไม่เคยส่งค่าส่งหรือยอดรวมมา**
- หลักฐาน 2 ตา: (white) `components/CheckoutForm.tsx:76` `body: JSON.stringify({ items: cart, coupon, shipping, payment, address: form })` · (runtime) HAR `out\bug01.har` / `out\pawpantry-main.har`: body POST `/api/orders` keys = `items, coupon, shipping, payment, address` โดย `shipping` เป็นแค่ `"standard"`/`"express"` (A1: `rea-probe/evidence/04-har-api-table.md`)
- server คำนวณราคาใหม่จาก `priceLines()` อยู่แล้วทุกครั้ง (TC-SEC-03 ของบท 03) → บล็อก PP-231 ไม่ได้กันอะไรเพิ่ม · ไม่มี tracker/git history ให้ตรวจ PP-231 (`HANDOVER-NOTES`: "tracker เดิมปิดไปแล้ว") = ตัวอย่าง "คอมเมนต์ในระบบเดิมเชื่อไม่ได้"
- ได้ 1 ในข้อ 11 ต้องมีทั้ง **ไฟล์:บรรทัด** และ **การเทียบคอมเมนต์กับ HAR/body ที่ส่งจริง**

### 4.4 วิธีแก้ 2 แบบ และกับดักของ `>=`

| วิธี | diff | ผล BUG-01 | ผลต่อ CR-01 (A5 รันจริง `CR-DESIGN` §2.6) | ข้อสรุป |
|---|---|---|---|---|
| ✅ **A ลบบล็อกคำนวณซ้ำ + import ที่ไม่ใช้** (= reverse diff ของ `CR-DESIGN` §2.2) | import กลับเป็น `import { computeTotals, priceLines, type CartLine, type ShippingMethod } from "./pricing";` · ลบ `:63-67` | ฿999 → ฿999 ✅ · ฿999+PAW10 → ฿900 ✅ | ค่าห่อถูกทุกกรณี W1–W10 | **ต้นเหตุ** · `computeTotals()` เป็นแหล่งเดียว |
| ⚠️ **B เปลี่ยน `>` เป็น `>=` อย่างเดียว** | `:65` | ฿999 → ฿999 ✅ (test BUG-01 เขียว · ชุดเดิมเขียว) | ❌ บล็อกยังเขียนทับ `totals.total` โดยไม่รู้จักค่าห่อ: **W2 หน้า checkout/ปุ่ม ฿269 แต่คำสั่งซื้อ ฿239** · W3 ฿1,029 → ฿999 · W4 ฿1,529 → ฿1,499 · TC-GIFT แบบ UI ล้ม 2/3 (W5 ฿1,500 ไม่เห็นเพราะค่าห่อฟรี · W7 FREESHIP และ W8 ด่วน ไม่เข้าเงื่อนไขบล็อก) | **ปลายเหตุ** · ปิดอาการแต่ทิ้งกับดักให้ CR ถัดไป |

**ทำไมเป็นกับดักที่ดี:** วิธี B ผ่านทุก test ของ LAB 6 → ผู้เรียนจะเจอผลของมันใน LAB 8 (ฟีเจอร์ใหม่ "หาย" ในคำสั่งซื้อ) = บทเรียน "แก้ปลายเหตุ = หนี้ที่ CR ถัดไปต้องจ่าย"

**วิธีแก้ผิดอื่นที่เจอได้ (ได้ 0 ในข้อ 12 ทั้งหมด):**

| วิธี | ทำไมผิด |
|---|---|
| ให้บล็อกซ้ำเรียก `shippingCost()` แทนสูตรเอง | ยังเขียนทับ `totals.total` → ค่าห่อหายเหมือนวิธี B |
| แก้ฝั่ง browser ให้ใช้ `>` ด้วย (หน้าเว็บแสดง ฿1,049) | ทำให้ "ตรงกัน" แต่ผิด [D] TEST-DATA "ฟรีเมื่อซื้อครบ ฿999" |
| ให้ browser ส่ง `shippingFee`/`total` ไปให้ server ใช้ | ผิดหลัก "server คำนวณเงินเอง" (และทำให้คอมเมนต์ PP-231 กลายเป็นจริง) |
| ใน LAB 8 เพิ่มค่าห่อเข้าไปในบล็อกซ้ำ (`+ giftWrap`) เพื่อให้ TC-GIFT เขียว | กฎเงินกลายเป็น 2 ชุดที่ต้องแก้คู่กันตลอดไป |

**ตรวจเร็ว:** `grep -n "FREE_SHIPPING_MIN\|STANDARD_SHIPPING\|totals\.total =\|totals\.shipping =" petshop/lib/orders.ts` ต้องว่าง · ถ้าผู้เรียนใช้วิธี B ใน LAB 6 แล้วเจอผลใน LAB 8 และ **ย้อนแก้ที่ต้นเหตุพร้อมบันทึกใน `BUG-01.md`** ให้ข้อ 12 = 1 (อธิบายได้แล้ว) และเก็บเป็น 👀 ของห้อง

### 4.5 test ที่ควรเพิ่ม (regression ของ BUG-01)

| ID (แนะนำ) | ทดสอบ | ผลที่คาดหวัง (ที่มา) |
|---|---|---|
| TC-SHIP-05 | ฿999 ส่งธรรมดา สั่งจนจบ · ตรวจปุ่ม + response + หน้าคำสั่งซื้อ + `/account` | ฿999 ทุกจุด · `shipping: 0` — [D] |
| TC-SHIP-06 | ฿998 ส่งธรรมดา สั่งจนจบ | ฿1,048 ทุกจุด (คู่ขอบ) — [D] |
| TC-SHIP-07 | ฿999 + PAW10 สั่งจนจบ | ลด ฿99 · ส่งฟรี · ฿900 — [D] + กฎเดิม "ส่งฟรีดูยอดก่อนหักส่วนลด" |
| (oracle หลัก) | ทุก test ที่สั่งซื้อจนจบ: เงินบนปุ่มยืนยัน = เงินในคำสั่งซื้อ | [R] เงินที่แสดงก่อนกดต้องเท่ากับเงินที่เก็บ |

ทำไมชุดเดิมจับไม่ได้: TC-CART-03 ตรวจส่งฟรีที่ ฿790/฿2,680 บนหน้าตะกร้าเท่านั้น · ไม่มี test สั่งซื้อจนจบที่ ฿999 · ไม่มี test เทียบหน้าเว็บกับ server (A5: suite บท 03 ก็ 46/48 เท่าเดิมทั้งก่อน/หลังใส่บั๊ก)

---

## 5. เฉลย CR-01: คำถามร้าน · impact · ค่าขอบ

ใบ CR (พรอมต์ LAB 7 · AC1–AC6): ค่าห่อ ฿30 (ไม่บอกว่าต่อคำสั่งซื้อหรือต่อชิ้น) · "ซื้อครบ ฿1,500 ห่อฟรี" (ไม่บอกว่าก่อนหรือหลังหักส่วนลด) · ไม่พูดถึงคูปองและเกณฑ์ส่งฟรี → ความกำกวมเหล่านี้ตั้งใจไว้ให้ถาม

### 5.1 คำถามที่ควรถามร้าน + คำตอบร้าน

คำตอบร้านอยู่ใน `<details>` ของ README LAB 7 · ตัวเลข "ถ้าตีความผิด" ในคอลัมน์ขวา = คำนวณจากกฎ (ยังไม่ได้รัน) ใช้ตรวจว่าผู้เรียนยกตัวอย่างยอดที่ต่างกันได้จริง

| คำถาม | คำตอบร้าน | ตะกร้าที่ทำให้ยอดต่าง (ตีความถูก vs ผิด) |
|---|---|---|
| ฿1,500 ดูยอด **ก่อน** หรือ **หลัง** หักส่วนลด | ก่อนหักส่วนลด (แบบเดียวกับส่งฟรี ฿999) | W6 ฿1,500 + PAW10: ถูก ฿1,350 (ห่อฟรี) · ถ้าใช้ยอดหลังลด ฿1,350 < ฿1,500 → +30 = ฿1,380 |
| FREESHIP ยกเว้นค่าห่อไหม · PAW10 ลดค่าห่อไหม | ไม่ยกเว้น · ไม่ลด | W7 ลูกแมว 400 g + FREESHIP: ถูก ฿219 · ถ้า FREESHIP ยกเว้นค่าห่อ = ฿189 |
| ค่าห่อนับเข้ายอดส่งฟรี ฿999 / ขั้นต่ำ NEWCAT50 ไหม | ไม่นับ | ตะกร้า ฿970–998: ถ้านับค่าห่อ จะได้ส่งฟรีผิด ๆ |
| ค่าห่อต่อคำสั่งซื้อหรือต่อชิ้น | ต่อคำสั่งซื้อ | W4 3 ชิ้น: ถูก ฿1,529 · ถ้าต่อชิ้น = ฿1,589 |
| (อื่น ๆ) | "ใช้แบบที่ง่ายที่สุดที่ไม่ขัดกับข้อบน แล้วติด ⚠️ สมมติฐาน" | — |

รูบริกข้อ 13 = 1 ต้องมี ≥ 2 เรื่อง **และ** แต่ละเรื่องมีตะกร้าตัวอย่างที่ยอดต่างกัน

### 5.2 impact ที่ต้องได้

| ไฟล์ | แก้อะไร | กับดัก |
|---|---|---|
| `lib/pricing.ts` | `GIFT_WRAP_FEE = 30` · `GIFT_WRAP_FREE_MIN = 1500` · `giftWrapCost(subtotal, selected)` · `computeTotals({ giftWrap })` · `Totals.giftWrap` + `giftWrapSelected` | ต้องอยู่ฟังก์ชันเดียว ห้ามคำนวณซ้ำใน component |
| `lib/orders.ts` | `const giftWrap = input.giftWrap === true` ส่งเข้า `computeTotals` · เก็บ `giftWrap` `giftWrapFee` ลง order | ห้ามรับยอด/ค่าห่อจาก client · ถ้า BUG-01 แก้แบบปลายเหตุ ค่าห่อจะหาย (ข้อ 4.4) |
| `lib/store.ts` | `Order.giftWrap: boolean` · `giftWrapFee: number` | — |
| `components/OrderSummary.tsx` | `useCartTotals(shipping, giftWrap)` · แถว `summary-giftwrap` ใน `SummaryRows` | — |
| `components/CheckoutForm.tsx` | state + checkbox `gift-wrap` · ส่ง `giftWrap` ใน body | ปุ่ม `place-order` ใช้ `totals.total` อยู่แล้ว ได้ค่าห่อฟรี |
| **`app/orders/[id]/page.tsx`** | แถว `summary-giftwrap` (หลังค่าจัดส่ง ก่อน `summary-total-row`) | ⚠️ **หน้านี้เขียน `<dl className="summary-rows">` เอง (`:104-122`) ไม่ใช้ `SummaryRows`** → ลืมง่ายที่สุด · ค้นด้วย `grep -rn "summary-total" app components` จะเห็น |
| ไม่ต้องแตะ (ตรวจแล้ว) `app/api/orders/route.ts` · `app/account/page.tsx` | route ส่ง body ทั้งก้อนเข้า `createOrder(user, body)` (`:24`) · บัญชีใช้ `o.total` (`:23` `:77`) | ผู้เรียนต้อง "ยืนยันว่าไม่ต้องแก้" พร้อมผลค้นหา ไม่ใช่เดา |

### 5.3 ค่าขอบและผลที่คาดหวัง (A5 รันจริงบน prototype ผ่าน API + UI · `CR-DESIGN` §1.3)

| # | ตะกร้า (ส่งธรรมดา เว้นแต่ระบุ) | ห่อ | คูปอง | สินค้า | ลด | ส่ง | ห่อ | **ยอดชำระ** |
|---|---|---|---|---|---|---|---|---|
| W1 | ลูกแมว 400 g ×1 | ไม่ | — | 189 | 0 | 50 | — | **239** |
| W2 | ลูกแมว 400 g ×1 | ✅ | — | 189 | 0 | 50 | 30 | **269** |
| W3 | ไม้ตกแมว + ชามกินช้า ×3 (฿999) | ✅ | — | 999 | 0 | ฟรี | 30 | **1,029** |
| W4 | ลูกแมว 400 g + น้ำพุแมว + สุนัขพันธุ์เล็ก (**฿1,499**) | ✅ | — | 1,499 | 0 | ฟรี | 30 | **1,529** (ขอบล่าง) |
| W5 | ชามกินช้า + สุนัขโต แกะ 3 kg + สุนัขพันธุ์เล็ก (**฿1,500**) | ✅ | — | 1,500 | 0 | ฟรี | ฟรี | **1,500** (ขอบ) |
| W6 | เหมือน W5 | ✅ | PAW10 | 1,500 | 150 | ฟรี | ฟรี | **1,350** |
| W7 | ลูกแมว 400 g | ✅ | FREESHIP | 189 | 0 | ฟรี | 30 | **219** |
| W8 | ลูกแมว 1.5 kg ส่งด่วน | ✅ | — | 590 | 0 | 120 | 30 | **740** |
| W9 | ลูกแมว 400 g · API `giftWrap: "true"` | (สตริง) | — | 189 | 0 | 50 | — | **239** |
| W10 | ลูกแมว 400 g · API `giftWrap: 1` | (ตัวเลข) | — | 189 | 0 | 50 | — | **239** |

- ไม่มีตะกร้า ฿1,501 ที่ทำได้ด้วยสินค้า ≤ 3 ชิ้น (A5 ค้นด้วยสคริปต์) → ยอมรับคู่ ฿1,499/฿1,500 เป็น ±1 · ผู้เรียนที่หาตะกร้า ฿1,501 ด้วย 4 ชิ้นขึ้นไปได้ = ดี (ต้องคำนวณจากราคาจริง)
- TC ขั้นต่ำ (รูบริก 15): W4 + W5 (ขอบ) · W9 และ/หรือ W10 (ผิดชนิด) · ที่ดีควรมีเพิ่ม: W1↔W2 ติ๊ก/เอาออก (TC-GIFT-04: เอาติ๊กออกแล้วแถวหาย ยอดกลับ ฿239 · `giftWrap=false`) · W6 W7 (ผสมคูปอง) · W8 (ด่วน) · W2 ตรวจ `/account` = หน้าคำสั่งซื้อ ฿269
- ผิดบ่อย: ใช้ `if (input.giftWrap)` (truthy → W9 ได้ ฿269) · คิดค่าห่อใน component แยกจาก `computeTotals` · ลืม `/orders/[id]` (หน้าเว็บถูก คำสั่งซื้อถูก แต่หน้าคำสั่งซื้อไม่มีแถว → AC5 ไม่ผ่าน) · ตะกร้าที่คำนวณจากราคาเดา ไม่ได้ดูจากเว็บ/API

---

## 6. เฉลย PR-1 (LAB 10)

> ⚠️ **ยังไม่มีใคร implement/รันก่อนรอบถ่ายทำ** (`CR-DESIGN` §4) · ผลจริงของรอบถ่ายทำดู README ข้อ 2 / `_design/results/LAB10_RESULT.md` · ถ้ารอบจริงต่างจากนี้ ให้ยึดรอบจริง

| เรื่อง | เฉลย |
|---|---|
| อาการ | "สูตรลดก้อนขน" สต็อก 3 (TEST-DATA [D] "ใกล้หมด (3)") · เพิ่ม 2 → toast "เพิ่ม…ลงตะกร้าแล้ว" ✅ · เพิ่มอีก 2 → เพิ่มได้จริง 1 แต่ toast ยังบอก "เพิ่ม…ลงตะกร้าแล้ว" · ตะกร้า 3 ชิ้น ฿1,560 (520 × 3) |
| ผลที่คาดหวัง [D] (คำตอบร้าน) | เพิ่มได้ไม่ครบ → แจ้งเตือน (ไม่ใช่ข้อความสำเร็จ) `เพิ่มได้อีกเพียง {n} ชิ้น (สินค้าเหลือ {สต็อก} ชิ้น)` เช่น `เพิ่มได้อีกเพียง 1 ชิ้น (สินค้าเหลือ 3 ชิ้น)` · เพิ่มไม่ได้เลย / เพิ่มครบ = ข้อความเดิม |
| ต้นเหตุ | `components/ProductCard.tsx:59-70` `useAddToCart()` เช็กแค่ `if (added > 0)` (`:63`) ไม่เทียบกับ `qty` ที่ขอ |
| impact | `useAddToCart` เป็น helper กลาง ใช้ในการ์ดสินค้า · หน้าสินค้า · Finder → ทุกหน้าที่กดเพิ่มลงตะกร้ากระทบ · ตัวจำกัดจำนวนจริงอยู่ `ShopProvider` `addToCart` (ไม่ต้องแก้) |
| แก้ที่ถูก | แก้ที่ helper กลางที่เดียว: แยกกรณี `added === qty` / `0 < added < qty` / `added === 0` · ไม่แก้ทีละหน้า · ไม่เปลี่ยนการจำกัดจำนวน |
| ลำดับที่ต้องเห็น (รูบริก 20) | ทำซ้ำ black-box → `pr1-add-to-cart.spec.ts` แดง (ถามร้านเรื่องข้อความก่อนถ้ายังไม่มี [D]) → ต้นเหตุ + impact → **ถามก่อนแก้** → แก้ → build → test เขียว → chromium → `npm run test:all` → แถว PR-1 ใน CHANGE-REPORT |
| ผิดบ่อย | เขียนผลที่คาดหวังเป็นข้อความที่ AI แต่งเอง โดยไม่ถาม · แก้ทั้ง `ProductCard` และ `ProductDetail` แยกกัน · ปรับให้เพิ่มเกินสต็อกได้ · test ใหม่ไปชนสต็อกที่ test ขนานใช้ร่วม (ต้องใช้ผู้ใช้/ตะกร้าแยก · ห้าม reset) |

---

## 7. ผลที่คาดหวังจาก REA + ป้าย authority

ค่าอ้างอิงจาก A1 รันจริง (`REA-FEASIBILITY` §2 · `rea-probe/evidence/`) บน build ที่ยังมี BUG_MODE → ตัวเลขของรอบนี้ต่างเล็กน้อยได้ · ป้าย = 4 ถังของ `REA-THEORY` §3.2 (🔵 static `artifact-bytes`/`ast-static-analysis` · 🟢 runtime `passive-cdp-runtime`/`controlled-replay`/HAR ที่บันทึกจริง · 🟡 inference `static-relationship-inference`/`cross-layer-reconciliation`/`cross-version-comparison` · ⚪ unknown)

| LAB | สิ่งที่เจอ | คำสั่ง | ป้ายที่ถูก | อ่านให้ถูก | ผิดบ่อย |
|---|---|---|---|---|---|
| 2 | static: ไฟล์ 21 · endpoint 9 = `/api/products` `/api/orders` `/api/auth/login` `/api/auth/logout` `/api/auth/register` `/api/coupons/validate` | `analyze-javascript-application …/.next/static` | 🔵 | "มีโค้ดเรียก" ไม่ใช่ "ถูกเรียก" | 🟢 |
| 2 | endpoint `a` `b` `c` (mechanism `call:Uv.delete` / `call:e.get`) | ″ | 🔵 ว่ามีการเรียก · ค่า URL ⚪ | ชื่อตัวแปรถูก minify ค่าจริงเป็น dynamic | เขียนว่ามี API ชื่อ `/a` |
| 2 | ไม่มี `/api/recommendations` `/api/auth/me` `/api/orders/[id]` `/api/products/[slug]` `/api/health` `/api/test/reset` ใน static | ″ | ⚪ (❓ไม่เจอ) | coverage `partial` · template literal / เรียกจาก server · **หาไม่เจอ ≠ ไม่มี** | "ไม่มี API นี้" (รูบริก 4 = 0) |
| 2 | storage 3 node `local-storage` `name: null` (getItem/setItem/removeItem) | ″ | 🔵 ว่ามีการใช้ localStorage · key ⚪ | key ส่งผ่านตัวแปร | เดาชื่อ key จากโค้ดแล้วติด 🔵 |
| 2 | server: กู้ path ต้นทาง ~53 ไฟล์จาก source map (API route ครบ 12) | `analyze-javascript-application …/.next/server` | 🔵 (`artifact-bytes` + source map) | ใช้ทำ triangulation กับ CODEBASE-MAP | — |
| 2 | node ป้าย `electron-renderer` | ″ | 🟡 | ชนิดที่ analyzer อนุมาน ไม่ใช่ Electron | "PawPantry เป็น Electron" |
| 2 | trace คูปอง (seed `string` `coupons/validate` · `incoming`) ~16 node รวม `app/api/coupons/validate/route.ts` + `components_CartView_tsx` | `trace-application-feature` | 🟡 (เดินตาม edge · ผ่าน `contains` ลามได้) | ไม่ใช่ทุก node ที่เดินถึงคือส่วนของฟีเจอร์ | ถือว่าทุก node = ต้อง regression |
| 2 | `subject.digest` / `evidence_id` | ทุกคำสั่ง | — | ผูกหลักฐานกับ bytes ของ build v1 · build ใหม่ = ต้องเก็บใหม่ | ไม่จด digest |
| 3 | HAR: ~97 records · API 4 ตัว (ดู LAB 3) · cookie redaction อัตโนมัติ · `Paw12345` ไม่อยู่ใน `har.json` | `inspect-web-network-capture … --sensitive-value` | 🟢 (บันทึกจริง ณ เวลานั้น · ไม่ยิงซ้ำ) | ยืนยัน 2 ตาให้ API ที่ static เห็น | คิดว่า REA ตัดค่าลับในไฟล์ `.har` ด้วย |
| 3 | scenario 11/11 step · storage `pp-recent` `pp-cart` `pp-coupon` · a11y `ใช้คูปอง PAW10 แล้ว` `ส่วนลด PAW10 -฿6` `ยอดชำระทั้งหมด ฿113` · `completeness: incomplete` | `capture-browser-scenario` (`-Network pawpantry05_default`) | 🟢 (`controlled-replay` · REA ขับเอง) | incomplete เพราะ RSC prefetch ถูก abort = ปกติของ Next · URL `petshop:3000` | ถือว่า scenario พัง · ไม่บอกว่ามีผลข้างเคียง |
| 9 | SHA-256 source v1↔ปัจจุบัน: ต่าง = 6 ไฟล์ CR-01 (รวม `lib/orders.ts` ที่แก้ทั้ง BUG-01/CR-01) + PR-1 · `next-env.d.ts`/`tsconfig.json` อาจต่างเพราะ build เขียนเอง | `Get-FileHash` | 🔵 (bytes) | ส่วนเกินต้องอธิบายได้ | นับไฟล์ที่ build เขียนเป็น "แก้โดยไม่ตั้งใจ" โดยไม่อธิบาย |
| 9 | s2b baseline v1src→v1build ≈ unchanged 44 · duplicated 9 · unknown 3 (`globals.css` `eslint.config.mjs` `next.config.ts`) · modified 0 | `import-reference-source` + `compare-source-to-bundle` (server bundle) | `unchanged`/`duplicated` = digest ตรง 🔵 · `unknown` = ⚪ | unknown 3 ตัวนี้เป็นไฟล์ที่ไม่ได้ลง server bundle ตั้งแต่ต้น | — |
| 9 | ตาราง 4 ทิศ: ไฟล์ที่แก้ = `unknown` ในคู่ข้ามเวอร์ชัน · `unchanged`/`duplicated` ในคู่เวอร์ชันเดียวกัน · **modified = 0 ทุกคู่** (A1: `lib/pricing.ts` = duplicated / unknown / unknown / duplicated) | `--s2b-table` | 🟡 การสรุปว่า "ไฟล์นี้ถูกแก้" มาจากการเทียบ 4 ทิศ + SHA-256 | unknown = หา digest ไม่เจอ **ไม่ใช่ไฟล์หาย** · รายงานครบ 7 คลาสแม้เป็น 0 | รอคำว่า modified · เทียบกับ static bundle (A1: unknown ทั้ง 56 ไฟล์ เพราะไม่มี source map) |
| 9 | compare-application-versions: `changed`/`unknown` หลายร้อยรายการ (A1 server: changed 273 · unknown 1479) | `compare-application-versions` | 🟡 (`cross-version-comparison`) | coverage partial + ชื่อ chunk hash เปลี่ยนทั้งชุด → อ่านยากกว่าตาราง 4 ทิศ · static diff = candidate ไม่ใช่สาเหตุ | ถือว่าแก้ไป 273 ที่ |
| 9 | HAR ใหม่: API 4 ตัวเดิม status เดิม · response `/api/orders` มี `giftWrap` `giftWrapFee` เพิ่ม | `record-har.mjs --out out\after` + inspect | 🟢 | หลักฐานว่าสัญญา API เดิมไม่พัง + ส่วนที่เพิ่มตรง AC4 | ไม่เทียบกับ API-INVENTORY |

ตัวเลขของรอบถ่ายทำบทนี้: README ข้อ 2 แถว LAB 2 3 9

---

## 8. หมายเหตุผู้ตรวจ (LESSON-PLAN §4.1)

| ข้อรูบริก | สิ่งที่ผู้ตรวจมองหา (เฉลย) |
|---|---|
| ข้อ 8 | ตะกร้า ฿999 ส่งธรรมดา: ตะกร้า/ปุ่ม ฿999 แต่คำสั่งซื้อ ฿1,049 → ต้องเป็น test คู่ `legacy-quirk` + `test.fail` ไม่ใช่ `expect(1049)` |
| ข้อ 11 | ต้นเหตุ = บล็อก `// PP-231` ใน `lib/orders.ts` คำนวณค่าส่งซ้ำด้วย `>` แล้วเขียนทับ `totals.total` · HAR: body POST `/api/orders` มีแค่ `shipping: "standard"` → คอมเมนต์ "must not trust the shipping fee shown in the browser" ไม่ตรงความจริง |
| ข้อ 12 | วิธีที่ถูก = ลบบล็อกซ้ำ + import ที่ไม่ใช้ (กฎเงินอยู่ `lib/pricing.ts` ที่เดียว) · `>`→`>=` = ปลายเหตุ (CR-01 ค่าห่อจะหาย ฿269 → ฿239 · `CR-DESIGN` §2.6) |
| ข้อ 14 | impact ต้องมี `app/orders/[id]/page.tsx` (เขียนสรุปเงินเอง ไม่ใช้ `SummaryRows`) · ไม่ต้องแก้ `app/api/orders/route.ts` `app/account/page.tsx` (ตรวจแล้ว) |
| ข้อ 17 | ไฟล์ที่ต่าง = 6 ไฟล์ CR-01 (+ `lib/orders.ts` ของ BUG-01) + PR-1 · ไฟล์ที่ build เขียนเอง (`next-env.d.ts`) อธิบายได้ |
