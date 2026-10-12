# LAB 3_RESULT · ดูตอนรันจริง: HAR + REA ขับเบราว์เซอร์ → API-INVENTORY

| หัวข้อ | ค่า |
|---|---|
| เวลาเริ่ม · จบ · ใช้ไป | 2026-10-12 09:44 · 09:52 · ~8 นาที (เครื่อง ~0.5 นาที: HAR 3.4 s · REA inspect 2.3 s · scenario 3.8 s · ภาพ ~10 s · agent ~7.5) |
| cwd ของเซสชัน / settings มีผลไหม | runner เป็น Agent-tool session (cwd ไม่ใช่ `w/`) → `w/CLAUDE.md` และ `w/.claude/settings.json` **ไม่ได้ถูกบังคับโดย harness · runner ทำตามเอง** (ทุกคำสั่งรันจาก `w/` ด้วย PowerShell tool / path เต็ม) |
| ไฟล์ที่สร้าง/แก้ | `w/API-INVENTORY.md` ใหม่ 87 บรรทัด · `w/out/` ใหม่: `pawpantry-main.har` 1,629,955 B · `har-steps.json` 1,153 B · `har.json` 1,784,518 B · `scenario.json` 4,544,420 B · `scenario-final.png` 182,349 B |
| สคริปต์ชั่วคราว | `w/rea/scratch/har-peek.mjs` `w/rea/scratch/scn-peek.mjs` (อ่าน key/ค่าจาก `out\har.json` `out\scenario.json` แทนการเปิดตรง) · `../tools/lab3/shots.mjs` (ภาพ README) · stderr ของคำสั่ง REA/summarize ทุกตัว redirect ไป `../tools/lab3/*.stderr.txt` (ตาม tip LAB 2 · รอบนี้ทั้ง 4 ไฟล์ **0 byte**) |
| โหมดการรัน · shell ที่ agent ใช้จริง | A · PowerShell tool (Windows PowerShell 5.1) สำหรับทุกคำสั่งในพรอมต์ · Git Bash ใช้แค่อ่านไฟล์เล็ก/เขียนสคริปต์ scratch และรัน `node rea/scratch/*.mjs` |
| timeout / รันซ้ำ | ตั้ง timeout 5–10 นาทีให้ REA/HAR (ใช้จริง < 4 s) · ไม่มีการสั่งซ้ำ |
| สถานะเว็บ | `pawpantry05` Up (healthy) บน 4000 · ไม่ได้ rebuild ใน LAB นี้ · build เดียวกับ `out\v1` (chunk 15/15 ชื่อตรง) |
| ข้อมูลทดสอบ | reset 1 ครั้ง (ใน `record-har.mjs`) · ผู้ใช้ demo (ตาม TEST-DATA.md) · หลัง LAB มีออเดอร์ `PP-100001` ค้างใน RAM · ภาพของ runner ไม่ login ไม่สร้างข้อมูลฝั่ง server |

## ข้อห้ามที่ทำตาม (และที่พลาด ถ้ามี)

- ไม่แก้ `petshop/` · ไม่เปิด `_solution/` · ไม่ใช้ Playwright MCP (ภาพใช้ Playwright headless ใน `../tools/`)
- ไม่เปิด `.har` / `har.json` / `scenario.json` ตรง ๆ: ใช้ `rea-summarize.mjs` + สคริปต์ scratch ที่พิมพ์เฉพาะ key/ค่าที่ต้องใช้ · การตรวจ `Paw…` ใน `.har` ใช้ `Select-String -Quiet` ตามพรอมต์
- ไม่แตะ `e2e-legacy/` `TEST-DATA.md`: `git diff --stat -- e2e-legacy TEST-DATA.md` ว่าง (exit 0) · ไม่มีการเลี่ยง deny ผ่าน shell
- ไม่มี git ที่เปลี่ยนสถานะ (ใช้แค่ `git status` `git diff --stat` `git check-ignore`)
- ไม่แตะ container `sabai06-*` (4100/5533) `exref-*` · `multi-account-devtool`
- ไม่มีรหัสผ่าน/อีเมล demo ใน `API-INVENTORY.md` (ตรวจด้วย `Select-String` ทุก `*.md` ใน `w/` → เจอเฉพาะไฟล์เดิม `TEST-DATA.md:7` และ `e2e-legacy/README-LEGACY.md:35` ที่มากับบทอยู่แล้ว) · ในไฟล์นี้เขียนค่า `--sensitive-value` แบบปิดไว้

## คำตอบสรุปที่แสดงในแชท

