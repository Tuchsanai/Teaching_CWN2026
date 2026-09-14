# plan-v1 — แผนเอกสารและ offline mock

เวอร์ชัน: `plan-v1`
created_at (UTC จริง): `2026-09-14T12:35:53.783903Z`

## เป้าหมาย

baseline: baseline-filtered-v2 / INPUT_READY เฉพาะเอกสารและ offline mock ตาม /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/input-audit.md และ /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/provenance.md; แผนแรกจากช่องว่างหลักฐานตรวจ ไม่ใช่ต่อจากตัวอย่าง plan-v0

วางแผนแรกเพื่อผลิตรายงานตรวจเทียบ FR และโครงร่างทดสอบ พร้อมตรวจเอกสารและ offline mock จาก baseline-filtered-v2 ที่ INPUT_READY เท่านั้น. ใช้ 18 แถว US ที่เปิดแล้ว; รหัสอ้างภายใน US-20 ไม่เพิ่มขอบเขต และไม่กู้ข้อความที่ปิดใน US-12 หรือเอกสารอื่น. อ่าน plan-v0.example.json เพื่อรูปแบบเท่านั้น ไม่ใช้เป็นเวอร์ชันก่อน. ไม่เปิด reveal, README, baseline อื่น, diff, audit เก่า, logs หรือเว็บ.

## Diff จากเวอร์ชันก่อน

เป็นแผนแรกของการรันนี้ ไม่ใช่ผลต่อจากตัวอย่าง v0; ตัวอย่างใช้ดูรูปแบบเท่านั้น ไม่มีสถานะงานจากตัวอย่างที่ยกมาใช้. ทุก task ใน snapshot เป็น planned.

## ลำดับทำและ priority

P0: verify-plan ต้อง PASS ก่อน Executor. P1: audit-fr-baseline → verify-fr. P2: หลัง verify-fr PASS งาน verify-flow และ draft-test-outline พร้อมทำได้อิสระ; หากมีผู้ทำคนเดียวให้ verify-flow ก่อนเพื่อลดความเสี่ยงการส่งต่อ แล้ว draft-test-outline. P3: verify-test-outline รอทั้ง draft-test-outline และผลตรวจ verify-fr/verify-flow. P4: verify-ui รอ outline และผลตรวจที่จำเป็นครบ. P5: evaluate-handoff รอทุก upstream และ PASS ที่จำเป็น. ลำดับปฏิบัติแบบคนเดียวคือ verify-plan → audit-fr-baseline → verify-fr → verify-flow → draft-test-outline → verify-test-outline → verify-ui → evaluate-handoff. นี่เป็นลำดับตาม gate ไม่ใช่ตำแหน่ง tasks ใน JSON; ไม่เรียก agent เพิ่มในรอบ Planner นี้.

## งาน/dependency

### verify-plan — Evaluator ตรวจ plan-v1 ทั้ง JSON/Markdown ก่อน Executor เริ่ม

kind: `verify`; status: `planned`
US refs: US-01, US-02, US-03, US-04, US-05, US-06, US-07, US-08, US-10, US-11, US-12, US-13, US-15, US-16, US-19, US-20, US-25, US-26
depends_on: ไม่มี

Inputs:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/plan-v1.json`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/plan-v1.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/input/plan.schema.json`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/plan-v1-validation.json`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/provenance.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/input-audit.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/fr-nfr.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/flow.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/state-machine.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/structure.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-mockup.html`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-contract.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/us-initial.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/fr-check.json`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/flow-check.json`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-check.json`

Outputs ที่วางแผน ยังไม่ได้สร้าง:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/plan-v1-review.md`

เหตุผลและ dependency ทุกเส้น: ไม่มี dependency เพราะเป็น gate แรกของแผน ไม่ใช่งาน Executor; Evaluator ตรวจคู่ JSON/Markdown และหลักฐาน Planner validation โดยตรวจ draft-07 พร้อม date-time format, unique id, dependency target, DAG, path และขอบเขตซ้ำ ตรวจเหตุผลทุกเส้น ลำดับทำงาน ข้อค้างและ reuse เทียบ hash baseline จริง; ผลต้องระบุ hash ของแผนทั้งสองไฟล์, verdict PASS/FAIL/BLOCKED, ขอบเขตเอกสาร/offline mock และรายการแก้พร้อม affected task IDs. PASS อนุญาตเฉพาะ Executor ตามแผนนี้; ผล Planner validation ไม่แทนผล Evaluator.

### audit-fr-baseline — Executor สร้างรายงานตรวจเทียบ FR/NFR ตั้งต้นกับ US ที่เปิดแล้ว

kind: `create`; status: `planned`
US refs: US-01, US-02, US-03, US-04, US-05, US-06, US-07, US-08, US-10, US-11, US-12, US-13, US-15, US-16, US-19, US-20, US-25, US-26
depends_on: verify-plan

Inputs:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/plan-v1-review.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/provenance.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/input-audit.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/us-initial.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/fr-nfr.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/fr-check.json`

Outputs ที่วางแผน ยังไม่ได้สร้าง:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/execution/fr-baseline-audit-v1.md`

เหตุผลและ dependency ทุกเส้น: verify-plan → audit-fr-baseline: ต้องมีผล Evaluator PASS ผูก hash แผนก่อน Executor เริ่ม. ช่องว่างคือยังไม่มีรายงานเทียบ FR/NFR ของ session นี้: สร้าง matrix ของ 18 US/18 FR และ NFR ที่เกี่ยวข้อง คัดข้อความ US/AC จากสำเนาตรงตัว พร้อม path/บรรทัด/hash; แยกข้อความเดิมจากวิธีตรวจที่เสนอ ตรวจตัวเลข หน่วย สัดส่วน จุดวัด และ scope. บันทึก Q เฉพาะรหัสที่มีจริง ไม่กู้ข้อความที่ปิดไว้ ไม่สร้าง FR ใหม่จากรหัสในเซลล์; แยกผล upstream 108/108 จากข้อสังเกตใหม่และให้สถานะข้อที่ยังตรวจไม่ได้ตามจริง. รายงานนี้ยังต้องผ่าน verify-fr ไม่ใช่ใบรับรองระบบ.

### verify-fr — Evaluator ตรวจรายงานเทียบ FR/NFR และสิทธิ์ใช้ baseline ต่อ

kind: `verify`; status: `planned`
US refs: US-01, US-02, US-03, US-04, US-05, US-06, US-07, US-08, US-10, US-11, US-12, US-13, US-15, US-16, US-19, US-20, US-25, US-26
depends_on: audit-fr-baseline

Inputs:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/execution/fr-baseline-audit-v1.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/plan-v1-review.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/us-initial.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/fr-nfr.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/provenance.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/input-audit.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/fr-check.json`

Outputs ที่วางแผน ยังไม่ได้สร้าง:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/fr-v1-check.md`

