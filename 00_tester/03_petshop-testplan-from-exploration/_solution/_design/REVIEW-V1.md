# REVIEW-V1: link check and number cross-check (report only)

Reviewed: `README.md` (671 lines) and `_solution/README.md` (307 lines), 2026-10-10.
This review edited no repo file except this one.

## Summary

- **Links and images: 71/71 local paths exist.** No broken links. A script parsed every `![](…)`, `[](…)`, `<img src>` and `href`, skipping http/mailto/#. The TOC anchors in `_solution/README.md` match GitHub's slug rules (checked by hand).
- **Numbers in the ✅ ผลจริง sections: no wrong number found.** Every number I checked matches `_design/LAB*_RESULT.md` and the artifacts. The findings below are small: wording, missing info, and one claim that has no source.

### What was checked, with sources

| Claim (README / _solution README) | Checked against | Result |
|---|---|---|
| LAB 1: healthy, `{"ok":true}`, ~1 min, ~6 s | LAB1_RESULT | ✅ |
| LAB 2: 13 pages + mobile menu, 3 need login, 22 features, 28 products (14/14), 7 "ยังไม่รู้" items, 19 images, PP-100001 ฿581, ~12 min | LAB2_RESULT · `EXPLORATION.md` (F rows = 22) · `exploration/` = 19 files | ✅ |
| LAB 3: 61 rules, first tag [D]13/[R]32/[O]8/[O-ยังไม่ยืนยัน]8, ⚠️ 4, 22 risks P1 10/P2 8/P3 4, 14 questions (19 after LAB 5), 12 error messages | LAB3_RESULT · counted from `EXPLORATION.md` (R=61, first tags 13/32/8/8, ⚠️=4, K=22 → 10/8/4, E=19) | ✅ |
| LAB 4: overview 5 rows, test 20 / don't test 11 rows, F1–F22 22/22, 390×844, 5 stop-and-ask questions | LAB4_RESULT | ✅ |
| LAB 5: 47 cases, P1 29/P2 13/P3 5, techniques 13/11/11/8/8/4, sources 23/21/3, 45/47 match, 108 s, the 2 mismatches | LAB5_RESULT | ✅ (see F2) |
| LAB 6: 47→48, P1 29→30, sources 24/21/3 (6.3%), ⚠️ 4→1, broad expected results 3→0, Exit ≥46/48, 8.1 = 14 · 8.2 = 14, 7.1 = 10 rows · 7.2 = 17 rows, rubric 14/18 → 17/18 | LAB6_RESULT · `TEST-PLAN.md` (counted with a script: 48 TC, P1 30/P2 13/P3 5, first source D24/R21/O3; 7.1 = 10, 7.2 = 17, M1–M14, Q1–Q14) · `PLAN-REVIEW.md` §2 | ✅ |
| TEST-PLAN by module | AUTH 4 · REG 3 · SRCH 2 · CAT 1 · PROD 3 · CART 6 · WISH 1 · FIND 1 · COUP 10 · SHIP 4 · CHK 7 · ACC 1 · SEC 3 · UI 2 = 48 | ✅ matches the e2e file split in LAB7_RESULT (7/6/6/2/10/4/7/1/3/2) |
| LAB 7: 48 tests in 10 files, 144 runs, 138 passed, 8.7 min, every browser 30/30 P1 · 46/48 = 95.8%, failures SRCH-01 + CART-05, 663/675 checkpoints | LAB7_RESULT · `e2e/tests/*.spec.ts` (`test(` counts 7+6+6+2+10+4+7+1+3+2 = 48, 48 unique `plan('TC-…')`) · image `img/report-summary.png` (shows 8.7 min, 30/30, 46/48, 663/675, 144) | ✅ |
| LAB 8: every browser P1 26/30 · 41/48 = 85.4%, the same 7 failures, 144 runs / 123 passed / 21 failed, 618/660, 16.8 min, EX3 = 4, EX4 7/7, catches 3/3, oracle 5/5 vs 0/5 | LAB8_RESULT · `e2e/test-report/data.json` (computed: bugMode true, duration 16.82 min, per browser 41/48 and P1 26/30, runs 123/21, checkpoints 618/660) · `e2e/triage.json` (7 entries) · `BUG-HUNT.md` · image `_solution/img/report-bug-summary.png` | ✅ |
| _solution §8.3: 45 PNGs, 3 failing-test GIFs + 3 passing-test GIFs, ~9.6 MB | `ls test-report/media`: 45 png + 6 gif (AUTH-01, CHK-03, COUP-01, COUP-04, PROD-01, WISH-01) · `du -sb` = 9,609,978 B | ✅ (see F3 for "~97 MB") |
| _solution §6 rubric 19/20 | Summed the table: 4+0+3+7+3+2 = 19 | ✅ |
| Root `.gitignore` covers `.playwright-mcp/` and `_solution/e2e/{node_modules,test-results,playwright-report}/` | `.gitignore` | ✅ |

---

## Findings

### F1: README.md:468 (low): LAB 7 is the only ✅ ผลจริง line with no duration

