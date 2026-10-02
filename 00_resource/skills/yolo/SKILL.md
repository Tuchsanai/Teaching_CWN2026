---
name: yolo
description: เรียก Claude Code อีกบัญชีผ่านคำสั่ง yolo1–yolo5 (หรือโปรไฟล์ yoloN ผ่าน CLAUDE_CONFIG_DIR) — ส่ง prompt ให้บัญชีอื่นทำงานแทน เลือกโมเดลและ effort ได้ ส่งค่าต่อกันข้ามบัญชีหรือข้าม CLI ได้ เช็คสถานะล็อกอินด้วย auth status และโควตา /usage ข้ามบัญชีได้ฟรี ใช้เมื่อผู้ใช้ขอ "เรียก yolo1", "สั่ง Claude อีก account", "แบ่งงานไปอีกบัญชี", "เช็คโควตาแต่ละบัญชี" หรืออยากเทียบคำตอบข้ามบัญชี
argument-hint: "[-a <N>] [-m <model>] [-e <effort>] <prompt>"
allowed-tools: Bash(yolo1 *), Bash(yolo2 *), Bash(yolo3 *), Bash(yolo4 *), Bash(yolo5 *), Bash(env IS_SANDBOX=1 CLAUDE_CONFIG_DIR=/root/workspace/ai-accounts/.Claude/yolo* claude *), Bash(cyolo1 *), Bash(cyolo2 *), Bash(cyolo3 *), Bash(cyolo4 *), Bash(cyolo5 *)
---

# บัญชีที่ใช้ได้

`yolo1`–`yolo5` คือ 5 โปรไฟล์ที่แยก config/credential กันคนละชุด (`/root/workspace/ai-accounts/.Claude/yolo<N>`) บางตัวอาจยังไม่ได้ล็อกอิน — เช็คด้วย `auth status` ก่อนใช้ (ดูหัวข้อถัดไป)

- ไม่ระบุบัญชีให้ใช้ `yolo1` ถ้าผู้ใช้ระบุ index มาให้ใช้ตามนั้น รับ N เป็นเลขฐานสิบ `[1-9][0-9]*` เท่านั้น ไม่ส่งค่าอื่นไปประกอบคำสั่ง shell
- launcher บนเครื่องนี้รองรับชื่อ `yolo1`–`yolo5` เท่านั้น (`case yolo[1-5]`) ถ้าผู้ใช้ขอ N มากกว่า 5 และโปรไฟล์ `/root/workspace/ai-accounts/.Claude/yolo<N>` มีอยู่แล้ว ให้เรียกคำสั่งเทียบเท่าโดยตรง:

  ```bash
  env IS_SANDBOX=1 CLAUDE_CONFIG_DIR=/root/workspace/ai-accounts/.Claude/yolo<N> claude --dangerously-skip-permissions -p ... "<prompt>" < /dev/null
  ```

  ไม่สร้างโปรไฟล์หรือ symlink ใหม่เอง ถ้าโปรไฟล์ไม่มีให้แจ้งผู้ใช้
- อย่าเดาว่าบัญชีไหนผูกกับใครหรือแพลนอะไร `auth status` บอก `subscriptionType` ได้ (เช่น `max`, `team`) แต่ถ้างานต้องเจาะจงตัวตนหรือองค์กร ให้ถามผู้ใช้
- ถ้าบัญชีที่ผู้ใช้ระบุยังไม่ได้ล็อกอิน ให้แจ้งและให้ผู้ใช้รัน `! yolo<N>` แล้ว `/login` เอง (หรือ `! yolo<N> auth login`) ห้ามสลับไปบัญชีอื่นเองเงียบ ๆ
- เรียกบัญชีเดียวกับ session ที่รันอยู่ได้ (ทดสอบซ้อนแล้วผ่าน) แต่อย่ารันหลายตัวของบัญชีเดียวกัน **พร้อมกัน** เพราะเขียน `CLAUDE_CONFIG_DIR` เดียวกัน — ให้เรียงทีละตัว ส่วนคนละบัญชีขนานกันได้

# ตรวจสถานะล็อกอิน (auth status)

