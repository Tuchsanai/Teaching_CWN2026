# LAB 005 · สร้าง Skill yolo และ cyolo ด้วย Claude Code

LAB ที่ 2 ของชุด skill ต่อจาก [LAB 004 · Skill คืออะไร](../004_LAB_Skill_Basics/README.md) และก่อน [LAB 006 · ใช้ Skill และเปรียบเทียบ](../006_LAB_Use_Skill_Compare/README.md)

## 1. วัตถุประสงค์

1. ใช้ Claude Code สร้าง skill `yolo` และ `cyolo` (`SKILL.md` อย่างละ 1 ไฟล์ต่อ CLI รวม 4 ไฟล์) ลงใน `shared/skills` ของ LAB 001 ด้วยพรอมต์เดียว
2. ตรวจสอบว่า skill ถูกวางถูกที่ ทุกบัญชีมองเห็น มีค่าเริ่มต้นตามที่กำหนด และผ่านการทดสอบเรียกจริงโดย AI
3. อ่านตัวอย่าง `SKILL.md` ที่ AI สร้างจริง เพื่อเข้าใจส่วนประกอบของ skill ที่ดี

## 2. ข้อกำหนดเบื้องต้น

| รายการ | ข้อกำหนด |
|---|---|
| LAB ที่ต้องผ่านก่อน | LAB 004 (โครงสร้าง `shared/skills` ถูกต้อง และ `yolo1`, `yolo2`, `cyolo1` ล็อกอินแล้ว) |
| โมเดลของผู้สร้าง | `yolo1` ค่าเริ่มต้นของ CLI คือ **Opus · high** ไม่ต้องเปลี่ยน |
| ค่าเริ่มต้นที่ skill ต้องใช้ | `yolo` = opus · high, `cyolo` = gpt-6-astra · medium (ระบุไว้ในพรอมต์) |
| เวลา | 15–20 นาที (AI ทำงานประมาณ 6 นาที) |
| ค่าใช้จ่าย | ระหว่างทำงาน AI จะเรียก `yolo1`, `yolo2`, `cyolo1` จริงหลายครั้งเพื่อทดสอบ |

## 3. หลักการของพรอมต์

พรอมต์ในขั้นที่ 4.1 กำหนดให้ AI (1) ตรวจของจริงบนเครื่องก่อน ห้ามเดา: wrapper, `--help`, สถานะล็อกอินทั้ง 10 บัญชี และ official docs ของทั้งสอง CLI (2) เขียน `SKILL.md` ที่มี frontmatter, ตารางบัญชี, คำสั่ง non-interactive ที่ทดสอบแล้ว, ค่าเริ่มต้น, กฎความปลอดภัย และวิธี relay (3) ทดสอบเรียกจริงทุกบัญชีที่ล็อกอินแล้ว และ (4) เขียนรายงาน PASS/FAIL/SKIP ห้ามล็อกอินแทนผู้ใช้และห้ามแตะไฟล์ credential

## 4. ขั้นตอนการทดลอง

### 4.1 วางพรอมต์

เปิด `yolo1` ตรวจว่าหน้าจอแสดง Opus 5 · high แล้วคัดลอกพรอมต์ทั้งกรอบไปวางในช่องสนทนา

**พรอมต์สำหรับคัดลอก (ทั้งกรอบ)**
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

![Claude Code ในคอนเทนเนอร์ทดสอบ: วางพรอมต์แล้ว ก่อนกด Enter](img/claude-paste-prompt.png)

ข้อความ `[Pasted text …]` แสดงว่าวางพรอมต์แล้ว กด Enter เพื่อเริ่ม รอจนขึ้นข้อความหยุดรอ

### 4.2 ผลที่คาดหวัง (ผลรันจริง Opus · high)