**Problem:** The ✅ lines for LAB 2–6 and LAB 8 all start with "ใช้เวลาราว …". LAB 7 gives only the run time (8.7 นาที). Students may think the whole LAB takes 9 minutes. LAB7_RESULT says it took about 1 hour (35 min of selector work and writing tests, plus 3 full runs of ~9 min each). `_solution/README.md:54` already says "≈ 1 ชม.".

**Suggested fix:** Replace
`✅ **ผลจริง (ตัวอย่าง)** ได้ test **48 ข้อ ใน 10 ไฟล์** รันรวม 144 รอบ (48 × 3 เบราว์เซอร์) ใน **8.7 นาที**`
with
`✅ **ผลจริง (ตัวอย่าง)** ใช้เวลาราว 1 ชม. (สำรวจ selector + เขียน test ~35 นาที · รันเต็มรอบละ ~9 นาที) ได้ test **48 ข้อ ใน 10 ไฟล์** รันรวม 144 รอบ (48 × 3 เบราว์เซอร์) ใน **8.7 นาที**`

### F2: README.md:348 (low): technique counts add up to 55, not 47, with no explanation

**Problem:** `Happy 13 · Negative 11 · Boundary 11 · Partition 8 · State 8 · Security 4` adds up to 55, but the plan has 47 cases. LAB5_RESULT says this row counts every technique in a case ("ข้อที่ใช้หลายเทคนิคนับทุกตัว"). The README leaves that out, so a student who adds up the numbers will think they are wrong. Side note: I could not check "State 8" against the 47-case version, because only the 48-case plan is in git (one commit, ae13d0b). PLAN-REVIEW §2.2 reports State as 7 → 8 by first technique and 10 counting all techniques after the fix. That fits State 8 only if ACC-01 got "/ State" during review. It is probably correct, but I could not confirm it.

**Suggested fix:** Change the cell `| เทคนิค |` to `| เทคนิค (ข้อที่ใช้หลายเทคนิคนับทุกตัว) |`.

### F3: _solution/README.md:297 (low): "เดิม ~97 MB" has no source

**Problem:** No `_design/LAB*_RESULT.md` file gives 97 MB. LAB7_RESULT says "โฟลเดอร์ `test-report` รวม ~76 MB" (for the LAB 7 run). LAB8_RESULT gives no size. This also contradicts line 6, which says "ตัวเลขทุกตัวในหน้านี้มาจาก `_design/LAB*_RESULT.md`". (The "~9.6 MB" after trimming is correct: 9,609,978 B.)

**Suggested fix:** If 97 MB was measured from the LAB 8 run, add it to LAB8_RESULT. Otherwise change it to
`` `e2e/test-report/` เดิมหลายสิบ MB (รอบ LAB 7 ≈ 76 MB · มี MP4 + GIF ทุกข้อ) ตัดเหลือ ~9.6 MB เพื่อเก็บใน git: ``
and soften line 6 to `ตัวเลขผลจริงทุกตัวในหน้านี้มาจาก …` (section 8.3 describes trimming that happened after the LABs).

### F4: _solution/e2e/triage.json, TC-CHK-03 note (info: an artifact, not a README)

**Problem:** The note says "ผลข้อย่อยที่เหลือยืนยันด้วย Playwright MCP แทน". LAB8_RESULT says the part-2 re-exploration used "สคริปต์ Node Playwright headless ของตัวเอง (ไม่ได้ใช้ Chrome จริงของผู้ใช้)". `_solution/README.md:63` says only "ยืนยันด้วยการสำรวจแทน", which is fine.

**Suggested fix (optional):** In triage.json, change `ยืนยันด้วย Playwright MCP แทน` to `ยืนยันด้วยการสำรวจซ้ำ (สคริปต์ Playwright headless) แทน`. index.html shows the triage note, so a re-render from `data.json` would be needed. If not, leave it, since the README is already correct.

### F5: _solution/README.md:93 (info): alt text names only 2 browsers

**Problem:** The alt text says "ตารางแยกเบราว์เซอร์ Chromium กับ Firefox ผ่าน P1 26/30 รวม 41/48". That is accurate, because the screenshot cuts off before WebKit. A reader using alt text might still think WebKit is missing from the result.

**Suggested fix (optional):** Add `(ภาพตัดก่อนแถว WebKit ซึ่งผลเหมือนกัน)` at the end of the alt text.

---

## No problem found (things checked that might look suspicious)

- `_solution/README.md:36` `_design/SPEC-reference.md` exists (20 KB).
- README.md:200 alt text says "14 แถว". That is 13 pages + the mobile menu row, which is consistent.
- LAB 7 checkpoints are 675 and LAB 8 are 660. The difference is expected: in bug mode, TC-CHK-03 timed out before its later sub-steps ran.
- README.md:418 tp-6-criteria alt text matches the image (EN1/EN2, EX1 30/30, EX2 46/48, counting rule).
- README.md:478 alt text says "TC-SRCH-01 ไม่ผ่าน 70%". The image shows 70% · 21/30.
- `e2e/index.html` now has `"bugMode":true` (the LAB 8 report), as `_solution/README.md:32` says.
