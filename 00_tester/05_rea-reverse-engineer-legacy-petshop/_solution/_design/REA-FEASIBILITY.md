# REA-FEASIBILITY: ผู้เรียนบน Windows + Docker ใช้ REA กับ PawPantry ได้แค่ไหน

> งาน A1 · รันจริงเมื่อ 12 ต.ค. 2026 บน Windows 11 + Docker Desktop · image `rea-lab:6.4.0` (REA 6.4.0, Node 24.20, Chromium 1243)
> ที่ทำงาน: `C:/t/work/a1/` (สำเนา petshop v1 และ v2) · ไฟล์ช่วยและ evidence ย่ออยู่ที่ [`rea-probe/`](rea-probe/)
> ตัวเลขทุกตัวในเอกสารนี้มาจากการรันจริง เวลาเป็น wall-clock ของคำสั่ง `docker run` นั้นทั้งคำสั่ง (รวมเวลา start container ประมาณ 1–2 วินาที)

## 0. สรุปสั้น

- **ใช้ได้จริงทุกข้อที่ทดสอบ** (exit 0) แต่ "อ่านรู้เรื่อง" ไม่เท่ากัน
  - ดีมาก: HAR → API inventory, browser scenario (screenshot/a11y/storage), source-to-bundle (พิสูจน์ว่าเปลี่ยนแค่ที่ตั้งใจ), MCP ใน Claude Code
  - ดีเมื่อชี้ไปที่ `.next/server`: route/endpoint inventory, trace (เพราะ Next 16 มี source map ฝั่ง server ทำให้ REA กู้ชื่อไฟล์จริงได้ 53 ไฟล์ รวม API route ทั้ง 12 ตัว)
  - อ่านยาก: `.next/static` (ชื่อ chunk เป็น hash), `compare-application-versions` (noise เยอะมาก ทุกอย่างเป็น `unknown`)
- **ปัญหาเฉพาะเครื่องนี้:** พอร์ต 3051 อยู่ในช่วงพอร์ตที่ Windows จองไว้ (`2970–3069`) จึง publish ไม่ได้เลย ต้องเปลี่ยนไปใช้ Docker network ภายใน (รายละเอียดที่ §3)
- **กับดักที่ผู้เรียนจะเจอแน่ ๆ:** PowerShell 5.1 ใช้ `>` แล้วได้ไฟล์ที่มี BOM หรือเป็น UTF-16 ซึ่ง REA ไม่ยอมรับเป็น input (แก้ด้วย `rea.ps1 -Out`) · Git Bash แปลง path `/work` ให้เอง · Evidence หนึ่งไฟล์ใหญ่ราว 54 MB

## 1. ตารางสรุป

| # | ความสามารถ | ใช้ได้? | คำสั่ง (ย่อ) | เวลา | เหมาะกับ LAB |
|---|---|---|---|---|---|
| 1a | `rea doctor` | ✅ แต่ exit 1 | `docker run --rm rea-lab:6.4.0 doctor` | 2.4 s | 5.0 setup (อธิบายว่าที่ fail คือ Hopper/Ghidra/IDA ซึ่งงานเว็บไม่ต้องใช้) |
| 1b | `rea capabilities` | ✅ | `docker run --rm rea-lab:6.4.0 capabilities` | 2.6 s | อ้างอิงเฉย ๆ (ข้อมูล 164 KB ยาวเกินกว่าจะให้ผู้เรียนอ่าน) |
| 1c | `rea mcp doctor` | ✅ healthy | `docker run --rm rea-lab:6.4.0 mcp doctor` | 4 s | 5.4 MCP |
| 2a | analyze `.next/static` | ✅ partial | `analyze-javascript-application /work/.next/static --json` | 38 s · 54 MB | 5.1 (endpoint ที่ฝั่ง client เรียก + localStorage) |
| 2b | analyze `.next/server` | ✅ partial | `analyze-javascript-application /work/.next/server --json` | 25 s · 54 MB | **5.1 แผนที่ route/API จาก build** ⭐ |
| 2c | `inspect-analysis-view` | ✅ | `inspect-analysis-view /w/out/view-summary.json` | 10 s | ใช้ประกอบ (summary มีแต่ตัวนับ ไม่มีรายชื่อ endpoint) |
| 3 | `trace-application-feature` | ⚠️ ได้เฉพาะ seed `string` | `trace-application-feature /w/out/trace-*.in.json --json` | 10–12 s | 5.1 (ใช้ `incoming` บน server bundle) |
| 4 | HAR + `inspect-web-network-capture` | ✅ | `inspect-web-network-capture /har/pawpantry-main.har har --json` | HAR 5–7 s · inspect 2 s | **5.2 API inventory → characterization test** ⭐ |
| 5 | `capture-browser-scenario` | ✅ (ผ่านเมื่อรอบที่ 2) | `capture-browser-scenario /w/out/scenario-a1.json --json` | 3 s | **5.3 black-box evidence** ⭐ |
| 6 | `compare-application-versions` | ✅ แต่อ่านยาก | `compare-application-versions /w/out/cmp-server.in.json --json` | 17 s | ใช้เป็นตัวอย่างประกอบใน 5.4 (ไม่ใช่ตัวหลัก) |
| 7 | `import-reference-source` + `compare-source-to-bundle` | ✅ (server) | `import-reference-source /src --json` แล้ว `compare-source-to-bundle … --json` | 3 s + 9 s | **5.4 "พิสูจน์ว่าแก้แค่ที่ตั้งใจ"** ⭐ |
| 8 | REA เป็น MCP ใน Claude Code | ✅ | `--mcp-config` → `docker run -i --rm -v …:/work rea-lab:6.4.0 mcp` | 19–56 s ต่อพรอมต์ | **5.4/5.5 Agent ใช้ REA เอง** ⭐ |
| 9 | path บน Windows | ✅ | PowerShell `"${PWD}:/work"` · Git Bash `MSYS_NO_PATHCONV=1` + `$(pwd -W)` | – | ทุก LAB |