> | ส่วน | จำนวนแถว | ยืนยันด้วย runtime ได้ | ยังไม่รู้ |
> |---|---|---|---|
> | A · API ที่เห็นตอนรัน | 4 | 4 | 1 (key ใน body ของ login ถูกปิด) |
> | B · เติมช่องว่าง SYSTEM-MAP | 17 | 8 🟢 + 1 🟡 | 8 |
> | C · API ในโค้ดที่ไม่เห็น | 9 | 1 (`/api/health` นอกเบราว์เซอร์) · 1 🟡 (`/api/test/reset`) | 7 |
> | D · 3 วิธี | 3 | 2 (HAR · scenario) | – |

## ตัวเลขสำคัญ (นับจากไฟล์จริง พร้อมคำสั่งที่ใช้นับ)

| ตัวเลข | ค่า | นับด้วย |
|---|---|---|
| HAR ขั้น · เวลารวม | 8 ขั้น · 3,080 ms (wall 3.36 s) | `out\har-steps.json` |
| records ใน HAR | 97 (document 2 · stylesheet 2 · script 21 · fetch 72 = API 4 + RSC 68) | `rea-summarize` + `rea\scratch\har-peek.mjs … types` |
| API | 4: POST `/api/coupons/validate` 200 · POST `/api/auth/login` 200 · POST `/api/orders` 201 · GET `/api/products` 200 | `rea-summarize out\har.json --md` |
| ค่าจริงใน HAR | คูปอง `discount 20` (subtotal 207 = 69×3) · order `PP-100001` `total 237 = 207 − 20 + 50` · `/api/products` `total 28` | `har-peek.mjs … api` |
| redaction | 42 จุด (explicit-sensitive-value 4 · transport-credential 38) · `sensitive_value_count 2` | `har-peek.mjs … red` |
| ค่าลับ | `out\har.json` มีรหัส demo: **False** · มีอีเมล demo: **False** · `.har` ต้นฉบับมีรหัส demo: **True** (1 บรรทัด) | `Select-String -SimpleMatch -Quiet` |
| scenario | 11/11 step completed · duration 1,682 ms (wall 3.79 s) · events 421 (dropped 0) · request-failed 23 (ทั้งหมด `net::ERR_ABORTED` RSC prefetch) · console error 1 (`/favicon.ico` 404) · `completeness: incomplete` missing `events` | `rea-summarize` + `node -e` บน `out\scenario.json` |
| storage | localStorage `pp-recent` `pp-cart` `pp-coupon` · session 0 · cookie 0 | `rea-summarize` |
| a11y | `alert: ใช้คูปอง PAW10 แล้ว` · `ส่วนลด PAW10 "-฿6"` · `ค่าจัดส่ง ฿50` · `ยอดชำระทั้งหมด ฿113` · `ซื้อเพิ่มอีก ฿930 เพื่อส่งฟรี` | `rea-summarize` + `scn-peek.mjs grep ยอดชำระ` |
| URL ที่ REA เห็น | `start_origin http://petshop:3000` · ทุก `after_url` = `http://petshop:3000/...` | `rea-summarize` |
| build ที่รัน vs `out\v1` | `/_next/static/*` ใน HAR 15 ไฟล์ · พบใน `out\v1\.next\static` 15/15 | `node -e` เทียบชื่อไฟล์ |
| `docker network ls` | มี `pawpantry05_default` ✅ (อื่น ๆ: bridge, host, none, kind, exref-net, sabai06-net, sabai-net, deep_vision_5090_vllm_default) | `docker network ls` |

## คำสั่งที่รัน (REA/docker/playwright: คำสั่ง | exit | เวลา | ขนาดผล)

| คำสั่ง (PowerShell จาก `w/`) | exit | เวลา | ขนาดผล |
|---|---|---|---|
| `Invoke-RestMethod http://localhost:4000/api/health` | ok | – | `{"ok":true}` |
| `node rea\record-har.mjs` | 0 | 3.36 s | `.har` 1,629,955 B · `har-steps.json` 1,153 B |
| `powershell -NoProfile -ExecutionPolicy Bypass -File .\rea\rea.ps1 -Out out\har.json inspect-web-network-capture /work/out/pawpantry-main.har har --sensitive-value <รหัส demo> --sensitive-value <อีเมล demo> --json 2> ..\tools\lab3\har-inspect.stderr.txt` | 0 | 2.30 s | 1,784,518 B · `ev_4db99f23` |
| `node rea\rea-summarize.mjs out\har.json --md` (+ แบบไม่มี `--md`) | 0 | <1 s | ตาราง 4 แถว |
| `… rea.ps1 -Network pawpantry05_default -Out out\scenario.json capture-browser-scenario /work/rea/scenario-coupon.json --json 2> ..\tools\lab3\scenario.stderr.txt` | 0 | 3.79 s | 4,544,420 B · `ev_956755da` |
| `node rea\rea-summarize.mjs out\scenario.json --png out\scenario-final.png` | 0 | <1 s | png 182,349 B |
| `git check-ignore -v out/pawpantry-main.har out/har.json` | 0 | – | ทั้งคู่โดน `.gitignore:1:out/` |
| (runner) `npm install playwright@1.63.0` ใน `../tools` + `node lab3/shots.mjs` | 0 | ~1 s + ~10 s | 2 ภาพ |

