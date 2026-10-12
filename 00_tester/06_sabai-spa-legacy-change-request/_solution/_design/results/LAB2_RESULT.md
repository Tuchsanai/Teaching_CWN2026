# LAB 2 RESULT · มองแบบ black-box ด้วย REA (บท 06 สบายใจ สปา)

> รอบจริงรันที่ 4100/5533 · ผู้เรียนใช้ 4000/5433

## 1. ตารางหัว

| รายการ | ค่า |
|---|---|
| เวลาเริ่ม | 2026-10-12 09:46:23 |
| เวลาจบ (งานตามพรอมต์) | 09:50:30 · เขียน result เสร็จ ~09:55 |
| เวลาที่ใช้ | ~4 นาที ตามพรอมต์: npm install 3.8 วิ · docker cp 0.4 วิ · analyze **48.1 วิ** · summary 6.6 วิ · record-har 10.1 วิ · inspect HAR 2.1 วิ · scenario 3.5 วิ (REA วัด 1,590 ms) · ที่เหลือ = อ่านผล + เขียน REA-INVENTORY ~2 นาที · รวมเขียน result ~9 นาที |
| ไฟล์ที่สร้าง/แก้ใน w/ | สร้าง `docs/REA-INVENTORY.md` (18,387 B) · `rea-out/` ทั้งโฟลเดอร์ (ignored ผ่าน `.git/info/exclude`) · `tools/node_modules/` (ignored) · **`tools/package-lock.json` (untracked · ผลข้างเคียงของ npm install)** · ไม่ได้ commit (พรอมต์ไม่ได้สั่ง) |
| สคริปต์ชั่วคราว / log | `tools/lab2/` : `start.txt` · `rea-analyze.stderr.txt` (140 บรรทัด progress) · `rea-summary.stderr.txt` · `rea-har.stderr.txt` · `rea-scenario.stderr.txt` · `record-har.out.txt` · `endpoints.txt` · `har-records.txt` · `har-api.txt` — **stderr ของ REA ทุกคำสั่งถูก redirect ลงไฟล์เหล่านี้ (`2> ...`) เพื่อไม่ให้ progress หลายร้อยบรรทัดท่วม context** · `design/logs/lab2-npm-install.txt` |
| ภาพ | `design/shots/lab2-scenario-final.png` (คัดลอกจาก `w/rea-out/scenario-final.png` · 107,054 B · 1280×720 · ภาพที่ REA ถ่ายเอง) |
| สถานะเว็บตอนจบ | `sabai06-web` + `sabai06-db` เปิดค้าง healthy · `/api/health` → `{"ok":true,"db":true}` |
| ข้อมูลทดสอบ | `record-har.mjs` reset เองตอนเริ่ม (now = `2026-10-10T10:00:00+07:00`) แล้ว **จอง B14 และยกเลิก B05** → DB ตอนจบ ≠ สถานะ reset · scenario ของ REA หยุดที่หน้าสรุป ไม่กดยืนยัน (ไม่สร้างนัด) |
| พอร์ตที่ใช้จริง | เว็บ **4100**→3000 · db **5533**→5432 (D10) · health ใช้ `http://localhost:4100/api/health` · HAR ใช้ `http://127.0.0.1:4100` · REA scenario ผ่าน network `sabai06-net` ที่ `http://sabai06-web:3000` (ไม่ต้องแก้ scenario) · **ผู้เรียนเห็น 4000 / 5433** → เวลาเขียน README แปลง `4100`→`4000`, `127.0.0.1:4100`→`127.0.0.1:4000`, `5533`→`5433` |
| เซสชัน / โหมดสิทธิ์ | runner (Agent tool) ทำแทนเซสชันใหม่ของผู้เรียน · โหมด A · ใช้เครื่องมือ PowerShell สำหรับคำสั่งในพรอมต์ (cwd = `C:\t\work\b2run\w`) · ไม่ได้เปิด `claude -p`/`yolo.cmd` · ยังไม่มี `w/CLAUDE.md` / `w/.claude/settings.json` (สร้างใน LAB 4) → บังคับข้อห้ามของพรอมต์เอง (self-enforced) |

## 2. ข้อห้ามที่ทำตาม และจุดที่ทำต่างจากพรอมต์

