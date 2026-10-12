# LESSON-PLAN · บท 06 `06_sabai-spa-legacy-change-request` (สบายใจ สปา: รับงานแก้ระบบเดิม)

> สำหรับผู้สอน/ผู้ผลิตบท · เขียน 12 ต.ค. 2026 (งาน B2) · **v2 แก้ตาม `REVIEW-PLAN-V1.md` (งาน B2F · ดู "Fix log" ท้ายไฟล์รีวิว)** · **ยังไม่ได้รัน LAB จริง** — ตัวเลขในไฟล์นี้มี 4 แบบ:
> **[รันจริง:A2]** = REA-FEASIBILITY.md (รันบนสำเนาพอร์ต 3261) · **[รันจริง:A6]** = CODEBASE-NOTES.md (รันบนสำเนา) · **[บันทึกบท 04]** = ผลที่บท 04 บันทึกไว้ (LEGACY-TESTSUITES) · **[รันจริง:PREP]** = ต้องยืนยันใน `PREP-LOG.md` · **[คาด]** = คำนวณ/ประมาณ ต้องแทนด้วยผลรอบ RUNNER ก่อนเขียน README
> เอกสารคู่กัน: `PREP.md` (เตรียมโฟลเดอร์ตั้งต้น · agent แยก) · `PROMPTS.md` (พรอมต์ทุก LAB) · `RUNNER.md` · `CHANGE-REQUESTS-DRAFT.md` (หนังสือ CR + คำตอบ) · `EXAM-DRAFT.md` · อ้างอิง `CR-DESIGN.md` (ย่อ **CRD**) `CODEBASE-NOTES.md` (**CN**) `EXAM-BLUEPRINT.md` (**EB**) `LEGACY-TESTSUITES.md` (**LT**) `REA-FEASIBILITY.md` (**RF**) และของบท 05 `REA-THEORY.md` (**RT**) `METHODS.md` (**MT**) `STYLE-GUIDE.md` (**SG**)

---

## 1. เป้าหมายของบท

**ชื่อบท (README):** `# สบายใจ สปา: รับงานแก้ระบบเดิมด้วย Change Request (Copy & Paste)`

**ประโยคหลักของบท:** **"ทำตามที่ขอ ≠ ของเดิมไม่พัง ≠ ส่งมอบได้"**
แต่ละช่วงต้องมีหลักฐานของตัวเอง: เทสต์ใหม่แดง→เขียว (ทำตามที่ขอ) · regression เต็มชุด 3 เบราว์เซอร์ (ของเดิมไม่พัง) · traceability + แผนถอยกลับ + ตรวจรับ (ส่งมอบได้)

| # | หลังจบบท ผู้เรียนทำได้ | วัดใน |
|---|---|---|
| O1 | รับมอบระบบเดิม: เปิดระบบ 2 compose project · รันชุดทดสอบที่ส่งมอบ · แยก "คำอ้างของผู้รับเหมา" กับ "ผลจริง" | LAB 1 · รูบริก 1 |
| O2 | ให้ Agent เข้าใจระบบจาก 3 มุม (REA black-box · อ่าน repo · อ่าน schema DB) แล้ว triangulate · ตรวจทานคำอธิบายของ AI กับ `file:line` | LAB 2–3 · ข้อสอบข้อ 1 |
| O3 | เขียน `CLAUDE.md` + รั้ว `permissions.deny` ให้ Agent ทำงานกับ legacy อย่างปลอดภัย | LAB 4 |
| O4 | สร้างตาข่ายกันพลาด (golden master + characterization UI + known issue + test seam) และวัดคุณภาพตาข่ายด้วย mutant | LAB 5 · ข้อสอบข้อ 2 |
| O5 | ทำ CR ครบวงจร: คำถาม → impact (ไฟล์ × เทสต์) → plan → เทสต์แดงก่อน → แก้ → regression 3 เบราว์เซอร์ → traceability CR → BR → TC | LAB 6–10 · ข้อสอบข้อ 3–7 |
| O6 | เปลี่ยน schema บนฐานที่มีข้อมูลจริง: migration แยกไฟล์ รันซ้ำได้ ถอยกลับได้ ไม่ใช้ `down -v` | LAB 8, 12 · ข้อสอบข้อ 6 |
| O7 | แยก regression ที่ตั้งใจ (มี CR อนุญาต · บันทึกใน `ORACLE-CHANGES.md`) กับที่ไม่ตั้งใจ | LAB 6–11 · ข้อสอบข้อ 8 |
| O8 | ส่งมอบแบบตรวจย้อนได้: REA เทียบเวอร์ชัน (รู้ว่าเห็นอะไร/ไม่เห็นอะไร) · release notes ภาษาคน · UAT checklist · ซ้อมถอยกลับ | LAB 11–12 |

## 2. เรื่องเล่า

ระบบจองคิว "สบายใจ สปา" (บท 04) ใช้งานจริงมาแล้ว ผู้รับเหมาเดิม "บริษัท โค้ดไว จำกัด" (ชื่อสมมติ) ส่งมอบโค้ด + `SPEC.md` + ชุดตรวจ 2 ชุด แล้ว **หมดสัญญา** (บันทึกส่งมอบ 30 ก.ย. 2026) · คุณจันทร์จ้างทีมใหม่ = **เรา + Claude Code** · วันที่ 12 ต.ค. 2026 ร้านส่ง **หนังสือขอเปลี่ยนแปลงระบบ 5 ฉบับ** (CR-01–05) · เหมือนงานภาครัฐ: ระบบมีข้อมูลจริง · เอกสารเก่าไม่ตรงโค้ด · ต้องมีหลักฐานให้คณะกรรมการตรวจรับ · ทุกการเปลี่ยนต้องย้อนกลับได้

> กติกาวันที่ (m11 · SG §7 ข้อ 18): ข้อความ README ใช้ **ค.ศ.** (10 ต.ค. 2026 ฯลฯ) · **พ.ศ. 2569 ใช้เฉพาะในหนังสือ CR / บันทึกส่งมอบ / ทะเบียน** (สมจริงแบบหนังสือราชการ และเป็นโจทย์แปลงปีของ CR-02) · README มีหมายเหตุ 1 บรรทัด "2569 = 2026"

## 3. บทนี้ต่างจากบท 04 และ 05 อย่างไร (ตาราง 📦 ใน README)

| | บท 04 | บท 05 | **บท 06 (บทนี้)** |
|---|---|---|---|
| ตอนเริ่มมี | บันทึกสัมภาษณ์ | เว็บ PawPantry (ทีมเดิมหายไป) | **ระบบจริง 2 กล่อง + SPEC เก่า + ชุดทดสอบที่ส่งมอบ + หนังสือ CR 5 ฉบับ** |
| เว็บมาจาก | Claude สร้างใหม่ | ให้มา (ไม่มีเอกสาร) | **ให้มา = ระบบที่ใช้งานจริง มีข้อมูลลูกค้าอยู่** |
| ผลที่คาดหวังมาจาก | [D] [R] [A] [O] | + **[E]** หลักฐานจากระบบ | **[E] ใช้ต่อทุก LAB** (`[E ev_xxxxxxxx]` / golden + SHA-256 ย่อ · เฉพาะล็อกพฤติกรรมเดิม) + **[D:CR-0N]** ค่าที่ร้านยืนยันในคำตอบ CR · **[E] ขัด [D:CR] = ผู้ต้องสงสัยบั๊ก** · ค่าเดิมเปลี่ยนได้เฉพาะมี CR |
| งานหลัก | สร้าง → แผน → พิสูจน์ | เข้าใจ → ล็อก → แก้ 1 CR + 1 บั๊ก | **รับมอบ → เข้าใจ 3 มุม → ตาข่าย → 5 CR → ส่งมอบ** |
| บั๊ก | `BUG_MODE` 3 ตัว (Claude เลือก) | BUG-01 อบในโค้ด | **ไม่มีสวิตช์ · บั๊กจริงของระบบเดิม** (เจอผ่านเรื่องร้องเรียน/สำรวจ) |
| ฐานข้อมูล | สร้างจาก init | ไม่มี (in-memory) | **migration บนฐานที่มีข้อมูล + ซ้อมถอยกลับ** |
| ทักษะที่ได้ | ครบวงจรสร้าง | REA + legacy พื้นฐาน | **Change Request ครบวงจรแบบหน่วยงานรัฐ** |

## 4. สิ่งที่บท 05 สอนแล้ว (ใช้ "กล่องทบทวน" สั้น ๆ ไม่สอนซ้ำ)

| เรื่อง | กล่องทบทวนในบท 06 อยู่ที่ | ภาพที่ใช้ซ้ำ (ลิงก์ไปบท 05 ไม่สร้างใหม่) |
|---|---|---|
| REA theory · Evidence · authority | 🎓 ข้อ 2 · LAB 2 | `../05_rea-reverse-engineer-legacy-petshop/img/concept-05-evidence-not-opinion.jpg` |
| "ไม่เจอ ≠ ไม่มี" (coverage partial) | 🎓 ข้อ 2 · LAB 2 · LAB 11 | `../05_…/img/concept-06-missing-not-absent.jpg` |
| ป้าย **[E]** หลักฐานระบบ (RT §4.2 กติกา 1–4) | 🎓 ข้อ 2 · LAB 2, 5, 6–10 | `../05_…/img/concept-12-evidence-badge-e.jpg` |
| black / white / grey box | 🎓 ข้อ 2 | `../05_…/img/concept-03-black-white-grey-box.jpg` |
| rea-lab Docker · `rea.ps1` · HAR → API inventory · bundle analysis · feature trace | LAB 2 (คำสั่งชุดเดิม ใช้กับ Sabai · REA ต่อเว็บผ่าน network `sabai06-net` D7) | `../05_…/img/three-eyes.png` · `../05_…/img/concept-10-passive-driven-har.jpg` |
| CODEBASE-MAP / CLAUDE.md โดย agent | LAB 3–4 | — |
| characterization test Playwright · `test.fail` known bug | LAB 5 | — |
| impact analysis · failing-test-first | 🎓 ข้อ 4 | — |
| version comparison | LAB 11 | `../05_…/img/concept-08-version-compare.jpg` |

ชื่อไฟล์บท 05 ตรวจกับ `05_…/img/` แล้ว (12 ต.ค. 2026 · หลังเปลี่ยนเลข concept) · ก่อนเขียน README ให้ link-check `../05_…/img/*` อีกครั้ง

> ถ้าผู้เรียนข้ามบท 05 มา: README มีบรรทัด "ยังไม่ได้ทำบท 05? อ่าน 🎓 ของบท 05 ข้อ 1–4 ก่อน (~15 นาที) และต้องมี image `rea-lab:6.4.0`" (LAB 0 ตรวจให้)

---

## 5. 🎓 พื้นฐาน: ดูรูปก่อนลงมือ (เนื้อหาสำหรับ README)

แต่ละข้อ = รูป concept + ตาราง 3–4 คอลัมน์ (หัวคอลัมน์มี emoji) + blockquote กับดัก · ภาพทั้งหมดอยู่ในตาราง IMAGES ข้อ 12

### 1) ระบบเดิมแบบหน่วยงานรัฐ: รับมอบ → หนังสือ CR → ตรวจรับ
ภาพ: `concept-01-inherited-system.jpg` · `concept-02-cr-lifecycle.jpg`

| 📦 ของที่ได้รับมอบ | 📨 Change Request (CR) | ✍️ ตรวจรับ (UAT / sign-off) |
|---|---|---|
| โค้ด · ฐานข้อมูลที่มีข้อมูลจริง · เอกสารที่อาจเก่า · ชุดทดสอบที่อาจแดงค้าง · คำอ้างของผู้รับเหมา | หนังสือจากเจ้าของงาน 1 ฉบับ = 1 เรื่อง · ภาษาคน มีช่องว่าง · ต้องถามก่อนทำ · มีทะเบียนคุมสถานะ | กรรมการ (คุณจันทร์) ตรวจตามรายการที่ตกลง · ดูหลักฐาน ไม่ดูคำพูด |

> **คำอ้าง ≠ หลักฐาน** "ผ่านทั้งหมด" ในบันทึกส่งมอบคือ [A] ของผู้รับเหมา · เรารันเองแล้วจดผลก่อนเชื่อ

### 2) มองระบบ 3 ตา + ตาที่ 4 คือฐานข้อมูล (ทบทวนบท 05 + เพิ่ม DB)
ภาพ: ทบทวน `../05_…/img/concept-03-black-white-grey-box.jpg` · `../05_…/img/concept-05-evidence-not-opinion.jpg` · `../05_…/img/concept-06-missing-not-absent.jpg` · `../05_…/img/concept-12-evidence-badge-e.jpg` · ใหม่ `concept-03-four-eyes.jpg` · `concept-04-browser-only.jpg` · `concept-05-outdated-docs.jpg` · ไดอะแกรม `three-eyes-db.png`

