# สเปกการออกแบบชุดบทเรียน Skill_LAB (ผู้สอน)

วันที่ออกแบบ: 2026-09-10 · ผู้ออกแบบ: Claude Fable 5.1 (yolo2) · ผู้ทดลอง: คอนเทนเนอร์ Devtools Lab (`tuchsanai/devtools:2569_1`)

## เป้าหมายของชุด

ให้ผู้เรียนที่ผ่าน LAB 001–004 แล้ว เข้าใจ **skill** ของ Claude Code และ Codex CLI ทั้งทฤษฎีและปฏิบัติ
โดยเรียงจากง่ายไปยาก: เขียน SKILL.md ด้วยมือหนึ่งไฟล์ → ควบคุมการเลือกใช้ → รับอาร์กิวเมนต์ → ดึงข้อมูลสดและสคริปต์ →
แยกไฟล์อ้างอิง (progressive disclosure) → รันในบริบทแยก/เปลี่ยนโมเดล → สร้าง skill ที่ประสานหลายบัญชีและวัดผลแบบ A/B

ทุก LAB ใช้ **โจทย์ธุรกิจเดียวกัน** ที่ผู้เรียนคุ้นจาก LAB 001: ร้านค้าลด 10% เมื่อซื้อครบ 1000 บาท
เพื่อให้เห็นว่า skill เปลี่ยนพฤติกรรม AI อย่างไรโดยไม่ต้องเรียนโจทย์ใหม่

## กติกาการผลิตบทเรียน (evidence-only)

1. ตัวเลข ข้อความผิดพลาด และผลลัพธ์ทุกอย่างใน README ต้องมาจากการรันจริงในคอนเทนเนอร์ และเก็บไฟล์ดิบไว้ใน `evidence/` ของ LAB นั้น
2. สิ่งที่ยังไม่ได้ทดลองต้องติดป้าย **แนวทาง — ยังไม่ได้ทดลอง**
3. ห้ามมีอีเมล ชื่อองค์กร token หรือ credential ในไฟล์ใด ๆ (`<email>`, `<ORG>`)
4. รูปแบบ README ตาม LAB 004: วัตถุประสงค์ → ข้อกำหนดเบื้องต้น → ความรู้พื้นฐาน → ขั้นตอน (พรอมต์/คำสั่งคัดลอกทั้งกรอบ + ผลรันจริง + จุดที่ต้องตรวจ) → ผลเปรียบเทียบ → สรุป → หมายเหตุวิธีการทดลอง
5. เวอร์ชันที่ทดลอง: Claude Code ตามที่ `install.sh` ให้ ณ วันทดลอง และ codex-cli จาก npm ณ วันทดลอง (บันทึกใน `evidence/02-versions.txt` ของแต่ละ LAB)

## โครงสร้างโฟลเดอร์

```
Week1/
├── Skill_LAB_000_Theory/            ทฤษฎีทั้งหมด + แผนที่ชุดบทเรียน + สเปกนี้
├── Skill_LAB_001_Hello_Skill/       ★     เขียน SKILL.md ไฟล์เดียวด้วยมือ วางใน shared/skills ให้ทั้งสอง CLI เห็น
├── Skill_LAB_002_Trigger_Control/   ★★    description คือสวิตช์: วัดอัตราการถูกเลือก + ปิด/เปิดการเรียกอัตโนมัติ
├── Skill_LAB_003_Arguments/         ★★    $ARGUMENTS, $0/$1, arguments:, argument-hint และวิธีทำอย่างเดียวกันใน Codex
├── Skill_LAB_004_Live_Context/      ★★★   !`คำสั่ง` ดึงข้อมูลสด, scripts/ + ${CLAUDE_SKILL_DIR}, allowed-tools, กรณีสคริปต์ล้มเหลว
├── Skill_LAB_005_Reference_Files/   ★★★   progressive disclosure: SKILL.md เป็นตัวชี้ทาง + references/ โหลดเฉพาะที่ใช้ วัดด้วย /skill-doctor
├── Skill_LAB_006_Fork_and_Model/    ★★★★  context: fork, agent, model, effort, background — วัดต้นทุนและเวลาจริง
└── Skill_LAB_007_Second_Opinion/    ★★★★★ skill ที่เรียก yolo2 + cyolo1 ขนานกันแล้วเทียบคำตอบ; ให้ AI สร้างเทียบกับเขียนเอง; วัดผล A/B
```

