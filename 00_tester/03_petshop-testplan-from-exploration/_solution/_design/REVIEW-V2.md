# REVIEW-V2 · Answer-key leakage and layout check (report only)

Reviewer: V2 · Date: 2026-10-10 · Scope: `03_petshop-testplan-from-exploration/`
No repo files were edited apart from this report. Only read-only git commands were used.

Hidden bugs checked for: **B1** PAW10 gives 1% · **B2** wishlist ♥ counter does not go down · **B3** 9-digit phone is accepted.

## Verdict

| Rule | Result |
|---|---|
| (a) README.md does not reveal the 3 bugs or contain the full reference plan or exploration | ❌ **FAIL**: 2 direct leaks (images), 1 strong location hint (prompt text), several softer hints |
| (b) petshop/ has no SPEC.md and petshop/README lists no bugs | ✅ PASS (see the note about source comments) |
| (c) root contains only README.md, TEST-DATA.md, petshop/, img/, _solution/, .gitignore | ✅ PASS (an ignored `img/.ipynb_checkpoints/` exists on disk; see A7) |
| (d) _solution/README.md contains the full answer key | ✅ PASS, but the file is **untracked** (`?? _solution/README.md`) |
| (e) files over 3 MB | ⚠️ 1 file: `_solution/_design/shots/lab8-gif-TC-CHK-03.gif`, **9.6 MB, tracked** |

---

## (a) README.md leaks: findings and exact fixes

### A1 · HIGH · `img/tp-8-quality.png` shows B1 in plain words
- README.md:420 embeds `img/tp-8-quality.png`. Row **M1** of the image reads: **"คูปอง PAW10 คิด % ผิด (เช่น ลด 1% หรือไม่หักเลย)"**. This is the exact LAB 8 bug.
- The alt text is clean, so the leak is in the image itself.
- **Fix:** re-render the image with the M1 cell changed to `คูปอง PAW10 คิด % ผิด (เช่น ลด 5% หรือหักจากยอดผิด)`. Any example other than "1%" works; `5%` is safe. If `_solution/TEST-PLAN.md` §8.1 M1 also says "1%", you can keep that wording there because it is the answer key. Only the student-facing PNG must change. Then crop or re-capture from an edited copy, not from `_solution/TEST-PLAN.md` directly.

### A2 · HIGH · `img/concept-03-bake-the-bug.jpg` shows the exact B1 output
- README.md:84. The laptop in the image shows **"ราคาที่แสดงบนหน้าเว็บ ฿7 (ควรเป็น ฿79)"**, and the robot copies **฿7**. ฿799 × 1% = ฿7.99 → ฿7, so this is the buggy BUG_MODE=1 discount on the ฿799 item. The alt text also says "ลอกตัวเลข 7 บาท … ที่ควรเป็น 79 บาท".
- **Fix:** regenerate the image (see the `cyolo exec` memory) with a number that is not one of the bugs, for example a wrong total **"฿1,049 (ควรเป็น ฿999)"**. This matches README's own free-shipping-edge example and M2, which is not a hidden bug. Then change the README.md:84 alt text to:
  `![ฉากในครัว หุ่นยนต์ Playwright ลอกตัวเลข 1,049 บาทจากหน้าจอแล็ปท็อป ที่ควรเป็น 999 บาท ใส่ลงชามผสมแป้งชื่อ ผลที่คาดหวัง ในเตามีเค้กที่มีแมลงเต่าทองซ่อนอยู่ เด็กชายตกใจชี้ หัวเรื่อง อย่าอบบั๊กลงในผลที่คาดหวัง](img/concept-03-bake-the-bug.jpg)`
- Do **not** use ฿80 vs ฿79. That is the open rounding question E1, and it would mislead students.

### A3 · HIGH · The LAB 8 part 2 prompt names all three bug areas
- README.md:521: `1. ใช้ Playwright MCP เดินสำรวจเว็บตอนนี้ซ้ำแบบ LAB 3 เฉพาะเรื่องคูปอง รายการโปรด และฟอร์มที่อยู่`. This lists coupon, wishlist and address form, which are exactly B1, B2 and B3. It also contradicts README.md:502, which says "ไม่บอกว่าอยู่ตรงไหน".
- **Fix:** replace the line with:
  `1. ใช้ Playwright MCP เดินสำรวจเว็บตอนนี้ซ้ำแบบ LAB 3 เฉพาะส่วนที่มี test ล้มในส่วนที่ 1`
  This still focuses the work, but the areas come from the student's own failures.

