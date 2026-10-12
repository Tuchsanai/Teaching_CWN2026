# PREP · เตรียมโฟลเดอร์ตั้งต้นบท 06 (งานของ agent "PREP" แยกจาก RUNNER)

> เขียน 12 ต.ค. 2026 (งาน B2F · แก้ H1 ของ `REVIEW-PLAN-V1.md`) · แทน `LESSON-PLAN.md` §8.2 เดิม (ไฟล์นี้เป็นตัวจริง)
> ผู้ทำ = agent PREP **1 ตัว** ที่ orchestrator อนุญาตให้แก้ `web/` `db/` `e2e-legacy/` ของบท 06 · **ไม่ใช่ runner** (runner ห้ามเห็น `_solution/`)
> ผลลัพธ์: โฟลเดอร์บทพร้อมแจก + `_solution/_design/PREP-LOG.md` + `C:/t/work/b2prep/MANIFEST.sha256` (ให้ RUNNER ตรวจโดยไม่ต้องเปิด `_solution/`)

ตัวแปรในไฟล์นี้: `CH` = `C:/Users/oishi/Documents/GitHub/CWN/Teaching/00_tester/.claude/worktrees/agent-orchestrator-rea-testing-2872ad/00_tester/06_sabai-spa-legacy-change-request` · `CH05` = `…/00_tester/05_rea-reverse-engineer-legacy-petshop` · `DES` = `$CH/_solution/_design` · `VER` = `C:/t/work/b2prep/verify` (สำเนาสำหรับรันตรวจ)

---

## 0. กติกาก่อนเริ่ม (บังคับ)

| # | กติกา |
|---|---|
| 0.1 | อ่าน `C:/t/orch/BRIEF.md` (D1–D9) ก่อน · ห้าม git ที่เปลี่ยนสถานะ · ห้ามแตะ `multi-account-devtool` / volume `ai-accounts` / container `sabai-*` ของบท 04 |
| 0.2 | ได้รับยืนยันจาก orchestrator ว่า agent อื่นที่ทำงานใน `web/ db/ e2e-legacy/ img/` **จบแล้ว** · ถ้ายังไม่ได้ยืนยัน หยุด |
| 0.3 | แก้ไฟล์ **เฉพาะ** ที่อยู่ในตาราง P1–P8 · ไม่แตะ `img/` `db/init/*` `web/lib/server/*` `web/ASSETS.md` `web/private/` (P11) |
| 0.4 | ห้าม `npm install` / `docker compose` / Playwright ในโฟลเดอร์บทจริง (จะเกิด `node_modules` `test-report`) → รันตรวจทั้งหมดใน `VER` (ข้อ V) |
| 0.5 | พอร์ต: orchestrator ให้ `WEB_PORT` และ `DB_PORT` ในช่วง 4100–4199 (D6) · ค่าแนะนำ `WEB_PORT=4140` `DB_PORT=4141` · ห้ามใช้ 4000/5433 ตอนตรวจ (กันชน runner) |
| 0.6 | ก่อนเปิด container: `docker ps -a --filter name=sabai06` และ `docker volume ls --filter name=sabai06` และ `docker network ls --filter name=sabai06` ต้อง**ว่าง** · ถ้าไม่ว่าง = มีงานอื่นใช้ชื่อเดียวกัน → หยุดถาม orchestrator (ห้ามหยุด/ลบของคนอื่น) · จดผลลง PREP-LOG |
| 0.7 | ทุกไฟล์ที่เขียน = UTF-8 **ไม่มี BOM** · line ending LF (ใช้เครื่องมือ Write/Edit ไม่ใช้ `>` ของ PowerShell 5.1) |
| 0.8 | ทุกขั้นจดใน PREP-LOG: คำสั่ง · ผลจริง · เวลา · ถ้าไม่ตรง "ผลที่ต้องได้" ให้หยุดขั้นนั้น เขียนสาเหตุ ห้ามแต่งผล |

## 1. สถานะก่อนเริ่ม (ตรวจโดย B2F อ่านอย่างเดียว · 12 ต.ค. 2026)

| P | สถานะ | หลักฐาน |
|---|---|---|
| P1 ถอด BUG_MODE | ❌ ยังไม่ทำ | `web/lib/flags.ts` มีอยู่ · grep เจอ 12 ไฟล์ (รวม SPEC.md, compose.yaml) |
| P2 check-rules ค่าเริ่ม 4000 | ✅ ทำแล้ว → **ตรวจซ้ำอย่างเดียว** | บรรทัด 2, 3, 8 เป็น `http://localhost:4000` |
| P3 ชื่อ `sabai06-*` | ❌ | compose ยังเป็น `sabai-web` `sabai-db` `sabai-net` · พอร์ต `"4000:3000"` ตายตัว · volume `sabai06-pgdata` ✅ แล้ว |
| P4 SPEC.md | ❌ | ยังมีบล็อกโหมดบั๊ก แถว `BUG_MODE` และ `data-bug-mode` |
| P5 e2e-legacy | ✅ ทำแล้ว → **ตรวจซ้ำอย่างเดียว** | มี `test.fail` 3 ข้อ (TC-GC-04 · TC-SEC-04 · TC-TRN-03) · `BASE_URL` 4000 · `README-LEGACY.md` ไม่มี `sabai-net` แล้ว (บอก "ตามชื่อใน db/compose.yaml") |
| P6 tools/ | ❌ | ไม่มีโฟลเดอร์ |
| P7 CHANGE-REQUESTS/ | ❌ | ไม่มีโฟลเดอร์ |
| P8 EXAM.md | ❌ | ไม่มีไฟล์ |

