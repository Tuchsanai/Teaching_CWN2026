# verify-flow — ผลตรวจเอกสารหลังกรอง

REVIEW_MODE: artifacts; TASK_ID: verify-flow; RUN_ID: audit-fr-review; plan-v1; ตรวจ UTC: 2026-09-14T12:49:49.985266Z.
ผลรวม: **FAIL เฉพาะ traceability เอกสาร F-01 (US-11)**; พฤติกรรมใน Flow/AC ยังถูกเก็บไว้. ไม่ใช่ผล FAIL ของระบบจริง; Mock-up และระบบจริง **NOT_TESTED**.
Path ย่อจากราก LAB; B = reference/step-00-input/baseline-filtered-v2; F = B/flow.md; S = B/state-machine.md; T = B/structure.md.
Gate: audit-fr-baseline มี output จริง; verify-fr PASS ถูกบันทึกก่อนเริ่มงานนี้; hash target/reuse ตรง. Snapshot ยังคง planned.

วิธีตรวจจริง: อ่าน Flow ทุก main/alternative/error พร้อม guard/ผลหลังจบ; Python เทียบ AC และ quote กับ FR, ตรวจ reference/mapping, เทียบตาราง state/structure กับฉบับรวม และ hash bytes ปัจจุบัน.
PASS เชิงโครงสร้าง: 30 flows (main 14/alternative 9/error 7), 54 คู่ Flow–FR มี AC/พฤติกรรมอ้างตรงตัว; coverage มี 18 US; ไม่ใช่การพิสูจน์ความครบ screen ปลายทาง (พบ F-01).
PASS: merge mapping 111 แถว ครอบคลุม root 36 flows และสำเนาสอง node; ทุก target/path type ตรง; KF-07 แยก MRG-10/P-07 และ MRG-11/P-06 โดยคง P-04/P-05 (F:102–212,373–374).
PASS: transition 17 แถว เทียบ entity/current/event/actor/guard/next/side-effect/refs/quote/locator/support/assumption กับ S ครบ; FR ทั้ง 18 พบพฤติกรรม+AC ตรงใน F/S; ภาคผนวก F คง 15 NFR/18 traceability/18 Q ตรง FR.
PASS การคงโครงสร้าง: 11 modules, 23 entities, 16 screens, 31 permissions ตรงระหว่าง T กับ F หลังแปลง namespace; การคัดตรงไม่แก้ช่องว่างที่มีอยู่ใน T (F-01).