เหตุผลและ dependency ทุกเส้น: audit-fr-baseline → verify-fr: ต้องได้รายงานที่ Executor ผลิตก่อน Evaluator ตรวจย้อนกับ baseline. ตรวจความครบและความถูกต้องทุกแถว ข้อความ/ตัวเลข/หน่วย/สัดส่วน รวมการคงคำถามและแยกสมมติฐาน ตรวจ hash ของ FR และรายงานเป้าหมาย. ส่ง PASS เฉพาะความสอดคล้องเอกสารเมื่อครบเกณฑ์, FAIL เมื่อพบความคลาดเคลื่อน, BLOCKED เมื่อขาดหลักฐานจำเป็น; ไม่ยก 108/108 upstream เป็นผลรันใหม่. คำถามธุรกิจที่บันทึกครบไม่ขัด PASS เอกสาร แต่ห้ามปิดคำถามโดย AI.

### verify-flow — Evaluator ตรวจ Flow/state/structure หลังกรองเทียบ FR ที่ตรวจแล้ว

kind: `verify`; status: `planned`
US refs: US-01, US-02, US-03, US-04, US-05, US-06, US-07, US-08, US-10, US-11, US-12, US-13, US-15, US-16, US-19, US-20, US-25, US-26
depends_on: audit-fr-baseline, verify-fr

Inputs:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/execution/fr-baseline-audit-v1.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/fr-v1-check.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/fr-nfr.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/flow.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/state-machine.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/structure.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/us-initial.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/provenance.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/input-audit.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/flow-check.json`

Outputs ที่วางแผน ยังไม่ได้สร้าง:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/flow-v1-check.md`

เหตุผลและ dependency ทุกเส้น: audit-fr-baseline → verify-flow: ใช้ matrix และตำแหน่งหลักฐาน FR ที่ผลิตจริง; verify-fr → verify-flow: รอ PASS เอกสารก่อนใช้ matrix เป็นฐาน. ช่องว่างตาม input-audit คือ flow-check เดิมเกิดก่อนกรอง: ตรวจ 30 merged flows, coverage 18 US, main/alternative/error, merge mapping ที่ปรากฏในสำเนา, guard/transition/status mapping และ module/entity/screen/permission เทียบ FR พร้อม hash ปัจจุบัน. แยก state รายการ/ออเดอร์/ชำระเงิน/โต๊ะจากสถานะ task; ไม่กู้ส่วนที่ปิด ไม่รับรอง initial/terminal หรือสิทธิ์ Unknown. ตรวจ MC-01–MC-03 และข้อเสนอให้คง unresolved; ระบุลิงก์ต้นทางที่ไม่อยู่ในสำเนาเป็นข้อจำกัด ไม่เปิดตาม. ผลใหม่ PASS/FAIL/BLOCKED จำกัดเอกสารหลังกรองเท่าที่มีหลักฐาน โดยไม่ลบ READINESS: BLOCKED ของระบบจริง.

### draft-test-outline — Executor สร้างโครงร่างทดสอบเอกสารและ offline mock

kind: `create`; status: `planned`
US refs: US-01, US-02, US-03, US-04, US-05, US-06, US-07, US-08, US-10, US-11, US-12, US-13, US-15, US-16, US-19, US-20, US-25, US-26
depends_on: audit-fr-baseline, verify-fr

Inputs:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/execution/fr-baseline-audit-v1.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/fr-v1-check.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/us-initial.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/fr-nfr.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-contract.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-mockup.html`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/input-audit.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-check.json`

Outputs ที่วางแผน ยังไม่ได้สร้าง:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/test-outline-v1.md`

เหตุผลและ dependency ทุกเส้น: audit-fr-baseline → draft-test-outline: ต้องใช้ matrix/คำถามที่สร้างจริง; verify-fr → draft-test-outline: ต้องรอผล PASS ของ matrix และ FR ก่อนร่าง expected outcomes. ร่างจาก FR/US และ fixture contract จึงยังไม่ใช้ Flow เป็นฐานตัดสินและไม่ต้องรอ verify-flow ในช่วงร่าง; verify-test-outline จะเป็น gate รวมภายหลัง. สร้าง coverage 18 US โดยแยกการตรวจเอกสาร, mock smoke/edge และเกณฑ์ระบบจริงที่ยังไม่รัน. ทุกกรณีระบุ source/AC ตรงตัว, precondition/fixture จำลอง, การกระทำ, expected outcome ที่ยืนยันหรือสมมติฐาน, หลักฐานที่จะเก็บ, คำถามที่กีดกันการสรุป และสถานะ NOT_RUN. รักษาตัวเลขและหน่วยทุกข้อ ไม่ลดสัดส่วนจริงเป็น smoke sample; US-07 คงสูตร/ช่วงเร่งด่วน/เกณฑ์เดิมในเอกสารแต่ยังไม่มีค่า ETA หรือผลความแม่นยำ; US-26 ระบุยังไม่มีตัวติดตั้ง/ผล offline ระบบจริง. ตรวจที่วางไว้รวม selector template/uniqueness แบบ scoped, role/reset, stock/cash/slip จำลอง, ราคา snapshot, session เก่า, direct route, รูป/ตัวเลือก/ข้ามวัน/วัตถุดิบซ้อนและขนาดจอ; ใช้เฉพาะบัญชีจำลอง. พฤติกรรม fixture ที่ต้นฉบับไม่ยืนยันติดป้ายสมมติฐาน ไม่เป็น AC ใหม่.

### verify-test-outline — Evaluator ตรวจโครงทดสอบและความสอดคล้องกับ Flow ก่อนตรวจ UI

kind: `verify`; status: `planned`
US refs: US-01, US-02, US-03, US-04, US-05, US-06, US-07, US-08, US-10, US-11, US-12, US-13, US-15, US-16, US-19, US-20, US-25, US-26
depends_on: draft-test-outline, verify-fr, verify-flow

Inputs:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/test-outline-v1.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/fr-v1-check.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/flow-v1-check.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/us-initial.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/fr-nfr.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/flow.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/state-machine.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/structure.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-contract.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-mockup.html`

Outputs ที่วางแผน ยังไม่ได้สร้าง:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/test-outline-v1-check.md`

เหตุผลและ dependency ทุกเส้น: draft-test-outline → verify-test-outline: ต้องมีโครงทดสอบฉบับที่จะตรวจ; verify-fr → verify-test-outline: ใช้ผลตรวจ FR ที่อ้าง hash เดียวกันเป็นเกณฑ์; verify-flow → verify-test-outline: รอ PASS เอกสารหลังกรองและรายการข้อค้างเพื่อ reconcile โครงทดสอบกับ flow/state/structure. ตรวจ coverage 18 US และเกณฑ์จริงทุกตัวเลข/หน่วย/สัดส่วนตรงต้นฉบับ ตรวจว่า mock และสมมติฐานไม่แทนระบบจริง, US-07/US-26 ไม่ถูกประกาศผ่าน, sample ของ smoke ไม่ถูกใช้รับรอง AC จริง. ผล PASS/FAIL/BLOCKED ต้องอ้าง hash outline และ input; ถ้ามีข้อผิดพลาดในร่างให้ส่งรายการแก้เพื่อแผนรุ่นถัดไป ไม่แก้ทับ outline ฉบับนี้.

### verify-ui — Evaluator รัน browser ตรวจ UI baseline สำเนานี้ใน offline mock

kind: `verify`; status: `planned`
US refs: US-01, US-02, US-03, US-04, US-05, US-06, US-07, US-08, US-10, US-11, US-12, US-13, US-15, US-16, US-19, US-20, US-25, US-26
depends_on: draft-test-outline, verify-test-outline, verify-fr, verify-flow

Inputs:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/test-outline-v1.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/test-outline-v1-check.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/fr-v1-check.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/flow-v1-check.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-mockup.html`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-contract.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-check.json`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/fr-nfr.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/input-audit.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/provenance.md`

