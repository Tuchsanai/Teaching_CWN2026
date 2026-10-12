# FIX6T · เพิ่มคำสั่งใน rea-tools + ปรับพรอมต์ LAB 2 / LAB 11 (บท 06)

agent FIX6T · 12 ต.ค. 2026 · ที่มา: `C:/t/work/b2run/design/results/LAB2_RESULT.md` §10 ข้อเสนอ 1–5 (runner ต้องใช้ `node -e` เองเพราะ rea-tools ไม่มีคำสั่งให้ evidence_id · สถิติ · ผล scenario · รายการหน้า)

## 1. สิ่งที่เปลี่ยน

| ไฟล์ | เปลี่ยนอะไร |
|---|---|
| `tools/rea-tools.mjs` | เพิ่ม 4 คำสั่ง (สไตล์เดิม: `node rea-tools.mjs <cmd> …` · ไม่มี dependency · พิมพ์ตาราง Markdown สั้น ๆ · UTF-8 ไม่มี BOM · LF) + บรรทัดวิธีใช้ในหัวไฟล์ · คำสั่งเดิมไม่แตะ |
| `tools/.gitignore` | เพิ่ม `package-lock.json` (ข้อเสนอ 5: `npm install` ทำให้ lock โผล่ใน `git status`) |
| `_solution/_design/PROMPTS.md` | LAB 2 + LAB 11: ใช้คำสั่งใหม่ · `2> rea-out\<ชื่อ>.log` ทุกคำสั่ง `rea.ps1` · คำเตือนบรรทัดเดียวว่า record-har reset + จอง B14 + ยกเลิก B05 · **ผลที่คาด** เพิ่มตัวเลขจากการทดสอบนี้ (LAB 2) และผลคาดของ `pages` v1↔v2 (LAB 11 · [คาด]) |
| `_solution/_design/README-PART-B.md` | แก้ข้อความในกล่องพรอมต์ LAB 2 + LAB 11 **ตรงตัวเหมือน PROMPTS.md** (สคริปต์เดียวกัน 14 คู่ แต่ละคู่ต้องเจอ 1 ครั้งพอดี) |
| `fast_track/README.md` | ขั้นที่ 2 และ 11 ใช้คำสั่งชุดเดียวกัน → แก้ทั้งแบบบอกใบ้และไม่บอกใบ้ (10 คู่ แต่ละคู่ต้องเจอ 2 ครั้งพอดี = สองแบบยัง "คำสั่งเหมือนกันทุกตัวอักษร") |
| `_solution/_design/PREP.md` | P6: แถว `.gitignore` และ `rea-tools.mjs` บันทึกว่ามีการเพิ่มของ FIX6T |

### คำสั่งใหม่

| คำสั่ง | ใช้แทน (ใน LAB 2 รอบ RUNNER) | ทำอะไร |
|---|---|---|
| `ids <ไฟล์หรือโฟลเดอร์ ...>` | `node -e` อ่าน `.evidence_id` | ตาราง ไฟล์ · ขนาด (byte) · operation · ป้าย `[E ev_xxxxxxxx]` · หมายเหตุ (view ของใคร · records x/y · completeness · coverage) · ไฟล์ที่ไม่ใช่ Evidence (HAR ดิบ, PNG) ได้ป้าย `[E <ไฟล์> sha256 xxxxxxxx]` ตามกติกา M3 · input ของ view/compare ได้ `-` · ส่งโฟลเดอร์ได้ (PowerShell ไม่ขยาย `*.json` ให้ node) |
| `summary <static.json \| summary.json>` | `node -e` อ่าน `.normalized_result.summary` | node ตามชนิด + edges · endpoint `/api/*` ไม่ซ้ำ + จุดอื่น · statistics · coverage application/semantic + unknown · ตาราง semantic family · จำนวน limitations (แยกรายไฟล์) · รับได้ทั้งผล analyze และผล inspect-analysis-view · Evidence ชนิดอื่นบอกให้ใช้คำสั่งที่ตรง |
| `scenario-sum <scenario.json> [regex]` | `node -e` อ่าน `.steps[].status` + ค้น DOM | step completed x/y + ตารางทุก step · URL สุดท้าย · API ที่หน้าเว็บเรียก (method/path/status/step) · ข้อความในหน้าสุดท้ายของ element ที่ `data-testid` ตรง regex (ค่าเริ่ม `total\|summary-service\|summary-when`) พร้อม `data-amount` · scenario ไม่ได้ขอ accessibility tree จึงอ่านจาก DOM สุดท้าย (บอกไว้ในผล) |
| `pages <static.json> [static-v2.json]` | `find … -name "page-*.js"` | ตาราง route ← `chunks/app/**/page-<hash>.js` + fetch ที่ REA เห็นในไฟล์นั้น · ใส่ 2 ไฟล์ = เทียบ v1/v2 (เหมือนเดิม / ไฟล์เปลี่ยน (hash ต่าง) / ใหม่ใน v2 / หายใน v2) สำหรับ LAB 11 |