| รายการ | ผลรันจริง |
|---|---|
| ไฟล์ที่สร้าง | `.Claude/shared/skills/{yolo,cyolo}/SKILL.md` และ `.Codex/shared/skills/{yolo,cyolo}/SKILL.md` (md5 ตรงกันเป็นคู่) |
| ค่าเริ่มต้นใน skill | `yolo`: `yolo1` / `opus` / `high` · `cyolo`: `cyolo1` / `gpt-6-astra` / `medium` |
| ทั้งสอง CLI มองเห็น skill | PASS (Claude เห็นทันทีใน session เดิม, Codex ตอบว่ามีทั้ง `yolo` และ `cyolo`) |
| เรียก `yolo1`, `yolo2`, `cyolo1` ด้วยโจทย์ `12*12` | `144` ทั้งสาม → PASS |
| relay `yolo1` → `cyolo1` | PASS |
| `yolo3`–`yolo5`, `cyolo2`–`cyolo5` | SKIP (ยังไม่ล็อกอิน) |
| รายงาน `skill-report.md` | PASS 9 · SKIP 8 · FAIL 0 |
| เวลาและรอบ | 5 นาที 58 วินาที · 29 รอบ · list price ที่ CLI รายงาน $1.39 (บัญชี subscription ไม่ถูกเรียกเก็บตามตัวเลขนี้) |

เกณฑ์ผ่าน: มี SKILL.md ครบ 4 ไฟล์ใน `shared/skills`, ทั้งสอง CLI มองเห็น, บัญชีที่ล็อกอินแล้ว PASS บัญชีอื่น SKIP, และค่าเริ่มต้นตรงตามที่กำหนด ถ้อยคำ จำนวนรอบ เวลา และค่าใช้จ่ายต่างกันได้ รายงานฉบับจริงอยู่ที่ [evidence/06-skill-report.md](evidence/06-skill-report.md)

### 4.3 การตรวจสอบ (Terminal หน้าต่างใหม่)

```bash
find $HOME/ai-accounts -path '*/shared/skills/*' -name SKILL.md -not -path '*/.system/*'
diff $HOME/ai-accounts/.Claude/shared/skills/yolo/SKILL.md $HOME/ai-accounts/.Codex/shared/skills/yolo/SKILL.md && echo SAME
grep -n -A4 'ค่าเริ่มต้น' $HOME/ai-accounts/.Claude/shared/skills/yolo/SKILL.md
ls -la $HOME/ai-accounts/.Claude/yolo2/skills/ $HOME/ai-accounts/.Codex/cyolo2/skills/
```

- [ ] `find` ได้ 4 ไฟล์ และ `diff` พิมพ์ `SAME`
- [ ] ค่าเริ่มต้นใน `yolo/SKILL.md` เป็น `opus` + `high` และใน `cyolo/SKILL.md` เป็น `gpt-6-astra` + `medium`
- [ ] บัญชีที่ยังไม่ล็อกอินก็เห็นโฟลเดอร์ `yolo/` และ `cyolo/` ผ่าน symlink
- [ ] `skill-report.md` มีตาราง PASS/FAIL/SKIP และไม่มีอีเมล token หรือข้อมูลลับ

## 5. ตัวอย่าง SKILL.md ที่ AI สร้างจริง

ไฟล์ด้านล่างคือผลลัพธ์จริงของขั้นที่ 4.1 คัดลอกทั้งไฟล์โดยไม่ตัดต่อ ใช้เทียบเท่านั้น ไม่ต้องคัดลอกไปใช้ ของผู้เรียนต่างกันได้ในถ้อยคำ แต่ควรมีส่วนประกอบเดียวกัน: frontmatter → ตารางบัญชีและวิธีตรวจสถานะสด → คำสั่ง non-interactive ที่ทดสอบแล้ว → ค่าเริ่มต้น → กฎความปลอดภัย → ตัวอย่าง relay → รูปแบบรายงาน ต้นฉบับอยู่ที่ [evidence/generated-skills/](evidence/generated-skills/)

`$HOME/ai-accounts/.Claude/shared/skills/yolo/SKILL.md` (สำเนาใน `.Codex/shared/skills/yolo/` เหมือนกันทุกไบต์):

````markdown
---
name: yolo
description: เรียกใช้ Claude Code บัญชีอื่นบนเครื่องนี้ผ่านคำสั่ง yolo1..yolo5 แบบ non-interactive ใช้เมื่อผู้ใช้พูดว่า "เรียก yoloN", "ให้ Claude อีกบัญชีทำ...", "ให้บัญชี N ช่วยตรวจ/ช่วยคิด", "บัญชี Claude ไหนล็อกอินอยู่", หรือเมื่อต้องกระจายงานไปหลายบัญชี Claude แล้วรวมผลลัพธ์ ไม่ใช้เมื่องานนั้นทำเองในเซสชันปัจจุบันได้อยู่แล้ว
---

# yolo — เรียก Claude Code หลายบัญชี