แต่ละ LAB มี `README.md`, `evidence/` (ผลรันดิบ + สคริปต์), `img/` (ภาพ ttyd ผ่าน Playwright เฉพาะจุดสำคัญ) และ `skills/` (ไฟล์ skill ฉบับสมบูรณ์ที่ใช้ในการทดลอง คัดลอกไปวางได้)

## เนื้อหาต่อ LAB (สรุปสำหรับผู้ทดลอง)

| LAB | skill ที่สร้าง | สิ่งที่ต้องวัดจริง | หลักฐานที่ต้องเก็บ |
|---|---|---|---|
| 001 | `discount` (กฎลด 10% เมื่อครบ 1000) | ทั้งสอง CLI มองเห็น; เรียกด้วยมือ `/discount`, `$discount`; เรียกอัตโนมัติจากประโยคธรรมดา; ก่อน/หลังมี skill คำตอบต่างกัน; frontmatter ที่ `---` ไม่อยู่บรรทัดแรก | session log ที่เห็น `Skill(discount)` / `cat .../discount/SKILL.md`, ผล `/skills`, ภาพ TUI |
| 002 | `discount` 3 ฉบับ description (แย่ / ดี / ดี+when_to_use), `disable-model-invocation`, `user-invocable`, `allow_implicit_invocation` (Codex) | อัตราการถูกเลือกต่อประโยคทดสอบ (ตรง 3 ประโยค / ไม่ตรง 2 ประโยค × 2 รอบ × 2 CLI); `/skill-doctor` | ตาราง trigger, JSON/JSONL ทุกครั้ง, ผล skill-doctor |
| 003 | `discount` รับ `/discount 1500 10` | `$ARGUMENTS` ต่อท้ายอัตโนมัติ, `$0 $1`, `arguments: [amount, rate]`, อาร์กิวเมนต์ที่ขาด; Codex `$discount 1500 10` | ผล `-p "/discount …"` และ rollout ของ Codex |
| 004 | `accounts` (ตารางสถานะบัญชีสด) + `scripts/status.sh` | Claude: ข้อมูลอยู่ในบริบทก่อนคิด (0 tool call) vs Codex รันสคริปต์ 1 ครั้ง; คำสั่ง exit ≠ 0 ทำให้ skill ล้ม → `\|\| true`; `allowed-tools`; `disableSkillShellExecution` | ข้อความ error จริง, จำนวน tool call จาก log |
| 005 | `shop-rules` + `references/{pricing,shipping,returns}.md` | ถามเรื่องส่งของ → อ่านเฉพาะ `shipping.md`; ขนาดบริบท (`/skill-doctor`, โทเคน cache_read) เทียบไฟล์เดียวใหญ่ vs แยกไฟล์ | log การ Read, ตัวเลขโทเคนจาก JSON |
| 006 | `cheap-check` (`context: fork`, `agent: Explore`, `model: haiku`, `effort: low`, `background: false`) | `modelUsage` มี key haiku; `total_cost_usd`/เวลา เทียบ skill เดียวกันที่ไม่ fork; subagent ไม่เห็นประวัติสนทนา | JSON ของ `-p`, session log ของ subagent |
| 007 | `second-opinion` (fan-out yolo2 + cyolo1 → ตารางเทียบ) ฉบับเขียนเอง vs ฉบับที่ `$skill-creator`/Claude สร้าง | 3 รอบต่อ CLI ต่อฉบับ: เรียกครบ 2 บัญชีหรือไม่, ตรวจล็อกอินก่อน, ระบุ model/effort, เวลา, ต้นทุน; `quick_validate.py` ผ่าน | ตาราง A/B, สคริปต์ driver, skill ทั้งสองฉบับ |

## สภาพแวดล้อมทดลอง

- คอนเทนเนอร์ `devtools-skilllab-<hash>` port 2280→22, 7681→7681 (ttyd สำหรับถ่ายภาพ)
- ติดตั้งด้วย `container-setup/00-bootstrap.sh` และวางโครงสร้าง LAB 001 ด้วย `01-lab001-result.sh` (คัดลอกจาก LAB 004)
- ยืมเฉพาะไฟล์ credential ของ `yolo1`, `yolo2`, `cyolo1` จากเครื่องผู้สอน ไม่ล็อกอินใหม่ บัญชีอื่น SKIP
- ผู้เรียก: Claude = Opus · high (ค่าเริ่มต้นของ CLI), Codex = gpt-6-astra · medium เว้นแต่ LAB ระบุ
- ลบคอนเทนเนอร์หลังจบทุกการทดลอง