### A4 · MEDIUM · `img/concept-05-rule-hunting.jpg` shows a 9-digit phone
- README.md:225. A card in the image shows **"081234567?"**, which is 9 digits followed by a question mark. The alt text repeats "ช่องเบอร์โทร 081234567?". Taken alone it is a boundary-value example, but it is the exact B3 input.
- `_design/IMAGES-W1.md:14` says the oracle image intentionally avoided phone and wishlist examples. The same policy should apply here.
- **Fix:** regenerate the card as a postcode boundary, **"รหัสไปรษณีย์ 1020?"** (4 digits). Change the alt text to:
  `… ป้ายราคาคูปองเปอร์เซ็นต์ ช่องรหัสไปรษณีย์ 1020? …`
  You can keep README.md:231 and :588 ("เบอร์ 9/10/11 หลัก", "เบอร์ 9/10 หลัก"). They are generic BVA instructions that a good plan needs in order to catch B3, and keeping them is fair.

### A5 · MEDIUM · `img/review-matrix.png` hints at B2
- README.md:432. Callout ③ on row F8 reads **"WISH-01 ไม่บอกว่าตรวจตัวเลข ♥ ตอนไหน → ตรวจทันที + หลังรีโหลด"**. `_solution/README.md:121` says this exact review fix is *why* the sample plan catches B2, so showing it gives the catch away.
- The image also reproduces the **entire** 21-row PLAN-REVIEW coverage matrix. That is an answer-key artifact, though not the TEST-PLAN or EXPLORATION.
- **Fix:** re-render with rows F1–F7 only, and add a footer `… อีก 14 ฟีเจอร์ (F8–F21)`. This drops the F8 callout and avoids a full answer key. Update the alt text at README.md:432 to: `PLAN-REVIEW.md coverage matrix ตัวอย่างแถว F1 ถึง F7 คอลัมน์ 6 เทคนิค Happy Negative Boundary Partition State Security วงแดงช่องเตือน`. If you want to keep a ⚠️ example, use the F11 COUP-05 ฿500 callout instead. It is already in the alt text and is not a hidden bug.

### A6 · LOW · Softer hints in the LAB 8 "สังเกต" list (README.md:553–562)
- `**ข้อความ error ของเว็บก็ขัดกับพฤติกรรมเว็บเองได้**` hints at B3: the error says "10 หลัก" while 9 digits pass. **Fix:** move this bullet to `_solution/README.md` §4, or reword it to the generic `อย่าเชื่อ [O] ข้อเดียว ถ้าสองแหล่งในหน้าเว็บขัดกันเอง ให้ถามทีม`.
- The bullet `1 test ที่มีหลายข้อย่อย … ข้อย่อยแรกสั่งซื้อสำเร็จไปแล้ว ข้อย่อยที่เหลือเลยหาช่องกรอกไม่เจอ` hints that a checkout form input wrongly succeeds (B3). **Fix:** move it to the instructor notes in `_solution/README.md`. It is already in §2 notes, line 63, so it can simply be deleted here. Or make it generic: `1 test ที่มีหลายข้อย่อย ระวังผลข้างเคียง: ถ้าข้อย่อยหนึ่งทำให้สถานะเปลี่ยน ข้อย่อยถัดไปอาจล้มเพราะเริ่มจากหน้าผิด → แยกเป็น test ละค่า`.
- `ตรวจผิดจังหวะ?` in the first bullet slightly hints at B2. Acceptable; no change needed.
- The README.md:530–549 summary tables ("5 ข้อใหม่", "P1 2 ตัว · P2 1 ตัว", "3/3") give counts only. Acceptable, but consider moving them below the 🔒 link so students see them only after running LAB 8. Optional.

### A7 · OK · Other images and text checked
- Viewed directly: `intro-05-mystery-bugs.jpg` (only "?" bugs), `oracle-badges.png` (postcode and PAW10 10%, no phone or wishlist), `lab-flow.png`, `tp-5-testcases.png` (7 of 48 rows), `exploration-rules.png` (R1–R8 of 22+; "฿69 → ฿7" there is correct 10% rounding, not B1), `exploration-questions.png` (E1–E6 of 19), `report-bug-summary.png` (counts only, no TC IDs), `report-table.png` (first 10 rows, BUG_MODE=0). Alt text for all other images was reviewed by grep. No other leaks.
- Excerpts of TEST-PLAN and EXPLORATION are partial and each image is labelled "… อีก N ข้อ". The full files are linked only under `_solution/`. ✅
- `grep` of README.md for `1%`, `9 หลัก` paired with acceptance, `badge`, `ไม่ลด` and `counter` found nothing beyond the items above.

