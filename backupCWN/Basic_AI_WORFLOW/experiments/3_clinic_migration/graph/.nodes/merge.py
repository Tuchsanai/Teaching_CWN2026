import json,re
from pathlib import Path
nodes={n:json.loads(Path('.nodes',n+'.json').read_text()) for n in ['N1','N1b','N2','N3','N4']}
for n,x in nodes.items():
 assert set(x)=={'node','status','output','assumptions'}
 assert x['node']==n and x['status']=='DONE'
 assert isinstance(x['output'],str) and isinstance(x['assumptions'],list)
trace='''# 1. Execution trace

| Node | สถานะ | หมายเหตุ |
|---|---|---|
| N1 | DONE | ตรวจ CSV ครบ 5 แถว; ทำเครื่องหมายประเด็นกำกวมทุกแถว โดยแยกความกำกวมของค่าจากความสัมพันธ์ระหว่างระเบียน |
| N1b | DONE | ใช้ conditional edge; ตรวจหลักฐานและวันในสัปดาห์ ระบุเรื่องที่ยังต้องให้มนุษย์ยืนยัน |
| N2 | DONE | เริ่มหลัง N1/N1b DONE; ทำ As-Is โดยไม่เห็นผล N3/N4 |
| N3 | DONE | เริ่มหลัง N1/N1b DONE; ทำ To-Be/ERD โดยไม่เห็นผล N2/N4 |
| N4 | DONE | เริ่มหลัง N1/N1b DONE; ทำ mapping/migration โดยไม่เห็นผล N2/N3 |
| N5 | DONE | รับเฉพาะ contract ที่ตรวจแล้วและสถานะ DONE; รวมหลัง N2–N4 ครบ พร้อม gap, roll-out, version log และรายการข้อขัดแย้ง |

N2–N4 ใช้ผู้ทำงานแยกกันและทำงานพร้อมกัน รับเฉพาะ INPUT และผล N1/N1b ไม่มีการส่งผลระหว่างกัน ทุก Node สำเร็จในการทำงานครั้งแรก จึงไม่ต้อง retry; ไม่มี Node FAILED และไม่มีผลงานของ Node ที่ขาด หยุดเมื่อ N5 DONE รายการรอตรวจข้อมูลไม่ใช่ความล้มเหลวของการจัดทำแผน

# 2. ผลงานส่งมอบสุดท้ายที่รวมแล้ว

## ขอบเขตและหลักฐานต้นทาง

แผนย้ายระบบนัดหมายคลินิกทันตกรรมจาก Google Sheet แยกสาขาและ LINE สู่ระบบกลาง เอกสารนี้เป็นแบบออกแบบและแผนดำเนินงาน ยังไม่ได้ย้ายข้อมูลจริงหรือรับรองนัดใดให้เปิดใช้งาน

หลักฐานตั้งต้น: “คลินิกทันตกรรม 3 สาขา ใช้ Google Sheet แยกสาขา ร่วมกับจองผ่าน LINE ต้องการย้ายมาระบบนัดหมายกลาง” เลขแถวต่อไปนี้นับเฉพาะข้อมูล ไม่รวม header:

```csv
'''+Path('.nodes/input.csv').read_text()+'''```

ทุก entity, field, บทบาท, สถานะและวิธีควบคุมใน To-Be/Migration/Roll-out เป็น **ข้อเสนอ** ไม่ใช่กฎเดิมที่โจทย์ยืนยัน ไม่กำหนดวันเปิดจริง ระยะเวลาบริการ ความจุ เป้าหมายเชิงตัวเลข หรือเกณฑ์คะแนนจับคู่ที่โจทย์ไม่ได้ให้ การอนุมัติที่ระบุเป็นกิจกรรมในแผนของคลินิก ไม่ใช่การถามผู้ใช้ในการรันนี้

## Data Quality Findings — N1

'''
body=trace+nodes['N1']['output']+'\n## ข้อสรุปแถวกำกวม — N1b\n\n'+nodes['N1b']['output']+'\n'+nodes['N2']['output']+'\n'
n3=nodes['N3']['output']
# Editorial harmonization: optional draft/review relations, complete lineage and rollback model.
for a,b in {
'PATIENT ||--o{ APPOINTMENT : attends':'PATIENT o|--o{ APPOINTMENT : attends',
'BRANCH ||--o{ APPOINTMENT : hosts':'BRANCH o|--o{ APPOINTMENT : hosts',
'SERVICE ||--o{ APPOINTMENT : requested_service':'SERVICE o|--o{ APPOINTMENT : requested_service',
'POLICY_VERSION ||--o{ APPOINTMENT : validated_under':'POLICY_VERSION o|--o{ APPOINTMENT : validated_under',
'BRANCH ||--o{ SCHEDULE_EXCEPTION : applies_at':'BRANCH o|--o{ SCHEDULE_EXCEPTION : applies_at',
'REVIEW_DECISION ||--o{ CANONICAL_MAPPING : authorizes':'REVIEW_DECISION o|--o{ CANONICAL_MAPPING : authorizes',
'คืน receipt หรือผลเดิม\\nไม่สร้าง patient / appointment ซ้ำ':'อ่าน receipt และ processing state\\nคืนผลที่เสร็จแล้วหรือ resume งานค้าง',
'        string status\n        uuid policy_version_id FK':'        string status\n        string note_optional\n        uuid policy_version_id FK',
'        string importer_version\n':'        string importer_version\n        string mapping_version\n        string normalization_version\n',
'    IMPORT_BATCH ||--o{ SOURCE_RECORD : contains':'    IMPORT_BATCH ||--o{ SOURCE_RECORD : contains\n    SOURCE_RECORD ||--o{ PATIENT_ALIAS : provenance\n    SOURCE_RECORD o|--o{ RESOURCE_SCHEDULE : supports\n    REVIEW_DECISION o|--o{ REVIEW_DECISION : supersedes\n    IMPORT_BATCH ||--o{ IMPORT_OPERATION : runs\n    SOURCE_RECORD ||--o{ IMPORT_OPERATION : processed_by\n    IMPORT_OPERATION ||--o{ IMPORT_MUTATION : records'
}.items():
 assert a in n3,a
 n3=n3.replace(a,b)