| US | FR locator; coverage F/T; Flow ID | ผลเอกสาร | Mock-up / ระบบจริง |
|---|---|---|---|
| US-01 | B/fr-nfr.md:20; F:42/T:214; MRG-01,MRG-12 | PASS — ส่วนที่เปิดและข้อค้างคงอยู่ | NOT_TESTED / NOT_TESTED |
| US-02 | B/fr-nfr.md:21; F:43/T:215; MRG-01,MRG-04,MRG-12,MRG-13 | PASS — ส่วนที่เปิดและข้อค้างคงอยู่ | NOT_TESTED / NOT_TESTED |
| US-03 | B/fr-nfr.md:22; F:44/T:216; MRG-02,MRG-04,MRG-14 | PASS — ส่วนที่เปิดและข้อค้างคงอยู่ | NOT_TESTED / NOT_TESTED |
| US-04 | B/fr-nfr.md:23; F:45/T:217; MRG-03,MRG-04 | PASS — ส่วนที่เปิดและข้อค้างคงอยู่ | NOT_TESTED / NOT_TESTED |
| US-05 | B/fr-nfr.md:24; F:46/T:218; MRG-05 | PASS — ส่วนที่เปิดและข้อค้างคงอยู่ | NOT_TESTED / NOT_TESTED |
| US-06 | B/fr-nfr.md:25; F:47/T:219; MRG-08,MRG-09,MRG-18 | PASS — ส่วนที่เปิดและข้อค้างคงอยู่ | NOT_TESTED / NOT_TESTED |
| US-07 | B/fr-nfr.md:26; F:48/T:220; MRG-03,MRG-04 | PASS — ส่วนที่เปิดและข้อค้างคงอยู่ | NOT_TESTED / NOT_TESTED |
| US-08 | B/fr-nfr.md:27; F:49/T:221; MRG-03,MRG-04,MRG-06,MRG-07,MRG-10,MRG-11 | PASS — ส่วนที่เปิดและข้อค้างคงอยู่ | NOT_TESTED / NOT_TESTED |
| US-10 | B/fr-nfr.md:28; F:50/T:222; MRG-04 | PASS — ส่วนที่เปิดและข้อค้างคงอยู่ | NOT_TESTED / NOT_TESTED |
| US-11 | B/fr-nfr.md:29; F:51/T:223; MRG-05 | FAIL F-01 — ขาดจอผู้รับหน้าร้าน | NOT_TESTED / NOT_TESTED |
| US-12 | B/fr-nfr.md:30; F:52/T:224; MRG-08,MRG-18,MRG-19 | PASS — ส่วนที่เปิดและข้อค้างคงอยู่ | NOT_TESTED / NOT_TESTED |
| US-13 | B/fr-nfr.md:31; F:53/T:225; MRG-09,MRG-20 | PASS — ส่วนที่เปิดและข้อค้างคงอยู่ | NOT_TESTED / NOT_TESTED |
| US-15 | B/fr-nfr.md:32; F:54/T:226; MRG-04,MRG-06,MRG-07,MRG-10,MRG-11,MRG-13,MRG-14 | PASS — ส่วนที่เปิดและข้อค้างคงอยู่ | NOT_TESTED / NOT_TESTED |
| US-16 | B/fr-nfr.md:33; F:55/T:227; MRG-12,MRG-13,MRG-15,MRG-16,MRG-17 | PASS — ส่วนที่เปิดและข้อค้างคงอยู่ | NOT_TESTED / NOT_TESTED |
| US-19 | B/fr-nfr.md:34; F:56/T:228; MRG-21,MRG-22,MRG-23,MRG-24,MRG-25 | PASS — ส่วนที่เปิดและข้อค้างคงอยู่ | NOT_TESTED / NOT_TESTED |
| US-20 | B/fr-nfr.md:35; F:57/T:229; MRG-23,MRG-25 | PASS — ส่วนที่เปิดและข้อค้างคงอยู่ | NOT_TESTED / NOT_TESTED |
| US-25 | B/fr-nfr.md:36; F:58/T:230; MRG-26,MRG-27,MRG-28 | PASS — ส่วนที่เปิดและข้อค้างคงอยู่ | NOT_TESTED / NOT_TESTED |
| US-26 | B/fr-nfr.md:37; F:59/T:231; MRG-29,MRG-30 | PASS — ส่วนที่เปิดและข้อค้างคงอยู่ | NOT_TESTED / NOT_TESTED |

F-01 — expected: B/fr-nfr.md:29 และ F:71/MRG-05 กำหนดครัวกด → จอหน้าร้านแสดงสถานะใหม่ โดยคง 1 แตะ/5 วินาทีบน LAN/อย่างน้อย 18 จาก 20 ครั้ง.
F-01 — actual: F:51 และ T:223 ให้ US-11 เพียง SCR-04 (ลูกค้า) กับ SCR-06 (ครัว), ตาม F:447,449 / T:69,71. ไม่มี screen ของหน้าร้านใดอ้าง FR-11/MRG-05.
F-01 — จุดที่ขาด: SCR-08 หน้าร้านมีเพียง MRG-13/14/04 และ FR-02/03/10/15/16 (F:451; T:73); MOD-06 เช่นกัน (F:406; T:22). แม้ Flow/transition กล่าวถึงผู้รับถูกต้อง แต่ handoff ไป screen/module ขาดปลายทางของ AC.
แก้เฉพาะจุด: ในฉบับแก้ใหม่เชื่อม FR-11/US-11 และ MRG-05 ไปจอรับสถานะของหน้าร้านที่เลือก เช่น SCR-08 พร้อม module/coverage และข้อมูลสถานะออเดอร์ให้ตรงกันทั้ง T/F; ไม่เปลี่ยนตัวเลข AC หรือใช้สถานะเงินแทนสถานะอาหาร. การเลือกจอเป็นข้อเสนอการจัดวาง ไม่ใช่กฎร้านใหม่.
ส่ง Planner: baseline ห้ามแก้และ plan-v1 ไม่มีงาน revise Flow/structure; ต้องวาง producer/outputs รุ่นใหม่และ dependency recheck ก่อนแก้ ห้ามทับหลักฐานเดิม. งานนี้ตรวจครั้งที่ 1 แก้ artifacts 0 รอบ; เพดาน 2 รอบต่อปัญหาเป็นข้อตกลงการเรียน.
Downstream BLOCKED: verify-test-outline → verify-ui → evaluate-handoff รอ verify-flow PASS; draft-test-outline ยังเริ่มจาก FR ที่ผ่านได้ตาม dependency โดยต้องคง F-01 และห้ามถือว่าการตรวจข้าม Flow ผ่านแล้ว.

