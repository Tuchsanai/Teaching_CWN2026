# LAB 2_RESULT · REA ส่องของที่ build แล้ว → SYSTEM-MAP
| หัวข้อ | ค่า |
|---|---|
| เวลาเริ่ม · จบ · ใช้ไป | 2026-10-12 09:34 · 09:45 · 11 นาที (เครื่อง ~4 · agent ~7) |
| cwd ของเซสชัน / settings มีผลไหม | runner cwd ไม่ใช่ `w/` (รันคำสั่งทุกตัวด้วย `Set-Location C:\t\work\run05\w`) · `w/CLAUDE.md` และ `w/.claude/settings.json` **ไม่ได้ถูกบังคับโดย harness — runner ทำตามเองอย่างเคร่งครัด** |
| ไฟล์ที่สร้าง/แก้ | `w/SYSTEM-MAP.md` ใหม่ 149 บรรทัด · `w/out/v1/` (สำเนา petshop 120 ไฟล์ + `.next` 87 MB + node_modules) · `w/out/v1-static.json` `v1-server.json` `trace-coupon.in.json` `trace-coupon.json` · ไม่แก้ไฟล์อื่น |
| สคริปต์ชั่วคราว | ไม่มีใน `rea\scratch\` (ไม่ได้ใช้) · `../tools/lab2/build.log` (log ของ build) · `../tools/lab2/sha_start.txt` (SHA ตั้งต้น e2e-legacy/TEST-DATA) |
| โหมดการรัน · shell ที่ agent ใช้จริง | A · คำสั่งในพรอมต์ทั้งหมดรันด้วย **PowerShell tool** (Windows PowerShell 5.1) · Git Bash ใช้เฉพาะงานอ่าน/นับของ runner (grep/wc/sha256sum/date) ไม่ได้ใช้แทนคำสั่งในพรอมต์ |
| timeout / รันซ้ำ | build ตั้ง timeout 15 นาที (foreground) · REA analyze ทั้งสองตั้ง 15 นาที · ไม่มีการสั่งซ้ำ |
| สถานะเว็บ | `pawpantry05` Up · healthy · `GET /api/health` = `{"ok":true}` · ไม่ได้ rebuild container ใน LAB นี้ (เปิดค้างไว้) |
| ข้อมูลทดสอบ | ไม่ได้ reset · ไม่ได้ใช้ผู้ใช้ใด (LAB นี้ไม่เปิดเว็บ) |

## ข้อห้ามที่ทำตาม (และที่พลาด ถ้ามี)
- ไม่แก้ `petshop/` · ไม่เปิด `_solution/` (ไม่มีใน sandbox) · `git status` หลังจบ: untracked แค่ `.claude/ CLAUDE.md CODEBASE-MAP.md SYSTEM-MAP.md` (`out/` ถูก ignore)
- **ไม่เปิดไฟล์ `.json` ใน `out/` ตรง ๆ** — ใช้ `node rea\rea-summarize.mjs` (ค่าเริ่มต้น / `--md` / `--md --all`) เท่านั้น · ค่าที่ summarize ไม่แสดง (ไฟล์ของ `electron-renderer` · method) จดใน "ยังไม่รู้" แทนการขุด JSON
- ข้อที่ต้องบอกตามจริง: runner **grep ไฟล์ .js ใน `out/v1/.next/static/chunks/`** (ไม่ใช่ JSON ของ REA) เพื่อหาที่มาของ `a b c` · `/api/recommendations` · key `pp-*` — พรอมต์ไม่ได้ห้าม แต่ก็ไม่ได้สั่ง · ใน SYSTEM-MAP เขียนกำกับไว้ทุกจุดว่า "grep build เอง ไม่ใช่ REA"
- deny/เลี่ยง deny ผ่าน shell: ไม่มีการเขียนไฟล์ใน `e2e-legacy/` หรือ `TEST-DATA.md` · `git diff --stat -- e2e-legacy TEST-DATA.md petshop` = ว่าง · SHA-256 ของ `TEST-DATA.md` `e2e-legacy/*.ts` `package.json` `tests/*.ts` ตรงกับตอนเริ่ม LAB (`diff` ว่าง)
- ไม่แตะ container บทอื่น (`docker ps` ตอนเริ่มมีแค่ `pawpantry05` `multi-account-devtool` และ container ที่ไม่เกี่ยว) · ไม่แก้ helper ใน `w/rea/`
- ไม่ใช้ `>` / `Set-Content` กับ JSON (ผล REA ผ่าน `-Out` ตามพรอมต์)

## คำตอบสรุปที่แสดงในแชท
> | ส่วน | จำนวนแถว | ✅ | ⚠️ | ❓ |
> |---|---|---|---|---|
> | A · REA เห็นอะไร | 17 | – | – | – |
> | B1 · หน้าเว็บ | 12 | 12 | 0 | 0 |
> | B2 · API | 13 | 6 | 1 | 6 |
> | B3 · state | 8 | 0 | 2 | 6 |
> | **B รวม** | **33** | **18** | **3** | **12** |
> | C · คำตอบ | 5 ข้อ | – | – | – |
>
> C(5): 2 ตา 22 แถว (white+grey 21 · white+black 1 = `/api/health` จาก HEALTHCHECK) · ตาเดียว (white) 11 แถว → ตาที่สองต้องเป็น black-box (ยิง API ตรง / HAR / REA ขับเบราว์เซอร์ / ดูพฤติกรรม)

## ตัวเลขสำคัญ (นับจากไฟล์จริง พร้อมคำสั่งที่ใช้นับ)
| ค่า | static | server | ที่มา |
|---|---|---|---|
| evidence_id_short | `ev_64fa462f` | `ev_ac8d9821` | rea-summarize |
| subject_digest_short | `8887b53bc4b2` | `dcd04a88daaf` | rea-summarize |
| files | 21 | 445 | rea-summarize |
| node kinds | javascript-asset 21 · javascript-module 19 · unknown 10 · endpoint 9 · artifact 1 · storage 3 (รวม 63) | source-module 729 · javascript-module 185 · javascript-asset 169 · unknown 196 · artifact 89 · source-map 95 · endpoint 63 · **electron-renderer 2** (รวม 1,528) | rea-summarize |
| edges | 68 | 1,868 | rea-summarize |
| coverage (application/semantic) | partial/partial | partial/partial | rea-summarize |
| limitations | 16 | 202 | rea-summarize |
| endpoint แถวในสรุป | 9 (ของร้าน 6 + `a` `b` `c`) | 34 (ของร้าน 6 + `/` + noise header/query/cookie) | `ConvertFrom-Json` นับ `.endpoints.Count` |
| storage | local-storage ×3 (get/set/remove) `name: null` | ×3 เหมือนกัน · file_node `chunks/ssr/_01-bhf61ps_r7._.js` | rea-summarize |
| recovered_source_files | 0 | **52** (API route 12 · `page.tsx` 11 · app อื่น 2 · components 18 · lib 9) | `ConvertFrom-Json` + `Where-Object` |
| retained_on_file_nodes | 0 | 90 | rea-summarize |

trace คูปอง (`ev_d404eddd` · source `ev_ac8d9821…`): matched_seeds 13 · traced_nodes 16 · traced_edges 75 · terminal_paths 0 · native_handoffs 0 · observed_facts 149 · inferred_facts 3 · unknown/unavailable 0 · coverage partial · source_files = `app/api/coupons/validate/route.ts` (1 ไฟล์) · มี node `chunks/ssr/components_CartView_tsx_12yx7o-868btn._.js`

SYSTEM-MAP ส่วน B นับด้วย Git Bash: `awk '/^### B1/,/^## C/' SYSTEM-MAP.md | grep -E '^\| (…)'` → 33 แถว · `grep -cF "| ✅ |"` 18 · `"| ⚠️ |"` 3 · `"| ❓ |"` 12 · `"| white + grey"` 21 · `"| white + black"` 1 · `"| white |$"` 11

## คำสั่งที่รัน (REA/docker/playwright: คำสั่ง | exit | เวลา | ขนาดผล)
| คำสั่ง | exit | เวลา | ขนาดผล |
|---|---|---|---|
| `robocopy petshop out\v1 /E /XD node_modules .next /NFL /NDL /NJH /NJS` | 1 (= คัดลอกสำเร็จ) | 0.1 s | 120 ไฟล์ |
| `docker run --rm -v "${PWD}\out\v1:/app" -w /app -e NEXT_TELEMETRY_DISABLED=1 node:24-alpine sh -c "npm ci --no-audit --no-fund && npm run build"` | 0 | **159 s** (รวม npm ci · ไม่ได้แยกเวลา) · Next 16.4.0 Turbopack compile 3.7 s · TS 8.5 s | `.next` 87 MB · 24 route (`ƒ` ทั้งหมด) |
| `REA -Out out\v1-static.json analyze-javascript-application /work/out/v1/.next/static --json` | 0 | **38.7 s** | 54,420,963 B |
| `REA -Out out\v1-server.json analyze-javascript-application /work/out/v1/.next/server --json` | 0 | **37.6 s** | 54,029,530 B |
| `node rea\rea-summarize.mjs out\v1-static.json` | 0 | 0.4 s | – |
| `node rea\rea-summarize.mjs out\v1-server.json` | 0 | 0.2 s | – |
| `node rea\rea-input.mjs trace out\v1-server.json string coupons/validate incoming out\trace-coupon.in.json` | 0 | 0.5 s | 54,029,620 B (ห่อทั้ง evidence ของ server) |
| `REA -Out out\trace-coupon.json trace-application-feature /work/out/trace-coupon.in.json --json` | 0 | **10 s** | 262,894 B |
| `node rea\rea-summarize.mjs out\trace-coupon.json` (+ `--md --all`) | 0 | <1 s | – |

(`REA` = `powershell -NoProfile -ExecutionPolicy Bypass -File .\rea\rea.ps1`) · ทุก evidence_id ขึ้นต้น `ev_` · helper `rea-input.mjs` / `rea-summarize.mjs` ทำงานถูกต้องทุกครั้ง

## ตัวอย่างแถวเด่น 3–6 แถว (สำหรับ README)
| รายการ | REA เห็น | โค้ดบอก | ตรงไหม | ตา |
|---|---|---|---|---|
| POST `/api/coupons/validate` | static+server `call:fetch` (CartView chunk) · trace เจอ route.ts + CartView | `app/api/coupons/validate/route.ts:6` · `components/CartView.tsx:161` | ✅ | white + grey |
| GET `/api/recommendations` | ไม่มีใน endpoint (UI เรียกจริง แต่ URL เป็น template literal) | `components/FinderWizard.tsx:95` | ❓ | white + grey (grep build เอง) |
| GET `/api/auth/me` | กู้ได้แค่ชื่อไฟล์ route.ts จาก source map | `app/api/auth/me/route.ts:6` · UI ไม่เรียก | ❓ | white |
| localStorage `pp-*` | get/set/remove ×3 `name: null` | `components/ShopProvider.tsx:59-62` | ⚠️ | white + grey |
| `a` `b` `c` (static endpoint) | `call:Uv.delete` / `e.get` | โค้ด polyfill ทดสอบ `URLSearchParams` (`"https://a/c%20d?a=1&c=3"`) ไม่ใช่ API | 🟡 noise | grey |
| node `electron-renderer` ×2 (server) | ชนิด runtime ที่ REA จัด | แอปเป็น Next.js ไม่ใช่ Electron | ⚪/🟡 | grey |

## ตัดสินแทนผู้เรียน (คำถาม | คำตอบ | ที่มา 🧑/ตัดสินเอง | เหตุผล)
LAB 2 ไม่มีหัวข้อ 🧑 และพรอมต์ไม่มีจุด "ถามก่อน" — การตัดสินที่ทำเองระหว่างทาง:

| คำถาม | คำตอบ | ที่มา | เหตุผล |
|---|---|---|---|
| เกณฑ์ ✅/⚠️/❓ ในส่วน B | ✅ = REA เห็นตัวสิ่งนั้นและตรงโค้ด · ⚠️ = เห็นบางส่วน/ผิดชนิด · ❓ = ไม่เห็นตัวสิ่งนั้น (แม้กู้ชื่อไฟล์ route.ts ได้) | ตัดสินเอง | พรอมต์ไม่ได้นิยาม · ชื่อไฟล์จาก source map ไม่ใช่ endpoint (URL = 🟡) · เขียนเกณฑ์ไว้หัวส่วน B |
| หน้าเว็บที่ REA เห็นแค่ไฟล์ `page.tsx` นับ ✅ ไหม | ✅ (ป้าย 🔵 path · URL 🟡) | ตัดสินเอง | หน้าไม่มี fetch ให้จับ · ไฟล์ที่กู้ได้ตรงกับโค้ดทุกหน้า — ต่างจาก API ที่ REA ตั้งใจจับเป็น endpoint |
| แถวใน B ใช้รายการไหน | หน้า 12 (รวม 404) · API 13 (แยก GET/POST `/api/orders` ตาม CODEBASE-MAP C) · state 8 (ตาม CODEBASE-MAP E · localStorage 4 key รวมเป็น 1 แถว) | ตัดสินเอง | ตามโครง CODEBASE-MAP ตรงตัว |
| HEALTHCHECK `healthy` จาก `docker ps` นับเป็นตา black ไหม | นับ (1 แถว `/api/health`) | ตัดสินเอง | เป็นผลจากการเรียก API จริงจากข้างนอกโค้ด · เขียนกำกับที่มาไว้ |
| grep ไฟล์ build เองนับเป็นตา grey ไหม | นับ แต่เขียนกำกับ "grep build เอง ไม่ใช่ REA" (ใช้เป็นตาที่สองจริง 1 แถว = `/api/recommendations` · localStorage ใช้เป็นข้อมูลเสริม เพราะ REA เห็น storage เองอยู่แล้ว) | ตัดสินเอง | grey = มองของที่ build · แต่ต้องแยกให้เห็นว่า REA พลาด |
| `electron-renderer` มาจากไฟล์ไหน | ไม่ขุด JSON → ใส่ "ยังไม่รู้" | ตัดสินเอง | พรอมต์ห้ามเปิด JSON ใน out/ ตรง ๆ และ summarize ไม่แสดง |

## ข้อสังเกต 👀 (บทเรียนจากรอบจริง ไม่ใช่สรุปผลซ้ำ)
- **static (ของที่ browser ได้) กู้ source ได้ 0 ไฟล์ แต่ server กู้ได้ 52** — มุม "คนนอก" จริง ๆ เห็นแค่ static · ผลจาก server bundle คือมุม "ได้ไฟล์ deploy ทั้งก้อน" ควรสอนให้แยกสองมุมนี้ชัด
- REA **พลาด `/api/recommendations` ทั้งที่ UI เรียกจริง** เพราะ URL เป็น template literal — ตัวอย่างดีของ "ไม่เจอ ≠ ไม่มี" (grep build เจอทันที)
- key localStorage มีอยู่ใน bundle เป็นสตริงตรง ๆ (`i="pp-cart"`) แต่ REA ให้ `name: null` เพราะส่งผ่านตัวแปร — REA ไม่ทำ data flow ข้ามตัวแปร
- endpoint ฝั่ง server 34 แถว เป็นของร้านแค่ 6 ที่เหลือเป็นชื่อ header / OTel attribute / cookie / query — ผู้เรียนต้องคัด noise เอง ถ้าไม่สอนจะนับ "API 34 ตัว"
- ไม่ได้อ้าง skill ของ REA ในคำตอบ C(3) เพราะ `rea/README.md` (ที่พรอมต์สั่งให้อ่าน) ไม่ได้พูดถึง skill/แนวทาง "เมื่อไรไม่ควรใช้ REA" — คำตอบ C(3) จึงมาจากผลรันเทียบกับ CODEBASE-MAP
- REA ส่ง progress เป็นบรรทัด JSON (`rea_progress`) ออก stderr **492 บรรทัด (~88 KB)** ต่อการ analyze 2 ครั้ง — ในเซสชัน agent จริงจะกิน context มาก (runner ต้องเปิดจากไฟล์ที่ระบบเก็บไว้) · trace ใส่ `2>$null` แล้วเงียบ
- เวลาเครื่องเร็วกว่าที่คาด: build 159 s · analyze 38.7 s / 37.6 s · trace 10 s

## ปัญหา / วิธีแก้
- stderr progress ของ REA ท่วม output ของ tool (88 KB) → ดูผลจากบรรทัดที่พิมพ์เองท้ายคำสั่ง (`exit=… secs=… size=…`) · คำสั่ง trace ใส่ `2>$null`
- `robocopy` คืน exit 1 → tool รายงานว่า "Exit code 1" (error) แม้จะสำเร็จ · พรอมต์บอกไว้แล้วว่า 0–7 = สำเร็จ จึงไปต่อได้
- ไม่มีปัญหาอื่น · helper ทำงานถูกทุกครั้ง

## ข้อเสนอแก้พรอมต์ (ระดับ H = ทำต่อไม่ได้/ผลผิด · M = ได้ผลแต่สับสน · m = ถ้อยคำ)
- **H:** ไม่มี
- **M:** ข้อ 2 ให้เติม `2>$null` ท้ายคำสั่ง REA analyze (หรือให้ `rea.ps1 -Out` ทิ้ง/ย่อ stderr progress เอง) — progress 492 บรรทัดจะท่วม context ของ agent ผู้เรียน
- **M:** ข้อ 5 ไม่ได้นิยาม ✅/⚠️/❓ และไม่บอกว่า "REA เห็น" นับจาก static อย่างเดียวหรือรวม server (ชื่อไฟล์ route.ts จาก source map) — ผลนับ ❓ จะต่างกันมากระหว่างผู้เรียน · เสนอเติม "❓ = ไม่อยู่ในรายการ endpoint ของ REA (ถึงจะกู้ชื่อไฟล์ได้ก็นับ ❓ และเขียนกำกับ)"
- **M:** `rea-summarize.mjs` (ห้ามแก้ใน LAB) ไม่แสดงไฟล์ของ node `electron-renderer` และ method ของ endpoint — ถ้า LAB ต้องการให้อธิบาย electron-renderer ควรให้ helper แสดง label/path ของ node ชนิดที่ไม่คาด (ข้อเสนอแก้ helper สำหรับผู้ดูแลบท ไม่ใช่ runner)
- **m:** ข้อ 5 "ยืนยันด้วยตา" — ระบุว่าการ grep ไฟล์ build เองนับเป็น grey ได้ไหม และนับ HEALTHCHECK/`docker ps` เป็น black ได้ไหม
- **m:** ข้อ 6 (3) ถ้าต้องการให้อ้างแนวทางของ REA ("เมื่อไรไม่ควรใช้") ต้องบอกว่าอ่านจากไหน (`rea/README.md` ไม่มี)
- **m:** ข้อ 1 อาจบอกว่า exit 1 ของ robocopy จะถูกเครื่องมือ agent แสดงเป็น error (agent บางตัวจะหยุดหรือรันซ้ำ)

## ภาพที่ควรใช้ใน README (../design/shots/labN-*.png 1280×800 + คำอธิบาย 1 บรรทัด)
- ไม่ได้ถ่ายภาพ (LAB นี้ไม่เปิดเว็บ) · เสนอให้ผู้ทำรูปทำจาก result: (1) ตาราง static vs server (กู้ source 0 vs 52) · (2) แถว `/api/recommendations` ❓ คู่กับบรรทัด `fetch(\`/api/recommendations?${…}\`)` ใน bundle · (3) ตารางสรุป ✅18 ⚠️3 ❓12
