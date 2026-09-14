# ผลรันล่วงหน้า LAB 004

วันที่ UTC: 2026-09-14

สร้าง UI ด้วย Codex CLI 0.154.0; โมเดล `gpt-6-astra (ตาม flag ที่สั่ง CLI ไม่ยืนยันกลับ)`; reasoning effort `high`
Browser: Playwright 1.62.0, Chromium 151.0.7922.34, chromium.launch(), file://; ไม่ต้องใช้ CDP

ใช้ผลอ้างอิง ไม่ใช่ผลที่นักศึกษารันเอง ต้นทาง LAB 003 ยังคง READINESS: BLOCKED เพราะ MC-01–MC-03; การทดลองนี้พร้อมเฉพาะ mock ตาม contract ของ LAB 004 และไม่ได้ยืนยันกฎที่ค้าง

| รอบ | Prompt | ผ่าน | ตก | edge | สถานะ |
|---|---|---:|---:|---|---|
| round-1 | 01-build-ui.md | 19 | 0 | pass | หยุดแก้ ส่งตรวจ AI |

มีเพียง 1 รอบ ไม่มีรอบแก้และไม่มีภาพก่อน–หลังการแก้ เพดานชุดนี้รวมไม่เกิน 3 รอบ ต่างจากกิจกรรมผู้เรียนที่นับ baseline 0 + แก้ 1–3

## เปิดหลักฐาน

