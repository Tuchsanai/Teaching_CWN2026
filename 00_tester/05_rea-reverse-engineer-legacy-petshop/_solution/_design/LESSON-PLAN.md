# LESSON-PLAN · บท 05 `05_rea-reverse-engineer-legacy-petshop` (งาน B1 · 12 ต.ค. 2026)

> แผนการสอน + ข้อตัดสินใจของบท · อ่านคู่กับ `PROMPTS.md` (พรอมต์ทุก LAB) และ `RUNNER.md` (วิธีรันจริง)
> ที่มา: `REA-THEORY.md` `REA-FEASIBILITY.md` `METHODS.md` `CODEBASE-NOTES.md` `CR-DESIGN.md` `STYLE-GUIDE.md` และ `06/_solution/_design/LEGACY-TESTSUITES.md`
> **ตัวเลขเวลาในแผนนี้เป็นค่าประมาณ** (ยังไม่ได้รันพรอมต์ฉบับนี้) · ตัวเลขผลจริงทุกตัวใน README ต้องมาจาก `results/LABn_RESULT.md` ที่ RUNNER เขียน

## 0. ข้อตัดสินใจของบท (ฉบับสุดท้าย)

| เรื่อง | ตัดสิน | เหตุผล |
|---|---|---|
| BUG_MODE | **เอาออกทั้งหมด** (พฤติกรรม = `BUG_MODE=0` เดิม) | ตาม `CR-DESIGN` §3 · ระบบเดิมจริงไม่มีสวิตช์บอกบั๊ก · `grep bugMode` เฉลย 3 บั๊กใน 10 วินาที · ไม่มี `data-bug-mode` ให้ REA เห็น |
| BUG-01 | **อบลงโค้ดถาวร** (diff `CR-DESIGN` §2.2 ใส่หลังเอา BUG_MODE ออก) | ฿999 พอดี: หน้าเว็บส่งฟรี แต่คำสั่งซื้อจริง ฿1,049 · suite เดิมจับไม่ได้ = "เทสต์เขียว ≠ ไม่มีบั๊ก" |
| ลำดับงาน | เข้าใจ → ล็อก → **BUG-01 ก่อน** → CR-01 → พิสูจน์ | CR-01 แตะ `lib/orders.ts` ไฟล์เดียวกับต้นเหตุ BUG-01 · แก้แบบปลายเหตุ (`>`→`>=`) ทำค่าห่อหาย (`CR-DESIGN` §2.6) |
| ชุดเทสต์เดิม | `e2e-legacy/` ตัดจากบท 02 (40 test) ตาม `LEGACY-TESTSUITES` §4.1 · `BASE_URL` ค่าเริ่มต้น `http://localhost:4000` · ไม่ตัด test ข้อไหน (D3: ไม่มีข้อไหนจับ BUG-01 · 3 ข้อที่เคยจับ BUG_MODE ตอนนี้ตรวจพฤติกรรมที่ถูกเฉย ๆ) | ผู้เรียน **เพิ่ม** test ได้เฉพาะ `e2e-legacy/tests/new/` · ไฟล์เดิมล็อกด้วย `.claude/settings.json` (ผู้เรียนให้ agent เขียนใน LAB 1) |
| compose / ชื่อ (D7 D8) | `docker-compose.yml` บรรทัดแรก `name: pawpantry05` · `container_name: pawpantry05` · `image: pawpantry05:latest` · service ยังชื่อ `petshop` (= ชื่อ DNS ใน network) → network = **`pawpantry05_default`** | โฟลเดอร์ `petshop/` ของบท 02 03 05 ชื่อเดียวกัน ถ้าไม่ตั้ง `name:` project จะเป็น `petshop` ทั้ง 3 บท → `compose up/down` บท 05 ไป recreate/ลบ container ของบทอื่น · ห้ามใช้ชื่อ `petshop` `pawpantry` `sabai-*` |
| พอร์ต | เว็บ `localhost:4000` (D5) · `ports: "${WEB_PORT:-4000}:3000"` (เปลี่ยนได้เฉพาะตอนแก้ปัญหา/sandbox) · **REA ใน container เข้าเว็บทาง docker network `pawpantry05_default` ที่ `http://petshop:3000` (ทางหลัก D7)** · `host.docker.internal:4000` = ทางสำรอง ใช้เมื่อ RUNNER LAB 0 ทดสอบผ่านแล้วเท่านั้น · Playwright/เบราว์เซอร์บนเครื่องผู้เรียนใช้ `http://localhost:4000` | network ภายในคือแบบที่ `REA-FEASIBILITY` §3 พิสูจน์แล้ว ไม่ขึ้นกับ WinNAT/firewall/VPN · `host.docker.internal` ยังไม่เคยรัน และ resolve ได้ IPv6 (เสี่ยงกับ Chromium ใน container) |
| shell (D9) | ทุกพรอมต์มีบรรทัด "รันคำสั่งด้วย PowerShell" · `.ps1` เรียกด้วย `powershell -NoProfile -ExecutionPolicy Bypass -File …` เสมอ (ExecutionPolicy ค่าเริ่มต้น Windows 11 = Restricted) · คำสั่งที่นาน > 2 นาที (docker build · `npm ci && npm run build` · `compose up --build` · `npm run test:all` · `playwright install`) พรอมต์บอกให้ตั้ง timeout ≥ 10 นาที หรือรันเบื้องหลังแล้วรอจนจบ | Claude Code บน Windows ใช้ Git Bash เป็นค่าเริ่มต้นได้ → `${PWD}` ได้ `/c/...` และ MSYS แปลง `/work` (`REA-FEASIBILITY` §2.9) · timeout ค่าเริ่มต้นของเครื่องมือ 2 นาที → agent รันซ้ำ/สรุปผิด |
| image REA | build `rea-lab:6.4.0` ใน 🧰 **ก่อนเข้าคลาส** (ผู้เรียนรันในเทอร์มินัลเอง) · LAB 0 แค่ตรวจว่ามี | image ~2.65 GB ใช้เวลานานเกิน LAB 0 และเกิน timeout ของ agent |
| บท 05 กับบท 06 | ใช้ host port 4000 ทั้งคู่ → **รัน LAB ของสองบทพร้อมกันไม่ได้** บนเครื่องเดียว (ผู้เรียน: `docker compose down` บทหนึ่งก่อนเปิดอีกบท · RUNNER: ดู `RUNNER.md` "คิวพอร์ต 4000") | บท 06 รองรับ `WEB_PORT` (06 LESSON-PLAN P3) จึงย้ายไป 41xx ใน sandbox ได้ · บท 05 ก็รองรับ `WEB_PORT` แต่พรอมต์ฮาร์ดโค้ด 4000 |
| REA | ใช้เฉพาะคำสั่งที่ผ่านใน `REA-FEASIBILITY` §1: `doctor` · `analyze-javascript-application` (static+server) · `trace-application-feature` (seed `string` + `incoming`) · `inspect-web-network-capture` (+`--sensitive-value`) · `capture-browser-scenario` · `import-reference-source` + `compare-source-to-bundle` · `compare-application-versions` (ดูข้อจำกัดเท่านั้น) · MCP (ทางเลือก) | ตัวหลักที่ "พิสูจน์ว่าแก้แค่ที่ตั้งใจ" = source-to-bundle 4 ทิศ |
| เอกสารเก่า (D4) | เพิ่ม `petshop/HANDOVER-NOTES.md` ของทีมเดิม มีข้อเท็จจริงเก่า 2 ข้อ | สอน "เอกสารบอก ≠ โค้ดทำ" โดยไม่ชี้ตำแหน่ง BUG-01 |

## 1. เป้าหมาย · เรื่องเล่า · ประโยคหลัก

**เรื่องเล่า:** ทีมที่สร้าง PawPantry ลาออกหมดแล้ว เราได้ repo + เว็บที่รันอยู่ + ชุดเทสต์เก่า + เอกสารส่งมอบ 1 หน้า · ร้านส่งมาสองเรื่อง: ลูกค้าบ่นว่า "โดนเก็บเงินเกิน" (BUG-01) และอยากได้ "ห่อของขวัญ" (CR-01) · เราคือ tester ที่ทำงานคู่ Claude Code
**ประโยคหลัก:** **"โค้ดบอก ≠ ระบบทำ ≠ ร้านต้องการ"** · ลำดับงาน **"เข้าใจ → ล็อก → แก้ → พิสูจน์"**

| # | หลังจบบท ผู้เรียน… | วัดใน |
|---|---|---|
| O1 | อธิบาย RE ตาม Chikofsky & Cross · static vs dynamic · black/white/grey-box ได้ด้วยตัวอย่าง PawPantry **และติดป้ายงานของตัวเองได้** | Quiz 1–3 · LAB 1 ส่วน I · LAB 2 ส่วน C ข้อ 5 · LAB 9 ส่วนที่ 1 ข้อ 5 |
| O2 | สั่ง agent อ่าน repo แล้ว **รีวิว** `CODEBASE-MAP.md` + `CLAUDE.md` (แยก "ยืนยันจาก" กับ "เดา") | LAB 1 |
| O3 | ใช้ REA กับของที่ build/รันอยู่ แล้วอ่าน Evidence เป็น (authority · coverage · digest · หาไม่เจอ ≠ ไม่มี) และรู้ว่าเมื่อไร **ไม่ต้องใช้ REA** | LAB 2–3 |
| O4 | ล็อกพฤติกรรมเดิมด้วย characterization/golden master โดยไม่อบบั๊ก ([E] vs [D]) | LAB 4 |
| O5 | แก้บั๊ก/เพิ่มฟีเจอร์แบบ failing-test-first + impact analysis + แก้ที่ต้นเหตุ | LAB 5–8, 10 |
| O6 | พิสูจน์ว่าของที่ส่งมอบเปลี่ยนเฉพาะที่ตั้งใจ (digest + REA source-to-bundle + regression 3 เบราว์เซอร์) แล้วเขียน `CHANGE-REPORT.md` | LAB 8–9 |

**ต่างจากบทก่อน (ตาราง 📦):**

| | บท 03 | บท 04 | **บท 05 (บทนี้)** |
|---|---|---|---|
| ตอนเริ่มมี | เว็บ + TEST-DATA | บันทึกสัมภาษณ์ | **repo ที่ทีมเก่าทิ้งไว้ + เว็บ + ชุดเทสต์เก่า + เอกสารส่งมอบ** |
| เราอ่านโค้ดไหม | ห้าม (black-box) | ห้าม | **อ่านได้ + ส่องของที่ build ด้วย REA (3 ตา)** |
| ผลที่คาดหวังมาจาก | [D] [R] [O] | [D] [R] [A] [O] | **[D] [R] [E] [O]** (เพิ่มหลักฐานจากระบบ) |
| บั๊ก | BUG_MODE 3 ตัว | Claude เลือกเอง 3 ตัว | **ไม่มีสวิตช์ · บั๊กจริงจากลูกค้า 1 ตัว + ที่ซ่อนอยู่ 1 ตัว** |
| แก้ repo | ไม่ | สร้างใหม่ | **แก้ระบบเดิม ≥ 6/10 LAB** |
| ทักษะ | สำรวจ เขียนแผน | ครบวงจรสร้างใหม่ | **รับช่วงระบบ: เข้าใจ → ล็อก → แก้ → พิสูจน์ (ปูทางบท 06)** |

## 2. LAB (10 + LAB 0) · ✏️ แก้ repo = 6/10

