# แผน Dynamic Workflow — round 0 / plan-v4

PHASE=plan; ROUND=0; สถานะ **PLAN_READY_WAITING_EXTERNAL_EXECUTE** เฉพาะเอกสารแผน ไม่ใช่ผลผ่านของชิ้นงานหรือ UI

ทุก path หลักฐานในเอกสารนี้สัมพัทธ์จาก `AI_Workflow_Engineering_for_SA/` และ resolve `../../../` จาก cwd ขั้นนี้ ชื่อไฟล์สั้นและ `round-0/` ในคำอธิบายหมายถึงภายในขั้นนี้

## แผนเดิม → ข้อมูลใหม่ → แผนรอบนี้

แผนเดิม `005_LAB_Dynamic_Workflow_Replanning/reference/step-07-plan-v3/plan-v3.json` มี 13 tasks ใช้สาย FR → ตรวจ → สัญญาข้อมูล → ตรวจ → Flow → ตรวจ → outline → ตรวจ → UI → ตรวจ → handoff และบริบทขยาย 26 US สถานะเดิมมีงาน audit done และงาน planned/needs_recheck ทั้งหมดเป็นประวัติของแผน ไม่ใช่ผลรอบนี้

ข้อมูลใหม่เป็นโจทย์สมมติ US-21 เปลี่ยนเฉพาะค่าเพดานที่ใช้ทดสอบ N=5 → N=3 คงหน้าต่าง 15 นาทีเริ่ม 00/15/30/45 และทดสอบ 3 จาก 3 รอบ เมื่อจำนวนออเดอร์ที่ยืนยันในหน้าต่างถึง N ลูกค้าใหม่เห็น “ครัวเต็ม รอประมาณ X นาที” ก่อนยืนยัน โดยไม่เพิ่มกฎปฏิเสธออเดอร์

ใช้ snapshot เป็นฐานชิ้นงาน 21 US/21 FR/17 NFR; ไม่ขยายเป็น 26 US การเปลี่ยน state ในตารางนี้เป็นสถานะงาน AI เท่านั้น คงรหัส US/FR/NFR/MRG/MOD/SCR/C-V2/selector ของระบบเดิม ผู้รับผิดชอบเป็นบทบาทใน phase ไม่มีการมอบหมายให้ผู้ช่วยหรือ CLI เพิ่ม

เพิ่มงานออกแบบกรณี threshold/boundary และบันทึกต้นทุน แยก self-check, ผลสคริปต์ และ evaluate ยกเลิกการผลิต data-contract/state-machine/structure/ui-contract/outline แยกไฟล์เฉพาะการทดลองนี้ โดยรวมส่วนตรวจที่ยังจำเป็นไว้ใน Flow/scenarios/execution ไม่มีการยกเลิก AC หรือแก้ baseline ต้นทาง

ลำดับใหม่: CHG-001 → CHG-002 → CHG-003 → CHG-004 → CHG-005 → CHG-006 → CHG-007 → CHG-008 → CHG-009 (ผู้ทดลอง) → CHG-010 (เรียก evaluate ภายนอก) ทุกงานหลัง CHG-001 ยังไม่ดำเนินการ

## Tasks และ dependency

ผลย่อยที่ระบุ anchor ใน execution.md เป็นบันทึกภายในไฟล์เดียว ซึ่ง CHG-008 รวบรวมใน execute การตรวจระหว่าง producer เป็น self-check ไม่ใช่การเรียก phase evaluate แทรก

