# งาน: สื่อสอน "Web Automation แบบ code-in-control ด้วย Playwright CLI"

ROOT=/root/workspace/CWN/Teaching/00_setup (ทำงานในนี้เท่านั้น)
- ผลงานสุดท้าย: $ROOT/06_Playwright_CLI_Trip/ ให้มีแค่ README.md, img/, log/ (น้อยที่สุด)
- ไฟล์ทำงาน/โค้ด/scratch ทั้งหมด: $ROOT/.work/06_pwcli/ (ห้ามเขียนนอก ROOT, ห้ามติดตั้งอะไรลงใน 06)
- ห้ามแตะ/ปิด chrome ที่ :9222 (ของ Playwright MCP) ห้าม pkill -f แบบกว้าง
- ห้ามแสดงค่าใน .env / token / อีเมล

## อ่านก่อน
- $ROOT/03_MultiAccount_Container/README.md (สไตล์สื่อสอน: 🖥️ shell · 💬 พรอมต์ในกรอบ text, "ผลที่ควรได้", ภาพจริง) — 06 ต่อจาก LAB 03:
  นศ ใช้ container multi-account-devtool (มี yolo1/yolo2 ล็อกอินแล้ว, @playwright/mcp global, Chromium ที่ /ms-playwright, รันเป็น root, ไม่มีจอ)
- skill playwright-cli: $(npm root -g)/@playwright/mcp/node_modules/playwright-core/lib/tools/skills/playwright-cli/SKILL.md

## ข้อเท็จจริงที่ตรวจแล้ว (ใช้ได้เลย แต่ต้องรันยืนยันเองก่อนเขียนลง README)
- ไม่มี `playwright-cli` ใน PATH แต่มีตัวจริงมากับ @playwright/mcp:
  node "$(npm root -g)/@playwright/mcp/node_modules/playwright-core/lib/tools/cli-client/cli.js" (--version = 1.63.0-alpha)
  wrapper ที่เตรียมไว้: $ROOT/.work/06_pwcli/pwcli (unset PLAYWRIGHT_MCP_CDP_ENDPOINT/OUTPUT_DIR เพราะเครื่องนี้ตั้ง env global ไว้ ทำให้ CLI ไปเกาะ browser :9222)
- config: .playwright/cli.config.json ใน cwd (ดู $ROOT/.work/06_pwcli/.playwright/cli.config.json) ต้องมี "chromiumSandbox": false เพราะรันเป็น root
  viewport 1920x1080, deviceScaleFactor 2, outputDir ใน .work; บนเครื่องนี้ใช้ headless:false + DISPLAY=:99 (มีจอ noVNC ให้ดู) ส่วนใน README ของ นศ ใช้ headless (ค่าเริ่มต้น)
- ref จริงหน้าตาแบบ `f1e13` (ไม่ใช่ e13) — README ต้องใช้ของจริง
- `snapshot --boxes` ให้ [box=x,y,w,h] (css px, viewport-relative) → ใช้วาดวงกลมแดง; `snapshot --filename=...` เซฟ YAML
- `screenshot --filename=... --hires` = ภาพ 2x; `eval "() => ..."` / `eval "el => ..." <ref>`; `find "text"`
- LLM ผู้ตัดสินใจ: `yolo1 -p --model <m> --effort low --output-format json --json-schema '<schema>' --no-session-persistence --strict-mcp-config` (ตรวจ --help เอง, ห้ามให้ LLM มี tool — ตัดสินใจอย่างเดียว)

## 0. ก่อนเริ่ม
- 06_Playwright_CLI_Trip ตอนนี้ว่าง (มีแค่ .ipynb_checkpoints) ถ้าเจอไฟล์อื่นห้ามเขียนทับ ให้สรุปแล้วหยุด
- รัน `--help` ของทุกคำสั่งย่อยที่ใช้ (open, goto, snapshot, find, click, fill, type, press, select, screenshot, eval, close) และทดลองจริง
  README ใช้ได้เฉพาะ syntax ที่รันผ่านแล้ว

## 1. แนวคิดที่ต้องสอน (ทฤษฎีกระชับ)
- Playwright CLI = ตาและมือ (snapshot YAML + [ref=...], action ผ่าน ref)
- โจทย์ + LLM = ผู้ตัดสินใจ: อ่าน snapshot (ตัดเหลือส่วนที่เกี่ยว) + เป้าหมายของ step → ตอบ JSON schema ตายตัว {action, ref, value, reason}
- โค้ด = ผู้คุม flow: เป็นเจ้าของ loop, max step, allowlist action, denylist, guardrail, เงื่อนไขหยุด; validate ทุกคำตอบก่อนเรียก CLI; LLM สั่ง shell เองไม่ได้
- Loop Observe → Decide → Act → Verify (verify ด้วยโค้ดจาก snapshot ใหม่ เช่น ช่อง From มี "Bangkok")
- ref ใช้ได้กับ snapshot ล่าสุดเท่านั้น หน้าเปลี่ยน = snapshot ใหม่ ห้ามใช้ ref เก่า (ทดลองให้เห็น error จริงของ CLI)

