
# บันทึกการรัน 2026-09-16T08:08:52.668120+00:00

## Plan v1 — PLANNER

| งาน | คำอธิบาย | Dependency | สถานะ (TODO / DONE / DROPPED) |
|---|---|---|---|
| T1 | กำหนดขอบเขต สมมติฐาน และ As-Is Process | - | TODO |
| T2 | ตรวจคุณภาพข้อมูลตัวอย่างและผลกระทบรายแถว | T1 | TODO |
| T3 | ออกแบบ To-Be Process และ Data Model | T2 | TODO |
| T4 | จัดทำ Data Mapping วิธีจับคู่คนไข้ และแผน Migration | T3 | TODO |
| T5 | จัดทำ Gap Analysis และ Roll-out Plan | T4 | TODO |
| T6 | ประกอบเอกสาร ตรวจความครบถ้วนและ Mermaid แล้วส่งมอบ | T5 | TODO |

- เหตุผล: แผนเริ่มต้นตามข้อกำหนด; NEW INFORMATION = NONE
- สิ่งที่เปลี่ยน: สร้าง T1–T6; ยังไม่มีการปรับแผน
- ผลกระทบ: ครอบคลุมผลงานทั้งหกส่วน; เป้าหมายคือเอกสารออกแบบและแผนย้าย ไม่ใช่การย้ายระบบจริง
- Reuse: ยังไม่มีงาน DONE
- จำนวน Re-plan: 0/3


## EXECUTOR / EVALUATOR — T1
- Dependency: ไม่มี; ทำงานตาม Plan v1
- ผลลัพธ์: output.md หัวข้อ 3.1–3.2 ระบุขอบเขต หลักฐาน A1–A7 และ As-Is Mermaid; แยกข้อเท็จจริงออกจากกระบวนการที่อนุมาน
- สถานะ: T1 DONE
- EVALUATOR: แผนยังเหมาะสมอยู่หรือไม่? **ใช่** ผลลัพธ์ครอบคลุม 3 สาขาและ LINE; T2 พร้อมดำเนินการ ไม่จำเป็นต้องทำ T1 ซ้ำ

## EXECUTOR / EVALUATOR — T2
- Dependency: T1 DONE; ทำงานตาม Plan v1
- ผลลัพธ์: output.md หัวข้อ 3.3 พบ 12 กลุ่มปัญหา; ตรวจปฏิทินออฟไลน์ยืนยันว่า R5 ไม่ตรงวันพุธทั้งสองการตีความ; นัดซ้ำและคิวชนยังเป็นข้อสันนิษฐาน
- สถานะ: T2 DONE
- EVALUATOR: แผนยังเหมาะสมอยู่หรือไม่? **ไม่** พบงานที่ยังไม่มีในแผน: ทะเบียนตัดสินข้อมูลกำกวมพร้อมหลักฐานและการกักกัน ต้องทำก่อนใช้ผลตรวจเป็นกติกาออกแบบ/นำเข้า ไม่อาจแก้ด้วยการ format เพียงอย่างเดียว
- Trigger: ผลลัพธ์ทำให้พบงานใหม่; ไม่ใช่ NEW INFORMATION และไม่ใช่การเพิ่มข้อกำหนดจากผู้ใช้


### Plan v2 — PLANNER

| งาน | คำอธิบาย | Dependency | สถานะ (TODO / DONE / DROPPED) |
|---|---|---|---|
| T1 | กำหนดขอบเขต สมมติฐาน และ As-Is Process | - | DONE |
| T2 | ตรวจคุณภาพข้อมูลตัวอย่างและผลกระทบรายแถว | T1 | DONE |
| T2a | กำหนดทะเบียนตัดสินข้อมูล หลักฐาน ผู้รับผิดชอบ และกติกากักกันรายแถว | T2 | TODO |
| T3 | ออกแบบ To-Be Process และ Data Model ที่รองรับผล T2a | T2a | TODO |
| T4 | จัดทำ Data Mapping วิธีจับคู่คนไข้ และแผน Migration พร้อม review gate | T3 | TODO |
| T5 | จัดทำ Gap Analysis และ Roll-out Plan | T4 | TODO |
| T6 | ประกอบเอกสาร ตรวจความครบถ้วนและ Mermaid แล้วส่งมอบ | T5 | TODO |

