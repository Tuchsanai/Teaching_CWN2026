# ผลการทดลอง Workflow

ผลจากไฟล์จริง ณ 2026-09-16T15:47:22+07:00 ตรวจใหม่ด้วย [สคริปต์ตรวจ](../tests/check_experiments.py) และเก็บรายละเอียดใน [JSON](../tests/experiments-results.json)

```bash
# รันจากรากโปรเจกต์ ไม่ต้องส่ง argument
python3 tests/check_experiments.py
```

สคริปต์อ่านทุกชุดที่มี log.jsonl ตรวจผลฉบับปัจจุบัน แล้วเขียน JSON และหน้านี้ใหม่ ใช้ Python, markdown-it-py, Playwright/Chromium และ Mermaid JS ในเครื่องตาม tools/render_md.py; ไม่เรียก AI และไม่เขียนทับหลักฐานดิบ หากเครื่องมือหรือหลักฐานขาดให้ผล ‘ไม่มีข้อมูล’ ส่วน FAIL คือพบว่าไม่ตรงกฎตรวจ

## วิธีทดลองซ้ำ

ใช้สำเนาโฟลเดอร์ทดลองใหม่และคง prompt ภาษาไทยเดิม เลือกคำสั่งตัวอย่างตาม engine; ตัวอย่างต่อไปนี้รันจากโฟลเดอร์สำเนานั้น ใช้เฉพาะ cyolo1 หรือ yolo1 และเลือกเพียงคำสั่งเดียวต่อการรัน

```bash
# Codex: เฟสแรก
date -u +%FT%TZ > .start
printf "%s\n" "codex cyolo1" > .engine
cyolo1 exec --json -m gpt-6-astra -c model_reasoning_effort="high" -o response.md "$(cat prompt.md)" < /dev/null > log.jsonl 2> .stderr.txt
printf "exit=%s\n" "$?" > .exit
date -u +%FT%TZ > .end
```

```bash
# Claude: เฟสแรก; รันบัญชีนี้ทีละ process
date -u +%FT%TZ > .start
printf "%s\n" "claude yolo1" > .engine
yolo1 -p --model fable --effort high --strict-mcp-config --output-format stream-json --verbose "$(cat prompt.md)" < /dev/null > log.jsonl 2> .stderr.txt
printf "exit=%s\n" "$?" > .exit
date -u +%FT%TZ > .end
python3 - <<'PY'
import json
from pathlib import Path
rows = [json.loads(line) for line in Path("log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
result = next((r for r in reversed(rows) if r.get("type") == "result"), {})
Path("response.md").write_text(result.get("result", ""), encoding="utf-8")
PY
```

ชื่อโมเดลในตัวอย่างเป็นค่าคำสั่งของ harness ไม่ใช้แทนชื่อโมเดลที่ขาดใน log ผลทดลองจริง สำหรับเฟส 2 ให้อ่าน thread_id/session_id ของเฟสแรกเป็น SESSION แล้ว resume session เดิมหลังได้รับผลเฟสแรก เก็บ .start2/.end2/.exit2 และ .stderr2.txt แยกจากเฟสแรก

```bash
# เลือกตาม engine; SESSION คือรหัสจาก log ของการรันซ้ำของตนเอง
cyolo1 exec --json -m gpt-6-astra -c model_reasoning_effort="high" -o response-phase2.md resume "$SESSION" "$(cat prompt-phase2.md)" < /dev/null > log-phase2.jsonl 2> .stderr2.txt
yolo1 -p --resume "$SESSION" --model fable --effort high --strict-mcp-config --output-format stream-json --verbose "$(cat prompt-phase2.md)" < /dev/null > log-phase2.jsonl 2> .stderr2.txt
```

สำหรับ Claude ให้แยก result เป็น response-phase2.md ด้วยวิธีเดียวกับเฟสแรก จำกัด yolo1 ทีละ 1 process และ cyolo1 ไม่เกิน 2 jobs พร้อมกัน เมื่อโควตาหมดหยุดรอ ไม่สลับบัญชี หลังทดลองใช้ tools/events_from_log.py และ tools/shoot.py ตาม --help กับสำเนาชุดใหม่เพื่อเก็บ events และภาพ

## โครงไฟล์ต่อชุด

แต่ละชุดอยู่ที่ `<โจทย์>/<workflow>/`: prompt.md คือคำสั่งที่คงเดิม; log.jsonl คือ event ดิบ; response.md คือคำตอบ; trace.md คือบันทึกกระบวนการ; events.md คือสรุป event; output.html หรือ output.md คือผลงาน; shoot.json และภาพ PNG คือหลักฐาน capture ส่วน .engine, .start/.end บอก engine และเวลารัน เฟส 2 ใช้ prompt-phase2.md, log-phase2.jsonl, response-phase2.md และ .start2/.end2

## ตารางเปรียบเทียบ 3 × 3

