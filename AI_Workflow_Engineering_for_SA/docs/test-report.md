# รายงานสถานะทดสอบบทเรียน

วันที่เริ่มตรวจสไลด์: **2026-09-14T23:24:05.026892+07:00** (เวลาไทย UTC+7); เวลา UI แต่ละรุ่นอยู่ใน JSON

ผลนี้มาจากการเปิดเบราว์เซอร์และรันสคริปต์จริง ไม่ได้เรียกโมเดลสร้างผลรันล่วงหน้าเพิ่ม เวลา/รอบ/โทเคนของการเรียกโมเดลใหม่: **ไม่มีข้อมูล — ไม่ได้เรียก**

เครื่องมือ QA ที่ตรวจรุ่นจริง: **Playwright 1.62.0 / Chromium 151.0.7922.34** ผ่าน launch; Codex CLI 0.154.0 ตรวจด้วยคำสั่งแสดงเวอร์ชัน

รุ่นที่โจทย์ระบุคือ Playwright 1.63 Chromium แต่ package index ของเครื่องนี้มีถึงรุ่นที่ใช้จริงข้างต้น จึงไม่ได้รับรองผลบนรุ่นที่ร้องขอ ส่วน Excalidraw MCP 2.0.0 เป็นเครื่องมือของภาพเดิมตาม [ทะเบียนภาพ](../img/README.md) ไม่ได้เรียกวาดภาพใหม่ในรอบ QA

ค่าผลทดสอบทั้งหมดด้านล่างอ่านจาก [results.json](../tests/results.json) และ [link-report.json](../tests/link-report.json); ค่าเสริมใน context คัดจากหลักฐานเดิมพร้อมระบุขอบเขต

## ทดสอบแล้ว

| รายการ | ผลจริง | หลักฐาน / ขอบเขต |
|---|---|---|
| สไลด์ | 143 หน้า / 143 ภาพ / console error และ pageerror 0 / ล้น 0; pass | [ภาพทุกหน้า](../tests/screenshots/slides/); file://, viewport 1600×900 |
| overview | pass | เปิดภาพรวม ตรวจทุกหน้าแสดง คลิกเลือกหน้า และออกด้วย Esc |
| iframe | ครัวคุณยาย UI v1 แบบโต้ตอบ: pass; ครัวคุณยาย UI v2 เล่นได้: pass | สลับลูกค้า → ครัว → หน้าร้าน → ผู้จัดการ แล้วรีเซ็ต |
| UI v1 | ผ่าน 11 / ตก 3 / ข้าม 0 | [ภาพ UI v1](../tests/screenshots/ui-v1/) |
| UI v2 | ผ่าน 12 / ตก 2 / ข้าม 0 | [ภาพ UI v2](../tests/screenshots/ui-v2/) |
| ลิงก์ในไฟล์ที่นักศึกษาใช้ | ตรวจ 2832 / เสีย 0 / แก้ 69 occurrence (4 ไฟล์) | ผ่าน; ขอบเขตเริ่มต้นของ check_links.py |
| ลิงก์ในหลักฐานดิบผูก SHA-256 | ตรวจ 311 / เสีย 121 = known issue | ตรวจ Markdown/HTML 331 ไฟล์ตามรายชื่อ manifest; รายการเสียครบใน evidence.broken |

### ผลต่อ scenario

ใช้ fixture เดิมของ LAB ทั้งสองรุ่น ครบทุกเคสและแยก context ต่อเคส ไม่ปรับ selector หรือความคาดหวังเพื่อให้ผ่าน สถานะ pass หมายถึง assertions ของ mock ผ่านเท่านั้น

| Scenario / US | v1 | v2 | สาเหตุกรณีตก |
|---|---|---|---|
| TS-US-01-101 / US-01 | pass | pass | — |
| TS-US-02-101 / US-02 | pass | pass | — |
| TS-US-03-101 / US-03 | pass | pass | — |
| TS-US-04-101 / US-04 | pass | pass | — |
| TS-US-05-101 / US-05 | pass | pass | — |
| TS-US-06-101 / US-06 | pass | pass | — |
| TS-US-08-101 / US-08 | pass | pass | — |
| TS-US-08-102 / US-08 | pass | pass | — |
| TS-US-09-101 / US-09 | fail | fail | v1: ฟีเจอร์ที่เพิ่มใน UI v2; เก็บผลตกบน UI v1 ตามชุด scenario เดิม; v2: fixture mismatch: payment-summary-total ไม่มีใน UI v2 (รายงานเดิม F01) |
| TS-US-11-101 / US-11 | pass | pass | — |
| TS-US-12-101 / US-12 | pass | pass | — |
| TS-US-14-101 / US-14 | fail | pass | v1: ฟีเจอร์ที่เพิ่มใน UI v2; เก็บผลตกบน UI v1 ตามชุด scenario เดิม |
| TS-US-21-101 / US-21 | fail | fail | v1: ฟีเจอร์ที่เพิ่มใน UI v2; เก็บผลตกบน UI v1 ตามชุด scenario เดิม; v2: fixture mismatch: rush-start ไม่มี และขาดขั้น nav-capacity (รายงานเดิม F02) |
| TS-US-25-101 / US-25 | pass | pass | — |

หลักฐานเดิม LAB 006 ผ่าน 12 / ตก 2 / ข้าม 0 ตรงกับผล v2 รอบนี้; อ่านคำวิเคราะห์ [F01/F02](../006_LAB_Test_Scenarios_Traceability/reference/step-05-ui-run/ui-run-report.md) โดยไม่แก้หลักฐานเดิม