- เหตุผลที่เปลี่ยนแผน: Trigger “พบงานที่ยังไม่มีในแผน” จาก T2 — ข้อมูลตัวอย่างต้องตัดสินเชิงความหมาย ไม่ใช่เพียงเปลี่ยนรูปแบบวันที่หรือเบอร์
- สิ่งที่เปลี่ยน: เพิ่ม T2a; เปลี่ยน dependency T3 จาก T2 เป็น T2a; ขยายรายละเอียด T3/T4 ให้รองรับ quarantine และหลักฐานการตัดสิน ไม่มีงาน DROPPED
- Impact analysis: T3 ต้องเพิ่มโครงสร้าง source lineage, review และ identity decision; T4 ต้องแยกข้อมูลที่เข้าได้ออกจากรายการรอตรวจ; T5 ต้องเพิ่มเกณฑ์ปิดเคสก่อน cutover; T6 ต้องตรวจความสอดคล้องของส่วนเหล่านี้ งานเหล่านี้ยังไม่เริ่ม จึงไม่มีผลงาน DONE ที่ต้องทำซ้ำ
- Reuse: เก็บ T1 (As-Is และ A1–A7) และ T2 (findings และผลคำนวณวัน) ใช้ต่อทั้งหมด
- จำนวน Re-plan: 1/3; NEW INFORMATION ยังคงเป็น NONE


## EXECUTOR / EVALUATOR — T2a
- Dependency: T2 DONE; ทำงานตาม Plan v2
- ผลลัพธ์: output.md หัวข้อ 3.4 มีทะเบียน R1–R5 พร้อม candidate dates, case IDs, เจ้าของเคส, หลักฐาน, READY gate และ quarantine; ตัวอย่างยังไม่มีรายการที่ได้รับการอนุมัตินำเข้า
- สถานะ: T2a DONE ในขอบเขตการกำหนดกติกาและทะเบียน; ไม่อ้างว่าคลินิกตัดสินข้อมูลจริงแล้ว
- EVALUATOR: แผนยังเหมาะสมอยู่หรือไม่? **ใช่** งานใหม่รองรับความไม่แน่นอนได้โดยไม่เดาหรือรวมคนผิด; T3 ใช้ข้อกำหนดนี้ต่อได้

## EXECUTOR / EVALUATOR — T3
- Dependency: T2a DONE; ทำงานตาม Plan v2
- ผลลัพธ์: output.md หัวข้อ 3.5–3.6 มี To-Be Mermaid, ER diagram 16 entities, กติกาป้องกันคิวชนข้ามสาขา, identity review, source lineage, audit และ notification outbox
- สถานะ: T3 DONE
- EVALUATOR: แผนยังเหมาะสมอยู่หรือไม่? **ใช่** แบบรองรับเบอร์ร่วม คนไม่มีเบอร์ วันกำกวม และนัดที่มาจากหลายแถว โดยไม่บังคับรวมคนอัตโนมัติ; T4 ดำเนินต่อได้

### หมายเหตุแก้คำบรรยาย T3
ER diagram มี 15 entities ไม่ใช่ 16 ตามคำบรรยายก่อนหน้า; เป็นการแก้จำนวนในบันทึก ไม่เปลี่ยนแบบหรือทำงาน DONE ซ้ำ

## EXECUTOR / EVALUATOR — T4
- Dependency: T3 DONE; ทำงานตาม Plan v2
- ผลลัพธ์: output.md หัวข้อ 3.7–3.9 มี mapping ครบ 8 คอลัมน์, patient matching แยกจาก appointment dedup, migration Mermaid, M0–M7, stable source keys, idempotency/delta, reconciliation, acceptance และ rollback ก่อน/หลังเปิดเขียน
- สถานะ: T4 DONE
- EVALUATOR: แผนยังเหมาะสมอยู่หรือไม่? **ใช่** ไม่มีการทิ้งแถวหรือ merge จากเบอร์อย่างเดียว; การย้อนระบบรักษารายการที่เกิดหลัง cutover; ยังมี T5 รองรับ gap และการเปิดใช้ จึงไม่ต้องเพิ่มงานหรือ re-plan

