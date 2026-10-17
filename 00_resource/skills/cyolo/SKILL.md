---
name: cyolo
description: เรียก OpenAI Codex CLI บัญชี cyolo1–cyoloN (ค่าเริ่มต้น gpt-6.1-sol/medium) เป็นฝั่งเดียวที่ **สร้างภาพ (image generation)** ได้ รัน multi-agent หลายตัวพร้อมกันข้ามบัญชี หลายตัวต่อบัญชี ผสมกับ Claude (yoloN) ด้วยสคริปต์ swarm ที่ฝังในไฟล์นี้ เลือกระดับความคิด low→ultra ตามความยากของงานอัตโนมัติ ตรวจโควตาฟรี ส่งค่าข้ามบัญชี/ข้าม CLI ย้ายเครื่องได้ (ไม่มี path ตายตัว) ใช้เมื่อผู้ใช้ขอ "เรียก cyoloN", "ใช้ codex อีก account", "ให้ gpt ทำ...", "สร้างภาพ/gen รูป", "แบ่งงานหลาย agent", "เช็คโควตา codex" หรือเทียบคำตอบข้ามบัญชี/ข้ามค่าย
argument-hint: "[-a <N>] [-m <model>] [-e <effort>] <prompt>"
allowed-tools: Bash(cyolo* *), Bash(codex *), Bash(env CODEX_HOME=* codex *), Bash(python3 */swarm.py *), Bash(awk *)
---

# cyolo — Codex หลายบัญชี + multi-agent + สร้างภาพ