`claude auth status` เป็น subcommand ที่ **ไม่เสียโทเคน ไม่ต้องเปิด session** และเร็วกว่า `/usage` ใช้แยกบัญชีที่ล็อกอินแล้วออกจากบัญชีที่ยังไม่ได้ล็อกอิน:

```bash
auth_all() {
  for n in "$@"; do
    out=$("yolo$n" auth status --json </dev/null 2>/dev/null)
    printf 'yolo%s | %s\n' "$n" "$(printf '%s' "$out" | python3 -c '
import json,sys
try: d=json.load(sys.stdin)
except Exception: print("อ่านสถานะไม่ได้"); sys.exit()
print("logged in · " + str(d.get("subscriptionType")) + " · " + str(d.get("authMethod")) if d.get("loggedIn") else "ไม่ได้ล็อกอิน")')"
  done
}
auth_all 1 2 3 4 5
```

- ล็อกอินแล้ว → JSON มี `loggedIn: true`, `authMethod: "claude.ai"`, `subscriptionType` และ exit code 0
- ยังไม่ได้ล็อกอิน → `loggedIn: false`, `authMethod: "none"` และ **exit code 1** (ต่างจาก `-p` ที่ exit 0 เสมอ) ใช้ exit code ตัดสินได้
- JSON มี `email`/`orgId` ของบัญชีด้วย ใช้ยืนยันตัวตนบัญชีได้เมื่อผู้ใช้ถาม แต่ห้ามคัดลอกลงไฟล์หรือส่งต่อไปที่อื่น
- `--text` ให้ข้อความอ่านง่ายแทน JSON

# ค่าที่รองรับ

- Model: `opus` (ค่าเริ่มต้น) → `claude-opus-5-5`, `fable` → `claude-fable-5-1`, `sonnet` → `claude-sonnet-5-5`, `haiku` → `claude-haiku-4-5` (mapping ของ Claude Code 2.1.287 — alias ชี้รุ่นใหม่ให้เองเมื่ออัปเกรด CLI ตรวจจาก `canonicalModel` ทุกครั้งที่อัปเกรด) — ใช้ alias เท่านั้น หรือ model ID เต็มที่ตรวจสอบแล้ว เติม `[1m]` ต่อท้ายเพื่อขอ context 1M เช่น `opus[1m]`
- Effort: `low`, `medium` (ค่าเริ่มต้น), `high`, `xhigh`, `max` — สูงขึ้น = คิดมากขึ้นจริง วัดได้จาก `thinkingTokens` ไม่ใช่แค่ชื่อ flag
- ต้องใส่ทั้งสอง flag เสมอ ค่าที่ผู้ใช้ระบุเองมีสิทธิ์เหนือค่าเริ่มต้นเสมอ
- อ่าน `$ARGUMENTS`: `-a <N>`, `-m <model>`, `-e <effort>` ที่เหลือคือ prompt — ไม่มี prompt ให้ถามผู้ใช้ก่อน หากเลขบัญชีจาก `-a` ขัดกับบัญชีที่ผู้ใช้ระบุในข้อความ ให้ถามก่อนรัน

เลือก effort จากโจทย์ ไม่ใช่จากขนาดโมเดล: งานเลขหรือ reasoning ที่มีคำตอบตายตัวใช้ `max`/`xhigh` งานเรียกดูข้อมูลหรือสรุปสั้นใช้ `low`/`medium` งาน probe หรือทดสอบ pipeline ใช้ `haiku`/`low` (ถูกสุด ~$0.02 list price ต่อ call)

# การเรียกใช้งาน

```bash
yolo<N> -p --model <model> --effort <effort> --strict-mcp-config "<prompt>" < /dev/null
```

ต้องมี `-p` เสมอ (ไม่ใส่จะเปิด TUI ค้าง) และ `< /dev/null` เสมอ กัน stdin ค้าง (ยกเว้นตอนป้อนข้อมูลทาง stdin)
`--strict-mcp-config` ใส่ไว้ทุกครั้ง: launcher ส่ง `--mcp-config=<BASE_PATH>/.Claude/shared/mcp/mcp.json` (playwright) มาให้เองอยู่แล้ว flag นี้จึง **เก็บ playwright ไว้** และตัดเฉพาะ connector ของ claude.ai (Docs, Drive, Gmail, Canva ฯลฯ) ออก (เหลือ 54 tools จาก 147) ถอดออกเฉพาะงานที่ต้องใช้ connector ของ claude.ai จริง