## EXECUTOR / EVALUATOR — T5
- Dependency: T4 DONE; ทำงานตาม Plan v2
- ผลลัพธ์: output.md หัวข้อ 3.10–3.11 มี gap 12 เรื่อง, owner/P0/P1, rollout W1–W6, UAT/monitoring gates และการใช้คิวกลางทั้ง 3 สาขาตั้งแต่ pilot แม้ขยายผู้ใช้ UI ทีละสาขา
- สถานะ: T5 DONE
- EVALUATOR: แผนยังเหมาะสมอยู่หรือไม่? **ใช่** แผนปิดช่องคิวหมอข้ามสาขาระหว่างทยอยเปิดใช้ มีเจ้าของและ go/no-go ชัด; เหลือ T6 ตรวจเอกสารและสรุปผล ไม่มี trigger ใหม่

## EXECUTOR / EVALUATOR — T6
- Dependency: T5 DONE; ทำงานตาม Plan v2
- ผลลัพธ์: ประกอบ output.md ฉบับเต็มและ response.md ตาม OUTPUT FORMAT; ตรวจว่าทุกหัวข้อครบ, Mermaid 4 blocks และ ER 15 entities มีโครงสร้าง/references สอดคล้อง; ตรวจ CSV 5 แถว/8 คอลัมน์/3 สาขา เบอร์ และวัน/เวลาออฟไลน์; สถานะปิดงาน 7 งาน DONE
- Impact analysis: การตรวจพบภาพ T3 บังคับ appointment สำหรับ AuditEvent แต่ตารางระบุ audit ประเภทอื่นได้ จึงแก้เฉพาะ cardinality เป็น optional; reuse T3 ส่วนอื่นทั้งหมด ไม่มีการเปลี่ยน dependency หรือข้อกำหนด ไม่เกิด trigger re-plan ใหม่
- ผลตรวจรอบแรก: assertion นับข้อความ T2a แบบกว้างเกินไป จึงนับรวมช่อง dependency และบันทึกงาน; เป็นข้อผิดพลาดของสคริปต์ตรวจ แก้เป็นนับแถวงานที่ขึ้นต้นด้วย T2a แล้วตรวจซ้ำผ่าน ไม่ได้เปลี่ยนแผนหรือจำนวนงาน
- ข้อจำกัด: ไม่มี mmdc/mermaid executable และ mermaid/mermaid-cli module ที่ resolve ได้จาก workspace; ไม่ได้รัน Mermaid syntax parser/render; ไม่ติดตั้งแพ็กเกจหรือใช้เครือข่าย
- สถานะ: T6 DONE
- EVALUATOR: แผนยังเหมาะสมอยู่หรือไม่? **ใช่** และยืนยันว่าบรรลุเป้าหมายการส่งมอบเอกสารครบถ้วน ทุกงาน DONE ไม่มี DROPPED; re-plan 1/3 ครั้ง จึงหยุดตาม STOP CONDITION
- สิ่งที่ยังไม่ยืนยัน: วันที่/ตัวตน/นัดซ้ำ/คิวชนและข้อมูลปฏิบัติการจริงมี owner และ gate ในเอกสารแล้ว; การส่งมอบไม่ใช่การอนุมัติ production migration

# เฟส 2 — NEW INFORMATION

### Plan v3 — PLANNER (updated: change request)

