# 🤖 เครื่องตรวจอัตโนมัติ ข้อสอบบท 06 (ชุด A / B)

> 🔒 ผู้สอนเท่านั้น · ตรวจงานส่งของผู้สอบ 1 คน (repo ที่มี commit `EX0` … `EX8` + `EX5-red`) แล้วออกใบคะแนน CSV + Markdown ตามตารางคะแนนใน `EXAM.md` / `EXAM-B.md` / `EXAM-KEY.md` §10
> **เครื่องให้ 84 คะแนน** (ส่วน "ตรวจอัตโนมัติ") · **ผู้สอนกรอกเอง 16 คะแนน** (ช่องว่างในใบคะแนน)
> รันจริงแล้ว 12 ต.ค. 2026 (งาน GRADER) · ตัวเลขทุกตัวในไฟล์นี้มาจากการรันจริง

---

## 1. ต้องมีอะไร

| สิ่งที่ต้องมี | หมายเหตุ |
|---|---|
| Windows + PowerShell 5.1 ขึ้นไป | `grade.ps1` เป็นตัวเรียก · งานจริงอยู่ใน `grade.mjs` |
| Node ≥ 22.18 บนเครื่องผู้สอน | ใช้ `node:util` `parseArgs` + import ไฟล์ `.ts` |
| Docker Desktop (เปิดอยู่) | image ที่ใช้: `postgres:16-alpine` · `node:22-alpine` · `mcr.microsoft.com/playwright:v1.63.0-noble` (ดึงเองครั้งแรก) |
| git | อ่าน commit ของผู้สอบ (เครื่องตรวจ clone ไปไว้ใน work dir · **ไม่แตะโฟลเดอร์ต้นฉบับ**) |
| ไฟล์ข้างเคียง | `../exam-ref/mutants/M*.diff` · `../exam-ref/prod-data-A.sql` `prod-data-B.sql` · โฟลเดอร์บท (`web/` `db/` `e2e-legacy/`) = ระบบตั้งต้น |

**ไม่ใช้พอร์ตของเครื่อง** · ทุกระบบอยู่ใน docker network ของผู้สอบแต่ละคน (`<prefix>-<id>-net`) → ไม่ชนกับระบบ LAB (4000/5433) และตรวจได้แม้ Windows จองช่วง 2970–3069

## 2. วิธีใช้ (PowerShell)

```powershell
cd <repo คอร์ส>\00_tester\06_sabai-spa-legacy-change-request\_solution\grader

# ① เตรียมครั้งเดียวต่อชุด: image ระบบตั้งต้น + mutant 4 ตัวของชุด + node_modules ของ Playwright
powershell -ExecutionPolicy Bypass -File grade.ps1 -Prep -Set B

# ② ตรวจ 1 คน (.bundle หรือโฟลเดอร์ repo) · ไม่ใส่ -Variant = อ่านจาก exam/VARIANT.json ของผู้สอบ
powershell -ExecutionPolicy Bypass -File grade.ps1 -Submission C:\exam\in\6501234.bundle -Set B -Variant 2

# ③ ตรวจทุก .bundle ในโฟลเดอร์ (ทีละคน)
powershell -ExecutionPolicy Bypass -File grade.ps1 -Submission C:\exam\in -Set B -All

# ④ หลังตรวจเสร็จทั้งหมด: ลบ container/network/image ของเครื่องตรวจ (ไม่แตะ sabai06-* / sabai06x-* / volume ใด ๆ)
powershell -ExecutionPolicy Bypass -File grade.ps1 -Cleanup -Images
```

| พารามิเตอร์ | ค่าเริ่ม | ความหมาย |
|---|---|---|
| `-Set` | (บังคับ) | `A` หรือ `B` |
| `-Variant` | อ่านจาก `exam/VARIANT.json` | v ตาม `variants.json` (= EXAM-KEY §1) · ถ้าไฟล์ของผู้สอบไม่ตรงกับที่สั่ง ใบคะแนนจะเตือน |
| `-E2E` | `full` | `full` = e2e-legacy 4 project (api chromium firefox webkit) · `quick` = api+chromium · `skip` = ไม่รัน (ข้อ 8 "ตัวเลข REGRESSION" 3 คะแนนกลายเป็นช่องผู้สอน) |
| `-Work` | `%USERPROFILE%\sabai-grader-work` | ที่เก็บ clone / ไฟล์ชั่วคราว / ผล · ต้องอยู่ในไดรฟ์ที่ Docker Desktop mount ได้ |
| `-Prefix` | `exref-g` | ขึ้นต้นชื่อ container/network/image ทั้งหมดของเครื่องตรวจ (เปลี่ยนได้ เช่น `sabai-grader`) |
| `-Map` | — | กรณีผู้สอบตั้งชื่อ commit ผิด: `-Map "EX4=abc123,EX5=def456"` |
| `-Keep` | ปิด | ไม่ลบ container หลังตรวจ (ไว้ดูปัญหา) |

