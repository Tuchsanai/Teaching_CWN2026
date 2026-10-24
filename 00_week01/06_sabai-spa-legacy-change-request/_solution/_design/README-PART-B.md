## LAB 0 · เช็กเครื่อง + พอร์ตที่ Windows จอง

🎯 🔍 รู้ก่อนว่าเครื่องพร้อมไหม และเข้าใจว่า **ทำไมบทนี้เปิดเว็บที่พอร์ต 4000** ไม่ใช่ 3000 (อ่านอย่างเดียว ได้ตารางในแชท)

![ทางเดินในสปามีประตูไม้เรียงกัน ป้ายเลข 2970 … 3000 … 3069 ทุกบานคล้องแม่กุญแจและติดป้าย Windows จองไว้ ประตู 4000 เปิดอยู่มีแสงอุ่น คุณจันทร์ยืนเปิดประตูยิ้มต้อนรับ หุ่นยนต์โบกมือชวนเด็กสะพายเป้เดินเข้าไป ป้ายไม้สีทองด้านบน 3000 ถูกจอง ใช้ 4000](img/concept-17-reserved-ports.jpg)

💬 **คัดลอกพรอมต์นี้** (กดปุ่ม Copy มุมขวาของกรอบ)

```text
ตรวจเครื่องให้พร้อมสำหรับงานแก้ระบบเดิม "สบายใจ สปา" (อ่านอย่างเดียว ห้ามติดตั้ง ห้ามแก้ไฟล์ ห้ามหยุด container ใด ๆ) ทุกค่าต้องมาจากคำสั่งที่รันจริงใน PowerShell
1. Docker Desktop: docker version และ docker compose version
2. Node.js: node -v (ต้อง 22.18 ขึ้นไป เพราะชุดตรวจ web/scripts/check-rules.mjs import ไฟล์ .ts ตรง) · npm -v · git --version
3. ช่วงพอร์ตที่ Windows จองไว้: netsh interface ipv4 show excludedportrange protocol=tcp
   - บอกว่าพอร์ต 3000, 4000, 5433 อยู่ในช่วงที่จองไหม (ถ้าอยู่ให้บอกช่วงที่ครอบ)
   - อธิบายสั้น ๆ ภาษาง่าย ๆ ว่าทำไมบทนี้เปิดเว็บที่พอร์ต 4000 แทน 3000
4. พอร์ต 4000 และ 5433 มีโปรแกรมใช้อยู่ไหม: Get-NetTCPConnection -LocalPort 4000,5433 -State Listen -ErrorAction SilentlyContinue (ไม่มีผล = ว่าง) และ docker ps --format "{{.Names}} {{.Ports}}" · ถ้าไม่ว่าง บอกด้วยว่าเป็น container ไหน (เช่น เว็บบท 05 ที่เปิดค้างไว้ที่ 4000)
5. มี container หรือ volume ชื่อขึ้นต้นด้วย sabai จากบทก่อนไหม: docker ps -a --filter name=sabai และ docker volume ls --filter name=sabai (บอกอย่างเดียว ยังไม่ต้องปิด)
6. REA: docker image inspect rea-lab:6.4.0 --format "{{.Id}}" · ถ้ามีให้รัน docker run --rm rea-lab:6.4.0 mcp doctor แล้วบอก exit code (0 = พร้อม) · ถ้าไม่มี image ให้บอกคำสั่ง build จากโฟลเดอร์ 05_rea-reverse-engineer-legacy-petshop\rea ใน repo คอร์สที่ clone ไว้ (ยังไม่ต้อง build · build นานหลายนาที)
7. สิทธิ์รันสคริปต์ PowerShell: Get-ExecutionPolicy -List (บอกอย่างเดียว ห้ามแก้ · บทนี้เรียก .ps1 ด้วย powershell -ExecutionPolicy Bypass -File จึงไม่ต้องเปลี่ยนค่าเครื่อง · แถว Process อาจเป็น Bypass เพราะเครื่องมือที่เปิด PowerShell ตั้งให้ชั่วคราว ไม่ใช่ค่าถาวรของเครื่อง)
8. โฟลเดอร์นี้มี web/ db/ e2e-legacy/ tools/ CHANGE-REQUESTS/ ครบไหม · และอยู่ข้างใน git repo อื่นหรือเปล่า: git rev-parse --show-toplevel · error = ยังไม่เป็น repo · ได้ path ของโฟลเดอร์นี้เอง = โฟลเดอร์บทเป็น repo ของตัวเองอยู่แล้ว (ใช้ได้) · ได้ path อื่นที่ไม่ใช่โฟลเดอร์นี้ = อยู่ใน repo อื่น
สรุปเป็นตาราง: รายการ | ผล | พร้อมไหม | ถ้าไม่พร้อมต้องทำอะไร
```

✅ **ผลจริง** <!-- RESULT:LAB0:summary --> ⏳ *บรรทัดสรุป "พร้อม N/N รายการ" · ช่วงพอร์ตที่จองบนเครื่องที่รันจริง · เวลาที่ใช้ (~N นาที)*

<!-- RESULT:LAB0:table --> ⏳ *ตาราง รายการ | ผล | พร้อมไหม 5–7 แถวเด่น (Docker · Node · ช่วงพอร์ตที่จอง · 4000/5433 · rea-lab `mcp doctor` · ExecutionPolicy · โฟลเดอร์อยู่ใน repo อื่นไหม)*

<!-- RESULT:LAB0:img/lab0-checklist.png --> ⏳ *ภาพ `img/lab0-checklist.png` ตารางผล LAB 0 ธีมมืด + บรรทัดสรุปสีเขียว (alt ใส่ตัวเลขทุกตัวในภาพ)*

