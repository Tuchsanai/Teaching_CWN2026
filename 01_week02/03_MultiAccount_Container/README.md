# การสร้าง Docker image สำหรับระบบหลายบัญชีจาก Dockerfile

**สไลด์ประกอบการสอน:** [Multi_Account_Container_Slides.html](Multi_Account_Container_Slides.html) (เปิดในเบราว์เซอร์ กด ← → เปลี่ยนหน้า) · [ฉบับ PDF](Multi_Account_Container_Slides.pdf)

## 1. เปรียบเทียบ 3 แบบของการเตรียมสภาพแวดล้อม

บทเรียนใน `01_week02` เตรียมสภาพแวดล้อมสำหรับทำงานกับ AI ไว้ 3 แบบ แต่ละแบบต่อยอดจากแบบก่อนหน้า

![แบบที่ 1 container devtools มีเฉพาะเครื่องมือพื้นฐาน, แบบที่ 2 ใช้ docker exec ติดตั้ง yolo1–5 และ cyolo1–5 เพิ่มลงใน devtools ที่กำลังทำงาน, แบบที่ 3 build Dockerfile เป็น image multi-account:1.0 แล้ว docker run ได้ container ที่ติดตั้งครบและพร้อมใช้ทันที](img/concept-01-three-approaches.png)

| | แบบที่ 1 · devtools | แบบที่ 2 · devtools + ติดตั้งภายหลัง | แบบที่ 3 · build จาก Dockerfile |
|---|---|---|---|
| บทเรียน | [01_Docker_VSCode_Setup](../01_Docker_VSCode_Setup/README.md) | [02_Setup_Multi_Account](../02_Setup_Multi_Account/README.md) | บทนี้ |
| จุดเริ่มต้น | image สำเร็จรูป `tuchsanai/devtools:2569_1` | container `devtools` จากแบบที่ 1 | Dockerfile |
| สิ่งที่มีใน container | เครื่องมือพื้นฐาน: Ubuntu, Python, Node.js, Git, Docker, JupyterLab | เครื่องมือพื้นฐาน + ระบบหลายบัญชี | เครื่องมือพื้นฐาน + ระบบหลายบัญชี |
| ระบบหลายบัญชีเข้ามาอย่างไร | ไม่มี | ติดตั้งภายหลังผ่าน `docker exec` | ติดตั้งไว้ตั้งแต่ขั้น build |
| ข้อมูลล็อกอินเก็บที่ | – | ภายใน container | volume `ai-accounts` |
| เมื่อ container ถูกลบ | สร้างใหม่ได้เครื่องมือพื้นฐานชุดเดิม | ต้องติดตั้งและล็อกอินใหม่ | `docker run` ใหม่แล้วพร้อมใช้ทันที |

ภาพเคลื่อนไหวด้านล่างแสดงขั้นตอนของแต่ละแบบ และผลที่เกิดขึ้นเมื่อ container ถูกลบ

![ภาพเคลื่อนไหว: ขั้นตอนของแบบที่ 1, 2 และ 3 ตามลำดับ และผลเมื่อลบ container ของแต่ละแบบ](img/gif-three-approaches.gif)

*ภาพเคลื่อนไหวประกอบแนวคิด เวลาของแบบที่ 2 มาจากผลรันจริงในบท `02_Setup_Multi_Account` (ติดตั้ง ~5 นาที) และเวลาโดยประมาณของการล็อกอิน (~15 นาที) ตัวเลขของแบบที่ 3 มาจากการรันจริงในบทนี้*

## 2. องค์ประกอบของ Docker ที่ใช้ในบทนี้

![Dockerfile ผ่าน docker build เป็น image ที่อ่านได้อย่างเดียว แล้ว docker run ได้หลาย container ที่ต่อกับ volume สำหรับเก็บข้อมูลถาวร](img/concept-02-docker-terms.png)

| องค์ประกอบ | ความหมาย | ในบทนี้ |
|---|---|---|
| **Dockerfile** | ไฟล์ข้อความที่ระบุขั้นตอนการสร้าง image ทีละคำสั่ง | `MultiAccountDevtool/Dockerfile` ที่ Claude เขียน |
| **image** | ผลลัพธ์จากการ build เป็นต้นแบบที่อ่านได้อย่างเดียว (read-only) | `multi-account:1.0` |
| **container** | ตัวที่ทำงานจริง สร้างจาก image และมีชั้นข้อมูลที่เขียนได้ของตัวเอง ลบแล้วข้อมูลในชั้นนี้หายไปด้วย | `multi-account` |
| **volume** | พื้นที่เก็บข้อมูลที่ Docker จัดการแยกจาก container ข้อมูลยังคงอยู่แม้ลบ container | `ai-accounts` → `/root/ai-accounts` |

เมื่อ build image แล้ว จะสร้าง container จาก image นี้กี่ครั้ง หรือบนเครื่องใดก็ได้ ทุกครั้งจะได้โปรแกรมชุดเดียวกัน ส่วนข้อมูลล็อกอินเป็นของแต่ละเครื่อง เก็บใน volume ของเครื่องนั้น

![ภาพเคลื่อนไหว: Dockerfile ถูก build เป็น image multi-account:1.0 แล้ว docker run เป็น container บนเครื่องผู้เรียน เครื่องเพื่อนร่วมทีม และ container ที่สร้างใหม่หลังลบ โดยเครื่องผู้เรียนใช้ volume ai-accounts ตัวเดียวกัน](img/gif-build-once.gif)

*ภาพเคลื่อนไหวประกอบแนวคิด คำสั่งใน Dockerfile เป็นสรุปย่อ ดูฉบับเต็มได้ที่ [`_solution/MultiAccountDevtool/Dockerfile`](_solution/MultiAccountDevtool/Dockerfile)*

### 2.1 โครงสร้างของ image `multi-account:1.0`

image ประกอบด้วยชั้น (layer) ซ้อนกัน แต่ละชั้นเกิดจากคำสั่งใน Dockerfile ส่วนข้อมูลที่ต้องเก็บถาวรอยู่นอก image