## 2. รายละเอียดทีละข้อ

ตัวแปรที่ใช้ในคำสั่ง (Git Bash ตอนทดสอบ): `export MSYS_NO_PATHCONV=1` · โค้ด v1 อยู่ที่ `C:/t/work/a1/petshop` และ v2 อยู่ที่ `C:/t/work/a1/petshop-v2`

### 2.1 `doctor` / `capabilities`

```bash
docker run --rm rea-lab:6.4.0 doctor          # exit 1, 2.4 s
docker run --rm rea-lab:6.4.0 capabilities    # exit 0, 2.6 s, 164 KB (TOON)
docker run --rm rea-lab:6.4.0 mcp doctor      # exit 0, 4 s, healthy: true
```

| check | ผล | ความหมายสำหรับบท 05 |
|---|---|---|
| node / host | ✅ 24.20.0 / ubuntu 24.04 | – |
| hopper / ghidra / ida-registration | ❌ `missing_analysis_engine` | ใช้แค่กับ binary native งานเว็บไม่ต้องมี |
| skill:identity | ❌ `config_drift` (ยังไม่ได้ติดตั้ง skill) | ไม่กระทบการใช้ CLI หรือ MCP |
| catalog | CLI 127 คำสั่ง · MCP 170 tools · 6 prompts | – |
| mcp doctor | initialize ✅, tools 170/170 ✅, request-flow ✅ | MCP พร้อมใช้ |

> ต้องบอกผู้เรียนว่า `healthy: false` ไม่ได้แปลว่าใช้ไม่ได้ ถ้าไม่บอก ผู้เรียนจะตกใจ

### 2.2 Static bundle

Build (ใน container ไม่ต้องลง Node บน host):

```bash
docker run --rm -v "C:/t/work/a1/petshop:/app" -w /app -e NEXT_TELEMETRY_DISABLED=1 node:24-alpine \
  sh -c "npm ci --no-audit --no-fund && npm run build"        # 2m57s (npm ci ~2m) · v2 ใช้ 163 s
docker run --rm -v "C:/t/work/a1/petshop:/work" rea-lab:6.4.0 analyze-javascript-application /work/.next/static --json > out/v1-static.json   # 38 s
docker run --rm -v "C:/t/work/a1/petshop:/work" rea-lab:6.4.0 analyze-javascript-application /work/.next/server --json > out/v1-server.json   # 25 s
```

| | `.next/static` (client) | `.next/server` |
|---|---|---|
| ไฟล์ที่วิเคราะห์ | 21 | 449 |
| node | module 19 · asset 21 · **endpoint 9** · **storage 3** · unknown 10 · artifact 1 | source-module **735** · javascript-module 173 · asset 171 · source-map 97 · artifact 89 · endpoint 60 · unknown 210 · electron-renderer 2 |
| edges | 68 | 1870 |
| coverage | partial (11 chunk เกิน result budget หรือ heap ของ worker) | partial |
| ขนาด JSON | 54.2 MB (ส่วนใหญ่เป็น `semantic_graph`) | 54.1 MB |

**สิ่งที่กู้ได้**

| ประเภท | `.next/static` | `.next/server` |
|---|---|---|
| Endpoint จริง | `/api/products` `/api/orders` `/api/auth/login` `/api/auth/logout` `/api/auth/register` `/api/coupons/validate` (`call:fetch`) | ส่วนใหญ่เป็น noise คือชื่อ header (`Cache-Control`, `cookie`, `set-cookie`, `next.route`…) และ query key (`pet`, `type`, `life`, `grainFree`, `noChicken`) |
| Endpoint ปลอม | `a`, `b`, `c` (ชื่อย่อจาก minify ของ router ภายใน Next) | – |
| ที่หายไป | `/api/auth/me`, `/api/orders/[id]`, `/api/products/[slug]`, `/api/recommendations`, `/api/health`, `/api/test/reset` | – |
| Route / ไฟล์ต้นทาง | ไม่มี (ชื่อ chunk เป็น hash เช่น `chunks/2u0e345l_sgw0.js`) | **กู้ path จริงได้ 53 ไฟล์จาก source map**: API route ครบทั้ง 12 ไฟล์ (`app/api/**/route.ts`), page 13 ไฟล์, `components/*`, `lib/*` ([evidence/02](rea-probe/evidence/02-server-v1.summary.json)) |
| Storage | `localStorage` get/set/remove (`name: null` คือไม่รู้ชื่อ key) | – |