เมื่อต้องอ่านผลลัพธ์และค่าใช้จ่ายแบบมีโครงสร้าง:

```bash
yolo<N> -p --model <model> --effort <effort> --strict-mcp-config --output-format json --no-session-persistence "<prompt>" < /dev/null
```

JSON ให้ `result`, `is_error`, `total_cost_usd`, `duration_ms`, `duration_api_ms`, `session_id`, `num_turns`, `permission_denials`, `subagent_stats` และ `modelUsage.<id>.{canonicalModel,thinkingTokens,outputTokens}`
`modelUsage` บน 2.1.287 มี key เดียวคือรุ่นที่สั่ง (รุ่นเก่าเคยมี `claude-haiku-4-5-20251001` ติดมาด้วยจากงานเบื้องหลัง) — ถ้าเห็นหลาย key ให้ถือ key ที่ไม่ใช่ haiku เป็นรุ่นที่ทำงานจริง

**ต้องการค่าที่ parse ได้แน่นอน** ให้ใส่ `--json-schema '<schema>'` แล้วอ่านจาก `structured_output` แทนการ regex จาก `result` — CLI บังคับให้โมเดลตอบตาม schema และ validate ให้:

```bash
yolo<N> -p --model haiku --effort low --strict-mcp-config --output-format json --no-session-persistence \
  --json-schema '{"type":"object","properties":{"answer":{"type":"integer"}},"required":["answer"]}' \
  "12*12 เท่ากับเท่าไร" < /dev/null | python3 -c "import json,sys;print(json.load(sys.stdin)['structured_output']['answer'])"
```

(ทดสอบแล้วได้ `structured_output: {"answer": 144}` และ `result` เป็นสตริง JSON เดียวกัน)

`--max-budget-usd <amount>` ใช้เฉพาะเมื่อผู้ใช้กำหนดวงเงินหรือยอมรับวงเงินนั้นแล้ว ค่านี้อาจหยุดคำขอหลังค่าใช้จ่ายเริ่มเกิดขึ้น ไม่ใช่เพดานที่รับประกัน (ใช้ได้กับ `-p` เท่านั้น เช่นเดียวกับ `--no-session-persistence`, `--json-schema` และ `--fallback-model`)

`cd` เข้าโฟลเดอร์เป้าหมายก่อนรัน เพราะ sub-agent เขียนไฟล์ลง cwd งานทดลองให้รันใน scratchpad และเปิดสิทธิ์โฟลเดอร์เพิ่มด้วย `--add-dir` เมื่อจำเป็น

ก่อนรัน ให้แจ้งบัญชี, model, effort และวงเงินถ้ามี หลังรัน ให้สรุปผลสำเร็จหรือข้อผิดพลาด, ไฟล์ที่เปลี่ยน, `canonicalModel` และ `total_cost_usd` เมื่อมีข้อมูล ห้าม retry งานที่เสียเงินโดยอัตโนมัติหลัง budget หมดหรือ API error

# ตรวจโควตาข้ามบัญชี (/usage)

`/usage` ใช้ผ่าน `-p` ได้ **ไม่เสียโทเคนและไม่คิดเงิน** (`total_cost_usd=0`, `modelUsage={}`) จึงเช็คก่อนเลือกบัญชีได้เสมอ แต่ช้ากว่า `auth status` เพราะต้องเปิด session — ใช้ `auth status` กรองบัญชีที่ล็อกอินแล้วก่อน แล้วค่อย `/usage` เฉพาะบัญชีที่ใช้ได้

```bash
usage_all() {
  for n in "$@"; do
    if ! "yolo$n" auth status --json </dev/null >/dev/null 2>&1; then
      printf 'yolo%s | ไม่ได้ล็อกอิน\n' "$n"; continue
    fi
    out=$("yolo$n" -p --strict-mcp-config "/usage" </dev/null 2>&1)
    if printf '%s\n' "$out" | grep -q '^Current'; then
      printf '%s\n' "$out" | grep '^Current' | sed "s/^/yolo$n | /"
    else
      printf 'yolo%s | /usage ใช้ไม่ได้\n' "$n"
    fi
  done
}
usage_all 1 2 3 4 5
```

