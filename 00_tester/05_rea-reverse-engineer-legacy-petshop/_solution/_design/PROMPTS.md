# PROMPTS · บท 05 รับช่วงระบบเดิม PawPantry (REA + legacy)

ทุก LAB = 1 พรอมต์ (LAB 9 มี 2 ส่วน) วางใน Claude Code ที่ **โฟลเดอร์บท** ได้ทันที · แนะนำเปิดเซสชันใหม่ทุก LAB
ไฟล์ที่แต่ละ LAB สร้างคือความจำที่ส่งต่อ · พรอมต์ไม่อ้าง "LAB x" (เซสชันใหม่ไม่รู้จัก) อ้างชื่อไฟล์แทน
คำสั่ง shell ทุกตัวเป็น **PowerShell** และรันจากโฟลเดอร์บท เว้นแต่พรอมต์บอกโฟลเดอร์อื่น · **ทุกพรอมต์ที่มีคำสั่งบอก shell ในตัวพรอมต์เอง** (BRIEF D9) เพราะ Claude Code บน Windows อาจใช้ Git Bash เป็นค่าเริ่มต้น
- บรรทัดมาตรฐาน **[SH]** (อยู่ในวงเล็บต้นพรอมต์): `รันคำสั่ง shell ทุกตัวด้วย PowerShell จากโฟลเดอร์บท · ถ้ามีแต่ bash ให้เขียนคำสั่งลงไฟล์ rea\scratch\run.ps1 แล้วรัน powershell -NoProfile -ExecutionPolicy Bypass -File rea\scratch\run.ps1 · ห้ามแปลงคำสั่งเป็น bash เอง`
- REA เรียกด้วย `powershell -NoProfile -ExecutionPolicy Bypass -File .\rea\rea.ps1 …` เสมอ (ExecutionPolicy ค่าเริ่มต้นของ Windows 11 = Restricted · `.\rea\rea.ps1` ตรง ๆ จะถูกปฏิเสธ) · ในพรอมต์ย่อว่า `REA …` หลังประกาศครั้งแรก
- คำสั่งนาน > 2 นาทีมีวงเล็บ **[นาน]** = `(นาน ~N นาที: ตั้ง timeout อย่างน้อย 10 นาที หรือรันเบื้องหลังแล้วรอจนจบ ห้ามสั่งซ้ำระหว่างรอ)` เพราะ timeout ค่าเริ่มต้นของเครื่องมือ = 2 นาที
- `rea.ps1` ทิ้งบรรทัด `rea_progress` ใน stderr ให้เอง (หลัง RUN05 · ไม่ต้องใส่ `2>$null`) · `rea-summarize.mjs` แสดง key ของ HAR 2 ชั้น · `--samples` = body ตัวอย่างแบบย่อ · ผล analyze มีคอลัมน์ method (อ่านจาก bundle) และตาราง electron-renderer (รายละเอียด + ผลทดสอบ: `PROMPT-FIX-LOG.md`)
- สคริปต์ชั่วคราวของ agent อยู่ `rea\scratch\` (import `playwright` ได้เพราะใช้ `rea\node_modules` · ถูก `.gitignore`)
- regression 3 เบราว์เซอร์ใช้ `npm run test:all` ในโฟลเดอร์ e2e-legacy (ไม่ขึ้นกับ syntax env ของ shell)
- **FIX5 (12 ต.ค. 2026 หลัง RUN05 · ยังไม่รัน LAB ซ้ำทั้งพรอมต์):** ข้อห้าม `_solution/` ทุกพรอมต์ขยายเป็น `_solution/ fast_track/ และ README.md ของโฟลเดอร์บท` (D15) · LAB 1 ให้ settings.json deny `Read(/README.md)` `Read(./fast_track/**)` `Read(./_solution/**)` + CLAUDE.md เขียนข้อห้ามเดียวกัน · LAB 2 ข้อ 6(3) อ้างประโยค skill ของ REA แทนการเปิด README · LAB 3 ข้อ 5 หัวข้อ "ขอบเขตที่ได้รับอนุญาต" (จริยธรรม) · LAB 4 ย้ายวงเล็บ expected-fail ขึ้นข้อ 5 · LAB 7 ข้อ 2 เพิ่ม REA trace `api/orders` incoming · LAB 8 คำจำแนกเทสต์ล้ม 4 แบบ · LAB 9 ข้อ 1 ทางสำรองเมื่อไม่ใช่ git repo · ข้อ 5 คอลัมน์ "ที่มาของผลคาดหวัง" · ส่วน 2 ข้อ 3 "ห้ามเดาว่าผ่าน" · คำว่า test ในร้อยแก้วของพรอมต์ → "เทสต์" (ตรงบท 06)
- ทดสอบ rule อ่าน (FIX5 · `claude -p` sonnet ใน sandbox `C:/t/work/fix5deny-*`): `Read(./README.md)` **กัน `petshop/README.md` ด้วย** (pattern ไม่มี / กลางคำ = ทุกระดับ) · `Read(/README.md)` กันเฉพาะรากโฟลเดอร์ · `Read(./fast_track/**)` `Read(./_solution/**)` กันได้ · Grep ไม่คืนไฟล์ที่ถูกกัน · ชุดรวม (Edit 5 + Read 3) → 3 เป้าถูกปฏิเสธ `petshop/README.md` อ่านได้

เงื่อนไขตั้งต้น: โฟลเดอร์บททำตาม `LESSON-PLAN.md` ข้อ 7 ครบแล้ว (ไม่มี BUG_MODE · มี BUG-01 · compose `name: pawpantry05` · มี `e2e-legacy/` `rea/` `TEST-DATA.md`)

แต่ละ LAB มี: 💬 พรอมต์ (ตรงตัวตามที่จะอยู่ใน README) · 🎯 ผลที่คาดหวัง (ค่าที่ทำนายจากเอกสารออกแบบ ติดที่มาไว้ · **ไม่ใช่ผลจริง** ผลจริงต้องมาจาก `results/LABn_RESULT.md`) · ✔️ ไปต่อได้เมื่อ · (บาง LAB) 🧑 คำตอบของผู้เรียน/ร้าน สำหรับจุด "ถามผมก่อน" · 👀 ข้อสังเกตที่ README ควรบอก

---

## 🧰 ก่อนเข้าคลาส (ผู้เรียนรันเองในเทอร์มินัล PowerShell · ไม่ใช่พรอมต์)

```powershell
cd <โฟลเดอร์บท 05>
docker build -t rea-lab:6.4.0 rea          # ครั้งเดียว · image ~2.65 GB · ใช้เวลานาน (ขึ้นกับเน็ต)
docker image ls rea-lab                     # ต้องเห็น 6.4.0
```

**ถ้าเจอปัญหา (README):**

| อาการ | ทำอย่างไร |
|---|---|
| `.\rea\rea.ps1 cannot be loaded because running scripts is disabled` | เรียกผ่าน `powershell -NoProfile -ExecutionPolicy Bypass -File .\rea\rea.ps1 …` (พรอมต์ทุกตัวใช้แบบนี้แล้ว) |
| พอร์ต 4000 มีคนใช้ | `docker ps` ดูว่าเป็น container บทอื่นไหม (บท 06 ก็ใช้ 4000) → `docker compose down` ในโฟลเดอร์บทนั้น |
| พอร์ต 4000 อยู่ในช่วงที่ Windows จอง | ผู้ดูแลเครื่อง: PowerShell (Run as Administrator) `net stop winnat` แล้ว `net start winnat` → ตรวจ `netsh interface ipv4 show excludedportrange protocol=tcp` ซ้ำ · ถ้ายังติด: `$env:WEB_PORT="4100"` ก่อน `docker compose up` และบอก agent ว่าเว็บอยู่ `http://localhost:4100` (เทสต์: `$env:BASE_URL="http://localhost:4100"` · HAR: `node rea\record-har.mjs --base http://localhost:4100`) · REA ใน container ไม่กระทบเพราะเข้าทาง network `pawpantry05_default` |
| REA ต่อเว็บไม่ได้ (`net::ERR_NAME_NOT_RESOLVED petshop`) | เว็บยังไม่ขึ้น หรือไม่ได้ใส่ `-Network pawpantry05_default` · ตรวจ `docker network ls` |
| agent รอคำสั่งนานแล้วรันซ้ำ | บอก agent "รันเบื้องหลังแล้วรอจนจบ ห้ามสั่งซ้ำ" |
| agent อ่านไฟล์/ค้นหาด้วย Git Bash ทั้งที่พรอมต์บอก PowerShell | ปกติ (การอ่านใช้ shell ไหนก็ได้) · กติกา PowerShell มีไว้สำหรับ **คำสั่งในพรอมต์** (docker · REA · npm · npx) |
| ชื่อสินค้าภาษาไทยจาก `Invoke-RestMethod` เพี้ยน · ไฟล์ JSON ภาษาไทยพังหลัง `Get-Content \| Set-Content` | PowerShell 5.1 ใช้ codepage เดิม → อ่าน API ด้วย `node -e "fetch('http://localhost:4000/api/products').then(r=>r.json()).then(j=>console.log(j))"` หรือดูหน้าเว็บ · แก้ไฟล์ JSON ด้วย node ไม่ใช้ `Get-Content \| Set-Content` |
| `npm run test:all` ล้มด้วย `409 สินค้าไม่พอ` หรือปุ่ม `qty-plus` กดไม่ได้ | ข้อมูลทดสอบ (สต็อก) หมด ไม่ใช่เว็บพัง: `global-setup` reset ครั้งเดียวต่อการรัน แต่ 3 เบราว์เซอร์ใช้สต็อกก้อนเดียวกัน → รันทีละเบราว์เซอร์ `npx playwright test --project=chromium` แล้ว `--project=firefox` `--project=webkit` (reset ทุกรอบ) |

---

## LAB 0 · เช็กเครื่อง + เตรียม REA (🔍)

```text
ตรวจเครื่องและเตรียมของให้พร้อมสำหรับบทนี้ ทุกค่าต้องมาจากคำสั่งที่รันจริง · ถ้าขั้นไหนไม่ผ่านให้หยุดแล้วบอกสาเหตุ
(รันคำสั่ง shell ทุกตัวด้วย PowerShell จากโฟลเดอร์บท · ถ้ามีแต่ bash ให้เขียนคำสั่งลงไฟล์ rea\scratch\run.ps1 แล้วรัน powershell -NoProfile -ExecutionPolicy Bypass -File rea\scratch\run.ps1 · ห้ามแปลงคำสั่งเป็น bash เอง · คำสั่งที่เขียนว่า "นาน" ให้ตั้ง timeout อย่างน้อย 10 นาที หรือรันเบื้องหลังแล้วรอจนจบ ห้ามสั่งซ้ำระหว่างรอ)
1. docker version · docker compose version · node -v (ต้อง 20 ขึ้นไป) · npm -v · Get-ExecutionPolicy -List
2. พอร์ตที่ Windows จองไว้: netsh interface ipv4 show excludedportrange protocol=tcp
   บอกว่าพอร์ต 3000 และ 4000 อยู่ในช่วงที่ถูกจองไหม · แล้วเช็กว่า 4000 มีโปรแกรมหรือ container ใช้อยู่ไหม (Get-NetTCPConnection -LocalPort 4000 -ErrorAction SilentlyContinue และ docker ps) ยังไม่ต้องปิดอะไร
   อธิบายสั้น ๆ ว่าทำไมบทนี้ใช้พอร์ต 4000 ไม่ใช่ 3000
3. REA: docker image inspect rea-lab:6.4.0 --format "{{.Size}}" · ถ้าไม่มี image ให้หยุดบอกผม (image นี้ต้อง build ก่อนเข้าคลาส ไม่ต้อง build เอง)
   แล้วรัน powershell -NoProfile -ExecutionPolicy Bypass -File .\rea\rea.ps1 doctor --filter-output healthy,checks (ผลสั้น ~30 บรรทัด) · คำสั่งนี้อาจจบด้วย exit 1 ให้อ่านผลก่อน แล้วบอกว่าข้อไหนไม่ผ่าน และกระทบงานเว็บของเราไหม
4. เปิดเว็บ: ในโฟลเดอร์ petshop รัน docker compose up -d --build (ครั้งแรกนาน ~3 นาที · ครั้งต่อไปใช้ cache ไม่กี่วินาที) รอจน container pawpantry05 ขึ้น healthy (docker ps) แล้วเรียก http://localhost:4000/api/health
   แล้วเช็กว่า REA ใน container มองเห็นเว็บทาง docker network: docker network ls (ต้องมี pawpantry05_default) และ
   docker run --rm --network pawpantry05_default --entrypoint node rea-lab:6.4.0 -e "fetch('http://petshop:3000/api/health').then(r=>r.text()).then(console.log)"
5. ในโฟลเดอร์ e2e-legacy และโฟลเดอร์ rea รัน npm install (โฟลเดอร์ละ ~1 นาที) แล้วในโฟลเดอร์ e2e-legacy รัน npx playwright install chromium firefox webkit (นาน ~3 นาที · ติดตั้งครั้งเดียวใช้ได้ทั้ง 2 โฟลเดอร์เพราะ Playwright เวอร์ชันเดียวกัน)
สรุปเป็นตาราง: รายการ | ผล | พร้อมไหม | ถ้าไม่พร้อมต้องทำอะไร
```

🎯 **ผลที่คาดหวัง**
- ExecutionPolicy ส่วนใหญ่ `Restricted`/`Undefined` · บางเครื่องเป็น `RemoteSigned` · ถ้ารันผ่าน Claude Code จะเห็น scope `Process = Bypass` = ปกติ → เรียก `.ps1` ผ่าน `-ExecutionPolicy Bypass -File` จึงรันได้ (ไม่ต้องเปลี่ยน policy ของเครื่อง)
- `docker compose up -d --build` ครั้งที่ 2 ขึ้นไปใช้ cache จบในไม่กี่วินาที (RUN05 ~11 s) ไม่ต้องตกใจที่ไม่ถึง 3 นาที
- ช่วงพอร์ตที่จองบนเครื่องผู้สอน: `2970–3069` และ `3070–3169` (มี 3000 อยู่ในช่วง) · 4000 ไม่อยู่ในช่วงและว่าง (BRIEF D5 · `REA-FEASIBILITY` §3)
- image `rea-lab:6.4.0` ~2.65 GB · `doctor --filter-output healthy,checks` ~30 บรรทัด (ไม่กรอง ~2,800 บรรทัด) · `healthy: false` exit 1 เพราะ hopper / ghidra / ida-registration = `missing_analysis_engine` และ `skill:identity` = `config_drift` · node 24.20 / ubuntu 24.04 ผ่าน → **ไม่กระทบงานเว็บ** (`REA-FEASIBILITY` §2.1)
- container `pawpantry05` healthy · `/api/health` → `{"ok":true}` · network `pawpantry05_default` มี · probe จาก container → `{"ok":true}` (D7)
- ตาราง ≥ 9 แถว

👀 "เว็บเดียวกันมี 2 ที่อยู่: เบราว์เซอร์ของเราใช้ `localhost:4000` · REA ที่อยู่ใน container ใช้ `petshop:3000` (ชื่อ service ใน docker network เดียวกัน)"

✔️ **ไปต่อได้เมื่อ:** Docker · Node · image rea-lab · `rea.ps1 doctor` รันได้ · เว็บ :4000 healthy · probe ใน network ได้ `{"ok":true}` · npm install ครบ 2 โฟลเดอร์

---

## LAB 1 · ให้ Agent อ่าน repo → CODEBASE-MAP + CLAUDE.md (🔍)

```text
ผมเพิ่งรับช่วงระบบร้าน PawPantry ในโฟลเดอร์ petshop ทีมเดิมออกไปหมดแล้ว ช่วยอ่าน repo แล้วเขียน CODEBASE-MAP.md และ CLAUDE.md ที่โฟลเดอร์บท
(ยังไม่ต้องแก้โค้ดใด ๆ · ห้ามเปิด _solution/ fast_track/ และ README.md ของโฟลเดอร์บท (มีเฉลย) · อ่านได้: petshop/ (รวม petshop/README.md) e2e-legacy/ rea/README.md TEST-DATA.md · อ่านไฟล์ใช้เครื่องมืออ่านไฟล์ได้ · ถ้าต้องรันคำสั่ง shell ให้ใช้ PowerShell)
1. ใช้ Explore subagent อ่าน petshop/ แล้วเขียน CODEBASE-MAP.md (บนสุดใส่วันที่ทำแผนที่) มี 6 ส่วน
   - A ภาพรวม: stack · รันยังไง · ข้อมูลเก็บที่ไหน (server / browser)
   - B หน้าเว็บ: URL | ไฟล์ | component หลัก | ข้อมูลมาจากไหน
   - C API: method | path | ไฟล์ | ทำอะไร | ต้อง login ไหม
   - D กฎธุรกิจ (ราคา คูปอง ค่าส่ง สต็อก ฟอร์ม): กฎ | ไฟล์:บรรทัด | ถูกใช้หรือถูกเขียนซ้ำที่ไหนอีก (browser / server / ข้อความบนจอ)
   - E state: อะไร | เก็บที่ไหน | key หรือตัวแปร | /api/test/reset ล้างได้ไหม
   - F ชุดเทสต์เดิมใน e2e-legacy: ครอบคลุมอะไร · ตรวจเงินที่หน้าไหน · ยังไม่ครอบคลุมอะไร
   ทุกแถวมีคอลัมน์ "ยืนยันจาก" = ไฟล์:บรรทัดที่เปิดดูจริง · ถ้าเดาจากชื่อไฟล์ให้เขียนว่า "เดา"
2. ส่วน G "เอกสารบอก ≠ โค้ดทำ": เทียบ petshop/README.md, petshop/HANDOVER-NOTES.md, TEST-DATA.md และคอมเมนต์ในโค้ด กับโค้ดจริง
   ตาราง: เรื่อง | เอกสารหรือคอมเมนต์บอก | โค้ดทำ (ไฟล์:บรรทัด) | ตรงไหม ✅ / ⚠️ / ❌ · ห้ามตัดสินเองว่าฝั่งไหนถูก ให้เขียนเป็นคำถามถึงเจ้าของร้าน
3. ส่วน H "อ่านโค้ดอย่างเดียวยังพิสูจน์ไม่ได้": สิ่งที่ต้องรันระบบหรือดูของที่ build แล้วถึงจะรู้ เช่น หน้าไหนเรียก API จริงตอนใช้งาน · ของที่รันอยู่ตรงกับโค้ดนี้ไหม
4. ส่วน I "งานนี้คือ reverse engineering แบบไหน" (Chikofsky & Cross 1990): ตาราง ส่วน A–H | ชนิดงาน (redocumentation = เขียนสิ่งที่โค้ดทำใหม่ในระดับเดียวกัน · design recovery = ประกอบเป็นความเข้าใจระดับสูงขึ้น เช่นกฎธุรกิจ) | ได้จากตาไหน (white-box = อ่านโค้ด · black-box = ดูระบบจากภายนอก · grey-box = ผสม) | เหตุผล 1 บรรทัด
   ปิดท้าย 2 บรรทัด: ทำไมงานในไฟล์นี้ยังไม่ใช่ re-engineering · ส่วนไหนควรยืนยันด้วยตาที่สองก่อนเชื่อ
5. เขียน CLAUDE.md ไม่เกิน 60 บรรทัด: วิธีรันใน PowerShell (เว็บพอร์ต 4000 · reset ข้อมูล · รันเทสต์ chromium: npx playwright test · 3 เบราว์เซอร์: npm run test:all · เรียก REA: powershell -NoProfile -ExecutionPolicy Bypass -File .\rea\rea.ps1 · สคริปต์ชั่วคราวไว้ใน rea\scratch\)
   · บอกว่ามีแผนที่ระบบใน CODEBASE-MAP.md (เขียนเป็นชื่อไฟล์ธรรมดา ห้ามใช้ @ เพื่อไม่ให้ถูกโหลดเข้าทุกเซสชัน) · ห้ามแตะ (ไฟล์เดิมใน e2e-legacy/ · TEST-DATA.md) ทั้งด้วยเครื่องมือแก้ไฟล์และด้วยคำสั่ง shell
   · กติกาการแก้ (อธิบายก่อนแก้ · ทำตาราง impact ก่อนแก้ · แก้ให้เล็กที่สุด · ห้ามแก้เทสต์เดิมให้ผ่าน · เทสต์ใหม่อยู่ใน e2e-legacy/tests/new/) · เอกสารเก่าอาจไม่ตรงโค้ด
   · ห้ามเปิด README.md ที่รากโฟลเดอร์บท fast_track/ และ _solution/ (มีเฉลยของบทเรียน · petshop/README.md อ่านได้)
6. เขียน .claude/settings.json ให้ห้าม Edit: e2e-legacy/playwright.config.ts · e2e-legacy/global-setup.ts · e2e-legacy/package.json · ไฟล์ .ts ชั้นบนสุดของ e2e-legacy/tests/ · TEST-DATA.md
   และห้าม Read 3 rule: Read(/README.md) · Read(./fast_track/**) · Read(./_solution/**) (README ต้องขึ้นต้น / ตัวเดียว = เฉพาะไฟล์ที่รากโฟลเดอร์บท · ถ้าเขียน ./README.md หรือ README.md จะกัน petshop/README.md ไปด้วย)
   เขียน path แบบ relative กับโฟลเดอร์บท เช่น Edit(e2e-legacy/tests/*.ts) · ห้ามใช้ ** หรือ // ที่จะกินโฟลเดอร์ย่อย tests/new/ ไปด้วย
   แต่ยังสร้างไฟล์ใหม่ใน e2e-legacy/tests/new/ ได้ · แสดงไฟล์ให้ผมดูก่อนบันทึก
ไม่แน่ใจเรื่องไหนให้เขียนไว้ในหัวข้อ "ยังไม่รู้" อย่าเดา · ถ้าเจอโค้ดที่น่าจะเป็นบั๊ก ให้จดในหัวข้อ "ยังไม่รู้" เป็นสมมติฐาน (ไฟล์:บรรทัด + อาการที่คาด) ยังไม่ใช่ข้อสรุป เพราะยังไม่ได้รันระบบ
สรุปเป็นตาราง: ส่วน | จำนวนแถว | แถวที่ "เดา" | ⚠️ / ❌
```

🎯 **ผลที่คาดหวัง** (ข้อเท็จจริงจาก `CODEBASE-NOTES.md`)
- A: Next.js 16.4 App Router · ข้อมูล server อยู่ใน RAM (`globalThis.__pawpantryStore`) · ตะกร้า/โปรด/ล่าสุด/คูปองอยู่ใน localStorage `pp-*`
- B ≈ 11 หน้า + not-found · C = **12 API route** · D ควรเห็น "กฎค่าส่งอยู่ `lib/pricing.ts` และถูกเขียนซ้ำในข้อความบนจอหลายจุด" และ "หน้า `/orders/[id]` เขียนสรุปเงินเอง" · ถ้าเห็นบล็อกคำนวณค่าส่งซ้ำใน `lib/orders.ts` (คอมเมนต์ PP-231) ก็ถูก (เป็นการค้นพบแบบ white-box ไม่ต้องห้าม)
- G เจอ 2 เรื่องเก่าใน HANDOVER-NOTES (SUMMER20 · หน้าเว็บดึงผ่าน `/api/products`) เป็น ⚠️/❌ พร้อมคำถามถึงร้าน
- I: A B C E F = redocumentation · D G = design recovery · ทุกส่วน = white-box (อ่านโค้ด) · H = รายการที่ต้องใช้ black/grey-box → ยังไม่ใช่ re-engineering เพราะยังไม่เปลี่ยนระบบ
- CLAUDE.md อ้าง `CODEBASE-MAP.md` แบบชื่อไฟล์ ไม่ใช่ `@CODEBASE-MAP.md`
- `.claude/settings.json` มี `permissions.deny` แบบ `Edit(...)` (ไม่ใช่ `Write(...)` ซึ่งใช้ไม่ได้กับ file rule · `METHODS` M1) + `Read(/README.md)` `Read(./fast_track/**)` `Read(./_solution/**)` (FIX5 · ยังไม่ผ่านรอบ RUN)

🧑 **คำตอบของผู้เรียน (ข้อ 6):** "บันทึกได้"

👀 "`permissions.deny Edit(...)` กันแค่เครื่องมือแก้ไฟล์ ไม่กันคำสั่ง shell (`Set-Content`, `>`) → จึงต้องเขียนกติกาใน CLAUDE.md ด้วย และเราต้องตรวจ diff เอง"
👀 (ตัดสินใจหลัง RUN05) agent อาจเห็นบล็อกค่าส่งซ้ำใน `lib/orders.ts` (PP-231) ตั้งแต่ LAB นี้ = การค้นพบแบบ white-box · **คงไว้** แต่สอนว่า "พบโค้ดน่าสงสัย ≠ หลักฐาน — จดเป็นสมมติฐานในส่วน ยังไม่รู้" (พรอมต์บรรทัดท้ายบอกแล้ว) · LAB 5 ต้องพิสูจน์แบบ black-box ก่อนเชื่อ
👀 reads: agent มักอ่านไฟล์ด้วย Git Bash/Grep แม้พรอมต์บอก PowerShell = ปกติ · กติกา PowerShell มีไว้สำหรับคำสั่งในพรอมต์

✔️ **ไปต่อได้เมื่อ:** มี `CODEBASE-MAP.md` ส่วน A–I · `CLAUDE.md` ≤ 60 บรรทัด · `.claude/settings.json` ตรวจรั้ว **2 ข้อความแยกกันในเซสชันใหม่** (agent ที่ถูกปฏิเสธข้อแรกมักหยุดทั้งชุด): ① "แก้ไฟล์ e2e-legacy/tests/01-home.spec.ts เพิ่มบรรทัดว่างท้ายไฟล์" → ต้องถูกปฏิเสธ (ข้อความพูดว่า "directory … denied" แม้ rule เป็นไฟล์ = ปกติ) ② (ข้อความใหม่) "สร้างไฟล์ e2e-legacy/tests/new/_probe.spec.ts ว่าง ๆ แล้วลบทิ้ง" → ต้องสร้างได้ (RUN05: ① ถูกปฏิเสธ ② สร้างได้)

---

## LAB 2 · REA ส่องของที่ build แล้ว → SYSTEM-MAP (🔍)

```text
ส่องของที่ build แล้วของ PawPantry ด้วย REA (มุมคนนอกที่เห็นแค่ของส่งมอบ) แล้วเทียบกับโค้ด เขียนผลลง SYSTEM-MAP.md
(ห้ามแก้ petshop/ · ห้ามเปิด _solution/ fast_track/ และ README.md ของโฟลเดอร์บท (มีเฉลย) · ไฟล์ .json ใน out/ ใหญ่มาก ห้ามเปิดอ่านตรง ๆ ให้ย่อด้วย node rea\rea-summarize.mjs เท่านั้น
 รันคำสั่ง shell ทุกตัวด้วย PowerShell จากโฟลเดอร์บท · ถ้ามีแต่ bash ให้เขียนคำสั่งลงไฟล์ rea\scratch\run.ps1 แล้วรัน powershell -NoProfile -ExecutionPolicy Bypass -File rea\scratch\run.ps1 · ห้ามแปลงคำสั่งเป็น bash เอง
 คำสั่งที่เขียนว่า "นาน" ให้ตั้ง timeout อย่างน้อย 10 นาที หรือรันเบื้องหลังแล้วรอจนจบ ห้ามสั่งซ้ำระหว่างรอ)
เรียก REA ด้วย powershell -NoProfile -ExecutionPolicy Bypass -File .\rea\rea.ps1 <อาร์กิวเมนต์> (ด้านล่างเขียนย่อว่า REA <อาร์กิวเมนต์>) · path ที่ส่งให้ REA ต้องขึ้นต้น /work/ · อ่านวิธีใช้ใน rea/README.md ก่อน
1. สำเนาโค้ดตอนนี้ไปที่ out\v1: robocopy petshop out\v1 /E /XD node_modules .next /NFL /NDL /NJH /NJS (exit code 0–7 = สำเร็จ · เครื่องมืออาจแสดง exit 1 เป็น error ไม่ต้องรันซ้ำ) แล้ว build ใน container (นาน ~3 นาที):
   docker run --rm -v "${PWD}\out\v1:/app" -w /app -e NEXT_TELEMETRY_DISABLED=1 node:24-alpine sh -c "npm ci --no-audit --no-fund && npm run build"
   จดเวลา · out\v1 คือ "ของเดิม" ไว้เทียบทีหลัง ห้ามแก้จนจบบท
2. วิเคราะห์ 2 ส่วนของ build (ตัวละ ~30–40 วินาที):
   REA -Out out\v1-static.json analyze-javascript-application /work/out/v1/.next/static --json
   REA -Out out\v1-server.json analyze-javascript-application /work/out/v1/.next/server --json
   ย่อทั้งสองด้วย node rea\rea-summarize.mjs <ไฟล์> --md แล้วจด: จำนวนไฟล์ · node แต่ละชนิด · edge · coverage · endpoint (พร้อม method และคอลัมน์ "ที่มา") · storage · evidence_id_short · subject_digest_short · (server) จำนวน recovered_source_files · node electron-renderer มาจากไฟล์ไหน
   (คอลัมน์ method = ตัวย่ออ่านจาก bundle ตรงตำแหน่งที่ REA ชี้ ไม่ใช่ผลของ REA เอง · แถวที่มา "file node" = REA เก็บ fact ไว้ที่ node ของไฟล์เพราะชนเพดานผลลัพธ์ ตัวย่อนับรวมให้แล้ว)
3. ตามรอยฟีเจอร์คูปอง: node rea\rea-input.mjs trace out\v1-server.json string coupons/validate incoming out\trace-coupon.in.json
   แล้ว REA -Out out\trace-coupon.json trace-application-feature /work/out/trace-coupon.in.json --json และย่อด้วย node rea\rea-summarize.mjs out\trace-coupon.json: เจอไฟล์ต้นทางอะไรบ้าง
4. SYSTEM-MAP.md ส่วน A "REA เห็นอะไร": สิ่งที่เจอ | ชนิด | มาจาก static หรือ server bundle | ป้าย 🔵 static · 🟢 runtime · 🟡 inference · ⚪ unknown | evidence_id
5. ส่วน B triangulation: ทุกหน้า API และ storage ใน CODEBASE-MAP.md ส่วน B C E → รายการ | REA เห็น | โค้ดบอก (ไฟล์:บรรทัด) | ตรงไหม ✅ / ⚠️ / ❓ไม่เจอ | ยืนยันด้วยตา (white = อ่านโค้ด · grey = REA หรือการค้นข้อความ (grep) ในของที่ build · black = เปิดเว็บ/HAR/HEALTHCHECK ดูจากข้างนอก)
   ✅ = อยู่ในรายการ endpoint/storage ของ REA (static หรือ server) และตรงกับโค้ด · ⚠️ = REA เห็นแต่ไม่ครบหรือต่างจากโค้ด (เช่นไม่มีชื่อ key · ชื่อถูกย่อ) · ❓ = ไม่อยู่ในรายการ endpoint/storage ของ REA (ถ้ากู้ได้แค่ชื่อไฟล์ route.ts จาก source map ให้นับ ❓ แล้วเขียนกำกับ "เห็นชื่อไฟล์")
   ข้อที่ REA ไม่เจอ ให้บอกเหตุผลที่เป็นไปได้ และห้ามสรุปว่า "ไม่มี"
6. ส่วน C ตอบ 5 ข้อ: (1) ผลไหนเป็นแค่ inference หรือชื่อที่ถูกย่อ (minify) (2) ถ้ามีแต่ build ไม่มี source เราจะรู้อะไรได้และไม่ได้
   (3) งานแบบไหนควรใช้ REA งานแบบไหนอ่าน source ก็พอ (skill ของ REA เขียนว่า "Skip REA for ordinary source-repository architecture analysis." อธิบายว่าหมายถึงอะไรกับงานนี้) (4) subject digest มีไว้ทำอะไรกับงานทดสอบ
   (5) นับแถวในส่วน B: ยืนยันด้วย 2 ตา กี่แถว · ตาเดียวกี่แถว (ตาไหน) · แถวตาเดียวต้องใช้หลักฐานอะไรมาเป็นตาที่สอง
ทุกตัวเลขต้องมาจากผลที่รันจริง · ไม่แน่ใจให้เขียนใน "ยังไม่รู้" อย่าเดา
สรุปเป็นตาราง: ส่วน | จำนวนแถว | ✅ | ⚠️ | ❓
```

🎯 **ผลที่คาดหวัง** (`REA-FEASIBILITY` §2.2–2.3 · ตัวเลขจะต่างเล็กน้อยเพราะโค้ดไม่มี BUG_MODE แล้ว)
- build ~3 นาที (npm ci ~2 นาที) · analyze static ~38 s · server ~25 s · ไฟล์ละ ~54 MB
- static: ไฟล์ 21 · endpoint ~9 (`/api/products` `/api/orders` `/api/auth/login|logout|register` `/api/coupons/validate` + `a` `b` `c`) · storage 3 แบบ `local-storage` `name: null` · coverage `partial`
- server: กู้ path ต้นทางได้ ~53 ไฟล์จาก source map (API route ครบ 12) · มี node `electron-renderer` 2 ตัว (ตัวย่อบอกไฟล์: `pages/500.html` · `app/_global-error.html` = หน้า HTML ที่มี `<script src>` · ต้องอธิบายว่าไม่ใช่ Electron) · endpoint ส่วนใหญ่เป็น noise ชื่อ header/query
- endpoint `/api/*` ของ server ทั้ง 6 ตัวมาจากแถวที่มา **file node** (REA ชนเพดานผลลัพธ์ของ chunk แล้วเก็บ fact ไว้ที่ node ของไฟล์ · ตัวย่อนับรวมให้) · ตรวจตัวย่อกับผลจริง RUN05: method ที่ตัวย่ออ่านจาก bundle = POST ทุกตัว ยกเว้น `/api/products` = GET (ทั้ง static และ server)
- trace (server, incoming): ~16 node รวม `app/api/coupons/validate/route.ts` และ `components_CartView_tsx` → ✅ ตรงกับโค้ด
- B: ❓ ไม่เจอใน static: `/api/auth/me` `/api/orders/[id]` `/api/products/[slug]` `/api/recommendations` `/api/health` `/api/test/reset` · storage key ⚪ unknown
- C(3): อ้าง skill ของ REA "Skip REA for ordinary source-repository architecture analysis" (ผ่าน README หัวข้อ 🎓 ข้อ 4 · `rea/README.md` ไม่มีเรื่องนี้)
- progress ของ REA (~490 บรรทัด `rea_progress` ใน stderr ต่อการ analyze 2 ครั้ง) **ไม่ขึ้นแล้ว** เพราะ `rea.ps1` ทิ้งให้เอง (หลัง RUN05 · ดู `PROMPT-FIX-LOG.md`)
- C(5): API ที่ static เห็น (`/api/products` `/api/orders` `/api/auth/*` `/api/coupons/validate`) = 2 ตา · ที่เหลือ white-box ตาเดียว → ตาที่สองมาจาก runtime (HAR/scenario ในขั้นถัดไป)

✔️ **ไปต่อได้เมื่อ:** มี `out\v1\.next\` · `SYSTEM-MAP.md` ส่วน A B C · ทุกแถวมีป้าย 🔵🟢🟡⚪ · ไม่มีแถวไหนสรุปว่า "ไม่มี" จาก static

---

## LAB 3 · ดูตอนรันจริง: HAR + REA ขับเบราว์เซอร์ → API-INVENTORY (🔍)

```text
บันทึกการใช้งานจริงของเว็บ (มุม runtime) แล้วทำ API-INVENTORY.md
(ห้ามแก้ petshop/ · ห้ามเปิด _solution/ fast_track/ และ README.md ของโฟลเดอร์บท (มีเฉลย) · ไฟล์ .har และ .json ใหญ่ใน out/ ห้ามเปิดอ่านตรง ๆ ให้ย่อด้วย node rea\rea-summarize.mjs
 รันคำสั่ง shell ทุกตัวด้วย PowerShell จากโฟลเดอร์บท · ถ้ามีแต่ bash ให้เขียนคำสั่งลงไฟล์ rea\scratch\run.ps1 แล้วรัน powershell -NoProfile -ExecutionPolicy Bypass -File rea\scratch\run.ps1 · ห้ามแปลงคำสั่งเป็น bash เอง)
เรียก REA ด้วย powershell -NoProfile -ExecutionPolicy Bypass -File .\rea\rea.ps1 <อาร์กิวเมนต์> (ด้านล่างเขียนย่อว่า REA <อาร์กิวเมนต์>)
1. เช็ก http://localhost:4000/api/health แล้วบันทึก HAR: node rea\record-har.mjs (ผลไปที่ out\)
   (สคริปต์ reset ข้อมูลแล้วเดิน หน้าแรก → ค้นหา → สินค้า → ตะกร้า → คูปอง → login → สั่งซื้อ) · จดเวลาแต่ละขั้นจาก out\har-steps.json
2. ให้ REA อ่าน HAR โดยปิดค่าลับ (รหัสและอีเมลของบัญชี demo จาก TEST-DATA.md · ถ้าคัดคำสั่งนี้ลงเอกสารใด ๆ ให้เขียน <รหัส demo> และ <อีเมล demo> แทนค่าจริง):
   REA -Out out\har.json inspect-web-network-capture /work/out/pawpantry-main.har har --sensitive-value Paw12345 --sensitive-value demo@pawpantry.test --json
   แล้ว node rea\rea-summarize.mjs out\har.json --md --samples (key 2 ชั้น + body ตัวอย่างแบบย่อ · อีเมลถูกแทนด้วย <อีเมล>) · ตรวจด้วย Select-String ว่า out\har.json ไม่มีคำว่า Paw12345 แต่ไฟล์ .har ต้นฉบับยังมี
3. ให้ REA ขับเบราว์เซอร์เองตาม rea\scenario-coupon.json (ค้นหา → ใส่ตะกร้า → ใช้ PAW10) ใน docker network ของเว็บ (pawpantry05_default · ใน network นี้เว็บชื่อ http://petshop:3000):
   REA -Network pawpantry05_default -Out out\scenario.json capture-browser-scenario /work/rea/scenario-coupon.json --json
   ย่อด้วย node rea\rea-summarize.mjs out\scenario.json --md --samples --png out\scenario-final.png: step ผ่านกี่ step · ชื่อ key ใน localStorage · ข้อความใน accessibility tree เรื่องคูปองและยอดเงิน (ป้ายกับตัวเลขอยู่บรรทัดเดียวกัน เช่น "ยอดชำระทั้งหมด = ฿…")
4. เขียน API-INVENTORY.md
   - ส่วน A API ที่เห็นตอนรันจริง: method | path | status | request keys | response keys | ค่าตัวอย่าง (จาก --samples · ห้ามใส่รหัสผ่าน อีเมล cookie) | หน้าที่เรียก
   - ส่วน B เติมช่องว่างจาก SYSTEM-MAP.md: แถวที่เป็น ⚪ หรือ ❓ ตอนนี้ runtime ยืนยันได้ไหม (เช่นชื่อ key ใน localStorage) เปลี่ยนป้ายเป็น 🟢 พร้อมไฟล์หลักฐาน
   - ส่วน C API ที่มีในโค้ด (CODEBASE-MAP.md ส่วน C) แต่ไม่เห็นในการรันรอบนี้: ทำไม และจะเก็บหลักฐานเพิ่มอย่างไร
   - ส่วน D 3 วิธีที่ใช้วันนี้ (analyze build · HAR · scenario): ใครคุมเบราว์เซอร์ | มีผลกับข้อมูลในระบบไหม | หลักฐานบอกอะไร | บอกอะไรไม่ได้
5. เช็กว่า .gitignore ของโฟลเดอร์บทกัน out/ และ *.har แล้ว และเขียนใน API-INVENTORY.md หัวข้อ "ขอบเขตที่ได้รับอนุญาต" 3 บรรทัด: ระบบที่ส่อง (URL · container) · ใครอนุญาต (ร้านที่เรารับช่วงระบบมา · รันบนเครื่องเราเอง) · ข้อมูลลับที่เจอ (รหัส · cookie · อีเมล) จัดการอย่างไร และทำไมไฟล์ HAR ห้ามส่งต่อ
ทุกค่าต้องมาจากไฟล์ผลที่รันจริง · ไม่แน่ใจให้เขียนใน "ยังไม่รู้" อย่าเดา · สรุปเป็นตาราง: ส่วน | จำนวนแถว | ยืนยันด้วย runtime ได้ | ยังไม่รู้
```

🎯 **ผลที่คาดหวัง** (`REA-FEASIBILITY` §2.4–2.5)
- HAR 8 ขั้น ~3 s · ไฟล์ ~1.6 MB · inspect ~2 s · **~97 records** · API 4 ตัว: POST `/api/coupons/validate` 200 · POST `/api/auth/login` 200 · POST `/api/orders` 201 · GET `/api/products` 200
- ค่าจริงใน HAR: คูปองลด ฿20 (subtotal ฿207) · order `total 237 = 207 − 20 + 50` (คาด · ยอดเดิมไม่แตะเกณฑ์ ฿999)
- `Paw12345` ไม่อยู่ใน `out\har.json` แต่อยู่ใน `.har` · redaction cookie อัตโนมัติ ~36 จุด
- `--samples` (ตรวจกับ `out\har.json` ของ RUN05): coupon validate `{"code":"PAW10","items":[{"slug":"lickable-salmon-treat","size":"4 ซอง","qty":3}]}` → `discount 20` · order response `subtotal 207 · discount 20 · shipping 50 · total 237` · login = `(redacted)` · response keys 2 ชั้น เช่น `order{id,…,total,…}` `items[]{slug,…}`
- scenario 11 step completed ~3 s · storage key `pp-recent` `pp-cart` `pp-coupon` · a11y (ตัวย่อรวมคู่ term/definition แล้ว): `ใช้คูปอง PAW10 แล้ว` · `ส่วนลด PAW10 = -฿6` · `ยอดชำระทั้งหมด = ฿113` · `completeness: incomplete` (RSC prefetch ถูก abort = ปกติของ Next)
- URL ใน steps/a11y/screenshot ของ scenario = `http://petshop:3000/...` (ไม่ใช่ localhost:4000)
- ⚠️ ถ้า network `pawpantry05_default` ไม่มี → compose ไม่มี `name: pawpantry05` (LESSON-PLAN §7 #3) ให้ RUNNER ดู `docker network ls` แล้วจดเป็นข้อเสนอแก้ระดับ H

👀 "URL ในผลของ REA เป็น `petshop:3000` เพราะ REA อยู่ใน docker network เดียวกับเว็บ ส่วนเราเปิด `localhost:4000` = เว็บตัวเดียวกัน คนละประตู" · "scenario สร้างผลข้างเคียงได้ (driven) ส่วน HAR อ่านอย่างเดียว (ไม่ยิงซ้ำ)"

✔️ **ไปต่อได้เมื่อ:** `API-INVENTORY.md` ส่วน A–D · ไม่มีรหัสผ่านในไฟล์ .md ใด ๆ · มี `out\scenario-final.png`

---

## LAB 4 · ล็อกพฤติกรรมเดิมก่อนแตะโค้ด (✏️)

```text
ก่อนแก้อะไรในระบบ ล็อกพฤติกรรมเดิมไว้ก่อน (characterization / golden master) แล้วเขียน BASELINE.md
(ห้ามแก้ petshop/ · ห้ามแก้ไฟล์เดิมใน e2e-legacy/ เพิ่มไฟล์ได้เฉพาะใน e2e-legacy/tests/new/ · ห้ามเปิด _solution/ fast_track/ และ README.md ของโฟลเดอร์บท (มีเฉลย)
 รันคำสั่ง shell ทุกตัวด้วย PowerShell · ถ้ามีแต่ bash ให้เขียนคำสั่งลงไฟล์ rea\scratch\run.ps1 แล้วรัน powershell -NoProfile -ExecutionPolicy Bypass -File rea\scratch\run.ps1
 คำสั่งที่เขียนว่า "นาน" ให้ตั้ง timeout อย่างน้อย 10 นาที หรือรันเบื้องหลังแล้วรอจนจบ ห้ามสั่งซ้ำระหว่างรอ)
1. รันชุดเทสต์เดิมในโฟลเดอร์ e2e-legacy: npx playwright test (chromium) แล้ว npm run test:all (3 เบราว์เซอร์ · นาน ~2–5 นาที)
   จดผ่าน / ล้ม / เวลา แยกเบราว์เซอร์ · ถ้ามีข้อล้มให้หยุดบอกผมก่อน
2. อ่าน e2e-legacy/tests ทั้งหมด แล้วทำตาราง "ชุดเดิมตรวจกฎเงินแค่ไหน": กฎใน TEST-DATA.md | TC เดิมที่ตรวจ | ตรวจที่ไหน (ตะกร้า · checkout · คำสั่งซื้อที่ server บันทึก) | ช่องว่าง
3. เขียน characterization test ใน e2e-legacy/tests/new/char-money.spec.ts (เพิ่มไฟล์ใน new/ ได้) สำหรับส่วนที่ชุดเดิมยังไม่ครอบ
   - เลือกตะกร้าที่ค่าขอบของกฎค่าส่งและคูปองใน TEST-DATA.md (ราคาสินค้าดูจากเว็บ หรืออ่าน API ด้วย node fetch · ไม่ใช้ Invoke-RestMethod เพราะชื่อภาษาไทยเพี้ยน) · ถ้าไม่มีตะกร้าที่ได้ค่าขอบพอดี ใช้ค่าใกล้ที่สุดสองฝั่งได้
   - ตะกร้าเดียวกันตรวจเงิน 4 จุด: หน้าตะกร้า · ปุ่มยืนยันสั่งซื้อ (data-testid place-order) · response ของ POST /api/orders · หน้าคำสั่งซื้อ /orders/PP-… หลังกดสั่ง
   - สต็อกเป็นของร่วม: npm run test:all reset ครั้งเดียวแล้วรัน 3 เบราว์เซอร์ขนานกัน → จำนวนชิ้นที่เทสต์ใหม่ซื้อจริงรวมกัน × 3 เบราว์เซอร์ ต้องไม่เกินสต็อกหลัง reset (ดู stock จาก GET /api/products) · เลือกสินค้าสต็อกมาก และอย่าใช้สินค้าที่เทสต์เดิมพึ่งสต็อก
   - API golden: GET /api/products และ POST /api/coupons/validate ตาม API-INVENTORY.md เก็บ response จริงเป็นไฟล์ e2e-legacy/tests/new/golden/*.json (ตัดฟิลด์ที่เปลี่ยนเองเช่นสต็อก) แล้วเทียบด้วย toEqual · ไม่ใช้ toMatchSnapshot
   - ห้ามเรียก /api/test/reset ในเทสต์ (ชุดเดิมรันขนานกัน) · สร้างผู้ใช้ใหม่อีเมลสุ่มแบบชุดเดิม (ใช้ helper ใน tests/fixtures.ts ได้ ห้ามแก้) · ห้ามล็อกเลขคำสั่งซื้อหรือจำนวนสต็อกตรง ๆ
4. ทุกค่าที่ล็อกให้มี annotation บอกที่มา: [E] = ได้จากการรันจริง (อ้างไฟล์ผล) และถ้า TEST-DATA.md บอกไว้ด้วยให้เขียน [D] คู่กัน
   ถ้าค่าที่เว็บทำ [E] ขัดกับ [D] ห้ามล็อกค่าของเว็บเป็นผลที่คาดหวัง ให้เขียนเทสต์คู่: ข้อหนึ่งล็อกค่าปัจจุบัน (annotation legacy-quirk) อีกข้อใช้ test.fail() กับค่าตาม [D] (annotation KNOWN-ISSUE) แล้วจดใน BASELINE.md หัวข้อ "ผู้ต้องสงสัย"
5. รันเฉพาะ tests/new บน chromium 2 รอบ (npx playwright test tests/new · เช็กว่าผลนิ่ง) แล้วรันทั้งชุด 3 เบราว์เซอร์ 1 รอบ (npm run test:all · นาน)
   (Playwright นับ test.fail() ที่ล้มตามคาดรวมใน "passed" ของบรรทัดสรุป → นับ expected-fail จากจำนวน test.fail() × เบราว์เซอร์ แล้วหักออกจากช่องผ่าน)
BASELINE.md: ผลชุดเดิม · ตารางช่องว่าง · ตารางเทสต์ใหม่ | ล็อกอะไร | ค่า | ที่มา [E]/[D] | ผล · ผู้ต้องสงสัย (ถ้ามี)
ห้ามแก้ผลที่คาดหวังให้ผ่าน · สรุปเป็นตาราง: ชุด | เบราว์เซอร์ | ผ่าน | ล้ม | expected-fail
```

🎯 **ผลที่คาดหวัง**
- ชุดเดิม: **40/40** ต่อเบราว์เซอร์ = 120/120 (บันทึกบท 02 ที่ `BUG_MODE=0`: 1.1 นาที 4 workers · `LEGACY-TESTSUITES` §1) · **ต้องยืนยัน** เพราะยังไม่เคยรันกับ build ที่มี BUG-01 · ถ้ามีข้อล้ม → ผู้เรียนตอบ "บันทึกไว้ แล้วทำต่อ" และ RUNNER รายงานผู้สร้างบท
- ตารางช่องว่างควรบอกว่า: TC-CART-03 ตรวจส่งฟรีที่ ฿2,680 (หน้าตะกร้า) · **TC-CHK-03** สั่งซื้อจริงที่ ฿378 (ใช้ FREESHIP · TC-CHK-01 = ยังไม่ login ถูกพาไปหน้า login) · **ไม่มีข้อไหนสั่งซื้อจริงที่ยอด ฿999 พอดี**
- 👀 ที่ดี: TC-CART-03 ชื่อ "ซื้อครบ ฿999 ได้ส่งฟรี" แต่ตรวจที่ ฿790 / ฿2,680 → **ชื่อ test ≠ สิ่งที่ test ตรวจ** ต้องอ่านตัว test ไม่ใช่แค่ชื่อ (ไม่เฉลย เพราะเป็นข้อมูลของชุดเทสต์เดิม)
- ถ้า agent เลือกตะกร้า ฿999 (ไม้ตกแมว ขนนก ฿129 + ชามกินช้า ฿290 ×3) จะเจอ: ตะกร้า/ปุ่ม ฿999 แต่ response/หน้าคำสั่งซื้อ ฿1,049 → ผู้ต้องสงสัย + test คู่ (`CR-DESIGN` §2.4) · ถ้าไม่เลือก = ช่องว่างยังอยู่ (บันทึกเป็น 👀 "golden master ล็อกแค่ที่เราเลือกดู")
- golden: `/api/products` 28 รายการ (ตัด stock) · coupon validate PAW10/FREESHIP/NEWCAT50/SUMMER20/โค้ดมั่ว
- RUN05 จริง: agent เลือกตะกร้า ฿999 จาก [D] เองแล้วเจอ **S1** (หน้าตะกร้า/ปุ่ม ฿999 แต่ server บันทึก ฿1,049) → test คู่ TC-CHAR-SHIP-02 `legacy-quirk` + SHIP-03 `test.fail` KNOWN-ISSUE · 3 เบราว์เซอร์ 141 passed (= เดิม 120 + ใหม่ 21 ซึ่งมี expected-fail 3 ที่ reporter นับเป็น passed) · เลี่ยงชามกินช้า ×3 ซ้ำ 3 test (27 > สต็อก 18)

👀 (ตัดสินใจหลัง RUN05) "ล็อกพฤติกรรมเดิม + เทียบ [D] แล้วเจอจุดขัดก่อนลูกค้าแจ้ง = ดีมาก แต่ทำเป็น `test.fail` KNOWN-ISSUE + จดผู้ต้องสงสัย **ไม่ใช่แก้ทันที**" · LAB 5 ต่อยอดจาก S1 (ลูกค้าแจ้งยืนยัน) · "สต็อกเป็นทรัพยากรร่วมของเทสต์ขนาน: ชิ้นต่อ test × 3 เบราว์เซอร์ ≤ สต็อกหลัง reset"

🧑 **คำตอบของผู้เรียน (ถ้าชุดเดิมมีข้อล้ม):** "จดไว้ใน BASELINE.md ว่าเป็นของเดิม แล้วทำต่อ"

✔️ **ไปต่อได้เมื่อ:** ชุดเดิมรันครบ 3 เบราว์เซอร์ · `tests/new/char-money.spec.ts` + `golden/` · ผล chromium 2 รอบเท่ากัน · ไม่มีค่าที่ขัด [D] ถูกล็อกเป็นผลที่คาดหวัง

---

## LAB 5 · BUG-01: ทำซ้ำ → test แดง → หาต้นเหตุ (✏️)

```text
มีลูกค้าแจ้งปัญหา (ข้อความอยู่ท้ายพรอมต์) ช่วยทำซ้ำให้เห็นกับตา เขียนเทสต์ที่ "แดง" ตามอาการ แล้วหาสาเหตุ เขียน BUG-01.md ที่โฟลเดอร์บท · ขั้นนี้ยังไม่ต้องแก้โค้ดเว็บ
(ห้ามแก้ petshop/ · ห้ามแก้ไฟล์เดิมใน e2e-legacy/ · ห้ามเปิด _solution/ fast_track/ และ README.md ของโฟลเดอร์บท (มีเฉลย)
 สคริปต์ชั่วคราวเก็บใน rea\scratch\ (ไฟล์ .mjs ที่ import จาก "playwright" ได้เพราะใช้ rea\node_modules) · รันคำสั่ง shell ด้วย PowerShell จากโฟลเดอร์บท · ถ้ามีแต่ bash ให้เขียนคำสั่งลงไฟล์ rea\scratch\run.ps1 แล้วรัน powershell -NoProfile -ExecutionPolicy Bypass -File rea\scratch\run.ps1)
ถ้า BASELINE.md หรือ CODEBASE-MAP.md มีผู้ต้องสงสัยเรื่องนี้อยู่แล้ว ให้ถือเป็นสมมติฐานที่ต้องพิสูจน์ ไม่ใช่คำตอบ · ขั้นนี้ต้องได้หลักฐานใหม่: ตะกร้าของลูกค้าตรงตัว · ยอดใน /account · HAR
ขั้นที่ 1 black-box (ยังไม่เปิดโค้ดใน petshop/ และยังไม่ใช้ CODEBASE-MAP.md ส่วน D): ทำตามที่ลูกค้าเล่าบน http://127.0.0.1:4000 (= localhost:4000 · ใช้ 127.0.0.1 เพราะ REA ไม่รับ HAR ที่อัดผ่าน localhost) ด้วย Playwright แบบ headless (สคริปต์ใน rea\scratch\)
   บันทึก HAR รอบนี้ไว้ที่ out\bug01.har ด้วย recordHar ของ browser context แบบเก็บเฉพาะ API: recordHar: { path: "out/bug01.har", urlFilter: /\/api\// } (ไม่กรองจะได้ไฟล์ ~40 MB)
   reset ข้อมูลก่อนเริ่มทุกรอบ (POST /api/test/reset) เพราะสินค้าบางตัวสต็อกน้อย (ชามกินช้า 18 ใบ) รันซ้ำหลายรอบจะเจอ 409 "สินค้าไม่พอ"
   - ดูเงิน 4 จุด: ตะกร้า · ปุ่มยืนยันสั่งซื้อ · response ของ POST /api/orders · หน้าคำสั่งซื้อ และยอดใน /account
   - ลองตะกร้าข้างเคียง: ยอดต่ำกว่า/สูงกว่า 1 บาท · ใช้คูปองใน TEST-DATA.md · ส่งด่วน แล้วทำตารางว่าผิดเฉพาะกรณีไหน
   - คำนวณผลที่ถูกเองจาก TEST-DATA.md [D] ก่อนเทียบกับเว็บ พร้อมวิธีคิด · กรณีที่ [D] ไม่พอจะคำนวณ (เช่นส่งฟรีนับก่อนหรือหลังหักส่วนลด) อย่าเดาตัวเลข ให้ใช้ oracle [R] "ยอดบนปุ่มยืนยัน = ยอดในคำสั่งซื้อ" และจดคำถามไว้ใน "ยังไม่รู้"
ขั้นที่ 2 เขียน e2e-legacy/tests/new/bug01-shipping.spec.ts ชื่อเทสต์ขึ้นต้น BUG-01 · ผลที่คาดหวังตาม [D] หรือ [R] เท่านั้น (ห้ามลอกจากเว็บ) · ต้องมีข้อที่ตรวจว่า "เงินบนปุ่มยืนยัน = เงินในคำสั่งซื้อ"
   รันบน chromium ต้อง "แดง" ด้วยเหตุผลที่ตรงอาการ · ถ้าเทสต์ใน tests/new/ ข้อไหนล็อกเรื่องนี้ไว้แล้ว (legacy-quirk / KNOWN-ISSUE) ให้บอก
ขั้นที่ 3 white-box: ตอนนี้เปิดโค้ดได้ หาต้นเหตุ (ไฟล์:บรรทัด) อธิบายว่าทำไมหน้าเว็บกับคำสั่งซื้อคิดไม่เท่ากัน
   คอมเมนต์ในโค้ดตรงนั้นพูดจริงไหม ให้ตรวจจาก HAR ว่า browser ส่งอะไรไปให้ server จริง
ขั้นที่ 4 impact: เสนอวิธีแก้อย่างน้อย 2 แบบ ตาราง วิธีแก้ | ไฟล์:บรรทัดที่แตะ | ใครเรียกใช้ | ผลต่อกฎอื่นและฟีเจอร์ในอนาคต | เทสต์ที่ต้องรันซ้ำ | ความเสี่ยง แล้วแนะนำ 1 แบบพร้อมเหตุผล
BUG-01.md: อาการ · ขั้นตอนทำซ้ำ · ตาราง กรณี | ผลที่คาดหวัง [D] | ผลจริง [E] (ไฟล์หลักฐาน) · ต้นเหตุ · ตาราง impact · ทำไมชุดเทสต์เดิมจับไม่ได้
ไม่แน่ใจให้เขียนใน "ยังไม่รู้" อย่าเดา · สรุปเป็นตาราง: กรณี | ตะกร้า | ปุ่ม | คำสั่งซื้อ | ถูกไหม

--- ข้อความจากลูกค้า ---
📩 เรื่อง: โดนเก็บเงินเกินจากที่หน้าเว็บบอก
สวัสดีค่ะ เมื่อวานสั่งของในร้าน ไม้ตกแมว 1 อัน กับชามกินช้า 3 ใบ ในตะกร้าขึ้นว่า "ได้ส่งฟรีแล้ว!" ตอนกดปุ่มก็เขียนว่า "ยืนยันสั่งซื้อ ฿999"
แต่พอสั่งเสร็จ หน้าคำสั่งซื้อกับในประวัติบัญชีกลับเป็น ฿1,049 ค่ะ เก็บเงินปลายทางด้วย กลัวไรเดอร์เก็บเกิน ฝากตรวจสอบให้หน่อยนะคะ
ก่อนหน้านี้สั่งยอดพันกว่าบาทไม่เคยเป็นแบบนี้
— คุณนุ่น (สั่งในระบบจริงของร้าน · เลขคำสั่งซื้อนั้นไม่มีในเครื่องทดสอบของเรา)
```

🎯 **ผลที่คาดหวัง** (`CR-DESIGN` §2.4–2.6 · รันจริงโดย A5)

| กรณี | ตะกร้า/ปุ่ม | คำสั่งซื้อ | ถูกไหม |
|---|---|---|---|
| ฿999 ส่งธรรมดา | ฿999 ส่งฟรี | **฿1,049** (shipping 50) | ❌ |
| ฿999 + PAW10 | ฿900 | **฿950** | ❌ |
| ฿998 ส่งธรรมดา | ฿1,048 | ฿1,048 | ✅ |
| ฿999 + FREESHIP | ฿999 | ฿999 | ✅ |
| ฿999 ส่งด่วน | ฿1,119 | ฿1,119 | ✅ |

- ต้นเหตุ: `lib/orders.ts` บล็อก `// PP-231 …` คำนวณค่าส่งซ้ำด้วย `>` แล้วเขียนทับ `totals.total` (กฎจริง `lib/pricing.ts` `shippingCost()` ใช้ `>=`) · HAR: body ของ POST `/api/orders` มีแค่ `shipping: "standard"` ไม่มีค่าส่ง → คอมเมนต์ "must not trust the shipping fee shown in the browser" ไม่จริง
- impact: วิธี A ลบบล็อกซ้ำ + import ที่ไม่ใช้ (กฎเงินที่เดียว) · วิธี B `>` → `>=` (ปิดอาการ แต่บล็อกที่เขียนทับ total ยังอยู่ → ฟีเจอร์ที่เพิ่มค่าใหม่ในยอดรวมจะหาย) · ควรแนะนำ A
- test BUG-01 แดงบน chromium (ปุ่ม ฿999 ≠ คำสั่งซื้อ ฿1,049) · ชุดเดิมจับไม่ได้เพราะไม่มี TC สั่งซื้อจริงที่ ฿999
- RUN05 จริง: 7 กรณี ผิด 2 (฿999 ส่งธรรมดา · ฿999+PAW10 ปุ่ม ฿900 → คำสั่งซื้อ ฿950) · spec 3 แดง / 6 เขียว · HAR ไม่กรอง 40 MB 2,447 entries (หลังแก้พรอมต์ใช้ `urlFilter` เหลือเฉพาะ API) · กรณี PAW10 ใช้ oracle [R] "ปุ่ม = คำสั่งซื้อ" เพราะ [D] ไม่บอกว่าส่งฟรีนับก่อน/หลังส่วนลด

👀 "ถ้า agent เคยเห็นโค้ดน่าสงสัยใน `CODEBASE-MAP.md` (white-box) หรือ S1 ใน `BASELINE.md` มาก่อน ก็ยังต้องทำซ้ำแบบ black-box ให้เห็นกับตา — ความเข้าใจจากโค้ด ≠ หลักฐานว่าระบบทำแบบนั้นจริง · คุณค่าของขั้นนี้คือหลักฐานใหม่ (ตะกร้าลูกค้าตรงตัว · /account · ค่าขอบ ฿998/฿1,000 · HAR) ไม่ใช่การค้นพบ" · "เลขคำสั่งซื้อในข้อความลูกค้าเป็นของระบบจริง ห้ามไปหาในเครื่องทดสอบ (หลัง reset เลขคำสั่งซื้อแรกในเครื่องเราเป็นของคำสั่งซื้อที่สคริปต์ HAR สร้าง ไม่ใช่ของลูกค้า)"

✔️ **ไปต่อได้เมื่อ:** `BUG-01.md` ครบ 6 หัวข้อ · test BUG-01 แดงด้วยเหตุผลเรื่องเงิน (ไม่ใช่ timeout/locator) · มี `out\bug01.har`

---

## LAB 6 · แก้ BUG-01 ที่ต้นเหตุ (✏️)

```text
แก้ BUG-01 ตามวิธีที่แนะนำใน BUG-01.md · ก่อนเริ่มให้ถามผมก่อนว่าจะใช้วิธีไหน
(ห้ามแก้ไฟล์เดิมใน e2e-legacy/ · ห้ามแก้ผลที่คาดหวังใน tests/new/bug01-shipping.spec.ts · ห้ามเปิด _solution/ fast_track/ และ README.md ของโฟลเดอร์บท (มีเฉลย)
 รันคำสั่ง shell ทุกตัวด้วย PowerShell จากโฟลเดอร์บท · ถ้ามีแต่ bash ให้เขียนคำสั่งลงไฟล์ rea\scratch\run.ps1 แล้วรัน powershell -NoProfile -ExecutionPolicy Bypass -File rea\scratch\run.ps1
 คำสั่งที่เขียนว่า "นาน" ให้ตั้ง timeout อย่างน้อย 10 นาที หรือรันเบื้องหลังแล้วรอจนจบ ห้ามสั่งซ้ำระหว่างรอ)
1. ก่อนแก้: แสดงไฟล์และบรรทัดที่จะแตะ เทียบกับตาราง impact ใน BUG-01.md · ถ้าแตะเกินตารางต้องบอกเหตุผล
2. แก้ให้เล็กที่สุด แล้ว build เว็บใหม่: ในโฟลเดอร์ petshop รัน docker compose up -d --build (นาน 1–3 นาที) รอจน healthy
3. รัน tests/new/bug01-shipping.spec.ts บน chromium ต้องผ่าน
   ถ้ามีเทสต์คู่ใน tests/new/ ที่ล็อกพฤติกรรมเดิมของเรื่องนี้ไว้ (legacy-quirk) หรือ KNOWN-ISSUE ที่ตอนนี้ขึ้น "Expected to fail, but passed"
   ข้อยกเว้นเดียวที่แก้เทสต์ได้: ปรับเทสต์คู่นั้นตามพฤติกรรมที่ตั้งใจเปลี่ยน (ทั้งค่าและ tag/annotation เช่น legacy-quirk → bug01-fixed · เอา test.fail() ออก) แล้วจดเหตุผลอ้าง BUG-01
4. รันชุดเดิม + tests/new ทั้งหมดบน chromium · ถ้ามีข้อล้มให้หยุดบอกผม
5. ยิง API ซ้ำทุกกรณีในตารางของ BUG-01.md แล้วจดผลใหม่ · ถ้าใช้สคริปต์เดิมที่เขียนผลทับไฟล์ใน out\ ให้คัดผลก่อนแก้ไปไว้ที่ out\bug01-before-fix\ ก่อนรัน (หลักฐาน "ก่อน" ต้องยังอยู่)
6. เพิ่มใน BUG-01.md หัวข้อ "แก้แล้ว": บรรทัดที่เปลี่ยน (ทีละไฟล์: git diff --no-index out\v1\<ไฟล์> petshop\<ไฟล์> · exit 1 = มีความต่าง ไม่ใช่ error · ห้าม diff ทั้งโฟลเดอร์เพราะ out\v1 มี node_modules และ .next) · ผลเทสต์ก่อน/หลัง · ตารางกรณีเดิมหลังแก้
ทุกค่าต้องมาจากที่รันจริง · สรุปเป็นตาราง: เทสต์หรือกรณี | ก่อนแก้ | หลังแก้
```

🧑 **คำตอบของผู้เรียน:** "ใช้วิธีที่ทำให้กฎเงินอยู่ที่เดียว (ลบการคำนวณค่าส่งซ้ำ) ไม่ใช่แค่เปลี่ยนเครื่องหมาย" · ถ้า BUG-01.md แนะนำแบบอื่นมา ให้ตอบแบบนี้และจดว่าผู้เรียนไม่เห็นด้วยเพราะอะไร

🎯 **ผลที่คาดหวัง**
- แตะ `lib/orders.ts` ไฟล์เดียว: −12/+1 บรรทัดโดยประมาณ (reverse diff ของ `CR-DESIGN` §2.2) · `next build` ผ่าน
- BUG-01 test เขียว · ชุดเดิม 40/40 chromium · กรณี ฿999 → 999 · ฿999+PAW10 → 900 · ที่เหลือเท่าเดิม
- `git diff --no-index` exit 1 = มีความต่าง (ปกติ ไม่ใช่ error)
- test คู่ใน `char-money` พลิก: SHIP-02 `legacy-quirk` → `@bug01-fixed` · SHIP-03 เอา `test.fail` ออก (RUN05) = ข้อยกเว้นที่พรอมต์อนุญาต

👀 "เปลี่ยนพฤติกรรมโดยตั้งใจ = อัปเดต oracle ของ test คู่พร้อมเหตุผล (ทั้งค่าและ tag) ไม่ใช่แก้ test ให้ผ่าน" · "หลักฐานก่อนแก้ต้องไม่ถูกเขียนทับ (`out\bug01-before-fix\`)"

✔️ **ไปต่อได้เมื่อ:** test BUG-01 เขียว · ชุดเดิมไม่มีข้อล้ม · `BUG-01.md` มีหัวข้อ "แก้แล้ว"

---

## LAB 7 · CR-01: ถามก่อน → impact → test แดงก่อน (✏️)

```text
ร้านขอฟีเจอร์ใหม่ CR-01 (ใบขออยู่ท้ายพรอมต์) ขั้นนี้ยังไม่แก้โค้ดเว็บ ให้เตรียม 3 อย่าง: คำถามถึงร้าน · impact · เทสต์ที่แดงก่อน แล้วเขียน CR-01.md
(ห้ามแก้ petshop/ · ห้ามแก้ไฟล์เดิมใน e2e-legacy/ · ห้ามเปิด _solution/ fast_track/ และ README.md ของโฟลเดอร์บท (มีเฉลย) · รันคำสั่ง shell ด้วย PowerShell
 ทุกค่าต้องมาจากราคาจริงในเว็บหรือ API (อ่าน API ด้วย node fetch ไม่ใช้ Invoke-RestMethod เพราะชื่อภาษาไทยเพี้ยน) · ตัวเลขเงินคำนวณเองพร้อมวิธีคิด ห้ามเดา)
1. ทำตาราง "ต้องถามร้าน": เรื่องที่ใบ CR ยังไม่ชัด | ตีความได้กี่แบบ | ยอดเงินต่างกันเท่าไร (ยกตะกร้าที่มีจริงในร้าน) · ถามผมก่อน แล้วจดคำตอบลง CR-01.md
2. impact analysis จาก CODEBASE-MAP.md + โค้ดจริง: ไฟล์ที่ต้องแตะ | ทำไม | ใครเรียกใช้ (ผลค้นหา) | หน้า/API ที่กระทบ | เทสต์เดิมที่ต้องรันซ้ำ | ความเสี่ยง
   เพิ่มรายการ "ไฟล์ที่ไม่ต้องแตะ แต่ตรวจแล้ว" · ระวังจุดที่คำนวณหรือแสดงเงินมากกว่า 1 ที่
   ตาที่สองจากของที่ build แล้ว: node reaea-input.mjs trace out1-server.json string api/orders incoming out	race-orders.in.json แล้ว powershell -NoProfile -ExecutionPolicy Bypass -File .eaea.ps1 -Out out	race-orders.json trace-application-feature /work/out/trace-orders.in.json --json (~10 วินาที · ห้ามเปิด .json ใน out/ ตรง ๆ ย่อด้วย node reaea-summarize.mjs out	race-orders.json)
   ไฟล์ต้นทาง (source_files) และ chunk ที่ trace เจอต้องอยู่ในตาราง impact หรือในรายการ "ตรวจแล้ว" · trace เห็นแค่ส่วนที่ build ต่อถึงกัน (coverage partial) ไฟล์ที่ trace ไม่เจอจึงไม่ได้แปลว่าไม่กระทบ
3. ออกแบบ TC-GIFT-xx จากใบ CR + คำตอบร้าน: ค่าขอบ ±1 บาท · ผสมคูปองและส่งด่วน · ติ๊กแล้วเอาออก · API ส่ง giftWrap ผิดชนิด (ตรวจทั้งยอด และ field giftWrap = false · giftWrapFee = 0 ใน response) · เงินตรง 4 จุด (checkout · ปุ่ม · response · หน้าคำสั่งซื้อและ /account)
   ตาราง ID | AC | ตะกร้า | ผลที่คาดหวังพร้อมวิธีคิด | ที่มา [D] · ราคาสินค้าดูจากเว็บหรือ API จริง ตะกร้าต้องหาได้จริงในร้าน
   สต็อกเป็นของร่วม: จำนวนชิ้นที่เทสต์ทั้งไฟล์ซื้อจริงรวมกัน (รวมกับเทสต์อื่นใน tests/new/ ที่ซื้อสินค้าตัวเดียวกัน) × 3 เบราว์เซอร์ ต้องไม่เกินสต็อกหลัง reset (ดู stock จาก GET /api/products) · ตะกร้าของ API test ที่ซื้อซ้ำหลายข้อให้ใช้สินค้าสต็อกมาก
4. เขียนเทสต์ทั้งหมดใน e2e-legacy/tests/new/cr01-giftwrap.spec.ts แล้วรันบน chromium
   ตั้ง timeout สั้นในไฟล์เทสต์เอง (test.use({ actionTimeout: 3_000 }) และ expect.configure({ timeout: 3_000 })) เพราะ config เดิมรอ expect 8 วินาที · ห้ามแก้ playwright.config.ts
   ทุกข้อควรแดงเพราะ "ยังไม่มีฟีเจอร์" ไม่ใช่เพราะเทสต์เขียนผิด · ข้อไหนเขียวตั้งแต่ตอนนี้ให้บอกว่าเป็น guard ที่ถูกต้อง หรือเทสต์อ่อนไป
CR-01.md: ใบ CR · คำถาม + คำตอบร้าน · impact · TC · ผลรอบแรก (แดงเพราะอะไร)
สรุปเป็นตาราง: TC | AC | ผลที่คาดหวัง | ผลรอบแรก | เหตุผล

--- ใบ Change Request ---
CR-01 · บริการห่อของขวัญ (จากเจ้าของร้าน)
ลูกค้าหลายคนซื้อเป็นของขวัญ อยากให้เลือก "ห่อของขวัญ" ได้ตอนชำระเงิน คิดค่าห่อ ฿30 ถ้าซื้อครบ ฿1,500 ห่อให้ฟรี
AC1 หน้า /checkout มี checkbox ห่อของขวัญ data-testid="gift-wrap" ค่าเริ่มต้นไม่ติ๊ก
AC2 ติ๊กแล้ว สรุปยอดมีแถว "ห่อของขวัญ" data-testid="summary-giftwrap" แสดง ฿30 หรือ ฟรี · summary-total และปุ่ม place-order รวมค่าห่อทันที · ไม่ติ๊ก = ไม่มีแถวนี้
AC3 ยอดชำระ = ยอดสินค้า − ส่วนลด + ค่าส่ง + ค่าห่อ · server คำนวณเองทุกครั้ง
AC4 POST /api/orders รับ giftWrap: true (boolean เท่านั้น ค่าอื่นถือว่าไม่ห่อ) · response และ GET /api/orders/[id] มี giftWrap (boolean) และ giftWrapFee (ตัวเลข)
AC5 หน้า /orders/[id] แสดงแถวห่อของขวัญตรงกับที่สั่ง · ยอดใน /account ตรงกับหน้าคำสั่งซื้อ
AC6 เทสต์เดิมที่ผ่านอยู่ต้องยังผ่าน
```

🧑 **คำตอบร้าน (ผู้เรียนเปิดจาก `<details>` ใน README · RUNNER ใช้ตอบ)**

| คำถามที่ควรถูกถาม | คำตอบ |
|---|---|
| ฿1,500 ดูยอดก่อนหรือหลังหักส่วนลด | **ก่อนหักส่วนลด** (แบบเดียวกับกฎส่งฟรี ฿999) |
| ค่าห่อนับเข้ายอดส่งฟรี ฿999 / ขั้นต่ำ NEWCAT50 ไหม | **ไม่นับ** |
| PAW10 ลดค่าห่อด้วยไหม · FREESHIP ยกเว้นค่าห่อไหม | **ไม่ลด · ไม่ยกเว้น** |
| ค่าห่อต่อคำสั่งซื้อหรือต่อชิ้น | **ต่อคำสั่งซื้อ** |
| (อื่น ๆ ที่ไม่มีในตารางนี้) | "ใช้แบบที่ง่ายที่สุดที่ไม่ขัดกับข้อบน แล้วติด ⚠️ สมมติฐาน" |

🎯 **ผลที่คาดหวัง** (`CR-DESIGN` §1.3–1.5 · ตัวเลขรันจริงบน prototype)
- trace (FIX5 ทดสอบแยกกับ `out1-server.json` ของ RUN05 · 9.5 s): `matched_seeds` 21 · node 26 · edge 86 · coverage partial · `source_files` = `app/api/orders/route.ts` `app/api/orders/%5Bid%5D/route.ts` + chunk `ssr/components_CheckoutForm_tsx_…` · ไม่เห็น `lib/*` → agent ต้องบอกว่า trace ยืนยันผู้เรียก แต่ impact หลักยังมาจากการค้นโค้ด
- impact ควรมี 6 ไฟล์: `lib/pricing.ts` `lib/orders.ts` `lib/store.ts` `components/OrderSummary.tsx` `components/CheckoutForm.tsx` `app/orders/[id]/page.tsx` (**หน้านี้เขียนสรุปเงินเอง ไม่ใช้ `SummaryRows`**) · ไม่ต้องแตะ `app/api/orders/route.ts` `app/account/page.tsx` (ตรวจแล้ว)
- ตะกร้าขอบ: ฿1,499 (ลูกแมว 400 g + น้ำพุแมว + สุนัขพันธุ์เล็ก) ห่อ → ฿1,529 · ฿1,500 (ชามกินช้า + สุนัขโต แกะ 3 kg + สุนัขพันธุ์เล็ก) ห่อ → ฿1,500 · +PAW10 → ฿1,350 · ลูกแมว 400 g ห่อ → ฿269 · +FREESHIP → ฿219 · ฿999 ห่อ → ฿1,029 · ลูกแมว 1.5 kg ด่วน ห่อ → ฿740 · `giftWrap: "true"` / `1` → ฿239
- รอบแรก: UI test แดงเพราะหา `gift-wrap` ไม่เจอ · API test แดงเพราะไม่มี field `giftWrap`/`giftWrapFee` · ข้อ "ส่งค่าผิดชนิด" แดงเพราะยังไม่มี field (ถ้าตรวจแค่ยอด ฿239 จะเขียวตั้งแต่ตอนนี้ = guard · พรอมต์ระบุให้ตรวจ field แล้วหลัง RUN05) · RUN05 รอบแรก 18 แดง / 3 เขียว
- ⚠️ RUN05: ตะกร้าหลักของ API test = ลูกแมวแซลมอน 16 ชิ้นต่อเบราว์เซอร์ (สต็อก 25) → LAB 8 `test:all` ล้ม 46 ข้อ (409 สินค้าไม่พอ) · พรอมต์เพิ่มกติกาสต็อก × 3 เบราว์เซอร์แล้ว

✔️ **ไปต่อได้เมื่อ:** `CR-01.md` มีคำถาม+คำตอบ ≥ 2 ข้อ · impact มีหน้า `/orders/[id]` · `cr01-giftwrap.spec.ts` แดงด้วยเหตุผล "ยังไม่มีฟีเจอร์"

---

## LAB 8 · ทำ CR-01 + regression 3 เบราว์เซอร์ (✏️)

```text
ทำ CR-01 ตาม CR-01.md ให้เทสต์ TC-GIFT ทุกข้อผ่าน โดยของเดิมไม่พัง
(ห้ามแก้ไฟล์เดิมใน e2e-legacy/ · ห้ามแก้ผลที่คาดหวังใน tests/new/cr01-giftwrap.spec.ts · ห้ามรัน -u · ห้ามเปิด _solution/ fast_track/ และ README.md ของโฟลเดอร์บท (มีเฉลย)
 รันคำสั่ง shell ทุกตัวด้วย PowerShell จากโฟลเดอร์บท · ถ้ามีแต่ bash ให้เขียนคำสั่งลงไฟล์ rea\scratch\run.ps1 แล้วรัน powershell -NoProfile -ExecutionPolicy Bypass -File rea\scratch\run.ps1
 คำสั่งที่เขียนว่า "นาน" ให้ตั้ง timeout อย่างน้อย 10 นาที หรือรันเบื้องหลังแล้วรอจนจบ ห้ามสั่งซ้ำระหว่างรอ · สคริปต์ชั่วคราวเก็บใน rea\scratch\)
1. แสดงแผนก่อน: ไฟล์ที่จะแตะเทียบกับตาราง impact ใน CR-01.md แล้วรอผมอนุมัติ
2. กฎเงินต้องอยู่ที่เดียวและใช้ร่วมกันทั้ง browser และ server · server คำนวณเงินเอง ไม่เชื่อตัวเลขจาก browser · data-testid ตามใบ CR
3. build ใหม่ (docker compose up -d --build ในโฟลเดอร์ petshop · นาน 1–3 นาที) รอจน healthy แล้วรัน cr01-giftwrap.spec.ts บน chromium จนผ่าน
   ถ้าล้ม ให้บอกก่อนว่าเป็น เว็บผิด / เทสต์เก่าล้าสมัย / เทสต์ใหม่เขียนผิด / ข้อมูลทดสอบหมด แล้วค่อยแก้ฝั่งนั้น (เทสต์เก่าห้ามแก้ · เทสต์ใหม่เขียนผิดแก้ได้เฉพาะวิธีหา element หรือจังหวะรอ ห้ามแตะผลที่คาดหวัง)
4. regression เต็ม: ในโฟลเดอร์ e2e-legacy รัน npm run test:all (3 เบราว์เซอร์ · นาน ~2–5 นาที) · มีข้อล้มให้หยุดบอกผม
   แต่ถ้าล้มด้วย 409 "สินค้าไม่พอ" หรือปุ่ม qty-plus กดไม่ได้ = ข้อมูลทดสอบ (สต็อก) หมด ไม่ใช่เว็บพัง (reset ครั้งเดียวแต่ 3 เบราว์เซอร์ใช้สต็อกร่วมกัน)
   → ยืนยันจากข้อความ error แล้วรันทีละเบราว์เซอร์ npx playwright test --project=chromium แล้ว --project=firefox แล้ว --project=webkit (reset ทุกรอบ) รวมผล และจดเหตุผลใน CR-01.md · ห้ามแก้ตะกร้าในเทสต์หรือ config เพื่อเลี่ยง
5. ตรวจอีกชั้นโดยไม่ผ่าน UI: ยิง POST /api/orders ตามตาราง TC (login ด้วยผู้ใช้ใหม่) แล้วเทียบยอดกับตาราง
6. ถ่ายภาพหน้า checkout ที่ติ๊กห่อของขวัญด้วย Playwright headless 1280x800 (สคริปต์ใน rea\scratch\) เก็บที่ out\shots\lab8-checkout-giftwrap.png
7. เพิ่มใน CR-01.md หัวข้อ "ทำแล้ว": ไฟล์ที่แก้ (+/− บรรทัด ทีละไฟล์ตามตาราง impact: git diff --no-index --stat out\v1\<ไฟล์> petshop\<ไฟล์> · exit 1 = มีความต่าง · ห้าม diff ทั้งโฟลเดอร์เพราะ out\v1 มี node_modules และ .next · lib/orders.ts เทียบ out\v1 จะรวมการแก้ BUG-01 ด้วย ให้แยกบอก) · ผลทุกชุด 3 เบราว์เซอร์ · ผลยิง API
สรุปเป็นตาราง: ชุด | chromium | firefox | webkit
```

🧑 **คำตอบของผู้เรียน (ข้อ 1):** อนุมัติถ้าแผนมี `app/orders/[id]/page.tsx` และกฎค่าห่ออยู่ใน `lib/pricing.ts` ที่เดียว · ถ้าขาดให้ตอบ "หน้า /orders/[id] แสดงเงินจากไหน ตรวจก่อน" แล้วจดว่าเกิดขึ้น

🎯 **ผลที่คาดหวัง**
- 6 ไฟล์ ~+60/−9 บรรทัด (prototype `CR-DESIGN` ภาคผนวก A) · `next build` ผ่าน
- TC-GIFT ทุกข้อเขียว · ชุดเดิม 40/40 × 3 = 120/120 · tests/new ทั้งหมดเขียว (prototype: suite บท 03 46/48 เท่าเดิม)
- ถ้าใน LAB 6 แก้แบบเปลี่ยนเครื่องหมายอย่างเดียว: คาดว่า UI ฿269 แต่คำสั่งซื้อ ฿239 → TC เงิน 4 จุดแดง (`CR-DESIGN` §2.6) = 👀 สำคัญ ให้ RUNNER จด
- เวลาประมาณ ~25 นาที (build ~3 นาที × 1–2 รอบ + regression 3 เบราว์เซอร์) · RUN05: build ใช้ cache 11 s
- RUN05 จริง (**H** ก่อนแก้พรอมต์): `test:all` รอบเดียว 185 passed / 46 failed ทั้งหมดเป็น 409 สินค้าไม่พอ (ลูกแมวแซลมอน 20 ชิ้นต่อเบราว์เซอร์ × 3 > สต็อก 25) · รันทีละเบราว์เซอร์ = 77/77 × 3 · `lib/orders.ts` diff รวม BUG-01 (+1/−7)

👀 "test ใหม่ที่เขียวบน chromium ทำให้ชุดเดิมแดงบนเบราว์เซอร์อื่นได้ ถ้ากินข้อมูลร่วม (สต็อก) → อ่านข้อความ error ก่อนตัดสินว่าเว็บพัง" · "test data isolation: test ที่เขียนข้อมูลต้องไม่แย่งทรัพยากรกัน (ชิ้นต่อ test × เบราว์เซอร์ ≤ สต็อก หรือ reset/ข้อมูลแยกต่อ test)"

✔️ **ไปต่อได้เมื่อ:** ตาราง 3 เบราว์เซอร์ไม่มีข้อล้ม (รันรวมหรือทีละเบราว์เซอร์ก็ได้ ถ้าข้อล้มรอบรวมเป็น 409 สต็อกหมดทั้งหมด) · มีภาพ checkout · `CR-01.md` หัวข้อ "ทำแล้ว"

---

## LAB 9 · พิสูจน์ว่าแก้แค่ที่ตั้งใจ + CHANGE-REPORT (🔍)

### ส่วนที่ 1

```text
พิสูจน์ว่าของที่จะส่งมอบเปลี่ยนเฉพาะที่ตั้งใจ (ตาม BUG-01.md และ CR-01.md) ด้วยหลักฐาน 2 ชั้น แล้วเขียน CHANGE-PROOF.md
(ห้ามแก้โค้ด · ไฟล์ .json ใหญ่ใน out/ ห้ามเปิดตรง ๆ ให้ย่อด้วย node rea\rea-summarize.mjs · ห้ามเปิด _solution/ fast_track/ และ README.md ของโฟลเดอร์บท (มีเฉลย)
 รันคำสั่ง shell ทุกตัวด้วย PowerShell จากโฟลเดอร์บท · ถ้ามีแต่ bash ให้เขียนคำสั่งลงไฟล์ rea\scratch\run.ps1 แล้วรัน powershell -NoProfile -ExecutionPolicy Bypass -File rea\scratch\run.ps1 · ห้ามแปลงคำสั่งเป็น bash เอง
 คำสั่งที่เขียนว่า "นาน" ให้ตั้ง timeout อย่างน้อย 10 นาที หรือรันเบื้องหลังแล้วรอจนจบ ห้ามสั่งซ้ำระหว่างรอ)
เรียก REA ด้วย powershell -NoProfile -ExecutionPolicy Bypass -File .\rea\rea.ps1 <อาร์กิวเมนต์> (ด้านล่างเขียนย่อว่า REA <อาร์กิวเมนต์>)
1. ชั้น source: คำนวณ SHA-256 ทุกไฟล์ใน out\v1 และ petshop (ไม่รวม node_modules และ .next · ใช้ Get-FileHash -LiteralPath เพราะ path อย่าง app\orders\[id]\page.tsx มี [ ] ถ้าไม่ใส่ -LiteralPath จะได้ค่าว่างแบบเงียบ ๆ) แล้วทำตาราง ไฟล์ | สถานะ (เหมือน / ต่าง / มีแค่ฝั่งเดียว)
   ตรวจตัวนับไฟล์ที่ต่างกับ git status --short petshop ให้ตรงกัน (ถ้าโฟลเดอร์บทไม่ใช่ git repo ให้ใช้ git diff --no-index --stat ทีละไฟล์ที่ hash ต่างเป็นแหล่งที่สองแทน แล้วจดว่าใช้ทางไหน) · ไฟล์ที่ต่างแต่ไม่ได้ตั้งใจแก้ ให้หาว่าเกิดจากอะไร
2. build เวอร์ชันใหม่: robocopy petshop out\v2 /E /XD node_modules .next /NFL /NDL /NJH /NJS (exit 0–7 = สำเร็จ) แล้ว build แบบเดียวกับ out\v1 (นาน ~3 นาที):
   docker run --rm -v "${PWD}\out\v2:/app" -w /app -e NEXT_TELEMETRY_DISABLED=1 node:24-alpine sh -c "npm ci --no-audit --no-fund && npm run build"
   แล้ว REA -Out out\v2-server.json analyze-javascript-application /work/out/v2/.next/server --json
3. ชั้น bundle (REA เทียบ source กับของที่ build 4 ทิศ):
   REA -Out out\v1-src.json import-reference-source /work/out/v1 --json  และ  REA -Out out\v2-src.json import-reference-source /work/out/v2 --json
   ทั้ง 4 คู่ ตั้งชื่อผล out\s2b-v1src-v1build.json · out\s2b-v1src-v2build.json · out\s2b-v2src-v1build.json · out\s2b-v2src-v2build.json
   ทีละคู่: node rea\rea-input.mjs s2b out\<src>.json out\<v1 หรือ v2>-server.json out\s2b.in.json แล้ว REA -Out out\s2b-<คู่>.json compare-source-to-bundle /work/out/s2b.in.json --json (คู่ละ ~10 วินาที)
   ย่อแต่ละคู่ด้วย node rea\rea-summarize.mjs out\s2b-<คู่>.json --md แล้วจดตัวนับครบ 7 คลาส (unchanged · modified · removed · split · merged · duplicated · unknown)
   ทำตาราง 4 ทิศ: node rea\rea-summarize.mjs --s2b-table out\s2b-v1src-v1build.json out\s2b-v1src-v2build.json out\s2b-v2src-v1build.json out\s2b-v2src-v2build.json (แสดงเฉพาะไฟล์ที่สถานะต่างกันระหว่างคู่ ไฟล์อื่นไม่ได้หาย)
   อ่านให้ถูก: unknown = REA หา digest ของไฟล์นั้นใน bundle ไม่เจอ ไม่ได้แปลว่าไฟล์หาย · REA มีคลาส modified แต่อย่าคาดว่าไฟล์ที่แก้จะขึ้นเป็น modified ให้ดูจากตัวนับจริง
4. เทียบ 3 รายการ: ไฟล์ที่ตั้งใจแก้ (จาก BUG-01.md และ CR-01.md) | ไฟล์ที่ hash ต่าง | ไฟล์ที่ REA บอกว่า bundle ต่าง → ตรงกันไหม ✅ / ⚠️ · ส่วนเกินต้องมีคำอธิบาย
5. obligation ledger "ของใหม่ต้องทำได้เท่าของเดิม": จาก BASELINE.md และ API-INVENTORY.md เลือกพฤติกรรมเดิมที่ไฟล์ที่แก้แตะถึง ≥ 6 ข้อ (กฎเงิน คูปอง ค่าส่ง สั่งซื้อ)
   ตาราง ของเดิมที่ต้องยังทำได้ | ชนิด (positive = ทำได้เหมือนเดิม · negative = ยังปฏิเสธสิ่งที่เคยปฏิเสธ · malformed = ข้อมูลผิดรูปยังถูกจัดการ) | ที่มาของผลคาดหวัง [D] / [R] / [E] | หลักฐาน (เทสต์ไหน · ไฟล์ผลไหน) | ผล ✅ / ❌ / ⚪ ยังไม่มีหลักฐาน
   ข้อที่ยังไม่มีหลักฐานให้เขียน ⚪ ห้ามเดาว่าผ่าน · ข้อที่มีแค่ [E] และไฟล์ที่แก้เปลี่ยนพฤติกรรมนั้น ให้ติด ⚪ และเขียนคำถามถึงร้าน · อ้างผลรันที่จดไว้ใน BUG-01.md และ CR-01.md ได้ · ถ้ารันใหม่ให้รันทีละเบราว์เซอร์ (--project=) เพราะ test:all รอบเดียวทำสต็อกหมด
CHANGE-PROOF.md: ตารางข้อ 1 · ตาราง 4 ทิศ + ตัวนับ 7 คลาสของทุกคู่ · ตาราง 3 รายการ · obligation ledger · evidence_id_short ของทุกผล REA (ผล import-reference-source ไม่มี evidence_id ให้ใช้ root_sha256_short ที่ตัวย่อพิมพ์แทน)
ทุกค่าต้องมาจากผลที่รันจริง · สรุปเป็นตาราง: หลักฐาน | บอกอะไร | ตรงกับที่ตั้งใจไหม
```

### ส่วนที่ 2

```text
อ่าน CHANGE-PROOF.md, BUG-01.md, CR-01.md และ BASELINE.md แล้วปิดงานด้วย CHANGE-REPORT.md
(ห้ามแก้โค้ด · ไฟล์ใหญ่ใน out/ ย่อด้วย node rea\rea-summarize.mjs เท่านั้น · ห้ามเปิด _solution/ fast_track/ และ README.md ของโฟลเดอร์บท (มีเฉลย)
 รันคำสั่ง shell ทุกตัวด้วย PowerShell จากโฟลเดอร์บท · ถ้ามีแต่ bash ให้เขียนคำสั่งลงไฟล์ rea\scratch\run.ps1 แล้วรัน powershell -NoProfile -ExecutionPolicy Bypass -File rea\scratch\run.ps1 · ห้ามแปลงคำสั่งเป็น bash เอง)
เรียก REA ด้วย powershell -NoProfile -ExecutionPolicy Bypass -File .\rea\rea.ps1 <อาร์กิวเมนต์> (ด้านล่างเขียนย่อว่า REA <อาร์กิวเมนต์>)
1. ดูข้อจำกัดของอีกเครื่องมือ: node rea\rea-input.mjs compare out\v1-server.json out\v2-server.json out\cmp.in.json
   แล้ว REA -Out out\cmp.json compare-application-versions /work/out/cmp.in.json --json (~20 วินาที) · ย่อด้วย node rea\rea-summarize.mjs out\cmp.json แล้วจดเฉพาะตัวนับ summary และ items_total · อธิบาย 2 บรรทัดว่าทำไมผลนี้อ่านยากกว่าตาราง 4 ทิศ
2. บันทึก HAR รอบใหม่: node rea\record-har.mjs --out out\after แล้ว REA -Out out\after\har.json inspect-web-network-capture /work/out/after/pawpantry-main.har har --sensitive-value Paw12345 --sensitive-value demo@pawpantry.test --json
   ย่อด้วย node rea\rea-summarize.mjs out\after\har.json --md แล้วเทียบ API กับ API-INVENTORY.md: API เดิมยังครบไหม · status เหมือนเดิมไหม · keys ที่เพิ่ม (ตัวย่อแสดง key 2 ชั้น เช่น order{…} จึงเห็น key ที่เพิ่มใน object ซ้อน)
3. เขียน CHANGE-REPORT.md ตาราง: CR/BUG | ชนิดงาน (Chikofsky & Cross: restructuring = เปลี่ยนโครงสร้างโดยพฤติกรรมเดิม · re-engineering = เปลี่ยนพฤติกรรม/เพิ่มความสามารถ) | ไฟล์ที่แก้ (+/−) | เทสต์ใหม่ (แดงก่อน / เขียวหลัง) | regression 3 เบราว์เซอร์ | หลักฐาน REA (evidence_id) | พฤติกรรมที่เปลี่ยนโดยตั้งใจ | ความเสี่ยงคงค้าง | วิธี rollback
   ทุกตัวเลขอ้างไฟล์ผลที่มาจากการรันจริง · มีหัวข้อ "สิ่งที่หลักฐานยังพิสูจน์ไม่ได้" · ข้อไหนหลักฐานไม่พอให้ย้ายไปหัวข้อนี้ ห้ามเดาว่าผ่าน
สรุปเป็นตาราง: หัวข้อใน CHANGE-REPORT | อ้างไฟล์ไหน
```

🎯 **ผลที่คาดหวัง** (`REA-FEASIBILITY` §2.6–2.7)
- ข้อ 1: ต่าง = 6 ไฟล์ของ CR-01 (มี `lib/orders.ts` ที่แก้ทั้ง BUG-01 และ CR-01) · out\v1 อาจมี `next-env.d.ts` เพิ่ม/`tsconfig.json` ต่าง เพราะ `next build` เขียนให้ → ต้องอธิบายได้ว่าเป็นไฟล์ที่ build สร้าง ไม่ใช่การแก้
- build v2 ~3 นาที · import-reference-source ~3 s (~59 KB) · s2b ~9–10 s ต่อคู่ · baseline v1src→v1build ≈ unchanged 44 · duplicated 9 · unknown 3 (`globals.css` `eslint.config.mjs` `next.config.ts`)
- ตาราง 4 ทิศ: ไฟล์ที่แก้ออกมาเป็น **unknown ในคู่ข้ามเวอร์ชัน** และ unchanged/duplicated ในคู่เวอร์ชันเดียวกัน · REA มีคลาส `modified` แต่ในรอบที่รันจริง (A1) `modified = 0` ทุกคู่ เพราะจับคู่ด้วย digest ไม่ได้ (`rea-probe/evidence/07`) → ตัวนับ 7 คลาสต้องรายงานครบแม้เป็น 0
- 3 รายการตรงกัน (✅) ยกเว้นไฟล์ที่ build สร้าง
- obligation ledger: กฎเงินเดิม (PAW10 floor 10% · FREESHIP · ส่งด่วน ฿120 · ส่งฟรีที่เกณฑ์) = positive · คูปองหมดอายุ/โค้ดมั่วยังถูกปฏิเสธ = negative · `giftWrap: "true"` ไม่คิดค่าห่อ = malformed · หลักฐานจาก golden/char/TC-GIFT · ข้อที่ไม่มี test → ⚪
- CHANGE-REPORT: BUG-01 = restructuring ของกฎเงิน (ทำให้ server ใช้กฎเดียวกับหน้าเว็บ) หรือ re-engineering ถ้าตีความว่าเปลี่ยนพฤติกรรม (ต้องมีเหตุผล) · CR-01 = re-engineering
- compare-application-versions: ~17 s · ส่วนใหญ่ `changed`/`unknown` เป็นร้อยรายการ (A1: server changed 273 · unknown 1479) · อธิบายว่า coverage partial + ชื่อ chunk hash เปลี่ยนทั้งชุด
- HAR ใหม่: API 4 ตัวเดิม status เดิม · ตัวย่อ (key 2 ชั้น · ตรวจกับ `out\after\har.json` ของ RUN05) แสดง request `…, giftWrap` และ response `order{…,shipping,giftWrap,giftWrapFee,total,…}` (ก่อนแก้ตัวย่อ RUN05 เห็นแค่ `order, id` จึงมองไม่เห็น key ที่เพิ่ม)
- RUN05: `Get-FileHash` ไม่ใส่ `-LiteralPath` นับไฟล์ต่างได้ 5 แทน 6 (หลุด `app/orders/[id]/page.tsx`) → พรอมต์บังคับ `-LiteralPath` + เทียบ `git status --short petshop` แล้ว · `next-env.d.ts` มีแค่ใน v1 = ไฟล์ที่ `next build` สร้าง (gitignored) ไม่ใช่การแก้

👀 "เครื่องมือที่ล้มแบบเงียบ (ได้ค่าว่างไม่ error) อันตรายกว่าเครื่องมือที่ error → ตัวนับสำคัญต้องเทียบกับแหล่งที่สอง (git status)"

✔️ **ไปต่อได้เมื่อ:** `CHANGE-PROOF.md` ตาราง 3 รายการไม่มี ⚠️ ที่อธิบายไม่ได้ · `CHANGE-REPORT.md` ทุกช่องมีไฟล์อ้างอิง

---

## LAB 10 · ฝึกเดี่ยวครบวงจร PR-1 (✏️)

```text
ฝึกครบวงจรกับปัญหาอีกเรื่อง (ข้อความลูกค้าอยู่ท้ายพรอมต์) ทำตามกติกาใน CLAUDE.md ทุกข้อ
(ห้ามเปิด _solution/ fast_track/ และ README.md ของโฟลเดอร์บท (มีเฉลย) · รันคำสั่ง shell ทุกตัวด้วย PowerShell จากโฟลเดอร์บท · ถ้ามีแต่ bash ให้เขียนคำสั่งลงไฟล์ rea\scratch\run.ps1 แล้วรัน powershell -NoProfile -ExecutionPolicy Bypass -File rea\scratch\run.ps1
 คำสั่งที่เขียนว่า "นาน" ให้ตั้ง timeout อย่างน้อย 10 นาที หรือรันเบื้องหลังแล้วรอจนจบ ห้ามสั่งซ้ำระหว่างรอ · สคริปต์ชั่วคราวเก็บใน rea\scratch\)
1. ทำซ้ำแบบ black-box ก่อนเปิดโค้ด (reset ข้อมูลก่อนทำซ้ำทุกรอบ · สินค้านี้สต็อกน้อย) แล้วเขียน e2e-legacy/tests/new/pr1-add-to-cart.spec.ts ที่แดงตามอาการ · ผลที่คาดหวัง (ทั้งข้อความและชนิดของการแจ้งเตือน) ต้องมาจาก [D] หรือ [R] พร้อมเหตุผล ถ้ายังไม่มีให้ถามผมก่อน
2. หาต้นเหตุ (ไฟล์:บรรทัด) + ตาราง impact (ใครใช้โค้ดนี้อีก · หน้าไหนกระทบ · เทสต์ที่ต้องรันซ้ำ) แล้วถามผมก่อนแก้
3. แก้ให้เล็กที่สุด → build ใหม่ (docker compose up -d --build ในโฟลเดอร์ petshop · นาน 1–3 นาที) → เทสต์ใหม่เขียว → รันชุดเดิม + tests/new บน chromium (npx playwright test) แล้วค่อย 3 เบราว์เซอร์ (npm run test:all · นาน)
   ถ้า test:all ล้มด้วย 409 "สินค้าไม่พอ" หรือปุ่ม qty-plus กดไม่ได้ = สต็อกหมด ไม่ใช่เว็บพัง → รันทีละเบราว์เซอร์ (npx playwright test --project=firefox แล้ว --project=webkit) แล้วรวมผล
4. เพิ่ม PR-1 ในตารางสรุปของ CHANGE-REPORT.md (เป็นแถวหรือคอลัมน์ตามรูปแบบเดิมของตาราง: ชนิดงาน · ไฟล์ที่แก้ +/− ทีละไฟล์ด้วย git diff --no-index --stat out\v1\<ไฟล์> petshop\<ไฟล์> · เทสต์แดงก่อน/เขียวหลัง · regression)
ทุกค่าต้องมาจากที่รันจริง · ห้ามแก้เทสต์เดิมให้ผ่าน · สรุปเป็นตาราง: ขั้น | หลักฐาน (ไฟล์) | ผล

--- ข้อความจากลูกค้า ---
📩 กดเพิ่ม "สูตรลดก้อนขน" 2 ชิ้นจากหน้าสินค้า แล้วกดเพิ่มอีก 2 ชิ้น ระบบขึ้นว่า "เพิ่ม…ลงตะกร้าแล้ว" ทั้งสองรอบ
แต่ในตะกร้ามีแค่ 3 ชิ้น งงว่าอีกชิ้นหายไปไหน
```

🧑 **คำตอบร้าน / ผู้เรียน**
- ข้อความที่ถูก [D]: เพิ่มได้ไม่ครบ → แจ้งเตือน (ไม่ใช่ข้อความสำเร็จ) `เพิ่มได้อีกเพียง {จำนวนที่เพิ่มได้} ชิ้น (สินค้าเหลือ {สต็อก} ชิ้น)` เช่น `เพิ่มได้อีกเพียง 1 ชิ้น (สินค้าเหลือ 3 ชิ้น)` · เพิ่มไม่ได้เลย = ข้อความเดิม · เพิ่มได้ครบ = ข้อความเดิม
- ข้อ 2 "ถามก่อนแก้": อนุมัติถ้าแก้ที่ helper กลาง (`useAddToCart`) ที่เดียว

🎯 **ผลที่คาดหวัง** (`CR-DESIGN` §4 PR-1 · **ยังไม่มีใคร implement/รัน**)
- สต็อกสูตรลดก้อนขน = 3 · รอบแรกเพิ่ม 2 → ข้อความสำเร็จ · รอบสองเพิ่มได้ 1 แต่ข้อความยังบอก "เพิ่ม…แล้ว" · ตะกร้า 3 ชิ้น ฿1,560
- ต้นเหตุ: `components/ProductCard.tsx` `useAddToCart` เช็กแค่ `added > 0` · ใช้ร่วมกับการ์ดสินค้า/หน้าสินค้า/Finder → impact หลายหน้า
- แก้ 1 ไฟล์ (คาด) · test PR-1 แดง → เขียว · ชุดเดิม 40/40 × 3
- RUN05: `test:all` รอบเดียวล้มเพราะสต็อกร่วมหมด (ซ้ำ LAB 8) → รันทีละเบราว์เซอร์ · toast หายใน ~2.8 วิ test ที่ตรวจ toast อาจ flaky บนเครื่องช้า · CHANGE-REPORT จาก LAB 9 เป็นตารางแนวตั้ง → PR-1 เป็นคอลัมน์

👀 "บทเรียนข้อมูลทดสอบหมด (ซ้ำ LAB 8): ข้อล้มที่ error คือ 409 สินค้าไม่พอ = ข้อมูลทดสอบ ไม่ใช่โค้ด · ทุก test ใหม่ที่ซื้อของเพิ่มภาระสต็อกให้ทั้งชุด"

✔️ **ไปต่อได้เมื่อ:** test PR-1 แดงก่อน/เขียวหลัง · regression ไม่มีข้อล้ม (รันรวมหรือทีละเบราว์เซอร์) · PR-1 ใน `CHANGE-REPORT.md`

---

## ทางเลือก MCP · ให้ Agent ใช้ REA เอง (ไม่นับ LAB · อยู่ใน 🔁 รันซ้ำ)

ตั้งค่า 1 ครั้ง: สร้างไฟล์ `.mcp.json` ที่โฟลเดอร์บท ด้วยเนื้อหานี้ (แทน `C:/path/to/…` ด้วย path เต็มของโฟลเดอร์บท ใช้ `/` · รูปเดียวกับ `rea-probe/mcp-rea.example.json` ที่ทดสอบแล้วผ่าน `--mcp-config`) แล้วเปิดเซสชันใหม่และอนุมัติ server `rea`:

```json
{
  "mcpServers": {
    "rea": {
      "type": "stdio",
      "command": "docker",
      "args": ["run", "-i", "--rm", "-v", "C:/path/to/05_rea-reverse-engineer-legacy-petshop:/work", "rea-lab:6.4.0", "mcp"]
    }
  }
}
```
> ⚠️ **ยังไม่ทดสอบ** แบบ `.mcp.json` ระดับ project (ทดสอบแล้วแค่ `claude --mcp-config <ไฟล์>`) · ไม่ใช้ `claude mcp add … -- docker …` เพราะ npm shim `.ps1` ของ PowerShell อาจกิน `--` · `.mcp.json` มี path เครื่องตัวเอง ห้าม commit

```text
ใช้เฉพาะเครื่องมือของ MCP server ชื่อ rea (ห้ามใช้ Bash และห้ามเปิดไฟล์ใน out/ ตรง ๆ)
1. เรียก analyze_javascript_application กับ /work/out/v1/.next/static ถ้าได้ resource_constraint ให้ใช้ evidence_id ที่คืนมาแทน
2. เรียก trace_application_feature ด้วย evidence นั้น seed ชนิด string ค่า /api/ ทิศ outgoing
3. ตอบ: ปุ่มใช้คูปองเรียก API อะไร อยู่ใน chunk ไหน · อะไรเป็น observed อะไรเป็น inference อะไรยังไม่รู้
สรุปเป็นตาราง: endpoint | mechanism | chunk | ป้าย 🔵🟢🟡⚪
```

🎯 คาด (`REA-FEASIBILITY` §2.8): analyze ได้ `resource_constraint` (≥ 10,544,542 bytes เกินเพดาน 10,484,736) + `evidence_id` · trace ได้ 6 endpoint `call:fetch` ~55 s · `.mcp.json` แบบ project **ยังไม่เคยรันจริง** (ทดสอบแล้วแค่ `--mcp-config` · RUNNER ทดสอบได้ถ้ามีเวลา แล้วจด)