`inspect-analysis-view` (ต้องห่อ input เป็น `{source:{kind:"inline",evidence:…},view:{kind:"summary"}}`; ไฟล์ input จึงใหญ่ 54 MB):
- `summary` ได้ TOON ขนาด 16 KB ใน 10 s มีแค่สถิติ coverage และ limitation 27 ข้อ **ไม่มีรายชื่อ endpoint**
- `page modules 0–32` ได้ 18 KB ใน 10 s เป็นรายการ `node_id, kind, path` ที่ path เป็น chunk hash ล้วน
- สรุป: ให้ใช้ [`rea-summarize.mjs`](rea-probe/rea-summarize.mjs) (`node rea-summarize.mjs out/v1-static.json`) ดึง endpoint/storage ออกมาเอง ไม่ต้องลง `jq` (บน host ไม่มี `jq`)

> ⚠️ REA ติดป้าย HTML page ใน `.next/server` เป็น `electron-renderer` เพราะเครื่องมือออกแบบมาสำหรับ Electron ด้วย ต้องเตือนผู้เรียนว่าไม่ได้แปลว่าแอปนี้เป็น Electron

### 2.3 `trace-application-feature`

Input = `{application: <evidence ทั้งก้อน>, seed: {kind, value}, direction}` ส่วน `direction` รับได้แค่ `outgoing | incoming | both` (ใส่ `backward` จะได้ `invalid_request`)

| seed | input | direction | ผล | เวลา |
|---|---|---|---|---|
| `api` `/api/coupons/validate` | static | both | **no-match** (seed kind `api` หมายถึง API ของ Electron ไม่ใช่ HTTP) | 10.8 s |
| `route` `/api/coupons/validate` | static | both | **no-match** | 12.1 s |
| `api` `/api/orders` | static | both | **no-match** | 11.5 s |
| `string` `coupon` | static | both | match 1 · 63 nodes · 21 paths คือได้**ทั้ง graph** (ลากผ่าน artifact root) อ่านไม่ได้ | 10.3 s |
| `string` `coupon` | static | **incoming** | 4 nodes: `endpoint:/api/coupons/validate ← module chunks/2u0e345l_sgw0.js ← asset ← artifact root` + ตำแหน่ง `line 1, col 3338–3466` | ~10 s |
| `string` `coupon` | static | outgoing | 1 node (ตัว endpoint เอง) | ~10 s |
| `string` `/api/orders` | static | incoming | 4 nodes (`chunks/2bxbzaw5q8rvv.js`) | ~10 s |
| `string` `localStorage` | static | incoming | 3 storage nodes ← `chunks/2ir-3fmt1dgqd.js` | ~10 s |
| `string` `coupons/validate` | **server** | incoming | 13 seed matches · 16 nodes ได้แก่ `app/api/coupons/validate/route.js`, **`source-module: app/api/coupons/validate/route.ts`**, **`chunks/ssr/components_CartView_tsx_….js`**, manifests | 10 s |
| `string` `coupons/validate` | server | outgoing | 27 nodes (route → turbopack runtime, `path`, `url`, `worker_threads`) | 10 s |

**ผู้เรียนเข้าใจได้ไหม:** บน static ได้แค่ "endpoint นี้อยู่ใน chunk hash นี้" ซึ่งยังพอใช้ได้ บน server ได้ "API นี้ = ไฟล์ `route.ts` นี้ และหน้าที่เรียกคือ `CartView.tsx`" ซึ่ง**มีประโยชน์จริง** ข้อแนะนำ: ใช้ seed `string` + `incoming` กับ `.next/server` ห้ามใช้ `both` · ผลดูง่ายที่สุดผ่าน MCP (§2.8)

### 2.4 HAR → `inspect-web-network-capture`

สคริปต์: [`rea-probe/record-har.mjs`](rea-probe/record-har.mjs) (ใช้ไลบรารี `playwright` 1.63, headless, `recordHar` แบบ `content: "embed"` และตัด font/รูปออก)
เส้นทาง: home → ค้นหา "แซลมอน" → หน้า `lickable-salmon-treat` → เพิ่มลงตะกร้า ×3 → คูปอง PAW10 → checkout ถูกพาไป login → login `demo@pawpantry.test` → กรอกที่อยู่ → สั่งซื้อ → `PP-100001`