โทเคนและเวลาคือผลรวมของเฟสที่มีข้อมูล (เวลารันแต่ละเฟส ไม่รวมเวลาพักระหว่างเฟส) Codex total = input + output โดย cached เป็นส่วนหนึ่งของ input; Claude input = input_tokens + cache_creation_input_tokens และ total = input + cached + output จาก result.usage; ไม่บวก modelUsage ซ้ำ จึงไม่ใช่ยอดบิลทั้งบัญชี ค่า reasoning เป็นส่วนของ output และไม่บวกซ้ำ

รอบนับจาก trace: Loop นับเลข Iteration ไม่ซ้ำ, Graph นับ node ID ไม่ซ้ำ (การรัน node เดิมซ้ำไม่เพิ่มจำนวน), Dynamic นับ Plan version ไม่ซ้ำ จำนวนผ่าน/ทั้งหมดรวมเกณฑ์ไม่มีข้อมูลไว้ในตัวหาร จึงไม่ใช่คะแนนรับรองคุณภาพ

| Workflow | โจทย์ 1: จองห้องประชุม | โจทย์ 2: เบิกค่าใช้จ่าย | โจทย์ 3: ย้ายระบบนัดหมาย |
|---|---|---|---|
| Loop | [prompt.md](1_meeting_room/loop/prompt.md) · [trace.md](1_meeting_room/loop/trace.md) · [events.md](1_meeting_room/loop/events.md) · [output.html](1_meeting_room/loop/output.html) · [response.md](1_meeting_room/loop/response.md)<br>codex / ไม่มีข้อมูล<br>iterations: 1; token total: 255,365; เวลา: 217.0 s<br>ผ่าน 4/4; ไม่มีข้อมูล 0 | [prompt.md](2_expense_claim/loop/prompt.md) · [trace.md](2_expense_claim/loop/trace.md) · [events.md](2_expense_claim/loop/events.md) · [output.md](2_expense_claim/loop/output.md) · [response.md](2_expense_claim/loop/response.md)<br>codex / ไม่มีข้อมูล<br>iterations: 1; token total: 188,831; เวลา: 302.0 s<br>ผ่าน 5/6; ไม่มีข้อมูล 0 | [prompt.md](3_clinic_migration/loop/prompt.md) · [trace.md](3_clinic_migration/loop/trace.md) · [events.md](3_clinic_migration/loop/events.md) · [output.md](3_clinic_migration/loop/output.md) · [response.md](3_clinic_migration/loop/response.md)<br>codex / ไม่มีข้อมูล<br>iterations: 3; token total: 679,002; เวลา: 548.0 s<br>ผ่าน 4/6; ไม่มีข้อมูล 0 |
| Graph | [prompt.md](1_meeting_room/graph/prompt.md) · [trace.md](1_meeting_room/graph/trace.md) · [events.md](1_meeting_room/graph/events.md) · [output.html](1_meeting_room/graph/output.html) · [response.md](1_meeting_room/graph/response.md)<br>codex / ไม่มีข้อมูล<br>nodes: 6; token total: 598,889; เวลา: 392.0 s<br>ผ่าน 4/4; ไม่มีข้อมูล 0 | [prompt.md](2_expense_claim/graph/prompt.md) · [trace.md](2_expense_claim/graph/trace.md) · [events.md](2_expense_claim/graph/events.md) · [output.md](2_expense_claim/graph/output.md) · [response.md](2_expense_claim/graph/response.md)<br>codex / ไม่มีข้อมูล<br>nodes: 6; token total: 852,825; เวลา: 521.0 s<br>ผ่าน 5/6; ไม่มีข้อมูล 0 | [prompt.md](3_clinic_migration/graph/prompt.md) · [trace.md](3_clinic_migration/graph/trace.md) · [events.md](3_clinic_migration/graph/events.md) · [output.md](3_clinic_migration/graph/output.md) · [response.md](3_clinic_migration/graph/response.md)<br>codex / ไม่มีข้อมูล<br>nodes: 6; token total: 2,461,294; เวลา: 1,179.0 s<br>ผ่าน 5/6; ไม่มีข้อมูล 0 |
| Dynamic | [prompt.md](1_meeting_room/dynamic/prompt.md) · [trace.md](1_meeting_room/dynamic/trace.md) · [events.md](1_meeting_room/dynamic/events.md) · [output.html](1_meeting_room/dynamic/output.html) · [response.md](1_meeting_room/dynamic/response.md)<br>codex / ไม่มีข้อมูล<br>plan_versions: 1; token total: 383,635; เวลา: 400.0 s<br>ผ่าน 4/4; ไม่มีข้อมูล 0 | [prompt.md](2_expense_claim/dynamic/prompt.md) · [trace.md](2_expense_claim/dynamic/trace.md) · [events.md](2_expense_claim/dynamic/events.md) · [output.md](2_expense_claim/dynamic/output.md) · [response.md](2_expense_claim/dynamic/response.md)<br>codex / ไม่มีข้อมูล<br>plan_versions: 1; token total: 233,379; เวลา: 444.0 s<br>ผ่าน 5/6; ไม่มีข้อมูล 0 | [prompt.md](3_clinic_migration/dynamic/prompt.md) · [trace.md](3_clinic_migration/dynamic/trace.md) · [events.md](3_clinic_migration/dynamic/events.md) · [output.md](3_clinic_migration/dynamic/output.md) · [response.md](3_clinic_migration/dynamic/response.md)<br>codex / ไม่มีข้อมูล<br>plan_versions: 3; token total: 1,591,469; เวลา: 1,105.0 s<br>ผ่าน 6/6; ไม่มีข้อมูล 0 |
| loop_claude (ชุดเสริม) | [prompt.md](1_meeting_room/loop_claude/prompt.md) · [trace.md](1_meeting_room/loop_claude/trace.md) · [events.md](1_meeting_room/loop_claude/events.md) · [output.html](1_meeting_room/loop_claude/output.html) · [response.md](1_meeting_room/loop_claude/response.md)<br>claude / claude-fable-5-1<br>iterations: 1; token total: 128,963; เวลา: 145.0 s<br>ผ่าน 2/4; ไม่มีข้อมูล 0 | ไม่มีข้อมูล | ไม่มีข้อมูล |

