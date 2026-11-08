# Claude Code CLI (`yoloN`) — รายละเอียด

ตรวจกับ Claude Code 2.1.319 ใน container `multi-account` (2026-11-08) อัปเกรด CLI แล้วให้ตรวจ `claude --help` และเรียกจริงซ้ำ

## บัญชี

- `BASE=/root/ai-accounts` (volume `ai-accounts` คงอยู่แม้ลบ container) · บัญชีอยู่ที่ `$BASE/.Claude/yoloN` = `CLAUDE_CONFIG_DIR`
- `yolo1`–`yolo5` เป็น wrapper (`/usr/local/bin/yoloN` → `account-wrapper`) ตั้ง `CLAUDE_CONFIG_DIR`, `IS_SANDBOX=1`, `--dangerously-skip-permissions` และ `--mcp-config=$BASE/.Claude/shared/mcp/mcp.json` ให้เอง
- ไม่มี wrapper (N > 5) → `macore.launch()` เรียก `claude` ตรงพร้อม env เดียวกัน
- `$BASE/.Claude/yoloN/skills` เป็น symlink ทั้งโฟลเดอร์ไป `../shared/skills` วางสกิลใน shared แล้วทุกบัญชีเห็นทันที
- ทุกบัญชีเป็น root คนเดียวกัน แยกกันระดับโฟลเดอร์เท่านั้น

## เรียกงานเดียว

```bash
yolo2 -p "<prompt>" --model haiku --effort low --output-format json \
      --no-session-persistence --strict-mcp-config < /dev/null
```

- ต้องมี `-p` และปิด stdin (`< /dev/null`) เสมอ ไม่งั้นค้างรอ input
- prompt ต้องอยู่ก่อน flag ที่รับหลายค่า (`--allowedTools`, `--add-dir`, `--mcp-config`, `--tools`, `--betas`) ไม่งั้น flag กลืน prompt · prompt ที่ขึ้นต้นด้วย `-` สคริปต์เติมช่องว่างนำหน้าให้
- `--no-session-persistence` ทำให้บัญชีเดียวรันหลายตัวพร้อมกันได้ (โควตาใช้ร่วมกันทั้งบัญชี)
- `--strict-mcp-config` ใช้เฉพาะ MCP จาก `--mcp-config` (wrapper ใส่ mcp.json ของ shared) ตัด connector อื่นออก
- `cd` ไปโฟลเดอร์งานก่อน (หรือ `--cwd`) เพราะ agent เขียนไฟล์ลง cwd
- ผลแบบมีโครงสร้าง: `--json-schema '<schema>'` แล้วอ่าน `structured_output`
- `--max-budget-usd` ใช้เมื่อผู้ใช้กำหนดวงเงินเท่านั้น

## JSON ที่ได้ (`--output-format json`)

| ฟิลด์ | ความหมาย |
|---|---|
| `result` | คำตอบ (หรือข้อความ error เมื่อ `is_error`) |
| `is_error` | **ตัวตัดสินจริง** — exit code 0 ได้แม้ล้ม และ 1 เมื่อ auth ล้ม |
| `duration_ms`, `num_turns`, `session_id` | เวลา จำนวนรอบ |
| `total_cost_usd` | ราคาตามรายการ (list price) ไม่ใช่ยอดจ่ายจริงของ subscription |
| `usage.{input_tokens, cache_read_input_tokens, cache_creation_input_tokens, output_tokens}` | `output_tokens_details.thinking_tokens` = reasoning |
| `modelUsage.<รุ่นจริง>` | เช่น `claude-haiku-5-5` (`canonicalModel`, `costUSD`) |
| `structured_output` | เมื่อใส่ `--json-schema` |

การบันทึกลง ledger (ให้ Claude กับ Codex เทียบกันได้): `input_tokens` = input + cache read + cache write · `cached_input_tokens` = cache read · `cache_write_tokens` = cache creation · `reasoning_tokens` = thinking tokens

## ความพร้อมของบัญชี

| สถานะ | ตรวจอย่างไร |
|---|---|
| ไม่ได้ล็อกอิน | `yoloN auth status --json` → `loggedIn: false` (ไม่ใช้โทเค็น) |
| ล็อกอินแล้วแต่หมดอายุ | `loggedIn: true` แต่เรียกจริงได้ `is_error: true`, `result: "Failed to authenticate: OAuth session expired and could not be refreshed"` (~50 ms, tokens 0) |
| พร้อม | เรียกจริง `haiku`/`low` "ตอบ OK" ได้ `OK` (~3 s, ~$0.003 list) |

`yolo.py check` ทำครบทั้งสามขั้นและเก็บผลไว้ที่ `/workspace/.agent-team/readiness.json` (agent-team ใช้ซ้ำภายใน 10 นาที) · `auth status --json` มี email/orgId — สคริปต์อ่านแค่ `loggedIn`, `subscriptionType`

## โควตา

`yoloN -p "/usage" --strict-mcp-config --no-session-persistence` เป็นคำสั่งในตัว ไม่เรียกโมเดล ได้บรรทัด:

```
Current session: 0% used · resets Nov 8, 11:10am (Asia/Bangkok)
Current week (all models): 2% used · resets Nov 9, 1pm (Asia/Bangkok)
Current week (Fable): 1% used · resets Nov 9, 1pm (Asia/Bangkok)
```

- เป็น **% ที่ใช้ไปแล้ว** แต่ละบัญชีรีเซ็ตไม่ตรงกัน · บางบัญชีไม่มีบรรทัด `Current session` (ไม่มี session window ที่กำลังนับ) → รายงานเท่าที่มี ห้ามเดา
- ไม่มีบรรทัด `Current …` เลย → สคริปต์รายงาน "ไม่มีข้อมูลโควตา"
- เวลาของข้อมูล = เวลาที่เรียก (ข้อมูลสด) เก็บใน `/workspace/.agent-team/quota.json`

## ผลวัดจริง (2026-11-08, 2.1.319)

| การทดสอบ | ผล |
|---|---|
| `haiku`/`low` "ตอบ OK" yolo1, yolo2 พร้อมกัน | 3.3 s ต่อครั้ง · in ~27.7k (cache) · out 4 · $0.003 list |
| บัญชีไม่ล็อกอิน (yolo3) เรียกจริง | exit 1 · `is_error` · `OAuth session expired` · 45 ms · 0 tokens |
| alias → รุ่นจริง | `haiku` → `claude-haiku-5-5` |

จากชุดเดิม (2.1.302): `opus`→`claude-opus-5-5`, `sonnet`→`claude-sonnet-5-5`, `fable`→`claude-fable-5-1` · หลายตัวต่อบัญชีพร้อมกันได้ (ทดสอบ 4 ตัว/บัญชี) · effort มีผลกับงานที่ต้องคิดจริงเท่านั้น โจทย์ง่ายถูกทุกระดับ · `--bare` ใช้ไม่ได้ (ไม่อ่าน OAuth)

## ความปลอดภัย

`yoloN` ข้าม permission ทั้งหมด ทำเฉพาะงานและไฟล์ที่ผู้ใช้อนุญาต ห้ามส่งข้อมูลลับออกนอก ห้ามแตะ `.credentials.json` / `.claude.json` · ledger เก็บแค่จำนวนตัวอักษรของ prompt ไม่เก็บข้อความ
