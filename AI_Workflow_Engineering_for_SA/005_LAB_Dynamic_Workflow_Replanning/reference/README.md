# หลักฐานรันล่วงหน้า LAB 005

Path เต็มใน prompt-used/plan-*/evaluator เป็น path เครื่องที่รันล่วงหน้า ให้อ่านเป็น `<LAB_ROOT>`; คงไฟล์หลักฐานเดิมเพราะผูก SHA-256

รันจริงวันที่ **14 กันยายน 2026 (UTC)** ด้วย **Codex CLI 0.154.0** โมเดล **gpt-6-astra (ตาม flag ที่สั่ง CLI ไม่ยืนยันกลับ)**, effort **high**.
แต่ละ Planner, Executor และ Evaluator เริ่ม session ใหม่ตามลำดับ โดยไม่ resume. ใช้ Python 3, jsonschema, Playwright/Chromium ผ่าน file:// และ Node.js wrapper ของตัวตรวจ.
คำสั่งกลางสำหรับทำซ้ำ: `codex exec --json -m gpt-6-astra -c model_reasoning_effort="high" -o summary.md "$(cat prompt-used.md)" </dev/null > log.jsonl 2>stderr.txt`.
ใช้ working directory ของแต่ละขั้น และปรับ path ใน prompt ให้ตรงสำเนาที่ใช้จริง.

## สถานะและหลักฐาน

| ขั้น | ผลจริง | หลักฐาน |
|---|---|---|
| เตรียม Input | Audit 3 รอบ: BLOCKED → BLOCKED → INPUT_READY เฉพาะเอกสาร/mock | [ต้นทางและ SHA](step-00-input/provenance.md), [baseline ที่ใช้](step-00-input/baseline-filtered-v2/provenance.md), [รอบสุดท้าย](step-00-input/round-3/summary.md) |
| plan-v1 | 8 tasks; schema/DAG ผ่าน; Evaluator PLAN_READY | [JSON](step-01-plan-v1/plan-v1.json), [Markdown](step-01-plan-v1/plan-v1.md), [schema](step-01-plan-v1/schema-check.json), [Evaluator](step-01-plan-v1/evaluation/summary.md) |
| execute-v1 | ทำ 2 งาน; FR PASS, Flow FAIL F-01, outline BLOCKED จาก Flow | [FR audit](step-02-execute-v1/audit-fr-baseline/evaluator.md), [outline](step-02-execute-v1/draft-test-outline/evaluator.md) |
| reveal-1 | เปิดหลังตรวจ v1: 2026-09-14T12:59:16.228451Z | [ข้อมูล](step-03-reveal-1/reveal-1.md), [เวลาเปิด](step-03-reveal-1/meta.json) |
| plan-v2 | 11 tasks; US-09/14/21; impact 11 แถว; PLAN_READY | [JSON](step-04-plan-v2/plan-v2.json), [Markdown](step-04-plan-v2/plan-v2.md), [impact](step-04-plan-v2/impact-analysis.md), [Evaluator](step-04-plan-v2/evaluator.md) |
| execute-v2 | FR/Flow/outline ผ่าน; F-01 closed; UI regression 19/19 และฟีเจอร์ 8/8 ในขอบเขตจำลอง | [FR](step-05-execute-v2/fr-nfr-v2.md), [Flow](step-05-execute-v2/flow-v2.md), [UI เปิดเล่น](step-05-execute-v2/ui-mockup-v2.html), [Evaluator](step-05-execute-v2/evaluator.md), [handoff](session/evaluations/handoff-v2.md) |
| reveal-2 | เปิดหลังผลตรวจ v2: 2026-09-14T14:01:50.953728Z | [ข้อมูล](step-06-reveal-2/reveal-2.md), [เวลาเปิด](step-06-reveal-2/meta.json) |
| plan-v3 | 13 tasks; วิเคราะห์ US-17/18/22/23/24; schema/DAG ผ่าน; PLAN_READY เฉพาะเอกสารวิเคราะห์; ยังไม่ execute | [JSON](step-07-plan-v3/plan-v3.json), [Markdown](step-07-plan-v3/plan-v3.md), [impact](step-07-plan-v3/impact-analysis-v3.md), [Evaluator](step-07-plan-v3/evaluation/evaluator.md) |
| กิจกรรมปรับ Prompt ก่อน–หลัง 5.6 | ตัวอย่างประกอบ — ยังไม่ได้รันจริง; ไม่มีข้อมูล | การแก้ปัญหารันด้านล่างไม่ใช่การทดลองแบบควบคุม |