| 🔦 REA (grey-box) | 📖 อ่าน repo (white-box) | 🗄️ อ่าน schema DB | 📜 เอกสารเก่า |
|---|---|---|---|
| เห็นสิ่งที่ส่งถึงเบราว์เซอร์: หน้า · endpoint ที่ client เรียก · สัญญา API จาก HAR · **ไม่เห็นกฎฝั่งเซิร์ฟเวอร์** [รันจริง:A2 static 9/25 route · HAR 7 endpoint] | เห็นทุกอย่างที่เขียน · REA เองบอกว่ามี source ครบให้อ่าน repo | กฎที่ DB บังคับ: CHECK 51 · EXCLUDE 2 (ห้องและนักบำบัดห้ามซ้อน) [รันจริง:A2] · REA ไม่อ่าน Postgres | `SPEC.md` ฉบับส่งมอบ ไม่ตรงโค้ดหลายจุด · **ห้าม AI ตัดสินเองว่าฝั่งไหนถูก** → ถามร้าน |

> **ตรงกัน 3 ตา = มั่นใจ · ไม่ตรง = เจอเรื่องต้องถาม** ตัวอย่างจริง: แก้ `GROUP_MAX` เป็น 8 ในโค้ดอย่างเดียว DB จะปฏิเสธ (CHECK `party_size <= 6`) — REA และ HAR ไม่มีทางบอกเรื่องนี้ [รันจริง:A2]
>
> **ป้าย [E] จากบท 05 ใช้ต่อทั้งบท:** สิ่งที่ REA/HAR/golden บันทึกได้ติด `[E ev_xxxxxxxx]` = "ระบบทำอยู่" ใช้ล็อกพฤติกรรมเดิม · ค่าที่ร้านตอบใน CR ติด `[D:CR-0N]` = "ควรทำ" · **[E] ขัด [D] → ผู้ต้องสงสัยบั๊ก ไม่ใช่ค่าคาดหวัง** (เช่น เรื่องร้องเรียน CR-03: [E] guest จองซ้ำได้ 201 ขัด [D:CR-03] "ต้องไม่ซ้ำ")

### 3) ตาข่ายก่อนแก้: ล็อกพฤติกรรมเดิม · seam · ทำพังเองเพื่อวัดตาข่าย
ภาพ: `concept-06-safety-net.jpg` · `concept-07-lock-not-correct.jpg` · `concept-08-test-seam.jpg` · `concept-09-mutation.jpg`

| 🕸️ ตาข่าย 3 ชั้น | 📸 characterization ≠ ความถูกต้อง | 🎛️ test seam | 🧪 mutant |
|---|---|---|---|
| ① `check-rules.mjs` 90 เคส (ส่งมอบ) ② `e2e-legacy/` 42 TC (ส่งมอบ) ③ golden master ที่เราสร้าง | ล็อก "ระบบทำอะไรอยู่" รวมบั๊กด้วย · บั๊กที่รู้แล้วล็อกคู่ `test.fail()` | จุดที่เปลี่ยนพฤติกรรมเพื่อทดสอบได้โดยไม่แก้กฎ เช่น `POST /api/test/clock` เลื่อนนาฬิกาโดยไม่ล้างข้อมูล | แก้โค้ดให้ผิด 1 บรรทัดเอง → ตาข่ายต้องแดง · รอด = ตาข่ายมีรู |

> **เทสต์เขียว ≠ ไม่มีบั๊ก** ระบบนี้ check-rules เขียว 90/90 แต่ยังมีบั๊กจริงอย่างน้อย 6 ตัว [รันจริง:A6 CN §7]

### 4) วงจรแก้อย่างปลอดภัย: impact → แผน → แดงก่อน → แก้ → regression → โยงกลับ
ภาพ: `concept-10-impact-ripple.jpg` · `concept-11-red-first.jpg` · `concept-12-intended-vs-unintended.jpg` · ไดอะแกรม `safe-change-loop.png`