## เวลาและโทเคนรายเฟส

| ชุด / เฟส | เริ่ม (+07:00) | จบ (+07:00) | วินาที | input | cached | output | total |
|---|---|---|---:|---:|---:|---:|---:|
| 1_meeting_room/dynamic / phase1 | 2026-09-16T14:50:53+07:00 | 2026-09-16T14:57:33+07:00 | 400.0 | 365,708 | 328,320 | 17,927 | 383,635 |
| 1_meeting_room/graph / phase1 | 2026-09-16T14:41:13+07:00 | 2026-09-16T14:47:45+07:00 | 392.0 | 590,224 | 528,000 | 8,665 | 598,889 |
| 1_meeting_room/loop / phase1 | 2026-09-16T14:20:38+07:00 | 2026-09-16T14:24:15+07:00 | 217.0 | 244,784 | 212,096 | 10,581 | 255,365 |
| 1_meeting_room/loop_claude / phase1 | 2026-09-16T15:28:45+07:00 | 2026-09-16T15:31:10+07:00 | 145.0 | 25,501 | 91,253 | 12,209 | 128,963 |
| 2_expense_claim/dynamic / phase1 | 2026-09-16T14:59:24+07:00 | 2026-09-16T15:06:48+07:00 | 444.0 | 212,713 | 175,232 | 20,666 | 233,379 |
| 2_expense_claim/graph / phase1 | 2026-09-16T14:41:29+07:00 | 2026-09-16T14:50:10+07:00 | 521.0 | 832,671 | 771,840 | 20,154 | 852,825 |
| 2_expense_claim/loop / phase1 | 2026-09-16T14:26:30+07:00 | 2026-09-16T14:31:32+07:00 | 302.0 | 174,129 | 152,576 | 14,702 | 188,831 |
| 3_clinic_migration/dynamic / phase1 | 2026-09-16T15:08:13+07:00 | 2026-09-16T15:17:28+07:00 | 555.0 | 347,232 | 305,280 | 24,817 | 372,049 |
| 3_clinic_migration/dynamic / phase2 | 2026-09-16T15:17:28+07:00 | 2026-09-16T15:26:38+07:00 | 550.0 | 1,168,976 | 1,085,568 | 50,444 | 1,219,420 |
| 3_clinic_migration/graph / phase1 | 2026-09-16T14:50:36+07:00 | 2026-09-16T14:58:48+07:00 | 492.0 | 589,489 | 552,448 | 16,693 | 606,182 |
| 3_clinic_migration/graph / phase2 | 2026-09-16T14:58:48+07:00 | 2026-09-16T15:10:15+07:00 | 687.0 | 1,819,842 | 1,749,888 | 35,270 | 1,855,112 |
| 3_clinic_migration/loop / phase1 | 2026-09-16T14:28:04+07:00 | 2026-09-16T14:32:15+07:00 | 251.0 | 150,108 | 121,728 | 12,446 | 162,554 |
| 3_clinic_migration/loop / phase2 | 2026-09-16T14:32:15+07:00 | 2026-09-16T14:37:12+07:00 | 297.0 | 490,035 | 433,280 | 26,413 | 516,448 |

## เกณฑ์และข้อจำกัด

F1/F3 ของ loop_claude เป็น FAIL เพราะปุ่ม “ยกเลิก” ปรากฏหลังมีการจองเท่านั้น (state-dependent) เป็นข้อจำกัดของ heuristic ที่สำรวจจากสถานะเริ่มต้น ไม่ใช่ข้อสรุปว่าเว็บไม่มีฟีเจอร์ยกเลิก; คงผลตรวจเดิมไว้