## การเก็บรุ่นและเหตุที่มีหลายรอบ

1. ใช้ไฟล์จริงจาก reference ของ LAB 002–004 โดย UI มาจาก LAB 004 `reference/final/ui-mockup.html` ตาม [provenance](step-00-input/provenance.md). เก็บสำเนาต้นฉบับไว้ก่อนกรอง. Audit พบรายละเอียด reveal ในคำอธิบาย Flow จึงสร้าง baseline-filtered และ baseline-filtered-v2 พร้อม diff/hash; ครั้งที่สามจึงส่งต่อได้. การกรองไม่แก้ US/AC ที่เปิดแล้ว.
2. ผล v1 ไม่ผ่านทั้งสาย: FR ผ่าน แต่ Flow ขาด US-11/FR-11/MRG-05 → หน้าร้าน (F-01). เก็บ FAIL และ outline BLOCKED เป็นหลักฐานให้ v2 แก้ mapping ใน Flow/state/structure.
3. การคัด reveal-1 ครั้งแรกไม่จบเพราะตัวแปรสคริปต์; [บันทึกความพยายามแรก](step-03-reveal-1/copy-attempt-1-log.jsonl) ถูกเก็บไว้. เวลาเปิดอย่างสำเร็จใช้ meta ของขั้น ไม่แต่งเวลา.
4. Prompt รวม plan-v2 มี CURRENT_PLAN ค้างในส่วนวิเคราะห์ แม้คำสั่งท้ายผูก v2. จึงรัน [รอบตรวจ impact เพิ่ม](step-04-plan-v2/round-2/impact-analysis-review.md) ด้วย placeholder ที่แทนครบ. พบ locator ราคา snapshot ควรอ่านบรรทัด 103 แทน 102 ใน hash เดิม; บันทึกไว้โดยไม่แก้ plan/impact เก่า.
5. Outline v2 ถูกสร้างใน directory ของขั้นก่อนส่งต่อ จึงคัดลอก byte-identical ไปตำแหน่งที่ plan ระบุ พร้อม [artifact-transfer](step-05-execute-v2/draft-test-outline/artifact-transfer.json). ไม่เปลี่ยนข้อความหรือแก้ JSON เพื่อให้ตรงผล.
6. ชุดตรวจฟีเจอร์ UI รอบแรกได้ 7/8 เพราะ locator ตัวตรวจจับ item-state หลายตำแหน่ง. เก็บ script/report เดิม; รุ่นแก้เจาะ item-resolution ได้ [8/8](step-05-execute-v2/ui-browser/round-2/ui-feature-check-v2.json). [diff และ hash ตัวตรวจ](step-05-execute-v2/ui-browser/script-revisions.json) ยืนยันว่า UI ไม่เปลี่ยน.
7. Evaluator รัน Node wrapper ที่เรียก Python checker เดิมและชุดฟีเจอร์ที่แก้ scope ใน directory ใหม่อีกครั้ง: [observations](session/execution/ui-v2-observations.json), [script](session/execution/ui-checks-v2.spec.js). การรันซ้ำเป็นการยืนยัน ไม่เพิ่มจำนวนสถานการณ์ไม่ซ้ำ.

## เวลาและโทเคน

