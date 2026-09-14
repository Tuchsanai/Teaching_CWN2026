# แผนภาพ AI Workflow Engineering for SA

สร้างวันที่ 2026-09-14 (UTC) ด้วย Excalidraw CLI `mcp-excalidraw-server` 2.0.0 และ canvas ภายในเครื่อง

มี 10 แผนภาพหลัก × 3 รูปแบบ และสำเนาประจำ LAB 7 ชุด × 3 รูปแบบ รวม 51 ไฟล์ภาพ/แผนภาพ และ README นี้ 1 ไฟล์

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
