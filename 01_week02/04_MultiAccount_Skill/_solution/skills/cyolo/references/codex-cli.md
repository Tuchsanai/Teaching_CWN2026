# Codex CLI (`cyoloN`) — รายละเอียด

ตรวจกับ codex-cli 0.167.0 ใน container `multi-account` (2026-11-08) อัปเกรดแล้วให้ตรวจ `codex exec --help` และเรียกจริงซ้ำ

## บัญชี

- บัญชีอยู่ที่ `/root/ai-accounts/.Codex/cyoloN` = `CODEX_HOME` (volume `ai-accounts`)
- `cyolo1`–`cyolo5` เป็น wrapper ตั้ง `CODEX_HOME`, `--dangerously-bypass-approvals-and-sandbox`, `-c cli_auth_credentials_store="file"` และแปลง MCP จาก `shared/mcp/mcp.json` ให้ · ไม่มี wrapper → `macore.launch()` เรียก `codex` ตรงด้วย env เดียวกัน
- `$CODEX_HOME/skills` เป็น**โฟลเดอร์จริง** มี symlink รายสกิล `../../shared/skills/<สกิล>` และ Codex เขียน `skills/.system` เอง → ห้าม symlink ทั้งโฟลเดอร์ · wrapper สร้าง symlink ของสกิลใหม่ให้ทุกครั้งที่เรียก (`link_shared_skills`) และ `install.sh` สร้างให้ทันทีหลังติดตั้ง
- ห้ามเรียก `codex` เปล่าโดยไม่กำหนด `CODEX_HOME` (จะใช้โปรไฟล์อื่น)

## เรียกงานเดียว

```bash
cyolo1 exec --skip-git-repo-check --ephemeral -m gpt-6.1-sol -c model_reasoning_effort="low" \
       --json -o /abs/answer.txt "<prompt>" < /dev/null > log.jsonl
```

- คำตอบอยู่ในไฟล์ `-o` (stdout มี banner / `Reading additional input from stdin...` ปนใน stderr)
- `--output-schema <ไฟล์>` → คำตอบใน `-o` เป็น JSON ตาม schema (ใช้ schema แบบ strict: ทุก property อยู่ใน `required` และ `additionalProperties: false`)
- `-C <dir>` หรือ `cd` ก่อน เพราะ codex เขียนไฟล์ลง cwd
- prompt ที่ขึ้นต้นด้วย `-` สคริปต์เติมช่องว่างนำหน้าให้

## stdout `--json` (JSONL)

```json
{"type":"thread.started","thread_id":"…"}
{"type":"turn.started"}
{"type":"item.completed","item":{"type":"agent_message","text":"OK"}}
{"type":"turn.completed","usage":{"input_tokens":17780,"cached_input_tokens":12288,"cache_write_input_tokens":0,"output_tokens":5,"reasoning_output_tokens":0}}
```

ล้ม: `{"type":"error","message":"Reconnecting... n/5 (…401…)"}` ซ้ำหลายครั้ง แล้ว `{"type":"turn.failed","error":{"message":"…"}}` · `input_tokens` ของ Codex รวม cached แล้ว (ตรงกับที่ ledger ใช้)

## ความพร้อมของบัญชี

| สถานะ | ตรวจอย่างไร |
|---|---|
| ไม่ได้ล็อกอิน | `cyoloN login status` พิมพ์ `Not logged in` (ดูข้อความ ไม่ใช่ exit code) |
| ล็อกอินแล้วแต่หมดอายุ | `Logged in using ChatGPT` แต่เรียกจริงได้ `turn.failed` ที่มี 401 / auth |
| พร้อม | เรียกจริง `low` "ตอบ OK" ได้ `OK` (~3–4 s) |

ผลวัด 0.167.0: บัญชีไม่ล็อกอินเรียก exec → 401 retry 5+5 ครั้ง ~15 s แล้ว `turn.failed` **exit 1** (สเปกเดิมบอก exit 0 — ไม่ว่าแบบไหน สคริปต์ไม่ใช้ exit code ตัดสิน)

## รุ่นและ effort (`$CODEX_HOME/models_cache.json`)