Outputs ที่วางแผน ยังไม่ได้สร้าง:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/execution/ui-checks-v1.spec.js`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/execution/ui-v1-observations.json`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/ui-v1-check.md`

เหตุผลและ dependency ทุกเส้น: draft-test-outline → verify-ui: ใช้ชุดกรณีและหลักฐานที่ต้องเก็บจากไฟล์ร่างจริง; verify-test-outline → verify-ui: ต้องรอ PASS ของชุดกรณีก่อนรัน; verify-fr → verify-ui: ต้องรอ PASS และคง traceability กับ FR hash ที่ตรวจแล้ว; verify-flow → verify-ui: ต้องรอผลตรวจ Flow หลังกรองและข้อค้างเพื่อไม่ตีความ state/permission เกินต้นฉบับ. ช่องว่างคือผล upstream 19/19 ยังไม่ใช่ผล browser ของสำเนานี้. สร้างสคริปต์ตรวจที่ทำซ้ำได้และ observations โดยเปิด HTML baseline ผ่าน file://, แยก browser context/reset แต่ละกรณี, ปิด network, ใช้ mock seed/PIN สาธารณะเท่านั้น; เก็บ script, runtime evidence, browser/version/UTC, hash HTML/contract/outline และผลรายกรณีใน outputs ที่ระบุ. browser profile/cache/temp ที่จำเป็นต้องอยู่ session เท่านั้น และหากทำไม่ได้ให้ BLOCKED เฉพาะการรัน browser. ตรวจ DOM ที่สร้างจริงและ selector scoped ตาม contract รวม smoke เดิมและ edge ใน outline; ไม่อนุมานว่า selector template หายจาก literal search. สรุป PASS/FAIL/BLOCKED เฉพาะ mock ที่รันจริง แยก US-07 ยังไม่มี ETA และ US-26 ยังไม่พิสูจน์ระบบจริง รวมข้อค้างธุรกิจ; ไม่อ้าง SLA/LAN/load/security จริงหรือการโอนเงินจริง. หากเครื่องมือไม่พร้อมให้ระบุ NOT_RUN/BLOCKED ไม่แต่ง observations ผ่าน.

### evaluate-handoff — Evaluator ตรวจชุดหลักฐานก่อนส่งต่อเอกสารและ offline mock

kind: `verify`; status: `planned`
US refs: US-01, US-02, US-03, US-04, US-05, US-06, US-07, US-08, US-10, US-11, US-12, US-13, US-15, US-16, US-19, US-20, US-25, US-26
depends_on: verify-plan, audit-fr-baseline, verify-fr, verify-flow, draft-test-outline, verify-test-outline, verify-ui

Inputs:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/plan-v1.json`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/plan-v1.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/plan-v1-review.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/plan-v1-validation.json`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/execution/fr-baseline-audit-v1.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/fr-v1-check.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/flow-v1-check.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/test-outline-v1.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/test-outline-v1-check.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/execution/ui-checks-v1.spec.js`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/execution/ui-v1-observations.json`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/ui-v1-check.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/provenance.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/input-audit.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/fr-nfr.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/flow.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/state-machine.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/structure.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-mockup.html`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-contract.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/us-initial.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/fr-check.json`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/flow-check.json`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-check.json`

Outputs ที่วางแผน ยังไม่ได้สร้าง:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/handoff-v1.md`

เหตุผลและ dependency ทุกเส้น: verify-plan → evaluate-handoff: ตรวจว่ารันตามแผนที่ Evaluator อนุญาตและ hash ตรง; audit-fr-baseline → evaluate-handoff: ต้องมีรายงาน FR ที่ส่งต่อจริง; verify-fr → evaluate-handoff: ต้องมี PASS รับรองความสอดคล้องเอกสาร FR; verify-flow → evaluate-handoff: ต้องมี PASS เอกสาร Flow หลังกรอง; draft-test-outline → evaluate-handoff: ต้องมีโครงทดสอบจริง; verify-test-outline → evaluate-handoff: ต้องมี PASS ของโครงทดสอบ; verify-ui → evaluate-handoff: ต้องมี script/observations/ผล browser ของสำเนานี้และ PASS ในขอบเขต mock ก่อนปล่อยชุดงาน. แต่ละเส้นเป็นทั้ง artifact และ quality gate ตามหน้าที่ ไม่ใช้สถานะ planned แทนผลตรวจ. ตรวจ hash/traceability และทุกรายการ outputs เทียบรายงานจริง, แยกงานสร้างจริง/reuse/recheck, ข้อค้าง human-required และสิ่งที่ยังไม่ทดสอบ; สรุป PASS/FAIL/BLOCKED ของชุดเอกสาร/offline mock เท่านั้น. ถ้ามี upstream FAIL/BLOCKED ให้หยุดการส่งต่อและบันทึกผลตามจริงเมื่อประเมินได้ ไม่อนุมัติระบบจริง และไม่แก้สถานะ snapshot นี้.

## การตัดสินใจ

### d-scope — เป้าหมายและ trigger baseline

authority: `ai`

วางแผนแรกเพื่อผลิตรายงานตรวจเทียบ FR และโครงร่างทดสอบ พร้อมตรวจเอกสารและ offline mock จาก baseline-filtered-v2 ที่ INPUT_READY เท่านั้น. ใช้ 18 แถว US ที่เปิดแล้ว; รหัสอ้างภายใน US-20 ไม่เพิ่มขอบเขต และไม่กู้ข้อความที่ปิดใน US-12 หรือเอกสารอื่น. อ่าน plan-v0.example.json เพื่อรูปแบบเท่านั้น ไม่ใช้เป็นเวอร์ชันก่อน. ไม่เปิด reveal, README, baseline อื่น, diff, audit เก่า, logs หรือเว็บ.

หลักฐาน:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/input-audit.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/provenance.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/us-initial.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/input/plan-v0.example.json`

### d-schedule — Priority และลำดับที่เคารพ dependency

authority: `ai`

P0: verify-plan ต้อง PASS ก่อน Executor. P1: audit-fr-baseline → verify-fr. P2: หลัง verify-fr PASS งาน verify-flow และ draft-test-outline พร้อมทำได้อิสระ; หากมีผู้ทำคนเดียวให้ verify-flow ก่อนเพื่อลดความเสี่ยงการส่งต่อ แล้ว draft-test-outline. P3: verify-test-outline รอทั้ง draft-test-outline และผลตรวจ verify-fr/verify-flow. P4: verify-ui รอ outline และผลตรวจที่จำเป็นครบ. P5: evaluate-handoff รอทุก upstream และ PASS ที่จำเป็น. ลำดับปฏิบัติแบบคนเดียวคือ verify-plan → audit-fr-baseline → verify-fr → verify-flow → draft-test-outline → verify-test-outline → verify-ui → evaluate-handoff. นี่เป็นลำดับตาม gate ไม่ใช่ตำแหน่ง tasks ใน JSON; ไม่เรียก agent เพิ่มในรอบ Planner นี้.

หลักฐาน:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/input/plan.schema.json`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/input-audit.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/flow-check.json`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-check.json`

