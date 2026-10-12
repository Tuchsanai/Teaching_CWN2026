# METHODS · กล่องเครื่องมือ: เพิ่มฟีเจอร์ / แก้บั๊กใน "ระบบเดิม" แบบ tester + AI agent (บท 05–06)

> สำหรับผู้วางแผน LAB / ข้อสอบ บท 05 (PawPantry legacy) และ 06 (Sabai Spa แบบหน่วยงานรัฐ + Change Request)
> ตรวจจริง 12 ต.ค. 2026 บน Windows 11 · `@playwright/test@1.63.0` · Claude Code 2.1.296 · image `rea-lab:6.4.0`
> โค้ดที่ใช้ยืนยันอยู่ที่ `C:/t/work/a3/` (แอปจำลอง "Mini Shop" ที่มีบั๊กฝัง + เทสต์ 10 ข้อ × 3 browser)
> สัญลักษณ์: ✅ = รันจริงแล้วได้ผลตามที่เขียน · 📖 = ตรวจจาก `--help` / type definition / docs เท่านั้น (เปิด GUI หรือโต้ตอบไม่ได้ในงานนี้)

ประโยคหลัก: **"อ่านก่อน → ล็อกพฤติกรรมเดิม → แก้ให้เล็กที่สุด → พิสูจน์ว่าอย่างอื่นไม่พัง"**

---

## 0. เลือกเครื่องมือเร็ว ๆ