```bash
# ตอนทดสอบรันใน container เพราะ host publish 3051 ไม่ได้ (ดู §3) ส่วนผู้เรียนรันบน host ด้วย BASE_URL=http://localhost:3000 ได้เลย
docker run --rm --network a1net -v "C:/t/work/a1/har:/har" -w /har -e BASE_URL=http://pawpantry:3051 \
  mcr.microsoft.com/playwright:v1.63.0-noble sh -c "npm init -y >/dev/null && npm i playwright@1.63.0 >/dev/null && node record-har.mjs"
docker run --rm -v "C:/t/work/a1/har/out:/har" rea-lab:6.4.0 inspect-web-network-capture /har/pawpantry-main.har har --json > out/har-inspect.json
docker run --rm -v "C:/t/work/a1/har/out:/har" rea-lab:6.4.0 inspect-web-network-capture /har/pawpantry-main.har har \
  --sensitive-value Paw12345 --sensitive-value demo@pawpantry.test --json > out/har-inspect-redacted.json
```

ผล: เดิน 8 step ทั้งหมดใช้ 3.0 s (`total_ms` 3032 รวม launch browser) ([evidence/04-har-steps](rea-probe/evidence/04-har-steps.json)) · HAR 1.57 MB · inspect 2 s (exit 0) ได้ JSON 1.7 MB · **97 records** (เป็น RSC `?_rsc` ของหน้า/prefetch 70, `_next/static` 23, API 4) · redaction อัตโนมัติ 36 จุด (cookie/set-cookie ที่ระบุ `transport-credential`)

**API inventory จากผลของ REA** (`node rea-summarize.mjs out/har-inspect.json --md`):

| # | method | path | status | request body keys | response keys |
|---|---|---|---|---|---|
| 1 | POST | `/api/coupons/validate` | 200 | code, items | ok, code, discount, freeShipping, message |
| 2 | POST | `/api/auth/login` | 200 | email, password | user |
| 3 | POST | `/api/orders` | 201 | items, coupon, shipping, payment, address | order, id |
| 4 | GET | `/api/products` | 200 | – | items, total |

ค่าจริงใน HAR: คูปองตอบ `{"ok":true,"discount":20,"message":"ใช้คูปอง PAW10 แล้ว"}` (subtotal 207) · order `total 237 = 207 − 20 + 50`

> ⚠️ **รหัสผ่านอยู่ใน HAR แบบ plain text** (body ของ `/api/auth/login`) REA ไม่ปิดให้เอง ถ้าใส่ `--sensitive-value` REA จะทำ field นั้นทั้ง field เป็น `null` (ทดสอบแล้ว: ในผลไม่มีคำว่า `Paw12345` อยู่เลย) แต่**ไฟล์ HAR ต้นฉบับยังมีรหัสอยู่** จึงห้าม commit ไฟล์ HAR · ตอนเรียกผ่าน MCP Claude เองก็เตือนเรื่องนี้ ([evidence/08-mcp-yolo-har](rea-probe/evidence/08-mcp-yolo-har.txt))

### 2.5 `capture-browser-scenario`

ไฟล์: [`rea-probe/scenario-coupon.json`](rea-probe/scenario-coupon.json) (ตัวสำหรับผู้เรียนตั้ง `start_url` เป็น `http://host.docker.internal:3000/` ส่วนตอนทดสอบเปลี่ยนเป็น `http://pawpantry:3051/`)
มี 10 action: wait hero → fill ค้นหา → click → wait `result-count` → click สินค้า → add-to-cart → cart → fill PAW10 → apply → wait `coupon-message` · capture `dom, accessibility, screenshot, url, storage` + events `console, page-errors, network` (มี body)

```bash
docker run --rm --network a1net -v "C:/t/work/a1:/w" rea-lab:6.4.0 capture-browser-scenario /w/out/scenario-a1.json --json > out/scenario-capture.json
```

| รอบ | ผล |
|---|---|
| 1 | exit 0 แต่ step `results-ready` **failed**: `strict mode violation: getByTestId('product-card') resolved to 12 elements` แล้ว step ที่เหลือเป็น `cancelled` ทั้งหมด (เป็น Playwright strict mode เหมือนในบท 03) |
| 2 (แก้ locator) | exit 0 · **ทั้ง 11 step completed** · scenario ใช้ 1,140 ms · wall 3 s · JSON 4.5 MB |

สิ่งที่ได้ ([evidence/05](rea-probe/evidence/05-scenario.summary.json), [screenshot](rea-probe/evidence/05-scenario-final.png)):
- **Accessibility tree เป็นภาษาไทยอ่านง่าย** เช่น `alert: ใช้คูปอง PAW10 แล้ว` · `ส่วนลด PAW10 -฿6` · `ยอดชำระทั้งหมด ฿113`
- **Storage: ได้ชื่อ key ของ localStorage ที่ static analysis หาไม่เจอ** คือ `pp-recent`, `pp-cart`, `pp-coupon` (ค่าเป็น sha256 ไม่โชว์ตัวค่าจริง)
- Network 84 requests และได้ body ของ `/api/coupons/validate` ครบ · console error 1 จุด (favicon 404)
- `completeness: incomplete` (events ขาด) เพราะ RSC prefetch 21 ตัวถูก abort (`net::ERR_ABORTED`) เป็นเรื่องปกติของ Next แต่มีผลให้ `equality_eligible: false`
- locator รองรับ `test_id` / `role` / `css` จึงใช้ `data-testid` ชุดเดียวกับบท 03 ได้เลย