เคสคืนรายการของ v2 แสดงยอดจำลองที่ปรับแล้วในภาพ แต่ fixture ค้นหา payment-summary-total ซึ่งไม่มีใน DOM; เคสกำลังการผลิตใช้ rush-start ที่ไม่มีและไม่ได้เปิด nav-capacity ก่อน จึงยังไม่ใช่หลักฐานว่ากฎธุรกิจสองข้อนี้ผ่านครบ

เปิดดูภาพตัวอย่างด้วยสายตาที่หน้าฝัง v2 และเคสคืนรายการประกอบ DOM; ภาพหน้าที่เหลือเก็บด้วย automation ไม่ได้อ้างว่าตรวจทุก pixel ด้วยสายตา

### การแก้ลิงก์

ตารางนี้แจกแจงทุกการแก้ลิงก์เสียใน Markdown; occurrence คือจำนวนที่พบในเนื้อหา ไม่ใช่จำนวนไฟล์ ส่วนลิงก์ต้นฉบับที่เพิ่มแทน path ภายในและข้อแก้ถ้อยคำตามรายการสะสมอยู่ในตารางถัดไป

| ไฟล์ | เดิม | ปลายทางที่มีจริง | occurrence |
|---|---|---|---|
| `004_LAB_Conditional_Graph_UI_Mockup/reference/review/summary.md` | `work/click-review-round-1.md` | `click-review-round-1.md` | 1 |
| `004_LAB_Conditional_Graph_UI_Mockup/reference/review/summary.md` | `work/manual-shots/round-1/` | `manual-shots/round-1` | 1 |
| `004_LAB_Conditional_Graph_UI_Mockup/reference/round-1/summary.md` | `work/ui-mockup.html` | `ui-mockup.html` | 1 |
| `004_LAB_Conditional_Graph_UI_Mockup/reference/round-1/summary.md` | `work/build-notes.md` | `build-notes.md` | 1 |
| `006_LAB_Test_Scenarios_Traceability/README.md` | `../../step-00-input/fr-nfr-v2.md` | `reference/step-00-input/fr-nfr-v2.md` | 4 |
| `006_LAB_Test_Scenarios_Traceability/README.md` | `../../step-00-input/flow-v2.md` | `reference/step-00-input/flow-v2.md` | 4 |
| `006_LAB_Test_Scenarios_Traceability/README.md` | `../../../../docs/case-study-source.md` | `../docs/case-study-source.md` | 3 |
| `006_LAB_Test_Scenarios_Traceability/README.md` | `../../../input/coverage-criteria.md` | `input/coverage-criteria.md` | 3 |
| `006_LAB_Test_Scenarios_Traceability/README.md` | `../../step-00-input/scenario-set-round-0.json` | `reference/step-00-input/scenario-set-round-0.json` | 2 |
| `006_LAB_Test_Scenarios_Traceability/README.md` | `../../step-01-fanout/customer/scenarios-customer.md` | `reference/step-01-fanout/customer/scenarios-customer.md` | 1 |
| `006_LAB_Test_Scenarios_Traceability/README.md` | `../../step-01-fanout/kitchen-front/scenarios-kitchen-front.md` | `reference/step-01-fanout/kitchen-front/scenarios-kitchen-front.md` | 1 |
| `006_LAB_Test_Scenarios_Traceability/README.md` | `../../step-01-fanout/manager/scenarios-manager.md` | `reference/step-01-fanout/manager/scenarios-manager.md` | 1 |
| `006_LAB_Test_Scenarios_Traceability/README.md` | `../../step-00-input/input-check.md` | `reference/step-00-input/input-check.md` | 3 |
| `006_LAB_Test_Scenarios_Traceability/README.md` | `../../../input/ui-scenarios.json` | `input/ui-scenarios.json` | 3 |
| `006_LAB_Test_Scenarios_Traceability/README.md` | `../../step-00-input/ui-mockup-v2.html` | `reference/step-00-input/ui-mockup-v2.html` | 1 |
| `006_LAB_Test_Scenarios_Traceability/README.md` | `../round-1/coverage-round-1.md` | `reference/step-02-coverage/round-1/coverage-round-1.md` | 2 |
| `006_LAB_Test_Scenarios_Traceability/README.md` | `../../../input/scenario-template.md` | `input/scenario-template.md` | 1 |
| `006_LAB_Test_Scenarios_Traceability/README.md` | `scenarios-customer-round-1.md` | `reference/step-02-coverage/fix-1/scenarios-customer-round-1.md` | 3 |
| `006_LAB_Test_Scenarios_Traceability/README.md` | `scenarios-kitchen-front-round-1.md` | `reference/step-02-coverage/fix-1/scenarios-kitchen-front-round-1.md` | 2 |
| `006_LAB_Test_Scenarios_Traceability/README.md` | `scenarios-manager-round-1.md` | `reference/step-02-coverage/fix-1/scenarios-manager-round-1.md` | 2 |
| `006_LAB_Test_Scenarios_Traceability/README.md` | `../fix-1/scenario-set-round-1.json` | `reference/step-02-coverage/fix-1/scenario-set-round-1.json` | 1 |
| `006_LAB_Test_Scenarios_Traceability/README.md` | `../fix-1/scenarios-customer-round-1.md` | `reference/step-02-coverage/fix-1/scenarios-customer-round-1.md` | 1 |
| `006_LAB_Test_Scenarios_Traceability/README.md` | `../fix-1/scenarios-kitchen-front-round-1.md` | `reference/step-02-coverage/fix-1/scenarios-kitchen-front-round-1.md` | 1 |
| `006_LAB_Test_Scenarios_Traceability/README.md` | `../fix-1/scenarios-manager-round-1.md` | `reference/step-02-coverage/fix-1/scenarios-manager-round-1.md` | 1 |
| `006_LAB_Test_Scenarios_Traceability/README.md` | `../fix-1/coverage-fixes-round-1.md` | `reference/step-02-coverage/fix-1/coverage-fixes-round-1.md` | 1 |
| `006_LAB_Test_Scenarios_Traceability/README.md` | `../step-00-input/fr-nfr-v2.md` | `reference/step-00-input/fr-nfr-v2.md` | 2 |
| `006_LAB_Test_Scenarios_Traceability/README.md` | `../step-00-input/flow-v2.md` | `reference/step-00-input/flow-v2.md` | 1 |
| `006_LAB_Test_Scenarios_Traceability/README.md` | `../../../docs/case-study-source.md` | `../docs/case-study-source.md` | 1 |
| `006_LAB_Test_Scenarios_Traceability/README.md` | `../../../docs/data-issues.md` | `../docs/data-issues.md` | 1 |
| `006_LAB_Test_Scenarios_Traceability/README.md` | `../step-03-merge/test-scenarios.md` | `reference/step-03-merge/test-scenarios.md` | 2 |
| `006_LAB_Test_Scenarios_Traceability/README.md` | `../step-03-merge/traceability.csv` | `reference/step-03-merge/traceability.csv` | 2 |
| `006_LAB_Test_Scenarios_Traceability/README.md` | `../step-03-merge/traceability-notes.md` | `reference/step-03-merge/traceability-notes.md` | 1 |
| `006_LAB_Test_Scenarios_Traceability/README.md` | `ui-test-results.json` | `reference/step-05-ui-run/ui-test-results.json` | 1 |
| `006_LAB_Test_Scenarios_Traceability/README.md` | `../../input/ui-scenarios.json` | `input/ui-scenarios.json` | 1 |
| `006_LAB_Test_Scenarios_Traceability/README.md` | `../step-04-nfr-split/nfr-split.md` | `reference/step-04-nfr-split/nfr-split.md` | 1 |
| `006_LAB_Test_Scenarios_Traceability/README.md` | `../step-00-input/provenance.md` | `reference/step-00-input/provenance.md` | 1 |
| `006_LAB_Test_Scenarios_Traceability/README.md` | `../step-00-input/input-check.md` | `reference/step-00-input/input-check.md` | 1 |
| `006_LAB_Test_Scenarios_Traceability/README.md` | `runner/log.jsonl` | `reference/step-05-ui-run/runner/log.jsonl` | 1 |
| `006_LAB_Test_Scenarios_Traceability/reference/step-02-coverage/fix-1/prompt-used.md` | `../../../../../../../docs/case-study-source.md` | `../../../../docs/case-study-source.md` | 1 |
| `006_LAB_Test_Scenarios_Traceability/reference/step-02-coverage/fix-1/prompt-used.md` | `../../../../../../input/coverage-criteria.md` | `../../../input/coverage-criteria.md` | 1 |
| `006_LAB_Test_Scenarios_Traceability/reference/step-02-coverage/fix-1/prompt-used.md` | `../../step-00-../../../input/scenario-set-round-0.json` | `../../step-00-input/scenario-set-round-0.json` | 1 |
| `006_LAB_Test_Scenarios_Traceability/reference/step-02-coverage/fix-1/prompt-used.md` | `../../step-00-../../../../../../input/input-check.md` | `../../step-00-input/input-check.md` | 1 |
| `006_LAB_Test_Scenarios_Traceability/reference/step-02-coverage/fix-1/prompt-used.md` | `../../step-00-../../../../../../input/fr-nfr-v2.md` | `../../step-00-input/fr-nfr-v2.md` | 1 |
| `006_LAB_Test_Scenarios_Traceability/reference/step-02-coverage/fix-1/prompt-used.md` | `../../step-00-../../../../../../input/flow-v2.md` | `../../step-00-input/flow-v2.md` | 1 |
| `006_LAB_Test_Scenarios_Traceability/reference/step-02-coverage/fix-1/prompt-used.md` | `../../step-00-../../../input/ui-mockup-v2.html` | `../../step-00-input/ui-mockup-v2.html` | 1 |
| `004_LAB_Conditional_Graph_UI_Mockup/reference/review/summary.md` | `work/ai-review-round-1.md` | `review.md` | 1 |

