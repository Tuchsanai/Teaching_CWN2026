# Setup Multi Account

> [!IMPORTANT]
> **📋 กล่องสีม่วงที่ขึ้นต้นด้วย 📋 คือส่วนที่ต้องคัดลอกไปวาง** กดปุ่ม copy มุมขวาบนของกรอบโค้ด

## ทำไมต้องมีหลายบัญชี?

งานใหญ่ใช้บัญชีเดียวโควตาไม่พอและช้า จึงรวมหลายบัญชีไว้ใน container เดียว แล้วแบ่งงานทำพร้อมกัน

![ภาพรวม: องค์กรมีหลายบัญชีหลายแพ็กเกจ รวมไว้ใน container devtools เป็น yolo1–5 และ cyolo1–5 แล้วแบ่งงานใหญ่ทำขนานกันจนรวมผลได้](img/intro-01-why-multi-account.png)

![ภาพเคลื่อนไหว: แบบบัญชีเดียวทำทีละชิ้นและติดลิมิตต้องรอ เทียบกับหลายบัญชีทำ 6 ชิ้นพร้อมกันแล้วรวมผล](img/intro-03-parallel-flow.gif)

![ผู้ควบคุมงานแบ่งงานให้ Claude Code และ Codex CLI ตามจุดเด่น แล้วรวมผลและตรวจไขว้กัน](img/intro-04-mix-models.png)

## จุดเริ่มต้น → เป้าหมาย

เพิ่มระบบหลายบัญชีเข้าไปใน `devtools` ตัวเดิม **ขณะที่ยังรันอยู่** Claude ทำให้ทั้งหมด ยกเว้น **การล็อกอิน** ที่เราทำเอง

![Terminal จริงใน devtools ก่อนปรับ: มี claude และ codex แต่ไม่มี ai-accounts และไม่มีคำสั่ง yolo1 cyolo1](img/devtools-before-plain.png)

![ก่อนและหลัง: devtools เดิมเป็น Linux ธรรมดา หลังปรับมีโฟลเดอร์ ai-accounts แยก yolo และ cyolo พร้อม shared และคำสั่งใน /usr/local/bin](img/arch-01-before-after.png)

![Claude Code Desktop บน Windows ส่งคำสั่ง docker exec เข้าไปใน devtools ที่กำลังรัน เพื่อสร้างโฟลเดอร์ คำสั่ง yolo/cyolo และติดตั้ง skill กับ MCP กลาง](img/arch-02-desktop-outside.png)

## ภาพรวมการทดลอง

![ภาพเคลื่อนไหว: วางพรอมต์ใน Claude Code Desktop, Claude ใช้ docker exec สร้างโฟลเดอร์และคำสั่งใน devtools, เราล็อกอินใน JupyterLab, Claude ทดสอบทุกบัญชีจนผ่าน](img/arch-04-protocol-flow.gif)

| ขั้น | ทำที่ไหน | ใครทำ |
|---|---|---|
| **1 · ตั้งค่าหลายบัญชี** | 💻 Claude Code Desktop | Claude |
| **2 · ตรวจผลข้างใน** | 🖥️ JupyterLab ของ `devtools` | เรา |
| **3 · ล็อกอิน + ตรวจล็อกอิน** | 🖥️ JupyterLab → 💻 Claude Code Desktop | เรา + Claude |
| **4 · ทดสอบ skill/MCP ข้ามบัญชี** | 💻 Claude Code Desktop | Claude |

**ก่อนเริ่ม:** Docker Desktop ขึ้น **Engine running** · container `devtools` กำลังรัน · Claude Code Desktop ล็อกอินแล้ว

## ขั้นที่ 1 · 💻 ให้ Claude Code Desktop ตั้งค่าหลายบัญชี (~10 นาที)

![ภาพเคลื่อนไหว วางพรอมต์ปรับโครงสร้าง devtools ใน Claude Code Desktop ด้วย Ctrl+V แล้วกด Enter](img/desktop-setup-paste.gif)

