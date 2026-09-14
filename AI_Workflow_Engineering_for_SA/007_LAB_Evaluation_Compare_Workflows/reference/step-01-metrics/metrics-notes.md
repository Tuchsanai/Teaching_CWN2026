# เงื่อนไขการเก็บ metrics

วันที่ UTC: 2026-09-14T15:19:11.094976+00:00
เครื่องมือเก็บ: /opt/venv/bin/python3 tools/collect-metrics.py; Python 3.12.3
คำสั่ง: `/opt/venv/bin/python3 tools/collect-metrics.py --root .. --out reference/step-01-metrics/metrics.csv --summary reference/step-01-metrics/metrics-summary.md`
Codex CLI 0.154.0; โมเดล gpt-6-astra (ตาม flag ที่สั่ง CLI ไม่ยืนยันกลับ); effort high สำหรับการรันใหม่ของ LAB 007; รุ่นของหลักฐานเดิมให้ดู metadata แต่ละรอบ
pre-run ครั้งเดียวต่อขั้น ไม่ใช่ค่าเฉลี่ย; snapshot นี้เก็บก่อนเริ่มการเรียก AI ของ LAB 007 จึงมี LAB 001–006 เท่านั้น; ค่า LAB 007 อยู่ใน lab-metrics.csv แยก
ต้นทุนเงิน: ไม่มีข้อมูล เพราะไม่มีตารางราคาที่ตรวจสอบได้

## ข้อจำกัดของสคริปต์ที่ใช้จริง
ไม่แก้ tools/: สคริปต์อ่านเฉพาะ log.jsonl จึงไม่ได้นับ log-original.jsonl.gz ซ้ำ แต่สำเนา session กับผลคัดลอก log.jsonl อาจซ้ำกัน ยอดต่อ LAB คือยอดไฟล์ที่สแกน ไม่ใช่ยอดการเรียกที่ตัดซ้ำหรือใบแจ้งหนี้
calls นับ terminal events ไม่ใช่จำนวนรอบ; failed คือ turn.failed ไม่ใช่ rubric FAIL หรือ UI fail
duration_s อ่านเฉพาะ meta.json/run-meta.md ข้าง log ไม่อ่าน run-meta.json หรือ loop-log rounds[]/calls[]; ค่าเหล่านั้นคง ไม่มีข้อมูล ใน CSV ห้ามเติมมือ
reasoning_output_tokens ที่ usage ไม่ส่งคืนเป็น ไม่มีข้อมูล; cached_input_tokens เป็นส่วนหนึ่งของ input ห้ามบวกซ้ำ
lab และ step ระบุที่มา: <lab>/reference/<step>/log.jsonl; ตารางด้านล่างระบุ source ตรงทุกแถว

## ค่าประกอบจากหลักฐานแยก (ไม่เติมกลับ CSV)
LAB 002 loop-log.json ใช้ rounds[]; e1-set/loop-log-e1.json ใช้ rounds[]; schema-compatible ใช้ calls[] ตาม schema ไม่ใช่การเรียกเพิ่ม
LAB 002 หลัก: checker 1 รอบ PASS; e1-set: checker 2 รอบ FAIL → fix → PASS เป็นการทดลองเสริม ไม่รวมเป็นลูปหลัก
LAB 003 parallel-meta.json วัดช่วงขนานสะอาด 268.956333307 s (แสดง 268.956 s); reference/README.md รายงาน wall รวม retry 526.073 s (ประมาณ 526 s เมื่อปัด) เป็นคนละช่วง ไม่บวกกัน
LAB 004 demo-fix-path คือ edge=fix จากข้อบกพร่องที่ฉีดเพื่อสาธิต ไม่ใช่ลูปหลัก
LAB 006 step-05-ui-run/ui-test-results.json: ผ่าน 12 / ตก 2; ไม่ใช่ผ่านทั้งหมด