| Task | งาน | Phase | Dependency | Owner | State |
|---|---|---|---|---|---|
| CHG-001 | ตรวจ baseline วิเคราะห์ผลกระทบ และจัดทำแผนรอบ 0 | plan | — | Planner | done |
| CHG-002 | ปรับ FR-21 และข้อความเกณฑ์ US-21 เฉพาะ N ทดสอบ | execute | CHG-001 | Executor | planned |
| CHG-003 | ตรวจ diff FR/NFR และตรึงเกณฑ์ก่อนส่ง Flow | execute | CHG-002 | Executor | planned |
| CHG-004 | ปรับ Flow และ fixture threshold ที่ MRG-34/35 | execute | CHG-003 | Executor | planned |
| CHG-005 | ตรวจ traceability และสัญญาข้อมูลที่ใช้ซ้ำ | execute | CHG-004 | Executor | planned |
| CHG-006 | จัดทำ scenario v3 และรายการ regression จาก snapshot | execute | CHG-005 | Executor | planned |
| CHG-007 | ปรับ UI seed/ข้อความ N และคงพฤติกรรมเดิม | execute | CHG-006 | Executor | planned |
| CHG-008 | ตรวจความสอดคล้องและบันทึก execution ตาม dependency | execute | CHG-002, CHG-003, CHG-004, CHG-005, CHG-006, CHG-007 | Executor | planned |
| CHG-009 | รันสคริปต์ตรวจภายนอกเพื่อสร้างหลักฐานรอบนี้ | external-test | CHG-008 | ผู้ทดลอง | waiting_external |
| CHG-010 | ประเมินข้อเปลี่ยนเดียวและ regression | evaluate | CHG-008, CHG-009 | Evaluator | waiting_external |

### CHG-001 — inputs / outputs / stop rule

Inputs:

- `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/manifest.md`
- `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/fr-nfr-v2.md`
- `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/flow-v2.md`
- `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/ui-mockup-v2.html`
- `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/ui-scenarios.json`
- `007_LAB_Evaluation_Compare_Workflows/reference/change-conditions.md`
- `005_LAB_Dynamic_Workflow_Replanning/reference/step-07-plan-v3/plan-v3.json`

Outputs:

- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/plan-round-0.md`
- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/plan-v4.json`
- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/impact-analysis-change.md`

Stop rule: สร้างเอกสารแผนสามไฟล์ ตรวจ JSON/dependency/path แล้วจบการเรียก; ไม่ผลิต outputs ของ execute

### CHG-002 — inputs / outputs / stop rule

Inputs:

- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/plan-round-0.md`
- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/plan-v4.json`
- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/impact-analysis-change.md`
- `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/fr-nfr-v2.md`

Outputs:

- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/fr-nfr-v3.md`

Stop rule: แก้เฉพาะ N=5 → N=3 และข้อความ provenance ที่จำเป็น; หาก AC อื่นเปลี่ยนต้องแก้ก่อนส่งต่อ

### CHG-003 — inputs / outputs / stop rule

Inputs:

- `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/fr-nfr-v2.md`
- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/fr-nfr-v3.md`

Outputs:

- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/execution.md#CHG-003`

Stop rule: ตรวจ 21 US/21 FR/17 NFR และ AC อื่นคงเดิม; ไม่ปล่อย downstream หาก diff เกินข้อเปลี่ยน

### CHG-004 — inputs / outputs / stop rule

Inputs:

- `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/flow-v2.md`
- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/fr-nfr-v3.md`

Outputs:

- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/flow-v3.md`

Stop rule: คง MRG/C-V2/MOD/SCR เดิม; เปลี่ยนตัวอย่างก่อนถึง 3/ถึง 3 โดยไม่เพิ่ม transition หรือกฎปฏิเสธ

### CHG-005 — inputs / outputs / stop rule

Inputs:

- `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/flow-v2.md`
- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/flow-v3.md`
- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/fr-nfr-v3.md`
- `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/ui-mockup-v2.html`

Outputs:

- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/execution.md#CHG-005`

Stop rule: ตรวจ confirmed_at/count หน้าต่าง 15 นาที คำเตือนก่อนยืนยัน และการคงกฎเดิม; ขาดหลักฐานให้ระบุ gap ไม่เดากฎ

### CHG-006 — inputs / outputs / stop rule

Inputs:

- `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/ui-scenarios.json`
- `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/ui-mockup-v2.html`
- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/fr-nfr-v3.md`
- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/flow-v3.md`

