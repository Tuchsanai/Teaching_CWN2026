# SPEC · สื่อการสอน "Web Automation แบบ code-in-control ด้วย Playwright MCP"

## 0. บริบทและกติกา (อ่านให้ครบก่อนลงมือ)
- Workdir: `/root/workspace/CWN/Teaching/00_setup` เท่านั้น ไฟล์/log ทุกอย่างอยู่ใต้โฟลเดอร์นี้
- ปลายทางสุดท้าย: `06_Playwright/01_playwright-mcp/` มีแค่ `README.md`, `img/`, `log/` (ให้น้อยที่สุดที่จำเป็น)
- พื้นที่ทำงานชั่วคราว (โค้ดอ้างอิง, ผลทดลองดิบ, โน้ต): `06_Playwright/.work_mcp/`
- **ต้นแบบ**: `06_Playwright/00_playwright-cli/README.md` (อ่านทั้งไฟล์ 1,767 บรรทัด) + `img/` + `log/`
  สื่อใหม่ต้องใช้ idea เดียวกันทั้งหมด: โจทย์ Google Flights เดิม, ส่วน A ทฤษฎี / ส่วน B LAB 1–8 / ส่วน C ข้อควรรู้,
  สัญลักษณ์ 🎯 💬 📖 🔍 ✅, กล่อง "จำง่าย", ภาพ compare (หน้าเว็บจริง + YAML), เดินดูทีละ step ของ LAB 6, LAB 7 guardrail A/B, checklist + คำถามทบทวนพร้อมเฉลย
  ต่างกันที่ "ตาและมือ" เปลี่ยนจาก playwright-cli เป็น **Playwright MCP server** โดยมี **โค้ด Python ของเราเป็น MCP client**
- ภาษา: ไทย อ่านง่าย ประโยคสั้น ศัพท์เทคนิคอังกฤษได้ ไม่มี emoji นอกจากสัญลักษณ์ของ LAB
- ห้ามใส่ email, token, รหัสผ่าน, ชื่อบัญชีจริง ลงเอกสาร/ภาพ/log ห้ามอ่าน `.credentials.json`/`auth.json`
- **ห้ามเดา** syntax, ชื่อ tool, พารามิเตอร์, รูปแบบ response, ข้อความ error — ทุกอย่างใน README ต้องมาจากการรันจริงและอ้างอิงผลจริงได้
- ถ้าพบว่าข้อเท็จจริงของ MCP ต่างจาก CLI (เช่น ไม่มี box, snapshot แบบ diff, ref format ต่าง) ให้สอนตามของจริง และถือว่านี่คือเนื้อหาสำคัญของบท

## 1. สภาพแวดล้อมทดลอง (container ที่เตรียมไว้แล้ว)
- container: `devtools-pwmcp-c34a6add` จาก image `tuchsanai/multi-account-devtool:2569_1` (volume `ai-accounts` = บัญชีล็อกอินแล้ว)
  เข้าด้วย `docker exec devtools-pwmcp-c34a6add bash -lc '...'` และคัดลอกไฟล์ด้วย `docker cp` (โฟลเดอร์งานของนักศึกษาใน container คือ `/workspace`)
- ใน container: `@playwright/mcp` 0.0.83, launcher `/usr/bin/playwright-mcp`, Chromium ที่ `/ms-playwright`, รันเป็น root, headless, ไม่มีจอ
- `yolo1` ใน container ล็อกอินแล้ว (max) · `yolo2` **ยังไม่ล็อกอิน** · `cyolo1` ล็อกอินแล้ว
- wrapper `yolo1` ส่ง `--mcp-config=/root/ai-accounts/.Claude/shared/mcp/mcp.json` ให้ Claude ทุกครั้ง (มี server `playwright` ด้วย args `--browser chromium --headless --isolated --no-sandbox --output-dir ...`) → yolo1 ที่นักศึกษาเปิด "ถือ" Playwright MCP อยู่แล้ว = LLM-in-control (ใช้เป็นตัวอย่างเปรียบเทียบได้)
- ห้าม stop/rm container นี้ (ผู้ควบคุมจะลบเอง) ห้ามแตะ container อื่น ปิดเบราว์เซอร์/โปรเซส MCP ที่เปิดเองทุกครั้งเมื่อจบ
- วันที่รันจริง: 2026-09-30 (เวลาไทย) → วันเดินทาง = วันที่ 15 ของเดือนถัดไป = 2026-10-15 (โค้ดต้องคำนวณเอง)