| งาน | คำอธิบาย | Dependency | สถานะ (TODO / DONE / DROPPED) |
|---|---|---|---|
| T1 | ขอบเขต สมมติฐาน และ As-Is ฉบับเฟส 1 | - | DONE |
| T2 | Data Quality Findings ของ CSV ฉบับเฟส 1 | T1 | DONE |
| T2a | ทะเบียนตัดสินและกักกันข้อมูลฉบับเฟส 1 | T2 | DONE |
| T3 | To-Be และ Data Model ฉบับเฟส 1 | T2a | DONE |
| T4 | Mapping และ Migration ฉบับเฟส 1 | T3 | DONE |
| T5 | Gap และ Roll-out ฉบับเฟส 1 | T4 | DONE |
| T6 | ตรวจและส่งมอบเฟส 1 | T5 | DONE |
| T7 | ออกแบบความยินยอมและเพิ่มข้อกำหนด/ช่องว่างข้อมูล/เกณฑ์ตรวจของเฟส 2 | T1, T2, T2a, T6 | TODO |
| T8 | ปรับ To-Be และ Data Model ให้จองเองผ่าน LINE OA พร้อม consent lifecycle | T7, T3 | TODO |
| T9 | ปรับ Mapping, patient linking และ Migration รวม legacy consent และ rollback | T8, T4 | TODO |
| T10 | ปรับ Gap, Roll-out และ acceptance ให้ PDPA consent กับ LINE OA self-service เป็น P0 | T9, T5 | TODO |
| T11 | ตรวจการเปลี่ยนแปลง การ reuse ความครบถ้วน และส่งมอบเฟส 2 | T10, T6 | TODO |

- เหตุผลที่เปลี่ยนแผน: Trigger “NEW INFORMATION ทำให้ข้อกำหนดเปลี่ยนไป” — เจ้าของคลินิกกำหนดให้เก็บความยินยอมของคนไข้ตาม PDPA และให้คนไข้จองเองผ่าน LINE OA ได้
- สิ่งที่เปลี่ยน: เพิ่มงานส่วนต่าง T7–T11; LINE OA self-service เปลี่ยนจากส่วนเสริมในแผนเดิมเป็นข้อกำหนด P0 ก่อนเปิดให้คนไข้ใช้; เพิ่ม purpose/version/evidence/withdrawal ของ consent และการผูก LINE กับคนไข้ ไม่ตัดงานหรือข้อกำหนดเดิม ไม่มี DROPPED
- Impact analysis: T1 เฉพาะขอบเขต/A5 ใน 3.1; T2 เพิ่ม findings เรื่อง consent/LINE ใน 3.3 โดยไม่ตรวจ CSV เดิมซ้ำ; T2a เพิ่ม review gate ใน 3.4; T3 ปรับ flow/model/notification ใน 3.5–3.6; T4 ปรับ mapping, identity linking, import, reconciliation และ rollback ใน 3.7–3.9; T5 ปรับ P0, rollout และ UAT ใน 3.10–3.11; T6 ปรับผลตรวจและคำตัดสินใน 3.12 พร้อม Version Log/Work Log การแก้ผล DONE จำกัดเฉพาะส่วนที่ระบุนี้ ผ่าน T7–T11
- Reuse: คง As-Is 3.2 ทั้งหมด; findings CSV 12 กลุ่มและผลปฏิทินเดิม; ทะเบียน R1–R5 เดิม; master/ตารางคิว/กฎห้าม merge จากเบอร์; source lineage, idempotency, single writer และ rollback journal ใช้ต่อโดยเพิ่มข้อกำหนดใหม่ ไม่ทำงานเดิมซ้ำทั้งงาน
- ขอบเขตการยืนยัน: ส่งมอบเอกสารออกแบบ ไม่ใช่ลงระบบจริงหรือรับรองการปฏิบัติตามกฎหมาย ต้องให้ผู้รับผิดชอบ PDPA ของคลินิกทบทวนวัตถุประสงค์ ฐานการประมวลผล ข้อความ และอายุการเก็บก่อนใช้งาน; ไม่ใช้เครือข่าย/ติดตั้งแพ็กเกจตาม harness เดิม
- จำนวน Re-plan สะสม: 2/3 ครั้ง (v1 → v2 ครั้งที่ 1; v2 → v3 ครั้งที่ 2); เหลือได้อีก 1 ครั้งหากเกิด trigger ใหม่
- สถานะ DONE ของ T1–T6/T2a คือผลเฟส 1 ที่ส่งมอบแล้ว ไม่ได้หมายความว่าส่วนที่ได้รับผลกระทบในเฟส 2 เสร็จก่อน T7–T11


