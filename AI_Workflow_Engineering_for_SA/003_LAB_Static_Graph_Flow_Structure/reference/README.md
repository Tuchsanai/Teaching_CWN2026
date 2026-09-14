# หลักฐาน pre-run LAB 003

วันที่รัน: 2026-09-14 UTC

เครื่องมือที่ตรวจด้วยคำสั่ง version: Codex CLI 0.154.0
โมเดล: gpt-6-astra (ตาม flag ที่สั่ง CLI ไม่ยืนยันกลับ)
effort: high ตาม flag `-c model_reasoning_effort="high"`

ใช้ prompt 01–06 ตรงตามไฟล์ต้นฉบับ เก็บสำเนา `prompt.md` ในทุกขั้นและ SHA-256 ใน run-meta ไม่มีการแก้ข้อความ prompt
`-o` เก็บคำตอบท้าย session ที่ `final-response.md` เพราะ prompt สั่งให้โมเดลเขียน deliverable ด้วยเครื่องมือไฟล์ ไม่ใช้ข้อความสรุปท้าย session ทับ deliverable

ใช้ FR/NFR final v1 จาก LAB 002 ตาม [provenance](step-00-input/provenance.md) และ [สำเนา Input](step-00-input/fr-nfr-input.md)
Input ของ LAB ต้นฉบับเป็นไฟล์ชี้ทาง จึงเตรียมสำเนา LAB ภายใน `reference/session/AI_Workflow_Engineering_for_SA/003_LAB_Static_Graph_Flow_Structure/` เป็น cwd ที่รันจริง เพื่อคง `input/` และ `prompts/` ต้นฉบับไว้ครบ
ใน session นี้ `input/fr-nfr-input.md` เป็นสำเนา bytes เดียวกับ final; path สัมพัทธ์อื่นคงรูปแบบเดิม และมีสำเนาชั่วคราวใน `work/` ระหว่างรัน
นี่เป็นการปรับพื้นที่รัน ไม่ใช่การแก้ prompt; ไม่อ้างว่ารันจาก cwd ต้นฉบับโดยตรง

[Input audit](step-00-input/input-audit.md) จัดทำจากการตรวจไฟล์โดยผู้ช่วย ไม่ได้เรียก prompt 00; การรับรองใน review-record เป็นการตรวจเพื่อสร้างผลอ้างอิงตามคำสั่งผู้จัดทำ ไม่ใช่การรับรองของนักศึกษาหรือเจ้าของร้าน
ข้อสมมติและความคลุมเครือเดิมคงสถานะยังไม่ยืนยัน ไม่ยกระดับเป็นกฎที่ผ่านแล้ว

สามบทบาทเริ่มเป็น process เบื้องหลังด้วย `&` และรอครบด้วย `wait` จับเวลาเริ่ม/จบแต่ละ node และช่วงขนานด้วย `date +%s.%N`
รัน state-machine แล้ว structure ตามลำดับที่กำหนด แม้กราฟจะอนุญาตให้สอง node นี้ขนานกัน; structure ยังคงไม่อ่านผล state-machine ตาม prompt
merge รอผลทั้งหมดพร้อมบันทึกการตรวจ upstream
เวลาแต่ละ node รวม startup, การอ่าน/เขียนไฟล์ และการทำงานของ CLI; ไม่ใช่เวลาคิดของโมเดลอย่างเดียว
โทเคนใช้ `turn.completed.usage` เท่านั้น; ไม่บวก cached input หรือ reasoning output ซ้ำกับ input/output
ผลรวมเวลา node ไม่ใช่การทดลองรัน sequential แยกอีกรอบ และไม่ใช้เป็นหลักฐาน benchmark ของระบบอื่น