> ถ้าตอนเริ่มงานสถานะต่างจากตารางนี้ (เช่น agent อื่นทำ P1 ไปแล้ว) ให้ทำข้อ "ตรวจ" ของ P นั้นแทนการแก้ แล้วจดว่า "พบว่าทำแล้ว"

---

## 2. รายการเตรียม P1–P11 (ทำตามลำดับ)

> คำสั่งในเซลล์ตารางเขียน `\|` แทน `|` (ข้อจำกัดของตาราง markdown) · ตอนรันให้ใช้ `|` · คำสั่ง grep/find/sha256sum ทั้งหมดรันใน Git Bash ที่ `$CH`

### P1 · ถอด `BUG_MODE` / `flags.ts` (ตาม CR-DESIGN §2.3 · ค่าเท่ากับ `BUG_MODE=0` เดิมทุกกรณี)

1. **สร้าง** `web/lib/config.ts`:

```ts
// ค่าตั้งของระบบที่อ่านจาก env จุดเดียว
export const config = {
  /** เปิด /api/test/*, นาฬิกาทดสอบ, บัญชีทดสอบหน้า login, ปุ่มรีเซ็ต /admin */
  get allowTestReset(): boolean {
    return (process.env.ALLOW_TEST_RESET ?? "1") === "1";
  },
};
```

2. **ลบ** `web/lib/flags.ts`
3. แก้แบบ "ข้อความเดิม → ข้อความใหม่" (ตรงตัว · ทุกข้อต้องเจอข้อความเดิม 1 ครั้งพอดี ถ้าไม่เจอให้หยุด):

| ไฟล์ | ข้อความเดิม | ข้อความใหม่ |
|---|---|---|
| `web/lib/rules/slots.ts` | `import { flags } from "../flags.ts";⏎` | (ลบทั้งบรรทัด) |
| `web/lib/rules/slots.ts` | `return startMin + durationMin <= CLOSE_MIN - flags.closingBufferMin;` | `return startMin + durationMin <= CLOSE_MIN;` |
| `web/lib/rules/points.ts` | `import { flags } from "../flags.ts";⏎` | (ลบทั้งบรรทัด) |
| `web/lib/rules/points.ts` | `const net = flags.loyaltyBasis === "net" ? b.gross - b.discountAmount - b.pointsDiscount : b.gross - b.pointsDiscount;⏎  return Math.max(0, net - b.giftcardPaid);` | `return Math.max(0, b.gross - b.discountAmount - b.pointsDiscount - b.giftcardPaid);` |
| `web/lib/rules/pricing.ts` | `import { flags } from "../flags.ts";⏎` | (ลบทั้งบรรทัด) |
| `web/lib/rules/pricing.ts` | บล็อก 16 บรรทัดตั้งแต่ `let running = gross;` ถึง `const subtotal = running;` (ดูด้านล่าง) | บล็อกใหม่ 6 บรรทัด (ดูด้านล่าง) |
| `web/app/layout.tsx` | `import { flags } from "@/lib/flags.ts";⏎` | (ลบทั้งบรรทัด) |
| `web/app/layout.tsx` | `<html lang={lang} data-ready="false" data-bug-mode={flags.bugMode}>` | `<html lang={lang} data-ready="false">` |
| `web/lib/clock.ts` | `import { flags } from "./flags.ts";` | `import { config } from "./config.ts";` |
| `web/lib/clock.ts` | `if (flags.allowTestReset) {` | `if (config.allowTestReset) {` |
| `web/app/admin/page.tsx` | `import { flags } from "@/lib/flags.ts";` | `import { config } from "@/lib/config.ts";` |
| `web/app/admin/page.tsx` | `allowReset={flags.allowTestReset}` | `allowReset={config.allowTestReset}` |
| `web/app/login/page.tsx` | `import { flags } from "@/lib/flags.ts";` | `import { config } from "@/lib/config.ts";` |
| `web/app/login/page.tsx` | `testAccounts={flags.allowTestReset ? TEST_ACCOUNTS : []}` | `testAccounts={config.allowTestReset ? TEST_ACCOUNTS : []}` |
| `web/app/api/test/reset/route.ts` | `import { flags } from "@/lib/flags.ts";` | `import { config } from "@/lib/config.ts";` |
| `web/app/api/test/reset/route.ts` | `if (!flags.allowTestReset)` | `if (!config.allowTestReset)` |
| `web/app/api/test/today/route.ts` | `import { flags } from "@/lib/flags.ts";` | `import { config } from "@/lib/config.ts";` |
| `web/app/api/test/today/route.ts` | `if (!flags.allowTestReset)` | `if (!config.allowTestReset)` |
| `web/scripts/check-rules.mjs` | บล็อก 7 บรรทัด (ดูด้านล่าง) | บล็อกใหม่ 3 บรรทัด |