## EXECUTOR / EVALUATOR — T7 (เฟส 2)
- Dependency: T1, T2, T2a, T6 DONE; ทำตาม Plan v3
- ผลลัพธ์: output.md 3.1 ปรับ A5 และเพิ่ม CR1/CR2, purpose matrix, consent lifecycle/evidence/withdrawal; 3.3 เพิ่ม findings 3 กลุ่มจากข้อมูลเดิม; 3.4 เพิ่ม consent/LINE review gates แยกจาก migration status; ทุกส่วนที่แก้มี (updated: change request)
- Reuse: As-Is 3.2, findings เดิม 12 กลุ่ม, ผลปฏิทิน และทะเบียนเดิมไม่ถูกทำซ้ำ; raw 5 / quarantine 5 / READY 0 ยังเดิม
- ข้อจำกัด: ไม่ใช้เครือข่ายตาม harness จึงไม่อ้างตรวจ PDPA ล่าสุด; กำหนดผู้รับผิดชอบอนุมัติฐาน ข้อความ และสิทธิ์แทนก่อนใช้งานจริง
- สถานะ: T7 DONE
- EVALUATOR: แผนยังเหมาะสมอยู่หรือไม่? **ใช่** รองรับ consent ที่มีหลักฐาน ไม่ยก consent ให้ทุกฐาน และไม่ใช้ consent การตลาดบังคับจอง; ข้อจำกัดอยู่ในงานออกแบบที่กำหนด ไม่เกิด trigger ใหม่

## EXECUTOR / EVALUATOR — T8 (เฟส 2)
- Dependency: T7, T3 DONE; ทำตาม Plan v3
- ผลลัพธ์: output.md 3.5 เปลี่ยนเส้นทางหลักเป็นคนไข้จองเองผ่าน LINE OA จน commit/รับ receipt มี auth, authorization, consent, concurrency/idempotency และ fallback; 3.6 ขยาย ER จาก 15 เป็น 23 entities พร้อม consent event/version/authority และ booking request
- Reuse: กติกาคิวหมอ/เก้าอี้/การเดินทาง, lifecycle นัด, outbox, audit และโมเดลเดิม; แก้เฉพาะส่วนที่ Impact analysis ของ v3 ระบุ
- สถานะ: T8 DONE
- EVALUATOR: แผนยังเหมาะสมอยู่หรือไม่? **ใช่** happy path ไม่รอเจ้าหน้าที่ ไม่ใช้ LINE login แทน consent ไม่เปิดแฟ้มจากเบอร์ และไม่คืนสิทธิ์ที่ถอนไปจาก merge/retry; T9/T10 ที่วางไว้ครอบคลุมผลต่อ migration/rollout แล้ว

## EXECUTOR / EVALUATOR — T9 (เฟส 2)
- Dependency: T8, T4 DONE; ทำตาม Plan v3
- ผลลัพธ์: output.md 3.7 เพิ่ม mapping 8 กรณีสำหรับ consent/LINE; 3.8 เพิ่ม verified linking, proxy scope และ merge/withdrawal rules; 3.9 ปรับ migration flow และเพิ่ม M0–M7, legacy unknown, event reconciliation และ rollback ที่ไม่คืนสิทธิ์ withdrawn/revoked
- Reuse: mapping CSV เดิม, candidate identity/dedup, raw disposition, source keys, data journal และขั้นตอน M0–M7 เดิมใช้ต่อ ไม่แก้ raw หรือสร้างหลักฐานยินยอมปลอม
- สถานะ: T9 DONE
- EVALUATOR: แผนยังเหมาะสมอยู่หรือไม่? **ใช่** แยก consent จากฐานการใช้ข้อมูลและ account authority; แม้ freeze/restore ยังรักษา withdrawal journal และปิดกิจกรรมที่ยังบังคับสิทธิ์ไม่ได้; T10 รองรับการตรวจรับครบ ไม่มี trigger ใหม่