PASS/FAIL ใน heuristic คือผลกฎข้อความที่ระบุ ไม่ยืนยันความหมายทั้งหมด F1/F3 ตรวจ keyword ที่มองเห็น (รวมป้าย nav) และสำรวจ candidate ที่ระบุในสคริปต์ จึงไม่พิสูจน์ว่าจองหรือยกเลิกสำเร็จจริง แต่ละเส้นทางเริ่มด้วย browser context ใหม่; F2 ตรวจ error ขณะเปิดหน้าและรายงาน error ระหว่างสำรวจแยกต่างหาก; F4 ตรวจแหล่งอ้างอิงภายนอกและคำขอที่ browser พบโดยปิด network

E1 ตรวจ keyword ใน Traceability โดยไม่ได้พิสูจน์ mapping ทุก FR/BR; E3 ตรวจบริบท 100 ตัวอักษรรอบจำนวนเงิน; E4 เทียบชื่อ literal ของ participant/entity กับ ERD จึงอาจ FAIL กับชื่อระบบหรือบทบาทที่ไม่ใช่ Entity ต้องอ่าน diagram ประกอบ ส่วนเกณฑ์ M ตรวจรูปแบบเอกสาร/marker ตามกติกาเท่านั้น; M4 รองรับหัวข้อภาษาไทยและ Plan vN ด้วย ไม่เปลี่ยน v1.1 ให้เป็น v2. Mermaid ตรวจด้วย render_markdown จาก tools/render_md.py จริงโดยไม่เขียน output.render.html

### 1_meeting_room