| ช่วง | LAB | 🔍/✏️ | เป้าหมาย | input | output | ⏱️ ประมาณ |
|---|---|---|---|---|---|---|
| 🧰 | ก่อนเข้าคลาส (ไม่นับ LAB) | — | ผู้เรียนรันในเทอร์มินัล PowerShell เอง: `docker build -t rea-lab:6.4.0 rea` (image ~2.65 GB) | `rea/Dockerfile` | image `rea-lab:6.4.0` | ยังไม่เคยวัดบนเครื่องผู้เรียน (RUNNER จด) |
| ⚙️ | 0 เช็กเครื่อง | 🔍 | Docker · Node · **พอร์ตที่ Windows จอง** · ExecutionPolicy · มี image `rea-lab` · `rea.ps1 doctor` · เปิดเว็บ :4000 · REA เห็นเว็บใน network `pawpantry05_default` · npm install | `rea/` `petshop/` | (ตาราง) | ~10 (+ `compose up --build` ~3 · npm/playwright install ~3) |
| 🟢 เข้าใจ | 1 อ่าน repo → แผนที่ | 🔍 | Agent อ่าน + อธิบาย repo · เราตรวจ "ยืนยันจาก" · เอกสารบอก ≠ โค้ดทำ · **ติดป้ายงานตาม Chikofsky & Cross + ตาไหน (ส่วน I)** | `petshop/` `HANDOVER-NOTES.md` `TEST-DATA.md` `e2e-legacy/` | `CODEBASE-MAP.md` `CLAUDE.md` `.claude/settings.json` | ~12 |
| | 2 REA ส่อง build | 🔍 | build สำเนา v1 → analyze static/server → trace คูปอง → triangulation REA เห็น / โค้ดบอก / ตรงไหม · ติดป้าย 🔵🟢🟡⚪ · **แต่ละแถวยืนยันด้วยกี่ตา ตาไหน** | `CODEBASE-MAP.md` | `SYSTEM-MAP.md` · `out/v1/` (ห้ามแก้จนจบบท) | ~15 |
| | 3 HAR + scenario | 🔍 | ดูตอนรันจริง: HAR → API inventory (ปิดค่าลับ) · REA ขับเบราว์เซอร์ → ชื่อ key localStorage · เติม ⚪ จาก LAB 2 | `SYSTEM-MAP.md` `rea/*` | `API-INVENTORY.md` | ~10 |
| 🟡 ล็อก | 4 characterization | ✏️ | รัน suite เดิม 3 เบราว์เซอร์ · หาช่องว่าง · เขียน golden master เงิน 4 จุด + API golden · [E] ขัด [D] → test คู่ `test.fail` | `API-INVENTORY.md` `TEST-DATA.md` | `e2e-legacy/tests/new/char-*.spec.ts` `golden/*.json` `BASELINE.md` | ~20 |
| 🔵 แก้บั๊ก | 5 BUG-01 ทำซ้ำ + ต้นเหตุ | ✏️ | ข้อความลูกค้า → black-box ทำซ้ำ + HAR → **test แดง** → white-box หาต้นเหตุ → impact 2 วิธี | ข้อความลูกค้า (ในพรอมต์) | `tests/new/bug01-*.spec.ts` `BUG-01.md` `out/bug01.har` | ~15 |
| | 6 แก้ BUG-01 | ✏️ | แก้ที่ต้นเหตุให้เล็กที่สุด → build → แดงเป็นเขียว → regression chromium | `BUG-01.md` | `petshop/lib/orders.ts` · `BUG-01.md` ส่วน "แก้แล้ว" | ~10 |
| 🟠 ฟีเจอร์ | 7 CR-01 ถาม + impact + test แดง | ✏️ | ถามร้านก่อน (AC กำกวม) · impact (จุดแสดงเงินซ้ำ) · TC-GIFT ค่าขอบ ±1 · test แดงเพราะยังไม่มีฟีเจอร์ | ใบ CR (ในพรอมต์) · คำตอบร้าน (README `<details>`) | `CR-01.md` `tests/new/cr01-giftwrap.spec.ts` | ~15 |
| | 8 ทำ CR-01 + regression | ✏️ | แผน → อนุมัติ → แก้ 6 ไฟล์ (คาด) → TC-GIFT เขียว → suite ทั้งหมด 3 เบราว์เซอร์ | `CR-01.md` | โค้ดใน `petshop/` · `CR-01.md` ส่วน "ทำแล้ว" | ~25 ☕ |
| 🟣 พิสูจน์ | 9 พิสูจน์ + ส่งมอบ | 🔍 | SHA-256 source v1↔ปัจจุบัน · build v2 · REA source-to-bundle 4 ทิศ (ตัวนับครบ 7 คลาส) · **obligation ledger** ของเดิมที่ต้องยังทำได้ · compare-versions (ดูข้อจำกัด) · HAR ใหม่เทียบ API | `out/v1/` `BUG-01.md` `CR-01.md` `BASELINE.md` | `CHANGE-PROOF.md` `CHANGE-REPORT.md` `out/v2/` | ~20 (2 ส่วน) |
| | 10 ฝึกเดี่ยว PR-1 | ✏️ | วงจรเต็มในพรอมต์เดียวกับบั๊กเดิมที่ซ่อนอยู่ (toast เพิ่มลงตะกร้า) | ข้อความลูกค้า + `CLAUDE.md` | `tests/new/pr1-*.spec.ts` · โค้ด · แถว PR-1 ใน `CHANGE-REPORT.md` | ~25 |

**นิยาม ✏️ "แก้ repo":** แก้โค้ดแอปใน `petshop/` **หรือ** เพิ่ม test ลงชุดเทสต์เดิม (`e2e-legacy/tests/new/`) · แก้โค้ดแอปจริง = LAB 6 8 10 · เพิ่มเทสต์ใน suite เดิม = LAB 4 5 7 → 6/10 · ถ้าอยากให้แก้โค้ดแอปมากขึ้น ใส่ PR-2/PR-3 (`CR-DESIGN` §4) ใน 🔁 รันซ้ำ (ใช้พรอมต์ LAB 10 เปลี่ยนข้อความลูกค้า)

**ทฤษฎี → ลงมือ (ผู้สอนกำหนด: ทุกแนวคิดต้องถูกใช้ในพรอมต์):**

| แนวคิด (🎓) | ใช้จริงที่ | ชิ้นงานที่ตรวจได้ |
|---|---|---|
| Chikofsky & Cross (forward · reverse · redocumentation · design recovery · restructuring · re-engineering) | LAB 1 ส่วน I · LAB 9 ส่วนที่ 2 ข้อ 3 (คอลัมน์ "ชนิดงาน") | ตาราง ส่วนของไฟล์ ↔ ชนิดงาน + เหตุผล ใน `CODEBASE-MAP.md` · แถว BUG-01/CR-01/PR-1 ระบุ restructuring หรือ re-engineering |
| black / white / grey-box | LAB 1 ส่วน I · LAB 2 ส่วน C ข้อ 5 · LAB 5 (ขั้นที่ 1 black → ขั้นที่ 3 white) | คอลัมน์ "ตาไหน" ใน `CODEBASE-MAP.md` · คอลัมน์ "ยืนยันด้วยตา" ใน `SYSTEM-MAP.md` ส่วน B |
| static vs dynamic · 4 ถัง authority | LAB 2 ข้อ 4 · LAB 3 ส่วน B D | ป้าย 🔵🟢🟡⚪ ทุกแถว |
| obligation ("ของใหม่ต้องทำได้เท่าของเดิม") | LAB 9 ส่วนที่ 1 ข้อ 5 | ตาราง obligation ledger ใน `CHANGE-PROOF.md` (ของเดิม · positive/negative/malformed · หลักฐาน · ผล) |
| characterization / [E] | LAB 4 ข้อ 3–4 | annotation [E]/[D] ใน `char-money.spec.ts` |
| digest / version compare | LAB 2 ข้อ 2 · LAB 9 ส่วนที่ 1 ข้อ 1–4 | digest 12 ตัวใน `SYSTEM-MAP.md` · ตาราง 4 ทิศ |

ทางเลือก (ไม่นับ LAB): **REA เป็น MCP ให้ Agent ใช้เอง** (`PROMPTS.md` หัวข้อ "ทางเลือก MCP") วางไว้ใน 🔁 รันซ้ำ

## 3. 🎓 พื้นฐาน (8 หัวข้อ ทฤษฎีก่อนลงมือ · ทุกหัวข้อมีรูป + ตาราง + LAB ที่ได้ใช้)

1) **Reverse engineering คืออะไร (Chikofsky & Cross 1990)** · `concept-01-reverse-engineering.jpg` + `re-taxonomy.png`
   ตาราง: คำ | ทิศ | เปลี่ยนระบบไหม | ตัวอย่าง PawPantry (forward · reverse · redocumentation · design recovery · restructuring · re-engineering) · ประโยคจำ "RE = ดู ไม่ใช่แก้ · แก้ = re-engineering ที่ต้องมี RE ก่อน" · บันได 5 ขั้น bytes → code → modules → features → กฎธุรกิจ (ขั้นบนสุดต้องถามร้าน [D]) · Feathers: legacy code = code without tests → **ใช้ LAB 1 ส่วน I** (ติดป้ายว่า CODEBASE-MAP แต่ละส่วนเป็น redocumentation หรือ design recovery) · **LAB 9 ส่วนที่ 2 ข้อ 3** (คอลัมน์ "ชนิดงาน": BUG-01/CR-01/PR-1 เป็น restructuring หรือ re-engineering) · Quiz ข้อ 1
2) **4 ช่องทางรู้จักระบบ: static vs dynamic** · `concept-02-static-vs-dynamic.jpg`
   ตาราง: ช่องทาง (อ่าน source · static analysis ของ build · runtime observation · HAR) | พิสูจน์ได้ | พิสูจน์ไม่ได้ | เครื่องมือในบท · กฎ Dijkstra + Rice → coverage partial เป็นเรื่องปกติ · ใช้ LAB 1 ส่วน H, LAB 2 ข้อ 6, LAB 3 ส่วน D
3) **3 ตา: black / white / grey-box + เมื่อไรใช้ REA** · `concept-03-black-white-grey-box.jpg` + `three-eyes.png` + `concept-04-rea-or-read.jpg` + `when-rea.png`
   ตาราง: มีอะไรในมือ | มุม | ใช้อะไร (เฉพาะ URL → HAR/scenario · เฉพาะ build → analyze/trace · source ไม่แน่ใจว่าตรง deploy → source-to-bundle · source ครบเชื่อได้ → อ่าน repo **ข้าม REA** ตาม skill ของ REA) · triangulation = 2 มุมยืนยันกัน · **ใช้ LAB 1 ส่วน I** (แต่ละส่วนของ CODEBASE-MAP ได้จากตาไหน) · **LAB 2 ส่วน B + ส่วน C ข้อ 5** (แถวละกี่ตา ตาไหน) · LAB 5 (black ก่อน → white ทีหลัง) · LAB 9 ส่วนที่ 1 ข้อ 4
4) **Evidence ไม่ใช่ความเห็น + หาไม่เจอ ≠ ไม่มี** · `concept-05-evidence-not-opinion.jpg` + `concept-06-missing-not-absent.jpg` + `evidence-4-buckets.png`
   ฟิลด์ Evidence (subject+digest · provider · authority · confidence · limitations · coverage · locations · evidence_id) · 4 ถัง 🔵 static · 🟢 runtime · 🟡 inference · ⚪ unknown · ตัวอย่างจริง: endpoint `a b c` (minify) · ไม่เจอ `/api/recommendations` (template literal) · storage `name: null` → runtime เจอ `pp-cart` `pp-coupon` `pp-recent` · ป้าย `electron-renderer` ไม่ได้แปลว่าเป็น Electron · ใช้ LAB 2 ข้อ 4–5, LAB 3 ส่วน B
5) **ลายนิ้วมือของไฟล์ (SHA-256) และการเทียบเวอร์ชัน** · `concept-07-content-digest.jpg` + `concept-08-version-compare.jpg`
   hash เท่ากัน = bytes เดียวกัน (ไม่ได้แปลว่าถูก) · path เดียวกันไม่ได้แปลว่าเนื้อเดียวกัน · `next build` ใหม่ = digest ใหม่ = ต้องเก็บหลักฐานใหม่ · version compare: unchanged / changed / unknown · source-to-bundle มี 7 คลาส `unchanged · modified · removed · split · merged · duplicated · unknown` แต่**ในรอบที่รันจริง ไฟล์ที่แก้ออกมาเป็น `unknown` (modified = 0)** เพราะ REA จับคู่ด้วย digest ไม่ได้ → อย่ารอคำว่า modified · ใช้ LAB 2 ข้อ 2 (จด digest), LAB 9 ส่วนที่ 1 ข้อ 1–4
6) **แผนที่แอป · ตามรอยฟีเจอร์ · 3 วิธีดูตอนรัน** · `concept-09-feature-trace.jpg` + `concept-10-passive-driven-har.jpg` + `rea-architecture.png`
   node/edge/provenance · seed `string` + `incoming` = "ใครเรียกสิ่งนี้" (`both` = ได้ทั้งกราฟ) · passive (คนคุม) / driven (REA ขับ Playwright · มีผลข้างเคียง) / HAR (ประวัติ ไม่ยิงซ้ำ) · ใช้ LAB 2 ข้อ 3, LAB 3
7) **จากหลักฐานสู่ test oracle** · `concept-11-obligation-ledger.jpg` + `concept-15-characterization-lock.jpg` + `concept-12-evidence-badge-e.jpg` + `oracle-badges-e.png`
   obligation = "ของใหม่ต้องทำได้เท่าของเดิม" (positive/negative/malformed · fail-closed) · characterization ล็อก "ที่ทำอยู่" ไม่ใช่ "ที่ควร" · ป้าย **[E]** = หลักฐานระบบ: เชื่อได้ว่า *ทำ* ไม่ใช่ว่า *ควร* · [E] ขัด [D] = ผู้ต้องสงสัยบั๊ก [D] ชนะ · `[E?]` สำหรับ inferred · coverage partial ห้ามเขียน TC "ต้องไม่มี X" · ใช้ LAB 4 ข้อ 4, LAB 5 ขั้นที่ 1 · **obligation ledger ลงมือใน LAB 9 ส่วนที่ 1 ข้อ 5** (ของเดิม | positive / negative / malformed | หลักฐาน | ผล)