## ตัวอย่างแถวเด่น 3–6 แถว (สำหรับ README)

| method | path | status | request keys | response keys | ค่าตัวอย่าง |
|---|---|---|---|---|---|
| POST | `/api/coupons/validate` | 200 | `code` `items[{slug,size,qty}]` | `ok` `code` `discount` `freeShipping` `message` | ×3 → `discount 20` · ×1 (scenario) → `discount 6` |
| POST | `/api/auth/login` | 200 | (REA ปิด) | (REA ปิด) + `Set-Cookie pp_session` HttpOnly SameSite=Lax | – |
| POST | `/api/orders` | 201 | `items` `coupon` `shipping` `payment` `address{…}` | `order{…subtotal,discount,shipping,total…}` `id` | `PP-100001` · `total 237 = 207 − 20 + 50` |

ส่วน B เด่น: key localStorage ⚪ → 🟢 `pp-recent` `pp-cart` `pp-coupon` · method `/api/orders` ⚪ → 🟢 POST · cookie `pp_session` ⚠️ → 🟢 · container = build `out\v1` (ยังไม่รู้) → 🟢 15/15 chunk

## ตัดสินแทนผู้เรียน (คำถาม | คำตอบ | ที่มา 🧑/ตัดสินเอง | เหตุผล)

| คำถาม | คำตอบ | ที่มา | เหตุผล |
|---|---|---|---|
| LAB 3 ไม่มีหัวข้อ 🧑 · พรอมต์ไม่มีจุดถาม | – | – | – |
| ส่วน A ใส่ `/api/health` ไหม (เรียกด้วย Invoke-RestMethod ไม่ใช่เบราว์เซอร์) | ไม่ใส่ใน A · ใส่ใน B (🟢 คำสั่ง) และ C | ตัดสินเอง | A = สิ่งที่ HAR/scenario เห็น · health ไม่มีไฟล์หลักฐาน |
| request keys ของ login | เขียนว่า "REA ปิด" ไม่เปิดโค้ดมาเติม | ตัดสินเอง | พรอมต์บอก "ทุกค่าต้องมาจากไฟล์ผลที่รันจริง" |
| อ่านค่าตัวอย่างจาก `har.json` อย่างไรโดยไม่เปิดตรง | สคริปต์ `rea\scratch\har-peek.mjs` พิมพ์เฉพาะ key/ค่า API (ตัดที่ 600–900 ตัวอักษร) | ตัดสินเอง | `rea-summarize` ให้แค่ชื่อ key ไม่มีค่าตัวอย่าง แต่พรอมต์ขอ "ค่าตัวอย่าง" |

## ข้อสังเกต 👀 (บทเรียนจากรอบจริง ไม่ใช่สรุปผลซ้ำ)