อ่านผล 3 บรรทัดต่อบัญชี: `Current session` (หน้าต่าง 5 ชม.), `Current week (all models)` และ `Current week (<model>)` ซึ่งเป็นโควตาเฉพาะรุ่นระดับบน แต่ละบรรทัดมีเวลารีเซ็ตของตัวเอง และรีเซ็ตของแต่ละบัญชีไม่ตรงกัน บัญชีที่ยังไม่เคยใช้ในหน้าต่างนั้นจะไม่มี `resets ...` ต่อท้าย

- ตัวเลขเป็น **% ที่ใช้ไปแล้ว** ไม่ใช่โทเคนคงเหลือ — CLI ไม่บอกจำนวนโทเคนดิบ
- บรรทัดรุ่นจะโชว์ bucket ที่บัญชีนั้นแตะไป **ไม่ขึ้นกับ `--model` ที่ส่งไป** สั่ง `--model opus` ก็ยังอาจเห็นบรรทัด `(Fable)`
- บางบัญชีมีท่อน "What's contributing to your limits usage?" ต่อท้าย เป็นสถิติ session ในเครื่องนี้เท่านั้น ไม่รวมเครื่องอื่นหรือ claude.ai
- ก่อนโยนงานหนัก (`opus` + `xhigh`/`max`) ให้ `usage_all` ก่อน แล้วเลือกบัญชีที่ `% used` ต่ำสุดหรือใกล้รีเซ็ตที่สุด แล้วรายงานตัวเลขที่ใช้ตัดสินใจให้ผู้ใช้ทราบ ใช้โควตาประกอบการเลือกบัญชีเมื่อผู้ใช้มอบหมายให้เลือกเท่านั้น ห้ามเปลี่ยนบัญชีที่ผู้ใช้ระบุเพียงเพราะอีกบัญชีมีโควตามากกว่า

# ทำให้เร็วขึ้น

วัดจริงด้วย `haiku`/`low` โจทย์บรรทัดเดียว เทียบ wall clock กับ `duration_api_ms` เพื่อแยก overhead ในเครื่องออกจากเวลา API

- **`--strict-mcp-config` คือตัวคุ้มที่สุด** ตัด connector ของ claude.ai ออก call แรก (cold) ช่วยได้ wall 5.7s → 2.7s แต่ call ถัดไปที่ connector ยัง `pending` อยู่ต่างกันอยู่ในระดับ noise (~2.7–2.8s) (2026-10-02) การเลี่ยง launcher เพื่อตัด playwright ด้วย (`env ... claude --strict-mcp-config`) ลดจาก 54 เหลือ 29 tools (context เล็กลง) แต่ wall เท่าเดิม
- **ขนานคนละบัญชี** 3 งานเรียงกัน 9.1s → ขนาน 3.3s (2.8×) บัญชีเดียวกันขนานไม่ได้ ต้องเรียงทีละตัว
- **สั่งให้ worker ใช้เชลล์คำนวณ** ตัวแปรที่แกว่งที่สุดคือ worker เลือกคิดในหัวหรือเรียกเครื่องมือ งานเดียวกันต่างกัน 10s vs 38s ดูหัวข้อ fan-out
- ไม่ช่วย: `--disable-slash-commands` (เท่าเดิม) · `--system-prompt` สั้น ๆ (ช้ากว่า เพราะ prompt cache ไม่ hit) · รันใน cwd ว่างเปล่า (อยู่ในระดับ noise)
- ใช้ไม่ได้: `--bare` ตอบ `Not logged in` เพราะบังคับ auth ผ่าน `ANTHROPIC_API_KEY` ไม่อ่าน OAuth ของบัญชี
- `--disallowedTools "Bash,Edit,Write,Read,Glob,Grep,WebFetch,WebSearch,Task,TodoWrite,NotebookEdit"` ตัด context เหลือ ~1/3 (cache read 21607 → 7039 โทเคน) แต่ wall เท่าเดิม — ใช้ประหยัดโควตาสำหรับงานถาม-ตอบล้วน ไม่ใช่เพื่อความเร็ว และห้ามใช้กับงานที่ต้องคำนวณ (`--tools ""` ปิดเครื่องมือทั้งหมดในความหมายเดียวกัน)
- **gotcha**: flag แบบ variadic (`--disallowedTools`, `--allowedTools`, `--tools`, `--mcp-config`, `--add-dir`, `--file`, `--betas`) กลืน argument ถัดไป วางไว้ก่อน prompt แล้วจะได้ `Error: Input must be provided either through stdin or as a prompt argument` — ให้วาง prompt ก่อน แล้วให้ flag พวกนี้อยู่ท้ายสุด (`--json-schema` รับค่าเดียว วางก่อน prompt ได้)