## 3. ผลที่ได้ (`<Work>\results\<id>\`)

| ไฟล์ | เนื้อหา |
|---|---|
| `score.md` | ใบคะแนน: ทุกเกณฑ์ของ 8 ข้อ (เครื่อง/ผู้สอน) · เต็ม · ได้ · รายละเอียดว่าผ่าน/ไม่ผ่านเพราะอะไร · ตารางรวมรายข้อพร้อมช่อง `___` ให้ผู้สอนกรอก · กติกาหักคะแนน · ไฟล์ที่ต้องส่ง ✓/✗ · เวลาตรวจ |
| `score.csv` | ข้อมูลเดียวกัน (UTF-8 BOM เปิดใน Excel ได้) · แถวผู้สอนช่อง score ว่าง |
| `raw.json` | ผลดิบทุกขั้น (commit · ผล hidden ทุกเคส · check-rules · migration · e2e) |
| `grade.log` `hidden.log` `e2e-*.log` | log สำหรับตรวจย้อนกรณีสงสัย |
| `<Work>\results\results.csv` | 1 แถวต่อคน: คะแนนอัตโนมัติรายข้อ + รวม + วินาทีที่ใช้ (ต่อท้ายทุกครั้งที่ตรวจ) |

## 4. เครื่องตรวจทำอะไรบ้าง (ต่อผู้สอบ 1 คน)

| ขั้น | ทำ | ข้อ/เกณฑ์ |
|---|---|---|
| 0 | clone → หา commit `EX0`…`EX8` `EX5-red` (ใช้ commit สุดท้ายที่ขึ้นต้นตรง) · ข้อที่ไม่มี commit หรือ commit ว่าง (skip) = ข้อนั้น 0 | ทุกข้อ |
| 1 | ไม่เปิดระบบ: `exam/Q1.json` เทียบ `keys/<ชุด>.json` (path + regex) · `IMPACT.md` นับจุดที่พบ 10 จุด · แยกเคสใน `check-rules.mjs` / `e2e-legacy` ที่เปลี่ยนในแต่ละ commit (ค่าคาดหวังเปลี่ยน / เตรียมสถานการณ์อย่างเดียว / เอา `test.fail` ออก / ลบ / skip) เทียบรายการอนุญาตและแถวใน `ORACLE-CHANGES.md` · grep `down -v` | 1 · 3 · 4 · 5 · 8② · กติกาหัก |
| 2 | ขนานกัน: ระบบตั้งต้น + mutant 4 ตัว (A: M2 M3 M4 M7 · B: M1 M6 M8 M9) รัน `tests/exam2/run.mjs` ของ commit `EX2` (ตั้งต้นต้อง exit 0 · mutant ต้อง ≠ 0) · smoke บนระบบตั้งต้น (ต้อง ≠ 0) · ชุด B ทำซ้ำ `EX5-EVIDENCE.json` | 2 · 8④ · 5 (B) |
| 3 | build image เว็บของ HEAD / EX4 / EX5 / EX5-red / EX7 (ขนาน · tree เดียวกัน = image เดียว) | — |
| 4 | ระบบหลัก: ฐาน "ใช้งานจริง" (init ตั้งต้น + `prod-data-<ชุด>.sql`) → migration ของผู้สอบ **2 รอบ** ก่อนเปิดเว็บ → ตรวจข้อมูลเดิม + smoke (นับแถวก่อน/หลัง) **ก่อน reset** → hidden API ข้อ 4–7 → hidden UI (Playwright) → check-rules ⑥ → golden HEAD → เทสต์ของผู้สอบข้อ 7 | 4 · 5 · 6 · 7 · 8③④ |
| 5 | ระบบของ commit `EX4` `EX5` (`EX7` ถ้าโค้ดต่างจาก HEAD): check-rules ของ commit นั้น · เทสต์ใหม่ใน `EX5-red` ต้อง**แดง**บนโค้ด `EX5-red` และ**เขียว**บน `EX5` | 4 · 5 · 7 |
| 6 | e2e-legacy ของ HEAD แยก 3 ระบบขนาน (api+chromium · firefox · webkit) จากการติดตั้งใหม่ด้วย `db/init` ของ HEAD (ตรวจ ⑤ "ติดตั้งใหม่" ก่อน) → เทียบตัวเลข passed / expected-fail / failed กับ `REGRESSION.md` | 6⑤ · 8① |
| 7 | ออกใบคะแนน · ลบ container / network / image ของผู้สอบคนนี้ (image ฐาน + mutant เก็บไว้ใช้ต่อ) | — |

