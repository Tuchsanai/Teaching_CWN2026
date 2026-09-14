# เปรียบเทียบข้อกำหนดเปลี่ยน — Single Prompt / Dynamic

วันที่ UTC 2026-09-14; Codex CLI 0.154.0; gpt-6-astra (ตาม flag ที่สั่ง CLI ไม่ยืนยันกลับ); effort high
baseline และ plan-v3 เดียวกันตาม manifest; ผลทดลองหนึ่งคู่ไม่ใช่ค่าเฉลี่ย

| เกณฑ์ | Single Prompt | Dynamic | แหล่งค่า (จริง/ประมาณ/ไม่มีข้อมูล) |
|---|---|---|---|
| ข้อเปลี่ยน | US-21 N=5 → N=3; 15 นาที; 00/15/30/45; 3 จาก 3 รอบ; เตือนก่อนยืนยัน ไม่เพิ่มกฎปฏิเสธ | เหมือน Single ทุกคำในส่วนข้อกำหนดเปลี่ยน | จริง: prompt-used.md ทั้งสองขั้น |
| จำนวนเรียก AI | 1 | 3 (plan + execute + evaluate) | จริง: terminal events ของทุก phase |
| จำนวนรอบทดลอง | 1 การเรียก; ไม่มีการแก้ซ้ำ | round 0; ไม่มี replan/รอบแก้ | จริง: log/meta และ evaluation-round-0.md |
| input_tokens | 1420196 | 1959100 | จริง: usage; รวมทุก phase |
| output_tokens | 20384 | 35578 | จริง: usage; รวมทุก phase |
| โทเคนรวม input+output | 1440580 | 1994678 | จริง: บวกสองคอลัมน์ข้างต้น ไม่บวก cache ซ้ำ |
| เวลา AI รวม (s) | 411.758 | 707.744 | จริง: ผลรวม wall ของ subprocess รายเรียก ไม่ใช่ wall แบบขนาน |
| เวลา UI runner (s) | 15.805 | 16.257 | จริง: ui-run-meta.json แยกจาก AI |
| เวลา AI + UI runner (s) | 427.563 | 724.001 | จริง: ผลรวมช่วงที่วัด แยกจากเวลารอระหว่างขั้น |
| ช่วงเริ่ม AI ถึงจบตรวจ (s) | 464.927 | 779.935 | จริง: timestamps; รวมช่องว่างระหว่างขั้น; Single จบที่ script, Dynamic จบ evaluate |
| จำนวนไฟล์หลักที่กระทบ | 4: FR, Flow, UI, scenarios | 4: FR, Flow, UI, scenarios | จริง: เทียบไฟล์กับ baseline; ไม่นับเอกสารกำกับ |
| ไฟล์ที่ AI ผลิตรวมเอกสารกำกับ | 8: 4 หลัก + impact + scenario Markdown 3 | 9: 4 หลัก + execution + plan 3 ไฟล์ + evaluation | จริง: นับไฟล์ที่มีอยู่ ไม่รวม log/meta/summary/ภาพ/รายงานตรวจภายนอก |
| แถวข้อกำหนดที่ใช้ซ้ำ | US/FR/NFR นอก US-21/FR-21 คงเดิมทุกแถว | เหมือน Single | จริง: เทียบข้อความทุกแถวรวม ID ที่ซ้ำใน traceability |
| ส่วน UI ที่ใช้ซ้ำ | selectors, role, reset, capacity window/count/notice และ submit | เหมือน Single | ประมาณด้านความหมายจาก diff/source; ไม่ใช่การรับรองทุกพฤติกรรม |
| ผล Shared UI | ผ่าน 18 / ตก 1 / skip 0 จาก 19 | ผ่าน 18 / ตก 1 / skip 0 จาก 19 | จริง: tests.json; ใช้ shared-tests-v2.json hash เดียวกัน |
| N−1/N ในสามรอบ | 6/6 fixture ผ่าน | 6/6 fixture ผ่าน | จริง: TS-US-21-101–106; ยังไม่ครบทุก AC US-21 |
| ข้อผิดพลาด UI ที่พบ | 1: TS-US-09-101 ไม่พบ payment-summary-total | 1: TS-US-09-101 ไม่พบ payment-summary-total | จริง: runner assertions; ต้องแยก UI/fixture mismatch ต่อ |
| รูปแบบ scenarios ที่ AI ผลิต | ดัชนี role→Markdown ไม่ใช่ executable action array | steps เป็นข้อความ ไม่ตรง runner action/testid | จริง: JSON และโค้ด runner; ไม่ใช้ไฟล์เหล่านี้แทนชุดร่วมที่ผู้ทดลองตรึง |
| ข้อค้างด้านเกณฑ์ | รอยต่อ clock 00/15/30/45; ยืนยันใบถัดไปหลังเต็ม; server/LAN และอื่น ๆ | เหมือนกัน พร้อมทะเบียน gap จาก evaluate | ไม่มีข้อมูล runtime ของเกณฑ์ที่ไม่ได้รัน; แผนหรือ source ไม่ใช่ผลผ่าน |
| สถานะรวม | STOP_WITH_GAPS ตามผลตรวจภายนอก | STOP_WITH_GAPS ตาม evaluate | จริง: มี regression ตกและเกณฑ์ไม่ครบ |
| ต้นทุนเงิน | ไม่มีข้อมูล | ไม่มีข้อมูล | ไม่มีข้อมูล: ไม่มีตารางราคาที่ตรวจสอบได้ |
| ผลของนักศึกษา | ไม่มีข้อมูล | ไม่มีข้อมูล | ไม่มีข้อมูล: ชุดนี้เป็น reference |

## รายการหลักฐานและนิยาม

