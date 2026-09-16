# แผนภาพ AI Workflow Engineering for SA

สร้างวันที่ 2026-09-14 (UTC) ด้วย Excalidraw CLI `mcp-excalidraw-server` 2.0.0 และ canvas ภายในเครื่อง

มี 16 แผนภาพหลัก × 3 รูปแบบ และสำเนาประจำ LAB 7 ชุด × 3 รูปแบบ รวม 69 ไฟล์ภาพ/แผนภาพ และ README นี้ 1 ไฟล์

- `.excalidraw`: scene JSON ที่ยังแก้กล่อง ข้อความ และลูกศรได้
- `.png`: ภาพสำหรับอ่านหรือแทรกสไลด์ ตรวจภาษาไทยจากภาพจริงแล้ว
- `.svg`: ภาพเวกเตอร์ที่เก็บข้อความเป็น text; การแสดงฟอนต์บนเครื่องอื่นขึ้นกับฟอนต์ที่มี

## แผนภาพหลัก

| ชื่อ | เนื้อหาและ LAB ที่ใช้ | ไฟล์ |
|---|---|---|
| 01-workflow-ladder | บันได 5 ขั้น + LAB 001–007 ใช้เปิดภาพรวมบทเรียน | [excalidraw](01-workflow-ladder.excalidraw) / [png](01-workflow-ladder.png) / [svg](01-workflow-ladder.svg) |
| 02-single-prompt | Single Prompt · LAB 001 | [excalidraw](02-single-prompt.excalidraw) / [png](02-single-prompt.png) / [svg](02-single-prompt.svg) |
| 03-loop | Loop สร้าง–ตรวจ–แก้ · LAB 002 | [excalidraw](03-loop.excalidraw) / [png](03-loop.png) / [svg](03-loop.svg) |
| 04-static-graph | Static Graph แยก 3 บทบาท · LAB 003 | [excalidraw](04-static-graph.excalidraw) / [png](04-static-graph.png) / [svg](04-static-graph.svg) |
| 05-conditional-graph | Conditional Graph ตรวจ UI · LAB 004 | [excalidraw](05-conditional-graph.excalidraw) / [png](05-conditional-graph.png) / [svg](05-conditional-graph.svg) |
| 06-dynamic-replanning | Dynamic Workflow + Re-planning · LAB 005 | [excalidraw](06-dynamic-replanning.excalidraw) / [png](06-dynamic-replanning.png) / [svg](06-dynamic-replanning.svg) |
| 07-architecture | สถาปัตยกรรมร้าน · ประกอบ LAB 001–006 โดยเฉพาะ LAB 003 | [excalidraw](07-architecture.excalidraw) / [png](07-architecture.png) / [svg](07-architecture.svg) |
| 08-state-machine | สถานะออเดอร์/การจ่ายเงิน/โต๊ะ · ประกอบ LAB 003–006 | [excalidraw](08-state-machine.excalidraw) / [png](08-state-machine.png) / [svg](08-state-machine.svg) |
| 09-test-traceability | Scenario และ Traceability · LAB 006 | [excalidraw](09-test-traceability.excalidraw) / [png](09-test-traceability.png) / [svg](09-test-traceability.svg) |
| 10-evaluation | ประเมินและเปรียบเทียบ · LAB 007 | [excalidraw](10-evaluation.excalidraw) / [png](10-evaluation.png) / [svg](10-evaluation.svg) |
| 11-loop-cycle | ทฤษฎี Loop: Generate–Evaluate–Feedback–Revise, Regression และเงื่อนไขหยุด | [excalidraw](11-loop-cycle.excalidraw) / [png](11-loop-cycle.png) / [svg](11-loop-cycle.svg) |
| 12-graph-patterns | ทฤษฎี Graph: Sequential, Fan-out, Fan-in และ Split–Parallel–Merge | [excalidraw](12-graph-patterns.excalidraw) / [png](12-graph-patterns.png) / [svg](12-graph-patterns.svg) |
| 13-conditional-dag-loop | ทฤษฎี Graph: Static/Conditional และ DAG/Graph ที่มี Loop | [excalidraw](13-conditional-dag-loop.excalidraw) / [png](13-conditional-dag-loop.png) / [svg](13-conditional-dag-loop.svg) |
| 14-dynamic-planner-loop | ทฤษฎี Dynamic: Problem–Planner–Plan–Executor–Result–Evaluator, Finish/Re-plan และ Planning Constraints | [excalidraw](14-dynamic-planner-loop.excalidraw) / [png](14-dynamic-planner-loop.png) / [svg](14-dynamic-planner-loop.svg) |
| 15-replan-operations | ทฤษฎี Re-planning: Add, Split, Cancel, Reorder, Dependency พร้อม Plan Versioning และ Reuse | [excalidraw](15-replan-operations.excalidraw) / [png](15-replan-operations.png) / [svg](15-replan-operations.svg) |
| 16-theory-ladder | บันไดทฤษฎีทั่วไป 8 ขั้น พร้อมคำถามที่แต่ละระดับตอบ ไม่ผูก LAB | [excalidraw](16-theory-ladder.excalidraw) / [png](16-theory-ladder.png) / [svg](16-theory-ladder.svg) |