PASS การแยกสถานะ: F:272–296,311–315 และ S:36–157 แยกออเดอร์/ชำระเงิน/โต๊ะ; ส่วนรายการที่ปิดไว้ไม่ถูกกู้; AI task status ไม่ใช่ธุรกิจ. initial/terminal และ O-04 mapping ยังเป็นข้อเสนอ ไม่ได้อนุมัติ.
PASS ผลกระทบ: US-05/07/11 ใช้จุดจบ ETA แยกเสร็จแล้ว (F:69–71,283,302–305); F-01 เกี่ยวปลายทาง US-11 ไม่เปลี่ยนจุดวัดลูกค้า US-05 และไม่ปิด A-05 ของ US-07.
PASS ผลกระทบ: US-08/15 fallback ไม่ทำให้จ่ายแล้ว ต้องกดหน้าร้านพร้อม log; US-16 ปิดรอบไม่แปลว่าจ่ายแล้ว (F:72–83,285–296).
PASS ผลกระทบ: US-12/13/19/20 → เมนู/ตัวเลือก → US-06/04/08 คงกฎแมป/ราคาเดิม/ยอดและใบครัว; ไม่เปลี่ยนออเดอร์ที่รับแล้วเองหรือแก้ US-20 อ้าง US-14 (F:74–75,84–91; T:36–57).
BLOCKED เฉพาะยืนยันกฎจริง: MC-01–MC-03 unresolved (F:239–241); 43 assumptions ยังไม่ยืนยัน (F:510–552); หมายเหตุ ก./ค./ช., สิทธิ์ Unknown, กฎซ้ำ/แข่ง/วัตถุดิบซ้อน/ค้างจ่ายและ initial/terminal ยังรอมนุษย์.
NOT_TESTED: UI/data-testid/DOM/click/responsive, LAN/ความเร็ว/โหลด/สัดส่วน AC/ETA/log/security, Ubuntu/ติดตั้ง/offline/ชำระเงินจริง; ไม่มี browser run และไม่ใช้ UI check เดิมแทน.
ข้อจำกัดที่มา: node JSON/flow-state-machine.md/flow-structure.md/review-record และต้นทางก่อนกรองไม่อยู่ในสำเนาที่ตรวจ ไม่เปิดตามลิงก์หรือ reveal; hash ประวัติก่อนกรองไม่ใช่ expected hash ปัจจุบัน. flow-check.json เป็นผล upstream เท่านั้น.

| หลักฐาน | SHA-256 |
|---|---|
| reference/session/plan-v1.json | `4bd023624fb2cb5c1ec9975528e8ffbcb6ac830cd40f9b61c5db28523ae25cfe` |
| reference/session/plan-v1.md | `10f2d1da058fafe1a6ed75047ad157ab0694cb7ee40ddd89c91874fa4d3310ae` |
| reference/session/execution/fr-baseline-audit-v1.md | `78f8ce610526fdaa3e7911b3765fbff8246ea223d9772611e370bb42d5374175` |
| B/fr-nfr.md | `da31640e540b825d4fec555627ea098f092daf4243d5d304fd4c32ae6db734cd` |
| B/flow.md | `d0a5fcd029f4f315a02fcd2c057a44907bdf7362fbce17b8664a75b82773595d` |
| B/state-machine.md | `b4bc79de9e95f1526ca05326211a6025981b0420f3681b574e37189319f35adf` |
| B/structure.md | `fc8facf9088ad320d8dc3a7157edc14b337c1cb7081c3b098bcf91ceab08c560` |
| reference/session/evaluations/fr-v1-check.md | `b533a2d6b8618f590d3de91bdc4250172ad8d987df6060860f16e0a672403c5a` |
สร้างจริง: reference/session/evaluations/flow-v1-check.md; output hash/รายละเอียด input hashes อยู่รายงานหลักและ audit-fr-review-evidence.json หลังเขียน; ไม่ลบ READINESS: BLOCKED ของ F:5.
