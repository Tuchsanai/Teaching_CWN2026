# skill-report.md — LAB 004: สกิล yolo / cyolo สำหรับหลายบัญชี

วันที่ตรวจ: 2026-09-09
ตัวแปรตั้งค่า: `BASE_PATH="$HOME/ai-accounts"` (= `/root/ai-accounts`)
เวอร์ชัน: Claude Code 2.1.266, codex-cli 0.153.4

## ตำแหน่งไฟล์ SKILL.md (4 ไฟล์)

| # | ไฟล์ | มองเห็นผ่าน |
|---|---|---|
| 1 | $BASE_PATH/.Claude/shared/skills/yolo/SKILL.md | $BASE_PATH/.Claude/yolo1..5/skills/yolo/SKILL.md (symlink) |
| 2 | $BASE_PATH/.Claude/shared/skills/cyolo/SKILL.md | $BASE_PATH/.Claude/yolo1..5/skills/cyolo/SKILL.md (symlink) |
| 3 | $BASE_PATH/.Codex/shared/skills/yolo/SKILL.md | $BASE_PATH/.Codex/cyolo1..5/skills/yolo/SKILL.md (symlink) |
| 4 | $BASE_PATH/.Codex/shared/skills/cyolo/SKILL.md | $BASE_PATH/.Codex/cyolo1..5/skills/cyolo/SKILL.md (symlink) |

เนื้อหาไฟล์ 1 = 3 และ 2 = 4 (ตรวจด้วย `diff` ได้ IDENTICAL)

## สถานะล็อกอินที่ตรวจได้ (ตรวจด้วย `yoloN auth status` / `cyoloN login status`)

| คำสั่ง | CLI | config root | สถานะ |
|---|---|---|---|
| yolo1 | Claude Code | $BASE_PATH/.Claude/yolo1 | ล็อกอินแล้ว |
| yolo2 | Claude Code | $BASE_PATH/.Claude/yolo2 | ล็อกอินแล้ว |
| yolo3 | Claude Code | $BASE_PATH/.Claude/yolo3 | ยังไม่ล็อกอิน |
| yolo4 | Claude Code | $BASE_PATH/.Claude/yolo4 | ยังไม่ล็อกอิน |
| yolo5 | Claude Code | $BASE_PATH/.Claude/yolo5 | ยังไม่ล็อกอิน |
| cyolo1 | Codex CLI | $BASE_PATH/.Codex/cyolo1 | ล็อกอินแล้ว |
| cyolo2 | Codex CLI | $BASE_PATH/.Codex/cyolo2 | ยังไม่ล็อกอิน |
| cyolo3 | Codex CLI | $BASE_PATH/.Codex/cyolo3 | ยังไม่ล็อกอิน |
| cyolo4 | Codex CLI | $BASE_PATH/.Codex/cyolo4 | ยังไม่ล็อกอิน |
| cyolo5 | Codex CLI | $BASE_PATH/.Codex/cyolo5 | ยังไม่ล็อกอิน |

## ผลทดสอบ