`web/lib/rules/pricing.ts` เดิม (บรรทัด ~68–83):

```ts
  let running = gross;
  let discountAmount = 0;
  let pointsRedeemed = 0;
  let pointsDiscount = 0;
  for (const step of flags.priceSteps) {
    if (step === "percent") {
      discountAmount = percentOf(running, best.pct);
      running -= discountAmount;
    } else {
      const r = redeemPoints(input.type === "course" ? 0 : input.redeemBlocks, input.points, running);
      pointsRedeemed = r.blocks * 100;
      pointsDiscount = r.discount;
      running -= pointsDiscount;
    }
  }
  const subtotal = running;
```

ใหม่:

```ts
  // ② ส่วนลด % → ③ หักแลกแต้ม
  const discountAmount = percentOf(gross, best.pct);
  const r = redeemPoints(input.type === "course" ? 0 : input.redeemBlocks, input.points, gross - discountAmount);
  const pointsRedeemed = r.blocks * 100;
  const pointsDiscount = r.discount;
  const subtotal = gross - discountAmount - pointsDiscount;
```

`web/scripts/check-rules.mjs` เดิม (บรรทัด ~640–646):

```js
  // ให้ unit test ใช้โหมดเดียวกับเว็บที่กำลังตรวจ
  const html = await fetch(`${BASE}/`).then((r) => r.text());
  const mode = html.match(/data-bug-mode="(\d)"/)?.[1] ?? "0";
  process.env.BUG_MODE = mode;
  R = await import("../lib/rules/index.ts");

  console.log(`ตรวจกฎร้าน ${BASE} (BUG_MODE=${mode}) · ${cases.length} เคส\n`);
```

ใหม่:

```js
  R = await import("../lib/rules/index.ts");

  console.log(`ตรวจกฎร้าน ${BASE} · ${cases.length} เคส\n`);
```

(แถว `BUG_MODE` ใน `web/compose.yaml` ถูกลบใน P3 · ใน `web/SPEC.md` ใน P4)

**ตรวจ P1** (ทำหลัง P4 · m1-ก): Git Bash ที่ `$CH`
`grep -rniE "bug_mode|bug-mode|bugmode|flags" web --exclude-dir=node_modules --exclude-dir=.next` → **ไม่มีผลลัพธ์** (exit 1) · ผลรันอยู่ใน V3–V4 (build ผ่าน + check-rules 90/90)

### P2 · `web/scripts/check-rules.mjs` ค่าเริ่ม 4000 — **ตรวจอย่างเดียว**

`grep -n "localhost:4000" web/scripts/check-rules.mjs` → ต้องได้บรรทัด 2, 3, 8 · `grep -c "localhost:3000" web/scripts/check-rules.mjs` → `0` · คอมเมนต์อ้าง TEST-DATA.md/REQUIREMENTS.md ที่ไม่มีแล้ว **คงไว้** (เอกสารเก่าสมจริง)

### P3 · ชื่อ `sabai06-*` (อนุมัติแล้ว BRIEF D7–D8) + พอร์ตปรับได้

เขียนทับ `web/compose.yaml` ทั้งไฟล์:

```yaml
name: sabai06-web

services:
  sabai06-web:
    build:
      context: .
      dockerfile: Dockerfile
      additional_contexts:
        dbinit: ../db/init
    image: sabai06-web:latest
    container_name: sabai06-web
    restart: unless-stopped
    ports:
      - "${WEB_PORT:-4000}:3000"
    environment:
      DATABASE_URL: postgres://sabai:sabai@sabai06-db:5432/sabai
      HOSTNAME: 0.0.0.0
      TZ: Asia/Bangkok
      ALLOW_TEST_RESET: ${ALLOW_TEST_RESET:-1}
      SESSION_SECRET: ${SESSION_SECRET:-sabai-jai-local-session-secret-2026}
      TODAY: ${TODAY:-}
    networks:
      - sabai06-net
    healthcheck:
      test: ["CMD", "node", "-e", "fetch('http://127.0.0.1:3000/api/health').then(r=>r.json()).then(j=>process.exit(j.db?0:1)).catch(()=>process.exit(1))"]
      interval: 10s
      timeout: 5s
      retries: 12
      start_period: 15s

networks:
  sabai06-net:
    external: true
```

เขียนทับ `db/compose.yaml` ทั้งไฟล์:

```yaml
name: sabai06-db

services:
  sabai06-db:
    image: postgres:16-alpine
    container_name: sabai06-db
    restart: unless-stopped
    environment:
      POSTGRES_USER: sabai
      POSTGRES_PASSWORD: sabai
      POSTGRES_DB: sabai
      TZ: Asia/Bangkok
      PGTZ: Asia/Bangkok
    ports:
      - "${DB_PORT:-5433}:5432"
    volumes:
      - sabai06-pgdata:/var/lib/postgresql/data
      - ./init:/docker-entrypoint-initdb.d:ro
    networks:
      - sabai06-net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U sabai -d sabai"]
      interval: 5s
      timeout: 5s
      retries: 20

volumes:
  sabai06-pgdata:
    name: sabai06-pgdata

networks:
  sabai06-net:
    external: true
```

**ตรวจ P3:** `grep -rnE "sabai-(web|db|net|pgdata)" web/compose.yaml db/compose.yaml` → ไม่มีผล · `grep -c "sabai06-" web/compose.yaml` → `7` · `grep -c "sabai06-" db/compose.yaml` → `8` · `grep -c "BUG_MODE" web/compose.yaml` → `0` · host ใน `DATABASE_URL` = `sabai06-db` = `container_name` ของ db (m1-จ)

### P4 · `web/SPEC.md` = เอกสารเก่า ฉบับ 1.0 (ลบเฉพาะส่วนเฉลย · T4)

| # | ทำ |
|---|---|
| 1 | หลังบรรทัดแรก `# SPEC · เว็บ สบายใจ สปา · Sabai Jai Wellness Spa` แทรก 2 บรรทัด: บรรทัดว่าง + `> เอกสารส่งมอบ ฉบับ 1.0 · ก.ย. 2569 · บริษัท โค้ดไว จำกัด` |
| 2 | ลบ 4 บรรทัดนี้ (รวมบรรทัดว่างที่ตามมา 1 บรรทัด): `# เปิดโหมดบั๊ก / ปิด` · `$env:BUG_MODE = "1"; docker compose -f web/compose.yaml up -d --force-recreate` · `$env:BUG_MODE = "0"; docker compose -f web/compose.yaml up -d --force-recreate` · (บรรทัดว่าง) |
| 3 | ลบแถวตาราง env ที่ขึ้นต้น `` | `BUG_MODE` | web | `` ทั้งแถว (แถวเดียวที่อ้าง `BUGS.md` และ `lib/flags.ts`) |
| 4 | ในบรรทัด "ทุกหน้ามี header …" แทน `` `<html data-ready="true|false" data-bug-mode="0|1" lang="th|en|zh">` `` ด้วย `` `<html data-ready="true|false" lang="th|en|zh">` `` |
| 5 | **ไม่แก้ส่วนอื่น:** พอร์ต 3000 · `sabai-net` `sabai-db` `sabai-web` · "Next.js 15" · คำอธิบาย `TODAY` · S2–S9 ทั้งหมดคงไว้ (= SPEC-GAPS ที่ LAB 3 ต้องเจอ) |

**ตรวจ P4:** `grep -niE "bug|flags" web/SPEC.md` → ไม่มีผล · `grep -c "localhost:3000" web/SPEC.md` ≥ 1 (ยังเป็นเอกสารเก่า) · `head -3 web/SPEC.md` เห็นบรรทัด "เอกสารส่งมอบ ฉบับ 1.0"

### P5 · `e2e-legacy/` — **ตรวจอย่างเดียว** (ทำไว้แล้วตาม LEGACY-TESTSUITES §4.2)

| ตรวจ (Git Bash ที่ `$CH`) | ผลที่ต้องได้ |
|---|---|
| `grep -rn "test.fail(true" e2e-legacy/tests \| wc -l` | `3` (giftcard · security.api · transport) |
| `grep -n '"name"' e2e-legacy/package.json` | `"sabai-legacy-e2e"` |
| `grep -rn "localhost:4000" e2e-legacy/playwright.config.ts e2e-legacy/global-setup.ts \| wc -l` | ≥ 2 |
| `grep -rniE "bug-mode\|bugmode\|meta\.json\|sabai-net" e2e-legacy --exclude-dir=node_modules` | ไม่มีผล (P5b: `README-LEGACY.md` ไม่อ้างชื่อ network ตายตัวแล้ว · ถ้ายังเจอ `sabai-net` ให้แก้เป็น `sabai06-net` แล้วจด) |
| `ls e2e-legacy` | มี `.gitignore` `README-LEGACY.md` `fixtures/selfie-test.png` `global-setup.ts` `package.json` `package-lock.json` `plan-cases.json` `playwright.config.ts` `tests/` (12 spec + `fixtures.ts`) `tsconfig.json` · **ไม่มี** `node_modules/` `test-report/` `scripts/` `triage.json` |

