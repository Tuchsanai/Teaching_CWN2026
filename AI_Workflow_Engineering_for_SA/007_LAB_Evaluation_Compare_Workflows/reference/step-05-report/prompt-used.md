# ขั้น 7.4 — รายงานเปรียบเทียบ Workflow
## บริบทและ Input
คุณเป็น SA สรุปหลักฐานให้ทีมตัดสินใจเลือก workflow ตามงาน
อ่าน 007_LAB_Evaluation_Compare_Workflows/reference/evidence-index.md, 007_LAB_Evaluation_Compare_Workflows/reference/metrics.csv, 007_LAB_Evaluation_Compare_Workflows/reference/step-01-metrics/metrics-summary.md, 007_LAB_Evaluation_Compare_Workflows/reference/rubric-filled.md,
007_LAB_Evaluation_Compare_Workflows/reference/change-conditions.md และผล single/dynamic/ผลตรวจ/log ที่ index อ้างเท่านั้น
## งานและ Output
สร้าง 007_LAB_Evaluation_Compare_Workflows/reference/step-05-report/comparison-report.md มีขอบเขตทดลอง Input และ hash, เครื่องมือ/รุ่น/โมเดล/effort,
Prompt/Output รุ่นที่ใช้, เพดานงบ/รอบ/เวลา, รายการหลักฐาน และข้อจำกัดการเทียบ
ตาราง LAB ทั้ง 7: คุณภาพ M1–M5, ช่องว่าง, เวลา, รอบ, calls, tokens, ค่าใช้จ่าย และ path
ตารางทดลองข้อเปลี่ยน: Single/Dynamic, ผล criteria เดียวกัน, regression, ภาระรวมและข้อค้าง
ทุกค่าติดประเภท ค่าจริง/ประมาณ/ไม่มีข้อมูล; ห้ามเปลี่ยนผล fixture เป็นผล UI ระบบจริง
ผลจาก reference กับผลของนักศึกษาแยกแถว; ห้ามนำโทเคน reference ไปอ้างว่าเป็นงานนักศึกษา
เรียงเหตุผลจากหลักฐานที่เห็น; ห้ามสรุปเชิงเหตุว่า workflow ทำให้ดีขึ้นจากการทดลองคู่เดียว
อธิบาย tradeoff กรณีงานเล็ก input คงที่ กับงานเปลี่ยน/มี dependency โดยผูกกับหลักฐาน
ส่วนที่ยังไม่วัดให้เป็นแผนตรวจต่อ ไม่เติมตัวเลขหรือข้อสรุปชนะไว้ก่อน
ส่งรายงาน ชิ้นงานรุ่นสุดท้าย ข้อบกพร่อง และรายการระบบจริงที่ยังต้องทดสอบให้ทีม


## ข้อกำหนดการเก็บผลรันล่วงหน้า
ทำรายงาน comparison-report.md ใน cwd ขั้นนี้เท่านั้น; summary.md เป็นข้อความสรุปสั้นที่ CLI เก็บให้ ห้ามเขียนไฟล์อื่นหรือแก้หลักฐานต้นทาง ห้ามใช้ work/ ห้าม git add/commit/push ห้ามเรียก CLI หรือผู้ช่วยเพิ่ม
path ทั้งหมดใน prompt สัมพัทธ์จาก AI_Workflow_Engineering_for_SA/ ให้ resolve ../../../ จาก cwd; ใช้ path แบบนี้ในรายงานและใส่ locator ข้อสรุปสำคัญ
เครื่องมือ Codex CLI 0.154.0; gpt-6-astra (ตาม flag ที่สั่ง CLI ไม่ยืนยันกลับ); effort high; วันที่ UTC ตาม meta ของการรัน
รายงานต้องมีอย่างน้อย 80 บรรทัดเนื้อหามีสาระ (แนะนำ 110–150 บรรทัด) มีหัวข้อ เงื่อนไขทดลอง / ค่าจริง / ค่าประมาณ / ไม่มีข้อมูล / ข้อสังเกตที่ไม่สรุปว่าซับซ้อนกว่าดีกว่าเสมอ / ภาระที่เพิ่มขึ้นต่อ LAB
ครบ 7 LAB พร้อมตารางคุณภาพ เวลา calls โทเคน รอบ และภาระที่เพิ่มขึ้นจากหลักฐานจริง; แยกค่า snapshot 001–006 จากค่าของ 007 ใน lab-metrics-before-report.csv; ต้นทุนการเขียนรายงานรอบนี้ยังไม่มี usage จนจบ ให้กล่าวว่ารายละเอียดสุดท้ายจะอยู่ lab-metrics.csv ไม่แต่งค่าของตัวเอง
ใช้ค่าจาก CSV เท่านั้น; subtotal ที่สังเกตได้ไม่ใช่ยอดเต็ม; 36 log ใน snapshot ไม่มี terminal event; ไม่รวม cached input ซ้ำและไม่เอาเวลา sequential sum ไปเป็น parallel wall
LAB 002 e1-set FAIL→fix→PASS แยกจากลูปหลัก; LAB 004 demo-fix-path เป็น edge=fix ฉีดข้อบกพร่องสาธิต ไม่ใช่ลูปหลัก; LAB 003 ช่วงขนานสะอาด 268.956 s และรวม retry 526.073 s (ประมาณ 526 s เมื่อปัด) แสดงทั้งสองช่วงพร้อม path; LAB 006 ผล UI เดิมผ่าน 12 ตก 2 ห้ามเปลี่ยนเป็นผ่านหมด
ต้นทุนเงินทุกแห่งเขียน ไม่มีข้อมูล เพราะไม่มีตารางราคา; ห้ามประมาณเงินบาทหรือดอลลาร์
คะแนน rubric เป็นประมาณโดย AI และ path verification ไม่ใช่คนรับรองคะแนน; LAB 007 rubric เป็น snapshot ก่อนจบ Single/Dynamic/report คงคะแนนเดิมและบอกช่องว่างด้านเวลาประเมิน
coverage กิจกรรม LAB 004 มี 16 US แม้กล่าวถึง input 18 US; LAB 005 แผน 26 US แต่ baseline FR/UI v2 มี 21 US; LAB 006 traceability26 ไม่ใช่ UI ผ่าน26
ต้องอธิบายข้อบกพร่องร่วมของ baseline scenario index และ missing docs/ui-contract.md; shared tests ตรึงหลังเริ่มการเรียก AI และมีแก้ setup เป็น v2 ตาม DOM baseline ก่อนรัน จึงไม่ใช่ controlled trial สมบูรณ์
อย่าเหมารวมผล Shared UI กับระบบจริงหรือกับการออกแบบ scenarios ที่โมเดลผลิตเอง; แยกเหตุที่ตก/เกณฑ์ยังไม่ครอบคลุมและ STOP_WITH_GAPS ตามผลที่มี
ห้ามเขียนชื่อบัญชีจริง รหัสงานทีมภายใน absolute path ในผล
ให้กล่าวถึงผลนักศึกษาแยกชัดว่า ไม่มีข้อมูล; ไม่อ้าง usage ของ reference เป็นของนักศึกษา