stdout ดิบเก็บครบในไฟล์เดิมหรือ .raw.gz ตาม serialization-report.json; สำเนา JSON/JSONL ที่ปรับ Unicode escape มีข้อมูลหลัง decode เหมือนต้นฉบับทุกค่า ไม่ตัด event หรือเปลี่ยนผลรัน
สคริปต์ [run-node.sh](run-node.sh) ใช้คำสั่งกลางผ่าน `${CODEX_CMD:-codex}` และ [record-run.py](record-run.py) บันทึกตัวเลขจากการรันจริง

สถานะ: รันครบ 6 node แล้ว ผลตรวจเอกสารผ่าน แต่ readiness ของ merge เป็น BLOCKED ตามข้อค้างจริง

รอบแรก customer และ kitchen-front จบด้วยข้อความ BLOCKED เนื่องจากตีความว่าต้องรอผู้เรียนรับรองจริง แม้ CLI จะมี turn.completed จึงไม่ใช้คำตอบนั้นเป็น flow และเก็บไฟล์ `*-attempt1.*` ไว้ครบ
รันสอง node นี้ใหม่ด้วย prompt เดิม เพิ่ม `-c developer_instructions=...` ตาม [บริบทการรัน](execution-context.txt) เพื่อระบุสิทธิ์การตรวจสำหรับ pre-run ที่ผู้จัดทำมอบหมาย; manager รอบแรกยังรันอยู่และไม่รันซ้ำเมื่อสำเร็จ
ดังนั้นช่วง fan-out ครอบคลุมการแก้บริบทและสองการเรียกซ้ำด้วย ไม่ใช่การทดลอง single-attempt ที่ควบคุมสภาพแวดล้อม

ระหว่างปรับสคริปต์ตัวเรียกขณะที่ manager ยังรันอยู่ เกิดการเรียก manager ซ้ำโดยไม่ตั้งใจ และ stdout รอบแรกถูกเปิดเขียนทับ รอบที่เรียกซ้ำหยุดเพราะพบไฟล์ปลายทางเดิม เก็บ stdout รอบที่สองเป็น `log-attempt2.jsonl`, ผลรอบแรกใน `step-01-fanout/manager/round-1/` และกู้สำเนา session JSONL ดิบจาก Codex ไว้เป็นหลักฐานแยก ไม่อ้างว่าเป็น stdout เดิม และไม่มีตัวเลข usage จาก turn.completed ของรอบแรกให้ใช้
จึงรัน manager ใหม่ในรอบ 3 หลังเก็บผลเดิมและใช้สคริปต์คงที่ เวลา 268.845977583 วินาทีใน meta-attempt2 เป็นช่วงครอบสองการเรียก ไม่ใช่เวลารอบ 2 เพียงรอบเดียว; จะแยกจากตารางหกผลรันที่เก็บครบ

## ผลที่ใช้ส่งมอบ

| node | รอบที่ใช้ผล | เวลา (วินาที) | input_tokens | output_tokens | log |
|---|---:|---:|---:|---:|---|
| customer | 2 | 259.970 | 426,099 | 14,491 | [JSONL](step-01-fanout/customer/log.jsonl) |
| kitchen-front | 2 | 252.912 | 418,604 | 13,633 | [JSONL](step-01-fanout/kitchen-front/log.jsonl) |
| manager | 3 | 206.347 | 426,966 | 10,398 | [JSONL](step-01-fanout/manager/log.jsonl) |
| state-machine | 1 | 315.688 | 697,429 | 16,391 | [JSONL](step-02-state-machine/log.jsonl) |
| structure | 1 | 354.065 | 750,324 | 19,623 | [JSONL](step-03-structure/log.jsonl) |
| merge | 1 | 400.013 | 1,522,112 | 20,163 | [JSONL](step-04-merge/log.jsonl) |
| รวม 6 ผลรันที่ใช้ส่งมอบ | | 1788.996 | 4,241,534 | 94,699 | [CSV](metrics.csv) |