👀 **สังเกต**
- **ช่วงพอร์ตที่ Windows จองต่างกันแต่ละเครื่อง** และเปลี่ยนได้หลังรีบูต (Hyper-V / WSL / WinNAT จองไว้) · ดูของเครื่องตัวเองทุกครั้ง · ถ้า 4000 ถูกจองให้ใช้แถว `bind` ใน [ถ้าเจอปัญหา](#ถ้าเจอปัญหา-คัดลอกพรอมต์นี้)
- **ExecutionPolicy เป็น `Restricted` ก็ไม่เป็นไร** บทนี้เรียก `.ps1` ด้วย `powershell -ExecutionPolicy Bypass -File` ทีละคำสั่ง ไม่ต้องแก้ค่าเครื่อง · แถว `Process` เป็น `Bypass` ได้เพราะเครื่องมือที่เปิด PowerShell ตั้งให้ชั่วคราว ไม่ใช่ค่าถาวร
- **เช็ก REA ด้วย `mcp doctor`** (exit 0 = พร้อม) ไม่ใช่ `--version` ซึ่งไม่ใช่คำสั่งที่พิสูจน์แล้ว
- ⚠️ **container ของบท 04 ยังเปิดอยู่ = พอร์ตชน** ชื่อไม่ชนเพราะบทนี้ใช้ `sabai06-*` แต่ฐานข้อมูลบท 04 ใช้ host 5433 เหมือนกัน · ปิดแบบไม่ลบ volume ก่อน LAB 1
- ⚠️ **เว็บบท 05 ใช้ 4000 เหมือนกัน** รอบจริงเจอ 4000 ไม่ว่างเพราะ `pawpantry05` เปิดค้าง · `docker stop pawpantry05` (ไม่ลบอะไร) หรือย้ายพอร์ตด้วย `$env:WEB_PORT` + `$env:BASE_URL`
- **โฟลเดอร์บทอยู่ใน repo คอร์สที่ clone มา?** คัดลอกทั้งโฟลเดอร์ไป `C:\work\sabai06` แล้วเปิด Claude Code ที่นั่น (กัน repo ซ้อน repo ตอน `git init` ใน LAB 1) · ถ้า `--show-toplevel` ได้โฟลเดอร์บทเอง = บทเป็น repo ของตัวเองอยู่แล้ว ใช้ต่อได้

✔️ **ไปต่อได้เมื่อ:** Docker ✅ · Node ≥ 22.18 ✅ · git ✅ · 4000 และ 5433 ว่างและไม่อยู่ในช่วงที่จอง · มี `rea-lab:6.4.0` และ `mcp doctor` exit 0 · โฟลเดอร์ไม่อยู่ใน repo อื่น

---

## LAB 1 · รับมอบระบบ

🎯 🔍 เปิดระบบเดิม 2 กล่อง · รันชุดตรวจที่ผู้รับเหมาส่งมอบ 2 ชั้น · **เทียบคำอ้างในบันทึกส่งมอบกับผลจริง** · ตั้ง baseline ด้วย git → ได้ `HANDOVER-CHECK.md` + commit แรก

![ห้องทำงานสปา เครื่องจักรไม้เก่าป้าย ระบบเดิม ยังพิมพ์การ์ด จองคิว ออกมาเรื่อย ๆ โปสเตอร์ SPEC v1.0 บนผนังถูกขีดกากบาท ผู้รับเหมาใส่แว่นดำถือกระเป๋าเดินออกประตูพร้อมพูดว่า ผ่านหมดแล้วนะ เด็กยิ้มเปิดกล่องเครื่องมือป้าย ทีมใหม่ หุ่นยนต์ถือป้าย คำอ้าง ≠ หลักฐาน ป้ายไม้สีทองด้านบน ระบบที่ได้รับมอบ](img/concept-01-inherited-system.jpg)

💬 **คัดลอกพรอมต์นี้**

```text
รับมอบระบบเดิม "สบายใจ สปา" จากผู้รับเหมาเดิม แล้วเขียน HANDOVER-CHECK.md (รันคำสั่งด้วย PowerShell จากโฟลเดอร์นี้ · ห้ามแก้ไฟล์ใน web/ db/ e2e-legacy/ · ห้ามเปิด README.md ของบท fast_track/ _solution/ และ CHANGE-REQUESTS/answers/)
0. อ่าน CHANGE-REQUESTS/00-HANDOVER-MEMO.md ก่อน แล้วแยกคำอ้างของผู้รับเหมาเป็นข้อ ๆ (H1, H2, …) · อ่าน e2e-legacy/README-LEGACY.md ด้วย (เป็นคำอ้างของผู้รับเหมาเหมือนกัน ใช้เลข H ต่อจากบันทึกส่งมอบ)
1. เปิดระบบ: docker network create sabai06-net (ถ้ามีแล้วข้ามได้) → docker compose -f db/compose.yaml up -d --wait → docker compose -f web/compose.yaml up -d --build --wait (build ครั้งแรกอาจนานเกิน 2 นาที ให้รันแบบ background หรือตั้ง timeout ยาว แล้วรอจนเสร็จ) · จดเวลาที่ใช้ (เสร็จเร็วและขึ้น CACHED = เคย build แล้ว ไม่ใช่ปัญหา)
2. ตรวจ: GET http://localhost:4000/api/health ต้องได้ {"ok":true,"db":true} · POST http://localhost:4000/api/test/reset · จดเวอร์ชัน Next.js (web/package.json) PostgreSQL (SELECT version()) และ Node ใน container
3. ชุดตรวจที่ส่งมอบ ชั้น 1: node web/scripts/check-rules.mjs → ผ่านกี่ข้อจากกี่ข้อ ใช้เวลาเท่าไร
4. ชุดตรวจที่ส่งมอบ ชั้น 2: Push-Location e2e-legacy; npm install; npx playwright install chromium firefox webkit; npx playwright test; Pop-Location (ค่าเริ่ม = api + chromium · ไม่ต้องใส่ --reporter เพราะ config พิมพ์ผลรายข้อและเขียนรายงาน html ให้ npm run report ตามที่ README-LEGACY อ้างอยู่แล้ว) → แยก ผ่านจริง / คาดว่าล้ม (test.fail) / ล้ม / เวลา · Playwright นับข้อ "คาดว่าล้มแล้วล้มจริง" รวมไว้ใน passed ของบรรทัดสรุป และผลรายข้อแสดง ✘ เหมือนข้อที่ล้มจริง → ข้อ ✘ ที่ไม่อยู่ในรายชื่อ failed ท้ายผล = คาดว่าล้ม · ยืนยันด้วย Select-String -Path e2e-legacy\tests\*.ts -SimpleMatch -Pattern "test.fail("
5. ทุกข้อที่ล้มหรือติด test.fail: เปิดอ่านเทสต์ข้อนั้น (อ่านได้ ห้ามแก้) แล้วจำแนกเป็น บั๊กของระบบ / เทสต์ล้าสมัย / ยังไม่รู้ พร้อมหลักฐาน
6. เทียบคำอ้างทุกข้อในบันทึกส่งมอบกับผลที่รันได้จริง: ตรง ✅ / ไม่ตรง ❌ / ตรวจไม่ได้ตอนนี้ ⚠️ (ข้อไหนตรวจไม่ได้ให้บอกว่าต้องใช้วิธีไหนตรวจ)
7. ตั้ง baseline ด้วย git (เขียน HANDOVER-CHECK.md ให้เสร็จก่อน แล้วค่อย commit · commit id บอกในแชทแล้วเติมลงไฟล์ทีหลังได้):
   - ถ้า git rev-parse --show-toplevel ชี้ไปโฟลเดอร์อื่นที่ไม่ใช่โฟลเดอร์นี้ ให้หยุดแล้วบอกผมก่อน
   - ยังไม่เป็น repo → git init · เป็น repo ของโฟลเดอร์นี้อยู่แล้ว → ข้าม init
   - เพิ่มบรรทัดที่ยังไม่มีใน .git/info/exclude: /_solution/ /img/ /README.md /EXAM.md /fast_track/ rea-out/ backups/ node_modules/ test-results/ test-report/ playwright-report/ (มี / นำหน้า = เฉพาะที่รากโฟลเดอร์บท ไม่กัน README.md ในโฟลเดอร์ย่อย)
   - git add -A → git status ต้องไม่เห็นไฟล์ที่ exclude → git commit -m "baseline: ระบบที่รับมอบ" (repo ที่มี commit อยู่แล้วและเปลี่ยนแค่ HANDOVER-CHECK.md ก็ commit ไฟล์นั้นเป็น baseline) → บอก commit id และจำนวนไฟล์
HANDOVER-CHECK.md มี: เวอร์ชัน · container และพอร์ต · เวลาเปิดระบบ · ผลชุดตรวจ 2 ชั้น · ตารางข้อที่ล้ม · ตารางคำอ้าง vs ผลจริง · commit baseline
ทุกตัวเลขต้องมาจากคำสั่งที่รันจริง ถ้าขั้นไหนไม่ผ่านให้หยุดแล้วบอกสาเหตุ ห้ามแก้เทสต์ให้ผ่าน
สรุปเป็นตาราง: ชุดตรวจ | ผ่าน | ล้ม | คาดว่าล้ม | เวลา
```

✅ **ผลจริง** <!-- RESULT:LAB1:summary --> ⏳ *ได้ `HANDOVER-CHECK.md` · check-rules ผ่าน/ทั้งหมด · e2e-legacy ผ่านจริง / คาดว่าล้ม / ล้ม · เวลา build และเวลารวม (~N นาที)*

<!-- RESULT:LAB1:table-suites --> ⏳ *ตาราง ชุดตรวจ | ผ่าน | ล้ม | คาดว่าล้ม | เวลา (check-rules · e2e-legacy api + chromium) จาก LAB1_RESULT*

<!-- RESULT:LAB1:table-claims --> ⏳ *ตาราง คำอ้าง H1–H6 | ผลจริง | ✅ / ❌ / ⚠️ คัด 3–6 แถว (ห้ามใส่คำตอบการจำแนกข้อที่ล้มในข้อความนำ)*

<!-- RESULT:LAB1:img/lab1-handover.png --> ⏳ *ภาพ `img/lab1-handover.png` 2 ตาราง (ชุดตรวจ · คำอ้าง vs ผลจริง) + บรรทัดสรุป commit baseline*

👀 **สังเกต**
- **Playwright นับข้อ `test.fail()` ที่ล้มตามคาดรวมเป็น passed** ในบรรทัดสรุป และผลรายข้อขึ้น ✘ เหมือนข้อที่ล้มจริง → ข้อ ✘ ที่ไม่อยู่ในรายชื่อ failed ท้ายผล = คาดว่าล้ม (ยืนยันด้วย `test.fail(` ในไฟล์เทสต์) ไม่งั้นตัวเลข "ผ่านจริง + คาดว่าล้ม + ล้ม" จะไม่ตรงกับบรรทัดสรุป · ไม่ใส่ `--reporter` เพื่อให้ `npm run report` ของผู้รับเหมายังใช้ได้
- **ข้อแดงไม่ได้แปลว่าระบบผิดเสมอ** อ่านก่อนว่าเทสต์คาดอะไร ระบบตอบอะไร แล้วจำแนก บั๊ก / เทสต์ล้าสมัย / ยังไม่รู้ · ห้ามแก้ให้เขียว
- **บันทึกส่งมอบ = คำอ้าง [A] ของผู้รับเหมา** เอกสารของผู้รับเหมาเองยังอาจขัดกันเอง · เราเชื่อเฉพาะสิ่งที่รันเองแล้วจด
- ⚠️ **build ครั้งแรกนานเกิน 2 นาที** ถ้า Claude ตัดคำสั่งกลางทาง ให้สั่งรันแบบ background แล้วรอผลจริง
- **ไฟล์ใหญ่ห้ามเข้า git** (`rea-out/` `node_modules/` `backups/`) · `.git/info/exclude` กันไว้ตั้งแต่ commit แรก · ไฟล์ของบทเขียนมี `/` นำหน้า (`/README.md`) ไม่งั้น README.md ในโฟลเดอร์ย่อย เช่น `tests/golden/README.md` จะหายจาก commit ไปด้วย
- **เลข H ไม่ต้องตรงกับเพื่อน** บันทึกส่งมอบแตกได้หลายแบบ (รอบจริงได้ 12 ข้อ + README-LEGACY ต่อเลข) · เทียบกันด้วยเนื้อหาของคำอ้าง

✔️ **ไปต่อได้เมื่อ:** `/api/health` ได้ `db:true` · `HANDOVER-CHECK.md` มีตัวเลขผ่าน/ทั้งหมดของชุดตรวจ 2 ชั้น · ข้อที่ล้มหรือติด `test.fail` ทุกข้อถูกจำแนกพร้อมหลักฐาน · มี commit baseline

---

## LAB 2 · มองแบบ black-box ด้วย REA

🎯 🔍 ใช้ REA ดู **ของที่ส่งถึงเบราว์เซอร์** (static bundle) + **คำขอจริงจากการใช้งาน** (HAR) + **ขับหน้าจองด้วยสคริปต์** แล้วติดป้าย static / runtime / inference / unknown และ `[E ev_xxxxxxxx]` ทุกแถว → ได้ `docs/REA-INVENTORY.md` + `rea-out/`

![สปาตอนกลางคืน หุ่นยนต์ส่องไฟฉายป้าย REA ไปที่หน้าต่างร้านที่สว่าง เห็นป้าย หน้าเว็บ และ API ส่วนห้องหลังที่มีเครื่องคิดเงินป้าย กฎราคา และประตูห้องใต้ดินป้าย ฐานข้อมูล อยู่ในเงามืด เด็กถือป้าย ไม่เห็น ≠ ไม่มี ป้ายไม้สีทองด้านบน REA เห็นแค่หน้าร้าน](img/concept-04-browser-only.jpg)

> 🔁 **ทบทวนบท 05:** 3 วิธีสังเกตเว็บที่รันอยู่ · LAB นี้ใช้ครบทั้ง static (bundle) · HAR (บันทึกย้อนหลัง) · driven (`capture-browser-scenario`) · ยังไม่ได้ทำบท 05 ดู [บท 05](../05_rea-reverse-engineer-legacy-petshop/README.md)
>
> ![3 ช่องภาพ หัวเรื่อง 3 วิธีสังเกตเว็บที่รันอยู่ ช่องแรก Passive: ดูอย่างเดียว เด็กนั่งดูหน้าร้านสัตว์เลี้ยงในจอ ช่องกลาง Driven: ขับตามสคริปต์ หุ่นยนต์ถือรีโมตพาเคอร์เซอร์ไปที่ตะกร้า ช่องขวา HAR: ดูบันทึกย้อนหลัง เด็กเปิดสมุดที่มีซองจดหมายวิ่งระหว่างเบราว์เซอร์กับเซิร์ฟเวอร์ ข้างหีบป้าย ความลับ ที่มีกุญแจและคุกกี้ แมวส้มกับลูกหมานั่งดู](../05_rea-reverse-engineer-legacy-petshop/img/concept-10-passive-driven-har.jpg)

💬 **คัดลอกพรอมต์นี้**

```text
มองระบบที่รันอยู่แบบ black-box ด้วย REA แล้วเขียน docs/REA-INVENTORY.md (รันคำสั่งด้วย PowerShell · ขั้นนี้ห้ามเปิดอ่านโค้ดใน web/ db/ · ห้ามเปิด README.md ของบท fast_track/ และ _solution/ · ใช้เฉพาะคำสั่งข้างล่าง)
ทุกคำสั่งรันจากโฟลเดอร์บทใน PowerShell · เรียก REA ผ่าน powershell -NoProfile -ExecutionPolicy Bypass -File tools\rea.ps1 (ไม่ต้องแก้ execution policy ของเครื่อง) · ผลของ REA ใหญ่มาก ห้ามเปิดไฟล์ JSON ทั้งไฟล์ ให้ใช้ tools\rea-tools.mjs สรุป · REA พิมพ์ความคืบหน้าทาง stderr หลายร้อยบรรทัด จึงต่อท้ายคำสั่ง rea.ps1 ด้วย 2> rea-out\<ชื่อ>.log ตามข้างล่าง (เปิด log เฉพาะเมื่อคำสั่ง error)
0. เตรียม: Push-Location tools; npm install; Pop-Location · ระบบต้องเปิดอยู่ (GET http://localhost:4000/api/health ได้ db:true)
1. Static bundle = ของที่ส่งถึงเบราว์เซอร์:
   - ถ้า rea-out\v1\.next\static มีอยู่แล้ว ให้บอกผมก่อนลบแล้วคัดลอกใหม่ (คัดลอกทับจะได้ static\static)
   - New-Item -ItemType Directory -Force rea-out\v1\.next | Out-Null
   - docker cp sabai06-web:/app/.next/static rea-out\v1\.next\static
   - powershell -NoProfile -ExecutionPolicy Bypass -File tools\rea.ps1 -Out rea-out\static-v1.json analyze-javascript-application /work/rea-out/v1/.next/static --json 2> rea-out\static-v1.log
   - node tools\rea-tools.mjs endpoints rea-out\static-v1.json
   - node tools\rea-tools.mjs summary rea-out\static-v1.json (node ตามชนิด · endpoint · statistics · coverage · limitations)
   - node tools\rea-tools.mjs pages rea-out\static-v1.json (หน้า/route จากชื่อไฟล์ใน bundle)
   - node tools\rea-tools.mjs view rea-out\static-v1.json rea-out\view-v1.json แล้ว powershell -NoProfile -ExecutionPolicy Bypass -File tools\rea.ps1 -Out rea-out\summary-v1.json inspect-analysis-view /work/rea-out/view-v1.json --format json 2> rea-out\summary-v1.log · node tools\rea-tools.mjs summary rea-out\summary-v1.json (summary ที่ REA ทำเอง: statistics และ coverage ต้องตรงกับบรรทัดก่อน)
2. HAR ของเส้นทางใช้งานจริง (ต้องใช้ 127.0.0.1 ไม่ใช่ localhost):
   - ⚠️ record-har.mjs reset ข้อมูลก่อนเดิน แล้วจองนัดใหม่ (รอบรับมอบได้ B14) และยกเลิก B05 → ข้อมูลในระบบเปลี่ยน ถ้างานถัดไปต้องการข้อมูลตั้งต้นให้ reset ใหม่ (POST /api/test/reset)
   - node tools\record-har.mjs http://127.0.0.1:4000 rea-out\journeys.har
   - node tools\rea-tools.mjs har-records rea-out\journeys.har (ได้รายการ --record ของคำขอ /api/*)
   - powershell -NoProfile -ExecutionPolicy Bypass -File tools\rea.ps1 -Out rea-out\har-api.json inspect-web-network-capture /work/rea-out/journeys.har har <วาง --record ทั้งหมดที่ได้> --sensitive-value Nida@2026 --sensitive-value Owner@2026 --json 2> rea-out\har-api.log (body ของคำขอ login จะว่างเพราะ --sensitive-value = ตั้งใจ)
   - node tools\rea-tools.mjs har-api rea-out\har-api.json
3. ขับเบราว์เซอร์ด้วย REA (REA อยู่ใน docker network เดียวกับเว็บ จึงเปิด http://sabai06-web:3000 ได้): powershell -NoProfile -ExecutionPolicy Bypass -File tools\rea.ps1 -Network sabai06-net -Out rea-out\scenario.json capture-browser-scenario /work/tools/scenario-book-quote.json --json 2> rea-out\scenario.log · node tools\rea-tools.mjs scenario-sum rea-out\scenario.json (step completed x/y · URL สุดท้าย · API ที่เรียก · ยอดในหน้าสรุป) · ดึงภาพหน้าจอที่ REA ถ่าย: node tools\rea-tools.mjs shot rea-out\scenario.json rea-out\scenario-final.png
4. เขียน docs/REA-INVENTORY.md:
   - ตาราง endpoint | เห็นจาก static | เห็นจาก HAR (method, query, body keys, status) | ป้าย static / runtime / inference / unknown | แหล่ง [E ev_xxxxxxxx] (evidence_id 8 ตัวแรกของ Evidence ที่เห็นแถวนั้น · ได้จาก node tools\rea-tools.mjs ids rea-out)
   - ตาราง หน้า (route) ที่เห็นจากชื่อไฟล์ใน bundle (ผลของ pages)
   - หัวข้อ "สิ่งที่ REA ไม่เห็น": ห้ามเขียนว่า "ระบบไม่มี X" ถ้า coverage เป็น partial ให้เขียน "ไม่พบในหลักฐานนี้ เพราะ…"
   - หัวข้อ "คำถามที่ต้องไปหาคำตอบจากโค้ดหรือฐานข้อมูล" อย่างน้อย 5 ข้อ
   - ขนาดไฟล์ เวลา และ evidence_id ย่อ 8 ตัวแรกของ Evidence แต่ละก้อน (ขนาดและป้ายจาก node tools\rea-tools.mjs ids rea-out)
   - หัวข้อ "ค่าที่ล็อกได้เป็น [E]": ยอดหน้าสรุปจาก scenario และสถานะ/คีย์ของ API จาก HAR พร้อมป้าย [E ev_xxxxxxxx] · เขียนกำกับว่า [E] = "ระบบทำอยู่" ใช้ล็อกพฤติกรรมเดิมได้ แต่ไม่ใช่ "ควรทำ"
ถ้าคำสั่งไหน error ให้หยุดแล้วบอกข้อความ error จริง ห้ามเดาผล
สรุปเป็นตาราง: แหล่ง | endpoint ที่เห็น | เวลา | coverage | evidence_id ย่อ
```

✅ **ผลจริง** <!-- RESULT:LAB2:summary --> ⏳ *ได้ `docs/REA-INVENTORY.md` · endpoint จาก static · route stub · HAR กี่ endpoint / กี่ครั้ง · scenario กี่ step และยอดหน้าสรุป · coverage · เวลา (~N นาที)*

<!-- RESULT:LAB2:table --> ⏳ *ตาราง แหล่ง | endpoint ที่เห็น | เวลา | coverage | evidence_id ย่อ (static · HAR · scenario) + 3–5 แถวเด่นของตาราง endpoint พร้อมป้าย*

<!-- RESULT:LAB2:img/lab2-rea-inventory.png --> ⏳ *ภาพ `img/lab2-rea-inventory.png` ตาราง endpoint | REA static | HAR | ป้าย + บรรทัดสรุปตัวเลขจาก LAB2_RESULT*

<!-- RESULT:LAB2:img/lab2-scenario-final.png --> ⏳ *ภาพ `img/lab2-scenario-final.png` หน้าจอสรุปก่อนจ่ายที่ REA `capture-browser-scenario` ถ่ายเองในรอบจริง (ดึงด้วย `rea-tools.mjs shot`)*

👀 **สังเกต**
- **อัด HAR ผ่าน `127.0.0.1` ไม่ใช่ `localhost`** · `localhost` อาจกลายเป็น `[::1]` แล้ว REA ไม่รับไฟล์
- ⚠️ **รหัสผ่านใน body ของ HAR ไม่ถูกปิดเอง** ต้องส่ง `--sensitive-value` ทุกค่า ก่อนเอาหลักฐานไปแชร์
- **ไม่เจอ ≠ ไม่มี** หน้าที่อ่านข้อมูลฝั่งเซิร์ฟเวอร์ตรง (Server Component) จะไม่มีคำขอโผล่ใน HAR · coverage `partial` จึงห้ามเขียน "ระบบไม่มี X"
- **`>` ของ PowerShell 5.1 เขียนไฟล์มี BOM** REA อ่าน JSON นั้นไม่ได้ → ใช้ `rea.ps1 -Out` เสมอ
- **[E] = "ระบบทำอยู่" ไม่ใช่ "ควรทำ"** ใช้ล็อกพฤติกรรมเดิมได้ แต่ห้ามใช้ตัดสินว่ากฎถูก
- **REA เห็นเฉพาะกฎที่อยู่ฝั่งเบราว์เซอร์** กฎที่คิดฝั่งเซิร์ฟเวอร์ (ราคา จองซ้ำ กฎในฐานข้อมูล) ไม่อยู่ใน bundle · รอบจริงช่อง REA ของกฎเหล่านี้ใน triangulation (LAB 3) จึงเป็น "REA ไม่เห็น" + เหตุผล ไม่ใช่ `ev_` ที่แต่งขึ้น
- ⚠️ **`record-har.mjs` เปลี่ยนข้อมูล** (reset → จองนัดใหม่ → ยกเลิก B05) · งานถัดไปที่ต้องการข้อมูลตั้งต้นให้ reset ก่อน · body ของ login ใน HAR ว่างเพราะ `--sensitive-value` = ตั้งใจ

✔️ **ไปต่อได้เมื่อ:** ตาราง endpoint ติดป้ายครบ (static / runtime / inference / unknown + `[E ev_…]`) · ไม่มีประโยค "ระบบไม่มี…" · มีคำถามถึงโค้ด/ฐานข้อมูล ≥ 5 ข้อ · `git status` ไม่เห็น `rea-out/`

---

## LAB 3 · Agent อ่าน repo + DB → แผนที่ระบบ

🎯 🔍 ให้ Claude อ่าน repo และ schema ฐานข้อมูล แล้ว **เทียบ 3 ตา (REA · source · DB) + เอกสารเก่า** → ได้ `SYSTEM-MAP.md` (ทุกแถวมี `file:line`) และ `docs/SPEC-GAPS.md` (เป็นคำถามถึงร้าน) จากนั้น **เราตรวจทานเอง 5 แถว**

![สปาผ่าครึ่งเป็นหน้าร้าน หลังร้าน และห้องใต้ดิน หุ่นยนต์ถือเครื่องสแกนป้าย REA ส่องหน้าร้าน เด็กอ่านหนังสือป้าย โค้ด คุณจันทร์ผายมือ น้องบัวโบกธงในห้องใต้ดินข้างถังข้อมูลที่ล็อกด้วยแม่กุญแจป้าย CHECK และ EXCLUDE เส้นสีทองโยงสามจุดเป็นสามเหลี่ยม ป้ายกลาง ตรงกัน = มั่นใจ ป้ายไม้สีทองด้านบน มอง 3 ทาง + ฐานข้อมูล](img/concept-03-four-eyes.jpg)

💬 **คัดลอกพรอมต์นี้** (ส่วนที่ 1 · แผนที่ระบบ)

```text
อ่าน repo นี้แล้วเขียน SYSTEM-MAP.md = แผนที่ระบบเดิมสำหรับทีมใหม่ และ docs/SPEC-GAPS.md (รันคำสั่งด้วย PowerShell · ห้ามแก้โค้ด · ห้ามเปิด README.md ของบท fast_track/ _solution/ และ CHANGE-REQUESTS/answers/)
ใช้ Explore subagent ช่วยค้นได้ แต่ทุกแถวในไฟล์ต้องอ้าง ไฟล์:บรรทัด หรือชื่อฟังก์ชัน/ชื่อ constraint ที่เปิดดูจริง
1. สถาปัตยกรรม: compose 2 project · network · container · พอร์ต · env ที่มีผล (web/compose.yaml, db/compose.yaml, web/Dockerfile)
2. ชั้นของโค้ด หน้า → API route → lib/server → lib/rules · ตาราง route ทุกตัวใน web/app/api: method | path | ฟังก์ชันที่เรียก | component ไหนเรียก (หรือไม่มี) · นับ 2 แบบแล้วรายงานทั้งคู่: จำนวนไฟล์ route.ts และจำนวน handler (method + path)
3. กฎร้าน: ไล่ web/lib/rules ทุกไฟล์ → ตาราง กฎ (ภาษาคน) | ค่าคงที่ | ฟังก์ชัน | ถูกเรียกจาก | ข้อความที่พูดกฎเดียวกันซ้ำ (i18n, แชท, หน้าเว็บ)
4. ฐานข้อมูล: docker exec sabai06-db psql -U sabai -d sabai -c "\dt" แล้ว -c "\d booking" และ -c "\d booking_slot" → ตาราง: ตาราง | กฎที่ DB บังคับ (CHECK / EXCLUDE / UNIQUE) | กฎเดียวกันในโค้ดอยู่ไหน
   นับ constraint ทั้งระบบด้วยคำสั่ง (ไม่นับด้วยตา): docker exec sabai06-db psql -U sabai -d sabai -c "SELECT contype, count(*) FROM pg_constraint WHERE connamespace = 'public'::regnamespace GROUP BY 1 ORDER BY 1" (c = CHECK · f = FK · x = EXCLUDE · p = PK · u = UNIQUE) และแยกต่อตารางด้วย SELECT conrelid::regclass, contype, count(*) … GROUP BY 1, 2
5. Test hooks และ "วันนี้" ของระบบ: /api/test/* ทำอะไร · นาฬิกาอ่านจากไหน · reset ล้างตารางไหนและเอา seed มาจากไหน
6. กับดักถ้าจะแก้: ค่าที่เขียนตายตัว · กฎที่คิดซ้ำทั้งเซิร์ฟเวอร์และเบราว์เซอร์ · ไฟล์ db/init รันตอนไหน
7. Triangulation: เทียบกับ docs/REA-INVENTORY.md → ตาราง endpoint/กฎ | REA เห็น [E ev_xxxxxxxx] | source บอก [source ไฟล์:บรรทัด] | DB บอก [DB ชื่อ constraint] | SPEC บอก [SPEC §] | ตรงไหม ✅/⚠️/❌ | ถ้า REA ไม่เห็น เพราะอะไร · ทุกช่องต้องมีป้ายแหล่ง (ช่องที่ REA ไม่เห็นให้เขียน "REA ไม่เห็น" + เหตุผล ห้ามแต่ง ev_) · แถวที่ [E] หรือ [source] ขัดกับ [SPEC] ให้ส่งต่อเป็นคำถามใน SPEC-GAPS (ห้ามตัดสินเอง)
8. เอกสารเก่า: เทียบ web/SPEC.md กับโค้ดจริงแล้วเขียน docs/SPEC-GAPS.md: SPEC บอก | โค้ดทำ | หลักฐาน | คำถามถึงร้าน (ห้ามตัดสินเองว่าฝั่งไหนถูก)
ท้าย SYSTEM-MAP.md ใส่วันที่และ commit ที่ใช้ทำแผนที่ (git rev-parse --short HEAD) · ไม่แน่ใจข้อไหนให้เขียนในหัวข้อ "ยังไม่รู้" อย่าเดา
สรุปเป็นตาราง: หัวข้อ | จำนวนแถว | ข้อที่ยังไม่รู้
```

💬 **คัดลอกพรอมต์นี้** (ส่วนที่ 2 · เซสชันเดียวกัน · เราตรวจทานเอง)

```text
(รันคำสั่งด้วย PowerShell) ผมจะตรวจทาน SYSTEM-MAP.md ด้วยตาตัวเอง สุ่มมา 5 แถว: กฎร้าน 2 แถว · route 1 แถว · ฐานข้อมูล 1 แถว · กับดัก 1 แถว (สุ่มเลขแถวในแต่ละหัวข้อด้วย Get-Random ไม่เลือกแถวเอง)
แต่ละแถว เปิดไฟล์ตามที่อ้างแล้วคัดบรรทัดจริงมาให้ผมดู (ไม่เกิน 5 บรรทัดต่อข้อ) ฐานข้อมูลให้รัน psql ให้ดูผลจริง
ถ้าแถวไหนอ้างผิดหรือไม่ครบ ให้แก้ SYSTEM-MAP.md แถวนั้น แล้วบอกว่าผิดเพราะอะไร
เพิ่มหัวข้อ "ตรวจทานโดยคน" ท้าย SYSTEM-MAP.md
สรุปเป็นตาราง: แถวที่สุ่ม | ที่อ้าง | บรรทัดจริง | ตรงไหม ✅/❌ | แก้อะไร
```

✅ **ผลจริง** <!-- RESULT:LAB3:summary --> ⏳ *ได้ `SYSTEM-MAP.md` + `docs/SPEC-GAPS.md` · จำนวน route · กฎร้าน · ตาราง · constraint (CHECK / FK / EXCLUDE) · จำนวนแถว SPEC-GAPS · ผลตรวจทาน x/5 · เวลา (~N นาที)*

<!-- RESULT:LAB3:table-triangulation --> ⏳ *ตาราง กฎ/endpoint | REA | source | DB | SPEC | ตรงไหม 5–7 แถวเด่น 🔒 ห้ามมีแถวเรื่องที่สงวนไว้สำหรับข้อสอบชุด B (ดู LESSON-PLAN M10)*

<!-- RESULT:LAB3:img/lab3-triangulation.png --> ⏳ *ภาพ `img/lab3-triangulation.png` ตาราง triangulation จาก SYSTEM-MAP รอบจริง (กฎเดียวกับข้างบน: ไม่มีแถวสงวน)*

<!-- RESULT:LAB3:img/lab3-db-rules.png --> ⏳ *ภาพ `img/lab3-db-rules.png` ตาราง constraint | กฎ | โค้ดที่ตรวจซ้ำ จาก `\d booking` รอบจริง + บรรทัดสรุปจำนวนตารางและ constraint*

![โต๊ะทำงาน แฟ้มเก่าสีเหลืองหน้าบึ้งป้าย SPEC v1.0 พูดว่า พอร์ต 3000 แล็ปท็อปหน้ายิ้มขึ้นเลข 4000 หุ่นยนต์มีเครื่องหมายคำถามเหนือหัวถือป้าย ถามเจ้าของ ไม่เดา คุณจันทร์โบกมือผ่านวิดีโอคอลบนโทรศัพท์ เด็กเท้าคางยิ้ม ป้ายไม้สีทองด้านบน เอกสารเก่าไม่ตรงโค้ด](img/concept-05-outdated-docs.jpg)

👀 **สังเกต**
- **AI ชอบเดาหน้าที่จากชื่อไฟล์** แถวที่ไม่มี `file:line` = ยังไม่ได้เปิดดูจริง · ส่วนที่ 2 จึงให้คัดบรรทัดจริงมาให้เราดู
- **Explore subagent ส่งกลับแค่ข้อสรุป ไม่ใช่เนื้อไฟล์** · ข้อสรุปต้องมีที่อ้างที่เราเปิดตามได้
- **SPEC ขัดโค้ด = คำถามถึงร้าน ไม่ใช่คำตัดสิน** เอกสารเก่าอาจถูกและโค้ดผิดก็ได้ · คนตัดสินคือเจ้าของงาน
- **REA ไม่อ่าน Postgres** กฎที่ฐานข้อมูลบังคับเห็นได้จาก `\d` และนับครบด้วยคิวรี `pg_constraint` (ไม่นับด้วยตา) · ช่อง DB ใน triangulation จึงสำคัญเวลาจะเปลี่ยนตัวเลขกฎ
- **route นับได้ 2 แบบ** ไฟล์ `route.ts` กับ handler (method + path) ได้เลขต่างกัน 1 · เขียนทั้งคู่ ตัวเลขจะไม่ชวนเถียง
- **คำตอบข้อ 5–6 (test hooks · กับดัก) เก็บไว้ให้ดี** งานแก้ระบบใน LAB ถัด ๆ ไปต้องย้อนกลับมาใช้

✔️ **ไปต่อได้เมื่อ:** ทุกแถวมี `file:line` หรือชื่อ constraint · มีตาราง triangulation 3 ตา (+ SPEC) พร้อมป้ายแหล่งทุกช่อง · SPEC-GAPS เป็นคำถาม ไม่ใช่คำตัดสิน · ตรวจทานครบ 5 แถว

---

## LAB 4 · CLAUDE.md + รั้ว

🎯 ✏️ เขียนกติกาให้ Agent ทำงานกับระบบเดิมอย่างปลอดภัย → ได้ `CLAUDE.md` · `.claude/settings.json` (รั้ว `Edit(e2e-legacy/**)` + กันอ่าน `README.md` ของบท `fast_track/` `_solution/`) · `docs/IMPACT-TEMPLATE.md` · `docs/ORACLE-CHANGES.md` แล้ว **ทดสอบรั้วในเซสชันใหม่**

![สวนสปา ตู้กระจกบนแท่นป้าย e2e-legacy ล้อมรั้วไม้ป้าย ห้ามแตะ เด็กใช้ค้อนตอกเสารั้วต้นสุดท้าย หุ่นยนต์อ่านกระดานป้าย CLAUDE.md มี 3 ข้อ อธิบายก่อนแก้ แดงก่อน ห้าม down -v ป้ายตกแต่งมุมซ้าย พัก คิด ทำให้ดี ไปด้วยกัน ป้ายไม้สีทองด้านบน กติกาให้ Agent](img/concept-18-claude-md-fence.jpg)

💬 **คัดลอกพรอมต์นี้** (ส่วนที่ 1 · เขียนกติกา)

```text
เขียน CLAUDE.md สำหรับระบบเดิมนี้ + .claude/settings.json + docs/IMPACT-TEMPLATE.md + docs/ORACLE-CHANGES.md (รันคำสั่งด้วย PowerShell · ห้ามแก้โค้ดใน web/ db/ · ห้ามเปิด README.md ของบท fast_track/ และ _solution/)
อ่าน SYSTEM-MAP.md, docs/SPEC-GAPS.md และ HANDOVER-CHECK.md ก่อน
1. CLAUDE.md ไม่เกิน ~60 บรรทัด หัวข้อ: รันยังไง (PowerShell จากโฟลเดอร์บท: เปิดระบบ · reset · node web/scripts/check-rules.mjs · e2e ด้วย Push-Location/Pop-Location · ค่าเริ่ม api+chromium และคำสั่งครบ 3 เบราว์เซอร์ npm run test:all) · แผนที่: ลิงก์ไป SYSTEM-MAP.md แบบธรรมดา (ไม่ใช้ @ เพราะไฟล์ใหญ่ จะถูกโหลดเข้าทุกเซสชัน) · ห้ามแตะ · กติกาการแก้ · กับดัก (จาก SYSTEM-MAP) · เอกสารเก่า (@docs/SPEC-GAPS.md)
2. กติกาที่ต้องมี:
   - อธิบายและทำ impact ตาม docs/IMPACT-TEMPLATE.md ก่อนแก้ทุกครั้ง · เทสต์ใหม่ต้องแดงก่อนแก้ · แก้ให้เล็กที่สุด
   - ห้ามแก้ค่าที่คาดหวังเดิมใน web/scripts/check-rules.mjs, e2e-legacy/ และ tests/golden/ ถ้าไม่มี CR อนุญาต (ถ้าจำเป็นให้หยุดถาม แล้วจดใน docs/ORACLE-CHANGES.md)
   - ค่าที่คาดหวังติดป้ายแหล่งเสมอ: [D:CR-0N] จากคำตอบร้าน · [E ev_xxxxxxxx] จากหลักฐานระบบ (ใช้ได้เฉพาะล็อกพฤติกรรมเดิม) · [E] ขัด [D] = ผู้ต้องสงสัยบั๊ก ให้รายงาน ห้ามใช้ [E] นั้นเป็นค่าคาดหวัง
   - ห้าม docker compose down -v และห้ามลบ volume sabai06-pgdata (มีข้อมูลลูกค้าจริง)
   - เปลี่ยนโครงฐานข้อมูลด้วยไฟล์ migration แยก (db/migrations/) = ทางเดียวสำหรับฐานที่มีข้อมูลอยู่แล้ว · รันซ้ำได้ มีวิธีถอยกลับ · แก้ db/init ได้เฉพาะเพื่อให้เครื่องติดตั้งใหม่และ reset ตรงกับ migration ห้ามใช้ db/init เป็นวิธี deploy · รัน SQL ด้วย docker cp + psql -f (ห้าม pipe ไฟล์ภาษาไทยผ่าน PowerShell)
   - ภาษาไทย/จีนกับ PowerShell 5.1: ยิง API ที่มีข้อความไทย/จีนด้วยสคริปต์ node หรือ curl.exe --data-binary '@ไฟล์.json' (ห้าม Invoke-RestMethod -Body '<ไทย>' · curl เฉย ๆ = Invoke-WebRequest) · ตรวจข้อความไทยใน DB ด้วยการเทียบใน SQL (เช่น SELECT name_th = '<ข้อความ>') หรืออ่านผ่าน API ด้วย node · ห้ามตัดสินจากตัวอักษรที่ PowerShell แสดง (อาจเพี้ยนทั้งที่ข้อมูลถูก) และห้ามแก้ข้อมูลเพราะเห็นตัวอักษรเพี้ยนบนจอ
   - build หรือชุดทดสอบที่นานเกิน 2 นาที (เช่น docker compose up --build ครั้งแรก · e2e 3 เบราว์เซอร์) ให้รันแบบ background หรือ timeout ยาว แล้วรอผลจริง
   - ข้อความใหม่ต้องครบ 3 ภาษา (th/en/zh) · error ใหม่ต้องตรวจผลในแชทบอทด้วย
   - เอกสารเก่าขัดกับโค้ด ให้รายงานแล้วถาม ห้ามเลือกเอง
   - ห้ามเปิดอ่าน README.md ที่รากโฟลเดอร์บท fast_track/ และ _solution/ (เอกสารผู้สอนและเฉลย) ทั้งด้วยเครื่องมืออ่านไฟล์และคำสั่ง shell
3. .claude/settings.json: permissions.deny = ["Edit(e2e-legacy/**)", "Read(/README.md)", "Read(./fast_track/**)", "Read(./_solution/**)"] (กฎ Edit(...) กันเครื่องมือแก้/เขียนไฟล์ของ Claude Code ทุกตัว · Read(/README.md) ขึ้นต้นด้วย / = เฉพาะ README.md ที่รากโฟลเดอร์บท ไม่กัน README ในโฟลเดอร์ย่อย · deny ไม่กันคำสั่ง shell จึงต้องเขียนห้ามใน CLAUDE.md ด้วย)
4. docs/IMPACT-TEMPLATE.md (แม่แบบของ docs/impact/CR-0N.md ทุก CR): คำถามถึงร้าน · ตาราง ไฟล์ที่จะแตะ | เหตุผล (CR) | ใครเรียกใช้ (หลักฐาน grep ไฟล์:บรรทัด) | หน้าจอ/API/แชทที่กระทบ | ตาราง DB | เทสต์ที่ต้องรันซ้ำ | ความเสี่ยง · ค่าที่คาดหวังใหม่พร้อมวิธีคิด · เทสต์ใหม่ที่จะเขียนก่อน (ต้องแดง) · วิธีถอยกลับ
5. docs/ORACLE-CHANGES.md: ตาราง วันที่ | ไฟล์เทสต์ | เคส | ค่าเดิม → ใหม่ | CR ที่อนุญาต | ผู้อนุมัติ (ตอนนี้ยังว่าง)
ไม่แน่ใจข้อไหนให้ถามผมก่อน · เสร็จแล้ว git add -A (รวม HANDOVER-CHECK.md docs/REA-INVENTORY.md SYSTEM-MAP.md docs/SPEC-GAPS.md ที่ยังไม่ได้ commit · rea-out/ ถูก exclude แล้ว) → git status ตรวจว่าไม่มีไฟล์ที่ไม่ควรเข้า → commit "docs: CLAUDE.md + รั้ว"
สรุปเป็นตาราง: ไฟล์ | หัวข้อ | จำนวนบรรทัด
```

💬 **คัดลอกพรอมต์นี้** (ส่วนที่ 2 · **ปิดแล้วเปิดเซสชันใหม่** ก่อนวาง เพื่อให้ settings ใหม่มีผล · เปิดด้วย `claude` ธรรมดา ห้ามใส่ `--dangerously-skip-permissions`)

```text
(รันคำสั่งด้วย PowerShell) ทดสอบรั้วของโปรเจกต์นี้: ลองเพิ่มคอมเมนต์ 1 บรรทัด "// test fence" ที่บรรทัดแรกของ e2e-legacy/playwright.config.ts ด้วยเครื่องมือแก้ไฟล์ปกติ
ห้ามใช้ PowerShell หรือคำสั่ง shell แก้แทน · ถ้าแก้ได้ ให้ลบบรรทัดนั้นคืนทันทีแล้วบอกผมว่ารั้วไม่ทำงาน
รายงานข้อความที่ได้รับจริง แล้วตรวจ git status ว่า e2e-legacy/ ไม่มีไฟล์เปลี่ยน
จากนั้นลองเปิดอ่าน README.md ที่รากโฟลเดอร์นี้ด้วยเครื่องมืออ่านไฟล์ปกติ (ห้ามใช้ shell) · ถ้าอ่านได้ ห้ามสรุปเนื้อหา ให้บอกแค่ว่า "อ่านได้ = รั้วอ่านไม่ทำงาน"
สรุปเป็นตาราง: ทดสอบ | ผล | ข้อความจริง | git status
```

✅ **ผลจริง** <!-- RESULT:LAB4:summary --> ⏳ *ได้ 4 ไฟล์ + commit · จำนวนบรรทัด CLAUDE.md · ผลทดสอบรั้ว (ถูกปฏิเสธไหม) · โหมดสิทธิ์ที่ใช้ทดสอบ · เวลา (~N นาที)*

<!-- RESULT:LAB4:table --> ⏳ *ตาราง ไฟล์ | หัวข้อ | จำนวนบรรทัด + แถวผลทดสอบรั้ว ทดสอบ | ผล | ข้อความจริง | git status*

<!-- RESULT:LAB4:img/lab4-deny-test.png --> ⏳ *ภาพ `img/lab4-deny-test.png` หน้าจอ Claude Code เซสชันใหม่ตอนแก้ `e2e-legacy/playwright.config.ts` แล้วถูกปฏิเสธ กรอบแดงรอบข้อความ (ถ่าย TUI ไม่ได้ให้ทำเป็นภาพตารางจากข้อความใน LAB4_RESULT)*

👀 **สังเกต**
- **กฎ `Edit(...)` กันเครื่องมือแก้/เขียนไฟล์ทุกตัว** ไม่ต้องเขียน `Write(...)` แยก · `Read(...)` กันการเปิดอ่าน · `Read(/README.md)` มี `/` นำหน้า = เฉพาะ README ที่รากบท ไม่กัน README ในโฟลเดอร์ย่อย
- ⚠️ **deny กันเครื่องมือของ Claude แต่ไม่กันคำสั่ง shell** (เช่น `Set-Content` `Get-Content` `sed`) · CLAUDE.md จึงต้องเขียนห้ามเป็นคำพูดด้วย และพรอมต์ส่วนที่ 2 ห้ามใช้ shell แก้แทน · รอบจริงรั้วปฏิเสธทั้งโหมดปกติ (acceptEdits) และ bypass
- **settings ใหม่มีผลในเซสชันใหม่** ทดสอบในเซสชันเดิมอาจได้ผลหลอก
- **CLAUDE.md สั้นดีกว่ายาว** ~60 บรรทัด ลิงก์ไป `SYSTEM-MAP.md` แบบธรรมดา ไม่ใช้ `@` (`@` = โหลดทั้งไฟล์ ~46 KB เข้าทุกเซสชัน) · พรอมต์ CR สั่งให้อ่านเองเมื่อต้องใช้
- **commit นี้รวมไฟล์ของ LAB 1–3** (`git add -A`) ไม่งั้น CLAUDE.md ชี้ไปไฟล์ที่ไม่อยู่ใน repo
- **ไม่ได้ล้อมรั้ว `db/init/`** เพราะกติกาบอกแล้วว่าแก้ได้เฉพาะเพื่อเครื่องติดตั้งใหม่และ reset · รั้วที่แน่นเกินทำให้งานจริงเดินไม่ได้

✔️ **ไปต่อได้เมื่อ:** รั้วปฏิเสธจริงในเซสชันใหม่ และ `git status` ไม่มีไฟล์เปลี่ยนใน `e2e-legacy/` · CLAUDE.md มีคำสั่งรันทุกชุด + ห้าม `down -v` + กติกาป้ายค่าที่คาดหวัง [D:CR-0N] / [E]

---

## LAB 5 · ตาข่ายกันพลาด

🎯 ✏️ ก่อนรับ CR ใด ๆ สร้างตาข่ายชั้นที่ 3 ของเราเอง: **seam เลื่อนนาฬิกา** · **golden master ของ API** · **characterization หน้าจอ + known issue** แล้ว **ทำพังเองเพื่อวัดตาข่าย** → ได้ `web/app/api/test/clock/` · `tests/golden/` · `e2e-cr/` · `KNOWN-ISSUES.md`

![เคาน์เตอร์สปา หุ่นยนต์หมุนปุ่มป้าย นาฬิกาทดสอบ ใต้นาฬิกาแขวน ปฏิทินพลิกหน้าไปข้างหน้า ส่วนกล่องการ์ด จองวันนี้ จองพรุ่งนี้ จองสัปดาห์หน้า บนโต๊ะยังอยู่ที่เดิม หุ่นยนต์พูดว่า ข้อมูลยังอยู่ เด็กชูนิ้วโป้ง คุณจันทร์ยิ้มพนมมือ ป้ายไม้สีทองด้านบน เลื่อนนาฬิกา ไม่ล้างข้อมูล](img/concept-08-test-seam.jpg)

💬 **คัดลอกพรอมต์นี้** (ส่วนที่ 1 · seam + golden master)

```text
สร้างตาข่ายกันพลาดก่อนรับ Change Request (รันคำสั่งด้วย PowerShell · อ่าน CLAUDE.md ก่อน · ห้ามแก้ไฟล์ใน web/lib/rules/ และ web/lib/server/booking.ts · ห้ามแก้ e2e-legacy/ · ห้ามเปิด README.md ของบท fast_track/ และ _solution/)
ส่วน A · test seam: เพิ่ม POST /api/test/clock {"now":"<ISO>"} = เปลี่ยน "วันนี้" ของระบบโดยไม่ล้างข้อมูล
   - ใช้เงื่อนไขเปิด/ปิดเดียวกับ /api/test/reset (ALLOW_TEST_RESET=0 → 404) · แก้แค่ค่า test_today ไม่แตะตารางอื่น
   - rebuild: docker compose -f web/compose.yaml up -d --build --wait (ถ้านานเกิน 2 นาทีให้รันแบบ background แล้วรอ)
   - พิสูจน์: reset → จองนัดใหม่ 1 นัดผ่าน API → เลื่อนนาฬิกา → GET /api/test/today เปลี่ยน · นัดยังอยู่ในตารางคิว
   - พิสูจน์ปิดได้: $env:ALLOW_TEST_RESET="0"; docker compose -f web/compose.yaml up -d --wait → clock ได้ 404 → ตั้งกลับ "1" แล้ว up อีกครั้ง
ส่วน B · golden master ของ API ที่ tests/golden/run.mjs (Node ≥ 22.18 ไม่ใช้ dependency · BASE_URL ค่าเริ่ม http://localhost:4000)
   - reset {"now":"2026-10-10T10:00:00+07:00"} ก่อนทุกกลุ่ม
   - POST /api/price: ผู้ใช้ seed (ไม่ล็อกอิน + U01–U08) × แบบจอง (เดี่ยว คู่ กลุ่ม 3–6 แพ็กเกจ คอร์ส) × แลกแต้ม/ไม่แลก × Gift Card/ไม่ใช้ × รถ (ไม่ใช้ H01 H04 H05) เลือกชุดที่ถูกกฎราว 40–60 เคส (นับเฉพาะ /api/price · slots และตารางคิวนับแยก)
   - GET /api/slots: S01 S02 P01 วันที่ 2026-10-22 และ 2026-10-24
   - ตารางคิวหลังร้าน (ล็อกอิน owner) วันที่ 2026-10-12 ถึง 2026-10-17
   - node tests/golden/run.mjs --update เขียน tests/golden/*.json · ไม่ใส่ --update = เทียบ แล้ว exit 1 ถ้าต่าง พร้อมบอกเคสและฟิลด์ที่ต่าง
   - ตัดฟิลด์ที่เปลี่ยนเองทุกรอบ (id ที่รัน, เวลาสร้าง, cookie) ก่อนเทียบ แล้วเขียนเหตุผลใน tests/golden/README.md
   - รัน --update 1 ครั้ง แล้วรันเทียบอีก 2 ครั้ง ต้องผ่านทั้ง 2 ครั้ง (นิ่ง)
   - tests/golden/README.md ระบุว่าค่าทั้งหมดเป็นป้าย [E] (หลักฐานจากระบบที่รับมอบ = ล็อกพฤติกรรมเดิม ไม่ใช่ตัดสินว่าถูก) พร้อมตาราง ไฟล์ golden | SHA-256 ย่อ 8 ตัว (Get-FileHash) | จำนวนเคส | เวลาที่รัน --update · ใน README อ้างค่าใดให้เขียน [E golden/<ไฟล์>:<sha8>]
ทุกค่าใน golden มาจากการรันระบบที่รับมอบ ห้ามเดาหรือแก้ให้ "ถูก" · เจอค่าที่ดูแปลกให้จดไว้ใน README อย่าแก้
สรุปเป็นตาราง: ส่วน | ไฟล์ | จำนวนเคส | ผล
```

💬 **คัดลอกพรอมต์นี้** (ส่วนที่ 2 · ล็อกหน้าจอ + known issue)

```text
ล็อกหน้าจอสำคัญ และบันทึกพฤติกรรมแปลกเป็น known issue (รันคำสั่งด้วย PowerShell · ห้ามแก้โค้ดใน web/ · ห้ามแก้ e2e-legacy/ · ห้ามเปิด README.md ของบท fast_track/ และ _solution/)
1. สร้างโฟลเดอร์ e2e-cr/ ข้าง web/ (ห้ามสร้างข้างใน web/) = ชุด Playwright ใหม่ของทีม: @playwright/test 1.63.0 · baseURL จาก BASE_URL ค่าเริ่ม http://localhost:4000 · chromium firefox webkit · workers 1 · locale th-TH · timezone Asia/Bangkok · reset ก่อนทุก test · รอ html[data-ready="true"]
   (ดูแนวทางจาก e2e-legacy/playwright.config.ts และ global-setup.ts ได้ แต่ห้ามแก้ของเดิม)
2. e2e-cr/tests/char-booking.spec.ts: ไม่ล็อกอิน จอง S01 วันที่ 12 ต.ค. 15:00 จนถึงหน้าสรุป → ล็อกยอดจาก data-amount และโครงหน้าสรุปด้วย toMatchAriaSnapshot ที่มี /children: equal · ใส่ annotation ป้ายแหล่งของยอด: [E ev_xxxxxxxx] จาก rea-out\scenario.json (ยอดหน้าสรุปที่ REA บันทึกไว้ใน docs/REA-INVENTORY.md) ถ้ายอดที่ล็อกได้ไม่ตรงกับ [E] นั้นให้หยุดบอกผม · เขียน template ของ aria snapshot เองเป็นข้อความตรง (เช่น ยอด "฿1,000") ห้ามใช้ regex ที่ Playwright สร้างให้ (ตัวเลขที่กลายเป็น regex = ไม่ได้ล็อกยอด)
3. ลองของแปลก 3 เรื่อง แล้วเขียน KNOWN-ISSUES.md (อาการ | วิธีทำซ้ำ | หลักฐาน | ผลกระทบ | สถานะ "ยังไม่แก้" | ต้องถามร้านไหม)
   - หน้าจอง: ใส่รหัส Gift Card ที่ไม่มีอยู่ ดูว่ามีข้อความเตือนไหม (เทียบกับคำตอบของ GET /api/giftcards/<รหัส>)
   - จองแบบไม่ล็อกอินด้วยเบอร์โทร "abc"
   - เจ้าของร้าน (owner) ยกเลิกนัดของลูกค้าผ่าน API
   ก่อนตัดสินว่าเป็นบั๊ก ให้เทียบกับ docs/SPEC-GAPS.md (ถ้าเรื่องนั้นยังเป็นคำถามค้างถึงร้าน = "ต้องถามร้าน" ล็อกพฤติกรรมอย่างเดียว ไม่ต้องมี test.fail)
   ข้อที่คิดว่าเป็นบั๊ก: เขียนเทสต์คู่ใน e2e-cr ① ล็อกพฤติกรรมปัจจุบัน ② test.fail() ที่ assert พฤติกรรมที่ควรเป็น + annotation อ้าง KNOWN-ISSUES.md
4. Push-Location e2e-cr; npm install; npx playwright test; Pop-Location (3 เบราว์เซอร์) รัน 2 รอบ ต้องได้ผลเท่ากันทั้ง 2 รอบ (บรรทัดสรุปนับ test.fail ที่ล้มตามคาดรวมใน passed ให้แยกนับในตาราง)
ห้ามแก้บั๊กที่เจอ (ยังไม่มี CR สั่ง) · ไม่แน่ใจว่าบั๊กหรือตั้งใจ ให้เขียน "ต้องถามร้าน"
สรุปเป็นตาราง: test | chromium | firefox | webkit | รอบ 1 = รอบ 2 ไหม | known issue
```

![หุ่นยนต์ใส่แว่นนิรภัยใช้ไขควงคลายน็อตป้าย 1 บรรทัด บนเครื่องป้าย กฎร้าน กระดิ่งแดงป้าย ตาข่าย ดังขึ้น เด็กเขียน จับได้ บนคลิปบอร์ด อีกด้านมีน็อตหลวมอีกตัวกับกระดิ่งเทาหน้าเศร้าป้าย รอด = มีรู คุณจันทร์ยิ้มพนมมือ ป้ายไม้สีทองด้านบน ทำพังเองเพื่อวัดตาข่าย](img/concept-09-mutation.jpg)

💬 **คัดลอกพรอมต์นี้** (ส่วนที่ 3 · ทำพังเองเพื่อวัดตาข่าย)

```text
วัดว่าตาข่ายจับการพังได้จริงไหม (mutation testing แบบมือ · รันคำสั่งด้วย PowerShell จากโฟลเดอร์บท) · ทำทีละตัว และต้องคืนไฟล์ทุกครั้ง (ห้าม commit โค้ดที่ทำพัง · ห้ามเปิด README.md ของบท fast_track/ และ _solution/)
ตัวทำพัง 3 ตัว แก้ตัวละ 1 บรรทัด:
  X1 web/lib/rules/tier.ts: spend >= GOLD_MIN → spend > GOLD_MIN
  X2 web/lib/rules/transport.ts: SEATS_PER_VEHICLE = 4 → 5
  X3 web/lib/rules/pricing.ts: GROUP_PCT = 10 → 15
ต่อ 1 ตัว: แก้ → docker compose -f web/compose.yaml up -d --build --wait (golden ยิง API จึงต้อง rebuild ทุกตัว) → node tests/golden/run.mjs → node web/scripts/check-rules.mjs → Push-Location e2e-cr; npx playwright test --project=chromium; Pop-Location (chromium อย่างเดียวพอ) → จดว่าชุดไหนจับได้ → คืนไฟล์ด้วย git checkout -- <ไฟล์> → git status ต้องสะอาดในไฟล์นั้น
จบครบ 3 ตัวแล้ว rebuild โค้ดปกติ แล้วรัน golden ต้องผ่าน
ตัวที่ไม่มีชุดไหนจับได้ (รอด): อธิบายว่าตาข่ายมีรูตรงไหน แล้วเสนอเคสที่จะอุดรู (ยังไม่ต้องเขียน) ลง tests/golden/README.md
ถ้าคืนไฟล์ไม่ได้หรือ rebuild ล้ม ให้หยุดแล้วบอกผม
เสร็จแล้ว git add tests e2e-cr KNOWN-ISSUES.md web → git status ตรวจว่าไฟล์ครบ (tests/golden/README.md และ tests/golden/*.json ต้องอยู่ในรายการที่จะ commit) → commit "safety-net: seam + golden + characterization"
สรุปเป็นตาราง: ตัวทำพัง | golden | check-rules | e2e-cr | ถูกจับ / รอด
```

✅ **ผลจริง** <!-- RESULT:LAB5:summary --> ⏳ *seam ปิดได้ (404) · golden กี่เคส นิ่ง x/2 รอบ · e2e-cr กี่ test × 3 เบราว์เซอร์ รอบ 1 = รอบ 2 · known issue 3 เรื่อง · mutant ถูกจับ x/3 · เวลาแยกส่วน (~N นาที)*

<!-- RESULT:LAB5:table-golden --> ⏳ *ตาราง กลุ่ม | เคส | รอบ update | รอบเทียบ 1 | รอบเทียบ 2 (price · slots · ตารางคิว) + SHA-256 ย่อของไฟล์ golden*

<!-- RESULT:LAB5:img/lab5-golden.png --> ⏳ *ภาพ `img/lab5-golden.png` ตาราง golden จาก LAB5_RESULT + บรรทัดสรุปจำนวนเคสและเวลา*

<!-- RESULT:LAB5:table-mutants --> ⏳ *ตาราง ตัวทำพัง | golden | check-rules | e2e-cr | ถูกจับ / รอด (X1–X3 จากรอบจริง)*

<!-- RESULT:LAB5:img/lab5-mutants.png --> ⏳ *ภาพ `img/lab5-mutants.png` ตาราง mutant X1–X3 ช่องที่รอดสีเหลือง*

👀 **สังเกต**
- **characterization ล็อก "ระบบทำอะไรอยู่" รวมบั๊กด้วย** ข้อที่คิดว่าเป็นบั๊กจึงล็อกคู่: ค่าปัจจุบัน + `test.fail()` ของค่าที่ควรเป็น · ยังไม่มี CR = ยังไม่แก้
- **aria snapshot ที่ Playwright สร้างให้แปลงตัวเลขเป็น regex** (`/฿\d+,\d+/`) = ไม่ได้ล็อกยอด · รอบจริงต้องเขียน template เองเป็นข้อความตรง และอ่านยอดจาก `data-amount` อีกชั้น
- **golden ต้องตัดฟิลด์ที่เปลี่ยนเองทุกรอบ** (id · เวลาสร้าง · cookie) ไม่งั้นแดงเองแม้ไม่มีใครแก้อะไร · รันเทียบ 2 รอบติดคือวิธีพิสูจน์ว่านิ่ง
- ⚠️ **`--update` ห้ามรันโดยไม่อ่านว่าค่าไหนเปลี่ยน** = อบพฤติกรรมใหม่ (ที่อาจผิด) ลง golden
- **mutant รอด = ตาข่ายมีรู ไม่ใช่ความล้มเหลวของเรา** · จดเคสที่จะอุดรูไว้ · และคืนไฟล์ทุกตัว (`git status` ต้องสะอาดก่อน commit) · รอบจริง 3 ตัวถูก golden + check-rules จับหมด แต่ e2e-cr ไม่จับเลย = ตาข่ายหน้าจอบาง
- **known issue ที่ยังเป็นคำถามค้างใน SPEC-GAPS = ต้องถามร้าน** ล็อกพฤติกรรมอย่างเดียว ไม่ต้องมี `test.fail()` · และดู `git status` ก่อน commit ว่าไฟล์ครบ (`tests/golden/README.md` · `*.json`)

✔️ **ไปต่อได้เมื่อ:** golden ผ่าน 2 รอบติด · e2e-cr ผลเท่ากัน 2 รอบ × 3 เบราว์เซอร์ · `git status` สะอาดหลังคืน mutant · มี `KNOWN-ISSUES.md` 3 เรื่อง · มี commit "safety-net"

---

## LAB 6 · CR-02 เปลี่ยนกฎ (วันมีผล)

🎯 ✏️ CR แรก: **เปลี่ยนกฎส่วนลดกลุ่มที่มีวันมีผล** · อธิบายการคิดราคาเดิมก่อน · ทำ impact · คำนวณค่าที่คาดหวังเอง · เทสต์แดงก่อนแก้ · `check-rules.mjs` ต้อง **diff ว่าง** → ได้ `docs/impact/CR-02.md` · `tests/cr02.mjs` · commit แดง → แก้

![ปฏิทินใหญ่ 2 แผ่น 31 ต.ค. กับ 1 พ.ย. หน้าแต่ละแผ่นมีลูกค้าผู้หญิงกลุ่มละ 3 คน ป้ายราคาใต้แผ่นแรก ฿3,000 ใต้แผ่นที่สอง ฿2,850 นาฬิกาตรงกลางชี้เที่ยงคืน หุ่นยนต์ชี้เส้นแบ่งพูดว่า นับวันที่จอง เด็กกับคุณจันทร์ยืนสองข้าง ป้ายไม้สีทองด้านบน กฎใหม่มีผล 1 พ.ย.](img/concept-19-effective-date.jpg)

LAB 6–10 ใช้จังหวะเดียวกัน: **ส่วนที่ 1 วางใน Plan mode** (กด `Shift+Tab` จนขึ้น plan mode ก่อนวาง) → อ่านแผนและค่าที่คาดหวัง → **สลับกลับโหมดปกติ** แล้ววางส่วนที่ 2 ในเซสชันเดียวกัน · **Plan mode เขียนไฟล์ไม่ได้**: คำถามและ impact จึงอยู่ในแผนก่อน · กดอนุมัติแผน = ออกจาก Plan mode แล้ว Claude บันทึก `docs/impact/CR-0N.md` แล้วหยุดรอส่วนที่ 2

💬 **คัดลอกพรอมต์นี้** (ส่วนที่ 1 · วิเคราะห์ใน Plan mode)

```text
วิเคราะห์ CHANGE-REQUESTS/CR-02.md ก่อนแก้ (รันคำสั่งด้วย PowerShell · ยังห้ามแก้โค้ด · อ่าน CLAUDE.md และ SYSTEM-MAP.md ก่อน · ห้ามเปิด README.md ของบท fast_track/ และ _solution/ · Plan mode เขียนไฟล์ไม่ได้ ทุกอย่างให้อยู่ในแชทและแผน)
1. สรุปคำขอเป็นภาษาคน 3–5 ข้อ แล้วแสดง "คำถามถึงร้าน" ทุกเรื่องที่ยังไม่ชัดในแชท
1.5 อธิบายของเดิมก่อนแก้ (อ้างไฟล์:บรรทัด): ระบบคิดส่วนลดกลุ่มและเลือกส่วนลดที่มากที่สุดอย่างไร (bestPercent / calcPrice / buildQuote) · ใครเรียกฟังก์ชันเหล่านี้บ้าง · "วันนี้ของระบบ" ที่ใช้ตอนคิดราคามาจากไหน
2. แสดงคำถามเสร็จแล้วค่อยเปิด CHANGE-REQUESTS/answers/CR-02-ANSWERS.md · บอกว่าคำถามไหนได้คำตอบ ข้อไหนยังค้าง (ข้อค้างให้ใช้สมมติฐานที่ระบุชัด ติด ⚠️)
3. เนื้อหา impact (จะบันทึกเป็น docs/impact/CR-02.md) ตาม docs/IMPACT-TEMPLATE.md · ทุกแถวมีหลักฐาน grep (ไฟล์:บรรทัด) · ต้องครอบ: ฟังก์ชันราคา · ผู้เรียกทุกตัว (รวมแชท) · unit test ใน web/scripts/check-rules.mjs ที่เรียกฟังก์ชันราคาตรง · ข้อความ i18n · หน้าจอ
4. คำนวณค่าที่คาดหวังเองจากกฎใหม่ (แสดงวิธีคิด ฿ − % =) อย่างน้อย 8 เคส: กลุ่ม 2/3/4/5/6/7 คน · ขอบวันมีผล (31 ต.ค. 23:59 กับ 1 พ.ย. 00:00) · ส่วนลดกลุ่มเท่ากับส่วนลดสมาชิก · แพ็กเกจ · นัดที่จองก่อนวันมีผลแต่วันนัดอยู่หลัง · เคสที่ยอดเท่าเดิมแต่ชนิดส่วนลดเปลี่ยน (เช่น Gold กลุ่ม 3) ต้องตรวจ discountKind ด้วย ไม่ใช่แค่ยอด · ทุกแถวติดป้ายแหล่ง: [D:CR-02] = ตรงกับตัวอย่าง/กฎที่ร้านยืนยัน · [E golden/<ไฟล์>:<sha8>] = ค่าเดิมที่ต้องไม่เปลี่ยน (ก่อนวันมีผล) · ถ้า [E] ขัดกับ [D:CR-02] ให้เขียนว่า "ผู้ต้องสงสัยบั๊ก" แล้วถามผม ห้ามใช้ [E] นั้นเป็นค่าคาดหวัง
5. เสนอแผนแก้ทีละขั้น + รายการเทสต์ใหม่ที่จะเขียนก่อน (ต้องแดงบนโค้ดเดิม) แล้วรอผมอนุมัติ · หลังผมอนุมัติ (ออกจาก Plan mode) ให้บันทึกเนื้อหา impact ทั้งหมดเป็น docs/impact/CR-02.md อย่างเดียวแล้วหยุด รอพรอมต์ถัดไป
สรุปเป็นตาราง: ไฟล์ที่จะแตะ | เหตุผล | เทสต์ที่ต้องรันซ้ำ | ความเสี่ยง
```

💬 **คัดลอกพรอมต์นี้** (ส่วนที่ 2 · ลงมือในโหมดปกติ)

```text
ทำ CR-02 ตามแผนใน docs/impact/CR-02.md (รันคำสั่งด้วย PowerShell · อ่าน CLAUDE.md ก่อน · ห้ามแก้ e2e-legacy/ · ห้ามแก้ค่าที่คาดหวังเดิมใน web/scripts/check-rules.mjs และ tests/golden/ · ห้ามเปิด README.md ของบท fast_track/ และ _solution/)
0. ถ้ายังไม่มี docs/impact/CR-02.md ให้บันทึกจากแผนที่ผมอนุมัติก่อน
1. เทสต์ก่อน: tests/cr02.mjs (Node ไม่ใช้ dependency · reset เอง · คุม "วันที่จอง" ด้วย reset {now} หรือ POST /api/test/clock) ใส่ทุกเคสจากข้อ 4 ของ impact
   รันบนโค้ดเดิม → เคสอัตราใหม่ต้องแดง · บันทึกผลแดงลง docs/impact/CR-02.md → git add tests/cr02.mjs docs/impact/CR-02.md → git commit "CR-02 test: แดงก่อนแก้"
2. แก้โค้ดให้เล็กที่สุดตามแผน · อัตราส่วนลดอยู่จุดเดียว ไม่ hardcode ซ้ำ · ค่าเริ่มของพารามิเตอร์ใหม่ต้องให้ผลเหมือนเดิม · rebuild web
3. เขียว: node tests/cr02.mjs ผ่านทุกเคส
4. Regression (จากโฟลเดอร์บท): node web/scripts/check-rules.mjs (ต้องผ่านเท่าเดิม และ git diff web/scripts/check-rules.mjs ต้องว่าง) · node tests/golden/run.mjs · Push-Location e2e-cr; npx playwright test --project=chromium; Pop-Location · Push-Location e2e-legacy; npx playwright test; Pop-Location (ค่าเริ่ม api + chromium · 3 เบราว์เซอร์รอบเต็มทำตอนส่งมอบ)
5. ข้อไหนแดงที่ไม่ได้ตั้งใจ ให้หยุดแล้วบอกผมว่าเป็น เว็บผิด / เทสต์เก่าล้าสมัย / เทสต์ใหม่เขียนผิด · ห้ามแก้เทสต์ให้ผ่านเฉย ๆ
6. เอกสาร: อัปเดต web/SPEC.md เฉพาะกฎส่วนลดกลุ่ม + บรรทัดประวัติแก้ไข · docs/TRACEABILITY.md (สร้างถ้ายังไม่มี) แถว CR-02 → BR-06 (ข้อความกฎใหม่) → TC ทุกตัวที่พิสูจน์ (ใหม่ + regression) → ผล · CHANGE-REPORT.md ส่วน CR-02: ไฟล์ที่แก้ (git diff --stat) · แดง→เขียว · regression · พฤติกรรมที่เปลี่ยนโดยตั้งใจ · ความเสี่ยงคงค้าง · วิธีถอยกลับ
7. อัปเดตสถานะใน CHANGE-REQUESTS/REGISTER.md ก่อน (สถานะ + hash ของ commit แดง) → git add -A → git status ตรวจไฟล์ → git commit "CR-02: ส่วนลดกลุ่มขั้นบันได มีผล 1 พ.ย. 2026"
สรุปเป็นตาราง: ชุดทดสอบ | ก่อนแก้ | หลังแก้ | หมายเหตุ
```

![ภาพ 2 ช่อง ช่องซ้ายไฟจราจรติดแดง หุ่นยนต์เขียนการ์ด เทสต์ใหม่ = แดง คุณจันทร์ยืนพนมมือ ช่องขวาไฟเปลี่ยนเป็นเขียวหลังหุ่นยนต์ใช้ประแจขันน็อตป้าย แก้ เด็กชูกำปั้นถือป้าย แดงก่อน แล้วค่อยแก้ ป้ายไม้สีทองด้านบน เทสต์แดงก่อนแก้](img/concept-11-red-first.jpg)

✅ **ผลจริง** <!-- RESULT:LAB6:summary --> ⏳ *ได้ `docs/impact/CR-02.md` + `tests/cr02.mjs` · กี่เคส แดงกี่ → เขียวกี่ · `git diff web/scripts/check-rules.mjs` ว่างไหม · regression · commit 2 ตัว · เวลา (~N นาที)*

<!-- RESULT:LAB6:table-cases --> ⏳ *ตาราง เคส | ค่าที่คาดหวัง (วิธีคิด ฿ − % =) | ป้าย [D:CR-02] / [E golden…] | ก่อนแก้ | หลังแก้ 3–6 แถวเด่น*

<!-- RESULT:LAB6:img/lab6-red-green.png --> ⏳ *ภาพ `img/lab6-red-green.png` ตาราง ชุดทดสอบ | ก่อนแก้ | หลังแก้ (cr02 · check-rules · golden · e2e-cr · e2e-legacy) + บรรทัด "git diff check-rules.mjs = ว่าง"*

👀 **สังเกต**
- **"วันที่จอง" ≠ "วันนัด"** อ่านคำตอบร้านให้ชัดว่ากฎใหม่ผูกกับวันไหน · ขอบวันมีผลต้องทดสอบทั้งสองฝั่ง
- **พารามิเตอร์ใหม่ต้องมีค่าเริ่มที่ให้ผลเหมือนเดิม** · ชุดตรวจเดิมบางข้อเรียกฟังก์ชันราคาตรง ไม่ผ่าน API · ค่าเริ่มเปลี่ยน = ของเดิมพังเงียบ ๆ
- **ราคาที่เห็นตอนสรุปกับตอนกดยืนยันอาจคิดคนละวัน** (ข้ามเที่ยงคืน) · ดูว่าระบบเดิมจัดการเรื่องนี้ไว้อย่างไรก่อนแก้
- **ค่าที่คาดหวังเดิมห้ามขยับ** ถ้าเทสต์เดิมต้องเปลี่ยนจริง = หยุดถาม + จดใน `docs/ORACLE-CHANGES.md` · diff ว่าง = หลักฐานว่าไม่ได้ "แก้เทสต์ให้ผ่าน"
- **[E] ขัด [D:CR-02] = ผู้ต้องสงสัยบั๊ก** ไม่ใช่ค่าที่คาดหวัง
- **ยอดเท่าเดิมไม่ได้แปลว่าไม่เปลี่ยน** Gold กลุ่ม 3 ได้ ฿2,850 ทั้งก่อนและหลัง แต่ชนิดส่วนลดเปลี่ยน · ตรวจ `discountKind` ด้วย ไม่งั้นเทสต์เขียวตั้งแต่ก่อนแก้

✔️ **ไปต่อได้เมื่อ:** `tests/cr02.mjs` เขียวทุกเคส · commit แดงมาก่อน commit แก้ · `git diff web/scripts/check-rules.mjs` ว่าง · regression ไม่มีแดงใหม่ · มีแถว CR-02 ใน `docs/TRACEABILITY.md` และ `REGISTER.md`

---

## LAB 7 · CR-03 แก้บั๊กจากเรื่องร้องเรียน

🎯 ✏️ **ทำซ้ำเรื่องร้องเรียนให้แดงก่อน** · หาต้นเหตุด้วย `file:line` · แก้ฝั่งเซิร์ฟเวอร์ให้ครอบทุกช่องทาง (หน้าเว็บ · API · แชท · กดพร้อมกัน) → ได้ `docs/impact/CR-03.md` · `tests/cr03.mjs` · `e2e-cr/tests/cr03.spec.ts`

![ล็อบบี้สปา ลูกค้าชายวัยกลางคนใส่แว่นเสื้อลายทางนั่งโซฟา กดปุ่ม จอง บนโทรศัพท์ที่สัญญาณ Wi-Fi อ่อน ตั๋ว จอง 2 ใบลอยออกมา หุ่นยนต์รับตั๋วใบที่สองด้วยแม่กุญแจทองป้าย ล็อกก่อนจอง พูดว่า มีนัดแล้ว เด็กถือการ์ดเบอร์ 081-000-0003 คุณจันทร์ยืนไหว้หลังเคาน์เตอร์ ป้ายไม้สีทองด้านบน คนเดียวกัน เวลาทับ = ซ้ำ](img/concept-20-double-tap.jpg)

💬 **คัดลอกพรอมต์นี้** (ส่วนที่ 1 · วิเคราะห์ใน Plan mode)

```text
วิเคราะห์ CHANGE-REQUESTS/CR-03.md (เรื่องร้องเรียน) ก่อนแก้ (รันคำสั่งด้วย PowerShell · ยังห้ามแก้โค้ด · อ่าน CLAUDE.md และ SYSTEM-MAP.md ก่อน · ห้ามเปิด README.md ของบท fast_track/ และ _solution/ · Plan mode เขียนไฟล์ไม่ได้ ทุกอย่างให้อยู่ในแชทและแผน)
1. ทำซ้ำเรื่องร้องเรียนก่อน: reset แล้วยิง POST /api/bookings แบบไม่ล็อกอินด้วยข้อมูลเดียวกับนัดของคุณสมชาย (เบอร์ 081-000-0003 · 13 ต.ค. 10:00 · บริการเดียวกับนัดเดิม) ด้วยสคริปต์ node (ชื่อภาษาไทยใน body) · ลองเขียนเบอร์แบบไม่มีขีดด้วย · จดสถานะและรหัสนัดที่ได้
2. แสดง "คำถามถึงร้าน" ในแชทก่อน แล้วค่อยเปิด CHANGE-REQUESTS/answers/CR-03-ANSWERS.md · บอกข้อที่ได้คำตอบ/ยังค้าง
3. หาต้นเหตุ: ไล่การสร้างนัดตั้งแต่ API → service → DB constraint · อธิบายว่าทำไมชุดตรวจที่ส่งมอบไม่จับเรื่องนี้ และทำไมหน้าเว็บกดสองครั้งไม่ซ้ำแต่ API/แชทซ้ำได้ (อ้างไฟล์:บรรทัด)
4. เนื้อหา impact (จะบันทึกเป็น docs/impact/CR-03.md) ตาม docs/IMPACT-TEMPLATE.md · ต้องครอบ: ทุกช่องทางที่สร้างนัด (หน้าเว็บ แชท) · การกดพร้อมกัน 2 คำขอ (สมาชิก และไม่ล็อกอิน) · เทสต์เดิมที่ยิงคำขอพร้อมกันคนละคนต้องยังได้ผลเดิม · เทสต์เดิมที่จองทับนัด seed ด้วยบัญชีหรือเบอร์ของเจ้าของนัดเอง (ไล่ใน e2e-legacy/tests และ web/scripts/check-rules.mjs) → กำหนดลำดับ error เมื่อคำขอเข้าทั้ง "คิวเต็ม" และ "นัดซ้ำ" พร้อมกัน ให้เทสต์เดิมได้ผลเดิม · ข้อความ 3 ภาษา
5. ค่าที่คาดหวังใหม่อย่างน้อย 8 เคส (ซ้ำ · ต่อกันพอดี · คนละเบอร์ · สมาชิก · ยกเลิกแล้วจองใหม่ · คู่ทับเดี่ยว · พร้อมกัน · แชท) · ทุกแถวติดป้าย [D:CR-03] หรือ [E …] · ผลที่ได้จากข้อ 1 (201 ซ้ำได้) คือ [E] ที่ขัด [D:CR-03] = หลักฐานบั๊ก ห้ามนำไปเป็นค่าคาดหวัง · เสนอแผนแล้วรอผมอนุมัติ · หลังผมอนุมัติ (ออกจาก Plan mode) ให้บันทึกเนื้อหา impact ทั้งหมดเป็น docs/impact/CR-03.md อย่างเดียวแล้วหยุด รอพรอมต์ถัดไป
สรุปเป็นตาราง: ไฟล์ที่จะแตะ | เหตุผล | เทสต์ที่ต้องรันซ้ำ | ความเสี่ยง
```

💬 **คัดลอกพรอมต์นี้** (ส่วนที่ 2 · ลงมือในโหมดปกติ)

```text
แก้ CR-03 ตาม docs/impact/CR-03.md (รันคำสั่งด้วย PowerShell · อ่าน CLAUDE.md ก่อน · ห้ามแก้ e2e-legacy/ · ห้ามแก้ค่าที่คาดหวังเดิมใน web/scripts/check-rules.mjs และ tests/golden/ · ห้ามเปิด README.md ของบท fast_track/ และ _solution/)
0. ถ้ายังไม่มี docs/impact/CR-03.md ให้บันทึกจากแผนที่ผมอนุมัติก่อน
1. เทสต์ที่ทำซ้ำเรื่องร้องเรียนก่อน: tests/cr03.mjs ทุกเคสจาก impact (กดพร้อมกันใช้ Promise.all 2 คำขอ) + e2e-cr/tests/cr03.spec.ts (ขั้นยืนยันในหน้าจองแสดง book-error ที่มี data-error-code="DUPLICATE_BOOKING" และรหัสนัดเดิม)
   รันบนโค้ดเดิม → ต้องแดง (เคสเรื่องร้องเรียนได้ 201) · เก็บ log ผลแดง → git add tests/cr03.mjs e2e-cr/tests/cr03.spec.ts docs/impact/CR-03.md → git commit "CR-03 test: ทำซ้ำเรื่องร้องเรียน (แดง)"
2. แก้ฝั่งเซิร์ฟเวอร์ให้เล็กที่สุด: ตรวจตอนสร้างนัด (ไม่ใช่แค่ปิดปุ่ม) · normalize เบอร์เหลือตัวเลข · กันคำขอพร้อมกันทั้งสมาชิกและไม่ล็อกอิน · ลำดับล็อกคงที่ (กัน deadlock) · ข้อความ 3 ภาษา · rebuild web
3. เขียว: node tests/cr03.mjs และ Push-Location e2e-cr; npx playwright test tests/cr03.spec.ts --project=chromium; Pop-Location (CR LAB รัน chromium · 3 เบราว์เซอร์รอบเต็มทำตอนส่งมอบ) · ถามแชทจองซ้ำด้วยภาษาไทยและจีนด้วยสคริปต์ node (POST /api/chat · ห้ามส่งข้อความไทย/จีนผ่าน Invoke-RestMethod · แชทต้องคุยครบ 5 ข้อความ ขอจอง → วัน → เวลา → ชื่อ+เบอร์ → ยืนยัน และส่ง state ที่ได้กลับไปทุกครั้ง) แล้วตรวจว่าคำตอบมีข้อความตามภาษาและรหัสนัดเดิม · ภาษาของ error จาก API มาจาก cookie lang ไม่ใช่ lang ใน body (เทสต์ข้อความ en/zh ของ API ต้องส่ง cookie)
4. Regression (จากโฟลเดอร์บท): node web/scripts/check-rules.mjs (diff ว่าง) · node tests/golden/run.mjs · node tests/cr02.mjs · Push-Location e2e-cr; npx playwright test --project=chromium; Pop-Location · Push-Location e2e-legacy; npx playwright test; Pop-Location (api + chromium) · ดูให้แน่ว่าเทสต์จองพร้อมกันคนละคนยังได้ SLOT_TAKEN
5. แดงที่ไม่ได้ตั้งใจ → หยุดบอกผม (เว็บผิด / เทสต์เก่าล้าสมัย / เทสต์ใหม่เขียนผิด) ห้ามแก้เทสต์ให้ผ่าน
6. เอกสาร: web/SPEC.md (กฎใหม่ BR-21 + error ใหม่) · docs/TRACEABILITY.md แถว CR-03 → BR-21 → TC → ผล · CHANGE-REPORT.md ส่วน CR-03 (ต้นเหตุ ไฟล์:บรรทัด · ทำไมชุดเดิมไม่จับ) · อัปเดต REGISTER.md (สถานะ + hash commit แดง) → git add -A → git status → git commit "CR-03: กันจองซ้ำของคนเดียวกัน"
สรุปเป็นตาราง: เคส | ก่อนแก้ | หลังแก้ | ช่องทาง
```

✅ **ผลจริง** <!-- RESULT:LAB7:summary --> ⏳ *ผลทำซ้ำเรื่องร้องเรียนก่อนแก้ (สถานะ · รหัสนัดที่ได้) · cr03 กี่เคส แดง → เขียว · cr03.spec 3 เบราว์เซอร์ · แชทไทย/จีน · regression · เวลา (~N นาที)*

<!-- RESULT:LAB7:table --> ⏳ *ตาราง เคส | ก่อนแก้ | หลังแก้ | ช่องทาง 4–6 แถวเด่น (เรื่องร้องเรียน · ต่อกันพอดี · กดพร้อมกัน · แชท · เทสต์เดิมที่จองพร้อมกันคนละคน)*

<!-- RESULT:LAB7:img/lab7-duplicate-error.png --> ⏳ *ภาพ `img/lab7-duplicate-error.png` หน้า `/book` ขั้นยืนยันหลังแก้ แสดง `book-error` ข้อความนัดซ้ำพร้อมรหัสนัดเดิม วงแดงรอบข้อความ*

<!-- RESULT:LAB7:img/gif-TC-CR03-11.gif --> ⏳ *GIF `img/gif-TC-CR03-11.gif` หัวเรื่อง "🎬 TC-CR03-11 …" (วงแดง = จุดที่ Playwright คลิก · ป้ายมุมซ้ายล่าง = ชื่อ test) จาก Playwright chromium รอบจริง*

👀 **สังเกต**
- **ผลตอนทำซ้ำเรื่องร้องเรียนคือ [E] ที่ขัด [D:CR-03]** = หลักฐานบั๊ก · ห้ามเอาไปเป็นค่าที่คาดหวัง
- **ปิดปุ่มบนหน้าเว็บอย่างเดียวไม่พอ** API และแชทสร้างนัดได้โดยไม่ผ่านปุ่ม · การกันต้องอยู่ที่เซิร์ฟเวอร์ตอนสร้างนัด
- **กดพร้อมกัน "คนละคน" ต้องยังได้ผลเดิม** · กติกาใหม่ห้ามไปเปลี่ยน error ของกรณีที่ไม่เกี่ยวกับ CR
- **ลำดับการล็อกต้องคงที่** ไม่งั้นสองคำขอรอกันเอง (deadlock)
- ⚠️ **ข้อความไทย/จีนส่งผ่าน API ด้วยสคริปต์ node** ไม่ใช่ `Invoke-RestMethod -Body` ของ PowerShell 5.1 · ภาษาของ error มาจาก cookie `lang` ไม่ใช่ `lang` ใน body
- **ชุดเทสต์เดิมจับ regression ได้จริง** รอบจริงแก้ครั้งแรกแล้ว TC-BOOK-07 (สมาชิกจองทับนัดของตัวเองตอนคิวเต็ม) แดง เพราะตรวจ "นัดซ้ำ" ก่อน "คิวเต็ม" · แก้ที่ลำดับการตรวจในโค้ด ไม่แก้เทสต์ · กฎใหม่ที่เพิ่มเงื่อนไขปฏิเสธต้องคิดลำดับ error เสมอ

✔️ **ไปต่อได้เมื่อ:** commit เทสต์แดงมาก่อน commit แก้ · `tests/cr03.mjs` เขียว · `cr03.spec.ts` เขียว (chromium) · e2e-legacy (api + chromium) เท่า baseline · มีแถว CR-03 ใน TRACEABILITY และ REGISTER

---

## LAB 8 · CR-04 migration วันหยุดร้าน

🎯 ✏️ เพิ่มตารางใหม่ **บนฐานข้อมูลที่มีข้อมูลลูกค้าอยู่แล้ว**: migration แยกไฟล์ที่รันซ้ำได้ + ไฟล์ถอยกลับ · ซ้อมบนฐานที่มีนัดจริง · เครื่องติดตั้งใหม่และ reset ต้องยังใช้ได้ → ได้ `db/migrations/001_shop_holiday.sql` (+ `.down.sql`) · `tests/cr04.mjs` · `docs/MIGRATION-RUNBOOK.md`

![ตู้เอกสารสูงเต็มแฟ้มลูกค้าเปิดอยู่ หุ่นยนต์ดึงลิ้นชักใหม่ป้าย shop_holiday และกดปุ่ม migration พูดว่า รันซ้ำได้ เด็กกำมือดีใจ คุณจันทร์ยิ้มพนมมือ น้องบัวชูป้ายหยุดสีแดงกันรถดันดินป้าย down -v ป้ายไม้สีทองด้านบน เพิ่มได้ ห้ามล้าง](img/concept-13-live-db-migration.jpg)

💬 **คัดลอกพรอมต์นี้** (ส่วนที่ 1 · วิเคราะห์ใน Plan mode)

```text
วิเคราะห์ CHANGE-REQUESTS/CR-04.md ก่อนแก้ (รันคำสั่งด้วย PowerShell · ยังห้ามแก้โค้ด · อ่าน CLAUDE.md และ SYSTEM-MAP.md ก่อน · ห้ามเปิด README.md ของบท fast_track/ และ _solution/ · Plan mode เขียนไฟล์ไม่ได้ ทุกอย่างให้อยู่ในแชทและแผน)
หนังสือบอกว่าระบบใช้งานจริงอยู่ ข้อมูลลูกค้าและนัดห้ามหาย
1. แสดง "คำถามถึงร้าน" ในแชทก่อน แล้วค่อยเปิด CHANGE-REQUESTS/answers/CR-04-ANSWERS.md · ตัดสินว่ารอบนี้ทำส่วน ข (หลังร้าน) ไหม ให้ถามผมก่อน
2. ตอบด้วยหลักฐานจาก repo (ไฟล์:บรรทัด): ถ้าเพิ่มตารางใน db/init/01-schema.sql อย่างเดียว ฐานข้อมูลที่รันอยู่จะได้ตารางไหม เพราะอะไร · ข้อมูลทดสอบของ reset มาจากไฟล์ไหน เข้าไปใน image ตอนไหน · reset ล้างตารางอะไรบ้าง ถ้ามีตารางใหม่ต้องแก้ที่ไหน
3. ออกแบบ: ตารางใหม่ · migration ไฟล์แยก db/migrations/001_shop_holiday.sql ที่รันซ้ำได้ + 001_shop_holiday.down.sql · สิ่งที่ต้องแก้สำหรับเครื่องที่ติดตั้งใหม่ · สิ่งที่ต้องแก้ให้ reset ยังผ่าน · ทุกช่องทางที่จองได้ (หน้าเว็บ ราคา จอง คอร์ส แชท) · ลำดับ error เมื่อวันที่เกินช่วงจองและเป็นวันหยุดพร้อมกัน
4. เนื้อหา impact (จะบันทึกเป็น docs/impact/CR-04.md) ตาม docs/IMPACT-TEMPLATE.md + ค่าที่คาดหวังใหม่อย่างน้อย 8 เคส (ติดป้าย [D:CR-04] หรือ [E …] ทุกแถว) + ขั้นตอนซ้อมบนฐานที่มีข้อมูล + ลำดับ deploy (migration ก่อน rebuild เว็บ) และลำดับถอย (เว็บก่อน down.sql) พร้อมเหตุผล + วิธีถอยกลับ (ข้อมูลอะไรหายบ้างถ้าถอย)
5. เสนอแผนแล้วรอผมอนุมัติ · หลังผมอนุมัติ (ออกจาก Plan mode) ให้บันทึกเนื้อหา impact ทั้งหมดเป็น docs/impact/CR-04.md อย่างเดียวแล้วหยุด รอพรอมต์ถัดไป
สรุปเป็นตาราง: ไฟล์/ตารางที่จะแตะ | เหตุผล | เทสต์ที่ต้องรันซ้ำ | ความเสี่ยง
```

💬 **คัดลอกพรอมต์นี้** (ส่วนที่ 2 · ลงมือส่วน ก ในโหมดปกติ) ☕

```text
ทำ CR-04 ส่วน ก ตาม docs/impact/CR-04.md (รันคำสั่งด้วย PowerShell · อ่าน CLAUDE.md ก่อน · ห้าม docker compose down -v · ห้ามลบ volume · ห้ามแก้ e2e-legacy/ · ห้ามแก้ค่าที่คาดหวังเดิม · ห้ามเปิด README.md ของบท fast_track/ และ _solution/)
0. ถ้ายังไม่มี docs/impact/CR-04.md ให้บันทึกจากแผนที่ผมอนุมัติก่อน
1. เทสต์ก่อน: tests/cr04.mjs (ทุกเคสใน impact) → รันบนโค้ดเดิมต้องแดง → git add tests/cr04.mjs docs/impact/CR-04.md (+ e2e-cr/tests/cr04.spec.ts ถ้าเขียนแล้ว) → git commit "CR-04 test: แดงก่อนแก้"
2. เขียน db/migrations/001_shop_holiday.sql (รันซ้ำได้: บรรทัดแรก SET client_min_messages = warning; · CREATE TABLE IF NOT EXISTS · INSERT … ON CONFLICT DO NOTHING) และ 001_shop_holiday.down.sql
3. ซ้อมบนฐานที่มีข้อมูลแบบระบบจริง (เว็บตัวเดิมยังรันอยู่):
   - สำรอง: New-Item -ItemType Directory -Force backups | Out-Null · docker exec sabai06-db pg_dump -U sabai -d sabai -f /tmp/before-cr04.sql แล้ว docker cp sabai06-db:/tmp/before-cr04.sql backups\before-cr04.sql
   - reset แล้วจองนัดใหม่ 1 นัดผ่าน API ด้วยสคริปต์ node (ไม่ล็อกอิน S01 2026-10-20 14:00) จดรหัสนัด
   - รัน migration 2 ครั้ง: docker cp db\migrations\001_shop_holiday.sql sabai06-db:/tmp/001.sql แล้ว docker exec sabai06-db psql -U sabai -d sabai -v ON_ERROR_STOP=1 -f /tmp/001.sql (ห้าม pipe ไฟล์ผ่าน PowerShell เพราะภาษาไทยจะเพี้ยน) · ตัดสินผลจาก $LASTEXITCODE (ต้องเป็น 0) และบรรทัดผลของ psql (ครั้งแรก INSERT 0 3 · ครั้งที่ 2 INSERT 0 0) · ถ้าเห็น NOTICE "already exists, skipping" ที่ PowerShell 5.1 แสดงเป็นตัวแดง (NativeCommandError) = ข้อความแจ้ง ไม่ใช่ error
   - ตรวจ: ไม่ error ทั้ง 2 ครั้ง · นัดใหม่ยังอยู่ · SELECT count(*) FROM shop_holiday = 3 · ชื่อไทยถูกต้องตรวจด้วย SQL ไม่ใช่ด้วยตา: SELECT holiday_date, name_th = 'วันปิยมหาราช' AS th_ok FROM shop_holiday WHERE holiday_date = '2026-10-23' ต้องได้ t (ตัวอักษรไทยที่ PowerShell แสดงอาจเพี้ยนทั้งที่ข้อมูลถูก ห้ามแก้ข้อมูลเพราะเห็นบนจอ · ถ้าได้ f ให้รันคำสั่งเดียวกันจากไฟล์ .sql ด้วย docker cp + psql -f ก่อนสรุป)
4. แก้ให้เครื่องติดตั้งใหม่และ reset ใช้ได้ + โค้ดทุกช่องทาง + ข้อความ 3 ภาษา + แชท ตามแผน
5. ลำดับ deploy: migration (ข้อ 3) ต้องรันก่อน rebuild เว็บเสมอ (เว็บใหม่บน schema เก่า → reset/slots/price/bookings ตอบ 500) · เก็บ image เดิมไว้ถอยกลับ: docker tag sabai06-web:latest sabai06-web:before-cr04 · แล้ว rebuild web
6. พิสูจน์: node tests/cr04.mjs เขียว · reset 2 ครั้งติดได้ 200 ทั้งคู่ · หน้า /book เลือกวันที่ 23 ต.ค. เห็นข้อความร้านหยุด (เพิ่มเทสต์ใน e2e-cr/tests/cr04.spec.ts รัน --project=chromium) · ติดตั้งใหม่: docker run --rm -d --name sabai06-fresh -e POSTGRES_USER=sabai -e POSTGRES_PASSWORD=sabai -e POSTGRES_DB=sabai -v "${PWD}\db\init:/docker-entrypoint-initdb.d:ro" postgres:16-alpine → รอ init เสร็จก่อนตรวจ (pg_isready ผ่านได้ระหว่าง init ยังไม่จบ: วนถาม docker exec sabai06-fresh psql -U sabai -d sabai -tAc "SELECT count(*) FROM shop_holiday" ทุก 1 วินาที สูงสุด ~60 วินาที จนได้ตัวเลข) แล้วตรวจว่าได้ 3 แถว จากนั้น docker stop sabai06-fresh
7. Regression (จากโฟลเดอร์บท): node web/scripts/check-rules.mjs (diff ว่าง) · node tests/golden/run.mjs · node tests/cr02.mjs · node tests/cr03.mjs · Push-Location e2e-cr; npx playwright test --project=chromium; Pop-Location · Push-Location e2e-legacy; npx playwright test; Pop-Location (api + chromium) · แดงที่ไม่ได้ตั้งใจ → หยุดบอกผม
8. docs/MIGRATION-RUNBOOK.md (สำรอง · คำสั่งรัน · ตรวจ ($LASTEXITCODE + INSERT 0 n) · หัวข้อ "ลำดับ": deploy = สำรอง → migration → rebuild เว็บ · ถอย = เว็บกลับ image before-cr04 ก่อน แล้วค่อย down.sql (เว็บใหม่อ่าน/TRUNCATE ตารางนี้ ถ้า down ก่อน = 500) · ข้อมูลที่จะหาย) · TRACEABILITY แถว CR-04 → BR-01/BR-03 → TC · CHANGE-REPORT ส่วน CR-04 · SPEC.md · อัปเดต REGISTER.md (สถานะ + hash commit แดง) → git add -A (backups/ ถูก exclude) → git status → git commit "CR-04: วันหยุดร้าน + migration 001"
สรุปเป็นตาราง: ขั้น | คำสั่ง | ผล | เวลา
```

💬 **คัดลอกพรอมต์นี้** (ส่วนที่ 3 · ทางเลือก · ส่วน ข หลังร้าน ทำเมื่อเวลาเหลือ)

```text
ทำ CR-04 ส่วน ข: เจ้าของร้านเพิ่ม/ลบวันหยุดเองในหน้าหลังร้าน ตามที่ตกลงใน CHANGE-REQUESTS/answers/CR-04-ANSWERS.md (รันคำสั่งด้วย PowerShell · อ่าน CLAUDE.md ก่อน · ห้ามแก้ค่าที่คาดหวังเดิม · ห้ามเปิด README.md ของบท fast_track/ และ _solution/)
1. เพิ่มเคสใน tests/cr04.mjs ก่อน (เพิ่มวันที่มีนัดยืนยัน · วันว่าง · วันนี้ · อดีต · ลบ · สมาชิกเรียก · ไม่ล็อกอิน · ชื่อวันหยุดภาษาไทยส่งด้วย node แล้วอ่านกลับจาก GET /api/holidays ต้องตรงตัว) → แดง → commit
2. API + ส่วนหน้าหลังร้าน + ข้อความ 3 ภาษา → rebuild → เขียว
3. Regression ชุดเดียวกับส่วน ก · อัปเดต TRACEABILITY / CHANGE-REPORT / REGISTER · commit "CR-04b: หลังร้านจัดการวันหยุด"
สรุปเป็นตาราง: เคส | ก่อนแก้ | หลังแก้
```

✅ **ผลจริง** <!-- RESULT:LAB8:summary --> ⏳ *migration รัน 2 ครั้งไม่ error · นัดใหม่ยังอยู่ · วันหยุดกี่แถว · `th_ok` · reset 2 ครั้ง · cr04 แดง → เขียว · ติดตั้งใหม่มีตาราง · ทำส่วน ข ไหม · เวลา (~N นาที)*

<!-- RESULT:LAB8:table --> ⏳ *ตาราง ขั้น | คำสั่ง | ผล | เวลา (สำรอง → จองนัดใหม่ → migration รอบ 1 → รอบ 2 → ตรวจ → reset × 2 → ติดตั้งใหม่)*

<!-- RESULT:LAB8:img/lab8-migration-twice.png --> ⏳ *ภาพ `img/lab8-migration-twice.png` ตารางขั้นซ้อม migration จาก LAB8_RESULT*

<!-- RESULT:LAB8:img/lab8-shop-closed.png --> ⏳ *ภาพ `img/lab8-shop-closed.png` หน้า `/book` เลือกวันหยุดร้านแล้วเห็นข้อความร้านหยุด ไม่มีปุ่มรอบ วงแดง (screenshot รอบจริง)*

👀 **สังเกต**
- ⚠️ **รัน SQL ด้วย `docker cp` + `psql -f` เท่านั้น** · pipe ไฟล์ผ่าน PowerShell 5.1 (`Get-Content | docker exec -i`) ทำภาษาไทยกลายเป็น `?` จริงในฐานข้อมูล
- **ผล psql ภาษาไทยบนจอ PowerShell อาจเพี้ยนทั้งที่ข้อมูลถูก** · ตรวจด้วย SQL (`name_th = '…'` ได้ `t`) · ห้ามแก้ข้อมูลเพราะเห็นตัวอักษรเพี้ยนบนจอ
- **`db/init/` ไม่ใช่วิธี deploy** ฐานที่มีข้อมูลอยู่แล้วจะไม่รันซ้ำ · แต่เครื่องติดตั้งใหม่และ reset ต้องได้ schema เดียวกับ migration
- **reset พังหลังเพิ่มตาราง?** ย้อนดูคำตอบข้อ 2 ของส่วนที่ 1 (reset ล้างอะไร เอาข้อมูลจากไหน) · ระบบเดิมมักมีรายการตายตัวที่ต้องอัปเดตตาม
- ⚠️ **`down -v` = ข้อมูลลูกค้าหาย = ผิดหนังสือ CR** · สำรองก่อนทุกครั้ง (สร้าง `backups\` ก่อน `docker cp`) และ tag image เดิมไว้ถอยกลับ
- **รันซ้ำได้จริง = ครั้งแรก `INSERT 0 3` ครั้งที่ 2 `INSERT 0 0`** (รอบจริง) · ครั้งที่ 2 psql พิมพ์ NOTICE `already exists, skipping` ที่ PowerShell 5.1 แสดงเป็นตัวแดงทั้งที่ exit 0 → ดู `$LASTEXITCODE` หรือใส่ `SET client_min_messages = warning;`
- ⚠️ **ลำดับ: migration ก่อน rebuild เว็บ · ถอย: เว็บก่อน `down.sql`** รอบจริงลองกลับลำดับ: เว็บใหม่บน schema เก่า → slots / price / bookings / reset ตอบ 500 · เครื่องติดตั้งใหม่ก็ต้องรอ init จบก่อนตรวจ (`pg_isready` ผ่านได้ก่อน)

✔️ **ไปต่อได้เมื่อ:** migration รัน 2 ครั้งบนฐานที่มีนัดใหม่ผ่าน · reset ผ่าน 2 ครั้งติด · `tests/cr04.mjs` เขียว · มี `docs/MIGRATION-RUNBOOK.md` + `backups/before-cr04.sql` (ไม่ commit) + image `sabai06-web:before-cr04`

---

## LAB 9 · CR-01 ฟีเจอร์ใหม่ เลื่อนนัด

🎯 ✏️ ฟีเจอร์ใหม่ที่ใหญ่ที่สุด: **แตกงาน 3 ขั้น** (A API เลื่อนนัด → B รอบที่เลื่อนได้ → C หน้า `/account`) · เทสต์แดงก่อนทุกขั้น · ปิดท้ายด้วย **regression เต็ม 3 เบราว์เซอร์** → ได้ `tests/cr01.mjs` · `e2e-cr/tests/cr01.spec.ts`

![คู่รักหนุ่มสาวเลื่อนการ์ดนัดบนกระดานตารางเวลาไม้จาก 19:00 ไป 19:30 เหลือเงาจาง ๆ ของการ์ดเดิม ข้างกันมีการ์ดนักบำบัดป้าย คนเดิม หุ่นยนต์ถือป้าย ไม่นับชนกับตัวเอง คุณจันทร์ยิ้ม ป้ายไม้สีทองด้านบน เลื่อนนัดเอง](img/concept-21-reschedule-self-overlap.jpg)

💬 **คัดลอกพรอมต์นี้** (ส่วนที่ 1 · วิเคราะห์ + แตกงานใน Plan mode)

```text
วิเคราะห์ CHANGE-REQUESTS/CR-01.md (ฟีเจอร์ใหม่ ใหญ่ที่สุด) ก่อนแก้ (รันคำสั่งด้วย PowerShell · ยังห้ามแก้โค้ด · อ่าน CLAUDE.md และ SYSTEM-MAP.md ก่อน · ห้ามเปิด README.md ของบท fast_track/ และ _solution/ · Plan mode เขียนไฟล์ไม่ได้ ทุกอย่างให้อยู่ในแชทและแผน)
1. แสดง "คำถามถึงร้าน" ในแชทก่อน แล้วค่อยเปิด CHANGE-REQUESTS/answers/CR-01-ANSWERS.md · บอกข้อที่ได้คำตอบ/ยังค้าง
2. อธิบายด้วยหลักฐาน (ไฟล์:บรรทัด): เวลาของนัดเก็บที่ตารางไหนบ้าง คอลัมน์ไหนคำนวณเอง คอลัมน์ไหนต้องอัปเดตเอง · กฎห้ามซ้อนของนักบำบัดและห้องอยู่ที่ไหน (โค้ดและ DB) · ถ้าเลื่อนไปเวลาที่ทับเวลาเดิมของนัดตัวเองจะชนอะไร
3. ทำไมใช้ /api/slots เดิมหาเวลาว่างให้การเลื่อนไม่ได้ · ทำไม "ยกเลิกแล้วจองใหม่" ข้างในโค้ดอาจทำให้คอร์สหรือสิทธิ์เดือนเกิดเพี้ยน
4. เนื้อหา impact (จะบันทึกเป็น docs/impact/CR-01.md) ตาม docs/IMPACT-TEMPLATE.md · แตกงาน 3 ขั้น: ขั้น A API เลื่อนนัด · ขั้น B รอบที่เลื่อนได้ (เฉพาะนักบำบัด/ห้องเดิม ไม่นับนัดตัวเอง) · ขั้น C หน้า /account
5. ค่าที่คาดหวังอย่างน้อย 12 เคส ครอบ: ขอบ 24 ชม. · ช่วงวัน +30/+31 · รอบสุดท้าย · เวลาเดิม · คนเดิมไม่ว่าง · ทับเวลาเดิมของตัวเอง (นัดคู่) · สิทธิ์ (คนอื่น/ไม่ล็อกอิน/owner) · นัดที่ใช้บริการแล้ว · เดือนเกิด · คอร์สหมดอายุ · ราคาและแต้มไม่เปลี่ยน · รอบเดิมว่างให้คนอื่น · ทุกแถวติดป้าย [D:CR-01] (คำตอบร้าน) หรือ [E …] (ค่าเดิมที่ต้องคงไว้ เช่น ยอด/แต้มของนัดก่อนเลื่อน)
6. เสนอแผนทีละขั้น แล้วรอผมอนุมัติ · หลังผมอนุมัติ (ออกจาก Plan mode) ให้บันทึกเนื้อหา impact ทั้งหมดเป็น docs/impact/CR-01.md อย่างเดียวแล้วหยุด รอพรอมต์ถัดไป
สรุปเป็นตาราง: ขั้น | ไฟล์ที่จะแตะ | เทสต์ที่พิสูจน์ | ความเสี่ยง
```

💬 **คัดลอกพรอมต์นี้** (ส่วนที่ 2 · ขั้น A + B · API) ☕

```text
ทำ CR-01 ขั้น A และ B ตาม docs/impact/CR-01.md (รันคำสั่งด้วย PowerShell · อ่าน CLAUDE.md ก่อน · ห้ามแก้ e2e-legacy/ · ห้ามแก้ค่าที่คาดหวังเดิม · ยังไม่ทำหน้าเว็บ · ห้ามเปิด README.md ของบท fast_track/ และ _solution/)
0. ถ้ายังไม่มี docs/impact/CR-01.md ให้บันทึกจากแผนที่ผมอนุมัติก่อน
1. เทสต์ก่อน: tests/cr01.mjs ทุกเคส API จาก impact (reset {now} คุมเวลา) → รันบนโค้ดเดิมต้องแดง (endpoint ยังไม่มี) → git add tests/cr01.mjs docs/impact/CR-01.md → git commit "CR-01 test: แดงก่อนแก้"
2. ขั้น A: POST /api/bookings/:id/reschedule ตามที่ตกลง · อัปเดตเวลาทุกตารางที่เก็บเวลา ใน transaction เดียว · ไม่คิดราคา/แต้ม/บัตร/คอร์สใหม่ · error ใหม่ครบ 3 ภาษา · rebuild → รันเฉพาะเคสขั้น A
3. ขั้น B: GET /api/bookings/:id/reschedule-slots?date= · ใช้กฎรอบเวลาเดิม แต่ตรวจเฉพาะนักบำบัด (และห้อง) เดิม และไม่นับนัดตัวเอง · rebuild → node tests/cr01.mjs ต้องเขียวทุกเคส (ถ้าเขียน A และ B เสร็จพร้อมกัน rebuild ครั้งเดียวได้ แต่รันเคสขั้น A ให้เขียวก่อน แล้วจึงรันทั้งหมด)
4. Regression ระหว่างทาง (จากโฟลเดอร์บท): node web/scripts/check-rules.mjs (diff ว่าง) · node tests/golden/run.mjs · node tests/cr02.mjs · node tests/cr03.mjs · node tests/cr04.mjs
5. แดงที่ไม่ได้ตั้งใจ → หยุดบอกผม ห้ามแก้เทสต์ให้ผ่าน · อัปเดต REGISTER.md (ขั้น A+B เสร็จ) → git add -A → git status → git commit "CR-01 A+B: API เลื่อนนัด"
สรุปเป็นตาราง: เคส | ก่อนแก้ | หลังแก้
```

💬 **คัดลอกพรอมต์นี้** (ส่วนที่ 3 · ขั้น C หน้าเว็บ + regression เต็ม)

```text
ทำ CR-01 ขั้น C หน้า /account ตาม testid ใน CHANGE-REQUESTS/answers/CR-01-ANSWERS.md (รันคำสั่งด้วย PowerShell · อ่าน CLAUDE.md ก่อน · ห้ามแก้ e2e-legacy/ · ห้ามแก้ค่าที่คาดหวังเดิม · ห้ามเปิด README.md ของบท fast_track/ และ _solution/)
1. เทสต์ก่อน: e2e-cr/tests/cr01.spec.ts = คุณนิดา (nida@sabai.test) เลื่อนนัด B05 ไป 12 ต.ค. 10:00 ผ่านหน้าเว็บ → รีโหลดแล้วเห็นเวลาใหม่ · ปุ่มเลื่อนของนัดวันนี้ (B06) กดไม่ได้ → รันต้องแดง → git add e2e-cr/tests/cr01.spec.ts → git commit -m "CR-01 C test: แดงก่อนแก้"
2. ทำปุ่ม กล่องเลือกวัน รอบ ยืนยัน ข้อความสำเร็จ/ผิดพลาด 3 ภาษา · rebuild → cr01.spec.ts เขียวทั้ง chromium firefox webkit
3. Regression เต็ม (จากโฟลเดอร์บท): node web/scripts/check-rules.mjs · node tests/golden/run.mjs · node tests/cr01.mjs ถึง cr04.mjs · Push-Location e2e-cr; npx playwright test; Pop-Location (3 เบราว์เซอร์) · Push-Location e2e-legacy; $env:PLAYWRIGHT_JSON_OUTPUT_NAME="test-report\legacy-all.json"; npx playwright test --project=api --project=chromium --project=firefox --project=webkit --reporter=list,json; Pop-Location (= npm run test:all + ไฟล์ JSON · 3 เบราว์เซอร์ ~13 นาที → รันแบบ background แล้วรอผล)
   แยก passed / expected-fail / failed ต่อ project จาก JSON ด้วยสคริปต์ node (tests[].status = expected และ expectedStatus = failed คือ expected-fail · status = unexpected คือ failed · flaky แยกไว้) · e2e-cr ก็แยกแบบเดียวกัน (บรรทัดสรุปนับ test.fail รวมใน passed)
   ข้อที่ล้มแต่ไม่เกี่ยวกับไฟล์ที่ CR แตะ (เช่น TC-UI-02 หน้า /skin บน webkit) ให้รันซ้ำเฉพาะข้อ (--project=webkit -g TC-UI-02 --repeat-each=3) · ถ้ายังผ่านบ้างล้มบ้าง ให้พิสูจน์บน image เดิม sabai06-web:before-cr04 (container ชั่วคราว sabai06-old พอร์ต 4001 ต่อ sabai06-net env เดียวกับ web/compose.yaml แล้วรันข้อนั้นด้วย BASE_URL พอร์ตนั้น · เสร็จแล้ว docker stop) ว่าล้มแบบเดียวกัน = flaky เดิม ไม่ใช่ regression · ห้ามแก้เทสต์
4. เอกสาร: web/SPEC.md (API และหน้าใหม่) · TRACEABILITY แถว CR-01 → BR-01/02/03/04/07/13/14 (+ กฎใหม่ "เลื่อนนัดเอง") → TC · CHANGE-REPORT ส่วน CR-01 · อัปเดต REGISTER.md → git add -A → git status → git commit "CR-01 C: หน้าเลื่อนนัด"
สรุปเป็นตาราง: ชุดทดสอบ | chromium | firefox | webkit | หมายเหตุ
```

✅ **ผลจริง** <!-- RESULT:LAB9:summary --> ⏳ *cr01 API กี่เคส แดง → เขียว · cr01.spec 3 เบราว์เซอร์ · e2e-legacy `test:all` ผ่านจริง / คาดว่าล้ม / ล้ม เทียบ baseline · commit กี่ตัว · เวลาแยกขั้น (~N นาที)*

<!-- RESULT:LAB9:table-cases --> ⏳ *ตาราง เคส | ก่อนแก้ | หลังแก้ 4–6 แถวเด่น (ทับเวลาเดิมของตัวเอง · คนเดิมไม่ว่าง · ขอบ 24 ชม. · สิทธิ์ · คอร์ส)*

<!-- RESULT:LAB9:table-browsers --> ⏳ *ตาราง ชุดทดสอบ | chromium | firefox | webkit | หมายเหตุ จากส่วนที่ 3*

<!-- RESULT:LAB9:img/lab9-reschedule-dialog.png --> ⏳ *ภาพ `img/lab9-reschedule-dialog.png` หน้า `/account` ของคุณนิดาเปิดกล่องเลื่อนนัด เลือกวันและรอบ ปุ่มของนัดวันนี้กดไม่ได้ (screenshot รอบจริง)*

<!-- RESULT:LAB9:img/gif-TC-CR01-15.gif --> ⏳ *GIF `img/gif-TC-CR01-15.gif` หัวเรื่อง "🎬 TC-CR01-15 …" `/account` → เลื่อนนัด → เลือกวัน/รอบ → ยืนยัน → รีโหลดเห็นเวลาใหม่*

👀 **สังเกต**
- **หารอบว่างสำหรับ "เลื่อน" ≠ หารอบว่างสำหรับ "จองใหม่"** เงื่อนไขต่างกัน (ใครทำนัดนี้ · ไม่นับนัดตัวเอง) · ใช้ของเดิมตรง ๆ ได้คำตอบที่ดูถูกแต่ผิด
- **เวลาของนัดเก็บมากกว่า 1 ที่** บางคอลัมน์ DB คำนวณให้เอง บางคอลัมน์ต้องอัปเดตเอง · ต้องอยู่ใน transaction เดียว
- **"ยกเลิกแล้วจองใหม่" ข้างในโค้ดไม่เท่ากับ "เลื่อน"** · ตรวจสิทธิ์คอร์ส แต้ม และราคาหลังเลื่อนว่าไม่เปลี่ยน
- **แตกงานแล้วรัน regression ระหว่างทาง** เจอแดงตอนขั้น A แก้ง่ายกว่าเจอตอนจบขั้น C
- ⚠️ **e2e-legacy 3 เบราว์เซอร์ใช้เวลานาน** (~13 นาที) ให้รันแบบ background แล้วรอผลจริง · นับ expected-fail แยกจาก passed ด้วยไฟล์ JSON (`--reporter=list,json`)
- **flaky ≠ regression แต่ต้องพิสูจน์** รอบจริง webkit ล้ม TC-UI-02 (หน้า `/skin` ที่ CR-01 ไม่ได้แตะ) · รันซ้ำ 3 รอบล้ม 2 · รันบน image ก่อน CR (`before-cr04`) ก็ล้ม 1/3 = ปัญหาเดิม ไม่ใช่ของเรา · จดไว้ ห้ามแก้เทสต์

✔️ **ไปต่อได้เมื่อ:** `tests/cr01.mjs` เขียวทุกเคส · `cr01.spec.ts` เขียว 3 เบราว์เซอร์ · regression ไม่มีแดงใหม่ (e2e-legacy เท่า baseline) · มีแถว CR-01 ใน TRACEABILITY และ REGISTER

---

## LAB 10 · CR-05 รายงาน + CSV

🎯 ✏️ หน้ารายงานยอดใหม่สำหรับเจ้าของร้าน · **ค่าที่คาดหวังมาจาก SQL ที่รันก่อนเขียนโค้ด** (oracle อิสระ) · CSV ภาษาไทยเปิด Excel ได้ → ได้ `docs/impact/CR-05.md` (SQL + ผล) · `tests/cr05.mjs` · `e2e-cr/tests/cr05.spec.ts`

![ห้องทำงาน หุ่นยนต์คิดยอดด้วยลูกคิดจากสมุดบัญชีหนาป้าย SQL เด็กเอามือปิดจอป้าย หน้ารายงานใหม่ ที่ขึ้นตัวเลข 1250 320 875 640 2090 พร้อมพูดว่า อย่าลอกจากจอ ป้ายตกแต่งบนผนังและโต๊ะ ความรู้ ช่วยให้ งานง่ายขึ้น · งานดี ชีวิตดี สมดุล · คิด วิเคราะห์ สู่การพัฒนาที่ดีกว่า ป้ายไม้สีทองด้านบน ค่าที่คาดหวังมาจากทางอื่น](img/concept-22-independent-oracle.jpg)

💬 **คัดลอกพรอมต์นี้** (ส่วนที่ 1 · วิเคราะห์ + ค่าที่คาดหวังจาก SQL ใน Plan mode)

```text
วิเคราะห์ CHANGE-REQUESTS/CR-05.md ก่อนแก้ (รันคำสั่งด้วย PowerShell · ยังห้ามแก้โค้ด · อ่าน CLAUDE.md และ SYSTEM-MAP.md ก่อน · ห้ามเปิด README.md ของบท fast_track/ และ _solution/)
1. เขียน "คำถามถึงร้าน" แล้วค่อยเปิด CHANGE-REQUESTS/answers/CR-05-ANSWERS.md
1.5 อธิบายของเดิมที่จะต่อยอด (อ้างไฟล์:บรรทัด): หน้าและ API หลังร้านเดิม (lib/server/admin.ts · component ตารางคิว AdminQueue · เมนู NavMenu) · ตรวจสิทธิ์ owner ที่ไหนและอย่างไร · เงินเก็บเป็นหน่วยอะไรในโค้ดและแปลงจาก NUMERIC ที่ไหน · ส่วนไหนใช้ซ้ำได้ ส่วนไหนต้องเขียนใหม่
2. ค่าที่คาดหวังต้องมาจากทางอื่น ไม่ใช่จากหน้ารายงานที่กำลังจะสร้าง: reset แล้วเขียน SQL ตรงกับตาราง booking / booking_slot / point_txn ฯลฯ รันด้วย docker exec sabai06-db psql -U sabai -d sabai -c "<SQL>" (นับตามวันนัดเวลาไทย) สำหรับช่วง 2026-09-01 ถึง 2026-09-30 · 2026-10-01 ถึง 2026-10-31 · 2026-10-06 ถึง 2026-10-09
   ทุกตัวเลขในรายงาน (จำนวนแยกสถานะ · ยอดขาย · บัตรของขวัญ · ช่องทางอื่น · ค่ารถ · ส่วนลด 3 แบบ · แต้ม · ครั้งคอร์ส · ยอดนัดที่ยังไม่มา · คิวต่อนักบำบัด) ต้องมี SQL และผลจริง · ป้าย: นิยามตัวเลขมาจาก [D:CR-05] · ค่ามาจาก [E sql:<ชื่อคิวรี>] · ถ้าค่าจาก SQL ไม่ตรงตัวอย่างในคำตอบร้าน = หยุดถามผม (ห้ามปรับ SQL ให้ตรง)
3. docs/impact/CR-05.md ตาม docs/IMPACT-TEMPLATE.md + SQL ทั้งหมดพร้อมผล + เคสขอบ (92/93 วัน · from > to · สิทธิ์) + เรื่องโซนเวลาและหน่วยเงิน
4. เสนอแผนแล้วรอผมอนุมัติ
สรุปเป็นตาราง: ช่วงวัน | ตัวเลข | ค่าจาก SQL | SQL ที่ใช้ (ย่อ)
```

💬 **คัดลอกพรอมต์นี้** (ส่วนที่ 2 · ลงมือในโหมดปกติ)

```text
ทำ CR-05 ตาม docs/impact/CR-05.md (รันคำสั่งด้วย PowerShell · อ่าน CLAUDE.md ก่อน · ห้ามแก้ e2e-legacy/ · ห้ามแก้ค่าที่คาดหวังเดิม · ห้ามเปิด README.md ของบท fast_track/ และ _solution/)
1. เทสต์ก่อน: tests/cr05.mjs ใช้ค่าจาก SQL ใน impact เป็นผลที่คาดหวัง (ห้ามรันหน้ารายงานแล้วลอกค่า) + เคส CSV (หัวคอลัมน์ · จำนวนแถว · ขึ้นต้นด้วย BOM) + สิทธิ์ → แดง → commit "CR-05 test: แดงก่อนแก้"
2. API + หน้า /admin/report + ลิงก์เมนู + CSV + ข้อความ 3 ภาษา · rebuild → node tests/cr05.mjs เขียว
3. e2e-cr/tests/cr05.spec.ts: owner เปิดหน้า เลือกช่วง ก.ย. กดดู ยอดตรงกับ SQL · กดโหลด CSV แล้วตรวจไฟล์ที่ดาวน์โหลดใน test ด้วย Node (3 ไบต์แรก EF BB BF + ชื่อบริการภาษาไทยตรงตัว · ไม่ตัดสินจากหน้าจอ PowerShell) · 3 เบราว์เซอร์
4. ตรวจเพิ่ม: ยอดขายในรายงาน = ผลรวมยอดในตารางคิวหลังร้านของนัดที่ใช้บริการแล้วทุกวันในช่วง · ถ้าเทสต์ต้อง "กดใช้บริการเสร็จ" นัดใด ให้ตั้งเวลาระบบ (reset {now} หรือ /api/test/clock) ให้ถึงเวลานัดนั้นก่อนกด
5. Regression (จากโฟลเดอร์บท): node web/scripts/check-rules.mjs · node tests/golden/run.mjs · node tests/cr01.mjs ถึง cr05.mjs · Push-Location e2e-cr; npx playwright test --project=chromium; Pop-Location · Push-Location e2e-legacy; npx playwright test; Pop-Location (api + chromium) · แดงที่ไม่ได้ตั้งใจ → หยุดบอกผม
6. เอกสาร: SPEC.md · TRACEABILITY แถว CR-05 · CHANGE-REPORT ส่วน CR-05 · git commit "CR-05: รายงานยอด + CSV" · REGISTER.md
สรุปเป็นตาราง: ช่วงวัน | ตัวเลข | SQL | API | หน้าเว็บ | ตรงไหม
```

✅ **ผลจริง** <!-- RESULT:LAB10:summary --> ⏳ *SQL กี่คิวรี · cr05 กี่เคส แดง → เขียว · CSV ขึ้นต้นด้วย BOM ไหม · ยอดรายงาน = ผลรวมตารางคิวไหม · cr05.spec 3 เบราว์เซอร์ · เวลา (~N นาที)*

<!-- RESULT:LAB10:table --> ⏳ *ตาราง ช่วงวัน | ตัวเลข | SQL | API | หน้าเว็บ | ตรงไหม 4–6 แถวเด่น (ค่าจาก SQL รอบจริงเท่านั้น)*

<!-- RESULT:LAB10:img/lab10-report-page.png --> ⏳ *ภาพ `img/lab10-report-page.png` หน้า `/admin/report` ช่วง 1–30 ก.ย. ยอดและจำนวนนัดแยกสถานะ + ปุ่ม CSV (screenshot รอบจริงหลังแก้)*

👀 **สังเกต**
- **ค่าที่คาดหวังห้ามลอกจากหน้ารายงานที่เพิ่งสร้าง** = อบบั๊ก · SQL ต้องรันและจดผลก่อน commit แก้
- **SQL ไม่ตรงตัวอย่างในคำตอบร้าน = หยุดถาม** ห้ามปรับ SQL ให้ตรง · อาจเป็นนิยามที่เข้าใจไม่ตรงกัน หรือเจอเรื่องใหม่
- **โซนเวลา** นับวันนัดแบบ UTC ทำให้นัดตอนเช้าตกไปอีกวัน · นิยามช่วงวันต้องเป็นเวลาไทย
- **หน่วยเงิน** ฐานข้อมูลเก็บ NUMERIC โค้ดอาจใช้หน่วยอื่น · หาจุดแปลงก่อนเขียนตัวเลข
- **CSV ไม่มี BOM → Excel แสดงภาษาไทยเพี้ยน** · ตรวจไบต์แรกของไฟล์ด้วย node ไม่ใช่ตัดสินจากตา

✔️ **ไปต่อได้เมื่อ:** ค่าที่คาดหวังทุกตัวมี SQL + ผลจริงใน impact ก่อน commit แก้ · `tests/cr05.mjs` เขียว · CSV เปิดแล้วภาษาไทยไม่เพี้ยน · มีแถว CR-05 ใน TRACEABILITY และ REGISTER

---

## LAB 11 · Regression เต็ม + REA เทียบเวอร์ชัน

🎯 🔍 พิสูจน์ "ของเดิมไม่พัง" ด้วยทุกชุด 3 เบราว์เซอร์ · ใช้ REA เทียบ **bundle · HAR · scenario ก่อน/หลัง** · ทุกไฟล์ที่เปลี่ยนโยงกับ CR ได้ → ได้ `REGRESSION-REPORT.md` + `docs/TRACEABILITY.md` ฉบับสมบูรณ์

![หน้าร้านสปา 2 หลังเหมือนกันป้าย v1 และ v2 ทั้งคู่มีหน้าต่างป้าย หน้าบัญชี หุ่นยนต์แปะสติกเกอร์ส้ม changed ที่หน้าบัญชีของ v2 ห้องหลังร้านป้าย กฎหลังร้าน อยู่ในหมอกมีป้าย REA มองไม่เห็น เด็กเขียนบนคลิปบอร์ด พิสูจน์ด้วยเทสต์ ป้ายไม้สีทองด้านบน เทียบเวอร์ชันที่ส่งมอบ](img/concept-23-version-compare-sabai.jpg)

> 🔁 **ทบทวนบท 05:** เทียบเวอร์ชัน = หลักฐานว่าแก้ตรงไหน · กล่องในหมอก = "ไม่รู้" ไม่ใช่ "เหมือนเดิม"
>
> ![ชั้นวางกล่อง 2 แถวป้าย v1 และ v2 แต่ละกล่องมีลายนิ้วมือ สองคู่แรกป้าย เหมือนเดิม คู่ที่สามลายนิ้วมือต่างสีป้าย เปลี่ยน คู่สุดท้ายอยู่ในหมอกมีเครื่องหมายคำถามป้าย ไม่รู้ หุ่นยนต์ส่องแว่นขยาย เด็กถือคลิปบอร์ด ต้องทดสอบซ้ำ แมวส้มกับลูกหมาเชียร์ หัวเรื่อง เทียบเวอร์ชัน = หลักฐานว่าแก้ตรงไหน](../05_rea-reverse-engineer-legacy-petshop/img/concept-08-version-compare.jpg)

💬 **คัดลอกพรอมต์นี้** ☕

```text
พิสูจน์ว่าทุก CR "ทำตามที่ขอ" และ "ของเดิมไม่พัง" แล้วเขียน REGRESSION-REPORT.md (รันคำสั่งด้วย PowerShell จากโฟลเดอร์บท · ห้ามแก้โค้ด · ห้ามแก้เทสต์ · ห้ามเปิด README.md ของบท fast_track/ และ _solution/)
1. reset แล้วรันทุกชุดบนโค้ดล่าสุด จดผ่าน/ทั้งหมด/เวลา: node web/scripts/check-rules.mjs · node tests/golden/run.mjs · node tests/cr01.mjs ถึง cr05.mjs · Push-Location e2e-cr; npx playwright test; Pop-Location (3 เบราว์เซอร์) · Push-Location e2e-legacy; npm run test:all; Pop-Location (3 เบราว์เซอร์ ~13 นาที → รันแบบ background แล้วรอผล) · ผล Playwright ให้แยก passed / expected-fail (annotation fail) / failed ต่อ project เพราะบรรทัดสรุปนับ expected-fail รวมใน passed
2. REA เทียบของที่ส่งมอบ (bundle) ก่อน/หลัง: ใช้ rea-out\v1 เดิมเป็นฝั่งซ้าย
   - ถ้า rea-out\v2\.next\static มีอยู่แล้ว ให้บอกผมก่อนลบแล้วคัดลอกใหม่
   - New-Item -ItemType Directory -Force rea-out\v2\.next | Out-Null; docker cp sabai06-web:/app/.next/static rea-out\v2\.next\static
   - powershell -NoProfile -ExecutionPolicy Bypass -File tools\rea.ps1 -Out rea-out\static-v2.json analyze-javascript-application /work/rea-out/v2/.next/static --json 2> rea-out\static-v2.log
   - node tools\rea-tools.mjs pages rea-out\static-v1.json rea-out\static-v2.json (หน้าไหนไฟล์เปลี่ยน/ใหม่ จาก hash ในชื่อไฟล์ · hash ต่าง = ไฟล์ใน bundle เปลี่ยน แต่ไม่บอกว่าเปลี่ยนตรงไหน)
   - node tools\rea-tools.mjs cmp-input rea-out\static-v1.json rea-out\static-v2.json rea-out\cmp.json
   - powershell -NoProfile -ExecutionPolicy Bypass -File tools\rea.ps1 -Out rea-out\cmp-out.json compare-application-versions /work/rea-out/cmp.json --json 2> rea-out\cmp-out.log
   - node tools\rea-tools.mjs cmp-sum rea-out\cmp-out.json
2b. REA ดูสัญญา API ของเส้นทางเดิมหลังแก้ (HAR ชุดเดียวกับตอนรับมอบ · ต้องใช้ 127.0.0.1):
   - ⚠️ record-har.mjs reset ข้อมูลก่อนเดิน แล้วจองนัดใหม่ (รอบรับมอบได้ B14) และยกเลิก B05 → ข้อมูลในระบบเปลี่ยน ถ้างานถัดไปต้องการข้อมูลตั้งต้นให้ reset ใหม่ (POST /api/test/reset)
   - node tools\record-har.mjs http://127.0.0.1:4000 rea-out\journeys-v2.har
   - node tools\rea-tools.mjs har-records rea-out\journeys-v2.har
   - powershell -NoProfile -ExecutionPolicy Bypass -File tools\rea.ps1 -Out rea-out\har-api-v2.json inspect-web-network-capture /work/rea-out/journeys-v2.har har <วาง --record ทั้งหมดที่ได้> --sensitive-value Nida@2026 --sensitive-value Owner@2026 --json 2> rea-out\har-api-v2.log
   - node tools\rea-tools.mjs har-api rea-out\har-api-v2.json แล้วเทียบกับ node tools\rea-tools.mjs har-api rea-out\har-api.json (ของตอนรับมอบ) → ตาราง endpoint | v1 (status · คีย์) [E ev_…] | v2 [E ev_…] | เหมือนเดิม/เปลี่ยน | CR ที่อนุญาตให้เปลี่ยน (ป้าย [E] ได้จาก node tools\rea-tools.mjs ids rea-out)
2c. REA ขับหน้าจองเดิมซ้ำบนโค้ดใหม่: powershell -NoProfile -ExecutionPolicy Bypass -File tools\rea.ps1 -Network sabai06-net -Out rea-out\scenario-v2.json capture-browser-scenario /work/tools/scenario-book-quote.json --json 2> rea-out\scenario-v2.log · node tools\rea-tools.mjs scenario-sum rea-out\scenario-v2.json · node tools\rea-tools.mjs shot rea-out\scenario-v2.json rea-out\scenario-v2-final.png · เทียบจำนวน step และยอดหน้าสรุป (จาก scenario-sum) กับ docs/REA-INVENTORY.md (ยอดเดิมคือ [E] ของตอนรับมอบ · ต่างได้เฉพาะเมื่อมี CR อนุญาต)
3. ตาราง: CR | ส่วนที่ควรเปลี่ยนใน bundle (หน้าไหน) | REA static เห็นไหม (changed / unknown / ไม่เห็น) | HAR/scenario เห็นไหม | ถ้าไม่เห็นเพราะอะไร | เทสต์ไหนพิสูจน์แทน · อ่านเฉพาะ changed ที่เป็นโค้ดหน้าเว็บ (chunks/app/...) ส่วน unknown ห้ามสรุปว่าไม่เปลี่ยน · "REA ไม่เห็น" ≠ "ไม่ได้เปลี่ยน"
4. git diff --stat ตั้งแต่ commit baseline ถึง HEAD → ทุกไฟล์ที่เปลี่ยนต้องโยงกับ CR ได้ (ตาราง ไฟล์ | CR) ไฟล์ที่โยงไม่ได้ติด ⚠️
5. ค่าที่คาดหวังเดิม: git diff baseline..HEAD -- web/scripts/check-rules.mjs e2e-legacy tests/golden ต้องว่าง หรือทุกจุดมีแถวใน docs/ORACLE-CHANGES.md
6. docs/TRACEABILITY.md ฉบับสมบูรณ์: ทุก CR มี BR และ TC ที่ผ่าน · ทุก TC ใหม่มี CR
ตัวเลขทุกตัวต้องมาจากการรันรอบนี้ · ข้อไหนแดงให้หยุดแล้วบอกผม ห้ามแก้ให้ผ่าน
สรุปเป็นตาราง: ชุด | ผ่าน/ทั้งหมด | เบราว์เซอร์ | เวลา | หมายเหตุ
```

✅ **ผลจริง** <!-- RESULT:LAB11:summary --> ⏳ *ได้ `REGRESSION-REPORT.md` · ทุกชุดผ่าน/ทั้งหมด · e2e-legacy `test:all` ผ่านจริง / คาดว่าล้ม / ล้ม · REA changed / unknown · HAR v1↔v2 · scenario v2 · ไฟล์ ⚠️ ที่โยง CR ไม่ได้ · เวลา (~N นาที)*

<!-- RESULT:LAB11:table-suites --> ⏳ *ตาราง ชุด | ผ่าน/ทั้งหมด | เบราว์เซอร์ | เวลา (check-rules · golden · cr01–05 · e2e-cr · e2e-legacy)*

<!-- RESULT:LAB11:img/lab11-regression.png --> ⏳ *ภาพ `img/lab11-regression.png` ตารางเดียวกันจาก REGRESSION-REPORT รอบจริง*

<!-- RESULT:LAB11:table-rea --> ⏳ *ตาราง CR | ส่วนที่ควรเปลี่ยนใน bundle | REA static เห็นไหม | HAR/scenario เห็นไหม | เทสต์ที่พิสูจน์แทน ครบ 5 แถว + ตาราง HAR v1↔v2 ติดป้าย [E]*

<!-- RESULT:LAB11:img/lab11-rea-compare.png --> ⏳ *ภาพ `img/lab11-rea-compare.png` ตาราง CR × REA + บรรทัด summary ของ `cmp-sum` + ตาราง HAR v1↔v2*

👀 **สังเกต**
- **"REA ไม่เห็น" ≠ "ไม่ได้เปลี่ยน"** กฎฝั่งเซิร์ฟเวอร์ไม่อยู่ใน bundle · CR แบบนั้นพิสูจน์ได้ด้วยเทสต์เท่านั้น
- **อ่านเฉพาะ `changed` ที่เป็นโค้ดหน้าเว็บ (`chunks/app/...`)** · `unknown` จำนวนมากเป็นเรื่องปกติของ coverage partial ห้ามสรุปว่าเหมือนเดิม
- **HAR และ scenario ซ้ำบน v2 = หลักฐาน [E] ว่าเส้นทางเดิมของลูกค้าไม่เปลี่ยน** ไม่ใช่หลักฐานว่า CR ทำงาน
- **expected-fail นับต่อ project** ชุดที่อยู่ project `api` รันครั้งเดียว · ตัวเลข 3 เบราว์เซอร์จึงไม่ใช่ "baseline × 3" ทุกข้อ
- **ไฟล์ที่โยง CR ไม่ได้ = ⚠️ ต้องอธิบาย** ของที่เปลี่ยนโดยไม่มีใครขอคือ regression ที่ไม่ตั้งใจจนกว่าจะพิสูจน์ได้

✔️ **ไปต่อได้เมื่อ:** ตัวเลขทุกชุดในรายงานมาจากรอบนี้ · ตาราง CR × REA ครบ 5 แถว (static + HAR/scenario) · ตาราง HAR v1↔v2 ติดป้าย [E] ครบ · diff ค่าที่คาดหวังเดิมว่างหรือมีแถวใน ORACLE-CHANGES ครบ · ไม่มีไฟล์ ⚠️ ที่อธิบายไม่ได้

---

## LAB 12 · ส่งมอบ + ซ้อมถอยกลับ

🎯 ✏️ เขียน **smoke test แบบอ่านอย่างเดียว** · **ซ้อมถอยกลับจริง** บนฐานที่มีข้อมูล · runbook วันขึ้นระบบ · เอกสารส่งมอบภาษาคน → ได้ `tests/smoke.mjs` · `docs/DEPLOY-RUNBOOK.md` · `RELEASE-NOTES.md` · `UAT-CHECKLIST.md` · `CHANGE-REPORT.md` ฉบับรวม

![เด็กสะพายกล่องป้าย สำรองข้อมูล กับหุ่นยนต์โดดร่มสีเขียวป้าย แผนถอยกลับ ลงจากแท่นฝึกเตี้ย ๆ ป้าย ซ้อม คุณจันทร์ถือเช็กลิสต์ยิ้ม ป้ายไม้สีทองด้านบน ซ้อมถอยกลับก่อนใช้จริง](img/concept-14-rollback.jpg)

💬 **คัดลอกพรอมต์นี้** (ส่วนที่ 1 · ซ้อมถอยกลับ + runbook)

```text
ซ้อมถอยกลับ migration บนฐานที่มีข้อมูลจริง เขียน smoke test ให้ทีมใช้วันขึ้นระบบ แล้วเขียน docs/DEPLOY-RUNBOOK.md (รันคำสั่งด้วย PowerShell จากโฟลเดอร์บท · ห้าม docker compose down -v · ห้ามลบ volume · ห้ามแก้โค้ดระบบใน web/ db/ · ห้ามเปิด README.md ของบท fast_track/ และ _solution/)
0. เขียน tests/smoke.mjs (Node ≥ 22.18 ไม่ใช้ dependency · BASE_URL ค่าเริ่ม http://localhost:4000) = ตรวจหลังขึ้นระบบจริงแบบ **อ่านอย่างเดียว** (ห้าม reset · ห้ามสร้างหรือแก้ข้อมูล): health db:true · /api/services ตอบ 200 · /api/holidays มีวันหยุดที่ร้านแจ้ง · หน้า /book ตอบ 200 · API ใหม่ของ CR-01 และ CR-05 เมื่อไม่ล็อกอินต้องตอบ 401 (ไม่ใช่ 404 = มี endpoint จริง) · พิมพ์ตาราง ข้อ | ผล แล้ว exit 0 เมื่อผ่านทุกข้อ ไม่งั้น exit 1 · รันตอนนี้ต้อง exit 0
1. สำรอง: New-Item -ItemType Directory -Force backups | Out-Null · docker exec sabai06-db pg_dump -U sabai -d sabai -f /tmp/before-rollback.sql แล้ว docker cp sabai06-db:/tmp/before-rollback.sql backups\before-rollback.sql
2. reset แล้วจองนัดใหม่ 1 นัดผ่าน API ด้วยสคริปต์ node (ไม่ล็อกอิน S05 2026-10-21 11:00) จดรหัสนัด
3. หยุดเว็บชั่วคราว: docker compose -f web/compose.yaml stop → node tests/smoke.mjs ต้อง exit 1 (พิสูจน์ว่า smoke จับระบบล่มได้)
4. ถอย: docker cp db\migrations\001_shop_holiday.down.sql sabai06-db:/tmp/001down.sql แล้ว docker exec sabai06-db psql -U sabai -d sabai -v ON_ERROR_STOP=1 -f /tmp/001down.sql → ตรวจว่าตารางวันหยุดหายและนัดใหม่ยังอยู่
5. ไปข้างหน้าอีกครั้ง: รัน 001_shop_holiday.sql ด้วยวิธีเดียวกัน → วันหยุดกลับมา 3 แถว · นัดใหม่ยังอยู่
6. เปิดเว็บ: docker compose -f web/compose.yaml start → health db:true → node tests/smoke.mjs exit 0 → node tests/cr04.mjs เขียว
7. docs/DEPLOY-RUNBOOK.md ลำดับวันขึ้นระบบจริง: สำรอง → tag image เดิม → รัน migration → build/up เว็บ → node tests/smoke.mjs (ผลที่ต้องเห็น) → เงื่อนไขที่ต้องถอย → ขั้นถอย (image เดิม + down.sql) · ใส่เวลาที่วัดได้จริงจากการซ้อม และข้อมูลที่จะหายถ้าถอย
8. git add tests/smoke.mjs docs/DEPLOY-RUNBOOK.md แล้ว commit "release: smoke test + deploy runbook" · เพิ่มแถว smoke ใน docs/TRACEABILITY.md (โยงทุก CR)
ทุกขั้นจดคำสั่งและผลจริง ขั้นไหนไม่ผ่านให้หยุดบอกผม
สรุปเป็นตาราง: ขั้น | คำสั่ง | ผล | เวลา
```

💬 **คัดลอกพรอมต์นี้** (ส่วนที่ 2 · เอกสารส่งมอบ)

```text
เขียนเอกสารส่งมอบให้คุณจันทร์และคณะกรรมการตรวจรับ (รันคำสั่งด้วย PowerShell · ห้ามแก้โค้ด · ห้ามเปิด README.md ของบท fast_track/ และ _solution/ · อ่าน CHANGE-REPORT.md, REGRESSION-REPORT.md, docs/TRACEABILITY.md, KNOWN-ISSUES.md, docs/SPEC-GAPS.md ก่อน)
1. RELEASE-NOTES.md ภาษาคน ไม่มีศัพท์โปรแกรม: ต่อ CR บอก อะไรเปลี่ยน · ลูกค้าเห็นอะไร · ร้านต้องทำอะไร · มีผลเมื่อไร · หัวข้อ "เรื่องที่ยังไม่ได้แก้" (จาก KNOWN-ISSUES.md และสิ่งที่เจอระหว่างทางแต่ไม่อยู่ใน CR) พร้อมผลกระทบและข้อเสนอ
2. UAT-CHECKLIST.md: ต่อ CR 3–6 ขั้นที่ร้านกดเองได้บนหน้าเว็บ · ผลที่ต้องเห็น (ตัวเลข/ข้อความ) · ช่อง ผ่าน/ไม่ผ่าน · ลงชื่อ · วันที่
3. CHANGE-REPORT.md ส่วนสรุปรวม: ตาราง CR | commit แดง | commit แก้ | ไฟล์ที่แก้ | เทสต์ใหม่ | regression | ความเสี่ยงคงค้าง | วิธีถอยกลับ
4. ตรวจความครบ: ทุกคำขอในหนังสือ CR-01–05 มีแถวใน UAT · ทุกแถว UAT โยงกับ TC ใน TRACEABILITY · ข้อไหนขาดให้บอก
5. อัปเดต CHANGE-REQUESTS/REGISTER.md เป็น "รอตรวจรับ (UAT)" · git commit "release: พร้อมตรวจรับ CR-01–05"
ไม่แน่ใจว่าร้านจะเข้าใจคำไหน ให้เขียนแบบง่ายกว่า · สรุปเป็นตาราง: เอกสาร | ส่วน | จำนวนรายการ
```

![โต๊ะกรรมการ คุณจันทร์ประทับตราสีเขียว ตรวจรับแล้ว บนแฟ้มหนาที่มีแถบสี เทสต์ ภาพ commit แผนถอยกลับ หุ่นยนต์ยื่นถุงหลักฐานใสที่มีเอกสารและภาพ เด็กกำมือดีใจ ป้ายไม้สีทองด้านบน ตรวจรับด้วยหลักฐาน](img/concept-16-audit-signoff.jpg)

✅ **ผลจริง** <!-- RESULT:LAB12:summary --> ⏳ *smoke exit 0 ตอนปกติ / exit 1 ตอนหยุดเว็บ · ซ้อมถอยกลับ: นัดใหม่ยังอยู่ไหม วันหยุดกลับมากี่แถว · เวลาที่วัดได้จริงแต่ละขั้น · เอกสารส่งมอบกี่รายการ · REGISTER "รอตรวจรับ" ครบไหม · เวลา (~N นาที)*

<!-- RESULT:LAB12:table-rollback --> ⏳ *ตาราง ขั้น | คำสั่ง | ผล | เวลา (สำรอง → จองนัด → stop web + smoke → down → ตรวจ → up → start + smoke → cr04)*

<!-- RESULT:LAB12:img/lab12-rollback.png --> ⏳ *ภาพ `img/lab12-rollback.png` ตารางขั้นซ้อมถอยกลับจาก LAB12_RESULT*

<!-- RESULT:LAB12:img/lab12-release-notes.png --> ⏳ *ภาพ `img/lab12-release-notes.png` ส่วนแรกของ RELEASE-NOTES.md วงแดง ①②③ ที่ "ลูกค้าเห็นอะไร" "ร้านต้องทำอะไร" "เรื่องที่ยังไม่แก้" 🔒 ครอปแถวที่สงวนไว้สำหรับข้อสอบชุด B ออก (LESSON-PLAN M10)*

👀 **สังเกต**
- **smoke test รันบนระบบจริง จึงต้องอ่านอย่างเดียว** ห้าม reset ห้ามสร้างข้อมูล · และต้องพิสูจน์ว่า "จับได้" (exit 1 ตอนเว็บหยุด) ไม่ใช่เขียวตลอด
- **ถอยกลับมีราคา** ข้อมูลที่เกิดหลัง migration (เช่น วันหยุดที่ร้านเพิ่มเองภายหลัง) อาจหายเมื่อรัน down · ต้องเขียนไว้ในแผน ไม่ใช่รู้ตอนถอยจริง
- **ซ้อมจริงดีกว่าเขียนอย่างเดียว** เวลาใน runbook ต้องมาจากการซ้อม คณะกรรมการถามว่า "ถอยกลับใช้กี่นาที" ได้คำตอบทันที
- **เรื่องที่รู้แต่ยังไม่แก้ต้องอยู่ใน RELEASE-NOTES** (จาก KNOWN-ISSUES ข้อที่ติด `test.fail` ในชุดส่งมอบ และที่เจอระหว่างทาง) · ปิดไว้ = เจ้าของงานเจอเองทีหลัง
- **ภาษาคน** คุณจันทร์ต้องอ่านเข้าใจโดยไม่ต้องถามว่า endpoint คืออะไร · UAT เป็นขั้นที่กดเองได้บนหน้าเว็บ

✔️ **ไปต่อได้เมื่อ:** ซ้อมถอยกลับผ่านทุกขั้นโดยข้อมูลนัดไม่หาย · `tests/smoke.mjs` exit 1 ตอนเว็บหยุด / exit 0 ตอนปกติ · runbook เรียก smoke และไม่มี `down -v` · RELEASE-NOTES ไม่มีศัพท์โปรแกรม · REGISTER เป็น "รอตรวจรับ (UAT)" ครบ 5 CR

---

## ✅ รูบริก: เช็กลิสต์ "รับงานแก้ระบบเดิมที่ดี"

ให้คะแนน 1 คะแนนต่อข้อที่ทำได้ · **ดีมาก ≥ 18/20 · ใช้ได้ 14–17 · ต้องแก้ < 14**

**A. รับมอบและเข้าใจ (LAB 1–3)**
- ☐ 1. `HANDOVER-CHECK.md` ทุกตัวเลขมาจากคำสั่งที่รันจริง · คำอ้างทุกข้อในบันทึกส่งมอบได้ ✅ / ❌ / ⚠️ พร้อมหลักฐาน · ข้อแดงจำแนกโดยไม่แก้เทสต์
- ☐ 2. `docs/REA-INVENTORY.md` แยก static / runtime / inference / unknown · ทุกแถวมี `[E ev_xxxxxxxx]` · ไม่มีประโยค "ไม่มี X" จากหลักฐาน coverage partial
- ☐ 3. `SYSTEM-MAP.md` ทุกแถวอ้าง `file:line` หรือชื่อฟังก์ชัน/constraint · ตรวจทานด้วยตาตัวเองครบ 5 ข้อ
- ☐ 4. triangulation มีครบ REA / source / DB พร้อม ✅ ⚠️ ❌ · `SPEC-GAPS.md` เป็นคำถามถึงร้าน ไม่ใช่ AI ตัดสินเอง

**B. รั้วและตาข่าย (LAB 4–5)**
- ☐ 5. CLAUDE.md สั้น มีวิธีรัน / ห้ามแตะ / กับดัก · ทดสอบรั้วในเซสชันใหม่แล้วถูกปฏิเสธจริง
- ☐ 6. golden master รันเทียบ 2 รอบติดผ่านทั้งคู่ (นิ่ง) · ตัดฟิลด์ที่เปลี่ยนเองและเขียนเหตุผล
- ☐ 7. known issue ล็อกคู่ (ค่าปัจจุบัน + `test.fail`) ไม่ได้แอบแก้ · seam ปิดได้เมื่อ `ALLOW_TEST_RESET=0`
- ☐ 8. mutant 3 ตัวรันครบ คืนไฟล์ครบ · ตัวที่รอดอธิบายรูของตาข่ายได้

**C. Change Request (LAB 6–10)**
- ☐ 9. ทุก CR มีคำถาม + อธิบายของเดิมด้วย `file:line` + `docs/impact/CR-0N.md` (ไฟล์ × เทสต์ · DB · i18n · แชท · หลักฐาน grep) **ก่อน** diff · ค่าที่คาดหวังทุกแถวมีป้าย [D:CR-0N] หรือ [E]
- ☐ 10. ทุก CR มี commit เทสต์แดงก่อน commit แก้
- ☐ 11. `web/scripts/check-rules.mjs` `tests/golden/` `e2e-legacy/` ไม่มีค่าที่คาดหวังเปลี่ยน หรือทุกจุดมีแถวใน `ORACLE-CHANGES.md`
- ☐ 12. CR-02 ทดสอบทั้ง 2 ฝั่งของวันมีผล และนัดเก่าไม่เปลี่ยนยอด
- ☐ 13. CR-03 ทดสอบกดพร้อมกัน (สมาชิกและไม่ล็อกอิน) + แชท · เทสต์เดิมที่จองพร้อมกันคนละคนยังได้ `SLOT_TAKEN`
- ☐ 14. CR-04 migration รัน 2 ครั้งบนฐานที่มีนัดใหม่ ไม่ error ข้อมูลอยู่ครบ · reset ผ่าน 2 ครั้งติด · ไม่ใช้ `down -v`
- ☐ 15. CR-01 มีเคสเลื่อนทับเวลาเดิมของตัวเอง + นักบำบัดคนเดิมไม่ว่าง + Playwright 3 เบราว์เซอร์
- ☐ 16. CR-05 ค่าที่คาดหวังมาจาก SQL ที่รันก่อนเขียนโค้ด · CSV มี BOM เปิด Excel ภาษาไทยไม่เพี้ยน

**D. Regression (LAB 11)**
- ☐ 17. ตัวเลขผ่าน/ทั้งหมดทุกชุดใน `REGRESSION-REPORT.md` ตรงกับการรันซ้ำ · ครบ 3 เบราว์เซอร์
- ☐ 18. ตาราง "CR × REA เห็นไหม" (static + HAR v1↔v2 + scenario) อธิบายสิ่งที่ REA มองไม่เห็นและเทสต์ที่พิสูจน์แทน · ไฟล์ที่เปลี่ยนทุกไฟล์โยง CR ได้ · TRACEABILITY ครบ

**E. ส่งมอบ (LAB 12)**
- ☐ 19. `RELEASE-NOTES.md` ภาษาคน คุณจันทร์อ่านเข้าใจ · มีเรื่องที่ยังไม่แก้ · `UAT-CHECKLIST.md` ต่อ CR มีช่องลงชื่อ
- ☐ 20. ซ้อมถอยกลับจริง (สำรอง → down → up) ข้อมูลนัดอยู่ครบ · `tests/smoke.mjs` อ่านอย่างเดียว exit 1 ตอนเว็บหยุด / exit 0 ตอนปกติ · runbook เรียก smoke และไม่มี `down -v`

---

## 🔁 รันซ้ำ

| อยากทำ | 💬 พรอมต์ |
|---|---|
| ล้างข้อมูลทดสอบ | `เรียก POST http://localhost:4000/api/test/reset แล้วเช็กว่าได้ {"ok":true}` |
| รันตาข่ายทั้งหมด | `รันทุกชุดตามหัวข้อ "รันยังไง" ใน CLAUDE.md (e2e ครบ 3 เบราว์เซอร์ รันแบบ background แล้วรอ · แยก passed / expected-fail / failed) แล้วสรุปเป็นตาราง ชุด \| ผ่าน/ทั้งหมด \| เวลา ห้ามแก้อะไร` |
| ดูข้อมูลในฐานข้อมูล | `ใช้ docker exec sabai06-db psql -U sabai -d sabai ดูจำนวนนัดแยกสถานะ (อ่านอย่างเดียว ห้ามแก้)` |
| ปิดระบบ (เก็บข้อมูล) | `ปิดระบบ: docker compose -f web/compose.yaml down แล้ว docker compose -f db/compose.yaml down ห้ามใส่ -v` |
| เทียบงานกับเฉลย (หลังจบ LAB 12 · ลบ 3 กฎ `Read(...)` ออกจาก `.claude/settings.json` เองก่อน แล้วเปิดเซสชันใหม่) | `เทียบ docs/impact/CR-0N.md และ tests/ ของผมกับ _solution/ บอกเคสหรือไฟล์ที่ผมยังขาด และข้อที่ของผมดีกว่า` |

## ถ้าเจอปัญหา: คัดลอกพรอมต์นี้

| อาการ | 💬 พรอมต์ |
|---|---|
| `bind: An attempt was made to access a socket…` (พอร์ตถูก Windows/WinNAT จอง) | `เปิดเว็บไม่ได้ error bind forbidden ช่วยรัน netsh interface ipv4 show excludedportrange protocol=tcp ดูว่า 4000 หรือ 5433 อยู่ในช่วงที่จองไหม ถ้าอยู่ ให้เสนอพอร์ตว่างนอกช่วง แล้วบอกวิธีตั้ง $env:WEB_PORT / $env:DB_PORT และ $env:BASE_URL ก่อนทำ` |
| container ชื่อชนหรือพอร์ตชนกับบทก่อน | `docker compose ขึ้นว่าชื่อ container ซ้ำหรือพอร์ตถูกใช้ ช่วยหาว่า container ไหนชน บอกผมก่อนว่าจะหยุดหรือลบอะไร (ห้ามลบ volume)` |
| พอร์ต 4000 ถูกใช้อยู่ (เว็บบท 05 เปิดค้าง) | `พอร์ต 4000 ถูกใช้อยู่ ช่วยดู docker ps ว่าเป็น container ไหน ถ้าเป็นเว็บบท 05 (pawpantry05) ให้บอกผมก่อนแล้วหยุดด้วย docker stop pawpantry05 (ไม่ลบอะไร) หรือเสนอให้ตั้ง $env:WEB_PORT และ $env:BASE_URL เป็นพอร์ตว่างอื่น` |
| `running scripts is disabled` / `UnauthorizedAccess` ตอนเรียก `.ps1` | `PowerShell ไม่ยอมรัน tools\rea.ps1 ช่วยรันใหม่ด้วย powershell -NoProfile -ExecutionPolicy Bypass -File tools\rea.ps1 … (ไม่แก้ค่าเครื่อง) ถ้ายังติดเพราะไฟล์มาจาก zip ที่ดาวน์โหลด ให้บอกผมก่อนรัน Unblock-File -Path tools\*` |
| check-rules ขึ้น error import `.ts` | `node web/scripts/check-rules.mjs error ตอน import ไฟล์ .ts ช่วยเช็ก node -v ถ้าต่ำกว่า 22.18 ให้บอกวิธีอัปเดต หรือรันใน container node:22-alpine ที่อยู่ใน network sabai06-net แทน` |
| REA อ่าน JSON ไม่ได้ (BOM) | `REA บอกว่า JSON input begins with a UTF-8 byte-order mark ช่วยรันใหม่ด้วย powershell -NoProfile -ExecutionPolicy Bypass -File tools\rea.ps1 -Out <ไฟล์> แทนการใช้ > ของ PowerShell` |
| HAR schema validation failed | `REA ตรวจ HAR ไม่ผ่าน ช่วยเช็กว่าบันทึก HAR ผ่าน http://127.0.0.1:4000 ไม่ใช่ localhost แล้วบันทึกใหม่` |
| คำสั่งค้าง / ถูกตัดเพราะ timeout (build · e2e 3 เบราว์เซอร์) | `คำสั่งนี้นานเกิน 2 นาทีแล้วถูกตัด ช่วยรันใหม่แบบ background หรือตั้ง timeout ยาว แล้วรอจนจบ รายงานผลจริงจาก log อย่าสรุปจากผลที่ยังไม่จบ` |
| migration แล้วภาษาไทยเป็น `?` | `ชื่อวันหยุดในฐานข้อมูลเป็น ??? ช่วยเช็กก่อนว่าข้อมูลเพี้ยนจริงไหมด้วย SQL SELECT name_th = '<ข้อความไทย>' (ตัวอักษรที่ PowerShell แสดงอาจเพี้ยนทั้งที่ข้อมูลถูก) ถ้าเพี้ยนจริง ให้เช็กว่ารัน SQL ด้วย docker cp + psql -f หรือเปล่า ถ้า pipe ผ่าน PowerShell ให้แก้ข้อมูลด้วย migration ที่รันซ้ำได้ แล้วรันใหม่ด้วยวิธีที่ถูก` |
| ยิง API แล้วภาษาไทย/จีนเป็น `?` | `ข้อความไทย/จีนที่ส่งผ่าน API กลายเป็น ? ช่วยเช็กว่าส่งด้วย Invoke-RestMethod -Body หรือ curl ของ PowerShell หรือเปล่า ให้เปลี่ยนเป็นสคริปต์ node หรือ curl.exe --data-binary '@ไฟล์.json' (UTF-8) แล้วส่งใหม่ อย่าแก้ข้อมูลเดิมจนกว่าจะยืนยันด้วย SQL ว่าเพี้ยนจริง` |
| migration รอบ 2 ขึ้นตัวแดง `NOTICE … already exists, skipping` | `migration รอบ 2 ขึ้นตัวแดง NOTICE already exists ช่วยเช็ก $LASTEXITCODE และบรรทัด INSERT 0 n ก่อน ถ้า exit 0 = ไม่ใช่ error (PowerShell 5.1 แสดง stderr ของ psql เป็นสีแดง) · ถ้าอยากให้เงียบ ใส่ SET client_min_messages = warning; บรรทัดแรกของ migration` |
| migration รันรอบ 2 แล้ว error | `migration รันครั้งที่ 2 แล้ว error ช่วยบอกบรรทัดที่ error และสาเหตุ แก้ไฟล์ migration ให้รันซ้ำได้ (IF NOT EXISTS · ON CONFLICT DO NOTHING) โดยไม่ลบข้อมูลที่มีอยู่ แล้วซ้อมรัน 2 ครั้งใหม่ ห้าม down -v` |
| reset ไม่ได้ 200 | `POST /api/test/reset ไม่ได้ 200 ช่วยอ่าน docker logs sabai06-web ช่วงนั้นแล้วบอกสาเหตุจาก error จริงก่อนแก้ ห้ามลบ volume และห้ามแก้ค่าที่คาดหวังของเทสต์` |
| เทสต์เดิมแดงหลังแก้ | `เทสต์เดิมข้อนี้แดงหลังแก้ CR ช่วยบอกว่าเว็บผิด เทสต์เก่าล้าสมัย หรือเทสต์ใหม่เขียนผิด พร้อมหลักฐาน ห้ามแก้เทสต์ให้ผ่าน ถ้าต้องเปลี่ยนค่าที่คาดหวังให้บอกผมก่อนและจดใน docs/ORACLE-CHANGES.md` |
| Claude จะแก้ e2e-legacy หรือใช้ `down -v` | `หยุดก่อน e2e-legacy เป็นชุดที่ส่งมอบ ห้ามแก้ และห้าม docker compose down -v เพราะข้อมูลลูกค้าจะหาย ถ้าเห็นว่าเทสต์ข้อไหนล้าสมัยให้เขียนเหตุผลแล้วถามผม ส่วนงานฐานข้อมูลให้หาวิธีที่ไม่ลบ volume` |
| e2e ผ่านบ้างล้มบ้าง (รอบ 1 ≠ รอบ 2) | `test ข้อนี้ผ่านบ้างล้มบ้าง ช่วยรันซ้ำ --repeat-each=5 บอกสาเหตุ (เช่น นาฬิกาหรือข้อมูลไม่ได้ reset) ถ้าเป็นเทสต์ที่ส่งมอบและไม่เกี่ยวกับไฟล์ที่ CR แตะ ให้พิสูจน์บน image เดิมก่อนสรุปว่า regression ห้ามแก้ e2e-legacy · ถ้าเป็นเทสต์ของเรา แก้ที่ test โดยไม่เปลี่ยนผลที่คาดหวัง` |
| mutant ค้างอยู่ในโค้ด | `เช็ก git status และ git diff ใน web/lib/rules ว่ายังมีโค้ดที่ทำพังค้างอยู่ไหม ถ้ามีให้คืนด้วย git checkout -- <ไฟล์> แล้ว rebuild และรัน golden` |

## 📝 ข้อสอบ: EXAM.md

จบบทแล้ว (อย่างน้อย LAB 0–8) ลองงานจริงย่อส่วนใน [`EXAM.md`](EXAM.md): ระบบเดิม 1 ชุด + หนังสือขอเปลี่ยนแปลง **8 ข้อ 100 คะแนน · ใช้ Claude Code ได้ทุกข้อ**

| เรื่อง | รายละเอียด |
|---|---|
| ชุด | **A · ฝึก** อยู่ใน `EXAM.md` · **B · สอบจริง** แจกวันสอบ รูปแบบเหมือน A ทุกข้อแต่เรื่องและค่าขอบต่างกันหมด |
| แก้ repo เดิม | **6/8 ข้อ · 84 คะแนน** (โค้ด/schema 4 ข้อ · เทสต์ใน repo 2 ข้อ) |
| ทักษะที่ใช้ | ข้อ 1 อ่าน repo ≈ LAB 3 · ข้อ 2 ตาข่าย ≈ LAB 5 · ข้อ 3 impact ≈ ส่วนที่ 1 ของ LAB 6–10 · ข้อ 4–7 แก้กฎ / บั๊ก / migration / ฟีเจอร์ ≈ LAB 6–9 · ข้อ 8 regression + ส่งมอบ ≈ LAB 11–12 |
| ระบบข้อสอบ | แยกชื่อ `sabai06x-*` · **ปิดระบบ LAB ก่อน** (พอร์ต 4000/5433 ชนกัน) ด้วย `down` ที่**ไม่มี** `-v` |
| ส่งงาน | `git bundle` · 1 commit ต่อข้อ (`EX1:` … `EX8:`) · ข้อแก้บั๊กต้องมี commit เทสต์แดงก่อน |
| เกณฑ์ผ่าน | **≥ 60 คะแนน และข้อ 4–7 รวม ≥ 30/58** |

> เฉลยชุด A ผู้สอนแจกหลังฝึก · ชุด B ไม่มีเฉลยเผยแพร่

## 🎉 จบบทแล้ว

![สวนสปายามเย็น คุณจันทร์ถือเอกสารลงชื่อ ตรวจรับแล้ว จับมือกับเด็ก หุ่นยนต์กับน้องบัวแปะมือกัน กระดานด้านหลังติดซอง CR-01 CR-02 CR-03 CR-04 CR-05 มีเครื่องหมายถูกสีเขียวทุกซอง ป้ายไม้สีทองด้านบน ส่งมอบสำเร็จ](img/outro-01-signoff-party.jpg)

ระบบเดิมไม่ได้เริ่มจากศูนย์: **รับมอบ → เข้าใจ → ตาข่าย → แก้ทีละ CR → ส่งมอบพร้อมหลักฐาน** แล้วหนังสือฉบับถัดไปก็จะมาอีก 🔁
**"ทำตามที่ขอ ≠ ของเดิมไม่พัง ≠ ส่งมอบได้"** ทุกช่วงต้องมีหลักฐานของตัวเอง

## 📖 คำศัพท์

คำจากบท 04–05 (Test oracle · [D] [R] [A] [O] [E] · REA · Evidence · HAR · characterization) ใช้ต่อได้ · ตารางนี้เฉพาะคำใหม่

| คำ | ความหมายง่าย ๆ |
|---|---|
| **ระบบเดิม (legacy)** | ระบบที่ใช้งานอยู่แล้ว คนสร้างไม่อยู่ เอกสารอาจเก่า |
| **บันทึกส่งมอบ** | เอกสารที่ผู้รับเหมาเดิมบอกว่าส่งอะไร ผ่านอะไร = คำอ้าง ไม่ใช่หลักฐาน |
| **Change Request (CR)** | หนังสือขอเปลี่ยนระบบ 1 เรื่อง จากเจ้าของงาน |
| **ทะเบียน CR (register)** | ตารางคุมสถานะทุก CR |
| **ตกลงขอบเขต** | คำตอบ + สิ่งที่ตกลงร่วมกันก่อนลงมือ |
| **UAT / ตรวจรับ** | เจ้าของงานลองเองตามรายการแล้วลงชื่อรับ |
| **Triangulation** | เทียบ 3 แหล่ง (REA · โค้ด · DB) ตรงกันจึงมั่นใจ |
| **Constraint (CHECK / EXCLUDE)** | กฎที่ฐานข้อมูลบังคับเอง แม้โค้ดลืมตรวจ |
| **Golden master** | ผลจริงทั้งก้อนที่บันทึกไว้เทียบทุกครั้งหลังแก้ |
| **Characterization test** | เทสต์ที่ล็อก "ระบบทำอะไรอยู่" ไม่ใช่ "ควรทำอะไร" |
| **Known issue** | บั๊กที่รู้แล้วแต่ยังไม่แก้ ล็อกด้วย `test.fail()` |
| **Test seam** | จุดที่ทำให้ทดสอบได้โดยไม่แก้กฎ เช่น เลื่อนนาฬิกา |
| **Mutant / mutation testing** | โค้ดที่แกล้งทำผิด 1 จุด ใช้ดูว่าตาข่ายจับได้ไหม |
| **Impact analysis** | ตาราง "แก้ตรงนี้กระทบไฟล์ไหน เทสต์ไหน" ก่อนลงมือ |
| **Plan mode** | โหมดที่ Claude วางแผนอย่างเดียว ยังไม่แก้ไฟล์ (`Shift+Tab`) |
| **Regression ที่ตั้งใจ / ไม่ตั้งใจ** | ค่าเดิมเปลี่ยนเพราะ CR สั่ง / เปลี่ยนเองโดยไม่มีใครขอ |
| **ORACLE-CHANGES** | บันทึกค่าที่คาดหวังเดิมที่เปลี่ยน พร้อม CR ที่อนุญาต |
| **วันมีผล (effective date)** | วันที่กฎใหม่เริ่มใช้ ก่อนหน้านั้นใช้กฎเดิม |
| **Migration** | ไฟล์ SQL เปลี่ยนโครงฐานข้อมูลที่มีข้อมูลอยู่แล้ว |
| **Idempotent** | รันซ้ำกี่ครั้งผลเท่าครั้งแรก ไม่ error |
| **Rollback / แผนถอยกลับ** | วิธีย้อนระบบกลับเวอร์ชันก่อนถ้าพัง |
| **Advisory lock** | กุญแจใน PostgreSQL กันคำขอพร้อมกันทำงานซ้อน |
| **Self-overlap** | เวลาใหม่ทับเวลาเดิมของนัดตัวเอง ต้องไม่นับว่าชน |
| **Oracle อิสระ** | ค่าที่คาดหวังที่ได้จากทางอื่น (SQL) ไม่ใช่จากหน้าจอที่เพิ่งสร้าง |
| **BOM** | ไบต์หัวไฟล์ที่ทำให้ Excel รู้ว่าเป็น UTF-8 |
| **Traceability matrix** | ตารางโยง CR → BR → TC → ผล |
| **Release notes** | สรุปการเปลี่ยนแปลงภาษาคนสำหรับเจ้าของงาน |
| **Smoke test** | เทสต์สั้น ๆ แบบอ่านอย่างเดียว รันทันทีหลังขึ้นระบบจริงว่าระบบหลัก "ยังหายใจ" |
| **Excluded port range** | ช่วงพอร์ตที่ Windows จองไว้ โปรแกรมอื่นใช้ไม่ได้ |
| **[D:CR-0N]** | ป้ายค่าที่คาดหวังจากคำตอบที่ร้านยืนยันใน CR นั้น |
| **[E ev_xxxxxxxx]** | ป้ายค่าจากหลักฐานของระบบ (REA / HAR / golden) = "ทำอยู่" ไม่ใช่ "ควรทำ" · ขัด [D] = ผู้ต้องสงสัยบั๊ก |

### ไฟล์ในบทนี้

**ก่อนเริ่ม** (มีให้แค่นี้)

```text
06_sabai-spa-legacy-change-request/
├─ README.md               # 📖 บทเรียน + พรอมต์ทุก LAB
├─ EXAM.md                 # 📝 ข้อสอบ (ชุด A ฝึก + กติกาชุด B)
├─ CHANGE-REQUESTS/        # 📨 บันทึกส่งมอบ · ทะเบียน · หนังสือ CR-01–05
│  └─ answers/             # 🔒 คำตอบข้อซักถาม (เปิดเมื่อพรอมต์สั่ง)
├─ web/                    # ระบบเดิม Next.js (SPEC.md = เอกสารเก่า ฉบับ 1.0)
│  └─ scripts/check-rules.mjs   # ชุดตรวจที่ส่งมอบ ชั้น 1
├─ db/                     # PostgreSQL 16 · init/01-schema.sql · init/02-seed.sql
├─ e2e-legacy/             # ชุดทดสอบที่ส่งมอบ ชั้น 2 (Playwright)
├─ tools/                  # rea.ps1 · rea-tools.mjs · record-har.mjs · scenario-book-quote.json
├─ img/                    # 🖼️ รูปประกอบ
├─ fast_track/             # ⚡ พรอมต์เดียวทำครบ (Agent ห้ามอ่าน)
└─ _solution/              # 🔑 เฉลย (ห้ามเปิดก่อนจบ)
```

**หลังจบทุก LAB** (สร้าง/แก้จากพรอมต์ทั้งหมด · ✏️ = แก้ของเดิม)

```text
06_sabai-spa-legacy-change-request/
├─ HANDOVER-CHECK.md          # LAB 1  คำอ้าง vs ผลจริง · baseline
├─ rea-out/                   # LAB 2, 11  Evidence ของ REA · HAR v1/v2 · scenario (ไม่ commit)
├─ backups/                   # LAB 8, 12  pg_dump (ไม่ commit)
├─ docs/
│  ├─ REA-INVENTORY.md        # LAB 2
│  ├─ SPEC-GAPS.md            # LAB 3
│  ├─ IMPACT-TEMPLATE.md      # LAB 4
│  ├─ ORACLE-CHANGES.md       # LAB 4 (อัปเดต LAB 6–11)
│  ├─ impact/CR-0N.md         # LAB 6–10
│  ├─ TRACEABILITY.md         # LAB 6–12
│  ├─ MIGRATION-RUNBOOK.md    # LAB 8
│  └─ DEPLOY-RUNBOOK.md       # LAB 12
├─ SYSTEM-MAP.md              # LAB 3
├─ CLAUDE.md · .claude/settings.json   # LAB 4  กติกา + รั้ว (ห้ามแก้ e2e-legacy · ห้ามอ่านเฉลย)
├─ KNOWN-ISSUES.md            # LAB 5
├─ tests/
│  ├─ golden/                 # LAB 5  run.mjs + *.json + README.md
│  ├─ cr01.mjs … cr05.mjs     # LAB 6–10
│  └─ smoke.mjs               # LAB 12  ตรวจหลังขึ้นระบบ (อ่านอย่างเดียว)
├─ e2e-cr/                    # LAB 5–10  Playwright ชุดใหม่ (char-booking · cr01 · cr03 · cr04 · cr05)
├─ web/                       # ✏️ LAB 5–10  seam + โค้ด CR (ดู diff ด้วย git) · SPEC.md อัปเดตต่อ CR
├─ db/                        # ✏️ LAB 8  migrations/001_shop_holiday.sql + .down.sql · init/ ให้ตรง migration
├─ CHANGE-REPORT.md           # LAB 6–12
├─ REGRESSION-REPORT.md       # LAB 11
├─ RELEASE-NOTES.md · UAT-CHECKLIST.md   # LAB 12
└─ CHANGE-REQUESTS/REGISTER.md   # ✏️ อัปเดตสถานะทุก CR
```