เอกสารเพิ่มที่ต้องอ่าน: 007_LAB_Evaluation_Compare_Workflows/reference/change-compare.md, 007_LAB_Evaluation_Compare_Workflows/reference/lab-metrics-before-report.csv, 007_LAB_Evaluation_Compare_Workflows/reference/step-01-metrics/metrics-notes.md, 007_LAB_Evaluation_Compare_Workflows/reference/publication-meta.json, 007_LAB_Evaluation_Compare_Workflows/reference/shared-tests-notes.md, 007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/evaluation-round-0.md
publication-meta.json บอกการปรับคำ/ชื่อ key ในแผนและ scenarios หลัง evaluate โดยเก็บข้อความรุ่นเดิมใน publication-source/log.jsonl; hash ใน execution/evaluation เป็นรุ่นที่ใช้รันจริง ส่วน hash เผยแพร่เป็นอีกรุ่น ห้ามถือว่าค่าทดสอบหรือคะแนนเปลี่ยน

## เอกสารแนบ: metrics.csv

lab,step,calls,failed,input_tokens,cached_input_tokens,output_tokens,reasoning_tokens,duration_s
001_LAB_Single_Prompt_Baseline,step-01/round-1,1,0,321508,284800,17758,1268,ไม่มีข้อมูล
001_LAB_Single_Prompt_Baseline,step-02/round-1,1,0,386796,331776,12187,498,ไม่มีข้อมูล
001_LAB_Single_Prompt_Baseline,step-03/round-1,1,0,804599,726144,17218,1191,ไม่มีข้อมูล
002_LAB_Loop_FR_NFR,e1-set/step-02/round-1,1,0,395674,353024,10855,295,200.935
002_LAB_Loop_FR_NFR,e1-set/step-02/round-2,1,0,679097,611456,17352,521,313.925
002_LAB_Loop_FR_NFR,e1-set/step-03/round-1,1,0,568817,510592,29273,622,504.05
002_LAB_Loop_FR_NFR,step-01/round-1,1,0,320575,279296,16797,564,297
002_LAB_Loop_FR_NFR,step-02/round-1,1,0,377083,333056,9111,257,173
003_LAB_Static_Graph_Flow_Structure,step-01-fanout/customer,1,0,426099,368512,14491,1237,259.970197083
003_LAB_Static_Graph_Flow_Structure,step-01-fanout/kitchen-front,1,0,418604,364160,13633,834,252.91237089
003_LAB_Static_Graph_Flow_Structure,step-01-fanout/manager,1,0,426966,375040,10398,696,206.347334509
003_LAB_Static_Graph_Flow_Structure,step-01-fanout/manager/round-1/session,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล
003_LAB_Static_Graph_Flow_Structure,step-02-state-machine,1,0,697429,620800,16391,996,315.688285671
003_LAB_Static_Graph_Flow_Structure,step-03-structure,1,0,750324,675712,19623,1805,354.064948025
003_LAB_Static_Graph_Flow_Structure,step-04-merge,1,0,1522112,1403008,20163,2757,400.013340799
004_LAB_Conditional_Graph_UI_Mockup,demo-fix-path/round-2,1,0,270348,225152,3895,419,ไม่มีข้อมูล
004_LAB_Conditional_Graph_UI_Mockup,review,1,0,3252625,3055232,27473,3701,ไม่มีข้อมูล
004_LAB_Conditional_Graph_UI_Mockup,round-1,1,0,829124,756096,23170,2140,ไม่มีข้อมูล
005_LAB_Dynamic_Workflow_Replanning,.,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,0.039076
005_LAB_Dynamic_Workflow_Replanning,session/browser-temp,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,0.003017
005_LAB_Dynamic_Workflow_Replanning,session/evaluations,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,0.116509
005_LAB_Dynamic_Workflow_Replanning,session/evaluations/plan-v1,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,0.047227
005_LAB_Dynamic_Workflow_Replanning,session/evaluations/plan-v2,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,0.073929
005_LAB_Dynamic_Workflow_Replanning,session/evaluations/plan-v3,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,0.012022
005_LAB_Dynamic_Workflow_Replanning,session/execution,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,0.042342
005_LAB_Dynamic_Workflow_Replanning,session/execution/plan-v1/audit-fr-baseline-run,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,0.013906
005_LAB_Dynamic_Workflow_Replanning,session/execution/plan-v1,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,0.008257
005_LAB_Dynamic_Workflow_Replanning,session/execution/plan-v1/test-outline-run,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,0.013333
005_LAB_Dynamic_Workflow_Replanning,session/execution/plan-v2/flow-v2-run,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,0.013447
005_LAB_Dynamic_Workflow_Replanning,session/execution/plan-v2/fr-v2-run,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,0.013335
005_LAB_Dynamic_Workflow_Replanning,session/execution/plan-v2,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,0.01393
005_LAB_Dynamic_Workflow_Replanning,session/execution/plan-v2/outline-v2-run,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,0.013737
005_LAB_Dynamic_Workflow_Replanning,session/execution/plan-v2/ui-v2-run,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,0.013292
005_LAB_Dynamic_Workflow_Replanning,session/execution/ui-v2-evaluator-runtime/feature-shots,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,0.093093
005_LAB_Dynamic_Workflow_Replanning,session/execution/ui-v2-evaluator-runtime/features,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,32.187471
005_LAB_Dynamic_Workflow_Replanning,session/execution/ui-v2-evaluator-runtime,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,0.056159
005_LAB_Dynamic_Workflow_Replanning,session/execution/ui-v2-evaluator-runtime/regression-shots,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,0.225524
005_LAB_Dynamic_Workflow_Replanning,session,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,0.132731
005_LAB_Dynamic_Workflow_Replanning,step-00-input/baseline-filtered,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,0.122037
005_LAB_Dynamic_Workflow_Replanning,step-00-input/baseline-filtered-v2,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,0.108685
005_LAB_Dynamic_Workflow_Replanning,step-00-input/baseline-screen,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,0.945
005_LAB_Dynamic_Workflow_Replanning,step-00-input/baseline-ui-run,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,16.536
005_LAB_Dynamic_Workflow_Replanning,step-00-input/baseline-ui-run/shots,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,0.182578
005_LAB_Dynamic_Workflow_Replanning,step-00-input,1,0,419349,369664,6139,273,131.811
005_LAB_Dynamic_Workflow_Replanning,step-00-input/round-2,1,0,402790,351616,7110,528,143.06
005_LAB_Dynamic_Workflow_Replanning,step-00-input/round-3,1,0,594494,529664,9773,1582,196.94
005_LAB_Dynamic_Workflow_Replanning,step-01-plan-v1/evaluation,1,0,661394,587904,10991,1215,218.179
005_LAB_Dynamic_Workflow_Replanning,step-01-plan-v1,1,0,614588,531712,14771,1621,298.33
005_LAB_Dynamic_Workflow_Replanning,step-02-execute-v1/audit-fr-baseline/evaluation,1,0,3750973,3601152,22563,2435,492.838
005_LAB_Dynamic_Workflow_Replanning,step-02-execute-v1/audit-fr-baseline,1,0,788539,722944,11797,723,237.703
005_LAB_Dynamic_Workflow_Replanning,step-02-execute-v1/draft-test-outline/evaluation,1,0,716975,645248,8041,838,174.496
005_LAB_Dynamic_Workflow_Replanning,step-02-execute-v1/draft-test-outline,1,0,599870,532864,10183,485,205.292
005_LAB_Dynamic_Workflow_Replanning,step-02-execute-v1,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,0.00661
005_LAB_Dynamic_Workflow_Replanning,step-03-reveal-1,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,0.023672
005_LAB_Dynamic_Workflow_Replanning,step-04-plan-v2/evaluation,1,0,707874,632192,8031,293,168.555
005_LAB_Dynamic_Workflow_Replanning,step-04-plan-v2,1,0,772834,700416,16376,1809,313.425
005_LAB_Dynamic_Workflow_Replanning,step-04-plan-v2/round-2,1,0,475042,412032,5654,369,133.544
005_LAB_Dynamic_Workflow_Replanning,step-05-execute-v2/baseline-import,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,0.032292
005_LAB_Dynamic_Workflow_Replanning,step-05-execute-v2/browser-regression,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,16.19
005_LAB_Dynamic_Workflow_Replanning,step-05-execute-v2/browser-regression/shots,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,0.186297
005_LAB_Dynamic_Workflow_Replanning,step-05-execute-v2/draft-test-outline/evaluation,1,0,790587,722688,8881,946,189.368
005_LAB_Dynamic_Workflow_Replanning,step-05-execute-v2/draft-test-outline,1,0,668503,585728,13036,927,248.326
005_LAB_Dynamic_Workflow_Replanning,step-05-execute-v2/evaluation,1,0,1804845,1704192,16896,1634,377.147
005_LAB_Dynamic_Workflow_Replanning,step-05-execute-v2,1,0,1028656,927488,24302,1662,460.839
005_LAB_Dynamic_Workflow_Replanning,step-05-execute-v2/revise-flow/evaluation,1,0,903004,823424,9260,435,189.817
005_LAB_Dynamic_Workflow_Replanning,step-05-execute-v2/revise-flow,1,0,1275863,1158912,22594,1378,420.492
005_LAB_Dynamic_Workflow_Replanning,step-05-execute-v2/revise-fr/evaluation,1,0,584095,517888,8106,557,174.652
005_LAB_Dynamic_Workflow_Replanning,step-05-execute-v2/revise-fr,1,0,465303,394112,11264,562,210.751
005_LAB_Dynamic_Workflow_Replanning,step-05-execute-v2/ui-browser,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,0.038534
005_LAB_Dynamic_Workflow_Replanning,step-05-execute-v2/ui-browser/round-1,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,9.273271
005_LAB_Dynamic_Workflow_Replanning,step-05-execute-v2/ui-browser/round-2,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,10.279308
005_LAB_Dynamic_Workflow_Replanning,step-06-reveal-2,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,0.020942
005_LAB_Dynamic_Workflow_Replanning,step-07-plan-v3/evaluation,1,0,1064474,962944,12340,832,262.52
005_LAB_Dynamic_Workflow_Replanning,step-07-plan-v3,1,0,1062611,956672,20613,2010,383.28
006_LAB_Test_Scenarios_Traceability,step-00-input,1,0,1349396,1254016,10475,897,243.023
006_LAB_Test_Scenarios_Traceability,step-01-fanout/customer,1,0,639601,555392,24275,1777,469.919
006_LAB_Test_Scenarios_Traceability,step-01-fanout/kitchen-front,1,0,1547200,1450240,26511,2834,513.646
006_LAB_Test_Scenarios_Traceability,step-01-fanout/manager,1,0,1701022,1594112,28648,3509,636.925
006_LAB_Test_Scenarios_Traceability,step-02-coverage/fix-1,1,0,676078,596992,18119,1335,334.576
006_LAB_Test_Scenarios_Traceability,step-02-coverage/round-1,1,0,2001703,1862272,18369,2775,383.913
006_LAB_Test_Scenarios_Traceability,step-02-coverage/round-2,1,0,1972697,1832960,17770,1560,355.925
006_LAB_Test_Scenarios_Traceability,step-03-merge,1,0,886509,794880,28339,2379,503.494
006_LAB_Test_Scenarios_Traceability,step-04-nfr-split,1,0,793302,718464,19824,723,378.177
006_LAB_Test_Scenarios_Traceability,step-05-ui-run,1,0,583279,512512,11313,1196,218.734
006_LAB_Test_Scenarios_Traceability,step-05-ui-run/runner,0,0,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,ไม่มีข้อมูล,13.299