## สำเนาประจำ LAB

ทุกไฟล์คัดลอกด้วย `cp` จากแผนภาพหลักและต้องตรงกันทุกไบต์

| LAB | แผนภาพต้นทาง | ไฟล์ใน LAB |
|---|---|---|
| 001 · Single Prompt Baseline: วิเคราะห์ User Story และร่าง FR/NFR ในคำสั่งเดียว | 02-single-prompt | `workflow-001`: [excalidraw](../001_LAB_Single_Prompt_Baseline/img/workflow-001.excalidraw) / [png](../001_LAB_Single_Prompt_Baseline/img/workflow-001.png) / [svg](../001_LAB_Single_Prompt_Baseline/img/workflow-001.svg) |
| 002 · Loop Engineering: สร้าง–ตรวจ–แก้ FR/NFR จนผ่านเกณฑ์ | 03-loop | `workflow-002`: [excalidraw](../002_LAB_Loop_FR_NFR/img/workflow-002.excalidraw) / [png](../002_LAB_Loop_FR_NFR/img/workflow-002.png) / [svg](../002_LAB_Loop_FR_NFR/img/workflow-002.svg) |
| 003 · Static Graph: Flow, State, โมดูล, ข้อมูล, หน้าจอ, สิทธิ์ แบบ fan-out/fan-in | 04-static-graph | `workflow-003`: [excalidraw](../003_LAB_Static_Graph_Flow_Structure/img/workflow-003.excalidraw) / [png](../003_LAB_Static_Graph_Flow_Structure/img/workflow-003.png) / [svg](../003_LAB_Static_Graph_Flow_Structure/img/workflow-003.svg) |
| 004 · Conditional Graph: สร้าง UI Mock-up ที่เล่นได้จริงจาก Flow | 05-conditional-graph | `workflow-004`: [excalidraw](../004_LAB_Conditional_Graph_UI_Mockup/img/workflow-004.excalidraw) / [png](../004_LAB_Conditional_Graph_UI_Mockup/img/workflow-004.png) / [svg](../004_LAB_Conditional_Graph_UI_Mockup/img/workflow-004.svg) |
| 005 · Dynamic Workflow + Re-planning: Planner–Executor–Evaluator รับข้อมูลใหม่ระหว่างงาน | 06-dynamic-replanning | `workflow-005`: [excalidraw](../005_LAB_Dynamic_Workflow_Replanning/img/workflow-005.excalidraw) / [png](../005_LAB_Dynamic_Workflow_Replanning/img/workflow-005.png) / [svg](../005_LAB_Dynamic_Workflow_Replanning/img/workflow-005.svg) |
| 006 · Test Scenarios และตาราง Traceability US→FR→Flow→UI→Test | 09-test-traceability | `workflow-006`: [excalidraw](../006_LAB_Test_Scenarios_Traceability/img/workflow-006.excalidraw) / [png](../006_LAB_Test_Scenarios_Traceability/img/workflow-006.png) / [svg](../006_LAB_Test_Scenarios_Traceability/img/workflow-006.svg) |
| 007 · ประเมินและเปรียบเทียบ Workflow ด้วย Rubric และค่าที่วัดได้จริง | 10-evaluation | `workflow-007`: [excalidraw](../007_LAB_Evaluation_Compare_Workflows/img/workflow-007.excalidraw) / [png](../007_LAB_Evaluation_Compare_Workflows/img/workflow-007.png) / [svg](../007_LAB_Evaluation_Compare_Workflows/img/workflow-007.svg) |

