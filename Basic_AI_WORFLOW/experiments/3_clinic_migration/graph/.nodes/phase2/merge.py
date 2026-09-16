import json,re,hashlib
from pathlib import Path
P=Path('.nodes/phase2'); OLD=Path('.nodes')
n={k:json.loads((P/(k+'.json')).read_text()) for k in ['N1','N1b','N2','N3','N4']}
prev={k:json.loads((OLD/(k+'.json')).read_text()) for k in n}
for k,d in n.items():
 assert set(d)=={'node','status','output','assumptions'} and d['status']=='DONE' and d['node']==k
 assert isinstance(d['output'],str) and isinstance(d['assumptions'],list)
assert n['N1']['output']!=prev['N1']['output']
assert n['N1b']==prev['N1b'] and n['N2']==prev['N2']
assert n['N3']['output']!=prev['N3']['output'] and n['N4']['output']!=prev['N4']['output']
base=(P/'output-before.md').read_text()
marker='(updated: change request)'
execution='''# 1. Execution trace ของการรันซ้ำครั้งนี้ (updated: change request)

## ตารางการรันซ้ำ (updated: change request)

| Node | รันซ้ำหรือไม่? (yes/no) | เหตุผล |
|---|---|---|
| N1 | yes | INPUT เพิ่ม PDPA consent และ LINE OA self-booking แม้ CSV ไม่เปลี่ยน จึงมี completeness findings ใหม่ |
| N1b | yes | ผล N1 เปลี่ยน ต้องตรวจใหม่; หลักฐานของค่ากำกวมเดิมไม่เปลี่ยน ผลลัพธ์จึงเท่าเดิมทุกประการ |
| N2 | yes | Dependency N1 เปลี่ยน ต้องประเมิน As-Is ใหม่; requirement อนาคตไม่เปลี่ยนหลักฐาน As-Is จึงคงผลเดิมทุกประการ |
| N3 | yes | Dependency N1 เปลี่ยน ต้องเพิ่มกระบวนการและ model ของ consent/LINE self-booking |
| N4 | yes | Dependency N1 เปลี่ยน ต้องเพิ่ม mapping/migration/rollback ของข้อมูลใหม่ |
| N5 | yes | ผล N3/N4 เปลี่ยน จึงรวมใหม่ตาม MERGE RULES หลังทุก dependency DONE |

ไม่มี Node ที่เข้าเงื่อนไข no ในรอบนี้: N1 เพิ่มช่องว่างความครบถ้วนที่มีผลต่อปลายทาง จึงทำให้ dependency ของ N2–N4 เปลี่ยนจริง การรันแล้วได้ผลเดิม (N1b/N2) แยกจากการ reuse โดยไม่รัน ไม่ได้แก้ผลเดิมเพื่อทำให้ดูเหมือนมีการเปลี่ยนแปลง

| Node | สถานะ | หมายเหตุ |
|---|---|---|
| N1 | DONE | ผลเปลี่ยน: เพิ่มข้อค้นพบที่มีที่มาจาก requirement ใหม่; findings CSV เดิมคงอยู่ |
| N1b | DONE | ประเมินหลัง N1 DONE; contract เท่าผลเดิมทุกไบต์ ไม่มีหลักฐานใหม่เลือกค่ากำกวม |
| N2 | DONE | รันหลัง N1/N1b DONE อย่างอิสระ; contract เท่าผลเดิมทุกไบต์ |
| N3 | DONE | รันหลัง N1/N1b DONE โดยไม่เห็น N2/N4; เพิ่ม consent/LINE flows และ model |
| N4 | DONE | รันหลัง N1/N1b DONE โดยไม่เห็น N2/N3; เพิ่ม mapping/onboarding/migration |
| N5 | DONE | รับเฉพาะ DONE contracts หลัง N2–N4 ครบ; รวมความต่าง ตรวจแผนภาพ และคงส่วนเดิมที่ไม่เปลี่ยน |

ไม่พบ Node FAILED และไม่ต้อง retry; ไม่มีผลงานขาด หยุดเมื่อ N5 DONE ข้อมูลหรือ policy ที่ยังรอยืนยันไม่ใช่ความล้มเหลวของ Node ในการจัดทำแผน ผลรันเดิมและ trace เดิมคงอยู่; เพิ่มบันทึกเฟส 2 ต่อท้ายเท่านั้น

'''
report=execution+base[base.index('# 2. ผลงานส่งมอบสุดท้ายที่รวมแล้ว'):]
report=report.replace('# 2. ผลงานส่งมอบสุดท้ายที่รวมแล้ว','# 2. ผลงานส่งมอบสุดท้ายที่รวมแล้ว '+marker,1)
report=report.replace('## ขอบเขตและหลักฐานต้นทาง','## ขอบเขตและหลักฐานต้นทาง '+marker,1)
insert='''### ข้อกำหนดเพิ่มจากเจ้าของคลินิก (updated: change request)

- “ต้องเก็บความยินยอมของคนไข้ตาม PDPA”
- “คนไข้ต้องจองคิวเองผ่าน LINE OA ได้”

CSV เดิมไม่เปลี่ยน ข้อกำหนดทั้งสองเป็นความต้องการของระบบเป้าหมาย ไม่มีหลักฐานว่าเป็นกระบวนการที่ใช้อยู่แล้ว ทุกส่วนที่เปลี่ยนทำเครื่องหมาย `(updated: change request)` ที่หัวข้อหรือข้อความที่แก้; ถ้า marker อยู่ที่หัวข้อ ให้รวมเนื้อหา ตาราง และ Mermaid ในหัวข้อนั้นด้วย เนื้อหา As-Is และข้อสรุปค่ากำกวมคงผลเดิม เอกสารออกแบบการเก็บและใช้หลักฐาน ไม่ถือว่าการมี consent table ทำให้ปฏิบัติตาม PDPA ครบแล้ว รายละเอียด policy/implementation ยังต้องรับรองตามบริบทจริง ไม่มีการใช้เครือข่ายในรันนี้

'''
report=report.replace('## Data Quality Findings — N1',insert+'## Data Quality Findings — N1 '+marker,1)
assert prev['N1']['output'] in report
report=report.replace(prev['N1']['output'],n['N1']['output'],1)
# N3: preserve phase-1 merger corrections while applying N3's independent phase-2 result.
new3=n['N3']['output']
new3=new3.replace('คืน receipt หรือผลเดิม\\nไม่สร้าง patient / appointment ซ้ำ','อ่าน receipt และ processing state\\nคืนผลที่เสร็จแล้วหรือ resume งานค้าง')
for field in ['patient_id','branch_id','service_id','start_at','end_at','timezone_iana','policy_version_id']:
 # Only in the core appointment block; canonical names remain as in phase 1, nullability is documented.
 a=new3.index('    APPOINTMENT {');b=new3.index('\n    }',a)
 block=new3[a:b].replace(field+'_optional',field)
 new3=new3[:a]+block+new3[b:]
