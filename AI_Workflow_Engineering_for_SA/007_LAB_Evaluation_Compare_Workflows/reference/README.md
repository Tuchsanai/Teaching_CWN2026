# ผลรันล่วงหน้า LAB 007

วันที่ UTC: 2026-09-14
เครื่องมือ: Codex CLI 0.154.0; Python collect-metrics.py; Playwright ผ่าน tests/run-scenarios.py ของ LAB 006
โมเดล: gpt-6-astra (ตาม flag ที่สั่ง CLI ไม่ยืนยันกลับ); reasoning effort: high
ผลในโฟลเดอร์นี้เป็น reference ของผู้จัดทำ ไม่ใช่ผลนักศึกษา; แต่ละ phase รันครั้งเดียว ไม่ใช่ค่าเฉลี่ย

| ขั้น | สถานะ | หลักฐาน |
|---|---|---|
| 1 เก็บ metrics | สำเร็จ 85 แถว ครบ LAB 001–006; ข้อมูลบางช่องขาด | [CSV](metrics.csv), [เงื่อนไข](step-01-metrics/metrics-notes.md) |
| 2 Rubric | AI ให้ครบ 35 แถว; พบไฟล์จริงครบ 38 path; รอคนตรวจคะแนน | [Rubric](rubric-filled.md), [ตรวจ path](step-02-rubric/verification.md) |
| 3 Single | ผลิตครบ; UI ผ่าน 18 ตก 1; STOP_WITH_GAPS | [FR ฉบับแก้](step-03-change-single/fr-nfr-v3.md), [ผลตรวจ](step-03-change-single/check-report.md) |
| 4 Dynamic | ครบ plan/execute/evaluate; UI ผ่าน 18 ตก 1; STOP_WITH_GAPS | [plan-v4](step-04-change-dynamic/plan-v4.json), [ผลตรวจ](step-04-change-dynamic/round-0/check-report.md) |
| 5 Report | สำเร็จ 174 บรรทัด ครบ 7 LAB | [รายงาน](comparison-report.md), [log](step-05-report/log.jsonl), [meta](step-05-report/meta.json) |

## วิธีอ่านค่าจริงและข้อจำกัด

- [metrics.csv](metrics.csv) เป็นสำเนาตรงจาก collect-metrics.py เก็บ snapshot ก่อนเริ่ม AI ของ LAB 007 ไม่เติมค่าด้วยมือ
- [lab-metrics.csv](lab-metrics.csv) เป็นทรัพยากรของ LAB นี้ตามขั้น สร้างด้วย [collect-run-metrics.py](collect-run-metrics.py); โทเคนอ่าน turn.completed/turn.failed usage และเวลาจาก meta ของการเรียกจริง
- เวลา step-01 จาก wall_time_seconds ของเครื่องมือเรียกคำสั่ง รวมเริ่ม shell/redirection; ขั้น AI จับด้วย monotonic รอบ subprocess; ไม่มีข้อมูลเป็นคนละความหมายกับศูนย์
- [environment](experiment-environment.json) บันทึกลำดับรัน: Rubric/Single/Dynamic plan เริ่มขนานกัน จึงไม่ใช่สภาพแวดล้อมที่แยกโหลด
- ต้นทุนเงินไม่มีข้อมูล เพราะไม่มีตารางราคาที่ตรวจสอบได้; cached input ไม่บวกซ้ำกับ input
- [baseline manifest](change-baseline/manifest.md) และ [conditions](change-conditions.md) ระบุ input/แผน/รุ่น/hash ร่วม โดยเก็บข้อบกพร่องเดิมไว้
- [ชุดตรวจร่วมรุ่น v2](shared-tests-v2.json) ใช้กับทั้งสองวิธี; [ที่มาและการปรับ setup](shared-tests-notes.md) อธิบายว่าตรึงหลังเริ่ม AI และ baseline scenario ที่ให้เป็นดัชนีเอกสาร
- 18/1 เป็นผล fixture mock ใหม่ของ LAB 007; ผลเดิม LAB 006 ยังคง 12/2. ยังไม่วัดครบ clock boundary/การยืนยันหลังเต็ม/ระบบจริง
- คะแนน Rubric เป็นประมาณโดย AI ตาม snapshot ก่อนจบการทดลอง/รายงาน ไม่แก้คะแนนย้อนหลัง; path verification ไม่ใช่การตรวจคะแนนซ้ำโดยคน
- [coverage counts](coverage-evidence-counts.json) นับรหัส US ตามไฟล์ที่ลิงก์กับ ✓ เดิม; [สำเนา traceability](coverage-source-traceability.csv) มาจาก LAB 006 สำหรับประเมิน ไม่ใช่รันใหม่