- **ไม่เปิดโค้ดใน `web/` `db/`** · ไม่เปิด `_solution/` (ไม่มีใน w/) · ไม่เปิดไฟล์ JSON ของ REA ทั้งไฟล์ (static 33 MB ไม่เคย cat/Read)
- เรียก REA ผ่าน `powershell -NoProfile -ExecutionPolicy Bypass -File tools\rea.ps1` ทุกครั้ง · ไม่แก้ execution policy
- ข้อ 1 "ถ้า `rea-out\v1\.next\static` มีอยู่แล้ว ให้บอกผมก่อนลบ" → ตรวจแล้ว `exists=False` จึงไม่ต้องถาม
- **พอร์ต:** แทน 4000 ด้วย 4100 ใน health และ `record-har.mjs http://127.0.0.1:4100` · ไม่แตะ `pawpantry05` (4000) และ `exref-*`
- **จุดที่ใช้คำสั่งนอกรายการ "ใช้เฉพาะคำสั่งข้างล่าง"** (เพราะพรอมต์ไม่มีคำสั่งให้ข้อมูลที่ต้องเขียน):
  - evidence_id ย่อ · statistics/coverage/limitations ของ summary · สถานะ step และยอดใน scenario · cookie ของ login → ใช้ `node -e` สั้น ๆ ดึงเฉพาะฟิลด์ (`.evidence_id`, `.normalized_result.summary`, `.steps[].status`) ไม่ได้พิมพ์ไฟล์ทั้งไฟล์
  - ตารางหน้า (route) → `find rea-out/v1/.next/static/chunks/app -name "page-*.js"` (ชื่อไฟล์ใน bundle ที่คัดลอกมา · `rea-tools endpoints` พิมพ์เฉพาะ route ของ API)
- ไม่มี git ที่เปลี่ยนสถานะ (พรอมต์ LAB 2 ไม่สั่ง commit) · `git status --short` ตอนจบ: ` M HANDOVER-CHECK.md` (ค้างจาก LAB 1) · `?? docs/` · `?? tools/package-lock.json` · **ไม่เห็น `rea-out/`** ✔

## 3. คำตอบสรุปที่แสดงในแชท

> | แหล่ง | endpoint ที่เห็น | เวลา | coverage | evidence_id ย่อ |
> |---|---|---|---|---|
> | static bundle (79 ไฟล์ · 1.15 MB) | fetch **9** (`/api/price` `/api/bookings` `/api/auth/login` `/api/auth/logout` `/api/test/reset` `/api/chat` `/api/courses` `/api/quiz` `/api/giftcards`) + เศษ `[[...]]` `[]` `[...]` + `/_next/image` ×2 · ชื่อไฟล์ route **25** · หน้า **14** | analyze 48.1 วิ + summary 6.6 วิ | **partial** (semantic truncated · unknown 8 รายการ/7 ไฟล์) | `ev_11d475e1` (summary `ev_24390574`) |
> | HAR (135 record → เลือก 10) | **7 endpoint / 10 ครั้ง**: GET slots ·1 · POST price ·2 · POST bookings ·1 (201) · POST auth/login ·2 · POST bookings/{id}/cancel ·1 · POST auth/logout ·1 · GET admin/bookings ·2 | 10.1 วิ + 2.1 วิ | runtime_attribution unknown · เฉพาะเส้นทางที่เดิน | `ev_6fbeaec6` |
> | REA scenario (network `sabai06-net`) | 2 (GET slots · POST price) · **12/12 step completed** · ยอดหน้าสรุป **฿1,000** | 3.5 วิ (1,590 ms) | complete (equality_eligible) | `ev_8dc23d9f` |
>
> เขียน `docs/REA-INVENTORY.md` แล้ว: ตาราง endpoint 25 แถว (ป้าย static/runtime/inference/unknown + [E] ทุกแถว) · ตารางหน้า 14 + `_not-found` + layout · "สิ่งที่ REA ไม่เห็น" 8 ข้อ · คำถาม 8 ข้อ · "ค่าที่ล็อกได้เป็น [E]" 9 แถว (กำกับว่า [E] = ระบบทำอยู่ ไม่ใช่ควรทำ)

## 4. ตัวเลขสำคัญ (คำสั่งที่ใช้นับ)