| ต้องการ | ทำอย่างไร |
|---|---|
| เริ่มใช้ (ครั้งเดียวต่อ session) | [1. เตรียม](#1-เตรียม-ครั้งเดียวต่อ-session) |
| งานเดียว | `cx <N> exec --skip-git-repo-check --ephemeral -m <model> -c model_reasoning_effort="<e>" --json -o <out> "<prompt>" < /dev/null` ([4](#4-เรียกงานเดียว)) |
| สร้างภาพ | **มีแค่ cyolo ที่ทำได้** — [5](#5-สร้างภาพ-cyolo-เท่านั้น) |
| หลายงานพร้อมกัน หลายบัญชี หลายตัวต่อบัญชี ผสม Claude | `python3 "$SW" run jobs.json` ([6](#6-multi-agent-หลายตัวพร้อมกัน-swarm)) |
| เลือกระดับความคิดตามความยาก | `"difficulty": 1–6` ใน job ([3](#3-เลือกโมเดลและระดับความคิดตามความยาก)) |
| หา `CODEX_HOME` บนเครื่องนี้ | `python3 "$SW" home cyolo<N>` |
| ดูโควตา (ฟรี) | [8. โควตา](#8-โควตา) |
| ย้ายไปเครื่องอื่น | [9](#9-ย้ายไปเครื่องอื่น) |

กฎเหล็ก: ทุก call ต้องมี `exec` และ `< /dev/null` · คำตอบอ่านจากไฟล์ `-o` เท่านั้น · **exit code 0 แม้ล้มเหลว** (ตรวจ `turn.failed` + `-o` ไม่ว่าง / swarm ตรวจให้) · ใส่ `--ephemeral` ทุกงาน ยกเว้นรีเฟรชโควตา · ค่าที่ผู้ใช้ระบุชนะค่าเริ่มต้นเสมอ · ห้าม retry อัตโนมัติหลัง error

# 1. เตรียม (ครั้งเดียวต่อ session)

ตำแหน่ง `CODEX_HOME` ต่างกันได้ทุกเครื่อง จึงไม่เขียน path ตายตัว — สคริปต์ `swarm.py` (ฝังท้ายไฟล์นี้) หาให้:

```bash
export SWARM_SKILL=<path ของ SKILL.md นี้>     # base directory ที่แสดงตอนโหลดสกิล + /SKILL.md
SW=${TMPDIR:-/tmp}/swarm.py
awk '/^# === swarm.py BEGIN/{f=1} f; /^# === swarm.py END/{exit}' "$SWARM_SKILL" > "$SW"
# cx <N> ... = cyolo<N> ... ถ้ามี launcher; ไม่งั้น (หรือเมื่อตั้ง AI_ACCOUNTS_BASE/AI_CODEX_ROOT) เรียก codex ด้วย CODEX_HOME ที่หาเจอ
cx() { local a="cyolo$1"; shift
  if command -v "$a" >/dev/null && [ -z "$AI_ACCOUNTS_BASE$AI_CODEX_ROOT" ]; then "$a" "$@"
  else local h; h=$(python3 "$SW" home "$a") || return 1
    env CODEX_HOME="$h" codex --dangerously-bypass-approvals-and-sandbox -c 'cli_auth_credentials_store="file"' "$@"; fi; }
python3 "$SW" where  cyolo1 cyolo2     # แต่ละบัญชีชี้ไปที่ไหน (ไม่เสียโทเคน)
python3 "$SW" status cyolo1 cyolo2     # ล็อกอินหรือยัง (ไม่เสียโทเคน)
```

ถ้าต้องเรียก Claude ด้วย ใช้ฟังก์ชัน `cl` จากสกิล [yolo](../yolo/SKILL.md)

# 2. บัญชี

- ไม่ระบุใช้ `cyolo1` · N ต้องเป็น `[1-9][0-9]*` · ไม่มีคำสั่ง `cyolo` เปล่า · อย่าเรียก `codex` เปล่าโดยไม่กำหนด `CODEX_HOME` (จะใช้โปรไฟล์คนละชุด)
- อ่าน `$ARGUMENTS`: `-a <N>`, `-m <model>`, `-e <effort>` ที่เหลือคือ prompt · ไม่มี prompt → ถาม · `-a` ขัดกับข้อความ → ถาม
- `CODEX_HOME=$(python3 "$SW" home cyolo<N>)` ใช้ของบัญชีที่เลือกตลอดงาน (`models_cache.json`, `sessions/`, `generated_images/`) ห้ามอ่าน/ส่งต่อ `auth.json`
- สถานะล็อกอินอ่านจากข้อความ `Logged in using ChatGPT` ไม่ใช่ exit code · ไม่ล็อกอิน → ให้ผู้ใช้รัน `! cyolo<N> login` เอง (ไม่มี launcher: `! env CODEX_HOME=<ผลของ home> codex login`) **ห้ามสลับบัญชีเอง** (บัญชีไม่ล็อกอินพ่น `401` + retry แต่ exit 0)
- launcher (ถ้ามี) รองรับ `cyolo1`–`cyolo5`; N > 5 หรือเครื่องไม่มี launcher ใช้ `cx <N>` · ไม่สร้างโปรไฟล์/symlink ใหม่เอง
- **บัญชีเดียวรันหลายตัวพร้อมกันได้** (ทดสอบ 6 ตัว/บัญชี) โควตาใช้ร่วมกันทั้งบัญชี

# 3. เลือกโมเดลและระดับความคิดตามความยาก

ค่าเริ่มต้น: `-m gpt-6.1-sol` + `model_reasoning_effort="medium"` — ใส่ทั้งสองค่าเสมอ อย่าพึ่ง `config.toml`

| difficulty | ลักษณะงาน | effort (Codex) | Claude (yolo) เทียบเท่า |
|---|---|---|---|
| 1 | ดึงข้อมูล จัดรูปแบบ คำนวณด้วยเชลล์ probe · **สร้างภาพ** | `low` | `haiku`/`low` |
| 2 | สรุป ถาม-ตอบทั่วไป แก้โค้ดจุดเดียว (ค่าเริ่มต้น) | `medium` | `sonnet`/`medium` |
| 3 | แก้โค้ดหลายไฟล์ debug วิเคราะห์ | `high` | `opus`/`high` |
| 4 | reasoning ซับซ้อน อัลกอริทึม คณิตที่มีคำตอบตายตัว | `xhigh` | `opus`/`xhigh` |
| 5 | ยากสุด ต้องถูกแน่นอน | `max` | `opus`/`max` |
| 6 | งานใหญ่หลายขั้นที่ควรแตกงานย่อยเอง (auto delegation) | `ultra` | `opus`/`max` |

- ใส่ `"difficulty": N` ใน job ของ swarm แล้วสคริปต์เลือก effort ให้ โดยอ่าน `models_cache.json` ของบัญชีนั้น — รุ่นไม่รองรับระดับที่ขอ → ลดลงเป็นระดับสูงสุดที่รองรับ (เช่น `gpt-6-luna` ไม่มี `ultra` → `max`) ผลจริงอยู่ใน `summary.json` (`effort`, `effort_from`)
- effort ที่ระบุตรง ๆ แต่รุ่นไม่รองรับ → job ล้มก่อนรัน (CLI เองอาจ HTTP 400 `unsupported_value` หรือ fallback เงียบ) · `ultra` เป็นโหมดฝั่ง client อย่านำไปใช้เป็นค่า API `reasoning.effort`
- ระดับสูงช้าลงชัดเจน (โจทย์คิดล้วน: `low` 20s, `medium`–`ultra` 48–66s) ใช้เท่าที่งานต้องการ · codex ไม่รู้ effort ของตัวเอง ยืนยันจากฝั่งคำสั่งเท่านั้น

รุ่นที่ใช้ได้ (`models_cache.json` ของ cyolo1, client 0.163.0, 2026-10-17 — บัญชีอื่น/รุ่นใหม่ให้อ่านจาก `$(python3 "$SW" home cyolo<N>)/models_cache.json`):

| Model | effort ที่รองรับ | default ของรุ่น |
|---|---|---|
| `gpt-6.1-sol` (ค่าเริ่มต้นของสกิล) | low medium high xhigh max ultra | low |
| `gpt-6-astra` | low medium high xhigh max ultra | medium |
| `gpt-6-sol` | low medium high xhigh max ultra | medium |
| `gpt-6-luna` | low medium high xhigh max | medium |
| `gpt-5.6-sol` | low medium high xhigh max ultra | low |
| `gpt-5.6-terra` | low medium high xhigh max ultra | medium |
| `gpt-5.6-luna` | low medium high xhigh max | medium |

# 4. เรียกงานเดียว

```bash
cx <N> exec --skip-git-repo-check --ephemeral -m gpt-6.1-sol -c model_reasoning_effort="medium" --json -o answer.txt "<prompt>" < /dev/null > log.jsonl
```

- `cd` ไปโฟลเดอร์งานก่อน (codex เขียนไฟล์ลง cwd) · บรรทัด `Reading additional input from stdin...` เป็นเรื่องปกติ
- **`--ephemeral` เร็วขึ้น 3.5×** (42s → 12s ต่อ call) เพราะไม่ต้องเขียน rollout ตอนจบ
- คำตอบอยู่ใน `-o` (stdout มี banner ปน · ห้าม `-o /dev/stdout` คำตอบซ้ำสองรอบ)
- `--json`: สำเร็จมี `turn.completed.usage.{input_tokens,cached_input_tokens,output_tokens,reasoning_output_tokens}` · ล้มเหลวมี `turn.failed.error.message`
- ไม่ต้องการ bypass: `env CODEX_HOME="$(python3 "$SW" home cyolo<N>)" codex exec --sandbox read-only` (หรือ `workspace-write`)
- ก่อนรัน แจ้งบัญชี/model/effort · หลังรัน สรุปผล ไฟล์ที่เปลี่ยน tokens · รายงานของ codex เชื่อไม่ได้ทั้งหมด ตรวจไฟล์/รันทดสอบซ้ำเอง

# 5. สร้างภาพ (cyolo เท่านั้น)

Codex มี feature `image_generation` (stable) + system skill `imagegen` · Claude ไม่มีเครื่องมือนี้ งานภาพทุกงานส่งมาฝั่งนี้

```bash
cx 1 exec --skip-git-repo-check --ephemeral -m gpt-6.1-sol -c model_reasoning_effort="low" --json -o img.out \
  "สร้างภาพ (image generation) <รายละเอียด> แล้วบันทึกเป็นไฟล์ PNG ที่ $PWD/cat.png ตอบ path อย่างเดียว" < /dev/null > img.jsonl
head -c 8 cat.png | od -An -c     # ต้องขึ้นต้นด้วย 211 P N G
```

ผลทดสอบ effort กับภาพซับซ้อน (8 เงื่อนไข: ข้อความบนกระดาน, ลำดับสีหุ่นยนต์ 3 ตัว, ป้ายเลข, นาฬิกา 3:15, แมว 2 ตัว, หน้าต่าง 4 บาน, กระบองเพชร, ไม่มีคน × 6 ระดับ × 2 ภาพ):

| effort | เวลา/ภาพ | ครบเงื่อนไข |
|---|---|---|
| low | 73–78s | 8/8, 8/8 |
| medium | 67–79s | 8/8, 8/8 |
| high | 65–76s | 8/8, 8/8 |
| xhigh | 80–95s | 8/8, 8/8 |
| max | 76–111s | 8/8, 8/8 |
| ultra | 101–109s | 8/8, 8/8 |

- **effort ไม่ทำให้ภาพดีขึ้น** — ภาพวาดโดยโมเดลภาพแยกต่างหาก effort มีผลแค่การวางแผนของ agent และทำให้ช้าลงถึง ~40% → ใช้ `low` (difficulty 1) กับงานภาพ
- สิ่งที่ทำให้ภาพซับซ้อนออกมาถูก คือ **prompt ที่แจกแจงทุกเงื่อนไขเป็นข้อ ๆ** (จำนวน สี ตำแหน่ง ข้อความที่ต้องอยู่ในภาพ)
- ถ้าเนื้อหาภาพต้องคำนวณหรือค้นคว้าก่อน (ตัวเลข ข้อมูล ข้อเท็จจริง) ให้ทำเป็น job แยก (เลือก difficulty ตามความยากของงานนั้น) ตรวจผล แล้วค่อยใส่ค่าลงใน prompt ภาพ
- ระบุ **path แบบ absolute** เสมอ ต้นฉบับอยู่ที่ `$(python3 "$SW" home cyolo<N>)/generated_images/<thread_id>/*.png` แล้ว agent `cp` มาให้
- ภาพหลายภาพรันขนานผ่าน swarm (ทดสอบ 12 ภาพบน 2 บัญชี 6 ตัว/บัญชี wall 111s) · ตรวจว่าเป็น PNG จริง (swarm ทำให้) และเปิดดูภาพก่อนส่งมอบเมื่อทำได้

# 6. Multi-agent หลายตัวพร้อมกัน (swarm)

```bash
python3 "$SW" run jobs.json --accounts cyolo1,cyolo2 --per-account 4 --out swarm-out          # Codex ล้วน
python3 "$SW" run jobs.json --accounts yolo1,yolo2,cyolo1 --per-account 4 --out swarm-out     # ผสม Claude + Codex
```

```json
[
  {"id": "a1",   "account": "cyolo", "difficulty": 1, "prompt": "คำนวณผลรวมในไฟล์ /abs/p1.txt ด้วยคำสั่งเชลล์ ตอบตัวเลขล้วน"},
  {"id": "algo", "account": "cyolo", "difficulty": 5, "prompt": "..."},
  {"id": "a2",   "account": "any",   "prompt": "..."},
  {"id": "pic1", "image": "out/pic1.png", "difficulty": 1, "prompt": "ภาพหุ่นยนต์รดน้ำต้นไม้ สีพาสเทล"}
]
```

| ฟิลด์ | ความหมาย |
|---|---|
| `prompt` | งาน (ต้องมี) · `id` ชื่อไฟล์ผล (default `job1`…) |
| `account` | `cyolo1`/`yolo2` = บัญชีนั้น · `cyolo`/`yolo` = ฝั่งนั้น บัญชีที่ว่างสุด · `any` (default) = ทุกบัญชีใน `--accounts` |
| `difficulty` | 1–6 → effort ตามตารางหัวข้อ 3 |
| `model`, `effort` | ระบุตรง ๆ (default cyolo `gpt-6.1-sol`/`medium`, yolo `opus`/`medium`) |
| `image` | path PNG → ไป cyolo เสมอ ตรวจว่าเป็น PNG จริง |
| `schema` | yolo เท่านั้น |
| `cwd`, `timeout` | โฟลเดอร์ทำงาน, วินาที (default `--timeout 900`) |

- เครื่องที่มีแต่ Codex: ใส่เฉพาะ `cyoloN` ใน `--accounts` (default `yolo1,yolo2,cyolo1` — บัญชีที่หาไม่เจอ/ไม่ล็อกอินจะถูกข้ามพร้อมแจ้ง)
- swarm ใส่ `--ephemeral` + `--json` + `-o` ต่อ job เอง ตรวจ `turn.failed` / `-o` ว่าง / PNG · จำกัด `--per-account` (default 4) / `--max` (default 12) · kill เมื่อ timeout · เขียน `swarm-out/summary.json` (`tokens_in/out/reasoning`, `secs`, `effort`) · exit 1 ถ้ามี job ล้ม
- ส่ง path ข้อมูล + สั่งให้ใช้เชลล์คำนวณ อย่ายัดข้อมูลใน prompt · ไม่ให้ worker เขียนไฟล์ผลเอง · แยก `cwd`/worktree เมื่อแก้โค้ดชนกันได้ · parent รวมและตรวจด้วยสคริปต์อิสระเสมอ · ยอด tokens อาจไม่รวม sub-agent ของ `ultra`
- งานสั้นจำนวนมาก yolo `haiku` เร็วกว่า (~6s เทียบ ~12–16s) — ใช้ cyolo เมื่อต้องการ GPT, ต้องสร้างภาพ หรือเทียบคำตอบข้ามค่าย

# 7. ส่งค่าต่อกัน (relay) รวมข้าม CLI

- อ่านค่าจาก `-o` หลังตรวจว่าไม่มี `turn.failed` สั่งรูปแบบที่ hop ถัดไปต้องการ (ตัวเลขล้วน/JSON) ตรวจก่อนส่งต่อ · hop ล้ม → หยุดสายและรายงาน
- ส่งค่าด้วย argument ที่ quote ถูกหรือไฟล์ ห้าม `eval` ห้ามรันผลลัพธ์เป็น shell
- hop ฝั่ง Claude ใช้ `cl` จากสกิล [yolo](../yolo/SKILL.md) · ตัวอย่าง Codex `7*6` → Claude `+100` → Codex `*3` = `42 → 142 → 426` ตรวจทุก hop ด้วยการคำนวณอิสระ

# 8. โควตา

โควตาอยู่ใน rollout `<CODEX_HOME>/sessions/YYYY/MM/DD/*.jsonl` (event `token_count` → `payload.rate_limits`) ไม่อยู่ใน stdout `--json` — อ่านค่าล่าสุดได้ฟรี:

```bash
for n in 1 2; do python3 - "cyolo$n" "$(python3 "$SW" home cyolo$n)" <<'EOF'
import glob, json, os, sys, datetime as dt
acct, home = sys.argv[1], sys.argv[2]
for f in sorted(glob.glob(home + "/sessions/*/*/*/*.jsonl"), key=os.path.getmtime, reverse=True):
    last = None
    for line in open(f, errors="replace"):
        try: e = json.loads(line)
        except ValueError: continue
        p = e.get("payload") or {}
        if p.get("type") == "token_count" and p.get("rate_limits"): last = (e.get("timestamp"), p["rate_limits"])
    if last:
        ts, rl = last; out = [f"{acct} | ข้อมูล ณ {ts}"]
        for w in ("primary", "secondary"):
            x = rl.get(w)
            if x: out.append(f"{w} {x['used_percent']}% used / {x['window_minutes']} นาที รีเซ็ต "
                             + dt.datetime.fromtimestamp(x["resets_at"]).astimezone().isoformat(timespec="minutes"))
        c = rl.get("credits") or {}
        if c.get("has_credits"): out.append(f"credits {c.get('balance')}")
        print(" · ".join(out)); break
else: print(f"{acct} | ไม่มีข้อมูลโควตาใน sessions/")
EOF
done
```

- รายงาน timestamp ด้วยเสมอ อย่าอ้างข้อมูลเก่าว่าเป็นสถานะสด · `used_percent` = % ที่ใช้ไปแล้ว (window อาจเป็น `null`) · `credits.balance` คือเครดิตเติมเงิน แยกจาก subscription
- รีเฟรช = ส่ง prompt สั้นหนึ่งครั้ง (แจ้งผู้ใช้ว่าใช้โทเคน) `gpt-6-luna`/`low` ได้ **ห้ามใส่ `--ephemeral`** แล้วรันสคริปต์ด้านบนอีกครั้ง
- ใช้โควตาเลือกบัญชีเฉพาะเมื่อผู้ใช้มอบหมาย ห้ามเปลี่ยนบัญชีที่ผู้ใช้ระบุ ไม่ต้อง probe ทุกบัญชีก่อนงาน `max`/`ultra` อัตโนมัติ

# 9. ย้ายไปเครื่องอื่น

คัดลอก `cyolo/SKILL.md` (และ `yolo/SKILL.md` ถ้าใช้ Claude) ไปโฟลเดอร์ skills ของเครื่องปลายทาง ต้องมี `codex` + `node` (+ `claude`) และ `python3` ≥ 3.8 — ไม่ต้องลง package เพิ่ม

ลำดับที่ swarm หาโฟลเดอร์บัญชี (หยุดที่อันแรกที่เจอ):

1. `AI_CODEX_ROOT` / `AI_CLAUDE_ROOT` = โฟลเดอร์ที่มี `cyoloN` / `yoloN` อยู่ข้างในตรง ๆ (ชื่ออะไรก็ได้ คนละที่ได้)
2. `AI_ACCOUNTS_BASE` หรือ `python3 "$SW" --base DIR ...` = โฟลเดอร์ที่มี `.Codex/cyoloN` และ `.Claude/yoloN`
3. launcher `cyoloN`/`yoloN` บน PATH (ถ้าไม่ได้ตั้ง 1–2)
4. `BASE_PATH` ใน `config.sh` (`$AI_ACCOUNTS_CONFIG` ถ้าตั้ง ไม่งั้น `/opt/ai-accounts/config.sh`, `~/.config/ai-accounts/config.sh`)
5. `CODEX_HOME` / `CLAUDE_CONFIG_DIR` ของ session ปัจจุบัน
6. `SWARM_SKILL` → `~/ai-accounts` → `$PWD` และโฟลเดอร์แม่

```bash
export AI_CODEX_ROOT=/srv/codex-homes          # หรือ export AI_ACCOUNTS_BASE=/data/me/ai-accounts
python3 "$SW" where cyolo1 && python3 "$SW" status cyolo1 && python3 "$SW" home cyolo1
```

# 10. ผลทดสอบ

2026-10-17 · codex-cli 0.163.0 · Claude Code 2.1.302 · บัญชีทดสอบ cyolo1, cyolo2 (ChatGPT), yolo1 (`max`), yolo2 (`team`)

| การทดสอบ | ผล |
|---|---|
| หลายตัวต่อบัญชี: cyolo1 ×4 + yolo1 ×4 + yolo2 ×4 พร้อมกัน | ถูก 12/12 |
| `--ephemeral` | 42s → 12s ต่อ call (เลี่ยง launcher / ปิด feature ไม่ช่วย) |
| 12 job: `--per-account 1` vs `4` | 141s → 48s (2.9×) ถูก 12/12 |
| swarm 15 job ผสม (12 คำนวณ + schema + ภาพ 2) | 15/15 · 61.6s |
| ค่าเริ่มต้น `gpt-6.1-sol`/`medium` (คำนวณ 2 + ภาพ 1) | 3/3 · ภาพ 57s |
| effort low→ultra โจทย์คิดล้วน (นับ a²+b² ≤ 1000 = 330) | ถูกทุกระดับ · low 20s · medium–ultra 48–66s |
| effort low→ultra ภาพซับซ้อน 12 ภาพ | 8/8 ทุกภาพ · effort ไม่มีผลต่อคุณภาพ (หัวข้อ 5) |
| `difficulty` → effort (luna/ultra → max, ระบุ effort ผิด → ล้มก่อนรัน) | ถูกทุกกรณี |
| เครื่องไม่มี launcher / `config.sh` / path คนละที่ | 6 วิธีหาเจอถูก · `cx` + โควตาใช้ได้ |

- โจทย์ยากพอจะเห็นผลของ effort (รุ่นเก่า `gpt-5.6-sol` นับ a²+b² ≤ 500: `low` ผิด, `max` ถูก) · โจทย์ง่ายถูกทุกระดับ จึงอย่าใช้ระดับสูงเกินจำเป็น

# 11. ความปลอดภัย

`cyolo<N>` / `cx` ข้าม approval และ sandbox ทั้งหมด ทำเฉพาะงานและไฟล์ที่ผู้ใช้อนุญาต ห้ามขยายขอบเขต ส่งข้อมูลลับ หรือเปลี่ยนแปลงภายนอกที่ไม่ได้ร้องขอ ห้ามอ่าน/ส่งต่อ `auth.json`

# สคริปต์ swarm.py

ฝังไว้ให้แตกด้วยคำสั่ง awk ในหัวข้อ 1 · สำเนาเดียวกันอยู่ในสกิล yolo — แก้แล้วต้อง sync ทั้งสองไฟล์ให้เหมือนกัน

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