### d-gates — เงื่อนไขเดินงานและหลักฐาน

authority: `ai`

depends_on หมายถึงรอ artifact ที่สร้างจริงและผล PASS ในขอบเขตที่ระบุสำหรับทุกงาน verify ต้นทาง ไม่ใช่รอเพียง process จบ. ผล upstream เก่าเป็นหลักฐานประกอบเท่านั้น. ทุกผลตรวจใหม่ต้องระบุ target path/hash, เวลา UTC, ขอบเขต, verdict, สิ่งที่รันจริงและไม่ได้รัน. เอกสารที่บันทึกข้อค้างธุรกิจครบสามารถผ่านการตรวจเอกสารโดยไม่ยืนยันกฎนั้น. หากขาด input หรือพบ blocking limit ของงานให้ BLOCKED เฉพาะงาน/สาย downstream ที่เกี่ยวข้องและบันทึก path ที่ขาด; งานอิสระที่ผ่าน gate แล้วทำต่อได้. l-plan-gate และ l-check-gates เป็น blocker การเริ่ม/ส่งต่อที่ยังไม่ถูกปลดใน snapshot.

หลักฐาน:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/input-audit.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/input/plan.schema.json`

### d-reuse-no-revise — ใช้ baseline โดยตรงและไม่สร้างฉบับแก้โดยไม่มีหลักฐาน

authority: `ai`

ใช้ US/FR/Flow/state/structure/UI/contract ตาม hash ใน reuse. สถานะงานทุกงานเป็น planned; disposition reuse คือเลือกแหล่งข้อมูล ไม่ใช่งาน done/reused หรือผล PASS ใหม่. ยังไม่วาง revise-fr/revise-flow/revise-ui เพราะยังไม่มีข้อผิดพลาดที่พิสูจน์และมีคำตอบเพียงพอให้แก้: ช่องว่างปัจจุบันต้องสร้างรายงานและ verify ก่อน. US-07 ไม่มีข้อมูลให้คำนวณ ETA ส่วน US-26 ไม่มีตัวติดตั้ง ไม่เติมตัวเลขหรือระบบจริงเพื่อให้ดูครบ. หากผลใหม่พบจุดแก้ ให้เก็บหลักฐานแล้วจัดแผนรุ่นถัดไปด้วย ID เดิมสำหรับหน้าที่เดิม เช่น verify-fr, verify-flow, verify-ui; งานแก้จึงใช้ revise-flow/revise-ui เมื่อจำเป็น และใช้ session/fr-nfr-v1.md, session/flow-v1.md, session/ui-mockup-v1.html เฉพาะเมื่อไม่เคยมีไฟล์และแผนใหม่อนุญาต. paths เหล่านี้เป็นแนวทางการตั้งชื่อ ยังไม่ใช่ outputs ของ plan-v1.

หลักฐาน:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/input-audit.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/fr-check.json`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/flow-check.json`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-check.json`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-mockup.html`

### d-offline-boundary — ขอบเขตจำลองและการคง AC

authority: `ai`

AI เลือกวิธีตรวจ รูปแบบรายงาน ลำดับงาน และ fixture สำหรับทดสอบที่ติดป้ายจำลองได้; AI ยืนยันกฎร้านที่หายไม่ได้. โครงทดสอบต้องคัด US/AC ตรงตัวจากไฟล์อนุญาต รักษาตัวเลข หน่วย สัดส่วน จุดวัดและสูตรโดยไม่ใช้ค่าจำลองแทนผลจริง. พฤติกรรมตาม ui-contract เป็น fixture; ถ้าข้อใดยังไม่มี FR รองรับให้ติดป้ายสมมติฐาน/ยังไม่ยืนยัน. US-07 ตรวจได้เพียงข้อความข้อจำกัดปัจจุบัน ไม่ถือว่ามี ETA ตามสูตร; US-26 ตรวจได้เพียงเอกสารความต้องการ ยังไม่ทดสอบติดตั้งหรือถอดอินเทอร์เน็ตระบบจริง. หน้ารายงานเป็น placeholder ตรวจสิทธิ์ตาม US-25 เท่านั้น. แผนงาน AI แยกจาก state machine รายการ/ออเดอร์/ชำระเงิน/โต๊ะเสมอ.

หลักฐาน:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/fr-nfr.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-contract.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-mockup.html`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/state-machine.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/structure.md`

### d-snapshot — Snapshot และการส่ง Evaluator

authority: `ai`

สร้าง plan-v1.json/plan-v1.md พร้อมผลตรวจเชิงโครงสร้างของ Planner ที่ evaluations/plan-v1-validation.json. ส่งคู่แผนเป็น inputs ของ verify-plan; ยังไม่มีผล Evaluator และยังไม่เริ่ม Executor. ไม่แก้สถานะใน plan-v1 หลังสร้าง; ผู้ปฏิบัติบันทึกหลักฐาน execution และผู้ตรวจบันทึก evaluations ตาม outputs แล้วจึงรวมสถานะในแผนรุ่นถัดไป. ทุกไฟล์ใช้การสร้างใหม่เท่านั้น; ถ้าเป้าหมายมีอยู่ให้หยุดและรายงาน path ไม่ overwrite. ห้ามเขียนนอก session ตามข้อกำหนดรอบนี้.

หลักฐาน:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/input-audit.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/input/plan.schema.json`

### d-human-status — Q-05/Q-07/Q-11; MC-01 / DI-07 / A-05

authority: `human-required`

ยังไม่มีคำยืนยันจากมนุษย์: เสร็จแล้วกับพร้อมเสิร์ฟสัมพันธ์กันอย่างไร จุดจบ ETA และ transition/การกดซ้ำ/ย้อนกลับใดได้รับอนุญาต? คงชื่อเดิมแยกกันและไม่เพิ่ม transition รายการ. ผูกข้อค้าง l-q-status กับ affected_tasks ตาม limits; เป็น blocker การยืนยันกฎ/ระบบจริงตาม l-real-scope แต่ไม่ขัดงานตรวจเอกสารและ offline mock ที่คงป้ายยังไม่ยืนยัน. ให้เจ้าของข้อกำหนดตอบพร้อมหลักฐานก่อนนำไปแก้ baseline ในแผนรุ่นถัดไป.

หลักฐาน:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/fr-nfr.md#คำถามรอยืนยัน`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/flow.md:239`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/state-machine.md:104`

### d-human-eta — Q-07; หมายเหตุ ช.

authority: `human-required`