| ตัวเลข | ค่า | คำสั่ง/แหล่ง |
|---|---|---|
| static bundle | 79 ไฟล์ · 1,149,873 B | `Get-ChildItem -Recurse -File rea-out\v1\.next\static` |
| `static-v1.json` | 34,083,464 B (~32.5 MiB) | `(Get-Item).Length` |
| `view-v1.json` | 34,083,529 B | ″ |
| `summary-v1.json` | 16,686 B | ″ |
| `journeys.har` | 3,861,694 B · 135 record | ″ · `normalized_result.total_records` |
| `har-api.json` | 59,767 B | ″ |
| `scenario.json` / `scenario-final.png` | 247,833 B / 107,054 B (1280×720) | ″ |
| analyze เวลา | 48.1 วิ (exit 0 · stderr 140 บรรทัด) | `Measure-Command` |
| statistics | relevant/parsed JS 54 · parse_failures 0 · modules 346 · findings 950 · AST nodes 272,719 · text bytes 884,586 | `summary.statistics` |
| coverage | application partial · semantic partial truncated · 12 family partial ทั้งหมด (request 58 · data-flow 16,541 · call-flow 132 · closure 1,222 · object-flow 2,593) · view complete-within-view 579/627 | `summary.coverage` · `normalized_result.coverage` |
| limitations | 25 รายการใน view (18 ทั่วไป + 7 รายไฟล์ heap/budget) · `limitation_count` ใน summary = 14 | `.limitations.length` |
| endpoint static | 9 จริง + 3 เศษ (`children.get`) + `/_next/image` ×2 = 14 บรรทัด | `rea-tools endpoints` |
| route file API | 25 | `rea-tools endpoints` |
| unknown files | 8 บรรทัด (polyfills ซ้ำ 2 → 7 ไฟล์) | `rea-tools endpoints` |
| หน้า | 14 + `_not-found` + `layout` | `find … -name "page-*.js"` = 15 |
| har-records | `--record 37 39 40 41 69 75 77 126 130 134` (10) | `rea-tools har-records` |
| HAR API | 7 endpoint / 10 ครั้ง | `rea-tools har-api` |
| scenario | 12 step (`scenario_start` + 11 action) completed · `summary-amount-total` data-amount 1000 · "ยอดสุทธิ: ฿1,000" | `steps[].status` · DOM ใน scenario.json |
| record-har log | reset 200 now 2026-10-10 · quote ฿1,000 · booked **B14** · account 8 bookings · B06 cancel disabled = true · cancel B05 ยกเลิกแล้ว · admin rows 2026-10-12 = 2 | `tools/lab2/record-har.out.txt` |
| sensitive | `<รหัสทดสอบ>` ×2 ไม่อยู่ใน `har-api.json` (false/false) · อยู่ใน `journeys.har` ดิบ 1 จุด (Nida) | `JSON.stringify().includes` · `grep -c` |

## 5. ตัวอย่างแถวเด่นสำหรับ README

| endpoint | static | HAR | ป้าย | แหล่ง |
|---|---|---|---|---|
| `/api/price` | fetch @ `app/book/page` | POST · 14 body keys · 200 ×2 | static + runtime | [E ev_11d475e1] [E ev_6fbeaec6] |
| `/api/bookings` | fetch @ `app/book/page` | POST · body + `quotedTotal` · **201** · B14 | static + runtime | [E ev_11d475e1] [E ev_6fbeaec6] |
| `/api/bookings/{id}/cancel` | ชื่อไฟล์ route เท่านั้น | POST · 200 · B05 ยกเลิก | runtime (static ไม่เห็น call) | [E ev_6fbeaec6] |
| `/api/slots` | ชื่อไฟล์ route เท่านั้น | GET `service,date,type,people` · 200 | runtime | [E ev_6fbeaec6] [E ev_8dc23d9f] |
| `/api/me/bookings` | ชื่อไฟล์ route เท่านั้น | ไม่เห็น (ทั้งที่ /account แสดง 8 นัด) | static (ชื่อไฟล์) · inference | [E ev_11d475e1] |
| ค่าที่ล็อก | scenario S01 เดี่ยว 1 คน 12 ต.ค. 15:00 → ฿1,000 · 12/12 step | | [E] | [E ev_8dc23d9f] |

## 6. ตัดสินแทนผู้เรียน

| คำถาม | คำตอบ | เหตุผล |
|---|---|---|
| `rea-out\v1\.next\static` มีอยู่แล้ว ลบไหม | ไม่ต้องถาม | ตรวจแล้วไม่มีโฟลเดอร์ (`exists=False`) |
| ตาราง endpoint ใส่แถวไหนบ้าง | ทุก route 25 ไฟล์ (union ของ static fetch + ชื่อไฟล์ route + HAR) | พรอมต์ต้องการคอลัมน์ "เห็นจาก static" กับ "เห็นจาก HAR" → ต้องโชว์ทั้งที่เห็นและไม่เห็น · route ที่มีแค่ชื่อไฟล์ใช้ป้าย "static (ชื่อไฟล์) · unknown" |
| ป้ายของ endpoint ที่ HAR เห็นแต่ static ไม่เห็น call | "runtime (static ไม่เห็น call)" + เหตุผลแบบ inference ในหัวข้อ 4 | ไม่ได้เปิดโค้ดยืนยัน จึงไม่เขียนว่า "เป็น template literal" เป็นข้อเท็จจริง |
| evidence_id ย่อ 8 ตัว | `ev_` + 8 hex แรก (เช่น `ev_11d475e1`) | ตามรูปแบบ `[E ev_xxxxxxxx]` ในพรอมต์ |