# แบ่งงานให้หลายบัญชีช่วยกัน (fan-out)

แบ่งข้อมูลเป็น chunk เขียนลงไฟล์ ส่งให้ worker แค่ **path** ไม่ใช่ตัวข้อมูล และ **สั่งให้คำนวณด้วยคำสั่งเชลล์ ห้ามคิดเอง** ข้อมูลจะไม่เข้า context เลย

```bash
fan() { yolo$1 -p --model haiku --effort low --strict-mcp-config --output-format json \
  --no-session-persistence "$2" </dev/null \
  | python3 -c "import json,sys;print(str(json.load(sys.stdin).get('result','')).strip())"; }

for n in 1 2 3; do
  fan $n "คำนวณผลรวมของตัวเลขในไฟล์ $PWD/part$n.txt ด้วยคำสั่งเชลล์ (awk หรือ python) ห้ามบวกเองในหัว ตอบเป็นตัวเลขล้วนอย่างเดียว" > "r$n.txt" &
done
wait
```

ผลวัดจริง — บวกเลข 300 ตัว แบ่ง 3 chunk ให้ yolo1/2/3 ทำขนานกัน (เฉลย 1604841 คำนวณแยกด้วย python):

| วิธีส่งข้อมูล | wall | ถูกต้อง | output tokens |
|---|---|---|---|
| path + สั่งใช้เชลล์ | **9.0s / 10.5s** | ✅ ทั้ง 2 รอบ | **1370–1549** |
| ยัดข้อมูลทาง stdin | 10.8s / 36.4s / 38.6s | ✅ ทั้ง 3 รอบ | 2753–11195 |
| path เฉย ๆ ไม่สั่งเครื่องมือ | 32.5s | ❌ worker บวกในหัวผิด | 7965 |
| ยัดข้อมูลใน prompt (inline) | 41.5s | ✅ | 11198 |
| path + ให้ worker เขียนไฟล์ผลเอง | 61.7s | ❌ ผิด 2 ใน 3 | 11907 |

- ส่ง **path + บังคับใช้เชลล์** เร็วที่สุด ถูกทุกรอบ และเปลืองโทเคนน้อยที่สุด ~8 เท่า
- **stdin ใช้ร่วมกับ prompt argument ได้** (`cmd -p "คำสั่ง" < data.txt`) เหมาะกับข้อมูลสั้นที่ใหญ่เกินใส่ argv แต่ข้อมูลจะเข้า context และเวลาแกว่ง 4 เท่าตามว่า worker เลือกคิดเองหรือไม่
- อย่าให้ worker เขียนไฟล์ผลลัพธ์เอง — ช้าที่สุดและผิด ให้ parent อ่านจาก `.result` (หรือ `.structured_output` เมื่อใช้ `--json-schema`) แทน
- ตรวจ `is_error` ของทุก job ก่อนรวม exit code 0 อย่างเดียวไม่ยืนยันว่าสำเร็จ (บัญชีที่ไม่ได้ล็อกอินก็ exit 0) ห้ามเอาผลจาก job ที่ล้มเหลวมารวม
- รวมผลเองที่ parent เสมอ และตรวจด้วยสคริปต์อิสระ อย่าให้ worker ตัวใดตัวหนึ่งเป็นคนรวม