### ข้อแก้เอกสารและขอบเขตที่รักษา

| ไฟล์ | การแก้ที่ได้รับอนุญาต |
|---|---|
| `004_LAB_Conditional_Graph_UI_Mockup/reference/review/summary.md` | แก้ลิงก์ไปผลผู้ตรวจที่เผยแพร่จริง |
| `docs/case-study-source.md` | แทนแหล่งข้อมูลภายในด้วยลิงก์ต้นฉบับสำหรับผู้เรียน |
| `docs/data-issues.md` | ลิงก์ต้นฉบับและลบชื่อขั้นตอนภายใน |
| `docs/rubric.md` | แทนการอ้างขั้นตอนภายในด้วยคำอธิบายแบบฟอร์มและลิงก์ |
| `003_LAB_Static_Graph_Flow_Structure/README.md` | แทน marker ด้วยลิงก์ผลจริงและเปิดเผย execution context |
| `003_LAB_Static_Graph_Flow_Structure/README.md` | เปิดเผย execution context ตามข้อสังเกต |
| `003_LAB_Static_Graph_Flow_Structure/input/us-by-role.md` | ชี้ต้นฉบับจาก input/ และอธิบายฐานของ path เดิม |
| `005_LAB_Dynamic_Workflow_Replanning/README.md` | แทน absolute path ในข้อความที่แสดงด้วย placeholder ตามคำขอ |
| `005_LAB_Dynamic_Workflow_Replanning/reference/README.md` | อธิบาย path ในหลักฐานที่ห้ามเปลี่ยน |
| `006_LAB_Test_Scenarios_Traceability/README.md` | ขยายสาเหตุเคสที่ตกตามรายงานเดิม โดยคงสถานะเดิม |
| `007_LAB_Evaluation_Compare_Workflows/README.md` | เปิดเผยเหตุยอดรวมไม่มีข้อมูลตามข้อสังเกต |
| `002_LAB_Loop_FR_NFR/README.md` | ระบุขอบเขตลูปหลักโดยไม่เปลี่ยนตัวเลข |
| `img/README.md` | ลบชื่อขั้นตอนภายในและแทน path เครื่องในเอกสารภาพ |