## 2. แนวคิดหลักที่ต้องสอน
ระบบ 3 ส่วน:
- **Playwright MCP = ตาและมือ**: MCP server (stdio, JSON-RPC 2.0) มี tool เช่น snapshot / click / type / press / screenshot / evaluate (ตรวจชื่อจริงจาก `tools/list`)
- **LLM + prompt โจทย์ = ผู้ตัดสินใจ**: ไม่มี tool (`--tools "" --strict-mcp-config`) อ่าน snapshot ที่ตัดแล้ว ตอบ JSON schema ตายตัว `{action, ref, value, reason}`
- **โค้ด Python = MCP client + ผู้คุม flow**: spawn MCP server เอง, handshake, เป็นเจ้าของ loop, จำนวน step, allowlist, denylist, verify, การหยุด, หลักฐาน
หัวใจเฉพาะของบทนี้: **MCP ตัวเดียวกัน ใครเป็น client คนนั้นคุม** — ถ้าต่อ MCP เข้ากับ LLM โดยตรง (yolo1 ปกติ) = LLM-in-control; ถ้าโค้ดเป็น client และ LLM แค่ตอบ JSON = code-in-control
Loop: Observe → Decide → Validate→Act → Verify, ref ใช้ได้กับ snapshot ล่าสุดเท่านั้น, verify ด้วยโค้ด (oracle), prompt คือคำขอร้อง โค้ดคือกฎหมาย

ทฤษฎีที่ต้องเพิ่มจากบท CLI:
- MCP คืออะไร: host / client / server, transport stdio (และ HTTP ถ้ามี `--port`), JSON-RPC 2.0 (id, method, params, result/error), ลำดับ `initialize` → `notifications/initialized` → `tools/list` → `tools/call`, content blocks (text / image), `isError`
  แสดงข้อความ JSON-RPC **จริง** ที่ส่ง/รับ (ตัดให้สั้น)
- **ความแตกต่าง playwright-mcp vs playwright-cli** (ส่วนสำคัญ ต้องมีตารางละเอียด + ตัวเลขวัดจริง): process model, interface (tool + JSON schema vs คำสั่ง shell), การได้ snapshot (อัตโนมัติหลัง action? เต็มหรือ diff?), ref format, box/พิกัด, screenshot (base64 ใน response vs ไฟล์), session/อายุเบราว์เซอร์, config, ขนาด output ต่อ action (วัด bytes/บรรทัดจริงของ action เดียวกันทั้งสองแบบ), ใครเหมาะใช้อะไร, ผลต่อ token, ความเสี่ยงด้านความปลอดภัย
  (ใน container มี playwright-cli ตามวิธี LAB 1 ของบท CLI — สร้าง wrapper ใน /usr/local/bin ได้เพื่อวัดเทียบ)

## 3. โจทย์สาธิต (เหมือนบท CLI ทุกประการ)
- https://www.google.com/travel/flights?hl=en · One way · Suvarnabhumi Airport (BKK) → Tokyo, Japan · Economy · ผู้ใหญ่ 1
- วันเดินทาง = วันที่ 15 ของเดือนถัดไป คำนวณในโค้ด พิมพ์ลง log
- ค้นหาอย่างเดียว ห้ามล็อกอิน/จอง/Select flight/Select fare/กรอกข้อมูลส่วนตัว/จ่ายเงิน — บังคับด้วยโค้ด (denylist ชื่อ element จริงใน snapshot → หยุดทั้ง run), ปิด cookie/consent ได้แค่ Reject all
- CAPTCHA / unusual traffic / element หาไม่เจอ → หยุดและรายงานพร้อมหลักฐาน ห้ามหลบ
- 3 อันดับแรกอ่านจาก snapshot ด้วยโค้ด พร้อมเลขบรรทัดที่มา ห้ามเดาราคา

