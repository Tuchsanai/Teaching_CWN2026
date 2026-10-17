---
name: yolo
description: เรียก Claude Code บัญชีอื่น (yolo1–yoloN) และรัน multi-agent หลายตัวพร้อมกันข้ามบัญชี หลายตัวต่อบัญชี ผสมกับ Codex (cyoloN) ได้ในรอบเดียวด้วยสคริปต์ swarm ที่ฝังในไฟล์นี้ เลือกระดับความคิด (effort) ตามความยากของงานอัตโนมัติ (low→max ฝั่ง Claude, low→ultra ฝั่ง cyolo) งานสร้างภาพส่งให้ cyolo เอง ส่งค่าต่อข้ามบัญชี/ข้าม CLI เช็คล็อกอินและโควตาฟรี ย้ายเครื่องได้ (ไม่มี path ตายตัว) ใช้เมื่อผู้ใช้ขอ "เรียก yolo1", "สั่ง Claude อีก account", "แบ่งงานหลาย agent/หลายบัญชี", "รันขนาน", "เช็คโควตาแต่ละบัญชี" หรือเทียบคำตอบข้ามบัญชี
argument-hint: "[-a <N>] [-m <model>] [-e <effort>] <prompt>"
allowed-tools: Bash(yolo1 *), Bash(yolo2 *), Bash(yolo3 *), Bash(yolo4 *), Bash(yolo5 *), Bash(cyolo1 *), Bash(cyolo2 *), Bash(cyolo3 *), Bash(cyolo4 *), Bash(cyolo5 *), Bash(env IS_SANDBOX=1 CLAUDE_CONFIG_DIR=* claude *), Bash(env CODEX_HOME=* codex *), Bash(python3 */swarm.py *), Bash(awk *)
---

# yolo — Claude Code หลายบัญชี + multi-agent