hidden test อยู่ที่ `hidden/<ชุด>/` (ค่าคาดหวังจาก EXAM-KEY §5–§8 ตาม VARIANT) · ทุกเคส reset เอง · น้ำหนักแต่ละเคสอยู่ในไฟล์ (`s.check(id, label, น้ำหนัก, …)` และ `[w=…]` ในชื่อ test Playwright)

## 5. ผลการรันจริง (12 ต.ค. 2026 · เครื่อง 32 core / RAM 64 GB · Docker Desktop)

| งานส่งที่ใช้ทดสอบ | คะแนนอัตโนมัติ | เวลา (wall-clock) |
|---|---|---|
| เฉลยชุด A v0 (`selftest/make-selftest.mjs`: `exam-ref/A-*.diff` + `selftest/A/` · commit EX0–EX8 + EX5-red) | **84 / 84** | 5 นาที 47 วินาที (image มี build cache) |
| เฉลยชุด A v0 แบบ build ใหม่ทั้งหมด (`--salt`: 3 image ขนาน 39 วินาที) | **84 / 84** | 5 นาที 7 วินาที |
| เฉลยชุด A v0 · `-E2E skip` | 81 / 84 (+3 ช่องผู้สอน) | 2 นาที 26 วินาที |
| โฟลเดอร์ตั้งต้นที่ยังไม่ทำ (ไม่มี `.git`) | **0 / 84** | 5 วินาที |
| เฉลยชุด A v0 แต่ทำข้อ 7 พัง (`--break 7`: API คืนรายการเรียงเก่า → ใหม่) | **73 / 84** · ข้อ 7 = 4/15 (API 2/10 · UI 1/3 · เทสต์ของผู้สอบ 0/1 · check-rules 1/1) · ข้ออื่นเท่าเดิมทุกเกณฑ์ | 4 นาที 41 วินาที |
| เฉลยชุด B v0 เฉพาะโค้ด (`exam-ref/B-*-v0.diff` + B-2 + B-7 · ไม่มีเอกสาร) · `-E2E skip` | ข้อ 2 4 5 6 เต็ม · ข้อ 7 14/15 (ไม่มีเทสต์ของผู้สอบ) · ข้อ 1 3 8 = 0 (ไม่มีไฟล์) | 1 นาที 34 วินาที |
| hidden test ชุด A / B รันกับโค้ดตั้งต้นตรง ๆ (ตรวจว่าไม่ผ่านง่าย) | hidden API (ไม่รวม UI): A v0 ได้ 1.8 จาก 30 (เคสถอยหลังที่กฎไม่เปลี่ยน เช่น H06 นอกพื้นที่ · แพ็กเกจ) · B v2 ได้ 4.5 จาก 30.5 | — |

**เวลาโดยประมาณ:** ~5–6 นาที/คน (e2e ครบ) · ~2.5–3 นาที/คน (`-E2E skip`) · เตรียมครั้งเดียว ~3–5 นาทีบนเครื่องใหม่ (build image ~35 วินาที/ตัวขนาน + `npm ci` · รันจริงครั้งนี้ 5 วินาทีเพราะมี build cache) · ตรวจทีละคน (ไม่ควรรันหลายคนพร้อมกันบนเครื่องเดียว: แต่ละคนเปิด ~10 ระบบพร้อมกัน)

ทดสอบเครื่องตรวจซ้ำได้เอง:

```powershell
node selftest\make-selftest.mjs --out C:\t\st\ref-a        # เฉลย A v0 (ต้องได้ 84)
node selftest\make-selftest.mjs --out C:\t\st\brk --break 7 # ข้อ 7 พัง (ต้องเสียเฉพาะข้อ 7)
node selftest\make-selftest.mjs --out C:\t\st\blank --blank # โฟลเดอร์ตั้งต้น (ต้องได้ 0)
powershell -ExecutionPolicy Bypass -File grade.ps1 -Submission C:\t\st\ref-a -Set A -Variant 0
```

## 6. ข้อจำกัด / สิ่งที่ผู้สอนต้องรู้