ยังไม่มีคำยืนยันจากมนุษย์: ขอหมายเหตุ ช. นิยามค่าเฉลี่ยต่อออเดอร์/ต่อเมนู วิธีเลือกเมนูที่นานที่สุด การปัดเศษ กรณีไม่มีประวัติ และการนับประชากร/ใบยังไม่พร้อมเสิร์ฟเมื่อจบวันทดสอบ โดยคงสูตรและเกณฑ์เดิม. ไม่สร้างข้อมูล 7 วันหรือค่า ETA ขึ้นแทน. ผูกข้อค้าง l-q-eta กับ affected_tasks ตาม limits; เป็น blocker การยืนยันกฎ/ระบบจริงตาม l-real-scope แต่ไม่ขัดงานตรวจเอกสารและ offline mock ที่คงป้ายยังไม่ยืนยัน. ให้เจ้าของข้อกำหนดตอบพร้อมหลักฐานก่อนนำไปแก้ baseline ในแผนรุ่นถัดไป.

หลักฐาน:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/fr-nfr.md:26`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/fr-nfr.md#คำถามรอยืนยัน`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-mockup.html:346`

### d-human-payment — Q-08; MC-02; หมายเหตุ ก.

authority: `human-required`

ยังไม่มีคำยืนยันจากมนุษย์: ขอหมายเหตุ ก. จุดเริ่มนับ 10 นาที วิธีส่ง/ตรวจสลิป ที่ตั้งค่าปิด PromptPay และเมื่อปิดแล้วการเลือกได้ 2 แบบทุกออเดอร์ต้องทำงานอย่างไร? fixture เดิมไม่ใช่คำตอบของธุรกิจ. ผูกข้อค้าง l-q-payment กับ affected_tasks ตาม limits; เป็น blocker การยืนยันกฎ/ระบบจริงตาม l-real-scope แต่ไม่ขัดงานตรวจเอกสารและ offline mock ที่คงป้ายยังไม่ยืนยัน. ให้เจ้าของข้อกำหนดตอบพร้อมหลักฐานก่อนนำไปแก้ baseline ในแผนรุ่นถัดไป.

หลักฐาน:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/fr-nfr.md:27`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/flow.md:240`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-contract.md`

### d-human-mapping — Q-12/Q-13/Q-20; MC-03 / DI-04 / A-03; หมายเหตุ ค.

authority: `human-required`

ยังไม่มีคำยืนยันจากมนุษย์: ขอหมายเหตุ ค. กติกาวัตถุดิบหมดซ้อน/กดซ้ำ/แก้แมประหว่างปิด และยืนยันรหัสอ้างใน US-20 ว่าตั้งใจเช่นเดิมหรือควรแก้รหัสใด? คงข้อความ US-20 ที่อ้าง US-14; การเชื่อม US-12/US-13 ยังเป็นข้อเสนอและไม่ขยาย US ที่ไม่เปิด. ผูกข้อค้าง l-q-mapping กับ affected_tasks ตาม limits; เป็น blocker การยืนยันกฎ/ระบบจริงตาม l-real-scope แต่ไม่ขัดงานตรวจเอกสารและ offline mock ที่คงป้ายยังไม่ยืนยัน. ให้เจ้าของข้อกำหนดตอบพร้อมหลักฐานก่อนนำไปแก้ baseline ในแผนรุ่นถัดไป.

หลักฐาน:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/us-initial.md:18`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/fr-nfr.md:35`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/flow.md:241`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-contract.md:115`

### d-human-operations — Q-02/Q-03/Q-04/Q-06/Q-10/Q-11/Q-15/Q-16

authority: `human-required`

ยังไม่มีคำยืนยันจากมนุษย์: ใครจัดการ QR/table_id ผิด; เวลาสั่งและช่วงรับยึดเหตุการณ์ใด; ตัวเลือกมีเงื่อนไขใด; คำสั่งชนหมด/ส่งซ้ำตัดสินอย่างไร; เลข monotonic มีขอบเขตข้ามวัน/รีสตาร์ตใด; เขตเวลาของเลขรับและนโยบาย log คืออะไร; เปิด/ปิดโต๊ะขณะค้างทำหรือค้างจ่ายและหน้าเดิมทำงานอย่างไร? ใช้รายละเอียดคำถามต้นทางแต่ละรหัส ไม่ตอบแทนและไม่รวมเลขออเดอร์กับเลขรับ. ผูกข้อค้าง l-q-operations กับ affected_tasks ตาม limits; เป็น blocker การยืนยันกฎ/ระบบจริงตาม l-real-scope แต่ไม่ขัดงานตรวจเอกสารและ offline mock ที่คงป้ายยังไม่ยืนยัน. ให้เจ้าของข้อกำหนดตอบพร้อมหลักฐานก่อนนำไปแก้ baseline ในแผนรุ่นถัดไป.

หลักฐาน:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/fr-nfr.md#คำถามรอยืนยัน`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/state-machine.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/structure.md`

### d-human-environment — Q-01/Q-19/Q-25/Q-26 และสิทธิ์ Unknown

authority: `human-required`

ยังไม่มีคำยืนยันจากมนุษย์: ขอสภาพชุดทดสอบมือถือ/เครือข่าย นิยาม MB/ราคา ผลลบเมนูที่ค้าง ขอบเขตบัญชี/ตัวนับล็อก/สิทธิ์ Unknown และสภาพ Ubuntu ก่อนติดตั้งตามคำถามต้นทาง. หน่วย 2 MB และเกณฑ์เดิมต้องคงไว้; ค่า byte/clock/permission ใน fixture เป็นสมมติฐาน. ไม่เพิ่ม SLA งบประมาณ การสำรอง/กู้คืน หรือสิทธิ์ที่ไม่มีคำยืนยัน. ผูกข้อค้าง l-q-environment กับ affected_tasks ตาม limits; เป็น blocker การยืนยันกฎ/ระบบจริงตาม l-real-scope แต่ไม่ขัดงานตรวจเอกสารและ offline mock ที่คงป้ายยังไม่ยืนยัน. ให้เจ้าของข้อกำหนดตอบพร้อมหลักฐานก่อนนำไปแก้ baseline ในแผนรุ่นถัดไป.

หลักฐาน:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/fr-nfr.md#คำถามรอยืนยัน`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/structure.md:84`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-contract.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/input-audit.md`

## ใช้ซ้ำ

### us-initial.md

artifact: `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/us-initial.md`
source_version: `baseline-filtered-v2; SHA-256 56a439f6e22f4a8d17f552b023c3c8fe61556f5bd31f1f1e9b70c1f9da6049d2`
disposition: `reuse`

ใช้ 18 แถวเป็นขอบเขตและข้อความต้นทางโดยตรง; input-audit ตรวจ 18 รหัสไม่ซ้ำและ hash แล้ว. คงเซลล์ที่ปิดใน US-12 และรหัสอ้างใน US-20 ไม่กู้ต้นฉบับหรือเพิ่ม scope.