ทะเบียนปัญหาข้อมูลกล่าวถึงรหัสอ้างในเซลล์ US-20 อยู่แล้ว; input ของ LAB 005 อธิบายฐาน path และชี้ UI ที่มีจริงแล้ว; รายงานเปรียบเทียบและ impact ของ LAB สุดท้ายระบุ docs/ui-contract.md ว่าไม่มีไฟล์เป็นข้อความธรรมดาอยู่แล้ว จึงรักษาข้อความและหลักฐานเดิม

ลบ cache/checkpoint และ symlink absolute ใน session ตามคำขอ โดยไม่ลบเป้าหมายของ symlink; รายการอยู่ใน [cleanup.json](../tests/cleanup.json) โค้ด metrics ที่อยู่นอก tests กลางและภาพแผนภาพไม่ได้แก้

ไฟล์บทเรียนยังไม่ได้อยู่ใน Git index จึงใช้ git diff เพียงอย่างเดียวสรุปการแก้ไม่ได้ เก็บรายการไฟล์ที่เปลี่ยนเทียบ snapshot ก่อนงานและตรวจ hash ไฟล์ที่ห้ามแก้ใน [scope-audit.json](../tests/scope-audit.json) โดยไม่มีการ add/commit/push

### known issue ในหลักฐานดิบ (ลิงก์ 121 จุดใน 42 ไฟล์ที่ผูก SHA-256 — ไม่แก้)

แยกเฉพาะไฟล์ที่ path อยู่ใน keys ของ protected-evidence.json เป็นหลักฐานดิบผูก SHA-256; ไฟล์อื่นทั้งหมดอยู่ในขอบเขตนักศึกษาที่ต้องไม่มีลิงก์เสีย โดยไม่คัดออกด้วยชื่อ README หรือ summary ลิงก์ในหลักฐานเสียเพราะ AI เขียน path สัมพัทธ์กับ work/ หรือ cwd ขณะรัน เมื่อนำผลมาเก็บใน reference/ ตำแหน่งจึงต่างออกไป

ผลขอบเขตนักศึกษาผ่านเมื่อ broken ว่าง ส่วนรายการต่อไปนี้คงครบใน evidence.broken และเป็น known issue เพื่อรักษา hash ต้นฉบับ ใช้ check_links.py --all เพื่อตรวจรวมทุกขอบเขต ซึ่งคืน exit 1 เมื่อพบลิงก์เสียในหลักฐานด้วย

ดูทะเบียน hash ต้นทางรายไฟล์ใน [protected-evidence.json](../tests/protected-evidence.json); ตารางด้านล่างไม่สร้างลิงก์ใหม่ไปยัง path ที่เสีย