- `rea-summarize` ให้แค่ **ชื่อ key** แต่ส่วน A ขอ "ค่าตัวอย่าง" → ผู้เรียน/agent ต้องเขียนสคริปต์อ่าน `out\har.json` เอง (หรือเปิดไฟล์ใหญ่ซึ่งห้าม) · agent ที่ทำตามกติกาจะเสียเวลาหาโครงสร้าง (`normalized_result.records[].reported.request/response`)
- REA ปิด body ของ login ทั้งก้อน (ไม่ใช่แค่ค่า) เพราะมีค่าลับ → request keys ของ login หายไปจาก inventory · บทเรียน: ปิดค่าลับแล้วเสียข้อมูลโครงสร้างด้วย
- stderr ของ REA ใน LAB นี้ (inspect HAR / scenario ที่มี `-Out`) **ว่าง 0 byte** — tip เรื่อง progress หลายร้อยบรรทัดใช้กับคำสั่ง analyze ของ LAB 2 เป็นหลัก
- `completeness: incomplete` มาจาก `missing_sections: ["events"]` + `request-failed` 23 ครั้ง ทั้งหมดเป็น RSC prefetch `ERR_ABORTED` (Next ยกเลิก prefetch ตอนเปลี่ยนหน้า) = ปกติ ไม่ใช่ scenario พัง
- ตัวเลขชวนสงสัยที่ runtime เห็นเอง: ส่วนลด 10% ของ ฿207 = 20 และของ ฿69 = 6 (ปัดลง) · แถบส่งฟรีใช้ยอดก่อนหักส่วนลด (999 − 69 = 930) — เป็นวัตถุดิบดีสำหรับคำถาม "กฎธุรกิจจริงคืออะไร"
- HAR มี RSC prefetch 68 จาก 72 fetch → API จริงจมอยู่ในเสียงรบกวน · ถ้าไม่มี REA/summarize ผู้เรียนจะหลงในไฟล์ 1.6 MB
- หน้า `/products/[slug]` และ `/orders/[id]` ไม่เรียก API คู่ของมัน (server component อ่านข้อมูลเอง) → อธิบายได้ว่าทำไม `/api/products/[slug]` `/api/orders/[id]` "มีแต่ไม่มีใครเรียก"
- การเทียบชื่อ chunk ใน HAR กับ `out\v1` เป็นวิธีถูก ๆ ที่ตอบ "ยังไม่รู้" ข้อสุดท้ายของ SYSTEM-MAP ได้ (container = build เดียวกัน)

## ปัญหา / วิธีแก้

- ไม่มีปัญหาทางเทคนิค: ทุกคำสั่ง exit 0 รอบแรก · network `pawpantry05_default` มีอยู่ · พอร์ต 4000 เป็นของ `pawpantry05` (sabai06 อยู่ 4100 ไม่ชน)
- `../tools/` ยังไม่มี playwright → ติดตั้ง `playwright@1.63.0` (browser cache ใช้ร่วมกับ `w/rea` ที่เป็น 1.63.0 อยู่แล้ว)

## ข้อเสนอแก้พรอมต์ (ระดับ H = ทำต่อไม่ได้/ผลผิด · M = ได้ผลแต่สับสน · m = ถ้อยคำ)

- **M** ข้อ 4 ส่วน A ขอ "ค่าตัวอย่าง" แต่ `rea-summarize.mjs` ไม่แสดงค่า และห้ามเปิดไฟล์ใหญ่ → เสนอ: เพิ่มตัวเลือก `--samples` ใน `rea-summarize.mjs` (พิมพ์ body ย่อของ API ที่ไม่ถูกปิด) หรือเขียนในพรอมต์ว่า "ค่าตัวอย่างให้เขียนสคริปต์อ่านใน `rea\scratch\`"
- **M** ข้อ 2 ใส่รหัสผ่าน demo ตรง ๆ ในคำสั่ง (`--sensitive-value <รหัส demo>` และใน Select-String) ขณะที่ ✔️ บอก "ไม่มีรหัสผ่านในไฟล์ .md ใด ๆ" → agent ที่คัดคำสั่งลง API-INVENTORY.md (ส่วน D/ภาคผนวก) จะทำผิดเอง · เสนอเพิ่มวงเล็บ "(ถ้าคัดคำสั่งลงเอกสาร ให้เขียน `<รหัส demo>` แทน)"
- **m** ข้อ 3 "step ผ่านกี่ step" — summarize ให้ `steps_completed: "11/11"` ตรงตัวแล้ว · แต่ "ข้อความใน accessibility tree เรื่องคูปองและยอดเงิน": summarize ตัดบรรทัด `term: ยอดชำระทั้งหมด` ออก (เหลือแค่ `definition: ฿113`) ต้องหาเพิ่มเอง · เสนอให้ filter ของ summarize เก็บคู่ term/definition
- **m** ข้อ 1 "จดเวลาแต่ละขั้นจาก out\har-steps.json" ✅ ใช้ได้ (stdout ก็พิมพ์อยู่แล้ว)

## ภาพที่ควรใช้ใน README (../design/shots/lab3-*.png 1280×800 + คำอธิบาย 1 บรรทัด)

- `lab3-cart-paw10-localhost.png` — หน้าตะกร้าที่ `localhost:4000` หลังใช้ PAW10 (1 ชิ้น: ส่วนลด -฿6 ยอด ฿113) = ภาพเดียวกับที่ REA เห็นผ่าน `petshop:3000` "เว็บเดียวกัน คนละประตู"
- `lab3-rea-scenario-final.png` — `out\scenario-final.png` ของ REA วางบนกรอบ 1280×800 พร้อมคำบรรยาย (ภาพดิบ 1280×720 อยู่ที่ `lab3-scenario-final-raw.png`)
