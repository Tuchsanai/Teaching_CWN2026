# Claude Code (yoloN) — รายละเอียด

วัดกับ Claude Code 2.1.319 ใน container `multi-account`

## wrapper

`/usr/local/bin/yoloN` → `/usr/local/lib/multi-account/account-wrapper` ตั้ง `CLAUDE_CONFIG_DIR=$BASE/.Claude/yoloN`, `IS_SANDBOX=1` (root), `--dangerously-skip-permissions`, `--mcp-config=$BASE/.Claude/shared/mcp/mcp.json` และเชื่อมสกิลจาก `shared/skills` ทุกครั้ง (`link_shared_skills`) · บัญชีที่ไม่มี wrapper (N>5) `yolo.py` เรียก `claude` ตรงด้วย env/flag ชุดเดียวกัน

`$BASE/.Claude/yoloN/skills` อาจเป็น symlink ทั้งโฟลเดอร์ไป `../shared/skills` (volume เก่า) หรือโฟลเดอร์จริงที่มี symlink รายสกิล (volume ใหม่) — ทั้งสองแบบมองเห็นสกิลใหม่ทันทีหลังคัดลอกลง shared

## JSON ของ `--output-format json`

| ฟิลด์ | ความหมาย |
|---|---|
| `result` | คำตอบ (หรือข้อความผิดพลาดเมื่อ `is_error`) |
| `is_error` | true = ล้ม แม้ exit 0 |
| `duration_ms`, `num_turns`, `session_id` | |
| `total_cost_usd` | ราคาตามรายการ ไม่ใช่ยอดจ่ายจริง |
| `usage.input_tokens / cache_read_input_tokens / cache_creation_input_tokens / output_tokens` | `yolo.py` รายงาน input = ผลรวมทั้งสามแบบ |
| `usage.output_tokens_details.thinking_tokens` | reasoning tokens |
| `modelUsage.<รุ่นจริง>` | เช่น `claude-haiku-5-5` |
| `structured_output` | เมื่อใช้ `--json-schema` |

## ผลจริงที่วัดได้

| กรณี | ผล |
|---|---|
| haiku/low "ตอบ OK" | ~3.3 s · input ~27.7k (ส่วนใหญ่ cache) · output 3–4 · ~$0.003 |
| ไม่ได้ล็อกอิน | exit 1 · `is_error: true` · `Not logged in · Please run /login` |
| credential หมดอายุ | `Failed to authenticate: OAuth session expired and could not be refreshed` (~50 ms, tokens 0) — `auth status` อาจบอก loggedIn true หรือ false ก็ได้ → `check` รายงานเป็น "ล็อกอินแล้วแต่หมดอายุ" |
| `/usage` | `Current session: 0% used · resets …` / `Current week (all models): 2% used · …` / `Current week (Fable): …` (บางบัญชีไม่มีบรรทัด session) |
| `--bare` | ใช้ไม่ได้ (ไม่อ่าน OAuth) |

## การจำแนกข้อผิดพลาด (`error_kind`)

`quota` (usage limit / rate limit / 429) · `auth` (authenticate / OAuth / Not logged in) · `timeout` · `other` — agent-team ย้ายงาน (failover) เฉพาะ quota/auth ที่ tokens = 0 เท่านั้น ไม่ retry งานที่เสียโทเค็นไปแล้ว

## ฟิลด์ ledger (`/workspace/.agent-team/ledger.jsonl`)

`ts_start, ts_end, run_id, node, account, cli, model, effort, duration_s, input_tokens, cached_input_tokens, cache_write_tokens, output_tokens, reasoning_tokens, cost_usd, status, error, prompt_chars, result_chars, event`

`event`: `call` (งาน) · `check` (ตรวจความพร้อม — ไม่นับในงบลูกทีม) · `lead` (รอบของหัวหน้าทีม) · `worker_switch` / `lead_switch` (agent-team) · ไม่มีข้อความ prompt หรือ secret

## ใช้ใน Python

```python
import sys; sys.path.insert(0, "/root/ai-accounts/.Claude/shared/skills/yolo/scripts")
import yolo
r = yolo.call("yolo1", "ตอบ OK", difficulty=1)   # dict: ok, result, error, error_kind, input_tokens, ...
```