| เรื่อง | รายละเอียด |
|---|---|
| ยังไม่ได้รันผ่าน grader | ชุด A v1 · ชุด B v1 v2 (hidden test ใช้ค่าตาม `variants.json` ที่ EXREF ยืนยันแล้วทุก variant แต่ grader รันจริงเฉพาะ A v0 และ B v0) · ชุด B ทั้งชุดพร้อมเอกสาร (Q1 / IMPACT / REGRESSION ของชุด B ยังไม่มีเฉลยอ้างอิงให้ทดสอบ) |
| ข้อ 1 และ 3 ใช้ regex | `keys/A.json` `keys/B.json` · ตอบถูกแต่ใช้คำต่าง (เช่นภาษาอังกฤษล้วน) อาจไม่ได้ → ใบคะแนนบอก "path ถูก → ผู้สอนพิจารณาครึ่ง" · ปรับ regex ได้ในไฟล์ key |
| แยก "ค่าคาดหวัง" กับ "การเตรียม" | ใช้หลัก: literal ในบรรทัด `ck.eq/ok` / `expect` เปลี่ยน หรือ literal เดิมหายไป = เปลี่ยนค่าคาดหวัง · เพิ่มบรรทัดอย่างเดียว = เตรียมสถานการณ์ (รันกับเฉลยทั้ง 4 ชุดตรงทุกเคส) · ถ้าผู้สอบแก้ค่าในบรรทัดเตรียมเดิม จะถูกนับว่าเปลี่ยนค่าคาดหวัง → ผู้สอนดูรายละเอียดในใบคะแนน |
| แถว ORACLE | ต้องมีรหัสเคส (`E74` `TC-TRN-01` หรือช่วง `E74–E79`) และคำว่า "ข้อ N" ในบรรทัดเดียวกัน · golden ต้องมีชื่อไฟล์ (ไม่ต้องมี `.json`) |
| เทสต์ของผู้สอบ (ข้อ 5 แดง/เขียว · ข้อ 7) | หาจากไฟล์ที่เปลี่ยนใน commit นั้นใต้ `tests/` หรือ `*.spec.ts` / `web/scripts/check-rules.mjs` · `.mjs` รันด้วย `node <ไฟล์>` จากรากของ repo · `.spec.ts` นอก `e2e-legacy` ถูกคัดไป `e2e-legacy/tests/zz-learner/` แล้วรันด้วย project chromium (ต้อง import จาก `@playwright/test` ได้เอง) · ถ้าไฟล์ spec เดิมที่ผู้สอบแก้มี TC-SEC-05 (ล้มตั้งแต่ส่งมอบ) อยู่ด้วย "เขียว" จะไม่ผ่าน → ผู้สอนดู |
| ข้อ 8 ① | ค้นตัวเลข `N passed` · `expected-fail N` · `N failed` และ `ผ่าน/ทั้งหมด` ของ check-rules ใน `REGRESSION.md` · ต้องตรงกับที่เครื่องรัน (เฉลย: 113 passed · expected-fail 4 · 1 failed · 90/90) · เขียนรูปแบบอื่น = 0 + ตัวเลขของเครื่องในรายละเอียด ให้ผู้สอนเทียบ · ผล e2e มีโอกาส flaky (ใบคะแนนแสดงจำนวน flaky) |
| กติกาหัก | คิดอัตโนมัติแล้วแสดงใน "กติกาหักคะแนน" (×0.5 / ×0) · `down -v` ค้นแบบตรงตัวใน `MIGRATION.md` `db/migrations/` `RELEASE-NOTES.md` → แม้เขียนว่า "ห้ามใช้ down -v" ก็โดน (ตาม EXAM-KEY §11) ผู้สอนยกเลิกได้ |
| คะแนนเป็นข้อ | ข้อที่ไม่มี commit หรือ commit ว่าง = 0 ทั้งข้อ (ไม่ดูจาก HEAD) · ตั้งชื่อ commit ผิดให้ใช้ `-Map` |
| วันที่ของรายการแต้มใหม่ (A ข้อ 7) | ไม่เทียบวัน (= เวลาเครื่องจริง ตาม EXAM-KEY §8) · ตรวจแค่รูปแบบ `YYYY-MM-DD` |
| ความปลอดภัย | สคริปต์ของผู้สอบ (golden · smoke · check-rules · เทสต์) รันใน container `node:22-alpine` / Playwright เท่านั้น ไม่รันบนเครื่องผู้สอน · repo ของผู้สอบถูก clone มาไว้ใน `-Work` |

## 7. โครงไฟล์

```text
grader/
├─ grade.ps1                  ตัวเรียก (PowerShell 5.1 · UTF-8 BOM)
├─ grade.mjs                  ขั้นตอนทั้งหมด (Node)
├─ variants.json              ค่ารายคน (= EXAM-KEY §1)
├─ keys/A.json · keys/B.json  ข้อ 1 · ข้อ 3 · รายการเคสที่ต้องเปลี่ยน (ข้อ 4 · 5) · ไฟล์ที่ต้องส่ง · mutant ของชุด
├─ lib/                       sh · docker (ระบบที่ทดสอบ) · static (git · แยกเคส · ORACLE · regex) · rubric (แถวคะแนน)
├─ hidden/lib.mjs + A/ B/     hidden test ข้อ 4–7 (API: *.mjs · หน้าจอ: *.ui.spec.ts) · ex6-pre (ก่อน reset) · ex6-fresh (ติดตั้งใหม่) · B/ex5-evidence
└─ selftest/                  make-selftest.mjs + เอกสาร/เทสต์เฉลยชุด A (Q1 · IMPACT · ORACLE · BUGFIX · MIGRATION · smoke · RELEASE-NOTES)
```