## 2. ผลทดสอบกับผลจริงของ RUNNER LAB 2 (`C:/t/work/b2run/w/rea-out/` · อ่านอย่างเดียว · รันจาก `w/` หลังคัดลอก)

ทุกคำสั่ง exit 0 · `node --check` ผ่าน · ไฟล์ผลขึ้นต้นไม่ใช่ `ef bb bf` · รันซ้ำผ่าน PowerShell 5.1 ได้ผลเดียวกัน (ภาษาไทยแสดงถูก)

### `node tools\rea-tools.mjs ids rea-out`
```text
| ไฟล์ | ขนาด (byte) | operation | ป้ายแหล่ง | หมายเหตุ |
|---|---|---|---|---|
| har-api.json | 59,767 | inspect_web_network_capture | [E ev_6fbeaec6] | records 10/135 |
| journeys.har | 3,861,694 | - | [E journeys.har sha256 da902fa6] | HAR ดิบ 135 entries |
| scenario.json | 247,833 | capture_browser_scenario | [E ev_8dc23d9f] | completeness complete · 1590 ms |
| static-v1.json | 34,083,464 | analyze_javascript_application | [E ev_11d475e1] | coverage partial |
| summary-v1.json | 16,686 | inspect_analysis_view | [E ev_24390574] | view ของ ev_11d475e1 |
| view-v1.json | 34,083,529 | - | - | input ของ inspect-analysis-view (จาก ev_11d475e1) |
```

### `node tools\rea-tools.mjs summary rea-out\static-v1.json`
```text
## analyze_javascript_application [E ev_11d475e1]
input /work/rea-out/v1/.next/static · directory · root sha256 458a1f88

| ชนิด node | จำนวน |
|---|---|
| javascript-module | 549 |
| javascript-asset | 30 |
| javascript-chunk | 26 |
| endpoint | 13 |
| unknown | 8 |
| artifact | 1 |
| (edges) | 1401 |

endpoint ที่เห็น 14 จุด · /api/* ไม่ซ้ำ **9**: /api/auth/login /api/auth/logout /api/bookings /api/chat /api/courses /api/giftcards /api/price /api/quiz /api/test/reset
อื่น ๆ 5 จุด (ไม่ใช่ /api/ หรือชื่อที่ REA ประกอบไม่ได้): [[...]] [] /_next/image /_next/image [...]

| statistics | ค่า |
|---|---|
| relevant_files | 54 |
| nested_asar_containers | 0 |
| text_bytes_read | 884586 |
| invalid_utf8_files | 0 |
| parsed_javascript_files | 54 |
| visited_ast_nodes | 272719 |
| findings | 950 |
| modules | 346 |
| parse_failures | 0 |

coverage: application **partial** (truncated false) · semantic **partial** (truncated true) · unknown: application 8 · semantic 5029

| semantic family | status | retained | unknown |
|---|---|---|---|
| boundary | partial | 21 | 7 |
| call-flow | partial | 132 | 1753 |
| child-process | partial | 0 | 7 |
| closure | partial | 1222 | 7 |
| configuration | partial | 0 | 7 |
| data-flow | partial | 16541 | 999 |
| event | partial | 0 | 7 |
| object-flow | partial | 2593 | 2171 |
| promise-ownership | partial | 160 | 43 |
| request | partial | 58 | 14 |
| resource-lifecycle | partial | 0 | 7 |
| timer | partial | 2 | 7 |

limitations: 14 ใน Evidence นี้ (รายไฟล์ที่ติด resource constraint 7)
อ่านว่า: partial = หลักฐานไม่ครบ → "ไม่พบในหลักฐานนี้" ≠ "ระบบไม่มี"
```