- [step-03-change-single/prompt-used.md](step-03-change-single/prompt-used.md) — `007_LAB_Evaluation_Compare_Workflows/reference/step-03-change-single/prompt-used.md`
- [step-03-change-single/log.jsonl](step-03-change-single/log.jsonl) — `007_LAB_Evaluation_Compare_Workflows/reference/step-03-change-single/log.jsonl`
- [step-03-change-single/meta.json](step-03-change-single/meta.json) — `007_LAB_Evaluation_Compare_Workflows/reference/step-03-change-single/meta.json`
- [step-03-change-single/impact.md](step-03-change-single/impact.md) — `007_LAB_Evaluation_Compare_Workflows/reference/step-03-change-single/impact.md`
- [step-03-change-single/tests.json](step-03-change-single/tests.json) — `007_LAB_Evaluation_Compare_Workflows/reference/step-03-change-single/tests.json`
- [step-03-change-single/ui-run-meta.json](step-03-change-single/ui-run-meta.json) — `007_LAB_Evaluation_Compare_Workflows/reference/step-03-change-single/ui-run-meta.json`
- [step-03-change-single/check-report.md](step-03-change-single/check-report.md) — `007_LAB_Evaluation_Compare_Workflows/reference/step-03-change-single/check-report.md`
- [step-04-change-dynamic/prompt-used.md](step-04-change-dynamic/prompt-used.md) — `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/prompt-used.md`
- [step-04-change-dynamic/log.jsonl](step-04-change-dynamic/log.jsonl) — `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/log.jsonl`
- [step-04-change-dynamic/meta.json](step-04-change-dynamic/meta.json) — `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/meta.json`
- [step-04-change-dynamic/execute/log.jsonl](step-04-change-dynamic/execute/log.jsonl) — `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/execute/log.jsonl`
- [step-04-change-dynamic/execute/meta.json](step-04-change-dynamic/execute/meta.json) — `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/execute/meta.json`
- [step-04-change-dynamic/evaluate/log.jsonl](step-04-change-dynamic/evaluate/log.jsonl) — `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/evaluate/log.jsonl`
- [step-04-change-dynamic/evaluate/meta.json](step-04-change-dynamic/evaluate/meta.json) — `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/evaluate/meta.json`
- [step-04-change-dynamic/plan-v4.json](step-04-change-dynamic/plan-v4.json) — `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/plan-v4.json`
- [step-04-change-dynamic/impact-analysis-change.md](step-04-change-dynamic/impact-analysis-change.md) — `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/impact-analysis-change.md`
- [step-04-change-dynamic/round-0/execution.md](step-04-change-dynamic/round-0/execution.md) — `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/execution.md`
- [step-04-change-dynamic/round-0/tests.json](step-04-change-dynamic/round-0/tests.json) — `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/tests.json`
- [step-04-change-dynamic/round-0/ui-run-meta.json](step-04-change-dynamic/round-0/ui-run-meta.json) — `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/ui-run-meta.json`
- [step-04-change-dynamic/evaluation-round-0.md](step-04-change-dynamic/evaluation-round-0.md) — `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/evaluation-round-0.md`
- [change-artifact-check.json](change-artifact-check.json) — `007_LAB_Evaluation_Compare_Workflows/reference/change-artifact-check.json`
- [shared-tests-notes.md](shared-tests-notes.md) — `007_LAB_Evaluation_Compare_Workflows/reference/shared-tests-notes.md`
- [shared-test-baseline-dom.json](shared-test-baseline-dom.json) — `007_LAB_Evaluation_Compare_Workflows/reference/shared-test-baseline-dom.json`
- [publication-meta.json](publication-meta.json) — `007_LAB_Evaluation_Compare_Workflows/reference/publication-meta.json`

## ข้อจำกัดการเปรียบเทียบ

Baseline FR มี 21 US ขณะที่แผนก่อนเปลี่ยนมี 26 US; shared suite 19 fixture ไม่แทนทั้ง 26 US. scenario baseline ที่ส่งเป็นดัชนี และ manifest อ้างสัญญาเดิมที่ไม่มีไฟล์ จึงต้องบันทึกเป็นข้อผิดพลาดร่วมของ input
ชุดตรวจแรกตรึงหลัง AI เริ่มแล้ว; รุ่น v2 แก้ setup ตาม DOM baseline ก่อนรันจริง โดยคง expected และ regression. ไม่ใช่ controlled trial สมบูรณ์; Single และ Dynamic plan เริ่มพร้อม Rubric ทำให้ wall อาจได้รับผลจากโหลดร่วม
ค่าเวลา end-to-end มีจุดจบต่างกันเพราะ Dynamic มี evaluate; ใช้ดูภาระกระบวนการครั้งนี้ ไม่แปลเป็นความเร็วสร้าง UI ล้วน. เวลาจัดเตรียมชุดทดลอง/DOM inspection/ผู้ตรวจไม่ถูกวัดครบ จึงไม่มีข้อมูลต้นทุนดำเนินการทั้งหมด
LAB 006 ผลเดิมยังผ่าน 12 ตก 2; 18/1 ที่นี่เป็นผลทดสอบใหม่ด้วย fixture ร่วมที่ต่างจากเดิม. ไม่มีการสรุปว่าความซับซ้อนมากขึ้นทำให้ผลดีกว่าเสมอ
ชื่อ key ของแผนและถ้อยคำ scenarios รุ่นเผยแพร่ปรับตาม publication-meta.json หลัง evaluate; เก็บข้อความ/hash รุ่นที่ใช้รันไว้ใน publication-source/log.jsonl. HTML/ผลทดสอบ/คะแนน/ค่าทรัพยากรไม่เปลี่ยน