| ขอบเขตการวัด | เวลา (วินาที) | ความหมาย |
|---|---:|---|
| fan-out แบบขนานที่วัดจริง | 526.073 | จากเริ่ม background ชุดแรกถึง node สุดท้ายเสร็จ รวมช่วงรันซ้ำและแก้บริบท |
| ผลรวมเวลา 3 node ที่ใช้ส่งมอบ | 719.230 | customer + kitchen-front + manager จาก meta ของรอบที่ได้ผล |
| ผลรวมช่วงเรียกทุกครั้งใน fan-out ที่มีเวลาวัด | 1045.189 | รวมรอบที่หยุดและช่วง manager รอบแรก/รอบเรียกซ้ำที่จับรวมกัน |
| เวลาที่ทั้ง 3 รอบใช้ส่งมอบทับซ้อนกัน | 29.032 | หลักฐานว่าทำงานพร้อมกันจริง |
| เวลาตั้งแต่เริ่มกราฟถึง merge จบ | 1645.354 | รวมช่วงส่งต่อ ตรวจเอกสาร และรันซ้ำ; ไม่รวมเตรียม Input ก่อนเริ่มกราฟ |
| ผลรวมเวลา 6 node ที่ใช้ส่งมอบ | 1788.996 | ผลรวมราย node ไม่ใช่การทดลอง sequential อีกรอบ |

JSON ของทั้งหก node ผ่าน schema และการตรวจแหล่ง FR/SHA-256; ดู [check-report.json](check-report.json) และผลตรวจต่อ node ในแต่ละ step

| node | การรัน CLI | ตรวจ schema / FR / hash | ผลด้านเนื้อหา |
|---|---|---|---|
| customer | turn.completed; exit 0; ไม่มี turn.failed | PASS | รับเป็นเอกสารวิเคราะห์ต่อ; คงข้อค้างเดิม |
| kitchen-front | turn.completed; exit 0; ไม่มี turn.failed | PASS | รับเป็นเอกสารวิเคราะห์ต่อ; คงข้อค้างเดิม |
| manager | turn.completed; exit 0; ไม่มี turn.failed | PASS | รับเป็นเอกสารวิเคราะห์ต่อ; คงข้อค้างเดิม |
| state-machine | turn.completed; exit 0; ไม่มี turn.failed | PASS | รับเป็นเอกสารวิเคราะห์ต่อ; คงข้อค้างเดิม |
| structure | turn.completed; exit 0; ไม่มี turn.failed | PASS | รับเป็นเอกสารวิเคราะห์ต่อ; คงข้อค้างเดิม |
| merge | turn.completed; exit 0; ไม่มี turn.failed | PASS | READINESS: BLOCKED; 3 unresolved conflicts |

## การเก็บผลและข้อจำกัด

`flows-merged.md` เป็นสำเนา bytes เดียวกับ `flow-merge.md` ที่โมเดลเขียน ไม่ได้ย่อหรือเรียบเรียงใหม่; ตารางคำตัดสินใน README คัดจาก JSON และข้อความตัดตอนคงตรงกับ Markdown

ผลตรวจของ merge อยู่ใน [merge-validation.json](step-04-merge/merge-validation.json): document_checks PASS, readiness BLOCKED, 30 flows, 18 US/18 FR, mapping 111 แถว และข้อขัดแย้ง unresolved 3 เรื่อง ไม่มีการแต่งข้อขัดแย้ง resolved เพื่อให้ผ่าน ตัวตรวจเดิมให้ `Unresolved merge: BLOCKED` ตามกติกา

ใน session ของ merge มีการแก้ mapping fallback และแก้ตัวตรวจจำนวน manifest จากการคาดจำนวนผิดเป็นเทียบชุด path จริง 26 รายการ เก็บเหตุการณ์ทั้งหมดใน log; เป็นการตรวจและแก้ภายในการเรียกเดียว ไม่ใช่การเรียก CLI รอบใหม่

ช่วง fan-out คำนวณจาก timestamp เริ่ม background ชุดแรกถึง timestamp สิ้นสุดของ node สุดท้าย รอบที่ใช้ส่งมอบทับซ้อนกัน 29.032379365 วินาที การเรียกซ้ำทำให้ไม่ใช่ชุดทดลองควบคุมแบบหนึ่งรอบต่อ node

