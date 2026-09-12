# LAB 006 · ใช้ Skill จากทุกบัญชี และเปรียบเทียบกับการไม่มี Skill

LAB ที่ 3 ของชุด skill ต่อจาก [LAB 004 · Skill คืออะไร](../004_LAB_Skill_Basics/README.md) และ [LAB 005 · สร้าง Skill](../005_LAB_Create_Multi_Account_Skill/README.md)

## 1. วัตถุประสงค์

1. ใช้ skill `yolo` และ `cyolo` จากหน้าสนทนาและจาก shell ของทั้ง Claude Code และ Codex
2. ตรวจสอบจากบันทึก session ว่า AI เลือก skill เองและรันคำสั่งตามที่ skill กำหนด
3. เปรียบเทียบผลกับการทดลองก่อนมี skill ใน LAB 004 ด้วยประโยคสั่งงานเดียวกัน

## 2. ข้อกำหนดเบื้องต้น

| รายการ | ข้อกำหนด |
|---|---|
| LAB ที่ต้องผ่านก่อน | LAB 005 (มี `SKILL.md` ครบ 4 ไฟล์ใน `shared/skills` และ `skill-report.md` ผ่าน) |
| บัญชีที่ต้องล็อกอิน | `yolo1`, `yolo2`, `cyolo1` |
| โมเดล | ค่าเริ่มต้นของแต่ละ CLI: Claude Code = **Opus · high**, Codex = **gpt-6-astra · medium** ตรงกับค่าเริ่มต้นใน skill |
| เวลา | 15–20 นาที |

**ประโยคทดสอบ** ใช้ประโยคเดียวกับ LAB 004 ขั้นที่ 4.3 เฉลยของโจทย์คือ 900 บาท

ฝั่ง Claude Code (yolo2 คิด แล้ว cyolo1 ตรวจ):

```text
เรียก yolo2 ให้คิดว่าซื้อของ 1000 บาท ลด 10% ต้องจ่ายกี่บาท แล้วส่งทั้งโจทย์และคำตอบนั้นให้ cyolo1 ตรวจ นำผลกลับมาสรุปสั้น ๆ ในหน้านี้ ถ้าเรียกไม่ได้ให้บอกตามจริง
```

ฝั่ง Codex (yolo2 คิด แล้ว Codex ตรวจเอง):

```text
เรียก yolo2 ให้คิดว่าซื้อของ 1000 บาท ลด 10% ต้องจ่ายกี่บาท แล้วคุณตรวจคำตอบนั้นเอง นำผลกลับมาสรุปสั้น ๆ ในหน้านี้ ถ้าเรียกไม่ได้ให้บอกตามจริง
```

## 3. ขั้นตอนการทดลอง

### ขั้นที่ 1 · ใช้ skill ฝั่ง Claude Code

**1.1 หน้าสนทนา** เปิด `yolo1` พิมพ์ `/skills` เพื่อดูรายการ จะเห็น `cyolo` และ `yolo` ชนิด `user` สถานะ `on` กด Esc แล้ววางประโยคทดสอบฝั่ง Claude

![รายการ skill ในหน้า Claude Code: cyolo และ yolo](img/claude-skills-list.png)

![ประโยคทดสอบในหน้า Claude Code (Opus · high)](img/claude-prompt-typed.png)

![หลังมี skill: Claude โหลด skill yolo และ cyolo เอง เรียก yolo2 (opus · high) แล้วส่งให้ cyolo1 (gpt-6-astra · medium) ตรวจ](img/claude-skill-call-result.png)

ผลรันจริง (39 วินาที): Claude แสดง `Skill(yolo)` และ `Skill(cyolo)` ตรวจสถานะล็อกอิน แล้วรัน `yolo2 -p --model opus --effort high "…"` และ `cyolo1 exec --skip-git-repo-check -m gpt-6-astra -c model_reasoning_effort=medium -o … "…"` สรุปว่า yolo2 ตอบ 900 บาท และ cyolo1 ตรวจว่าถูกต้อง (บันทึก session: [evidence/08-skill-claude-tui-session.txt](evidence/08-skill-claude-tui-session.txt))

**1.2 shell** กด Ctrl+C สองครั้งเพื่อกลับมาที่ shell แล้วรัน