Outputs:

- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/ui-scenarios-v3.json`

Stop rule: ตรวจ JSON และ mapping ก่อน UI; แยก scenario ที่ออกแบบใหม่จาก path อ้างอิงเดิมซึ่งยังไม่ได้อ่าน; ห้ามอ้างว่าชุดเดิมผ่าน

### CHG-007 — inputs / outputs / stop rule

Inputs:

- `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/ui-mockup-v2.html`
- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/fr-nfr-v3.md`
- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/flow-v3.md`
- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/ui-scenarios-v3.json`

Outputs:

- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/ui-mockup-v3.html`

Stop rule: ใช้ N=3 ทั้ง reset/ค่าหน้าจอ/fixture; ไม่แก้เลข 5 ทั่วไฟล์; ตรวจ selector เดิมและไม่ปิดยืนยันเพราะเต็ม

### CHG-008 — inputs / outputs / stop rule

Inputs:

- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/plan-round-0.md`
- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/plan-v4.json`
- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/impact-analysis-change.md`
- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/fr-nfr-v3.md`
- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/flow-v3.md`
- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/ui-scenarios-v3.json`
- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/ui-mockup-v3.html`

Outputs:

- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/execution.md`

Stop rule: ระบุ diff/hash ผลตรวจที่ทำจริงและ gaps; จบ execute แล้วรอผู้ทดลองรันสคริปต์และเรียก evaluate; ไม่สรุป COMPLETE เอง

### CHG-009 — inputs / outputs / stop rule

Inputs:

- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/execution.md`
- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/fr-nfr-v3.md`
- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/flow-v3.md`
- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/ui-mockup-v3.html`
- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/ui-scenarios-v3.json`

Outputs:

- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/tests.json`

Stop rule: ต้องมีผลจริงผูกกับไฟล์รอบนี้; ถ้ารันไม่ได้ให้บันทึก missing/error ไม่สร้าง PASS; ไม่ใช่การเรียก AI อัตโนมัติ

### CHG-010 — inputs / outputs / stop rule

Inputs:

- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/plan-round-0.md`
- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/plan-v4.json`
- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/impact-analysis-change.md`
- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/execution.md`
- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/tests.json`
- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/fr-nfr-v3.md`
- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/flow-v3.md`
- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/ui-mockup-v3.html`
- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/ui-scenarios-v3.json`

Outputs:

- `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/evaluation-round-0.md`

Stop rule: COMPLETE เมื่อหลักฐานครบ; pre-run รอบ 0 หากยังมี gap ให้ STOP_WITH_GAPS และหยุด ไม่มีการเรียกรอบแก้เอง

## Diff จากแผนเดิม

ใช้ JSON Pointer อ้าง task เดิมเพื่อคงสายที่มา โดยใช้รหัสงานรอบนี้ CHG- เท่านั้น รายละเอียด source state และ mapping อยู่ใน plan-v4.json