| Workflow | เกณฑ์ | วิธี | ผล | Evidence |
|---|---|---|---|---|
| dynamic | F1_features_present — พบข้อความสื่อ 5 feature ใน DOM หน้าแรกหรือ nav ชั้นแรก | heuristic | PASS | output.html: DOM file://, 1280×800, nav ชั้นแรก 8 ตัว; ห้อง: 0 คลิก: หน้าแรก; เวลาว่าง: 0 คลิก: หน้าแรก; จอง: 0 คลิก: หน้าแรก; ยกเลิก: 1 คลิก: หน้าแรก → การจองของฉัน; สถานะ: 1 คลิก: หน้าแรก → การจองของฉัน |
| dynamic | F2_opens_no_console_error — เปิด file:// โดยไม่มี console error/pageerror | script | PASS | output.html: Playwright เปิด file:// ใน context ใหม่; console/pageerror หน้าแรก=0; error รวมระหว่างสำรวจ=0; ปิด network |
| dynamic | F3_two_clicks — เข้าถึง keyword ของทุก feature ภายใน 2 คลิก | heuristic | PASS | output.html: DOM file://, 1280×800, nav ชั้นแรก 8 ตัว; ห้อง: 0 คลิก: หน้าแรก; เวลาว่าง: 0 คลิก: หน้าแรก; จอง: 0 คลิก: หน้าแรก; ยกเลิก: 1 คลิก: หน้าแรก → การจองของฉัน; สถานะ: 1 คลิก: หน้าแรก → การจองของฉัน |
| dynamic | F4_no_cdn — ไม่มีการอ้างทรัพยากรเครือข่ายภายนอก | script | PASS | output.html: สแกน source ทั้งไฟล์; ไม่พบ src/href/CSS URL/import/fetch ภายนอกใน source |
| graph | F1_features_present — พบข้อความสื่อ 5 feature ใน DOM หน้าแรกหรือ nav ชั้นแรก | heuristic | PASS | output.html: DOM file://, 1280×800, nav ชั้นแรก 11 ตัว; ห้อง: 0 คลิก: หน้าแรก; เวลาว่าง: 0 คลิก: หน้าแรก; จอง: 0 คลิก: หน้าแรก; ยกเลิก: 1 คลิก: หน้าแรก → จองห้อง; สถานะ: 1 คลิก: หน้าแรก → จองห้อง; เส้นทางที่ตรวจไม่สำเร็จ 1, จำกัด candidate=False |
| graph | F2_opens_no_console_error — เปิด file:// โดยไม่มี console error/pageerror | script | PASS | output.html: Playwright เปิด file:// ใน context ใหม่; console/pageerror หน้าแรก=0; error รวมระหว่างสำรวจ=0; ปิด network |
| graph | F3_two_clicks — เข้าถึง keyword ของทุก feature ภายใน 2 คลิก | heuristic | PASS | output.html: DOM file://, 1280×800, nav ชั้นแรก 11 ตัว; ห้อง: 0 คลิก: หน้าแรก; เวลาว่าง: 0 คลิก: หน้าแรก; จอง: 0 คลิก: หน้าแรก; ยกเลิก: 1 คลิก: หน้าแรก → จองห้อง; สถานะ: 1 คลิก: หน้าแรก → จองห้อง; เส้นทางที่ตรวจไม่สำเร็จ 1, จำกัด candidate=False |
| graph | F4_no_cdn — ไม่มีการอ้างทรัพยากรเครือข่ายภายนอก | script | PASS | output.html: สแกน source ทั้งไฟล์; ไม่พบ src/href/CSS URL/import/fetch ภายนอกใน source |
| loop | F1_features_present — พบข้อความสื่อ 5 feature ใน DOM หน้าแรกหรือ nav ชั้นแรก | heuristic | PASS | output.html: DOM file://, 1280×800, nav ชั้นแรก 14 ตัว; ห้อง: 0 คลิก: หน้าแรก; เวลาว่าง: 0 คลิก: หน้าแรก; จอง: 0 คลิก: หน้าแรก; ยกเลิก: 0 คลิก: หน้าแรก; สถานะ: 0 คลิก: หน้าแรก |
| loop | F2_opens_no_console_error — เปิด file:// โดยไม่มี console error/pageerror | script | PASS | output.html: Playwright เปิด file:// ใน context ใหม่; console/pageerror หน้าแรก=0; error รวมระหว่างสำรวจ=0; ปิด network |
| loop | F3_two_clicks — เข้าถึง keyword ของทุก feature ภายใน 2 คลิก | heuristic | PASS | output.html: DOM file://, 1280×800, nav ชั้นแรก 14 ตัว; ห้อง: 0 คลิก: หน้าแรก; เวลาว่าง: 0 คลิก: หน้าแรก; จอง: 0 คลิก: หน้าแรก; ยกเลิก: 0 คลิก: หน้าแรก; สถานะ: 0 คลิก: หน้าแรก |
| loop | F4_no_cdn — ไม่มีการอ้างทรัพยากรเครือข่ายภายนอก | script | PASS | output.html: สแกน source ทั้งไฟล์; ไม่พบ src/href/CSS URL/import/fetch ภายนอกใน source |
| loop_claude | F1_features_present — พบข้อความสื่อ 5 feature ใน DOM หน้าแรกหรือ nav ชั้นแรก | heuristic | FAIL | output.html: DOM file://, 1280×800, nav ชั้นแรก 3 ตัว; ห้อง: 0 คลิก: หน้าแรก; เวลาว่าง: 0 คลิก: หน้าแรก; จอง: 0 คลิก: หน้าแรก; ยกเลิก: ไม่พบในเส้นทางที่ตรวจ; สถานะ: 0 คลิก: หน้าแรก |
| loop_claude | F2_opens_no_console_error — เปิด file:// โดยไม่มี console error/pageerror | script | PASS | output.html: Playwright เปิด file:// ใน context ใหม่; console/pageerror หน้าแรก=0; error รวมระหว่างสำรวจ=0; ปิด network |
| loop_claude | F3_two_clicks — เข้าถึง keyword ของทุก feature ภายใน 2 คลิก | heuristic | FAIL | output.html: DOM file://, 1280×800, nav ชั้นแรก 3 ตัว; ห้อง: 0 คลิก: หน้าแรก; เวลาว่าง: 0 คลิก: หน้าแรก; จอง: 0 คลิก: หน้าแรก; ยกเลิก: ไม่พบในเส้นทางที่ตรวจ; สถานะ: 0 คลิก: หน้าแรก |
| loop_claude | F4_no_cdn — ไม่มีการอ้างทรัพยากรเครือข่ายภายนอก | script | PASS | output.html: สแกน source ทั้งไฟล์; ไม่พบ src/href/CSS URL/import/fetch ภายนอกใน source |

### 2_expense_claim