`yolo1`..`yolo5` คือ Claude Code คนละบัญชี แต่ละคำสั่งตั้ง `CLAUDE_CONFIG_DIR` ไปยังโฟลเดอร์บัญชีของตัวเอง โดยไม่แตะ `$HOME`

ตัวแปรฐาน: `BASE_PATH="$HOME/ai-accounts"` (แก้ที่เดียว ที่อื่นอ้างอิงตัวแปรนี้)

## ตารางบัญชี

สถานะล็อกอินตรวจเมื่อ 2026-09-09 ด้วย `yoloN auth status`

| คำสั่ง | CLI | config root | สถานะล็อกอิน |
|---|---|---|---|
| `yolo1` | Claude Code 2.1.266 | `$BASE_PATH/.Claude/yolo1` | ล็อกอินแล้ว (claude.ai, แผน max) |
| `yolo2` | Claude Code 2.1.266 | `$BASE_PATH/.Claude/yolo2` | ล็อกอินแล้ว (claude.ai, แผน team) |
| `yolo3` | Claude Code 2.1.266 | `$BASE_PATH/.Claude/yolo3` | ยังไม่ล็อกอิน |
| `yolo4` | Claude Code 2.1.266 | `$BASE_PATH/.Claude/yolo4` | ยังไม่ล็อกอิน |
| `yolo5` | Claude Code 2.1.266 | `$BASE_PATH/.Claude/yolo5` | ยังไม่ล็อกอิน |

ตารางนี้เป็นภาพ ณ เวลาที่เขียน ก่อนใช้บัญชีให้ตรวจสถานะจริงก่อนเสมอ:

```bash
for n in 1 2 3 4 5; do echo "== yolo$n =="; yolo$n auth status < /dev/null; done
```

`auth status` คืน JSON ที่มีฟิลด์ `loggedIn` — ใช้ฟิลด์นี้ตัดสิน ไม่ต้องเปิดไฟล์ใด ๆ ในโฟลเดอร์บัญชี

## วิธีเรียกแบบไม่เปิดหน้าจอ (non-interactive)

```bash
yoloN -p --model <model> --effort <effort> "<prompt>" < /dev/null
```

- `-p` / `--print` = พิมพ์คำตอบแล้วออก ไม่เปิด TUI
- `--model` รับ alias (`opus`, `sonnet`, `fable`) หรือชื่อเต็ม (`claude-opus-5`)
- `--effort` รับ `low`, `medium`, `high`, `xhigh`, `max`
- `< /dev/null` ปิด stdin กัน process ค้างรอ input
- คำตอบออกทาง stdout ล้วน เก็บลงตัวแปรได้ด้วย `$(...)` หรือ redirect ลงไฟล์

ตัวอย่างที่ทดสอบแล้วบนเครื่องนี้:

```bash
yolo1 -p --model opus --effort high "ตอบเป็นตัวเลขล้วนอย่างเดียว: 12*12" < /dev/null
# -> 144
```

## ค่าเริ่มต้นเมื่อผู้ใช้ไม่ระบุ

| สิ่งที่ไม่ระบุ | ค่าเริ่มต้น |
|---|---|
| บัญชี | `yolo1` |
| model | `opus` |
| effort | `high` |

ผู้ใช้ระบุเองได้เสมอ และค่าที่ผู้ใช้ระบุมาก่อนค่าเริ่มต้นทุกกรณี

## กฎความปลอดภัย

- บัญชีที่ผู้ใช้ระบุ **ยังไม่ล็อกอิน** → หยุด แล้วแจ้งผู้ใช้ว่าบัญชีนั้นยังไม่ล็อกอิน พร้อมบอกว่ามีบัญชีไหนพร้อมใช้บ้าง
- **ห้ามสลับไปบัญชีอื่นเอง** เมื่อบัญชีที่ผู้ใช้ขอใช้ไม่ได้ — ให้ผู้ใช้เลือก
- **ห้ามล็อกอินแทนผู้ใช้** ห้ามรัน `yoloN auth login` / `claude auth login` เอง หากผู้ใช้ต้องการล็อกอิน ให้บอกให้ผู้ใช้รัน `yoloN auth login` ในเทอร์มินัลของตัวเอง
- **ห้ามอ่าน คัดลอก แสดง หรือส่งต่อไฟล์ credential** ใด ๆ ใน `$BASE_PATH/.Claude/<บัญชี>/` (เช่น `.credentials.json`, token, cookie) และห้ามใส่เนื้อหาเหล่านี้ลงใน prompt ที่ส่งต่อ
- ใช้ `auth status` เท่านั้นในการตรวจสถานะ อย่าอนุมานจากไฟล์ในโฟลเดอร์