### 2.6 `compare-application-versions` (v1 กับ v2)

การเปลี่ยนใน v2 (ตั้งใจไว้ 2 จุด):
1. `lib/pricing.ts`: `notFound: "ไม่พบคูปองนี้"` → `"ไม่พบโค้ดส่วนลดนี้ กรุณาตรวจสอบตัวสะกด"`
2. เพิ่ม `app/api/coupons/active/route.ts` (GET คืนรายการคูปอง)

```bash
# input = {left: <v1 evidence>, right: <v2 evidence>} แต่ละไฟล์ใหญ่ ~108 MB
docker run --rm -v "C:/t/work/a1:/w" rea-lab:6.4.0 compare-application-versions /w/out/cmp-static.in.json --json   # 17 s · 457 KB
docker run --rm -v "C:/t/work/a1:/w" rea-lab:6.4.0 compare-application-versions /w/out/cmp-server.in.json --json   # 17 s · 9.7 MB
```

| | unchanged | added | removed | changed | unknown |
|---|---|---|---|---|---|
| static | 0 | 0 | 0 | 10 | 87 |
| server | 0 | 0 | 0 | 273 | 1479 |

**อ่านรู้เรื่องไหม: ไม่** เพราะ
- coverage เป็น partial ทำให้ REA ไม่กล้าบอกว่า added/removed ทุกอย่างจึงกลายเป็น `unknown` ("The opposite graph is incomplete…")
- build ID และชื่อ chunk ที่เป็น hash เปลี่ยนทั้งชุด เกิด noise หลายร้อยรายการ ข้อความที่เปลี่ยนไปอยู่ใน 7 chunk ของ v2 ซึ่งชื่อไม่ตรงกับ v1 เลย
- ถ้ากรองด้วยสคริปต์จะ**เจอการเปลี่ยนที่ตั้งใจ**: `app/api/coupons/active/route.ts` เป็น `right-only` และ `lib/pricing.ts` ไม่จับคู่ทั้งสองฝั่ง ([evidence/06](rea-probe/evidence/06-compare-versions.summary.json)) แต่ต้องคุ้ยจาก 1,752 รายการ

→ ไม่ควรใช้เป็นตัวหลักของ LAB ให้ใช้ §2.7 แทน

### 2.7 `compare-source-to-bundle` ⭐

```bash
docker run --rm -v "C:/t/work/a1/petshop:/src:ro" rea-lab:6.4.0 import-reference-source /src --json > out/v1-source-graph.json   # 3 s · 59 KB
# input = {reference: <HistoricalSourceGraph>, application: <analyze evidence>}
docker run --rm -v "C:/t/work/a1:/w" rea-lab:6.4.0 compare-source-to-bundle /w/out/s2b-server.in.json --json         # 9–10 s
```

- กับ `.next/static`: unknown ทั้งหมด 56 ไฟล์ (client ไม่มี source map) **ใช้ไม่ได้**
- กับ `.next/server`: v1 src → v1 build ได้ **unchanged 44 · duplicated 9 · unknown 3** (`globals.css`, `eslint.config.mjs`, `next.config.ts` ซึ่งไม่ได้อยู่ใน bundle อยู่แล้ว) จับคู่ด้วย sha256 แบบ exact

**ตาราง 4 ทิศ (แสดงเฉพาะไฟล์ที่ผลต่างจาก baseline)** ([evidence/07](rea-probe/evidence/07-s2b-diff-table.md)):

| source file | v1src→v1build | v1src→v2build | v2src→v1build | v2src→v2build |
|---|---|---|---|---|
| `app/api/coupons/active/route.ts` | (ไม่มีใน src) | (ไม่มีใน src) | unknown | unchanged |
| `lib/pricing.ts` | duplicated | **unknown** | **unknown** | duplicated |

อ่านได้ทันทีว่า **"ระหว่าง v1 กับ v2 มีแค่ 2 ไฟล์นี้ที่ต่างกัน และ build v2 ตรงกับ source v2 ทุกไฟล์"** จึงตอบโจทย์ "prove we changed only what we intended" และ "build ที่ส่งมอบตรงกับ repo หรือไม่" ได้ตรง ๆ
หมายเหตุ: REA ไม่เคยใช้คำว่า `modified` ในกรณีนี้ ไฟล์ที่ถูกแก้จะออกมาเป็น `unknown` (หา digest ไม่เจอ) ต้องสอนผู้เรียนให้อ่านแบบนี้

### 2.8 REA เป็น MCP server ใน Claude Code

