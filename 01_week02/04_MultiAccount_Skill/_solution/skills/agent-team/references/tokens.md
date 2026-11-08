# บริหารโทเค็น โควตา และสถิติ

## ledger

ทุกครั้งที่สคริปต์ของสกิล (yolo.py, cyolo.py, team.py) เรียก `yoloN`/`cyoloN` จะต่อท้าย 1 บรรทัด JSON ใน `/workspace/.agent-team/ledger.jsonl` และใน `<run>/ledger.jsonl` ถ้าอยู่ใน run

| ฟิลด์ | ความหมาย |
|---|---|
| `ts_start`, `ts_end`, `duration_s` | เวลา |
| `run_id`, `node`, `role` | `role`: worker / lead / reviewer / candidate / judge / check |
| `account`, `cli`, `model`, `effort` (+ `model_used`, `effort_from`) | |
| `input_tokens` | input ทั้งหมดรวม cache (Claude = input + cache read + cache write · Codex = `input_tokens`) |
| `cached_input_tokens`, `cache_write_tokens` | cache read / write |
| `output_tokens`, `reasoning_tokens` | reasoning: Claude thinking tokens · Codex `reasoning_output_tokens` |
| `cost_usd` | Claude เท่านั้น ราคาตามรายการ ไม่ใช่ยอดจ่ายจริง |
| `status`, `error` | `ok` `auth` `limit` `timeout` `killed` `error` + ข้อความสั้น |
| `prompt_chars`, `result_chars` | ความยาวเท่านั้น **ไม่เก็บข้อความ prompt หรือ secret** |
| `event` | `call` (เรียกโมเดล) · `auth_status` / `login_status` / `quota` (ไม่เรียกโมเดล, 0 tokens) · `worker_pause` `worker_switch` `account_down` `lead_switch` |

`team.py stats` รวมเฉพาะ `event == "call"` → ตาราง ตามบัญชี / ตามรุ่น (`cli:model`) / ตาม run: ครั้ง สำเร็จ ล้ม input cache-read cache-write output reasoning $list เวลารวม เวลาเฉลี่ย · `--json` สำหรับตรวจด้วยสคริปต์ · `--run <id>` ใช้ ledger ของ run

## โควตา

| ฝั่ง | แหล่ง | ความสด |
|---|---|---|
| Claude | `yoloN -p "/usage"` → `Current session` / `Current week (…)` % ที่ใช้ไป | สด ณ เวลาที่เรียก (ไม่เรียกโมเดล) |
| Codex | rollout ล่าสุดใน `sessions/` → `rate_limits.primary/secondary.used_percent` | เวลาของ event ล่าสุด (งาน `--ephemeral` ไม่อัปเดต) |

เก็บไว้ใน `/workspace/.agent-team/quota.json` · scheduler อ่านใหม่เมื่อเก่ากว่า 10 นาที · บัญชีที่ไม่มีข้อมูลรายงานว่า "ไม่มีข้อมูล" และถือว่าใช้ไป 0% ในการจัดอันดับ

## ตัวจัดคิว (scheduler) ทำอะไรให้

1. **ก่อนสั่งงาน:** ตรวจความพร้อมด้วยการเรียกจริง (แคช 10 นาที), อ่านโควตาทุกบัญชีที่พร้อม, รวมโทเค็นที่แต่ละบัญชีใช้ใน run จาก ledger
2. **จัดงานให้คุ้ม** (งบลูกทีมนับเฉพาะงานจริง ไม่นับการตรวจความพร้อม): รุ่น/effort ตาม difficulty · งานที่ไม่ผูกบัญชีได้ `planned` = บัญชีที่คะแนนต่ำสุด (งานที่รัน+คิว + โควตาที่ใช้ไป/25 แล้วโทเค็นใน run) → กระจายงาน ไม่ให้บัญชีเดียวรับซ้อน
3. **สลับเชิงรุก:** โควตา ≥ `--quota-threshold` (80) หรือโทเค็น worker ใน run ≥ `--worker-token-budget` → บัญชีนั้น `paused` (หยุดรับงาน) งานที่รันอยู่จบตามปกติ งานในคิวที่ planned ไว้ย้ายไปคนอื่น (`worker_switch`)
4. **สลับเชิงรับ:** งานล้มเพราะ `limit` หรือ `auth` (ไม่เสียโทเค็น) → บัญชีนั้น `unavailable` ใน run นี้ งานกลับเข้าคิวและย้ายไปบัญชีอื่นฝั่งเดียวกัน (ไม่มีจึงข้ามฝั่งถ้าไม่ผูก CLI) · ความคืบหน้าใน `msgs/<id>__progress.md` ถูกส่งให้ผู้รับต่อ
5. **ไม่สลับเงียบ:** งานที่ระบุบัญชีเอง (`yolo2`) ไม่ย้าย → ล้มพร้อมข้อความ "ไม่ย้ายอัตโนมัติ" · ทุกการย้ายอยู่ใน `state.json` (`events`), `board.md`, ledger
6. **ภาพรวม:** `team.py status`

```
| บัญชี | บทบาท | งานที่รัน | งานในคิว | tokens ใน run | โควตาล่าสุด | สถานะ |
| yolo1 | ลูกทีม | - | - | 59288 | week (all models) 22% · week (Fable) 0% (ข้อมูล ณ 06:59) | พร้อม |
| yolo2 | ลูกทีม | - | - | 27867 | session 0% · week (all models) 2% · week (Fable) 1% (ข้อมูล ณ 06:58) | หยุดรับงาน (ใช้โทเค็นใน run นี้ 27867 ≥ งบ 1000) |
| yolo3 | - | - | - | 0 | ไม่มีข้อมูล | ใช้ไม่ได้ (ไม่ได้ล็อกอิน) |
```

สถานะ: **พร้อม** · **ใกล้หมด** (โควตา ≥ เกณฑ์−15 หรือใช้งบ ≥ 70%) · **หยุดรับงาน** · **ใช้ไม่ได้** (ไม่ได้ล็อกอิน / หมดอายุ / ล้มระหว่าง run)

## ประหยัดโทเค็น

- งานง่ายใช้ difficulty 1 (`haiku`/`low`, Codex `low`) — โจทย์ง่ายถูกทุกระดับ effort สูงแค่ช้าและแพง
- ส่งข้อมูลยาวเป็นไฟล์ (`{{file:id}}`) และสั่งให้ใช้เชลล์คำนวณ แทนการยัดลง prompt
- การเรียกแต่ละครั้งมี overhead ของ system prompt (~17–28k input ส่วนใหญ่เป็น cache) รวมงานเล็กที่เกี่ยวกันเป็นงานเดียวเมื่อทำได้
- `--worker-token-budget` กันไม่ให้ลูกทีมคนใดใช้เกินส่วน
