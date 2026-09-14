# ขั้น 5.3/5.5 — Planner ปรับแผนจากข้อมูลที่เปิดเผย

## บริบทและเป้าหมาย
คุณเป็น Planner ปรับชุดงานและ dependency โดยรักษาประวัติและผลงานที่ยังใช้ได้
PREV_PLAN = /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/plan-v2.json
REVEAL_FILE = /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-06-reveal-2/reveal-2.md
## Input
- /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/plan-v2.json และ Markdown คู่กัน; ต้องเป็นแผนล่าสุดที่มีผลตรวจ
- /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-06-reveal-2/reveal-2.md พร้อม reveal ก่อนหน้าที่เปิดแล้วตาม trigger ของ PREV_PLAN
- /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/input/plan.schema.json, /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/provenance.md, /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/input-audit.md
- ผล execution/evaluations และ artifacts ที่ PREV_PLAN อ้าง รวม impact analysis รุ่นก่อนถ้ามี
- /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/us-initial.md และสัญญา UI ที่ใช้อยู่
## งาน
ยืนยันว่า PREV_PLAN เป็น v1 เมื่อเปิด reveal-1 ครั้งแรก หรือ v2 เมื่อเปิด reveal-2 ครั้งแรก
เมื่อใช้แก้ข้อบกพร่องแผนในรอบเพิ่มเติม ให้เพิ่มเลข N ต่อจากแผนสูงสุดจริงและบันทึก trigger การแก้
อ่านทุกคอลัมน์ reveal ตรงตัว; ระบุชัดว่าเปิดเผยข้อมูลจากต้นฉบับ ไม่ใช่ข้อกำหนดใหม่
วิเคราะห์ผลโดยตรงและ transitive จาก US ไป FR/NFR, Flow/state, ข้อมูล, UI, การตรวจ
รวมสถานะจาก execution/evaluations จริง; done ต้องมีผลตรวจรองรับ ไม่เดาจากการมีไฟล์
ตัดสิน create/revise/verify/cancel แยกรายงาน พร้อมระบุงานเพิ่ม งานแยก งานยกเลิก งานจัดลำดับใหม่
หากประเภทใดไม่จำเป็น ให้เขียนว่าไม่เปลี่ยนและเหตุผล ไม่สร้างงานเกินจำเป็นเพื่อให้ครบประเภท
คง id ของหน้าที่เดิม; งานที่แยกใช้ id ใหม่พร้อม mapping ต้นทาง; เก็บงานยกเลิกไว้เป็น cancelled
แก้ dependency ทั้งผู้ผลิต ผู้ตรวจ และผู้ใช้ผล; ห้ามอ้าง output ที่ยกเลิกไปแล้ว
ทำให้ FR v2 และผลตรวจมาก่อน Flow v2 และผลตรวจ จากนั้นจึง UI v2 และผลตรวจ
ระบุ outputs รุ่น v2 เป็น /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/fr-nfr-v2.md, /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/flow-v2.md, /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/ui-mockup-v2.html
สำหรับ reveal-2 อย่างน้อยวางแผนครบและวิเคราะห์ผลกระทบ; งานผลิต v3 จะยัง planned ได้
ทำตาราง reuse แยกส่วนที่ใช้ซ้ำได้กับส่วนต้องตรวจใหม่พร้อม hash/evidence และเหตุผล
AI จัดงานได้ แต่ห้ามอนุมัตินโยบายคืนเงินจริง สูตร X หรือการแมปสถานะที่ต้นฉบับไม่ชัด
human-required ต้องมีคำถามใน decisions และ blocking limits ที่ผูก affected_tasks
ตรวจ schema และ DAG; JSON/Markdown ต้องตรงกันและคงข้อมูลรุ่นเดิมไว้ครบ
## รูปแบบ Output และตำแหน่งบันทึก
สร้าง /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/plan-vN.json ตาม /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/input/plan.schema.json โดย N=เลข PREV_PLAN+1
สร้าง /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/plan-vN.md พร้อมหัวข้อ Diff จากเวอร์ชันก่อน, เหตุผล, ข้อจำกัด
Diff ใช้คอลัมน์ task id | งาน/dependency เดิม | งาน/dependency ใหม่ | การเปลี่ยน | หลักฐาน
trigger ระบุ path reveal และเหตุที่ปรับ; created_at เป็น UTC จริง; เก็บ decisions/reuse/limits
ไม่เขียนทับ PREV_PLAN หรือ artifacts เดิม และไม่ทำงาน Executor ใน session นี้
ส่งแผนคู่ใหม่ไป prompts/05-impact-analysis.md แล้วให้ Evaluator ตรวจ ก่อนทำงานผลิตตามแผน