## เอกสารแนบ: rubric-filled.md

# JOB-7.2 — ให้คะแนน Rubric จากหลักฐาน

ประเมินตาม `docs/rubric.md` หัวข้อ “เกณฑ์ 5 มิติ ระดับคะแนน 0–3” โดยอ่านเฉพาะ Input ที่กำหนดและหลักฐานใน index; เป็นผลอ้างอิง ไม่ใช่ผลนักศึกษา ทุก path หลักฐานด้านล่างสัมพัทธ์จาก AI_Workflow_Engineering_for_SA/ และเปิดอ่านได้จริงพร้อมตรวจ locator แล้ว การประเมินนี้อ่านเอกสารและ JSON ผลตรวจ ไม่ได้รัน UI ใหม่หรือรับรองภาพด้วยสายตา

**คะแนนตัวเลขทุกช่องเป็นประมาณโดย AI ต้องให้คนตรวจซ้ำก่อนใช้ตัดสิน** ส่วนค่าจริงในเหตุผลหมายถึงค่าที่บันทึกในหลักฐานเดิม ไม่ทำให้คะแนน rubric เป็นค่าจริง ช่อง “ไม่มีข้อมูล” ใช้เมื่อมิติไม่เกี่ยวข้องหรือยังไม่มีผลในขอบเขตนั้น ไม่ใช่ 0; ไม่พบหลักฐานเพียงพอให้ใช้คะแนน 0 ในชุดนี้ ไม่คำนวณคะแนนรวมหรือจัดอันดับ LAB ต่างขอบเขต หากนำไปหาค่าเฉลี่ยภายหลัง ต้องตัดช่องไม่มีข้อมูลออกจากทั้งผลรวมและตัวหาร

