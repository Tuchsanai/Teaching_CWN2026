# Skill Report — yolo / cyolo multi-account skills

วันที่ทดสอบ: 2026-09-09
เครื่อง: Linux WSL2 / working dir `/root/lab004`
ตัวแปรฐาน: `BASE_PATH="$HOME/ai-accounts"` → `/root/ai-accounts`
เวอร์ชันที่ติดตั้ง: Claude Code `2.1.266` · Codex CLI `codex-cli 0.153.4`

## 1. ตำแหน่งไฟล์ SKILL.md ทั้ง 4 ไฟล์

| # | ไฟล์ | md5 |
|---|---|---|
| 1 | `$BASE_PATH/.Claude/shared/skills/yolo/SKILL.md` | `fd9f790db04204b9d712799e9beeed17` |
| 2 | `$BASE_PATH/.Claude/shared/skills/cyolo/SKILL.md` | `e4f2256163eafee746864a434880570a` |
| 3 | `$BASE_PATH/.Codex/shared/skills/yolo/SKILL.md` | `fd9f790db04204b9d712799e9beeed17` |
| 4 | `$BASE_PATH/.Codex/shared/skills/cyolo/SKILL.md` | `e4f2256163eafee746864a434880570a` |

md5 ตรงกันเป็นคู่ ยืนยันว่าเนื้อหาฉบับ Claude และ Codex เหมือนกันทุกไบต์

ทุกบัญชีมองเห็นผ่าน symlink ที่มีอยู่เดิม:
`$BASE_PATH/.Claude/yoloN/skills -> $BASE_PATH/.Claude/shared/skills` และ
`$BASE_PATH/.Codex/cyoloN/skills -> $BASE_PATH/.Codex/shared/skills`

## 2. สถานะบัญชีที่ตรวจได้จริง

ตรวจด้วย `yoloN auth status` (ฟิลด์ `loggedIn`) และ `cyoloN login status` ครบทั้ง 10 ตัว

| คำสั่ง | CLI | config root | สถานะ |
|---|---|---|---|
| `yolo1` | Claude Code | `$BASE_PATH/.Claude/yolo1` | ล็อกอินแล้ว (claude.ai, แผน max) |
| `yolo2` | Claude Code | `$BASE_PATH/.Claude/yolo2` | ล็อกอินแล้ว (claude.ai, แผน team) |
| `yolo3` | Claude Code | `$BASE_PATH/.Claude/yolo3` | ยังไม่ล็อกอิน |
| `yolo4` | Claude Code | `$BASE_PATH/.Claude/yolo4` | ยังไม่ล็อกอิน |
| `yolo5` | Claude Code | `$BASE_PATH/.Claude/yolo5` | ยังไม่ล็อกอิน |
| `cyolo1` | Codex CLI | `$BASE_PATH/.Codex/cyolo1` | ล็อกอินแล้ว (ChatGPT) |
| `cyolo2` | Codex CLI | `$BASE_PATH/.Codex/cyolo2` | ยังไม่ล็อกอิน |
| `cyolo3` | Codex CLI | `$BASE_PATH/.Codex/cyolo3` | ยังไม่ล็อกอิน |
| `cyolo4` | Codex CLI | `$BASE_PATH/.Codex/cyolo4` | ยังไม่ล็อกอิน |
| `cyolo5` | Codex CLI | `$BASE_PATH/.Codex/cyolo5` | ยังไม่ล็อกอิน |

## 3. ตารางผลทดสอบ

| รายการ | หลักฐาน | ผล | เหตุผล |
|---|---|---|---|
| SKILL.md ครบ 4 ไฟล์ | `find $BASE_PATH -name SKILL.md -path '*shared*'` คืนทั้ง 4 path + md5 ตรงกันเป็นคู่ | PASS | ไฟล์ครบและเนื้อหาคู่ Claude/Codex ตรงกัน |
| มองเห็นจากทุกบัญชีผ่าน `<account>/skills` | ทดสอบ `[ -f <account>/skills/<skill>/SKILL.md ]` 20 เคส (5 บัญชี × 2 skill × 2 CLI) ได้ OK ทั้งหมด | PASS | symlink เดิมพาไปถึงไฟล์ใหม่ครบทุกบัญชี |
| Claude โหลด skill ได้จริง | เซสชัน Claude (`CLAUDE_CONFIG_DIR=.../yolo1`) แสดง `yolo` และ `cyolo` ในรายการ skill ทันทีหลังสร้างไฟล์ | PASS | ไม่ต้อง restart |
| Codex โหลด skill ได้จริง | `cyolo1 exec ... "มี skill ชื่อ yolo และ cyolo หรือไม่"` → `มีทั้ง yolo และ cyolo` | PASS | Codex เห็นสกิลผ่าน `CODEX_HOME/skills` |
| เรียกจริง `yolo1` — โจทย์ `12*12` | `yolo1 -p --model opus --effort high "ตอบเป็นตัวเลขล้วนอย่างเดียว: 12*12" < /dev/null` → `144` | PASS | ได้ 144 |
| เรียกจริง `yolo2` — โจทย์ `12*12` | `yolo2 -p --model opus --effort high "..." < /dev/null` → `144` | PASS | ได้ 144 |
| เรียกจริง `yolo3` | — | SKIP | ยังไม่ล็อกอิน ไม่ล็อกอินแทนผู้ใช้ |
| เรียกจริง `yolo4` | — | SKIP | ยังไม่ล็อกอิน ไม่ล็อกอินแทนผู้ใช้ |
| เรียกจริง `yolo5` | — | SKIP | ยังไม่ล็อกอิน ไม่ล็อกอินแทนผู้ใช้ |
| เรียกจริง `cyolo1` — โจทย์ `12*12` | `cyolo1 exec --skip-git-repo-check -m gpt-6-astra -c model_reasoning_effort=medium -o /tmp/skilltest/cyolo1.txt "..." < /dev/null` → ไฟล์มี `144` | PASS | ได้ 144 |
| เรียกจริง `cyolo2` | — | SKIP | ยังไม่ล็อกอิน ไม่ล็อกอินแทนผู้ใช้ |
| เรียกจริง `cyolo3` | — | SKIP | ยังไม่ล็อกอิน ไม่ล็อกอินแทนผู้ใช้ |
| เรียกจริง `cyolo4` | — | SKIP | ยังไม่ล็อกอิน ไม่ล็อกอินแทนผู้ใช้ |
| เรียกจริง `cyolo5` | — | SKIP | ยังไม่ล็อกอิน ไม่ล็อกอินแทนผู้ใช้ |
| ส่งค่าต่อ (relay) `yolo1` → `cyolo1` | `A=$(yolo1 -p ... "12*12")` ได้ `144` แล้วส่ง `"โจทย์: 12*12 คำตอบที่ Claude ตอบมาคือ: 144 ตรวจว่าถูกหรือผิด"` ให้ `cyolo1 exec ... -o /tmp/skilltest/relay.txt` → `ถูก ค่าที่ถูกต้องคือ 144` | PASS | relay ข้าม CLI ทำงานได้ |