> [!IMPORTANT]
> **📋 คัดลอกกล่องนี้ → Claude Code Desktop → New session → Ctrl+V → Enter แล้วรอจน Claude สรุปผล**
>
> ```text
> ช่วยปรับโครงสร้างข้างใน container ชื่อ devtools ที่กำลังรันอยู่ ให้รองรับหลายบัญชี AI
> ทำทุกอย่างข้างใน container ผ่าน docker exec เท่านั้น ห้ามแก้ไฟล์บนเครื่อง Windows ห้ามหยุด ลบ หรือสร้าง container ใหม่
> ถ้า devtools ไม่ได้รันอยู่ ให้รายงานแล้วหยุด
>
> ข้างในมี Claude Code และ Codex CLI แล้ว ห้ามติดตั้งซ้ำ ตรวจ --version ก่อน
> ตรวจ --help ของเวอร์ชันจริงก่อนใช้ env/flag ห้ามเดา
>
> ## เป้าหมาย (BASE=/root/ai-accounts)
> - yolo1..yolo5   → claude --dangerously-skip-permissions  (CLAUDE_CONFIG_DIR=$BASE/.Claude/yoloN)
> - cyolo1..cyolo5 → codex --dangerously-bypass-approvals-and-sandbox  (CODEX_HOME=$BASE/.Codex/cyoloN)
> - wrapper วางใน /usr/local/bin ให้พิมพ์ได้ทันที ส่งต่อ "$@" ครบ แจ้งชัดถ้าโฟลเดอร์บัญชีไม่มี ไม่พิมพ์ secret
> - $BASE/.Claude/shared และ $BASE/.Codex/shared มี skills/ และ mcp/ แก้ครั้งเดียว ทุกบัญชีของ CLI นั้นเห็นตอนเปิดครั้งถัดไป
>
> ## กติกา
> - แยก credential/config/session ต่อบัญชี เปิดพร้อมกันได้ ใช้ CLAUDE_CONFIG_DIR/CODEX_HOME เท่านั้น ห้ามเปลี่ยน $HOME
> - Codex ใช้ file-based credential ต่อ CODEX_HOME ห้ามแชร์ credential ใน shared
> - สร้าง installer เป็นไฟล์ใน container รันซ้ำได้ ไม่เขียนทับ credential/config เดิม ห้ามแก้ .bashrc/Git/SSH
> - MCP ส่วนกลางตัวแรก: Playwright (@playwright/mcp) + Chromium ติดตั้งครั้งเดียว
> - skill ตัวอย่าง shared-check: ตอบ SHARED_SKILL_OK-<tool>-<ค่าสุ่มตอนติดตั้ง> ซึ่งมีในไฟล์ skill เท่านั้น
>
> ## ข้อเท็จจริงจากการทดลอง (ตรวจว่ายังจริงกับเวอร์ชันนี้)
> - root ต้องตั้ง IS_SANDBOX=1; CODEX_HOME ต้อง mkdir -p ก่อน
> - Claude: skill อ่านจาก $CLAUDE_CONFIG_DIR/skills; MCP ส่งผ่าน --mcp-config=<ไฟล์> (ต้องมี =)
>   ห้าม symlink .claude.json (มีสถานะล็อกอิน); claude mcp list ไม่แสดง MCP นี้ ให้ตรวจด้วย /mcp
> - Codex: skill อ่านจาก $CODEX_HOME/skills และเขียน skills/.system เอง ห้าม symlink ทั้งโฟลเดอร์
>   MCP ส่งด้วย -c mcp_servers.<name>={...} (ใช้กับ codex mcp list ได้)
> - Playwright ใน root container: --browser chromium --headless --isolated --no-sandbox และ --output-dir นอกโฟลเดอร์งาน
>   ติดตั้ง Chromium ด้วย playwright ในแพ็กเกจ @playwright/mcp ให้เวอร์ชันตรงกัน (อาจต้อง install-deps)
>
> ## ทดสอบใน container (PASS/FAIL/SKIP ตามจริง)
> - 10 คำสั่ง --version ครบ, config root คนละโฟลเดอร์, installer รอบ 2 ไม่ทำลายของเดิม
> - cyoloN mcp list เห็น playwright, skill shared-check ทุกบัญชี readlink -f ไปไฟล์เดียวกันใน shared
> - อะไรที่ต้องล็อกอิน = SKIP
>
> ## รายงาน (ห้ามมี secret) เขียนไว้ใน container ที่ /workspace/multi-account/
> - setup-report.md: โครงสร้างโฟลเดอร์, wrapper, แต่ละ CLI อ่าน skill/MCP จากไหน, ข้อจำกัด
> - login-guide.md: ล็อกอินทีละบัญชีใน JupyterLab Terminal
> - checklist.md: รายการ | หลักฐาน | PASS/FAIL/SKIP
> เสร็จแล้วสรุปเป็นตารางสั้น ๆ แล้วหยุดรอ ห้ามล็อกอินแทนฉัน
> ```

**ผลจริง:** 0 FAIL ส่วนข้อ SKIP คือข้อที่ต้องล็อกอินก่อน