ขอบเขตที่ใช้: LAB 001 วิเคราะห์ 26 US; LAB 002–004 ใช้ 18 US ตามชุดส่งต่อ โดย LAB 003 เป็น Flow/โครงสร้างและ LAB 004 เป็น mock UI; LAB 005 ผลชิ้นงานถึง v2 จำนวน 21 US และวิเคราะห์แผน v3 เพิ่มอีก 5 US; LAB 006 ออกแบบทดสอบ 26 US แต่รันเพียง 14 fixture บน UI v2; LAB 007 ประเมินเฉพาะขั้น metrics และการเตรียมทดลองที่มีแล้ว ตาม `007_LAB_Evaluation_Compare_Workflows/reference/evidence-index.md` บรรทัด 3–5 ไม่อนุมานผลทดลองข้อเปลี่ยนหรือรายงานที่ยังไม่เกิด

| LAB | มิติ | คะแนน | หลักฐาน | ค่าจริง/ประมาณ/ไม่มีข้อมูล | เหตุผล |
|---|---|---|---|---|---|
| 001 | M1 | 2 | `001_LAB_Single_Prompt_Baseline/reference/check-report.md` บรรทัด 15–23, 27–52, 69; `001_LAB_Single_Prompt_Baseline/reference/final-work/fr-nfr-v0.md` หัวข้อ Functional Requirements / Non-functional Requirements | ประมาณโดย AI; จำนวนจากรายงานตรวจเป็นค่าจริง | ครบสามกลุ่มบทบาท 26 US, 26 FR, 22 NFR และรักษา AC/ตัวเลข มีวิธีตรวจเป็นส่วนใหญ่ แต่ ETA, จุดเริ่มเวลา, ความจุ และนิยามธุรกิจบางข้อยังรอยืนยัน จึงยังไม่ยืนยันวิธีตัดสิน AC ทุกข้อระดับ 3 |
| 001 | M2 | 2 | `001_LAB_Single_Prompt_Baseline/reference/final-work/fr-nfr-v0.md` หัวข้อ Traceability; `001_LAB_Single_Prompt_Baseline/reference/check-report.md` บรรทัด 62–64, 70–71, 79 | ประมาณโดย AI | US→FR/NFR ย้อนกลับได้ตามขั้นเอกสารที่มี แต่ FR หนึ่งแถวรวมหลายกฎ ตารางสถานะผิดรูปแบบ 35 แถว และลิงก์ภายในสำเนาผลดิบบางรายการยังใช้ฐานตำแหน่งเดิม ต้องแยกตรวจราย clause/ตำแหน่งอ้างอิงก่อนถือว่าตรวจย้อนกลับครบ |
| 001 | M3 | ไม่มีข้อมูล | `001_LAB_Single_Prompt_Baseline/reference/final-work/fr-nfr-v0.md` บรรทัด 5; `001_LAB_Single_Prompt_Baseline/reference/check-report.md` บรรทัด 72 | ไม่มีข้อมูล | ขั้นนี้ส่งมอบเอกสารวิเคราะห์ ยังไม่มีการสร้างและรัน UI ตาม Test Scenarios ตัวเลขใน AC เป็นเกณฑ์อนาคต จึงไม่ใช้เป็นผลผ่านหรือตก |
| 001 | M4 | 2 | `001_LAB_Single_Prompt_Baseline/reference/final-work/fr-nfr-v0.md` หัวข้อ ข้อมูลขาดและข้อขัดแย้ง / ข้อเสนอและสมมติฐานที่ยังไม่ยืนยัน; `001_LAB_Single_Prompt_Baseline/reference/check-report.md` บรรทัด 54–64 | ประมาณโดย AI | แยก Q/DI/สมมติฐาน คงหมายเหตุ ก./ค./ช. ที่ขาดและ US-20 อ้าง US-14 โดยไม่ตอบแทน มีผลกระทบและคำถามส่งต่อ แต่ baseline ยังไม่แก้ตารางสถานะ และไม่มีวงจรแผนก่อน–หลังกับผลตรวจซ้ำให้ยืนยันระดับ 3 ในขั้นนี้ |
| 001 | M5 | 1 | `007_LAB_Evaluation_Compare_Workflows/reference/metrics.csv` แถว lab=001_LAB_Single_Prompt_Baseline, step-01/round-1 ถึง step-03/round-1; `007_LAB_Evaluation_Compare_Workflows/reference/step-01-metrics/metrics-summary.md` แถว LAB 001; `007_LAB_Evaluation_Compare_Workflows/reference/step-01-metrics/metrics-notes.md` บรรทัด 11–15 | ประมาณโดย AI; events/usage ค่าจริง; เวลาใน CSV และเงินไม่มีข้อมูล | มี 3 terminal events, input 1,512,903 และ output 47,163 tokens แต่ duration_s ขาดทั้งสามแถวจากข้อจำกัดตัวเก็บ ไม่ใช่เวลา 0 และไม่ใช่หลักฐานว่า 3 events เท่ากับ 3 รอบลูป เงื่อนไขเทียบทรัพยากรยังไม่ครบ |
| 002 | M1 | 2 | `002_LAB_Loop_FR_NFR/reference/final/fr-nfr-input.md` บรรทัด 3, ตาราง FR แถว FR-10 และตาราง traceability; `002_LAB_Loop_FR_NFR/reference/loop-summary.md` บรรทัด 25–28, 48–53 | ประมาณโดย AI; ผล checker เป็นค่าที่รายงาน | v1 ครบ 18 US/18 FR/15 NFR ในขอบเขตสามบทบาท วิธีตรวจคงตัวเลขและละเอียดขึ้น เช่น 30 ออเดอร์สองเครื่องสามรอบ แต่ยังมีนิยามต้นทางรอยืนยัน ผล 90/90 ของ checker ไม่แปลงเป็น rubric 3 โดยอัตโนมัติ |
| 002 | M2 | 2 | `002_LAB_Loop_FR_NFR/reference/final/fr-nfr-input.md` หัวข้อ ตาราง traceability — 18 แถว; `002_LAB_Loop_FR_NFR/reference/e1-set/summary-e1.md` บรรทัด 3–5, 31–42 | ประมาณโดย AI | เชื่อม US→FR/NFR และส่งต่อ v1 ได้ แต่การตรวจ E1 แยกพบ v1 ขาดรหัส AC/การอ้างวิธีตรวจหลายจุด โดย E1 ผ่านเพียง 2/18 ก่อนแก้ เป็นหลักฐานข้อจำกัดระดับ clause ของ v1; v2-e1 ที่แก้แล้วเป็นชุดสาธิต ไม่ใช่ฉบับส่งต่อหลัก |
| 002 | M3 | ไม่มีข้อมูล | `002_LAB_Loop_FR_NFR/reference/final/fr-nfr-input.md` บรรทัด 7–10; `002_LAB_Loop_FR_NFR/reference/loop-summary.md` บรรทัด 52 | ไม่มีข้อมูล | งานสร้าง–ตรวจ FR/NFR ไม่มี UI runtime ในขอบเขตนี้ PASS ของเอกสารไม่ใช่ผลทดสอบ UI |
| 002 | M4 | 2 | `002_LAB_Loop_FR_NFR/reference/loop-summary.md` บรรทัด 44–53, 59–61; `002_LAB_Loop_FR_NFR/reference/e1-set/summary-e1.md` บรรทัด 21–24, 40–42, 62 | ประมาณโดย AI | ลูปหลักคงคำถามและข้อขัดแย้ง ปรับวิธีตรวจ v0→v1 และหยุดหลัง checker รอบแรกผ่าน จึงไม่มีหลักฐาน fixer/regression ในลูปหลัก ชุด E1 มี FAIL→แก้→PASS และตรวจซ้ำ 92 คู่ แต่ต้องแยกผลนั้น ไม่ใช้ยืนยันความสามารถรับข้อเปลี่ยนของลูปหลักเต็มรูปแบบ |
| 002 | M5 | 2 | `002_LAB_Loop_FR_NFR/reference/loop-log.json` ฟิลด์ rounds, checker_rounds, duration_s, wall_seconds; `002_LAB_Loop_FR_NFR/reference/loop-summary.md` บรรทัด 19, 36, 59; `002_LAB_Loop_FR_NFR/reference/e1-set/loop-log-e1.json` ฟิลด์ rounds, duration_s, wall_seconds | ประมาณโดย AI; เวลา/usage/การนับค่าจริง; เงินไม่มีข้อมูล | หลัก: 2 calls, checker 1 รอบ, เวลาการเรียกรวม 470 s, wall 479 s, input+output 723,566 tokens; มีเพดาน checker 3 รอบ/1800 s ชุด E1 แยก 3 calls, checker 2 รอบ, เวลาการเรียก 1,018.910 s, wall 1,059.808 s ไม่ใช้ยอดรวม 5 calls เป็นลูปหลัก ยังไม่มีการเทียบคุณภาพ/ทรัพยากรภายใต้เงื่อนไขเดียวกันครบระดับ 3 |
| 003 | M1 | 2 | `003_LAB_Static_Graph_Flow_Structure/reference/step-04-merge/merge-report.md` บรรทัด 5–7 และหัวข้อ Coverage / Readiness และการแก้ต้นทาง; `003_LAB_Static_Graph_Flow_Structure/reference/README.md` บรรทัด 75 | ประมาณโดย AI | ขยาย 18 US/18 FR สู่ 30 flows ครบสามบทบาท รวม state/โครงสร้าง แต่ guard, session, สถานะ, ราคาและสิทธิ์บางส่วนยังค้าง ประเมินความครบของการแปลงข้อกำหนดเป็นแบบวิเคราะห์ ไม่เรียกร้อง UI runtime ที่ยังไม่อยู่ในขั้นนี้ |
| 003 | M2 | 2 | `003_LAB_Static_Graph_Flow_Structure/reference/step-04-merge/merge-report.md` หัวข้อ Coverage / Conflict ledger / Merge mapping และบรรทัด 199–210 | ประมาณโดย AI | มี US→FR→Flow→Module/Screen และ mapping รวมต้นทาง ตรวจผลกระทบได้เป็นส่วนใหญ่ แต่ MC-01–MC-03 กับจุดเชื่อม state/guard ยัง unresolved มีเส้นทางส่งกลับผู้ดูแล FR/US จึงไม่ยกระดับ readiness BLOCKED เป็นความสอดคล้องสมบูรณ์ |
| 003 | M3 | ไม่มีข้อมูล | `003_LAB_Static_Graph_Flow_Structure/reference/step-04-merge/merge-report.md` บรรทัด 7; `003_LAB_Static_Graph_Flow_Structure/reference/README.md` บรรทัด 60–75 | ไม่มีข้อมูล | ผล schema/FR/hash และ coverage เป็นการตรวจเอกสาร Flow/โครงสร้าง ยังไม่ได้รัน Mock-up หรือ Test Scenarios ของ UI |
| 003 | M4 | 2 | `003_LAB_Static_Graph_Flow_Structure/reference/step-04-merge/merge-report.md` หัวข้อ Conflict ledger และบรรทัด 197–210 | ประมาณโดย AI | เปิดเผยสามข้อขัดแย้งและผลต่อ flow/state/data/สิทธิ์ คงสมมติฐานและระบุทางแก้ต้นทางครบหลายด้าน แต่ยังไม่มีข้อมูลใหม่ที่ยืนยันแล้ว แผนแก้ที่ execute และผลตรวจซ้ำส่วนใช้ซ้ำ จึงยังไม่ถึงระดับ 3 |
| 003 | M5 | 1 | `003_LAB_Static_Graph_Flow_Structure/reference/parallel-meta.json` ฟิลด์ wall_parallel_seconds; `003_LAB_Static_Graph_Flow_Structure/reference/timing.json` ฟิลด์ wall_parallel_seconds, actual_cli_invocations, missing_stdout_usage; `003_LAB_Static_Graph_Flow_Structure/reference/README.md` บรรทัด 32–37, 81; `007_LAB_Evaluation_Compare_Workflows/reference/step-01-metrics/metrics-notes.md` บรรทัด 20 | ประมาณโดย AI; ช่วงเวลาที่บันทึกค่าจริง; usage บางครั้งและเงินไม่มีข้อมูล | ช่วงขนานสะอาด 268.956 s; ช่วงรวม retry 526.073 s เป็นคนละช่วง ห้ามบวกกัน มีการเรียกจริง 10 ครั้ง แต่ CSV กลางเห็น 6 terminal events และ manager รอบแรกไม่มี stdout usage; เวลาบางช่วงครอบสองการเรียก จึงยังตรวจต้นทุนทุก attempt ไม่ครบ ไม่ใช้ความเร็วขนานให้คะแนนสูง |
| 004 | M1 | 1 | `004_LAB_Conditional_Graph_UI_Mockup/reference/review/review.md` บรรทัด 5, 25, 32, 60; `004_LAB_Conditional_Graph_UI_Mockup/reference/decision-log.md` บรรทัด 15–18 | ประมาณโดย AI | mock มีบทบาทและพฤติกรรมที่ตรวจได้หลายส่วน แต่ FR-07/US-07 ในขอบเขต 18 US ยังไม่มีการคำนวณ ETA ซึ่งเป็นหน้าที่สำคัญ และช่วงรับเปลี่ยนเองโดยนโยบายยังไม่ยืนยัน จึงไม่ถือว่าความครบของ UI ตามข้อกำหนดถึงระดับ 2 เพียงเพราะ smoke ผ่าน |
| 004 | M2 | 2 | `004_LAB_Conditional_Graph_UI_Mockup/reference/review/review.md` ตารางเทียบ Flow/Structure/Check บรรทัด 27–61 โดยเฉพาะ FR-07 บรรทัด 32; `004_LAB_Conditional_Graph_UI_Mockup/reference/decision-log.md` บรรทัด 15–18 | ประมาณโดย AI | เชื่อม Flow/FR/US→Screen→check และข้อสังเกตได้เป็นส่วนใหญ่ แต่ FR-07 ไม่มี check รองรับและ mock ไม่ครบต้นทาง คงข้อขัดแย้งและส่งประเด็นให้ SA จึงยังมีจุดเชื่อมขาด |
| 004 | M3 | 1 | `004_LAB_Conditional_Graph_UI_Mockup/reference/round-1/ui-check.json` ฟิลด์ passed, failed, edge; `004_LAB_Conditional_Graph_UI_Mockup/reference/review/review.md` บรรทัด 7, 25, 32, 60 | ประมาณโดย AI; smoke 19/19 เป็นค่าจริงตาม JSON | ลูปหลัก 19 ผ่าน 0 ตก; ผู้ตรวจรายงาน 38 executions ผ่านบนสอง viewport แต่ชุด smoke ไม่ตรวจ ETA และทางเลือก stale slot เมื่อพิจารณา UI ตามขอบเขตธุรกิจจริงยังมีหน้าที่หลักไม่สำเร็จ จึงให้ระดับ 1 ไม่แก้ raw edge=pass ให้เป็น fail และไม่อ้างว่า assertion เดิมตก |
| 004 | M4 | 2 | `004_LAB_Conditional_Graph_UI_Mockup/reference/decision-log.md` บรรทัด 7–18; `004_LAB_Conditional_Graph_UI_Mockup/reference/review/review.md` บรรทัด 84–100; `004_LAB_Conditional_Graph_UI_Mockup/reference/demo-fix-path/summary.md` บรรทัด 3–7, 45 | ประมาณโดย AI | แยกผล checks จากข้อค้างธุรกิจและสมมติฐาน หยุดตามกราฟและส่งข้อค้นพบหลัง pass ให้ SA แต่ไม่มีแผนใหม่ที่ execute ในลูปหลัก ชุด demo-fix ฉีด defect แล้ว 17/19→19/19 เป็นสาธิตแยก ไม่ใช่การแก้ข้อผิดพลาดจากการสร้างหลัก และยังไม่ได้ทดลอง cancel |
| 004 | M5 | 1 | `007_LAB_Evaluation_Compare_Workflows/reference/metrics.csv` แถว LAB 004 แยก round-1, review, demo-fix-path/round-2; `004_LAB_Conditional_Graph_UI_Mockup/reference/decision-log.md` บรรทัด 9–11; `004_LAB_Conditional_Graph_UI_Mockup/reference/demo-fix-path/summary.md` บรรทัด 61–68; `007_LAB_Evaluation_Compare_Workflows/reference/step-01-metrics/metrics-notes.md` บรรทัด 13, 21 | ประมาณโดย AI; events/usage ค่าจริง; เวลาใน CSV และเงินไม่มีข้อมูล | หลักมีสร้าง 1 และ review 1 event; demo-fix เพิ่ม 1 event แยก ไม่ใช่หลักแก้ 3 รอบ เพดานหลักรวม 3 รอบ duration_s กลางไม่มีข้อมูล ชุด demo มีเวลาเรียก 85.839 s ที่รายงานแยก แต่ไม่ใช้เติมเวลาลูปหลักหรือเหมาว่าวัดครบทั้ง LAB |
| 005 | M1 | 2 | `005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/fr-nfr-v2.md` บรรทัด 6–8 และหัวข้อ FR เพิ่มจาก reveal-1 / NFR เพิ่มจาก reveal-1; `005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/evaluation/evaluator.md` บรรทัด 4–8; `005_LAB_Dynamic_Workflow_Replanning/reference/README.md` บรรทัด 50–53 | ประมาณโดย AI | v2 ครบ 21 US และคง AC เดิม รวม US-09/14/21 แต่กฎ refund/X/สถานะและวิธีพิสูจน์บาง AC ยังไม่ครบ ผล UI ไม่ครอบคลุม full outline; อีก 5 US มีเฉพาะแผน v3 ไม่ใช้เป็นหลักฐานว่าผลิต FR/Flow/UI v3 แล้ว |
| 005 | M2 | 2 | `005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/fr-nfr-v2.md` หัวข้อ Traceability US → FR/NFR / Mapping US → FR → Flow → UI และการใช้ซ้ำ; `005_LAB_Dynamic_Workflow_Replanning/reference/step-07-plan-v3/plan-v3.json` ฟิลด์ limits ข้อจำกัดสายที่มาภายนอกชุด; `005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/evaluation/evaluator.md` บรรทัด 6–8 | ประมาณโดย AI | v2 มี mapping และตรวจ hash/126 เซลล์พร้อมแก้การส่งสถานะครัวถึงหน้าร้าน แต่หลักฐานรับรองสายที่มาภายนอก snapshot ยังจำกัด และผล UI ไม่ครอบคลุมทุก clause แผน v3 ผูก dependency ได้ในระดับแผน ยังไม่ใช่สายชิ้นงาน v3 ที่รันครบ |
| 005 | M3 | 2 | `005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/ui-check-v2.json` ฟิลด์ passed/failed; `005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/ui-feature-check-v2.json` ฟิลด์ passed, unique_scenarios, capacity_rounds; `005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/evaluation/evaluator.md` บรรทัด 6–8 | ประมาณโดย AI; 19/19 และ 8/8 ค่าจริงตามผลตรวจ | เส้นทางหลักที่รันบน mock v2 ผ่าน regression 19/19 และ feature 8/8 ซึ่งเป็น 6 สถานการณ์ไม่ซ้ำ โดย N=5 ซ้ำสาม context เวลา 12:00; threshold 12:15/12:30 และขั้นละเอียดตาม outline ยังไม่ครบ ไม่รวม UI v3 หรือ NFR ระบบจริง |
| 005 | M4 | 3 | `005_LAB_Dynamic_Workflow_Replanning/reference/README.md` บรรทัด 12–19, 25–29; `005_LAB_Dynamic_Workflow_Replanning/reference/step-07-plan-v3/impact-analysis-v3.md` บรรทัด 20–53 และหัวข้อ คำถามรอคำตอบ; `005_LAB_Dynamic_Workflow_Replanning/reference/step-07-plan-v3/evaluation/evaluator.md` บรรทัด 5–9 | ประมาณโดย AI | มีแผน v1→v2→v3 หลังเปิดข้อมูลตามลำดับ แสดงเหตุผล งาน/dependency ที่เปลี่ยน ชิ้นงานกระทบและ reuse/recheck ผูก hash แยกผล v2 ที่ตรวจแล้วจาก v3 NOT_TESTED และมีคำถามมนุษย์ 11 ข้อพร้อมขอบเขตที่บล็อก ให้ 3 เฉพาะความครบของการรับข้อมูลเพิ่มและวางแผน ไม่ใช่ผล execute v3 |
| 005 | M5 | 1 | `005_LAB_Dynamic_Workflow_Replanning/reference/metrics.csv` ทั้ง 22 แถว; `005_LAB_Dynamic_Workflow_Replanning/reference/README.md` บรรทัด 32–42; `007_LAB_Evaluation_Compare_Workflows/reference/step-01-metrics/metrics-summary.md` แถว LAB 005; `007_LAB_Evaluation_Compare_Workflows/reference/step-01-metrics/metrics-notes.md` บรรทัด 11–15 | ประมาณโดย AI; ผลรวมค่าที่บันทึกเป็นค่าจริง; wall ทั้ง workflow/เงินไม่มีข้อมูล | CSV เฉพาะ 22 calls รวมเวลา 5,631.365 s, input 20,152,663/output 278,721; เป็นผลรวมรายเรียก ไม่ใช่เวลารอทั้งกราฟ ยอดกลาง 5,718.442563 s รวมช่วงอื่นด้วยและยอดโทเคนกลางยังไม่มีข้อมูล มีประวัติรอบ แต่ยังไม่พบเพดานทรัพยากรและเงื่อนไขเทียบที่ครบในหลักฐานที่ใช้ จึงยังไม่ถึงระดับ 2 |
| 006 | M1 | 2 | `006_LAB_Test_Scenarios_Traceability/reference/step-03-merge/test-scenarios.md` บรรทัด 3, ดัชนีครบ 26 US; `006_LAB_Test_Scenarios_Traceability/reference/step-04-nfr-split/summary.md` บรรทัด 1–5; `006_LAB_Test_Scenarios_Traceability/reference/step-03-merge/traceability-notes.md` บรรทัด 21–28 | ประมาณโดย AI; จำนวนเอกสารเป็นค่าที่รายงาน | ออกแบบ 114 scenarios ครบสามบทบาท/26 US และแยก functional/NFR 63 แถว คง AC พร้อมทางสำเร็จ/ข้อยกเว้น แต่ oracle ธุรกิจบางส่วนยังขาดและ upstream ห้า US ยังไม่มี active mapping จึงเป็นขั้นต่ำออกแบบ ไม่ใช่วิธีตรวจที่พร้อมตัดสินทุกข้อ |
| 006 | M2 | 2 | `006_LAB_Test_Scenarios_Traceability/reference/step-03-merge/traceability-notes.md` บรรทัด 13–30, 40; `006_LAB_Test_Scenarios_Traceability/reference/step-05-ui-run/ui-run-report.md` บรรทัด 24–45 | ประมาณโดย AI | Traceability ส่วนใหญ่ตาม US/FR/Flow/Screen/TestID ได้และเชื่อมผล 14 fixture ด้วย TestID แต่ US-17/18/22/23/24 มี FR/Flow/Screen MISSING; US-26 ไม่มี Screen ตามขอบเขต CSV ที่แจกแจงผลคูณระดับ US ไม่พิสูจน์ทุกคู่ Flow→Screen รายเหตุการณ์ คงผู้รับผิดชอบ/ช่องว่างและผล fail จึงไม่ถึง 3 |
| 006 | M3 | 1 | `006_LAB_Test_Scenarios_Traceability/reference/step-05-ui-run/ui-test-results.json` ฟิลด์ passed=12, failed=2, skipped=0 และ results.id=TS-US-09-101/TS-US-21-101; `006_LAB_Test_Scenarios_Traceability/reference/step-05-ui-run/ui-run-report.md` บรรทัด 40–55 | ประมาณโดย AI; ผล 12/2/0 เป็นค่าจริงตาม JSON | ผ่าน 12 ตก 2 จาก 14 fixture เส้นทางคืนรายการจบ assertion ไม่สำเร็จเพราะไม่พบ payment-summary-total และครัวเต็มหยุดที่ setup rush-start จึงยังพิสูจน์เส้นทางหลักทั้งชุดไม่ครบ ให้ 1 สำหรับความสำเร็จของการทดสอบ ไม่สรุปว่า logic ธุรกิจสองส่วนเสีย ไม่เปลี่ยน failure เป็น skip/ไม่มีข้อมูล |
| 006 | M4 | 2 | `006_LAB_Test_Scenarios_Traceability/reference/step-02-coverage/decision-log.md` บรรทัด 5–13; `006_LAB_Test_Scenarios_Traceability/reference/step-03-merge/traceability-notes.md` บรรทัด 19–30; `006_LAB_Test_Scenarios_Traceability/reference/step-05-ui-run/ui-run-report.md` หัวข้อ F01 / F02 | ประมาณโดย AI | มีทะเบียนช่องว่าง แก้ coverage หนึ่งรอบจากขั้นต่ำ 19/26→26/26 แล้วหยุด STOP_WITH_GAPS แยกสาเหตุ fixture/ข้อมูลธุรกิจและเสนอผลกระทบการแก้ แต่ F01/F02 ยังไม่แก้และตรวจซ้ำจริง รวมถึง mapping upstream ที่ค้าง จึงยังไม่ครบหลักฐานระดับ 3 |
| 006 | M5 | 2 | `006_LAB_Test_Scenarios_Traceability/reference/metrics.csv` ทั้ง 10 แถว; `006_LAB_Test_Scenarios_Traceability/reference/README.md` บรรทัด 22, 32–36; `006_LAB_Test_Scenarios_Traceability/reference/step-05-ui-run/ui-run-report.md` บรรทัด 20; `007_LAB_Evaluation_Compare_Workflows/reference/step-01-metrics/metrics-summary.md` แถว LAB 006 | ประมาณโดย AI; ผลรวมค่าที่บันทึกเป็นค่าจริง; เงินไม่มีข้อมูล | 10 calls รวมเวลารายเรียก 4,038.332 s, input 12,150,787/output 203,643; browser runner 13.299 s แยก รวมจึงเป็น 4,051.631 s ตามตารางกลาง ไม่ใช่ wall ของ fan-out มีแก้ 1 จากเพดาน 2 รอบและนิยามการนับ แต่ยอด usage กลางยังไม่มีข้อมูลและไม่มีการเทียบเงื่อนไขเดียวกันครบระดับ 3 |
| 007 | M1 | ไม่มีข้อมูล | `007_LAB_Evaluation_Compare_Workflows/reference/change-conditions.md` บรรทัด 5–8; `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/manifest.md` บรรทัด 8–14; `007_LAB_Evaluation_Compare_Workflows/reference/evidence-index.md` บรรทัด 5 | ไม่มีข้อมูล | มี baseline และเงื่อนไข US-21 N=5→N=3 แต่ยังไม่มี FR/Flow/UI/scenarios หลังข้อเปลี่ยนให้ตรวจความครบ ไม่ใช้ชิ้นงานที่นำเข้ามาแทนผลผลิต LAB 007 |
| 007 | M2 | 2 | `007_LAB_Evaluation_Compare_Workflows/reference/step-01-metrics/metrics-notes.md` บรรทัด 11–25 และตาราง source; `007_LAB_Evaluation_Compare_Workflows/reference/step-01-metrics/metrics-summary.md` นิยามการนับและตารางต่อ LAB; `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/manifest.md` บรรทัด 8–14 | ประมาณโดย AI | ประเมินเฉพาะความสอดคล้อง/ตรวจย้อนกลับของงานวัดขั้น 7.1 และทะเบียน baseline ที่มีแล้ว: metrics ระบุ lab/step/source และ manifest ระบุ version/hash แต่ยังมีความเสี่ยงนับสำเนาซ้ำและช่วงเวลาต่างขอบเขต ไม่ใช้คะแนนนี้รับรอง traceability ของชิ้นงานทดลองข้อเปลี่ยนที่ยังไม่มี |
| 007 | M3 | ไม่มีข้อมูล | `007_LAB_Evaluation_Compare_Workflows/reference/evidence-index.md` บรรทัด 5; `007_LAB_Evaluation_Compare_Workflows/reference/change-conditions.md` บรรทัด 5–11 | ไม่มีข้อมูล | ยังไม่มีผลรัน UI หลังข้อเปลี่ยนของ Single/Dynamic ใน snapshot ที่อนุญาตอ่าน ข้อกำหนดให้ทดสอบสามรอบเป็นเงื่อนไข ไม่ใช่หลักฐานผ่าน |
| 007 | M4 | ไม่มีข้อมูล | `007_LAB_Evaluation_Compare_Workflows/reference/change-conditions.md` บรรทัด 4–9; `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/manifest.md` บรรทัด 14; `007_LAB_Evaluation_Compare_Workflows/reference/evidence-index.md` บรรทัด 5 | ไม่มีข้อมูล | เตรียม baseline/แผนก่อนเปลี่ยนและเพดานแล้ว แต่ยังไม่มีแผนหลัง N=3, impact และผลตรวจของสอง workflow จึงยังให้คะแนนการรับมือข้อเปลี่ยนครั้งนี้ไม่ได้ |
| 007 | M5 | ไม่มีข้อมูล | `007_LAB_Evaluation_Compare_Workflows/reference/step-01-metrics/metrics-summary.md` แถว LAB 007; `007_LAB_Evaluation_Compare_Workflows/reference/step-01-metrics/metrics-notes.md` บรรทัด 6–8; `007_LAB_Evaluation_Compare_Workflows/reference/change-conditions.md` บรรทัด 7–11 | ไม่มีข้อมูล | snapshot metrics เก็บก่อนการเรียก AI ของ LAB 007 จึงไม่มี usage/เวลา/รอบของการทดลองนี้ เพดาน 3600 s/8,000,000 tokens ไม่ใช่ค่าที่ใช้จริง และไม่แต่งเวลา/โทเคนของ JOB-7.2 ผู้ทดลองจะอ่านจาก log หลังจบเอง เงินไม่มีข้อมูล |