| รายการ | หลักฐาน | ผล | เหตุผล |
|---|---|---|---|
| SKILL.md ครบ 4 ไฟล์ | `ls` ผ่าน symlink `<account>/skills/<name>/SKILL.md` ครบ 20 path (10 บัญชี × 2 สกิล) | PASS | ไฟล์อยู่ใน shared/skills และทุกบัญชี symlink มาที่เดียวกัน |
| Claude Code โหลดสกิลจริง | `yolo1 -p` ถามรายชื่อสกิล ได้ `yolo, cyolo` | PASS | ยืนยันว่า CLAUDE_CONFIG_DIR/skills ถูกสแกนในเวอร์ชัน 2.1.266 |
| Codex CLI โหลดสกิลจริง | `cyolo1 exec` ถามรายชื่อสกิล ได้ `yolo, cyolo` | PASS | ยืนยันว่า CODEX_HOME/skills ถูกสแกนในเวอร์ชัน 0.153.4 |
| yolo1: `-p --model fable --effort medium "ตอบเป็นตัวเลขล้วนอย่างเดียว: 12*12"` | stdout = `144`, exit 0 | PASS | |
| yolo2: คำสั่งเดียวกัน | stdout = `144`, exit 0 | PASS | |
| yolo3 | `auth status` → loggedIn=false | SKIP | ยังไม่ล็อกอิน (ห้ามล็อกอินแทน) |
| yolo4 | `auth status` → loggedIn=false | SKIP | ยังไม่ล็อกอิน |
| yolo5 | `auth status` → loggedIn=false | SKIP | ยังไม่ล็อกอิน |
| cyolo1: `exec --skip-git-repo-check -m gpt-6-astra -c model_reasoning_effort=medium -o /tmp/cyolo1-test.txt "..."` | ไฟล์ -o = `144`, exit 0, header แสดง model gpt-6-astra / reasoning effort medium | PASS | |
| cyolo2 | `login status` → Not logged in | SKIP | ยังไม่ล็อกอิน |
| cyolo3 | `login status` → Not logged in | SKIP | ยังไม่ล็อกอิน |
| cyolo4 | `login status` → Not logged in | SKIP | ยังไม่ล็อกอิน |
| cyolo5 | `login status` → Not logged in | SKIP | ยังไม่ล็อกอิน |
| Relay yolo1 → cyolo1 | yolo1 ตอบ `144` → ใส่โจทย์+คำตอบใน prompt ของ cyolo1 → ไฟล์ -o = `CORRECT` | PASS | ส่งค่าข้าม CLI ได้จริง |

## การตรวจ docs / flag ก่อนเขียน

- Claude Code docs (code.claude.com/docs/en/skills): frontmatter `name`, `description` (description ใช้ตัดสินว่าจะเรียกสกิลเมื่อไร)
- Codex docs (developers.openai.com/codex/skills → redirect ไป learn.chatgpt.com/docs/build-skills): frontmatter ขั้นต่ำ `name`, `description`
- `claude --help`: `-p, --print`, `--model <model>` (alias fable/opus/sonnet), `--effort <low|medium|high|xhigh|max>`
- `codex exec --help`: `-m, --model`, `-c, --config <key=value>`, `-o, --output-last-message <FILE>`, `--skip-git-repo-check`
- ใช้ frontmatter เฉพาะ `name` + `description` เพื่อให้ไฟล์เดียวกันใช้ได้ทั้ง 2 CLI

## ข้อจำกัดที่พบ

1. บัญชี yolo3-5 และ cyolo2-5 ยังไม่ล็อกอิน จึงทดสอบเรียกจริงไม่ได้ (SKIP) และตามกฎไม่ล็อกอินแทน
2. ตารางสถานะในสกิลเป็น snapshot ณ วันที่ตรวจ สกิลจึงสั่งให้ตรวจสดด้วย `auth status` / `login status` ก่อนใช้ทุกครั้ง
3. Codex docs ทางการระบุตำแหน่งสกิลเป็น `$HOME/.agents/skills` และ `.agents/skills` เป็นหลัก แต่จากการทดสอบจริง codex-cli 0.153.4 สแกน `$CODEX_HOME/skills` ด้วย (มีโฟลเดอร์ `.system` ที่ codex สร้างเองอยู่ในนั้น) — หากอัปเกรดเวอร์ชันควรทดสอบซ้ำ
4. `codex exec` พิมพ์ log (model, session id, tokens) ปนใน stdout จึงต้องอ่านคำตอบจากไฟล์ `-o` เท่านั้น
5. wrapper ทั้งสองรันในโหมด bypass permissions/sandbox อยู่แล้ว prompt ที่ส่งไปจึงมีสิทธิ์แก้ไฟล์ได้ ควรระบุขอบเขตใน prompt ให้ชัด
6. ไม่ได้อ่านหรือแสดงไฟล์ credential ใด ๆ ใช้เฉพาะคำสั่งตรวจสถานะของแต่ละ CLI