## 2. โจทย์สาธิต (รันจริงบนเครื่องนี้)
- https://www.google.com/travel/flights?hl=en · One way · BKK → Tokyo, Japan · Economy · ผู้ใหญ่ 1
- วันเดินทาง = วันที่ 15 ของเดือนถัดจากวันที่รัน คำนวณในโค้ด (ห้าม hardcode) และ print ลง log
- ค้นหาอย่างเดียว denylist บังคับในโค้ด (ชื่อ element ที่ LLM เลือก ตรง Book / Sign in / Continue to book / Payment / Select fare ฯลฯ → หยุดทันที)
  ปิด cookie/consent ได้ ห้ามล็อกอิน
- CAPTCHA/ถูกบล็อก/หา element ไม่เจอ → หยุด รายงาน step ที่ติด พร้อม snapshot/screenshot
- ห้ามเดาราคา: 3 อันดับแรกคัดจาก snapshot จริง พร้อม ref/บรรทัดที่มา

## 3. หลักฐานทุก step (หัวใจของ README)
06_Playwright_CLI_Trip/log/steps/NN_<ชื่อ>/ : snapshot.yml (เต็ม), page.png (ภาพจริง 2x มีวงกลมแดงรอบ element ที่จะ action — PIL จาก box), decision.json (คำตอบ LLM + ผล validate)
+ log/run.log (สั้น) — บีบอัด png ให้เล็กแต่ยังคม รวม log/ ไม่ควรเกิน ~15MB
เพิ่มการทดลอง guardrail จริง 1 ครั้ง (เช่น เป้าหมายหลอกให้กด Sign in → โค้ดหยุด) เก็บเฉพาะ decision.json + บรรทัด log

## 4. README.md (สื่อสอน ภาษาไทย, prompt-based)
- โครง: เป้าหมาย/ต้องมีก่อน → ทฤษฎี (3 ส่วน, loop, ref ใช้ครั้งเดียว, schema, guardrail) → LAB ทีละขั้น → ข้อควรรู้
- ทุก LAB: 🖥️ คำสั่ง shell หรือ 💬 พรอมต์ในกรอบ ```text ให้ copy วาง (รันใน yolo1 ของ container LAB 03, cwd /workspace)
  **พรอมต์ต้องสั้น กระชับ แต่ครบพอให้ได้ผลเดิม** (นศ อ่าน) ไม่ใช่สเปกยาวแบบไฟล์นี้
- ทุก LAB มี "ผลที่ควรได้" จากการรันจริง (code block ของ output จริง ไม่ใช่ภาพ terminal ปลอม) + ภาพ page.png จริงพร้อมวงกลมแดง
- LAB ที่ควรมี: (1) เตรียม alias playwright-cli + config (2) ลองเป็น "ตาและมือ" ด้วยมือ: open/snapshot/find/click บน Google Flights
  (3) ref เก่าใช้ไม่ได้ (4) ให้ AI สร้าง agent code-in-control แล้วรัน → ตาราง step + ภาพ + 3 อันดับเที่ยวบินพร้อม ref ที่มา
  (5) ทดสอบ guardrail (6) checklist ตรวจผล
- ภาพแนวคิด 1–2 ภาพ (สถาปัตยกรรม 3 ส่วน + loop) ให้เว้นที่ไว้เป็น img/concept-*.png แล้วเขียนคำบรรยายภาพที่ต้องการลง $ROOT/.work/06_pwcli/imagegen_todo.md (ผมจะสร้างด้วย cyolo1)
- โค้ด agent อ้างอิงที่ใช้รันจริงให้อยู่ใน .work; README แสดงเฉพาะแก่นสั้น ๆ (เช่น validate()) ไม่ต้องแปะทั้งไฟล์

## ส่งมอบ
สรุปสั้น: ไฟล์ใน 06 + ขนาด, วันที่ที่คำนวณได้, ผลแต่ละ step PASS/FAIL, 3 อันดับเที่ยวบิน (ตามจริง), ปัญหาที่เจอ
ปิด browser ของ playwright-cli เมื่อเสร็จ (ไม่แตะ :9222 และไม่ปิด Xvfb/x11vnc/websockify)