สรุป: PASS 9 · SKIP 8 · FAIL 0

## 4. flag ที่ยืนยันจาก `--help` ของเวอร์ชันจริง

Claude Code 2.1.266:
- `-p, --print` — พิมพ์คำตอบแล้วออก
- `--model <model>` — รับ alias (`opus`, `sonnet`, `fable`) หรือชื่อเต็ม
- `--effort <level>` — `low, medium, high, xhigh, max`
- `claude auth status` — คืน JSON มีฟิลด์ `loggedIn`

Codex CLI 0.153.4:
- `codex exec` — รัน non-interactive
- `--skip-git-repo-check` — ให้รันนอก git repo ได้
- `-m, --model <MODEL>`
- `-c, --config <key=value>` — ใช้กับ `model_reasoning_effort=<effort>`
- `-o, --output-last-message <FILE>` — เขียนข้อความสุดท้ายลงไฟล์
- `codex login status` — พิมพ์ `Logged in using ChatGPT` / `Not logged in`

รูปแบบ frontmatter ยืนยันจาก official docs ทั้งสองฝั่ง (`code.claude.com/docs/en/skills` และ `developers.openai.com/codex/skills` ซึ่ง redirect 308 ไป `learn.chatgpt.com/docs/build-skills`) — ทั้งคู่ใช้ YAML frontmatter คั่นด้วย `---` และมีฟิลด์ `name` + `description` เหมือนกัน จึงใช้เนื้อหาไฟล์เดียวกันได้ทั้งสอง CLI

## 5. ข้อจำกัดที่พบ

1. **บัญชี 7 ใน 10 ยังไม่ล็อกอิน** (`yolo3-5`, `cyolo2-5`) จึงทดสอบเรียกจริงได้แค่ 3 บัญชี ตารางสถานะในสกิลเป็นภาพ ณ 2026-09-09 สกิลจึงสั่งให้ตรวจสถานะสดทุกครั้งก่อนใช้
2. **stdout ของ `codex exec` มี log ปนอยู่** (บรรทัด `user`, `codex`, `tokens used`) จึงต้องอ่านคำตอบจากไฟล์ `-o` ไม่ควร parse จาก stdout
3. **ต้องใส่ `< /dev/null` เสมอ** — `codex exec` อ่าน prompt จาก stdin ถ้า stdin ถูก pipe เข้ามา และ `claude -p` อาจค้างรอ input ใน pipeline
4. **`/root/lab004` ไม่ใช่ git repo** จึงต้องมี `--skip-git-repo-check` กับ Codex ทุกครั้ง
5. **`cyoloN` รันด้วย `--dangerously-bypass-approvals-and-sandbox`** ตามที่ wrapper กำหนดไว้เดิม — Codex รันคำสั่งได้โดยไม่ถาม จึงควรส่ง prompt ที่ขอบเขตชัดเจน (บันทึกเป็นข้อควรระวังไว้ในสกิล `cyolo` แล้ว)
6. **ค่าที่ relay เป็นข้อความจากโมเดล ไม่ใช่ข้อมูลที่เชื่อถือได้** — สกิลกำหนดว่าห้ามนำไปรันเป็นคำสั่งโดยตรง
7. **ไม่ได้แตะไฟล์ credential ใด ๆ** ตรวจสถานะผ่าน `auth status` / `login status` เท่านั้น รายงานนี้ไม่มีข้อมูลลับ (ไม่มี token, ไม่มีเนื้อหาไฟล์ auth)