8) **จริยธรรม + ขีดจำกัดของ REA** · `concept-13-ethics-permission.jpg` + `concept-14-rea-limits.jpg`
   ส่องเฉพาะระบบของเรา/ได้รับอนุญาต · พ.ร.บ.คอมพิวเตอร์ + PDPA (ภาพรวม) · HAR มีรหัสผ่าน plain text → `--sensitive-value` + ห้ามส่งต่อ/commit · ผลถูกส่งให้ model ของ agent · REA ไม่รู้เจตนาธุรกิจ ไม่เห็นตรรกะ server ใน client bundle ไม่ตัดสินถูกผิด · ใช้ LAB 3 ข้อ 2+5
> **กับดักท้าย 🎓:** "**เทสต์เขียว ≠ ไม่มีบั๊ก** · **หาไม่เจอ ≠ ไม่มี** · **ล็อกพฤติกรรมเดิม ≠ ยอมรับว่าถูก** · ตัวเลขเงินให้เทียบ [D] ก่อนล็อกเสมอ"

### 3.1 Quiz ทบทวน (README ท้าย 🎓 แสดง **เฉพาะคอลัมน์คำถาม** · คอลัมน์เฉลยไป `_solution/QUIZ.md` เท่านั้น)

> **กฎกันเฉลยรั่ว (H1):** README ส่วนที่อยู่ก่อน LAB 5 (🎓 · Quiz · รูบริก · LAB 0–4) ห้ามมี `1,049` `1049` `orders.ts` `PP-231` `/orders/[id]` `>=` `FREE_SHIPPING_MIN` · ส่วนก่อน LAB 7 ห้ามมี `/orders/[id]` `SummaryRows` · ตรวจรับด้วยคำสั่งใน §7 #15 · คำถามใช้ตัวอย่าง **สมมติ** ที่ไม่ใช่บั๊กจริงของบท

| # | คำถาม (README) | เฉลย (`_solution/QUIZ.md`) |
|---|---|---|
| 1 | RE ต่างจาก re-engineering อย่างไร งานในบทนี้ LAB ไหนเป็นแบบไหน | RE = ดูเพื่อสร้างตัวแทนระดับสูง ไม่เปลี่ยนระบบ (LAB 1–3) · re-engineering = RE แล้วแก้/สร้างใหม่ (LAB 5–10) |
| 2 | REA เจอ `fetch("/api/orders")` ใน bundle พิสูจน์ว่าลูกค้ากดสั่งซื้อแล้วไหม | ไม่ · static = มีโค้ดใน bytes เท่านั้น ต้องใช้ runtime/HAR |
| 3 | static ไม่เจอ `/api/recommendations` สรุปว่าอะไร | "ยังไม่พบ (coverage partial)" ห้ามสรุปว่าไม่มี · URL ประกอบตอนรัน |
| 4 | 3 คำถามที่ต้องถามทุกหลักฐาน | มาจาก bytes/การรันไหน (digest) · เห็นจริงหรืออนุมาน (authority) · ตรวจครบไหม (coverage) |
| 5 | ไฟล์ path เดียวกันใน 2 build แต่ hash ต่าง / hash เท่ากัน แปลว่าอะไร | ต่าง = เนื้อหาเปลี่ยน (ต้องเทสต์ส่วนที่เกี่ยว) · เท่ากัน = bytes เดียวกัน (ไม่ได้แปลว่าถูก) |
| 6 | มี source ครบแล้วทำไม skill ของ REA บอกให้ข้าม · บทนี้ใช้ REA ตอนไหน | อ่าน repo ตรงกว่า ถูกกว่า · ใช้เมื่อต้องดู "ของที่ส่งมอบ/รันอยู่": build, HAR, ยืนยันว่า build ตรงกับ source |
| 7 | `inspect-web-network-capture` ยิง request ซ้ำไหม · HAR มีอะไรอันตราย | ไม่ (offline) · มีรหัสผ่าน/cookie → `--sensitive-value` และห้ามส่งต่อไฟล์ HAR ต้นฉบับ |
| 8 | (สมมติ) characterization จับได้ว่าเว็บคิดค่าส่งด่วน ฿150 แต่ TEST-DATA [D] บอก ฿120 ควรล็อกค่าไหนเป็นผลที่คาดหวัง และทำอะไรต่อ | [E] ขัด [D] → [D] ชนะ · ห้ามล็อก ฿150 เป็นผลที่คาดหวัง · test คู่ (ข้อหนึ่งล็อกค่าปัจจุบัน `legacy-quirk` + อีกข้อ `test.fail` ตาม [D] `KNOWN-ISSUE`) + จดผู้ต้องสงสัยใน BASELINE แล้วถามร้าน |
| 9 | (สมมติ) แก้ไฟล์ A แล้ว build ใหม่ `compare-source-to-bundle` ของ source ใหม่กับ bundle เก่าขึ้น `unknown` ที่ไฟล์ A แปลว่าอะไร | REA หา digest ของ source ไฟล์ A ใน bundle นั้นไม่เจอ → สอดคล้องกับ "ไฟล์ถูกแก้" แต่ **ไม่ใช่หลักฐานว่าไฟล์หาย** · REA มีคลาส `modified` แต่ในรอบที่รันจริงไฟล์ที่แก้ออกมาเป็น `unknown` (modified = 0) เพราะจับคู่ด้วย digest ไม่ได้ → ต้องดู 4 ทิศและเทียบกับ SHA-256 ของ source ประกอบ |
| 10 | ชุดเทสต์เดิมเขียวทุกข้อ แปลว่าระบบไม่มีบั๊กไหม ต้องตรวจอะไรเพิ่ม | ไม่ · เขียว = ไม่มีข้อที่ **เขียนไว้** ล้ม · ต้องดูว่าชุดเดิมตรวจกฎอะไร ที่ค่าขอบไหน และตรวจที่จุดไหน (หน้าจอ vs สิ่งที่ server บันทึก) → หาช่องว่าง (LAB 4 ข้อ 2) · *(เฉลยเฉพาะบท หลังจบ LAB 5: ไม่มี test ไหนสั่งซื้อจนจบที่ยอดค่าขอบของกฎส่งฟรี และตรวจเงินแค่หน้าตะกร้า)* |

## 4. ✅ รูบริก "รับช่วงระบบเดิมอย่างมืออาชีพ" (20 ข้อ · ดีมาก ≥ 18 · ใช้ได้ 14–17 · ต้องแก้ < 14)

**A. เข้าใจระบบ (LAB 1–3)** 1. ทุกแถวใน CODEBASE-MAP มี "ยืนยันจาก" ไฟล์:บรรทัด และแถว "เดา" ≤ 10% · 2. ตาราง "เอกสารบอก ≠ โค้ดทำ" เจอเรื่องเก่าใน HANDOVER-NOTES ครบ 2 ข้อ และไม่ตัดสินเอง · 3. CLAUDE.md ≤ 60 บรรทัด มีคำสั่งรัน พอร์ต 4000 ห้ามแตะ กติกาการแก้ และ settings.json กันไฟล์เดิมได้จริง · 4. SYSTEM-MAP ติดป้าย 🔵🟢🟡⚪ ทุกแถว ไม่มีข้อ "ไม่เจอ" ที่สรุปว่า "ไม่มี" · 5. API-INVENTORY ไม่มีรหัสผ่าน/cookie และอธิบาย 3 วิธีดูระบบได้
**B. ล็อก (LAB 4)** 6. รัน suite เดิม 3 เบราว์เซอร์ก่อนแตะโค้ด · 7. golden master ตรวจเงินครบ 4 จุดของตะกร้าเดียวกัน · 8. ค่าที่ [E] ขัด [D] ไม่ถูกอบเป็นผลที่คาดหวัง
**C. BUG-01 (LAB 5–6)** 9. ทำซ้ำแบบ black-box และหาขอบเขตอาการ (กรณีข้างเคียง) ก่อนเปิดโค้ด · 10. test แดงก่อนแก้ ด้วยผลที่คาดหวัง [D] · 11. ต้นเหตุระบุไฟล์:บรรทัด และตรวจคอมเมนต์ในโค้ดตรงนั้นกับหลักฐาน HAR (ไม่เชื่อคอมเมนต์ทันที) · 12. แก้ที่ต้นเหตุ ไม่ใช่ปลายเหตุ และอธิบายได้ว่าทำไมวิธีที่เลือกเป็นต้นเหตุ
**D. CR-01 (LAB 7–8)** 13. ถามร้านก่อน ≥ 2 เรื่อง พร้อมตัวเลขที่ต่างกัน · 14. impact ครอบทุกจุดที่คำนวณ **และแสดง** เงิน (หน้าและ API) โดยตรวจด้วยการค้นโค้ด ไม่ใช่เดาจากชื่อไฟล์ · 15. TC มีค่าขอบ ±1 บาท + API ส่ง giftWrap ผิดชนิด · 16. TC-GIFT แดงก่อน → เขียวหลัง และ regression 3 เบราว์เซอร์ไม่มีข้อเดิมล้ม
**E. พิสูจน์ส่งมอบ (LAB 9–10)** 17. รายการไฟล์ที่ตั้งใจแก้ = ไฟล์ที่ hash ต่าง = ไฟล์ที่ REA บอกว่า bundle ต่าง (หรืออธิบายส่วนเกิน) · 18. CHANGE-REPORT ทุกตัวเลขอ้างไฟล์ผล + มี evidence_id + rollback · 19. ไม่มีการรัน `-u` หรือแก้ test เดิมให้ผ่าน · 20. PR-1 ทำครบวงจรในพรอมต์เดียว (แดง → ถามก่อนแก้ → เขียว → regression)

### 4.1 หมายเหตุผู้ตรวจ (อยู่ใน `_solution/GRADING.md` เท่านั้น · **ห้ามคัดลง README**)

| ข้อรูบริก | สิ่งที่ผู้ตรวจมองหา (เฉลย) |
|---|---|
| 8 | ตะกร้า ฿999 ส่งธรรมดา: ตะกร้า/ปุ่ม ฿999 แต่คำสั่งซื้อ ฿1,049 → ต้องเป็น test คู่ `legacy-quirk` + `test.fail` ไม่ใช่ `expect(1049)` |
| 11 | ต้นเหตุ = บล็อก `// PP-231` ใน `lib/orders.ts` คำนวณค่าส่งซ้ำด้วย `>` แล้วเขียนทับ `totals.total` · HAR: body POST `/api/orders` มีแค่ `shipping: "standard"` → คอมเมนต์ "must not trust the shipping fee shown in the browser" ไม่ตรงความจริง |
| 12 | วิธีที่ถูก = ลบบล็อกซ้ำ + import ที่ไม่ใช้ (กฎเงินอยู่ `lib/pricing.ts` ที่เดียว) · `>`→`>=` = ปลายเหตุ (CR-01 ค่าห่อจะหาย ฿269 → ฿239 · `CR-DESIGN` §2.6) |
| 14 | impact ต้องมี `app/orders/[id]/page.tsx` (เขียนสรุปเงินเอง ไม่ใช้ `SummaryRows`) · ไม่ต้องแก้ `app/api/orders/route.ts` `app/account/page.tsx` (ตรวจแล้ว) |
| 17 | ไฟล์ที่ต่าง = 6 ไฟล์ CR-01 (+ `lib/orders.ts` ของ BUG-01) + PR-1 · ไฟล์ที่ build เขียนเอง (`next-env.d.ts`) อธิบายได้ |

## 5. 📖 คำศัพท์ (README)

Reverse engineering · Forward engineering · Re-engineering · Redocumentation / Design recovery · Legacy code (code without tests) · Static analysis · Runtime observation (dynamic) · Black / White / Grey-box · Triangulation · REA · Evidence · Authority (🔵🟢🟡⚪) · Coverage `partial` · หาไม่เจอ ≠ ไม่มี · Content digest / SHA-256 · Application graph (node / edge) · Feature trace / seed · HAR · Scenario capture · Source-to-bundle · Characterization test / Golden master · ป้าย [E] · `test.fail` / KNOWN-ISSUE · Impact analysis · ต้นเหตุ vs ปลายเหตุ · Regression · Change Request / AC · CHANGE-REPORT · CODEBASE-MAP / CLAUDE.md · permissions deny · Excluded port range (WinNAT) · MCP

## 6. ไฟล์ในบท

