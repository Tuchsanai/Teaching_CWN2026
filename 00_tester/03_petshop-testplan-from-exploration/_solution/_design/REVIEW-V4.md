# REVIEW-V4 — live spot-check of TEST-PLAN + README image audit

Reviewer: V4 (report-only, no repo files edited) · Date: 2026-10-10

## Verdict

- **TEST-PLAN expected results: 12 of 12 test cases checked (58 checkpoints) match the live site (normal mode).** I found no wrong expected value.
- **README images: 19 viewed. No blocking errors.** All the numbers I checked add up. 2 images show a non-browser brand logo (the Playwright masks). 1 screenshot is hard to read. The rest are small nits.

---

## Part 1: Spot-check of TEST-PLAN.md expected results against the live site

**Setup**
- `GET /` → `<html data-bug-mode="0">` (normal mode), so no restart was needed.
- The script is an isolated headless Playwright Node script: `scratchpad/v4/spot.cjs`, using `playwright@1.64.0` installed in the scratch dir and Chromium.
- I did not use the MCP browser.
- Every test case gets a **new browser context** and a `POST /api/test/reset` before it runs. I did not clear any cookies.
- Selectors (`data-testid`) are the same ones `e2e/tests/fixtures.ts` uses. The expected values were typed by hand from TEST-PLAN.md section 5, not copied from the site.