```bash
yolo1 --model opus --effort high -p 'เรียก yolo2 ให้คิดว่าซื้อของ 1000 บาท ลด 10% ต้องจ่ายกี่บาท แล้วส่งทั้งโจทย์และคำตอบนั้นให้ cyolo1 ตรวจ นำผลกลับมาสรุปสั้น ๆ ถ้าเรียกไม่ได้ให้บอกตามจริง'
```

![shell: yolo1 -p ใช้ skill เรียก yolo2 และ cyolo1](img/claude-shell-result.png)

ผลรันจริง: "เรียกได้ทั้งสองบัญชี" พร้อมตาราง yolo2 (opus / high) = 900 บาท และ cyolo1 (gpt-6-astra / medium) = ถูกต้อง

### ขั้นที่ 2 · ใช้ skill ฝั่ง Codex

**2.1 หน้าสนทนา** พิมพ์ `cyolo1` (หน้าจอแสดง `model: gpt-6-astra`) พิมพ์ `/skills` กด Enter เลือก **List skills** จะได้ช่องพิมพ์ที่ขึ้นต้นด้วย `$` พิมพ์ `yol` เพื่อกรอง เลือก `yolo` กด Enter จะได้ `$yolo` ในช่องพิมพ์ แล้ววางประโยคทดสอบฝั่ง Codex ต่อท้าย กด Enter (หากข้อความยังอยู่ ให้กด Enter อีกครั้ง)

![รายการ skill ใน Codex เมื่อพิมพ์ $yol: yolo และ cyolo](img/codex-skills-list.png)

![$yolo ตามด้วยประโยคทดสอบในหน้า Codex](img/codex-prompt-typed.png)

![หลังมี skill: Codex อ่าน SKILL.md ของ yolo แล้วเรียก yolo2 -p --model opus --effort high](img/codex-skill-call-result.png)

ผลรันจริง (21 วินาที): Codex อ่าน `SKILL.md` รัน `yolo2 auth status` และ `yolo2 -p --model opus --effort high '…'` สรุปว่าเรียก yolo2 สำเร็จ ได้ 900 บาท และตรวจแล้วถูกต้อง

**2.2 shell** กด Ctrl+C สองครั้ง คำสั่งนี้ไม่ใส่ `$yolo` เพื่อทดสอบว่า Codex เลือก skill เองจาก description

```bash
cyolo1 exec --skip-git-repo-check --model gpt-6-astra -c model_reasoning_effort=medium 'เรียก yolo2 ให้คิดว่าซื้อของ 1000 บาท ลด 10% ต้องจ่ายกี่บาท แล้วคุณตรวจคำตอบนั้นเอง สรุปสั้น ๆ ถ้าเรียกไม่ได้ให้บอกตามจริง'
```

![shell: codex exec เลือก skill yolo เองแล้วเรียก yolo2 (ปิดบังอีเมลและชื่อองค์กร)](img/codex-shell-result.png)

ผลรันจริง: Codex เริ่มด้วย "ผมจะใช้สกิล yolo …" รัน `cat …/skills/yolo/SKILL.md`, `yolo2 auth status`, `yolo2 -p --model opus --effort high '…'` และสรุปว่าได้ 900 บาท ถูกต้อง หมายเหตุ: โหมด `exec` พิมพ์ผลของทุกคำสั่งออกหน้าจอ รวมถึง JSON ของ `auth status` ที่มีอีเมลและชื่อองค์กร จึงต้องปิดบังก่อนเผยแพร่ภาพ

### ขั้นที่ 3 · บันทึกผลเทียบกับ LAB 004

เติมตารางเดียวกับ LAB 004 ขั้นที่ 4.4 อีกครั้ง แล้วเทียบสองตาราง

| ผู้เรียก | AI ทำอะไร | มีการรัน `yolo2` จริงหรือไม่ | ระบุ model/effort หรือไม่ | คำตอบ 900 มาจากใคร |
|---|---|---|---|---|
| `yolo1` | | | | |
| `cyolo1` | | | | |

## 4. ผลการทดลองเปรียบเทียบ

### 4.1 วิธีวัด