**ก่อนเริ่ม** (หลังทำข้อ 7)
```text
05_rea-reverse-engineer-legacy-petshop/
├─ README.md            📖 บทเรียน + พรอมต์ทุก LAB
├─ TEST-DATA.md         🔑 [D] ข้อมูลจากร้าน (คัดจากบท 03 ไม่แก้)
├─ .gitignore           out/ *.har node_modules/ .next/ test-results/ playwright-report/ rea/scratch/ .mcp.json
├─ petshop/             ระบบเดิม (ไม่มี BUG_MODE · มี BUG-01 อบอยู่) + README.md + HANDOVER-NOTES.md · compose name: pawpantry05
├─ e2e-legacy/          ชุดเทสต์ของทีมเดิม 40 test (คัดจากบท 02) · ค่าเริ่มต้น chromium · npm run test:all = 3 เบราว์เซอร์ · tests/new/ (ว่าง)
├─ rea/                 Dockerfile · rea.ps1 · rea-input.mjs · rea-summarize.mjs · record-har.mjs · scenario-coupon.json · package.json · README.md · scratch/ (ignored · สคริปต์ชั่วคราวของ agent ใช้ playwright ของ rea/)
├─ img/                 🖼️ รูปประกอบ
└─ _solution/           🔑 เฉลย (ห้ามเปิดก่อนจบ) · QUIZ.md · GRADING.md · _design/
```
**หลังจบทุก LAB**
```text
├─ CODEBASE-MAP.md · CLAUDE.md · .claude/settings.json   # LAB 1
├─ SYSTEM-MAP.md                                         # LAB 2  REA เห็น / โค้ดบอก / ตรงไหม
├─ API-INVENTORY.md                                      # LAB 3
├─ BASELINE.md                                           # LAB 4
├─ BUG-01.md                                             # LAB 5–6
├─ CR-01.md                                              # LAB 7–8
├─ CHANGE-PROOF.md · CHANGE-REPORT.md                   # LAB 9 (+ แถว PR-1 จาก LAB 10)
├─ e2e-legacy/tests/new/  char-money · golden/ · bug01-shipping · cr01-giftwrap · pr1-* .spec.ts
├─ petshop/  lib/orders.ts (BUG-01) · lib/pricing.ts lib/store.ts components/OrderSummary.tsx components/CheckoutForm.tsx app/orders/[id]/page.tsx (CR-01) · components/ProductCard.tsx (PR-1 คาด)
├─ rea/scratch/  (ignored) สคริปต์ Playwright ชั่วคราวของ LAB 5 8 10
└─ out/  (ignored) v1/ v2/ *.json pawpantry-main.har bug01.har scenario-final.png after/ shots/
```

## 7. สิ่งที่ต้องทำกับโฟลเดอร์ตั้งต้น (ก่อนรัน RUNNER · ผู้สร้างบททำ ไม่ใช่ B1)