| สถานการณ์ | เครื่องมือหลัก | หัวข้อ |
|---|---|---|
| เปิด repo เดิมครั้งแรก ให้ agent เข้าใจระบบ | CLAUDE.md + CODEBASE-MAP + Explore subagent + Plan mode | [M1](#m1-context-engineering-ให้-agent-ทำงานกับ-codebase-เดิม) |
| ได้แค่เว็บที่รันอยู่ / ไฟล์ build / ไม่เชื่อ source | REA (black-box) + HAR | [M2](#m2-black-box-vs-white-box-เมื่อไรใช้-rea-เมื่อไรอ่าน-repo) [M4](#m4-har-บันทึกและเล่นซ้ำ-network) |
| ก่อนแตะโค้ดใด ๆ | Characterization test / golden master | [M3](#m3-characterization-test--golden-master-michael-feathers) |
| ต้องรู้ว่าแก้ตรงนี้แล้วกระทบอะไร | Impact analysis (grep, git, REA trace) | [M6](#m6-impact-analysis-แก้ตรงนี้กระทบอะไร) |
| ลงมือแก้บั๊ก / เพิ่มฟีเจอร์ | Safe change loop → CHANGE-REPORT | [M7](#m7-safe-change-loop-วงจรแก้อย่างปลอดภัย) |
| งานภาครัฐ มี CR / ต้องเซ็นรับ | CR form + traceability + migration ย้อนได้ | [M8](#m8-โครงการแบบภาครัฐ-change-request--traceability--sign-off) |

---

## M1. Context engineering: ให้ agent ทำงานกับ codebase เดิม

ปัญหาหลักของงาน legacy คือ **agent ไม่รู้ว่าอะไรห้ามแตะ อะไรเป็นพฤติกรรมที่ตั้งใจ** ถ้าไม่ให้ context ไว้ agent จะ "เขียนใหม่ให้สวย" แทนที่จะ "แก้ให้น้อย"

| เทคนิค | ใช้เมื่อ | ทำยังไง | กับดัก | LAB ที่เหมาะ |
|---|---|---|---|---|
| **CLAUDE.md** (`/init` แล้วแก้เอง) 📖 | เริ่มงานกับ repo ใหม่ทุกครั้ง | พิมพ์ `/init` ใน Claude Code → ได้ร่าง CLAUDE.md → **คนแก้เพิ่ม** ส่วน "ห้ามแตะ", "พฤติกรรมแปลกที่ตั้งใจ", "คำสั่งรันเทสต์" | `/init` เขียนจากโค้ดที่เห็น ไม่รู้กติกาธุรกิจ/ข้อห้าม · อย่าให้ยาวเกิน (ทุกบรรทัดกิน context ทุกเซสชัน) | 05 LAB แรก ๆ, 06 LAB เปิด |
| **CODEBASE-MAP.md** | repo ใหญ่กว่าที่ agent อ่านหมดในรอบเดียว | สั่ง agent อ่านแล้วเขียนตาราง: โฟลเดอร์/ไฟล์ · หน้าที่ · หน้าจอ/route · API · ตาราง DB · เทสต์ที่ครอบ · แล้ว **คนตรวจ** อ้างใน CLAUDE.md ด้วย `@CODEBASE-MAP.md` | แผนที่เก่าเร็ว → ใส่วันที่ + commit/เวอร์ชันที่ทำแผนที่ · AI อาจเดาหน้าที่จากชื่อไฟล์ → ให้ใส่ "ยืนยันจาก: บรรทัดไหน" | 05, 06 |
| **@file references** | ชี้ให้ agent อ่านไฟล์ที่ถูกต้อง ไม่ต้องค้นเอง | ในพรอมต์พิมพ์ `@web/lib/pricing.ts` (Tab เติมชื่อ) · ใน CLAUDE.md ใช้ `@docs/xxx.md` เพื่อ import | อ้างไฟล์ใหญ่ทั้งไฟล์ = เปลือง context · อ้างผิดไฟล์ = agent เชื่อไฟล์นั้น | ทุก LAB ที่แก้โค้ด |
| **Plan mode** ✅ (flag) | ก่อนแก้อะไรที่แตะ > 1 ไฟล์ | `Shift+Tab` สลับจนขึ้น plan mode หรือเปิดด้วย `claude --permission-mode plan` (choices ที่ตรวจจาก `claude --help`: `acceptEdits, auto, bypassPermissions, manual, dontAsk, plan`) | แผนดี ≠ โค้ดถูก ยังต้องมีเทสต์ · อย่ากดอนุมัติแผนโดยไม่อ่าน "ไฟล์ที่จะแตะ" | 06 ทุก CR |
| **Explore subagent** 📖 | ต้องอ่านหลายไฟล์เพื่อตอบคำถามเดียว ("ส่วนลดคิดตรงไหนบ้าง") | พรอมต์: `ใช้ Explore subagent ค้นว่า … ตอบเป็นตาราง ไฟล์:บรรทัด · หน้าที่` · Explore อ่านอย่างเดียว แก้ไฟล์ไม่ได้ | ได้ "ข้อสรุป" ไม่ได้เนื้อไฟล์ → ถ้าจะแก้ต้องให้ main agent เปิดไฟล์จริงอีกที | 05 LAB อธิบาย repo |
| **จำกัดไฟล์ที่แก้ได้** ✅ | กันไม่ให้ agent แตะเทสต์เดิม / DB init / โค้ดนอกขอบเขต CR | `.claude/settings.json` → `permissions.deny` ด้วย `Edit(path)` (ดูโค้ดด้านล่าง) · หรือ flag `--disallowedTools` | ⚠️ **`Write(path)` ใช้ไม่ได้กับ file rule** Claude Code เตือนตรง ๆ ว่า *"Write(locked/\*\*) is not matched by file permission checks — only Edit(path) rules are"* → ใช้ `Edit(...)` อย่างเดียว (ครอบทุกเครื่องมือแก้ไฟล์) · deny กัน Edit tool แต่ไม่กัน Bash `sed`/`echo >` → deny Bash ด้วยถ้าจริงจัง | 06 (ล็อก `e2e-legacy/`, `db/init/`) |
| **"อธิบายก่อนแก้"** | ทุกงานแก้ legacy | พรอมต์ข้อ 1: `ยังไม่ต้องแก้ อธิบายก่อนว่า flow นี้ทำงานยังไง อ้างไฟล์:บรรทัด` | agent ชอบข้ามไปแก้เลย → ต้องเขียน "ยังไม่ต้องแก้" ชัด ๆ | 05, 06 |
| **Impact analysis ก่อน diff** | ก่อนอนุมัติให้แก้ | พรอมต์: `ก่อนเขียน diff ให้ทำตาราง ไฟล์ที่จะแตะ · เหตุผล · ใครเรียกใช้ · เทสต์ที่ต้องรันซ้ำ · ความเสี่ยง แล้วรอผมอนุมัติ` | ตารางจาก AI อาจไม่ครบ → เทียบกับผล grep เอง (M6) | 06 ทุก CR |

**ตัวอย่าง `.claude/settings.json` ที่ตรวจแล้ว ✅** (`claude -p` + `--permission-mode acceptEdits`: แก้ `open/b.txt` ได้ · `locked/a.txt` ถูกปฏิเสธด้วยข้อความ *"File is in a directory that is denied by your permission settings."* ไฟล์ไม่เปลี่ยน)

```json
{
  "permissions": {
    "deny": ["Edit(e2e-legacy/**)", "Edit(db/init/**)", "Edit(web/scripts/check-rules.mjs)"]
  }
}
```

**โครง CLAUDE.md สำหรับ legacy** (คนเติมหลัง `/init`)

```markdown
# <ระบบ> — ระบบเดิม (legacy) อ่านก่อนแก้
## รันยังไง        คำสั่ง start / test / reset data (PowerShell)
## แผนที่          @CODEBASE-MAP.md
## ห้ามแตะ         e2e-legacy/ (ชุด regression เดิม) · db/init/ (ใช้ db/migrations/ แทน) · …
## พฤติกรรมแปลกที่ "ตั้งใจ"   เช่น ปัดเศษแต้มทิ้ง · ข้อความ error เป็นไทยตายตัว (เทสต์เดิมจับคำนี้)
## กติกาการแก้     อธิบายก่อนแก้ · ทำ impact table ก่อน diff · แก้ให้เล็กที่สุด · ห้ามแก้เทสต์เดิมให้ผ่าน
## เอกสารเก่า      SPEC.md อาจไม่ตรงโค้ด → ถ้าขัดกันให้รายงาน อย่าเลือกเอง
```

---

## M2. Black-box vs white-box: เมื่อไรใช้ REA เมื่อไรอ่าน repo

skill ของ REA เขียนเองใน `SKILL.md`: **"Skip REA for ordinary source-repository architecture analysis."** → มี source ครบและเชื่อได้ = อ่าน repo ปกติ · REA สำหรับ "ของที่ส่งมอบ/รันอยู่"

| มี/ไม่มีอะไร | มุม | ใช้อะไร | ได้อะไร |
|---|---|---|---|
| มีแค่ URL เว็บที่รันอยู่ | black-box | Playwright สำรวจ + HAR (M4) + REA `inspect-web-network-capture` | endpoint, payload, flow จริง |
| มีไฟล์ build (`.next/static`, bundle, ASAR) ไม่มี source | black-box | REA `analyze-javascript-application` → `trace-application-feature` | กราฟ module ↔ endpoint ↔ storage |
| มี source แต่ **ไม่แน่ใจว่าตรงกับที่ deploy** | ทั้งคู่ | REA `compare-source-to-bundle` / `compare-application-versions` + อ่าน repo | ส่วนที่ต่าง = ความเสี่ยง |
| มี source ครบ เชื่อได้ (กรณีส่วนใหญ่ของบท 06) | white-box | อ่าน repo + Grep + git (M6) — **ไม่ต้องใช้ REA** | ไฟล์:บรรทัด ที่ต้องแก้ |

**Triangulate = เอาสองมุมมายืนยันกัน** ตัวอย่างที่รันจริงบน PawPantry ✅

| มุม | คำสั่ง | ผล |
|---|---|---|
| black-box (REA) | `trace-application-feature` seed `/api/orders` direction `incoming` บน Evidence ของ `.next/static` | **4 node / 3 edge**: endpoint `/api/orders` (mechanism `call:fetch`) ← module `chunks/2bxbzaw5q8rvv.js` (14,231 bytes, มี class `checkout-*`) |
| white-box (grep) | `grep -rn "/api/orders" --include=*.tsx .` ใน `petshop/` | `components/CheckoutForm.tsx:74` `fetch("/api/orders", { method: "POST" …` |
| สรุป | สองมุมตรงกัน | ฟีเจอร์ checkout ↔ POST `/api/orders` ยืนยันแล้ว |

```powershell
# ✅ รันจริงใน PowerShell (โฟลเดอร์ปัจจุบันมี rea-static.json) → exit 0, traced_nodes 4, traced_edges 3
# ⚠️ PowerShell 5.1: '>' เขียนไฟล์มี BOM (ไบต์แรก 239 187 191) → JSON.parse ธรรมดา fail "Unexpected token" (เจอจริง)
#    → redirect ผ่าน cmd /c (ได้ไบต์แรก '{' ปกติ) และ/หรือ ตัด BOM ใน node
cmd /c "docker run --rm -v C:/t/pp:/work rea-lab:6.4.0 analyze-javascript-application /work/.next/static --json > rea-static.json"
node --input-type=module -e "import {readFileSync,writeFileSync} from 'node:fs'; const application=JSON.parse(readFileSync('rea-static.json','utf8').replace(/^\uFEFF/,'')); writeFileSync('trace-input.json', JSON.stringify({application, seed:{kind:'string', value:'/api/orders'}, direction:'incoming'}))"
cmd /c "docker run --rm -v %CD%:/work rea-lab:6.4.0 trace-application-feature /work/trace-input.json --json > trace-orders.json"
# Git Bash: ต้องใส่ MSYS_NO_PATHCONV=1 นำหน้า docker ไม่งั้น /work/... ถูกแปลงเป็น C:/Program Files/Git/work/... (เจอจริง → ENOENT)
```

| direction ✅ | node | edge | ใช้ทำอะไร |
|---|---|---|---|
| `incoming` | 4 | 3 | "ใครเรียก endpoint นี้" → หาไฟล์/หน้าที่กระทบ (**ใช้บ่อยสุด**) |
| `outgoing` | 1 | 0 | endpoint ไม่มีขาออกในกราฟ (มี terminal path 1) |
| `both` | 64 | 69 | **ได้แทบทั้งกราฟ** (แอปเล็ก ทุกอย่างเชื่อมกัน) → ไม่ช่วยจำกัดขอบเขต |

ค่า `direction` ที่รับได้ (จาก error ของ REA เมื่อส่งค่าผิด): `outgoing`, `incoming`, `both` · Evidence ของ PawPantry ทั้งก้อน (`C:/t/pp/rea-static.json`) ใหญ่ **49,759,480 bytes** → ใช้ `inspect-analysis-view` ฉาย summary ก่อนให้ agent อ่าน · coverage ของ trace = `partial` (บอกผู้เรียนว่า REA บอกเองว่าเห็นไม่ครบ)

กับดัก: black-box เห็นแค่ฝั่ง client (bundle) **ไม่เห็นกติกาฝั่ง server** (เช่นคิดราคาใน API route) → ต้องคู่กับการทดสอบพฤติกรรมจริง (M3) เสมอ · endpoint ที่ minify แล้วกู้ได้เป็นชื่อย่อ (`a`, `b`, `c`) อย่าเอาไปใส่รายงานเป็น endpoint จริง

---

## M3. Characterization test / golden master (Michael Feathers)

แนวคิด: ก่อนแก้ระบบที่ไม่มีเทสต์ ให้ **เขียนเทสต์ที่บันทึกสิ่งที่ระบบทำอยู่ตอนนี้** (ไม่ใช่สิ่งที่ "ควร" ทำ) รวมถึงจุดแปลก ๆ → แก้แล้วเทสต์แดง = รู้ทันทีว่าเปลี่ยนพฤติกรรม

| ชนิด snapshot (1.63) | API ที่ตรวจใน type definition ✅ | ล็อกอะไร | ไฟล์ baseline |
|---|---|---|---|
| โครงหน้า (accessibility tree) | `expect(locator).toMatchAriaSnapshot(\`…\`)` (inline) · `expect(page).toMatchAriaSnapshot({ name })` (ไฟล์) · มี `page.ariaSnapshot()` ด้วย | heading, ปุ่ม, ลิงก์, รายการ, ข้อความ | `*.aria.yml` (ไม่มี suffix browser/OS) |
| ภาพหน้าจอ | `expect(page).toHaveScreenshot(name, { maxDiffPixels, maxDiffPixelRatio })` | หน้าตา | `name-<project>-<os>.png` |
| ผล API (JSON) | `expect(JSON.stringify(body, null, 2)).toMatchSnapshot('x.json')` + `expect(res).toBeOK()` | ข้อมูล/รูปแบบ response | `x-<project>-<os>.json` |
| ค่าที่สำคัญ | `toHaveText('450')` ตรง ๆ | ตัวเลขเงิน, สถานะ | ในโค้ดเทสต์ |

**แยก "ถูกอยู่แล้ว" กับ "ผิดที่รู้อยู่แล้ว"** ด้วย `test.fail()` + `annotation`:

```ts
// ✅ รันจริง 3 browser (Mini Shop: ยอดรวมไม่นับสินค้าชิ้นสุดท้าย = บั๊กฝัง)
test('ยอดรวมปัจจุบัน = 450 (พฤติกรรมเดิม ล็อกไว้ตามจริง)', {
  annotation: { type: 'legacy-quirk', description: 'ยอดรวมไม่นับสินค้าชิ้นสุดท้าย → BUG-001' },
}, async ({ page }) => {
  await page.goto('/');
  await expect(page.getByTestId('total')).toHaveText('450');
});

test('ยอดรวมที่ถูกต้อง = 570 (known bug)', {
  annotation: { type: 'issue', description: 'BUG-001 ยังไม่แก้' },
}, async ({ page }) => {
  test.fail(); // ตอนนี้ต้อง fail · ถ้าวันไหนผ่าน = มีคนแก้แล้ว → รายงาน "Expected to fail, but passed."
  await page.goto('/');
  await expect(page.getByTestId('total')).toHaveText('570', { timeout: 2000 });
});

test('โครงหน้า (aria)', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('listitem').first()).toBeVisible();
  await expect(page.locator('body')).toMatchAriaSnapshot(`
    - heading "Mini Shop" [level=1]
    - list:
      - /children: equal
      - listitem: Dog Food ฿450
      - listitem: Cat Toy ฿120
  `);
});

test('API golden', async ({ request }) => {
  const res = await request.get('/api/products');
  await expect(res).toBeOK();
  expect(JSON.stringify(await res.json(), null, 2)).toMatchSnapshot('products.json');
});
```

**ผลจริง ✅** (เทสต์ 10 ข้อ × chromium/firefox/webkit = 30)

| รอบ | ผล | ความหมาย |
|---|---|---|
| รอบแรก (ยังไม่มี baseline) | 9 failed · 18 passed | *"A snapshot doesn't exist at … writing actual."* → รอบแรก **แดงเสมอ** แต่เขียนไฟล์ให้ (โหมด default = `missing`) |
| รอบสอง | **30 passed** (test.fail 3 ข้อแสดง `x` แต่นับเป็น pass) | baseline พร้อม |
| แก้บั๊กแล้ว (`$env:FIXED=1`) | **6 failed** = "450" ×3 + "Expected to fail, but passed." ×3 | เทสต์ 2 ตัวนี้คือ "สัญญาณ" ว่าพฤติกรรมเปลี่ยน → ไปอัปเดต: ลบ `test.fail()` และเปลี่ยน 450 เป็น 570 พร้อมอ้าง CR |
| แก้บั๊กแล้ว: screenshot `maxDiffPixelRatio: 0.01` | **ผ่าน (ไม่จับ!)** | ตัวเลข 450→570 ต่างแค่ **44 pixels (ratio 0.01)** → tolerance กลืนหมด · screenshot แบบไม่ตั้ง tolerance จับได้ |
| แก้บั๊กแล้ว: `home.aria.yml` | **ผ่าน (ไม่จับ!)** | ไฟล์ที่ Playwright สร้างเองเขียนตัวเลขเป็น regex: `listitem: /Dog Food ฿\d+/` · `paragraph: "/ยอดรวม: \\d+/"` |
| เพิ่มสินค้าชิ้นที่ 3 (`$env:EXTRA=1`) + aria inline **ไม่มี** `/children: equal` | **ผ่าน (ไม่จับ!)** | aria snapshot จับคู่ list แบบ "บางส่วน" โดย default |
| เหมือนบน แต่ **มี** `/children: equal` | fail ✅ | ใส่ `/children: equal` เมื่ออยากล็อกจำนวนรายการ |

| กับดัก | วิธีกัน |
|---|---|
| aria snapshot = **ล็อกโครง ไม่ล็อกค่า** (ตัวเลขกลายเป็น `\d+`) | ค่าเงิน/สถานะ ล็อกด้วย `toHaveText` หรือ API JSON snapshot |
| `-u` แก้ inline aria ให้เป็น **`test-results/rebaselines.patch`** (ไม่แตะ source; ต้อง `git apply`) และในรอบจริง patch **ลบ `/children: equal` และเปลี่ยนราคาเป็น regex** | อ่าน patch ทุกบรรทัดก่อน apply · ห้ามสั่ง agent "รัน -u ให้ผ่าน" |
| `-u` มีโหมด `all \| changed \| missing \| none` (default ตอนไม่ใส่ flag = `missing`, ใส่ `-u` เฉย ๆ = `changed`) | baseline ใหม่ต้องมีเหตุผล (CR/BUG id) ใน CHANGE-REPORT |
| screenshot/JSON มี suffix `-chromium-win32` → baseline บน Windows ใช้กับ Linux CI ไม่ได้ | ใช้ `snapshotPathTemplate` หรือสร้าง baseline บนเครื่องเดียวกับที่รัน |
| ข้อมูลเปลี่ยนเอง (เวลา, id, ลำดับ) → snapshot แดงทุกรอบ | reset data ก่อนเทสต์ · mask/ตัดฟิลด์ที่เปลี่ยนก่อน snapshot · ใช้ `mask:` ใน screenshot |
| เทสต์ที่ใช้ `test.fail()` ถ้าล้มด้วยเหตุผลอื่น (หน้าพัง) ก็ยัง "ผ่าน" | assertion ใน test.fail ต้องเจาะจงค่าที่ผิด และมีเทสต์คู่ที่ล็อกค่าปัจจุบัน (แบบ 450 ข้างบน) |

LAB ที่เหมาะ: 05 (ล็อก PawPantry ก่อนแตะ) · 06 (ก่อนรับ CR ทุกข้อ) · ข้อสอบ: "เขียน characterization 5 ข้อ แล้วระบุว่าข้อไหนคือ known bug"

---

## M4. HAR: บันทึกและเล่นซ้ำ network

| ใช้เมื่อ | ได้อะไร |
|---|---|
| ทำ **API inventory** ของระบบที่ไม่มีเอกสาร | รายการ request/response จริง → ส่งเข้า REA `inspect-web-network-capture <file.har> har --json` ได้ |
| ทดสอบ UI โดยไม่ต้องรัน backend / แช่ข้อมูลให้คงที่ | mock จากของจริง |
| อยากทดสอบกรณีที่สร้างยากในระบบจริง (เช่น สินค้า 0 ชิ้น) | แก้ HAR แล้วเล่นซ้ำ |

```ts
// ✅ 3 วิธี รันจริง 3 browser (12 passed)
// 1) บันทึก: recordHar ใน context (ต้อง close context ไฟล์ถึงถูกเขียน)
const context = await browser.newContext({ baseURL,
  recordHar: { path: `hars/products-${info.project.name}.har`, urlFilter: '**/api/**', mode: 'minimal' } });
// ... ใช้งานหน้าเว็บ ...
await context.close();

// 2) เล่นซ้ำ: request ที่ไม่มีใน HAR → abort (จับได้ว่า UI เรียกอะไรใหม่)
await page.routeFromHAR(`hars/products-${info.project.name}.har`, { url: '**/api/**', notFound: 'abort' });

// 3) บันทึกระหว่างเทสต์: update:true (options ที่ตรวจใน types: notFound, update, updateContent, updateMode, url)
await page.routeFromHAR('hars/upd.har', { url: '**/api/**', update: true, updateContent: 'embed', updateMode: 'minimal' });

// แก้ HAR เป็น mock: เพิ่มสินค้าชิ้นที่ 3 → หน้าแสดง 3 รายการ ✅
const h = JSON.parse(fs.readFileSync(src, 'utf8'));
const c = h.log.entries[0].response.content;           // { size, mimeType, text }
c.text = JSON.stringify([...JSON.parse(c.text), { id: 3, name: 'Bird Seed', price: 80 }]);
fs.writeFileSync(dst, JSON.stringify(h));
```

```powershell
# อัด HAR ระหว่างคลิกเอง (ได้ทั้งโค้ดและ HAR) 📖
npx playwright codegen --save-har=legacy.har --save-har-glob="**/api/**" http://localhost:3000
```

| กับดัก (เจอจริง ✅) | วิธีกัน |
|---|---|
| HAR จับคู่ด้วย **URL เต็มรวม host:port** — HAR ที่อัดที่ `127.0.0.1:8997` เล่นซ้ำบน `:9759` แล้ว **ไม่เจอ → test fail** | อัดและเล่นซ้ำบน base URL เดียวกันเสมอ (บท 05/06 ใช้พอร์ตตายตัว) |
| 3 project (browser) เขียน HAR ไฟล์เดียวกันพร้อมกัน → ไฟล์ทับกัน (รอบแรกได้ HAR ของ firefox) | ตั้งชื่อไฟล์ตาม `testInfo.project.name` |
| HAR `mode: 'full'` เก็บ cookie / header / token จริง | ใช้ `mode: 'minimal'` + `urlFilter` · **ห้าม commit HAR ที่มี session จริง** |
| เล่นซ้ำจาก HAR = backend ไม่ถูกทดสอบเลย | ใช้ HAR เฉพาะเทสต์ UI · regression จริงต้องยิงระบบจริง |

---

## M5. Codegen · Trace viewer · UI mode: เรียนรู้ระบบเดิมเร็ว ๆ

| เครื่องมือ | คำสั่ง (ตรวจจาก `--help` 1.63) | ใช้เรียนรู้ legacy ยังไง | กับดัก |
|---|---|---|---|
| **codegen** 📖 | `npx playwright codegen [url]` · `-o file` · `--target playwright-test` · `--test-id-attribute data-testid` · `--save-har` · `--save-storage auth.json` / `--load-storage` | คลิก flow จริงหนึ่งรอบ → ได้ locator ของระบบเดิม + HAR | locator ที่ได้อาจเปราะ (nth, text ยาว) · ไม่มี assertion → ต้องเติมเอง · เปิด browser มีหน้าต่าง (headed) ทำใน agent ไม่ได้ ให้ผู้เรียนทำเอง |
| **Trace viewer** 📖 GUI / ✅ CLI | `npx playwright show-trace trace.zip` · config `trace: 'retain-on-failure'` หรือ `--trace on` | ย้อนดู DOM snapshot, network, console ทีละ action | trace.zip มีข้อมูลจริง (cookie, payload) → อย่าแชร์ออกนอก |
| **Trace CLI (สำหรับ agent)** ✅ | `npx playwright trace open <zip>` → `trace actions` · `trace requests` · `trace console` · `trace errors` · `trace close` | agent อ่าน trace ได้โดยไม่ต้องเปิด GUI (รันจริง: ได้ตาราง action 13 แถว + request 2 แถว พร้อมคอลัมน์ Route `fulfilled` จาก HAR) | ต้อง `trace close` เมื่อจบ (ลบไฟล์ที่แตกไว้) |
| **UI mode** 📖 | `npx playwright test --ui` (`--ui-port 0` ให้เปิดในแท็บ) | เดินเทสต์เดิมทีละข้อ ดู before/after, watch mode | GUI → ผู้เรียนทำเอง ไม่ใช่ agent |
| อื่น ๆ ที่มีใน 1.63 📖 | `npx playwright init-agents --loop claude` (planner/generator/healer agents) · `npx playwright init-skills` | ทางเลือกสำหรับบทต่อ ๆ ไป | ยังไม่ได้ทดลองในงานนี้ |

---

## M6. Impact analysis: แก้ตรงนี้กระทบอะไร

| เทคนิค | คำสั่ง / วิธี | ได้อะไร | กับดัก |
|---|---|---|---|
| ค้นข้อความ | Claude Code: เครื่องมือ **Grep** (ripgrep ในตัว) · shell: `git grep -n "applyDiscount"` · `grep -rn "/api/orders" --include=*.tsx .` | ทุกจุดที่ใช้ชื่อ/ค่า | ⚠️ เครื่องผู้สอน **ไม่มี `rg`** ใน PATH (ตรวจแล้ว) → อย่าเขียน `rg` ในพรอมต์ ให้ใช้ Grep ของ Claude หรือ `git grep` · ชื่อที่ประกอบแบบ dynamic (`"api/" + x`) grep ไม่เจอ |
| call graph คร่าว ๆ | พรอมต์: `จาก ฟังก์ชัน X ไล่ว่าใครเรียก (ขึ้น 2 ชั้น) และ X เรียกใคร ทำเป็นตาราง caller → callee พร้อมไฟล์:บรรทัด` | เส้นทางที่กระทบ | AI อาจเดา → ให้แนบผล grep ประกอบทุกแถว |
| git archaeology ✅ | `git log -p -- <file>` · `git log -L '/fetch\("\/api\/orders/,+3:<file>'` · `git blame -L 70,80 <file>` | ทำไมโค้ดเป็นแบบนี้ ใครเปลี่ยนเมื่อไร | ⚠️ ใน worktree นี้ บท 05/06 ยัง **untracked** (`??`) และประวัติของบท 03 มี commit เดียวข้อความ `1` (b7c3d79) → archaeology แทบไม่ได้อะไร · ถ้าจะสอนต้องเตรียม repo ที่มีประวัติให้ (เช่น ทำ commit จำลอง 5–10 ครั้งใน repo แยกของบท) |
| REA trace (black-box) ✅ | `trace-application-feature` direction `incoming` (M2) | module/asset ที่เรียก endpoint | เห็นแค่ฝั่ง client · coverage `partial` |
| เลือกเทสต์ที่ต้องรันซ้ำ ✅ (flag) | `npx playwright test --list -g "checkout"` · `--grep` · `--last-failed` · `--only-changed [ref]` | ชุดเทสต์ที่เกี่ยว | `--only-changed` ใช้ git (ไฟล์ที่เปลี่ยน = ไฟล์เทสต์) ไม่ได้ดูว่าโค้ดแอปไหนเปลี่ยน · สุดท้ายต้องรันเต็มก่อนส่ง |

**ตาราง "ไฟล์ที่แตะ × เทสต์ที่ต้องรันซ้ำ"** (ให้ agent ส่งก่อน diff ทุกครั้ง)

| ไฟล์ที่จะแตะ | เหตุผล (CR/BUG) | ใครเรียกใช้ (grep) | หน้าจอ/API ที่กระทบ | เทสต์ที่ต้องรันซ้ำ | ความเสี่ยง |
|---|---|---|---|---|---|
| `components/CheckoutForm.tsx` | CR-01 | `app/checkout/page.tsx` | /checkout · POST /api/orders | `checkout.spec.ts`, `orders.spec.ts` | กลาง |

---

## M7. Safe change loop: วงจรแก้อย่างปลอดภัย

| ขั้น | ทำอะไร | คำสั่ง (PowerShell) | หลักฐานที่ต้องได้ |
|---|---|---|---|
| ① ล็อก | characterization ของส่วนที่จะแตะ (M3) | `npx playwright test` | เขียว ก่อนแตะโค้ด |
| ② reproduce | เขียนเทสต์ที่ **แดง** ตามบั๊ก/CR | `npx playwright test tests/cr-01.spec.ts` | ภาพ/ข้อความ fail ที่ตรงอาการ |
| ③ impact | ตาราง M6 → คนอนุมัติ | Plan mode | ตารางในแชต/ไฟล์ |
| ④ แก้ให้เล็กที่สุด | แตะเฉพาะไฟล์ในตาราง | — | `git diff --stat` ตรงกับตาราง |
| ⑤ เขียว | เทสต์ ② ผ่าน | `npx playwright test tests/cr-01.spec.ts` | pass |
| ⑥ regression 3 browser | รันทั้งชุด (ชุดเดิม `e2e-legacy/` + ชุดใหม่) | `npx playwright test --project=chromium --project=firefox --project=webkit` | 0 failed (ยกเว้นที่อธิบายได้ใน CHANGE-REPORT) |
| ⑦ เทียบเวอร์ชัน | source: `git diff` · ของที่ build: REA `compare-application-versions` (input `{left, right}` เป็น Evidence 2 ก้อน 📖) | `git diff --stat` | รายการสิ่งที่เปลี่ยน = ตรงกับ CR เท่านั้น |
| ⑧ รายงาน | CHANGE-REPORT.md | — | ไฟล์ตามแม่แบบล่าง |

ข้อห้ามที่ต้องใส่ในพรอมต์ทุกครั้ง: **ห้ามแก้เทสต์เดิมให้ผ่าน · ห้ามรัน `-u` โดยไม่บอก · ถ้า regression แดงที่ไม่เกี่ยว ให้หยุดแล้วรายงาน**

**แม่แบบ CHANGE-REPORT.md**

```markdown
# CHANGE-REPORT · CR-01 <ชื่อ>
| หัวข้อ | ค่า |
|---|---|
| CR / BUG | CR-01 → FR-07, BR-12 |
| ไฟล์ที่แก้ | 2 ไฟล์ (+18 / −4) ตาม `git diff --stat` |
| เทสต์ใหม่ | TC-CR01-01..03 (แดงก่อนแก้ ✅ / เขียวหลังแก้ ✅) |
| regression | e2e-legacy 42/42 × 3 browser · baseline ที่เปลี่ยน: 1 (เหตุผล…) |
| พฤติกรรมที่เปลี่ยนโดยตั้งใจ | ยอดรวมนับครบทุกชิ้น (เดิม 450 → 570) |
| migration | 003_add_x.sql (up ✅ / down ✅ บนฐานที่มีข้อมูล) |
| ความเสี่ยงคงค้าง | … |
| rollback | revert commit + รัน 003_down.sql |
```

---

## M8. โครงการแบบภาครัฐ: Change Request · traceability · sign-off

| เอกสาร/กิจกรรม | มีอะไร | ใครทำ | agent ช่วยอะไร |
|---|---|---|---|
| **แบบฟอร์ม CR** | เลข CR · ผู้ขอ/หน่วยงาน · วันที่ · เหตุผล · ข้อความเดิม→ใหม่ · ผลกระทบ (ระบบ/ข้อมูล/ผู้ใช้/งบ/เวลา) · ระดับ (เล็ก/กลาง/ใหญ่) · ผู้อนุมัติ | ผู้ใช้/PM | ร่าง "ผลกระทบ" จาก impact analysis |
| **traceability matrix** | CR → FR/BR (ข้อกำหนดที่เปลี่ยน) → TC (เทสต์) → ผล | tester | สร้างตาราง + หาช่องว่าง (FR ไม่มี TC) |
| **regression scope** | เทสต์ที่ต้องรันซ้ำ + เหตุผล (จาก M6) + เทสต์ที่ไม่รันพร้อมเหตุผล | tester | เสนอ scope จากตาราง M6 |
| **UAT / sign-off** | รายการตรวจรับ · ผล · ลายเซ็น/วันที่ · ข้อสังเกต | ผู้ใช้ | ร่างเอกสาร ไม่ใช่ผู้เซ็น |
| **DB migration ย้อนได้** | `db/migrations/NNN_<ชื่อ>.sql` (up) + `NNN_<ชื่อ>.down.sql` · วิธีรันกับฐานที่มีข้อมูล · ทดสอบ up→down→up | dev | เขียน + ทดสอบบน DB สำเนา |

```markdown
| CR | FR/BR ที่กระทบ | TC | ประเภท | ผล (รอบ 1) | ผล (หลังแก้) |
|---|---|---|---|---|---|
| CR-01 | BR-12 (ส่วนลดกลุ่ม) | TC-CR01-01 | ใหม่ | ❌ (reproduce) | ✅ |
| CR-01 | BR-12 | TC-PRICE-04 | regression เดิม | ✅ | ✅ |
```

กติกา migration (ตามการตัดสินใจ D1 ของบท 06): **ไม่แก้ `db/init/` ตรง ๆ** เพราะระบบจริงมีข้อมูลอยู่แล้ว init ไม่รันซ้ำ · migration ต้อง idempotent ถ้าทำได้ (`ADD COLUMN IF NOT EXISTS`) · คอลัมน์ใหม่ต้องมี default/backfill สำหรับแถวเก่า · down ต้องไม่ทำข้อมูลหาย (ถ้าหายต้องเขียนไว้ใน CR ชัด ๆ)

กับดัก: เอกสารเก่า (SPEC เดิม) ไม่ตรงโค้ด = เรื่องปกติของ legacy → ให้ทำตาราง "เอกสารบอก ≠ ระบบทำ" แล้วถามเจ้าของ CR **ห้ามให้ agent ตัดสินเองว่าฝั่งไหนถูก**

---

## M9. ตารางเทียบเทคนิค

| เทคนิค | ต้องมี source? | เวลา (โดยประมาณ) | จับอะไรได้ | ข้อจำกัด |
|---|---|---|---|---|
| CLAUDE.md + CODEBASE-MAP | ✅ | 15–30 นาที | ลด agent แก้ผิดที่/แตะของต้องห้าม | เก่าเร็ว · AI อาจเดาหน้าที่ไฟล์ |
| permissions deny `Edit(...)` | ✅ | 2 นาที | กัน Edit tool แตะไฟล์ต้องห้าม (ตรวจแล้ว) | ไม่กัน Bash · `Write(...)` ใช้ไม่ได้ |
| Plan mode / Explore | ✅ | 5–10 นาที | แผนผิดก่อนลงมือ | แผนดี ≠ โค้ดถูก |
| REA static + trace | ❌ (ใช้ build) | ~10 วินาทีต่อ trace (รันจริง) + เวลาอ่านผล | endpoint/module/storage ที่ใช้จริงใน bundle | client-side เท่านั้น · minify · coverage partial · ทดสอบบน Linux/Docker |
| HAR record/replay | ❌ | 5 นาที | API inventory · mock คงที่ | ผูก host:port · มีข้อมูลลับ · ไม่ทดสอบ backend |
| codegen / trace / UI mode | ❌ | 5–15 นาที | flow จริง, locator, network ต่อ action | locator เปราะ · GUI ทำใน agent ไม่ได้ (ยกเว้น trace CLI) |
| aria snapshot | ❌ | เร็ว (ms) | โครงหน้าหาย/เพิ่ม (ถ้าใส่ `/children: equal`) | **ไม่ล็อกตัวเลข** (regex) · list จับแบบบางส่วน |
| screenshot | ❌ | เร็ว แต่ baseline ต่อ browser×OS | layout/สีเปลี่ยน | tolerance กลืนตัวเลขเล็ก (44 px ไม่ถูกจับที่ 1%) · font ต่างเครื่อง |
| API JSON snapshot | ❌ | เร็ว (24 ms) | ข้อมูล/รูปแบบ response | ฟิลด์ที่เปลี่ยนเอง (เวลา/id) ต้องตัดก่อน |
| `toHaveText` ค่าเงิน + `test.fail` | ❌ | เร็ว | กติกาธุรกิจ, บั๊กที่รู้แล้ว ("Expected to fail, but passed") | ต้องรู้ค่าที่จะล็อก |
| grep / git grep | ✅ | นาที | ทุกจุดที่อ้างชื่อ | ชื่อ dynamic ไม่เจอ |
| git log -L / blame | ✅ + ประวัติ | นาที | เหตุผลเดิม, ใครแก้ | repo ที่ไม่มีประวัติ (บท 05/06 ตอนนี้) ไม่ได้อะไร |
| Safe change loop + CHANGE-REPORT | ✅ | 30–90 นาที/CR | regression ข้าม browser, การเปลี่ยนเกินขอบเขต | ช้ากว่าการแก้ตรง ๆ (ตั้งใจ) |
| CR + traceability + migration | ✅ | 30+ นาที/CR | ข้อกำหนดที่ไม่มีเทสต์ · migration ที่ย้อนไม่ได้ | งานเอกสารเยอะ |

---

## ข้อเสนอการวาง LAB

| บท | LAB | เทคนิค | ผลงาน |
|---|---|---|---|
| 05 | อธิบาย repo | M1 (`/init` + CODEBASE-MAP + Explore) | `CLAUDE.md`, `CODEBASE-MAP.md` |
| 05 | black-box vs white-box | M2 (REA trace `incoming` + grep) | ตาราง triangulate endpoint ↔ ไฟล์ |
| 05 | ล็อกพฤติกรรม | M3 + M4 | `e2e-char/` (aria + API JSON + `test.fail` known bug) + HAR |
| 05 | แก้บั๊กแรก | M6 + M7 | CHANGE-REPORT.md |
| 06 | รับ CR | M8 + M1 (deny `Edit(e2e-legacy/**)`, `Edit(db/init/**)`) | CR form + impact table |
| 06 | ทำ CR ที่แตะ DB | M7 + M8 migration | `db/migrations/NNN_*.sql` + down + regression 3 browser |
| 06 | EXAM | ผสม: ≥60% แก้ repo เดิม | ตรวจด้วย traceability + CHANGE-REPORT |

---

## บันทึกการตรวจสอบ (ทำอะไรจริง ได้อะไร)

| สิ่งที่ตรวจ | วิธี | ผล |
|---|---|---|
| ติดตั้ง | `npm i -D @playwright/test@1.63.0` ใน `C:/t/work/a3` | `Version 1.63.0` · browser chromium-1243 / firefox-1543 / webkit-2359 มีอยู่แล้ว |
| ชื่อ API | grep `node_modules/playwright/types/test.d.ts` + `playwright-core/types/types.d.ts` | มี `toMatchAriaSnapshot` (inline + `{name}`, ทั้ง locator และ page) · `toHaveScreenshot` · `toMatchSnapshot` · `toBeOK` · `test.fail()` / `test.fail(cond, desc)` · `recordHar {path, content, mode, urlFilter, omitContent(deprecated)}` · `routeFromHAR {notFound, update, updateContent, updateMode, url}` · `page.ariaSnapshot()` |
| CLI | `npx playwright --help`, `codegen --help`, `show-trace --help`, `trace --help`, `test --help`, `init-agents --help` | ตามที่อ้างในหัวข้อ M3–M6 |
| พอร์ต | ตั้งใจใช้ 3053 | ❌ `listen EACCES 0.0.0.0:3053` เพราะ Windows จองช่วง **2970–3069** (`netsh interface ipv4 show excludedportrange protocol=tcp`; ช่วงนี้ครอบ 3000 ด้วย) → ใช้ `server.listen(0)` ใน `globalSetup` ให้ OS เลือกพอร์ตว่าง · ⚠️ ผู้สอนควรเช็กว่าเครื่องผู้เรียนจองช่วงเดียวกันไหม (ถ้าจอง พอร์ต 3000 ของบท 03–06 จะเปิดไม่ได้) |
| เทสต์ | 10 ข้อ × 3 browser | 30 passed (7.2 s) · `FIXED=1`: 6 failed ตามคาด |
| permission deny | `claude -p … --permission-mode acceptEdits` + settings `deny` | `Edit(locked/**)` กันได้ · `Write(locked/**)` ถูกเตือนว่าใช้ไม่ได้ |
| REA trace | `rea-lab:6.4.0 trace-application-feature` บน Evidence ของ PawPantry (ทั้ง Git Bash และ PowerShell) | exit 0 · ~10 วินาที · ผลตามตาราง M2 · PowerShell `>` ใส่ BOM → ใช้ `cmd /c` · REA `compare-application-versions` ตรวจแค่ `--help` (ไม่ได้รัน เพราะยังไม่มี build เวอร์ชันที่ 2) |
| ไม่ได้รัน | `/init`, codegen, UI mode, show-trace GUI | ต้องโต้ตอบ/เปิดหน้าต่าง → ตรวจจาก help/docs เท่านั้น (📖) |

---

## แหล่งอ้างอิง

- Playwright aria snapshots: https://playwright.dev/docs/aria-snapshots
- Playwright visual comparisons: https://playwright.dev/docs/test-snapshots · `toMatchSnapshot`: https://playwright.dev/docs/api/class-snapshotassertions
- Playwright HAR mocking: https://playwright.dev/docs/mock#mocking-with-har-files · `routeFromHAR`: https://playwright.dev/docs/api/class-page#page-route-from-har · `recordHar`: https://playwright.dev/docs/api/class-browser#browser-new-context-option-record-har
- Playwright annotations (`test.fail`): https://playwright.dev/docs/test-annotations
- Playwright CLI (`-u`, `--only-changed`, `--last-failed`): https://playwright.dev/docs/test-cli
- Playwright codegen: https://playwright.dev/docs/codegen · trace viewer: https://playwright.dev/docs/trace-viewer · UI mode: https://playwright.dev/docs/test-ui-mode · global setup: https://playwright.dev/docs/test-global-setup-teardown
- Claude Code memory / CLAUDE.md / `@` imports: https://code.claude.com/docs/en/memory
- Claude Code permissions (`Edit(path)` rules): https://code.claude.com/docs/en/iam · settings: https://code.claude.com/docs/en/settings
- Claude Code subagents (Explore): https://code.claude.com/docs/en/sub-agents · Plan mode / common workflows: https://code.claude.com/docs/en/common-workflows
- REA: https://github.com/morluto/rea · docs: https://github.com/morluto/rea/tree/main/docs (`cli.md`, `javascript-application-workflows.md`, `web-network-captures.md`) · skill: `.agents/skills/reverse-engineer-anything/SKILL.md`
- Michael Feathers, *Working Effectively with Legacy Code* (2004) · Characterization testing: https://michaelfeathers.silvrback.com/characterization-testing
- HAR 1.2 spec: http://www.softwareishard.com/blog/har-12-spec/
