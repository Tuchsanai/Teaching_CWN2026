# ไฟล์ ledger และสถิติ

## โฟลเดอร์

```
/workspace/.agent-team/
  ledger.jsonl        สถิติทุกการเรียกผ่านสกิล (ทุก run + ask เดี่ยว + check)
  accounts.json       ผลตรวจความพร้อมล่าสุด (ใช้ซ้ำภายใน 15 นาที; run --recheck บังคับตรวจใหม่)
  quota.json          โควตาล่าสุดที่อ่านได้ พร้อมเวลาของข้อมูล
  <run_id>/
    graph.json  state.json  board.md  handoff.md  ledger.jsonl
    msgs/<จาก>__<ถึง>.md     ส่งต่องาน (งาน→งาน, หัวหน้า→งาน) และ <บัญชี>__<งาน>.progress.md
    out/<งาน>.md             ผล (ไม่มีบรรทัด BOARD:) · <งาน>.png ภาพ · <งาน>.best.md · <งาน>.review.md
    approvals/<งาน>          ไฟล์อนุมัติ
    tmp/                     ไฟล์ชั่วคราว (schema, tasks.json ของหัวหน้า)
```

JupyterLab อาจสร้าง `.ipynb_checkpoints` — สคริปต์ข้ามโฟลเดอร์ที่ขึ้นต้นด้วย `.` และโฟลเดอร์ที่ไม่มี `state.json`

## แถว ledger

```json
{"ts_start": "…", "ts_end": "…", "run_id": "…", "node": "a", "account": "yolo1", "cli": "claude",
 "model": "haiku", "effort": "low", "duration_s": 3.2, "input_tokens": 27684, "cached_input_tokens": 13920,
 "cache_write_tokens": 13762, "output_tokens": 3, "reasoning_tokens": 0, "cost_usd": 0.0029,
 "status": "ok", "error": null, "prompt_chars": 37, "result_chars": 2, "event": "call"}
```

`event`: `call` งาน · `check` ตรวจความพร้อม · `lead` รอบหัวหน้า (node `_lead.eN`) · `quota_refresh` · `worker_switch` / `lead_switch` (ไม่มี cli; มี `from`, เหตุผลใน `error`) · Claude `input_tokens` = input + cache read + cache creation · Codex `input_tokens` รวม cached แล้ว · `cost_usd` = ราคาตามรายการของ Claude (Codex = null) · ไม่มีข้อความ prompt/secret

## stats

`team.py stats [--run <id>] [--event call,lead] [--since 2026-11-08T10:00] [--json]` → ตารางตามบัญชี / รุ่น / run / ชนิดการเรียก: ครั้ง · สำเร็จ · ล้ม · input · cached · cache write · output · reasoning · ค่าใช้จ่ายตามรายการ · เวลารวม · เวลาเฉลี่ย (ไม่นับแถว switch) — ผลรวมคำนวณจาก ledger ตรง ๆ

ตรวจผลรวมด้วยตัวเอง:
```
python3 -c "import json;r=[json.loads(l) for l in open('/workspace/.agent-team/<run>/ledger.jsonl')];r=[x for x in r if x.get('cli')];print(len(r),sum(x['input_tokens'] for x in r),sum(x['output_tokens'] for x in r))"
```