## กติกาสำหรับทุกบทบาท
working directory = AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/
เริ่ม session ใหม่ ไม่ใช้ resume/continue ไม่เรียก agent เพิ่ม และไม่พึ่งประวัติสนทนา
อ่านเฉพาะไฟล์ Input ที่อนุญาตในขั้นนี้ ไม่ค้นทั้ง repository หรืออ่าน reveal ล่วงหน้า
รักษาข้อความ US/AC ตัวเลข หน่วย และสัดส่วนทดสอบ ห้ามแต่งข้อกำหนดหรือผลตรวจ
แยกแผนงาน AI จาก state machine ของรายการ/ออเดอร์/ชำระเงิน/โต๊ะ
ใช้ชื่อบัญชีและข้อมูลจำลองเท่านั้น ไม่ใช้บัญชีจริงหรือบริการชำระเงินจริง
เขียนเฉพาะ /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/; ห้ามแก้ input/, prompts/, reference/, img/ หรือต้นทาง LAB อื่น
ห้ามเขียนทับเวอร์ชันเดิมหรือหลักฐานเดิม; ถ้าเป้าหมายมีแล้ว ให้หยุดและรายงาน path
แผนเป็น snapshot; สถานะการทำงานใหม่เก็บใน execution/evaluations แล้วรวมในแผนรุ่นถัดไป
ถ้า Input ขาดหรือมี blocking limit ที่เกี่ยวกับงาน ให้ตอบ BLOCKED พร้อมสิ่งที่ขาด ไม่สร้างข้อมูลแทน
ข้อเสนอที่ต้นฉบับไม่ระบุให้ติดป้ายสมมติฐาน/ยังไม่ยืนยัน ไม่แปลงเป็น AC
ไม่อ่านเว็บเพื่อเติมกฎร้าน; หมายเหตุ ก./ค./ช. ที่หายให้คงเป็นข้อค้าง
ผลสรุปต้องบอกไฟล์ที่สร้างจริง ข้อค้าง และสิ่งที่ยังไม่ทดสอบ


# วิเคราะห์ผลกระทบและขอบเขตใช้ซ้ำ