หลักฐานตรวจเดิม/ที่มา:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/input-audit.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/provenance.md`

### fr-nfr.md

artifact: `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/fr-nfr.md`
source_version: `baseline-filtered-v2; SHA-256 da31640e540b825d4fec555627ea098f092daf4243d5d304fd4c32ae6db734cd`
disposition: `reuse`

ใช้ FR/NFR baseline โดยตรงเป็นฐานรายงาน ไม่มีการแก้ข้อความ. fr-check upstream รายงาน 108/108, failed 0 แต่ไม่มี target hash ภายใน; provenance ผูกสำเนาและ input-audit ตรวจ FR 18 แถว. ยังต้องสร้าง audit-fr-baseline และ verify-fr ใหม่ก่อน downstream; ไม่อ้างผลทดสอบจริง.

หลักฐานตรวจเดิม/ที่มา:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/fr-check.json`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/input-audit.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/provenance.md`

### flow.md

artifact: `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/flow.md`
source_version: `baseline-filtered-v2; SHA-256 d0a5fcd029f4f315a02fcd2c057a44907bdf7362fbce17b8664a75b82773595d`
disposition: `recheck`

ใช้ไฟล์เดิมเป็น input โดยตรงและรอ verify-flow หลังกรองก่อนใช้ข้อสรุปต่อ. flow-check upstream merge 30 flows, unresolved 3 เป็นก่อนกรอง; input-audit ตรวจ coverage/ข้อความ FR ไม่ครอบคลุมทุก mapping. คง MC-01–MC-03 และ READINESS: BLOCKED สำหรับระบบจริง.

หลักฐานตรวจเดิม/ที่มา:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/flow-check.json`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/input-audit.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/provenance.md`

### state-machine.md

artifact: `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/state-machine.md`
source_version: `baseline-filtered-v2; SHA-256 b4bc79de9e95f1526ca05326211a6025981b0420f3681b574e37189319f35adf`
disposition: `recheck`

ใช้ประกอบ verify-flow; ผล upstream เป็นก่อนกรองและ input-audit ตรวจเพียงความสอดคล้องบางส่วน. ตรวจ mapping/initial/terminal/event/invariant ที่มีในสำเนาและคงสมมติฐาน ไม่ตามลิงก์ที่ไม่มีไฟล์ ไม่ปะปน task state กับ business state.

หลักฐานตรวจเดิม/ที่มา:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/flow-check.json`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/input-audit.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/provenance.md`

### structure.md

artifact: `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/structure.md`
source_version: `baseline-filtered-v2; SHA-256 fc8facf9088ad320d8dc3a7157edc14b337c1cb7081c3b098bcf91ceab08c560`
disposition: `recheck`

ใช้ประกอบ verify-flow; input-audit ระบุ modules/data/screens/permissions/coverage มีครบ แต่ไม่ได้รับรองทุกข้อความหลังกรอง. ตรวจ key/cardinality/Unknown permission และเชื่อมกับ state โดยคงข้อเสนอ ไม่อนุมัติสิทธิ์ใหม่.

หลักฐานตรวจเดิม/ที่มา:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/flow-check.json`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/input-audit.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/provenance.md`

### ui-mockup.html

artifact: `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-mockup.html`
source_version: `baseline-filtered-v2; SHA-256 d2b7bfa0cff5700d3ca07f611c03cfa0304c54eafb51387f125e95edd11f7803`
disposition: `recheck`

ใช้ HTML เดิมผ่าน file:// สำหรับ offline mock และรอ verify-ui ของ hash นี้. ui-check upstream 19/19 เป็นผลบน path upstream; input-audit พบ embedded seed/CSP แต่ไม่ได้รัน browser สำเนานี้. ข้อความ ETA ยังประมาณไม่ได้ไม่ใช่สูตรทำงาน; HTML ไม่ใช่ตัวติดตั้งหรือระบบ offline จริง.

หลักฐานตรวจเดิม/ที่มา:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-check.json`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/input-audit.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/provenance.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-contract.md`

### ui-contract.md

artifact: `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-contract.md`
source_version: `baseline-filtered-v2; SHA-256 294b660d2e39b3745344f225400eee57c02c25b6efb108a3a7ecce7cdd060e68`
disposition: `reuse`

ใช้คู่กับ HTML hash ใน manifest เป็น fixture เท่านั้น. input-audit พบ selector 81 รายการ โดย 77 ชื่อพบตรงตัวและ 4 เป็น template; ยังต้อง verify DOM, uniqueness แบบ scoped และพฤติกรรมจริงใน verify-ui. ไม่เปลี่ยน fixture เป็นกฎร้าน.

หลักฐานตรวจเดิม/ที่มา:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/input-audit.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/provenance.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-mockup.html`

### fr-check.json

artifact: `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/fr-check.json`
source_version: `baseline-filtered-v2; SHA-256 1b0c604da9288ce926ba4c98eb258107b130f309f85b1ee96403e02ba0d0f98c`
disposition: `reuse`

ใช้เป็นหลักฐานประวัติ upstream 108/108 เท่านั้น ไม่ใช่ผล checker รอบนี้ ไม่ตาม output path นอกชุด.

หลักฐานตรวจเดิม/ที่มา:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/input-audit.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/provenance.md`

### flow-check.json

artifact: `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/flow-check.json`
source_version: `baseline-filtered-v2; SHA-256 3be4ccd3d045951e7c69e523e6ce2dfab052d45ece39d453741f310435d1c700`
disposition: `reuse`

ใช้เป็นหลักฐานประวัติ upstream ก่อนกรองเท่านั้น ไม่แทน PASS หลังกรองและไม่บวก unresolved ของทุก node เป็นจำนวนประเด็นไม่ซ้ำ.

หลักฐานตรวจเดิม/ที่มา:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/input-audit.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/provenance.md`

### ui-check.json

artifact: `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-check.json`
source_version: `baseline-filtered-v2; SHA-256 c09bf23c92abf0cd9c570f71ff890c1b572f8846c4d2ff8f5d2c3323be448af7`
disposition: `reuse`

ใช้เป็นรายการ smoke และหลักฐานประวัติ upstream 19/19 เท่านั้น ไม่รับรอง browser สำเนานี้หรือระบบจริง และไม่อ่าน HTML path นอกชุดที่รายงานอ้าง.

หลักฐานตรวจเดิม/ที่มา:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/input-audit.md`
- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/provenance.md`

### provenance.md

artifact: `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/provenance.md`
source_version: `baseline-filtered-v2; SHA-256 8059b1b47647d690ed7a73e6b4b9751e209edb3905868a4729269fb79330739a`
disposition: `reuse`

ใช้ manifest เฉพาะชุดนี้ คำนวณ SHA-256 ตรง 10/10 ในรอบ Planner; ไม่เปิด ../provenance.md หรือไฟล์ประวัตินอกชุด.