![container multi-account เชื่อมกับ 3 ส่วน: image multi-account:1.0 เก็บโปรแกรมทั้งหมด, volume ai-accounts เก็บล็อกอิน skill และ MCP, ./workspace เก็บไฟล์งาน ลบ container ได้โดยทั้งสามส่วนยังอยู่](img/concept-03-image-layers.png)

| ส่วน | เก็บอะไร | เมื่อลบ container |
|---|---|---|
| **ชั้นของ image** (4 ชั้น) | โปรแกรมทั้งหมด: ชั้นพื้นฐานเดียวกับ devtools, Claude Code + Codex CLI, Playwright MCP + Chromium + ฟอนต์ไทย และระบบหลายบัญชี | ยังอยู่ (เป็นส่วนของ image) |
| **container layer** | ไฟล์ที่เกิดขึ้นระหว่างทำงานซึ่งไม่ได้อยู่ใน volume เช่น ไฟล์งานใน `/workspace` | หายไป (คัดลอกออกมาด้วย `docker cp` ก่อนลบ) |
| **volume `ai-accounts`** | ข้อมูลล็อกอินของทุกบัญชี skill กลาง และ MCP กลาง | ยังอยู่ |

ทุกครั้งที่ container เริ่มทำงาน `multi-account-install` จะเตรียมโครงสร้างใน volume โดยไม่เขียนทับข้อมูลเดิม image จึง**ไม่มีข้อมูลล็อกอินอยู่ภายใน** และแชร์ให้ผู้อื่นได้โดยไม่เปิดเผยบัญชีของเรา

## 3. ภาพรวมขั้นตอนการทดลอง

![ขั้นตอนการทดลอง 5 ขั้นที่สั่งจาก Claude Code app: build image, run container, ล็อกอิน, ทดสอบ skill + MCP, ลบและสร้างใหม่](img/concept-04-lab-flow.png)

| ขั้น | ทำที่ไหน | ผู้ดำเนินการ | เวลารันจริง |
|---|---|---|---|
| **1 · build image** | Claude Code app | Claude | ~28 นาที (build ครั้งสุดท้าย 5 นาที) |
| **2 · สร้าง container จาก image** | Claude Code app | Claude | ~1 นาที |
| **3 · ล็อกอิน** | JupyterLab | ผู้เรียน | ~15 นาที |
| **4 · ทดสอบ skill/MCP ข้ามบัญชีแบบขนาน** | Claude Code app | Claude | ~5 นาที |
| **5 · ลบ container แล้วสร้างใหม่** | Claude Code app | Claude | ~3 นาที |

**ตรวจก่อนเริ่ม:** Docker Desktop แสดง **Engine running** · Claude Code app ล็อกอินแล้ว · มีพื้นที่ดิสก์ว่างอย่างน้อย ~10 GB (image ~4.5 GB + build cache)

**เปิดโฟลเดอร์งาน:** ใน Claude Code app เลือก **Code** → **New session** → เลือกโฟลเดอร์ `03_MultiAccount_Container` ของรีโปนี้

```text
03_MultiAccount_Container/
├── 00_Devtool_Container/     ← Dockerfile มาตรฐานของ devtools (input ที่ 1)
├── prompt_multi_account.md   ← สเปกระบบหลายบัญชี (input ที่ 2)
└── _solution/                ← เฉลยจากการรันจริง (หากต้องการให้ Claude ทำเองทั้งหมด ให้ย้ายโฟลเดอร์นี้ออกก่อน)
```

## ขั้นที่ 1 · ให้ Claude สร้าง image (~30 นาที)

### 1.1 · input และกระบวนการ

**เหตุผลที่ต้องทำขั้นนี้:** ในแบบที่ 2 ผู้เรียนแต่ละคนติดตั้งระบบหลายบัญชีลงใน container ของตนเองด้วยมือตามรายการบนกระดาน ผลที่ได้จึงต่างกันในแต่ละเครื่อง บางเครื่องไม่มีคำสั่ง `yolo1` บางเครื่องไม่มี Playwright ผู้สอนต้องเดินแก้ไขทีละเครื่อง และเมื่อลบ container ก็ต้องติดตั้งใหม่ทั้งหมด

![ห้องปฏิบัติการคอมพิวเตอร์ที่ผู้เรียนติดตั้งระบบหลายบัญชีด้วยมือตามรายการ 5 ข้อบนกระดาน จอสามเครื่องที่อยู่ติดกันแสดงผลต่างกัน คือ yolo1: command not found, playwright: not installed และ yolo1-5 OK ผู้เรียนยกมือขอความช่วยเหลือ ขณะที่ผู้สอนกำลังช่วยผู้เรียนอีกคน](img/photo-04-step1-why.jpg)

**กระบวนการ:** ขั้นนี้นำรายการติดตั้งดังกล่าวมาเขียนเป็นสเปก แล้วให้ Claude ใช้สเปกนั้นร่วมกับ Dockerfile มาตรฐานสร้างโฟลเดอร์ `MultiAccountDevtool/` และ build เป็น image เพียงครั้งเดียว ถ้าการทดสอบไม่ผ่าน Claude จะกลับไปแก้ Dockerfile แล้ว build ใหม่ ทุกเครื่องที่รัน image นี้จะได้สภาพแวดล้อมเหมือนกัน

![ระบบของขั้นที่ 1: input คือ 00_Devtool_Container (Dockerfile มาตรฐาน) และ prompt_multi_account.md (สเปกระบบหลายบัญชี) Claude Code app คัดลอก แก้ Dockerfile build และทดสอบ ถ้าไม่ผ่านจะวนกลับไปแก้ Dockerfile output คือโฟลเดอร์ MultiAccountDevtool และ image multi-account:1.0 ขนาด 4.47 GB ผลทดสอบ 9 PASS 0 FAIL 1 SKIP](img/concept-06-step1-process.png)

| input | บทบาท | เนื้อหา |
|---|---|---|
| [`00_Devtool_Container/`](00_Devtool_Container/readme.md) | ฐานของ image | `Dockerfile` และ `start.sh` ของ devtools: Ubuntu 24.04, Docker-in-Docker, Python, Node.js 22, JupyterLab |
| [`prompt_multi_account.md`](prompt_multi_account.md) | ข้อกำหนดของระบบหลายบัญชี | สิ่งที่ต้องมีใน image และเกณฑ์ทดสอบ (ดูข้อ 1.2) |