| Workflow | เกณฑ์ | วิธี | ผล | Evidence |
|---|---|---|---|---|
| dynamic | E1_trace_all_sentences — Traceability ครอบคลุม keyword ต้นทางทั้ง 9 กลุ่ม | heuristic | PASS | output.md: Traceability; กลุ่ม 1: 495; กลุ่ม 2: 496,503,504,508; กลุ่ม 3: 498; กลุ่ม 4: 499; กลุ่ม 5: 500; กลุ่ม 6: 501,502; กลุ่ม 7: 503; กลุ่ม 8: 504; กลุ่ม 9: 505 |
| dynamic | E2_conflict_open_issue — Open Issues มีเกณฑ์ 5,000 และ 10,000 | script | PASS | output.md:130,130; Open Issues: พบทั้งสองค่า |
| dynamic | E3_no_invented_amounts — ไม่พบตัวเลขวงเงินที่พักที่แต่งเพิ่มใน FR/BR | heuristic | PASS | output.md:61; สแกนตัวเลข+บาท ห่างจาก ที่พัก/คืน/วงเงิน ไม่เกิน 100 ตัวอักษร; ไม่พบค่านอก 5,000/10,000 |
| dynamic | E4_entity_consistency — ชื่อ participant/entity ใน Sequence/State เทียบกับ ERD | heuristic | FAIL | output.md:183,371,450; ERD 15 entity; ชื่อไม่พบ: D (ฐานข้อมูล), S (ระบบเบิกค่าใช้จ่าย); เทียบชื่อ literal (ตัด _/ไม่สนตัวพิมพ์); participant ที่เป็นระบบ/บทบาทอาจเป็น false positive; ไม่รับรอง attribute/ความหมาย |
| dynamic | E5_state_holder — ชื่อ state หรือ note ระบุผู้ถือเรื่อง | heuristic | PASS | output.md:453,454,455; ตรวจเฉพาะชื่อ state และ note |
| dynamic | E6_mermaid_renders — Mermaid ทุกบล็อก render ได้ | render | PASS | output.md:149,183,371,450; render_markdown ได้ SVG 4/4 บล็อก; ไม่เขียนไฟล์ render |
| graph | E1_trace_all_sentences — Traceability ครอบคลุม keyword ต้นทางทั้ง 9 กลุ่ม | heuristic | PASS | output.md: Traceability; กลุ่ม 1: 380; กลุ่ม 2: 381,388,389; กลุ่ม 3: 383; กลุ่ม 4: 384; กลุ่ม 5: 385; กลุ่ม 6: 386,387; กลุ่ม 7: 388; กลุ่ม 8: 389; กลุ่ม 9: 390 |
| graph | E2_conflict_open_issue — Open Issues มีเกณฑ์ 5,000 และ 10,000 | script | PASS | output.md:412,412; Open Issues: พบทั้งสองค่า |
| graph | E3_no_invented_amounts — ไม่พบตัวเลขวงเงินที่พักที่แต่งเพิ่มใน FR/BR | heuristic | PASS | output.md:41; สแกนตัวเลข+บาท ห่างจาก ที่พัก/คืน/วงเงิน ไม่เกิน 100 ตัวอักษร; ไม่พบค่านอก 5,000/10,000 |
| graph | E4_entity_consistency — ชื่อ participant/entity ใน Sequence/State เทียบกับ ERD | heuristic | FAIL | output.md:124,250,316; ERD 10 entity; ชื่อไม่พบ: A (ฝ่ายบัญชี), M (ผู้จัดการฝ่าย), T (หัวหน้าทีม); เทียบชื่อ literal (ตัด _/ไม่สนตัวพิมพ์); participant ที่เป็นระบบ/บทบาทอาจเป็น false positive; ไม่รับรอง attribute/ความหมาย |
| graph | E5_state_holder — ชื่อ state หรือ note ระบุผู้ถือเรื่อง | heuristic | PASS | output.md:319,321,322,324,326,328; ตรวจเฉพาะชื่อ state และ note |
| graph | E6_mermaid_renders — Mermaid ทุกบล็อก render ได้ | render | PASS | output.md:79,124,250,316; render_markdown ได้ SVG 4/4 บล็อก; ไม่เขียนไฟล์ render |
| loop | E1_trace_all_sentences — Traceability ครอบคลุม keyword ต้นทางทั้ง 9 กลุ่ม | heuristic | PASS | output.md: Traceability; กลุ่ม 1: 336; กลุ่ม 2: 337,342,343; กลุ่ม 3: 338; กลุ่ม 4: 339; กลุ่ม 5: 340; กลุ่ม 6: 341; กลุ่ม 7: 342; กลุ่ม 8: 343; กลุ่ม 9: 344 |
| loop | E2_conflict_open_issue — Open Issues มีเกณฑ์ 5,000 และ 10,000 | script | PASS | output.md:368,368; Open Issues: พบทั้งสองค่า |
| loop | E3_no_invented_amounts — ไม่พบตัวเลขวงเงินที่พักที่แต่งเพิ่มใน FR/BR | heuristic | PASS | output.md:25; สแกนตัวเลข+บาท ห่างจาก ที่พัก/คืน/วงเงิน ไม่เกิน 100 ตัวอักษร; ไม่พบค่านอก 5,000/10,000 |
| loop | E4_entity_consistency — ชื่อ participant/entity ใน Sequence/State เทียบกับ ERD | heuristic | FAIL | output.md:101,227,303; ERD 13 entity; ชื่อไม่พบ: App (ระบบเบิกค่าใช้จ่าย); เทียบชื่อ literal (ตัด _/ไม่สนตัวพิมพ์); participant ที่เป็นระบบ/บทบาทอาจเป็น false positive; ไม่รับรอง attribute/ความหมาย |
| loop | E5_state_holder — ชื่อ state หรือ note ระบุผู้ถือเรื่อง | heuristic | PASS | output.md:306,307,308,309,310,311; ตรวจเฉพาะชื่อ state และ note |
| loop | E6_mermaid_renders — Mermaid ทุกบล็อก render ได้ | render | PASS | output.md:68,101,227,303; render_markdown ได้ SVG 4/4 บล็อก; ไม่เขียนไฟล์ render |

