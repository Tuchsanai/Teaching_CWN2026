# LAB 004 · สร้าง Skill ให้ AI รู้จักบัญชี yolo1–N และ cyolo1–N

**เป้าหมาย:** ให้ Claude Code เขียน "skill" ที่บอกวิธีเรียกบัญชี `yolo1`–`yolo5` และ `cyolo1`–`cyolo5` เก็บไว้ในโฟลเดอร์ `shared/skills` ที่สร้างไว้ตั้งแต่ LAB 001 จากนั้นทุกบัญชีของทั้งสอง CLI จะเรียกอีกบัญชีได้ด้วยประโยคสั้น ๆ เช่น "เรียก yolo2 … แล้วให้ cyolo1 ตรวจ" และได้เห็นด้วยตาว่า **ก่อนมี skill** AI ทำประโยคเดียวกันไม่ได้

**ก่อนเริ่ม:** ทำ [LAB 001](../001_LAB_Setup_Multi_Account/README.md) ให้ครบ (มีคำสั่ง `yolo1`–`yolo5`, `cyolo1`–`cyolo5` และโฟลเดอร์ `$HOME/ai-accounts`) และล็อกอิน `yolo1`, `yolo2`, `cyolo1` แล้ว เปิด Terminal ในโฟลเดอร์งานเดิม

ต่างจาก [LAB 003](../003_LAB_Codex_Calls_Claude/README.md): ใน LAB 003 ผู้เรียนต้องบอก AI เองว่าให้ใช้คำสั่ง `yolo1 -p` หรือ `cyolo1 exec --skip-git-repo-check` ใน LAB นี้ AI จะรู้วิธีเรียกเองจาก skill

**โมเดลที่ใช้ตลอด LAB:** ค่าเริ่มต้นของแต่ละ CLI คือ Claude Code = **Opus · high** และ Codex = **gpt-6-astra · medium** ไม่ต้องเปลี่ยนโมเดล (ถ้าหน้าจอ Claude แสดงโมเดลอื่น ให้พิมพ์ `/model opus` และ `/effort high`) skill ที่สร้างในขั้นที่ 2 จะใช้ค่าเริ่มต้นชุดเดียวกันนี้เมื่อผู้ใช้ไม่ระบุ

เวลาโดยประมาณ: 40–50 นาที (ขั้นที่ 2 ให้ AI ทำงานประมาณ 6 นาที)

![ภาพรวม LAB 004: สร้างสกิลครั้งเดียว เก็บใน shared/skills ทุกบัญชีเห็น แล้วเรียกใช้ด้วยประโยคเดียว](img/overview.png)

## skill คืออะไร และทำไมต้องทำ

skill คือโฟลเดอร์ที่มีไฟล์ `SKILL.md` หนึ่งไฟล์ ส่วนหัวของไฟล์ (frontmatter) มี `name` และ `description` ส่วนเนื้อหาคือคำแนะนำวิธีทำงาน AI อ่าน `description` ของทุก skill ที่มี แล้วตัดสินใจเองว่าประโยคของผู้ใช้ตรงกับ skill ไหน จึงค่อยโหลดเนื้อหาของไฟล์นั้นมาทำตาม ผู้ใช้เรียกเองก็ได้ (`/yolo` ใน Claude Code, `$yolo` ใน Codex)

![skill คืออะไร: SKILL.md = ส่วนหัวบอกชื่อและใช้เมื่อไร + เนื้อหาบอกวิธีทำ AI เทียบประโยคกับ description แล้วทำตาม](img/what-is-skill.png)