| จุดใน plan-v3 | การปรับ | งานรอบนี้ | เหตุผล |
|---|---|---|---|
| `#/tasks/0` | replace | CHG-001 | ตรวจ provenance ของ snapshot ปัจจุบันแทนการนำสถานะ audit done เดิมมาใช้ |
| `#/tasks/1` | merge | CHG-001 | รวมตรวจโครงสร้างแผนใน plan; gate ต่อไปคือผู้ทดลองเรียก execute ตาม protocol นี้ |
| `#/tasks/2` | revise | CHG-002 | ลดขอบเขตผลิตเหลือข้อเปลี่ยน N ทดสอบ US-21; ไม่เปิดข้อมูลเพิ่ม |
| `#/tasks/3` | split | CHG-003, CHG-010 | แยก self-check ก่อนส่งต่อใน execute กับการตัดสินโดย evaluate ภายนอก |
| `#/tasks/4` | merge | CHG-005 | ยกเลิกการผลิต data-contract แยกไฟล์ในทดลองนี้; ใช้สัญญาข้อมูลที่มีใน Flow/UI |
| `#/tasks/5` | merge | CHG-005, CHG-010 | คงการตรวจข้อมูลนับใน Flow และ evaluate โดยไม่สร้าง gate ของไฟล์นอก outputs |
| `#/tasks/6` | revise | CHG-004 | ผลิต flow-v3 เท่านั้น; ไม่ผลิต state-machine/structure แยกหรือเปลี่ยนสถานะออเดอร์ |
| `#/tasks/7` | split | CHG-005, CHG-010 | ตรวจ traceability ก่อน scenarios และตรวจอิสระตอน evaluate |
| `#/tasks/8` | replace | CHG-006 | แทน outline ที่ขยาย 26 US ด้วย scenarios ของ snapshot 21 US พร้อมข้อเปลี่ยน |
| `#/tasks/9` | merge | CHG-006, CHG-010 | ตรวจรูปแบบและ coverage ใน execute แล้วประเมินผลใน evaluate |
| `#/tasks/10` | revise | CHG-007 | คง UI เดิม เปลี่ยน seed/ข้อความและ fixture N; ไม่ผลิต contract แยก |
| `#/tasks/11` | split | CHG-008, CHG-009, CHG-010 | แยกบันทึก self-check, ผลสคริปต์ของผู้ทดลอง และคำตัดสิน evaluate |
| `#/tasks/12` | replace | CHG-010 | เปลี่ยน gate ส่งต่อเดิมเป็น COMPLETE/REPLAN/STOP_WITH_GAPS ตามเพดานทดลอง |

## เกณฑ์ตรวจที่จะส่งต่อ execute / evaluate

ยังไม่มีการทดสอบใน phase นี้ เกณฑ์ต่อไปนี้เป็นแผนตรวจ ไม่ใช่ผล

- **CHG-AC-01 — FR/Flow ตรงข้อเปลี่ยน**: US-21/FR-21 ใช้ N=3 ในเกณฑ์ทดสอบและ fixture; คง 15 นาที, 00/15/30/45, 3 จาก 3 และข้อความก่อนยืนยัน หลักฐานที่ต้องมี: diff baseline→v3 พร้อม locator ทุกจุดที่แก้

- **CHG-AC-02 — threshold และจำนวนที่นับ**: ในช่วงเร่งด่วน N=3: มี 2 ออเดอร์ยืนยันแล้วไม่เตือน; มี 3 แล้วลูกค้าใหม่เห็นคำเตือนก่อนกดยืนยัน; มากกว่า 3 ยังเตือน; ตะกร้า/จำนวนจาน/เปิดหน้าไม่นับเป็นออเดอร์ หลักฐานที่ต้องมี: runtime observations แยก count=2,3,4 และก่อน/หลังยืนยัน

- **CHG-AC-03 — ยังยืนยันได้เมื่อเต็ม**: ที่ count=3 มีตะกร้าถูกต้อง เห็นข้อความก่อนยืนยันและ btn-submit-order ใช้งานได้; กดยืนยันแล้วเกิดออเดอร์ใหม่ count=4 โดยไม่เพิ่ม capacity rejection; กฎปฏิเสธเมนูหมด/session ปิด/ตะกร้าไม่ถูกต้องเดิมยังอยู่ หลักฐานที่ต้องมี: ลำดับเวลา/DOM ก่อนกด และออเดอร์/จำนวนหลังคลิก ไม่ใช้การพบ string ใน source แทนผล runtime

- **CHG-AC-04 — หน้าต่างคงที่และรอยต่อ**: ทดสอบก่อน/ตรงรอยต่อ 12:00,12:15,12:30,12:45 และ 13:00 ใน clock จำลอง; ออเดอร์ตรงขอบอยู่หน้าต่างใหม่ [start,end); ไม่ใช้ rolling 15 นาที ไม่ย้าย timezone เดิมของ UI หลักฐานที่ต้องมี: timestamp ของ fixture, window start/end และ count ก่อน/หลัง; ขอบและ timezone เป็นสมมติฐาน mock เดิม

