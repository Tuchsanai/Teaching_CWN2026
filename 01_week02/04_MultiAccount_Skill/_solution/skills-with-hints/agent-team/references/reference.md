# agent-team: รายละเอียด

## การเลือกบัญชีและคิว

- ตรวจความพร้อมด้วยการเรียกจริงก่อนเริ่ม บัญชีที่ใช้ไม่ได้ถูกข้ามพร้อมแจ้ง
- จำกัดพร้อมกัน: `--per-account 3`, `--max-total 8`, `--timeout 600` (ต่องาน) หรือคีย์เดียวกันระดับบนสุดของกราฟ
- จัดงานล่วงหน้าตามบัญชีที่ได้งานน้อยสุดและโควตาเหลือมากสุด งานภาพเริ่มก่อน
- บัญชีที่ `used_pct ≥ --quota-stop` (ค่าเริ่มต้น 80) หรือเกิน `--worker-token-budget` ถูกหยุดรับงาน งานที่กำลังรันจบตามปกติ งานในคิวย้ายทันที งบตรวจทันทีที่แต่ละงานจบ
- งานระบุบัญชีเอง (`yolo2`) ไม่ย้าย: ถ้าบัญชีใช้ไม่ได้ งานนั้นล้มพร้อมรายงาน
- `any` ข้ามฝั่งได้ · `yolo`/`cyolo` อยู่ฝั่งเดียว · งานภาพผูก Codex

## router (`account: any`)

| เงื่อนไข | ฝั่ง |
|---|---|
| `kind: image` / `task_type: image` / prompt มีคำว่าสร้างภาพ, .png | cyolo เท่านั้น |
| ระบุ `model` | ตามรุ่น |
| `task_type: code_review` / prompt ตรวจโค้ด, code review | Codex ก่อน |
| `task_type: long_doc` / prompt เอกสาร | Claude ก่อน |
| อื่น ๆ | บัญชีที่ได้งานน้อย/โควตาเหลือมาก ทั้งสองฝั่ง |

ความยาก → Claude: 1 haiku/low · 2 sonnet/medium · 3 opus/high · 4 opus/xhigh · 5–6 opus/max · Codex effort: low medium high xhigh max ultra (effort ที่รุ่นไม่รองรับถูกลดและบันทึก `effort_from`)

## failover

ย้ายเฉพาะ `quota`, `rate_limit`, `auth_expired`, `not_logged_in` ไปบัญชีอื่นในฝั่งเดียวกันก่อน (`any` ข้ามฝั่งได้) บันทึกใน `state.json` (`worker_switches`), `board.md`, ledger (`event: worker_switch`) งานที่ล้มด้วยเหตุอื่น (เสียโทเค็นแล้ว) ไม่ retry

## งานยาว

ตั้ง `"progress": true` ให้ลูกทีมเขียนความคืบหน้าลง `msgs/<บัญชี>__team.md` ผู้รับงานต่อจะได้รับ path นั้น

## human gate

`"approve": true` หยุดงานนั้นจนมีไฟล์ `approve/<node>.ok` ในโฟลเดอร์ run (`team.py approve <run> <node>`) งานอื่นรันต่อ ค่า `--approve-timeout 0` จบทันทีด้วย exit 3 แล้วค่อย `run --resume`

## run --resume

งานที่สำเร็จแล้วไม่รันซ้ำ รันเฉพาะที่ล้ม/ถูกบล็อก/รออนุมัติ แก้ค่าก่อนรันได้ด้วย `--set NODE.prompt=...`, `--set NODE.expect=text` หรือส่งกราฟใหม่ (`run g.json --resume <id>` อัปเดต prompt/expect ของงานที่ยังไม่สำเร็จ)

## lead

ผู้ควบคุมเป็นสคริปต์ ไม่ใช้โทเค็น รันหัวหน้าเป็นรอบ ๆ แต่ละรอบหัวหน้าได้ `handoff.md` + สรุปสถานะงาน และตอบ JSON สั่งงาน (`dispatch`), `merge` (รวมผลเป็นไฟล์เดียว), `finish`, `checkpoint`

- ลูกทีมรันเป็น process แยก ผลลง `out/` หัวหน้าเปลี่ยนตัวแล้วงานยังเดิน
- เชิงรุก: หลังทุกคำสั่งของหัวหน้า ถ้าเกิน `--lead-token-budget` หรือ `--quota-stop` ส่งไม้ต่อ
- เชิงรับ: เรียกล้ม (โควตา, rate limit, ล็อกอิน, timeout `--episode-timeout`) หรือตอบผิดรูปแบบ เริ่มหัวหน้าคนใหม่จาก checkpoint ล่าสุด
- ผู้สืบทอด: `--succession` หรือบัญชีพร้อมที่โควตาเหลือมาก ฝั่ง Claude ก่อน ไม่เลือก `--exclude`
- บันทึกทุกการสลับใน `state.json` (`lead_history`), `board.md`, ledger (`event: lead_switch`)
- ถ้าหัวหน้าไม่สั่ง finish ภายใน `--max-episodes` ผู้ควบคุมรวมผลเท่าที่มี และ exit 1

## ledger

แถวละ 1 การเรียก `/workspace/.agent-team/ledger.jsonl` และ `<run>/ledger.jsonl` ฟิลด์: `ts_start ts_end run_id node account cli model effort duration_s input_tokens cached_input_tokens cache_write_tokens output_tokens reasoning_tokens cost_usd status error prompt_chars result_chars` · node ขึ้นต้น `__` คือการตรวจ/โควตา/หัวหน้า · แถว `event` คือเหตุการณ์ (`worker_switch`, `lead_switch`, `account_stopped`) · Claude `input_tokens` ไม่รวม cache ส่วน Codex รวม cached