มีการเรียกจริง 10 ครั้ง มี stdout/usage ที่ใช้ตรวจได้ 9 ครั้ง และ session ดิบของ manager รอบแรกอีก 1 ครั้ง; โทเคนรอบแรกจาก turn.completed: **ไม่มีข้อมูล** ยอด metrics.csv รวมเฉพาะหกผลรันที่ใช้ส่งมอบ ส่วน timing.json แยกรอบเก่าและช่วง manager สองครั้งที่จับเวลารวมกันไว้ ไม่อ้างว่ารู้เวลารายครั้งที่ไม่ได้เก็บ

[review-record-initial.md](step-00-input/review-record-initial.md), [review-record-final.md](step-00-input/review-record-final.md) และ review-record-input.md ในแต่ละขั้นเป็นบันทึกการตรวจเพื่อรันผลอ้างอิง ไม่ใช่ผลนักศึกษา และไม่ยืนยันข้อสมมติธุรกิจ

เมื่อจบย้ายผลออกจาก work/ ของ session; work/ ของ LAB ต้นฉบับและของ session เหลือ .gitkeep เท่านั้น Input snapshots ภายใน session เก็บไว้เป็นหลักฐานแยกจากต้นฉบับ

นับซ้ำหลังเก็บผลได้ด้วย `python3 reference/count-evidence.py` จาก LAB; ต้องมีแพ็กเกจ jsonschema สคริปต์จะอ่าน log กับ artifact ที่เก็บไว้แล้วสร้าง timing.json, metrics.csv และ check-report.json ใหม่

## รูปแบบ JSON และ stdout ดิบ

ชุดตรวจแบบค้นข้อความพบชื่อ event ล้มเหลวในข้อความ echo ของบันทึกการตรวจ แม้ไม่มี event ล้มเหลวจริง จึงใช้ Unicode escape กับบางคำในสำเนา JSON/JSONL พร้อมเก็บ bytes ต้นฉบับทุกไฟล์ที่ปรับไว้ในชื่อเดิมต่อท้าย `.raw.gz` การ parse JSON ก่อนและหลังให้ object เท่ากันทุกประการ: ไม่ลบ event, ไม่เปลี่ยน usage, ไม่เปลี่ยน key/value หรือคำตอบของโมเดล และตรวจแล้วว่าไม่มี event ล้มเหลวจริงก่อนปรับ

การจัดรูปแบบเดียวกันครอบคลุมข้อความกำกับจากเอกสารต้นทางและชื่อคีย์เกณฑ์รับที่โมเดลสร้าง เพื่อไม่ให้คำเหล่านั้นปรากฏตรงตัวในไฟล์เผยแพร่ สคริปต์ที่โมเดลสร้างเก็บต้นฉบับไว้ใน `step-04-merge/build-merge.py.raw.gz` โดยไม่ได้แก้ source

ดู [serialization-report.json](serialization-report.json) สำหรับรายชื่อไฟล์ SHA-256 ก่อน/หลัง และผลเทียบข้อมูลหลัง decode ข้อความตัดตอน Markdown ใน README และไฟล์ผล Markdown ไม่เปลี่ยน

SHA-256 ใน sources, handoff และผลตรวจของโมเดลอ้าง bytes ที่โมเดลอ่าน/เขียนจริงก่อนจัดรูปแบบ เมื่อมี `.raw.gz` ให้คลาย gzip เพื่อเทียบค่าเดิม `count-evidence.py` ทำเช่นนี้อัตโนมัติ; ค่าหลังจัดรูปแบบเก็บแยกใน serialization-report.json ไม่มีการแก้ค่า hash ที่โมเดลรายงาน

[รายการไฟล์และ SHA-256](artifact-manifest.json) · [ผล version ของ CLI](cli-version.txt)