## แหล่งข้อมูลและสมมติฐาน

- เนื้อหาอ้าง [case-study-source.md](../docs/case-study-source.md) และ [ภาพรวมบทเรียน](../README.md)
- ภาพทั้งหมดวาดใหม่ด้วย rectangle + text element แยกกัน (fontFamily 2 / Helvetica พร้อมฟอนต์ไทย fallback) ไม่ใช้ label บน shape ไม่ใช้ภาพจาก HTML เดิม และไม่ใส่ชื่อบัญชีจริง
- ภาพ 03 นับรอบสร้าง–ตรวจเป็น 1 รอบและจำกัด 3 รอบตามโจทย์; ภาพ 05 ใช้เพดานตัวอย่าง 3 รอบ พร้อมหยุดเมื่อไม่คืบหน้า ไม่ใช่ผลนับรอบที่รันแล้ว
- ภาพ 06 เปิดเผยข้อมูลเดิมตามแผน: ครั้งที่ 1 US-09/14/21; ครั้งที่ 2 US-17/18/22/23/24 ส่วนรายละเอียด plan v1/v2/v3 เป็นตัวอย่างประกอบ — ยังไม่ได้รันจริง
- ภาพ 07 สมมติให้ผู้สั่งกลับบ้านเชื่อม Wi-Fi ร้านตามขอบเขตระบบภายในร้าน ไม่มีข้อกำหนดยืนยันการสั่งจากอินเทอร์เน็ตภายนอก
- ภาพ 08 แสดง “เสร็จแล้ว” และ “พร้อมเสิร์ฟ” แยกกล่องเพื่อคงถ้อยคำ US-05/07/11 โดยเส้นประหมายถึงการเทียบชื่อ **สมมติฐาน: เสร็จแล้ว = พร้อมเสิร์ฟ** ตามแผนบทเรียน ไม่ใช่การเพิ่มขั้นสถานะธุรกิจ
- เมื่อรายการทำไม่ได้ ให้เข้าสู่ “รอลูกค้าตัดสินใจ” ตาม US-14 ได้ทั้งก่อนเริ่มทำและระหว่างทำ; การส่งรายการที่เปลี่ยนเมนูกลับเข้า “รับออเดอร์” เป็นสมมติฐานการเข้าคิวใหม่ ส่วนคืนรายการคือลบรายการและปรับยอด ไม่ใช่ชื่อสถานะใหม่
- สถานะจ่ายเงินใช้ “ยังไม่จ่าย/ค้างจ่าย/จ่ายแล้ว”; โต๊ะใช้ “เปิด/ปิด” ตามโจทย์และ US-15/16 แยกจากสถานะออเดอร์
- ภาพ 09 ใช้ placeholder ในตัวอย่างแถว traceability เพื่อไม่สร้างรหัส FR/Flow/Test ที่อาจไม่ตรงกับชิ้นงานจริง ต้องแทนด้วยรหัสจากงาน LAB
- ภาพ 10 เป็นวิธีรวบรวมและประเมินผล ไม่ได้อ้างคะแนนหรือทรัพยากรที่วัดได้แล้ว
- ไม่เติมหมายเหตุ ก./ค./ช. ที่ต้นฉบับระบุว่าไม่พบข้อมูล
- สร้าง README นี้ตามคำสั่งใน Goal และ การตรวจไฟล์ ที่ระบุโดยตรง แม้รายการ glob ในหัวข้อ files ไม่ได้ใส่ README ไว้

## สิ่งที่ทำจริงและข้อจำกัด

อ่านสกิล Excalidraw และข้อมูลต้นทาง จากนั้นวาดทีละแผนภาพด้วย CLI `clear` → `add`/`apply` → `screenshot` → ตรวจภาพ → `export`/SVG → `cp` เข้าโครงการ เก็บ snapshot canvas ก่อนเริ่ม และเก็บภาพร่าง/รอบแก้เดิมไว้ที่พื้นที่ export ของเครื่องมือ

พื้นที่ export: `<EXPORT_DIR>/` ใช้ชื่อ `การจัดทำภาพ-final-<ชื่อ>` สำหรับภาพ 01/02/03/06/07/10, `การจัดทำภาพ-final-r2-<ชื่อ>` สำหรับภาพ 04/05/08 และ `การจัดทำภาพ-final-r3-09-test-traceability` สำหรับภาพ 09