## 4. หลักฐานทุก action: `log/steps/NN_<เป้าหมาย>-<action>/`
`snapshot.yml` (snapshot เต็มก่อนตัดสินใจ), `prompt.txt`, `decision.json` (คำตอบ LLM ดิบ + ผล validate ทีละข้อ + ผล verify),
`page.png` (ภาพจริงก่อนกด วงรีแดงรอบ element + callout "Step N · click <ref>" ไม่บัง element — inject overlay ผ่าน tool evaluate ด้วย createElement/createElementNS ห้าม innerHTML แล้ว screenshot แล้วลบ overlay),
`act.txt` (tool call ที่ส่งจริง + ผลย่อ + ผล verify + ref เดิมยังอยู่ไหม), `verify.yml`, และ **`rpc.jsonl`** (ข้อความ JSON-RPC ดิบที่ส่ง/รับใน step นั้น ตัดข้อมูลภาพ base64 ออก) + `log/run.log`
ตำแหน่ง element (box): ถ้า MCP ไม่ให้ box ใน snapshot ให้หาเองด้วย tool evaluate บน ref (getBoundingClientRect) และสอนว่านี่คือความต่างจาก CLI

## 5. ลำดับงาน (แบ่งเป็นเฟส ผู้ควบคุมจะสั่งทีละเฟส)
- **เฟส 1 · สำรวจและยืนยันของจริง** → `.work_mcp/notes.md` + ผลดิบใน `.work_mcp/probe/`
- **เฟส 2 · โค้ดอ้างอิง + รันจริง + หลักฐาน** → `.work_mcp/ref/` (mcp_client.py, agent.py ฯลฯ) และคัดหลักฐานไป `01_playwright-mcp/log/`
- **เฟส 3 · ภาพ** → ภาพแนวคิดด้วย `cyolo1` + skill imagegen (ใส่ "ภาพแนวคิด (Imagegen)" ใต้ภาพ) และภาพ compare จากหน้าเว็บจริง (ซ้ายภาพจริงมีกรอบสี+เลข, ขวาบรรทัด YAML สีและเลขตรงกัน แบบ `00_playwright-cli/img/lab*-compare.png`)
- **เฟส 4 · เขียน README.md** ตามโครงบท CLI
- **เฟส 5 · ทดสอบพรอมต์แบบนักศึกษา** ทุก LAB ใน /workspace ที่สะอาด ด้วย `yolo1 -p --model sonnet "<พรอมต์>"` ใน container ไล่ LAB 1→7 ต่อกัน แล้วแก้ README ให้ตรงผลจริง

## 6. การตัดสินใจหลังเฟส 1 (จากผู้ควบคุม)
- ห้ามแก้ /root/ai-accounts/.Claude/shared/mcp/mcp.json และไฟล์ของ Codex ใน volume (เป็นของส่วนกลาง) — ถ้าต้องสาธิต LLM-in-control ให้ใช้ --mcp-config ของงานเองที่ PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
- README ส่วน C ให้บันทึกอาการ Browser chrome-for-testing is not installed และวิธีแก้ (ชี้ PLAYWRIGHT_BROWSERS_PATH ไป /ms-playwright) เป็นปัญหาที่พบจริง
- พรอมต์นักศึกษาใช้ code-in-control ซึ่ง spawn server เองด้วย env ที่ถูก จึงไม่ขึ้นกับไฟล์นั้น