### 1.2 · เนื้อหาของ `prompt_multi_account.md`

สเปกนี้นำมาจากพรอมต์[ขั้นที่ 1 ของบท `02_Setup_Multi_Account`](../02_Setup_Multi_Account/README.md#ขั้นที่-1---ให้-claude-code-desktop-ตั้งค่าหลายบัญชี-10-นาที) บทดังกล่าวใช้สเปกนี้ติดตั้งลงใน container ที่กำลังทำงาน ส่วนบทนี้ใช้เป็นข้อกำหนดของ image ระบบหลายบัญชีของทั้งสองบทจึงมีโครงสร้างเหมือนกัน

| หัวข้อ | สาระ |
|---|---|
| เป้าหมาย | คำสั่ง `yolo1`–`yolo5` (Claude Code) และ `cyolo1`–`cyolo5` (Codex CLI) แยกโฟลเดอร์ต่อบัญชี และโฟลเดอร์ `shared` สำหรับ skill และ MCP กลาง |
| กติกา | แยก credential ต่อบัญชี installer รันซ้ำได้โดยไม่ทับของเดิม MCP ตัวแรกคือ Playwright และ skill ตัวอย่าง `shared-check` |
| ข้อเท็จจริงจากการทดลอง | ข้อควรรู้เฉพาะของแต่ละ CLI ที่พบจากการรันจริง เพื่อไม่ต้องลองผิดลองถูก |
| ทดสอบ | เกณฑ์ PASS/FAIL/SKIP |
| รายงาน | `setup-report.md`, `login-guide.md`, `checklist.md` |

ข้อความเต็มของไฟล์:

```text
ตรวจ --help ของเวอร์ชันจริงก่อนใช้ env/flag ห้ามเดา

## เป้าหมาย (BASE=/root/ai-accounts)
- yolo1..yolo5   → claude --dangerously-skip-permissions  (CLAUDE_CONFIG_DIR=$BASE/.Claude/yoloN)
- cyolo1..cyolo5 → codex --dangerously-bypass-approvals-and-sandbox  (CODEX_HOME=$BASE/.Codex/cyoloN)
- wrapper วางใน /usr/local/bin ให้พิมพ์ได้ทันที ส่งต่อ "$@" ครบ แจ้งชัดถ้าโฟลเดอร์บัญชีไม่มี ไม่พิมพ์ secret
- $BASE/.Claude/shared และ $BASE/.Codex/shared มี skills/ และ mcp/ แก้ครั้งเดียว ทุกบัญชีของ CLI นั้นเห็นตอนเปิดครั้งถัดไป

## กติกา
- แยก credential/config/session ต่อบัญชี เปิดพร้อมกันได้ ใช้ CLAUDE_CONFIG_DIR/CODEX_HOME เท่านั้น ห้ามเปลี่ยน $HOME
- Codex ใช้ file-based credential ต่อ CODEX_HOME ห้ามแชร์ credential ใน shared
- สร้าง installer เป็นไฟล์ใน container รันซ้ำได้ ไม่เขียนทับ credential/config เดิม ห้ามแก้ .bashrc/Git/SSH
- MCP ส่วนกลางตัวแรก: Playwright (@playwright/mcp) + Chromium ติดตั้งครั้งเดียว
- skill ตัวอย่าง shared-check: ตอบ SHARED_SKILL_OK-<tool>-<ค่าสุ่มตอนติดตั้ง> ซึ่งมีในไฟล์ skill เท่านั้น

## ข้อเท็จจริงจากการทดลอง (ตรวจว่ายังจริงกับเวอร์ชันนี้)
- root ต้องตั้ง IS_SANDBOX=1; CODEX_HOME ต้อง mkdir -p ก่อน
- Claude: skill อ่านจาก $CLAUDE_CONFIG_DIR/skills; MCP ส่งผ่าน --mcp-config=<ไฟล์> (ต้องมี =)
  ห้าม symlink .claude.json (มีสถานะล็อกอิน); claude mcp list ไม่แสดง MCP นี้ ให้ตรวจด้วย /mcp
- Codex: skill อ่านจาก $CODEX_HOME/skills และเขียน skills/.system เอง ห้าม symlink ทั้งโฟลเดอร์
  MCP ส่งด้วย -c mcp_servers.<name>={...} (ใช้กับ codex mcp list ได้)
- Playwright ใน root container: --browser chromium --headless --isolated --no-sandbox และ --output-dir นอกโฟลเดอร์งาน
  ติดตั้ง Chromium ด้วย playwright ในแพ็กเกจ @playwright/mcp ให้เวอร์ชันตรงกัน (อาจต้อง install-deps)

## ทดสอบใน container (PASS/FAIL/SKIP ตามจริง)
- 10 คำสั่ง --version ครบ, config root คนละโฟลเดอร์, installer รอบ 2 ไม่ทำลายของเดิม
- cyoloN mcp list เห็น playwright, skill shared-check ทุกบัญชี readlink -f ไปไฟล์เดียวกันใน shared
- อะไรที่ต้องล็อกอิน = SKIP

## รายงาน (ห้ามมี secret)
- setup-report.md: โครงสร้างโฟลเดอร์, wrapper, แต่ละ CLI อ่าน skill/MCP จากไหน, ข้อจำกัด
- login-guide.md: ล็อกอินทีละบัญชีใน JupyterLab Terminal
- checklist.md: รายการ | หลักฐาน | PASS/FAIL/SKIP
เสร็จแล้วสรุปเป็นตารางสั้น ๆ แล้วหยุดรอ ห้ามล็อกอินแทนฉัน
```

### 1.3 · วางพรอมต์

วางพรอมต์ทั้งกรอบใน Claude Code app (Ctrl+V) → Enter → อนุญาตคำสั่ง `docker` เมื่อระบบถาม แล้วรอจน Claude สรุปผล พรอมต์อ้างถึง input ทั้ง 2 อย่างในหัวข้อ "วัตถุดิบ"

![ภาพเคลื่อนไหว: วางพรอมต์ build image ใน Claude Code app, Claude อ่านสเปก คัดลอก 00_Devtool_Container แก้ Dockerfile แล้ว docker build และทดสอบ จนได้ตารางผล](img/desktop-step1-build.gif)

> [!IMPORTANT]
> **📋 คัดลอกกล่องนี้ → Claude Code app แล้วกด Enter**
>
> ```text
> ช่วยสร้าง Docker image ชื่อ multi-account:1.0 ที่เปิดมาแล้วใช้หลายบัญชี AI ได้ทันที
> ทำในโฟลเดอร์นี้ ใช้คำสั่ง docker ได้ แต่ห้ามลบ หยุด หรือแก้ container / image / volume ที่มีอยู่
> (ห้าม docker system prune และห้ามแตะ volume ai-accounts)
>
> วัตถุดิบ
> - ./00_Devtool_Container = Dockerfile มาตรฐานของ devtools คัดลอกเป็น ./MultiAccountDevtool แล้วแก้ในนั้นเท่านั้น
>   ถ้ามี ./MultiAccountDevtool อยู่แล้ว ให้เทียบกับสเปกแล้วแก้เฉพาะที่ขาด
> - ./prompt_multi_account.md = สเปกระบบหลายบัญชี ทุกข้อต้องเป็นจริงใน image
>   ส่วน "ข้อเท็จจริงจากการทดลอง" ให้ตรวจกับ --help ของเวอร์ชันจริงก่อนใช้
>
> สิ่งที่ต้องอยู่ใน image
> - Claude Code, Codex CLI, Playwright MCP (pin เวอร์ชัน) + Chromium + ฟอนต์ไทย
> - installer และคำสั่ง yolo1..5 / cyolo1..5 ใน /usr/local/bin ใช้ได้ทั้งใน JupyterLab Terminal และ docker exec
> - ห้ามมีข้อมูลล็อกอินใน image: /root/ai-accounts เป็น volume และ installer รันทุกครั้งที่ container start โดยไม่ทับของเดิม
> - คง Docker-in-Docker และ JupyterLab ไว้
>
> build ด้วย: docker build -t multi-account:1.0 ./MultiAccountDevtool
>
> ทดสอบด้วย container และ volume ทดสอบชื่อใหม่ แล้วลบทิ้งเมื่อเสร็จ (PASS/FAIL/SKIP ตามจริง)
> - yolo1..5 / cyolo1..5 --version ครบ 10 คำสั่ง และ config root คนละโฟลเดอร์
> - skill shared-check ทุกบัญชีชี้ไปไฟล์เดียวกันใน shared และ cyolo1 mcp list เห็น playwright
> - Playwright MCP ผ่าน stdio เปิด https://example.com แล้ว screenshot ได้
> - installer รอบ 2 ไม่ทับของเดิม และลบ container แล้วสร้างใหม่ ของใน volume ยังอยู่
> - JupyterLab /lab ตอบ 200
> ข้อที่ต้องล็อกอิน = SKIP ห้ามล็อกอินแทนผม
>
> เขียนรายงานตามหัวข้อ "รายงาน" ของสเปกไว้ใน ./MultiAccountDevtool (ห้ามมี secret)
> เสร็จแล้วสรุปเป็นตารางสั้น ๆ: ผลทดสอบ ขนาด image และเวลา build แล้วหยุด
> ```

**หลักการออกแบบพรอมต์**

- **ระบุ input ชัดเจน:** Claude ไม่ต้องคาดเดาฐานของ image หรือโครงสร้างระบบหลายบัญชี
- **แยก image ออกจาก volume:** โปรแกรมอยู่ใน image ข้อมูลล็อกอินอยู่ใน volume การแชร์ image จึงไม่เปิดเผยบัญชี
- **ไม่แตะทรัพยากรเดิม:** ทดสอบด้วย container และ volume ชั่วคราวแล้วลบทิ้ง
- **รายงานเป็น PASS/FAIL/SKIP:** ตรวจผลจากหลักฐานได้ ไม่ต้องอาศัยคำบอกเล่าของ AI

### 1.4 · ผลจริง

**ผลจริง** (7 พ.ย. 2026 · ~28 นาที): **9 PASS · 0 FAIL · 1 SKIP** (ข้อที่ต้องล็อกอิน) image ขนาด **4.47 GB** build ใหม่แบบไม่ใช้ cache ใช้ **302 วินาที** ได้ Claude Code 2.1.319, Codex 0.167.0, Playwright MCP 0.0.84

![ผลจริงจาก Claude: ตาราง PASS/SKIP 10 รายการ ขนาด image 4.47GB เวลา build 302 วินาที และข้อควรรู้](img/desktop-step1-result.png)

*ข้อความคำตอบจริงของ Claude จัดหน้าใหม่ให้อ่านง่าย (ตอนรันจริงใช้ชื่อ `my-multi-account` ภาพผลจริงทุกขั้นปรับชื่อเป็น `multi-account` ให้ตรงกับบทเรียน) ระหว่างทาง Claude build รอบแรก ตรวจ `--help` ของ CLI จริงใน container ชั่วคราว เขียน installer แล้ว build รอบสุดท้ายแบบไม่ใช้ cache เพื่อจับเวลา*

ไฟล์ที่ Claude สร้าง (เก็บเป็นเฉลยไว้ที่ [`_solution/MultiAccountDevtool/`](_solution/MultiAccountDevtool/))

```text
MultiAccountDevtool/
├── Dockerfile               ← Dockerfile ของ devtools + 4 ชั้นใหม่ (CLI, Playwright, ฟอนต์ไทย, ระบบหลายบัญชี)
├── start.sh                 ← dockerd + multi-account-install (ทุกครั้งที่ start) + jupyter lab
├── multi-account/           ← installer, wrapper ของ yoloN/cyoloN, ตัวแปลง MCP ให้ Codex
├── docker-compose.yml       ← ทางเลือก: build + run ด้วยคำสั่งเดียว
└── setup-report.md · login-guide.md · checklist.md   ← รายงาน 3 ไฟล์ตามสเปก
```

## ขั้นที่ 2 · สร้าง container จาก image (~1 นาที)

ขั้นที่ 1 ได้ image `multi-account:1.0` ซึ่งเป็นแม่แบบแบบอ่านอย่างเดียว ยังใช้งานโดยตรงไม่ได้ ขั้นนี้ใช้ `docker run` สร้าง container จาก image นั้นเพื่อนำมาใช้งานจริง แต่ละ option ของคำสั่งกำหนดว่า container จะเชื่อมกับเครื่องของเราอย่างไร หากไม่ได้ทำขั้นที่ 1 พรอมต์นี้จะดึง image สำเร็จรูปของผู้สอน `tuchsanai/multi-account:1` จาก Docker Hub มาใช้แทน

![image multi-account:1.0 จากขั้นที่ 1 ผ่านคำสั่ง docker run ได้ container multi-account สถานะ running ที่มี yolo1–5 · cyolo1–5, Playwright MCP และ JupyterLab ตัวเลือก --name ตั้งชื่อ container, --privileged เปิด Docker-in-Docker, -p 8886:8888 เปิด JupyterLab ที่ localhost:8886/lab ซึ่งพร้อมใน 1.96 วินาที, -v ai-accounts เชื่อม volume เก็บล็อกอิน skills และ MCP, -v ./workspace เชื่อมโฟลเดอร์ไฟล์งาน](img/concept-07-step2-run.png)

> [!IMPORTANT]
> **📋 คัดลอกกล่องนี้ → Claude Code app แล้วกด Enter**
>
> ````markdown
> # รัน container ชื่อ `multi-account` จาก image `multi-account:1.0`
>
> ## 1. เตรียม image และ container
>
> ถ้ายังไม่มี image `multi-account:1.0` ให้ดึงจาก Docker Hub แล้วตั้งชื่อใหม่
>
> ```bash
> docker pull tuchsanai/multi-account:1
> docker tag  tuchsanai/multi-account:1 multi-account:1.0
> ```
>
> ถ้ามี container ชื่อ `multi-account` อยู่แล้ว ให้ลบออก (ห้ามลบ volume `ai-accounts`)
>
> ```bash
> docker rm -f multi-account
> ```
>
> ## 2. สร้าง container
>
> `PORT` เริ่มที่ `8886` ถ้าชนใช้เลขว่างถัดไป
>
> ```bash
> docker run -dit \
>   --name multi-account \
>   --privileged \
>   -p <PORT>:8888 \
>   -v ai-accounts:/root/ai-accounts \
>   multi-account:1.0
> ```
>
> จับเวลาตั้งแต่ `docker run` จน `http://localhost:<PORT>/lab` ตอบ `200`
>
> ## 3. ตรวจผ่าน `docker exec` แล้วสรุปเป็นตาราง
>
> - `yolo1..5 --version` และ `cyolo1..5 --version`
> - `cyolo1 mcp list` ต้องเห็น `playwright`
> - สถานะล็อกอินทุกบัญชี (ห้ามล็อกอินแทนผม ห้ามแก้ไฟล์ใด ๆ)
>   - Claude: `yolo1` ถึง `yolo5` ใช้คำสั่ง `yoloN auth status` แล้วดูเฉพาะค่า `loggedIn`
>   - Codex: `cyolo1` ถึง `cyolo5` ใช้คำสั่ง `cyoloN login status`
> - ตารางสรุป: image มาจากไหน (build เอง / pull) · URL ของ JupyterLab · เวลาที่ใช้
>   และตาราง บัญชี | เวอร์ชัน | ล็อกอินแล้ว/ยัง ห้ามแสดงอีเมล ชื่อองค์กร หรือ token
> - ถ้ามีบัญชีที่ยังไม่ล็อกอิน ให้บอกวิธีล็อกอินใน JupyterLab Terminal
>   (พิมพ์ `yoloN` แล้วเลือก Claude account with subscription / พิมพ์ `cyoloN login --device-auth`)
> ````

**ความหมายของแต่ละ option ใน `docker run`**

| option | ความหมาย |
|---|---|
| `-dit` | รันเบื้องหลัง (`-d`) พร้อม terminal (`-it`) |
| `--name multi-account` | ตั้งชื่อ container |
| `--privileged` | เปิดให้ใช้ Docker-in-Docker ภายใน container |
| `-p <PORT>:8888` | เปิด JupyterLab ที่ `http://localhost:<PORT>/lab` |
| `-v ai-accounts:/root/ai-accounts` | volume เก็บล็อกอิน skill และ MCP ไม่หายเมื่อลบ container |
| `multi-account:1.0` | image ที่ใช้สร้าง container |

![ภาพเคลื่อนไหว: วางพรอมต์รัน container ใน Claude Code app แล้ว Claude ตรวจ image ลบ container เดิม docker run รอ JupyterLab ตอบ 200 และตรวจเวอร์ชัน MCP และสถานะล็อกอิน](img/desktop-step2-run.gif)

เปิด Docker Desktop หน้า **Containers** แล้วค้นหา `multi-account` จะเห็น container ที่เพิ่งสร้าง

![ภาพจริงจาก Docker Desktop: ค้นหา multi-account เหลือ 1 รายการ จุดสีเขียวกำลังทำงาน สร้างจาก image multi-account:1.0 port 8886:8888](img/docker-desktop-multi-account.png)

![ผลจริงจาก Claude: container multi-account พร้อมใน 2.7 วินาที ที่มาของ image URL ของ JupyterLab cyolo1 mcp list เห็น playwright ตารางเวอร์ชันกับสถานะล็อกอิน 10 บัญชี และวิธีล็อกอินบัญชีที่เหลือ](img/desktop-step2-result.png)

*เครื่องตัวอย่างใช้ volume `ai-accounts` ที่เคยล็อกอินไว้แล้ว 5 บัญชี จึงแสดง ✅ ตั้งแต่ยังไม่ได้ล็อกอินในแลปนี้ (ของผู้เรียนจะเป็น ❌ ทั้งหมดจนกว่าจะทำขั้นที่ 3) MCP `rea` มาจากแลปอื่นที่เคยติดตั้งไว้ใน volume เดียวกัน*

## ขั้นที่ 3 · ล็อกอินใน JupyterLab (~15 นาที)

เปิด JupyterLab ตาม URL ที่ได้จากขั้นที่ 2 แล้วล็อกอิน 1 บัญชีต่อ 1 แท็บ Terminal วิธีเดียวกับบท `02_Setup_Multi_Account` (ดูภาพเคลื่อนไหวครบทุกขั้นที่ [ขั้นที่ 3.1 ของบทดังกล่าว](../02_Setup_Multi_Account/README.md#31--ล็อกอิน-1-บัญชี--1-แท็บ-terminal)) อย่างน้อย `yolo1`, `yolo2`, `cyolo1`, `cyolo2`

| พิมพ์ | หน้าจอล็อกอิน | เลือก |
|---|---|---|
| `yolo1` … `yolo5` | Select login method | **Claude account with subscription** → ยืนยันในเบราว์เซอร์ → **Yes, I trust this folder** → `/exit` |
| `cyolo1` … `cyolo5` | Choose how you want to use Codex | **Sign in with ChatGPT** หรือ `cyolo1 login --device-auth` หากเบราว์เซอร์ส่งผลกลับไม่ได้ |

**ความต่างจากแบบที่ 2:** ข้อมูลล็อกอินถูกเก็บใน **volume `ai-accounts`** ไม่ใช่ใน container จึงล็อกอินเพียง**ครั้งเดียว** และยังใช้ได้แม้ลบ container หรือ build image ใหม่ (ทดสอบในขั้นที่ 5)

> **ผู้เรียนต้องล็อกอินด้วยตนเองเสมอ** ห้ามส่งรหัสผ่าน code หรือ URL ที่มี token ให้ AI หรือผู้อื่น

ไม่ต้องสั่ง Claude ตรวจสถานะแยกอีกครั้ง พรอมต์ของขั้นที่ 4 ตรวจสถานะล็อกอินทุกบัญชีก่อนเริ่มทดสอบ ขั้นที่ 4 ต้องมีอย่างน้อย 1 บัญชีต่อ CLI (แนะนำ CLI ละ 2 บัญชีเพื่อเทียบรหัส)

## ขั้นที่ 4 · ทดสอบ skill และ MCP ข้ามบัญชีแบบขนาน (~5 นาที)

แต่ละบัญชีเรียก skill กลาง `shared-check` และใช้ **Playwright MCP** เปิด Google Flights ค้นหาเที่ยวบิน BKK → Tokyo แล้วบันทึกภาพหน้าจอ **ค้นหาอย่างเดียว ไม่จองและไม่ชำระเงิน** ต่างจากแบบที่ 2 ตรงที่**ทุกบัญชีทำงานพร้อมกัน** ซึ่งเป็นวัตถุประสงค์หลักของการมีหลายบัญชี

พรอมต์มี 2 ส่วน: **เหนือเส้น `====`** คืองานของ Claude ใน Claude Code app (ตรวจล็อกอิน เลือกบัญชี สั่งรันพร้อมกัน สรุปผล) และ**ใต้เส้น `====`** คืองานที่แต่ละบัญชีทำภายใน container

> [!IMPORTANT]
> **📋 คัดลอกกล่องนี้ → Claude Code app แล้วกด Enter**
>
> ```text
> ช่วยทดสอบ skill/MCP ส่วนกลางข้ามบัญชีใน container multi-account
> ทำงานใน container ผ่าน docker exec เท่านั้น ห้ามแก้ไฟล์ตั้งค่า ห้ามล็อกอินแทนฉัน
> 0. ตรวจสถานะล็อกอิน yolo1..5 (yoloN auth status) และ cyolo1..5 (cyoloN login status)
>    แสดงตาราง บัญชี | ล็อกอินแล้ว/ยัง ห้ามแสดงอีเมล องค์กร หรือ token
>    เลือกบัญชีที่ล็อกอินแล้วฝั่งละไม่เกิน 2 บัญชี ถ้าไม่มีบัญชีไหนล็อกอินเลย ให้หยุดและบอกวิธีล็อกอินใน JupyterLab Terminal
> 1. บันทึกข้อความใต้เส้น ==== ตามตัวอักษรลง /workspace/multi-account/verify-prompt.txt ใน container
> 2. รันทุกบัญชีที่เลือกพร้อมกันจากโฟลเดอร์ /workspace/multi-account แล้วรอจนครบทุกบัญชี (timeout บัญชีละ 15 นาที):
>    yoloN -p "$(cat verify-prompt.txt)" / cyoloN exec --skip-git-repo-check "$(cat verify-prompt.txt)"
> 3. คัดลอกภาพที่แต่ละบัญชีรายงานไปเป็น /workspace/multi-account/evidence/<บัญชี>/1-open.png, 2-search.png, 3-results.png
>    พร้อม log คำตอบเป็น run.log ในโฟลเดอร์เดียวกัน แล้วคัดลอกโฟลเดอร์ evidence ออกมาไว้ที่ ./evidence บนเครื่องผม
>    ด้วย docker cp multi-account:/workspace/multi-account/evidence ./evidence
> 4. สรุปตาราง บัญชี | รหัส shared-check | tool ที่เรียก | เที่ยวบินอันดับ 1 | เวลาที่ใช้ | PASS/FAIL
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

![ภาพเคลื่อนไหว: วางพรอมต์ทดสอบใน Claude Code app, Claude เลือก yolo1 yolo2 cyolo1 cyolo2 รันพร้อมกัน แล้วได้ตารางผล PASS ทั้ง 4 บัญชี](img/desktop-step4-test.gif)

**ผลจริง** (7 พ.ย. 2026 · **5 นาที 20 วินาที** สำหรับ 4 บัญชีพร้อมกัน · แบบที่ 2 ในบท `02_Setup_Multi_Account` รันทีละบัญชีใช้ ~10 นาที)

![ผลจริงจาก Claude: ทั้ง 4 บัญชี PASS รหัส shared-check ตรงกันตาม CLI และเที่ยวบินอันดับ 1 Vietjet THB 5,956](img/desktop-step4-result.png)

| บัญชี | รหัสจาก `shared-check` | Playwright MCP | เที่ยวบินอันดับ 1 | เวลา |
|---|---|---|---|---|
| yolo1 | `…claude-84dd0687` | PASS | Vietjet · 9 ชม. · แวะ 1 · THB 5,956 | 175 วินาที |
| yolo2 | เหมือน yolo1 | PASS | Vietjet · 9 ชม. · แวะ 1 · THB 5,956 | 160 วินาที |
| cyolo1 | `…codex-4e38203a` | PASS | Vietjet · 9 ชม. · แวะ 1 · THB 5,956 | 108 วินาที |
| cyolo2 | เหมือน cyolo1 | PASS | Vietjet · 9 ชม. · แวะ 1 · THB 5,956 | 98 วินาที |

**การตีความผล**

- **skill กลางใช้งานได้:** บัญชีต่างกันแต่ใช้ CLI เดียวกันได้รหัสเดียวกัน แสดงว่าอ่าน `shared-check` จากไฟล์เดียวกันใน `shared` (รหัสสุ่มตอนติดตั้ง ของผู้เรียนจะต่างจากนี้)
- **MCP กลางใช้งานได้:** ทุกบัญชีเรียก tool ของ `playwright` ได้เอง (`browser_navigate`, `browser_type`, `browser_take_screenshot` ฯลฯ)
- **ทำงานพร้อมกันได้:** 4 บัญชีใช้ Chromium แยกกันใน container เดียวโดยไม่ชนกัน เวลารวมจึงใกล้เคียงกับบัญชีที่ช้าที่สุด (175 วินาที) บวกเวลาที่ Claude ใช้ตรวจและสรุป

หลักฐานอยู่ใน container ที่ `/workspace/multi-account/evidence/<บัญชี>/` และ Claude คัดลอกออกมาไว้บนเครื่องเราที่ `./evidence/<บัญชี>/` ด้วย `docker cp` (container ไม่ได้ map โฟลเดอร์ของเครื่องไว้ ไฟล์ใน `/workspace` จึงหายเมื่อลบ container) แต่ละโฟลเดอร์มี `1-open.png`, `2-search.png`, `3-results.png` และ `run.log`

![ภาพเคลื่อนไหวจากภาพจริงของ yolo1: เปิด Google Flights, กรอก BKK ไป Tokyo วันอังคาร 15 ธันวาคม, ผลค้นหาอันดับ 1 Vietjet THB 5,956](img/evidence-yolo1.gif)

![ผลค้นหาเที่ยวบินจาก Playwright MCP ของ yolo1 yolo2 cyolo1 cyolo2 เรียงเป็นตาราง 2x2 ได้ผลชุดเดียวกัน](img/evidence-results-4accounts.png)

*ภาพจริงที่แต่ละบัญชีบันทึกเอง ภาพของ cyolo1 กับ cyolo2 เหมือนกันทุกพิกเซล เพราะทำขั้นตอนเดียวกันบนหน้าเว็บเดียวกันในนาทีเดียวกัน (แต่ละบัญชีเขียนไฟล์ของตัวเองคนละเวลา) ราคาของผู้เรียนจะต่างตามวันที่ค้นหา*

## ขั้นที่ 5 · ทดสอบความคงทน: ลบ container แล้วสร้างใหม่ (~3 นาที)

ขั้นนี้ทดสอบความคงทนของสภาพแวดล้อม ในแบบที่ 2 การลบ `devtools` ทำให้ต้องติดตั้งระบบหลายบัญชีใหม่และล็อกอินใหม่ทุกบัญชี ขั้นนี้ตรวจว่าแบบที่ 3 คืนสภาพได้อย่างไร

![ลบ container multi-account ด้วย docker rm -f แล้ว volume ai-accounts ยังเก็บล็อกอินของ yolo1–5 และ cyolo1–5 ไว้ครบ container ใหม่จาก image multi-account:1.0 ต่อเข้ากับ volume เดิม](img/concept-05-volume-persistence.png)

> [!IMPORTANT]
> **📋 คัดลอกกล่องนี้ → Claude Code app แล้วกด Enter**
>
> ```text
> พิสูจน์ว่าทุกอย่างถูกอบไว้ใน image แล้ว ด้วยการลบ container multi-account แล้วสร้างใหม่
> - ก่อนลบ: บันทึกสถานะล็อกอินทุกบัญชี (ห้ามแสดงอีเมลหรือ token)
> - ลบด้วย docker rm -f แล้วรัน docker run คำสั่งเดิม (port เดิม volume ai-accounts เดิม)
>   ห้ามลบ volume ห้ามติดตั้งอะไรเพิ่ม จับเวลาตั้งแต่ลบจน JupyterLab ตอบ 200
> - หลังสร้างใหม่ ตรวจผ่าน docker exec: yolo1..5 และ cyolo1..5 --version, cyolo1 mcp list เห็น playwright,
>   skill shared-check ยังอยู่, สถานะล็อกอินเทียบกับก่อนลบ
> - ให้บัญชีแรกที่ล็อกอินแล้วของแต่ละฝั่งตอบสั้น ๆ ว่า "พร้อม" (yoloN -p / cyoloN exec --skip-git-repo-check) เพื่อยืนยันว่าใช้งานได้จริงทันที
> สรุปเป็นตาราง ก่อนลบ | หลังสร้างใหม่ และเวลาที่ใช้
> ```

![ภาพเคลื่อนไหว: วางพรอมต์ลบแล้วสร้างใหม่ใน Claude Code app แล้วได้ตารางก่อนลบและหลังสร้างใหม่](img/desktop-step5-recreate.gif)

**ผลจริง** (7 พ.ย. 2026 · ~3 นาที): ตั้งแต่ลบจน JupyterLab ตอบ 200 ใช้ **3.27 วินาที** (ลบ 0.84 + สร้าง 0.71 + รอ 1.73) เวอร์ชัน CLI, `playwright`, skill `shared-check`, และสถานะล็อกอินทั้ง 10 บัญชี **เหมือนก่อนลบทุกรายการ** และ `yolo1` / `cyolo1` ตอบ "พร้อม" ได้ทันที (13.5 / 5.6 วินาที) โดยไม่ต้องล็อกอินใหม่

![ผลจริงจาก Claude: ตารางก่อนลบและหลังสร้างใหม่ ทุกรายการเหมือนเดิม เวลา 3.27 วินาที และคอลัมน์บอกว่าแต่ละอย่างเก็บอยู่ใน image, volume หรือ ./workspace](img/desktop-step5-result.png)

*คอลัมน์ "เก็บอยู่ที่" ในคำตอบสรุปหลักการของบทนี้: **โปรแกรมอยู่ใน image · ล็อกอินและ skill อยู่ใน volume** ไม่มีข้อมูลสำคัญอยู่ใน container จึงลบได้โดยไม่สูญเสียข้อมูล ส่วนไฟล์งานใน `/workspace` ต้องคัดลอกออกมาด้วย `docker cp` ก่อนลบ (ตอนรันจริงยัง map `./workspace` ไว้ จึงมีคอลัมน์ `./workspace` ในภาพ) ประโยคแรกของคำตอบที่ระบุว่า "พิสูจน์ไม่ได้ว่าทุกอย่างอบไว้ใน image" มาจาก MCP `rea` ที่เครื่องตัวอย่างเคยเพิ่มไว้ใน volume จากแลปอื่น ซึ่งดาวน์โหลดผ่าน `npx` ขณะใช้งาน ผู้เรียนที่เริ่มจาก volume ใหม่จะไม่มี MCP ตัวนี้ (ข้อสังเกต: MCP ที่ใช้เป็นประจำควรติดตั้งไว้ใน image ด้วย)*

ภาพเคลื่อนไหวด้านล่างเปรียบเทียบเวลาในการคืนสภาพของแบบที่ 2 และแบบที่ 3

![ภาพเคลื่อนไหว: เมื่อ container ถูกลบ แบบที่ 2 ต้องติดตั้งและล็อกอินใหม่รวมประมาณ 20 นาที แบบที่ 3 docker run ใหม่พร้อมใช้ใน 3.27 วินาที](img/gif-recreate-compare.gif)

*ตัวเลขของแบบที่ 3 วัดจริงในขั้นนี้ ตัวเลขของแบบที่ 2 มาจากผลรันจริงในบท `02_Setup_Multi_Account` (ติดตั้ง ~5 นาที) และเวลาโดยประมาณของการล็อกอิน (~15 นาที)*

![ภาพจำลอง: นักศึกษา 3 คนในห้องปฏิบัติการ หน้าจอทั้งสามแสดง multi-account:1.0 yolo1-5 OK cyolo1-5 OK playwright OK และ ready in 3.27 s เหมือนกัน](img/photo-03-reproducible-team.jpg)

*(ภาพจำลอง) ทุกเครื่องที่สร้าง container จาก image เดียวกันได้สภาพแวดล้อมเหมือนกัน*

## สรุป: แบบที่ 2 เทียบกับแบบที่ 3

| | แบบที่ 2 · ติดตั้งใน container ที่กำลังทำงาน | แบบที่ 3 · build จาก Dockerfile |
|---|---|---|
| ระบบหลายบัญชีอยู่ที่ | ใน container `devtools` | ใน image `multi-account:1.0` |
| ข้อมูลล็อกอินอยู่ที่ | ใน container (หายเมื่อลบ) | ใน volume `ai-accounts` (คงอยู่) |
| เมื่อลบ container | ติดตั้งใหม่ + ล็อกอินใหม่ | `docker run` ใหม่ พร้อมใช้ใน 3.27 วินาที |
| เครื่องใหม่ / แชร์ให้ทีม | ทำซ้ำทุกเครื่อง ผลอาจต่างกัน | build จาก Dockerfile เดียวกัน หรือ push image ให้ทีม pull ได้ชุดเดียวกัน |

## ข้อควรรู้

- **ข้อมูลล็อกอินอยู่ใน volume:** `docker rm -f multi-account` ปลอดภัย แต่ `docker volume rm ai-accounts` หรือ `docker system prune --volumes` จะลบข้อมูลล็อกอินทุกบัญชี
- **JupyterLab ไม่มีรหัสผ่าน:** Terminal ใน JupyterLab เข้าถึง credential ทุกบัญชีได้ หากไม่ต้องการให้เครื่องอื่นในเครือข่ายเข้าถึง ให้ใช้ `-p 127.0.0.1:8886:8888` หรือตั้ง `-e JUPYTER_PASSWORD=...` (Claude แจ้งเตือนทั้งสองเรื่องไว้ในผลขั้นที่ 1–2)
- **image ต้องไม่มีข้อมูลล็อกอิน:** ก่อน push image ขึ้น Docker Hub ให้ตรวจทุกครั้งว่าไม่มี credential ติดไป (Claude ตรวจไว้แล้วในขั้นที่ 1 ข้อ "ไม่มีข้อมูลล็อกอินใน image")
- **การแยกบัญชีเป็นระดับโฟลเดอร์:** ทุกบัญชีทำงานในฐานะ `root` คนเดียวกัน ไม่ใช่การแยกสิทธิ์ระดับระบบปฏิบัติการ
- **anonymous volume ของ Docker-in-Docker:** `docker rm -f` จะเหลือ volume ของ `/var/lib/docker` ไว้ ใช้ `docker rm -f -v multi-account` หากต้องการลบด้วย (ไม่กระทบ `ai-accounts` เพราะเป็น named volume)
- **image สำเร็จรูป:** หากไม่ต้องการ build เอง ใช้ image ของผู้สอน `tuchsanai/multi-account-devtool:2569_1` ผ่านสกิล `/maccount` ได้ (ใช้ volume `ai-accounts` เดียวกัน)

## คำสั่งที่ใช้บ่อย

บนเครื่อง (หรือสั่ง Claude Code app เป็นภาษาธรรมชาติ)

```bash
docker logs -f multi-account          # ดู log ตอน start
docker exec -it multi-account bash    # เข้า shell ใน container
docker stop multi-account             # หยุด
docker start multi-account            # เริ่มใหม่
docker rm -f multi-account            # ลบ container (ล็อกอินยังอยู่ใน volume ai-accounts)
docker build -t multi-account:1.0 _solution/MultiAccountDevtool   # build จากเฉลย
```

ใน container (JupyterLab Terminal)

```bash
yolo1 auth status         # สถานะล็อกอิน Claude
cyolo1 login status       # สถานะล็อกอิน Codex
cyolo1 mcp list           # ตรวจ MCP ของ Codex
multi-account-install     # รัน installer ซ้ำ (ไม่ทับของเดิม)
```