- [HTML สุดท้าย เปิดเล่นผ่าน file://](final/ui-mockup.html)
- [Input provenance / SHA-256 / ต้นทางแต่ละไฟล์](step-00-input/provenance.md), [audit](step-00-input/input-audit.md), [แผนการทดลอง](step-00-input/session-plan.md)
- [Prompt รอบ 1 ที่ใช้จริง](round-1/prompt-used.md), [log.jsonl](round-1/log.jsonl), [metadata](round-1/run-meta.json), [build notes](round-1/build-notes.md)
- [HTML รอบแรก](round-1/ui-mockup.html), [ui-check.json](round-1/ui-check.json), [สรุป 19 checks และภาพ](round-1/ui-check-round-1.md)
- [decision-log](decision-log.md), [metrics.csv](metrics.csv)
- [Prompt ผู้ตรวจ AI](review/prompt-used.md), [log ผู้ตรวจ](review/log.jsonl), [รายงานผู้ตรวจ](review/review.md)
- [ภาพคลิกจริง 10 ภาพ: ลำดับคลิก/เวลา/ขนาด/hash](final/screenshots.json), [ภาพและวิธีเล่นในคู่มือ](../README.md)

## รูปแบบ log

[log-original.jsonl.gz](round-1/log-original.jsonl.gz) เก็บ stdout ดิบครบทุกไบต์ ส่วน log.jsonl ใช้ Unicode escapes เฉพาะบางข้อความใน tool output เพื่อไม่ให้การค้นชื่อ event แบบ regex ไปตรงกับโค้ด `return failed_ids`
ตรวจแล้วว่า parse JSON ของทุกบรรทัดได้ข้อมูลตรงต้นฉบับทั้งหมด ไม่มีการเปลี่ยน event, usage หรือผลลัพธ์; SHA-256 ของดิบอยู่ใน run-meta.json
ตรวจชนิด event ด้วย JSON parser ได้ตรงกว่า grep ข้อความ เพราะ log มี source code ที่โมเดลอ่านรวมอยู่ด้วย

## เวลาและโทเคน

| การเรียก | duration_s | input_tokens | output_tokens |
|---|---:|---:|---:|
| round-1 | 642.275 | 829124 | 23170 |
| ผู้ตรวจ AI | 609.910 | 3252625 | 27473 |
| รวม 2 การเรียก | 1252.185 | 4081749 | 50643 |

input/output มาจาก event turn.completed.usage; cached_input_tokens เป็นส่วนหนึ่งของ input_tokens ไม่บวกซ้ำ
เวลา wall วัดด้วย monotonic ครอบ subprocess ของ CLI และบันทึก UTC เริ่ม/จบใน run-meta.json ไม่ใช่เวลา simulation ใน UI
ต้นทุนเงิน: ไม่มีข้อมูล; ไม่เดาราคา
metrics.csv เก็บเฉพาะรอบสร้าง/แก้ ส่วนผู้ตรวจแยกใน review/run-meta.json เพื่อไม่ปนกับจำนวนรอบของกราฟ

## วิธีตรวจซ้ำ

จากโฟลเดอร์ LAB 004 เปิดไฟล์ final โดยตรง หรือใช้คำสั่งนี้กับปลายทางใหม่ที่ยังไม่มีรายงาน:

```bash
/opt/venv/bin/python3 tests/ui-check.py --html reference/final/ui-mockup.html --out /tmp/ui-check-new.json --shots /tmp/ui-shots-new
```

รูปแบบคำสั่งกลางที่ใช้รัน prompt จาก cwd ของ LAB (เตรียม work ตาม snapshot ก่อน; อย่าใช้ชื่อปลายทางเดิม):

```bash
codex exec --json -m gpt-6-astra -c model_reasoning_effort="high" -o <NEW_RUN_DIR>/summary.md "$(cat <PROMPT_USED.md>)" </dev/null > <NEW_RUN_DIR>/log.jsonl 2> <NEW_RUN_DIR>/stderr.txt
```

-o ใช้เก็บคำตอบสรุป; HTML ถูกเขียนใน work/ui-mockup.html ตาม prompt แล้วจึง snapshot หลัง turn.completed
HTML round-1 และ final มี SHA-256 เดียวกัน: `d2b7bfa0cff5700d3ca07f611c03cfa0304c54eafb51387f125e95edd11f7803`
ไม่มีการแก้ HTML ด้วยมือหลังผู้สร้างส่งผล และไม่ได้แก้ prompts/, tests/ หรือ input/

## ผลผู้ตรวจ AI และการจัดเก็บ

[รายงาน AI](review/review.md) และ [บันทึกคลิก/ทะเบียนภาพ 59 ภาพ](review/click-review-round-1.md) มาจาก Prompt 03 ที่เรียกหนึ่งครั้ง ไม่มี turn.failed
assertions ทั้ง 19 checks ผ่านที่ 1280×900 และ 390×844 รวม 38 executions; เป็นการตรวจของผู้ตรวจในชุดเดิม ไม่ใช่รอบแก้
ผู้ตรวจพบช่องว่าง ETA (บริบท FR-07/US-07) และ UX ที่เปลี่ยนช่วงรับเองโดยไม่แจ้ง; ส่งให้ SA วางแผนใหม่โดยคง raw edge=pass
ผู้ตรวจแยกเหตุ CSP ของคำสั่งรอในสคริปต์ชั่วคราวออกจาก UI แล้วตรวจเฉพาะกลุ่มรูป/ตัวเลือกซ้ำ เก็บภาพก่อน/หลังการลองเครื่องมือนั้นไว้ ไม่ถือเป็นรอบแก้ HTML
ต้นฉบับรายงานแบบ gzip อยู่ข้างรายงาน; ฉบับอ่านได้ปรับเฉพาะลิงก์ relative หลังย้ายจาก work/ พร้อม hash ใน review/run-meta.json
ข้อสังเกตของ AI ว่า screenshots.json และ log ผู้ตรวจเปลี่ยนระหว่าง session เกิดจากการถ่ายภาพประกอบ/บันทึก manifest และการเขียน stdout ที่ทำพร้อมการตรวจ ไม่ใช่การแก้ HTML หรือผล JSON

## ขอบเขตที่ยังไม่ยืนยัน

pass ยืนยันเพียง mock smoke suite ไม่รับรองกฎธุรกิจที่ยัง BLOCKED, LAN, หลายอุปกรณ์, load, authentication ฝั่ง server หรือการจ่ายเงินจริง
คง A-02, DI-04/A-03, DI-07/A-05; ETA ไม่มีข้อมูลค่าเฉลี่ยพอคำนวณ ทาง fix/cancel ไม่ได้ใช้กับ UI นี้เพราะรอบแรกผ่าน
ผลผู้ตรวจ AI แยกจาก raw edge หากพบข้อเพิ่มเติมต้องวางแผนชุดใหม่ ไม่เปลี่ยน JSON ให้เป็นผลอื่น
