# LAB 9_RESULT · พิสูจน์ว่าแก้แค่ที่ตั้งใจ + CHANGE-REPORT
| หัวข้อ | ค่า |
|---|---|
| เวลาเริ่ม · จบ · ใช้ไป | 2026-10-12 10:42 · 10:53 · ~11 นาที (เครื่อง ~4.2 · agent ~7) · เครื่อง = build v2 155.2 วิ + REA 7+2 คำสั่ง 83.2 วิ + rea-input 5 ครั้ง ~2.4 วิ + record-har 3.2 วิ |
| cwd ของเซสชัน / settings มีผลไหม | runner (Agent tool · cwd ไม่ใช่ w/) · ทุกคำสั่งรันจาก `C:\t\work\run05\w` · `w/CLAUDE.md` + `.claude/settings.json` **บังคับเอง** (ไม่ได้แก้โค้ด · ไม่แตะ e2e-legacy/TEST-DATA · ไม่เปิด _solution · ไฟล์ใหญ่ใน out/ อ่านผ่าน rea-summarize เท่านั้น) |
| ไฟล์ที่สร้าง/แก้ | `w/CHANGE-PROOF.md` (ใหม่ · 142 บรรทัด) · `w/CHANGE-REPORT.md` (ใหม่ · 62 บรรทัด) · ผลใน `out\`: `v2\` (build) `v2-server.json` `v1-src.json` `v2-src.json` `s2b.in.json` `s2b-*.json` ×4 `cmp.in.json` `cmp.json` `after\{pawpantry-main.har,har-steps.json,har.json}` · ไม่แตะ `petshop/` |
| สคริปต์ชั่วคราว | ไม่มีใน `rea\scratch\` (พรอมต์ไม่ต้องใช้) · runner: `../tools/lab9/rea-timed.ps1` (ห่อคำสั่ง REA ตรงตัว + จับ exit/เวลา/ขนาด/evidence · stderr → `../tools/lab9/<tag>.err`) · `evid.mjs` (อ่าน evidence_id 11 ตัว) · `rea-log.tsv` · `hash-table.csv` · `build-v2.log` |
| โหมดการรัน · shell ที่ agent ใช้จริง | A · PowerShell tool (Windows PowerShell 5.1) สำหรับทุกคำสั่งในพรอมต์ · Git Bash เฉพาะงานอ่าน/นับของ runner (`rea-summarize` · `ls` · `git diff --no-index --numstat`) |
| timeout / รันซ้ำ | build v2 รันเบื้องหลัง (timeout 20 นาที) รอจนจบ ไม่สั่งซ้ำ · REA ตั้ง 10–15 นาที · ไม่มีคำสั่งใดรันซ้ำเพราะ timeout · ข้อ 1 (hash) รัน 3 รอบ: รอบ 1 พังเพราะชื่อฟังก์ชัน `H` ชน alias `Get-History` · รอบ 2 ได้ผลผิด (ดูปัญหา) · รอบ 3 ถูก |
| สถานะเว็บ | pawpantry05 healthy (Up ตั้งแต่ 10:28 · image build 10:28:03 จาก source แก้ล่าสุด 10:27:45) · ไม่ได้ rebuild ใน LAB นี้ · ไม่แตะ sabai06-* / exref-* |
| ข้อมูลทดสอบ | reset 1 ครั้ง (โดย `record-har.mjs` ก่อนบันทึก HAR) · ผู้ใช้ demo (TEST-DATA) · ออเดอร์ `PP-100001` |

## ข้อห้ามที่ทำตาม (และที่พลาด ถ้ามี)
- ไม่แก้โค้ด (`git status` ยังเป็น 6 ไฟล์ ` M` เดิมจาก LAB 6/8) · `git diff --stat -- e2e-legacy TEST-DATA.md` **ว่าง** · ไม่มีการเขียนไฟล์ต้องห้ามผ่าน shell
- ไฟล์ .json ใหญ่ใน out/ ไม่เปิดตรง: ใช้ `rea-summarize` (+ `--md` `--all` `--s2b-table`) · runner อ่าน `evidence_id` ด้วย `../tools/lab9/evid.mjs` (JSON.parse แล้วพิมพ์ 2 ค่า ไม่แสดงเนื้อหา) เพื่อจดหน้าที่ runner · `har-steps.json` (1 KB) อ่านค่า total_ms ตรง
- ไม่ใช้ `rea\scratch\har-peek.mjs` อ่าน key ชั้นในของ HAR เพราะส่วนที่ 2 บอก "ย่อด้วย rea-summarize เท่านั้น" → key ชั้นในบันทึกเป็น "พิสูจน์ไม่ได้"
- ไม่เปิด `_solution/` · ไม่อ่าน LAB อื่น / REA-FEASIBILITY (อ่าน 🎯 ของ LAB 9 ได้ตามกติกา แต่ไม่ใช้เป็นคำตอบ)
- รหัส demo ถูกส่งเป็น `--sensitive-value` ตามพรอมต์ · log ของ runner แทนค่าด้วย `<demo-password>` แล้ว · ไม่มีใน result/เอกสาร
- ไม่ได้รัน regression (พรอมต์ LAB 9 ไม่สั่ง) → เลี่ยงปัญหาสต็อกหมดของ `test:all` จาก LAB 8 ได้เอง

## คำตอบสรุปที่แสดงในแชท
ส่วนที่ 1 (ตารางท้าย CHANGE-PROOF.md):
> | หลักฐาน | บอกอะไร | ตรงกับที่ตั้งใจไหม |
> |---|---|---|
> | SHA-256 `out\v1` vs `petshop` (ข้อ 1) | source ต่าง 6 ไฟล์ · มีแค่ v1 1 ไฟล์ (`next-env.d.ts`) · เหมือน 114 | ✅ 6 = ไฟล์ใน BUG-01.md + CR-01.md · ส่วนเกิน 1 = ไฟล์ที่ build สร้าง |
> | build v2 (`out\v2` · exit 0 · 155.2 วิ) + `ev_54c61f33` | โค้ดใหม่ build ผ่าน (TypeScript ผ่าน) · build สร้าง `next-env.d.ts` ตัวเดียวกับ v1 | ✅ |
> | s2b คู่เวอร์ชันเดียวกัน `ev_23cd4cec` `ev_f47a7dd1` | 44/0/0/0/0/8/3 ทั้งคู่ → source แต่ละรุ่นตรงกับ build ของตัวเอง | ✅ |
> | s2b คู่ข้ามเวอร์ชัน `ev_b034f50f` `ev_ba4bd111` | 41/0/0/0/0/5/9 → 6 ไฟล์ที่แก้กลายเป็น unknown · modified = 0 | ✅ 6 ไฟล์เดียวกับข้อ 1 · ไม่มีไฟล์อื่นเปลี่ยนใน bundle |
> | ตาราง 3 รายการ (ข้อ 4) | ตั้งใจ = hash ต่าง = bundle ต่าง | ✅ (⚠️ 1 ข้อ อธิบายได้) |
> | obligation ledger (ข้อ 5) | 15 ข้อมีหลักฐานผ่าน · 4 ข้อยังไม่มีหลักฐาน | ✅ เท่าที่มีหลักฐาน · ⚪ 4 ข้อห้ามถือว่าผ่าน |

ส่วนที่ 2:
> | หัวข้อใน CHANGE-REPORT | อ้างไฟล์ไหน |
> |---|---|
> | 1 ตารางสรุปงาน (ชนิดงาน · ไฟล์ +/− · test แดง/เขียว · regression · REA · พฤติกรรมที่เปลี่ยน · ความเสี่ยง · rollback) | `BUG-01.md` · `CR-01.md` §2–§6 · `CHANGE-PROOF.md` §1 §3 §5 · `git diff --no-index --numstat` |
> | 2 compare-application-versions | `out\cmp.json` (`ev_360083db`) |
> | 3 HAR รอบใหม่เทียบ API-INVENTORY | `out\after\har.json` (`ev_b1e9e721`) · `out\after\har-steps.json` · `API-INVENTORY.md` (`ev_4db99f23`) |
> | 4 สิ่งที่หลักฐานยังพิสูจน์ไม่ได้ | `CHANGE-PROOF.md` §5 · `CR-01.md` §2 §6 · `BUG-01.md` ยังไม่รู้ · `API-INVENTORY.md` §C |
> | 5 ไฟล์ผลที่อ้าง | ทุกไฟล์ข้างบน |

## ตัวเลขสำคัญ (นับจากไฟล์จริง พร้อมคำสั่งที่ใช้นับ)
- **ข้อ 1 hash** (`Get-ChildItem -LiteralPath -Recurse -File -Force` + `Get-FileHash -LiteralPath -Algorithm SHA256` · ตัด `\node_modules\` `\.next\`): out\v1 121 · petshop 120 (= `git ls-files petshop | wc -l` 120) · union 121 → เหมือน **114** · ต่าง **6** · มีแค่ v1 **1** (`next-env.d.ts`) · มีแค่ petshop 0 · hash ว่าง 0
- ต่าง 6 = `app/orders/[id]/page.tsx` `components/CheckoutForm.tsx` `components/OrderSummary.tsx` `lib/orders.ts` `lib/pricing.ts` `lib/store.ts` · numstat เทียบ out\v1: +8−0 · +19−2 · +11−3 · +6−8 · +15−2 · +2−0 = **+61 −15** (ตรง `git diff --stat -- petshop`)
- `next-env.d.ts`: out\v1 mtime 09:36:33 (ช่วง build v1) · อยู่ใน `petshop/.gitignore` · หลัง build v2 เกิดไฟล์ SHA `1862AC4BBBC5…` เท่ากับ v1 · `tsconfig.json` `06D0A398B847` เท่ากันทั้ง v1/petshop/v2
- **ตัวนับ 7 คลาสดิบทุกคู่** (`--s2b-table` บรรทัดท้าย):
  - `s2b-v1src-v1build` `{"unchanged":44,"modified":0,"removed":0,"split":0,"merged":0,"duplicated":8,"unknown":3}`
  - `s2b-v1src-v2build` `{"unchanged":41,"modified":0,"removed":0,"split":0,"merged":0,"duplicated":5,"unknown":9}`
  - `s2b-v2src-v1build` `{"unchanged":41,"modified":0,"removed":0,"split":0,"merged":0,"duplicated":5,"unknown":9}`
  - `s2b-v2src-v2build` `{"unchanged":44,"modified":0,"removed":0,"split":0,"merged":0,"duplicated":8,"unknown":3}`
  - รวม 55 ไฟล์ต่อคู่ · unknown คงที่ 3 = `app/globals.css` `eslint.config.mjs` `next.config.ts` · duplicated 8 = `components/AuthShell.tsx` + `lib/{auth,catalog,orders,pricing,products,store,validation}.ts`
  - ตาราง 4 ทิศ: 6 แถวพอดี (3 ไฟล์ unchanged→unknown · 3 ไฟล์ lib duplicated→unknown ในคู่ข้ามเวอร์ชัน)
  - ไฟล์ "ไม่ต้องแตะ" 8 ไฟล์ของ CR-01 §3: `unchanged exact` ในคู่ข้ามเวอร์ชัน (`--md --all` ของ `s2b-v2src-v1build`)
- import-reference-source: v1 / v2 = 154 entries · 58,226 B ทั้งคู่ · root `ae1f32c6afb8` / `087ee24a43b9` · languages 8 · `inventory_state: partial` · ไม่มี evidence_id
- analyze v1 (`ev_ac8d9821`) files 445 · edges 1,868 · limitations 202 / v2 (`ev_54c61f33`) files 445 · edges 1,859 · limitations 213 · coverage partial/partial ทั้งคู่ · v2 nodes: javascript-module 174 · source-module 729 · unknown 207 · javascript-asset 169 · endpoint 60 · artifact 89 · source-map 95 · electron-renderer 2
- **compare-application-versions** `ev_360083db`: unchanged 0 · added 0 · removed 0 · changed 235 · unknown 1,465 · items_total 1,700 · by kind (changed/unknown): unknown 101/116 · source-module **6**/730 · javascript-module 0/314 · source-map 12/84 · javascript-asset 103/69 · electron-renderer 0/4 · endpoint 0/70 · artifact 13/78
- **HAR หลังแก้** `ev_b1e9e721`: 97 records (เดิม 97 `ev_4db99f23`) · API 4 ตัวเดิม status 200/200/201/200 เท่าเดิม · `POST /api/orders` req keys `items coupon shipping payment address` **+ `giftWrap`** · res keys ชั้นบน `order id` เท่าเดิม · har-steps 8/8 · total_ms 2,919 (เดิม 3,080)
- ledger: 19 ข้อ (positive 11 · negative 4 · malformed 3 · positive-เปลี่ยนโดยตั้งใจ 1) → ✅ 15 · ❌ 0 · ⚪ 4 (O9 คูปองหมดอายุ/มั่วเข้า `/api/orders` ตรง · O14 body ผิดรูปอื่น · O18 key ชั้นในของ response · O19 ส่งฟรีก่อน/หลังส่วนลด)

## คำสั่งที่รัน (REA/docker/playwright: คำสั่ง | exit | เวลา | ขนาดผล)
| คำสั่ง | exit | เวลา | ขนาดผล | evidence_id 8 ตัว | stderr |
|---|---|---|---|---|---|
| `robocopy petshop out\v2 /E /XD node_modules .next /NFL /NDL /NJH /NJS` | 1 (สำเร็จ) | 0.12 วิ | 120 ไฟล์ | – | – |
| `docker run --rm -v "${PWD}\out\v2:/app" -w /app -e NEXT_TELEMETRY_DISABLED=1 node:24-alpine sh -c "npm ci --no-audit --no-fund && npm run build"` | 0 | 155.2 วิ | `.next` · added 348 packages in 2m · Compiled 3.5s · TypeScript 8.1s | – | `build-v2.log` (npm warn deprecated ถูก PS 5.1 ห่อเป็น NativeCommandError แต่ exit 0) |
| `REA -Out out\v2-server.json analyze-javascript-application /work/out/v2/.next/server --json` | 0 | 21.8 วิ | 54,072,942 | `ev_54c61f33` | 173,156 B (progress JSON 458 sequence · UTF-16 จาก PS 5.1 · ไม่ใช่ error) |
| `REA -Out out\v1-src.json import-reference-source /work/out/v1 --json` | 0 | 2.7 วิ | 58,226 | ไม่มี (root `ae1f32c6afb8`) | 0 |
| `REA -Out out\v2-src.json import-reference-source /work/out/v2 --json` | 0 | 2.7 วิ | 58,226 | ไม่มี (root `087ee24a43b9`) | 0 |
| `node rea\rea-input.mjs s2b out\v1-src.json out\v1-server.json out\s2b.in.json` | 0 | 0.45 วิ | 54,087,783 | – | – |
| `REA -Out out\s2b-v1src-v1build.json compare-source-to-bundle /work/out/s2b.in.json --json` | 0 | 9.0 วิ | 262,270 | `ev_23cd4cec` | 0 |
| `node rea\rea-input.mjs s2b out\v1-src.json out\v2-server.json out\s2b.in.json` | 0 | 0.44 วิ | 54,131,195 | – | – |
| `REA -Out out\s2b-v1src-v2build.json compare-source-to-bundle …` | 0 | 9.0 วิ | 264,070 | `ev_b034f50f` | 0 |
| `node rea\rea-input.mjs s2b out\v2-src.json out\v1-server.json out\s2b.in.json` | 0 | 0.44 วิ | 54,087,783 | – | – |
| `REA -Out out\s2b-v2src-v1build.json compare-source-to-bundle …` | 0 | 9.2 วิ | 257,300 | `ev_ba4bd111` | 0 |
| `node rea\rea-input.mjs s2b out\v2-src.json out\v2-server.json out\s2b.in.json` | 0 | 0.43 วิ | 54,131,195 | – | – |
| `REA -Out out\s2b-v2src-v2build.json compare-source-to-bundle …` | 0 | 9.1 วิ | 269,040 | `ev_f47a7dd1` | 0 |
| `node rea\rea-input.mjs compare out\v1-server.json out\v2-server.json out\cmp.in.json` | 0 | 0.69 วิ | 108,102,488 | – | – |
| `REA -Out out\cmp.json compare-application-versions /work/out/cmp.in.json --json` | 0 | 17.6 วิ | 9,336,638 | `ev_360083db` | 0 |
| `node rea\record-har.mjs --out out\after` | 0 | 3.2 วิ | HAR 1,602,013 · steps 1,160 | – | – |
| `REA -Out out\after\har.json inspect-web-network-capture /work/out/after/pawpantry-main.har har --sensitive-value <demo-password> --sensitive-value <อีเมล demo> --json` | 0 | 2.1 วิ | 1,766,785 | `ev_b1e9e721` | 0 |

เวลา REA = wall-clock ของ `powershell -File .\rea\rea.ps1` ทั้งก้อน (รวม docker run start) วัดด้วย Stopwatch ใน `../tools/lab9/rea-timed.ps1` · log ดิบ `../tools/lab9/rea-log.tsv`

## ตัวอย่างแถวเด่น 3–6 แถว (สำหรับ README)
| ไฟล์ | v1src→v1build | v1src→v2build | v2src→v1build | v2src→v2build |
|---|---|---|---|---|
| `lib/orders.ts` (BUG-01 + CR-01) | duplicated | unknown | unknown | duplicated |
| `app/orders/[id]/page.tsx` | unchanged | unknown | unknown | unchanged |
| `components/CheckoutForm.tsx` | unchanged | unknown | unknown | unchanged |

| ไฟล์ | ตั้งใจแก้ | hash | REA bundle | ตรงไหม |
|---|---|---|---|---|
| `lib/pricing.ts` | ✅ CR-01 | ต่าง | unknown ข้ามเวอร์ชัน | ✅ |
| `next-env.d.ts` | ❌ | มีแค่ out\v1 | ไม่อยู่ใน 55 ไฟล์ | ⚠️ อธิบายได้ (build สร้าง · v2 build ได้ไฟล์เดียวกันทุกไบต์) |

| ledger | ชนิด | ผล |
|---|---|---|
| O12 `giftWrap` = `"true"` `1` `"yes"` `null` → ไม่ห่อ | malformed | ✅ TC-GIFT-12 ×4 |
| O9 SUMMER20 ยิงตรงเข้า `POST /api/orders` | negative | ⚪ ไม่มี test |

## ตัดสินแทนผู้เรียน (คำถาม | คำตอบ | ที่มา 🧑/ตัดสินเอง | เหตุผล)
| คำถาม | คำตอบ | ที่มา | เหตุผล |
|---|---|---|---|
| ตาราง "ไฟล์ \| สถานะ" ต้องแสดงครบ 121 แถวไหม | แสดงแถวที่ไม่เหมือน 7 แถวเต็ม + สรุปไฟล์ที่เหมือน 114 ตามโฟลเดอร์ (รายการเต็มใน CSV ของ runner) | ตัดสินเอง (LAB 9 ไม่มี 🧑) | ตาราง 114 แถวของรูปภาพอ่านไม่ได้ประโยชน์ · ตัวเลขยังนับครบ |
| ledger ใช้หลักฐาน test จากไหน · ต้องรันเทสต์ใหม่ไหม | ใช้ผลรันจริงที่บันทึกใน `CR-01.md` §6 / `BUG-01.md` / `BASELINE.md` · ไม่รันใหม่ · ระบุเวลา source/image เพื่อยืนยันว่าเป็นโค้ดชุดเดียวกัน | ตัดสินเอง | พรอมต์ไม่สั่งรันเทสต์ ("ข้อที่ยังไม่มีหลักฐานให้เขียน ⚪") · `test:all` รอบเดียวทำสต็อกหมด (LAB 8) |
| import-reference-source ไม่มี evidence_id แต่พรอมต์ขอ "evidence_id_short ของทุกผล REA" | จด `root_sha256_short` + entries แทน และเขียนว่าไม่มี evidence_id | ตัดสินเอง | ไม่แต่งค่า |
| BUG-01 เป็น restructuring หรือ re-engineering | re-engineering (ขนาดเล็ก) ที่ทำด้วยวิธี restructuring · ให้เหตุผลตามนิยามในพรอมต์ (ผล server เปลี่ยน 2 กรณี) | ตัดสินเอง | นิยามในพรอมต์: restructuring = พฤติกรรมเดิม · ที่ ฿999 พฤติกรรม server เปลี่ยน |
| key ชั้นในของ `response.order` (giftWrap/giftWrapFee) | ไม่เปิดด้วยสคริปต์อื่น · ใส่ใน "สิ่งที่หลักฐานยังพิสูจน์ไม่ได้" + ledger O18 ⚪ | ตัดสินเอง | ส่วนที่ 2 ห้ามย่อไฟล์ใหญ่ด้วยวิธีอื่นนอกจาก rea-summarize |

## ข้อสังเกต 👀 (บทเรียนจากรอบจริง ไม่ใช่สรุปผลซ้ำ)
- **กับดัก `[id]` ใน PowerShell:** `Get-FileHash $_.FullName` (ไม่มี `-LiteralPath`) คืนค่าว่างโดยไม่ throw สำหรับ `app/orders/[id]/page.tsx` (และอีก 3 ไฟล์ที่มี `[id]` `[slug]`) → ค่าว่าง = ค่าว่างจึงนับเป็น "เหมือน" ได้ "ต่าง 5" แทน 6 · ไฟล์ที่ CR-01.md เตือนว่า "ลืมง่ายที่สุด" ดันหลุดจากหลักฐานชั้น source พอดี · จับได้เพราะเทียบกับ `git status`/`git diff --stat` — ควรสอนให้ cross-check ตัวนับกับ git เสมอ
- ชั้น bundle จับไฟล์นี้ได้ถูกต้อง (unknown ในคู่ข้ามเวอร์ชัน) → หลักฐาน 2 ชั้นช่วยกันจริง: ถ้าใช้ชั้นเดียวจะพลาด
- คู่ควบคุม (v1→v1 · v2→v2) ได้ตัวนับเท่ากันทุกตัว (44/0/0/0/0/8/3) → ส่วนต่าง 6 ในคู่ข้ามเวอร์ชันอ่านเป็น "6 ไฟล์ที่แก้" ได้ทันที · ไม่มีคู่ควบคุม ตัวเลข 41/5/9 อ่านไม่ออก
- `modified = 0` ทุกคู่จริง · ไฟล์ที่ถูกแก้ปรากฏเป็น unknown เท่านั้น · ไฟล์ใน lib ที่เป็น duplicated ก็กลายเป็น unknown เหมือนกัน
- compare-application-versions: unchanged **0** จาก 1,700 แม้ source เปลี่ยนแค่ 6 ไฟล์ — แต่ by_kind `source-module changed 6` ตรงกับจำนวนไฟล์ที่แก้ (ซ่อนอยู่ในรายละเอียด ไม่อยู่ใน summary · ยังไม่ได้ยืนยันว่าเป็น 6 ไฟล์เดียวกันเพราะ summarize ไม่แสดงชื่อ)
- import-reference-source ของ v1 และ v2 มีขนาดเท่ากันทุกไบต์ (58,226) แต่ root hash ต่าง — ขนาดไฟล์ผลบอกอะไรไม่ได้
- `next-env.d.ts` เป็นตัวอย่างดีของ "ต่างแต่ไม่ได้แก้": พิสูจน์ได้ 3 ทาง (gitignore · mtime ช่วง build · build v2 สร้างไฟล์เดียวกันทุกไบต์)
- `record-har.mjs` reset ข้อมูลเองก่อนบันทึก → รันระหว่างที่มีเทสต์อื่นใช้เว็บอยู่ไม่ได้ (รอบนี้ไม่มีชน)
- HAR เส้นทางหลักไม่ติ๊กห่อ แต่ request ยังมี `giftWrap` (UI ส่ง `false` เสมอ) → HAR บอกได้ว่า client ใหม่ส่ง key ใหม่ แต่ไม่ได้พิสูจน์ฟีเจอร์ห่อ

## ปัญหา / วิธีแก้
| ปัญหา | วิธีแก้ |
|---|---|
| `function H(...)` ชน alias `H` = `Get-History` (PowerShell) → error "Cannot bind parameter 'Id'" | เปลี่ยนชื่อเป็น `Get-TreeHash` |
| `Get-FileHash` / path ที่มี `[ ]` ได้ hash ว่าง (ไม่ throw) → ตารางข้อ 1 ผิด (ต่าง 5) | ใช้ `-LiteralPath` ทั้ง `Get-ChildItem` และ `Get-FileHash` · ตรวจว่า hash ว่าง = 0 · ได้ต่าง 6 ตรง git |
| robocopy exit 1 → PowerShell tool รายงาน "Exit code 1" | ตามพรอมต์ 0–7 = สำเร็จ · ไม่ต้องทำอะไร |
| `*>` / `2>` ของ docker/REA ใน PS 5.1 ห่อทุกบรรทัด stderr เป็น `NativeCommandError` (UTF-16) | exit code ยัง 0 · stderr ของ REA คือ progress JSON · บันทึกไว้ใน `../tools/lab9/*.err` |
| rea-summarize ไม่แสดง key ชั้นในของ response (`order.giftWrap`) | จดเป็น "พิสูจน์ไม่ได้" (ไม่ใช้ scratch script ตามข้อห้าม "เท่านั้น") |

## ข้อเสนอแก้พรอมต์ (ระดับ H = ทำต่อไม่ได้/ผลผิด · M = ได้ผลแต่สับสน · m = ถ้อยคำ)
- **M (เกือบ H)** ข้อ 1: เขียน "ใช้ `Get-FileHash -LiteralPath` (path มี `[id]` `[slug]`)" และ "ตรวจตัวนับกับ `git status --short petshop`" — ไม่งั้นได้ผลผิดเงียบ ๆ (ต่าง 5 แทน 6 · หลุด `app/orders/[id]/page.tsx`) ซึ่งผู้เรียนที่ไม่ cross-check จะรายงาน "ตรงกัน" ผิด หรือเห็น ⚠️ ปลอมในตาราง 3 รายการ
- **M** CHANGE-PROOF ขอ "evidence_id_short ของทุกผล REA" แต่ `import-reference-source` (HistoricalSourceGraph) ไม่มี evidence_id → บอกให้ใช้ `root_sha256_short` ที่ rea-summarize พิมพ์
- **M** ส่วนที่ 2 ข้อ 2 ขอ "keys ที่เพิ่ม" แต่ rea-summarize แสดงแค่ key ชั้นบน (`order` `id`) จึงไม่เห็น `giftWrap` `giftWrapFee` ใน `response.order` (ข้อห้าม "ย่อด้วย rea-summarize เท่านั้น" ห้ามทางอื่น) → ให้ rea-summarize แสดง key ชั้นที่ 2 ของ object ใน response (เช่น `order.*`) หรืออนุญาต `rea\scratch\` อ่าน key · (แก้ helper = งานผู้ดูแล ไม่ได้แก้เอง)
- **m** ข้อ 5 ไม่ได้บอกว่าหลักฐาน test ต้องรันใหม่หรือใช้ผลเดิม · และผลเดิมไม่มีไฟล์ reporter (มีแต่ใน CR-01.md) → เสนอ "อ้างผลรันใน CR-01.md/BUG-01.md ได้ · ถ้ารันใหม่ให้รันทีละเบราว์เซอร์ (`--project=`) เพราะ `test:all` ทำสต็อกหมด"
- **m** ข้อ 3 อาจบอกว่า `--s2b-table` แสดง "เฉพาะไฟล์ที่สถานะต่างกันระหว่างคู่" (ผู้เรียนอาจคิดว่าไฟล์อื่นหายไป)
- **m** ข้อ 2 robocopy: PowerShell tool / Claude Code แสดง "Exit code 1" เป็น error → พรอมต์บอกแล้ว (0–7) ใช้ได้ดี
- (ข้อสังเกตต่อ 🎯 ไม่ได้เทียบ REA-FEASIBILITY ตามคำสั่ง · ตัวเลขดิบทุกคู่อยู่ใน "ตัวเลขสำคัญ")

## ภาพที่ควรใช้ใน README (../design/shots/labN-*.png 1280×800 + คำอธิบาย 1 บรรทัด)
- ไม่ได้ถ่าย (LAB 9 เป็นงานเอกสาร/ตาราง · ไม่มีหน้าเว็บใหม่) · ผู้ทำรูปควรทำภาพจากตาราง 4 ทิศ + ตัวนับ 7 คลาส (หัวข้อ "ตัวเลขสำคัญ") และตาราง 3 รายการใน `w/CHANGE-PROOF.md` §4