`README-LEGACY.md` ตาราง "ผลรันล่าสุด" (41 passed · 1 failed / 113 passed · 1 failed) = คำอ้างของผู้รับเหมา **ไม่แก้** · V5 จะบอกว่าตรงไหม (จดใน PREP-LOG เท่านั้น)

### P6 · ใหม่ `tools/` (5 ไฟล์ + `.gitignore`)

| ไฟล์ | ที่มา | แก้อะไร |
|---|---|---|
| `tools/rea.ps1` | คัดลอก `$CH05/_solution/_design/rea-probe/rea.ps1` | แทนบล็อก "ตัวอย่าง (รันจากโฟลเดอร์บท 05):" 5 บรรทัด ด้วยบล็อกข้างล่าง · ส่วนอื่นไม่แตะ (มี `-Network` อยู่แล้ว) |
| `tools/rea-tools.mjs` | คัดลอก `$DES/rea-probe/rea-tools.mjs` | เพิ่มคำสั่ง `shot` (m5 · โค้ดข้างล่าง) + บรรทัดวิธีใช้ในหัวไฟล์ · FIX6T เพิ่ม `ids` `summary` `scenario-sum` `pages` (ดู `FIX6T.md`) |
| `tools/record-har.mjs` | คัดลอก `$DES/rea-probe/record-har.mjs` | `http://127.0.0.1:3000` → `http://127.0.0.1:4000` **2 จุด** (คอมเมนต์บรรทัด 2 + ค่า `BASE`) · `sabai-journeys.har` คงเดิม |
| `tools/scenario-book-quote.json` | คัดลอก `$DES/rea-probe/scenario-book-quote.json` | `"url": "http://host.docker.internal:3000/services"` → `"url": "http://sabai06-web:3000/services"` (D7: REA อยู่ใน network `sabai06-net` · พอร์ตใน container = 3000 เสมอ ไม่ขึ้นกับ `WEB_PORT`) |
| `tools/package.json` | ใหม่ | `{"name":"sabai06-tools","private":true,"type":"module","devDependencies":{"@playwright/test":"1.63.0"}}` + ขึ้นบรรทัดใหม่ท้ายไฟล์ |
| `tools/.gitignore` | ใหม่ | `node_modules/` + `package-lock.json` (FIX6T: npm install สร้าง lock แล้วโผล่ใน git status) |

บล็อกตัวอย่างใหม่ใน `tools/rea.ps1` (เรียกผ่าน `-ExecutionPolicy Bypass` ตาม D9 · M8):

```text
ตัวอย่าง (รันจากโฟลเดอร์บท 06 ใน PowerShell · ไม่ต้องแก้ execution policy ของเครื่อง):
  powershell -NoProfile -ExecutionPolicy Bypass -File tools\rea.ps1 doctor
  powershell -NoProfile -ExecutionPolicy Bypass -File tools\rea.ps1 -Out rea-out\static-v1.json analyze-javascript-application /work/rea-out/v1/.next/static --json
  powershell -NoProfile -ExecutionPolicy Bypass -File tools\rea.ps1 -Out rea-out\har-api.json inspect-web-network-capture /work/rea-out/journeys.har har --record 3 --json
  powershell -NoProfile -ExecutionPolicy Bypass -File tools\rea.ps1 -Network sabai06-net -Out rea-out\scenario.json capture-browser-scenario /work/tools/scenario-book-quote.json --json
```

โค้ด `shot` (วางก่อน `default:` ใน `switch` ของ `tools/rea-tools.mjs`):

```js
  case "shot": {
    // ภาพ PNG (base64) ตัวสุดท้ายใน Evidence ของ capture-browser-scenario → ไฟล์ .png
    let last = null;
    const walk = (v) => {
      if (typeof v === "string") {
        const m = v.match(/^(?:data:image\/png;base64,)?(iVBORw0KGgo[A-Za-z0-9+/=]+)$/);
        if (m) last = m[1];
      } else if (v && typeof v === "object") for (const x of Object.values(v)) walk(x);
    };
    walk(load(a[0]));
    if (!last) { console.error("ไม่พบภาพ PNG ใน Evidence นี้"); process.exit(1); }
    const buf = Buffer.from(last, "base64");
    writeFileSync(a[1], buf);
    console.log(`เขียน ${a[1]} (${buf.length} bytes)`);
    break;
  }
```

บรรทัดวิธีใช้ (ต่อท้ายบล็อกคอมเมนต์หัวไฟล์ ก่อน `import`):
`//   node rea-tools.mjs shot        <scenario-out.json> <out.png>                  ดึงภาพหน้าจอสุดท้ายที่ REA ถ่ายใน capture-browser-scenario`

> ถ้า V7 พบว่า Evidence ไม่ได้เก็บภาพเป็น base64 (shot ตอบ "ไม่พบภาพ") ให้หาโครงจริงด้วย `node -e` นับ key ที่มีคำว่า screenshot แล้วแก้ `shot` ให้ตรง · จดโครงที่พบใน PREP-LOG · ถ้าแก้ไม่ได้ ให้แจ้ง orchestrator (พรอมต์ LAB 2 ข้อ 3 จะต้องตัดขั้นภาพ)