- **CHG-AC-05 — ทำซ้ำครบสามรอบ**: รันชุด US-21 ที่ N=3 ด้วย initial state อิสระ 3 รอบ ผ่านครบ 3/3; แต่ละรอบครอบคลุม threshold คำเตือนก่อนยืนยัน ยืนยันต่อ และรอยต่อ ไม่ใช้สามออเดอร์แทนสามรอบ หลักฐานที่ต้องมี: tests.json แจกแจง repetition 1,2,3 พร้อมผลรายกรณีและ actual/expected

- **CHG-AC-06 — seed/reset/configuration และ X**: capacitySeed.limit และข้อความค่าเริ่มต้นเป็น 3; reset คืน 3; สลับบทบาทไม่ล้าง count; ช่อง N ยังตั้งค่าได้; X=10 พร้อมป้ายจำลองเดิม ไม่แทนสูตร ETA US-07 หลักฐานที่ต้องมี: source diff และ runtime ของ reset/ตั้งค่า/สลับบทบาท/ข้อความ

- **CHG-AC-07 — รักษา AC และรหัสเดิมทั้งหมดใน snapshot**: 21 US,21 FR,17 NFR คง ID และเกณฑ์เดิมนอกจากค่า N ทดสอบ US-21; คง MRG/MOD/SCR/C-V2 และ data-testid/data-action เดิม; ไม่ขยายเป็น 26 US ตามบริบทเก่าของแผน หลักฐานที่ต้องมี: inventory และ diff แบบ allowlist ระบุ metadata/provenance ที่เปลี่ยนแยกจาก AC; จำนวนเท่ากันอย่างเดียวไม่พอ

- **CHG-AC-08 — regression ของ offline mock**: ตรวจเส้นทางเดิมที่ snapshot รองรับ: QR/โต๊ะ, กลับบ้านและช่วงรับ, options/ราคา, ส่งคิว/สถานะถึงลูกค้าและหน้าร้าน, วัตถุดิบหมด/กลับมามี, คืน/เปลี่ยนรายการและยอด, เงินสด/PromptPay/fallback, รอบโต๊ะ, จัดการเมนู/แมป, สิทธิ์/PIN; คงข้อจำกัด Ubuntu/LAN/security/load/availability/ETA จริง หลักฐานที่ต้องมี: ตาราง US→กรณี→ผลจริงหรือ NOT_TESTED พร้อมเหตุผล; source preservation ไม่เท่ากับ runtime PASS


การออกแบบ ui-scenarios-v3.json ให้ระบุ schema/version, target ของ round-0, source_refs ที่คง key/value เดิม, scenarios ที่มี id/US/FR/Flow refs/preconditions/steps/expected/repetitions และ regression coverage แยกจาก legacy ที่ไม่ได้อ่าน หาก runner ต้องการ schema เฉพาะให้บันทึก adapter/ข้อจำกัดใน execution และอย่าอ้างว่าสาม path เดิมคือชุด runtime ที่ครบแล้ว รหัสกรณีเพิ่มใช้ CHG- ส่วนรหัสเดิมที่ปรากฏใน input ต้องคงไว้

ผล tests.json ต้องแยกตรวจเอกสารกับ runtime ระบุ artifact target/hash, วิธีหรือสคริปต์ที่รัน, ผลรายกรณี, actual/expected, repetition 1–3 และข้อผิดพลาด/NOT_TESTED พร้อม path หลักฐานที่มีจริง ถ้ารูปแบบสคริปต์จริงต่างออกไป evaluator ต้องทำ mapping จากข้อมูลจริง ไม่แต่ง field หรือ PASS การอ่าน source/syntax อย่างเดียวไม่พิสูจน์ 3/3 runtime

## Stop rule และการเรียก phase