# ส่งค่าต่อกันข้ามบัญชี (relay)

ดึงเฉพาะคำตอบด้วย `.result` แล้วส่งเข้า prompt ของบัญชีถัดไป สั่งให้ตอบค่าล้วนเสมอ ไม่งั้น hop ถัดไปจะได้ข้อความปนมา

```bash
val() { "yolo$1" -p --model "$2" --effort "$3" --strict-mcp-config --output-format json \
  --no-session-persistence "$4" </dev/null \
  | python3 -c "import json,sys;print(str(json.load(sys.stdin).get('result','')).strip())"; }

V1=$(val 1 fable low  "ตอบเป็นตัวเลขล้วนอย่างเดียว: 7*6")
V2=$(val 2 opus  high "ค่าที่ได้รับคือ $V1 จงบวก 100 ตอบเป็นตัวเลขล้วนอย่างเดียว")
V3=$(val 3 fable max  "ค่าที่ได้รับคือ $V2 จงคูณ 3 ตอบเป็นตัวเลขล้วนอย่างเดียว")
```

- ทุก hop ต้องคำนวณเฉลยด้วยสคริปต์อิสระมาเทียบ อย่าเชื่อค่าที่ relay มาโดยไม่ตรวจ hop ใดล้มเหลว (`is_error=true` หรือค่าผิดรูปแบบ) ให้หยุดสายงานและรายงาน
- ส่งค่าด้วย argument ที่ quote ถูกต้องหรือไฟล์ ไม่ประกอบคำสั่งด้วย `eval` และไม่รันข้อความผลลัพธ์เป็น shell
- ค่าที่ต้องเป็นตัวเลข/JSON แน่นอน ให้ใช้ `--json-schema` แล้วอ่าน `structured_output` แทน `.result` จะไม่ต้องพึ่งการสั่ง "ตอบค่าล้วน"
- **ข้าม CLI**: ส่งต่อไป Codex ใช้สกิล [cyolo](../cyolo/SKILL.md) (อ่านผลจากไฟล์ `-o`) เลือกบัญชี/model/effort ตามสกิลของฝั่งนั้น (launcher ปัจจุบันไม่มี `qyolo` แล้ว) ไม่ hard-code ชื่อรุ่นของค่ายอื่นลงในสกิลนี้

# กระจายงานข้าม CLI (yolo + cyolo) และ multi-agent ซ้อน

fan-out ผสมบัญชีได้ทั้ง Claude และ Codex ในรอบเดียว — แต่ละ job ใช้ไฟล์ผลของตัวเอง (`yN.json` ฝั่ง Claude, `-o cN.out` + `--json` log ฝั่ง Codex) แล้ว parent ตรวจและรวมเอง:

```bash
P() { echo "คำนวณผลรวมของตัวเลขในไฟล์ $PWD/part$1.txt ด้วยคำสั่งเชลล์ (awk หรือ python) ห้ามบวกเองในหัว ตอบเป็นตัวเลขล้วนอย่างเดียว"; }
yjob() { yolo$1 -p --model haiku --effort low --strict-mcp-config --output-format json --no-session-persistence "$(P $2)" </dev/null > y$1.json; }
cjob() { cyolo$1 exec --skip-git-repo-check -m gpt-6-astra -c model_reasoning_effort="low" --json -o c$1.out "$(P $2)" </dev/null > c$1.jsonl; }
yjob 1 1 & yjob 2 2 & yjob 3 3 & cjob 1 4 & cjob 2 5 & wait
# ฝั่ง yolo: ตรวจ is_error + อ่าน .result   ฝั่ง cyolo: ไม่มี "turn.failed" ใน jsonl + อ่าน cN.out
```