**ตรวจ P6:** `ls -a tools` = 6 รายการ · `grep -c "127.0.0.1:4000" tools/record-har.mjs` = `2` · `grep -c "sabai06-web:3000" tools/scenario-book-quote.json` = `1` · `grep -c "host.docker.internal" tools/scenario-book-quote.json` = `0` · `node --check tools/rea-tools.mjs` exit 0 · `head -c 3 tools/rea.ps1 | od -An -tx1` ไม่ใช่ `ef bb bf` (ไม่มี BOM)

### P7 · ใหม่ `CHANGE-REQUESTS/` (7 ไฟล์ + `answers/` 5 ไฟล์ = 12)

ที่มา: `$DES/CHANGE-REQUESTS-DRAFT.md` · แต่ละไฟล์ = เนื้อในกรอบ `~~~markdown` … `~~~` ของหัวข้อนั้น **ตรงตัว** (ไม่รวมบรรทัด `~~~`) · ห้ามคัดตาราง "เฉลยคำอ้าง (ผู้สอน)" และข้อความนอกกรอบ

| ไฟล์ | หัวข้อในไฟล์ร่าง |
|---|---|
| `CHANGE-REQUESTS/00-HANDOVER-MEMO.md` | §1 |
| `CHANGE-REQUESTS/REGISTER.md` | §2 |
| `CHANGE-REQUESTS/CR-01.md` … `CR-05.md` | §3.1–§3.5 |
| `CHANGE-REQUESTS/answers/CR-01-ANSWERS.md` … `CR-05-ANSWERS.md` | §4.1–§4.5 |

**ตรวจ P7** (= เช็กลิสต์ §5 ของไฟล์ร่าง ฉบับแก้ m7):
- `find CHANGE-REQUESTS -type f | wc -l` → `12`
- `grep -rnE "room_id|TABLES|testmode|init ไม่รันซ้ำ|docker-entrypoint-initdb|รันเฉพาะตอน volume ว่าง|self-overlap|advisory|บั๊ก|BUG|flags" CHANGE-REQUESTS` → ไม่มีผล
- `grep -c "sabai06-net" CHANGE-REQUESTS/00-HANDOVER-MEMO.md` → `1`
- คุณสมชาย `081-000-0003` และคุณนิดาใน CR-01/CR-03 ตรงกับ `db/init/02-seed.sql`: `grep -n "0810000003\|081-000-0003\|นิดา" db/init/02-seed.sql` ต้องเจอ
- ไม่มี BOM: `for f in $(find CHANGE-REQUESTS -type f); do head -c 3 "$f" | od -An -tx1; done | grep -c "ef bb bf"` → `0`

### P8 · ใหม่ `EXAM.md`

เนื้อในกรอบ `~~~markdown` ของ **ภาค 1** ใน `$DES/EXAM-DRAFT.md` ตรงตัว (ไม่รวมภาค 2–3)
**ตรวจ P8:** `grep -nE "\bM[1-9]\b|TABLES|room_id|EX-B[0-9]|NOT_STARTED|therapist_leave" EXAM.md` → ไม่มีผล · `grep -c "sabai06x-" EXAM.md` ≥ 1 (M11) · `grep -c "sabai06-net" EXAM.md` → `0`

### P9–P11 · ไม่อยู่ในงาน PREP

| P | เรื่อง | ทำเมื่อ |
|---|---|---|
| P9 | `_solution/` เฉลยอ้างอิง CR-01–05 · mutant X1–X3/M1–M9 · zip ข้อสอบ `sabai-legacy.zip` (ชื่อ `sabai06x-*` ตาม EXAM-DRAFT §3.11) · เครื่องตรวจ | งานถัดไป (หลังรอบ RUNNER) · เฉลยอ้างอิง CR-05 AC4 ต้อง `reset {now:"2026-10-10T15:00:00+07:00"}` ก่อนกดเสร็จ B06 (ไม่พึ่ง L2 · M10) |
| P10 | **ห้ามสร้าง** `db/migrations/` `docs/` `tests/` `e2e-cr/` `README.md` root `.gitignore` | ผู้เรียนสร้างเองใน LAB |
| P11 | **ห้ามแตะ** `web/ASSETS.md` `web/private/` `db/init/*` `web/lib/server/*` `img/` | บั๊กจริง L1–L8 ต้องคงอยู่ |

---

## 3. ตรวจรวม V1–V8 (รันใน `VER` · ผลทั้งหมดลง PREP-LOG)