### `node tools\rea-tools.mjs summary rea-out\summary-v1.json` (ย่อ)
```text
## inspect_analysis_view [E ev_24390574] (view ของ ev_11d475e1)
input /work/rea-out/v1/.next/static · directory · root sha256 458a1f88
(view summary ไม่มี graph → นับ node/endpoint ด้วย: node tools\rea-tools.mjs summary <static.json>)
…(ตาราง statistics เหมือนผลของ static-v1.json ทุกค่า — เทียบด้วย diff แล้ว)
coverage: application **partial** (truncated false) · semantic **partial** (truncated true) · unknown: application 8 · semantic 5029
view: complete-within-view · examined 579/627
limitations: 25 ใน Evidence นี้ (รายไฟล์ที่ติด resource constraint 7) · limitation_count ของ parent = 14
```

`summary rea-out\har-api.json` → `inspect_web_network_capture [E ev_6fbeaec6] — ไม่ใช่ผล analyze · ใช้ har-api / scenario-sum / cmp-sum / trace-sum แทน`

### `node tools\rea-tools.mjs scenario-sum rea-out\scenario.json`
```text
## capture-browser-scenario [E ev_8dc23d9f] · Chromium 153.0.8010.12 · 1590 ms · completeness complete

**step completed 12/12** (scenario_start + 11 action)

| # | step_id | action | status | ms | URL หลัง step |
|---|---|---|---|---|---|
| 0 | scenario_start | goto_start | completed | 489 | /services |
| 1 | open-book-S01 | click | completed | 66 | /services |
| 2 | step1-next | click | completed | 417 | /book?service=S01 |
| 3 | pick-date | fill | completed | 9 | /book?service=S01 |
| 4 | slots-ready | wait_for | completed | 28 | /book?service=S01 |
| 5 | pick-1500 | click | completed | 27 | /book?service=S01 |
| 6 | step2-next | click | completed | 33 | /book?service=S01 |
| 7 | contact-name | fill | completed | 8 | /book?service=S01 |
| 8 | contact-phone | fill | completed | 8 | /book?service=S01 |
| 9 | quote-ready | wait_for | completed | 288 | /book?service=S01 |
| 10 | step3-next | click | completed | 42 | /book?service=S01 |
| 11 | summary-ready | wait_for | completed | 41 | /book?service=S01 |

URL สุดท้าย: http://sabai06-web:3000/book?service=S01

| API ที่หน้าเว็บเรียก (method) | path | status | step |
|---|---|---|---|
| GET | /api/slots?service=S01&date=2026-10-12&type=single&people=1 | 200 | 4 |
| POST | /api/price | 200 | 9 |

| ข้อความในหน้าสุดท้าย (data-testid ~ /total|summary-service|summary-when/) | data-amount | ข้อความ |
|---|---|---|
| summary-service |  | นวดไทย 60 นาที |
| summary-when |  | วันเวลา: 12 ต.ค. 2026 15:00–16:00 |
| summary-line-total |  | ยอดสุทธิ ฿1,000 |
| summary-amount-total | 1000 | ฿1,000 |
| summary-total | 1000 | ยอดสุทธิ: ฿1,000 |

accessibility: not_requested (scenario ไม่ได้ขอ → ข้อความข้างบนมาจาก DOM สุดท้าย) · screenshot: captured (ดึงภาพด้วยคำสั่ง shot)
```