- **ตรวจความสำเร็จคนละแบบ**: yolo ใช้ `is_error` ใน JSON ส่วน cyolo ใช้ event `turn.failed` ใน `--json` และไฟล์ `-o` ต้องไม่ว่าง ทั้งสองฝั่ง exit 0 แม้ล้มเหลว
- **multi-agent ซ้อนใช้ได้ทั้งสองทิศ**: worker ที่เป็น orchestrator สั่ง `yoloN`/`cyoloN` ผ่านเชลล์ของตัวเองได้ (yolo bypass permission, cyolo bypass sandbox) ให้เขียนคำสั่งย่อยเต็ม ๆ ใน prompt พร้อม path ผลลัพธ์ และใช้ `--json-schema` กับ orchestrator ฝั่ง yolo เพื่อให้ได้ค่าย่อย + ผลรวมแบบ parse ได้ แล้ว parent ยังต้องตรวจซ้ำกับเฉลยอิสระ
- กฎบัญชีเดียวกันยังใช้กับงานซ้อน: orchestrator กับ worker ที่รันพร้อมกันต้องเป็นคนละบัญชี yolo (cyolo รันซ้อนบัญชีเดียวกันได้ตามสกิล cyolo)
- เลือก orchestrator ฝั่ง yolo เมื่อต้องการความเร็ว: งานซ้อนเดียวกัน yolo2 ใช้ 27s ส่วน cyolo2 ใช้ 72s (cyolo มี overhead ต่อ call สูงกว่า ~16–20s เทียบกับ yolo/haiku ~6–18s)

# ผลทดสอบ

Claude Code 2.1.287 + codex-cli 0.159.2 — ตรวจซ้ำ 2026-10-02 (launcher `/opt/ai-accounts/bin/ai-account`, `BASE_PATH=/root/workspace/ai-accounts`):

- `auth status --json`: yolo1 `max`, yolo2/yolo3 `team` (`claude.ai`, exit 0) — **yolo4/yolo5 ยังไม่ได้ล็อกอิน** (exit 1) ฝั่ง Codex: cyolo1/cyolo2 `Logged in using ChatGPT`, cyolo3–5 `Not logged in`
- alias map จาก `canonicalModel`: `opus` → `claude-opus-5-5`, `sonnet` → `claude-sonnet-5-5`, `fable` → `claude-fable-5-1`, `haiku` → `claude-haiku-4-5` ทุกตัว `is_error=false` ตอบ `144` ถูก (รันขนานคนละบัญชี)
- list price โจทย์บรรทัดเดียว `low`: haiku $0.018 · sonnet $0.038 · opus $0.075 · fable $0.23 — `duration_ms` 1.6–2.4s
- `--strict-mcp-config` ผ่าน launcher: เหลือ `playwright` ตัวเดียว (54 tools) ไม่ใส่จะโหลด connector claude.ai อีก 5 ตัว (147 tools, call แรก 5.7s เทียบกับ 2.7s)
- relay yolo ล้วน `yolo1(fable/low) → yolo2(opus/high) → yolo3(fable/max)` = `42 → 142 → 426` ✅
- relay ข้าม CLI `cyolo1(gpt-6-astra/low) → yolo2(opus/low) → cyolo2(gpt-6-astra/low)` = `42 → 142 → 426` ✅ รวม 34s
- fan-out ผสม 5 worker (yolo1/2/3 haiku/low + cyolo1/2 gpt-6-astra/low) บวกเลข 500 ตัว 5 chunk: ถูกทุก chunk รวม `25248998` ตรงเฉลย wall 19.9s (job ช้าสุดคือ cyolo2 19.9s)
- multi-agent ซ้อน: `yolo2(sonnet/low, --json-schema)` → สั่ง `cyolo1` + `yolo3` ขนาน ได้ `{cyolo1: 4952062, yolo3: 5047438, total: 9999500}` ✅ 27s · `cyolo2` → สั่ง `yolo1` + `cyolo1` ขนาน ได้ `{yolo1: 5188811, cyolo1: 4903876, total: 10092687}` ✅ 72s
- `--json-schema` คืน `structured_output: {"answer": 144}` ✅ · `/usage` ผ่าน `-p` ยัง `total_cost_usd=0`, `modelUsage={}` ครบ yolo1/2/3

matrix เดิม (2026-09-02) `yolo1/2/3 × {fable, opus} × {low, high, max}`:

- ทั้ง 6 ช่องผ่าน `is_error=false` ตอบถูกหมด
- relay `yolo1(fable/low) → yolo2(opus/high) → yolo3(fable/max)` ได้ `42 → 142 → 426` ตรงกับเฉลยที่คำนวณแยก
- **effort มีผลจริง** โจทย์นับเลข 1–1000 (เฉลย 401): `opus/low` think=27 → ตอบ **335 ผิด**, `opus/max` think=89 → **401 ถูก**; `fable/low` think=0 → **400 ผิด**, `fable/max` think=188 → **401 ถูก** — โจทย์ง่าย (`12*12`) ให้ think=0 ทุก effort จึงเห็นผลเฉพาะงานที่ต้องคิด
- `--model opus-5`, `opus-4-8` ถูกปฏิเสธด้วย `[claude-code:unrecognized_model]` จึงใช้ alias เท่านั้นจนกว่าจะตรวจ mapping ใหม่หลังอัปเกรด
- `--effort` ค่านอกลิสต์ (เช่น `ultra`) **ไม่ error** แต่เตือนแล้วตกกลับไปใช้ค่า default เงียบ ๆ จึงต้องสะกดให้ถูก
- `total_cost_usd` เป็น list price ไม่ใช่ยอดที่จ่ายจริงบน subscription และพองจาก cache creation ของ prompt ระบบ ใช้เทียบข้ามรันได้ อย่ารายงานเป็นค่าใช้จ่ายจริง
- prompt ภาษาไทยใช้ได้ปกติ
- รายงานของ sub-agent เชื่อไม่ได้ทั้งหมด ไฟล์ที่มันแก้ให้อ่านและรันทดสอบเองซ้ำ

# กลไก

`yolo1`–`yolo5` (และ `cyolo1`–`cyolo5`) เป็น symlink ใน `/usr/local/bin` ไป `/opt/ai-accounts/bin/ai-account` ซึ่งอ่าน `BASE_PATH` จาก `/opt/ai-accounts/config.sh` (ปัจจุบัน `/root/workspace/ai-accounts`) แล้ว `exec env IS_SANDBOX=1 CLAUDE_CONFIG_DIR=$BASE_PATH/.Claude/yolo<N> claude --dangerously-skip-permissions --mcp-config=$BASE_PATH/.Claude/shared/mcp/mcp.json "$@"` — `$HOME` ไม่ถูกเปลี่ยน การแยกบัญชีมาจาก `CLAUDE_CONFIG_DIR` อย่างเดียว (`IS_SANDBOX=1` จำเป็นเพราะ Claude Code ปฏิเสธ `--dangerously-skip-permissions` เมื่อรันเป็น root โดยไม่มีมัน) ถ้าโฟลเดอร์บัญชีไม่มี launcher จะ exit 1 พร้อมบอกให้รัน `install-ai-accounts`
คำสั่ง `env ...` สำหรับ N มากกว่า 5 ไม่ได้รับ shared MCP จาก launcher ถ้างานต้องใช้ playwright ให้เติม `--mcp-config=/root/workspace/ai-accounts/.Claude/shared/mcp/mcp.json` เอง
ฝั่ง Codex ดูสกิล [cyolo](../cyolo/SKILL.md) (`CODEX_HOME=$BASE_PATH/.Codex/cyolo<N>`) launcher ปัจจุบันไม่มี `qyolo` แล้ว
ทุกบัญชี share skills ผ่าน `<account>/skills -> /root/workspace/ai-accounts/.Claude/shared/skills` เพิ่ม skill ครั้งเดียวเห็นทุกบัญชี สำเนาเดียวกันมีที่ `/root/workspace/ai-accounts/.Codex/shared/skills/yolo` แก้แล้วให้ sync ทั้งสองที่

# ความปลอดภัย

`yolo<N>` ข้าม permission check ทั้งหมด จึงต้องทำเฉพาะงานและไฟล์ที่ผู้ใช้อนุญาต ห้ามขยายขอบเขต ส่งข้อมูลลับ หรือทำการเปลี่ยนแปลงภายนอกที่ผู้ใช้ไม่ได้ร้องขอ ห้ามอ่านหรือส่งต่อ `.credentials.json` ของบัญชีใด และไม่คัดลอก `email`/`orgId` จาก `auth status` ลงไฟล์หรือรายงานภายนอก