| V | ทำ (PowerShell เว้นแต่ระบุ) | ผลที่ต้องได้ |
|---|---|---|
| V1 | Git Bash ที่ `$CH`: grep ตรวจของ P1–P8 ครบทุกข้อ | ตรงทุกข้อ |
| V2 | สร้าง `VER` ใหม่ (ถ้ามีอยู่ ให้ลบเฉพาะ `C:/t/work/b2prep/verify` เอง) แล้วคัดลอก `$CH` ทั้งโฟลเดอร์ **ยกเว้น** `_solution/` `img/` → `VER` (`robocopy "$CH" C:\t\work\b2prep\verify /E /XD _solution img node_modules .next` · exit code 1 = คัดลอกสำเร็จ · ≥ 8 = ล้ม) | `VER/_solution` ไม่มี |
| V3 | ตามข้อ 0.6 ว่างแล้ว → `docker network create sabai06-net` → `$env:WEB_PORT="<ที่ได้>"; $env:DB_PORT="<ที่ได้>"` → ใน `VER`: `docker compose -f db/compose.yaml up -d --wait` → `docker compose -f web/compose.yaml up -d --build --wait` (build นานเกิน 2 นาทีได้ → รันแบบ background/timeout 10 นาที) · `Invoke-RestMethod http://localhost:$env:WEB_PORT/api/health` · `docker ps --filter name=sabai06 --format "{{.Names}} {{.Ports}}"` | build ผ่าน (= type check ของ P1 ผ่าน) · health `ok=True db=True` · container ชื่อ `sabai06-web` `sabai06-db` · พอร์ตตาม env |
| V4 | ที่ราก `VER`: `$env:BASE_URL="http://localhost:$env:WEB_PORT"; node web/scripts/check-rules.mjs` (รันจาก**ราก** = พิสูจน์ m2) · จดบรรทัดหัว "ตรวจกฎร้าน … · 90 เคส" และเวลา | **90/90** · ไม่มีคำว่า BUG_MODE ในผล |
| V5 | `Push-Location e2e-legacy; npm ci; npx playwright install chromium firefox webkit; npx playwright test --reporter=list; Pop-Location` (BASE_URL ยังตั้งอยู่) · นับจากผล: บรรทัดสรุป + จำนวนบรรทัดที่มี annotation `fail` | บรรทัดสรุป **41 passed · 1 failed** · ใน 41 มี expected-fail 3 (TC-TRN-03 · TC-GC-04 · TC-SEC-04) · failed = TC-SEC-05 · เวลา |
| V5b | (background ~13 นาที) `Push-Location e2e-legacy; npm run test:all -- --reporter=list; Pop-Location` | **114 รายการ: 113 passed · 1 failed** (expected-fail 7 = TC-TRN-03 ×3 · TC-GC-04 ×3 · TC-SEC-04 ×1 · failed = TC-SEC-05 ×1 เพราะอยู่ใน project `api` รันครั้งเดียว) · เวลา |
| V6 | `$env:ALLOW_TEST_RESET="0"; docker compose -f web/compose.yaml up -d --wait` → `POST /api/test/reset` → ตั้งกลับ `"1"` แล้ว up อีกครั้ง → health | 404 ตอนปิด · กลับมา 200 |
| V7 | REA ใน `VER` (D7): `Push-Location tools; npm install; Pop-Location` → `New-Item -ItemType Directory -Force rea-out\v1\.next \| Out-Null; docker cp sabai06-web:/app/.next/static rea-out\v1\.next\static` → `powershell -NoProfile -ExecutionPolicy Bypass -File tools\rea.ps1 -Out rea-out\static-v1.json analyze-javascript-application /work/rea-out/v1/.next/static --json` → `node tools\rea-tools.mjs endpoints rea-out\static-v1.json` → `node tools\record-har.mjs http://127.0.0.1:$env:WEB_PORT rea-out\journeys.har` → `node tools\rea-tools.mjs har-records rea-out\journeys.har` → `…rea.ps1 -Out rea-out\har-api.json inspect-web-network-capture /work/rea-out/journeys.har har <records> --sensitive-value Nida@2026 --sensitive-value Owner@2026 --json` → `node tools\rea-tools.mjs har-api rea-out\har-api.json` → `…rea.ps1 -Network sabai06-net -Out rea-out\scenario.json capture-browser-scenario /work/tools/scenario-book-quote.json --json` → `node tools\rea-tools.mjs shot rea-out\scenario.json rea-out\scenario-final.png` | exit 0 ทุกคำสั่ง · endpoint static 9 · route 25 · HAR 7 endpoint / 10 ครั้ง · scenario 12/12 step · ภาพ `scenario-final.png` เปิดแล้วเห็นหน้า "4. สรุปก่อนจ่าย" ฿1,000 (เทียบ RF ที่พอร์ต 3261 · ตัวเลขต่างได้ ให้จดค่าจริง) · **ถ้า `-Network sabai06-net` ล้ม** ให้ลองทางสำรอง `host.docker.internal:<WEB_PORT>` ในสำเนา scenario ใน `VER` เท่านั้น แล้วจดทั้ง 2 ผล |
| V8 | ปิด: `docker compose -f web/compose.yaml down` · `docker compose -f db/compose.yaml down` (ไม่ใส่ `-v`) · ถ้าข้อ 0.6 ยืนยันว่า PREP เป็นผู้สร้าง volume/network เอง → `docker volume rm sabai06-pgdata` · `docker network rm sabai06-net` (ให้ runner เริ่มจากฐานว่าง) · ลบ `VER` | `docker ps -a --filter name=sabai06` ว่าง |