### `node tools\rea-tools.mjs pages rea-out\static-v1.json`
```text
| route | ไฟล์ใน bundle | fetch ที่ REA เห็นในไฟล์นี้ |
|---|---|---|
| `(layout)` | chunks/app/layout-a97cb37b93e372f4.js | /api/auth/logout |
| `/` | chunks/app/page-2f4537628f4a6913.js | - |
| `/_not-found` | chunks/app/_not-found/page-cf434c1cae1a618c.js | - |
| `/account` | chunks/app/account/page-83b95202345b0663.js | - |
| `/admin` | chunks/app/admin/page-dadae58f822605e0.js | /api/test/reset |
| `/book` | chunks/app/book/page-9a898da259b34563.js | /api/price /api/bookings |
| `/chat` | chunks/app/chat/page-0b73a8abeea42996.js | /api/chat |
| `/giftcard` | chunks/app/giftcard/page-4312d11baf132502.js | /api/giftcards |
| `/login` | chunks/app/login/page-47ae529c1984e3d3.js | /api/auth/login |
| `/package` | chunks/app/package/page-d20f38ead7ad76ba.js | - |
| `/quiz` | chunks/app/quiz/page-cd45195efb6b8e9c.js | /api/quiz |
| `/services` | chunks/app/services/page-18fe2ed928dfbf8d.js | - |
| `/skin` | chunks/app/skin/page-a6a8ff6031f02e91.js | - |
| `/therapists` | chunks/app/therapists/page-50ae6c2617f1ee95.js | - |
| `/transport` | chunks/app/transport/page-98446bf6a9033721.js | - |
| `/wallet` | chunks/app/wallet/page-fae3da03df857b03.js | /api/courses |

หน้า 14 route + /_not-found + layout · API route ดูด้วยคำสั่ง endpoints
"-" = REA ไม่เห็น fetch ที่ URL เป็นค่าคงที่ในไฟล์นี้ (ไม่ได้แปลว่าหน้านี้ไม่เรียก API: URL ที่ประกอบตอนรัน หรือข้อมูลที่อ่านฝั่งเซิร์ฟเวอร์ จะไม่โผล่)
```

### `pages` แบบเทียบสองเวอร์ชัน (ยังไม่มี v2 จริง → ทดสอบด้วยสำเนา static-v1 ที่ตัด `/skin` เปลี่ยน hash `/account` และเพิ่ม `/admin/reports` ใน scratchpad แล้วลบทิ้ง · แสดงเฉพาะแถวที่ไม่ใช่ "เหมือนเดิม")
```text
| route | v1 hash | v2 hash | สถานะ |
|---|---|---|---|
| `/account` | 83b95202 | 11112222 | ไฟล์เปลี่ยน (hash ต่าง) |
| `/admin/reports` | - | aaaabbbb | ใหม่ใน v2 |
| `/skin` | a6a8ff60 | - | หายใน v2 |
```

### เทียบกับตัวเลขที่ runner ได้ด้วย `node -e` (LAB2_RESULT §4)

| รายการ | runner (`node -e`/`find`) | คำสั่งใหม่ | ตรงไหม |
|---|---|---|---|
| evidence_id static / summary / HAR / scenario | ev_11d475e1 / ev_24390574 / ev_6fbeaec6 / ev_8dc23d9f | เหมือนกัน (`ids`) | ✅ |
| ขนาด static / summary / HAR / scenario | 34,083,464 / 16,686 / 3,861,694 / 247,833 B | เหมือนกัน | ✅ |
| statistics (relevant 54 · modules 346 · findings 950 · AST 272,719) | ตามนั้น | เหมือนกัน (`summary`) | ✅ |
| coverage application/semantic | partial / partial truncated | เหมือนกัน · unknown 8 / 5029 | ✅ |
| limitations | summary 14 · view 25 | `summary` บอกทั้งสองค่าและที่มา | ✅ |
| endpoint static | 9 จริง + เศษ 3 + `/_next/image` ×2 | `/api/*` 9 + อื่น 5 จุด | ✅ |
| หน้า | 14 + `_not-found` (+ layout) | 14 route + `/_not-found` + layout | ✅ |
| scenario | 12/12 completed · ฿1,000 | 12/12 · `summary-amount-total` 1000 · ฿1,000 | ✅ |