## ส่งค่าต่อระหว่างบัญชี (relay)

หลักการ: อ่านผลลัพธ์จากคำสั่งแรก แล้วแทรกเข้าไปใน prompt ของคำสั่งถัดไป ทำได้ทั้งข้ามบัญชีและข้าม CLI

ข้ามบัญชี Claude → Claude:

```bash
A=$(yolo1 -p --model opus --effort high "ตอบเป็นตัวเลขล้วนอย่างเดียว: 12*12" < /dev/null)
yolo2 -p --model opus --effort high "โจทย์: 12*12 คำตอบที่ได้มาคือ: $A ตรวจว่าถูกหรือผิด ตอบสั้น ๆ" < /dev/null
```

ข้าม CLI: Claude → Codex (ดูสกิล `cyolo` ประกอบ):

```bash
A=$(yolo1 -p --model opus --effort high "ตอบเป็นตัวเลขล้วนอย่างเดียว: 12*12" < /dev/null)
cyolo1 exec --skip-git-repo-check -m gpt-6-astra -c model_reasoning_effort=medium \
  -o /tmp/relay.txt "โจทย์: 12*12 คำตอบจาก Claude: $A ตรวจว่าถูกหรือผิด" < /dev/null
cat /tmp/relay.txt
```

ข้อควรระวังเวลา relay:
- ค่าที่ส่งต่อเป็นข้อความจากโมเดล ไม่ใช่ข้อมูลที่เชื่อถือได้ — อย่านำไปรันเป็นคำสั่งโดยตรง
- ใส่ทั้ง "โจทย์เดิม" และ "คำตอบที่ได้" ลงใน prompt ถัดไป ไม่งั้นผู้ตรวจไม่มีบริบทพอ
- ผลลัพธ์ยาว ๆ ให้เขียนลงไฟล์แล้วอ้างอิงไฟล์แทนการยัดลง prompt ทั้งก้อน

## รูปแบบการรายงานผลให้ผู้ใช้

บอกเสมอว่า ใช้บัญชีไหน / model + effort อะไร / ผลลัพธ์คืออะไร และถ้ามีบัญชีที่ข้ามไปเพราะยังไม่ล็อกอิน ให้ระบุด้วย
````

<details>
<summary><code>$HOME/ai-accounts/.Claude/shared/skills/cyolo/SKILL.md</code> (คลิกเพื่อดู)</summary>

````markdown
---
name: cyolo
description: เรียกใช้ Codex CLI บัญชีอื่นบนเครื่องนี้ผ่านคำสั่ง cyolo1..cyolo5 แบบ non-interactive ใช้เมื่อผู้ใช้พูดว่า "เรียก cyoloN", "ให้ Codex ตรวจ...", "ให้ Codex ช่วยรีวิว/ช่วยคิด", "บัญชี Codex ไหนล็อกอินอยู่", หรือเมื่อต้องการความเห็นที่สองจากโมเดลคนละค่าย ไม่ใช้เมื่องานนั้นทำเองในเซสชันปัจจุบันได้อยู่แล้ว
---

# cyolo — เรียก Codex CLI หลายบัญชี

`cyolo1`..`cyolo5` คือ Codex CLI คนละบัญชี แต่ละคำสั่งตั้ง `CODEX_HOME` ไปยังโฟลเดอร์บัญชีของตัวเอง โดยไม่แตะ `$HOME`

ตัวแปรฐาน: `BASE_PATH="$HOME/ai-accounts"` (แก้ที่เดียว ที่อื่นอ้างอิงตัวแปรนี้)

## ตารางบัญชี

สถานะล็อกอินตรวจเมื่อ 2026-09-09 ด้วย `cyoloN login status`