ตรวจ PNG จริงทุกภาพทั้งตัวอักษรไทย ระยะกล่อง และทิศลูกศร แก้จุดคำกำกับทับเส้นทางก่อนส่งออกฉบับส่งมอบ วัดข้อความด้วย canvas measureText ใน Chromium ของ canvas หลัง document.fonts.ready

ไม่ได้รัน Prompt นักศึกษา ไม่ได้รัน scenario ของระบบร้าน และไม่ได้ประเมินคุณภาพ workflow จริงใน การจัดทำภาพ นี้ ดังนั้นผล pre-run / เวลา / รอบ / โทเคนของ LAB = **ไม่มีข้อมูล** ภาพกระบวนการเป็นตัวอย่างประกอบ — ยังไม่ได้รันจริง เพราะงานนี้รับผิดชอบการสร้างแผนภาพเท่านั้น

ไฟล์ SVG และ scene ไม่รับประกันฟอนต์ไทยเหมือนกันทุกเครื่อง หากแก้บนเครื่องอื่นควรมีฟอนต์ไทยแบบ sans-serif และตรวจภาพใหม่ PNG เป็นหลักฐานหน้าตาที่ตรวจแล้ว ส่วนลูกศรเป็นเส้นกำหนดจุดโดยตรง เมื่อย้ายกล่องใน editor อาจต้องปรับเส้นตาม

## รายการไฟล์ครบทุก path

Path ต่อไปนี้สัมพันธ์กับ โฟลเดอร์แม่ของบทเรียน:

- `AI_Workflow_Engineering_for_SA/img/01-workflow-ladder.excalidraw`
- `AI_Workflow_Engineering_for_SA/img/01-workflow-ladder.png`
- `AI_Workflow_Engineering_for_SA/img/01-workflow-ladder.svg`
- `AI_Workflow_Engineering_for_SA/img/02-single-prompt.excalidraw`
- `AI_Workflow_Engineering_for_SA/img/02-single-prompt.png`
- `AI_Workflow_Engineering_for_SA/img/02-single-prompt.svg`
- `AI_Workflow_Engineering_for_SA/img/03-loop.excalidraw`
- `AI_Workflow_Engineering_for_SA/img/03-loop.png`
- `AI_Workflow_Engineering_for_SA/img/03-loop.svg`
- `AI_Workflow_Engineering_for_SA/img/04-static-graph.excalidraw`
- `AI_Workflow_Engineering_for_SA/img/04-static-graph.png`
- `AI_Workflow_Engineering_for_SA/img/04-static-graph.svg`
- `AI_Workflow_Engineering_for_SA/img/05-conditional-graph.excalidraw`
- `AI_Workflow_Engineering_for_SA/img/05-conditional-graph.png`
- `AI_Workflow_Engineering_for_SA/img/05-conditional-graph.svg`
- `AI_Workflow_Engineering_for_SA/img/06-dynamic-replanning.excalidraw`
- `AI_Workflow_Engineering_for_SA/img/06-dynamic-replanning.png`
- `AI_Workflow_Engineering_for_SA/img/06-dynamic-replanning.svg`
- `AI_Workflow_Engineering_for_SA/img/07-architecture.excalidraw`
- `AI_Workflow_Engineering_for_SA/img/07-architecture.png`
- `AI_Workflow_Engineering_for_SA/img/07-architecture.svg`
- `AI_Workflow_Engineering_for_SA/img/08-state-machine.excalidraw`
- `AI_Workflow_Engineering_for_SA/img/08-state-machine.png`
- `AI_Workflow_Engineering_for_SA/img/08-state-machine.svg`
- `AI_Workflow_Engineering_for_SA/img/09-test-traceability.excalidraw`
- `AI_Workflow_Engineering_for_SA/img/09-test-traceability.png`
- `AI_Workflow_Engineering_for_SA/img/09-test-traceability.svg`
- `AI_Workflow_Engineering_for_SA/img/10-evaluation.excalidraw`
- `AI_Workflow_Engineering_for_SA/img/10-evaluation.png`
- `AI_Workflow_Engineering_for_SA/img/10-evaluation.svg`
- `AI_Workflow_Engineering_for_SA/img/11-loop-cycle.excalidraw`
- `AI_Workflow_Engineering_for_SA/img/11-loop-cycle.png`
- `AI_Workflow_Engineering_for_SA/img/11-loop-cycle.svg`
- `AI_Workflow_Engineering_for_SA/img/12-graph-patterns.excalidraw`
- `AI_Workflow_Engineering_for_SA/img/12-graph-patterns.png`
- `AI_Workflow_Engineering_for_SA/img/12-graph-patterns.svg`
- `AI_Workflow_Engineering_for_SA/img/13-conditional-dag-loop.excalidraw`
- `AI_Workflow_Engineering_for_SA/img/13-conditional-dag-loop.png`
- `AI_Workflow_Engineering_for_SA/img/13-conditional-dag-loop.svg`
- `AI_Workflow_Engineering_for_SA/img/14-dynamic-planner-loop.excalidraw`
- `AI_Workflow_Engineering_for_SA/img/14-dynamic-planner-loop.png`
- `AI_Workflow_Engineering_for_SA/img/14-dynamic-planner-loop.svg`
- `AI_Workflow_Engineering_for_SA/img/15-replan-operations.excalidraw`
- `AI_Workflow_Engineering_for_SA/img/15-replan-operations.png`
- `AI_Workflow_Engineering_for_SA/img/15-replan-operations.svg`
- `AI_Workflow_Engineering_for_SA/img/16-theory-ladder.excalidraw`
- `AI_Workflow_Engineering_for_SA/img/16-theory-ladder.png`
- `AI_Workflow_Engineering_for_SA/img/16-theory-ladder.svg`
- `AI_Workflow_Engineering_for_SA/001_LAB_Single_Prompt_Baseline/img/workflow-001.excalidraw`
- `AI_Workflow_Engineering_for_SA/001_LAB_Single_Prompt_Baseline/img/workflow-001.png`
- `AI_Workflow_Engineering_for_SA/001_LAB_Single_Prompt_Baseline/img/workflow-001.svg`
- `AI_Workflow_Engineering_for_SA/002_LAB_Loop_FR_NFR/img/workflow-002.excalidraw`
- `AI_Workflow_Engineering_for_SA/002_LAB_Loop_FR_NFR/img/workflow-002.png`
- `AI_Workflow_Engineering_for_SA/002_LAB_Loop_FR_NFR/img/workflow-002.svg`
- `AI_Workflow_Engineering_for_SA/003_LAB_Static_Graph_Flow_Structure/img/workflow-003.excalidraw`
- `AI_Workflow_Engineering_for_SA/003_LAB_Static_Graph_Flow_Structure/img/workflow-003.png`
- `AI_Workflow_Engineering_for_SA/003_LAB_Static_Graph_Flow_Structure/img/workflow-003.svg`
- `AI_Workflow_Engineering_for_SA/004_LAB_Conditional_Graph_UI_Mockup/img/workflow-004.excalidraw`
- `AI_Workflow_Engineering_for_SA/004_LAB_Conditional_Graph_UI_Mockup/img/workflow-004.png`
- `AI_Workflow_Engineering_for_SA/004_LAB_Conditional_Graph_UI_Mockup/img/workflow-004.svg`
- `AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/img/workflow-005.excalidraw`
- `AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/img/workflow-005.png`
- `AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/img/workflow-005.svg`
- `AI_Workflow_Engineering_for_SA/006_LAB_Test_Scenarios_Traceability/img/workflow-006.excalidraw`
- `AI_Workflow_Engineering_for_SA/006_LAB_Test_Scenarios_Traceability/img/workflow-006.png`
- `AI_Workflow_Engineering_for_SA/006_LAB_Test_Scenarios_Traceability/img/workflow-006.svg`
- `AI_Workflow_Engineering_for_SA/007_LAB_Evaluation_Compare_Workflows/img/workflow-007.excalidraw`
- `AI_Workflow_Engineering_for_SA/007_LAB_Evaluation_Compare_Workflows/img/workflow-007.png`
- `AI_Workflow_Engineering_for_SA/007_LAB_Evaluation_Compare_Workflows/img/workflow-007.svg`
- `AI_Workflow_Engineering_for_SA/img/README.md`

## ผล การตรวจไฟล์ ที่รันจริง

รันคำสั่ง การจัดทำภาพ ทั้ง 6 ชุดจาก รายการตรวจการจัดทำภาพ ด้วย bash ใน workspace วันที่ 2026-09-14 UTC: **ผ่าน 6/6 (exit 0 ทุกชุด)**