![ผลจริงจาก Claude: ตาราง PASS/SKIP การตั้งค่าหลายบัญชีใน devtools และรายการไฟล์ใน container](img/desktop-setup-result.png)

## ขั้นที่ 2 · 🖥️ ตรวจผลข้างใน devtools (~5 นาที)

### 2.1 · เปิด JupyterLab แล้วตรวจคำสั่ง

ใน VS Code คลิกขวา **devtools** → **Open in External Browser** → **8888 localhost:8885** → คลิก **Terminal**

> [!IMPORTANT]
> **📋 คัดลอกกล่องนี้ → JupyterLab Terminal**
>
> ```bash
> which yolo1 cyolo1
> yolo1 --version; cyolo1 --version
> yolo2 --version; cyolo2 --version
> yolo3 --version; cyolo3 --version
> ```

![ภาพเคลื่อนไหว: คลิกขวา devtools ใน VS Code เลือก Open in External Browser, คลิก Terminal ใน JupyterLab, พิมพ์ which และ --version ของ yolo1 ถึง yolo3 กับ cyolo1 ถึง cyolo3](img/open-jupyter-versions.gif)

### 2.2 · ตรวจโครงสร้างโฟลเดอร์ใน File Browser

ใน File Browser ไปที่ `/` → **root** → **ai-accounts**

![ภาพเคลื่อนไหวจริง: File Browser เปิด root/ai-accounts เห็น .Claude และ .Codex, ใน .Claude มี yolo1 ถึง yolo5 และ shared ที่มี mcp และ skills, ใน .Codex มี shared ที่มี mcp และ skills](img/devtools-folders.gif)

![MCP พื้นฐาน Playwright ติดตั้งครั้งเดียวใน shared/mcp ของ devtools ทุกบัญชี yolo1 ถึง yolo5 และ cyolo1 ถึง cyolo5 ใช้ร่วมกัน](img/mcp-01-playwright-included.png)

## ขั้นที่ 3 · 🖥️ ล็อกอินทีละบัญชี แล้วให้ Claude ตรวจ (~15 นาที)

### 3.1 · ล็อกอิน: 1 บัญชี = 1 แท็บ Terminal

ใน JupyterLab กด **+ → Terminal** เปิดแท็บใหม่ต่อ 1 บัญชี ทำอย่างน้อย `yolo1`, `yolo2`, `cyolo1`, `cyolo2` ใช้เฉพาะบัญชีที่มีสิทธิ์ใช้จริง และห้ามแชร์ข้อมูลล็อกอิน

![ภาพเคลื่อนไหว: yolo1 เปิด Terminal พิมพ์ yolo1 เลือก Claude account with subscription ยืนยันโฟลเดอร์ เข้าหน้าสนทนา เลือก Fable Medium, yolo2 ทำซ้ำ, cyolo1 พิมพ์ cyolo1 เลือก Sign in with ChatGPT เข้าหน้าสนทนา เลือก GPT-6-Astra Medium](img/login-flow.gif)

| พิมพ์ | หน้าจอล็อกอิน | เลือก | โมเดลที่ใช้ในแลป |
|---|---|---|---|
| `yolo1` … `yolo5` | Select login method | **Claude account with subscription** → ยืนยันในเบราว์เซอร์ → **Yes, I trust this folder** | `/model` → **Fable** · Medium |
| `cyolo1` … `cyolo5` | Choose how you want to use Codex | **Sign in with ChatGPT** (ถ้าเบราว์เซอร์ส่งผลกลับไม่ได้ ใช้ **Device Code** หรือ `cyolo1 login --device-auth`) | `/model` → **GPT-6-Astra** · Medium |

เสร็จแต่ละบัญชีพิมพ์ `/exit` (Claude) หรือกด Ctrl+C (Codex)

### 3.2 · 💻 ให้ Claude Code Desktop ตรวจว่าล็อกอินครบหรือยัง

> [!IMPORTANT]
> **📋 คัดลอกกล่องนี้ → Claude Code Desktop แล้วกด Enter**
>
> ```text
> ช่วยตรวจสถานะล็อกอินทุกบัญชีใน container devtools ทำผ่าน docker exec เท่านั้น ห้ามล็อกอินแทนฉัน ห้ามแก้ไฟล์ใด ๆ
> - Claude: yolo1 ถึง yolo5 ใช้คำสั่ง yoloN auth status แล้วดูเฉพาะค่า "loggedIn"
> - Codex: cyolo1 ถึง cyolo5 ใช้คำสั่ง cyoloN login status
> สรุปเป็นตาราง บัญชี | ล็อกอินแล้ว/ยัง เท่านั้น ห้ามแสดงอีเมล ชื่อองค์กร หรือ token
> ถ้ามีบัญชีที่ยังไม่ล็อกอิน ให้บอกวิธีล็อกอินใน JupyterLab Terminal
> (พิมพ์ yoloN แล้วเลือก Claude account with subscription / พิมพ์ cyoloN หรือ cyoloN login --device-auth)
> ```