| คำสั่ง | CLI | config root | สถานะล็อกอิน |
|---|---|---|---|
| `cyolo1` | Codex CLI 0.153.4 | `$BASE_PATH/.Codex/cyolo1` | ล็อกอินแล้ว (ChatGPT) |
| `cyolo2` | Codex CLI 0.153.4 | `$BASE_PATH/.Codex/cyolo2` | ยังไม่ล็อกอิน |
| `cyolo3` | Codex CLI 0.153.4 | `$BASE_PATH/.Codex/cyolo3` | ยังไม่ล็อกอิน |
| `cyolo4` | Codex CLI 0.153.4 | `$BASE_PATH/.Codex/cyolo4` | ยังไม่ล็อกอิน |
| `cyolo5` | Codex CLI 0.153.4 | `$BASE_PATH/.Codex/cyolo5` | ยังไม่ล็อกอิน |

ตารางนี้เป็นภาพ ณ เวลาที่เขียน ก่อนใช้บัญชีให้ตรวจสถานะจริงก่อนเสมอ:

```bash
for n in 1 2 3 4 5; do echo "== cyolo$n =="; cyolo$n login status < /dev/null; done
```

`login status` พิมพ์ `Logged in using ChatGPT` เมื่อพร้อมใช้ และ `Not logged in` เมื่อยังไม่ล็อกอิน — ใช้ข้อความนี้ตัดสิน ไม่ต้องเปิดไฟล์ใด ๆ ในโฟลเดอร์บัญชี

## วิธีเรียกแบบไม่เปิดหน้าจอ (non-interactive)

```bash
cyoloN exec --skip-git-repo-check -m <model> -c model_reasoning_effort=<effort> -o <ไฟล์ผลลัพธ์> "<prompt>" < /dev/null
```

- `exec` = โหมดรันครั้งเดียวไม่เปิด TUI
- `--skip-git-repo-check` จำเป็นเมื่อ working directory ไม่ใช่ git repo
- `-m` / `--model` เลือกโมเดล
- `-c model_reasoning_effort=<effort>` ตั้งระดับ reasoning (`low`, `medium`, `high`)
- `-o` / `--output-last-message <FILE>` เขียนเฉพาะข้อความสุดท้ายลงไฟล์ — ใช้ไฟล์นี้อ่านคำตอบ เพราะ stdout ยังมี log ของ session ปนอยู่
- `< /dev/null` ปิด stdin เพราะ `codex exec` จะอ่าน prompt จาก stdin ถ้า stdin ถูก pipe เข้ามา

ตัวอย่างที่ทดสอบแล้วบนเครื่องนี้:

```bash
cyolo1 exec --skip-git-repo-check -m gpt-6-astra -c model_reasoning_effort=medium \
  -o /tmp/out.txt "ตอบเป็นตัวเลขล้วนอย่างเดียว: 12*12" < /dev/null
cat /tmp/out.txt   # -> 144
```

## ค่าเริ่มต้นเมื่อผู้ใช้ไม่ระบุ

| สิ่งที่ไม่ระบุ | ค่าเริ่มต้น |
|---|---|
| บัญชี | `cyolo1` |
| model | `gpt-6-astra` |
| effort | `medium` |

ผู้ใช้ระบุเองได้เสมอ และค่าที่ผู้ใช้ระบุมาก่อนค่าเริ่มต้นทุกกรณี

## กฎความปลอดภัย

- บัญชีที่ผู้ใช้ระบุ **ยังไม่ล็อกอิน** → หยุด แล้วแจ้งผู้ใช้ว่าบัญชีนั้นยังไม่ล็อกอิน พร้อมบอกว่ามีบัญชีไหนพร้อมใช้บ้าง
- **ห้ามสลับไปบัญชีอื่นเอง** เมื่อบัญชีที่ผู้ใช้ขอใช้ไม่ได้ — ให้ผู้ใช้เลือก
- **ห้ามล็อกอินแทนผู้ใช้** ห้ามรัน `cyoloN login` / `codex login` เอง หากผู้ใช้ต้องการล็อกอิน ให้บอกให้ผู้ใช้รัน `cyoloN login` ในเทอร์มินัลของตัวเอง
- **ห้ามอ่าน คัดลอก แสดง หรือส่งต่อไฟล์ credential** ใด ๆ ใน `$BASE_PATH/.Codex/<บัญชี>/` (เช่น `auth.json`, token) และห้ามใส่เนื้อหาเหล่านี้ลงใน prompt ที่ส่งต่อ
- ใช้ `login status` เท่านั้นในการตรวจสถานะ อย่าอนุมานจากไฟล์ในโฟลเดอร์
- `cyoloN` รันด้วย `--dangerously-bypass-approvals-and-sandbox` — Codex จะรันคำสั่งได้โดยไม่ถาม ให้ส่ง prompt ที่ขอบเขตชัดเจน และอย่าส่งงานที่แก้ไฟล์นอกขอบเขตที่ผู้ใช้ขอ