- จาก `rea --help` คำสั่งที่เปิด MCP stdio server ได้คือ `rea mcp` และ `rea --mcp` ทดสอบส่ง `initialize` + `tools/list` ทาง stdin ใน `docker run -i` แล้วทั้งคู่ตอบ (protocol 2025-06-18, server `rea 6.4.0`)
- `rea setup` ใน docs จะเขียน config ของ client แบบถาวร (`npx -y rea-agents@<v> mcp`) ซึ่ง**ไม่เหมาะกับ docker** และงานนี้ห้ามแตะ config ถาวรอยู่แล้ว จึงใช้ `--mcp-config` ไฟล์ชั่วคราว + `--strict-mcp-config`

```json
{ "mcpServers": { "rea": { "type": "stdio", "command": "docker",
  "args": ["run", "-i", "--rm", "-v", "C:/t/work/a1/har/out:/work", "rea-lab:6.4.0", "mcp"] } } }
```

```bash
cmd.exe //c "C:\Users\oishi\bin\yolo.cmd" -p "Use ONLY the rea MCP server. Call its inspect_web_network_capture tool with capture_path \"/work/pawpantry-main.har\", format \"har\", record_ordinals [68, 78, 92, 93]. …" \
  --mcp-config "C:/t/work/a1/mcp-rea.json" --strict-mcp-config --output-format text < /dev/null
```

| ทดสอบ | ผล | เวลา |
|---|---|---|
| `inspect_web_network_capture` (เลือก 4 records) | ✅ ได้ตาราง 4 API ครบ · เรียก `mcp__rea__inspect_web_network_capture` · Claude เตือนเรื่องรหัสผ่านใน HAR เอง | 19 s |
| `analyze_javascript_application` `/work/.next/static` | ⚠️ ได้ `resource_constraint` เพราะผลใหญ่ ≥ 10,544,542 bytes เกินเพดานคำตอบ MCP 10,484,736 bytes **แต่ server เก็บ evidence ไว้และคืน `evidence_id` มาให้** | 56 s |
| ↳ `inspect_analysis_view` ด้วย `{kind:"retained-evidence", evidence_id}` | ✅ ได้ summary (ไม่มีรายชื่อ endpoint) | (รวมข้างบน) |
| `analyze` → `trace_application_feature` (retained, seed string `/api/`, outgoing) | ✅ ได้ตาราง 6 endpoint + ชื่อ chunk | 55 s |

แนะนำวิธีลงทะเบียนให้ผู้เรียน (ยังไม่ได้รันจริงในงานนี้ เพราะจะเขียนไฟล์ `.mcp.json`; ที่ทดสอบจริงคือรูปแบบเดียวกันผ่าน `--mcp-config`):
```powershell
# รันจากโฟลเดอร์บท 05 → ได้ .mcp.json ระดับ project (ไม่แตะ ~/.claude.json)
claude mcp add rea --scope project -- docker run -i --rm -v "${PWD}:/work" rea-lab:6.4.0 mcp
```
- ใน MCP ทุก path ต้องเป็น path ใน container (`/work/...`)
- ข้อดีเหนือ CLI: ใช้ `retained-evidence` ได้ ไม่ต้องสร้างไฟล์ input ขนาด 54–108 MB · ข้อเสีย: evidence อยู่แค่ใน 1 connection (container `--rm` จบก็หาย)

### 2.9 Path บน Windows กับ `docker -v`

| shell | รูปแบบที่ใช้ได้ (ทดสอบแล้ว) | รูปแบบที่พัง (ทดสอบแล้ว) |
|---|---|---|
| **PowerShell 5.1** (ผู้เรียนใช้) | `docker run --rm -v "${PWD}:/work" rea-lab:6.4.0 … /work/…` ✅ | `"$PWD:/work"` → parser error `Variable reference is not valid. ':' was not followed by a valid variable name character` |
| Git Bash | `MSYS_NO_PATHCONV=1 docker run --rm -v "$(pwd -W):/work" …` ✅ | ไม่ตั้ง `MSYS_NO_PATHCONV`: `/work` กลายเป็น `C:/Program Files/Git/work` · arg ของ REA `/work/x.har` ได้ error `Expected an absolute filesystem path on this host.` · `-v "$(pwd):/work"` สร้างโฟลเดอร์ขยะชื่อ `out;C` |
| PowerShell / ส่ง output ต่อ | `.\rea.ps1 -Out out\x.json <cmd> … --json` ✅ (UTF-8 ไม่มี BOM, ภาษาไทยครบ) | `… --json > x.json` ในเครื่องนี้ได้ UTF-8 **มี BOM** (`EF BB BF`) ส่วน PS 5.1 ค่า default ได้ UTF-16 พอเอาไฟล์นี้ไปเป็น input ของ REA จะได้ `JSON input begins with a UTF-8 byte-order mark (EF BB BF), which strict JSON input does not accept` และไฟล์ UTF-16 ก็ถูกปฏิเสธเหมือนกัน (ทดสอบแล้วทั้งสองแบบ) |