- **phase_end**: การเรียกนี้ PHASE=plan ROUND=0 เท่านั้น; จบเมื่อเขียนและตรวจสามไฟล์แผน หยุดรอ execute จากผู้ทดลอง
- **complete**: evaluate เท่านั้น: outputs ครบตรงรุ่น/hash, ข้อเปลี่ยนเดียวถูกต้อง, เกณฑ์ CHG-AC-01–08 มีหลักฐานตามขอบเขตเอกสาร/offline; การทดสอบ N=3 ผ่าน 3/3; ไม่มี regression หรือช่องว่างในขอบเขตที่อ้างว่าผ่าน
- **replan_general**: ใช้เฉพาะการทดลองที่อนุญาตรอบแก้: defect แก้ได้ มีงบและรอบเหลือ และมีแนวทางใหม่ที่คืบหน้า; รอบ 1/2 อ่าน evaluation รอบก่อนเป็น feedback และบันทึก diff task/dependency/evidence/expected result
- **pre_run_override**: change-conditions.md จำกัดรันล่วงหน้าที่ round 0; ถ้าเกณฑ์ยังไม่ครบให้ STOP_WITH_GAPS แม้ defect แก้ได้; ไม่ใช้ REPLAN เพื่อเปิด round 1/2 ในรันนี้
- **max_repair_rounds_general**: 2
- **max_repair_rounds_this_run**: 0
- **stop_with_gaps**: หยุดเมื่อ pre-run มี gap, งบหมด, ครบเพดานรอบแก้, ข้อเดิมไม่คืบ หรือหลักฐานจำเป็นขาด; ระบุข้อบกพร่อง หลักฐาน ส่วนที่ผ่าน และแนวแก้ถัดไปโดยไม่ดำเนิน phase ถัดไปเอง
- **no_progress**: เมื่ออนุญาตรอบแก้ ให้เทียบ defect เดิม/expected ที่ยังผิด/หลักฐานใหม่กับ evaluation ก่อนหน้า; หากปัญหาเดิมไม่ลดลงและไม่มีหลักฐานคืบหน้าให้ STOP_WITH_GAPS
- **missing_tests**: หาก tests.json ขาด รันผิดรุ่น หรือไม่มีหลักฐาน 3/3 ให้บันทึก NOT_TESTED/gap และ STOP_WITH_GAPS ใน evaluate; ห้ามสร้างผล PASS แทนสคริปต์


## ต้นทุนรวม

เพดานเวลารวมการเรียก 3600 วินาที และ input+output รวม 8000000 tokens ตาม change-conditions.md รวมทุก plan/execute/evaluate/แก้ และ orchestration ที่ล้มเหลวหรือหยุดด้วย การเรียกนี้นับเป็น plan 1 ครั้ง; execute/evaluate ยังไม่เกิด ผู้ทดลองอ่าน wall/usage จาก log หลังจบและตรวจงบก่อนเรียกถัดไป ตัวเลขจริงและต้นทุนเงินยังไม่มีข้อมูล ไม่ประมาณหรือแต่ง ไม่ใช้ log เป็น feedback ของ plan

## สถานะส่งต่อ

ROUND=0 ไม่มี evaluate รอบก่อนเป็น dependency จึงไม่อ่านผลรอบอื่นหรือผล single อ่านและตรวจ hash ของ snapshot ที่กำหนด 4 ไฟล์และ plan-v3 ตรง manifest ทั้ง 5 รายการ; ui-contract ที่ manifest กล่าวถึงไม่ได้เปิดอ่านแยก การตรวจนี้ยืนยันที่มาเท่านั้น

การเรียกนี้สร้างเฉพาะ plan-round-0.md, plan-v4.json และ impact-analysis-change.md ตรวจโครง JSON, dependency ไม่เป็นวงจร, mapping task เดิมครบ และ path อยู่ในขั้นที่กำหนด ไม่ผลิต round-0, execution.md, tests.json หรือ evaluation หยุดรอผู้ทดลองเรียก PHASE=execute ROUND=0