## summary

- ข้อบกพร่องที่ต้องตามต่อ: LAB 001 ตารางสถานะผิด 35 แถวและการอ้างอิงในสำเนายังมีข้อจำกัด; LAB 002 ฉบับส่งต่อ v1 ยังขาดการอ้าง AC รายข้อบางส่วน แม้ชุด E1 แก้ได้; LAB 003 ยัง BLOCKED จาก MC-01–MC-03; LAB 004 ขาด ETA และนโยบาย stale slot; LAB 005 v2 ยังตรวจ full outline ไม่ครบและ v3 ยังเป็นแผน; LAB 006 คงผล **ผ่าน 12 ตก 2** และ mapping ห้า US ที่ขาด ตามหลักฐานรายแถวข้างต้น
- หลักฐานที่ยังต้องเก็บด้านข้อกำหนด: คำตอบเจ้าของระบบต่อหมายเหตุ ก./ค./ช., สถานะพร้อมเสิร์ฟ, จุดเริ่มเวลา, refund, X, เขตเวลาและกฎรายงาน พร้อมรุ่นที่อนุมัติและผลกระทบต่อ AC/Flow/UI/Test ดู `003_LAB_Static_Graph_Flow_Structure/reference/step-04-merge/merge-report.md` หัวข้อ Readiness และการแก้ต้นทาง และ `005_LAB_Dynamic_Workflow_Replanning/reference/step-07-plan-v3/impact-analysis-v3.md` หัวข้อ คำถามรอคำตอบ
- หลักฐาน UI ที่ยังต้องเก็บ: fixture รุ่นใหม่สำหรับ TS-US-09-101/TS-US-21-101 พร้อม diff/รุ่น/ผลรันซ้ำและ regression โดยรักษา 12/2 เดิม; เปิดภาพและบันทึก visual review; ตรวจ threshold ต่างหน้าต่างและชุด US-09/14 ครบ AC เมื่อพร้อม ดู `006_LAB_Test_Scenarios_Traceability/reference/step-05-ui-run/ui-run-report.md` บรรทัด 47–64 และ `005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/evaluation/evaluator.md` บรรทัด 8 ไม่ใช้ mock รับรอง LAN, Security, Load, Availability หรือการติดตั้งจริง
- หลักฐานทรัพยากรที่ยังต้องเก็บ: ผูก run/attempt กับ log และ metadata เพื่อตัดสำเนาซ้ำ แยกเวลารายเรียก/ช่วงขนาน/เวลาทั้ง workflow/เวลา browser/เก็บหลักฐาน และอธิบาย usage ที่ขาดก่อนเปรียบเทียบ ช่วงสะอาด LAB 003 **268.956 s** กับรวม retry **526.073 s** ต้องคงแยก; e1-set และ demo-fix ต้องแยกจากลูปหลัก เงินทุก LAB **ไม่มีข้อมูล** ไม่ใช้ 0 และไม่ลดคะแนนเพียงเพราะเปิดเผยว่าไม่มีราคา ตาม `007_LAB_Evaluation_Compare_Workflows/reference/step-01-metrics/metrics-notes.md` บรรทัด 8–22
- สำหรับ LAB 007 ต้องเก็บผล Single/Dynamic หลัง N=3 พร้อมชิ้นงานแต่ละรุ่น, impact, ผลตรวจและ log ภายใต้เงื่อนไขร่วมก่อนสรุปความคุ้มค่า ตาม `007_LAB_Evaluation_Compare_Workflows/reference/change-conditions.md` บรรทัด 4–11 หนึ่งคู่ทดลองไม่ใช่ค่าเฉลี่ย และคะแนนดิบของ LAB ต่างขอบเขตไม่ใช้จัดอันดับ workflow
- **รอคนตรวจซ้ำทุกคะแนนของ AI** โดยเฉพาะขอบเขตการตีความ M3 ของ LAB 004/006 และ M2 ของ LAB 007 ให้บันทึกผู้ตรวจ วันที่ รุ่นหลักฐาน และเหตุผลเมื่อปรับคะแนน ขณะนี้ยังไม่มีผลตรวจซ้ำโดยคน ไม่คัดเกณฑ์ rubric ฉบับยาวซ้ำในรายงานนี้


## เอกสารแนบ: change-compare.md

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


## เอกสารแนบ: LAB 007 measured runs before report

step,duration_s,input_tokens,output_tokens
step-01-metrics,1.522843869,ไม่มีข้อมูล,ไม่มีข้อมูล
step-02-rubric,284.932,1288765,14155
step-03-change-single,411.758,1420196,20384
step-04-change-dynamic/evaluate,196.386,785183,9120
step-04-change-dynamic/execute,304.658,852970,15295
step-04-change-dynamic,206.7,320947,11163