[metrics.csv](metrics.csv) มี **22 การเรียกโมเดล**, รวม wall **5,631.365 วินาที**, input **20,152,663**, output **278,721** จาก `turn.completed.usage` เท่านั้น.
แต่ละรอบมี log.jsonl, prompt-used.md, meta.json และ run-meta.json ที่จับเริ่ม/จบ/วินาทีจริง. ตรวจว่าไม่มี turn.failed ก่อนนำผลไปใช้.
Input รวมส่วน cache ตามที่ CLI รายงาน; ไม่ใช่โทเคนใหม่ทั้งหมดหรือเงินที่จ่าย. ต้นทุนเงินไม่มีข้อมูล.
[สคริปต์นับหลักฐาน](count-evidence.py) ทำซ้ำได้โดย `python3 count-evidence.py --out metrics-round-2.csv`; ป้องกันเขียนทับ CSV ที่มีอยู่.
การคัดไฟล์ เปิด reveal ตรวจ browser และรวบรวมหลักฐานมี event กับเวลาแยกกัน ไม่สร้าง turn.completed หรือสมมติโทเคน.
[ตรวจ JSON events](model-event-check.json) ผ่านทั้ง 22 การเรียก มี turn.failed จริง 0 เหตุการณ์. [สคริปต์](check-model-events.py) ตรวจ field type ตรงตัวและแสดงตำแหน่งที่ regex จับข้อความใน command output ผิดเป็นสถานะ.
ตัวตรวจ `grep 'turn.failed'` มีจุด wildcard จึงจับ `return failed_ids` ที่อยู่ในโค้ด Python ซึ่งพิมพ์ลง log; ข้อความนี้ไม่ใช่ event ล้มเหลว. ชุดตรวจข้อความเดิมจึงไม่ผ่านที่ UI v2 แต่การตรวจแบบ literal `grep -Fq` ผ่าน. raw log เดิมไม่ถูกแก้หรือย้ายเพื่อเปลี่ยนผลตรวจ.

meta ชนิด evidence.collection ในโฟลเดอร์เก็บไฟล์เป็นเวลาจัดทำดัชนีเท่านั้น ไม่ใช่เวลาสร้างชิ้นงานหรือเวลาโมเดล.

## UI ภาพ และข้อจำกัด

[เปิด UI v2](step-05-execute-v2/ui-mockup-v2.html), [contract](step-05-execute-v2/ui-contract-v2.md), [regression 19/19](step-05-execute-v2/ui-check-v2.json), [ฟีเจอร์ 8/8](step-05-execute-v2/ui-feature-check-v2.json), [ตรวจภาพ](step-05-execute-v2/ui-browser/visual-review.json).
ภาพใหม่อยู่ [img](../README.md#ขั้น-54--ปรับ-frnfr-flow-และ-ui-v2-พร้อมตรวจ) ในบทเรียน; ภาพรอบผ่านมี 8 ภาพ ทุกภาพมากกว่า 10 KB. เวลา 1 มกราคมที่เห็นใน UI คือ fixture; เวลาที่รันจริงคือ 14 กันยายนใน meta.
ภาพเทียบครัว v1/v2 ใช้ viewport และ order/clock เดียวกันผ่าน file://. มีภาพปุ่มทำไม่ได้ รายการรอตัดสินใจ แจ้งลูกค้า ครัวเต็ม หน้าผู้จัดการ ยอดปรับ และมือถือ.

เอกสาร v2 ครบ 21 US และคง AC เดิม; ค่า X=10, เขตเวลา +07, หนึ่งรายการต่อจาน และการรับออเดอร์ต่อหลังถึง N เป็น fixture ที่ติดป้าย.
ผล 8/8 คือ 6 สถานการณ์รวม N=5 ซ้ำ 3 รอบเวลา 12:00; ตรวจขอบหน้าต่างอื่นแยก แต่ไม่อ้างว่าครบทุกกรณีของ outline หรือครบสัดส่วน AC บน LAN.
ไม่ได้ทดสอบ LAN/Wi-Fi/SLA/อุปกรณ์ร้าน/ความปลอดภัยจริง/เงินจริง/คืนเงินจริง/ETA เต็มสูตร/ติดตั้ง US-26. คำถามธุรกิจและหมายเหตุ ก./ค./ช. ที่หายยังรอคำตอบ.
v3 เป็นการวางแผนและวิเคราะห์ผลกระทบเท่านั้น; ยังไม่มี FR/Flow/UI v3 หรือผล runtime v3.

ใช้ `reference/session/` เป็นพื้นที่ทำงานของรอบนี้เพื่อคงหลักฐานรุ่นเดิมและจำกัดการเขียน. `work/` ของ LAB เหลือเพียง .gitkeep.
JSON ทุกแผนมาจาก nested CLI; สำเนาหลักตรง hash เดิม ไม่แก้ JSON ด้วยมือ. [บัญชีไฟล์และ SHA](artifact-manifest.json) ใช้ตามรอยไฟล์ทั้งหมด.