| # | TC | What was checked | Expected (plan) | Actual (live) | Result |
|---|---|---|---|---|---|
| 1 | TC-AUTH-02 | `Paw12346` and `paw12345`: stays on `/login`, error text, login-link still shown | "อีเมลหรือรหัสผ่านไม่ถูกต้อง" ×2 | same ×2 | ✅ |
| 2 | TC-PROD-03 | Freeze-dried chicken: detail button disabled, label, catalog card button, 🛒 | disabled · "หมด" · disabled · 0 | disabled · "สินค้าหมด" · card button "สินค้าหมด" disabled · 0 | ✅ |
| 3 | TC-CART-01 | Kitten 400 g ×2 | 378 / 0 / 50 / **428** · bar ฿621 · 🛒 2 | 378 / 0 / 50 / 428 · "ซื้อเพิ่มอีก ฿621 เพื่อส่งฟรี" · 2 | ✅ |
| 4 | TC-COUP-01 | PAW10 on ฿590 | −59 / 50 / **581** · message mentions PAW10 | −59 / 50 / 581 · "ใช้คูปอง PAW10 แล้ว" | ✅ |
| 5 | TC-COUP-03 | PAW10 on ฿799 (rounding) | −79 / 50 / **770** | −79 / 50 / 770 | ✅ (still `[O-ยังไม่ยืนยัน]` E1, correctly labelled) |
| 6 | TC-COUP-05 | NEWCAT50 at ฿499, then ฿534 | 499: 0 off, 549, message "ต้องซื้ออาหารแมวขั้นต่ำ ฿500" · 534: −50, **534** | same in both states | ✅ |
| 7 | TC-COUP-08 | SUMMER20 on ฿799 | "คูปองนี้หมดอายุแล้ว" · 0 · 849 | same | ✅ |
| 8 | TC-SHIP-01 | ฿998 (ball 199 + chicken 3 kg 799) | 50 · **1,048** · bar ฿1 | 50 · 1048 · "ซื้อเพิ่มอีก ฿1 เพื่อส่งฟรี" | ✅ |
| 9 | TC-SHIP-02 | ฿999 (wand 129 + bowl 290×3) | ฟรี · **999** · free-ship message | ฟรี · 999 · "ได้ส่งฟรีแล้ว!" | ✅ |
| 10 | TC-SHIP-03 | Express at ฿189 and at ฿999 (logged-in checkout) | 120/309 · 120/1,119 | 120/309 · 120/1119 | ✅ (the ฿999 case relies on the plan's stated assumption; the site agrees) |
| 11 | TC-CHK-03 | Phone `081234567` / `08123456789` / `1812345678` / `0812345678` | first 3: stay on `/checkout` + "เบอร์โทรต้องเป็นตัวเลข 10 หลัก ขึ้นต้นด้วย 0" · 10 digits starting with 0: order created | same | ✅ |
| 12 | TC-CHK-06 | 1.5 kg, express, PromptPay | button and order total **฿710**, order page shows PromptPay and express | 710 / 710 / PromptPay ✓ / ด่วน ✓ | ✅ |

12 different test case IDs were run, with 58 checkpoints. All of them matched. The plan's dependence on the observed message texts holds in normal mode.

**Minor plan notes from the run (not errors):**
- TC-PROD-03 says the label is "หมด". The live label is **"สินค้าหมด"**, and the catalog card button text is also "สินค้าหมด". "Contains หมด" passes. If someone automates it with an exact-text match it will fail. Suggest writing it as `ป้าย "สินค้าหมด"` to be exact.
- The phone error test id is `error-ship-phone`, not `error-phone`. This is fine in the suite; noting it only for anyone writing an ad-hoc script.

---

## Part 2: README.md image audit (top-level `README.md`, 35 images; 19 viewed)

Viewed: intro-01-explorer, intro-02-overview, oracle-badges, concept-02-oracle-3-sources, concept-03-bake-the-bug, lab1-docker, explore-home, explore-account, exploration-rules, explore-checkout-errors, lab5-coupon-paw10, lab5-toast-over-stock, report-summary, report-bug-summary, report-defect, tp-6-criteria, concept-05-rule-hunting, concept-07-plan-to-test, intro-05-mystery-bugs.

### Issues (most important first)

| Sev | Image | Finding | Suggestion |
|---|---|---|---|
| **Medium** | `img/concept-07-plan-to-test.jpg` | The robot's chest has the **Playwright red and green theater-masks logo** with the word "Playwright". That is a product brand logo, not a browser logo. The Chrome, Firefox and Safari logos on the 3 small robots are allowed browser logos. | Regenerate or paint over the masks with a generic gear/play icon. The word "Playwright" can stay as plain text if wanted. |
| **Medium** | `img/concept-03-bake-the-bug.jpg` | Same red and green masks logo on the robot's head, plus the "Playwright" label on its body. The alt text says "หุ่นยนต์ Playwright" but does not mention the logo. | Same fix as above. |
| Low | `img/intro-02-overview.png` | Step 4 uses the 🎭 theater-masks emoji, which is the de-facto Playwright mark. It is a generic emoji, so this is borderline, not a logo. | Optional: swap it for 🤖 or ▶️ to be consistent with the logo rule. |
| Low | `img/lab5-toast-over-stock.png` | This is the image that proves the P3 bug, but the **toast was captured mid-fade**: it is semi-transparent over the "ช่วงวัย" card and hard to read. The "เพิ่มลงตะกร้า" button text is covered by a red cursor dot. The 🛒 badge "3" is tiny. The alt text ("ตะกร้ามี 3 ชิ้น … toast บอกว่าเพิ่มสูตรลดก้อนขนลงตะกร้าแล้ว") is correct but is hard to check against the image. | Recapture after the toast finishes animating in, without the cursor dot. Consider a red annotation on the toast and on the 🛒 = 3 badge, like the other annotated shots. |
| Low | `img/report-summary.png` | The headline and cards say **95.8%**, but the per-browser table rows say **96%** (46/48 rounded). The numbers are consistent, but the precision differs within one screenshot. The alt text quotes 95.8%, which is fine. | Optional: make the report table use 1 decimal place. This is a reporter change, not an image change. |
| Low | `img/lab1-docker.png` | `docker compose up -d --build` shows "Started", but the very next `docker compose ps` shows "CREATED 16 minutes ago / Up 16 minutes". That reads as staged. The alt text matches the image. | Optional: recapture, or edit to "Up 10 seconds (healthy)". |
| Low | `img/exploration-rules.png` | Callout badge ③ (⚠) sits on top of the start of the R4 "ที่มา" text, so the first characters of "ปัดตามหลักคณิตศาสตร์ทั่วไป" are hidden. | Nudge the badge right or up a few px. |
| Nit | `img/concept-02-oracle-3-sources.jpg` | The alt text says "ฝั่งเอกสารข้อมูลทีมหนักที่สุด", but the 3-pan scale does not clearly show the D pan as lowest; the pans look at about the same height. | Soften the alt text ("หุ่นยนต์ชั่งน้ำหนัก 3 แหล่ง") or regenerate with the green pan clearly lowest. |
| Nit | `img/intro-01-explorer.jpg` | The laptop shows a made-up shop "Happy Paws", not PawPantry. It is not a real brand, so this is OK; the alt text only says "เว็บร้านอาหารสัตว์". | None needed. |

### Number checks (all correct ✅)

- **exploration-rules.png**:
  - R3: 999→99, 1,054→105.
  - R4 floor: 799→79, 189→18, 69→6, 35→3, 1,119→111. Rounding the usual way gives 80/19/7/4/112 ✓.
  - R7: 999−799=200, 999−189=810, 999−520=479 ✓.
  - R8: 1,054−105=949 ✓.
- **lab5-coupon-paw10.png**: 590 − 59 + 50 = 581, and the bar shows 999 − 590 = ฿409 ✓.
- **explore-checkout-errors.png**: 189 + 35×2 = 259, + 50 = 309, button ฿309 ✓. The 4 error texts match the alt text and TC-CHK-02 ✓. The phone and postcode boxes show grey placeholders, not typed values, so this still fits "กดยืนยันโดยไม่กรอก" ✓.
- **explore-account.png**: PP-100001, 3 items, ฿379, total spent ฿379, 1 order ✓ (matches the alt text).
- **report-summary.png**:
  - 48 TCs ×3 browsers = 144 runs ✓.
  - 46/48 = 95.8% ✓.
  - P1 30/30 ✓, which matches TEST-PLAN's count: 30 P1, 13 P2, 5 P3 = 48.
  - Failures TC-SRCH-01 (P2) and TC-CART-05 (P3) ✓.
- **report-bug-summary.png**: 41/48 = 85.4% ✓, P1 26/30, 4 P1 bugs open, 7/7 classified ✓. 30 − 26 = 4 matches "4 ข้อ" ✓.
- **report-defect.png**: 2/3 checkpoints = 67% per browser, 6 of 9 overall ✓. 520×3 = 1,560 ✓. The alt text matches.
  - Nit: Chromium has no "วิดีโอ" link while Firefox and WebKit do.
- **tp-6-criteria.png**: the text matches TEST-PLAN §6 exactly. The note "ตรง 45/47 … → 46/48" is a little confusing: 48 TCs, 47 checked by hand, 2 mismatched. It implies the one unchecked TC is assumed to pass. Suggest adding "(1 ข้อยังไม่ได้ลองมือ)" in TEST-PLAN.md line 212 so the jump from 47 to 48 is clear.

### Alt text versus content

All 19 viewed images: the alt text describes what is actually shown, with one exception — concept-02's "heaviest" claim (see the Nit above).

### Thai text readability

- All Thai text is readable. This covers the AI illustrations (titles "ไม่มีแผน? สำรวจแล้วเขียนเอง", "อย่าอบบั๊กลงในผลที่คาดหวัง", "ล่ากฎและความเสี่ยง", "บั๊กปริศนา", "จากแผนสู่ test", sign labels วิเคราะห์/กฎ/ความเสี่ยง, สังเกต/วิเคราะห์/ป้องกัน), the diagrams and the screenshots.
- I found no garbled glyphs or broken vowel or tone marks.
- The only readability problem is the faded toast in lab5-toast-over-stock.png (above).

---

## Summary of actions suggested

1. Remove the Playwright masks logo from `concept-07-plan-to-test.jpg` and `concept-03-bake-the-bug.jpg`.
2. Recapture `lab5-toast-over-stock.png` with the toast fully visible, no cursor dot, and ideally annotated.
3. Optional polish:
   - 🎭 emoji in intro-02
   - Docker "16 minutes" in lab1-docker
   - Badge ③ overlap in exploration-rules
   - concept-02 alt text
   - TEST-PLAN: "สินค้าหมด" exact label; 45/47 → 46/48 wording.