new_entities='''    IMPORT_OPERATION {
        uuid operation_id PK
        uuid batch_id FK
        uuid source_record_id FK
        string operation_key UK
        string mapping_version
        string normalization_version
        string decision_version
        string state
        json receipt
    }
    IMPORT_MUTATION {
        uuid mutation_id PK
        uuid operation_id FK
        string target_type
        string target_id
        string mutation_type
        json before_image
        json after_image
        string expected_target_revision
        string resulting_target_revision
        string reversal_state
    }
'''
pos=n3.index('\n```',n3.index('```mermaid\nerDiagram'))
n3=n3[:pos]+'\n'+new_entities+n3[pos:]
n3+='''
### ข้อกำกับแบบจำลองฉบับรวม

ERD แสดง nullable relation สำหรับ draft appointment; เมื่อ activate ต้องมี patient, branch, service, policy และทรัพยากรที่จำเป็นครบตาม policy ที่รับรอง สถานะ draft/held จึงไม่ขัดกับข้อมูลที่ยังขาด `REVIEW_DECISION` ของ mapping เป็น optional สำหรับการแปลงที่แน่นอนตาม rule version; ถ้าเป็นการยืนยันโดยมนุษย์ต้องมี decision เสมอ `branch_id_optional` ของ exception รองรับข้อยกเว้นระดับ resource เมื่อได้รับอนุมัติขอบเขตจริง

เพิ่ม `APPOINTMENT.note_optional` เพื่อแสดงหมายเหตุที่ยืนยันแล้ว โดยยังเก็บข้อความต้นทางของทุกแถวใน `SOURCE_RECORD.raw_payload` เสมอ หมายเหตุใน CSV ที่เป็นช่องว่างจริงต้องคงเป็นช่องว่าง ไม่เติมคำว่า “ว่าง” เป็นข้อมูลนำเข้า

`IMPORT_OPERATION` แยกการประมวลผลแต่ละ version ออกจาก source record: source key คงเดิมเมื่อ replay artifact เดิม ส่วน operation key รวม source identity และ mapping/normalization/decision version; batch ใหม่เพียงอย่างเดียวไม่ทำให้ source เดิมกลายเป็นนัดใหม่ ก่อน update ต้องตรวจ canonical mapping และ target revision เดิม ไม่สร้าง target ใหม่เพียงเพราะเปลี่ยน version สถานะค้างต้อง resume หรือ review ได้ ไม่คืนผลเสมือนสำเร็จ

`IMPORT_MUTATION` เป็น ledger แบบเสนอสำหรับ rollback มี before/after image และ revision; `target_type/target_id` อ้างได้หลาย entity จึงเป็น logical reference ที่ต้องตรวจใน application ไม่ใช่ FK ที่ฐานข้อมูลรับรองอัตโนมัติ `CANONICAL_MAPPING` คือ crosswalk ส่วน `REVIEW_DECISION` คือ decision audit การแก้ไขในระบบกลางหลัง cutover ต้องมีประวัติ version/before-after/reviewer เช่นกัน จึงใช้ ledger ที่อ้าง operation ของคำขอแก้ไขได้ โดย batch/source เก็บ request envelope ของระบบกลาง ไม่อ้างว่าเป็น Google source

ไม่กำหนดชนิดฐานข้อมูล/UUID/version implementation ให้เป็นข้อยุติของระบบปลายทาง ชื่อใน ERD เป็นชื่ออ้างอิงของเอกสารและ logical model ซึ่งต้องตรวจร่วมกับระบบที่เลือกก่อน implementation
'''
body+=n3+'\n## Data Mapping และแผน Migration — N4 ที่รวมเข้ากับแบบจำลอง\n\n'
n4=nodes['N4']['output']
start=n4.index('| คอลัมน์ต้นทาง |')
end=n4.index('\nการแปลงเป็น E.164',start)
canonical='''| คอลัมน์ต้นทาง | ฟิลด์ใน ERD ฉบับรวม | วิธีแปลง/จุดตรวจ |
|---|---|---|
| สาขา | `SOURCE_RECORD.raw_payload["สาขา"]` → `APPOINTMENT.branch_id` อ้าง `BRANCH` | เก็บ raw; trim ค่าค้นหา; ใช้ master ที่รับรอง ไม่ถือชื่อเป็นกุญแจถาวร |
| วันที่ | raw → `STAGING_CANDIDATE.proposed_value` → ส่วนวันที่ของ `APPOINTMENT.start_at` | แถว 2 ISO ชัด; 1/4/5 มี DMY/MDY; 3 ต้องยืนยันปี/ศักราช เก็บแต่ละ candidate แยกพร้อม evidence/rule_version; ไม่มี canonical instant ก่อนวันและ timezone ชัด |
| เวลา | raw → staging local time → `APPOINTMENT.start_at`, `APPOINTMENT.timezone_iana` | 10:00/13:30/09:00 parse เป็น local time ได้ แต่ยังไม่แปลง UTC; `end_at` ต้องมาจากการยืนยันหรือ policy ที่รับรอง ไม่เดาระยะเวลา |
| ชื่อคนไข้ | raw → staging name match key → `PATIENT.display_name`, `PATIENT_ALIAS.alias_text` | ใช้ Unicode NFC, trim/collapse whitespace, case-fold อังกฤษเฉพาะค่าค้นหา; เก็บต้นฉบับและไม่ลบเครื่องหมาย/วรรณยุกต์ไทย ไม่ตัด “คุณ”/ถอดเสียงเพื่อยืนยันตัวตนอัตโนมัติ; alias ต้องผ่าน review |
| เบอร์ | raw → staging phone digits/country/E.164 candidates → `CONTACT_POINT.normalized_value` โดย `channel=phone`; เชื่อม `PATIENT_CONTACT` | ลบเฉพาะขีด/ช่องว่างที่รู้ว่าเป็นตัวคั่น ตรวจอักขระอื่นแทนการลบทิ้งเงียบ ๆ; เก็บเป็น string: 1/2/5 = 0812345678, 4 = 0891112222; 3 เป็น missing/null โดย raw คงเดิม; country/rules รอยืนยัน ไม่ใช้เป็น patient unique key |
| หมอ | raw → `RESOURCE.resource_id` ผ่าน `APPOINTMENT_RESOURCE.resource_id` และ `role` หมอ | doctor_id ใน N4 คือ logical alias ของ resource_id ที่มี type เป็นหมอ ไม่ต้องเพิ่ม DOCTOR ที่ไม่มีความสัมพันธ์ใน ERD; ยืนยัน master และหมอเอข้ามสาขาก่อนผูกทรัพยากรเดียวกัน |
| บริการ | raw → `APPOINTMENT.service_id` อ้าง `SERVICE` | รับรอง crosswalk ของชื่อบริการ ไม่เติม duration/ราคา/จำนวนเก้าอี้จากชื่อ |
| หมายเหตุ | raw → `APPOINTMENT.note_optional`; hints ใน `STAGING_CANDIDATE` | เก็บทุกข้อความพร้อม source รวมทั้งเมื่อหลายแถวผูกนัดเดียว; ข้อความเรื่องซ้ำ/LINE/วันพุธใช้เปิด review; LINE ที่ยืนยันแล้วจึงสร้าง `CONTACT_POINT` channel=LINE พร้อม namespace; ไม่สร้างเวรจากข้อความทันที |

ฟิลด์ raw ทุกคอลัมน์อยู่ใน JSON payload ด้วยชื่อคอลัมน์เดิม ฟิลด์ `source.*`, `staging.*`, `appointment.local_date`, `local_start_time`, `starts_at`, `doctor_id`, `patient.aliases` และ `contact.phone_*` ในผล N4 เป็นชื่อแนวคิด/ค่าระหว่างแปลง: ตารางนี้ผูกกับ `SOURCE_RECORD`, `STAGING_CANDIDATE`, `APPOINTMENT.start_at`, `RESOURCE`, `PATIENT_ALIAS`, `CONTACT_POINT` ตามลำดับ จึงไม่ใช่ entity ที่หลุดจาก ERD `date_review_state`/`phone_review_state` ใช้ candidate resolution state และ decision; `migration_batch_id` ใช้ IMPORT_BATCH.batch_id; `import_record_id` ใช้ SOURCE_RECORD.source_record_id ซึ่งเป็น ID ที่สร้างตอน ingest แยกจาก stable ID ต้นทางที่อาจไม่มี
'''
n4=n4[:start]+canonical+n4[end:]
n4=n4.replace('กำหนด unique import operation key จาก batch/snapshot + import record + mapping/decision version','กำหนด source idempotency key จาก source namespace + artifact hash + row index (หรือ stable source ID/version เมื่อมี); กำหนด unique import operation key จาก source key + mapping/normalization/decision version โดย batch ใหม่ลำพังไม่ทำให้สร้าง target ใหม่')
body+=n4
body+='''
## Gap Analysis

| Gap และหลักฐาน | ความต้องการใน To-Be/Migration | ผู้รับผิดชอบที่เสนอ / เงื่อนไขผ่าน |
|---|---|---|
| Sheet แยกสาขา + LINE ตามบริบท | คิวกลางและ intake ที่มี source/request identity; ป้องกันจองพร้อมกันด้วย transaction | เจ้าของระบบ + เจ้าหน้าที่สาขา; ทดสอบจอง แก้ ยกเลิก และส่งคำขอซ้ำข้ามช่องทางแล้วได้ผลตาม policy |
| รูปแบบวันที่ 1/3/4/5 | raw/candidate/review แยกกันและ normalize เมื่อยืนยัน | เจ้าของข้อมูล; ประเด็นที่มีผลต่อ active appointment ต้องตัดสินพร้อมหลักฐาน |
| ชื่อ/เบอร์ต่างรูปแบบและ LINE ไม่มี ID | patient ID, aliases, shared contact, review matching | ผู้ดูแลทะเบียน; ยืนยัน linkage ของ 1/2/5 และตัวตน/ช่องทางแถว 3 โดยไม่สร้างค่าปลอม |
| แถว 1/2 ซ้ำและไม่มี stable IDs | แยก identity/appointment decisions, crosswalk, idempotent operations | ทีมย้ายข้อมูล; replay input เดิมไม่เพิ่ม patient/appointment และรักษา raw ทั้งคู่ |
| หมอบี 13:30 และหมอเอข้ามสาขา | ยืนยัน doctor master, เวร, duration/end, capacity, timezone และ exceptions | ผู้จัดคิว/ผู้จัดเวร; ตรวจชนคิวและ concurrent requests ด้วยค่าที่รับรองแล้ว ไม่ถือข้อสงสัยเป็นการชนที่ยืนยัน |
| หมายเหตุผสมข้อมูลหลายชนิด | note + review hints + contact/schedule ที่รับรองแล้ว | เจ้าของข้อมูล; ไม่มีข้อความสูญหายและไม่มี hint ถูกใช้เป็นกฎจริงโดยไม่ตรวจ |
| CSV ไม่มี updated_at/source change log | snapshot/delta reconciliation และ mutation ledger | ทีมย้ายข้อมูล + เจ้าของ source; ทุกรายการเปลี่ยนหลัง snapshot มี disposition ตรวจสอบได้ |
| ไม่ทราบวิธีทำงานจริง รายละเอียดระบบปลายทาง และสิทธิ์ผู้ใช้ | ยืนยัน As-Is ที่เป็นเส้นประ, integration mode และ role/access model | ผู้จัดการคลินิก + ผู้ดูแลระบบ; walkthrough/UAT ตามกระบวนการจริงและบัญชีผู้ใช้ที่ได้รับมอบหมาย |

## Roll-out Plan แบบผ่านเงื่อนไข

ไม่มีวันเริ่ม ระยะเวลา หรือสาขานำร่องที่ได้รับอนุมัติ ขั้นต่อไปเป็นลำดับเสนอ; ผู้รับผิดชอบทุกบทบาทต้องได้รับการแต่งตั้งจริง

| ระยะ | งานและความรับผิดชอบที่เสนอ | เกณฑ์ไปต่อ / ทางถอย |
|---|---|---|
| เตรียมความพร้อม | ผู้จัดการคลินิกยืนยันเจ้าของข้อมูล/ระบบและวิธีใช้ LINE; เจ้าของ source ยืนยัน convention/master/policy; ทีมระบบกำหนดสิทธิ์และ integration | ยังไม่เปิด active ถ้าค่าที่จำเป็นไม่ครบ; ใช้ source เดิมต่อและเก็บ review queue |
| ทดลองย้ายในสภาพแวดล้อมทดสอบ | ทีมย้ายข้อมูลทำ snapshot/staging/review และ reconciliation; เจ้าหน้าที่ทดสอบทั้ง 5 กรณีในตัวอย่าง รวม retry/แก้ version/rollback | raw ครบ 5 แถวพร้อม disposition ไม่ซ้อนกัน; ตรวจ field/lineage และทดสอบย้อนกลับได้; จำนวนคนไข้/นัดขึ้นกับ decision ไม่ตั้งยอดล่วงหน้า |
| ทดลองใช้งานสาขาที่คลินิกเลือก | ฝึกผู้ใช้ด้วยการจอง แก้ ยกเลิก ข้อมูลติดต่อไม่ครบ และคิวชน; ตรวจคิวหมอข้ามสาขาครอบคลุมสาขาที่ยังไม่ cutover | สาขาที่ยังใช้ Sheet ต้องมีช่องทางส่งการเปลี่ยนคิวและผู้รับผิดชอบตรวจข้ามสาขาที่รับรองได้ก่อนเปิดจริง; ถ้ารับรองไม่ได้ให้คงการทดลองแบบ shadow จนพร้อม ห้ามอ้างว่าคิวกลางรู้ทุกสาขาแล้ว |
| Cutover ตามขอบเขตที่อนุมัติ | เจ้าของระบบกำหนดจุดตัด; source owner freeze การเขียนหรือใช้ change log; ทีมย้ายข้อมูลรับ delta; เจ้าหน้าที่เก็บคำขอ LINE ระหว่าง freeze ในคิวที่ติดตามได้ | reconciliation และ walkthrough ผ่าน; ข้อค้างที่กระทบคิวในขอบเขตเปิดจริงต้องแก้ หรือมีเจ้าของและวิธีจัดการที่อนุมัติและไม่ทำให้นัดตกหล่น; source เดิมเปลี่ยน read-only หลังรับรอง |
| ขยายครบสามสาขา | ใช้ gate เดิมกับแต่ละขอบเขตที่เพิ่ม ทวน master/cross-branch และ train ผู้ใช้ | ขยายเมื่อเจ้าของงานรับรอง; ไม่เปิดให้เขียนสองแหล่งอย่างไร้การควบคุม |
| ดูแลหลังเปิดใช้ | เจ้าหน้าที่ติดตาม duplicate candidates, missing contacts, unresolved dates, conflicts และคำขอค้าง; ทีมระบบติดตาม reconciliation/audit | ค่ารับได้และช่วงติดตามให้คลินิกกำหนด; หากพบความคลาดเคลื่อนที่กระทบการใช้งาน ให้หยุด promote ขอบเขตนั้น รักษาคิวคำขอ แล้วให้ผู้รับผิดชอบตัดสิน reversal/แก้ไข |

Rollback ต้องอ้าง mutation ledger และ revision ไม่ restore snapshot ทับงานใหม่ หากกลับไปใช้ Sheet ต้องกำหนดแหล่งรับจองหลักอีกครั้งและนำคำขอ/แก้ไข/ยกเลิกที่เกิดหลัง cutover กลับให้ครบก่อนสลับ ห้ามปล่อยให้ LINE หรือสองระบบตอบยืนยันคิวขัดกัน การยังมี held record ไม่เท่ากับลบทิ้งนัดเดิม เจ้าหน้าที่ต้องติดตามนัดนั้นจนได้ข้อสรุป

## Plan Version Log

ชื่อ version ด้านล่างใช้ติดตามเอกสารในรันนี้ ไม่ใช่วัน deploy หรือ policy ที่คลินิกอนุมัติแล้ว

| Version | เหตุการณ์ที่เกิดในรัน | สิ่งที่เปลี่ยน / สถานะ |
|---|---|---|
| v1 | N1 DONE | บัญชีปัญหาและแถวกำกวมครบ; draft findings |
| v1.1 | N1b DONE | เพิ่ม candidate และหลักฐานวันในสัปดาห์; ไม่แปลงเรื่องค้างให้เป็นข้อเท็จจริง |
| v2-N2 / v2-N3 / v2-N4 | แต่ละ Node DONE อย่างอิสระ | As-Is, To-Be/model และ mapping/migration เป็นผลคนละสาย ไม่มี version ใดรับผลของอีกสาย |
| v3 | N5 รวมและตรวจความสอดคล้อง | เพิ่ม field crosswalk, note, operation/rollback ledger, แก้ optionality และ retry state ให้ตรงคำอธิบาย; เพิ่ม gap/roll-out และบันทึกเรื่องค้าง |

การเปลี่ยนครั้งต่อไปต้องบันทึก source/mapping/normalization/decision/policy version ที่เกี่ยวข้อง พร้อมผู้อนุมัติ หลักฐานและผลกระทบใน audit; ยังไม่มีการเปลี่ยนที่อ้างว่าได้รับอนุมัติจากคลินิก

## การตรวจผลงานและข้อจำกัด

ตรวจ JSON contract ของ N1/N1b/N2/N3/N4 ก่อนรับรวม ตรวจ coverage ของ 8 คอลัมน์และ 5 แถว ตรวจวันด้วย Python datetime ในเครื่อง และตรวจ Mermaid fenced blocks, เครื่องหมายคั่น, subgraph และชื่อ entity ที่ปลายความสัมพันธ์ทุกเส้นใน ERD ไม่มีการใช้เครือข่ายหรือการติดตั้งแพ็กเกจ ไม่พบ mmdc หรือ Mermaid parser ที่เรียกใช้ได้ จึงยังไม่ได้ยืนยันด้วย Mermaid renderer; การตรวจโครงสร้างจากข้อความไม่เท่ากับการ render สำเร็จ

รายละเอียดสมมติฐานราย Node เก็บใน contract ของ trace.md; สมมติฐานร่วมคือไม่มี convention/master/policy ที่ยืนยันเพิ่มเติม ไม่ใช้ข้อมูลนอก INPUT/N1/N1b มาเลือกค่ากำกวม และไม่ถือขั้นตอน As-Is ที่คาดขึ้นเป็นข้อเท็จจริง
'''
conflicts='''# 3. ข้อขัดแย้งที่พบและวิธีหาข้อสรุป

| ประเด็น | หลักฐานต้นทาง / ความต่างที่พบ | วิธีหาข้อสรุปและสถานะ |
|---|---|---|
| วันนัดแถว 1/4/5 และปีแถว 3 | CSV: “03/09/2026”, “09/03/2026”, “3 ก.ย. 69”; ISO “2026-09-03” อยู่แถว 2 | **ยังไม่ยุติ:** ไม่ตั้ง DMY/MDY หรือศักราชจากแถวอื่น; แถว 1 มี candidate ที่ได้รับแรงสนับสนุนจาก 2 แต่ต้องยืนยัน; เก็บ canonical ของวันแถว 2 ได้เท่านั้น |
| วันนัดกับวันเวรแถว 5 | “09/03/2026” และ “หมอเอมาช่วยสาขานี้ทุกวันพุธ”; datetime ให้ 9 มี.ค. 2026 = จันทร์ และ 3 ก.ย. 2026 = พฤหัสบดี | **ยังไม่ยุติ:** ทั้งสองการอ่านไม่ตรงพุธ; ไม่เลือกวันหรือแก้เวรเอง ต้องยืนยันวันนัด/เวร/ข้อยกเว้น |
| คนเดียวกันกับนัดเดียวกัน | “สมชาย ใจดี” / “Somchai Jaidee” และเบอร์เมื่อจัดรูปแบบตรงกัน; แถว 2 “จองซ้ำทางไลน์” แต่แถว 5 ต่างสาขา/เวลา/บริการ | **ยังไม่ยุติในข้อมูลจริง:** แยก patient decision และ appointment decision; 1/2 เป็นคู่ซ้ำต้องตรวจ, 5 เป็น identity candidate เท่านั้น ไม่ merge ตามเบอร์ |
| คิวชนหมอบี | แถว 3/4 “บางนา”, “13:30”, “หมอบี” ตรงกัน แต่วันกำกวมและไม่ให้ end/capacity | **ยังไม่ยุติ:** ตรวจหลังรับรองวันที่ หมอและpolicy ไม่ตัดสินว่า overbook หรือยกเลิกฝ่ายใด |
| สมมติฐาน As-Is กับการตรวจที่เสนอใน To-Be | INPUT ระบุเพียง “ใช้ Google Sheet แยกสาขา ร่วมกับจองผ่าน LINE”; ไม่ระบุว่ามีใครรับ/ตรวจ/ยืนยันอย่างไร | **ยุติการนำเสนอ:** ใช้เส้นประแสดงสมมติฐาน As-Is; ไม่ยก review/matching ของแผนใหม่ไปอ้างว่าเป็นงานเดิม ข้อเท็จจริงลำดับงานจริงยังรอยืนยัน |
| ชื่อฟิลด์ N4 ไม่ตรง ERD N3 | N4 ใช้ doctor_id, starts_at, contact.phone_* และ patient.aliases; N3 ใช้ RESOURCE, start_at, CONTACT_POINT, PATIENT_ALIAS; INPUT มีคอลัมน์ “หมอ”, “เวลา”, “เบอร์”, “ชื่อคนไข้” | **ยุติเชิงเอกสาร:** ทำตาราง semantic crosswalk เก็บทั้งชื่อแนวคิดและ entity ที่รองรับ ไม่เลือก schema ระบบจริงแทนคลินิก; รูปแบบ physical schema ยังไม่ยุติเพราะ INPUT ไม่ระบุ |
| note/audit/rollback ใน N4 ยังไม่ครบใน ERD N3 | INPUT มี “หมายเหตุ” และขอ “Data Mapping + แผน Migration”; N4 ต้องเก็บหมายเหตุและ mutation ledger แต่ ERD เดิมขาดฟิลด์แสดง note และ ledger | **ยุติด้วยการเติมข้อเสนอ:** เพิ่ม note_optional, IMPORT_OPERATION/IMPORT_MUTATION และ version metadata เพื่อให้แผนมีที่เก็บข้อมูลจริง รักษา raw “จองซ้ำทางไลน์”, “ไม่มีเบอร์ ติดต่อทางไลน์”, “ทุกวันพุธ” โดยไม่ตีความแทนมนุษย์ |
| ความสัมพันธ์บังคับกับ field optional ใน N3 | N3 อธิบาย draft และ deterministic mapping ได้ แต่เส้นเดิมบังคับ policy/master/reviewer; INPUT ไม่มี policy และแถว 3 ขาดเบอร์ | **ยุติความไม่สอดคล้องภายในแบบเสนอ:** ปรับ relation เป็น optional ตามสถานะ draft/held และ reviewer ตามวิธี resolve; active ต้องครบตาม policy ที่รับรอง ไม่อนุมาน mandatory phone จากข้อมูลว่าง |
| Idempotency N3/N4 คนละระดับ และ receipt ของงานค้าง | N3 ใช้ source key; N4 ใช้ operation/version; CSV ไม่มี appointment ID หรือ updated_at จึงไม่มีหลักฐานว่า snapshot ใหม่เป็นนัดใหม่ | **ยุติเชิงออกแบบ:** แยก source identity, versioned operation และ canonical mapping; retry คงผลเดิมหรือ resume state งานค้าง; เปลี่ยน version ตรวจ target revision ก่อน update ไม่สร้างซ้ำ; cross-snapshot matching ที่ไม่มี ID ยังต้อง review |
| ค่าเวร ระยะเวลา ความจุ timezone ประเทศเบอร์ และวิธี rollout | INPUT ไม่ระบุค่าเหล่านี้; “ทุกวันพุธ” ไม่มีช่วงเวลาหรือวันมีผล | **ยังไม่ยุติ:** ไม่เลือกค่าเริ่มต้นหรือกำหนดวันเปิดเอง; บันทึกเป็น readiness gate ให้ผู้รับผิดชอบรับรองก่อนใช้จริง |

ไม่มีผล Node ที่ถูกคัดทิ้ง ไม่มีการเลือกข้อสรุปธุรกิจที่หลักฐานไม่เพียงพอ การแก้ชื่อ/ความสัมพันธ์เป็นการทำให้ข้อเสนออ่านร่วมกันได้ ไม่ใช่การรับรองข้อมูลหรือกฎของคลินิก
'''
report=body+'\n'+conflicts
Path('output.md').write_text(report)
# Local structural checks, explicitly not a Mermaid parse/render claim.
mermaids=re.findall(r'```mermaid\n(.*?)\n```',report,re.S)
assert len(mermaids)==3
for diagram in mermaids:
 assert diagram.count('[')==diagram.count(']')
 assert diagram.count('{')==diagram.count('}') if diagram.startswith('flowchart') else True
 if diagram.startswith('flowchart'):
  assert len(re.findall(r'^\s*subgraph\b',diagram,re.M))==len(re.findall(r'^\s*end\s*$',diagram,re.M))