## 4. MANIFEST สำหรับ RUNNER (ไม่ต้องเปิด `_solution/`)

Git Bash ที่ `$CH` (หลัง V1 ผ่าน · ก่อน orchestrator คัดลอกไป `C:/t/work/b2run/w/`):

```bash
mkdir -p /c/t/work/b2prep
find . -type f ! -path './_solution/*' ! -path './img/*' ! -path '*/node_modules/*' ! -path '*/.next/*' ! -path '*/test-report/*' ! -path '*/test-results/*' -print0 | sort -z | xargs -0 sha256sum > /c/t/work/b2prep/MANIFEST.sha256
wc -l /c/t/work/b2prep/MANIFEST.sha256
```

RUNNER ตรวจด้วย `cd /c/t/work/b2run/w && sha256sum -c --quiet /c/t/work/b2prep/MANIFEST.sha256` (ไม่มีผล + exit 0 = ตรง) · ถ้าภายหลังมีใครแก้ไฟล์ในบท ต้องทำ MANIFEST ใหม่

## 5. `PREP-LOG.md` (เขียนที่ `$DES/PREP-LOG.md`)

```text
# PREP-LOG · บท 06 · <วันที่ เวลา> · agent <ชื่อ>
## สรุป: พร้อมให้ RUNNER ✅ / ❌ (เพราะ…)
## 0. ก่อนเริ่ม: ผล docker ps/volume/network ของ sabai06 · พอร์ตที่ได้รับ
## P1–P8: ตาราง P | สถานะ (แก้แล้ว / พบว่าทำแล้ว / ข้าม) | ไฟล์ | ผลตรวจ (คำสั่ง → ผลจริง)
## V1–V8: ตาราง V | คำสั่ง | ผลจริง | ตรงผลที่ต้องได้ไหม | เวลา
## ตัวเลขที่ใช้แทน [คาด] ใน PROMPTS/LESSON-PLAN: check-rules · e2e-legacy (default / test:all) · build · REA static/HAR/scenario
## MANIFEST: path · จำนวนไฟล์ · sha256 ของไฟล์ MANIFEST เอง
## ปัญหาที่เจอ / สิ่งที่ทำต่างจาก PREP.md (พร้อมเหตุผล)
## ทรัพยากร docker ที่ยังเหลือ (ควรว่าง)
```

จบงานพิมพ์สรุป ≤ 15 บรรทัด (BRIEF ข้อ 9)

## PREP notes

> เพิ่มโดย agent PREP6 · 12 ต.ค. 2026 09:30 · รายละเอียดใน `PREP-LOG.md`

| # | ข้อใน PREP.md | ที่พบตอนรันจริง | ทำอย่างไร |
|---|---|---|---|
| 1 | 0.5 ค่าแนะนำ `WEB_PORT=4140` `DB_PORT=4141` | ถูกแทนด้วย BRIEF D10 (`4100`/`5533`) | ใช้ 4100/5533 |
| 2 | P6 บล็อกตัวอย่าง `tools\rea.ps1 doctor` | `rea doctor` ใน `rea-lab:6.4.0` ตอบ exit 1 `healthy: false` (ไม่มี Hopper/Ghidra/IDA) · `mcp doctor` exit 0 = คำสั่งที่ LESSON-PLAN T12/m4 และ PROMPTS LAB 0 ใช้ | ในบทใช้ `tools\rea.ps1 mcp doctor` พร้อมคอมเมนต์ท้ายบรรทัด |
| 3 | V7 "endpoint static 9" | graph มี endpoint node 16 · 9 = endpoint `/api/*` จริง (ที่เหลือ = ชื่อย่อ minified + `/_next/image`) | ใน README เขียน "endpoint จริง 9" |
| 4 | P7 "คุณนิดาใน CR-01/CR-03" | คุณนิดาอยู่ใน `answers/CR-01-ANSWERS.md` ไม่ใช่ `CR-01.md` | ตรวจแล้วตรง seed |
| 5 | V5 นับ annotation `fail` | list reporter แสดง `x` ทั้ง expected-fail และ failed (ไม่พิมพ์ annotation) | นับจากชื่อ TC + บรรทัดสรุป |
| 6 | §4 MANIFEST | ระหว่างงานมี agent อื่นเขียน `EXAM.md` ใหม่และสร้าง `fast_track/` · คำสั่ง §4 รวม `fast_track/` ด้วย | ต้องรัน §4 ใหม่ทุกครั้งที่บทเปลี่ยน ก่อนคัดลอกให้ RUNNER |