![ผลจริงจาก Claude: ตารางสถานะล็อกอิน 10 บัญชี พร้อมวิธีล็อกอินบัญชีที่ยังขาด](img/desktop-login-check-result.png)

## ขั้นที่ 4 · 💻 ให้ Claude Code Desktop ทดสอบ skill/MCP ข้ามบัญชี (~15 นาที)

![ขั้นที่ 4: AI ในบัญชี yolo1 สั่งงานเป็นภาษาคน ผ่าน Playwright MCP ไปยัง Chromium ใน container เปิด Google Flights กรอก BKK ไป Tokyo แล้วเก็บหลักฐาน 3 ภาพ](img/mcp-02-playwright-step4.png)

### 4.1 · วางพรอมต์ทดสอบ

> [!IMPORTANT]
> **📋 คัดลอกกล่องนี้ → Claude Code Desktop แล้วกด Enter (ค้นหาเที่ยวบินอย่างเดียว ไม่จอง)**
>
> ```text
> ช่วยทดสอบ skill/MCP ส่วนกลางข้ามบัญชี yolo1 yolo2 cyolo1 cyolo2 ใน container devtools
> ทำงานใน container ผ่าน docker exec เท่านั้น ห้ามแก้ไฟล์ตั้งค่า ห้ามล็อกอินแทนฉัน
> 0. ตรวจสถานะล็อกอินทุกบัญชีก่อน: yoloN auth status และ cyoloN login status
>    แสดงเป็นตาราง บัญชี | ล็อกอินแล้ว/ยัง เท่านั้น ห้ามแสดงอีเมล องค์กร หรือ token
>    ถ้ามีบัญชีใดยังไม่ล็อกอิน ให้หยุดทันที แจ้งเตือนว่าต้องล็อกอินบัญชีไหน
>    พร้อมวิธีล็อกอินใน JupyterLab Terminal (พิมพ์ yoloN แล้วเลือก Claude account with subscription / cyoloN login --device-auth)
>    ห้ามทำข้อถัดไปจนกว่าจะล็อกอินครบ
> 1. บันทึกข้อความใต้เส้น ==== ตามตัวอักษรลง /workspace/multi-account/verify-prompt.txt ใน container
> 2. รันทีละบัญชีจาก shell ใน container (โฟลเดอร์ /workspace/multi-account):
>    yolo1 -p "$(cat verify-prompt.txt)", yolo2 เช่นเดียวกัน,
>    cyolo1 exec --skip-git-repo-check "$(cat verify-prompt.txt)", cyolo2 เช่นเดียวกัน
>    รันแบบ foreground ทีละบัญชี timeout บัญชีละ 15 นาที รอจนจบก่อนไปบัญชีถัดไป
> 3. คัดลอกภาพที่แต่ละบัญชีรายงานไปเป็น /workspace/multi-account/evidence/<บัญชี>/1-open.png, 2-search.png, 3-results.png
>    พร้อม log คำตอบเป็น run.log ในโฟลเดอร์เดียวกัน
> 4. สรุปตาราง บัญชี | config root | รหัส shared-check | tool ที่เรียก | เที่ยวบินอันดับ 1 | ภาพที่ได้ | PASS/FAIL
>    บัญชีต่างกันแต่ CLI เดียวกันต้องได้รหัสเดียวกัน ถ้าบัญชีใดล้มเหลวให้รายงานตามจริง ห้ามแก้แทนหรือเดาผล
> ====
> ตรวจว่า skill และ MCP ส่วนกลางใช้ได้จริงในบัญชีนี้ ทำตามลำดับ ห้ามแก้ไฟล์ตั้งค่าใด ๆ
>
> 1. แจ้ง config root ที่ใช้อยู่ (ค่า CLAUDE_CONFIG_DIR หรือ CODEX_HOME) ห้ามแสดง token อีเมล หรือข้อมูลบัญชี
> 2. ใช้ skill shared-check ตามกลไก skill ของ CLI นี้ แล้วรายงานรหัสที่ได้ พร้อม path ของ skill ตามที่ CLI แสดง
>    ห้ามค้นหาไฟล์เอง (find, grep, ls) และห้ามเปิดไฟล์จาก path ที่ไม่ได้มาจากรายการ skill ของ CLI
> 3. ใช้เครื่องมือของ MCP ชื่อ playwright เท่านั้น ห้ามใช้ curl, python, web search หรือ browser อื่น
>    เปิด https://www.google.com/travel/flights?hl=en
>    ค้นหาเที่ยวบินเที่ยวเดียว Bangkok (BKK) ไป Tokyo ญี่ปุ่น ชั้นประหยัด ผู้ใหญ่ 1 คน วันเดินทางคือวันที่ 15 ของเดือนถัดไป
>    ค้นหาอย่างเดียว ห้ามกดจอง ห้ามกรอกข้อมูลส่วนตัว ห้ามชำระเงิน ห้ามล็อกอินเว็บไซต์ใด
>    ถ้าหน้าเว็บไม่แสดงผล ให้รายงานตามจริงว่าติดตรงไหน ห้ามเดาราคา
> 4. บันทึกภาพหน้าจอด้วย tool screenshot ของ playwright เฉพาะส่วนที่มองเห็น 3 ภาพ
>    ตั้งชื่อ <บัญชี>-1-open.png (หน้าเว็บเปิดได้), <บัญชี>-2-search.png (กรอกเงื่อนไขครบก่อนกดค้นหา),
>    <บัญชี>-3-results.png (รายการผลเที่ยวบิน) แล้วรายงาน path เต็มของแต่ละภาพ
> 5. สรุปเป็นตาราง รายการ | PASS/FAIL | หลักฐาน โดยมีแถว: config root, รหัสจาก skill shared-check,
>    ชื่อ MCP server และชื่อ tool ที่เรียกจริง, ภาพหน้าจอ 3 ภาพ (path),
>    เที่ยวบิน 3 อันดับแรก: สายการบิน เวลาออก-ถึง ระยะเวลา จำนวนแวะ ราคา (ตามที่เห็นบนหน้าเว็บ)
> ```