**รูปแบบที่ควรให้ผู้เรียนใช้ใน PowerShell** (รันจากโฟลเดอร์บท 05):
```powershell
docker run --rm -v "${PWD}:/work" rea-lab:6.4.0 doctor
.\rea.ps1 -Out out\rea-server.json analyze-javascript-application /work/petshop/.next/server --json
.\rea.ps1 -Out out\har.json inspect-web-network-capture /work/out/pawpantry-main.har har --sensitive-value Paw12345 --json
.\rea.ps1 -Out out\scenario.json capture-browser-scenario /work/scenario-coupon.json --json
```

## 3. ข้อจำกัดและกับดัก

| # | กับดัก | อาการ | ทางแก้ / สิ่งที่ต้องเขียนในบท |
|---|---|---|---|
| 1 | **พอร์ตที่ Windows จองไว้** | `docker run -p 3051:3000` และ `-p 127.0.0.1:3051:3000` ได้ `ports are not available … bind: An attempt was made to access a socket in a way forbidden by its access permissions` · `netsh int ipv4 show excludedportrange protocol=tcp` แสดงช่วง `2970–3069` และ `3070–3169` (เครื่องนี้ 3000 ก็อยู่ในช่วงนี้) | ตอนทดสอบใช้ `docker network create a1net` + `--network-alias pawpantry -e PORT=3051` แล้วให้ REA/Playwright container เข้าผ่าน `http://pawpantry:3051` ทุกข้อทำงานได้โดยไม่ publish พอร์ต · ใน FAQ ของบทให้วิธีเช็กด้วย `netsh …` และให้เปลี่ยนพอร์ต host · **`host.docker.internal:<port>` ยังไม่ได้ทดสอบจริง** (resolve ได้ `fdc4:f303:9324::254` แต่ไม่มีพอร์ตที่ publish ให้ลอง) |
| 2 | Evidence ใหญ่ | analyze 1 ครั้งได้ราว 54 MB · ไฟล์ input ของ trace/compare 54–108 MB · โฟลเดอร์ `out/` ของงานนี้ใหญ่ 1.4 GB | ให้ทำเป็นไฟล์ใน `out/` ใส่ `out/` ใน `.gitignore` และใช้ `rea-summarize.mjs` · ห้ามให้ Claude อ่านไฟล์นี้ตรง ๆ |
| 3 | Coverage เป็น `partial` ตลอด | worker heap หมด หรือเกิน result budget ใน 11 chunk ทำให้ trace/compare เต็มไปด้วย `unknown` | สอนว่า "unknown ≠ ไม่มี" ซึ่งเป็นหลักของ REA เอง (`not evidence that the feature is absent`) |
| 4 | Seed kind ชวนเข้าใจผิด | `api` และ `route` → no-match กับ HTTP path | ใช้ `string` เท่านั้น |
| 5 | `direction: both` | ได้ทั้ง graph | ใช้ `incoming` |
| 6 | Strict mode ใน scenario | `wait_for` บน locator ที่ match หลายตัว → step fail แล้ว step ที่เหลือ cancelled | ใช้ testid ที่ไม่ซ้ำ หรือ css `[data-slug=…]` |
| 7 | HAR มีความลับ | รหัสผ่านอยู่ใน body | `--sensitive-value` + ห้าม commit HAR |
| 8 | node_modules ที่ copy มา | เอา `node_modules` ที่ tar มาจาก Windows ไปใช้ build ใน container ได้ `MODULE_NOT_FOUND` (symlink ใน `.bin` หาย) | `npm ci` ใหม่ใน container ทุกครั้ง |
| 9 | ป้าย Electron | `electron-renderer`, ส่วน `summary.electron.*` | บอกผู้เรียนว่าไม่เกี่ยวกับงานเว็บ ให้ข้ามไป |
| 10 | ผลของ MCP ใหญ่เกิน | `resource_constraint` แต่มี `evidence_id` | สอนแพทเทิร์น analyze → ใช้ id ต่อกับ trace/view |
| 11 | PowerShell positional binding | สคริปต์ wrapper รุ่นแรกจับ `doctor` เป็นค่า `-Out` | แก้แล้วด้วย `[CmdletBinding(PositionalBinding=$false)]` ใน `rea.ps1` |
| 12 | ขนาด image | `rea-lab:6.4.0` = 2.65 GB | ให้ build หรือ pull ไว้ก่อนเข้าคลาส |

## 4. LAB ที่เสนอสำหรับบท 05 (ใช้ REA)

แนวคิด: REA = มุม **black-box ของ tester** ต่อ "ของที่ส่งมอบ/รันอยู่" (build, เว็บที่รันอยู่, HAR) ส่วนการอ่าน source ใช้ Claude อ่าน repo ตามปกติ ซึ่งตรงกับที่ skill ของ REA บอกเองว่า "Skip REA for ordinary source-repository architecture analysis"