new3=new3.replace('        string status\n        uuid policy_version_id FK','        string status\n        string note_optional\n        uuid policy_version_id FK',1)
new3=new3.replace('        string importer_version\n','        string importer_version\n        string mapping_version\n        string normalization_version\n',1)
new3=new3.replace('    IMPORT_BATCH ||--o{ SOURCE_RECORD : contains','''    IMPORT_BATCH ||--o{ SOURCE_RECORD : contains
    SOURCE_RECORD ||--o{ PATIENT_ALIAS : provenance
    SOURCE_RECORD o|--o{ RESOURCE_SCHEDULE : supports
    REVIEW_DECISION o|--o{ REVIEW_DECISION : supersedes
    IMPORT_BATCH ||--o{ IMPORT_OPERATION : runs
    SOURCE_RECORD ||--o{ IMPORT_OPERATION : processed_by
    IMPORT_OPERATION ||--o{ IMPORT_MUTATION : records''',1)
old3=base[base.index('## N3 — To-Be ที่เสนอ'):base.index('## Data Mapping และแผน Migration — N4 ที่รวมเข้ากับแบบจำลอง')]
a=old3.index('    IMPORT_OPERATION {'); b=old3.index('\n```',a)
ledger_entities=old3[a:b]
a=new3.index('\n```',new3.index('```mermaid\nerDiagram'))
new3=new3[:a]+'\n'+ledger_entities+new3[a:]
# Add fields missing from the independent model that are required by its narrative / N4 mapping.
new3=new3.replace('        string activity_scope\n','        int version\n        string activity_scope\n',1)
new3=new3.replace('        string evidence_state\n        uuid last_event_id_optional','        string evidence_state\n        string review_state\n        uuid last_event_id_optional',1)
new3=new3.replace('        datetime occurred_at_optional\n        datetime recorded_at','        datetime notice_presented_at_optional\n        datetime occurred_at_optional\n        datetime effective_at_optional\n        datetime recorded_at\n        int aggregate_revision\n        string interaction_id_optional',1)
new3=new3.replace('        string payload_template_ref\n','        string message_kind\n        uuid request_id FK\n        uuid purpose_version_id FK\n        string payload_template_ref\n',1)
extra_rel='''    LINE_SCOPE ||--o{ INTEGRATION_EVENT : receives
    BOOKING_REQUEST o|--o{ INTEGRATION_EVENT : correlates
    CONSENT_EVENT o|--o{ INTEGRATION_EVENT : records_decision
    BOOKING_REQUEST ||--o{ NOTIFICATION_OUTBOX : schedules_delivery
    PURPOSE_VERSION ||--o{ NOTIFICATION_OUTBOX : delivery_purpose
    LINE_ACCOUNT ||--o{ IDENTITY_EVENT : history
    PATIENT_ACCOUNT_LINK o|--o{ IDENTITY_EVENT : link_history
    AUTHORIZATION_GRANT o|--o{ IDENTITY_EVENT : permission_history
'''
new3=new3.replace('    PURPOSE ||--o{ PURPOSE_VERSION : versions',extra_rel+'    PURPOSE ||--o{ PURPOSE_VERSION : versions',1)
extra_entities='''    PATIENT {
        uuid patient_id PK
    }
    INTEGRATION_EVENT {
        uuid integration_event_id PK
        uuid line_scope_id FK
        string source_event_id
        string event_dedupe_key UK
        string event_type
        string authenticity_state
        string source_revision_optional
        datetime received_at
        uuid request_id_optional FK
        uuid consent_event_id_optional FK
        json raw_envelope_ref_and_hash
        string processing_state
    }
    IDENTITY_EVENT {
        uuid identity_event_id PK
        uuid line_account_id FK
        uuid link_id_optional FK
        uuid grant_id_optional FK
        string event_type
        int aggregate_revision
        string actor_ref
        string evidence_ref
        json before_after
        datetime occurred_at
        datetime recorded_at
        string event_idempotency_key UK
    }
'''
a=new3.index('### ER extension');p=new3.index('\n```',new3.index('```mermaid\nerDiagram',a))
new3=new3[:p]+'\n'+extra_entities+new3[p:]
# Keep the phase-1 explanation, changing only the now-split runtime audit design.
q=old3[old3.index('### ข้อกำกับแบบจำลองฉบับรวม'):].strip()
q=q.replace('### ข้อกำกับแบบจำลองฉบับรวม','### ข้อกำกับแบบจำลองฉบับรวม '+marker,1)
q=q.replace('การแก้ไขในระบบกลางหลัง cutover ต้องมีประวัติ version/before-after/reviewer เช่นกัน จึงใช้ ledger ที่อ้าง operation ของคำขอแก้ไขได้ โดย batch/source เก็บ request envelope ของระบบกลาง ไม่อ้างว่าเป็น Google source','การแก้ไขในระบบกลางหลัง cutover ใช้ BOOKING_REQUEST/OPERATION_AUDIT เก็บ version/before-after/actor; IMPORT_OPERATION/IMPORT_MUTATION ใช้เฉพาะงานย้ายข้อมูล ทั้งสองอ้าง canonical appointment เดียวกันตาม ID/version ไม่สร้าง import batch เทียมให้คำขอของคนไข้')
q+='''

(updated: change request) คงชื่อ canonical fields ของ APPOINTMENT จากฉบับรวมเดิม เช่น start_at และ patient_id; คำลงท้าย `_optional` ที่ N3 ใช้เป็นสัญลักษณ์ของ nullability ใน draft จึงแปลเป็น relation/constraint ตามสถานะ ไม่สร้างฟิลด์สองชุด IMPORT ledger และ canonical crosswalk ที่แก้ในเฟส 1 ยังคงอยู่

(updated: change request) เพิ่ม INTEGRATION_EVENT เป็น inbox ของเหตุการณ์ LINE ที่ตรวจ authenticity แล้ว/รอตรวจ แยก source event dedup ออกจาก BOOKING_REQUEST idempotency และ NOTIFICATION_OUTBOX delivery key เหตุการณ์เดียวต้องไม่ส่งผลหลายครั้ง ส่วนหลาย event อาจอ้าง request เดียว; เก็บ state เพื่อ resume หลังล้มเหลว มี link ไป consent event ได้เมื่อเกี่ยวข้อง ไม่บังคับให้ทุก webhook เป็นคำขอจอง

(updated: change request) IDENTITY_EVENT เก็บประวัติ link/relink/revoke และ authorization changes แบบมี revision/evidence; before/after ใช้ตรวจและ rebuild สิทธิ์ล่าสุดตอน cutover/rollback ไม่คืนสิทธิ์จาก snapshot เก่า การเปลี่ยน PATIENT_ACCOUNT_LINK/AUTHORIZATION_GRANT ต้องบันทึก event ใน transaction เดียวกัน event ที่อ้าง link/grant ต้องตรงกับ account ของ event; schema แบบเสนอไม่ได้กำหนดระยะเวลาเก็บถาวร

(updated: change request) CONSENT_EVENT เพิ่ม notice_presented_at/effective_at/aggregate_revision/interaction_id เพื่อรองรับหลักฐานการแสดง notice และลำดับการมีผลจาก N4; เวลาที่ไม่ทราบยัง null และห้าม backdate effective_at โดยไม่มีหลักฐาน POLICY/NOTICE/PURPOSE version ที่ใช้งานต้องอ้างเนื้อหาและการอนุมัติที่ตรวจย้อนหลังได้ เก็บ evidence ของการถอนแม้ยังไม่พบ grant เดิม พร้อมใช้ policy ที่รับรองจัดการ unknown

(updated: change request) ก่อนประกาศ slot ว่างต้องจัดการนัด legacy ที่ยัง held หากวันที่กำกวมทำให้ระบุช่วงทรัพยากรที่ได้รับผลไม่ได้ ให้คง resource/scope ที่อาจได้รับผลในสถานะยังไม่พร้อม self-booking จนผู้รับผิดชอบตรวจได้ ไม่อ้างว่า held เท่ากับไม่มีนัด และไม่เดาช่วงเวลา block ขึ้นเอง
'''
new3+='\n'+q+'\n\n'
a=report.index('## N3 — To-Be ที่เสนอ');b=report.index('## Data Mapping และแผน Migration — N4 ที่รวมเข้ากับแบบจำลอง',a)
report=report[:a]+new3+report[b:]
# N4: preserve merged canonical mapping rather than reverting to draft aliases.
new4=n['N4']['output']
a=base.index('| คอลัมน์ต้นทาง | ฟิลด์ใน ERD ฉบับรวม |');b=base.index('\nการแปลงเป็น E.164',a)
canonical=base[a:b]
a=new4.index('| คอลัมน์ต้นทาง |');b=new4.index('\nการแปลงเป็น E.164',a)
new4=new4[:a]+canonical+new4[b:]
new4=new4.replace('กำหนด unique import operation key จาก batch/snapshot + import record + mapping/decision version','กำหนด source idempotency key จาก source namespace + artifact hash + row index (หรือ stable source ID/version เมื่อมี); กำหนด unique import operation key จาก source key + mapping/normalization/decision version โดย batch ใหม่ลำพังไม่ทำให้สร้าง target ใหม่')
new4=new4.replace('## แผน migration ที่ตรวจสอบและย้อนกลับได้','## แผน migration ที่ตรวจสอบและย้อนกลับได้ '+marker,1)
newmap='''## ตารางเทียบฟิลด์ใหม่กับ ERD ฉบับรวม (updated: change request)

ตารางนี้ทำให้ชื่อแนวคิดที่ N4 เสนอมีที่เก็บใน model ของ N3 ไม่ได้เลือก physical schema ของระบบจริงแทนคลินิก; ส่วนที่เป็น policy ยังรอรับรอง

| แนวคิด/ชื่อใน mapping N4 | ที่เก็บใน ERD ฉบับรวม | ข้อกำกับ |
|---|---|---|
| purpose_id/version | PURPOSE / PURPOSE_VERSION | ID/version ที่รับรอง ไม่สร้างจากชื่อบริการ |
| legal_basis_config_id/version, processing_activity, policy | PROCESSING_POLICY.processing_policy_id/version/activity_scope | ไม่ใช่ consent event; scheduling ใช้ POLICY_VERSION แยกกัน |
| notice_id/version/content/hash | NOTICE_VERSION + NOTICE_PURPOSE | version ที่แสดงจริงและขอบเขต purpose; consent ไม่อนุมานจากการเปิดอ่าน |
| consent_event_id, decision, actor/on_behalf_of, channel | CONSENT_EVENT.patient_id/purpose_version_id/event_type/actor_kind/actor_ref/channel พร้อม AUTHORIZATION_GRANT เมื่อให้แทน | grant/deny/withdraw เป็นเหตุการณ์จริงเท่านั้น; authority/evidence ต้องตรวจได้ |
| notice_presented_at, occurred_at, effective_at, recorded_at, interaction_id | CONSENT_EVENT fields ชื่อเดียวกัน/optional ตามที่ทราบ | ไม่สร้างวันที่ยินยอมจากวันนัดหรือเวลา ingest |
| evidence_ref/hash และ authority evidence | CONSENT_EVIDENCE.artifact_ref/artifact_hash/provenance; AUTHORIZATION_GRANT.evidence_ref | source/ผู้ตรวจ/หลักฐานการมีอำนาจแทนแยกจาก identity contact |
| withdrawal_request_id, aggregate_revision, restriction state | CONSENT_EVENT.event_idempotency_key/interaction_id/aggregate_revision; PATIENT_PURPOSE_STATE + PROCESSING_POLICY | คำขอถอนและผลต้องเชื่อมตรวจได้; processing restrictions ประเมินตาม purpose/policy ที่รับรอง |
| unknown/missing/verified, review state | PATIENT_PURPOSE_STATE.state/evidence_state/review_state และ STAGING_CANDIDATE สำหรับคนไข้ที่ยังไม่ resolve | ไม่สร้าง PATIENT ด้วยตัวตนที่เดาเพียงเพื่อเก็บ state; legacy row ที่ค้างยังมี source review ได้ |
| line_scope_id/line_subject_id, account ownership | LINE_SCOPE, LINE_ACCOUNT.subject_identifier, AUTH_SESSION | scope ต้องมาจาก integration ที่รับรอง; session เป็นหลักฐาน authentication ของบัญชี ไม่ใช่การพิสูจน์ patient โดยตัวมันเอง |
| patient_link_id/revision/verified evidence | PATIENT_ACCOUNT_LINK.link_id/version + IDENTITY_EVENT | verification/revoke history แยกจาก CONTACT_POINT ที่แชร์ได้ |
| booking request, actor, patient link, payload/slot/version | BOOKING_REQUEST + AUTHORIZATION_GRANT + POLICY_EVALUATION | policy evaluations มีผลต่อ purpose นั้น ไม่ใช้ owner เพียงอย่างเดียวเป็นสิทธิ์ |
| result_ref, booking_state, appointment revision | REQUEST_RECEIPT, BOOKING_REQUEST.status/result_appointment_id, APPOINTMENT.version | receipt ใช้ดูผลเดิมหลัง timeout แต่ตรวจสิทธิ์ก่อนเปิดเผย |
| source_event_id/event_scope/received_at/revision | INTEGRATION_EVENT และ LINE_SCOPE | event inbox แยก logical request; request_correlation ใช้ request_id_optional |
| notification_id/outbox_id/delivery/attempt | NOTIFICATION_OUTBOX + DELIVERY_ATTEMPT | ข้อความเป็นผลหลัง commit; retry การส่งไม่เรียกสร้าง appointment |
| consent/link delta และ rollback history | CONSENT_EVENT + IDENTITY_EVENT; IMPORT_OPERATION/IMPORT_MUTATION; OPERATION_AUDIT สำหรับ runtime | แยกประวัติการย้าย การกระทำคนไข้ และสิทธิ์ล่าสุด; rollback ไม่คืน grant/link ที่ถูกถอนแล้ว |

'''
a=new4.index('## Onboarding และ self-booking')
new4=new4[:a]+newmap+new4[a:]
a=report.index('## Data Mapping และแผน Migration — N4 ที่รวมเข้ากับแบบจำลอง');b=report.index('## Gap Analysis',a)
report=report[:a]+'## Data Mapping และแผน Migration — N4 ที่รวมเข้ากับแบบจำลอง '+marker+'\n\n'+new4+'\n\n'+report[b:]
# Gap and rollout additions, preserve all earlier rows/gates.
report=report.replace('## Gap Analysis','## Gap Analysis '+marker,1)
gap='''### Gap จากข้อกำหนดเพิ่ม (updated: change request)

| Gap / หลักฐาน | สิ่งที่เพิ่ม | ผู้รับผิดชอบที่เสนอ / เกณฑ์ผ่าน |
|---|---|---|
| “ต้องเก็บความยินยอมของคนไข้ตาม PDPA” แต่ CSV ไม่มี evidence | Purpose/notice/policy versions, consent events/evidence/withdrawal และ state แยก unknown | ผู้รับผิดชอบด้านข้อมูลส่วนบุคคลของคลินิก; รับรอง policy และทดสอบ grant/deny/withdraw โดยไม่ fabricate grant จาก legacy |
| “คนไข้ต้องจองคิวเองผ่าน LINE OA ได้” แต่ไม่มี scoped identity/link | Authentication, verified patient link, authorization และ actor audit | ผู้ดูแล integration + ทะเบียนคนไข้; บัญชีผิดคนหรือถูก revoke ต้องดู/แก้/ยกเลิกไม่ได้ แม้รู้ appointment ID |
| self-booking ต้องเลือกคิวจากหลายสาขา | Slot availability, atomic reservation, request idempotency และ outbox แยกส่งข้อความ | ทีมระบบ + ผู้จัดคิว; concurrent booking ผ่านตาม capacity ที่รับรอง; retry/timeout ไม่เพิ่มนัด |
| consent/link/นัดอาจเปลี่ยนระหว่างย้าย | Event checkpoints/delta และ rollback ที่ไม่คืนสิทธิ์เก่า | ทีมย้ายข้อมูล + เจ้าของ policy; ตรวจถอนระหว่าง freeze/dispatch และ fallback ใช้ restriction ล่าสุดได้ |
| ประเด็นกฎหมายและวิธีเชื่อม LINE ไม่อยู่ใน INPUT | รายการ policy/implementation ที่ต้องรับรองก่อนใช้จริง | ผู้รับผิดชอบที่คลินิกแต่งตั้ง; ยังไม่เลือกฐานกฎหมาย retention เกณฑ์อายุ OA configuration หรือสเปก API โดยไม่มีหลักฐาน |

'''
report=report.replace('## Roll-out Plan แบบผ่านเงื่อนไข',gap+'## Roll-out Plan แบบผ่านเงื่อนไข '+marker,1)
roll='''### Gate เพิ่มสำหรับ PDPA และ LINE OA (updated: change request)

ใช้ร่วมกับทุกระยะในตารางเดิม ไม่ถือว่าผ่านเกณฑ์เดิมอย่างเดียวแล้วเปิด self-booking ได้

| ระยะ | งานเพิ่มและเกณฑ์รับรอง |
|---|---|
| เตรียมพร้อม | รับรอง purpose/notice/processing basis, ผล denied/withdrawn/unknown, access/retention และกรณีผู้แทน; รับรอง LINE scope/authentication/session/authorization และวิธีเชื่อมต่อจริง โดยไม่เลือก API หรือ OA account structure จาก INPUT |
| Dry run/UAT | Legacy ทั้ง 5 แถวไม่สร้าง grant หรือ verified LINE link เอง; ทดสอบ onboarding คนไม่มีเบอร์และเบอร์ร่วม; grant ต้องมี purpose/notice/evidence; ทดสอบถอนและตรวจสิทธิ์คนอื่น/ถูก revoke; optional purpose ไม่เป็นเงื่อนไขบังคับทุกการจอง |
| ทดลอง self-booking | ใช้ผู้ใช้และสาขาที่คลินิกเลือก; slot จริงต้องผ่าน scheduling readiness ทุกสาขาที่ใช้ทรัพยากรร่วม; ทดสอบสองคำขอแย่ง capacity สุดท้าย, retry/timeout, duplicate/out-of-order events, key เดิม payload ต่าง, reschedule ที่ล้มเหลวคงนัดเดิม, cancel และ stale version |
| Cutover | กำหนด writer authority ของ booking/consent/identity; รับ delta และ checkpoint รวม withdraw/revoke/cancel; LINE มีช่องรับคำขอที่ไม่สูญหายช่วง freeze และเจ้าหน้าที่ติดตามนัด held; ระงับกิจกรรมใน scope ที่ยังประเมินสิทธิ์/คิวไม่ได้ |
| เปิดใช้/ดูแล | ตรวจ appointment, receipt, outbox และ delivery แยกสถานะ; ทดสอบส่งไม่สำเร็จไม่จองซ้ำ; worker ตรวจผู้รับและ purpose ใหม่ก่อนส่ง; ไม่มีการรับรองข้อความ exactly-once โดยไม่มีหลักฐาน provider |
| Rollback/fallback | ทวน consent/link/cancellation events ที่เกิดหลัง snapshot ก่อนคืนบริการ; ไม่คืน withdrawn เป็น granted หรือ revoked link เป็น active จาก backup; fallback ต้องบังคับสิทธิ์ล่าสุดได้ มิฉะนั้นคงกิจกรรมนั้น hold และรับคำขอถอน/ยกเลิกต่อ |

ไม่มีการกำหนดวันเปิด ระยะ pilot จำนวนผู้ใช้ทดสอบ หรือเกณฑ์คะแนนใหม่ ตัวอย่างกรณีทดสอบเป็นคุณสมบัติที่ต้องตรวจตามข้อกำหนด ไม่ใช่รายงานว่าระบบจริงผ่านแล้ว

'''
report=report.replace('## Plan Version Log',roll+'## Plan Version Log '+marker,1)
version='''### ประวัติการเปลี่ยนในเฟส 2 (updated: change request)

| Version | เหตุการณ์ที่เกิดขึ้น | ผล/สถานะ |
|---|---|---|
| v4-N1 | N1 รันใหม่หลัง INPUT เปลี่ยน | เพิ่ม completeness gaps ของ consent, LINE identity และ booking runtime; CSV/findings เดิมคงอยู่ |
| v4-N1b / v4-N2 | รันใหม่ตาม dependency ที่เปลี่ยน | ตรวจแล้ว output/assumptions เดิมทุกประการ; ไม่ถือว่าเป็นการข้ามรัน |
| v5-N3 / v5-N4 | fan-out อิสระหลัง N1/N1b DONE | เพิ่ม To-Be/model และ mapping/migration; ไม่เห็นผลกันและกัน |
| v6 | N5 รวมเฟส 2 | คง corrections ของ v3; เพิ่ม consent/identity/event/delivery crosswalk และ ledger ที่ขาด; ปรับ gap/roll-out/conflicts พร้อม marker |

ผล contract เดิมไม่ถูกแก้; ผลใหม่อยู่ใน .nodes/phase2 และ trace เพิ่มท้ายตามจริง ไม่มี approval จากคลินิกหรือข้อมูลจริงที่อ้างว่าได้รับแล้ว

'''
report=report.replace('## การตรวจผลงานและข้อจำกัด',version+'## การตรวจผลงานและข้อจำกัด '+marker,1)
a=report.index('## การตรวจผลงานและข้อจำกัด');b=report.index('# 3. ข้อขัดแย้ง',a)
verification='''## การตรวจผลงานและข้อจำกัด (updated: change request)

ตรวจ contract ของ dependency ทุก Node ก่อนรวม และเปรียบเทียบผลเก่า/ใหม่: N1/N3/N4 เปลี่ยน ส่วน N1b/N2 เท่าเดิมทุกไบต์ ตรวจว่า trace เดิมเป็น prefix เดิมด้วย SHA-256 และไฟล์ contract เฟส 1 ไม่เปลี่ยน ตรวจ coverage CSV ครบ 5 แถว/8 คอลัมน์พร้อมข้อค้างเดิม และ mapping ใหม่มี entity รองรับ

เอกสารมี Mermaid 5 แผนภาพ: As-Is, To-Be intake, ER หลัก, LINE self-booking/consent flow และ ER extension ตรวจ fenced blocks, เครื่องหมายคั่น/subgraph และชื่อ entity ทุก relationship โดยรวม model หลักกับ extension ซึ่งใช้ entity เดียวกันเมื่อชื่อเหมือนกัน ไม่พบ Mermaid renderer/parser ที่เรียกใช้ได้ จึงยังไม่รับรองการ render; ไม่มีการติดตั้งแพ็กเกจหรือใช้เครือข่าย

ยังไม่ได้ตรวจข้อกฎหมายหรือสเปก LINE API ปัจจุบันจากแหล่งภายนอก ข้อมูลนี้ใช้เพื่อออกแบบแผนและระบุสิ่งที่ต้องรับรอง ไม่ใช่คำรับรอง PDPA compliance หรือผลทดสอบ integration จริง ส่วนค่ากำกวมของ CSV, master, timezone, duration, capacity และ policy ที่ค้างยังต้องยืนยันก่อนใช้งานตามกิจกรรมที่เกี่ยวข้อง

'''
report=report[:a]+verification+report[b:]
report=report.replace('# 3. ข้อขัดแย้งที่พบและวิธีหาข้อสรุป','# 3. ข้อขัดแย้งที่พบและวิธีหาข้อสรุป '+marker,1)
conflicts='''
## ข้อขัดแย้งและการเทียบผลเฟส 2 (updated: change request)

| ประเด็น | หลักฐานต้นทาง/ความต่างของผล Node | วิธีหาข้อสรุปและสถานะ |
|---|---|---|
| Requirement ใหม่กับ As-Is เดิม | “ต้องเก็บความยินยอมของคนไข้ตาม PDPA” และ “คนไข้ต้องจองคิวเองผ่าน LINE OA ได้” ไม่ได้บอกว่าคลินิกทำสองอย่างนี้อยู่แล้ว | **ยุติการนำเสนอ:** N2 ประเมินใหม่แต่คงผลเดิมทุกประการ ไม่เติม consent/self-booking ลง As-Is เป็นข้อเท็จจริง ส่วน N1 เพิ่ม gaps ตามเป้าหมายใหม่ |
| ต้องเก็บ consent แต่ CSV ไม่มีหลักฐาน | CSV มีเพียง 8 คอลัมน์เดิม; แถว 2 “จองซ้ำทางไลน์” และแถว 3 “ไม่มีเบอร์ ติดต่อทางไลน์” ไม่ใช่คำยินยอม | **ยุติหลักการย้าย:** คง unknown/missing ไม่ backfill granted หรือ denied; หลักฐานรายคนและ policy ที่ใช้จริง **ยังไม่ยุติ** ต้องได้จากแหล่งที่รับรอง |
| Consent กับฐานประมวลผล/เงื่อนไขใช้บริการ | Requirement กล่าวเพียงให้เก็บความยินยอม “ตาม PDPA” ไม่ระบุ purpose, ฐานกฎหมาย, retention, ผู้แทนหรือผลการถอน | **ยังไม่ยุติเรื่อง policy:** ไม่เลือกว่าทุกกิจกรรมต้องใช้ consent หรือห้ามบริการทั้งหมดเมื่อ unknown; แยก PROCESSING_POLICY ต่อ purpose และ consent events; ต้องรับรองค่าจริงก่อนใช้ |
| Shared contact ใน model เดิมกับบัญชีจองเอง | เดิมพบเบอร์ 1/2/5 ตรงกัน; ใหม่ต้อง “จองคิวเองผ่าน LINE OA” แต่ CSV ไม่มี scoped account/actor | **ยุติเชิงแบบจำลอง:** CONTACT_POINT คงเป็นข้อมูลติดต่อ ส่วน LINE_ACCOUNT/PATIENT_ACCOUNT_LINK/AUTHORIZATION_GRANT แสดง authentication/identity/สิทธิ์คนละเรื่อง; ข้อเท็จจริงว่าเป็นบัญชี/คนเดียวกัน **ยังไม่ยุติ** ไม่เลือกผู้ใช้จากเบอร์ |
| N4 ใช้ field aliases ที่ยังไม่ปรากฏใน ERD N3 | N4 ต้องเก็บ notice_presented_at/effective_at/aggregate_revision, inbox events และ identity history เพื่อถอน/revoke/delta; N3 มีคำอธิบายแต่ model ยังแสดงบางส่วนไม่ครบ | **ยุติเชิงเอกสาร:** เพิ่มฟิลด์/INTEGRATION_EVENT/IDENTITY_EVENT และตาราง crosswalk รวมกับ ledger เดิม เพื่อรองรับ requirement ทั้งสอง; ไม่เลือก physical schema/LINE API ที่ INPUT ไม่ระบุ |
| ชื่อ optional fields และ audit ของการย้ายกับคำขอ runtime | N3 เฟส 2 ใช้ start_at_optional และ patient_id_optional ขณะที่ฉบับรวมเดิมใช้ชื่อ canonical; มี runtime OPERATION_AUDIT เพิ่มจาก import ledger เดิม | **ยุติความหมาย:** คงชื่อ canonical เดิมและใช้ optional relation/status constraints; import ใช้ IMPORT_OPERATION/IMPORT_MUTATION, runtime ใช้ BOOKING_REQUEST/OPERATION_AUDIT อ้าง appointment เดียวกัน ไม่ลบ corrections เฟส 1 |
| Key ของ event/request/notification | N3/N4 อธิบาย retry ต่างชั้น; requirement ต้องให้คนไข้ self-book ผ่าน LINE OA แต่ไม่ให้ event semantics ของ provider | **ยุติแบบออกแบบ:** แยก inbox delivery dedup, logical booking idempotency และ outbox retry; commit จองครั้งเดียวตาม request และตรวจ availability atomically; การรับประกันการส่งข้อความ/API behavior **ยังไม่ยุติ** จนตรวจ implementation จริง |
| Rollback คืน snapshot กับการถอนความยินยอม/สิทธิ์หลัง snapshot | Requirement ให้เก็บความยินยอม; N4 ระบุ withdraw/revoke delta ต้องอยู่ต่อ ขณะที่แผนเดิมมีการคืน before-image ของ batch | **ยุติแบบออกแบบ:** เก็บ consent/identity events และ restrictions ล่าสุดไว้ ทวน revision ก่อน reversal; ห้าม snapshot คืน granted/active ที่ถูกถอนแล้ว กฎ retention/ผลถอนตามบริบท **ยังไม่ยุติ** |
| Held legacy กับ slot self-booking | วันที่ 1/3/4/5 ยังรอยืนยันและหมอบี 13:30 อาจชน; self-booking ต้องใช้คิวจริง | **ยุติ gate:** ไม่ประกาศว่างเพียงเพราะ held ยังไม่เป็น active; ต้องตรวจนัดเดิมให้ได้หรือจำกัด scope ที่ยังไม่พร้อม ไม่เดาช่วงเวลาบล็อกเอง |

ไม่พบหลักฐานให้เปลี่ยนข้อสรุปวันนัด ตัวตนและคิวชนเดิม จึงคงข้อค้างในตารางก่อนหน้าตามเดิม การเพิ่ม entity/field เป็นการทำให้ข้อเสนอรองรับ requirements ไม่ใช่การรับรองว่าระบบจริงใช้ schema หรือ policy นั้นแล้ว
'''
report+='\n'+conflicts
# Verification before marking N5 complete.
assert n['N1b']['output'] in report and n['N2']['output'] in report
assert canonical in report
assert all(x in report for x in ['## Gap Analysis','## Roll-out Plan','## Plan Version Log',marker])
diagrams=re.findall(r'```mermaid\n(.*?)\n```',report,re.S)
assert len(diagrams)==5
all_entities=set()
for d in diagrams:
 if d.startswith('erDiagram'):
  all_entities.update(re.findall(r'^    ([A-Z_]+) \{',d,re.M))