ถ้ายังล็อกอินไม่ครบ Claude จะหยุดและบอกว่าต้องล็อกอินบัญชีไหน

![ผลจริงเมื่อยังล็อกอินไม่ครบ: Claude ตรวจข้อ 0 พบ yolo4 และ cyolo3 ยังไม่ล็อกอิน จึงหยุดและบอกวิธีล็อกอิน](img/desktop-verify-warn-result.png)

### 4.2 · ผลจริง

![ผลจริงจาก Claude: ข้อ 0 ล็อกอินครบ 4 บัญชี ผลทดสอบ yolo1 cyolo1 cyolo2 PASS ส่วน yolo2 FAIL เพราะ Google Flights error รหัส shared-check ตรงกันตาม CLI](img/desktop-verify-result.png)

บัญชีของ CLI เดียวกันต้องได้รหัส `shared-check` เดียวกัน ถ้า skill และ MCP ผ่าน แต่เว็บขึ้น error แบบนี้ เป็นปัญหาของเว็บภายนอก ให้รันเฉพาะบัญชีนั้นซ้ำ

![ภาพจริงรอบแรกของ yolo2: Google Flights กรอกเงื่อนไขครบแต่ขึ้น Oops something went wrong และปุ่ม Reload](img/evidence-yolo2-attempt1-error.png)

> [!IMPORTANT]
> **📋 คัดลอกกล่องนี้ → Claude Code Desktop (เปลี่ยน yolo2 เป็นบัญชีที่ FAIL)**
>
> ```text
> รัน yolo2 ซ้ำอีกรอบด้วยพรอมต์เดิม แล้วอัปเดตหลักฐาน
> ```

### 4.3 · ดูหลักฐานที่ Playwright เก็บไว้

ใน File Browser ไปที่ `/workspace/multi-account/evidence/` แต่ละบัญชีมีภาพ 3 ภาพและ `run.log`

![ภาพเคลื่อนไหวจากภาพจริงของ yolo1: เปิด Google Flights, กรอก BKK ไป Tokyo วันอังคาร 15 ธันวาคม, ผลค้นหา Top flights](img/evidence-yolo1.gif)

![ผลค้นหาเที่ยวบินจาก Playwright MCP ของ yolo1 yolo2 cyolo1 cyolo2 เรียงเป็นตาราง 2x2 ได้ผลชุดเดียวกัน](img/evidence-results-4accounts.png)