| LAB | step | source |
|---|---|---|
| 001_LAB_Single_Prompt_Baseline | step-01/round-1 | `001_LAB_Single_Prompt_Baseline/reference/step-01/round-1/log.jsonl` |
| 001_LAB_Single_Prompt_Baseline | step-02/round-1 | `001_LAB_Single_Prompt_Baseline/reference/step-02/round-1/log.jsonl` |
| 001_LAB_Single_Prompt_Baseline | step-03/round-1 | `001_LAB_Single_Prompt_Baseline/reference/step-03/round-1/log.jsonl` |
| 002_LAB_Loop_FR_NFR | e1-set/step-02/round-1 | `002_LAB_Loop_FR_NFR/reference/e1-set/step-02/round-1/log.jsonl` |
| 002_LAB_Loop_FR_NFR | e1-set/step-02/round-2 | `002_LAB_Loop_FR_NFR/reference/e1-set/step-02/round-2/log.jsonl` |
| 002_LAB_Loop_FR_NFR | e1-set/step-03/round-1 | `002_LAB_Loop_FR_NFR/reference/e1-set/step-03/round-1/log.jsonl` |
| 002_LAB_Loop_FR_NFR | step-01/round-1 | `002_LAB_Loop_FR_NFR/reference/step-01/round-1/log.jsonl` |
| 002_LAB_Loop_FR_NFR | step-02/round-1 | `002_LAB_Loop_FR_NFR/reference/step-02/round-1/log.jsonl` |
| 003_LAB_Static_Graph_Flow_Structure | step-01-fanout/customer | `003_LAB_Static_Graph_Flow_Structure/reference/step-01-fanout/customer/log.jsonl` |
| 003_LAB_Static_Graph_Flow_Structure | step-01-fanout/kitchen-front | `003_LAB_Static_Graph_Flow_Structure/reference/step-01-fanout/kitchen-front/log.jsonl` |
| 003_LAB_Static_Graph_Flow_Structure | step-01-fanout/manager | `003_LAB_Static_Graph_Flow_Structure/reference/step-01-fanout/manager/log.jsonl` |
| 003_LAB_Static_Graph_Flow_Structure | step-01-fanout/manager/round-1/session | `003_LAB_Static_Graph_Flow_Structure/reference/step-01-fanout/manager/round-1/session/log.jsonl` |
| 003_LAB_Static_Graph_Flow_Structure | step-02-state-machine | `003_LAB_Static_Graph_Flow_Structure/reference/step-02-state-machine/log.jsonl` |
| 003_LAB_Static_Graph_Flow_Structure | step-03-structure | `003_LAB_Static_Graph_Flow_Structure/reference/step-03-structure/log.jsonl` |
| 003_LAB_Static_Graph_Flow_Structure | step-04-merge | `003_LAB_Static_Graph_Flow_Structure/reference/step-04-merge/log.jsonl` |
| 004_LAB_Conditional_Graph_UI_Mockup | demo-fix-path/round-2 | `004_LAB_Conditional_Graph_UI_Mockup/reference/demo-fix-path/round-2/log.jsonl` |
| 004_LAB_Conditional_Graph_UI_Mockup | review | `004_LAB_Conditional_Graph_UI_Mockup/reference/review/log.jsonl` |
| 004_LAB_Conditional_Graph_UI_Mockup | round-1 | `004_LAB_Conditional_Graph_UI_Mockup/reference/round-1/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | . | `005_LAB_Dynamic_Workflow_Replanning/reference/./log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | session/browser-temp | `005_LAB_Dynamic_Workflow_Replanning/reference/session/browser-temp/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | session/evaluations | `005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | session/evaluations/plan-v1 | `005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/plan-v1/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | session/evaluations/plan-v2 | `005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/plan-v2/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | session/evaluations/plan-v3 | `005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/plan-v3/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | session/execution | `005_LAB_Dynamic_Workflow_Replanning/reference/session/execution/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | session/execution/plan-v1/audit-fr-baseline-run | `005_LAB_Dynamic_Workflow_Replanning/reference/session/execution/plan-v1/audit-fr-baseline-run/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | session/execution/plan-v1 | `005_LAB_Dynamic_Workflow_Replanning/reference/session/execution/plan-v1/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | session/execution/plan-v1/test-outline-run | `005_LAB_Dynamic_Workflow_Replanning/reference/session/execution/plan-v1/test-outline-run/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | session/execution/plan-v2/flow-v2-run | `005_LAB_Dynamic_Workflow_Replanning/reference/session/execution/plan-v2/flow-v2-run/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | session/execution/plan-v2/fr-v2-run | `005_LAB_Dynamic_Workflow_Replanning/reference/session/execution/plan-v2/fr-v2-run/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | session/execution/plan-v2 | `005_LAB_Dynamic_Workflow_Replanning/reference/session/execution/plan-v2/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | session/execution/plan-v2/outline-v2-run | `005_LAB_Dynamic_Workflow_Replanning/reference/session/execution/plan-v2/outline-v2-run/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | session/execution/plan-v2/ui-v2-run | `005_LAB_Dynamic_Workflow_Replanning/reference/session/execution/plan-v2/ui-v2-run/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | session/execution/ui-v2-evaluator-runtime/feature-shots | `005_LAB_Dynamic_Workflow_Replanning/reference/session/execution/ui-v2-evaluator-runtime/feature-shots/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | session/execution/ui-v2-evaluator-runtime/features | `005_LAB_Dynamic_Workflow_Replanning/reference/session/execution/ui-v2-evaluator-runtime/features/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | session/execution/ui-v2-evaluator-runtime | `005_LAB_Dynamic_Workflow_Replanning/reference/session/execution/ui-v2-evaluator-runtime/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | session/execution/ui-v2-evaluator-runtime/regression-shots | `005_LAB_Dynamic_Workflow_Replanning/reference/session/execution/ui-v2-evaluator-runtime/regression-shots/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | session | `005_LAB_Dynamic_Workflow_Replanning/reference/session/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-00-input/baseline-filtered | `005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-00-input/baseline-filtered-v2 | `005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-00-input/baseline-screen | `005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-screen/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-00-input/baseline-ui-run | `005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-ui-run/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-00-input/baseline-ui-run/shots | `005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-ui-run/shots/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-00-input | `005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-00-input/round-2 | `005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/round-2/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-00-input/round-3 | `005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/round-3/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-01-plan-v1/evaluation | `005_LAB_Dynamic_Workflow_Replanning/reference/step-01-plan-v1/evaluation/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-01-plan-v1 | `005_LAB_Dynamic_Workflow_Replanning/reference/step-01-plan-v1/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-02-execute-v1/audit-fr-baseline/evaluation | `005_LAB_Dynamic_Workflow_Replanning/reference/step-02-execute-v1/audit-fr-baseline/evaluation/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-02-execute-v1/audit-fr-baseline | `005_LAB_Dynamic_Workflow_Replanning/reference/step-02-execute-v1/audit-fr-baseline/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-02-execute-v1/draft-test-outline/evaluation | `005_LAB_Dynamic_Workflow_Replanning/reference/step-02-execute-v1/draft-test-outline/evaluation/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-02-execute-v1/draft-test-outline | `005_LAB_Dynamic_Workflow_Replanning/reference/step-02-execute-v1/draft-test-outline/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-02-execute-v1 | `005_LAB_Dynamic_Workflow_Replanning/reference/step-02-execute-v1/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-03-reveal-1 | `005_LAB_Dynamic_Workflow_Replanning/reference/step-03-reveal-1/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-04-plan-v2/evaluation | `005_LAB_Dynamic_Workflow_Replanning/reference/step-04-plan-v2/evaluation/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-04-plan-v2 | `005_LAB_Dynamic_Workflow_Replanning/reference/step-04-plan-v2/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-04-plan-v2/round-2 | `005_LAB_Dynamic_Workflow_Replanning/reference/step-04-plan-v2/round-2/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-05-execute-v2/baseline-import | `005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/baseline-import/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-05-execute-v2/browser-regression | `005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/browser-regression/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-05-execute-v2/browser-regression/shots | `005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/browser-regression/shots/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-05-execute-v2/draft-test-outline/evaluation | `005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/draft-test-outline/evaluation/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-05-execute-v2/draft-test-outline | `005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/draft-test-outline/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-05-execute-v2/evaluation | `005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/evaluation/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-05-execute-v2 | `005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-05-execute-v2/revise-flow/evaluation | `005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/revise-flow/evaluation/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-05-execute-v2/revise-flow | `005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/revise-flow/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-05-execute-v2/revise-fr/evaluation | `005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/revise-fr/evaluation/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-05-execute-v2/revise-fr | `005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/revise-fr/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-05-execute-v2/ui-browser | `005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/ui-browser/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-05-execute-v2/ui-browser/round-1 | `005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/ui-browser/round-1/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-05-execute-v2/ui-browser/round-2 | `005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/ui-browser/round-2/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-06-reveal-2 | `005_LAB_Dynamic_Workflow_Replanning/reference/step-06-reveal-2/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-07-plan-v3/evaluation | `005_LAB_Dynamic_Workflow_Replanning/reference/step-07-plan-v3/evaluation/log.jsonl` |
| 005_LAB_Dynamic_Workflow_Replanning | step-07-plan-v3 | `005_LAB_Dynamic_Workflow_Replanning/reference/step-07-plan-v3/log.jsonl` |
| 006_LAB_Test_Scenarios_Traceability | step-00-input | `006_LAB_Test_Scenarios_Traceability/reference/step-00-input/log.jsonl` |
| 006_LAB_Test_Scenarios_Traceability | step-01-fanout/customer | `006_LAB_Test_Scenarios_Traceability/reference/step-01-fanout/customer/log.jsonl` |
| 006_LAB_Test_Scenarios_Traceability | step-01-fanout/kitchen-front | `006_LAB_Test_Scenarios_Traceability/reference/step-01-fanout/kitchen-front/log.jsonl` |
| 006_LAB_Test_Scenarios_Traceability | step-01-fanout/manager | `006_LAB_Test_Scenarios_Traceability/reference/step-01-fanout/manager/log.jsonl` |
| 006_LAB_Test_Scenarios_Traceability | step-02-coverage/fix-1 | `006_LAB_Test_Scenarios_Traceability/reference/step-02-coverage/fix-1/log.jsonl` |
| 006_LAB_Test_Scenarios_Traceability | step-02-coverage/round-1 | `006_LAB_Test_Scenarios_Traceability/reference/step-02-coverage/round-1/log.jsonl` |
| 006_LAB_Test_Scenarios_Traceability | step-02-coverage/round-2 | `006_LAB_Test_Scenarios_Traceability/reference/step-02-coverage/round-2/log.jsonl` |
| 006_LAB_Test_Scenarios_Traceability | step-03-merge | `006_LAB_Test_Scenarios_Traceability/reference/step-03-merge/log.jsonl` |
| 006_LAB_Test_Scenarios_Traceability | step-04-nfr-split | `006_LAB_Test_Scenarios_Traceability/reference/step-04-nfr-split/log.jsonl` |
| 006_LAB_Test_Scenarios_Traceability | step-05-ui-run | `006_LAB_Test_Scenarios_Traceability/reference/step-05-ui-run/log.jsonl` |
| 006_LAB_Test_Scenarios_Traceability | step-05-ui-run/runner | `006_LAB_Test_Scenarios_Traceability/reference/step-05-ui-run/runner/log.jsonl` |

## ตรวจความครบถ้วน log ของ snapshot

ดู `007_LAB_Evaluation_Compare_Workflows/reference/step-01-metrics/log-audit.json` สำหรับ event type และกลุ่มไฟล์ไบต์เหมือนกัน
พบ 36 ไฟล์ที่ไม่มี terminal event จาก 85 ไฟล์; usage ในไฟล์เหล่านั้นไม่มีข้อมูล ไม่ใช่ศูนย์

| LAB | input ที่สังเกตได้ (subtotal) | output ที่สังเกตได้ (subtotal) |
|---|---|---|
| 001_LAB_Single_Prompt_Baseline | 1512903 | 47163 |
| 002_LAB_Loop_FR_NFR | 2341246 | 83388 |
| 003_LAB_Static_Graph_Flow_Structure | 4241534 | 94699 |
| 004_LAB_Conditional_Graph_UI_Mockup | 4352097 | 54538 |
| 005_LAB_Dynamic_Workflow_Replanning | 20152663 | 278721 |
| 006_LAB_Test_Scenarios_Traceability | 12150787 | 203643 |

subtotal รวมเฉพาะแถวที่วัดได้ ไม่แทนช่องยอดรวม ไม่มีข้อมูล ใน CSV/summary และยังไม่ตัดสำเนา log ซ้ำ

## ผล UI เดิมที่ยังตก

- TS-US-09-101: Step 18: AssertionError: Locator expected to be visible
Actual value: None
Error: element(s) not found 
Call log:
  - Expect "to_be_visible" with timeout 2500ms
  - waiting for get_by_test_id("payment-summary-total")

Aria snapshot:
- link "ข้ามไปเนื้อหา":
  - /url: "#main"
- banner:
  - text: ห้องทดลอง UI v2 • ข้อมูลจำลอง
  - heading "ครัวคุณยาย" 
- TS-US-21-101: Step 6: TimeoutError: Locator.evaluate: Timeout 2500ms exceeded.
Call log:
  - waiting for get_by_test_id("rush-start")


ที่มา `006_LAB_Test_Scenarios_Traceability/reference/step-05-ui-run/ui-test-results.json`; ความล้มเหลวของ UI เป็นคนละความหมายกับ terminal event turn.failed

สภาพแวดล้อมการรันใหม่ดู `007_LAB_Evaluation_Compare_Workflows/reference/experiment-environment.json`; Rubric, Single และ Dynamic plan เริ่มขนานกัน จึงอาจแข่งขันทรัพยากร; execute/evaluate ตาม dependency และไม่มีการควบคุมโหลด CPU/เครือข่ายเพื่อสรุปเชิงเหตุ
