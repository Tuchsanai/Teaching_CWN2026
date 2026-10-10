# FINAL-REVIEW: what was applied from REVIEW-V1 to V4

Date: 2026-10-10 · Scope: `README.md`, `_solution/README.md`, `img/`, `_solution/_design/shots/`
Not touched: `petshop/` and chapter 02. No git commands that change state were run.

> Note: a commit `1b3dc5e` (15:42:49) was made outside this session while the work was running. It already contains the first 3 re-rendered images (`tp-8-quality`, `review-matrix`, `exploration-rules`) and the 4 REVIEW files. Everything else below is still uncommitted.

## End state

| Check | Result |
|---|---|
| Container `petshop` | healthy · `printenv BUG_MODE` = `0` · `<html data-bug-mode="0">` · `/api/health` = `{"ok":true}` |
| Link check (`README.md` + `_solution/README.md`) | **81 links, images and anchors · 0 broken**. Thai anchors were checked with GitHub slug rules, which keep combining marks. |
| Files > 3 MB (excluding node_modules) | none |
| README.md search for `1%`, `081234567`, "คูปอง รายการโปรด และฟอร์มที่อยู่" | no bug leaks left. The only `10%` hits are TEST-DATA facts. |

---

## Fixed

### Answer-key leaks (V2)
| ID | Fix |
|---|---|
| A1 | `img/tp-8-quality.png` re-rendered. Row M1 now reads only "คูปอง PAW10 คิด % ผิด" (the "ลด 1%" example was removed). The header note changed from "ข้อความจริงจากไฟล์" to "ข้อความจากไฟล์ … (ย่อ)" because the image now differs from `_solution/TEST-PLAN.md`. |
| A2 + V4 logo | `img/concept-03-bake-the-bug.jpg` edited with `cyolo exec`. The laptop now shows ฿1,049 "(ควรเป็น ฿999)", the tag in the bowl shows ฿1,049, and the Playwright masks logo was replaced with a plain gear. Alt text updated. |
| A3 + V3-H4 | LAB 8 part 2 prompt: re-explore only "ส่วนที่มี test ล้มในส่วนที่ 1" instead of naming coupon, wishlist and address form. Added a `data-bug-mode` check and the black-box rule. "แบบ LAB 3" was replaced with a description that works in a new session. |
| A4 | `img/concept-05-rule-hunting.jpg`: the phone card "081234567?" now shows "รหัสไปรษณีย์ 1020?". Alt text updated. |
| A5 | `img/review-matrix.png` re-rendered with rows F1–F6 + F11 only, plus "…" rows that point to the full file. The F8 WISH-01 callout is gone, and the F11 ฿500 ⚠️ that is still waiting on the team is kept. Alt text updated. Note: the matrix has no F7 row, so "F1–F7" in the review means F1–F6. |
| A6 | LAB 8 "สังเกต": the two bullets that hinted at B3 were made generic. |

### README.md prompts and wording (V3)
- **H1/H2**: the LAB 7 prompt item 5 now describes `e2e/index.html` itself (verdict per browser, case table, triage from `e2e/triage.json`). It no longer says "แบบบท 02", because chapter 02 today only has `reporters/tester-report.ts` → `TEST-REPORT.md`. The prerequisite row was updated too. The line-495 note was reworded as "ยืม helper และ reporter จากบท 02 มาปรับ" so it still matches LAB7_RESULT, which says `html-report.ts` was copied from chapter 02 and then adapted (see Rejected).
- **H3**: "ห้ามเปิดโฟลเดอร์ _solution" was added to the prompts for LAB 2, 3, 4, 5, 6, 7 and 8 (both parts). Added a troubleshooting row. The "เทียบกับเฉลย" row in 🔁 now says "(หลังจบ LAB 8 เท่านั้น)".
- **H4**: LAB 8 part 1 now has a healthy + `data-bug-mode` = 1 check, writing triage to `e2e/triage.json` and re-rendering, a `_solution` ban, and "ห้ามแก้ test หรือแผนให้ผ่านเฉย ๆ".
- **M1** LAB 4: the 8 section names are listed and "แผนมาตรฐาน" was replaced (look at the chapter 02 TEST-PLAN for format only). **M2** LAB 6: Entry criteria are spelled out, and a black-box line was added. **M3** LAB 7: commands now say to run them in `e2e`.
- **M4**: "โหมดฝังบั๊ก" is now used throughout, matching chapter 02 (7 places; the LAB 8 heading keeps "ปริศนา").
- **M5 = V1-F2**: the technique row now explains why the count is 55 > 47.
- **M6**: the review stats row and rubric item 18 use `[O-ยังไม่ยืนยัน]`.
- **M7 + m5**: LAB 5 bullets reordered so "สคริปต์ชั่วคราว" is explained before it is used. The 47-case bullet was rewritten.
- **M8**: added "จุดตรวจ" to the glossary. LAB 8 now says "จุดตรวจผ่าน 618/660".
- **m1** "login" → "เข้าสู่ระบบ" (2 places). **m3** "ผลที่คาดหวัง" (table header + LAB 5 prompt). **m4** rubric link. **m6** note on scoring /18 vs /20. **m7** reset done by Claude. **m8** 28 product pages. **m9** "แบ่งเป็นข้อ → …".