ใช้ประโยคทดสอบเดียวกันบนเครื่องเดียวกัน (คอนเทนเนอร์ที่ตั้งค่าตาม LAB 001) เงื่อนไขละ 6 ครั้ง ได้แก่ ฝั่ง Claude (`yolo1`, Opus · high) และฝั่ง Codex (`cyolo1`, Astra · medium) ฝั่งละ 3 ครั้ง (หน้าสนทนา 1 ครั้ง shell 2 ครั้ง) เกณฑ์ตัดสินอ่านจากบันทึก session ไม่ใช้ข้อความสรุปของ AI ([evidence/ab/](evidence/ab/), [evidence/13-session-durations.txt](evidence/13-session-durations.txt)) เงื่อนไข "ไม่มี skill" วัดก่อนทำ LAB 005 บนเครื่องเดียวกัน

### 4.2 ผลสรุป

| ตัวชี้วัด | ไม่มี skill (6 ครั้ง) | มี skill (6 ครั้ง) |
|---|---|---|
| เรียก `yolo2` ได้จริง (มีคำสั่ง `yolo2 -p` ในบันทึก) | 2/6 (Codex `exec` เท่านั้น) | 6/6 |
| ตรวจสถานะล็อกอินก่อนเรียก | 0/6 | 6/6 |
| ระบุ model/effort ตามที่กำหนด (opus · high) | 0/6 | 6/6 |
| ฝั่ง Claude ส่งต่อให้ `cyolo1` ตรวจ | 0/3 | 3/3 |
| คำตอบสุดท้าย 900 บาท | 6/6 (4 ครั้งเป็นการคำนวณเองของผู้เรียก) | 6/6 (มาจาก yolo2 ทุกครั้ง) |

### 4.3 รายละเอียดรายครั้ง

| เงื่อนไข | ผู้เรียก | วิธี | สิ่งที่ AI ทำ (จากบันทึก) | เรียก yolo2 | เวลา | โทเคน / ค่าใช้จ่าย |
|---|---|---|---|---|---|---|
| ไม่มี skill | Claude | หน้าสนทนา | `ListAgents`, `ls`, `SendMessage` → ไม่พบเอเจนต์ | ✗ | 26 s | – |
| ไม่มี skill | Claude | shell #1 | `ListAgents` แล้วตอบว่าเรียกไม่ได้ | ✗ | 16 s | $0.11 |
| ไม่มี skill | Claude | shell #2 | `ListAgents`, `SendMessage` ×2 → ไม่ถึง | ✗ | 21 s | $0.17 |
| ไม่มี skill | Codex | หน้าสนทนา | ค้นรายการเครื่องมือหา "yolo2" → ไม่พบ | ✗ | 16 s | 52k in / 198 out |
| ไม่มี skill | Codex | shell #1 | `command -v`, `file`, `head -n 100 /usr/local/bin/yolo2`, `yolo2 -p '…'` (ไม่ระบุ model/effort) | ✓ | 36 s | 104k in / 377 out |
| ไม่มี skill | Codex | shell #2 | `command -v`, `ls -l`, `head -n 100`, `yolo2 -p '…'` (ไม่ระบุ model/effort) | ✓ | 33 s | 103k in / 398 out |
| มี skill | Claude | หน้าสนทนา | `Skill(yolo)` → auth status → `yolo2 -p --model opus --effort high` → `Skill(cyolo)` → login status → `cyolo1 exec … -o` | ✓ (+cyolo1) | 39 s | – |
| มี skill | Claude | shell #1 | เหมือนหน้าสนทนา | ✓ (+cyolo1) | 45 s | $0.26 |
| มี skill | Claude | shell #2 | อ่าน SKILL.md ทั้งสอง → auth/login status → yolo2 → cyolo1 | ✓ (+cyolo1) | 46 s | $0.22 |
| มี skill | Codex | หน้าสนทนา `$yolo` | `cat …/yolo/SKILL.md`, `yolo2 auth status`, `yolo2 -p --model opus --effort high` | ✓ | 21 s | 72k in / 291 out |
| มี skill | Codex | shell #1 (ไม่ใส่ `$yolo`) | เหมือนหน้าสนทนา | ✓ | 26 s | 86k in / 305 out |
| มี skill | Codex | shell #2 (ไม่ใส่ `$yolo`) | เหมือนหน้าสนทนา | ✓ | 26 s | 86k in / 318 out |