| ไฟล์หลักฐาน | path ที่เสีย | เหตุผลที่ยังคงไว้ |
|---|---|---|
| `001_LAB_Single_Prompt_Baseline/reference/final-work/fr-nfr-v0.md` | `../input/user-stories.md` | ผูก SHA-256 |
| `001_LAB_Single_Prompt_Baseline/reference/final-work/fr-nfr-v0.md` | `../input/context.md` | ผูก SHA-256 |
| `001_LAB_Single_Prompt_Baseline/reference/final-work/fr-nfr-v0.md` | `../../docs/data-issues.md` | ผูก SHA-256 |
| `001_LAB_Single_Prompt_Baseline/reference/final-work/fr-nfr-v0.md` | `../../docs/data-issues.md` | ผูก SHA-256 |
| `001_LAB_Single_Prompt_Baseline/reference/final-work/self-check.md` | `../input/user-stories.md` | ผูก SHA-256 |
| `001_LAB_Single_Prompt_Baseline/reference/final-work/self-check.md` | `../input/context.md` | ผูก SHA-256 |
| `001_LAB_Single_Prompt_Baseline/reference/final-work/self-check.md` | `../input/checklist-fr-nfr.md` | ผูก SHA-256 |
| `001_LAB_Single_Prompt_Baseline/reference/final-work/self-check.md` | `../../docs/data-issues.md` | ผูก SHA-256 |
| `001_LAB_Single_Prompt_Baseline/reference/final-work/us-analysis.md` | `../input/user-stories.md` | ผูก SHA-256 |
| `001_LAB_Single_Prompt_Baseline/reference/final-work/us-analysis.md` | `../input/context.md` | ผูก SHA-256 |
| `001_LAB_Single_Prompt_Baseline/reference/final-work/us-analysis.md` | `../../docs/data-issues.md` | ผูก SHA-256 |
| `001_LAB_Single_Prompt_Baseline/reference/step-01/round-1/output.md` | `work/us-analysis.md` | ผูก SHA-256 |
| `001_LAB_Single_Prompt_Baseline/reference/step-01/round-1/us-analysis.md` | `../input/user-stories.md` | ผูก SHA-256 |
| `001_LAB_Single_Prompt_Baseline/reference/step-01/round-1/us-analysis.md` | `../input/context.md` | ผูก SHA-256 |
| `001_LAB_Single_Prompt_Baseline/reference/step-01/round-1/us-analysis.md` | `../../docs/data-issues.md` | ผูก SHA-256 |
| `001_LAB_Single_Prompt_Baseline/reference/step-02/round-1/fr-nfr-v0.md` | `../input/user-stories.md` | ผูก SHA-256 |
| `001_LAB_Single_Prompt_Baseline/reference/step-02/round-1/fr-nfr-v0.md` | `../input/context.md` | ผูก SHA-256 |
| `001_LAB_Single_Prompt_Baseline/reference/step-02/round-1/fr-nfr-v0.md` | `../../docs/data-issues.md` | ผูก SHA-256 |
| `001_LAB_Single_Prompt_Baseline/reference/step-02/round-1/fr-nfr-v0.md` | `../../docs/data-issues.md` | ผูก SHA-256 |
| `001_LAB_Single_Prompt_Baseline/reference/step-02/round-1/output.md` | `work/fr-nfr-v0.md` | ผูก SHA-256 |
| `001_LAB_Single_Prompt_Baseline/reference/step-02/round-1/us-analysis.md` | `../input/user-stories.md` | ผูก SHA-256 |
| `001_LAB_Single_Prompt_Baseline/reference/step-02/round-1/us-analysis.md` | `../input/context.md` | ผูก SHA-256 |
| `001_LAB_Single_Prompt_Baseline/reference/step-02/round-1/us-analysis.md` | `../../docs/data-issues.md` | ผูก SHA-256 |
| `001_LAB_Single_Prompt_Baseline/reference/step-03/round-1/fr-nfr-v0.md` | `../input/user-stories.md` | ผูก SHA-256 |
| `001_LAB_Single_Prompt_Baseline/reference/step-03/round-1/fr-nfr-v0.md` | `../input/context.md` | ผูก SHA-256 |
| `001_LAB_Single_Prompt_Baseline/reference/step-03/round-1/fr-nfr-v0.md` | `../../docs/data-issues.md` | ผูก SHA-256 |
| `001_LAB_Single_Prompt_Baseline/reference/step-03/round-1/fr-nfr-v0.md` | `../../docs/data-issues.md` | ผูก SHA-256 |
| `001_LAB_Single_Prompt_Baseline/reference/step-03/round-1/output.md` | `<PROJECT_ROOT>/AI_Workflow_Engineering_for_SA/001_LAB_Single_Prompt_Baseline/work/self-check.md` | ผูก SHA-256 |
| `001_LAB_Single_Prompt_Baseline/reference/step-03/round-1/self-check.md` | `../input/user-stories.md` | ผูก SHA-256 |
| `001_LAB_Single_Prompt_Baseline/reference/step-03/round-1/self-check.md` | `../input/context.md` | ผูก SHA-256 |
| `001_LAB_Single_Prompt_Baseline/reference/step-03/round-1/self-check.md` | `../input/checklist-fr-nfr.md` | ผูก SHA-256 |
| `001_LAB_Single_Prompt_Baseline/reference/step-03/round-1/self-check.md` | `../../docs/data-issues.md` | ผูก SHA-256 |
| `001_LAB_Single_Prompt_Baseline/reference/step-03/round-1/us-analysis.md` | `../input/user-stories.md` | ผูก SHA-256 |
| `001_LAB_Single_Prompt_Baseline/reference/step-03/round-1/us-analysis.md` | `../input/context.md` | ผูก SHA-256 |
| `001_LAB_Single_Prompt_Baseline/reference/step-03/round-1/us-analysis.md` | `../../docs/data-issues.md` | ผูก SHA-256 |
| `002_LAB_Loop_FR_NFR/reference/step-01/round-1/fr-nfr-v0.md` | `../input/user-stories.md` | ผูก SHA-256 |
| `002_LAB_Loop_FR_NFR/reference/step-01/round-1/fr-nfr-v0.md` | `../input/context.md` | ผูก SHA-256 |
| `002_LAB_Loop_FR_NFR/reference/step-01/round-1/fr-nfr-v0.md` | `us-analysis.md` | ผูก SHA-256 |
| `002_LAB_Loop_FR_NFR/reference/step-01/round-1/fr-nfr-v0.md` | `../../docs/data-issues.md` | ผูก SHA-256 |
| `002_LAB_Loop_FR_NFR/reference/step-01/round-1/fr-nfr-v0.md` | `us-analysis.md` | ผูก SHA-256 |
| `002_LAB_Loop_FR_NFR/reference/step-01/round-1/fr-nfr-v0.md` | `../../docs/data-issues.md` | ผูก SHA-256 |
| `003_LAB_Static_Graph_Flow_Structure/reference/step-01-fanout/customer/final-response-attempt1.md` | `work/review-record.md` | ผูก SHA-256 |
| `003_LAB_Static_Graph_Flow_Structure/reference/step-01-fanout/customer/final-response.md` | `work/flow-customer.md` | ผูก SHA-256 |
| `003_LAB_Static_Graph_Flow_Structure/reference/step-01-fanout/customer/final-response.md` | `work/flow-customer.json` | ผูก SHA-256 |
| `003_LAB_Static_Graph_Flow_Structure/reference/step-01-fanout/kitchen-front/final-response-attempt1.md` | `work/input-audit.md` | ผูก SHA-256 |
| `003_LAB_Static_Graph_Flow_Structure/reference/step-01-fanout/kitchen-front/final-response-attempt1.md` | `work/review-record.md` | ผูก SHA-256 |
| `003_LAB_Static_Graph_Flow_Structure/reference/step-01-fanout/kitchen-front/final-response.md` | `work/flow-kitchen-front.md` | ผูก SHA-256 |
| `003_LAB_Static_Graph_Flow_Structure/reference/step-01-fanout/kitchen-front/final-response.md` | `work/flow-kitchen-front.json` | ผูก SHA-256 |
| `003_LAB_Static_Graph_Flow_Structure/reference/step-01-fanout/manager/final-response-attempt2.md` | `work/flow-manager.md` | ผูก SHA-256 |
| `003_LAB_Static_Graph_Flow_Structure/reference/step-01-fanout/manager/final-response-attempt2.md` | `work/flow-manager.json` | ผูก SHA-256 |
| `003_LAB_Static_Graph_Flow_Structure/reference/step-01-fanout/manager/final-response.md` | `work/flow-manager.md` | ผูก SHA-256 |
| `003_LAB_Static_Graph_Flow_Structure/reference/step-01-fanout/manager/final-response.md` | `work/flow-manager.json` | ผูก SHA-256 |
| `003_LAB_Static_Graph_Flow_Structure/reference/step-02-state-machine/final-response.md` | `work/flow-state-machine.md` | ผูก SHA-256 |
| `003_LAB_Static_Graph_Flow_Structure/reference/step-02-state-machine/final-response.md` | `work/flow-state-machine.json` | ผูก SHA-256 |
| `003_LAB_Static_Graph_Flow_Structure/reference/step-02-state-machine/final-response.md` | `work/state-machine.md` | ผูก SHA-256 |
| `003_LAB_Static_Graph_Flow_Structure/reference/step-03-structure/final-response.md` | `work/flow-structure.md` | ผูก SHA-256 |
| `003_LAB_Static_Graph_Flow_Structure/reference/step-03-structure/final-response.md` | `work/flow-structure.json` | ผูก SHA-256 |
| `003_LAB_Static_Graph_Flow_Structure/reference/step-03-structure/final-response.md` | `work/structure.md` | ผูก SHA-256 |
| `003_LAB_Static_Graph_Flow_Structure/reference/step-04-merge/final-response.md` | `work/flow-merge.md` | ผูก SHA-256 |
| `003_LAB_Static_Graph_Flow_Structure/reference/step-04-merge/final-response.md` | `work/flow-merge.json` | ผูก SHA-256 |
| `003_LAB_Static_Graph_Flow_Structure/reference/step-04-merge/final-response.md` | `work/merge-report.md` | ผูก SHA-256 |
| `003_LAB_Static_Graph_Flow_Structure/reference/step-04-merge/final-response.md` | `work/lab004-handoff.md` | ผูก SHA-256 |
| `005_LAB_Dynamic_Workflow_Replanning/reference/session/test-outline-v2.md` | `execution.md` | ผูก SHA-256 |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/state-machine.md` | `flow-state-machine.md` | ผูก SHA-256 |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/state-machine.md` | `flow-state-machine.json` | ผูก SHA-256 |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/structure.md` | `flow-structure.md` | ผูก SHA-256 |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/structure.md` | `flow-structure.json` | ผูก SHA-256 |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered/state-machine.md` | `flow-state-machine.md` | ผูก SHA-256 |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered/state-machine.md` | `flow-state-machine.json` | ผูก SHA-256 |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered/structure.md` | `flow-structure.md` | ผูก SHA-256 |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered/structure.md` | `flow-structure.json` | ผูก SHA-256 |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/state-machine.md` | `flow-state-machine.md` | ผูก SHA-256 |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/state-machine.md` | `flow-state-machine.json` | ผูก SHA-256 |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/structure.md` | `flow-structure.md` | ผูก SHA-256 |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/structure.md` | `flow-structure.json` | ผูก SHA-256 |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-02-execute-v1/draft-test-outline/evaluation/summary.md` | `../../../../session/evaluations/test-outline-v1-check.md` | ผูก SHA-256 |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-02-execute-v1/draft-test-outline/evaluation/summary.md` | `../../../../session/evaluations/plan-v1/test-outline-review.md` | ผูก SHA-256 |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-03-reveal-1/reveal-1.md` | `../../../appendix-a-restaurant.md` | ผูก SHA-256 |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/revise-flow/evaluation/summary.md` | `../session/evaluations/flow-v2-check.md` | ผูก SHA-256 |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/revise-flow/evaluation/summary.md` | `../session/evaluations/plan-v2/flow-v2-review.md` | ผูก SHA-256 |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/revise-flow/evaluation/summary.md` | `../session/evaluations/plan-v2/flow-v2-review-evidence.json` | ผูก SHA-256 |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/revise-fr/evaluation/summary.md` | `../../../../session/evaluations/fr-v2-check.md` | ผูก SHA-256 |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/revise-fr/evaluation/summary.md` | `../../../../session/evaluations/plan-v2/fr-v2-review.md` | ผูก SHA-256 |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-06-reveal-2/reveal-2.md` | `../../../appendix-a-restaurant.md` | ผูก SHA-256 |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-07-plan-v3/evaluator.md` | `../../session/evaluations/plan-v3-review.md` | ผูก SHA-256 |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-07-plan-v3/evaluator.md` | `../../session/evaluations/plan-v3/plan-v3-review.md` | ผูก SHA-256 |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-07-plan-v3/evaluation/summary.md` | `../session/evaluations/plan-v3-review.md` | ผูก SHA-256 |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-07-plan-v3/evaluation/summary.md` | `../session/evaluations/plan-v3/plan-v3-review.md` | ผูก SHA-256 |
| `006_LAB_Test_Scenarios_Traceability/reference/step-00-input/test-outline-v2.md` | `execution.md` | ผูก SHA-256 |
| `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/flow-v2.md` | `state-machine-v2.md` | ผูก SHA-256 |
| `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/flow-v2.md` | `structure-v2.md` | ผูก SHA-256 |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-03-change-single/flow-v3.md` | `state-machine-v2.md` | ผูก SHA-256 |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-03-change-single/flow-v3.md` | `structure-v2.md` | ผูก SHA-256 |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/execute/summary.md` | `round-0/execution.md` | ผูก SHA-256 |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/flow-v3.md` | `fr-nfr-v2.md` | ผูก SHA-256 |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/flow-v3.md` | `state-machine-v2.md` | ผูก SHA-256 |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/flow-v3.md` | `structure-v2.md` | ผูก SHA-256 |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-05-report/prompt-used.md` | `step-03-change-single/prompt-used.md` | ผูก SHA-256 |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-05-report/prompt-used.md` | `step-03-change-single/log.jsonl` | ผูก SHA-256 |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-05-report/prompt-used.md` | `step-03-change-single/meta.json` | ผูก SHA-256 |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-05-report/prompt-used.md` | `step-03-change-single/impact.md` | ผูก SHA-256 |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-05-report/prompt-used.md` | `step-03-change-single/tests.json` | ผูก SHA-256 |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-05-report/prompt-used.md` | `step-03-change-single/ui-run-meta.json` | ผูก SHA-256 |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-05-report/prompt-used.md` | `step-03-change-single/check-report.md` | ผูก SHA-256 |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-05-report/prompt-used.md` | `step-04-change-dynamic/prompt-used.md` | ผูก SHA-256 |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-05-report/prompt-used.md` | `step-04-change-dynamic/log.jsonl` | ผูก SHA-256 |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-05-report/prompt-used.md` | `step-04-change-dynamic/meta.json` | ผูก SHA-256 |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-05-report/prompt-used.md` | `step-04-change-dynamic/execute/log.jsonl` | ผูก SHA-256 |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-05-report/prompt-used.md` | `step-04-change-dynamic/execute/meta.json` | ผูก SHA-256 |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-05-report/prompt-used.md` | `step-04-change-dynamic/evaluate/log.jsonl` | ผูก SHA-256 |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-05-report/prompt-used.md` | `step-04-change-dynamic/evaluate/meta.json` | ผูก SHA-256 |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-05-report/prompt-used.md` | `step-04-change-dynamic/plan-v4.json` | ผูก SHA-256 |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-05-report/prompt-used.md` | `step-04-change-dynamic/impact-analysis-change.md` | ผูก SHA-256 |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-05-report/prompt-used.md` | `step-04-change-dynamic/round-0/execution.md` | ผูก SHA-256 |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-05-report/prompt-used.md` | `step-04-change-dynamic/round-0/tests.json` | ผูก SHA-256 |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-05-report/prompt-used.md` | `step-04-change-dynamic/round-0/ui-run-meta.json` | ผูก SHA-256 |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-05-report/prompt-used.md` | `step-04-change-dynamic/evaluation-round-0.md` | ผูก SHA-256 |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-05-report/prompt-used.md` | `change-artifact-check.json` | ผูก SHA-256 |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-05-report/prompt-used.md` | `shared-tests-notes.md` | ผูก SHA-256 |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-05-report/prompt-used.md` | `shared-test-baseline-dom.json` | ผูก SHA-256 |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-05-report/prompt-used.md` | `publication-meta.json` | ผูก SHA-256 |

## ยังไม่ทดสอบ

| รายการ | สถานะ / สิ่งที่ต้องทำต่อ |
|---|---|
| เปิดบนมือถือจริง / สแกน QR จริง | ยังไม่ทดสอบ; viewport ของ desktop ไม่ใช่ผลอุปกรณ์จริง |
| เบราว์เซอร์อื่นและระบบปฏิบัติการอื่น | ยังไม่ทดสอบ |
| เว็บไซต์ภายนอกและ anchor ID | ตรวจเฉพาะปลายทางไฟล์ relative; ไม่ได้ตรวจ HTTP หรือ anchor ภายใน |
| NFR บนระบบจริง | ยังไม่ทดสอบเวลา LAN/Wi-Fi, offline ระหว่างอุปกรณ์, ETA จาก log เซิร์ฟเวอร์, สิทธิ์ฝั่งเซิร์ฟเวอร์ และการติดตั้ง |
| แก้ fixture แล้วตรวจ US ที่ตกซ้ำ | ยังไม่ทำ; คง fixture และ HTML เดิมตามขอบเขต |
| readiness ผล LAB 003 | BLOCKED; ผล merge ไม่รับรองความพร้อมพัฒนา |

แผนและเกณฑ์ระบบจริงอยู่ใน [nfr-split.md](../006_LAB_Test_Scenarios_Traceability/reference/step-04-nfr-split/nfr-split.md); ผล readiness อยู่ใน [merge-validation.json](../003_LAB_Static_Graph_Flow_Structure/reference/step-04-merge/merge-validation.json)

## ข้อจำกัด

- UI เป็น mock-up ข้อมูลในหน่วยความจำ บทบาทและนาฬิกาจำลอง ไม่ได้ต่อระบบหลังบ้านหรือฐานข้อมูลจริง
- PromptPay และการคืนรายการเป็นการจำลอง ไม่มีการรับเงิน โอนเงิน หรือคืนเงินจริง
- ผล pre-run ของบทเรียนเป็นการรันครั้งเดียวต่อเงื่อนไข ไม่ใช่ค่าเฉลี่ย; จำนวนรอบสูงสุดของกิจกรรมไม่ใช่จำนวนรอบที่รันแล้ว
- ค่าที่ไม่มีข้อมูล เช่นต้นทุนเงินหรือยอดจาก log ที่ไม่มี terminal event คง “ไม่มีข้อมูล” ไม่แทนด้วยศูนย์; ยอดรายแถวที่มีหลักฐานยังอ่านจาก CSV ได้
- เก็บ log.jsonl และผลที่ผูก SHA-256 ตามเดิม ไม่ redact path เครื่องหรือข้อความในหลักฐาน เพราะต้องตรวจย้อนกลับและเทียบ hash ได้
- เกณฑ์ล้นตรวจ scrollHeight ตามที่กำหนด ไม่ครอบคลุมการตัดข้อความทุกลักษณะ; รูปและ iframe ภายในมีพื้นที่เลื่อนของตนเอง
- สคริปต์ UI ใช้ --allow-fail ตาม runner เดิม จึงต้องอ่าน failed ใน JSON; exit code สำเร็จไม่ได้แปลว่าทุก scenario ผ่าน
- README เป็นเอกสารแนะนำที่แก้ได้ ส่วน manifest ประวัติที่เคย hash README/ข้อมูลนำเข้าเป็น snapshot ของรอบเดิม ไม่ปรับ hash ย้อนหลัง

### ผลสแกนข้อความที่เหลือ

พบไฟล์ที่ยังมีชื่อขั้นตอนภายใน/alias บัญชี/path เครื่องหรือแหล่งข้อมูลภายใน 161 ไฟล์ในต้นฉบับทั้งหมด; รายไฟล์ หมวด และเลขบรรทัดอยู่ใน [source-audit.json](../tests/source-audit.json) ไม่คัดข้อความเหล่านั้นมาซ้ำในคู่มือ

รายการที่เหลือเป็น log/หลักฐานที่ผูก SHA หรือโค้ด HTML/JSON/ภาพที่อยู่นอกสิทธิ์แก้เนื้อหา จึงยังไม่ผ่านข้อกำหนดล้างข้อความทั้งโฟลเดอร์; README หลัก คู่มือทดสอบ และรายงานนี้ใช้ placeholder และลิงก์สำหรับผู้เรียน

สมมติฐาน QA: ใช้ผลอ้างอิงปัจจุบันเป็นไฟล์ทดสอบ ใช้เกณฑ์จาก fixture เดิมทุกเคส ลิงก์ในไฟล์นักศึกษาต้องเสียศูนย์ ส่วนไฟล์ใน protected-evidence.json รักษาต้นฉบับและรายงาน known issue แยกต่างหาก

การสแกนข้อความทั้งโฟลเดอร์รวมไฟล์ QA พบ 162 ไฟล์; รายงานลิงก์ต้องเก็บ path เสียตามจริงด้วย ส่วน grep ที่ไม่ข้าม binary พบ 182 ไฟล์ เพราะไบต์บีบอัดของ PNG บางไฟล์ตรง pattern สั้นโดยบังเอิญ ดู [text-scan.json](../tests/text-scan.json)

### ผลตรวจตามคำสั่งที่กำหนด

| ชุดตรวจ | exit code | สถานะ |
|---|---|---|
| required scripts and syntax | 0 | ผ่าน |
| results and screenshots | 0 | ผ่าน |
| all relative links | 0 | ผ่าน |
| independent Markdown links | 0 | ผ่าน |
| test report contents | 0 | ผ่าน |
| main README contents | 0 | ผ่าน |
| Git diff balance | 0 | ผ่าน |
| run_all.sh | 0 | ผ่าน |
| relative links with --all | 1 | ผ่านตามคาด: รายงานลิงก์เสียในหลักฐาน |

ผล stdout/stderr ของแต่ละชุดอยู่ใน [validation-results.json](../tests/validation-results.json); ชุด Git diff ผ่านเงื่อนไขคำสั่ง แต่ไม่มี diff ของไฟล์ untracked จึงใช้ integrity report ประกอบด้วย