## 7. ข้อสังเกต 👀

- **static เห็น call แค่ URL ที่เป็นค่าคงที่**: `/api/slots` (มี query) `/api/admin/bookings?date=` และ `/api/bookings/{id}/cancel` ไม่อยู่ในรายการ fetch ของ REA ทั้งที่ HAR เห็นจริง → ตัวอย่างชัดว่าทำไมต้องมี HAR คู่กับ static
- **`/api/me` `/api/me/bookings` `/api/services` ไม่ถูกเรียกจากเบราว์เซอร์เลย** ทั้งที่ /account และ /services แสดงข้อมูล → หลักฐานชี้ว่าอ่านฝั่งเซิร์ฟเวอร์ (inference) · ผู้เรียนอาจเผลอสรุปว่า "route นี้ไม่ได้ใช้" ถ้าไม่ระวังคำว่า partial
- **body ของ login ว่าง** ในตาราง `har-api` เพราะ `--sensitive-value` ทำให้ REA ตัด `postData.text` ทั้งก้อน (ไม่ใช่ไม่มี body) — ผู้เรียนอาจงง
- **`/api/test/reset` ไม่อยู่ใน 10 record** ทั้งที่ record-har log บอก `reset 200` → record-har เรียก reset ผ่าน API context ไม่ผ่านหน้าเว็บ (ไม่ถูกบันทึกเป็นคำขอ /api ของ HAR ที่ `har-records` เลือก)
- `rea-tools endpoints` พิมพ์ unknown ซ้ำ (polyfills 2 ครั้ง) → 8 บรรทัด แต่ 7 ไฟล์
- `limitation_count` ใน summary = 14 แต่ array `limitations` ของ view มี 25 (รวมรายไฟล์) → ตัวเลขที่ README อ้างต้องระบุว่านับจากไหน
- record-har **แก้ข้อมูล** (จอง B14 · ยกเลิก B05) — LAB ถัดไปที่ต้องการสถานะ seed ต้อง reset ก่อน
- ภาพ `scenario-final.png` ขนาด 1280×720 (viewport ของ REA) ไม่ใช่ 1280×800 ตามมาตรฐานภาพของ RUNNER §6 (RUNNER บอกให้ใช้ภาพ REA เอง ไม่ถ่ายใหม่ → ใช้ตามนั้น)

## 8. เจอระหว่างทาง (นอก CR)

- `/api/test/reset` ถูกเรียกจาก bundle ของหน้า `/admin` (static `ev_11d475e1`) และ reset ตอบ 200 ในระบบที่ส่งมอบ — ปุ่ม/โค้ด reset อยู่ใน production bundle (สอดคล้องกับ H6 ❌ ของ LAB 1)
- cookie `sabai_session` อายุ 7 วัน (expires 2026-10-19 จาก HAR) — เกี่ยวกับ TC-SEC-04 (logout แล้ว cookie เดิมยังใช้ได้) ที่ LAB 1 เจอ · หลักฐาน black-box นี้ยืนยันเฉพาะอายุ cookie ไม่ได้ยืนยันบั๊ก

## 9. ปัญหาที่เจอ / วิธีแก้

- ไม่มี error · ทุกคำสั่ง exit 0
- REA เขียน progress ลง stderr หลายสิบ–ร้อยบรรทัด (analyze 140 บรรทัด) → redirect `2> C:\t\work\b2run\tools\lab2\rea-*.stderr.txt` ทุกคำสั่ง (ไม่กระทบ `-Out` เพราะ stdout เขียนในคอนเทนเนอร์)
- `npm install` สร้าง `tools/package-lock.json` ที่ไม่ได้ ignore → โผล่ใน `git status` เป็น untracked

## 10. ข้อเสนอแก้พรอมต์