ค่าใช้จ่ายของ Claude คือ list price ที่ CLI รายงาน (`total_cost_usd`) ไม่ใช่ยอดที่บัญชี subscription ถูกเรียกเก็บ โทเคนของ Codex ส่วนใหญ่เป็น cache (86k in มี 74k เป็น cached)

ภาพอ้างอิงของเงื่อนไข "ไม่มี skill" (จาก LAB 004):

![ก่อนมี skill: Claude ค้นหา session ชื่อ yolo2 ไม่พบ](img/noskill-claude-result.png)

![ก่อนมี skill: Codex ค้นรายการเครื่องมือหา yolo2 ไม่พบ](img/noskill-codex-result.png)

### 4.4 อภิปรายผล

- การไม่มี skill ไม่ได้ทำให้ล้มเหลวเสมอไป Codex เดาถูก 2 ใน 3 ครั้งจากการอ่านไฟล์ wrapper แต่เป็นการเดาที่ไม่ระบุโมเดล ไม่ตรวจล็อกอิน และอีกครั้งหนึ่งยอมแพ้ ผลจึงไม่แน่นอนและตรวจสอบย้อนหลังยาก
- Claude ที่ไม่มี skill ล้มเหลวทั้ง 3 ครั้งเพราะตีความ "เรียก yolo2" เป็นการส่งข้อความหา session อื่นซึ่งเป็นความสามารถที่มันรู้จัก ไม่ใช่คำสั่ง shell ของเครื่องนี้ที่มันไม่รู้จัก
- เมื่อมี skill เวลาต่อครั้งของฝั่ง Claude เพิ่มขึ้น (16–26 s เป็น 39–46 s) เพราะมีการเรียก AI อีก 2 ตัวจริง ส่วนฝั่ง Codex เร็วขึ้น (33–36 s เป็น 21–26 s) เพราะไม่ต้องสำรวจไฟล์ก่อน
- ค่าเริ่มต้นใน skill (opus · high, gpt-6-astra · medium) ถูกส่งไปกับทุกคำสั่งโดยผู้ใช้ไม่ต้องพิมพ์ การแก้ที่ `SKILL.md` ที่เดียวมีผลกับทุกบัญชี

## 5. สรุป

1. ประโยคสั่งงานเดียวกันให้ผลต่างกันอย่างชัดเจน: ไม่มี skill เรียกได้ 2/6 และไม่ตรวจล็อกอินเลย มี skill เรียกได้ 6/6 พร้อมตรวจล็อกอินและใช้โมเดลตามกำหนด
2. skill ทำงานได้ทั้งจากหน้าสนทนาและจาก shell (`-p` / `exec`) และ AI เลือก skill เองจาก `description` ได้แม้ไม่ระบุ `$yolo`
3. skill ที่ AI สร้างมีตารางสถานะล็อกอินเป็นภาพ ณ วันที่สร้าง จึงกำหนดกฎให้ตรวจสดก่อนใช้ทุกครั้ง ห้ามล็อกอินแทน และห้ามสลับบัญชีเอง
4. ข้อควรระวัง: Codex 0.153.4 อ่าน skill จาก `<CODEX_HOME>/skills` ได้จริงแม้ docs ปัจจุบันจะเน้น `.agents/skills` หากอัปเกรดแล้ว `/skills` ไม่แสดง `yolo` ให้ตรวจตำแหน่งใหม่ และทั้งสอง wrapper รันแบบข้ามการขออนุญาต จึงควรระบุขอบเขตงานในพรอมต์ให้ชัดเสมอ

*ภาพและตัวเลขทั้งหมดมาจากการรันจริงในคอนเทนเนอร์ Devtools Lab (Ubuntu 24.04, Claude Code 2.1.266, codex-cli 0.153.4) ที่ตั้งค่าตามผลของ LAB 001 โดยใช้ credential ของบัญชี `yolo1`, `yolo2`, `cyolo1` ของผู้สอน ภาพหน้าจอปิดบังอีเมลและชื่อองค์กร หลักฐานดิบ (บันทึก session ทั้ง 12 ครั้ง สคริปต์วัดผล ระยะเวลา) อยู่ใน [evidence/](evidence/README.md) คอนเทนเนอร์ถูกลบหลังการทดลอง*