er=next(x for x in mermaids if x.startswith('erDiagram'))
entities=set(re.findall(r'^    ([A-Z_]+) \{',er,re.M))
relationships=re.findall(r'^    ([A-Z_]+) [|o{}.-]+ ([A-Z_]+) :',er,re.M)
assert relationships and all(a in entities and b in entities for a,b in relationships)
assert report.count('```')%2==0
assert all(c in report for c in ['สาขา','วันที่','เวลา','ชื่อคนไข้','เบอร์','หมอ','บริการ','หมายเหตุ'])
# Each node completion and merge event appended immediately after successful checks.
n5={'node':'N5','status':'DONE','output':report,'assumptions':['แบบจำลองและกลไกในฉบับรวมเป็นข้อเสนอ ไม่ใช่กฎที่คลินิกอนุมัติ','ผลลัพธ์นี้เป็นเอกสารแผน ไม่ใช่การย้ายข้อมูลจริง','ยังไม่ยุติเรื่องวันที่ ตัวตน คิวชน เวร และ policy ที่ INPUT ไม่รองรับ; ระบุผู้รับผิดชอบและ gate ไว้แล้ว','ตรวจ Mermaid แบบโครงสร้างเท่านั้น ไม่พบ renderer/parser ที่เรียกใช้ได้']}
Path('.nodes/N5.json').write_text(json.dumps(n5,ensure_ascii=False,indent=2))
with Path('trace.md').open('a') as f:
 f.write('\n```json\n'+json.dumps(n5,ensure_ascii=False,indent=2)+'\n```\n')
merge={'node':'N5','status':'DONE','output':{'event':'MERGE_COMPLETED','conflicts_and_resolutions':conflicts,'accepted_nodes':['N1','N1b','N2','N3','N4'],'missing_outputs':[],'checks':{'mermaid_blocks':len(mermaids),'erd_entities':len(entities),'erd_relationships':len(relationships),'mermaid_parser_run':False}},'assumptions':['เหตุการณ์นี้บันทึกผลรวม แยกจาก completion contract ของ N5; ไม่เปลี่ยนคำตัดสินข้อมูลที่ยังรอยืนยัน']}
with Path('trace.md').open('a') as f:
 f.write('\n```json\n'+json.dumps(merge,ensure_ascii=False,indent=2)+'\n```\n')
print('N5 DONE; output.md saved; N5 and MERGE_COMPLETED appended')
print('Structural checks:',len(mermaids),'Mermaid blocks;',len(entities),'ERD entities;',len(relationships),'relationships')