ทำไมต้องทำ: AI ไม่รู้ข้อเท็จจริงของ **เครื่องนี้** ว่า `yolo2` คือคำสั่ง wrapper ของ Claude Code อีกบัญชี ต้องเรียกด้วย flag อะไร ค่าเริ่มต้นคืออะไร และห้ามทำอะไร ในการทดลองจริงของ LAB นี้ (ดู[ส่วน C](#ส่วน-c--เปรียบเทียบ-ไม่มี-skill-กับ-มี-skill-ทดลองจริง)) เมื่อพิมพ์ประโยคเดียวกันโดยยังไม่มี skill:

- Claude Code ตีความ "เรียก yolo2" ว่าส่งข้อความหา session ชื่อ yolo2 หาไม่เจอ แล้วตอบว่า "เรียกไม่ได้" และคิดคำตอบเอง (0/3 ครั้งที่เรียกได้)
- Codex บางครั้งไปเปิดอ่านไฟล์ wrapper แล้วเดาคำสั่ง `yolo2 -p` เองโดยไม่ระบุโมเดล ไม่ตรวจล็อกอิน บางครั้งตอบว่าเรียกไม่ได้ (2/3 ครั้งที่เรียกได้)
- เมื่อมี skill ทั้งสอง CLI โหลด `SKILL.md` เอง ตรวจสถานะล็อกอิน แล้วรันคำสั่งตามที่เขียนไว้เหมือนกันทุกครั้ง (6/6)

skill จึงเป็นการ "เขียนข้อเท็จจริงของเครื่องนี้ครั้งเดียว" (บัญชี คำสั่ง ค่าเริ่มต้น กฎห้าม) วางใน `shared/skills` ให้ทุกบัญชีของทั้งสอง CLI ใช้ร่วมกัน ผลคือพิมพ์สั้นลง ทำซ้ำได้เหมือนเดิม และมีกฎความปลอดภัยติดมาด้วย

ทั้งสอง CLI อ่าน skill จาก config root ของบัญชี: Claude Code อ่าน `<CLAUDE_CONFIG_DIR>/skills/<ชื่อ>/SKILL.md` และ Codex อ่าน `<CODEX_HOME>/skills/<ชื่อ>/SKILL.md` ใน LAB 001 โฟลเดอร์ `skills` ของทุกบัญชีเป็น symlink ไปที่ `<tool>/shared/skills` จึงวางไฟล์ครั้งเดียวแล้วทุกบัญชีเห็น

## เส้นทางการเรียนรู้

| ขั้น | เนื้อหา | ใช้อะไร |
|---|---|---|
| 1 · ตรวจของเดิมและลองก่อนมี skill | ดูโฟลเดอร์ skill จาก LAB 001 ตรวจบัญชี แล้วพิมพ์ประโยคทดสอบให้ AI ที่ยังไม่มี skill | 🖥️ Terminal + 💬 yolo1 / cyolo1 |
| 2 · สร้าง skill | วางพรอมต์ 1 กรอบให้ Claude Code เขียน `SKILL.md` 4 ไฟล์และทดสอบเอง | 💬 yolo1 |
| 3 · ใช้ skill ฝั่ง Claude | พิมพ์ประโยคเดียวให้ Claude เรียก yolo2 และ cyolo1 | 💬 yolo1 + 🖥️ shell |
| 4 · ใช้ skill ฝั่ง Codex | พิมพ์ประโยคเดียวให้ Codex เรียก yolo2 | 💬 cyolo1 + 🖥️ shell |
| C · เปรียบเทียบ | ไม่มี skill กับมี skill จากการทดลองจริง 12 ครั้ง | อ่าน |

## ประโยคทดสอบ (ใช้ซ้ำทั้ง LAB)

ใช้ประโยคเดียวกันในขั้นที่ 1 (ก่อนมี skill) และขั้นที่ 3–4 (หลังมี skill) เพื่อเทียบผลได้ตรงกัน เฉลยของโจทย์คือ **900 บาท**

ฝั่ง Claude Code (ให้เรียก 2 บัญชี: yolo2 คิด แล้ว cyolo1 ตรวจ):

```text
เรียก yolo2 ให้คิดว่าซื้อของ 1000 บาท ลด 10% ต้องจ่ายกี่บาท แล้วส่งทั้งโจทย์และคำตอบนั้นให้ cyolo1 ตรวจ นำผลกลับมาสรุปสั้น ๆ ในหน้านี้ ถ้าเรียกไม่ได้ให้บอกตามจริง
```

ฝั่ง Codex (ให้เรียก yolo2 คิด แล้วตรวจเอง):

```text
เรียก yolo2 ให้คิดว่าซื้อของ 1000 บาท ลด 10% ต้องจ่ายกี่บาท แล้วคุณตรวจคำตอบนั้นเอง นำผลกลับมาสรุปสั้น ๆ ในหน้านี้ ถ้าเรียกไม่ได้ให้บอกตามจริง
```

ทั้งสองประโยคไม่ได้บอกชื่อคำสั่งหรือ flag ใด ๆ ต่างจาก LAB 003

## ขั้นที่ 1 · ตรวจของเดิม และลองก่อนมี skill (~10 นาที)

### 🎯 เป้าหมายของขั้นนี้
รู้ว่าจะวาง skill ไว้ที่ไหน บัญชีไหนใช้ทดสอบได้ และเห็นว่า AI ที่ยังไม่มี skill ทำประโยคทดสอบไม่ได้

### 1.1 ดูโฟลเดอร์ skill ที่ใช้ร่วมกัน (🖥️ Terminal)

```bash
ls -la $HOME/ai-accounts/.Claude/shared/skills $HOME/ai-accounts/.Codex/shared/skills
ls -la $HOME/ai-accounts/.Claude/yolo1/skills $HOME/ai-accounts/.Codex/cyolo1/skills
```

- ฝั่ง Claude ยังว่าง ฝั่ง Codex อาจมีโฟลเดอร์ `.system` ที่ Codex สร้างเองตอนรันครั้งแรก
- `yolo1/skills` และ `cyolo1/skills` ต้องเป็น symlink (`->`) ชี้ไปที่ `shared/skills` ของ CLI นั้น ถ้าไม่ใช่ ให้กลับไปทำ LAB 001 ขั้นที่ 2 ให้ผ่านก่อน

### 1.2 ตรวจว่าบัญชีไหนล็อกอินแล้ว (🖥️ Terminal)

```bash
yolo1 auth status --text; yolo2 auth status --text; yolo3 auth status --text
cyolo1 login status; cyolo2 login status
```

| CHECK | ACTUAL (ผลรันจริงในคอนเทนเนอร์ทดสอบ) |
|---|---|
| `yolo1 auth status --text` | `Login method: Claude Max account` |
| `yolo2 auth status --text` | `Login method: Claude Team account` |
| `yolo3 auth status --text` | `Not logged in. Run claude auth login to authenticate.` |
| `cyolo1 login status` | `Logged in using ChatGPT` |
| `cyolo2 login status` | `Not logged in` |
- **ต้องตรง:** `yolo1`, `yolo2`, `cyolo1` ล็อกอินแล้ว
- **ต่างได้:** ชนิดบัญชี (Max/Team/Pro) และบัญชีอื่นที่ยังไม่ล็อกอิน

`auth status` แบบไม่ใส่ `--text` จะพิมพ์ JSON ที่มีอีเมลและชื่อองค์กรของบัญชี อย่านำไปวางในรายงานหรือภาพหน้าจอ

### 1.3 ลองก่อนมี skill (💬 yolo1 แล้ว 💬 cyolo1)

**ฝั่ง Claude:** พิมพ์ `yolo1` ตอบหน้ายืนยันโฟลเดอร์และโหมด Bypass Permissions เหมือน LAB 001 (A.1) หน้าจอควรแสดง `Opus 5` และ `high` จากนั้นวางประโยคทดสอบฝั่ง Claude แล้วกด Enter

![ผลจริงก่อนมี skill: Claude หา session ชื่อ yolo2 และ cyolo1 ไม่เจอ ตอบว่าเรียกไม่ได้ แล้วคิดคำตอบเอง](img/noskill-claude-result.png)

**ผลตอบจริง (Opus · high, ใช้เวลา 26 วินาที):** Claude ใช้เครื่องมือ `ListAgents` และ `SendMessage` เพื่อหา "เอเจนต์" ชื่อ `yolo2` และ `cyolo1` ได้ `No agent named 'yolo2' is reachable` แล้วสรุปว่า "เรียกไม่ได้ครับ" พร้อมคำตอบที่คิดเอง 900 บาท ไม่มีการรันคำสั่ง `yolo2` เลย

กด Ctrl+C สองครั้งเพื่อออก

**ฝั่ง Codex:** พิมพ์ `cyolo1` หน้าจอแสดง `model: gpt-6-astra` วางประโยคทดสอบฝั่ง Codex แล้วกด Enter (ถ้าข้อความยังอยู่ในช่องพิมพ์ให้กด Enter อีกครั้ง)

![ผลจริงก่อนมี skill: Codex ค้นรายการเครื่องมือหา yolo2 ไม่พบ ตอบว่าเรียกไม่ได้ แล้วคิดคำตอบเอง](img/noskill-codex-result.png)

**ผลตอบจริง (Astra · medium, ใช้เวลา 16 วินาที):** Codex ค้นรายการเครื่องมือของตัวเองหาชื่อ `yolo2` ไม่พบ ตอบว่า "เรียก yolo2 ไม่ได้ครับ เพราะไม่มีเอเจนต์หรือเครื่องมือชื่อนี้ในเซสชัน" แล้วคำนวณเอง 900 บาท

ผลที่ผู้เรียนได้อาจต่างจากภาพ ในการทดลองซ้ำอีก 2 ครั้งผ่าน `cyolo1 exec` Codex ไปเปิดอ่านไฟล์ `/usr/local/bin/yolo2` แล้วเดาคำสั่ง `yolo2 -p '…'` เองจนได้คำตอบ แต่ไม่ระบุโมเดล ไม่ตรวจล็อกอิน (ดูส่วน C) นี่คือประเด็นของ LAB: **ไม่มี skill = ผลไม่แน่นอน**

กด Ctrl+C สองครั้งเพื่อออก แล้วไปขั้นที่ 2

## ขั้นที่ 2 · ให้ Claude Code สร้าง skill (💬 yolo1 | ~10 นาที)

### 🎯 เป้าหมายของขั้นนี้
ได้ `SKILL.md` 4 ไฟล์ (skill `yolo` และ `cyolo` อย่างละ 1 ไฟล์ต่อ CLI) ที่ AI ตรวจ docs, ตรวจ `--help` และทดสอบเรียกจริงแล้ว พร้อมรายงาน `skill-report.md`

### 2.1 เปิด Claude Code

```bash
yolo1
```

ตรวจว่าหน้าจอแสดง **Opus 5** และ **high** (ค่าเริ่มต้น) แล้วคัดลอกพรอมต์ทั้งกรอบด้านล่างไปวาง

### 📋 พรอมต์สำหรับคัดลอก (คัดลอกทั้งกรอบ วางใน 💬 ช่องสนทนา AI แล้ว Enter)
```text
สร้าง Skill ให้ Claude Code และ Codex CLI รู้จักบัญชีหลายบัญชีที่ตั้งค่าไว้แล้วบนเครื่องนี้
ห้ามอ่านไฟล์ README ของ LAB เพื่อหาเฉลย ห้ามล็อกอินแทนฉัน ห้ามอ่าน คัดลอก หรือแสดงไฟล์ credential ใด ๆ

## ตัวแปรตั้งค่า (แก้ที่นี่ที่เดียว ที่อื่นต้องอ้างอิงตัวแปรนี้)
BASE_PATH="$HOME/ai-accounts"

## สิ่งที่มีอยู่แล้ว (ตรวจจริงก่อน ห้ามเดา)
- คำสั่ง yolo1..yolo5 = Claude Code คนละบัญชี (CLAUDE_CONFIG_DIR=$BASE_PATH/.Claude/yoloN)
- คำสั่ง cyolo1..cyolo5 = Codex CLI คนละบัญชี (CODEX_HOME=$BASE_PATH/.Codex/cyoloN)
- $BASE_PATH/.Claude/shared/skills และ $BASE_PATH/.Codex/shared/skills คือโฟลเดอร์ skill ที่ทุกบัญชีของ CLI นั้นมองเห็นผ่าน symlink <account>/skills
- ตรวจว่าบัญชีไหนล็อกอินแล้วด้วย yoloN auth status และ cyoloN login status ครบทั้ง 10 ตัว บัญชีที่ยังไม่ล็อกอินให้บันทึกว่า "ยังไม่ล็อกอิน" เท่านั้น

## Skill ที่ต้องได้ (2 skill × 2 CLI = 4 ไฟล์ SKILL.md)
1. skill ชื่อ yolo  — ใช้เมื่อผู้ใช้พูดว่า "เรียก yoloN", "ให้ Claude อีกบัญชีทำ...", "บัญชี Claude ไหนล็อกอินอยู่"
2. skill ชื่อ cyolo — ใช้เมื่อผู้ใช้พูดว่า "เรียก cyoloN", "ให้ Codex ตรวจ...", "บัญชี Codex ไหนล็อกอินอยู่"
วางที่ $BASE_PATH/.Claude/shared/skills/<ชื่อ>/SKILL.md และสำเนาเนื้อหาเดียวกันที่ $BASE_PATH/.Codex/shared/skills/<ชื่อ>/SKILL.md

## เนื้อหาที่แต่ละ SKILL.md ต้องมี
- frontmatter name และ description ภาษาไทยที่บอกว่าใช้เมื่อไร ตามรูปแบบใน official docs ของแต่ละ CLI
- ตารางบัญชี: คำสั่ง | CLI | config root | สถานะล็อกอินที่ตรวจได้ตอนนี้
- วิธีเรียกแบบไม่เปิดหน้าจอ (non-interactive) ที่ทดสอบแล้วว่าใช้ได้จริงกับเวอร์ชันที่ติดตั้ง:
  Claude: yoloN -p --model <model> --effort <effort> "<prompt>" < /dev/null
  Codex:  cyoloN exec --skip-git-repo-check -m <model> -c model_reasoning_effort=<effort> -o <ไฟล์ผลลัพธ์> "<prompt>" < /dev/null
  ตรวจชื่อ flag จาก --help ของเวอร์ชันจริงก่อนเขียนลงสกิล
- ค่าเริ่มต้นเมื่อผู้ใช้ไม่ระบุ: บัญชี 1, Claude = opus + high, Codex = gpt-6-astra + medium ผู้ใช้ระบุเองได้เสมอ
- กฎ: บัญชีที่ผู้ใช้ระบุยังไม่ล็อกอิน → แจ้งผู้ใช้ ห้ามสลับบัญชีเอง ห้ามล็อกอินแทน ห้ามอ่านหรือส่งต่อไฟล์ credential
- วิธีส่งค่าต่อ (relay): อ่านผลจากคำสั่งแรกแล้วใส่ใน prompt ของคำสั่งถัดไป ทำได้ทั้งข้ามบัญชีและข้าม CLI

## Docs
ตรวจ official docs และ --help ของเวอร์ชันจริงก่อน implement ห้ามเดาตำแหน่งไฟล์ รูปแบบ frontmatter หรือ flag
- https://code.claude.com/docs/en/skills
- https://developers.openai.com/codex/skills

## ทดสอบ (รายงานตามจริง PASS / FAIL / SKIP)
- ไฟล์ SKILL.md ครบ 4 ไฟล์ และมองเห็นจากทุกบัญชีผ่าน <account>/skills
- เรียกจริง 1 ครั้งต่อบัญชีที่ล็อกอินแล้ว ด้วยโจทย์ "ตอบเป็นตัวเลขล้วนอย่างเดียว: 12*12" ผ่านวิธีในสกิล ได้ 144 = PASS
- ส่งค่าต่อ 1 ครั้ง: ให้ yolo1 ตอบ แล้วส่งโจทย์กับคำตอบให้ cyolo1 ตรวจ
- บัญชีที่ยังไม่ล็อกอิน = SKIP พร้อมเหตุผล

## รายงาน
เขียน skill-report.md ในโฟลเดอร์ปัจจุบัน: ตำแหน่งไฟล์ทั้ง 4, ตาราง รายการ | หลักฐาน | PASS/FAIL/SKIP | เหตุผล, ข้อจำกัดที่พบ ห้ามใส่ข้อมูลลับ

ทำเฉพาะขั้นนี้ เมื่อเสร็จให้แสดงเนื้อหา SKILL.md ของ yolo ฉบับ Claude และตารางทดสอบบนหน้าจอ แล้วหยุดรอ ห้ามทำขั้นถัดไปเอง
```

![Claude Code จริงในคอนเทนเนอร์: วางพรอมต์ขั้นที่ 2 ในช่องสนทนา](img/claude-paste-prompt.png)

ข้อความ `[Pasted text …]` คือพรอมต์ที่วางแล้ว กด Enter เพื่อเริ่มทำงาน ระหว่างนี้ AI จะเรียก `yolo1`, `yolo2`, `cyolo1` จริงหลายครั้งเพื่อทดสอบ (ใช้โควตาของบัญชีเหล่านั้น) รอจนขึ้นข้อความหยุดรอ

### ✅ Expected Output (ผลรันจริง Opus · high ในคอนเทนเนอร์ทดสอบ)
| CHECK | ACTUAL |
|---|---|
| ไฟล์ที่สร้าง | `.Claude/shared/skills/yolo/SKILL.md`, `.Claude/shared/skills/cyolo/SKILL.md`, `.Codex/shared/skills/yolo/SKILL.md`, `.Codex/shared/skills/cyolo/SKILL.md` (md5 ตรงกันเป็นคู่) |
| SKILL.md ของ yolo | frontmatter `name: yolo` + `description` ภาษาไทย, ตารางบัญชี 5 แถว, คำสั่ง `yoloN -p --model … --effort … "<prompt>" < /dev/null`, ค่าเริ่มต้น `yolo1` / `opus` / `high`, กฎห้ามสลับบัญชี/ห้ามอ่าน credential, ตัวอย่าง relay |
| SKILL.md ของ cyolo | ค่าเริ่มต้น `cyolo1` / `gpt-6-astra` / `medium` และคำสั่ง `cyoloN exec --skip-git-repo-check -m … -c model_reasoning_effort=… -o … "<prompt>" < /dev/null` |
| Claude Code เห็น skill | session ที่กำลังทำงานแสดง `yolo` และ `cyolo` ในรายการ skill ทันที → PASS |
| Codex เห็น skill | `cyolo1 exec` ถามว่ามี skill ชื่อ yolo และ cyolo หรือไม่ ได้ `มีทั้ง yolo และ cyolo` → PASS |
| yolo1 / yolo2 ตอบ `12*12` | `144` → PASS ทั้งคู่ |
| cyolo1 ตอบ `12*12` | ไฟล์ `-o` = `144` → PASS |
| relay yolo1 → cyolo1 | yolo1 ตอบ `144` ส่งให้ cyolo1 ตรวจได้ `ถูก ค่าที่ถูกต้องคือ 144` → PASS |
| yolo3–5, cyolo2–5 | SKIP (ยังไม่ล็อกอิน) |
| รายงาน | `skill-report.md` สรุป PASS 9 · SKIP 8 · FAIL 0 |
| เวลาและรอบ | 5 นาที 58 วินาที · 29 รอบสนทนา · ค่าใช้จ่ายตาม list price ที่ CLI รายงาน $1.39 (บัญชี subscription ไม่ถูกเรียกเก็บตามตัวเลขนี้) |
- **ต้องตรง:** (1) SKILL.md ครบ 4 ไฟล์ในโฟลเดอร์ `shared/skills` (2) ทั้งสอง CLI เห็น skill (3) บัญชีที่ล็อกอินแล้ว PASS บัญชีอื่น SKIP (4) ค่าเริ่มต้นในสกิลเป็น opus/high และ gpt-6-astra/medium
- **ต่างได้:** ถ้อยคำใน SKILL.md, จำนวนรอบ, เวลา, ค่าใช้จ่าย

ตัวอย่าง `SKILL.md` ที่ AI สร้างในการทดลองนี้อยู่ที่ [evidence/generated-skills/](evidence/generated-skills/) และรายงานที่ [evidence/06-skill-report.md](evidence/06-skill-report.md) ใช้เทียบเท่านั้น ไม่ต้องคัดลอกไปใช้

### 🔍 จุดที่ผู้เรียนต้องตรวจ (🖥️ Terminal เปิดหน้าต่างใหม่)

```bash
find $HOME/ai-accounts -path '*/shared/skills/*' -name SKILL.md -not -path '*/.system/*'
diff $HOME/ai-accounts/.Claude/shared/skills/yolo/SKILL.md $HOME/ai-accounts/.Codex/shared/skills/yolo/SKILL.md && echo SAME
grep -n -A4 'ค่าเริ่มต้น' $HOME/ai-accounts/.Claude/shared/skills/yolo/SKILL.md
ls -la $HOME/ai-accounts/.Claude/yolo2/skills/ $HOME/ai-accounts/.Codex/cyolo2/skills/
```

- [ ] `find` ได้ 4 ไฟล์
- [ ] `diff` ไม่มีผลต่างและพิมพ์ `SAME`
- [ ] ค่าเริ่มต้นใน `yolo/SKILL.md` เป็น `opus` + `high` (และใน `cyolo/SKILL.md` เป็น `gpt-6-astra` + `medium`)
- [ ] บัญชีที่ยังไม่ล็อกอิน (เช่น `yolo2`, `cyolo2`) ก็เห็นโฟลเดอร์ `yolo/` และ `cyolo/` ผ่าน symlink
- [ ] `skill-report.md` มีตาราง PASS/FAIL/SKIP และไม่มีอีเมล token หรือข้อมูลลับ

## ขั้นที่ 3 · ใช้ skill ฝั่ง Claude Code (💬 yolo1 | ~5 นาที)

ทำในหน้า Claude Code เดิม หรือเปิด `yolo1` ใหม่ (skill ที่เพิ่งสร้างถูกโหลดให้ทันทีโดยไม่ต้องเปิดใหม่)

### 3.1 · วิธีที่ 1: พิมพ์ในหน้าสนทนา AI

**1. ดูรายการ skill**

พิมพ์ `/skills` แล้วกด Enter จะเห็น `cyolo` และ `yolo` ชนิด `user` ทั้งคู่เปิดใช้ (`on`) กด Esc เพื่อปิดรายการ

![รายการ skill ในหน้า Claude Code: cyolo และ yolo](img/claude-skills-list.png)

**2. วางประโยคทดสอบฝั่ง Claude (ประโยคเดียวกับขั้นที่ 1.3)**

![พิมพ์ประโยคเดียวในหน้า Claude Code (Opus · high)](img/claude-prompt-typed.png)

**3. ส่งและดูผล**

กด Enter แล้วรอ คราวนี้ Claude แสดง `Skill(yolo)` และ `Skill(cyolo)` ว่าโหลด skill เอง ตรวจสถานะล็อกอิน แล้วรันคำสั่งของอีกสองบัญชี

![ผลจริงหลังมี skill: Claude โหลด skill yolo และ cyolo เอง เรียก yolo2 (opus · high) แล้วส่งให้ cyolo1 (gpt-6-astra · medium) ตรวจ](img/claude-skill-call-result.png)

**ผลตอบจริง (ใช้เวลา 39 วินาที):**

```text
สรุป
yolo2 (Claude Code, บัญชี team <email> / model opus / effort high)
  900 บาท — ลด 10% = 1000 × 0.10 = 100 บาท → 1000 − 100 = 900 (หรือ 1000 × 0.9 = 900)
cyolo1 (Codex CLI, ล็อกอิน ChatGPT / model gpt-6-astra / effort medium) — ผลตรวจ:
  ถูกต้องทั้งคำตอบและวิธีคิด ลด 10% ของ 1,000 บาท คือ 100 บาท จึงต้องจ่าย 900 บาท

ทั้งสองบัญชีเรียกได้ปกติ ไม่มีบัญชีไหนถูกข้าม ผลตรงกัน: จ่าย 900 บาท
```

สิ่งที่ Claude รันจริงเบื้องหลัง (จากบันทึก session ใน [evidence/08-skill-claude-tui-session.txt](evidence/08-skill-claude-tui-session.txt)): `yolo2 auth status` → `yolo2 -p --model opus --effort high "…"` → `cyolo1 login status` → นำคำตอบใส่ใน prompt ของ `cyolo1 exec --skip-git-repo-check -m gpt-6-astra -c model_reasoning_effort=medium -o … "…"` ตามที่เขียนไว้ใน skill ทุกประการ

### 3.2 · วิธีที่ 2: ส่งด้วยคำสั่งจาก shell

กด Ctrl+C สองครั้งเพื่อกลับมาที่ shell แล้วรันคำสั่งเดียว skill ทำงานในโหมด `-p` ด้วยเช่นกัน

```bash
yolo1 --model opus --effort high -p 'เรียก yolo2 ให้คิดว่าซื้อของ 1000 บาท ลด 10% ต้องจ่ายกี่บาท แล้วส่งทั้งโจทย์และคำตอบนั้นให้ cyolo1 ตรวจ นำผลกลับมาสรุปสั้น ๆ ถ้าเรียกไม่ได้ให้บอกตามจริง'
```

![ผลจริงจาก shell: yolo1 -p ใช้ skill เรียก yolo2 และ cyolo1](img/claude-shell-result.png)

**ผลตอบจริง:**

```text
เรียกได้ทั้งสองบัญชี ผลสรุป:

| ขั้น | บัญชี | model / effort | ผล |
|---|---|---|---|
| คิดโจทย์ | `yolo2` (claude.ai, team) | opus / high | **900 บาท** — 1000 × 0.9 = 900 |
| ตรวจคำตอบ | `cyolo1` (Codex, ChatGPT) | gpt-6-astra / medium | **ถูกต้อง** — ลด 10% = 100 บาท เหลือจ่าย 900 บาท |

ทั้งสองฝั่งตรงกัน: ต้องจ่าย **900 บาท** ไม่มีบัญชีไหนถูกข้ามเพราะยังไม่ล็อกอิน
```

## ขั้นที่ 4 · ใช้ skill ฝั่ง Codex (💬 cyolo1 | ~5 นาที)

### 4.1 · วิธีที่ 1: พิมพ์ในหน้าสนทนา AI

**1. เปิด Codex**

```bash
cyolo1
```

หน้าจอแสดง `model: gpt-6-astra` และ `permissions: YOLO mode` (ระดับ reasoning เริ่มต้นของ Astra คือ medium)

**2. ดูรายการ skill**

พิมพ์ `/skills` กด Enter (ถ้ายังไม่ทำงานให้กด Enter อีกครั้ง) เลือก **List skills** จะได้ช่องพิมพ์ที่ขึ้นต้นด้วย `$` พิมพ์ `yol` เพื่อกรอง จะเห็น `yolo` และ `cyolo` ชนิด `[Skill]` พร้อม description ภาษาไทยที่ AI เขียนไว้

![รายการ skill ใน Codex เมื่อพิมพ์ $yol: yolo และ cyolo](img/codex-skills-list.png)

**3. เลือก skill แล้วพิมพ์ประโยคทดสอบฝั่ง Codex**

เลื่อนไปที่ `yolo` กด Enter จะได้ `$yolo` ในช่องพิมพ์ แล้ววางประโยคทดสอบฝั่ง Codex ต่อท้าย

![พิมพ์ $yolo ตามด้วยประโยคเดียวในหน้า Codex](img/codex-prompt-typed.png)

**4. ส่งและดูผล**

กด Enter (ถ้าข้อความยังอยู่ในช่องพิมพ์ให้กด Enter อีกครั้ง) Codex จะอ่าน `SKILL.md` ตรวจสถานะล็อกอิน แล้วรัน `yolo2` ด้วยโมเดลและ effort ตามค่าเริ่มต้นในสกิล

![ผลจริงหลังมี skill: Codex อ่าน SKILL.md ของ yolo แล้วเรียก yolo2 -p --model opus --effort high](img/codex-skill-call-result.png)

**ผลตอบจริง (ใช้เวลา 21 วินาที):**

```text
ผมจะใช้สกิล yolo เรียก yolo2 แล้วตรวจคำตอบด้วยตัวเองครับ
  Explored: Read SKILL.md (yolo skill)
  Ran yolo2 auth status < /dev/null
  Ran yolo2 -p --model opus --effort high 'ซื้อของราคา 1000 บาท ลด 10% ต้องจ่ายกี่บาท? ตอบสั้น ๆ พร้อมวิธีคำนวณ' < /dev/null

เรียก yolo2 สำเร็จ (model: opus, effort: high) ได้คำตอบว่า 900 บาท
ผมตรวจแล้วถูกต้อง: ส่วนลด 1,000 × 10% = 100 บาท จึงจ่าย 1,000 − 100 = 900 บาท
```

### 4.2 · วิธีที่ 2: ส่งด้วยคำสั่งจาก shell

กด Ctrl+C สองครั้งเพื่อกลับมาที่ shell คำสั่งนี้ไม่ได้ใส่ `$yolo` เพื่อดูว่า Codex เลือก skill เองจาก description ได้หรือไม่

```bash
cyolo1 exec --skip-git-repo-check --model gpt-6-astra -c model_reasoning_effort=medium 'เรียก yolo2 ให้คิดว่าซื้อของ 1000 บาท ลด 10% ต้องจ่ายกี่บาท แล้วคุณตรวจคำตอบนั้นเอง สรุปสั้น ๆ ถ้าเรียกไม่ได้ให้บอกตามจริง'
```

![ผลจริงจาก shell: codex exec เลือก skill yolo เองแล้วเรียก yolo2 (ปิดบังอีเมลและชื่อองค์กร)](img/codex-shell-result.png)

**ผลตอบจริง:**

```text
เรียก yolo2 สำเร็จ (model: opus, effort: high) ได้คำตอบว่า 900 บาท

ผมตรวจแล้วถูกต้อง: ส่วนลด 1,000 × 10% = 100 บาท จึงจ่าย 1,000 − 100 = 900 บาท
```

Codex เริ่มด้วยข้อความ "ผมจะใช้สกิล yolo …" แล้วรัน `cat …/skills/yolo/SKILL.md`, `yolo2 auth status`, และ `yolo2 -p --model opus --effort high '…'` ตามลำดับ โหมด `exec` พิมพ์ผลของทุกคำสั่งออกหน้าจอ รวมถึง JSON ของ `auth status` ที่มีอีเมลและชื่อองค์กร จึงต้องปิดบังก่อนแชร์ภาพ

## ส่วน C · เปรียบเทียบ ไม่มี skill กับ มี skill (ทดลองจริง)

ทดลองด้วยประโยคทดสอบเดียวกัน บนเครื่องเดียวกัน (คอนเทนเนอร์ที่ตั้งค่าตาม LAB 001) เงื่อนไขละ 6 ครั้ง: ฝั่ง Claude (`yolo1`, Opus · high) 3 ครั้ง และฝั่ง Codex (`cyolo1`, Astra · medium) 3 ครั้ง แต่ละฝั่งรันจากหน้าสนทนา 1 ครั้งและจาก shell (`-p` / `exec`) 2 ครั้ง ผลทั้งหมดอ่านจากบันทึก session ไม่ได้เชื่อข้อความที่ AI สรุปเอง ([evidence/ab/](evidence/ab/) และ [evidence/13-session-durations.txt](evidence/13-session-durations.txt))

### ตารางสรุป

| | ไม่มี skill (6 ครั้ง) | มี skill (6 ครั้ง) |
|---|---|---|
| เรียก `yolo2` ได้จริง (มีคำสั่ง `yolo2 -p` ในบันทึก) | **2/6** (Codex `exec` 2 ครั้ง) | **6/6** |
| ตรวจสถานะล็อกอินก่อนเรียก | 0/6 | 6/6 |
| ระบุ model/effort ตามที่ต้องการ (opus · high) | 0/6 | 6/6 |
| ฝั่ง Claude ส่งต่อให้ `cyolo1` ตรวจได้ | 0/3 | 3/3 |
| คำตอบสุดท้าย 900 บาท | 6/6 แต่ 4 ครั้งเป็นการ "คิดเอง" ของผู้เรียก | 6/6 มาจาก yolo2 จริง |
| สิ่งที่ AI ทำแทน | Claude: `ListAgents` / `SendMessage` หา session ชื่อ yolo2 → ไม่พบ · Codex: อ่านไฟล์ wrapper 3 คำสั่งแล้วเดา หรือค้นรายการเครื่องมือแล้วยอมแพ้ | โหลด SKILL.md → `auth status` / `login status` → รันคำสั่งตามสกิล |

### รายละเอียดทั้ง 12 ครั้ง

| เงื่อนไข | ผู้เรียก | วิธี | สิ่งที่ AI ทำ (จากบันทึก) | เรียก yolo2? | คำตอบ | เวลา | โทเคน / ค่าใช้จ่าย |
|---|---|---|---|---|---|---|---|
| ไม่มี skill | Claude Opus·high | หน้าสนทนา | `ListAgents`, `ls`, `SendMessage` → "No agent named 'yolo2' is reachable" | ✗ | 900 (คิดเอง) | 26 s | – |
| ไม่มี skill | Claude | shell `-p` #1 | `ListAgents` แล้วตอบว่าเรียกไม่ได้ | ✗ | 900 (คิดเอง) | 16 s | $0.11 |
| ไม่มี skill | Claude | shell `-p` #2 | `ListAgents`, `SendMessage` ×2 → ไม่ถึง | ✗ | 900 (คิดเอง) | 21 s | $0.17 |
| ไม่มี skill | Codex Astra·medium | หน้าสนทนา | ค้นรายการเครื่องมือหา "yolo2" → ไม่พบ | ✗ | 900 (คิดเอง) | 16 s | 52k in / 198 out |
| ไม่มี skill | Codex | shell `exec` #1 | `command -v yolo2`, `file`, `head -n 100 /usr/local/bin/yolo2`, `yolo2 -p '…'` (ไม่ระบุ model/effort) | ✓ | 900 | 36 s | 104k in / 377 out |
| ไม่มี skill | Codex | shell `exec` #2 | `command -v`, `ls -l`, `head -n 100`, `yolo2 -p '…'` (ไม่ระบุ model/effort) | ✓ | 900 | 33 s | 103k in / 398 out |
| มี skill | Claude Opus·high | หน้าสนทนา | `Skill(yolo)` → auth status → `yolo2 -p --model opus --effort high` → `Skill(cyolo)` → login status → `cyolo1 exec … -o` | ✓ + cyolo1 ✓ | 900 / ถูกต้อง | 39 s | – |
| มี skill | Claude | shell `-p` #1 | เหมือนหน้าสนทนา | ✓ + cyolo1 ✓ | 900 / ถูกต้อง | 45 s | $0.26 |
| มี skill | Claude | shell `-p` #2 | อ่าน SKILL.md ทั้งสองไฟล์ → auth/login status → yolo2 → cyolo1 | ✓ + cyolo1 ✓ | 900 / ถูกต้อง | 46 s | $0.22 |
| มี skill | Codex Astra·medium | หน้าสนทนา `$yolo` | `cat …/yolo/SKILL.md`, `yolo2 auth status`, `yolo2 -p --model opus --effort high` | ✓ | 900 ✓ | 21 s | 72k in / 291 out |
| มี skill | Codex | shell `exec` #1 (ไม่ใส่ `$yolo`) | เหมือนหน้าสนทนา | ✓ | 900 ✓ | 26 s | 86k in / 305 out |
| มี skill | Codex | shell `exec` #2 (ไม่ใส่ `$yolo`) | เหมือนหน้าสนทนา | ✓ | 900 ✓ | 26 s | 86k in / 318 out |

ค่าใช้จ่ายของ Claude คือ list price ที่ CLI รายงาน (`total_cost_usd`) ไม่ใช่ยอดที่บัญชี subscription ถูกเรียกเก็บ โทเคนของ Codex ส่วนใหญ่เป็น cache (เช่น 86k in มี 74k เป็น cached)

### อ่านผลอย่างไร

- **ไม่มี skill ไม่ได้แปลว่าล้มเหลวเสมอ** Codex เดาถูก 2 ใน 3 เพราะไปอ่านไฟล์ wrapper เอง แต่เป็นการเดา: ไม่ระบุโมเดล ไม่ตรวจล็อกอิน และอีกครั้งหนึ่งก็ยอมแพ้ ผลจึงไม่แน่นอนและตรวจสอบย้อนหลังยาก
- **Claude ไม่มี skill ล้มเหลวทั้ง 3 ครั้ง** เพราะตีความคำว่า "เรียก yolo2" เป็นการส่งข้อความหา session อื่น ซึ่งเป็นความสามารถที่มันรู้จัก ไม่ใช่คำสั่ง shell ของเครื่องนี้ที่มันไม่รู้จัก
- **มี skill แล้วเวลาต่อครั้งของฝั่ง Claude เพิ่มขึ้น (16–26 s → 39–46 s)** เพราะมีการเรียก AI อีก 2 ตัวจริง ส่วนฝั่ง Codex กลับเร็วขึ้น (33–36 s → 21–26 s) เพราะไม่ต้องสำรวจไฟล์ก่อน
- ค่าเริ่มต้นในสกิล (opus · high, gpt-6-astra · medium) ถูกส่งไปกับทุกคำสั่งโดยผู้ใช้ไม่ต้องพิมพ์ เปลี่ยนที่ `SKILL.md` ที่เดียวแล้วทุกบัญชีได้ผลเหมือนกัน

### ก่อนและหลังในมุมผู้เรียน

| | LAB 003 (ยังไม่มี skill) | LAB 004 (มี skill) |
|---|---|---|
| สิ่งที่ผู้เรียนต้องพิมพ์ | "…เรียก Claude ผ่านคำสั่ง `yolo1 -p` …" / "…เรียก Codex ผ่านคำสั่ง `cyolo1 exec --skip-git-repo-check` …" | "เรียก yolo2 … แล้วให้ cyolo1 ตรวจ" |
| ใครรู้ flag และค่าเริ่มต้น | ผู้เรียน (ต้องบอกในพรอมต์ทุกครั้ง) | `SKILL.md` (เขียนครั้งเดียว) |
| ตรวจสถานะล็อกอินก่อนเรียก | ไม่มี | AI รัน `auth status` / `login status` เองตามกฎใน skill |
| ใช้ได้กับบัญชีไหน | บัญชีที่เปิดอยู่ | ทุกบัญชีของทั้งสอง CLI เพราะไฟล์อยู่ใน `shared/skills` |

## จุดที่ต้องเข้าใจ

- skill ไม่ได้ทำให้ AI "เก่งขึ้น" แต่ทำให้ AI รู้ข้อเท็จจริงของเครื่องนี้: มีบัญชีอะไร เรียกอย่างไร ค่าเริ่มต้นคืออะไร และห้ามทำอะไร
- AI เลือก skill จาก `description` เมื่อประโยคของผู้ใช้ตรงกับคำในนั้น จึงควรเขียน description ให้มีคำที่ผู้ใช้จะพูดจริง เช่น "เรียก yoloN"
- skill ที่ AI สร้างมีตารางสถานะล็อกอินเป็นภาพ ณ วันที่สร้าง จึงมีกฎให้ตรวจสดด้วย `auth status` / `login status` ก่อนใช้ทุกครั้ง และห้ามล็อกอินแทนหรือสลับบัญชีเอง
- ในการทดลองนี้ Codex 0.153.4 อ่าน skill จาก `<CODEX_HOME>/skills` ได้จริง แม้ docs ฉบับปัจจุบันจะเน้นโฟลเดอร์ `.agents/skills` หากอัปเกรดเวอร์ชันแล้ว `/skills` ไม่แสดง `yolo` ให้ตรวจตำแหน่งใหม่จาก docs
- ทั้งสอง wrapper รันแบบข้ามการขออนุญาต (LAB 001) skill จึงมีอำนาจรันคำสั่งได้เต็มที่ ควรระบุขอบเขตงานในพรอมต์ให้ชัดเสมอ

*ภาพและผลลัพธ์ทั้งหมดมาจากการรันจริงในคอนเทนเนอร์ Devtools Lab (Ubuntu 24.04, Claude Code 2.1.266, codex-cli 0.153.4) ที่ติดตั้งและตั้งค่าตามผลของ LAB 001 แล้วนำ credential ของบัญชี `yolo1`, `yolo2`, `cyolo1` ของผู้สอนเข้าไปใช้ทดลอง ภาพหน้าจอปิดบังอีเมลและชื่อองค์กร หลักฐานดิบ (พรอมต์ บันทึก session ทั้ง 12 ครั้ง รายงาน และ SKILL.md ที่ AI สร้าง) อยู่ใน [evidence/](evidence/README.md) คอนเทนเนอร์ถูกลบหลังการทดลอง*