| 🌊 impact (ไฟล์ × เทสต์) | 🔴 แดงก่อน | 🟢 regression 3 เบราว์เซอร์ | 🏷️ ค่าที่คาดหวังเปลี่ยนได้เมื่อ… |
|---|---|---|---|
| ไฟล์ที่จะแตะ · ใครเรียก (หลักฐาน grep) · หน้าจอ/API/**แชท** · ตาราง DB · ข้อความ 3 ภาษา · เทสต์ที่ต้องรันซ้ำ | เขียนเทสต์ตาม CR → รันบนโค้ดเดิม **ต้องแดง** → commit ก่อนแก้ | ชุดเดิมทั้งหมด + ชุดใหม่ · ระหว่างทำ CR: `api + chromium` (เร็ว) · ก่อนส่งมอบ (LAB 9 ส่วนที่ 3, LAB 11): chromium · firefox · webkit | มี CR อนุญาต + จดใน `docs/ORACLE-CHANGES.md` (ค่าเดิม → ใหม่ · CR ไหน) · ไม่งั้น = regression ที่ไม่ตั้งใจ |

> **ห้ามแก้เทสต์ให้ผ่าน** เทสต์เดิมแดงหลังแก้ → หยุด → จำแนก: เว็บผิด / เทสต์เก่าล้าสมัย (ต้องมี CR) / เทสต์ใหม่เขียนผิด

### 5) ฐานข้อมูลที่มีข้อมูลจริง: เพิ่มได้ ห้ามล้าง · รันซ้ำได้ · ถอยกลับได้
ภาพ: `concept-13-live-db-migration.jpg` · `concept-14-rollback.jpg`

| 🗂️ migration แยกไฟล์ | 🔁 รันซ้ำได้ (idempotent) | 🪂 แผนถอยกลับ | 🚫 ห้าม |
|---|---|---|---|
| `db/init/` รันเฉพาะตอน volume ว่าง → ระบบจริงต้องใช้ `db/migrations/NNN_*.sql` | `CREATE TABLE IF NOT EXISTS` · `ON CONFLICT DO NOTHING` → รัน 2 ครั้งไม่ error ข้อมูลเดิมอยู่ครบ | สำรองก่อน · down migration · image เดิม · ซ้อมจริงบนฐานที่มีข้อมูล | `docker compose down -v` = ข้อมูลลูกค้าหาย (ผิดหนังสือ CR-04) |

> **ระบบเดิมมีของซ่อน** ระบบเดิมมักมี "รายการตายตัว" ที่ต้องอัปเดตตามเมื่อเพิ่มตารางหรือข้อมูลใหม่ — หาให้เจอตอนทำ impact ก่อนแก้
>
> 🛠️ หมายเหตุผู้ผลิต — **ไม่ลง README** (M9 · ตัดสิน "ค้นพบแบบนำทาง": พรอมต์ LAB 3 ข้อ 5 และ LAB 8 ส่วนที่ 1 ข้อ 2 ถามตรง ๆ ว่า reset ล้างตารางอะไร/ถ้ามีตารางใหม่ต้องแก้ที่ไหน → ผู้เรียนเจอเองจากโค้ด · README ไม่ระบุชื่อ `TABLES` ก่อน LAB 8 · อาการ "reset 500" อยู่ใน 👀 ของ LAB 8 (หลังทำ) ไม่อยู่ในตาราง "ถ้าเจอปัญหา")

### 6) ส่งมอบแบบตรวจย้อนได้: CR → BR → TC · หลักฐานต่อ CR
ภาพ: `concept-15-traceability.jpg` · `concept-16-audit-signoff.jpg` · ไดอะแกรม `traceability-chain.png`

| 🔗 traceability | 🗃️ audit trail | 🔍 REA เทียบเวอร์ชัน | 🏷️ ป้ายใหม่ [D:CR-0N] |
|---|---|---|---|
| ทุก CR → กฎที่เปลี่ยน (BR) → เทสต์ที่พิสูจน์ (TC) → ผล | commit แดง→เขียวต่อ CR · ผลรันพร้อมเวลา · CHANGE-REPORT · REGISTER | bundle ที่ส่งมอบเปลี่ยนตรงหน้าที่ CR แตะไหม · กฎฝั่งเซิร์ฟเวอร์มองไม่เห็น → ต้องพิสูจน์ด้วยเทสต์ | ค่าที่ร้านยืนยันในคำตอบ CR = oracle ระดับ [D] ใหม่ · อ้างเลข CR ทุกครั้ง |

> ต่อยอด RT §3.6–3.7, §4.2: หลักฐานผลกระทบของการเปลี่ยน (change-impact evidence) + obligation ledger ในรูปที่คณะกรรมการอ่านได้ = traceability matrix + REGRESSION-REPORT

---

## 6. ตาราง LAB (12 LAB + LAB 0)

สัญลักษณ์: 🔍 = อ่าน/รัน/เขียนเอกสาร (ไม่แตะโค้ด เทสต์ หรือคอนฟิกของระบบ) · ✏️ = **แก้ repo เดิม** (โค้ด · schema · เทสต์ · คอนฟิก Agent)
เวลา = **[คาด]** จากขนาดงานใน CRD §3 และเวลารันที่บันทึกไว้ (check-rules ~20 วิ/รอบ [รันจริง:A6] · e2e-legacy api+chromium ~4 นาที · 3 เบราว์เซอร์ ~13 นาที [บันทึกบท 04 · README-LEGACY] · REA analyze ~53 วิ [รันจริง:A2] · build ~42 วิ)
**ขอบเขตเบราว์เซอร์ (M6 · ตัดสินแล้ว ไม่รอ RUNNER):** LAB 6, 7, 8, 10 รัน e2e-legacy ค่าเริ่ม `api + chromium` และ e2e-cr ทั้งชุดแค่ chromium (spec ใหม่ของ CR นั้น 3 เบราว์เซอร์) · **3 เบราว์เซอร์เต็มเฉพาะ LAB 9 ส่วนที่ 3 และ LAB 11** · mutant LAB 5 rebuild ทุกตัว (golden ยิง API) แต่ e2e-cr chromium อย่างเดียว

| ช่วง | LAB | 🔍/✏️ | ชื่อ | เป้าหมาย | input | output | ⏱️ |
|---|---|---|---|---|---|---|---|
| ⚙️ | 0 | 🔍 | เช็กเครื่อง + พอร์ตที่ Windows จอง | พร้อมทุกอย่าง · เข้าใจว่าทำไมใช้ 4000 | — | ตารางในแชท | 5 |
| 🟢 รับมอบ | 1 | 🔍 | รับมอบระบบ | เปิดระบบ · รันชุดส่งมอบ 2 ชั้น · ตรวจคำอ้าง · baseline git | `00-HANDOVER-MEMO.md` | `HANDOVER-CHECK.md` · commit baseline | 30 |
| | 2 | 🔍 | มองแบบ black-box ด้วย REA | static bundle + HAR → API inventory · แยก static/runtime/unknown · ป้าย [E] | `tools/*` | `docs/REA-INVENTORY.md` · `rea-out/` | 35 |
| 🟡 เข้าใจ | 3 | 🔍 | Agent อ่าน repo + DB → แผนที่ระบบ | SYSTEM-MAP + triangulation 3 ตา + SPEC-GAPS + ตรวจทาน 5 ข้อ | repo · `docs/REA-INVENTORY.md` · psql | `SYSTEM-MAP.md` · `docs/SPEC-GAPS.md` | 40 |
| | 4 | ✏️ | CLAUDE.md + รั้ว | กติกา legacy · deny `Edit(e2e-legacy/**)` · แม่แบบ impact · บันทึกค่าคาดหวังที่เปลี่ยน | SYSTEM-MAP · SPEC-GAPS | `CLAUDE.md` · `.claude/settings.json` · `docs/IMPACT-TEMPLATE.md` · `docs/ORACLE-CHANGES.md` | 20 |
| 🔵 ตาข่าย | 5 | ✏️ | ตาข่ายกันพลาด | seam นาฬิกา · golden master API · characterization UI · known issue · mutant 3 ตัว | ระบบที่รันอยู่ | `web/app/api/test/clock/` · `tests/golden/` · `e2e-cr/` · `KNOWN-ISSUES.md` | 90 |
| 🟠 Change Request | 6 | ✏️ | CR-02 เปลี่ยนกฎ (วันมีผล) | ส่วนลดกลุ่มขั้นบันได มีผล 1 พ.ย. · check-rules diff ว่าง | `CR-02.md` + answers | `docs/impact/CR-02.md` · `tests/cr02.mjs` · diff | 45 |
| | 7 | ✏️ | CR-03 แก้บั๊กจากเรื่องร้องเรียน | ทำซ้ำเรื่องร้องเรียนให้แดง · แก้ฝั่งเซิร์ฟเวอร์ · กดพร้อมกัน · แชท | `CR-03.md` + answers | `tests/cr03.mjs` · `e2e-cr/tests/cr03.spec.ts` · diff | 75 |
| | 8 | ✏️ | CR-04 migration วันหยุดร้าน | migration แยกไฟล์รันซ้ำได้บนฐานที่มีข้อมูล · reset/seed · แชท · runbook | `CR-04.md` + answers | `db/migrations/001_*.sql` (+down) · `tests/cr04.mjs` · `docs/MIGRATION-RUNBOOK.md` | 75 ☕ |
| | 9 | ✏️ | CR-01 ฟีเจอร์ใหม่ เลื่อนนัด | แตกงาน API → slots → UI · self-overlap · นักบำบัดคนเดิม · Playwright | `CR-01.md` + answers | `tests/cr01.mjs` · `e2e-cr/tests/cr01.spec.ts` · diff | 90 ☕ |
| | 10 | ✏️ | CR-05 รายงาน + CSV | ค่าคาดหวังจาก SQL (oracle อิสระ) · CSV ภาษาไทยเปิด Excel ได้ | `CR-05.md` + answers | `tests/cr05.mjs` · `e2e-cr/tests/cr05.spec.ts` · diff | 60 |
| 🟣 ส่งมอบ | 11 | 🔍 | Regression เต็ม + REA เทียบเวอร์ชัน | ทุกชุด 3 เบราว์เซอร์ · bundle v1↔v2 · **HAR v1↔v2 + scenario ซ้ำบน v2 (หลักฐาน [E] ว่าเส้นทางเดิมไม่เปลี่ยน)** · ไฟล์ที่เปลี่ยนทุกไฟล์โยง CR ได้ | ทุกอย่าง · `rea-out/v1` · `rea-out/har-api.json` | `REGRESSION-REPORT.md` · `docs/TRACEABILITY.md` ฉบับสมบูรณ์ | 55 |
| | 12 | ✏️ | ส่งมอบ + ซ้อมถอยกลับ | **smoke test ใน repo (`tests/smoke.mjs` อ่านอย่างเดียว ใช้ใน runbook)** · release notes ภาษาคน · UAT · runbook · ซ้อม down→up บนฐานที่มีข้อมูล | ทุกอย่าง | `tests/smoke.mjs` · `RELEASE-NOTES.md` · `UAT-CHECKLIST.md` · `docs/DEPLOY-RUNBOOK.md` · `CHANGE-REPORT.md` | 35 |

**นับ (m10):** ✏️ แก้ repo เดิม **8/12 LAB** (4–10, 12) · ถ้านับเฉพาะแก้โค้ด/schema/เทสต์ของระบบ (ไม่นับ CLAUDE.md/settings ของ LAB 4) = **7/12** (5–10, 12) > ครึ่ง · รวม LAB 0 = 7/13 ก็ยังเกินครึ่ง · ครบตามโจทย์: migration (LAB 8) · เปลี่ยนกฎ (LAB 6) · บั๊กจากร้องเรียน (LAB 7) · ฟีเจอร์ใหม่ (LAB 9)
**เวลารวม ~655 นาที ≈ 10.9 ชม.** [คาด · หลังใช้ขอบเขตเบราว์เซอร์ M6] → **2 วันเต็ม** (วันที่ 1 LAB 0–7 ≈ 5.7 ชม. · วันที่ 2 LAB 8–12 ≈ 5.3 ชม.) **หรือ 3 ครึ่งวัน** (LAB 0–5 ≈ 3.7 ชม. · LAB 6–8 ≈ 3.3 ชม. · LAB 9–12 ≈ 4 ชม.) · ปรับด้วยเวลาจริงจากรอบ RUNNER

ลำดับ CR ในบทเรียงเล็ก → ใหญ่ (กฎ → บั๊ก → schema → ฟีเจอร์ → รายงาน) ตาม CRD §1 ไม่ใช่ตามเลข CR

---

## 7. รายละเอียด LAB (สาระ · ผลที่คาด · กับดัก · ภาพ)

พรอมต์เต็มอยู่ใน `PROMPTS.md` · LAB 6–10 มี 💬 2 กล่อง (ส่วนที่ 1 วิเคราะห์ใน **Plan mode** · ส่วนที่ 2 ลงมือ) · LAB 9 มี 3 กล่อง · README บอกให้กด `Shift+Tab` จนขึ้น plan mode ก่อนวางส่วนที่ 1 แล้วสลับกลับก่อนวางส่วนที่ 2

| LAB | สาระที่ต้องเกิด | ผลที่คาด (แหล่ง) | 👀 กับดักที่ควรเขียน | ภาพ |
|---|---|---|---|---|
| 0 | docker · node ≥ 22.18 (check-rules import `.ts` ตรง) · git · `netsh … excludedportrange` · พอร์ต 4000/5433 ว่าง · container `sabai-*` ของบท 04 · image `rea-lab:6.4.0` + `mcp doctor` · `Get-ExecutionPolicy -List` | ช่วงจอง 2970–3069 ครอบ 3000 [รันจริง:A2 บนเครื่องผู้สอน] · 4000 นอกช่วง (D5) · `mcp doctor` exit 0 | ช่วงที่จองต่างกันแต่ละเครื่อง/หลังรีบูต · ถ้า 4000 โดนจอง ตั้ง `$env:WEB_PORT` (PREP P3) · execution policy `Restricted` ไม่เป็นไร (ใช้ `-ExecutionPolicy Bypass` · M8) · `rea-lab --version` ไม่ใช่คำสั่งที่พิสูจน์แล้ว (ใช้ `mcp doctor`) | `concept-17-reserved-ports.jpg` · `lab0-checklist.png` |
| 1 | เปิด 2 project · health · reset · check-rules · e2e-legacy (api+chromium) · จำแนกข้อแดง · เทียบคำอ้าง H1–H6 · `git init` + baseline | check-rules **90/90** [รันจริง:A6 ที่ BUG_MODE=0 · หลังถอดสวิตช์: รันจริง:PREP V4] · e2e-legacy api+chromium 42 รายการ (api 6 + UI 36): **Playwright สรุป "41 passed · 1 failed"** · ใน 41 มี expected-fail 3 (TC-TRN-03 · TC-GC-04 · TC-SEC-04) → ผ่านจริง 38 · failed 1 (TC-SEC-05) [บันทึกบท 04 + รันจริง:PREP V5] · build ~42 วิ [รันจริง:A2] | **Playwright นับ `test.fail()` ที่ล้มตามคาดเป็น passed** → ต้องนับจาก annotation (`--reporter=list`/html) ไม่งั้นงงว่า 38+3+1 ไม่ตรง 41+1 · TC-SEC-05 แดง = "เทสต์ล้าสมัย" ไม่ใช่บั๊ก (ระบบปฏิเสธถูก แค่ 422 ≠ 403) · ห้ามแก้ให้เขียว · ไฟล์ใหญ่ห้าม commit (`rea-out/`, `node_modules/`) · build ครั้งแรก > 2 นาที → background | `lab1-handover.png` |
| 2 | `docker cp` static → analyze → summary · `record-har.mjs` ผ่าน `127.0.0.1:4000` → `har-records` → inspect HAR + `--sensitive-value` → `har-api` · `capture-browser-scenario` ผ่าน network `sabai06-net` (`http://sabai06-web:3000` · D7) หน้าสรุป ฿1,000 → `rea-tools.mjs shot` ดึงภาพ · ติดป้าย static/runtime/inference/unknown + **`[E ev_xxxxxxxx]` ทุกแถว** | endpoint static **9** · route stub **25/25** · HAR **7 endpoint / 10 ครั้ง** · scenario 12/12 step ฿1,000 [รันจริง:A2 ที่พอร์ต 3261 · ผ่าน network: รันจริง:PREP V7] | `localhost` ใน HAR → `[::1]` REA ไม่รับ · รหัสผ่านใน body ไม่ถูกปิดเอง · `/api/me` `/api/services` ไม่อยู่ใน HAR เพราะ Server Component อ่าน DB ตรง (missing ≠ absent) · PowerShell `>` ได้ไฟล์ BOM → ใช้ `rea.ps1 -Out` · `.ps1` ถูกบล็อก → `powershell -ExecutionPolicy Bypass -File` · [E] = "ทำอยู่" ไม่ใช่ "ควรทำ" | ทบทวน `../05_…/img/concept-05-evidence-not-opinion.jpg` · `../05_…/img/concept-06-missing-not-absent.jpg` · `../05_…/img/concept-10-passive-driven-har.jpg` · `../05_…/img/concept-12-evidence-badge-e.jpg` · `lab2-rea-inventory.png` · `lab2-scenario-final.png` (ภาพจาก REA จริง) |
| 3 | Explore subagent อ่าน repo · psql `\dt` `\d booking` · ตาราง route 25 · BR-01–20 → ไฟล์:ฟังก์ชัน · DB constraint ↔ โค้ด · test hooks · กับดัก · triangulation ติดป้าย [E]/[source]/[DB]/[SPEC] · SPEC-GAPS · ตรวจทาน 5 ข้อด้วยตาตัวเอง | 19 ตาราง · CHECK 51 · FK 25 · EXCLUDE 2 [รันจริง:A2] · SPEC ไม่ตรง ≥ 7 จุด: **S2 S3 S5–S9** + พอร์ต/ชื่อ container ในเอกสารเก่า [CN §8 + PREP P4] · 🔒 S4 (= L2 ข้อสอบชุด B ข้อ 5) อาจโผล่ในรอบจริง → **ห้ามลง README/ภาพ** (M10) | AI เดาหน้าที่จากชื่อไฟล์ → ทุกแถวต้องมี `file:line` · ข้อ SPEC ขัดโค้ดให้เป็น "คำถามถึงร้าน" ไม่ตัดสินเอง · Explore ได้ข้อสรุป ไม่ได้เนื้อไฟล์ | `concept-03-four-eyes.jpg` (ใช้ซ้ำ) · `lab3-triangulation.png` · `lab3-db-rules.png` (ทั้งคู่ห้ามมีแถว S4/L2) |
| 4 | CLAUDE.md ≤ ~60 บรรทัด · deny `Edit(e2e-legacy/**)` · ทดสอบรั้ว**ในเซสชันใหม่** | Edit ถูกปฏิเสธ: *"File is in a directory that is denied by your permission settings."* [MT §M1 ตรวจแล้วบนเครื่องผู้สอน] | `Write(...)` ใช้กับ file rule ไม่ได้ · deny ไม่กัน Bash `sed` → เขียนห้ามไว้ใน CLAUDE.md ด้วย · ไม่ deny `db/init/` (CR-04 ต้องแก้ 01/02 สำหรับติดตั้งใหม่) | `concept-18-claude-md-fence.jpg` · `lab4-deny-test.png` |
| 5 | seam `POST /api/test/clock` (ปิดเมื่อ `ALLOW_TEST_RESET=0`) · golden API ~40–60 เคสนิ่ง 2 รอบ · README golden = ค่า **[E]** + SHA-256 ย่อของไฟล์ golden · `e2e-cr/` + characterization หน้าสรุป (ยอดเทียบ [E] ของ scenario LAB 2) · known issue 3 เรื่อง (บัตรปลอมไม่เตือน · เบอร์ "abc" · owner ยกเลิกแทน) · mutant X1–X3 | API บัตรปลอม 422 `GC_NOT_FOUND` แต่หน้าจอไม่เตือน · เบอร์ "abc" จองได้ 201 · owner ยกเลิก 200 [รันจริง:A6 CN §7 L5 L6 L7] · ผล mutant = [คาด: X2 X3 ถูกฆ่าด้วย golden ราคา/รถ · X1 ขึ้นกับว่ามีผู้ใช้ยอด ฿10,000 พอดีหรือไม่ — รอผลจริง] | aria snapshot ไม่ล็อกตัวเลข (ใช้ `data-amount`) · `-u` ห้ามรันโดยไม่อ่าน · คืนไฟล์ mutant ทุกครั้ง (`git checkout -- <ไฟล์>`) · golden ต้องตัด id/เวลาสร้าง | `concept-06` `07` `08` `09` (ใช้ใน 🎓) · `lab5-golden.png` · `lab5-mutants.png` |
| 6 | คำถาม → **อธิบายการคิดราคาเดิม (`bestPercent`/`calcPrice`/`buildQuote` + ที่มาของ "วันนี้") ด้วย file:line (m12)** → answers → impact (รวม unit test ใน check-rules ที่เรียก `calcPrice` ตรง E45/E50/E71) → ค่าคาดหวังคำนวณเอง → แดง → แก้ → check-rules **diff ว่าง** · golden ผ่าน (ล็อก 10 ต.ค. ก่อนวันมีผล) | กลุ่ม 3/5/6 ที่จอง 1 พ.ย. = ฿2,850 / ฿4,250 / ฿5,100 · 31 ต.ค. 23:59 = ฿3,000 · E26 ฿3,000 · E28 ฿4,500 · E79 ฿6,000 ไม่ต้องแก้ [CRD §1 คาด] | "วันที่จอง" ≠ วันนัด · default ของพารามิเตอร์ใหม่ใน `calcPrice` ต้องเป็นอัตราเดิม ไม่งั้น unit test เดิมพัง · ราคาเปลี่ยนข้ามเที่ยงคืน → 409 `PRICE_CHANGED` | `concept-19-effective-date.jpg` · `lab6-red-green.png` |
| 7 | ทำซ้ำเรื่องร้องเรียน (guest เบอร์ 0810000003 ซ้ำ B03) แดง = [E] ขัด [D:CR-03] · normalize เบอร์ · ล็อกกันกดพร้อมกัน (advisory lock ของ guest) · แชทได้ข้อความ 3 ภาษา · UI `book-error` | ก่อนแก้ guest ส่งซ้ำ 3 ครั้ง → 201 ทั้ง 3 [รันจริง:A6 CN §7 L1] · หลังแก้ AC1 409 `existing:"B03"` · AC8–9 `[201, 409]` [CRD คาด] | BOOK-06 (คนละคนกดพร้อมกัน) ต้องยังได้ `SLOT_TAKEN` ไม่ใช่ `DUPLICATE_BOOKING` · ตรวจแค่ปิดปุ่ม = แชท/API ยังซ้ำ · deadlock ถ้าลำดับล็อกไม่คงที่ | `concept-20-double-tap.jpg` · `lab7-duplicate-error.png` (screenshot) · `gif-TC-CR03-11.gif` |
| 8 | ทำไม init ไม่พอ · migration idempotent + down · รันบนฐานที่มีนัดใหม่ 2 ครั้ง · แก้ 01-schema/02-seed สำหรับติดตั้งใหม่และ reset · รายชื่อตารางที่ reset ล้าง · แชท · ส่วน ข (ถ้าทัน) · tag image เดิมก่อน build | AC1–9 [CRD คาด] · slots 22/24 ต.ค. S01 23 รอบ [รันจริง:A6] · check-rules 90/90 (ไม่มีเคสวันที่ 23 ต.ค./5 ธ.ค./31 ธ.ค.) [CN §6.1] | ⚠️ รัน SQL ด้วย `docker cp` + `psql -f` (ห้าม `Get-Content \| docker exec -i` ใน PowerShell 5.1 → ภาษาไทยกลายเป็น ?) · **ผล psql ภาษาไทยที่ PowerShell แสดงอาจเพี้ยนทั้งที่ใน DB ถูก** (ถอดด้วย OEM codepage) → ตรวจด้วย `SELECT name_th = 'วันปิยมหาราช'` ได้ `t` ห้ามแก้ข้อมูลเพราะเห็นบนจอ (M7) · ส่วน ข ส่งชื่อไทยด้วย node ไม่ใช่ `Invoke-RestMethod -Body` · 👀 (หลังทำ · M9) ลืมรายชื่อตาราง reset → reset 500 ทั้งชุด · ใส่ seed ไฟล์ใหม่ → reset ไม่มีวันหยุด · `down -v` = ผิดหนังสือ · `backups\` ต้องสร้างก่อน `docker cp` | `concept-13` (ใช้ซ้ำ) · `lab8-migration-twice.png` · `lab8-shop-closed.png` (screenshot) |
| 9 | แตกงาน 3 ขั้น (API เลื่อน · รอบเฉพาะคนเดิม · UI) · AC1–14 ด้วย API · AC15 Playwright 3 เบราว์เซอร์ | AC4 B02 19:00→19:30 = 200 (ไม่นับชนตัวเอง) · AC6 รอบของ B01 วันที่ 14 ต.ค. ไม่มี 16:00 ขณะ `/api/slots` มี · AC13 คอร์ส `reserved` = 1 ไม่ใช่ 2 [CRD คาด] | ใช้ `/api/slots` เดิมตรง ๆ = ผิด (ได้นักบำบัดคนอื่น) · `booking.period` เป็น GENERATED แต่ `booking_slot.period` ต้องอัปเดตเอง · "ยกเลิก+จองใหม่" ทำคอร์สหมด | `concept-21-reschedule-self-overlap.jpg` · `lab9-reschedule-dialog.png` (screenshot) · `gif-TC-CR01-15.gif` |
| 10 | **อธิบายหลังร้านเดิมที่จะต่อยอด (`lib/server/admin.ts` · `AdminQueue` · `NavMenu` · ตรวจสิทธิ์ owner · หน่วยเงิน) (m12)** · SQL บน seed คำนวณค่าคาดหวัง**ก่อน**เขียนโค้ด (ป้าย [D:CR-05] นิยาม + [E sql] ค่า) · API + หน้า + CSV BOM · 92/93 วัน · สิทธิ์ | ก.ย. completed 3 cancelled 1 revenue 1,900 · ต.ค. pending 11,130 [รันจริง:A6 SQL บน seed CN §2] | ค่าคาดหวังห้ามลอกจากหน้ารายงานที่เพิ่งทำ (อบบั๊ก) · โซนเวลา (นัดตกวันผิดถ้าใช้ UTC) · NUMERIC → สตางค์ · CSV ไม่มี BOM → Excel ภาษาไทยเพี้ยน | `concept-22-independent-oracle.jpg` · `lab10-report-page.png` (screenshot) |
| 11 | รันทุกชุด 3 เบราว์เซอร์ (`npm run test:all` · background) · `docker cp` static v2 → analyze → `cmp-input` → `compare-application-versions` → `cmp-sum` · **HAR ซ้ำบน v2 (`record-har.mjs` → `har-records` → `inspect-web-network-capture` → `har-api`) เทียบตาราง API v1↔v2 · `capture-browser-scenario` ซ้ำบน v2 + `shot`** (คำสั่งเดียวกับ LAB 2 ที่พิสูจน์แล้ว · M4) · ตาราง CR × "REA เห็นไหม" · ไฟล์ทุกไฟล์ใน `git diff --stat` โยง CR · ORACLE-CHANGES ครบ | e2e-legacy **114 รายการ: Playwright สรุป "113 passed · 1 failed"** = ผ่านจริง 106 · expected-fail 7 (TC-TRN-03 ×3 · TC-GC-04 ×3 · TC-SEC-04 ×1 เพราะ `security.api.spec.ts` อยู่ project `api` รันครั้งเดียว) · failed 1 (TC-SEC-05) [คาด · ยืนยันด้วย PREP V5b] · REA static เห็นเฉพาะ chunk ฝั่งเบราว์เซอร์ที่เปลี่ยน (เช่น v1→v3 เห็น `chunks/app/book/page` · v1→v2 กฎฝั่งเซิร์ฟเวอร์ไม่เห็น) [รันจริง:A2] → คาด: CR-01 (`account/page`) CR-05 (หน้าใหม่ · มัก `unknown`) เห็น · CR-02 CR-03 ไม่เห็น · `unknown` หลายร้อย · HAR v2: 7 endpoint เดิม status เดิม (+ `/api/holidays` ถ้าหน้าจองเรียก) · scenario v2 ฿1,000 เท่าเดิม [คาด] | อ่านเฉพาะ `changed` ที่เป็น `chunks/app/*` · `added` ได้เฉพาะ coverage complete (มักเป็น unknown) · REA ไม่เห็น ≠ ไม่ได้เปลี่ยน · HAR/scenario = หลักฐาน [E] ว่า "เส้นทางเดิมของลูกค้าไม่เปลี่ยน" ไม่ใช่หลักฐานว่า CR ทำงาน (ต้องใช้เทสต์ CR) | `concept-23-version-compare-sabai.jpg` · ทบทวน `../05_…/img/concept-08-version-compare.jpg` · `lab11-regression.png` · `lab11-rea-compare.png` |
| 12 | **✏️ `tests/smoke.mjs` (อ่านอย่างเดียว · exit 0/1) + commit** · release notes ถึงคุณจันทร์ · UAT ต่อ CR · runbook (สำรอง → tag image → migration → up → smoke → ถอยกลับ) · ซ้อมถอยกลับ: สำรอง → จองนัดใหม่ → stop web (smoke ต้อง exit 1) → down → ตรวจนัดอยู่ → up → start → smoke exit 0 → ตรวจ | นัดใหม่ยังอยู่หลัง down→up · วันหยุดกลับมา 3 วัน · smoke 0/1 ตามสถานะ [คาด] | known issues ที่ยังเหลือต้องเขียน (cookie หลัง logout · owner ยกเลิกแทน · reset เปิดในโหมดใช้งานจริง) · down ทำวันหยุดที่ร้านเพิ่มเองหาย → เขียนในแผน · smoke ห้าม reset/สร้างข้อมูล (รันบนระบบจริง) · 🔒 RELEASE-NOTES รอบจริงถ้ามีเรื่อง "กดเสร็จก่อนเวลานัด" (L2) ห้ามลงภาพ/README (M10) | `concept-16` (ใช้ซ้ำ) · `lab12-rollback.png` · `lab12-release-notes.png` · `outro-01-signoff-party.jpg` |

---

## 8. การตัดสินใจ และรายการ "แก้โฟลเดอร์เริ่มต้น" (ต้องทำก่อนรันรอบ RUNNER)

### 8.1 ข้อตัดสิน (D3 · D4 ของ orchestrator + ของบทนี้)

| # | เรื่อง | ตัดสิน | เหตุผล |
|---|---|---|---|
| T1 | `BUG_MODE` / `flags.ts` / `data-bug-mode` | **ถอดออกทั้งหมด** ตาม CRD §2.3 | บท 06 ให้ Agent อ่าน repo ทั้งหมด → สวิตช์บั๊กเฉลยใน 5 นาที · ระบบจริงไม่มีสวิตช์บั๊ก |
| T2 | บั๊กเทียม 3 ตัวของบท 04 | ไม่อยู่ใน repo · เป็น mutant ใน `_solution/mutants/` (ใช้กับข้อสอบ) | ใช้วัดตาข่าย |
| T3 | บั๊กจริง L1–L8 (CN §7) | **คงไว้** ไม่มีคอมเมนต์/flag · L1 → CR-03 · L5 L6 L7 → LAB 5 known issue · L4 → ข้อสอบ A ข้อ 5 · L2 → ข้อสอบ B ข้อ 5 · L3 L7 L8 → release notes · **กัน L2 รั่ว (M10):** ผลที่คาดของ SPEC-GAPS เขียน S2 S3 S5–S9 (ไม่มี S4) · README/IMAGES (`lab3-*`, `lab12-release-notes.png`) ห้ามมีแถว S4/L2 แม้รอบ RUNNER จะเจอ (เก็บใน `_solution` เท่านั้น) · CR-05 AC4 (CRD) ในเฉลยอ้างอิงต้อง `reset {now:"2026-10-10T15:00:00+07:00"}` ก่อนกดเสร็จ B06 (นัด 15:00) เพื่อไม่พึ่ง L2 · พรอมต์ LAB 10 ข้อ 4 สั่งตั้งเวลาให้ถึงเวลานัดก่อนกดเสร็จ | ระบบจริง "เขียวแต่ยังมีบั๊ก" · ข้อสอบชุด B ต้องใช้บั๊กที่ไม่มีเฉลยเผยแพร่ |
| T4 | `web/SPEC.md` (D4) | **เก็บไว้เป็นเอกสารเก่า** ลบเฉพาะส่วน BUG_MODE/BUGS.md · คงพอร์ต 3000 และชื่อ `sabai-web`/`sabai-db` เดิมในเอกสาร (ไม่ตรง compose ใหม่ = จุด SPEC-GAP เพิ่ม) | เอกสารเก่าไม่ตรงโค้ด = สมจริง ใช้สอน LAB 3 |
| T5 | known failures ใน e2e-legacy (D3) | TC-TRN-03 · TC-GC-04 · TC-SEC-04 ติด `test.fail(true, 'KNOWN-ISSUE …')` คำอธิบายตาม LT §4.2 · **TC-SEC-05 ปล่อยแดง** | เหมือนผู้รับเหมาบันทึก known issue ไว้ (ไม่ใช่เฉลยรั่ว: เป็นอาการที่ผู้ใช้เห็นอยู่แล้ว) · TC-TRN-03 ตรงกับข้อสอบ **ชุด A** (ฝึก) เท่านั้น · ชุด B (L2) ไม่มีเทสต์เดิมชี้ · SEC-05 = โจทย์ "เทสต์ล้าสมัยหรือบั๊ก" ใน LAB 1 |
| T6 | check-rules เดิม (D3) | เก็บทั้ง 90 เคส ไม่ตัด | ไม่มีเคสไหนเฉลย L1–L8 ตรง ๆ (grep แล้วไม่พบ L2 ใน CRD §2.2) · E39/E40/E88 กดเสร็จนัดอนาคต = ระเบิดเวลาของข้อสอบ B ข้อ 5 (ตั้งใจ) |
| T7 | ชื่อ container/project/network | **`sabai06-*` · อนุมัติแล้ว (BRIEF D7–D8)** (PREP P3) · ข้อสอบใช้ `sabai06x-*` แยก (M11) · `e2e-legacy/README-LEGACY.md` ไม่อ้างชื่อ network ตายตัวแล้ว (PREP P5 ตรวจ) | ชื่อ `sabai-web` `sabai-db` และ project `sabai-db` ชนบท 04 → compose จะ "ยึด" container บท 04 มาสร้างใหม่ · volume `sabai06-pgdata` ตาม D1 · REA ต่อเว็บผ่าน network `sabai06-net` ที่ `http://sabai06-web:3000` (D7) |
| T8 | ผู้เรียนทำงานที่ไหน | ในโฟลเดอร์บทเอง · LAB 1 `git init` · `.git/info/exclude` กัน `_solution/ img/ README.md EXAM.md rea-out/ node_modules/` · README แนะนำ: ถ้าโฟลเดอร์บทอยู่ใน repo คอร์สที่ clone มา ให้คัดลอกทั้งโฟลเดอร์ไป `C:\work\sabai06` ก่อน (กัน nested repo) | ต้องมี diff/commit ต่อ CR และใช้ git bundle ส่งข้อสอบ |
| T9 | คำตอบ CR | แยกไฟล์ `CHANGE-REQUESTS/answers/` เปิดหลังเขียนคำถาม · ให้ "สิ่งที่ตกลง" ทางเทคนิค + ตัวอย่าง 2–4 ตัว · AC เต็มอยู่ใน `_solution` | ฝึกถาม + ทำให้ผลของทุกคนตรวจด้วยชุดเดียวกันได้ |
| T10 | เทสต์ใหม่ของ CR วางที่ไหน | API: `tests/crNN.mjs` (Node ไม่มี dependency แบบ check-rules) · UI: `e2e-cr/` (Playwright ข้าง `web/`) · **ไม่เพิ่มเคสใน check-rules** ระหว่าง LAB | check-rules diff ต้องว่างตลอดบท (สอน "ค่าคาดหวังเดิมไม่แตะ") · ข้อสอบข้อ 4 จึงฝึกแก้ check-rules แบบมี ORACLE-CHANGES |
| T11 | mutant ใน LAB 5 | X1–X3 ใหม่ (tier ขอบ ฿10,000 · คันละ 5 คน · กลุ่ม 15%) **ไม่ซ้ำ M1–M9 ของข้อสอบ** | ไม่เฉลยตัวที่ grader ใช้ |
| T12 | rea-lab | ไม่ build ในบทนี้ · LAB 0 ตรวจด้วย `docker image inspect` + `mcp doctor` (exit 0) · ถ้าไม่มีให้ build จากโฟลเดอร์ `05_rea-reverse-engineer-legacy-petshop\rea` ใน repo คอร์สที่ clone ไว้ (2.65 GB · ไม่ใช้ path `../05_…` เพราะผู้เรียนอาจคัดลอกบทไป `C:\work\sabai06`) | ใช้ image เดียวกับบท 05 |
| T13 | `db/init` vs migration (m8 · BRIEF D1) | **migration (`db/migrations/NNN_*.sql`) = ทางเดียวสำหรับฐานที่มีข้อมูลอยู่แล้ว** · แก้ `db/init/01-schema.sql` + `02-seed.sql` ได้เฉพาะเพื่อให้เครื่องติดตั้งใหม่และ reset (`SEED_SQL_PATH`) ตรงกับ migration · ห้ามใช้ init เป็นวิธี deploy · ประโยคเดียวกันอยู่ใน CLAUDE.md (พรอมต์ LAB 4) | ตรง D1 (ไม่แก้ init "แทน" migration) แต่ระบบที่ติดตั้งใหม่ต้องได้ schema เดียวกัน |
| T14 | ขอบเขตเบราว์เซอร์ (M6) | CR LAB 6/7/8/10: e2e-legacy `api + chromium` · e2e-cr chromium (spec ใหม่ของ CR 3 เบราว์เซอร์) · 3 เบราว์เซอร์เต็มเฉพาะ LAB 9 ส่วนที่ 3 + LAB 11 | ประหยัด ~9 นาที × 4 LAB · ยังพิสูจน์ cross-browser ก่อนส่งมอบ |
| T15 | PowerShell 5.1 (M7, M8, D9) | ทุกพรอมต์บอก "รันคำสั่งด้วย PowerShell" · `.ps1` ผ่าน `powershell -NoProfile -ExecutionPolicy Bypass -File` · API ภาษาไทย/จีนส่งด้วย node · ตรวจไทยใน DB ด้วย SQL · path จากโฟลเดอร์บท + `Push-Location` | เครื่องผู้เรียน `Restricted` · encoding OEM/ISO-8859-1 ทำข้อมูลดูเพี้ยนหรือเพี้ยนจริง |

### 8.2 เตรียมโฟลเดอร์เริ่มต้น → ย้ายไป `PREP.md` (H1)

รายการ P1–P11 ฉบับใช้งานจริง (ข้อความเดิม→ใหม่ตรงตัว · คำสั่งตรวจ · V1–V8 · MANIFEST · รูปแบบ `PREP-LOG.md`) อยู่ใน **`PREP.md`** · ทำโดย **agent PREP แยก** (ได้รับอนุญาตแก้ `web/ db/ e2e-legacy/`) · **runner ไม่เตรียมเอง** และไม่เห็น `_solution/` — ตรวจแค่ checksum (`C:/t/work/b2prep/MANIFEST.sha256`) + grep ตาม RUNNER §1

| P | เรื่อง | สถานะ 12 ต.ค. 2026 (B2F อ่านอย่างเดียว) |
|---|---|---|
| P1 | ถอด `BUG_MODE`/`flags.ts` → `config.ts` (CRD §2.3) | ❌ ต้องทำ |
| P2 | check-rules ค่าเริ่ม 4000 | ✅ ทำแล้ว → ตรวจซ้ำเท่านั้น |
| P3 | compose `sabai06-web`/`sabai06-db`/`sabai06-net` · `${WEB_PORT:-4000}` `${DB_PORT:-5433}` (service key **และ** `container_name` · host ใน `DATABASE_URL` = `sabai06-db`) | ❌ ต้องทำ |
| P4 | `web/SPEC.md` = เอกสารเก่า 1.0 (ลบเฉพาะส่วน BUG_MODE) | ❌ ต้องทำ |
| P5 | `e2e-legacy/` (`test.fail` 3 ข้อ · 4000 · `README-LEGACY.md` ไม่อ้าง `sabai-net`) | ✅ ทำแล้ว → ตรวจซ้ำเท่านั้น |
| P6 | `tools/` (`rea.ps1` · `rea-tools.mjs` + คำสั่ง `shot` · `record-har.mjs` 4000 · scenario `http://sabai06-web:3000` · package.json · .gitignore) | ❌ ต้องทำ |
| P7 | `CHANGE-REQUESTS/` 7 ไฟล์ + `answers/` 5 ไฟล์ = 12 | ❌ ต้องทำ |
| P8 | `EXAM.md` (ภาค 1) | ❌ ต้องทำ |
| P9–P11 | เฉลยอ้างอิง/mutant/zip ข้อสอบ = งานถัดไป · ห้ามสร้าง `db/migrations` `docs` `tests` `e2e-cr` · ห้ามแตะ `db/init` `web/lib/server` `img/` | — |

ตรวจหลังเตรียม (PREP V1–V8): 2 project ขึ้น healthy (พอร์ตที่ orchestrator ให้) · check-rules **90/90** (รันจากราก) · e2e-legacy api+chromium = Playwright "41 passed · 1 failed" (expected-fail 3 อยู่ใน 41 · failed = TC-SEC-05) · `test:all` = 114 รายการ "113 passed · 1 failed" (expected-fail 7) · `grep -rniE "bug_mode|bug-mode|bugmode|flags" web` = 0 (ทำหลัง P4 · m1) · REA static/HAR/scenario ผ่าน network `sabai06-net` + `shot` ได้ภาพ

---

## 9. ✅ รูบริก: เช็กลิสต์ "รับงานแก้ระบบเดิมที่ดี" (20 ข้อ)

**ดีมาก ≥ 18/20 · ใช้ได้ 14–17 · ต้องแก้ < 14**

**A. รับมอบและเข้าใจ (LAB 1–3)**
- ☐ 1. `HANDOVER-CHECK.md` ทุกตัวเลขมาจากคำสั่งที่รันจริง · คำอ้างทุกข้อในบันทึกส่งมอบได้ ✅/❌/⚠️ พร้อมหลักฐาน · ข้อแดงจำแนกโดยไม่แก้เทสต์
- ☐ 2. `docs/REA-INVENTORY.md` แยก static / runtime / inference / unknown · ทุกแถวมี `[E ev_xxxxxxxx]` · ไม่มีประโยค "ไม่มี X" จากหลักฐาน coverage partial
- ☐ 3. `SYSTEM-MAP.md` ทุกแถวอ้าง `file:line` หรือชื่อฟังก์ชัน/constraint · ตรวจทานด้วยตาตัวเองครบ 5 ข้อ
- ☐ 4. triangulation มีครบ REA / source / DB พร้อม ✅⚠️❌ · `SPEC-GAPS.md` เป็นคำถามถึงร้าน ไม่ใช่ AI ตัดสินเอง

**B. รั้วและตาข่าย (LAB 4–5)**
- ☐ 5. CLAUDE.md สั้น มีวิธีรัน/ห้ามแตะ/กับดัก · ทดสอบรั้วในเซสชันใหม่แล้วถูกปฏิเสธจริง
- ☐ 6. golden master รันเทียบ 2 รอบติดผ่านทั้งคู่ (นิ่ง) · ตัดฟิลด์ที่เปลี่ยนเองและเขียนเหตุผล
- ☐ 7. known issue ล็อกคู่ (ค่าปัจจุบัน + `test.fail`) ไม่ได้แอบแก้ · seam ปิดได้เมื่อ `ALLOW_TEST_RESET=0`
- ☐ 8. mutant 3 ตัวรันครบ คืนไฟล์ครบ · ตัวที่รอดอธิบายรูของตาข่ายได้

**C. Change Request (LAB 6–10)**
- ☐ 9. ทุก CR มีคำถาม + อธิบายของเดิมด้วย file:line + `docs/impact/CR-0N.md` (ไฟล์ × เทสต์ · DB · i18n · แชท · หลักฐาน grep) **ก่อน** diff · ค่าคาดหวังทุกแถวมีป้าย [D:CR-0N] หรือ [E]
- ☐ 10. ทุก CR มี commit เทสต์แดงก่อน commit แก้
- ☐ 11. `web/scripts/check-rules.mjs` `tests/golden/` `e2e-legacy/` ไม่มีค่าคาดหวังเปลี่ยน หรือทุกจุดมีแถวใน `ORACLE-CHANGES.md`
- ☐ 12. CR-02 ทดสอบทั้ง 2 ฝั่งของวันมีผล และนัดเก่าไม่เปลี่ยนยอด
- ☐ 13. CR-03 ทดสอบกดพร้อมกัน (สมาชิกและไม่ล็อกอิน) + แชท · BOOK-06 ยังเป็น `SLOT_TAKEN`
- ☐ 14. CR-04 migration รัน 2 ครั้งบนฐานที่มีนัดใหม่ ไม่ error ข้อมูลอยู่ครบ · reset ผ่าน 2 ครั้งติด · ไม่ใช้ `down -v`
- ☐ 15. CR-01 มีเคสเลื่อนทับเวลาเดิมของตัวเอง + นักบำบัดคนเดิมไม่ว่าง + Playwright 3 เบราว์เซอร์
- ☐ 16. CR-05 ค่าคาดหวังมาจาก SQL ที่รันก่อนเขียนโค้ด · CSV มี BOM เปิด Excel ภาษาไทยไม่เพี้ยน

**D. Regression (LAB 11)**
- ☐ 17. ตัวเลขผ่าน/ทั้งหมดทุกชุดใน `REGRESSION-REPORT.md` ตรงกับการรันซ้ำ · ครบ 3 เบราว์เซอร์
- ☐ 18. ตาราง "CR × REA เห็นไหม" (static + HAR v1↔v2 + scenario) อธิบายสิ่งที่ REA มองไม่เห็นและเทสต์ที่พิสูจน์แทน · ไฟล์ที่เปลี่ยนทุกไฟล์โยง CR ได้ · TRACEABILITY ครบ

**E. ส่งมอบ (LAB 12)**
- ☐ 19. `RELEASE-NOTES.md` ภาษาคน คุณจันทร์อ่านเข้าใจ · มี known issues ที่ยังเหลือ · `UAT-CHECKLIST.md` ต่อ CR มีช่องลงชื่อ
- ☐ 20. ซ้อมถอยกลับจริง (สำรอง → down → up) ข้อมูลนัดอยู่ครบ · `tests/smoke.mjs` อ่านอย่างเดียว exit 1 ตอนเว็บหยุด / exit 0 ตอนปกติ · runbook เรียก smoke และไม่มี `down -v`

---

## 10. 📖 คำศัพท์ (ใหม่ในบท 06 · คำจากบท 04–05 ใช้ต่อได้)

| คำ | ความหมายง่าย ๆ |
|---|---|
| **ระบบเดิม (legacy)** | ระบบที่ใช้งานอยู่แล้ว คนสร้างไม่อยู่ เอกสารอาจเก่า |
| **บันทึกส่งมอบ** | เอกสารที่ผู้รับเหมาเดิมบอกว่าส่งอะไร ผ่านอะไร = คำอ้าง ไม่ใช่หลักฐาน |
| **Change Request (CR)** | หนังสือขอเปลี่ยนระบบ 1 เรื่อง จากเจ้าของงาน |
| **ทะเบียน CR (register)** | ตารางคุมสถานะทุก CR |
| **ตกลงขอบเขต** | คำตอบ + สิ่งที่ตกลงร่วมกันก่อนลงมือ |
| **UAT / ตรวจรับ** | เจ้าของงานลองเองตามรายการแล้วลงชื่อรับ |
| **Triangulation** | เทียบ 3 แหล่ง (REA · โค้ด · DB) ตรงกันจึงมั่นใจ |
| **Constraint (CHECK / EXCLUDE)** | กฎที่ฐานข้อมูลบังคับเอง แม้โค้ดลืมตรวจ |
| **Golden master** | ผลจริงทั้งก้อนที่บันทึกไว้เทียบทุกครั้งหลังแก้ |
| **Characterization test** | เทสต์ที่ล็อก "ระบบทำอะไรอยู่" ไม่ใช่ "ควรทำอะไร" |
| **Known issue** | บั๊กที่รู้แล้วแต่ยังไม่แก้ ล็อกด้วย `test.fail()` |
| **Test seam** | จุดที่ทำให้ทดสอบได้โดยไม่แก้กฎ เช่น เลื่อนนาฬิกา |
| **Mutant / mutation testing** | โค้ดที่แกล้งทำผิด 1 จุด ใช้ดูว่าตาข่ายจับได้ไหม |
| **Impact analysis** | ตาราง "แก้ตรงนี้กระทบไฟล์ไหน เทสต์ไหน" ก่อนลงมือ |
| **Plan mode** | โหมดที่ Claude วางแผนอย่างเดียว ยังไม่แก้ไฟล์ |
| **Regression ที่ตั้งใจ / ไม่ตั้งใจ** | ค่าเดิมเปลี่ยนเพราะ CR สั่ง / เปลี่ยนเองโดยไม่มีใครขอ |
| **ORACLE-CHANGES** | บันทึกค่าคาดหวังเดิมที่เปลี่ยน พร้อม CR ที่อนุญาต |
| **วันมีผล (effective date)** | วันที่กฎใหม่เริ่มใช้ ก่อนหน้านั้นใช้กฎเดิม |
| **Migration** | ไฟล์ SQL เปลี่ยนโครงฐานข้อมูลที่มีข้อมูลอยู่แล้ว |
| **Idempotent** | รันซ้ำกี่ครั้งผลเท่าครั้งแรก ไม่ error |
| **Rollback / แผนถอยกลับ** | วิธีย้อนระบบกลับเวอร์ชันก่อนถ้าพัง |
| **Advisory lock** | กุญแจใน PostgreSQL กันคำขอพร้อมกันทำงานซ้อน |
| **Self-overlap** | เวลาใหม่ทับเวลาเดิมของนัดตัวเอง ต้องไม่นับว่าชน |
| **Oracle อิสระ** | ค่าคาดหวังที่ได้จากทางอื่น (SQL) ไม่ใช่จากหน้าจอที่เพิ่งสร้าง |
| **BOM** | ไบต์หัวไฟล์ที่ทำให้ Excel รู้ว่าเป็น UTF-8 |
| **Traceability matrix** | ตารางโยง CR → BR → TC → ผล |
| **Release notes** | สรุปการเปลี่ยนแปลงภาษาคนสำหรับเจ้าของงาน |
| **Excluded port range** | ช่วงพอร์ตที่ Windows จองไว้ โปรแกรมอื่นใช้ไม่ได้ |
| **[D:CR-0N]** | ป้ายค่าที่คาดหวังจากคำตอบที่ร้านยืนยันใน CR นั้น |
| **[E ev_xxxxxxxx]** (ทบทวนบท 05) | ป้ายค่าที่ได้จากหลักฐานของระบบ (REA/HAR/golden) = "ทำอยู่" ไม่ใช่ "ควรทำ" · ขัด [D] = ผู้ต้องสงสัยบั๊ก |
| **Smoke test** | เทสต์สั้น ๆ แบบอ่านอย่างเดียว รันทันทีหลังขึ้นระบบจริง ว่าระบบหลัก "ยังหายใจ" |

---

## 11. ไฟล์ในบทนี้

**ก่อนเริ่ม** (หลัง PREP · `PREP.md`)

```text
06_sabai-spa-legacy-change-request/
├─ README.md               📖 บทเรียน + พรอมต์ทุก LAB
├─ EXAM.md                 📝 ข้อสอบ (ชุด A ฝึก + กติกาชุด B)
├─ CHANGE-REQUESTS/        📨 บันทึกส่งมอบ · ทะเบียน · หนังสือ CR-01–05
│  └─ answers/             🔒 คำตอบข้อซักถาม (เปิดเมื่อพรอมต์สั่ง)
├─ web/                    ระบบเดิม Next.js (SPEC.md = เอกสารเก่า ฉบับ 1.0)
│  └─ scripts/check-rules.mjs   ชุดตรวจที่ส่งมอบ ชั้น 1 (90 เคส)
├─ db/                     PostgreSQL 16 · init/01-schema.sql · init/02-seed.sql
├─ e2e-legacy/             ชุดทดสอบที่ส่งมอบ ชั้น 2 (Playwright 42 TC)
├─ tools/                  rea.ps1 · rea-tools.mjs (+ shot) · record-har.mjs · scenario-book-quote.json · package.json
├─ img/                    🖼️ รูปประกอบ
└─ _solution/              🔑 เฉลย (ห้ามเปิดก่อนจบ)
```

**หลังจบทุก LAB**

```text
06_sabai-spa-legacy-change-request/
├─ HANDOVER-CHECK.md          # LAB 1  คำอ้าง vs ผลจริง · baseline
├─ rea-out/                   # LAB 2, 11  Evidence ของ REA · HAR v1/v2 · scenario-final.png (ไม่ commit)
├─ backups/                   # LAB 8, 12  pg_dump (ไม่ commit)
├─ docs/
│  ├─ REA-INVENTORY.md        # LAB 2
│  ├─ SPEC-GAPS.md            # LAB 3
│  ├─ IMPACT-TEMPLATE.md      # LAB 4
│  ├─ ORACLE-CHANGES.md       # LAB 4 (อัปเดต LAB 6–11)
│  ├─ impact/CR-0N.md         # LAB 6–10
│  ├─ TRACEABILITY.md         # LAB 6–11
│  ├─ MIGRATION-RUNBOOK.md    # LAB 8
│  └─ DEPLOY-RUNBOOK.md       # LAB 12
├─ SYSTEM-MAP.md              # LAB 3
├─ CLAUDE.md · .claude/settings.json   # LAB 4
├─ KNOWN-ISSUES.md            # LAB 5
├─ tests/
│  ├─ golden/                 # LAB 5  run.mjs + *.json + README.md
│  ├─ cr01.mjs … cr05.mjs     # LAB 6–10
│  └─ smoke.mjs               # LAB 12  ตรวจหลังขึ้นระบบ (อ่านอย่างเดียว)
├─ e2e-cr/                    # LAB 5–10  Playwright ชุดใหม่ (char-booking · cr01 · cr03 · cr04 · cr05)
├─ web/                       # LAB 5–10  ✏️ seam + โค้ด CR (diff ดูด้วย git)
├─ db/migrations/             # LAB 8  001_shop_holiday.sql + .down.sql
├─ CHANGE-REPORT.md           # LAB 6–12
├─ REGRESSION-REPORT.md       # LAB 11
├─ RELEASE-NOTES.md · UAT-CHECKLIST.md   # LAB 12
└─ CHANGE-REQUESTS/REGISTER.md   # อัปเดตสถานะทุก CR
```

---

## 12. IMAGES (53 ไฟล์ใหม่ + อ้างภาพบท 05 อีก 4 ภาพ)

### 12.1 Style prefix ของภาพ jpg บท 06 (นำหน้าทุกพรอมต์ · ต่อด้วยพรอมต์ในตาราง)

```text
Cute kawaii anime-style flat cartoon illustration, thick clean outlines, soft bright pastel colors, bright cheerful lighting. Setting: a contemporary Thai wellness spa in banana-leaf green, cream and gold, with a Thai sala pavilion, lotus pond and orchids; when the scene says "office", use a tidy Thai government-style office with document folders, a rubber stamp and a wooden counter in the same palette. Recurring characters (draw them exactly like this): a cheerful boy with messy brown hair in a blue hoodie (the learner, usually holding a clipboard or a magnifying glass); a friendly round white robot with a black screen face, glowing blue eyes, a curved smile line and an antenna topped with a small blue ball (the AI agent) — the robot has NO logo, emblem, mask or symbol on its body; Khun Chan, the spa owner, a smiling Thai woman with her hair in a bun decorated with a flower, wearing a green Thai dress with gold trim; Nong Bua, a small lotus-flower mascot that waves. Thai title text in bold on a carved golden wooden sign at the top. Speech bubbles have at most 5 words. All Thai text must be spelled exactly as given in quotes. No real brand logos. 3:2 landscape, 1280x853.
```

### 12.2 ตารางภาพ

ประเภท: **jpg gen** = Codex (`cyolo exec - < prompt.txt`) · **png diagram** = HTML → PNG (Noto Sans Thai · 1280 CSS px DSF 2 · ใช้ `05_…/_solution/_design/diagrams/house.css` + `tools/render-png.mjs`) · **png result** = ตาราง markdown → HTML ธีมมืด 1280×800 (SG §4.2) · **screenshot** = headless 1280×800 จากรอบ RUNNER · **gif** = วิดีโอ Playwright → ffmpeg 800×500 (< 3 MB)

| # | ไฟล์ | ใช้ที่ | ประเภท | พรอมต์ภาพ (ต่อท้าย prefix) หรือเลย์เอาต์ HTML |
|---|---|---|---|---|
| 1 | `intro-01-legacy-handover.jpg` | หัวบท | jpg gen | Office scene. Three tired contractor workers in grey uniforms walk out of the door waving goodbye, one hands the boy a big cardboard box labeled "ระบบเดิม" with a sticky note "ผ่านหมดแล้ว". A dusty binder labeled "SPEC v1.0" with a cobweb sits on the box. The robot peeks into the box with a flashlight. Khun Chan stands behind the counter holding an envelope labeled "หนังสือขอเปลี่ยนแปลง". Nong Bua waves from a potted orchid. Title sign "รับงานแก้ระบบเดิม". |
| 2 | `intro-02-change-desk.jpg` | 🧭 ภาพรวม | jpg gen | Office scene. A wooden in-tray holds five envelopes numbered "CR-01" to "CR-05". The boy reads one letter with the robot beside him; the robot points at a whiteboard with five arrows "ถาม", "วิเคราะห์", "ทดสอบ", "แก้", "ตรวจรับ". Khun Chan smiles holding a rubber stamp. Title sign "หนังสือ CR 5 ฉบับ". |
| 3 | `overview-5-phases.png` | 🧭 ภาพรวม | png diagram | หัวเรื่อง "รับมอบ → เข้าใจ → ตาข่าย → Change Request → ส่งมอบ" · การ์ด 5 ใบสีตามช่วง 🟢🟡🔵🟠🟣 แต่ละใบ: เลขวงกลม ① ชื่อช่วง · LAB · pill ไฟล์ที่ได้ (① รับมอบ LAB 1–2 `HANDOVER-CHECK.md` `REA-INVENTORY.md` · ② เข้าใจ LAB 3–4 `SYSTEM-MAP.md` `CLAUDE.md` · ③ ตาข่าย LAB 5 `tests/golden/` `e2e-cr/` · ④ CR LAB 6–10 `docs/impact/` `tests/cr0N.mjs` · ⑤ ส่งมอบ LAB 11–12 `REGRESSION-REPORT.md` `RELEASE-NOTES.md`) · แถบล่าง 🎯 "ทำตามที่ขอ ≠ ของเดิมไม่พัง ≠ ส่งมอบได้" |
| 4 | `concept-01-inherited-system.jpg` | 🎓 1 | jpg gen | Office scene split in two. Left: a big old wooden machine labeled "ระบบเดิม" still running with customers' booking cards coming out; a faded poster on the wall says "SPEC v1.0" with crossed-out lines. Right: the boy and the robot open a toolbox labeled "ทีมใหม่". Above the machine a speech bubble from a departing contractor at the door: "ผ่านหมดแล้วนะ". The robot holds a sign "คำอ้าง ≠ หลักฐาน". Title sign "ระบบที่ได้รับมอบ". |
| 5 | `concept-02-cr-lifecycle.jpg` | 🎓 1 | jpg gen | A conveyor belt in the spa garden carrying one envelope "CR" through six small stations with signs: "รับเรื่อง", "ถามให้ชัด", "วิเคราะห์ผลกระทบ", "ทดสอบ", "แก้", "ตรวจรับ". The robot works at the middle stations, the boy checks a clipboard, and at the last station Khun Chan stamps a green seal. Title sign "ชีวิตของ 1 CR". |
| 6 | `concept-03-four-eyes.jpg` | 🎓 2 · LAB 3 | jpg gen | The spa building drawn as a cutaway: front shop (browser), back office (server) and a basement vault (database). Three viewers: the robot with an x-ray scanner labeled "REA" looking at the front shop, the boy reading an open book labeled "โค้ด", and Nong Bua peeking into the vault where padlocks are labeled "CHECK" and "EXCLUDE". A golden triangle connects the three viewers with a banner "ตรงกัน = มั่นใจ". Title sign "มอง 3 ทาง + ฐานข้อมูล". |
| 7 | `concept-04-browser-only.jpg` | 🎓 2 · LAB 2 | jpg gen | Night scene of the spa. The robot shines a flashlight labeled "REA" on the bright front window where menu boards "หน้าเว็บ" and "API" are visible. The back room with a cash register labeled "กฎราคา" and the basement door labeled "ฐานข้อมูล" stay in soft shadow. The boy holds a sign "ไม่เห็น ≠ ไม่มี". Title sign "REA เห็นแค่หน้าร้าน". |
| 8 | `concept-05-outdated-docs.jpg` | 🎓 2 · LAB 3 | jpg gen | Office desk. An old yellowed binder "SPEC v1.0" says in a bubble "พอร์ต 3000" while a cheerful laptop with a face shows "4000". The robot stands between them with a question mark, holding a card "ถามเจ้าของ ไม่เดา". Khun Chan answers through a phone. Title sign "เอกสารเก่าไม่ตรงโค้ด". |
| 9 | `three-eyes-db.png` | 🎓 2 | png diagram | หัวเรื่อง "4 แหล่งความจริงของระบบเดิม" · 4 คอลัมน์: 🔦 REA (ห้ามมี source · เห็น หน้า endpoint ฝั่งเบราว์เซอร์ สัญญา API จาก HAR · ไม่เห็น กฎฝั่งเซิร์ฟเวอร์ DB · ตัวเลขจริง static 9/25 route · HAR 7 endpoint) · 📖 source (เห็นทุกบรรทัด · ไม่บอกว่าใช้งานจริงไหม) · 🗄️ DB schema (CHECK 51 · EXCLUDE 2 · กฎที่บังคับแม้โค้ดลืม) · 📜 SPEC เก่า (อาจไม่ตรง → คำถามถึงร้าน) · แถวล่าง: ตัวอย่าง "กลุ่ม 8 คน: โค้ดแก้ได้ · DB ปฏิเสธ · REA ไม่รู้" · แถบล่าง 🎯 "ตรงกัน = มั่นใจ · ไม่ตรง = เจอเรื่องต้องถาม" |
| 10 | `concept-06-safety-net.jpg` | 🎓 3 | jpg gen | The boy walks a tightrope across the lotus pond carrying a box labeled "CR". Below him a strong net held by the robot and Nong Bua, woven from three ropes labeled "check-rules", "e2e-legacy", "golden". Khun Chan watches from the sala. Title sign "ตาข่ายก่อนแก้". |
| 11 | `concept-07-lock-not-correct.jpg` | 🎓 3 | jpg gen | The robot takes a photo of the spa reception with an old camera; in the scene a small ladybug sits on the booking book. The printed photo, labeled "ล็อกตามจริง", also shows the ladybug. The boy points at the ladybug in the photo, sticky note "ล็อก ≠ ถูก". Title sign "characterization ล็อกทั้งบั๊ก". |
| 12 | `concept-08-test-seam.jpg` | 🎓 3 | jpg gen | A big wall clock in the spa has a small labeled dial "นาฬิกาทดสอบ". The robot turns the dial and the calendar page flips forward, while booking cards on the desk stay exactly in place. The boy gives a thumbs up. Speech bubble "ข้อมูลยังอยู่". Title sign "เลื่อนนาฬิกา ไม่ล้างข้อมูล". |
| 13 | `concept-09-mutation.jpg` | 🎓 3 | jpg gen | The robot wearing safety goggles deliberately loosens one screw labeled "1 บรรทัด" in a machine labeled "กฎร้าน". A red alarm bell labeled "ตาข่าย" rings and the boy writes "จับได้" on a clipboard. In the background a second loosened screw has a silent bell with a sad face and label "รอด = มีรู". Title sign "ทำพังเองเพื่อวัดตาข่าย". |
| 14 | `concept-10-impact-ripple.jpg` | 🎓 4 | jpg gen | The boy drops a small stone labeled "CR-02" into the lotus pond. Ripples spread and touch lily pads labeled "pricing.ts", "หน้าจอ", "แชท", "ข้อความ 3 ภาษา", "เทสต์เดิม". The robot writes a table on a clipboard. Title sign "แก้ 1 จุด กระทบหลายที่". |
| 15 | `concept-11-red-first.jpg` | 🎓 4 | jpg gen | A traffic light with red lit. The robot writes a test card under the red light labeled "เทสต์ใหม่ = แดง". Next panel: the light turns green after the robot tightens a bolt labeled "แก้". The boy holds a sign "แดงก่อน แล้วค่อยแก้". Title sign "เทสต์แดงก่อนแก้". |
| 16 | `concept-12-intended-vs-unintended.jpg` | 🎓 4 | jpg gen | Two test cards on a table. Left card shows a number changing "฿3,000 → ฿2,850" with a green stamp "มี CR อนุญาต" and Khun Chan nodding. Right card shows "฿760 → ฿800" with a red siren and the robot looking shocked, label "ไม่มีใครขอ". The boy writes in a notebook titled "ORACLE-CHANGES". Title sign "เปลี่ยนตั้งใจ vs ไม่ตั้งใจ". |
| 17 | `safe-change-loop.png` | 🎓 4 | png diagram | หัวเรื่อง "วงจรแก้ 1 CR อย่างปลอดภัย" · วงกลม 8 จุดตามเข็มนาฬิกา ① ถามให้ชัด (answers) ② impact ไฟล์ × เทสต์ ③ Plan mode รออนุมัติ ④ เทสต์ใหม่แดง + commit ⑤ แก้ให้เล็กที่สุด ⑥ เทสต์ใหม่เขียว ⑦ regression 3 เบราว์เซอร์ ⑧ TRACEABILITY + CHANGE-REPORT + REGISTER · กล่องกลาง "ห้ามแก้เทสต์ให้ผ่าน · ค่าเดิมเปลี่ยนต้องมี CR" · pill ไฟล์ข้างแต่ละจุด · แถบล่าง 🎯 "ทำตามที่ขอ ≠ ของเดิมไม่พัง ≠ ส่งมอบได้" |
| 18 | `concept-13-live-db-migration.jpg` | 🎓 5 · LAB 8 | jpg gen | A tall filing cabinet full of customer folders stays open while the robot slides in a brand-new drawer labeled "shop_holiday". A small bulldozer labeled "down -v" is blocked by a red stop sign held by Nong Bua. The robot presses a button "migration" twice, speech bubble "รันซ้ำได้". Title sign "เพิ่มได้ ห้ามล้าง". |
| 19 | `concept-14-rollback.jpg` | 🎓 5 · LAB 12 | jpg gen | The boy and the robot practice jumping from a low training platform labeled "ซ้อม" with parachutes labeled "แผนถอยกลับ"; a box labeled "สำรองข้อมูล" is strapped to the boy's back. Khun Chan watches with a checklist. Title sign "ซ้อมถอยกลับก่อนใช้จริง". |
| 20 | `concept-15-traceability.jpg` | 🎓 6 | jpg gen | A red string runs from an envelope "CR-03" to a rule card "BR-21" to a test card "TC" to a big green check mark, pinned on a cork board in the office. Khun Chan follows the string with a magnifying glass while the robot holds the pins. Title sign "โยง CR → กฎ → เทสต์". |
| 21 | `concept-16-audit-signoff.jpg` | 🎓 6 · LAB 12 | jpg gen | A committee table in the office. Khun Chan stamps a green seal "ตรวจรับแล้ว" on a thick folder with colored tabs "เทสต์", "ภาพ", "commit", "แผนถอยกลับ". The robot presents a clear evidence bag, the boy stands proudly. Title sign "ตรวจรับด้วยหลักฐาน". |
| 22 | `traceability-chain.png` | 🎓 6 | png diagram | หัวเรื่อง "1 CR ต้องตามได้ถึงผลทดสอบ" · โซ่ 5 ห่วงซ้าย→ขวา: CR-03 (หนังสือ) → BR-21 "คนเดียวกันห้ามมีนัดเวลาทับกัน" → TC-CR03-01..11 (tests/cr03.mjs · e2e-cr/tests/cr03.spec.ts) → regression (check-rules · golden · e2e-legacy 3 เบราว์เซอร์) → ผล + commit แดง/เขียว · ด้านล่างตารางย่อ CR | BR | TC | ผล 2 แถวตัวอย่าง (CR-02 → BR-06 · CR-03 → BR-21) · แถบล่าง 🎯 "ไม่มีเทสต์ = ยังไม่เสร็จ" |
| 23 | `lab-flow.png` | 🗺️ เส้นทาง | png diagram | หัวเรื่อง "เส้นทาง 12 LAB" · ตอนเริ่ม: pill `web/` `db/` `e2e-legacy/` `CHANGE-REQUESTS/` · ⚙️ LAB 0 · 🟢 LAB 1–2 · 🟡 LAB 3–4 · 🔵 LAB 5 · 🟠 LAB 6–10 (ป้าย CR-02 → CR-03 → CR-04 → CR-01 → CR-05) · 🟣 LAB 11–12 · ทุกกล่องมีไฟล์ที่ได้ · ป้าย ✏️ บน LAB 4–10 · แถบล่าง 🎯 ประโยคหลัก |
| 24 | `concept-17-reserved-ports.jpg` | LAB 0 | jpg gen | A row of numbered doors in a hallway: doors "2970" to "3069" are locked with a padlock and a sign "Windows จองไว้"; door "3000" is among them. Door "4000" is open with warm light, the robot waves the boy inside. Title sign "3000 ถูกจอง ใช้ 4000". |
| 25 | `lab0-checklist.png` | LAB 0 | png result | ตารางผล LAB 0 ธีมมืด หัวส้ม "LAB 0 · เช็กเครื่อง — สบายใจ สปา (ระบบเดิม)" คอลัมน์ รายการ \| ผล \| พร้อมไหม (Docker · Compose · Node ≥ 22.18 · git · ช่วงพอร์ตที่จอง · 4000 · 5433 · container บท 04 · rea-lab:6.4.0) · บรรทัดเขียว "สรุป: พร้อม N/9" (ค่าจาก LAB0_RESULT) |
| 26 | `lab1-handover.png` | LAB 1 | png result | 2 ตาราง: ① ชุดตรวจ \| ผ่าน \| ล้ม \| คาดว่าล้ม \| เวลา ② คำอ้าง H1–H6 \| ผลจริง \| ✅❌⚠️ · บรรทัดสรุป baseline commit (ค่าจาก LAB1_RESULT) |
| 27 | `lab2-rea-inventory.png` | LAB 2 | png result | ตาราง endpoint \| REA static \| HAR \| ป้าย (static/runtime/unknown) · บรรทัดสรุป "static 9 · HAR 7 · route stub 25" (ค่าจาก LAB2_RESULT) |
| 28 | `lab2-scenario-final.png` | LAB 2 | screenshot | ภาพหน้าจอที่ REA `capture-browser-scenario` ถ่ายเอง (หน้า "4. สรุปก่อนจ่าย" ฿1,000) ดึงจาก Evidence รอบจริง · ต้นแบบ: `rea-probe/evidence/scenario-book-quote-final.png` |
| 29 | `lab3-triangulation.png` | LAB 3 | png result | ตาราง กฎ/endpoint \| REA \| source \| DB \| ตรงไหม 5–7 แถวเด่นจาก SYSTEM-MAP รอบจริง (เช่น กลุ่ม 3–6 คน · ห้องคู่ · `/api/me`) |
| 30 | `lab3-db-rules.png` | LAB 3 | png result | ตาราง constraint \| กฎ \| โค้ดที่ตรวจซ้ำ (จาก `\d booking` รอบจริง) · บรรทัดสรุป "19 ตาราง · CHECK 51 · EXCLUDE 2" |
| 31 | `concept-18-claude-md-fence.jpg` | LAB 4 | jpg gen | A spa garden with a low wooden fence around a glass case labeled "e2e-legacy" and a sign "ห้ามแตะ". The robot reads a rule board on a stand titled "CLAUDE.md" with three short lines "อธิบายก่อนแก้", "แดงก่อน", "ห้าม down -v". The boy hammers in the last fence post. Title sign "กติกาให้ Agent". |
| 32 | `lab4-deny-test.png` | LAB 4 | screenshot | หน้าจอ Claude Code (เซสชันใหม่) ตอนพยายามแก้ `e2e-legacy/playwright.config.ts` แล้วขึ้นข้อความปฏิเสธ · กรอบแดงรอบข้อความ (ถ่ายจากรอบจริง ถ้าถ่าย TUI ไม่ได้ ให้ทำเป็น png result จากข้อความใน LAB4_RESULT) |
| 33 | `lab5-golden.png` | LAB 5 | png result | ตาราง กลุ่ม \| เคส \| รอบ update \| รอบเทียบ 1 \| รอบเทียบ 2 · บรรทัดสรุปจำนวนเคสและเวลา (LAB5_RESULT) |
| 34 | `lab5-mutants.png` | LAB 5 | png result | ตาราง mutant X1–X3 \| golden \| check-rules \| e2e-cr \| ผล (ถูกฆ่า/รอด) · ช่องรอดสีเหลือง |
| 35 | `concept-19-effective-date.jpg` | LAB 6 | jpg gen | Two big calendar pages side by side: "31 ต.ค." and "1 พ.ย.". A group of three cartoon customers stands in front of each page; price tag under the first "฿3,000" and under the second "฿2,850". A clock shows midnight between them. The robot points at the line, speech bubble "นับวันที่จอง". Title sign "กฎใหม่มีผล 1 พ.ย.". |
| 36 | `lab6-red-green.png` | LAB 6 | png result | ตาราง ชุดทดสอบ \| ก่อนแก้ \| หลังแก้ (tests/cr02 แดง → เขียว · check-rules · golden · e2e-legacy · e2e-cr) + บรรทัด "git diff check-rules.mjs = ว่าง" |
| 37 | `concept-20-double-tap.jpg` | LAB 7 | jpg gen | A customer holding a smartphone with a weak Wi-Fi icon taps the "จอง" button twice; two identical booking tickets fly out. The robot catches the second ticket with a big golden padlock labeled "ล็อกก่อนจอง" and a bubble "มีนัดแล้ว". The boy checks a phone number card "081-000-0003". Title sign "คนเดียวกัน เวลาทับ = ซ้ำ". |
| 38 | `lab7-duplicate-error.png` | LAB 7 | screenshot | หน้า `/book` ขั้นยืนยัน แสดง `book-error` ข้อความนัดซ้ำพร้อมรหัสนัดเดิม (รอบจริงหลังแก้ · วงแดงรอบข้อความ) |
| 39 | `gif-TC-CR03-11.gif` | LAB 7 | gif | Playwright chromium: กรอกเบอร์ซ้ำ → ยืนยัน → ข้อความซ้ำ · วงแดงจุดคลิก · ป้ายชื่อ test มุมซ้ายล่าง |
| 40 | `lab8-migration-twice.png` | LAB 8 | png result | ตาราง ขั้น \| คำสั่ง \| ผล (จองนัดใหม่ → migration รอบ 1 → รอบ 2 → นัดยังอยู่ → วันหยุด 3 แถว → reset × 2) |
| 41 | `lab8-shop-closed.png` | LAB 8 | screenshot | หน้า `/book` เลือกวันที่ 23 ต.ค. ขึ้นข้อความร้านหยุด (วันปิยมหาราช) ไม่มีปุ่มรอบ · วงแดง |
| 42 | `concept-21-reschedule-self-overlap.jpg` | LAB 9 | jpg gen | A couple (young Thai man and woman) slide their appointment card on a big wooden schedule board from "19:00" to "19:30"; a translucent ghost of the old card remains. The robot holds a sign "ไม่นับชนกับตัวเอง". The same therapist figure stays next to the card with a tag "คนเดิม". Title sign "เลื่อนนัดเอง". |
| 43 | `lab9-reschedule-dialog.png` | LAB 9 | screenshot | หน้า `/account` ของคุณนิดา เปิด `reschedule-dialog` เลือกวันที่และรอบ · ปุ่มของนัดวันนี้ disabled (รอบจริงหลังแก้) |
| 44 | `gif-TC-CR01-15.gif` | LAB 9 | gif | Playwright chromium: `/account` → เลื่อนนัด → เลือกวัน/รอบ → ยืนยัน → รีโหลด เห็นเวลาใหม่ |
| 45 | `concept-22-independent-oracle.jpg` | LAB 10 | jpg gen | Office. The robot calculates totals from a thick ledger book labeled "SQL" with an abacus, while a brand-new shiny screen labeled "หน้ารายงานใหม่" shows numbers; the boy covers the screen with his hand. Speech bubble from the boy "อย่าลอกจากจอ". Title sign "ค่าที่คาดหวังมาจากทางอื่น". |
| 46 | `lab10-report-page.png` | LAB 10 | screenshot | หน้า `/admin/report` ช่วง 1–30 ก.ย. แสดงยอดและจำนวนนัดแยกสถานะ + ปุ่ม CSV (รอบจริงหลังแก้) |
| 47 | `concept-23-version-compare-sabai.jpg` | LAB 11 | jpg gen | Two identical spa shop-front boxes labeled "v1" and "v2". The robot puts an orange sticker "changed" on the window labeled "หน้าบัญชี" of v2. Behind v2, the back room labeled "กฎหลังร้าน" is in fog with a grey sticker "REA มองไม่เห็น". The boy writes on a clipboard "พิสูจน์ด้วยเทสต์". Title sign "เทียบเวอร์ชันที่ส่งมอบ". |
| 48 | `lab11-regression.png` | LAB 11 | png result | ตาราง ชุด \| ผ่าน/ทั้งหมด \| เบราว์เซอร์ \| เวลา (check-rules · golden · cr01–05 · e2e-cr · e2e-legacy) จาก REGRESSION-REPORT |
| 49 | `lab11-rea-compare.png` | LAB 11 | png result | ตาราง CR \| ควรเห็นที่ chunk ไหน \| REA เห็นไหม \| เทสต์ที่พิสูจน์แทน + บรรทัด summary ของ `cmp-sum` (changed/unknown) |
| 50 | `lab12-rollback.png` | LAB 12 | png result | ตาราง ขั้นซ้อมถอยกลับ \| คำสั่ง \| ผล \| เวลา (สำรอง → stop web → down → ตรวจนัด → up → start → ตรวจ) |
| 51 | `lab12-release-notes.png` | LAB 12 | png result | ภาพเอกสาร RELEASE-NOTES.md ส่วนแรก (ภาษาคน) พร้อมวงแดง ①②③ ที่หัวข้อ "ลูกค้าเห็นอะไร" "ร้านต้องทำอะไร" "เรื่องที่ยังไม่แก้" · คำอธิบายเลขใน `IMAGES-06.md` |
| 52 | `site-admin-queue.png` | 🧰 ก่อนเริ่ม | screenshot | หน้า `/admin` ตารางคิว 12 ต.ค. ของระบบที่รับมอบ (owner) |
| 53 | `outro-01-signoff-party.jpg` | 🎉 จบบท | jpg gen | Spa garden at golden hour. Khun Chan holds a signed document "ตรวจรับแล้ว" and shakes hands with the boy; the robot and Nong Bua high-five; five opened envelopes "CR-01"… "CR-05" are pinned on a board with green check marks. Title sign "ส่งมอบสำเร็จ". |

ภาพบท 05 ที่อ้างซ้ำ 7 ภาพ (ไม่สร้างใหม่ · ใช้ path `../05_rea-reverse-engineer-legacy-petshop/img/…` · ตรวจชื่อกับโฟลเดอร์จริงแล้ว 12 ต.ค. 2026): `concept-03-black-white-grey-box.jpg` · `concept-05-evidence-not-opinion.jpg` · `concept-06-missing-not-absent.jpg` · `concept-10-passive-driven-har.jpg` · `concept-12-evidence-badge-e.jpg` · `three-eyes.png` · `concept-08-version-compare.jpg` · link-check อีกครั้งก่อนเขียน README
นับ: jpg gen 26 · png diagram 5 · png result 13 · screenshot 7 · gif 2 = **53** · ทุก LAB มีอย่างน้อย 1 ภาพ (LAB 0 = 2 · 1 = 1 · 2 = 2 + ทบทวน · 3 = 2 + ซ้ำ · 4 = 2 · 5 = 2 + 🎓 · 6 = 2 · 7 = 3 · 8 = 2 + ซ้ำ · 9 = 3 · 10 = 2 · 11 = 3 + ทบทวน · 12 = 2 + ซ้ำ)

กติกาภาพ: ข้อความในภาพ **ห้ามเฉลยกับดัก** ก่อนถึง LAB นั้น (เช่น ห้ามเขียน "TABLES" "init ไม่รันซ้ำ" ในภาพ 🎓 ข้อ 5) · ตัวเลขในภาพ jpg ใช้เฉพาะค่าที่อยู่ในหนังสือ/คำตอบ CR ([D]) · png result ใช้ค่าจาก `results/LABn_RESULT.md` เท่านั้น · **ห้ามมีแถว S4/L2 ("กดใช้บริการเสร็จก่อนถึงเวลานัด") ใน `lab3-triangulation.png` `lab3-db-rules.png` `lab12-release-notes.png` และใน README** แม้รอบ RUNNER จะเจอ (= ข้อสอบชุด B ข้อ 5 · M10) · `lab11-rea-compare.png` เพิ่มตาราง HAR v1↔v2 (endpoint · status v1/v2 · [E] ย่อ) ใต้ตาราง CR × REA

---

## 13. ความเสี่ยง / สิ่งที่ต้องพิสูจน์ในรอบ RUNNER

| # | เรื่อง | ผลถ้าพลาด | วิธีพิสูจน์ |
|---|---|---|---|
| R1 | หลังทำ P1 check-rules ต้อง 90/90 | ตาข่ายชั้น 1 เพี้ยนตั้งแต่ต้น | PREP V4 (รันจากราก) |
| R2 | `rea.ps1` (บท 05) ใช้กับพาธ `/work/rea-out/...` ผ่าน `powershell -ExecutionPolicy Bypass -File` ได้ | LAB 2, 11 สะดุด | PREP V7 · ทางสำรอง = คำสั่ง `docker run … --entrypoint sh -c "rea … > /work/…"` (RF §5.2) |
| R3 | HAR ผ่าน `127.0.0.1:4000` · scenario ผ่าน network `sabai06-net` (`http://sabai06-web:3000` · D7) · `shot` ดึงภาพได้ | LAB 2, 11 | PREP V7 (ทางสำรอง `host.docker.internal` เฉพาะเมื่อ network ล้ม) |
| R4 | deny `Edit(e2e-legacy/**)` มีผลในเซสชันใหม่ (โหมด default/acceptEdits) | LAB 4 | รอบ RUNNER (บันทึกข้อความจริง + โหมด) |
| R5 | ~~e2e-legacy 3 เบราว์เซอร์ × 5 CR~~ → **ตัดสินแล้ว T14** | — | วัดเวลาจริง api+chromium ใน PREP V5 |
| R6 | ค่าคาดหวังใน answers ③ และ AC ใน CRD มาจากการคำนวณ ยังไม่ได้รัน | README เขียนตัวเลขผิด | เฉลยอ้างอิง (PREP P9 · งานถัดไป) รันผ่านทุก AC ก่อนเขียน README |
| R7 | เวลารวม ~10.9 ชม. [คาด] | เกิน 2 วัน | ปรับหลังรอบ RUNNER · ตัดส่วน ข ของ CR-04 เป็นทางเลือก |
| R8 | ผู้เรียนบางเครื่องจองพอร์ต 4000 | LAB 1 เปิดไม่ได้ | `$env:WEB_PORT=4100`/`$env:BASE_URL` (PREP P3) + แถว "ถ้าเจอปัญหา" |
| R9 | `git init` ใน `b2run/w` (นอก repo คอร์ส) ได้ไหม (m6-ง) | snapshot แทน git ต่างจากผู้เรียน | **รอ orchestrator ชี้ขาด** · ค่าเริ่ม = snapshot ตาม RUNNER §4 |
