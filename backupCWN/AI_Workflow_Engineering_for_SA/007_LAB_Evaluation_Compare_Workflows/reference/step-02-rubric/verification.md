# ตรวจ path หลักฐาน Rubric

ตรวจด้วย Python re.findall และ Path.exists (เทียบเท่า os.path.exists) จากราก AI_Workflow_Engineering_for_SA/
ตรวจเฉพาะการมีไฟล์ ไม่ยืนยันความถูกต้องของคะแนนหรือ locator และยังไม่ใช่การตรวจซ้ำโดยคน
ไม่แก้คะแนนที่ AI ให้; path ที่ไม่มีให้ทำเครื่องหมาย หลักฐานไม่พบ

| Path | ผลตรวจ |
|---|---|
| `001_LAB_Single_Prompt_Baseline/reference/check-report.md` | พบไฟล์ |
| `001_LAB_Single_Prompt_Baseline/reference/final-work/fr-nfr-v0.md` | พบไฟล์ |
| `002_LAB_Loop_FR_NFR/reference/e1-set/loop-log-e1.json` | พบไฟล์ |
| `002_LAB_Loop_FR_NFR/reference/e1-set/summary-e1.md` | พบไฟล์ |
| `002_LAB_Loop_FR_NFR/reference/final/fr-nfr-input.md` | พบไฟล์ |
| `002_LAB_Loop_FR_NFR/reference/loop-log.json` | พบไฟล์ |
| `002_LAB_Loop_FR_NFR/reference/loop-summary.md` | พบไฟล์ |
| `003_LAB_Static_Graph_Flow_Structure/reference/README.md` | พบไฟล์ |
| `003_LAB_Static_Graph_Flow_Structure/reference/parallel-meta.json` | พบไฟล์ |
| `003_LAB_Static_Graph_Flow_Structure/reference/step-04-merge/merge-report.md` | พบไฟล์ |
| `003_LAB_Static_Graph_Flow_Structure/reference/timing.json` | พบไฟล์ |
| `004_LAB_Conditional_Graph_UI_Mockup/reference/decision-log.md` | พบไฟล์ |
| `004_LAB_Conditional_Graph_UI_Mockup/reference/demo-fix-path/summary.md` | พบไฟล์ |
| `004_LAB_Conditional_Graph_UI_Mockup/reference/review/review.md` | พบไฟล์ |
| `004_LAB_Conditional_Graph_UI_Mockup/reference/round-1/ui-check.json` | พบไฟล์ |
| `005_LAB_Dynamic_Workflow_Replanning/reference/README.md` | พบไฟล์ |
| `005_LAB_Dynamic_Workflow_Replanning/reference/metrics.csv` | พบไฟล์ |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/evaluation/evaluator.md` | พบไฟล์ |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/fr-nfr-v2.md` | พบไฟล์ |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/ui-check-v2.json` | พบไฟล์ |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/ui-feature-check-v2.json` | พบไฟล์ |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-07-plan-v3/evaluation/evaluator.md` | พบไฟล์ |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-07-plan-v3/impact-analysis-v3.md` | พบไฟล์ |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-07-plan-v3/plan-v3.json` | พบไฟล์ |
| `006_LAB_Test_Scenarios_Traceability/reference/README.md` | พบไฟล์ |
| `006_LAB_Test_Scenarios_Traceability/reference/metrics.csv` | พบไฟล์ |
| `006_LAB_Test_Scenarios_Traceability/reference/step-02-coverage/decision-log.md` | พบไฟล์ |
| `006_LAB_Test_Scenarios_Traceability/reference/step-03-merge/test-scenarios.md` | พบไฟล์ |
| `006_LAB_Test_Scenarios_Traceability/reference/step-03-merge/traceability-notes.md` | พบไฟล์ |
| `006_LAB_Test_Scenarios_Traceability/reference/step-04-nfr-split/summary.md` | พบไฟล์ |
| `006_LAB_Test_Scenarios_Traceability/reference/step-05-ui-run/ui-run-report.md` | พบไฟล์ |
| `006_LAB_Test_Scenarios_Traceability/reference/step-05-ui-run/ui-test-results.json` | พบไฟล์ |
| `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/manifest.md` | พบไฟล์ |
| `007_LAB_Evaluation_Compare_Workflows/reference/change-conditions.md` | พบไฟล์ |
| `007_LAB_Evaluation_Compare_Workflows/reference/evidence-index.md` | พบไฟล์ |
| `007_LAB_Evaluation_Compare_Workflows/reference/metrics.csv` | พบไฟล์ |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-01-metrics/metrics-notes.md` | พบไฟล์ |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-01-metrics/metrics-summary.md` | พบไฟล์ |

ตรวจ 38 path; พบ 38; หลักฐานไม่พบ 0

## การตรวจทุกช่องคะแนน

- แถว 1: พบไฟล์หลักฐานครบ (2 path)
- แถว 2: พบไฟล์หลักฐานครบ (2 path)
- แถว 3: พบไฟล์หลักฐานครบ (2 path)
- แถว 4: พบไฟล์หลักฐานครบ (2 path)
- แถว 5: พบไฟล์หลักฐานครบ (3 path)
- แถว 6: พบไฟล์หลักฐานครบ (2 path)
- แถว 7: พบไฟล์หลักฐานครบ (2 path)
- แถว 8: พบไฟล์หลักฐานครบ (2 path)
- แถว 9: พบไฟล์หลักฐานครบ (2 path)
- แถว 10: พบไฟล์หลักฐานครบ (3 path)
- แถว 11: พบไฟล์หลักฐานครบ (2 path)
- แถว 12: พบไฟล์หลักฐานครบ (1 path)
- แถว 13: พบไฟล์หลักฐานครบ (2 path)
- แถว 14: พบไฟล์หลักฐานครบ (1 path)
- แถว 15: พบไฟล์หลักฐานครบ (4 path)
- แถว 16: พบไฟล์หลักฐานครบ (2 path)
- แถว 17: พบไฟล์หลักฐานครบ (2 path)
- แถว 18: พบไฟล์หลักฐานครบ (2 path)
- แถว 19: พบไฟล์หลักฐานครบ (3 path)
- แถว 20: พบไฟล์หลักฐานครบ (4 path)
- แถว 21: พบไฟล์หลักฐานครบ (3 path)
- แถว 22: พบไฟล์หลักฐานครบ (3 path)
- แถว 23: พบไฟล์หลักฐานครบ (3 path)
- แถว 24: พบไฟล์หลักฐานครบ (3 path)
- แถว 25: พบไฟล์หลักฐานครบ (4 path)
- แถว 26: พบไฟล์หลักฐานครบ (3 path)
- แถว 27: พบไฟล์หลักฐานครบ (2 path)
- แถว 28: พบไฟล์หลักฐานครบ (2 path)
- แถว 29: พบไฟล์หลักฐานครบ (3 path)
- แถว 30: พบไฟล์หลักฐานครบ (4 path)
- แถว 31: พบไฟล์หลักฐานครบ (3 path)
- แถว 32: พบไฟล์หลักฐานครบ (3 path)
- แถว 33: พบไฟล์หลักฐานครบ (2 path)
- แถว 34: พบไฟล์หลักฐานครบ (3 path)
- แถว 35: พบไฟล์หลักฐานครบ (3 path)

แถวคะแนนที่ตรวจ: 35; ต้องมี 35 แถว

## ข้อจำกัดการตีความ

คะแนน LAB 007 เป็น snapshot ก่อนจบ Single/Dynamic/report จึงไม่ใช่การประเมินชิ้นงานสุดท้าย; คงคะแนน AI เดิมทุกช่อง
Rubric บรรยายชุดส่งต่อ LAB 002–004 ว่า 18 US แต่ coverage กิจกรรม UI LAB 004 มี ✓ 16 US; การกล่าวถึง US ใน input ไม่เท่ากับ UI ครบหรือผ่าน ต้องให้ผู้สอนตรวจการตีความขอบเขตอีกครั้ง