### 3_clinic_migration

| Workflow | เกณฑ์ | วิธี | ผล | Evidence |
|---|---|---|---|---|
| dynamic | M1_five_problem_types — ตาราง Data Quality Findings มีอย่างน้อย 5 แถวปัญหา | heuristic | PASS | output.md:199,200,201,202,203,204,205,206,207,208,209,210; ตาราง Findings แรกมี 12 แถวข้อมูล (ไม่รับรองว่าทุกแถวเป็นคนละประเภท) |
| dynamic | M2_ambiguous_date_flagged — แถววันที่เป้าหมายมีข้อความ flag ความกำกวม | script | PASS | output.md:199; พบ marker ในบรรทัดเดียวกับวันที่เป้าหมาย; ไม่ตัดสินการตีความวันที่ |
| dynamic | M3_identity_strategy — หัวข้อ mapping/migration/identity มี normalization และการยืนยัน | heuristic | PASS | output.md:568,604,619; normalization marker; output.md:565,568,569; confirmation marker ในหัวข้อที่กำหนด |
| dynamic | M4_plan_version_log — บันทึกเวอร์ชันแผนมี v1 และ v2 | script | PASS | output.md:5,42,22,40; หัวข้อ Plan Version/ชื่อไทย/Plan vN: v1=True, v2=True; v1.1 ไม่นับเป็น v2 |
| dynamic | M5_impact_analysis — เฟส 2 มีคำ Impact และ Reuse หรือคงเดิม | script | PASS | Impact: output.md:36, output.md:75, output.md:784; Reuse/คงเดิม: output.md:19, output.md:37, output.md:71; ตรวจคำเท่านั้น |
| dynamic | M6_mermaid_renders — Mermaid ทุกบล็อก render ได้ | render | PASS | output.md:173,264,317,627; render_markdown ได้ SVG 4/4 บล็อก; ไม่เขียนไฟล์ render |
| graph | M1_five_problem_types — ตาราง Data Quality Findings มีอย่างน้อย 5 แถวปัญหา | heuristic | PASS | output.md:59,60,61,62,63,64,65,66,67,68,69,70; ตาราง Findings แรกมี 12 แถวข้อมูล (ไม่รับรองว่าทุกแถวเป็นคนละประเภท) |
| graph | M2_ambiguous_date_flagged — แถววันที่เป้าหมายมีข้อความ flag ความกำกวม | script | PASS | output.md:41,68,105,159,1024; พบ marker ในบรรทัดเดียวกับวันที่เป้าหมาย; ไม่ตัดสินการตีความวันที่ |
| graph | M3_identity_strategy — หัวข้อ mapping/migration/identity มี normalization และการยืนยัน | heuristic | PASS | output.md:841,901,924; normalization marker; output.md:833,838,839; confirmation marker ในหัวข้อที่กำหนด |
| graph | M4_plan_version_log — บันทึกเวอร์ชันแผนมี v1 และ v2 | script | PASS | output.md:993,994,995; หัวข้อ Plan Version/ชื่อไทย/Plan vN: v1=True, v2=True; v1.1 ไม่นับเป็น v2 |
| graph | M5_impact_analysis — เฟส 2 มีคำ Impact และ Reuse หรือคงเดิม | script | FAIL | Impact: ไม่พบใน output.md + response-phase2.md; Reuse/คงเดิม: output.md:14, output.md:810, output.md:841; ตรวจคำเท่านั้น |
| graph | M6_mermaid_renders — Mermaid ทุกบล็อก render ได้ | render | PASS | output.md:113,175,208,453,492; render_markdown ได้ SVG 5/5 บล็อก; ไม่เขียนไฟล์ render |
| loop | M1_five_problem_types — ตาราง Data Quality Findings มีอย่างน้อย 5 แถวปัญหา | heuristic | PASS | output.md:54,55,56,57,58,59,60,61,62,63; ตาราง Findings แรกมี 10 แถวข้อมูล (ไม่รับรองว่าทุกแถวเป็นคนละประเภท) |
| loop | M2_ambiguous_date_flagged — แถววันที่เป้าหมายมีข้อความ flag ความกำกวม | script | PASS | output.md:23,54; พบ marker ในบรรทัดเดียวกับวันที่เป้าหมาย; ไม่ตัดสินการตีความวันที่ |
| loop | M3_identity_strategy — หัวข้อ mapping/migration/identity มี normalization และการยืนยัน | heuristic | PASS | output.md:214,215,251; normalization marker; output.md:213,214,215; confirmation marker ในหัวข้อที่กำหนด |
| loop | M4_plan_version_log — บันทึกเวอร์ชันแผนมี v1 และ v2 | script | FAIL | output.md:289,290; หัวข้อ Plan Version/ชื่อไทย/Plan vN: v1=True, v2=False; v1.1 ไม่นับเป็น v2 |
| loop | M5_impact_analysis — เฟส 2 มีคำ Impact และ Reuse หรือคงเดิม | script | FAIL | Impact: ไม่พบใน output.md + response-phase2.md; Reuse/คงเดิม: output.md:7, output.md:360, output.md:445; ตรวจคำเท่านั้น |
| loop | M6_mermaid_renders — Mermaid ทุกบล็อก render ได้ | render | PASS | output.md:29,69,92,327; render_markdown ได้ SVG 4/4 บล็อก; ไม่เขียนไฟล์ render |

