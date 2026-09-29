# LAB 001 · ส่วนที่ 1: ใช้งานหลายบัญชีผ่าน JupyterLab (Claude Code + Codex CLI)

เวลาโดยประมาณสำหรับส่วนนี้: 35–50 นาที ขึ้นอยู่กับการตั้งค่าหลายบัญชีและล็อกอิน

**สิ่งที่จะได้:** ใช้เครื่องมือจาก LAB ก่อนหน้าเพื่อตั้งค่าหลายบัญชี ล็อกอิน เลือกโมเดล และตรวจว่า skill และ MCP ส่วนกลางใช้ได้จริงจากหลายบัญชี ผ่าน Terminal ใน JupyterLab

บทเรียนที่เชื่อมโยง: [AI Agent Routing](../ai-agent-routing.html) หัวข้อ 1.0 และ 4.0–4.3

ขอบเขต: Claude Code และ Codex CLI เท่านั้น

## 0 · ก่อนเริ่ม · ใช้ JupyterLab จาก LAB ก่อนหน้า

แลปนี้ทำทุกขั้นผ่าน **Terminal ใน JupyterLab ของ Linux container `devtools`** ที่เตรียมจาก [บท Docker และ VS Code](../01_Docker_VSCode_Setup/README.md) ให้ Docker และ container ทำงานอยู่ก่อนเริ่ม

### 0.1 · เปิด JupyterLab จาก VS Code (ทบทวนหัวข้อ 6.1 ของ LAB ก่อนหน้า)