หลักฐานตรวจเดิม/ที่มา:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/provenance.md`

### input-audit.md

artifact: `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/input-audit.md`
source_version: `baseline-filtered-v2; SHA-256 d4100680ed1f31ea3351144f202f85343fb47a23acfa0305116731ab8bb1bbd8`
disposition: `reuse`

ใช้ผล INPUT_READY เฉพาะเอกสาร/offline mock และรายการข้อจำกัดของสำเนานี้ ไม่ลบล้าง BLOCKED ธุรกิจ. เวลาใน audit เป็นเวลาตรวจ input ไม่ใช่ created_at ของแผน.

หลักฐานตรวจเดิม/ที่มา:

- `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/input-audit.md`

## เหตุผล

ช่องว่างที่รองรับงานใหม่คือยังไม่มีรายงานตรวจเทียบ FR และโครงร่างทดสอบของ session นี้ รวมถึง Flow หลังกรองและ DOM/browser สำเนา UI ที่ยังไม่ได้ตรวจ. ผลเดิมรองรับการเลือก baseline แต่ไม่รองรับการอ้าง PASS ของรอบนี้. จึงสร้างรายงานใหม่และตรวจตาม dependency โดยยังไม่แก้ baseline ที่ไม่มีหลักฐานข้อผิดพลาดหรือคำยืนยันเพียงพอ.

หลักฐานหลัก: `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/input-audit.md`, `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/provenance.md`, `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/flow-check.json`, `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-check.json`.

## ข้อจำกัด

blocking=true ของ gate ขัดการเดินสายงานที่เกี่ยวข้องจนมีหลักฐาน; l-real-scope ขัดระบบจริงที่อยู่นอก tasks จึง affected_tasks ว่าง. คำถามธุรกิจใน l-q-* เป็น nonblocking สำหรับงานเอกสารและ mock ตามขอบเขตนี้ แต่ต้องส่งคำตอบให้เจ้าของข้อกำหนดยืนยันก่อนแก้กฎจริง. ไม่ถือว่าเวลาผ่านไปเป็นคำยืนยัน.

### l-plan-gate

blocking: `true`
affected_tasks: audit-fr-baseline, verify-fr, verify-flow, draft-test-outline, verify-test-outline, verify-ui, evaluate-handoff

BLOCKING ต่อการเริ่ม Executor และงาน downstream: ยังไม่มีผล Evaluator PASS ของคู่แผนที่ /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/plan-v1-review.md. ต้องรอ verify-plan; Planner schema validation ไม่ปลด gate นี้. Snapshot ทุก task ยัง planned.

### l-check-gates

blocking: `true`
affected_tasks: verify-flow, draft-test-outline, verify-test-outline, verify-ui, evaluate-handoff

BLOCKING ตาม dependency แต่ละเส้น: ผลตรวจ FR/Flow/test-outline/UI ของรอบนี้ยังไม่มี. ห้ามงาน downstream ใช้ผล PASS เดิมแทนผลใหม่; หาก FAIL, input ขาด หรือ hash ไม่ตรง ให้หยุดสายที่เกี่ยวข้องและรายงาน path ใน evaluations. เงื่อนไขนี้ไม่ขัดการทำรายงานต้นทางหลัง verify-plan PASS.

### l-real-scope

blocking: `true`
affected_tasks: [] — ระบบจริงอยู่นอก tasks แผนนี้

BLOCKED สำหรับการพัฒนาหรือรับรองระบบจริง ซึ่งไม่มี task ในแผนนี้ จึง affected_tasks ว่างโดยตั้งใจ: ต้องมีคำตอบเจ้าของข้อกำหนดใน d-human-* / l-q-* พร้อม baseline ที่ยืนยันแล้ว, ระบบ/อุปกรณ์/ข้อมูลและหลักฐานจริง, และขอบเขตงานใหม่ที่อนุญาต. READINESS: BLOCKED ใน /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/flow.md:5 และธุรกิจ BLOCKED ใน /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-mockup.html:22 ยังคงอยู่. คำตอบอย่างเดียวไม่เท่ากับระบบผ่าน; ไม่ขัดการตรวจเอกสารหรือร่าง test/offline mock ของ tasks ปัจจุบัน.

### l-browser

blocking: `true`
affected_tasks: verify-ui, evaluate-handoff

เงื่อนไข BLOCKING ของ verify-ui และการส่งต่อหากไม่มี browser/runtime ที่เปิด file:// แบบปิด network ได้ หรือเก็บ profile/cache/temp ใน session ไม่ได้: รอบ Planner ยังไม่ตรวจความพร้อม browser. ให้บันทึก BLOCKED/NOT_RUN ตามจริง ห้ามสร้างผลผ่าน. ไม่ขัด audit-fr-baseline หรือ draft-test-outline. หลักฐานช่องว่าง: /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/input-audit.md และ /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-check.json.

### l-provenance

blocking: `false`
affected_tasks: verify-plan, audit-fr-baseline, verify-fr, verify-flow, draft-test-outline, verify-test-outline, verify-ui, evaluate-handoff

ข้อจำกัด nonblocking ของสายที่มาภายนอกชุด: fr-check ไม่มี hash target ภายใน, flow-check ก่อนกรอง, ui-check อ้าง HTML upstream; ใช้ hash ที่ตรวจตรง 10/10 จาก /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/provenance.md และ mapping ใน /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/input-audit.md. ไม่มี input-source/node JSON/review-record ในสำเนา ไม่เปิดลิงก์นอกชุดหรือกู้ข้อความที่ปิด. ผลตรวจใหม่ต้องระบุส่วนที่พิสูจน์ได้และไม่ได้; ไม่รับรอง chain นอกชุด.

### l-no-runtime-evidence

blocking: `false`
affected_tasks: draft-test-outline, verify-test-outline, verify-ui, evaluate-handoff

รอบ Planner ตรวจไฟล์และ schema เท่านั้น; ยังไม่รัน checker FR/Flow ใหม่, browser ของ HTML สำเนานี้, LAN/Wi-Fi หลายอุปกรณ์, load, security จริง, ค่า ETA/สัดส่วนตัวอย่างจริง, ติดตั้ง Ubuntu/ถอดอินเทอร์เน็ตหรือการชำระเงินจริง. US-07 มีข้อความยังประมาณไม่ได้ที่ /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-mockup.html:346 และ US-26 ยังไม่มีตัวติดตั้งตาม /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/input-audit.md. ข้อจำกัดเหล่านี้ต้องคงในโครงทดสอบและ handoff ไม่ถูกเปลี่ยนเป็นผลผ่าน.

### l-q-status

blocking: `false`
affected_tasks: verify-flow, draft-test-outline, verify-test-outline, verify-ui, evaluate-handoff

Q-05/Q-07/Q-11; MC-01 / DI-07 / A-05: เสร็จแล้วกับพร้อมเสิร์ฟสัมพันธ์กันอย่างไร จุดจบ ETA และ transition/การกดซ้ำ/ย้อนกลับใดได้รับอนุญาต? คงชื่อเดิมแยกกันและไม่เพิ่ม transition รายการ. ยังไม่ตอบ; nonblocking สำหรับ affected_tasks ซึ่งทำเพียงเอกสาร/offline mock และต้องติดป้ายสมมติฐาน/ยังไม่ยืนยัน. การรับรองกฎจริงถูก block ตาม l-real-scope. หลักฐาน: /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/fr-nfr.md#คำถามรอยืนยัน; /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/flow.md:239; /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/state-machine.md:104

### l-q-eta

blocking: `false`
affected_tasks: draft-test-outline, verify-test-outline, verify-ui, evaluate-handoff

Q-07; หมายเหตุ ช.: ขอหมายเหตุ ช. นิยามค่าเฉลี่ยต่อออเดอร์/ต่อเมนู วิธีเลือกเมนูที่นานที่สุด การปัดเศษ กรณีไม่มีประวัติ และการนับประชากร/ใบยังไม่พร้อมเสิร์ฟเมื่อจบวันทดสอบ โดยคงสูตรและเกณฑ์เดิม. ไม่สร้างข้อมูล 7 วันหรือค่า ETA ขึ้นแทน. ยังไม่ตอบ; nonblocking สำหรับ affected_tasks ซึ่งทำเพียงเอกสาร/offline mock และต้องติดป้ายสมมติฐาน/ยังไม่ยืนยัน. การรับรองกฎจริงถูก block ตาม l-real-scope. หลักฐาน: /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/fr-nfr.md:26; /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/fr-nfr.md#คำถามรอยืนยัน; /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-mockup.html:346

### l-q-payment

blocking: `false`
affected_tasks: verify-flow, draft-test-outline, verify-test-outline, verify-ui, evaluate-handoff

Q-08; MC-02; หมายเหตุ ก.: ขอหมายเหตุ ก. จุดเริ่มนับ 10 นาที วิธีส่ง/ตรวจสลิป ที่ตั้งค่าปิด PromptPay และเมื่อปิดแล้วการเลือกได้ 2 แบบทุกออเดอร์ต้องทำงานอย่างไร? fixture เดิมไม่ใช่คำตอบของธุรกิจ. ยังไม่ตอบ; nonblocking สำหรับ affected_tasks ซึ่งทำเพียงเอกสาร/offline mock และต้องติดป้ายสมมติฐาน/ยังไม่ยืนยัน. การรับรองกฎจริงถูก block ตาม l-real-scope. หลักฐาน: /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/fr-nfr.md:27; /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/flow.md:240; /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-contract.md

### l-q-mapping

blocking: `false`
affected_tasks: audit-fr-baseline, verify-fr, verify-flow, draft-test-outline, verify-test-outline, verify-ui, evaluate-handoff

Q-12/Q-13/Q-20; MC-03 / DI-04 / A-03; หมายเหตุ ค.: ขอหมายเหตุ ค. กติกาวัตถุดิบหมดซ้อน/กดซ้ำ/แก้แมประหว่างปิด และยืนยันรหัสอ้างใน US-20 ว่าตั้งใจเช่นเดิมหรือควรแก้รหัสใด? คงข้อความ US-20 ที่อ้าง US-14; การเชื่อม US-12/US-13 ยังเป็นข้อเสนอและไม่ขยาย US ที่ไม่เปิด. ยังไม่ตอบ; nonblocking สำหรับ affected_tasks ซึ่งทำเพียงเอกสาร/offline mock และต้องติดป้ายสมมติฐาน/ยังไม่ยืนยัน. การรับรองกฎจริงถูก block ตาม l-real-scope. หลักฐาน: /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/us-initial.md:18; /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/fr-nfr.md:35; /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/flow.md:241; /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-contract.md:115

### l-q-operations

blocking: `false`
affected_tasks: audit-fr-baseline, verify-fr, verify-flow, draft-test-outline, verify-test-outline, verify-ui, evaluate-handoff

Q-02/Q-03/Q-04/Q-06/Q-10/Q-11/Q-15/Q-16: ใครจัดการ QR/table_id ผิด; เวลาสั่งและช่วงรับยึดเหตุการณ์ใด; ตัวเลือกมีเงื่อนไขใด; คำสั่งชนหมด/ส่งซ้ำตัดสินอย่างไร; เลข monotonic มีขอบเขตข้ามวัน/รีสตาร์ตใด; เขตเวลาของเลขรับและนโยบาย log คืออะไร; เปิด/ปิดโต๊ะขณะค้างทำหรือค้างจ่ายและหน้าเดิมทำงานอย่างไร? ใช้รายละเอียดคำถามต้นทางแต่ละรหัส ไม่ตอบแทนและไม่รวมเลขออเดอร์กับเลขรับ. ยังไม่ตอบ; nonblocking สำหรับ affected_tasks ซึ่งทำเพียงเอกสาร/offline mock และต้องติดป้ายสมมติฐาน/ยังไม่ยืนยัน. การรับรองกฎจริงถูก block ตาม l-real-scope. หลักฐาน: /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/fr-nfr.md#คำถามรอยืนยัน; /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/state-machine.md; /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/structure.md

### l-q-environment

blocking: `false`
affected_tasks: audit-fr-baseline, verify-fr, verify-flow, draft-test-outline, verify-test-outline, verify-ui, evaluate-handoff

Q-01/Q-19/Q-25/Q-26 และสิทธิ์ Unknown: ขอสภาพชุดทดสอบมือถือ/เครือข่าย นิยาม MB/ราคา ผลลบเมนูที่ค้าง ขอบเขตบัญชี/ตัวนับล็อก/สิทธิ์ Unknown และสภาพ Ubuntu ก่อนติดตั้งตามคำถามต้นทาง. หน่วย 2 MB และเกณฑ์เดิมต้องคงไว้; ค่า byte/clock/permission ใน fixture เป็นสมมติฐาน. ไม่เพิ่ม SLA งบประมาณ การสำรอง/กู้คืน หรือสิทธิ์ที่ไม่มีคำยืนยัน. ยังไม่ตอบ; nonblocking สำหรับ affected_tasks ซึ่งทำเพียงเอกสาร/offline mock และต้องติดป้ายสมมติฐาน/ยังไม่ยืนยัน. การรับรองกฎจริงถูก block ตาม l-real-scope. หลักฐาน: /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/fr-nfr.md#คำถามรอยืนยัน; /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/structure.md:84; /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-contract.md; /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/input-audit.md

## ส่ง Evaluator ก่อน Executor

คู่ไฟล์ส่งตรวจ: `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/plan-v1.json` และ `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/plan-v1.md`.
ผลตรวจเชิงโครงสร้างของ Planner: `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/plan-v1-validation.json` — ต้องอ่านผลจริง ไม่ถือแทนการประเมินเนื้อหาโดย Evaluator.
งานถัดไปคือ verify-plan; ผล Evaluator ที่คาดว่าจะสร้างคือ `/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/plan-v1-review.md` ซึ่งยังไม่มีใน snapshot นี้. ยังไม่เรียก Evaluator เพิ่มและยังไม่เริ่ม Executor.

ไฟล์ที่สร้างในขั้น Planner มีเพียง plan-v1.json, plan-v1.md และ evaluations/plan-v1-validation.json; outputs ใน tasks เป็นงานอนาคตทั้งหมด. ห้ามอ้างว่าได้ผลิตหรือทดสอบตาม task แล้ว.

สิ่งที่ยังไม่ทดสอบ: checker FR/Flow ใหม่, browser/DOM/การคลิกของสำเนานี้, LAN/Wi-Fi หลายอุปกรณ์, load, security จริง, สูตร ETA/ความแม่นยำ/สัดส่วนตัวอย่างจริง, ติดตั้ง Ubuntu/ถอดอินเทอร์เน็ต และการชำระเงินจริง. คำถามธุรกิจทั้งหมดใน limits ยังรอยืนยัน.