ฟิลด์ที่ใช้: `models[].slug`, `supported_reasoning_levels[].effort`, `default_reasoning_level`, `visibility` · อย่าพิมพ์ส่วน `identity`

cyolo1, 2026-11-08:

| slug | efforts | default | visibility |
|---|---|---|---|
| gpt-6.1-sol | low medium high xhigh max ultra | low | list |
| gpt-6-astra | low medium high xhigh max ultra | medium | list |
| gpt-6.1-terra | low medium high xhigh max ultra | low | list |
| gpt-6-sol | low medium high xhigh max ultra | medium | list |
| gpt-6-luna | low medium high xhigh max | medium | list |
| gpt-5.6-sol / gpt-5.6-terra | low … ultra | low / medium | list |
| gpt-5.6-luna | low … max | medium | list |
| gpt-reserve, codex-auto-review | low … max | medium | hide |

ระดับที่รุ่นไม่รองรับ (เช่น `ultra` กับ `gpt-6-luna`) → `cyolo.pick()` ลดเป็นระดับสูงสุดที่รองรับ แล้วคืน `effort_from` เช่น "ลดจาก ultra เป็น max" ซึ่งบันทึกใน ledger ด้วย

## โควตา

ไม่อยู่ใน stdout แต่อยู่ใน rollout ที่ไม่ใช่ ephemeral: `$CODEX_HOME/sessions/YYYY/MM/DD/rollout-*.jsonl` event `payload.type == "token_count"` → `payload.rate_limits`:

```json
{"primary":{"used_percent":1.0,"window_minutes":10080,"resets_at":1794633702},"secondary":null,
 "credits":{"has_credits":true,"balance":"…"},"plan_type":"prolite","rate_limit_reached_type":null}
```

- `used_percent` = % ที่ใช้ไปแล้ว · window อาจเป็น `null` · **รายงานเวลาของข้อมูล (timestamp ของ event) เสมอ** อย่าอ้างข้อมูลเก่าว่าสด
- งาน `--ephemeral` ไม่อัปเดตไฟล์นี้ → `cyolo.py quota --refresh` เรียกสั้น 1 ครั้งแบบไม่ ephemeral ก่อนอ่าน

## สร้างภาพ (Codex เท่านั้น)

```bash
python3 cyolo.py image -a cyolo1 --out /workspace/cat.png "แมวสีส้ม 1 ตัว พื้นหลังขาว มินิมอล"
```

- สคริปต์ใช้ effort `low` และสั่ง "สร้างภาพ (image generation) … บันทึกเป็น PNG ที่ <absolute path>" แล้วตรวจ 8 ไบต์แรก `\x89PNG\r\n\x1a\n`
- ผลวัดชุดเดิม (0.163.0): ภาพซับซ้อน 8 เงื่อนไข × effort low→ultra ได้ครบ 8/8 ทุกระดับ แต่ระดับสูงช้ากว่า ~40% (low 73–78 s, ultra 101–109 s) → effort ไม่ทำให้ภาพดีขึ้น · สิ่งที่ทำให้ถูกคือ prompt ที่แจกแจงทุกเงื่อนไขเป็นข้อ
- ต้นฉบับอยู่ที่ `$CODEX_HOME/generated_images/<thread>/` แล้ว agent คัดลอกมาที่ path ที่สั่ง

## ผลวัดจริง (2026-11-08, 0.167.0)

| การทดสอบ | ผล |
|---|---|
| `gpt-6.1-sol`/`low` "ตอบ OK" cyolo1, cyolo2 พร้อมกัน | 3–4 s · in 17,780 (cached 12,288) · out 5 |
| `--ephemeral` เทียบไม่ ephemeral (ชุดเดิม) | 12 s vs 42 s ต่อครั้ง (3.5×) |
| บัญชีไม่ล็อกอิน (cyolo3) | 401 retry ~15 s → `turn.failed`, exit 1 |

## ความปลอดภัย

`cyoloN` ข้าม approval และ sandbox ทั้งหมด ทำเฉพาะงานและไฟล์ที่ผู้ใช้อนุญาต ห้ามแตะ `auth.json` · ledger ไม่เก็บข้อความ prompt