## หมายเหตุจากหลักฐาน

- `1_meeting_room/dynamic`: ไม่มีชื่อ model ใน thread/init หรือ .engine; ไม่อนุมานจาก launcher หรือคำสั่งมาตรฐาน; ไม่มี snapshot trace ก่อนหน้าให้พิสูจน์ append-only; CDN/external resources: ไม่พบ; trace.md: นับรหัสไม่ซ้ำ v1
- `1_meeting_room/graph`: ไม่มีชื่อ model ใน thread/init หรือ .engine; ไม่อนุมานจาก launcher หรือคำสั่งมาตรฐาน; ไม่มี snapshot trace ก่อนหน้าให้พิสูจน์ append-only; CDN/external resources: ไม่พบ; trace.md: นับรหัสไม่ซ้ำ N1, N1b, N2, N4, N3, N5
- `1_meeting_room/loop`: ไม่มีชื่อ model ใน thread/init หรือ .engine; ไม่อนุมานจาก launcher หรือคำสั่งมาตรฐาน; ไม่มี snapshot trace ก่อนหน้าให้พิสูจน์ append-only; CDN/external resources: ไม่พบ; trace.md: นับรหัสไม่ซ้ำ 1
- `1_meeting_room/loop_claude`: ไม่มี snapshot trace ก่อนหน้าให้พิสูจน์ append-only; CDN/external resources: ไม่พบ; trace.md: นับรหัสไม่ซ้ำ 1
- `2_expense_claim/dynamic`: ไม่มีชื่อ model ใน thread/init หรือ .engine; ไม่อนุมานจาก launcher หรือคำสั่งมาตรฐาน; trace.md กล่าวถึงการ append/ต่อท้าย; ไม่ใช่หลักฐานยืนยันประวัติไฟล์ทุกช่วง; trace.md: นับรหัสไม่ซ้ำ v1
- `2_expense_claim/graph`: ไม่มีชื่อ model ใน thread/init หรือ .engine; ไม่อนุมานจาก launcher หรือคำสั่งมาตรฐาน; trace.md กล่าวถึงการ append/ต่อท้าย; ไม่ใช่หลักฐานยืนยันประวัติไฟล์ทุกช่วง; trace.md: นับรหัสไม่ซ้ำ N1, N1b, N2, N3, N4, N5
- `2_expense_claim/loop`: ไม่มีชื่อ model ใน thread/init หรือ .engine; ไม่อนุมานจาก launcher หรือคำสั่งมาตรฐาน; ไม่มี snapshot trace ก่อนหน้าให้พิสูจน์ append-only; trace.md: นับรหัสไม่ซ้ำ 1
- `3_clinic_migration/dynamic`: ไม่มีชื่อ model ใน thread/init หรือ .engine; ไม่อนุมานจาก launcher หรือคำสั่งมาตรฐาน; ไม่มี snapshot trace ก่อนหน้าให้พิสูจน์ append-only; output คือฉบับหลังเฟส 2; เกณฑ์ตรวจฉบับปัจจุบัน; เวลา/โทเคนแยกตาม log ของแต่ละเฟส; trace.md: นับรหัสไม่ซ้ำ v1, v2, v3
- `3_clinic_migration/graph`: ไม่มีชื่อ model ใน thread/init หรือ .engine; ไม่อนุมานจาก launcher หรือคำสั่งมาตรฐาน; trace.md กล่าวถึงการ append/ต่อท้าย; ไม่ใช่หลักฐานยืนยันประวัติไฟล์ทุกช่วง; output คือฉบับหลังเฟส 2; เกณฑ์ตรวจฉบับปัจจุบัน; เวลา/โทเคนแยกตาม log ของแต่ละเฟส; trace.md: นับรหัสไม่ซ้ำ N1, N1b, N2, N3, N4, N5; รวมสองเฟส; จำนวน node ไม่ใช่จำนวนการเรียกซ้ำ
- `3_clinic_migration/loop`: ไม่มีชื่อ model ใน thread/init หรือ .engine; ไม่อนุมานจาก launcher หรือคำสั่งมาตรฐาน; ไม่มี snapshot trace ก่อนหน้าให้พิสูจน์ append-only; output คือฉบับหลังเฟส 2; เกณฑ์ตรวจฉบับปัจจุบัน; เวลา/โทเคนแยกตาม log ของแต่ละเฟส; trace.md: นับรหัสไม่ซ้ำ 1, 2, 3
