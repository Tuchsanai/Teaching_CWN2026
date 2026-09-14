# ที่มาและวิธีรัน

ใช้ผลอ้างอิงจาก LAB 001
ต้นทาง: ../001_LAB_Single_Prompt_Baseline/reference/step-02/round-1/fr-nfr-v0.md
วันที่ผล: 2026-09-14 10:28:10–10:31:52 UTC
SHA-256: 88d6f0ca6d91cbcddc48a24dbf3eb0c752e72430e57c4e20795d1157a03e9abc

ใช้ work/ ชั่วคราวตามขั้นตอนเตรียมและส่งต่อ เมื่อจบย้ายหลักฐานเข้า reference/ และเหลือ .gitkeep เท่านั้น
รันมือทีละขั้นตามลำดับของ input/run-loop.sh; ไม่แก้ prompts/ หรือ input/
เครื่องมือ: Codex CLI 0.154.0; โมเดล: gpt-6-astra (ตาม flag ที่สั่ง CLI ไม่ยืนยันกลับ); effort: high (ค่าที่สั่งผ่าน flag)
บัญชี: <บัญชี>

## ผลรันจริง

- started_at: 2026-09-14T11:01:00Z
- finished_at: 2026-09-14T11:08:59Z
- tool: Codex CLI 0.154.0
- model: gpt-6-astra (ตาม flag ที่สั่ง CLI ไม่ยืนยันกลับ)
- effort: high (ค่าที่สั่งผ่าน flag)
- duration_s: 470
- wall_seconds: 479
- status: completed; PASS 90/90
- stop_reason: pass
- calls: 2
- checker_rounds: 1
- baseline_source: ../001_LAB_Single_Prompt_Baseline/reference/step-02/round-1/fr-nfr-v0.md
- baseline_date_utc: 2026-09-14 10:28:10–10:31:52 UTC
- final_document: reference/final/fr-nfr-input.md

โทเคนรวมจาก turn.completed.usage ของทั้ง 2 calls:

- input_tokens: 697658
- output_tokens: 25908
- cached_input_tokens: 612352
- reasoning_output_tokens: 821

ไม่บวก cached_input_tokens หรือ reasoning_output_tokens ซ้ำในยอด input + output
ระยะเวลาเรียกรวม 470 วินาที; wall ทั้งชุด 479 วินาที รวมช่วงส่งต่อ 9 วินาที ใช้ date -u +%s คร่อมแต่ละคำสั่ง

รันมือทีละขั้นด้วย Prompt เดิมและ N=1 ตามค่าเริ่มต้น ใช้ loop-support.py บันทึก call ตรวจ matrix/RESULT/SCORE และเหตุหยุด; ไม่เรียก run-loop.sh ทั้งไฟล์ เพราะ AI_CMD รองรับเฉพาะคำสั่งกลางตรงตัว

[ผลทุก call](loop-log.json), [log ตาม schema เดิม](loop-log.schema-compatible.json), [log ก่อนย้าย work](loop-log-original.json), [สรุป](loop-summary.md), [ไฟล์ส่งต่อ LAB 003/005](final/fr-nfr-input.md)

## สมมติฐานรูปแบบข้อมูล

รูปแบบสรุปที่ต้องเก็บทุก call ใน rounds พร้อม step/log/usage ขัดกับ input/loop-log.schema.json ที่จำกัด rounds เฉพาะ checker และ additionalProperties=false จึงใช้ loop-log.json สำหรับทุก call และเก็บ loop-log.schema-compatible.json ตาม schema เดิมโดยใช้หลักฐานชุดเดียวกัน ไม่แก้ schema หรือ prompt

ใช้ work/ เป็นพื้นที่ชั่วคราวตามขั้นเตรียมและคำสั่งล้างงานที่กำหนด ไม่มีการแก้ไฟล์บทเรียนอื่นหรือสร้างผล LAB 003/005 เอง ขั้นปรับเกณฑ์ E1 อยู่นอกชุดนี้ จึงยังไม่ได้รัน

## การเก็บ stdout ดิบ

JSONL เก็บ stdout เดิมครบโดยไม่แก้ข้อความ คำสั่งของ checker อ่าน ../docs/data-issues.md เพิ่มตามการอ้างในเกณฑ์ จึงมีข้อความกำกับการจัดทำเดิมติดมาใน aggregated_output ของ log แต่ไม่ได้คัดข้อความกำกับนั้นลง README หรือสรุปผล ไม่มีการแก้เอกสารต้นทางนอกขอบเขตงาน