> **วิธีอ่าน:** ทำตามลำดับ #1 → #16 · `$CH` = `00_tester/05_rea-reverse-engineer-legacy-petshop` (รากบท) · คำสั่งตรวจรับเป็น **Git Bash จาก `$CH`** เว้นแต่ขึ้นต้น `PS>` (= Windows PowerShell 5.1 จาก `$CH`) · เลขบรรทัด = บรรทัดในไฟล์ **ก่อนแก้** (ไฟล์ CRLF · แก้จากล่างขึ้นบนเพื่อไม่ให้เลขเลื่อน) · งานชั่วคราวทำใน `C:/t/work/<ชื่องาน>/` (`$T`) · ข้อมูลอ้างอิงของ A1 อยู่ที่ `A=C:/t/work/a1/out` (ไฟล์ใหญ่ อ่านด้วยสคริปต์เท่านั้น)
> ตัวช่วยเทียบ JSON (ใช้ใน #9 #10): สร้าง `$T/jsoneq.mjs` = `import{readFileSync as r}from"node:fs";const j=p=>JSON.parse(r(p,"utf8").replace(/^\uFEFF/,""));const ok=JSON.stringify(j(process.argv[2]))===JSON.stringify(j(process.argv[3]));console.log(ok);process.exit(ok?0:1);` · ใช้ `node $T/jsoneq.mjs <ไฟล์เรา> <ไฟล์ A1>` ต้องพิมพ์ `true`

### 7.1 รายการงาน

| # | ไฟล์ (จาก `$CH`) | ทำอะไร (ตรงตัว) | ตรวจรับ (ต้องได้ตามนี้) |
|---|---|---|---|
| 1 | `petshop/**` (12 ไฟล์) | **เอา BUG_MODE ออก** ตามตาราง 7.2 ทุกบรรทัด (ผล = พฤติกรรม `BUG_MODE=0` เดิม) | `grep -rniE "bug_?mode" petshop --exclude-dir=node_modules --exclude-dir=.next \| wc -l` = `0` · `cd petshop && npm ci && npm run typecheck` exit 0 · `grep -c "ฝึกเขียนเทสต์" petshop/app/layout.tsx` = `0` |
| 2 | `petshop/lib/orders.ts` | **อบ BUG-01** หลัง #1: diff ใน 7.3 (= `CR-DESIGN` §2.2 ที่บรรทัด `computeTotals` ไม่มี `bugMode`) · แก้มือ หรือ `git apply --ignore-whitespace` บน **สำเนา** แล้วคัดกลับ (ห้าม git ที่เปลี่ยนสถานะ repo) | `grep -c "PP-231" petshop/lib/orders.ts` = `1` · หลัง #3: `node $T/verify-bug01.mjs` (7.4) พิมพ์ 4 แถว `999-standard total=1049` · `999-PAW10 total=950` · `999-FREESHIP total=999` · `999-express total=1119` แล้ว `ALL OK` |
| 3 | `petshop/docker-compose.yml` | เขียนทับด้วยเนื้อหา 7.5-A (บรรทัดแรก `name: pawpantry05` · `container_name: pawpantry05` · `image: pawpantry05:latest` · `"${WEB_PORT:-4000}:3000"` · ไม่มี BUG_MODE · service ชื่อ `petshop` = ชื่อ DNS) | `docker compose -f petshop/docker-compose.yml config \| head -1` = `name: pawpantry05` · `cd petshop && docker compose up -d --build` (นาน ~3 นาที) → `docker ps --filter name=pawpantry05 --format "{{.Status}}"` มี `(healthy)` · `docker network ls --filter name=pawpantry05_default -q \| wc -l` = `1` · `docker run --rm --network pawpantry05_default --entrypoint node rea-lab:6.4.0 -e "fetch('http://petshop:3000/api/health').then(r=>r.text()).then(console.log)"` = `{"ok":true}` · `curl -s localhost:4000/api/health` = `{"ok":true}` |
| 4 | `petshop/README.md` | เขียนทับด้วยเนื้อหา 7.5-B | `grep -ciE "bug_?mode\|ฝึก" petshop/README.md` = `0` · `test -f TEST-DATA.md` (ลิงก์ `../TEST-DATA.md` ชี้ถูก) |
| 5 | `petshop/HANDOVER-NOTES.md` (ใหม่) | เนื้อหา 7.5-C ตามตัว (≤ 15 บรรทัด · เรื่องเก่า 2 ข้อ: SUMMER20 · "ทุกหน้าดึงผ่าน `GET /api/products`") | `wc -l < petshop/HANDOVER-NOTES.md` ≤ 15 · `grep -ciE "ค่าส่ง\|ส่งฟรี\|shipping\|999\|PP-231\|orders.ts" petshop/HANDOVER-NOTES.md` = `0` |
| 6 | `TEST-DATA.md` | `cp ../03_petshop-testplan-from-exploration/TEST-DATA.md TEST-DATA.md` (ตามตัว) | `cmp TEST-DATA.md ../03_petshop-testplan-from-exploration/TEST-DATA.md` exit 0 |
| 7 | `e2e-legacy/` | ตาม `LEGACY-TESTSUITES` §4.1 (มีแล้ว) + `mkdir -p e2e-legacy/tests/new && touch e2e-legacy/tests/new/.gitkeep` · รันบน build #1–#3 แล้ว**แก้ตัวเลขในตาราง "ผลรันล่าสุด" ของ `e2e-legacy/README-LEGACY.md` ให้ตรงผลที่ได้จริง** (ทั้ง chromium และ `npm run test:all`) | `ls e2e-legacy/tests/*.spec.ts \| wc -l` = `10` · `test -f e2e-legacy/tests/new/.gitkeep` · `cd e2e-legacy && npm ci && npx playwright test` → `40 passed` · `npm run test:all` → `120 passed` (ถ้าไม่ใช่ ให้หยุดรายงาน orchestrator ก่อนเขียน README) |
| 8 | `rea/rea.ps1` | คัดจาก `_solution/_design/rea-probe/rea.ps1` แล้ว**แทนบล็อกตัวอย่างในหัวไฟล์** (บรรทัด 6–11) ด้วย 7.5-D · โค้ดส่วน `param(...)` ลงไปไม่แก้ | `PS> powershell -NoProfile -ExecutionPolicy Bypass -File .\rea\rea.ps1 doctor` แสดงผล doctor (exit 1 ได้ = ปกติ · `REA-FEASIBILITY` §2.1) · `PS> powershell -NoProfile -ExecutionPolicy Bypass -File .\rea\rea.ps1 -Out out\doctor.json doctor --json; Format-Hex out\doctor.json \| Select-Object -First 1` ไบต์แรก `7B` (ไม่มี BOM) |
| 9 | `rea/rea-summarize.mjs` | เขียนใหม่ตามสัญญา 7.6 (ทุกโหมด) | ทุกแถวในคอลัมน์ "ตรวจรับกับข้อมูล A1" ของ 7.6 ผ่าน |
| 10 | `rea/rea-input.mjs` (ใหม่) | เขียนตามสัญญา 7.7 | ทุกแถวในคอลัมน์ "ตรวจรับ" ของ 7.7 พิมพ์ `true` |
| 11 | `rea/record-har.mjs` | คัดจาก `rea-probe/` แล้วแก้ตามสัญญา 7.8 (เพิ่ม `--base` `--out` · ค่าเริ่มต้น 4000 · `OUT` เริ่มต้น = `<รากบท>/out`) | หลัง #3 #12: `PS> node rea\record-har.mjs` สร้าง `out\pawpantry-main.har` + `out\har-steps.json` (8 step) · `PS> node rea\record-har.mjs --out out\after` สร้างใน `out\after\` · รันจาก `petshop\` ด้วย `node ..\rea\record-har.mjs` ต้องเขียนลง `<รากบท>\out\` ไม่ใช่ `petshop\out\` |
| 12 | `rea/package.json` · `rea/scenario-coupon.json` | package.json = 7.5-E ตามตัว · scenario = คัดจาก `rea-probe/scenario-coupon.json` แก้บรรทัด `"start_url": { "url": "http://host.docker.internal:3000/" }` → `"start_url": { "url": "http://petshop:3000/" }` (ที่เหลือตามตัว) | `cd rea && npm install` แล้ว `node -e "import('playwright').then(()=>console.log('ok'))"` = `ok` · `mkdir -p rea/scratch && echo 'import "playwright";console.log("ok")' > rea/scratch/t.mjs && node rea/scratch/t.mjs` = `ok` (แล้วลบ `t.mjs`) · `PS> powershell -NoProfile -ExecutionPolicy Bypass -File .\rea\rea.ps1 -Network pawpantry05_default -Out out\scenario.json capture-browser-scenario /work/rea/scenario-coupon.json --json` exit 0 แล้ว `node rea\rea-summarize.mjs out\scenario.json` → `steps_completed` = `"11/11"` |
| 13 | `rea/README.md` | เนื้อหา 7.5-F ตามตัว (≤ 20 บรรทัด) | `wc -l < rea/README.md` ≤ 20 |
| 14 | `.gitignore` (ราก) | เนื้อหา 7.5-G ตามตัว | `git check-ignore -q out/x.json rea/scratch/a.mjs x.har` exit 0 (อ่านอย่างเดียว) |
| 15 | `README.md` (ราก · ผู้เขียน README) | ใช้ §3.1 **เฉพาะคอลัมน์คำถาม** + รูบริก §4 (ไม่รวม §4.1) · ใส่คำตอบร้านของ LAB 7 ใน `<details>` | กันเฉลยรั่ว: `awk '/^## .*LAB 5/{exit} {print}' README.md \| grep -nE '1,049\|1049\|orders\.ts\|PP-231\|/orders/\[id\]\|FREE_SHIPPING_MIN\|SummaryRows'` = ว่าง · `awk '/^## .*LAB 7/{exit} {print}' README.md \| grep -nE '/orders/\[id\]\|SummaryRows'` = ว่าง · `grep -c "PP-100001" README.md` = `0` |
| 16 | `_solution/QUIZ.md` · `_solution/GRADING.md` (ใหม่) | QUIZ = ตาราง §3.1 ทั้ง 2 คอลัมน์ (คำถาม + เฉลย) · GRADING = รูบริก §4 + ตาราง §4.1 | `grep -c "^| [0-9]" _solution/QUIZ.md` = `10` · `grep -c "1,049" _solution/GRADING.md` ≥ 1 |
| 17 | `img/` + `_solution/_design/diagrams/rea-architecture.html` | ชื่อไฟล์ jpg เดิม **rename แล้ว ✅** (ไม่ต้องทำ) · แก้ html บรรทัด 91 `<span class="pill">localhost:3000</span>` → `<span class="pill">localhost:4000 · petshop:3000</span>` · บรรทัด 78 `<div class="pv"><b>Browser / CDP observer</b><span class="pill">inspect-web-page</span></div>` → `<div class="pv"><b>Source ↔ bundle</b><span class="pill">compare-source-to-bundle</span></div>` และเพิ่ม `· CDP observer (inspect-web-page)` ต่อท้ายข้อความใน `<div class="off"><span>…</span>` บรรทัด 81 · เรนเดอร์ `node _solution/_design/tools/render-png.mjs _solution/_design/diagrams/rea-architecture.html img/rea-architecture.png` · แก้ alt ใน `IMAGES-NOTES.md` บรรทัด 31 ตาม | `grep -c "localhost:3000\|inspect-web-page</span></div>" _solution/_design/diagrams/rea-architecture.html` = `0` · เปิดดู PNG ด้วยตา · `grep -c "localhost:3000" README.md` = `0` |
| ✖ | ไม่ทำ | ไม่ให้ `e2e/` skeleton แยก (เทสต์ใหม่อยู่ `e2e-legacy/tests/new/`) · ไม่ให้ SPEC.md · ไม่ให้ `.claude/settings.json` และ `CLAUDE.md` (ผู้เรียนให้ agent เขียน) · ไม่มี git history (archaeology ทำไม่ได้ → ไม่สอน) | |

### 7.2 เช็กลิสต์เอา BUG_MODE ออก (#1 · บรรทัดก่อนแก้ · `→ (ลบบรรทัด)` = ลบทั้งบรรทัด)

| ไฟล์ | บรรทัด | เดิม | ใหม่ |
|---|---|---|---|
| `lib/bugmode.ts` | ทั้งไฟล์ | — | ลบไฟล์ |
| `lib/pricing.ts` | 94 | `  bugMode = false,` | (ลบบรรทัด) |
| | 114–117 | `    case "PAW10": {` / `      const percent = bugMode ? 1 : 10;` / `      return success(Math.floor((subtotal * percent) / 100));` / `    }` | `    case "PAW10":` / `      return success(Math.floor((subtotal * 10) / 100));` |
| | 142 | `  bugMode?: boolean;` | (ลบบรรทัด) |
| | 144 | `  const { lines, couponCode, shipping = "standard", bugMode = false } = opts;` | `  const { lines, couponCode, shipping = "standard" } = opts;` |
| | 146 | `…evaluateCoupon(couponCode, lines, bugMode) : null;` | `…evaluateCoupon(couponCode, lines) : null;` |
| `lib/validation.ts` | 81–82 | `export function isValidPhone(phone: string, bugMode = false): boolean {` / `  const re = bugMode ? /^0\d{8,9}$/ : /^0\d{9}$/;` | `export function isValidPhone(phone: string): boolean {` / `  const re = /^0\d{9}$/;` |
| | 86 | `export function validateShipping(input: ShipInput, bugMode = false): Partial<…> {` | `export function validateShipping(input: ShipInput): Partial<…> {` |
| | 89 | `  if (!isValidPhone(input.phone, bugMode)) errors.phone = MSG.shipPhone;` | `  if (!isValidPhone(input.phone)) errors.phone = MSG.shipPhone;` |
| `lib/orders.ts` | 19 | `export function createOrder(user: User, input: CreateOrderInput, bugMode: boolean): CreateOrderResult {` | `export function createOrder(user: User, input: CreateOrderInput): CreateOrderResult {` |
| | 34 | `  const errors = validateShipping(address, bugMode);` | `  const errors = validateShipping(address);` |
| | 55 | `  const totals = computeTotals({ lines, couponCode, shipping, bugMode });` | `  const totals = computeTotals({ lines, couponCode, shipping });` |
| `app/api/orders/route.ts` | 3 · 25 | `import { serverBugMode } from "@/lib/bugmode";` · `createOrder(user, body, serverBugMode())` | (ลบบรรทัด) · `createOrder(user, body)` |
| `app/api/coupons/validate/route.ts` | 2 · 16 | `import { serverBugMode } from "@/lib/bugmode";` · `evaluateCoupon(code, priceLines(items), serverBugMode())` | (ลบบรรทัด) · `evaluateCoupon(code, priceLines(items))` |
| `app/layout.tsx` | 16 | `import { serverBugMode } from "@/lib/bugmode";` | (ลบบรรทัด) |
| | 19 | `// BUG_MODE, the session and live stock are read per request (never baked in at build time).` | `// The session and live stock are read per request (never baked in at build time).` |
| | 27 | `  description: "ร้านอาหารแมวและสุนัขออนไลน์ สำหรับฝึกเขียนเทสต์ด้วย Playwright",` | `  description: "ร้านอาหารแมวและสุนัขออนไลน์",` (D4: ระบบจริงไม่บอกว่าเป็นของฝึก) |
| | 37 | `  const bugMode = serverBugMode();` | (ลบบรรทัด) |
| | 42 | `    <html lang="th" data-bug-mode={bugMode ? "1" : "0"}>` | `    <html lang="th">` |
| | 44 | `<ShopProvider initialUser={user} initialStock={stock} bugMode={bugMode}>` | `<ShopProvider initialUser={user} initialStock={stock}>` |
| `components/ShopProvider.tsx` | 27 · 108 · 113 · 288 · 314 | `  bugMode: boolean;` · `  bugMode,` · `  bugMode: boolean;` · `      bugMode,` · `      bugMode,` | (ลบทั้ง 5 บรรทัด) |
| | 225 · 227 | `      if (!bugMode) setWishlistBadge(next.length);` · `    [bugMode, commitWishlist],` | `      setWishlistBadge(next.length);` · `    [commitWishlist],` |
| | 238 · 241 | `      setWishlistBadge((b) => (bugMode ? b + 1 : next.length));` · `    [bugMode, commitWishlist, removeFromWishlist],` | `      setWishlistBadge(next.length);` · `    [commitWishlist, removeFromWishlist],` |
| `components/OrderSummary.tsx` | 4 · 9 · 12 · 13 | `import { clientBugMode } from "@/lib/bugmode";` · `const { cart, coupon, bugMode } = useShop();` · `computeTotals({ lines, couponCode: coupon, shipping, bugMode: bugMode \|\| clientBugMode() })` · `[lines, coupon, shipping, bugMode],` | (ลบบรรทัด) · `const { cart, coupon } = useShop();` · `computeTotals({ lines, couponCode: coupon, shipping })` · `[lines, coupon, shipping],` |
| `components/CheckoutForm.tsx` | 5 · 43 · 69 | `import { clientBugMode } from "@/lib/bugmode";` · `…refreshStock, showToast, bugMode } = useShop();` · `validateShipping(form, bugMode \|\| clientBugMode())` | (ลบบรรทัด) · `…refreshStock, showToast } = useShop();` · `validateShipping(form)` |
| `components/CartView.tsx` | 137 · 168 | `const { ready, cart, coupon, setCoupon, stockMap, bugMode } = useShop();` · `evaluateCoupon(code, lines, bugMode)` | `const { ready, cart, coupon, setCoupon, stockMap } = useShop();` · `evaluateCoupon(code, lines)` |
| `Dockerfile` | 34 | `# BUG_MODE and ALLOW_TEST_RESET are read at runtime (see docker-compose.yml).` | `# ALLOW_TEST_RESET is read at runtime (see docker-compose.yml).` |
| `docker-compose.yml` | ทั้งไฟล์ | — | 7.5-A (#3) |

### 7.3 diff BUG-01 (#2 · ใส่หลัง #1)

```diff
--- a/lib/orders.ts
+++ b/lib/orders.ts
@@ -1,6 +1,13 @@
 import "server-only";
 import { getProduct } from "./products";
-import { computeTotals, priceLines, type CartLine, type ShippingMethod } from "./pricing";
+import {
+  FREE_SHIPPING_MIN,
+  STANDARD_SHIPPING,
+  computeTotals,
+  priceLines,
+  type CartLine,
+  type ShippingMethod,
+} from "./pricing";
 import { db, nextOrderId, type Order, type User } from "./store";
 import { PROVINCES, validateShipping, type ShipInput } from "./validation";
 
@@ (บรรทัด computeTotals หลัง #1) @@
   const couponCode = typeof input.coupon === "string" && input.coupon.trim() ? input.coupon : null;
   const totals = computeTotals({ lines, couponCode, shipping });
+  // PP-231: server must not trust the shipping fee shown in the browser — recompute it here.
+  if (shipping === "standard" && !totals.coupon?.freeShipping) {
+    totals.shipping = totals.subtotal > FREE_SHIPPING_MIN ? 0 : STANDARD_SHIPPING;
+    totals.total = Math.max(0, totals.subtotal - totals.discount + totals.shipping);
+  }
 
   for (const [slug, qty] of qtyBySlug) store.stock[slug] -= qty;
```

### 7.4 `$T/verify-bug01.mjs` (ตรวจรับ #2 · Node 20+ · ไม่ต้องติดตั้งอะไร · ใช้ข้อมูลจริงใน `lib/products.ts`)

```js
const B = process.env.BASE_URL ?? "http://localhost:4000";
const post = (p, body, cookie) => fetch(B + p, { method: "POST", headers: { "content-type": "application/json", ...(cookie ? { cookie } : {}) }, body: JSON.stringify(body) });
const reg = await post("/api/auth/register", { name: "ตรวจ BUG-01", email: `chk${Date.now()}@example.test`, password: "Check1234", terms: true });
if (reg.status !== 201) throw new Error("register " + reg.status);
const cookie = reg.headers.get("set-cookie").split(";")[0];
const items = [{ slug: "cat-feather-wand", size: "1 ชิ้น", qty: 1 }, { slug: "dog-slow-bowl", size: "1 ใบ", qty: 3 }]; // 129 + 290×3 = 999
const address = { name: "ตรวจ ระบบ", phone: "0812345678", address: "99 ถนนสุขุมวิท แขวงคลองเตย", province: "กรุงเทพมหานคร", postcode: "10110" };
const cases = [["999-standard", null, "standard", 1049], ["999-PAW10", "PAW10", "standard", 950], ["999-FREESHIP", "FREESHIP", "standard", 999], ["999-express", null, "express", 1119]];
let ok = true;
for (const [name, coupon, shipping, want] of cases) {
  const r = await post("/api/orders", { items, coupon, shipping, payment: "cod", address }, cookie);
  const o = (await r.json()).order;
  console.log(`${name} total=${o.total} shipping=${o.shipping} (want ${want})`);
  if (o.total !== want) ok = false;
}
console.log(ok ? "ALL OK" : "MISMATCH"); process.exit(ok ? 0 : 1);
```
(ยอดที่ต้องได้มาจากการรันจริงของ A5 · `CR-DESIGN` §2.4 · สต็อกลดทุกครั้งที่รัน → รันก่อน `POST /api/test/reset` ถ้ารันหลายรอบ)

### 7.5 เนื้อหาไฟล์ตามตัว

**A. `petshop/docker-compose.yml`**
```yaml
name: pawpantry05
services:
  petshop:
    build: .
    image: pawpantry05:latest
    container_name: pawpantry05
    ports:
      - "${WEB_PORT:-4000}:3000"
    environment:
      ALLOW_TEST_RESET: "1"
    restart: unless-stopped
```

**B. `petshop/README.md`**
~~~markdown
# PawPantry — หน้าร้านออนไลน์

Next.js (App Router) + TypeScript · ข้อมูลร้านอยู่ในหน่วยความจำของ server (รีสตาร์ต container = ข้อมูลกลับค่าเริ่มต้น)

## เปิดเว็บ
```powershell
docker compose up -d --build     # http://localhost:4000
docker compose down              # ปิด
```

## ล้างข้อมูลทดสอบ
```powershell
Invoke-RestMethod -Method Post http://localhost:4000/api/test/reset
```
ใช้ได้เพราะ `ALLOW_TEST_RESET=1` ใน `docker-compose.yml`

## บัญชีและคูปองทดสอบ
ดู [`../TEST-DATA.md`](../TEST-DATA.md) · ชุดเทสต์ regression: `../e2e-legacy/README-LEGACY.md`
~~~

**C. `petshop/HANDOVER-NOTES.md`**
```markdown
# บันทึกส่งมอบ PawPantry (ทีมเดิม)

- Stack: Next.js App Router + TypeScript · ไม่มีฐานข้อมูล ข้อมูลอยู่ใน memory ของ server · ตะกร้าและรายการโปรดเก็บใน localStorage
- รัน: `docker compose up -d --build` ในโฟลเดอร์ `petshop` แล้วเปิด http://localhost:4000
- ทุกหน้าดึงรายการสินค้าผ่าน `GET /api/products` ถ้าจะแก้ข้อมูลสินค้าให้ดูที่ API ก่อน
- คูปองที่ใช้อยู่: PAW10 ลด 10% · FREESHIP · NEWCAT50 · SUMMER20 ลด 20% ใช้ได้ถึงสิ้นปี
- บัญชีทดสอบและข้อมูลร้าน: `../TEST-DATA.md`
- ชุดเทสต์ regression อยู่ `../e2e-legacy` ผ่านครบทุกข้อก่อน deploy รอบล่าสุด
- งานค้าง: ไม่มี (tracker เดิมปิดไปแล้ว)
```

**D. หัวไฟล์ `rea/rea.ps1` (แทนบรรทัด 6–11 เดิม)**
```text
ตัวอย่าง (รันจากรากบท 05 ใน PowerShell · ExecutionPolicy ค่าเริ่มต้นของ Windows 11 = Restricted จึงเรียกผ่าน -ExecutionPolicy Bypass):
  powershell -NoProfile -ExecutionPolicy Bypass -File .\rea\rea.ps1 doctor
  powershell -NoProfile -ExecutionPolicy Bypass -File .\rea\rea.ps1 -Out out\v1-static.json analyze-javascript-application /work/out/v1/.next/static --json
  powershell -NoProfile -ExecutionPolicy Bypass -File .\rea\rea.ps1 -Out out\har.json inspect-web-network-capture /work/out/pawpantry-main.har har --json
  powershell -NoProfile -ExecutionPolicy Bypass -File .\rea\rea.ps1 -Network pawpantry05_default -Out out\scenario.json capture-browser-scenario /work/rea/scenario-coupon.json --json
  powershell -NoProfile -ExecutionPolicy Bypass -File .\rea\rea.ps1 -Mcp          # MCP stdio server
```

**E. `rea/package.json`**
```json
{
  "name": "pawpantry-rea-tools",
  "private": true,
  "type": "module",
  "dependencies": { "playwright": "1.63.0" }
}
```

**F. `rea/README.md`**
```markdown
# rea/ — เครื่องมือส่องระบบด้วย REA (รันจากรากบทใน PowerShell)

| ไฟล์ | ทำอะไร |
|---|---|
| `Dockerfile` | image `rea-lab:6.4.0` = REA 6.4.0 + Chromium (build ครั้งเดียวก่อนเข้าคลาส: `docker build -t rea-lab:6.4.0 rea`) |
| `rea.ps1` | เรียก REA ใน container · mount รากบทเป็น `/work` · path ที่ส่งให้ REA ต้องขึ้นต้น `/work/` · เรียกด้วย `powershell -NoProfile -ExecutionPolicy Bypass -File .\rea\rea.ps1 …` |
| `rea-input.mjs` | ห่อผล REA เป็น input ของคำสั่งถัดไป (`trace` `s2b` `compare` `view`) |
| `rea-summarize.mjs` | ย่อผล REA ก้อนใหญ่ให้อ่านได้ (`--md` ตาราง · `--all` ทุกแถว · `--png` ภาพสุดท้ายของ scenario · `--s2b-table` ตาราง 4 ทิศ) |
| `record-har.mjs` | เดินเส้นทางหลักของร้านแบบ headless แล้วเก็บ HAR (`--out <โฟลเดอร์>` · ค่าเริ่มต้น `out\`) |
| `scenario-coupon.json` | สคริปต์ให้ REA ขับเบราว์เซอร์ (ใช้กับ `-Network pawpantry05_default`) |
| `scratch/` | ที่วางสคริปต์ Playwright ชั่วคราว (ใช้ playwright ของโฟลเดอร์นี้ · ไม่ถูก commit) |

- ทำไมต้อง `-Out`: `>` ของ PowerShell 5.1 ได้ไฟล์ UTF-16/มี BOM ซึ่ง REA ไม่รับเป็น input
- ผลใน `out\` ใหญ่หลายสิบ MB **ห้ามให้ AI เปิดตรง ๆ** ให้ย่อด้วย `node rea\rea-summarize.mjs` เท่านั้น
- ไฟล์ `.har` มีรหัสผ่าน/cookie จริง ห้ามส่งต่อหรือ commit
```

**G. `.gitignore` (ราก)**
```text
out/
*.har
node_modules/
.next/
test-results/
playwright-report/
rea/scratch/
.mcp.json
```

### 7.6 สัญญา `rea/rea-summarize.mjs` (#9)

**CLI:** `node rea/rea-summarize.mjs <evidence.json> [--md] [--all] [--png <file>]` หรือ `node rea/rea-summarize.mjs --s2b-table <a.json> <b.json> <c.json> <d.json>` · flag อยู่ลำดับไหนก็ได้ · path relative = จาก **cwd** · อ่านไฟล์แล้ว**ตัด BOM** (`\uFEFF`) ก่อน `JSON.parse` · เลือกโหมดจาก `ev.operation` (ถ้าไม่มี `operation` แต่ `ev.schema === "HistoricalSourceGraph"` = โหมด G) · ค่าเริ่มต้นพิมพ์ JSON (`JSON.stringify(out, null, 2)`) · `--md` พิมพ์ตาราง Markdown แทน · ทุกโหมดพิมพ์ `evidence_id_short` = `ev_` + 8 ตัวแรกหลัง `ev_` (เช่น `ev_ca3bd308`) · ผิด usage → exit 2 · ไฟล์ไม่ใช่ JSON → exit 1 พร้อมข้อความ · ให้ `nr = ev.normalized_result`

| โหมด | อ่านจาก (JSON path) | พิมพ์ (key ของ out · คอลัมน์ `--md`) | ตรวจรับกับข้อมูล A1 (`$A`) |
|---|---|---|---|
| A `analyze_javascript_application` | `nr.input_path` · `ev.subject.digest.sha256` · `nr.statistics.relevant_files` · `nr.graph.nodes[].kind` · `nr.graph.edges.length` · `nr.graph.coverage.status` · `nr.semantic_graph.coverage.status` · endpoint/storage = `node.observations[0].properties.{value,mechanism,storage_kind,name}` · `(nr.limitations ?? ev.limitations).length` | `operation evidence_id evidence_id_short input subject_digest subject_digest_short(12) files node_kinds{kind:n} edges coverage{application,semantic} endpoints[{value,mechanism,count}] (รวมค่าซ้ำ · เรียงตาม value) storage[{kind,name,mechanism}] limitations recovered_source_files[]` · recovered = label ของ node `source-module` → ตัด `^(\.\.\/)+` → `decodeURIComponent` → เก็บเฉพาะที่ตรง `^(app\|components\|lib)\/.+\.(ts\|tsx)$` และไม่มี `/__nextjs-internal-proxy` → unique + sort · `--md` = 3 ตาราง: `\| ชนิด node \| จำนวน \|` · `\| endpoint \| mechanism \| จำนวน \|` · `\| storage \| name \| mechanism \|` + บรรทัด `recovered_source_files: N` | `$A/v1-static.json` → files 21 · edges 68 · node_kinds endpoint 9 / javascript-asset 21 / javascript-module 19 / unknown 10 / storage 3 / artifact 1 · endpoints 9 (มี `a` `b` `c`) · storage 3 แถว `name: null` · `ev_ca3bd308` · digest `7ab17795d9f1` · `$A/v1-server.json` → files 449 · `recovered_source_files` 53 รายการ (ตรงรายชื่อใน `rea-probe/evidence/02`) |
| B `inspect_web_network_capture` | `nr.records[]` (ใช้ `x.reported ?? x`) · `.request.{method,url,postData.text}` · `.response.{status,content.text}` | `records api[{method,path,status,req_keys,res_keys}]` เฉพาะ URL ที่มี `/api/` · `--md` = `\| # \| method \| path \| status \| request body keys \| response keys \|` (ตามตัว `rea-probe/rea-summarize.mjs` เดิม) | `$A/har-inspect-redacted.json --md` = 4 แถวตรงกับ `rea-probe/evidence/04-har-api-table.md` |
| C `trace_application_feature` | `nr.seed` · `nr.direction` · `nr.summary` · `nr.coverage.status` · `nr.graph.nodes[]` → `kind` · `observations[0].label` · `observations[0].evidence.location.value.path` | `evidence_id_short source_evidence_id seed{kind,value} direction summary{matched_seeds,traced_nodes,traced_edges,terminal_paths,native_handoffs,observed_facts,inferred_facts,unknown_facts,unavailable_facts} coverage nodes[{kind,label,path}] (เรียง kind แล้ว label) source_files[]` (label ของ `source-module` ตัด `^(\.\.\/)+`) · `--md` = `\| kind \| label \|` + บรรทัด summary | `$A/trace-s1.json` → matched_seeds 13 · traced_nodes 16 · nodes 16 แถว · `source_files` = `["app/api/coupons/validate/route.ts"]` · มี label `chunks/ssr/components_CartView_tsx_12yx7o-868btn._.js` |
| D `compare_source_to_bundle` | `nr.summary` · `nr.items[].{source_path,status,confidence}` | `evidence_id_short summary` (ครบ **7 คลาสตามลำดับ** `unchanged modified removed split merged duplicated unknown`) `items[]` = เฉพาะ status ≠ `unchanged` เรียงตาม path (`--all` = ทุกแถว) · `--md` = บรรทัดตัวนับ 7 คลาส + `\| source_path \| status \| confidence \|` | `$A/s2b-server.json` → summary `{"unchanged":44,"modified":0,"removed":0,"split":0,"merged":0,"duplicated":9,"unknown":3}` · items 12 แถว = รายการ `s2b-server` ใน `rea-probe/evidence/07-source-to-bundle.summary.json` |
| D′ `--s2b-table a b c d` | ไฟล์ผล `compare_source_to_bundle` 4 ไฟล์ | Markdown: `\| source file \| <ชื่อไฟล์ a ไม่มี .json> \| … d \|` เฉพาะ source_path ที่ status **ไม่เหมือนกันทั้ง 4** · ไฟล์ที่ไม่มี path นั้น = `(not in src)` · เรียงตาม path · ต่อด้วย 4 บรรทัด `<ชื่อไฟล์>.json <summary JSON>` | `--s2b-table $A/s2b-server.json $A/s2b-v1src-v2server.json $A/s2b-v2src-v1server.json $A/s2b-v2src-v2server.json` = 2 แถว (`app/api/coupons/active/route.ts` · `lib/pricing.ts`) + 4 บรรทัดตัวนับ ตรงกับ `rea-probe/evidence/07-s2b-diff-table.md` |
| E `capture_browser_scenario` | `nr.duration_ms` · `nr.completeness` · `nr.steps[].{step_id,status,elapsed_ms,after_url.url}` · ขั้นสุดท้าย `artifacts.{storage.value,accessibility.value.text,screenshot.value.data_base64}` · `nr.events.items[]` (`kind` = `request`/`response`/`network-content`, จับคู่ด้วย `transaction_id`) | `evidence_id_short duration_ms completeness{status,missing_sections} steps[{step_id,status,elapsed_ms,after_url}] steps_completed ("<completed>/<ทั้งหมด>") local_storage_keys[] session_storage_keys[] cookies(count) a11y_lines[]` (บรรทัดของ accessibility text ที่มี `฿` หรือ `คูปอง` หรือ `PAW` · trim · ≤ 40) `api_calls[{method,path,status,request_body,response_body}]` (เฉพาะ URL มี `/api/` · body = `network-content` ที่ `body.state === "captured"` ถอด base64 เป็น UTF-8) · `--png <file>` = เขียน `Buffer.from(data_base64,"base64")` ของขั้นสุดท้ายลงไฟล์ (สร้างโฟลเดอร์แม่) แล้วพิมพ์ `png: <file> (<bytes> bytes)` · `--md` = `\| step \| status \| ms \| url \|` + บรรทัด keys + a11y | `$A/scenario-capture.json --png $T/final.png` → `steps_completed` `"11/11"` · completeness `incomplete` · keys `pp-recent pp-cart pp-coupon` · a11y มี `ใช้คูปอง PAW10 แล้ว` `-฿6` `฿113` · api_calls มี POST `/api/coupons/validate` 200 · `cmp $T/final.png _solution/_design/rea-probe/evidence/05-scenario-final.png` exit 0 (182,349 bytes) |
| F `compare_application_versions` | `nr.summary` · `nr.items[].{node_kind,status,left_node_id,right_node_id}` · label = หา node id ใน `nr.graph.nodes[]` → `observations[0].label` (ไม่เจอ = node id) | `evidence_id_short summary{unchanged,added,removed,changed,unknown} items_total by_kind_status{node_kind:{status:n}} sample[]` = 20 แถวแรกที่ status ≠ `unchanged` `{status,node_kind,label}` (`--all` = ทุกแถว) · `--md` = บรรทัด summary + `\| node_kind \| status \| จำนวน \|` | `$A/cmp-server.json` → summary `{"unchanged":0,"added":0,"removed":0,"changed":273,"unknown":1479}` · items_total 1752 · sample 20 แถว |
| G `HistoricalSourceGraph` (ผล `import-reference-source`) | `ev.schema` `ev.root_sha256` `ev.entries.length` `ev.languages` `ev.inventory_state` | `schema root_sha256_short(12) entries languages inventory_state` | `$A/v1-source-graph.json` → `HistoricalSourceGraph` · `038405ccb558` · entries 154 · inventory_state `partial` |
| อื่น ๆ | — | `operation evidence_id_short keys` (key ของ `nr`) | — |

### 7.7 สัญญา `rea/rea-input.mjs` (#10)

**CLI:** `node rea/rea-input.mjs <โหมด> …` · path relative = จาก **cwd** · อ่านทุกไฟล์แล้วตัด BOM ก่อน `JSON.parse` · เขียนผลด้วย `writeFileSync(out, JSON.stringify(obj), "utf8")` (บรรทัดเดียว · UTF-8 **ไม่มี BOM**) · สร้างโฟลเดอร์แม่ของ out ถ้ายังไม่มี · พิมพ์ 1 บรรทัด `wrote <out> (<bytes> bytes)` · ผิด usage/ค่าไม่ถูกต้อง → exit 2 พร้อม usage · **ลำดับ key ต้องตามตาราง** (ตรวจรับเทียบแบบ `JSON.stringify` ตรงตัว)

| โหมด | argv | ตรวจก่อนเขียน | JSON ที่เขียน (ลำดับ key ตามนี้) | ตรวจรับ (ต้องพิมพ์ `true`) |
|---|---|---|---|---|
| `trace` | `<analyze.json> <seedKind> <seedValue> <direction> <out.json>` | `ev.operation === "analyze_javascript_application"` · direction ∈ `incoming outgoing both` · seedKind ∈ `string api` (2 แบบที่พิสูจน์แล้ว) | `{"application": <ev ทั้งก้อน>, "seed": {"kind": seedKind, "value": seedValue}, "direction": direction}` | `node rea/rea-input.mjs trace $A/v1-server.json string coupons/validate incoming $T/t.in.json && node $T/jsoneq.mjs $T/t.in.json $A/trace-s1.in.json` |
| `s2b` | `<reference-source.json> <analyze.json> <out.json>` | ไฟล์แรกเป็นผล `import-reference-source --json` = **HistoricalSourceGraph ทั้งไฟล์** (`ref.schema === "HistoricalSourceGraph"` · ไม่มี evidence wrapper) · ไฟล์สองเป็น analyze | `{"reference": <ไฟล์แรกทั้งก้อน>, "application": <ev ทั้งก้อน>}` | `node rea/rea-input.mjs s2b $A/v1-source-graph.json $A/v1-server.json $T/s.in.json && node $T/jsoneq.mjs $T/s.in.json $A/s2b-server.in.json` · และ `… s2b $A/v1-source-graph.json $A/v2-server.json …` เทียบ `$A/s2b-v1src-v2server.in.json` |
| `compare` | `<left-analyze.json> <right-analyze.json> <out.json>` | ทั้งสองเป็น analyze | `{"left": <ev ซ้าย>, "right": <ev ขวา>}` | `node rea/rea-input.mjs compare $A/v1-server.json $A/v2-server.json $T/c.in.json && node $T/jsoneq.mjs $T/c.in.json $A/cmp-server.in.json` |
| `view` | `<analyze.json> <out.json>` | analyze | `{"source": {"kind": "inline", "evidence": <ev>}, "view": {"kind": "summary"}}` | `node rea/rea-input.mjs view $A/v1-static.json $T/v.in.json && node $T/jsoneq.mjs $T/v.in.json $A/view-summary.json` |

ทุกแถว: `head -c3 <out> | od -An -tx1` ต้องไม่ใช่ `ef bb bf`

### 7.8 สัญญา `rea/record-har.mjs` (#11)

| เรื่อง | กำหนด |
|---|---|
| CLI | `node rea/record-har.mjs [--base <url>] [--out <dir>]` |
| base URL | `--base` > env `BASE_URL` > `http://localhost:4000` |
| โฟลเดอร์ผล | `--out` (relative = จาก **cwd**) > env `OUT_DIR` (relative = จาก cwd) > `path.resolve(dirname(fileURLToPath(import.meta.url)), "..", "out")` = `<รากบท>/out` · `mkdirSync(recursive)` |
| ผล | `<out>/pawpantry-main.har` (recordHar `content: "embed"` `mode: "full"` urlFilter เดิม) · `<out>/har-steps.json` = `{"base", "out", "total_ms", "steps": [{"step","ms","url"}]}` |
| เส้นทาง | 8 ขั้นเดิมของ `rea-probe/record-har.mjs` ตามตัว (reset → home → ค้นหา "แซลมอน" → สินค้า → ใส่ตะกร้า ×3 → PAW10 → login demo → สั่งซื้อ COD) |
| ล้ม | พิมพ์ `✗ <step>: <message>` · ปิด browser · exit 1 |
| คอมเมนต์หัวไฟล์ | `// ใช้: node rea\record-har.mjs [--out out\after]  (รันจากรากบท · ต้องมี npm install ใน rea\)` |

## 8. IMAGES (เป้า 54 ไฟล์: jpg 27 · png ไดอะแกรม 9 · png ผล 13 · screenshot 3 · gif 2)

**Prefix jpg บท 05 (ต่อหน้าทุกพรอมต์):** `Cute kawaii flat cartoon illustration, thick clean outlines, soft bright pastel colors, bright PawPantry pet-food shop setting with shelves of cat and dog food, paw-print decorations and sky with fluffy clouds through big windows, a cheerful boy with messy brown hair in a blue hoodie (the tester, often holding a clipboard or magnifying glass), a friendly round white robot with a black screen face, glowing blue eyes and a curved smile, an antenna topped with a small blue ball, the robot has NO logo, NO emblem and NO theater-mask icon anywhere on its body, cute orange cat and brown puppy characters, Thai title text in bold navy rounded font inside a white rounded label, short Thai speech bubbles of at most 5 words, 3:2 landscape, 1280x853, no watermark.`
กติกาเพิ่ม: ข้อความในภาพห้ามมีตัวเลข BUG-01 (฿999 / ฿1,049) ก่อน LAB 5 · ภาพ LAB 5–6 ใช้ได้ (ลูกค้าแจ้งเองแล้ว) · เปิดดูทุกรูปหลังสร้าง

### 8.1 jpg (Codex · `cyolo exec`)

| ไฟล์ | ใช้ที่ | ชนิด | พรอมต์ (ต่อท้าย prefix) |
|---|---|---|---|
| `intro-01-legacy-handover.jpg` | หัวบท | jpg gen | A departing developer team waving goodbye through the shop door carrying boxes, leaving on the counter a dusty laptop showing the PawPantry website, a thin folder labeled "HANDOVER", and an old test toolbox; the boy and the robot step in, the boy looks surprised holding the folder, the orange cat sits on the laptop. Title label "รับช่วงระบบเดิม". Speech bubble from boy: "เอกสารแค่นี้เหรอ?" |
| `intro-02-understand-lock-change-prove.jpg` | 🧭 | jpg gen | Four connected stepping stones across a small river in the shop garden, each with a sign: "เข้าใจ" (magnifying glass), "ล็อก" (padlock on a test checklist), "แก้" (wrench), "พิสูจน์" (stamp with check mark); the boy and robot hop across, the puppy follows. Title label "เข้าใจ → ล็อก → แก้ → พิสูจน์" |
| `concept-01-reverse-engineering.jpg` | 🎓1 | มีแล้ว | (forward vs reverse) ไม่ต้องสร้างใหม่ |
| `concept-02-static-vs-dynamic.jpg` | 🎓2 | jpg gen | Split scene: left, the robot X-rays a closed cardboard box labeled ".next bundle" on a lightbox showing code lines inside, sign "static: ดูไม่ต้องรัน"; right, the boy watches a running mini toy shop on a CCTV monitor where a toy cart moves and a letter flies to a mailbox, sign "runtime: ดูตอนรันจริง"; between them a small sign "เห็นคนละอย่าง". Title label "static vs dynamic" |
| `concept-03-black-white-grey-box.jpg` | 🎓3 | มีแล้ว ✅ | rename แล้ว (เดิม 02) |
| `concept-04-rea-or-read.jpg` | 🎓3 | jpg gen | A fork in a path with two signposts: left path leads to an open book labeled "source ครบ" with sign "อ่าน repo เลย"; right path leads to a sealed shipping box and a running laptop with sign "ใช้ REA ส่อง"; the robot holds a small map, the boy points left while thinking. Title label "ใช้ REA เมื่อไร?" |
| `concept-05-evidence-not-opinion.jpg` | 🎓4 | มีแล้ว ✅ | rename แล้ว (เดิม 03) |
| `concept-06-missing-not-absent.jpg` | 🎓4 | มีแล้ว ✅ | rename แล้ว (เดิม 04) |
| `concept-07-content-digest.jpg` | 🎓5 | jpg gen | Two identical-looking parcels on a scale-like scanner, same label "orders.ts", but each has a different fingerprint sticker (one blue swirl, one orange swirl); the robot scans them with a magnifier and holds a sign "คนละกล่อง!"; the boy writes "SHA-256" on a clipboard. Title label "ลายนิ้วมือของไฟล์" |
| `concept-08-version-compare.jpg` | 🎓5 | มีแล้ว ✅ | rename แล้ว (เดิม 06) |
| `concept-09-feature-trace.jpg` | 🎓6 | มีแล้ว ✅ | rename แล้ว (เดิม 05) |
| `concept-10-passive-driven-har.jpg` | 🎓6 | มีแล้ว ✅ | rename แล้ว (เดิม 07) |
| `concept-11-obligation-ledger.jpg` | 🎓7 | jpg gen | A big checklist board titled with rows of small checkboxes; each completed row has three stamps (a person icon "เจ้าของ", a test tube "กรณีทดสอบ", a green check "ผลตรวจ"); one row is covered by a grey cloud with a padlock labeled "unknown"; the robot stamps, the boy reviews. Title label "ของใหม่ต้องทำได้เท่าของเดิม" |
| `concept-15-characterization-lock.jpg` | 🎓7 | jpg gen | The robot takes a photo of a slightly crooked cat-food shelf and pins the photo on a wall labeled "พฤติกรรมเดิม"; next to it a tiny ladybug hides on the crooked shelf; the boy holds a ruler labeled "[D] ร้าน" and frowns. Speech bubble from boy: "ล็อก ≠ ถูก". Title label "Characterization test" |
| `concept-12-evidence-badge-e.jpg` | 🎓7 | มีแล้ว ✅ | rename แล้ว (เดิม 08) |
| `concept-13-ethics-permission.jpg` | 🎓8 | มีแล้ว ✅ | rename แล้ว (เดิม 09) |
| `concept-14-rea-limits.jpg` | 🎓8 | jpg gen | The robot shines a flashlight that lights up only part of a warehouse: lit area shows boxes and API signs; a locked back room labeled "server" stays dark; above, a thought cloud labeled "ร้านอยากได้อะไร?" floats out of reach; the boy notes on a clipboard "บอกไม่ได้". Title label "สิ่งที่ REA บอกไม่ได้" |
| `concept-17-reserved-ports.jpg` | LAB 0 | jpg gen | A parking lot of numbered spaces; spaces around 3000 are blocked by orange cones and a sign "Windows จองแล้ว"; the robot drives a small delivery van labeled "PawPantry" into space 4000 marked green; the boy holds a checklist. Title label "พอร์ตที่ถูกจอง" |
| `concept-18-agent-reads-repo.jpg` | LAB 1 | jpg gen | The robot sits on a stack of folders reading code pages and drawing a colorful map titled "CODEBASE-MAP"; each map pin has a small tag "ไฟล์:บรรทัด"; the boy reviews the map with a red pen, circling one pin marked "เดา?". Title label "ให้ AI อ่าน → เราตรวจ" |
| `concept-16-legacy-safety-net.jpg` | LAB 4 | jpg gen | An old circus safety net under a tightrope, mostly strong and green but with one hole; the robot walks the rope carrying a box; the boy points at the hole while patching a new net piece labeled "test ใหม่"; a sign on the net post "ชุดเทสต์เดิม เขียวหมด". Title label "เทสต์เขียว ≠ ไม่มีบั๊ก" |
| `concept-19-customer-ticket.jpg` | LAB 5 | jpg gen | A cheerful young woman customer (bob haircut, yellow cardigan) holds a phone showing a receipt and a shop screen side by side with different totals (no exact numbers, just "฿ ?" and "฿ ?!"); a small ladybug with a question mark sits on the receipt; the boy takes notes, the robot opens a laptop. Title label "ลูกค้าแจ้ง: เงินไม่ตรง" |
| `concept-20-root-vs-symptom.jpg` | LAB 6 | jpg gen | A weed in the shop garden: the robot holds scissors near the leaves with sign "แก้ปลายเหตุ" (crossed out), the boy pulls the weed out by the root with sign "แก้ที่ต้นเหตุ" (check mark); a duplicate second root is visible underground. Title label "ต้นเหตุ vs ปลายเหตุ" |
| `concept-21-ask-before-build.jpg` | LAB 7 | jpg gen | A gift box with a ribbon on the counter; a change request card pinned above it with three question marks; the boy raises a hand asking the shop owner (a friendly shopkeeper with an apron and a cat-paw name tag) while the robot waits with tools down. Speech bubble from boy: "ก่อนหรือหลังลด?". Title label "ถามก่อนสร้าง" |
| `concept-22-red-then-green.jpg` | LAB 8 | jpg gen | A traffic light with three test cards: first the red light shows a test card "แดง: ยังไม่มีฟีเจอร์", then the robot builds a gift-wrap station, then the green light shows "เขียว"; three small browser icons (no brand logos, just colored circles) cheer. Title label "แดงก่อน → เขียวหลัง" |
| `concept-23-change-proof.jpg` | LAB 9 | jpg gen | Three scrolls laid side by side on a table labeled "ตั้งใจแก้", "hash ต่าง", "bundle ต่าง"; the robot draws lines connecting matching items across the scrolls; the boy holds a stamp "ส่งมอบได้". Title label "แก้แค่ที่ตั้งใจ" |
| `concept-24-solo-loop.jpg` | LAB 10 | jpg gen | The boy alone at a desk with a circular arrow poster showing four icons (magnifier, red test, wrench, green check), the robot gives a thumbs-up from the side, the puppy holds a small flag "ฝึกเดี่ยว". Title label "ครบวงจรด้วยตัวเอง" |
| `outro-01-handover-next.jpg` | 🎉 | jpg gen | The boy and robot hand a neat folder labeled "CHANGE-REPORT" to the next team member at the shop door; on the wall the old "HANDOVER" folder now looks thick and organized; a signpost points to a Thai spa building in the distance labeled "บท 06". Title label "ส่งต่ออย่างมืออาชีพ" |


### 8.2 png (HTML → PNG ด้วย `tools/render-png.mjs` · Noto Sans Thai · 2560 px · < 600 KB · `house.css`)

| ไฟล์ | ใช้ที่ | ชนิด | เลย์เอาต์ |
|---|---|---|---|
| `overview-5-phases.png` | 🧭 | png diagram | หัว "รับช่วงระบบเดิม: เข้าใจ → ล็อก → แก้ → พิสูจน์" · การ์ด 5 ใบตามสีช่วง ① เข้าใจ LAB 1–3 (pill `CODEBASE-MAP` `SYSTEM-MAP` `API-INVENTORY`) ② ล็อก LAB 4 (`BASELINE`) ③ แก้บั๊ก LAB 5–6 (`BUG-01`) ④ ฟีเจอร์ LAB 7–8 (`CR-01`) ⑤ พิสูจน์ LAB 9–10 (`CHANGE-PROOF` `CHANGE-REPORT`) · แถบล่าง 🎯 "โค้ดบอก ≠ ระบบทำ ≠ ร้านต้องการ" |
| `lab-flow.png` | 🗺️ | png diagram | ซ้าย "ตอนเริ่มมี" (petshop · e2e-legacy · rea · TEST-DATA · HANDOVER-NOTES) → กล่อง LAB 0–10 เรียงตามช่วงสี มีป้าย 🔍/✏️ และ pill ไฟล์ที่ได้ · แถบล่าง "✏️ แก้ repo 6 จาก 10 LAB" |
| `when-rea.png` | 🎓3 | png diagram | ผังตัดสินใจ 4 ขั้น: มี source ครบและเชื่อได้? → อ่าน repo · มีแค่ build? → analyze + trace · อยากเห็นตอนรัน? → HAR / scenario · ไม่แน่ใจว่า build ตรง source? → source-to-bundle · แถบล่าง "REA = ตาสำหรับของที่ส่งมอบ/รันอยู่" |
| `evidence-4-buckets.png` | 🎓4 | png diagram | 4 ถังสี 🔵 static · 🟢 runtime · 🟡 inference · ⚪ unknown แต่ละถังมี "แปลว่า" + ตัวอย่างจริง (`/api/orders` call:fetch · `pp-cart` จาก scenario · `electron-renderer` · endpoint `a b c`) · แถบล่าง "หาไม่เจอ ≠ ไม่มี" |
| `oracle-badges-e.png` | 🎓7 | png diagram | ต่อจาก `oracle-badges.png` บท 04: ป้าย [D] เขียว · [R] เหลือง · **[E] ฟ้า ใหม่** · [O] แดง · 2 คอลัมน์ "เชื่อได้ว่าระบบควรทำ" / "เชื่อได้ว่าระบบทำอยู่" · แถบล่าง "[E] ขัด [D] = ผู้ต้องสงสัยบั๊ก · [D] ชนะ" |
| `safe-change-loop.png` | LAB 5 | png diagram | วงกลม 8 ขั้น ① ล็อก ② ทำซ้ำ (แดง) ③ impact ④ แก้เล็กสุด ⑤ เขียว ⑥ regression 3 เบราว์เซอร์ ⑦ เทียบเวอร์ชัน ⑧ CHANGE-REPORT · ใต้ขั้นมี LAB ที่ทำ · แถบล่าง "ห้ามแก้เทสต์ให้ผ่าน" |
| `re-taxonomy.png` · `three-eyes.png` | 🎓1 · 🎓3 | มีแล้ว | — |
| `rea-architecture.png` | 🎓6 | มีแล้ว · เรนเดอร์ใหม่ (§7 #17) | `localhost:3000` → `localhost:4000 · petshop:3000` · กล่อง CDP `inspect-web-page` (ไม่เคยพิสูจน์ · บทนี้ไม่ใช้) → `compare-source-to-bundle` และย้าย CDP ไปแถวเทา "ไม่ใช้" |

### 8.3 ผลจริง / หน้าจอ / GIF (จาก `results/` และ `shots/` ของ RUNNER เท่านั้น)

| ไฟล์ | LAB | ชนิด | เนื้อหา |
|---|---|---|---|
| `lab0-checklist.png` | 0 | png result | ตารางธีมมืด: Docker · Node · ช่วงพอร์ตที่จอง (มี 3000 ไหม) · 4000 ว่าง · image rea-lab · doctor (exit 1 อธิบาย) · เว็บ healthy · สรุปเขียว "พร้อม N/N" |
| `lab1-codebase-map.png` | 1 | png result | ตัดส่วน D กฎธุรกิจ 5–6 แถว + ส่วน G เอกสารบอก ≠ โค้ดทำ |
| `lab2-rea-static.png` | 2 | png result | ตาราง node kinds static vs server · coverage · endpoint ที่กู้ได้ (มี `a b c` ไฮไลต์เทา) |
| `lab2-triangulation.png` | 2 | png result | ตาราง REA เห็น | โค้ดบอก | ตรงไหม ✅/⚠️/❓ 6–8 แถว |
| `lab3-api-inventory.png` | 3 | png result | ตาราง API จาก HAR + แถวเขียว "รหัสผ่านถูกปิดใน out/har.json" |
| `lab3-scenario-final.png` | 3 | screenshot | ภาพสุดท้ายจาก `capture-browser-scenario` (ตะกร้า + PAW10) |
| `lab4-baseline.png` | 4 | png result | ผล suite เดิม 3 เบราว์เซอร์ + test ใหม่ + expected-fail |
| `lab5-repro.png` | 5 | png result | ตารางกรณี ตะกร้า / ปุ่ม / คำสั่งซื้อ / ถูกไหม |
| `site-order-bug01.png` | 5 | screenshot | หน้า `/orders/PP-…` ยอดที่ไม่ตรงปุ่ม (headless 1280×800 · วงแดง) |
| `gif-bug-BUG-01.gif` | 5 | gif | test BUG-01 ล้มบน chromium (วงแดงจุดคลิก · ป้ายชื่อ test) < 3 MB |
| `lab6-fix-compare.png` | 6 | png result | test ก่อน/หลังแก้ + กรณีเดิมยิงซ้ำ |
| `lab7-impact.png` | 7 | png result | ตาราง impact (ไฟล์ · ใครเรียก · test ที่ต้องรันซ้ำ) |
| `site-checkout-giftwrap.png` | 8 | screenshot | หน้า checkout ติ๊กห่อของขวัญ แถวสรุป + ปุ่มยืนยัน |
| `gif-TC-GIFT-02.gif` | 8 | gif | TC ค่าขอบ ฿1,499 / ฿1,500 ผ่าน (หรือ TC ขอบที่ agent ตั้งชื่อ) |
| `lab8-regression.png` | 8 | png result | ชุด × chromium/firefox/webkit |
| `lab9-s2b-4way.png` | 9 | png result | ตาราง source-to-bundle 4 ทิศ เฉพาะไฟล์ที่ต่าง + 3 รายการตรงกันไหม |
| `lab9-change-report.png` | 9 | png result | หัวตาราง CHANGE-REPORT |
| `lab10-solo.png` | 10 | png result | ขั้น | หลักฐาน | ผล ของ PR-1 |

## 9. ความเสี่ยง / ต้องยืนยันตอนรันจริง

| เรื่อง | ทำไมเสี่ยง | ให้ RUNNER ทำ |
|---|---|---|
| `host.docker.internal:4000` (ทางสำรอง D7) | ไม่เคยรันจริง (A1 publish พอร์ตไม่ได้) · resolve เป็น IPv6 ได้ → Chromium ใน container อาจต่อไม่ได้แม้ `node fetch` ได้ | RUNNER LAB 0 ทดสอบ 2 ชั้น: `node fetch` + `capture-browser-scenario` ด้วยสำเนา scenario ที่ `start_url` = `http://host.docker.internal:4000/` (ไม่ใส่ `-Network`) จดผล · พรอมต์ใช้ network `pawpantry05_default` ที่พิสูจน์แล้ว |
| compose project ชนบท 02/03 | ถ้า `name: pawpantry05` หาย project จะเป็น `petshop` → ไป recreate/ลบ container บทอื่น | RUNNER ก่อน LAB 0 ตรวจ `docker compose config` บรรทัดแรก = `name: pawpantry05` · LAB 3 จด `docker network ls` |
| พอร์ต 4000 ชนบท 06 | บท 05 และ 06 ใช้ host 4000 ทั้งคู่ | RUNNER "คิวพอร์ต 4000": ห้ามรัน LAB บท 05 ขณะ `sabai06-web` ถือ 4000 (บท 06 ย้ายไป `WEB_PORT=41xx` ใน sandbox ได้ ตาม 06 LESSON-PLAN P3) |
| ExecutionPolicy / shell | Windows 11 ค่าเริ่มต้น Restricted · agent อาจใช้ Git Bash | ทุกพรอมต์บอก PowerShell + `-ExecutionPolicy Bypass -File` · LAB 0 ตรวจ `Get-ExecutionPolicy -List` · RUNNER จดว่า agent ใช้ shell ไหนจริง |
| คำสั่งนาน > 2 นาที | timeout ค่าเริ่มต้นของเครื่องมือ agent = 2 นาที | พรอมต์ระบุ timeout ≥ 10 นาที/รันเบื้องหลัง · RUNNER จดถ้า agent รันซ้ำเพราะ timeout |
| suite บท 02 กับ build ใหม่ | ยังไม่เคยรันกับ build ที่เอา BUG_MODE ออก + มี BUG-01 | LAB 4 จดผล 3 เบราว์เซอร์ · ถ้าไม่ใช่ 40/40 ให้รายงานผู้สร้างบทก่อนเขียน README |
| `.claude/settings.json` deny | glob `tests/*.ts` ต้องไม่กันไฟล์ใน `tests/new/` · deny `Edit(...)` ไม่กันการเขียนผ่าน shell | LAB 1 ลองแก้ไฟล์เดิม (ต้องถูกปฏิเสธ) และสร้างไฟล์ใน new/ (ต้องได้) · ทุก LAB จดว่า agent เลี่ยงไปเขียนผ่าน shell ไหม |
| CODEBASE-MAP โหลดอัตโนมัติ | ถ้า CLAUDE.md `@import` CODEBASE-MAP LAB 5 จะไม่ black-box จริง | LAB 1 สั่งให้ CLAUDE.md อ้าง CODEBASE-MAP เป็นชื่อไฟล์ธรรมดา (ไม่ใช้ `@`) · LAB 5 ขั้นที่ 1 ห้ามเปิด CODEBASE-MAP ส่วน D · RUNNER จดถ้า agent รู้ต้นเหตุก่อนขั้นที่ 3 |
| test ใหม่รันขนานกับ suite เดิม | suite เดิม `workers: 4` reset ครั้งเดียว · test ใหม่ห้าม reset | ดูความนิ่ง (รันซ้ำ 2 รอบ) · flaky ให้จด |
| CR-01 / PR-1 จาก agent | ไม่ deterministic · PR-1 ยังไม่เคยมีใคร implement | จดไฟล์ที่แตะจริง เทียบ `CR-DESIGN` §1.4 · ถ้าแก้แบบปลายเหตุใน LAB 6 ให้ดูว่า LAB 8 พังตามที่ทำนายไหม (เก็บเป็น 👀) |
| เวลา build image REA | 2.65 GB · ไม่เคยวัดบนเครื่องผู้เรียน | จดเวลา · README แนะนำ build ก่อนเข้าคลาส |
