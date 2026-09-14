# ผลรันอ้างอิง LAB 006

วันที่ UTC: 2026-09-14

เครื่องมือ Codex CLI 0.154.0; โมเดล gpt-6-astra, effort high ตาม flag ที่สั่ง CLI ไม่ยืนยันกลับจากบริการ

ใช้ Input ผลอ้างอิง LAB 005 ตาม [provenance](step-00-input/provenance.md); ไม่ใช่ผลของนักศึกษาและไม่ใช้ผลต้นทางเป็นผลรัน UI ใหม่

| ขั้น | สถานะการเรียก | ผลและหลักฐาน |
|---|---|---|
| step-00-input | completed | [ผล](step-00-input/input-check.md) · [prompt](step-00-input/prompt-used.md) · [log](step-00-input/log.jsonl) · [meta](step-00-input/meta.json) |
| step-01-fanout/customer | completed | [ผล](step-01-fanout/customer/scenarios-customer.md) · [prompt](step-01-fanout/customer/prompt-used.md) · [log](step-01-fanout/customer/log.jsonl) · [meta](step-01-fanout/customer/meta.json) |
| step-01-fanout/manager | completed | [ผล](step-01-fanout/manager/scenarios-manager.md) · [prompt](step-01-fanout/manager/prompt-used.md) · [log](step-01-fanout/manager/log.jsonl) · [meta](step-01-fanout/manager/meta.json) |
| step-01-fanout/kitchen-front | completed | [ผล](step-01-fanout/kitchen-front/scenarios-kitchen-front.md) · [prompt](step-01-fanout/kitchen-front/prompt-used.md) · [log](step-01-fanout/kitchen-front/log.jsonl) · [meta](step-01-fanout/kitchen-front/meta.json) |
| step-02-coverage/round-1 | completed | [ผล](step-02-coverage/round-1/coverage-round-1.md) · [prompt](step-02-coverage/round-1/prompt-used.md) · [log](step-02-coverage/round-1/log.jsonl) · [meta](step-02-coverage/round-1/meta.json) |
| step-02-coverage/fix-1 | completed | [ผล](step-02-coverage/fix-1/coverage-fixes-round-1.md) · [prompt](step-02-coverage/fix-1/prompt-used.md) · [log](step-02-coverage/fix-1/log.jsonl) · [meta](step-02-coverage/fix-1/meta.json) |
| step-02-coverage/round-2 | completed | [ผล](step-02-coverage/round-2/coverage-round-2.md) · [prompt](step-02-coverage/round-2/prompt-used.md) · [log](step-02-coverage/round-2/log.jsonl) · [meta](step-02-coverage/round-2/meta.json) |
| step-03-merge | completed | [ผล](step-03-merge/test-scenarios.md) · [prompt](step-03-merge/prompt-used.md) · [log](step-03-merge/log.jsonl) · [meta](step-03-merge/meta.json) |
| step-04-nfr-split | completed | [ผล](step-04-nfr-split/nfr-split.md) · [prompt](step-04-nfr-split/prompt-used.md) · [log](step-04-nfr-split/log.jsonl) · [meta](step-04-nfr-split/meta.json) |
| step-05-ui-run | completed | [ผล](step-05-ui-run/ui-run-report.md) · [prompt](step-05-ui-run/prompt-used.md) · [log](step-05-ui-run/log.jsonl) · [meta](step-05-ui-run/meta.json) |

CSV แจกแจงสมาชิกชุดความสัมพันธ์ระดับ US เป็น tuple ตามทะเบียน ไม่ใช่จำนวนการทดสอบหรือหลักฐานคู่ Flow → Screen รายเหตุการณ์ ดู [traceability-notes](step-03-merge/traceability-notes.md). การเรียกสำเร็จไม่แปลว่า COVERED/PASS: รอบแรกขั้นต่ำ19/26; หลังแก้ขั้นต่ำ26/26และ STOP_WITH_GAPS เพราะ mapping upstream/fixture/คำถามธุรกิจค้าง ใช้รอบแก้1จากเพดาน2 ดู [decision-log](step-02-coverage/decision-log.md)

ผ่าน 12 / ตก 2 / ข้าม 0 จาก 14 fixture; รายการที่ mock-up ทดสอบไม่ได้และเหตุผลอยู่ใน [รายงาน UI](step-05-ui-run/ui-run-report.md) ระบบจริง/NFR ยัง NOT_TESTED

ฉบับส่งต่อ: [test-scenarios.md](final/test-scenarios.md), [traceability.csv](final/traceability.csv), [nfr-split.md](final/nfr-split.md), [metrics.csv](metrics.csv)

final/test-scenarios.md คัดลอกจาก step-03-merge; final/traceability.csv คัดลอกจาก step-05-ui-run/traceability-after-ui.csv; final/nfr-split.md คัดลอกจาก step-04-nfr-split และ final/traceability-notes.md คัดลอกจาก step-03-merge แบบ bytes ตรงกัน ไม่มีการแก้ผล AI ด้วยมือ

การจัดเก็บ: snapshot อยู่ step-00-input ตามรายการส่งมอบ; prompt-used ปรับ path ให้เขียนตรงโฟลเดอร์ขั้นเพื่อไม่แตะ work/ ซึ่งเหลือ .gitkeep; manifest ตั้งต้นคงเดิมและใช้ฐานตำแหน่ง manifest ส่วน manifest หลังแก้ใช้ฐาน LAB

JSON UI เปลี่ยนเฉพาะ top-level html เป็น relative path เพื่อเผยแพร่; ต้นฉบับทุก bytes อยู่ใน runner/log.jsonl ส่วน results/reason/status/screenshot เท่าต้นฉบับทั้งหมด ไม่มีโทเคนสำหรับ browser runner; เวลาแยกไว้ใน [runner/meta.json](step-05-ui-run/runner/meta.json)

metrics อ่านโทเคนจาก turn.completed.usage และเวลา wall จาก meta ของแต่ละการเรียก; input_tokens รวม cached input ตาม CLI; fan-out รันขนาน ไม่รวมเวลาทีละแถวเป็นเวลารอจริง

กิจกรรมทดลอง Prompt 6.6: ตัวอย่างประกอบ — ยังไม่ได้รันจริง; รอบนี้สิ้นสุดที่ตรวจผล UI ไม่มีเวลา/โทเคน/ผลของ variant