1. ในหน้าต่าง **VS Code บนเครื่องผู้เรียน** เปิดแถบ **Containers** ทางซ้าย
2. คลิกขวาที่ container **devtools** แล้วเลือก **Open in External Browser**
3. เลือก **8888 localhost:8885** โดย `8888` คือพอร์ตภายใน container และ `8885` คือพอร์ตบนเครื่องผู้เรียน หาก LAB ก่อนหน้าใช้พอร์ตอื่น ให้เลือกรายการที่แมปจาก `8888` มายังพอร์ตนั้น
4. เบราว์เซอร์จะเปิด JupyterLab หากต้องการเปิดเอง สามารถเข้า [JupyterLab](http://localhost:8885/lab) โดยปรับพอร์ตให้ตรงกับที่ใช้จริง

![คลิกขวาที่ devtools ใน VS Code เลือก Open in External Browser แล้วเลือกพอร์ต JupyterLab](img/jupyter-open-from-vscode.png)

*นำภาพจากหัวข้อ 6.1 ของ LAB ก่อนหน้ามาใช้ซ้ำ: ภาพจากหน้าจอจริงที่ปรับด้วย Imagegen เพื่อซ่อนรายการที่ไม่เกี่ยวข้องและเน้นจุดที่ต้องเลือก*

เมื่อเปิด JupyterLab แล้ว ไปขั้นที่ 1 เพื่อคลิก Terminal ตามภาพ จากนั้นใช้ Terminal นี้ทำขั้นที่ 2

**อ่านสัญลักษณ์ให้ถูก:** 🖥️ Terminal / shell หมายถึง Terminal ใน JupyterLab ส่วน 💬 ช่องสนทนา AI หมายถึงหน้าสนทนาของ Claude Code หรือ Codex CLI ที่เปิดอยู่ใน Terminal นั้น คำสั่ง Bash พิมพ์ที่ shell; พรอมต์ยาวและคำสั่ง `/login` หรือ `/model` พิมพ์ในหน้าสนทนาของ CLI ที่ระบุ ไม่ต้องสร้าง Notebook หรือวางคำสั่งในเซลล์ Python

Terminal ทำงานบนเครื่องที่รัน Jupyter server ซึ่งในแลปนี้คือ container ไม่ใช่บนเบราว์เซอร์ ตาม [เอกสาร JupyterLab Terminal](https://jupyterlab.readthedocs.io/en/stable/user/terminal.html) การล็อกอินอาจเปิดหน้าเว็บแยก ให้ผู้เรียนยืนยันตัวตนเองแล้วกลับมาทำงานใน Terminal

### 0.2 · เส้นทางการเรียนรู้

| ส่วน | เนื้อหา | เอกสาร |
|---|---|---|
| **1 · ตั้งค่าหลายบัญชีและใช้งานเบื้องต้น** | ขั้นที่ 1–3: เปิด Claude Code ตั้งค่าหลายบัญชี ล็อกอิน เลือกโมเดล และตรวจ skill/MCP ส่วนกลาง | ไฟล์นี้ |

ทำตามขั้นที่ 1–3 เพื่อใช้เครื่องมือที่มีอยู่แล้วกับบัญชีที่แยกการตั้งค่ากัน

## ขั้นที่ 1 · เปิด Terminal ใน JupyterLab (~5 นาที)

ใช้เครื่องมือที่ติดตั้งไว้ใน `devtools` จาก LAB ก่อนหน้า ไม่ต้องติดตั้งซ้ำหรือสร้างโฟลเดอร์เพิ่มด้วยตนเอง

### 1.1 · คลิก Terminal ในหน้า Launcher

คลิก **Terminal** ในกลุ่ม **Other** ตามวงกลมและลูกศรในภาพ หากไม่เห็นหน้า Launcher ให้กดปุ่ม **+** ก่อน

![วงกลมและลูกศรชี้ปุ่ม Terminal ในกลุ่ม Other ของ JupyterLab Launcher](img/jupyter-launcher-terminal-highlight.png)

*ภาพ Launcher จาก LAB ก่อนหน้า เพิ่มวงกลม ลูกศร และคำกำกับด้วย Imagegen เพื่อชี้ตำแหน่งที่ต้องคลิก*

**หลังคลิก:** จะมีแท็บ Terminal เปิดขึ้นมา พร้อม shell สำหรับพิมพ์คำสั่งภายใน container

## ขั้นที่ 2 · ให้ Claude Code ตั้งค่าหลายบัญชี (~20 นาที)

ให้ Claude Code ตรวจเครื่องมือที่ติดตั้งไว้จาก LAB ก่อนหน้า และสร้างคำสั่ง `yolo1`–`yolo5` กับ `cyolo1`–`cyolo5` สำหรับใช้งานหลายบัญชี โดยแยกข้อมูลแต่ละบัญชีและยังไม่ล็อกอินบัญชีเหล่านี้

ใช้ Terminal ที่เปิดจากขั้นที่ 1 สำหรับตั้งค่าด้วยพรอมต์ด้านล่าง โดยเปิด Claude Code ด้วยคำสั่ง `claude` และล็อกอินบัญชีตัวช่วยตั้งค่าให้พร้อมก่อนวางพรอมต์ บัญชีแยกทั้ง 10 ช่องจะให้ผู้เรียนล็อกอินเองในขั้นที่ 3 **เปิดเซสชันตั้งค่านี้ค้างไว้** เพราะจะกลับมาใช้ทดสอบต่อในหัวข้อ 3.3

### 2.1 · ทำไมเราต้องใช้พรอมต์ตั้งค่าชุดนี้?

ลองนึกว่ามีลิ้นชักแยกตามบัญชี: คำสั่ง `yolo1` เลือกลิ้นชักของ Claude บัญชีที่ 1 ส่วน `yolo2` เลือกบัญชีที่ 2 ใช้โปรแกรม CLI เดิม แต่ชี้ไปยังข้อมูลคนละชุด ผู้เรียนจึงไม่ต้องจำคำสั่งกำหนดโฟลเดอร์ยาว ๆ ทุกครั้ง หลักเดียวกันใช้กับ `cyolo1`–`cyolo5` ของ Codex

![เหตุผลที่ตั้งค่าหลายบัญชีผ่าน JupyterLab Terminal ใน Linux container](img/multi-account-01-why.png)

*ภาพแนวคิดสร้างด้วย Imagegen ไม่ใช่ภาพหน้าจอหรือหลักฐานว่าติดตั้งแล้ว ภาพแสดงบางบัญชีเพื่อให้อ่านง่าย; พรอมต์สร้างช่องบัญชีเครื่องมือละ 5 ช่อง*

| สิ่งที่พรอมต์กำหนด | ช่วยผู้เรียนอย่างไร |
|---|---|
| คำสั่งสั้นแยกตามบัญชี | เลือกบัญชีได้ชัด และเปิด Terminal หลายแท็บเพื่อใช้คนละบัญชีได้ |
| โฟลเดอร์การตั้งค่าต่อบัญชี | ลดการปะปนของการตั้งค่าและประวัติ โดยต้องตรวจวิธีเก็บ credential ของ CLI ด้วย |
| Skills/MCP ส่วนกลางต่อเครื่องมือ | ดูแลต้นฉบับร่วมกันได้ เมื่อเชื่อมด้วยวิธีที่ CLI รองรับ |
| ตรวจเวอร์ชันและ help ก่อนสร้าง | ให้ AI สร้างคำสั่งแยกบัญชีให้ตรงกับเครื่องมือที่ติดตั้งไว้แล้ว |
| ติดตั้งซ้ำได้และมีรายงาน | ตรวจสอบผลได้ และลดโอกาสเขียนทับการตั้งค่าเดิม |

ข้อดีเหล่านี้เป็นเหตุผลของการออกแบบแลป ไม่ใช่ผลทดสอบของเครื่องผู้เรียน พรอมต์สร้างตัวช่วยเลือกบัญชีที่มีอยู่ ไม่ได้สมัครบัญชีหรือเพิ่มสิทธิ์ใช้งานให้ และผู้เรียนต้องล็อกอินแต่ละบัญชีเอง

### 2.2 · โฟลเดอร์ที่ได้ และความหมายของส่วนกลาง

![โครงสร้าง ai-accounts แยก Claude และ Codex พร้อมโฟลเดอร์รายบัญชีและ shared](img/multi-account-02-folders.png)

*ภาพแนวคิดสร้างด้วย Imagegen แสดงโครงสร้างเป้าหมายตามพรอมต์ โดย `shared` เป็นโฟลเดอร์ระดับเดียวกับโฟลเดอร์บัญชีภายในแต่ละ CLI*

- พรอมต์จะสร้างโฟลเดอร์การตั้งค่าบัญชีใต้ `~/ai-accounts` ส่วนรายงานจะเขียนในโฟลเดอร์ปัจจุบันที่เปิด Claude Code ไม่ต้องสร้างโฟลเดอร์เตรียมเอง
- Claude Code เลือกโฟลเดอร์การตั้งค่าด้วย `CLAUDE_CONFIG_DIR` ซึ่งเอกสารระบุว่าใช้กับหลายบัญชีพร้อมกันได้ ดู [Claude Code environment variables](https://code.claude.com/docs/en/env-vars)
- Codex เลือกที่เก็บการตั้งค่าและสถานะด้วย `CODEX_HOME` ดู [Codex configuration](https://learn.chatgpt.com/docs/config-file/config-advanced) ส่วน credential อาจเก็บเป็นไฟล์หรือในระบบจัดเก็บของ OS จึงต้องตรวจโหมดที่ใช้ ดู [Codex authentication](https://learn.chatgpt.com/docs/auth)
- การตั้งชื่อโฟลเดอร์ `shared/skills` หรือ `shared/mcp` ไม่ทำให้ CLI อ่านเอง ต้องมีวิธีเชื่อมที่รองรับ และไม่รวม token หรือข้อมูลล็อกอินไว้ในส่วนกลาง
- การแยก config เป็นการจัดระเบียบภายใต้ผู้ใช้ Linux เดียวกัน ไม่ใช่การแยกสิทธิ์ OS; ไฟล์โครงการและการตั้งค่าระดับโครงการอาจยังใช้ร่วมกันได้

### 2.3 · จากคำสั่งสั้นไปถึงบัญชีที่เลือก

![คำสั่ง yolo และ cyolo ผ่าน wrapper เพื่อเลือกโฟลเดอร์บัญชีก่อนเปิด CLI](img/multi-account-03-commands.png)

*ภาพแนวคิดสร้างด้วย Imagegen: wrapper คือสคริปต์ตัวช่วยที่ตั้งค่าโฟลเดอร์บัญชีแล้วเรียกโปรแกรม CLI; พาธในภาพอยู่ภายใต้ `~/ai-accounts`*

หลังตั้งค่าและล็อกอินแล้ว `yolo1` เปิด Claude ด้วยข้อมูลบัญชีที่ 1 ส่วน `yolo2` เปิดด้วยข้อมูลบัญชีที่ 2 และ `cyolo1` เปิด Codex ด้วยข้อมูลบัญชีที่ 1 คำสั่งเหล่านี้สร้างโดยแลป ไม่ใช่คำสั่งมาตรฐานของ Linux

หากต้องการเปลี่ยนบัญชีใน Terminal เดิม ให้ออกจาก CLI กลับมาที่ shell แล้วเรียกคำสั่งของบัญชีถัดไป หรือเปิด Terminal อีกแท็บเพื่อใช้พร้อมกัน การพิมพ์ชื่อ wrapper ในช่องสนทนา AI ไม่ใช่การสลับบัญชีของโปรแกรมที่กำลังเปิดอยู่

### 2.4 · วางพรอมต์ตรงไหนใน JupyterLab?

#### 2.4.1 · พิมพ์คำสั่งเปิด Claude ใน Terminal ก่อน

ใช้ Terminal ที่เปิดจากหัวข้อ 1.1 โดยอยู่ในโฟลเดอร์งานที่ต้องการ แล้วพิมพ์ `claude` และกด Enter เพื่อเปิดโปรแกรม

![พิมพ์ claude ใน Terminal ของ JupyterLab เพื่อเปิด Claude Code](img/devtools-open-claude-simple.png)

#### 2.4.2 · ล็อกอินบัญชีตัวช่วยตั้งค่าให้พร้อม

หากเปิดครั้งแรก ให้เลือกธีมตามหน้าจอ จากนั้นเลือก **Claude account with subscription** และยืนยันบัญชีของตนเองในเบราว์เซอร์ หากล็อกอินไว้แล้วให้ไปขั้นถัดไปได้

![หน้าล็อกอิน Claude Code ภายใน Terminal ของ JupyterLab บน devtools](img/devtools-claude-login-jupyter.png)


#### 2.4.3 · วางพรอมต์ในช่องสนทนาของ Claude

เมื่อเห็นช่องสนทนาพร้อมใช้งาน ให้คัดลอกข้อความทั้งกรอบด้านล่าง วางใน **ช่องสนทนาของ Claude Code ภายใน Terminal** แล้วกด Enter หากวางไม่ได้ ให้ลอง **Shift + คลิกขวา → Paste** ตามที่เบราว์เซอร์รองรับ รอ Claude ทำงานและสรุปรายงาน แล้วตรวจผลตามรายการท้ายขั้นนี้

##### 2.4.3.1 · 📋 พรอมต์สำหรับคัดลอก (คัดลอกทั้งกรอบ วางใน 💬 ช่องสนทนา AI แล้ว Enter)
```text
สร้างระบบหลายบัญชีใน Linux container devtools (ใช้ผ่าน JupyterLab Terminal)
Claude Code และ Codex CLI ติดตั้งไว้แล้ว ห้ามติดตั้งซ้ำ ตรวจ --version ก่อน ถ้าไม่พบให้รายงานปัญหา PATH แล้วหยุด
ห้ามอ่าน README ของ LAB เพื่อหาเฉลย ตรวจ official docs และ --help ของเวอร์ชันจริงก่อน ห้ามเดา env/path/flag

BASE_PATH="$HOME/ai-accounts"   # แก้ที่นี่ที่เดียว

## เป้าหมาย
- yolo1..yolo5   → claude --dangerously-skip-permissions  (CLAUDE_CONFIG_DIR=$BASE_PATH/.Claude/yoloN)
- cyolo1..cyolo5 → codex --dangerously-bypass-approvals-and-sandbox  (CODEX_HOME=$BASE_PATH/.Codex/cyoloN)
- $BASE_PATH/.Claude/shared และ .Codex/shared มี skills/ และ mcp/mcp.json ({"mcpServers":{...}}) แก้ครั้งเดียว ทุกบัญชีของ CLI นั้นเห็นตอนเปิดครั้งถัดไป โดยไม่ต้องรัน installer ซ้ำ
- wrapper ส่งต่อ "$@" ครบ แจ้งชัดถ้าโฟลเดอร์บัญชีไม่มี ไม่พิมพ์ secret

## กติกา
- แยก credential/config/session ต่อบัญชี เปิดพร้อมกันได้ ใช้ CLAUDE_CONFIG_DIR/CODEX_HOME เท่านั้น ห้ามเปลี่ยน $HOME
- Codex ใช้ file-based credential ต่อ CODEX_HOME ระบุสิ่งที่ยังร่วมกัน (project config, ผู้ใช้ Linux) ห้ามอ้างว่าเป็น OS isolation
- ห้ามแก้ .bashrc/Git/SSH ถ้าต้องเพิ่ม PATH ให้ขอยืนยันก่อน
- installer รันซ้ำได้ ไม่เขียนทับ credential/config เดิม ห้ามแชร์ credential ใน shared
- MCP ส่วนกลางตัวแรก: Playwright (@playwright/mcp) + Chromium ติดตั้งครั้งเดียว
- skill ตัวอย่าง shared-check: ตอบ SHARED_SKILL_OK-<tool>-<ค่าสุ่มตอนติดตั้ง> ซึ่งมีในไฟล์นี้เท่านั้น

## ข้อเท็จจริงจากการทดลอง (ตรวจว่ายังจริงกับเวอร์ชันนี้)
- root ต้องตั้ง IS_SANDBOX=1; CODEX_HOME ต้อง mkdir -p ก่อน
- Claude: skill อ่านจาก $CLAUDE_CONFIG_DIR/skills; MCP ส่งผ่าน --mcp-config=<ไฟล์> (ต้องมี =)
  ห้าม symlink .claude.json (มีสถานะล็อกอิน); claude mcp list ไม่แสดง MCP นี้ ให้ตรวจด้วย /mcp
- Codex: skill อ่านจาก $CODEX_HOME/skills และเขียน skills/.system เอง ห้าม symlink ทั้งโฟลเดอร์
  ห้ามใช้ ~/.agents/skills เป็นทางลัด; MCP ส่งด้วย -c mcp_servers.<name>={...} (ใช้กับ codex mcp list ได้)
- Playwright ใน root container: --browser chromium --headless --isolated --no-sandbox และ --output-dir นอกโฟลเดอร์งาน
  ติดตั้ง Chromium ด้วย playwright ในแพ็กเกจ @playwright/mcp ให้เวอร์ชันตรงกัน
- Codex ใน container ล็อกอินด้วย codex login --device-auth; login status ไม่ยืนยัน token ให้ทดสอบด้วย codex exec

## ทดสอบ (PASS/FAIL/SKIP ตามจริง)
- 10 คำสั่ง --version ครบ, config root คนละโฟลเดอร์ (find), installer รอบ 2 ไม่ทำลายของเดิม, Git/SSH ปกติ
- cyoloN mcp list เห็น playwright, skill shared-check ทุกบัญชี readlink -f ไปไฟล์เดียวกันใน shared
- อะไรที่ต้องล็อกอิน = SKIP

## รายงาน (ห้ามมี secret) ในโฟลเดอร์ปัจจุบัน
- setup-report.md: config root, ตำแหน่ง credential, แต่ละ CLI อ่าน skill/MCP จากไหน และเชื่อม shared อย่างไร, ข้อจำกัด
- login-guide.md: ล็อกอินทีละบัญชี และวิธีตรวจ skill/MCP หลังล็อกอิน
- checklist.md: รายการ | หลักฐาน | PASS/FAIL/SKIP | เหตุผล
เสร็จแล้วแสดงสาระสำคัญเป็นตาราง แล้วหยุดรอ ห้ามล็อกอินแทนฉัน ห้ามทำขั้นถัดไปเอง
```

![ขยายข้อความพรอมต์ตั้งค่าหลายบัญชีในช่องป้อน Claude Code บน JupyterLab ของ devtools](img/devtools-prompt-expanded.png)

ภาพหน้าจอจริงจาก JupyterLab ของคอนเทนเนอร์ `devtools` แสดงช่วงต้นของพรอมต์ในช่องป้อน โดยขยายข้อความที่ CLI ย่อไว้เป็น `[Pasted text …]` ด้วยการวางข้อความเดิมอีกครั้งตามตัวเลือก `Paste again to expand` ของเวอร์ชันที่ใช้ ภาพนี้ถ่ายจากพรอมต์ฉบับก่อนย่อ ข้อความจึงต่างจากกรอบด้านบนเล็กน้อย สำหรับการทำแลป ให้ตรวจพรอมต์ครบแล้วกด Enter เพื่อเริ่มทำงาน

### 2.5 · ผลหลังส่งพรอมต์และตั้งค่าเสร็จ (การสาธิตจริงใน devtools)

หลังวางพรอมต์แล้วกด Enter ให้รอ Claude ตรวจเครื่องมือ สร้างตัวติดตั้ง และทดสอบจนแสดงสรุปผล ภาพต่อไปนี้เป็นผลจากการรันจริงในคอนเทนเนอร์ `devtools` วันที่ 23 กันยายน 2026 ไม่ใช่ภาพจำลอง

![Claude สรุปผลตั้งค่าหลายบัญชีเสร็จใน JupyterLab ของ devtools](img/devtools-setup-complete.png)

### 2.6 · เปิดดูโฟลเดอร์ที่สร้างจริงผ่าน File Browser

#### 2.6.1 · เปิดโฟลเดอร์ ai-accounts

1. คลิกไอคอนรูปโฟลเดอร์ **File Browser** ที่แถบซ้ายสุดของ JupyterLab
2. กลับไปที่โฟลเดอร์บนสุด `/` แล้วดับเบิลคลิก **root** จากนั้นดับเบิลคลิก **ai-accounts**
3. ตรวจแถบตำแหน่งด้านบนให้เป็น **/ root / ai-accounts /** ตามวงกลมสีแดง ภายในจะเห็นโฟลเดอร์ **.Claude** และ **.Codex**

![ขยาย File Browser พร้อมวงกลมที่ root ai-accounts และลูกศรชี้ลำดับการเปิดดู .Claude และ .Codex](img/devtools-folder-navigation.png)

#### 2.6.2 · เปิดดูบัญชี Claude และ shared

ดับเบิลคลิก **.Claude** ใน File Browser จะเห็น **yolo1–yolo5** และ **shared** ตามโครงสร้างในหัวข้อ 2.2 ตรวจแถบตำแหน่งให้ลงท้ายด้วย **ai-accounts / .Claude /**

![File Browser ใน JupyterLab แสดงโฟลเดอร์จริง yolo1 ถึง yolo5 และ shared ภายใน .Claude](img/devtools-claude-account-folders-annotated.png)

ดับเบิลคลิก **shared** จะเห็นโฟลเดอร์ **mcp** และ **skills** ของ Claude

![โฟลเดอร์ mcp และ skills จริงภายใน .Claude shared ใน JupyterLab](img/devtools-claude-shared-folders-annotated.png)

#### 2.6.3 · เปิดดูบัญชี Codex และ shared

กลับไปที่ **ai-accounts** โดยคลิกแถบตำแหน่งด้านบน หากชื่อถูกย่อเป็น **…** ให้คลิกตำแหน่งนั้นเพื่อกลับขึ้นไป จากนั้นดับเบิลคลิก **.Codex** จะเห็น **cyolo1–cyolo5** และ **shared** ตามโครงสร้างในหัวข้อ 2.2

![File Browser ใน JupyterLab แสดงโฟลเดอร์จริง cyolo1 ถึง cyolo5 และ shared ภายใน .Codex](img/devtools-codex-account-folders-annotated.png)

ดับเบิลคลิก **shared** จะเห็นโฟลเดอร์ **mcp** และ **skills** ของ Codex

![โฟลเดอร์ mcp และ skills จริงภายใน .Codex shared ใน JupyterLab](img/devtools-codex-shared-folders-annotated.png)

### 2.7 · 🔍 จุดที่ผู้เรียนต้องตรวจ (🖥️ เปิด Terminal อีกแท็บใน JupyterLab)

กด **+ → Terminal** เพื่อเปิดอีกแท็บ คัดลอกคำสั่งทั้งสามบรรทัดในกรอบด้านล่าง วางพร้อมกันใน Terminal แล้วกด **Enter** เพื่อรันทั้งชุด:
```bash
yolo1 --version; cyolo1 --version
yolo2 --version; cyolo2 --version
yolo3 --version; cyolo3 --version
```

![วางคำสั่งทั้งสามบรรทัดพร้อมกันแล้วกด Enter แสดงผลเวอร์ชันครบหกคำสั่งใน JupyterLab](img/devtools-versions-block-paste.png)


## ขั้นที่ 3 · ล็อกอินและตรวจการแชร์ข้ามบัญชี (~15 นาที)

ใช้บัญชี `yolo1` และ `cyolo1` จากขั้นที่ 2 ผ่าน JupyterLab Terminal โดยใช้โฟลเดอร์งานเดียวกับตอนตั้งค่าในขั้นที่ 2 ตลอดแลป ทำหัวข้อ 3.1 ของ Claude Code แล้วทำหัวข้อ 3.2 ของ Codex จากนั้นกลับไปเซสชันตั้งค่าเพื่อทดสอบในหัวข้อ 3.3

ทำตามลำดับ **พิมพ์คำสั่งเปิดโปรแกรมใน Terminal → ล็อกอิน → เข้าหน้าสนทนา → เลือกโมเดล**

ผู้เรียนยืนยันตัวตนในเบราว์เซอร์ด้วยตัวเอง ไม่ส่งรหัสหรือข้อมูลบัญชีให้ AI

---

### 3.1 · Claude Code (yolo1)

#### 3.1.1 · เปิดโปรแกรมและล็อกอิน

##### 3.1.1.1 · พิมพ์คำสั่งเปิดบัญชีใน Terminal

ใน JupyterLab กด **+ → Terminal** แล้วพิมพ์คำสั่งต่อไปนี้ที่ shell และกด **Enter**

```bash
yolo1
```

![พิมพ์ yolo1 ใน Terminal ของ JupyterLab เพื่อเปิด Claude บัญชีแรก](img/devtools-yolo1-open.png)

##### 3.1.1.2 · เลือกวิธีล็อกอิน

หากบัญชีนี้ล็อกอินไว้แล้ว โปรแกรมอาจข้ามหน้าล็อกอิน ให้ไปต่อที่หัวข้อ 3.1.2 เพื่อเลือกโมเดล

หากมีหน้าจอเลือกธีม ให้เลือกธีมก่อน จากนั้นเลือก **Claude account with subscription** แล้วกด Enter

![เปิด yolo1 ในพื้นที่สาธิตที่ยังไม่ล็อกอิน แล้วเข้าสู่หน้าเลือกวิธีล็อกอินใน JupyterLab](img/devtools-yolo1-first-login.png)

##### 3.1.1.3 · ยืนยันบัญชี โฟลเดอร์ และเข้าสู่หน้าสนทนา

เปิดลิงก์ที่ Terminal แสดง ล็อกอินด้วยบัญชี Claude ที่มี subscription และยืนยันการเชื่อมต่อ หากหน้าจอให้คัดลอกรหัสกลับมา ให้ทำตามขั้นตอนนั้นด้วยตัวเอง

กลับมาที่ Terminal หากเป็นโฟลเดอร์แลปที่เตรียมไว้ ให้เลือก **Yes, I trust this folder**

![Claude Code ให้ยืนยันโฟลเดอร์งานใน JupyterLab](img/devtools-yolo1-trust.png)

คำสั่ง yolo1 จากขั้นที่ 2 เปิดโหมด Bypass Permissions หากมีหน้าขอยืนยันในคอนเทนเนอร์แลปที่เตรียมไว้ ให้เลือก **Yes, I accept** เพื่อทำต่อ เมื่อยืนยันแล้ว แถบด้านล่างของหน้าสนทนาจะแสดง **bypass permissions on** ตามภาพ

![หน้าแรกหลังเปิด yolo1 ใน JupyterLab พร้อมช่องสนทนาว่างและแถบ bypass permissions on](img/devtools-yolo1-fresh-ready.png)

#### 3.1.2 · เลือก Fable

##### 3.1.2.1 · พิมพ์คำสั่งเลือกโมเดล

พิมพ์ `/model` ในช่องสนทนาของ Claude Code ตามภาพ แล้วกด **Enter** เพื่อเปิดรายการโมเดล

![พิมพ์คำสั่ง slash model ในช่องสนทนา Claude Code ภายใน JupyterLab](img/devtools-fable-model-command.png)

##### 3.1.2.2 · เลือก Fable และปรับเป็น Medium

ใช้ลูกศรขึ้น/ลงเลื่อนไปที่ **Fable** จากนั้นใช้ลูกศรซ้าย/ขวาปรับ effort เป็น **Medium** ตรวจชื่อและระดับให้ตรงกับภาพ แล้วกด **Enter** ยืนยัน ด้านบนของช่องสนทนาจะแสดง **Fable 5.1 with medium effort**

![เลือก Fable และ Medium effort จากเมนูจริงใน JupyterLab](img/devtools-fable-select-medium.png)

พิมพ์ `/exit` เพื่อกลับ shell แล้วล็อกอิน `yolo2` ด้วยวิธีเดียวกัน เพื่อใช้ทดสอบข้ามบัญชีในหัวข้อ 3.3

---

### 3.2 · Codex (cyolo1)

#### 3.2.1 · เปิดโปรแกรมและล็อกอิน

##### 3.2.1.1 · เปิดบัญชี Codex ใน Terminal

พิมพ์คำสั่งต่อไปนี้ใน Terminal ของ JupyterLab แล้วกด **Enter**

```bash
cyolo1
```

![พิมพ์ cyolo1 ใน Terminal พื้นขาวของ JupyterLab](img/devtools-cyolo1-open.png)

##### 3.2.1.2 · เลือกวิธีล็อกอินและยืนยันบัญชี

หากยังไม่ได้ล็อกอิน ให้เลือก **Sign in with ChatGPT** แล้วกด **Enter** จากนั้นยืนยันบัญชีในเบราว์เซอร์ หากใช้ container หรือ SSH แล้วเบราว์เซอร์กลับมาที่ CLI ไม่ได้ ให้เลือก **Sign in with Device Code** และทำตามขั้นตอนบนหน้าจอ หากบัญชีนี้ล็อกอินไว้แล้ว ให้ไปต่อหัวข้อ 3.2.1.3

![หน้าเลือกวิธีล็อกอิน Codex ใน JupyterLab จากพื้นที่สาธิตที่ยังไม่ล็อกอิน](img/devtools-cyolo1-login.png)

##### 3.2.1.3 · เข้าสู่หน้าสนทนา

กลับมาที่ Terminal หากมีคำถามยืนยันโฟลเดอร์ ให้ตรวจว่าเป็นโฟลเดอร์แลปที่เตรียมไว้ก่อนดำเนินการต่อ เมื่อเห็นชื่อโมเดลและช่อง **Ask Codex to do anything** ให้ไปเลือกโมเดลในหัวข้อ 3.2.2

![หน้าพร้อมสนทนาของบัญชี cyolo1 ใน JupyterLab](img/devtools-cyolo1-ready.png)

#### 3.2.2 · เลือก Astra

##### 3.2.2.1 · เลือกโมเดล

ในหน้าสนทนา Codex พิมพ์ `/model` แล้วกด Enter เลือก **gpt-6-astra** และกด Enter อีกครั้ง

![เลือก Astra ในหน้า Codex](img/devtools-astra-model.png)

##### 3.2.2.2 · ปรับ effort

หน้าถัดไปให้เลือกระดับ reasoning เป็น **Medium** แล้วกด Enter ยืนยัน

![เลือกระดับ Medium ของ Astra](img/devtools-astra-effort.png)

พิมพ์ `/exit` เพื่อกลับ shell แล้วล็อกอิน `cyolo2` ด้วยวิธีเดียวกัน เพื่อใช้ทดสอบข้ามบัญชีในหัวข้อ 3.3

---

### 3.3 · ตรวจการแชร์ Skill และ MCP ข้ามบัญชี (หลังล็อกอิน)

ใช้ตรวจว่า skill `shared-check` และ Playwright MCP ที่ตั้งไว้ใน `shared` เรียกใช้ได้จริงจากหลายบัญชี และให้ Playwright บันทึกภาพหน้าเว็บจริงเป็นหลักฐาน ต้องล็อกอิน `yolo1`, `yolo2`, `cyolo1`, `cyolo2` ให้ครบก่อน หากเบราว์เซอร์ส่งผลล็อกอิน Codex กลับเข้า container ไม่ได้ ให้ใช้ `cyolo1 login --device-auth` แทน

#### 3.3.1 · 🖥️ ตรวจการเชื่อม shared ใน Terminal

```bash
for a in yolo1 yolo2 cyolo1 cyolo2; do printf "%-7s " $a; $a --version 2>/dev/null; done
ls -l ~/ai-accounts/.Claude/yolo1/skills ~/ai-accounts/.Codex/cyolo1/skills/ | grep -E "skills|shared"
cyolo1 mcp list 2>/dev/null
```

ต้องเห็นว่า `yolo1/skills` ชี้ไป `../shared/skills` ส่วน `cyolo1/skills/shared-check` ชี้ไป `.Codex/shared/skills/shared-check` และ `cyolo1 mcp list` มี `playwright` สำหรับ Claude จะเห็น MCP จาก `--mcp-config` ด้วยคำสั่ง `/mcp` ในหน้าสนทนาเท่านั้น ไม่แสดงใน `claude mcp list`

![ตรวจเวอร์ชัน ลิงก์ skill ไปยัง shared และ MCP playwright ของ cyolo1 ใน JupyterLab Terminal](img/devtools-shared-setup.png)

#### 3.3.2 · 📋 พรอมต์ทดสอบต่อจากเซสชันตั้งค่า (วางใน 💬 เซสชัน Claude จากขั้นที่ 2)

กลับไปที่แท็บ Terminal ของเซสชัน Claude ที่ใช้ตั้งค่าในขั้นที่ 2 (ถ้าปิดไปแล้ว ให้พิมพ์ `claude --continue` ในโฟลเดอร์งานเดิม) แล้ววางข้อความทั้งกรอบ Claude จะส่งพรอมต์ตรวจช่วงล่างไปให้ทีละบัญชี เก็บภาพหน้าเว็บ และสรุปผลรวม การทดสอบนี้ **ค้นหาเที่ยวบินอย่างเดียว ไม่จองและไม่ชำระเงิน**

```text
ฉันล็อกอิน yolo1 yolo2 cyolo1 cyolo2 แล้ว ทดสอบ skill/MCP ส่วนกลางข้ามบัญชีต่อจากเซสชันนี้
1. บันทึกข้อความใต้เส้น ==== ตามตัวอักษรลง ~/verify-prompt.txt
2. รันทีละบัญชีจาก shell: yolo1 -p "$(cat ~/verify-prompt.txt)", yolo2 เช่นเดียวกัน,
   cyolo1 exec --skip-git-repo-check "$(cat ~/verify-prompt.txt)", cyolo2 เช่นเดียวกัน
   รันแบบ foreground ทีละบัญชี (ไม่ใช้ background) timeout บัญชีละ 15 นาที รอจนจบก่อนไปบัญชีถัดไป
3. คัดลอกภาพ screenshot ที่แต่ละบัญชีรายงานไปไว้ที่ ./evidence/<บัญชี>/ ห้ามแก้ไฟล์ตั้งค่า
4. สรุปตารางรวม บัญชี | config root | รหัส shared-check | tool ที่เรียก | เที่ยวบินอันดับ 1 | ภาพที่ได้ | PASS/FAIL
   บัญชีต่างกันแต่ CLI เดียวกันต้องได้รหัสเดียวกัน ถ้าบัญชีใดล้มเหลวให้รายงานตามจริง ห้ามแก้แทนหรือเดาผล
====
ตรวจว่า skill และ MCP ส่วนกลางใช้ได้จริงในบัญชีนี้ ทำตามลำดับ ห้ามแก้ไฟล์ตั้งค่าใด ๆ

1. แจ้ง config root ที่ใช้อยู่ (ค่า CLAUDE_CONFIG_DIR หรือ CODEX_HOME) ห้ามแสดง token อีเมล หรือข้อมูลบัญชี
2. ใช้ skill $shared-check ตามกลไก skill ของ CLI นี้ แล้วรายงานรหัสที่ได้ พร้อม path ของ skill ตามที่ CLI แสดง
   ห้ามค้นหาไฟล์เอง (find, grep, ls) และห้ามเปิดไฟล์จาก path ที่ไม่ได้มาจากรายการ skill ของ CLI
3. ใช้เครื่องมือของ MCP ชื่อ playwright เท่านั้น ห้ามใช้ curl, python, web search หรือ browser อื่น
   เปิด https://www.google.com/travel/flights?hl=en
   ค้นหาเที่ยวบินเที่ยวเดียว Bangkok (BKK) ไป Tokyo ญี่ปุ่น ชั้นประหยัด ผู้ใหญ่ 1 คน วันเดินทางคือวันที่ 15 ของเดือนถัดไป
   ค้นหาอย่างเดียว ห้ามกดจอง ห้ามกรอกข้อมูลส่วนตัว ห้ามชำระเงิน ห้ามล็อกอินเว็บไซต์ใด
   ถ้าหน้าเว็บไม่แสดงผล ให้รายงานตามจริงว่าติดตรงไหน ห้ามเดาราคา
4. บันทึกภาพหน้าจอด้วย tool screenshot ของ playwright 3 ภาพ: 1-open.png (หน้าเว็บเปิดได้),
   2-search.png (กรอกเงื่อนไขครบก่อนกดค้นหา), 3-results.png (รายการผลเที่ยวบิน) แล้วรายงาน path เต็มของแต่ละภาพ
5. สรุปเป็นตาราง รายการ | PASS/FAIL | หลักฐาน โดยมีแถว:
   - config root
   - รหัสจาก skill shared-check
   - ชื่อ MCP server และชื่อ tool ที่เรียกจริง
   - ภาพหน้าจอ 3 ภาพ (path)
   - เที่ยวบิน 3 อันดับแรก: สายการบิน เวลาออก-ถึง ระยะเวลา จำนวนแวะ ราคา (ตามที่เห็นบนหน้าเว็บ)
```

หากต้องการทดสอบเองทีละบัญชี ให้คัดลอกเฉพาะข้อความใต้เส้น `====` ไปวางใน 💬 ช่องสนทนาของบัญชีนั้น ใน Codex คำว่า `$shared-check` คือการเรียก skill ตามชื่อ

#### 3.3.3 · 🖼️ ดูภาพหน้าเว็บจริงที่ Playwright เก็บไว้

เปิด **File Browser** ของ JupyterLab ไปที่โฟลเดอร์งาน แล้วเปิด `evidence/` จะมีโฟลเดอร์ย่อยตามบัญชี แต่ละโฟลเดอร์มีภาพ 3 ภาพ ดับเบิลคลิกเพื่อดูในแท็บใหม่

| ภาพ | ต้องเห็นอะไร | พิสูจน์อะไร |
|---|---|---|
| `1-open.png` | หน้า Google Flights โหลดครบ | Chromium ของ Playwright MCP เข้าถึงเว็บจริงได้จากบัญชีนั้น |
| `2-search.png` | ช่อง BKK → Tokyo, One way, Economy, 1 adult และวันที่ 15 ของเดือนถัดไป | MCP กรอกฟอร์มบนหน้าเว็บได้ |
| `3-results.png` | รายการเที่ยวบินพร้อมเวลาและราคา | การค้นหาทำงานจริง ไม่ใช่คำตอบที่โมเดลเดา |

ภาพของแต่ละบัญชีควรคล้ายกัน แต่ราคาและลำดับเที่ยวบินอาจต่างกันตามเวลาที่ค้นหา หากบัญชีใดไม่มีภาพ `3-results.png` ให้ดูในตารางสรุปว่าติดขั้นไหน

#### 3.3.4 · ผลการทดลองจริง (29 กันยายน 2026)

ภาพต่อไปนี้ถ่ายจาก JupyterLab Terminal ของ container ทดลองหลังล็อกอินบัญชีจริง ส่งพรอมต์ด้วยวิธี shell และครอปเฉพาะส่วนผลลัพธ์

![yolo1 ได้รหัส SHARED_SKILL_OK-claude จาก skill และค้นเที่ยวบินผ่าน playwright MCP สำเร็จ](img/devtools-shared-yolo1.png)

![yolo2 เป็นอีกบัญชีแต่ได้รหัส skill เดียวกับ yolo1 และค้นเที่ยวบินผ่าน playwright MCP สำเร็จ](img/devtools-shared-yolo2.png)

![cyolo1 ได้รหัส SHARED_SKILL_OK-codex จาก skill และเรียก tool mcp__playwright__ สำเร็จ](img/devtools-shared-cyolo1.png)

![cyolo2 เป็นอีกบัญชีแต่ได้รหัส skill เดียวกับ cyolo1 และเรียก tool mcp__playwright__ สำเร็จ](img/devtools-shared-cyolo2.png)

| บัญชี | config root | รหัสจาก `shared-check` | Playwright MCP |
|---|---|---|---|
| yolo1 | `.Claude/yolo1` | `SHARED_SKILL_OK-claude-…` | PASS |
| yolo2 | `.Claude/yolo2` | รหัสเดียวกับ yolo1 | PASS |
| cyolo1 | `.Codex/cyolo1` | `SHARED_SKILL_OK-codex-…` | PASS |
| cyolo2 | `.Codex/cyolo2` | รหัสเดียวกับ cyolo1 | PASS |

**อ่านผลอย่างไร:** บัญชีต่างกันแต่ได้รหัสเดียวกัน แปลว่าอ่าน skill จากไฟล์เดียวกันใน `shared` และการเรียก tool ชื่อ `playwright` แปลว่า MCP ส่วนกลางถูกโหลดในบัญชีนั้น รหัสและราคาของแต่ละเครื่องจะต่างจากภาพ เพราะรหัสสุ่มตอนติดตั้งและราคาเปลี่ยนตามเวลา

**ข้อควรรู้:** Claude เรียก skill ผ่านเครื่องมือ `Skill` ส่วน Codex ไม่มีเครื่องมือแยก จะเปิด `SKILL.md` จาก path ที่ CLI ระบุในรายการ skill ซึ่งเป็นกลไกปกติของ Codex คำตอบของโมเดลเป็นเพียงคำบอกเล่า หากต้องการหลักฐานการเรียกจริง ให้ตรวจ log ของ session ใน `$CLAUDE_CONFIG_DIR/projects/` หรือ `$CODEX_HOME/sessions/`