for d in diagrams:
 assert d.count('[')==d.count(']')
 if d.startswith('flowchart'):
  assert d.count('{')==d.count('}')
  assert len(re.findall(r'^\s*subgraph\b',d,re.M))==len(re.findall(r'^\s*end\s*$',d,re.M))
 if d.startswith('erDiagram'):
  for a,b in re.findall(r'^    ([A-Z_]+) [|o{}.-]+ ([A-Z_]+) :',d,re.M):
   assert a in all_entities and b in all_entities,(a,b)
assert report.count('```')%2==0
baseline=json.loads((P/'baseline.json').read_text())
t=Path('trace.md').read_bytes()
assert hashlib.sha256(t[:baseline['trace_bytes']]).hexdigest()==baseline['trace_sha256']
for k,v in baseline['node_hashes'].items():assert hashlib.sha256((OLD/(k+'.json')).read_bytes()).hexdigest()==v
Path('output.md').write_text(report)
n5={'node':'N5','status':'DONE','output':report,'assumptions':['(updated: change request) ทุก dependency DONE ก่อนรวม; N1b/N2 รันใหม่ได้ผลเดิมทุกไบต์ ไม่แก้ผลเก่า','(updated: change request) ไม่กำหนดฐานกฎหมาย/retention/LINE API สเปกหรือ policy ที่ไม่มีหลักฐาน; technical entities เป็นแบบเสนอ','(updated: change request) Unknown consent/link ไม่สร้าง grant หรือสิทธิ์ย้อนหลัง; CSV ambiguity เดิมยังต้องยืนยัน','(updated: change request) ตรวจ Mermaid แบบโครงสร้าง ไม่ได้ render; ไม่ใช้เครือข่าย/ติดตั้งแพ็กเกจ']}
(P/'N5.json').write_text(json.dumps(n5,ensure_ascii=False,indent=2))
with Path('trace.md').open('a') as f:f.write('\n```json\n'+json.dumps(n5,ensure_ascii=False,indent=2)+'\n```\n')
merge={'node':'N5','status':'DONE','output':{'event':'MERGE_COMPLETED_PHASE2','conflicts_and_resolutions':conflicts,'accepted_nodes':list(n),'unchanged_output_nodes':['N1b','N2'],'skipped_reused_nodes':[],'changed_output_nodes':['N1','N3','N4','N5'],'missing_outputs':[],'checks':{'mermaid_blocks':len(diagrams),'model_entities':len(all_entities),'mermaid_parser_run':False,'prior_trace_prefix_unchanged':True}},'assumptions':['(updated: change request) เหตุการณ์ merge แยกจาก N5 completion; ไม่มีการเปลี่ยนข้อมูลจริงหรือรับรอง policy แทนคลินิก']}
with Path('trace.md').open('a') as f:f.write('\n```json\n'+json.dumps(merge,ensure_ascii=False,indent=2)+'\n```\n\n'+execution)
(P/'execution.md').write_text(execution)
print('N5 DONE; output.md updated; appended completion, merge event and new execution trace')
print('Mermaid blocks:',len(diagrams),'logical entities:',len(all_entities))