| ต้องการ | ทำอย่างไร |
|---|---|
| เริ่มใช้ (ครั้งเดียวต่อ session) | [1. เตรียม](#1-เตรียม-ครั้งเดียวต่อ-session) |
| งานเดียว บัญชีเดียว | `cl <N> -p --model <m> --effort <e> ...` ([4](#4-เรียกงานเดียว)) |
| หลายงานพร้อมกัน หลายบัญชี หลายตัวต่อบัญชี ผสม Claude + Codex | `python3 "$SW" run jobs.json` ([5](#5-multi-agent-หลายตัวพร้อมกัน-swarm)) |
| ให้เลือกระดับความคิดตามความยาก | ใส่ `"difficulty": 1–6` ใน job ([3](#3-เลือกโมเดลและระดับความคิดตามความยาก)) |
| สร้างภาพ | **cyolo เท่านั้น** — job `{"image": "x.png", ...}` swarm ส่งไป cyolo เอง |
| ส่งค่าต่อกันเป็นทอด | [6. relay](#6-ส่งค่าต่อกัน-relay) |
| ดูโควตา (ฟรี) | [7. โควตา](#7-โควตา) |
| ย้ายไปเครื่องอื่น | [8](#8-ย้ายไปเครื่องอื่น) |

กฎเหล็ก: ทุก call ต้องมี `-p` และ `< /dev/null` · **exit code 0 ไม่ได้แปลว่าสำเร็จ** (ตรวจ `is_error` / swarm ตรวจให้) · ค่าที่ผู้ใช้ระบุเองชนะค่าเริ่มต้นเสมอ · ห้าม retry งานเสียเงินอัตโนมัติ · parent ตรวจผลเองด้วยสคริปต์อิสระเสมอ

# 1. เตรียม (ครั้งเดียวต่อ session)

ตำแหน่งโฟลเดอร์บัญชีต่างกันได้ทุกเครื่อง จึงไม่เขียน path ตายตัว — สคริปต์ `swarm.py` (ฝังท้ายไฟล์นี้) หาให้:

```bash
export SWARM_SKILL=<path ของ SKILL.md นี้>     # base directory ที่แสดงตอนโหลดสกิล + /SKILL.md
SW=${TMPDIR:-/tmp}/swarm.py
awk '/^# === swarm.py BEGIN/{f=1} f; /^# === swarm.py END/{exit}' "$SWARM_SKILL" > "$SW"
# cl <N> ... = yolo<N> ... ถ้ามี launcher; ไม่งั้น (หรือเมื่อตั้ง AI_ACCOUNTS_BASE/AI_CLAUDE_ROOT) เรียก claude ด้วย CLAUDE_CONFIG_DIR ที่หาเจอ
cl() { local a="yolo$1"; shift
  if command -v "$a" >/dev/null && [ -z "$AI_ACCOUNTS_BASE$AI_CLAUDE_ROOT" ]; then "$a" "$@"
  else local h; h=$(python3 "$SW" home "$a") || return 1
    env IS_SANDBOX=1 CLAUDE_CONFIG_DIR="$h" claude --dangerously-skip-permissions "$@"; fi; }
python3 "$SW" where  yolo1 yolo2 cyolo1     # แต่ละบัญชีชี้ไปที่ไหน (ไม่เสียโทเคน)
python3 "$SW" status yolo1 yolo2 cyolo1     # ล็อกอินหรือยัง (<1s, ไม่เสียโทเคน)
```

`python3 "$SW" home yolo1` พิมพ์ `CLAUDE_CONFIG_DIR` ของบัญชีบนเครื่องนี้ ถ้าต้องเรียก Codex ด้วย ใช้ฟังก์ชัน `cx` จากสกิล [cyolo](../cyolo/SKILL.md)

# 2. บัญชี

- `yolo<N>` = Claude Code ที่ `CLAUDE_CONFIG_DIR=<โฟลเดอร์บัญชี>/yolo<N>` ไม่ระบุใช้ `yolo1` · N ต้องเป็น `[1-9][0-9]*` เท่านั้น
- อ่าน `$ARGUMENTS`: `-a <N>`, `-m <model>`, `-e <effort>` ที่เหลือคือ prompt · ไม่มี prompt → ถามก่อน · `-a` ขัดกับข้อความ → ถามก่อน
- ไม่ได้ล็อกอิน → ให้ผู้ใช้รัน `! yolo<N> auth login` เอง (ไม่มี launcher: `! env CLAUDE_CONFIG_DIR=<ผลของ home> claude auth login`) **ห้ามสลับบัญชีเองเงียบ ๆ** · ไม่สร้างโปรไฟล์/symlink ใหม่เอง
- `auth status --json` บอก `subscriptionType` (เช่น `max`, `team`) อย่าเดาว่าบัญชีเป็นของใคร ห้ามคัดลอก `email`/`orgId` ออกไปที่อื่น
- **บัญชีเดียวรันหลายตัวพร้อมกันได้** (ทดสอบ 4 ตัว/บัญชี ขณะ session หลักก็ใช้บัญชีเดียวกัน) เงื่อนไข: ใส่ `--no-session-persistence` ทุก call · โควตาใช้ร่วมกันทั้งบัญชี

# 3. เลือกโมเดลและระดับความคิดตามความยาก

**โมเดล Claude** (ใช้ alias): `opus` (ค่าเริ่มต้น) → `claude-opus-5-5` · `sonnet` → `claude-sonnet-5-5` · `fable` → `claude-fable-5-1` · `haiku` → `claude-haiku-5-5` (ตรวจบน 2.1.302 — อัปเกรด CLI แล้วให้ดู `modelUsage` ใหม่) เติม `[1m]` เพื่อ context 1M

**ระดับความยาก → effort** ใช้ตารางเดียวกันทั้งสองฝั่ง ใส่ `"difficulty": N` ใน job ของ swarm แล้วสคริปต์เลือก effort ให้ (ถ้าใส่ `"effort"` ตรง ๆ จะใช้ค่านั้นแทน):

| difficulty | ลักษณะงาน | Claude (yolo) | Codex (cyolo) |
|---|---|---|---|
| 1 | ดึงข้อมูล จัดรูปแบบ คำนวณด้วยเชลล์ probe/ทดสอบ pipeline · **สร้างภาพ** | `haiku` / `low` | `low` |
| 2 | สรุป ถาม-ตอบทั่วไป แก้โค้ดจุดเดียว | `sonnet` / `medium` | `medium` (ค่าเริ่มต้น cyolo) |
| 3 | แก้โค้ดหลายไฟล์ debug วิเคราะห์ เขียนเอกสารยาว | `opus` / `high` | `high` |
| 4 | reasoning ซับซ้อน อัลกอริทึม คณิตที่มีคำตอบตายตัว | `opus` / `xhigh` | `xhigh` |
| 5 | ยากสุด ต้องถูกแน่นอน พิสูจน์ แข่งขัน | `opus` / `max` | `max` |
| 6 | งานใหญ่หลายขั้นที่ควรแตกงานย่อยเอง | `opus` / `max` (Claude ไม่มี ultra) | `ultra` (รุ่นที่รองรับ; ไม่รองรับ → ลดเป็น `max` อัตโนมัติ) |

**เมื่อ yolo ส่งงานให้ cyolo** ให้ประเมินความยากของงานนั้นแล้วใส่ `difficulty` เสมอ (หรือ `-c model_reasoning_effort=` ตามตารางเมื่อเรียกตรงด้วย `cx`) อย่าใช้ค่าเดียวกับทุกงาน — งานง่ายจะช้าและเปลืองโดยไม่จำเป็น งานยากจะได้คำตอบผิด

- **งานภาพใช้ difficulty 1 (`low`)**: ทดสอบภาพซับซ้อน 8 เงื่อนไข × 6 ระดับ ได้ครบ 8/8 ทุกระดับ แต่ระดับสูงช้ากว่าถึง ~40% (โมเดลภาพเป็นตัววาด effort มีผลแค่การวางแผน) — ภาพจะถูกต้องเพราะ **prompt แจกแจงทุกเงื่อนไขเป็นข้อ ๆ** ถ้าเนื้อหาภาพต้องคำนวณ/ค้นคว้า ให้แยกเป็น job ก่อน (difficulty ตามงานนั้น) แล้วค่อยใส่ผลลง prompt ภาพ
- ฝั่ง cyolo สคริปต์อ่าน `models_cache.json` ของบัญชีนั้นเพื่อรู้ว่ารุ่นรองรับระดับไหน ระดับที่ได้จริงอยู่ใน `summary.json` (`effort`, `effort_from`)
- effort ที่ระบุตรง ๆ แต่รุ่นไม่รองรับ → job ล้มก่อนรัน (CLI เองจะ fallback เงียบ ๆ หรือ HTTP 400) · effort สะกดผิด → swarm ปฏิเสธ
- ระดับสูง = ช้าและเปลืองขึ้นมาก ใช้เท่าที่งานต้องการ ผลวัดจริงอยู่ใน [9](#9-ผลทดสอบ)
- เลือก difficulty ตามงาน ไม่ใช่ตามความสำคัญ: งานง่ายที่สำคัญยังเป็นระดับ 1–2 แต่ให้ parent ตรวจผลซ้ำ

# 4. เรียกงานเดียว

```bash
cl <N> -p --model <model> --effort <effort> --strict-mcp-config --output-format json --no-session-persistence "<prompt>" < /dev/null
```

- `cd` ไปโฟลเดอร์งานก่อน (agent เขียนไฟล์ลง cwd) · `--strict-mcp-config` ตัด connector claude.ai ออก (เร็วขึ้น) ถอดเฉพาะงานที่ต้องใช้ Gmail/Drive/Docs
- อ่าน JSON: `result`, `is_error`, `total_cost_usd` (list price ไม่ใช่ยอดจ่ายจริง), `duration_ms`, `modelUsage.<id>`
- ค่าที่ต้อง parse แน่นอน: `--json-schema '{"type":"object","properties":{"answer":{"type":"integer"}},"required":["answer"]}'` แล้วอ่าน `structured_output`
- **gotcha**: flag variadic (`--allowedTools`, `--disallowedTools`, `--tools`, `--add-dir`, `--mcp-config`, `--file`, `--betas`) กลืน prompt ถ้าวางก่อน → วาง prompt ก่อน flag พวกนี้
- `--max-budget-usd` ใช้เมื่อผู้ใช้กำหนดวงเงินเท่านั้น · `--bare` ใช้ไม่ได้ (ไม่อ่าน OAuth)
- ก่อนรัน แจ้งบัญชี/model/effort · หลังรัน สรุปผล ไฟล์ที่เปลี่ยน รุ่นที่ใช้จริง และ cost

# 5. Multi-agent หลายตัวพร้อมกัน (swarm)

```bash
python3 "$SW" run jobs.json --accounts yolo1,yolo2,cyolo1 --per-account 4 --out swarm-out
```

`jobs.json` = list ของ job:

```json
[
  {"id": "sum1", "account": "yolo",  "difficulty": 1, "model": "haiku", "prompt": "คำนวณผลรวมในไฟล์ /abs/p1.txt ด้วยคำสั่งเชลล์ ตอบตัวเลขล้วน"},
  {"id": "plan", "account": "any",   "difficulty": 3, "prompt": "..."},
  {"id": "algo", "account": "cyolo", "difficulty": 6, "prompt": "..."},
  {"id": "pick", "account": "yolo2", "schema": {"type":"object","properties":{"answer":{"type":"integer"}},"required":["answer"]}, "prompt": "..."},
  {"id": "logo", "image": "out/logo.png", "difficulty": 1, "prompt": "โลโก้แมวสีส้ม มินิมอล"}
]
```

| ฟิลด์ | ความหมาย |
|---|---|
| `prompt` | งาน (ต้องมี) |
| `id` | ชื่อไฟล์ผล (default `job1`…) |
| `account` | `yolo2`/`cyolo1` = บัญชีนั้น · `yolo`/`cyolo` = ฝั่งนั้น บัญชีที่ว่างสุด · `any` (default) = ทุกบัญชีใน `--accounts` |
| `difficulty` | 1–6 → effort ตามตารางหัวข้อ 3 |
| `model`, `effort` | ระบุตรง ๆ (default yolo `opus`/`medium`, cyolo `gpt-6.1-sol`/`medium`) |
| `image` | path ภาพ PNG → **ไป cyolo เสมอ** (ระบุ `yolo*` จะถูกปฏิเสธ) ตรวจว่าเป็น PNG จริง |
| `schema` | JSON schema (yolo เท่านั้น) ผลเป็น object |
| `cwd`, `timeout` | โฟลเดอร์ทำงานของ agent, วินาที (default `--timeout 900`) |

swarm ทำให้เอง: เช็คล็อกอินทุกบัญชีก่อน (ข้ามบัญชีที่ใช้ไม่ได้ ปฏิเสธ job ที่ไม่มีบัญชีรองรับ) · จำกัด `--per-account` (default 4) และ `--max` รวม (default 12) · ใส่ `--no-session-persistence` (yolo) / `--ephemeral` (cyolo) · ตรวจ `is_error` / `turn.failed` / คำตอบว่าง / PNG · kill เมื่อ timeout · เขียน `swarm-out/summary.json` (+ ไฟล์ดิบต่อ job) · exit 1 ถ้ามี job ล้ม · `--json` พิมพ์ summary บรรทัดเดียว

กฎที่ทำให้เร็วและถูก (วัดจริง):

1. **ส่ง path ของข้อมูล + สั่งให้ใช้เชลล์คำนวณ** อย่ายัดข้อมูลใน prompt (ยัดข้อมูล/ไม่สั่งเครื่องมือ ช้าถึง 4 เท่าและเคยตอบผิด)
2. ไม่ให้ worker เขียนไฟล์ผลเอง อ่านจาก `result`/`structured_output` ใน summary
3. งานแก้โค้ดที่อาจชนกัน แยก `cwd`/worktree ต่อ job
4. งานสั้นจำนวนมาก yolo `haiku` ~6s/job, cyolo ~12–16s/job · ภาพ ~60–80s/ภาพที่ `low` — งานภาพมักเป็นคอขวด ใส่ไว้ต้น `jobs.json` หรือแยกรอบ
5. orchestrator ซ้อน (worker สั่ง `yoloN`/`cyoloN` ต่อ) ทำได้ทั้งสองทิศ แต่ parent ยังต้องตรวจซ้ำ

# 6. ส่งค่าต่อกัน (relay)

```bash
val() { cl "$1" -p --model "$2" --effort "$3" --strict-mcp-config --output-format json --no-session-persistence "$4" </dev/null \
  | python3 -c "import json,sys;d=json.load(sys.stdin);sys.exit(1) if d.get('is_error') else print(str(d['result']).strip())"; }
V1=$(val 1 haiku low "ตอบตัวเลขล้วน: 7*6") || exit 1
V2=$(val 2 sonnet medium "ค่าที่ได้คือ $V1 จงบวก 100 ตอบตัวเลขล้วน") || exit 1
```

- สั่งให้ตอบค่าล้วน (หรือใช้ `--json-schema`) ตรวจทุก hop กับเฉลยอิสระ · hop ล้ม → หยุดสายและรายงาน
- ส่งค่าด้วย argument ที่ quote ถูกหรือไฟล์ ห้าม `eval` ห้ามรันผลลัพธ์เป็น shell
- hop ฝั่ง Codex: ใช้ `cx` + อ่านไฟล์ `-o` ตามสกิล [cyolo](../cyolo/SKILL.md) เลือก effort ตามตารางหัวข้อ 3

# 7. โควตา

```bash
for n in 1 2; do ( cl $n auth status --json </dev/null >/dev/null 2>&1 || { echo "yolo$n ไม่ได้ล็อกอิน"; exit; }
  cl $n -p --strict-mcp-config "/usage" </dev/null 2>&1 | grep '^Current' | sed "s/^/yolo$n | /" ) & done; wait
```

- ไม่เสียโทเคน ได้ `Current session` (5 ชม.), `Current week (all models)`, `Current week (<model>)` เป็น **% ที่ใช้ไปแล้ว** แต่ละบัญชีรีเซ็ตไม่ตรงกัน
- ใช้โควตาเลือกบัญชีเฉพาะเมื่อผู้ใช้มอบหมาย ห้ามเปลี่ยนบัญชีที่ผู้ใช้ระบุ · ก่อนงาน difficulty 4–6 ควรเช็คแล้วรายงานตัวเลข
- โควตา Codex ดูสกิล [cyolo](../cyolo/SKILL.md)

# 8. ย้ายไปเครื่องอื่น

คัดลอก `yolo/SKILL.md` และ `cyolo/SKILL.md` (ไฟล์เดียวต่อสกิล) ไปโฟลเดอร์ skills ของเครื่องปลายทาง ต้องมี `claude` (+ `codex`, `node` ถ้าใช้ cyolo) และ `python3` ≥ 3.8 — ไม่ต้องลง package เพิ่ม

ลำดับที่ swarm หาโฟลเดอร์บัญชี (หยุดที่อันแรกที่เจอ):

1. `AI_CLAUDE_ROOT` / `AI_CODEX_ROOT` = โฟลเดอร์ที่มี `yoloN` / `cyoloN` อยู่ข้างในตรง ๆ (สองฝั่งอยู่คนละที่ได้ ชื่อโฟลเดอร์อะไรก็ได้)
2. `AI_ACCOUNTS_BASE` หรือ `python3 "$SW" --base DIR ...` = โฟลเดอร์ที่มี `.Claude/yoloN` และ `.Codex/cyoloN`
3. launcher `yoloN`/`cyoloN` บน PATH (ถ้าไม่ได้ตั้ง 1–2)
4. `BASE_PATH` ใน `config.sh` (`$AI_ACCOUNTS_CONFIG` ถ้าตั้ง ไม่งั้น `/opt/ai-accounts/config.sh`, `~/.config/ai-accounts/config.sh`)
5. `CLAUDE_CONFIG_DIR` / `CODEX_HOME` ของ session ปัจจุบัน
6. `SWARM_SKILL` → `~/ai-accounts` → `$PWD` และโฟลเดอร์แม่

```bash
export AI_ACCOUNTS_BASE=/data/me/ai-accounts                                # แบบรวม
export AI_CLAUDE_ROOT=/home/me/claude-profiles AI_CODEX_ROOT=/srv/codex     # หรือแบบแยก
python3 "$SW" where yolo1 cyolo1 && python3 "$SW" status yolo1 cyolo1
```

# 9. ผลทดสอบ

2026-10-17 · Claude Code 2.1.302 · codex-cli 0.163.0 · บัญชีทดสอบ yolo1 (`max`), yolo2 (`team`), cyolo1/cyolo2 (ChatGPT)

| การทดสอบ | ผล |
|---|---|
| หลายตัวต่อบัญชี: yolo1 ×4 + yolo2 ×4 + cyolo1 ×4 พร้อมกัน | ถูก 12/12 · `.claude.json` ไม่เสีย |
| 12 job: `--per-account 1` vs `4` | 141s → 48s (2.9×) ถูก 12/12 |
| cyolo `--ephemeral` | 42s → 12s ต่อ call (3.5×) |
| swarm 15 job (12 คำนวณ + schema + ภาพ 2) | 15/15 · 61.6s |
| ให้ yolo2 อ่านสกิลแล้วรัน swarm เองทั้งหมด | 4/4 ถูก · 14.2s |
| เครื่องไม่มี launcher / `config.sh` / path คนละที่ (6 วิธีหา) | หาเจอถูกทุกวิธี · รันจริงแบบ root แยก 2/2 |
| ค่าเริ่มต้น cyolo `gpt-6.1-sol`/`medium` (คำนวณ 2 + ภาพ 1) | 3/3 · ภาพ 57s |
| effort cyolo low→ultra โจทย์คิดล้วน (นับ a²+b² ≤ 1000 = 330) | ถูกทุกระดับ · low 20s · medium–ultra 48–66s |
| effort cyolo low→ultra ภาพซับซ้อน 8 เงื่อนไข × 12 ภาพ | 8/8 ทุกภาพ · low–high 65–79s, xhigh–ultra 76–111s → effort ไม่ทำให้ภาพดีขึ้น |
| `difficulty` → effort (Claude ไม่มี ultra → max, luna ไม่มี ultra → max, effort ผิด → ล้มก่อนรัน) | ถูกทุกกรณี |
- alias Claude → รุ่นจริง: `opus` → `claude-opus-5-5`, `sonnet` → `claude-sonnet-5-5`, `fable` → `claude-fable-5-1`, `haiku` → `claude-haiku-5-5` (list price โจทย์สั้น `low`: haiku $0.002 · sonnet $0.040 · opus $0.081 · fable $0.236)
- ไม่ช่วยเรื่องความเร็วฝั่ง yolo: `--disable-slash-commands`, `--system-prompt` สั้น, cwd ว่าง · `--disallowedTools ...` ลด context ~1/3 แต่ wall เท่าเดิม
- effort มีผลกับงานที่ต้องคิดจริงเท่านั้น (นับเลข 1–1000 เฉลย 401: `opus/low` ผิด `opus/max` ถูก) โจทย์ง่ายถูกทุกระดับ

# 10. ความปลอดภัย

`yolo<N>` ข้าม permission ทั้งหมด ทำเฉพาะงานและไฟล์ที่ผู้ใช้อนุญาต ห้ามขยายขอบเขต ส่งข้อมูลลับ หรือเปลี่ยนแปลงภายนอกที่ไม่ได้ร้องขอ ห้ามอ่าน/ส่งต่อ `.credentials.json` · รายงานของ sub-agent เชื่อไม่ได้ทั้งหมด ไฟล์ที่มันแก้ให้อ่านและทดสอบซ้ำเอง

# สคริปต์ swarm.py

ฝังไว้ให้แตกด้วยคำสั่ง awk ในหัวข้อ 1 · สำเนาเดียวกันอยู่ในสกิล cyolo — แก้แล้วต้อง sync ทั้งสองไฟล์ให้เหมือนกัน

```python
# === swarm.py BEGIN ===
"""swarm.py — run many yoloN (Claude Code) / cyoloN (Codex) agents in parallel.

Embedded in the yolo and cyolo SKILL.md (identical copy); extract with the awk line there.
Python 3.8+ stdlib only. No hard-coded machine paths — see account_root() for the lookup
order (wrapper on PATH, AI_ACCOUNTS_BASE / AI_CLAUDE_ROOT / AI_CODEX_ROOT, config.sh,
current CLAUDE_CONFIG_DIR / CODEX_HOME, SWARM_SKILL, ~/ai-accounts, $PWD).

  swarm.py where  [ACCOUNT ...]            show which command/dir each account resolves to
  swarm.py home   ACCOUNT                  print the account dir only (CODEX_HOME / CLAUDE_CONFIG_DIR)
  swarm.py status [ACCOUNT ...]            login check, parallel, no tokens
  swarm.py run JOBS.json [options]         run jobs in parallel, verify each one
  swarm.py run - < JOBS.json               jobs from stdin

JOBS.json is a list of objects (or {"jobs": [...]}):
  id       name used for output files            (default: job1, job2 ...)
  prompt   task text                              (required)
  account  "yolo1" / "cyolo2" = that account
           "yolo" / "cyolo" / "any" = least-busy account in --accounts (default "any")
  model, effort   default: yolo opus/medium, cyolo gpt-6.1-sol/medium
  difficulty 1..6 -> effort low/medium/high/xhigh/max/ultra when "effort" is not given;
           clamped to the highest level the model supports (yolo has no ultra -> max;
           cyolo checks models_cache.json of the account). An explicit unsupported
           effort fails the job before it runs instead of silently falling back.
  image    output path (.png) -> image job; runs on cyolo only
  schema   JSON schema (yolo only) -> value comes back as structured result
  cwd      working dir for the agent              (default: current dir)
  timeout  seconds                                (default: --timeout)

Global: --base DIR (= AI_ACCOUNTS_BASE, before the subcommand)
Options: --accounts yolo1,yolo2,cyolo1  --per-account 4  --max 12  --timeout 900
         --out DIR (default ./swarm-out)  --json (print summary JSON only)
Exit code: 0 if every job verified OK, 1 otherwise.
"""
import argparse, json, os, re, shutil, signal, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor

ACCT_RE = re.compile(r"^(c?yolo)([1-9][0-9]*)$")
DEFAULTS = {"yolo": ("opus", "medium"), "cyolo": ("gpt-6.1-sol", "medium")}
EFFORTS = {"yolo": ["low", "medium", "high", "xhigh", "max"],
           "cyolo": ["low", "medium", "high", "xhigh", "max", "ultra"]}
LEVELS = ["low", "medium", "high", "xhigh", "max", "ultra"]   # difficulty 1..6
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def kind_of(acct):
    m = ACCT_RE.match(acct)
    if not m:
        raise ValueError(f"bad account name {acct!r} (expected yoloN or cyoloN)")
    return m.group(1)


def _root_from(path, kind):
    """Accounts root for `kind` ("yolo"/"cyolo") implied by a path, or None.
    Accepts .../<root>/yoloN, a base that holds .Claude/ .Codex/, or any path below either."""
    sub = ".Claude" if kind == "yolo" else ".Codex"
    p = os.path.abspath(os.path.expanduser(path))
    while True:
        if re.fullmatch(rf"{kind}[1-9][0-9]*", os.path.basename(p)) and os.path.isdir(p):
            return os.path.dirname(p)                       # .../<root>/yolo1
        if os.path.isdir(os.path.join(p, sub)) and any(
                ACCT_RE.match(d) and kind_of(d) == kind for d in os.listdir(os.path.join(p, sub))):
            return os.path.join(p, sub)                     # <base>/.Claude/yolo1
        parent = os.path.dirname(p)
        if parent == p:
            return None
        p = parent


def _config_base():
    cfgs = ([os.environ["AI_ACCOUNTS_CONFIG"]] if os.environ.get("AI_ACCOUNTS_CONFIG") else
            ["/opt/ai-accounts/config.sh", os.path.expanduser("~/.config/ai-accounts/config.sh")])
    for cfg in cfgs:
        try:
            for line in open(cfg):
                m = re.match(r'\s*BASE_PATH="?([^"#\s]+)"?', line)
                if m:
                    return m.group(1)
        except OSError:
            pass
    return None


_ROOTS = {}


def account_root(kind):
    """Folder that contains yoloN (or cyoloN) dirs on THIS machine. Order:
    1 AI_CLAUDE_ROOT / AI_CODEX_ROOT   2 AI_ACCOUNTS_BASE (or --base)   3 config.sh BASE_PATH
    4 current CLAUDE_CONFIG_DIR / CODEX_HOME   5 SWARM_SKILL (path of the SKILL.md)
    6 ~/ai-accounts, $PWD and parents."""
    if kind in _ROOTS:
        return _ROOTS[kind]
    direct = os.environ.get("AI_CLAUDE_ROOT" if kind == "yolo" else "AI_CODEX_ROOT")
    if direct:
        _ROOTS[kind] = os.path.abspath(os.path.expanduser(direct))
        return _ROOTS[kind]
    cands = [os.environ.get("AI_ACCOUNTS_BASE"), _config_base(),
             os.environ.get("CLAUDE_CONFIG_DIR"), os.environ.get("CODEX_HOME"),
             os.environ.get("SWARM_SKILL"), "~/ai-accounts", os.getcwd()]
    for c in filter(None, cands):
        r = _root_from(c, kind)
        if r:
            _ROOTS[kind] = r
            return r
    _ROOTS[kind] = None
    return None


def explicit():
    return any(os.environ.get(v) for v in ("AI_ACCOUNTS_BASE", "AI_CLAUDE_ROOT", "AI_CODEX_ROOT"))


def launcher(acct):
    """-> (cmd prefix, env, where). A yoloN/cyoloN wrapper on PATH is used as-is (it knows its
    own paths) unless the user set an explicit root; otherwise call claude/codex with the
    account dir found by account_root()."""
    kind = kind_of(acct)
    wrapper = shutil.which(acct)
    if wrapper and not explicit():
        return [acct], os.environ.copy(), f"wrapper {os.path.realpath(wrapper)}"
    root = account_root(kind)
    if not root or not os.path.isdir(os.path.join(root, acct)):
        if wrapper:
            return [acct], os.environ.copy(), f"wrapper {os.path.realpath(wrapper)}"
        raise FileNotFoundError(f"{acct}: account dir not found (root={root}); set AI_ACCOUNTS_BASE, "
                                f"{'AI_CLAUDE_ROOT' if kind == 'yolo' else 'AI_CODEX_ROOT'} or --base")
    d = os.path.join(root, acct)
    env = os.environ.copy()
    if kind == "yolo":
        env.update(IS_SANDBOX="1", CLAUDE_CONFIG_DIR=d)
        return ["claude", "--dangerously-skip-permissions"], env, d
    env["CODEX_HOME"] = d
    return ["codex", "--dangerously-bypass-approvals-and-sandbox",
            "-c", 'cli_auth_credentials_store="file"'], env, d


def logged_in(acct):
    try:
        cmd, env, _ = launcher(acct)
        if kind_of(acct) == "yolo":
            r = subprocess.run(cmd + ["auth", "status", "--json"], env=env,
                               stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=60)
            d = json.loads(r.stdout or "{}")
            return bool(d.get("loggedIn")), str(d.get("subscriptionType") or "not logged in")
        r = subprocess.run(cmd + ["login", "status"], env=env, stdin=subprocess.DEVNULL,
                           capture_output=True, text=True, timeout=60)
        txt = (r.stdout + r.stderr).strip().splitlines()
        last = txt[-1] if txt else ""
        return last.startswith("Logged in"), last or "no output"
    except Exception as e:  # missing CLI, bad profile, timeout
        return False, f"error: {e}"


def supported_efforts(acct, model):
    """Effort list for model on this account; cyolo reads <CODEX_HOME>/models_cache.json."""
    kind = kind_of(acct)
    if kind == "yolo":
        return EFFORTS["yolo"]
    root = account_root(kind)
    try:
        cache = json.load(open(os.path.join(root, acct, "models_cache.json")))
        for m in cache.get("models", []):
            if m.get("slug") == model:
                return [x.get("effort") for x in m.get("supported_reasoning_levels", [])] or EFFORTS[kind]
    except (OSError, ValueError, TypeError):
        pass
    return EFFORTS[kind]          # model or cache unknown: allow the full CLI list


def pick_effort(job, acct, model):
    """-> (effort, note). Explicit effort is validated; difficulty is clamped down."""
    ok = supported_efforts(acct, model)
    if job.get("effort"):
        if job["effort"] not in ok:
            raise ValueError(f"effort {job['effort']!r} not supported by {model} on {acct} (ok: {ok})")
        return job["effort"], ""
    if job.get("difficulty") is not None:
        want = LEVELS[int(job["difficulty"]) - 1]
        for e in reversed(LEVELS[:LEVELS.index(want) + 1]):
            if e in ok:
                return e, f"difficulty {job['difficulty']}" + ("" if e == want else f" ({want} unsupported)")
    return DEFAULTS[kind_of(acct)][1], ""


def build_cmd(job, acct, outdir):
    kind = kind_of(acct)
    model = job.get("model") or DEFAULTS[kind][0]
    effort, _ = pick_effort(job, acct, model)
    prompt = job["prompt"]
    if job.get("image"):
        prompt += (f"\n\nใช้เครื่องมือสร้างภาพ (image generation) แล้วบันทึกภาพเป็นไฟล์ PNG ที่ "
                   f"{job['image']} ตอบกลับเป็น path ของไฟล์อย่างเดียว")
    cmd, env, _ = launcher(acct)
    jid = job["id"]
    if kind == "yolo":
        cmd += ["-p", "--model", model, "--effort", effort, "--strict-mcp-config",
                "--output-format", "json", "--no-session-persistence"]
        if "schema" in job:
            cmd += ["--json-schema", json.dumps(job["schema"])]
        cmd += [prompt]
        files = {"raw": f"{outdir}/{jid}.json"}
    else:
        files = {"raw": f"{outdir}/{jid}.jsonl", "answer": f"{outdir}/{jid}.out"}
        # --ephemeral: no rollout/state write at the end of the turn -> ~42s to ~12s per call
        cmd += ["exec", "--skip-git-repo-check", "--ephemeral", "-m", model,
                "-c", f'model_reasoning_effort="{effort}"', "--json", "-o", files["answer"], prompt]
    return cmd, env, files, model, effort


def verify(kind, job, files, rc):
    """-> (ok, result, error, extra). Exit code alone is never trusted: both CLIs exit 0 on failure."""
    extra = {}
    try:
        raw = open(files["raw"], encoding="utf-8", errors="replace").read()
    except OSError:
        return False, "", f"no output (exit {rc})", extra
    if kind == "yolo":
        try:
            d = json.loads(raw)
        except ValueError:
            return False, "", f"not JSON (exit {rc}): {raw[-200:]}", extra
        extra = {"cost_usd": d.get("total_cost_usd"),
                 "model_used": next((v.get("canonicalModel") for v in (d.get("modelUsage") or {}).values()), None)}
        result = d.get("structured_output") if "schema" in job else str(d.get("result", "")).strip()
        if d.get("is_error"):
            return False, result, f"is_error: {str(d.get('result'))[:200]}", extra
        if "schema" in job and result is None:
            return False, "", "no structured_output", extra
    else:
        failed, usage = None, {}
        for line in raw.splitlines():
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if e.get("type") in ("turn.failed", "error"):
                failed = (e.get("error") or {}).get("message") or e.get("message") or "turn.failed"
            if e.get("type") == "turn.completed":
                usage = e.get("usage") or {}
        extra = {"tokens_in": usage.get("input_tokens"), "tokens_out": usage.get("output_tokens"),
                 "tokens_reasoning": usage.get("reasoning_output_tokens")}
        try:
            result = open(files["answer"], encoding="utf-8").read().strip()
        except OSError:
            result = ""
        if failed:
            return False, result, f"turn.failed: {str(failed)[:200]}", extra
        if not result:
            return False, "", "empty -o answer file", extra
    if job.get("image"):
        try:
            with open(job["image"], "rb") as f:
                if f.read(8) != PNG_MAGIC:
                    return False, result, f"{job['image']} is not a PNG", extra
            extra["image_bytes"] = os.path.getsize(job["image"])
        except OSError:
            return False, result, f"image not written: {job['image']}", extra
    return True, result, "", extra


class Pool:
    """Picks an account per job and caps concurrent jobs per account."""

    def __init__(self, accounts, per_account):
        self.load = {a: 0 for a in accounts}
        self.cap = per_account
        self.cv = threading.Condition()

    def acquire(self, want, image):
        with self.cv:
            while True:
                if ACCT_RE.match(want):
                    cands = [want]
                else:
                    cands = [a for a in self.load if want in ("any", kind_of(a))]
                if image:
                    cands = [a for a in cands if kind_of(a) == "cyolo"]
                free = [a for a in cands if self.load.get(a, 0) < self.cap]
                if free:
                    a = min(free, key=lambda x: self.load.get(x, 0))
                    self.load[a] = self.load.get(a, 0) + 1
                    return a
                self.cv.wait()

    def release(self, acct):
        with self.cv:
            self.load[acct] -= 1
            self.cv.notify_all()


def run_job(job, pool, outdir, default_timeout):
    acct = pool.acquire(job.get("account", "any"), bool(job.get("image")))
    t0 = time.time()
    rec = {"id": job["id"], "account": acct}
    try:
        cmd, env, files, model, effort = build_cmd(job, acct, outdir)
        rec.update(model=model, effort=effort)
        note = pick_effort(job, acct, model)[1]
        if note:
            rec["effort_from"] = note
        timeout = job.get("timeout") or default_timeout
        with open(files["raw"], "wb") as out, open(f"{outdir}/{job['id']}.err", "wb") as err:
            p = subprocess.Popen(cmd, env=env, cwd=job.get("cwd") or None, stdin=subprocess.DEVNULL,
                                 stdout=out, stderr=err, start_new_session=True)
            try:
                rc = p.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid, signal.SIGKILL)
                p.wait()
                rec.update(ok=False, result="", error=f"timeout after {timeout}s")
                return rec
        ok, result, error, extra = verify(kind_of(acct), job, files, rc)
        rec.update(ok=ok, result=result, error=error, **extra)
    except Exception as e:
        rec.update(ok=False, result="", error=f"{type(e).__name__}: {e}")
    finally:
        rec["secs"] = round(time.time() - t0, 1)
        pool.release(acct)
    return rec


def load_jobs(path):
    data = json.load(sys.stdin if path == "-" else open(path, encoding="utf-8"))
    jobs = data["jobs"] if isinstance(data, dict) else data
    seen = set()
    for i, j in enumerate(jobs, 1):
        if not j.get("prompt"):
            sys.exit(f"swarm: job {i} has no prompt")
        j.setdefault("id", f"job{i}")
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", j["id"]) or j["id"] in seen:
            sys.exit(f"swarm: bad or duplicate id {j['id']!r}")
        seen.add(j["id"])
        if j.get("image"):
            j["image"] = os.path.abspath(j["image"])
            if ACCT_RE.match(j.get("account", "")) and kind_of(j["account"]) == "yolo":
                sys.exit(f"swarm: job {j['id']}: image generation is cyolo-only, got {j['account']}")
        d = j.get("difficulty")
        if d is not None and (not str(d).isdigit() or not 1 <= int(d) <= 6):
            sys.exit(f"swarm: job {j['id']}: difficulty must be 1..6, got {d!r}")
        if j.get("effort") and j["effort"] not in LEVELS:
            sys.exit(f"swarm: job {j['id']}: unknown effort {j['effort']!r} (use {LEVELS})")
        if "schema" in j and kind_of_job(j) == "cyolo":
            sys.exit(f"swarm: job {j['id']}: schema is yolo-only")
    return jobs


def kind_of_job(j):
    a = j.get("account", "any")
    return kind_of(a) if ACCT_RE.match(a) else (a if a in ("yolo", "cyolo") else "any")


def cmd_where(accounts):
    for a in accounts:
        try:
            cmd, _, where = launcher(a)
            print(f"{a:8} {where}")
        except Exception as e:
            print(f"{a:8} NOT FOUND  {e}")


def cmd_home(acct):
    """Account dir even when a wrapper is used (quota, generated_images, models_cache live there)."""
    root = account_root(kind_of(acct))
    d = os.path.join(root, acct) if root else None
    if not d or not os.path.isdir(d):
        sys.exit(f"swarm: {acct}: account dir not found (root={root}); set AI_ACCOUNTS_BASE, "
                 f"{'AI_CLAUDE_ROOT' if kind_of(acct) == 'yolo' else 'AI_CODEX_ROOT'} or --base")
    print(d)


def cmd_status(accounts):
    with ThreadPoolExecutor(len(accounts)) as ex:
        for a, (ok, info) in zip(accounts, ex.map(logged_in, accounts)):
            print(f"{a:8} {'OK ' if ok else 'NO '} {info}")


def cmd_run(args):
    jobs = load_jobs(args.jobs)
    accounts = [a for a in args.accounts.split(",") if a]
    named = {j["account"] for j in jobs if ACCT_RE.match(j.get("account", ""))}
    accounts = list(dict.fromkeys(accounts + sorted(named)))
    with ThreadPoolExecutor(len(accounts)) as ex:
        status = dict(zip(accounts, ex.map(logged_in, accounts)))
    live = [a for a in accounts if status[a][0]]
    for a in accounts:
        if not status[a][0]:
            print(f"swarm: skip {a}: {status[a][1]}", file=sys.stderr)
    for j in jobs:  # refuse up front instead of hanging on an account that cannot run
        want, k = j.get("account", "any"), kind_of_job(j)
        if ACCT_RE.match(want):
            ok = want in live
        else:
            ok = any((k == "any" or kind_of(a) == k) and (not j.get("image") or kind_of(a) == "cyolo")
                     for a in live)
        if not ok:
            sys.exit(f"swarm: job {j['id']}: no logged-in account for {want!r}"
                     + (" (image needs cyolo)" if j.get("image") else ""))
    os.makedirs(args.out, exist_ok=True)
    pool = Pool(live, args.per_account)
    t0 = time.time()
    with ThreadPoolExecutor(min(args.max, len(jobs))) as ex:
        recs = list(ex.map(lambda j: run_job(j, pool, os.path.abspath(args.out), args.timeout), jobs))
    summary = {"wall_secs": round(time.time() - t0, 1), "ok": sum(r["ok"] for r in recs),
               "failed": sum(not r["ok"] for r in recs), "jobs": recs}
    with open(f"{args.out}/summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False))
    else:
        for r in recs:
            res = r["result"] if isinstance(r["result"], str) else json.dumps(r["result"], ensure_ascii=False)
            res = res.replace("\n", " ")
            print(f"{'OK  ' if r['ok'] else 'FAIL'} {r['id']:12} {r['account']:7} {r['secs']:6}s  "
                  f"{(res[:70] if r['ok'] else r['error'][:70])}")
        print(f"-- {summary['ok']}/{len(recs)} ok, wall {summary['wall_secs']}s, details {args.out}/summary.json")
    return 0 if summary["failed"] == 0 else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", help="accounts base dir (same as AI_ACCOUNTS_BASE)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("status", "where"):
        sub.add_parser(name).add_argument("accounts", nargs="*")
    sub.add_parser("home").add_argument("account")
    r = sub.add_parser("run")
    r.add_argument("jobs")
    r.add_argument("--accounts", default="yolo1,yolo2,cyolo1")
    r.add_argument("--per-account", type=int, default=4)
    r.add_argument("--max", type=int, default=12)
    r.add_argument("--timeout", type=int, default=900)
    r.add_argument("--out", default="swarm-out")
    r.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.base:
        os.environ["AI_ACCOUNTS_BASE"] = os.path.abspath(os.path.expanduser(a.base))
    if a.cmd == "home":
        cmd_home(a.account)
        return 0
    if a.cmd in ("status", "where"):
        (cmd_status if a.cmd == "status" else cmd_where)(a.accounts or ["yolo1", "yolo2", "cyolo1"])
        return 0
    return cmd_run(a)


if __name__ == "__main__":
    sys.exit(main())
# === swarm.py END ===
```