## บริบทและเป้าหมาย
คุณเป็นผู้วิเคราะห์ผลกระทบ เปรียบเทียบแผนก่อน–หลังกับข้อมูลที่เปิดเผยจริง
PREV_PLAN = /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/plan-v2.json
CURRENT_PLAN = /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/plan-v3.json
REVEAL_FILE = /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-06-reveal-2/reveal-2.md
## Input
- /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/plan-v2.json และ Markdown คู่กัน
- /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/plan-v3.json และ Markdown คู่กัน
- /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-06-reveal-2/reveal-2.md และ reveal ก่อนหน้าที่เปิดแล้วเท่านั้น
- artifacts, execution/evaluations และ baseline ที่ทั้งสองแผนอ้าง
- /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/impact-analysis.md และ impact-analysis รุ่นก่อนถ้ามี
## งาน
ตรวจว่าแผนสองรุ่นต่อเนื่องและ trigger อ้าง reveal ที่กำหนด; ถ้าไม่ตรงให้หยุด
ติดตาม US → FR/NFR → Flow/state/data → UI → งานตรวจ และ dependency ต่อเนื่องทุกชั้น
แยกการเพิ่มข้อมูลจากต้นฉบับออกจากสมมติฐานของผู้วิเคราะห์
แยกการเปลี่ยนงาน AI ออกจากการเปลี่ยนสถานะออเดอร์; ไม่ใช้สองเรื่องแทนกัน
วิเคราะห์ผลต่อ US-05/07/08/12/15/19 โดยอ้างหลักฐานที่เกี่ยวข้องจริง
ถ้าไม่กระทบข้อใดให้ระบุเหตุผล/หลักฐาน ไม่เว้นว่างจนดูเหมือนไม่ได้ตรวจ
ตรวจยอดคืนรายการ สถานะจ่ายแล้ว ราคาที่เก็บกับออเดอร์ และผลต่อรายงานโดยไม่แต่งนโยบายเงินคืน
ตรวจช่วงเร่งด่วน/เวลารอว่าไม่สรุปเป็นค่าเดียวกันโดยไม่มีคำยืนยัน
ระบุส่วนที่ใช้ซ้ำได้พร้อมรุ่นและ hash; ส่วนที่เปลี่ยน upstream ต้อง needs_recheck หรือ replace พร้อมเหตุ
ระบุคำถามที่ต้องถามมนุษย์ งานที่ติดข้อค้าง และวิธีตรวจหลังมีคำตอบ
สำหรับ reveal-2 ต้องวิเคราะห์ครบทั้งห้า US แม้ยังไม่ผลิต FR/Flow/UI v3
## รูปแบบ Output และตำแหน่งบันทึก
สร้าง /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/impact-analysis-vN.md โดย N จาก CURRENT_PLAN และห้ามเขียนทับ
ตารางหลักใช้คอลัมน์: แผนเดิม | ข้อมูลใหม่ | งาน/dependency ที่เปลี่ยน | ชิ้นงานที่กระทบ | ส่วนที่ใช้ซ้ำ/ตรวจใหม่
ทุกแถวระบุ task id, US และ locator/hash ตามไฟล์ที่อ่านจริง พร้อมสถานะการยืนยัน
มีหัวข้อ ผลกระทบโดยตรง, ผลกระทบต่อเนื่อง, คำถามรอคำตอบ, ข้อจำกัด, งานถัดไป
สร้าง /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/impact-analysis.md ในครั้งแรก; ครั้งต่อไปเพิ่มท้ายทั้ง section รุ่นใหม่เท่านั้น
รักษาเนื้อหา section รุ่นเดิมทุกตัวอักษร ไม่เขียนทับประวัติหรือแก้ผลย้อนหลัง
ถ้ามี section รุ่นนี้แล้ว ให้หยุดเพื่อเลือกการรันใหม่ ไม่เพิ่มผลซ้ำ
ถ้าพบแผนตกหล่นให้รายงานแก่ Planner; ห้ามแก้แผนรุ่นเดิมเอง

## กติกาสำหรับทุกบทบาท
working directory = AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/
เริ่ม session ใหม่ ไม่ใช้ resume/continue ไม่เรียก agent เพิ่ม และไม่พึ่งประวัติสนทนา
อ่านเฉพาะไฟล์ Input ที่อนุญาตในขั้นนี้ ไม่ค้นทั้ง repository หรืออ่าน reveal ล่วงหน้า
รักษาข้อความ US/AC ตัวเลข หน่วย และสัดส่วนทดสอบ ห้ามแต่งข้อกำหนดหรือผลตรวจ
แยกแผนงาน AI จาก state machine ของรายการ/ออเดอร์/ชำระเงิน/โต๊ะ
ใช้ชื่อบัญชีและข้อมูลจำลองเท่านั้น ไม่ใช้บัญชีจริงหรือบริการชำระเงินจริง
เขียนเฉพาะ /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/; ห้ามแก้ input/, prompts/, reference/, img/ หรือต้นทาง LAB อื่น
ห้ามเขียนทับเวอร์ชันเดิมหรือหลักฐานเดิม; ถ้าเป้าหมายมีแล้ว ให้หยุดและรายงาน path
แผนเป็น snapshot; สถานะการทำงานใหม่เก็บใน execution/evaluations แล้วรวมในแผนรุ่นถัดไป
ถ้า Input ขาดหรือมี blocking limit ที่เกี่ยวกับงาน ให้ตอบ BLOCKED พร้อมสิ่งที่ขาด ไม่สร้างข้อมูลแทน
ข้อเสนอที่ต้นฉบับไม่ระบุให้ติดป้ายสมมติฐาน/ยังไม่ยืนยัน ไม่แปลงเป็น AC
ไม่อ่านเว็บเพื่อเติมกฎร้าน; หมายเหตุ ก./ค./ช. ที่หายให้คงเป็นข้อค้าง
ผลสรุปต้องบอกไฟล์ที่สร้างจริง ข้อค้าง และสิ่งที่ยังไม่ทดสอบ