1. **(H)** พรอมต์สั่ง "ใช้เฉพาะคำสั่งข้างล่าง" แต่ไม่มีคำสั่งใดให้ **evidence_id** · statistics/coverage อ่านได้ก็ต้องเปิด summary · สถานะ step/ยอดของ scenario ไม่มีคำสั่งสรุป → เพิ่มใน `rea-tools.mjs` เช่น `ids <file...>` (พิมพ์ evidence_id ย่อ + ขนาด) · `summary <summary.json>` (statistics/coverage/limitations) · `scenario-sum <scenario.json>` (step completed x/y + ข้อความ `summary-amount-total`) และใส่ในพรอมต์
2. **(H)** "ตาราง หน้า (route) ที่เห็นจากชื่อไฟล์ใน bundle" ไม่มีคำสั่ง → เพิ่ม `rea-tools pages <static.json>` หรือบอกให้ใช้ `Get-ChildItem rea-out\v1\.next\static\chunks\app -Recurse -Filter page-*.js`
3. **(M)** แนะนำให้ redirect stderr ของ REA ลงไฟล์ (`2> rea-out\*.log`) ในพรอมต์ เพื่อไม่ให้ progress ท่วม context ของ Agent
4. **(M)** บอกผู้เรียนว่า record-har **reset + จอง + ยกเลิก** (ข้อมูลเปลี่ยน) และ body ของ login จะว่างเพราะ `--sensitive-value`
5. **(L)** เพิ่ม `package-lock.json` ใน `tools/.gitignore` หรือ commit ไว้ล่วงหน้า (ไม่งั้น "ไปต่อได้เมื่อ … `git status` ไม่เห็น rea-out" ยังผ่าน แต่มี untracked เกินมา)
6. **(L)** ข้อ 2 "วาง --record ทั้งหมดที่ได้" ใช้ได้ดี (10 ค่า) · ข้อ 3 ผ่าน `sabai06-net` ใช้ได้โดยไม่ต้องแก้ scenario

## 11. ภาพที่ควรใช้ + เทียบกับผลที่คาด

- `design/shots/lab2-scenario-final.png` — หน้า "4. สรุปก่อนจ่าย" ที่ REA ถ่ายเองหลัง 12/12 step: นวดไทย 60 นาที · 12 ต.ค. 2026 15:00–16:00 · ยอดสุทธิ ฿1,000

> หมายเหตุความโปร่งใส: บล็อก "ผลที่คาด" อยู่ติดกับกล่องพรอมต์ของ LAB 2 ใน PROMPTS.md จึงเห็นตอนอ่านพรอมต์ (ไม่ได้ตั้งใจเปิดก่อน) · ตัวเลขทุกตัวข้างบนนับจากไฟล์/ผลจริง

| ผลที่คาด | ผลจริง | ตรงไหม |
|---|---|---|
| `docs/REA-INVENTORY.md` + `rea-out/` | มีทั้งคู่ | ✅ |
| static ~37 MB | 34,083,464 B (34.1 MB / 32.5 MiB) | ≈ (ต่ำกว่าคาด ~8%) |
| summary ~15 KB | 16,686 B | ✅ ≈ |
| HAR ~4 MB | 3,861,694 B | ✅ ≈ |
| `scenario-final.png` ~100 KB | 107,054 B | ✅ |
| endpoint จริง 9 (+ `a` `b` `c`) | 9 + เศษ `[[...]]` `[]` `[...]` + `/_next/image` ×2 | ✅ 9 · ⚠️ ชื่อเศษไม่ใช่ `a` `b` `c` (เป็นค่าจาก `children.get`) |
| route stub 25/25 | 25 | ✅ |
| หน้า 14 | 14 (+ `_not-found`) | ✅ |
| coverage partial | partial | ✅ |
| analyze ~53 วิ | 48.1 วิ | ✅ ≈ |
| HAR 7 endpoint / 10 ครั้ง | 7 / 10 | ✅ |
| scenario 12/12 ยอด ฿1,000 ผ่าน `sabai06-net` (ต้องยืนยัน PREP V7) | 12/12 completed · ฿1,000 · `-Network sabai06-net` → `http://sabai06-web:3000` สำเร็จ | ✅ **ยืนยันทาง network ได้** |
| "สิ่งที่ REA ไม่เห็น" อธิบาย `/api/me` `/api/services` (Server Component) และ `/cancel` (template literal) | มีทั้งสามประเด็น (เขียนเป็น inference: "ดึงข้อมูลฝั่งเซิร์ฟเวอร์" / "URL แทรก id") | ✅ |
| ทุกแถว endpoint มี `[E ev_…]` | 25/25 แถว | ✅ |
| ไปต่อได้: ไม่มี "ระบบไม่มี…" · คำถาม ≥ 5 · `rea-out/` ไม่ถูก commit | `grep "ระบบไม่มี"` = 0 · คำถาม 8 · `git status` ไม่เห็น rea-out | ✅ |