## คำสั่งกลางสำหรับรันซ้ำ

รันจากโฟลเดอร์ขั้นที่เตรียม prompt-used.md แล้ว ใช้โฟลเดอร์ผลรุ่นใหม่เพื่อเก็บหลักฐานเดิม:

```bash
codex exec --json -m gpt-6-astra -c model_reasoning_effort="high" -o summary.md "$(cat prompt-used.md)" </dev/null > log.jsonl 2> stderr.txt
```

ตัวอย่างนี้ไม่วัดเวลาเอง ผู้ทดลองต้องจับ wall time และสร้าง meta.json รอบคำสั่ง พร้อมตรวจ turn.completed และไม่มี turn.failed ก่อนใช้ผล
Dynamic ใช้ cwd ของ step-04-change-dynamic ทุก phase โดยแยก prompt/log/meta ของ execute/ และ evaluate/; ไม่ resume session
เก็บ snapshot/hash ก่อนรันชุดใหม่ และแยกผลนักศึกษาจาก reference ชุดนี้

[ตารางเปรียบเทียบข้อเปลี่ยน](change-compare.md) รวมทุก phase; [ประวัติรุ่นเผยแพร่ JSON](publication-meta.json) และ [ข้อความก่อนปรับ](publication-source/log.jsonl) เก็บต้นฉบับที่ใช้ตรวจโดยไม่เปลี่ยนตัวเลข/คะแนน/HTML

## ค่าทรัพยากร LAB 007 หลังจบทุกขั้น

| step | duration_s | input_tokens | output_tokens |
|---|---|---|---|
| step-01-metrics | 1.522843869 | ไม่มีข้อมูล | ไม่มีข้อมูล |
| step-02-rubric | 284.932 | 1288765 | 14155 |
| step-03-change-single | 411.758 | 1420196 | 20384 |
| step-04-change-dynamic/evaluate | 196.386 | 785183 | 9120 |
| step-04-change-dynamic/execute | 304.658 | 852970 | 15295 |
| step-04-change-dynamic | 206.7 | 320947 | 11163 |
| step-05-report | 319.155 | 1061529 | 16262 |

AI ทุกการเรียกมี turn.completed และไม่มี turn.failed; ผล UI ที่ตกเป็นคนละความหมายกับการเรียก CLI ล้มเหลว. บันทึกเวลารัน browser แยกใน ui-run-meta.json ไม่รวมซ้ำในตาราง AI. lab-metrics-before-report.csv เป็น snapshot ที่ส่งให้ผู้เขียนรายงาน; lab-metrics.csv รวมการเขียนรายงานที่เพิ่งจบด้วย

## รูปแบบ log และสำเนาดิบ

Rubric และ Report มีตัวอย่างข้อความชื่อ event ล้มเหลวอยู่ภายในผลอ่านเอกสาร จึง serialize log.jsonl ใหม่ด้วย Unicode escape ในข้อความที่อ้างนั้น เพื่อให้การค้นข้อความไม่สับสนกับ event จริง. ตรวจ JSON แล้วค่าทุก event/string เท่ากับต้นฉบับ และ actual failed events เป็น 0. เก็บ log-original.jsonl.gz กับ log-format.json ข้าง log ทั้งสองขั้น ไม่ใช้ไฟล์บีบอัดบวกยอดซ้ำ