## 3. ตรวจความตรงของพรอมต์

| ตรวจ | ผล |
|---|---|
| กล่อง ```` ```text ```` ของ PROMPTS.md (25) อยู่ใน README-PART-B.md ตรงตัวทุกกล่อง | 25/25 ✅ (README-PART-B มีเพิ่ม 2 กล่องที่เป็นแผนผังโฟลเดอร์ ไม่ใช่พรอมต์ · เหมือนก่อนแก้) |
| fast_track: ทุกคู่แก้เจอ 2 ครั้ง (บอกใบ้ + ไม่บอกใบ้) | 10/10 คู่ ✅ |
| `2>` กับ `rea.ps1 -Out` | stdout เขียนในคอนเทนเนอร์ (`-Out`) ส่วน `2>` รับ stderr ของ powershell ลูก → ไม่ชนกัน (runner LAB 2 ใช้วิธีนี้ทุกคำสั่ง exit 0) · log ไปอยู่ใน `rea-out\` ที่ไม่ถูก commit อยู่แล้ว |

## 4. sandbox + MANIFEST

- คัดลอก `tools/rea-tools.mjs` `tools/.gitignore` → `C:/t/work/b2run/w/tools/` และ `PROMPTS.md` → `C:/t/work/b2run/design/PROMPTS.md`
- commit ใน `w/`: `a9d58de orchestrator: rea-tools subcommands` (2 ไฟล์ · +135/−1) · ไม่ได้ add `HANDOVER-CHECK.md` `docs/` ของ runner · หลัง commit `git status` = ` M HANDOVER-CHECK.md` `?? docs/` (`tools/package-lock.json` หายจาก untracked แล้ว)
- MANIFEST ใหม่ตาม PREP §4 → `C:/t/work/b2prep/MANIFEST.sha256` 180 บรรทัด · sha256 ของไฟล์ MANIFEST = `5c8dad28…ea4d` · ต่างจากเดิม 3 บรรทัด: `fast_track/README.md` `tools/.gitignore` `tools/rea-tools.mjs`
- `sha256sum -c --quiet` ใน `w/` → **ไม่ตรง 1 ไฟล์ `fast_track/README.md`** เพราะคำสั่งงานให้คัดลอกเฉพาะ helper + PROMPTS (fast_track ไม่ได้คัดลอกเข้า `w/`) · ถ้าต้องการให้ตรง: คัดลอก `fast_track/README.md` จากบทเข้า `w/fast_track/` แล้ว commit แยก (runner ไม่ได้ใช้ fast_track ระหว่าง LAB)

## 5. ข้อสังเกต

- ผลที่คาด LAB 2 ใน PROMPTS ยังเขียนเศษ endpoint ว่า "ชื่อย่อ `a` `b` `c`" แต่รอบ RUNNER ได้ `[[...]]` `[]` `[...]` (ไม่ได้แก้ในงานนี้ · ให้ผู้รวมผล RUNNER ตัดสิน)
- `pages` บอกได้แค่ว่า "ไฟล์ของหน้านั้นเปลี่ยน" (Next.js ใส่ content hash ในชื่อไฟล์) ไม่ได้บอกว่าเปลี่ยนตรงไหน · พรอมต์ LAB 11 เขียนกำกับไว้แล้ว
- ไม่ได้แตะ container ใด ๆ · ไม่ได้ใช้ git ใน repo คอร์ส