| LAB | ชื่อ | ผู้เรียนทำ | REA ที่ใช้ | ผลงาน | เวลาเครื่อง |
|---|---|---|---|---|---|
| 5.1 | **แผนที่ระบบจาก build** | build petshop → analyze `.next/server` และ `.next/static` → ให้ Claude สรุป route/API/storage จาก `rea-summarize` → เทียบกับที่เห็นใน UI และกับ `app/` | `analyze-javascript-application`, `trace-application-feature` (string + incoming) | `SYSTEM-MAP.md`: ตาราง API 12 ตัว + หน้า 13 หน้า + endpoint ที่ client เรียก + key ของ localStorage | ~4 นาที (build ~3 นาที + analyze ~1 นาที) |
| 5.2 | **HAR → API inventory → characterization test** | รัน `record-har.mjs` → `inspect-web-network-capture --sensitive-value` → ตาราง API → ให้ Claude เขียน Playwright API test ที่ "ล็อกพฤติกรรมเดิม" (golden master) | `inspect-web-network-capture` | `API-INVENTORY.md` + `tests/api-characterization.spec.ts` | < 1 นาที |
| 5.3 | **Browser scenario เป็นหลักฐาน** | แก้ `scenario-coupon.json` (เช่นใส่คูปองผิด หรือ FREESHIP) → อ่าน a11y tree, screenshot, storage keys → เขียน bug report แนบหลักฐาน | `capture-browser-scenario` (+ ไอเดีย `compare-web-captures` ระหว่าง `BUG_MODE=0/1` ซึ่ง**ยังไม่ได้ทดสอบ**) | `EVIDENCE/*.png` + รายงาน | ~3 วินาทีต่อรอบ |
| 5.4 | **แก้ฟีเจอร์แล้วพิสูจน์ว่าแก้แค่ที่ตั้งใจ** | รับ CR เล็ก ๆ (เปลี่ยนข้อความคูปอง + เพิ่ม endpoint) → Claude แก้ repo → build → `import-reference-source` + `compare-source-to-bundle` ทำตาราง 4 ทิศ → รันเทสต์จาก 5.2 ซ้ำ | `import-reference-source`, `compare-source-to-bundle` (`compare-application-versions` เป็นตัวอย่างว่าทำไมไม่ใช้) | `CHANGE-PROOF.md` (ตารางแบบ §2.7) + ผลเทสต์ characterization | ~4 นาที |
| 5.5 | **ให้ Agent ใช้ REA เอง (MCP)** | `claude mcp add rea --scope project -- docker run -i --rm -v "${PWD}:/work" rea-lab:6.4.0 mcp` → พรอมต์ให้ Claude analyze → trace ด้วย retained evidence → ตอบคำถาม "ปุ่มใช้โค้ดเรียก API อะไร ไฟล์ไหน" | MCP: `analyze_javascript_application`, `trace_application_feature`, `inspect_web_network_capture` | บันทึกการสนทนา + คำตอบที่ตรวจด้วย HAR | ~1 นาทีต่อพรอมต์ |

ลำดับที่แนะนำ: 5.1 → 5.2 → 5.4 (หัวใจของบท = แก้ repo เดิมพร้อมหลักฐาน) · 5.3 และ 5.5 เป็นทางเลือกหรือการบ้าน

## 5. ไฟล์ตัวอย่างที่ควรแจกผู้เรียน (อยู่ใน `rea-probe/` แล้ว)

| ไฟล์ | ใช้ทำอะไร | สถานะ |
|---|---|---|
| [`rea.ps1`](rea-probe/rea.ps1) | wrapper สำหรับ PowerShell: mount `${PWD}` → `/work`, `-Out` เขียนไฟล์ UTF-8 ไม่มี BOM, `-Network`, `-Mcp` | ทดสอบใน PS 5.1 แล้ว (doctor, HAR inspect, scenario; ไทยครบ ไม่มี BOM) |
| [`record-har.mjs`](rea-probe/record-har.mjs) | Playwright เดินเส้นทางหลัก 8 step แล้วบันทึก HAR (`BASE_URL` ค่า default `http://localhost:3000`) | ทดสอบแล้ว (ใน container `playwright:v1.63.0-noble`) |
| [`scenario-coupon.json`](rea-probe/scenario-coupon.json) | scenario ค้นหา → ตะกร้า → PAW10 (`start_url` เป็น `host.docker.internal:3000`) | ทดสอบแล้ว (เปลี่ยน URL เป็น `pawpantry:3051`) |
| [`rea-summarize.mjs`](rea-probe/rea-summarize.mjs) | ย่อ evidence (analyze/HAR/compare) เป็น JSON สั้น หรือตาราง Markdown (`--md`) โดยไม่ต้องมี `jq` | ทดสอบแล้ว |
| [`mcp-rea.example.json`](rea-probe/mcp-rea.example.json) | ตัวอย่าง `--mcp-config` (ให้แก้ path) | รูปแบบเดียวกับที่ทดสอบแล้ว |
| `evidence/` | ผลย่อของแต่ละข้อ (ทุกไฟล์ < 300 KB) + screenshot | – |

ยังไม่ได้ทำ หรือต้องเตรียมเพิ่ม: build หรือแจก image `rea-lab:6.4.0` ล่วงหน้า · `.gitignore` สำหรับ `out/` และ `*.har` · ทดสอบ `compare-web-captures` และ `host.docker.internal` บนเครื่องที่ publish พอร์ตได้