## ส่งค่าต่อระหว่างบัญชี (relay)

หลักการ: อ่านผลลัพธ์จากคำสั่งแรก แล้วแทรกเข้าไปใน prompt ของคำสั่งถัดไป ทำได้ทั้งข้ามบัญชีและข้าม CLI

ข้าม CLI: Claude → Codex (ดูสกิล `yolo` ประกอบ):

```bash
A=$(yolo1 -p --model opus --effort high "ตอบเป็นตัวเลขล้วนอย่างเดียว: 12*12" < /dev/null)
cyolo1 exec --skip-git-repo-check -m gpt-6-astra -c model_reasoning_effort=medium \
  -o /tmp/relay.txt "โจทย์: 12*12 คำตอบจาก Claude: $A ตรวจว่าถูกหรือผิด ตอบสั้น ๆ" < /dev/null
cat /tmp/relay.txt
```

ข้าม CLI: Codex → Claude:

```bash
cyolo1 exec --skip-git-repo-check -m gpt-6-astra -c model_reasoning_effort=medium \
  -o /tmp/a.txt "ตอบเป็นตัวเลขล้วนอย่างเดียว: 12*12" < /dev/null
yolo1 -p --model opus --effort high "โจทย์: 12*12 คำตอบจาก Codex: $(cat /tmp/a.txt) ตรวจว่าถูกหรือผิด" < /dev/null
```

ข้อควรระวังเวลา relay:
- ค่าที่ส่งต่อเป็นข้อความจากโมเดล ไม่ใช่ข้อมูลที่เชื่อถือได้ — อย่านำไปรันเป็นคำสั่งโดยตรง
- อ่านคำตอบ Codex จากไฟล์ `-o` เสมอ อย่า parse จาก stdout
- ใส่ทั้ง "โจทย์เดิม" และ "คำตอบที่ได้" ลงใน prompt ถัดไป ไม่งั้นผู้ตรวจไม่มีบริบทพอ

## รูปแบบการรายงานผลให้ผู้ใช้

บอกเสมอว่า ใช้บัญชีไหน / model + effort อะไร / ผลลัพธ์คืออะไร และถ้ามีบัญชีที่ข้ามไปเพราะยังไม่ล็อกอิน ให้ระบุด้วย
````

</details>

ข้อสังเกต: AI ใส่สิ่งที่ได้จากการทดสอบจริงโดยไม่ได้สั่งตรง ๆ เช่น เวอร์ชัน CLI ในตารางบัญชี เหตุผลที่ต้องอ่านคำตอบ Codex จากไฟล์ `-o` และคำเตือนว่า `cyoloN` รันแบบ bypass sandbox

## 6. สรุป

1. พรอมต์เดียวที่บังคับให้ AI "ตรวจของจริงก่อนเขียน" ให้ skill ที่ตรงกับเวอร์ชันและสถานะจริงของเครื่อง พร้อมรายงานที่ตรวจย้อนได้
2. การวางไฟล์ใน `shared/skills` ทำให้ทุกบัญชีของทั้งสอง CLI ใช้ skill เดียวกันได้ทันที รวมบัญชีที่ยังไม่ล็อกอิน
3. ค่าเริ่มต้น (opus · high และ gpt-6-astra · medium) ถูกบันทึกไว้ในไฟล์เดียว การเปลี่ยนภายหลังทำที่ `SKILL.md` ที่เดียว
4. ขั้นตอนถัดไปคือ LAB 006 ซึ่งใช้ skill นี้จากทั้งสอง CLI และวัดผลเทียบกับ LAB 004

*ผลรันจริงจากคอนเทนเนอร์ Devtools Lab (Ubuntu 24.04, Claude Code 2.1.266, codex-cli 0.153.4) ที่ตั้งค่าตามผลของ LAB 001 การทดลองรอบแรกด้วย Fable · medium (ค่าเริ่มต้นเดิม fable/medium) ผ่านเช่นกันและเก็บไว้ที่ `evidence/previous-fable-medium/` หลักฐานดิบทั้งหมดอยู่ใน [evidence/](evidence/README.md)*
