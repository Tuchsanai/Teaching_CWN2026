# Codex CLI (cyoloN) — รายละเอียด

วัดกับ codex-cli 0.167.0 ใน container `multi-account`

## wrapper

`/usr/local/bin/cyoloN` ตั้ง `CODEX_HOME=$BASE/.Codex/cyoloN`, `--dangerously-bypass-approvals-and-sandbox`, `-c cli_auth_credentials_store="file"` และสร้าง symlink รายสกิลจาก `shared/skills` ทุกครั้ง (`link_shared_skills`; Codex เขียน `skills/.system` เอง จึงห้าม symlink ทั้งโฟลเดอร์) · N>5 `cyolo.py` เรียก `codex` ตรงด้วย env/flag ชุดเดียวกัน

## stdout ของ `--json` (JSONL)

```json
{"type":"thread.started","thread_id":"…"}
{"type":"turn.started"}
{"type":"item.completed","item":{"type":"agent_message","text":"OK"}}
{"type":"turn.completed","usage":{"input_tokens":17780,"cached_input_tokens":12288,"cache_write_input_tokens":0,"output_tokens":5,"reasoning_output_tokens":0}}
```

ล้ม: `{"type":"error","message":"… 401 Unauthorized …"}` ซ้ำ แล้ว `{"type":"turn.failed","error":{"message":"…"}}` · stderr `Reading additional input from stdin...` เป็นเรื่องปกติ

| ฟิลด์ ledger | มาจาก |
|---|---|
| `input_tokens` | `usage.input_tokens` (รวม cached แล้ว) |
| `cached_input_tokens` | `usage.cached_input_tokens` |
| `cache_write_tokens` | `usage.cache_write_input_tokens` |
| `output_tokens` / `reasoning_tokens` | `usage.output_tokens` / `usage.reasoning_output_tokens` |
| `cost_usd` | ไม่มี (null) |

## รุ่นและ effort

`$CODEX_HOME/models_cache.json` → `models[].slug`, `supported_reasoning_levels[].effort`, `default_reasoning_level`, `visibility` (`hide` = ไม่ใช้), `priority` · ตัวอย่างที่พบ: `gpt-6.1-sol` low…ultra · `gpt-6-luna` สูงสุด max · ห้ามพิมพ์ส่วน `identity`

`ultra` ส่งผ่าน `-c model_reasoning_effort=ultra` ให้ CLI จัดการ (เป็นโหมดฝั่ง client) เฉพาะรุ่นที่ประกาศว่ารองรับ · รุ่นที่ไม่รองรับ `cyolo.py` ลดเป็นระดับสูงสุดที่รองรับและใส่ `effort_note`

## โควตา

ไม่อยู่ใน stdout แต่อยู่ใน rollout ที่ไม่ใช่ ephemeral: `$CODEX_HOME/sessions/YYYY/MM/DD/rollout-*.jsonl` event ที่ `payload.type == "token_count"` → `payload.rate_limits.{primary, secondary}.{used_percent, window_minutes, resets_at}` (% ที่ใช้ไปแล้ว; window 10080 = 7 วัน; secondary อาจเป็น null) · `cyolo.py quota` รายงาน timestamp ของ event เสมอ · `--refresh` เรียก "ตอบ OK" แบบไม่ ephemeral 1 ครั้ง (ledger event `quota_refresh`) แล้วอ่านใหม่

## สร้างภาพ

prompt ที่ `cyolo.py image` ส่ง: "สร้างภาพ (image generation) ตามเงื่อนไขทุกข้อ: … บันทึกเป็นไฟล์ PNG ที่ <absolute path> แล้วตอบ path อย่างเดียว" · ไฟล์ต้นฉบับอยู่ที่ `$CODEX_HOME/generated_images/<thread>/` แล้ว agent คัดลอกมาที่ path · effort `low` (สูงกว่าไม่ทำให้ภาพดีขึ้นแต่ช้ากว่า ~40%) · ถ้าเนื้อหาภาพต้องคำนวณก่อน แยกเป็นงานก่อนหน้า · ตรวจ 8 ไบต์แรก = `89 50 4E 47 0D 0A 1A 0A`

## ใช้ใน Python

```python
import sys; sys.path.insert(0, "/root/ai-accounts/.Codex/shared/skills/cyolo/scripts")
import cyolo
r = cyolo.call("cyolo1", "ตอบ OK", difficulty=1)
img = cyolo.image("cyolo1", "วงกลมสีแดง 1 วง", "/workspace/x.png")   # img["is_png"]
```