## (b) petshop/
- No `SPEC.md` in petshop/. `petshop/README.md` lists no bugs; it only says "ยังไม่มีเอกสารข้อกำหนด (spec)". ✅
- grep of `SPEC` in petshop/ (case-insensitive) found:
  - `petshop/.dockerignore:13: SPEC.md`. This is a harmless leftover, but it tells a curious student that a spec once existed. **Fix (optional):** delete line 13 `SPEC.md` from `petshop/.dockerignore`.
  - The other matches are `globals.css` (`aspect-ratio`, `specificity`) and the petshop/README sentence above. These are fine.
- **Note, outside the stated rules:** the source code names every bug in comments:
  - `lib/pricing.ts:90` says `(training bug #1): PAW10 gives 1% instead of 10%`.
  - `components/ShopProvider.tsx:225` says `Training bug #2: … header badge is not decreased until reload`.
  - `lib/validation.ts:81` says `Training bug #3 (BUG_MODE): phone validation accepts 9 digits`.

  The prompts say "ห้ามเปิดอ่านโค้ด", but a single grep for "bug" reveals all three. **Suggested fix:** reword them to neutral comments, for example `/** BUG_MODE variant for the testing course (see _solution/README.md §3). */`, and remove the behaviour description from all three lines. Line 116 (`bugMode ? 1 : 10`) and line 83 (`/^0\d{8,9}$/`) still reveal the bugs to anyone who reads the code. That cannot be avoided in black-box teaching, so only the comments are worth fixing.

## (c) Root contents
- On disk: `.gitignore README.md TEST-DATA.md _solution/ img/ petshop/`. ✅
- `img/.ipynb_checkpoints/` (2 PNGs) and `_solution/_design/shots/.ipynb_checkpoints/` exist on disk. They are ignored by the parent `.gitignore:33 **/.ipynb_checkpoints/` and are not tracked. **Fix (cosmetic):** `rm -r img/.ipynb_checkpoints _solution/_design/shots/.ipynb_checkpoints`.
- The chapter tree diagram at README.md:647–671 matches the layout. ✅

## (d) _solution/README.md
- It has the full key: §3 lists the hidden bugs, §4 has the BUG-01, 02 and 03 details (PAW10 ~1%, ♥ not decreasing immediately, 9-digit phone), plus §5 must-have test cases, §6 rubric scores, §7 problems and §8 rerun steps. ✅
- ⚠️ **It is untracked** (`git status`: `?? _solution/README.md`). README.md:117 and :553 link to it. **Fix:** `git add _solution/README.md` before the next commit, or the links break for anyone who clones the repo.

## (e) Files larger than 3 MB (node_modules excluded)
| File | Size | Tracked | Suggested fix |
|---|---|---|---|
| `_solution/_design/shots/lab8-gif-TC-CHK-03.gif` | **9.6 MB** | yes (commit ae13d0b) | Delete it. A trimmed copy already exists as `_solution/img/gif-bug-phone9.gif` (1.5 MB) and as `_solution/e2e/test-report/media/TC-CHK-03.gif`. Or re-encode it, for example `ffmpeg -i in.gif -vf "fps=6,scale=960:-1:flags=lanczos" out.gif`. The file is already in history, so the blob stays in `.git` unless history is rewritten. |

The next largest files are 1–2.5 MB GIFs in `_solution/_design/shots/` and `_solution/img/`, which is fine. Chapter total: 78 MB on disk (`_solution` 60 MB, `img` 13 MB, `petshop` 5 MB).

---

## Fix checklist (in priority order)
1. ☐ A1: re-render `img/tp-8-quality.png` without "ลด 1%".
2. ☐ A2: regenerate `img/concept-03-bake-the-bug.jpg` with ฿1,049 vs ฿999 and update the alt text at README.md:84.
3. ☐ A3: README.md:521, replace "เฉพาะเรื่องคูปอง รายการโปรด และฟอร์มที่อยู่" with "เฉพาะส่วนที่มี test ล้มในส่วนที่ 1".
4. ☐ `git add _solution/README.md`.
5. ☐ A4: regenerate `img/concept-05-rule-hunting.jpg` with a postcode card and update the alt text at README.md:225.
6. ☐ A5: re-render `img/review-matrix.png` with rows F1–F7 and update the alt text at README.md:432.
7. ☐ A6: move or reword the 2 bullets in the LAB 8 "สังเกต" list.
8. ☐ (e): remove or shrink the 9.6 MB GIF.
9. ☐ (b) optional: neutralise the 3 "Training bug" comments and the `SPEC.md` line in `.dockerignore`.
10. ☐ (c) cosmetic: delete the `.ipynb_checkpoints/` folders.