## EXECUTOR / EVALUATOR — T10 (เฟส 2)
- Dependency: T9, T5 DONE; ทำตาม Plan v3
- ผลลัพธ์: output.md 3.10 เปลี่ยน LINE self-service เป็น P0 และเพิ่ม gap consent/withdrawal/verified linking; 3.11 ปรับ rollout ให้ pilot และขยายคนไข้จองเองครบ 3 สาขา พร้อม UAT-CR 18 สถานการณ์และเจ้าของ go/no-go
- Reuse: single writer/คิวหมอร่วม, master readiness, baseline acceptance และบทบาทปฏิบัติการเดิม; ปรับประมาณการเวลาให้รับขอบเขต integration ใหม่ ไม่อ้างกำหนดเดิมยังใช้ได้แน่นอน
- สถานะ: T10 DONE
- EVALUATOR: แผนยังเหมาะสมอยู่หรือไม่? **ใช่** ข้อกำหนดทั้งสองเป็นเกณฑ์ P0 ไม่ถูกลดเป็นงานเสริม; ระบุว่าตาราง UAT คือแผนทดสอบจริงในอนาคต ไม่อ้างรันแล้ว; เหลือ T11 ตรวจเอกสารตามแผน

## EXECUTOR / EVALUATOR — T11 (เฟส 2)
- Dependency: T10, T6 DONE; ทำตาม Plan v3
- ผลลัพธ์: output.md เป็นฉบับสมบูรณ์ v3 พร้อม log ทุกเวอร์ชันและงานเฟส 2; response-phase2.md เป็นข้อความตอบตาม OUTPUT FORMAT; ตรวจ 11 หัวข้อผลงานที่เปลี่ยนมี (updated: change request), 4 Mermaid blocks, ER 23 entities, UAT-CR 18 สถานการณ์ และสถานะสุดท้าย 12 งาน DONE
- ผลตรวจการเก็บประวัติ: SHA-256 ของ trace prefix เดิม 12,514 bytes ตรงกับ 9693bfb6d904735a50cf833cfb85f814a9ff2f5ccb14a6c172f68edf9368dd77; As-Is 3.2 และ response.md เฟส 1 มี hash ตรงเดิม ไม่มีการเขียนทับ trace ก่อนหน้า
- Impact analysis / การแก้ระหว่างตรวจ: ย้ายนิยาม ER ใหม่ 8 entities ของ T8 จากนอก fence เข้า mermaid block เดิม; เปลี่ยนเฉพาะการจัดวางตามขอบเขต T11 ไม่เปลี่ยนแบบหรือ dependency ไม่ต้อง re-plan
- สคริปต์ตรวจรอบแรกมี regex escape เกินเมื่อส่งผ่าน JavaScript ทำให้นับหัวข้อไม่ได้; แก้เป็น raw string แล้วตรวจซ้ำผ่านทุก assertion โดยไม่เปลี่ยนเนื้อหาเอกสารเพื่อให้ทดสอบผ่าน
- ข้อจำกัดการตรวจ: ตรวจเฉพาะโครงสร้าง Mermaid/references ไม่ใช่ syntax parser/render; ไม่รันระบบจริง ไม่เก็บ consent จริง ไม่ตรวจ PDPA ล่าสุดหรือ LINE API ผ่านเครือข่ายตาม harness; มี policy/legal/integration/UAT gates ก่อน production ในเอกสารแล้ว
- สถานะ: T11 DONE; T7–T11 DONE ทั้งหมด; งานเดิม 7 งานยัง DONE รวม 12 งาน ไม่มี DROPPED
- EVALUATOR: แผนยังเหมาะสมอยู่หรือไม่? **ใช่** และยืนยันบรรลุเป้าหมายการส่งมอบเอกสารที่รวม CR1 และ CR2 ครบ; ไม่เกิด trigger ใหม่ ใช้ re-plan สะสม 2/3 ครั้ง หยุดตาม STOP CONDITION เพราะทุกงานเสร็จและ EVALUATOR รับรอง