### Other
- **V1-F1**: LAB 7 ✅ line now has a duration (≈ 1 hr; selectors + tests ~35 min · ~9 min per full run). Source: LAB7_RESULT.
- **V1-F3** `_solution/README.md` §8.3: "~97 MB" (no source) → "หลายสิบ MB (รอบ LAB 7 ≈ 76 MB …)". Line 6 now says "ตัวเลขผลจริง… (ข้อ 8.3 เป็นการตัดไฟล์หลังจบ LAB)".
- **V1-F5**: report-bug-summary alt text notes that the screenshot cuts off before the WebKit row.
- **V4 concept-07**: Playwright masks logo replaced with a plain ▶ circle. The browser logos stay.
- **V4 lab5-toast-over-stock**: recaptured at BUG_MODE=0 (reset → add 2 → add 2). The toast is fully visible, there is no cursor dot, and red frames mark the toast and 🛒 = 3. Alt text updated. Data was reset again afterwards.
- **V4 🎭 emoji**: replaced with 🤖 in `intro-02-overview.png` and also in `lab-flow.png` (same source script).
- **V4 exploration-rules**: badge ③ moved above the ⚠️ so the "ปัดตามหลัก…" text is no longer covered.
- **V4 concept-02**: alt text softened to "ชั่งน้ำหนัก 3 แหล่ง".
- **V2 (e)**: `_shots/lab8-gif-TC-CHK-03.gif` re-encoded from 10.1 MB to **1.9 MB** (2 fps, 640 px, 64 colours, full 122 s kept). The old blob is still in git history.
- **V2 (c)**: deleted `img/.ipynb_checkpoints/` and `_solution/_design/shots/.ipynb_checkpoints/` (ignored, never tracked).

How the images were made: doc screenshots come from the W1 render scripts (`docs.js` / `diagrams.js`, Playwright HTML → PNG) copied to this session's scratchpad. The trimming was done only in the copy; `_solution/*.md` was not changed. The AI images were made with `cyolo exec -i <original>` as edits of the existing art. The toast image comes from a headless Playwright script.

---

## Rejected or not applied, and why

| Suggestion | Why |
|---|---|
| V3-H1 wording "index.html เป็นรายงานใหม่ของบทนี้" | Contradicts LAB7_RESULT ("คัดลอก … `reporters/html-report.ts` … จากบท 02" and then adapted). Used neutral wording instead: borrowed and adapted. |
| V3-m2 "ID" → "รหัส" in prompts and tables | The sample artifacts and screenshots (`tp-5-testcases.png`, `_solution/TEST-PLAN.md`, LAB5_RESULT) all use the column "ID". Renaming would make students' output differ from every example. Only the "คาดหวัง" → "ผลที่คาดหวัง" part (m3) was applied. |
| V2 (b) neutralise "Training bug" comments + `.dockerignore` `SPEC.md` | Inside `petshop/`, which is off-limits for this task. Listed under remaining issues. |
| V2 (d) `git add _solution/README.md` | Git-state commands are not allowed. (It is now tracked anyway through commit `1b3dc5e`.) |
| V1-F4 triage.json note "Playwright MCP" → "สคริปต์ headless" | This is an e2e artifact and would need an `index.html` re-render. The README is already correct. Low value. |
| V4 TEST-PLAN notes ("สินค้าหมด" exact label; 45/47 → 46/48 wording in TEST-PLAN line 212) | `_solution/TEST-PLAN.md` is the recorded LAB 5/6 output. Editing it would change a LAB artifact and break "ข้อความจริงจากไฟล์" in other screenshots. The current text works: "contains หมด" passes. |
| V4 report-summary 95.8% vs 96% | Needs a reporter code change plus a re-run. Cosmetic. |
| V4 lab1-docker "Up 16 minutes" | Recapturing would need a `--build` cycle that takes the shared container down. The alt text matches the image. Listed as remaining. |
| V3-M6 for README line 440 and `_solution` D18 ("[O] ล้วน") | Out of the reviewer's listed scope. Line 440 is a general remark, so it was left alone. |

## Remaining issues (need a human)

1. **`petshop/` source comments name all 3 bugs** (`lib/pricing.ts:90`, `components/ShopProvider.tsx:225`, `lib/validation.ts:81`), and `petshop/.dockerignore:13` lists `SPEC.md`. One `grep bug` reveals the answer key. Fix this in a task that is allowed to touch `petshop/`.
2. **Old binaries stay in git history**: the 10 MB GIF and the leaky images (`tp-8-quality`, `concept-03`, `concept-05`, `review-matrix`) can still be read from earlier commits unless history is rewritten.
3. `img/lab1-docker.png` still shows "Up 16 minutes" right after "Started". It looks staged.
4. `_solution/TEST-PLAN.md` M1 still says "ลด 1%". That is fine, because it is the answer key and the student image is now cropped. `_solution/README.md` §4 quotes it on purpose.
5. Uncommitted changes: `README.md`, `_solution/README.md`, 6 images in `img/`, the re-encoded GIF, and this file.