- ชุด 1: ผ่าน — ไฟล์หลัก 10 × 3 มีจริงและไม่ว่าง
- ชุด 2: ผ่าน — JSON ทุกไฟล์อ่านได้ มี ≥ 6 element และภาษาไทย
- ชุด 3: ผ่าน — PNG หลักและสำเนา LAB ทุกไฟล์ > 10,000 bytes
- ชุด 4: ผ่าน — ไฟล์ประจำ LAB 001–007 ครบทั้ง 3 รูปแบบ
- ชุด 5: ผ่าน — SVG มีแท็ก svg และ README มี mapping workflow-00 ครบ
- ชุด 6: ผ่าน — cmp สำเนา PNG ของ LAB 002 และ LAB 005 ตรงกับต้นฉบับ

การตรวจเพิ่มเติมที่รันจริง: PNG หลักทั้ง 10 ไฟล์ decode ได้; SVG หลักทั้ง 10 ไฟล์ parse XML ได้; scene หลักทุกไฟล์แยก text จาก rectangle ใช้ fontFamily 2 และลูกศรมีหัวบอกทิศทาง ไม่พบกล่องทับกันหรือชื่อบัญชีจริง ข้อความทั้งหมด 289 element ผ่านการวัดความกว้างใน Chromium โดยไม่พบข้อความในกล่องล้นขอบ

PNG หลักมีขนาด 134,141–275,714 bytes สำเนา LAB ทั้ง 21 ไฟล์ตรงกับต้นฉบับทุกไบต์ และไฟล์หลักทั้ง 30 ไฟล์ตรงกับไฟล์ export ที่ตรวจภาพแล้วทุกไบต์ ตรวจ PNG ด้วยสายตาทีละภาพครบ 10 ภาพ (ฉบับแก้ที่ส่งมอบ) ไม่ได้ถือ JSON validation เป็นผลตรวจหน้าตา


## ภาพทฤษฎี 11–16: แหล่งข้อมูล สมมติฐาน และสิ่งที่ทำจริง

เพิ่มภาพทฤษฎีทั่วไปตามโจทย์ใน `.work/router/context/task.md` เพื่อสอนก่อนเข้า LAB โดยใช้ rectangle + text แยกกัน, fontFamily 2 (Helvetica พร้อมฟอนต์ไทย fallback), สีและรูปแบบต่อเนื่องจากภาพเดิม และไม่มีชื่อบัญชีจริง ภาพ 01–10 และสำเนา LAB คงเดิม