# ข้อกำหนดเฉพาะการรันผลอ้างอิง (ใช้แทนข้อกำหนด path ด้านบน)
เริ่ม session ใหม่ ใช้เฉพาะเครื่องมือใน session นี้ ห้ามเรียก agent/CLI เพิ่ม ห้ามค้นทั้ง repository. ห้ามอ่าน README ของ LAB เพราะมีข้อมูลล่วงหน้า. ห้ามเขียนนอก /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference. ไม่แก้ input/prompts หรือต้นทาง. พื้นที่ work ของการรันนี้คือ /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session. ห้ามเขียนทับไฟล์ที่มีอยู่. ห้ามใส่ชื่อบัญชีจริงหรือรหัสงานทีมในไฟล์.
รอบนี้ทำ Planner + impact-analysis ต่อเนื่องเท่านั้นหลัง reveal-2 เปิดจริง; ไม่ execute v3.
สร้าง /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/plan-v3.json (schema draft07, UTCจริง), /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/plan-v3.md และ /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/impact-analysis-v3.md พร้อมสำเนาตรง /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-07-plan-v3/impact-analysis-v3.md.
Markdown กระชับประมาณ80–120บรรทัด มี Diff จาก v2, task/dependency, เหตุผลเพิ่ม/แยก/ยกเลิก/จัดลำดับ (ไม่มีการเปลี่ยนประเภทใดบอกเหตุ), reuse/recheck, limits.
เพิ่ม section v3 ท้าย /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/impact-analysis.md โดยรักษาเนื้อหาเก่าทั้งหมดตาม prompt; ห้ามเขียนทับ v1/v2/ชิ้นงาน/ผลตรวจ.
ใช้ actual evidence ปัจจุบัน: /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/handoff-v2.md, ui-v2-check.md, fr-v2-check.md, flow-v2-check.md, test-outline-v2-check.md, plan-v2-review.md; /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/execution/ui-v2-observations.json และ ui-v2-evaluator-evidence.json. canonical /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/evaluator.md. F-01 closedในเอกสารและ status-sync mock. UI v2 PASS เฉพาะเอกสาร/ชุดofflineที่รัน:19/19เดิม,8/8ใหม่=6สถานการณ์ N5ซ้ำ3contextเวลา12:00. fulloutline/US09/14ชุด5/5/LAN/เงินจริง/ETA/installยังNOT_TESTED. อย่าเขียน done เกินขอบเขต; ผลเก่าใช้เป็นประวัติ งานได้รับผลใหม่ต้อง needs_recheck.
อ่าน reveal2 จากสำเนาที่เปิดแล้ว /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-06-reveal-2/reveal-2.md + reveal1 ตามเดิม. วิเคราะห์ทั้ง US-17/18/22/23/24 ชัดเจนใน tasks และ impact table แผนเดิม→ข้อมูลใหม่→งาน/dependencyที่เปลี่ยน→ชิ้นงานกระทบ→ใช้ซ้ำ/ตรวจใหม่ พร้อม locator. โดยเฉพาะ round/orderยอดรวม→payment/report/CSV; timestamp/count→queue/ETA/capacity; takeaway-toggle→US02/04/15ไม่ทำลายQRหน้าร้าน; paid-only/adjustedvsoriginal→report; stock-out event(actor/time/count)→history.
รักษา AC ตัวเลขทุกคอลัมน์ ไม่แต่งนโยบายเงินคืน/รายงานหรือสูตรX; สถานะงานAIแยกสถานะออเดอร์. อะไรต้องตอบจากมนุษย์มี blocking limit ที่ affected_tasksถูกต้อง. วาง tasks producer/verify ครบinputoutputs dependencyไม่ใช้ v2 PASS แทน v3. แผนนี้วิเคราะห์ได้โดยไม่มีงานexecute v3.
ไม่ค้นทั้งrepo ไม่อ่านเว็บ/READMEหรือAGENTที่อื่น ไม่เรียกagent/CLIเพิ่ม. อ่านเฉพาะ inputs/pathในคำสั่งและที่planอ้าง. ไม่ใส่ชื่อบัญชี/คำรหัสทีมลงไฟล์.
ก่อนจบตรวจschema+DAGจริง บันทึก /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/plan-v3-validation.json แต่ไม่ทำ Evaluatorแทน; ส่งให้ sessionใหม่ต่อไป.