- ภาพ 11–13 วาดใน T07 วันที่ 2026-09-14 UTC; T08 อ่านและตรวจซ้ำโดยไม่แก้ไขไฟล์
- ภาพ 14–16 วาดด้วย `npx -y mcp-excalidraw-server` **2.0.0** บน canvas `127.0.0.1:3000` หลัง T07 เสร็จและผ่านเกณฑ์ exit 0 ตรวจ `date -u` ขณะเริ่มวาดได้ 2026-09-14 เวลา 23:59:11, 23:59:32 และ 23:59:53 UTC ตามลำดับ; ส่งออกและตรวจงานเสร็จวันที่ **2026-09-15 UTC**
- สำรอง canvas ไป `/tmp/t08-canvas-before.excalidraw` แล้วทำตามลำดับ `clear --yes` → `add` JSON → `screenshot` ตรวจภาพ → `export --out img/NN.excalidraw` → `screenshot --out img/NN.png` → `screenshot --format svg --out img/NN.svg`
- วัดข้อความภาพ 14–16 ทั้ง 108 text element ด้วย canvas `measureText()` ใน Chromium หลัง `document.fonts.ready`; ปรับถ้อยคำที่กว้างเกินพื้นที่ 4 จุด และตรวจซ้ำไม่พบข้อความเกินความกว้างที่กำหนด จัดป้าย B2/B3 ให้อยู่กลางกล่อง และจัดลูกศรบันไดให้เดินเหนือกล่อง
- เปิด PNG ฉบับส่งมอบจริงครบ 11–16 ตรวจข้อความไทย เครื่องหมาย ลูกศร ทางแยก/ทางย้อน และการทับซ้อน ภาพทั้งหกมีขนาด 1620×740 px จากพื้นที่วาด 1600×720 พร้อมขอบส่งออก
- ภาพ 11 ใช้เพดานตัวอย่าง 5 รอบ และไม่ดีขึ้น 2–3 รอบ; ภาพ 13 ใช้คะแนนผ่านตัวอย่าง 8 ทั้งหมดเป็นเกณฑ์สาธิต ไม่ใช่ผลทดลองที่วัดได้
- ภาพ 12 สมมติว่างานขนานไม่ขึ้นต่อกัน และรวมผลตามเกณฑ์รับงาน; ภาพ 13 แยกการเลือกเส้นทางออกจากการมีวงย้อน ซึ่งเป็นคนละมุมมองของกราฟ
- ภาพ 14 ใช้ข้อจำกัดตัวอย่างไม่เกิน 10 งาน ไม่เกินงบ และไม่เปลี่ยนเป้าหมายหลัก; การหยุดเพราะข้อจำกัดไม่ได้แปลว่าผ่านเกณฑ์
- ภาพ 15 แต่ละแถวเป็นตัวอย่างอิสระ การยกเลิก C และตัวอย่าง Reuse ที่ C ไม่ผ่านจึงไม่ใช่สถานะของแผนเดียวกัน ใช้ A/B ซ้ำได้เมื่อยังถูกต้องและตรวจผลกระทบแล้ว ส่วน D ยังไม่ทำ
- ภาพ 16 เป็นบันได 8 ขั้นทั่วไป แต่ละขั้นเพิ่มความสามารถและผสมแนวคิดได้ ไม่ได้บังคับว่าทุกงานต้องใช้ขั้นสูงสุด และไม่ได้แทนภาพ 01 ที่ผูกกับ LAB
- งานนี้สร้างและตรวจแผนภาพเท่านั้น ไม่ได้รัน workflow ตัวอย่างหรืออ้างผลคุณภาพ/เวลา/งบที่วัดจริง SVG และ scene ยังคงข้อความแก้ไขได้ แต่ฟอนต์ไทยบนเครื่องอื่นขึ้นกับฟอนต์ที่ติดตั้ง ลูกศรใช้จุดพิกัด จึงอาจต้องปรับตามเมื่อย้ายกล่อง

### ผลตรวจไฟล์ 11–16 ที่รันจริง · 2026-09-15 UTC

รัน Python (`json`, `re`, `struct`, Pillow, `xml.etree.ElementTree`, `hashlib`) ตรวจ 18 ไฟล์: **ผ่าน exit 0** ทุกไฟล์มีอยู่และไม่ว่าง, scene เป็น Excalidraw มีภาษาไทยและลูกศร, text แยกจากกล่องและใช้ fontFamily 2, ลูกศรมีหัวบอกทิศ, PNG มี signature ถูกต้องและ decode ได้, ขนาดอย่างน้อย 1200×400 และมากกว่า 10,000 bytes, SVG parse XML ได้และมี text ภาษาไทย

| ภาพ | Elements | ลูกศร | Text | PNG (px) | PNG (bytes) |
|---|---:|---:|---:|---|---:|
| 11-loop-cycle | 39 | 7 | 24 | 1620×740 | 213,941 |
| 12-graph-patterns | 64 | 15 | 27 | 1620×740 | 143,517 |
| 13-conditional-dag-loop | 58 | 11 | 30 | 1620×740 | 171,822 |
| 14-dynamic-planner-loop | 45 | 7 | 28 | 1620×740 | 195,907 |
| 15-replan-operations | 81 | 18 | 38 | 1620×740 | 197,146 |
| 16-theory-ladder | 58 | 7 | 42 | 1620×740 | 197,669 |

ตรวจ SHA-256 เทียบไฟล์ใน `img/` ที่มีอยู่ก่อน T08 (ยกเว้น README ที่ต้องอัปเดต): ตรงกันทุกไฟล์ รวมภาพ 11–13; ตรวจหน้าตาจาก PNG จริงแยกจากผลตรวจโครงสร้างไฟล์

รันคำสั่งเกณฑ์ผ่าน T08 ที่ผู้ใช้ให้มาครบทั้งชุดด้วย `bash -c` แล้ว: **exit code 0** ตรวจไฟล์ 14–16 ครบ 9 ไฟล์, JSON/ภาษาไทย/ลูกศร, PNG signature/ขนาด/จำนวน bytes, แท็ก SVG, การอ้าง PNG และ path Excalidraw ของ 11–16 ใน README และข้อความ “16 แผนภาพหลัก” ผ่านทั้งหมด
