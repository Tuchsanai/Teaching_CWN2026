# Evaluator — verify-ui / plan-v2

REVIEW_MODE: artifacts; TASK_ID: revise-ui; VERIFY_TASK: verify-ui; RUN_ID: ui-v2-review.
UTC รายงาน: 2026-09-14T14:00:55.172106Z. ผล **PASS เฉพาะเอกสารและชุด offline mock ที่รันตามขอบเขตครั้งนี้**; ไม่ใช่ผ่านทุกกรณีใน contract/outline หรือทุก AC ระบบจริง.
AC ระบบจริง **NOT_TESTED**; การยืนยันกฎที่ขาด **BLOCKED**. ตรวจ/รัน wrapper 1 ครั้ง; แก้ UI/แผน/สคริปต์เดิม 0 รอบ.

Path จากราก LAB: S=reference/session; B=reference/step-00-input/baseline-filtered-v2; E=reference/step-05-execute-v2; V=S/fr-nfr-v2.md; F=S/flow-v2.md; C=S/ui-contract-v2.md; H=S/ui-mockup-v2.html; O=S/test-outline-v2.md.
หลักฐานรวม: S/execution/ui-v2-evaluator-evidence.json (41 input hashes/126 เซลล์/12 dependency bindings); S/execution/ui-v2-observations.json (ผลจริงทั้งสอง checker, commands, hashes, UTC).

วิธีตรวจ: อ่านเฉพาะ inputs ที่อนุญาตและ reveal-1; SHA-256 จาก bytes; Draft7Validator+FormatChecker/UTC/unique IDs/DAG/cancel; ใช้ผล verify-plan ผูก hash สำหรับ JSON/Markdown/diff/ข้อจำกัดมนุษย์ ไม่ตรวจ baseline ทั้งชุดซ้ำ. รุ่นเลขล่าสุดคือ v2. เทียบ source→FR 21 US × 6 คอลัมน์ = 126 เซลล์ตรงทั้งหมด; reuse ผล FR/Flow/outline ที่ PASS และ hash target ตรง. ไม่เปิด README/reveal-2/เว็บ ไม่เรียก agent หรือ AI CLI เพิ่ม.

รันจริง `node reference/session/execution/ui-checks-v2.spec.js` ครั้งเดียว: Node v24.20.0 builtins wrapper เรียก Python checker เดิมและ corrected driver; ไม่ต้องติดตั้ง Node Playwright. เวลา UTC 2026-09-14T13:56:55.866Z ถึง 2026-09-14T13:58:45.807Z. Chromium 151.0.7922.34 (launch, ไม่มี CDP fallback); file://; reset และ context ใหม่ทุก execution; intercept/abort HTTP(S); TMPDIR/TMP/TEMP=S/browser-temp ก่อน launch; ไม่เปลี่ยน browser install/cache.

| ชุดตรวจ | ผล | หลักฐานจริง |
|---|---|---|
| baseline regression | PASS 19/19, exit 0 | S/execution/ui-v2-evaluator-runtime/regression.json; ทุก check และภาพแยก; ไม่ลด assertion |
| corrected feature driver | PASS 8/8, exit 0 | runtime/features/ui-feature-check-v2.json; 6 สถานการณ์ไม่ซ้ำ รวม capacity ซ้ำ 3 context |
| page/network ของ feature checks | PASS | page_errors=[] และ network_attempts=[] ทั้ง 8; regression ไม่มี offline violation; ไม่กล่าวว่าเก็บ console ทั้งระบบ |
| hash และ reuse | PASS | H canonical/session ตรงและไม่เปลี่ยนหลัง browser; contract ตรง canonical; dependency targets 12/12; rehash inputs 41/41 ก่อนเขียน |
| contract/testids เดิม | PASS ระดับ source + regression | C คัด baseline เป็น prefix ตรงทุก byte; selectors literal 77/77 คงอยู่; CSS/seed เดิมตรง; dynamic selector ทั้งหมดไม่ใช่สิ่งที่ inventory นี้พิสูจน์ |
| ข้อบกพร่อง assertion/UI ในชุดรันนี้ | ไม่พบ FAIL | ผล PASS จำกัด checks ที่รัน; รายการขาด coverage ด้านล่างคง NOT_TESTED |

ตารางทุก US: เอกสาร **PASS** ตาม source/FR/Flow/outline ที่ hash ตรง; mock **PASS เฉพาะ checks/ส่วนที่ระบุ** (ช่อง NOT_TESTED ยังคงไม่ผ่านการทดสอบ); **AC ระบบจริง NOT_TESTED ทุกแถว**. Locator V คือ US/FR line และ F คือ coverage line; รายละเอียดทุกคอลัมน์/ค่าตัวเลขเดิมอยู่ source และผล dependency ไม่เปลี่ยนเป็น fixture.

| US | V:US/FR → F:coverage | Mock checks / ขอบเขต | UI locator / ผลกระทบ |
|---|---|---|---|
| US-01 | 22/50 → 34 | table-menu | table-select → btn-open-menu → menu-list; QR จำลอง |
| US-02 | 23/51 → 35 | table-menu, close-table | active-table/session-id/front-order[data-table-id] |
| US-03 | 24/52 → 36 | takeaway-slot | order-mode/pickup-slot/takeaway-id; แยกช่วงรับจาก capacity |
| US-04 | 25/53 → 37 | option-price; replacement_reaches_kitchen | option-extra-egg/item-total; replacement-menu; ตัวเลือกแทนเพิ่มเติม NOT_TESTED |
| US-05 | 26/54 → 38 | status-sync | btn-status-next → customer-order-status ไม่ reload; LAN/5 วินาที/18 จาก 20 NOT_TESTED |
| US-06 | 27/55 → 39 | stock-whole, stock-option | order-message ปฏิเสธตะกร้าเก่า; ปิด catalog แยก pending item |
| US-07 | 28/56 → 40 | PASS เฉพาะป้ายข้อจำกัด; fullETA NOT_TESTED | ภาพ customer-capacity: ยังประมาณไม่ได้/ไม่มีค่าเฉลี่ย 7 วัน; X ไม่ใช่ ETA |
| US-08 | 29/57 → 41 | promptpay-slip, promptpay-disabled, promptpay-timeout-cash; return/replacement | payment-status/front-payment-status; customer-adjusted-total = front-adjusted-total |
| US-09 | 30/127 → 42 | unavailable_customer_return, replacement_reaches_kitchen | btn-item-unavailable → customer-unavailable-alert/สองปุ่ม → resolution-order-total; ชุด 5 จาก 5/LAN NOT_TESTED |
| US-10 | 31/58 → 43 | queue-order | kitchen-order[data-order-id][data-received-at]; หลายอุปกรณ์/โหลด NOT_TESTED |
| US-11 | 32/59 → 44 | status-sync | btn-status-next → สถานะอาหารใน front-order ใบเดียวกัน; F-01 ผ่าน mock; LAN NOT_TESTED |
| US-12 | 33/60 → 45 | stock-whole, stock-option, ingredient-mapping | ingredient-select/btn-out-of-stock/menu-item-m01/option-extra-egg; ช่องเพื่อยังปิด |
| US-13 | 34/61 → 46 | restock, ingredient-mapping | btn-restock → เมนู/ตัวเลือกเปิดคืนตามแมป; pending+restock เพิ่มเติม NOT_TESTED |
| US-14 | 35/128 → 47 | unavailable_customer_return, replacement_reaches_kitchen | item-resolution > item-state; kitchen-order scoped; item คืนถูกนำออกจากคิวที่ต้องทำ |
| US-15 | 36/62 → 48 | promptpay-slip, promptpay-timeout-cash, takeaway-slot; paid_return_keeps_payment_state | front-payment-status/payment-log คงเดิม; จ่ายแล้วไม่ย้อนสถานะหลังคืน |
| US-16 | 37/63 → 49 | close-table, reset | front-table-select/btn-close-table/session-id; table state แยกจาก item |
| US-19 | 38/64 → 50 | menu-management, return_uses_original_snapshot | front-total snapshot 50 แม้ catalog 99; adjusted 0; ชุด 5 ใบและรูป/ตัวเลือกครบ NOT_TESTED |
| US-20 | 39/65 → 51 | ingredient-mapping | mapping-menu/scope/ingredient/btn-save-mapping; คง Q-20 อ้าง US-14 |
| US-21 | 40/129 → 52 | capacity_n5_round_1/2/3 | capacity-start/end/limit/wait-minutes/message; N=5 ซ้ำ 3 context; 6 สถานการณ์รวมเป็น 8 executions |
| US-25 | 41/66 → 53 | roles, pin-lock, permission-denied, account-create | role-*/staff-user/staff-pin/auth-message; direct route เดิม /menu,/reports; /capacity deny NOT_TESTED |
| US-26 | 42/67 → 54 | NOT_TESTED การติดตั้ง; PASS เฉพาะเปิด offline HTML | file:// และ block HTTP(S); ไม่แทนการติดตั้ง/ตัดอินเทอร์เน็ตระบบจริง |

สถานะและยอด **PASS ในขอบเขตตรวจ**: H:402–470/C:175–181 แยก item queued/pending/replaced/returned จาก order รับออเดอร์/กำลังทำ/เสร็จแล้ว, payment ยังไม่จ่าย/ค้างจ่าย/จ่ายแล้ว, table/session และสถานะ task AI. Runtime คืนรายการคง order รับออเดอร์และ payment ยังไม่จ่าย; paid-return คงจ่ายแล้ว. Table return ไม่ปิดโต๊ะเป็น source review; ไม่อ้างทดสอบ session invariant ภายในครบ.
`front-total` H:366 มี label จริง **ยอด snapshot เดิม**; `front-adjusted-total` H:407–414 มี label **ยอดหลังปรับรายการ (จำลอง)**. คืน m01: snapshot 50 → adjusted 0 ทั้งลูกค้า/หน้าร้าน; เปลี่ยน m01→m02: snapshot 50 → adjusted 55; catalog แก้เป็น 99 ไม่เปลี่ยน snapshot 50. ไม่มีเหตุให้แก้ snapshot เดิม. คืนรายการไม่ใช่คืนเงินจริง; ป้าย refund-policy-note ระบุรอผู้อนุมัติ/ส่วนต่าง. F-01 status-sync ตรวจครัว→ลูกค้า→สถานะอาหาร front-order ใบเดียวกันจริง จึงปิดได้เฉพาะ mock; ไม่ใช้สถานะเงินแทน.

Visual **PASS เฉพาะภาพที่เปิดดูจริง** ผ่าน image viewer ใน session นี้: runtime/regression-shots/status-sync.png และ runtime/features/screen-v2-evaluator-{customer-alert,front-returned,customer-capacity,manager-capacity,mobile-customer-alert}.png. เห็นสองปุ่ม/สถานะรอ, ยอดเดิมแยกยอดหลังปรับ, X จำลองอยู่ก่อนปุ่มยืนยัน และฟอร์มผู้จัดการ. Desktop 1280×900; mobile 375×900 ตรวจ scrollWidth=375 เท่ากับ innerWidth=375; ภาพมือถือเห็นข้อความและสองปุ่มไม่ล้นใน panel ที่ตรวจ. Mobile scenario ตรวจ visibility/overflow แต่ไม่ได้คลิกสองปุ่มบน viewport มือถือ; keyboard/อุปกรณ์จริง NOT_TESTED. อ่าน E/ui-browser/visual-review.json เป็นหลักฐานเดิมประกอบ ไม่อ้างว่าได้เปิดทุกภาพในรายการเดิมหรือภาพเปรียบเทียบ v1 ในรอบนี้.

ประวัติ **PASS การรักษาหลักฐาน**: E/browser-regression เดิม 19/19; E/ui-browser/round-1 เดิม 7/8 เกิด strict-mode จาก global item-state; round-2 เดิม 8/8. ตรวจ script-revisions.json และ diff จริง: assertion เปลี่ยนเป็น `item-resolution.get_by_test_id("item-state")`, อีกสองจุดเปลี่ยน default run-dir/prefix. ไม่มี assertion ถูกลบ/UI เปลี่ยน; source script SHA 84d708bcfd8a36539ad1755fa2267824378166aead4011b3d2045e441dd769d4 → corrected 85a3cf688083e56d0f601a52b3fe2f3a2081bdd1a6c63cae4b034a860e2c30f1. ไม่แก้หรือทับ round-1/2. การแก้ locator เดิมหนึ่งรอบเป็นประวัติ; Evaluator รอบนี้ไม่เพิ่มรอบแก้.

| ข้อค้าง coverage | ผล | หลักฐาน/ข้อเสนอเฉพาะจุดสำหรับงานถัดไป |
|---|---|---|
| US-09/14 ชุด 5 จาก 5 แต่ละ US และ 10 วินาทีบน LAN | NOT_TESTED | O:50/C:204; driver มี return/replacement/snapshot/paid-return smoke ไม่ใช่สองชุด 5/5. ก่อนอ้างผ่าน AC ต้องเก็บสองจุดเวลาและ sample ตามต้นฉบับบนระบบจริง |
| US-21 รายละเอียด outline | NOT_TESTED เฉพาะส่วนขาด; N=5 ซ้ำ 3 รอบ PASS | driver check_capacity เริ่ม 12:00 ทุก context; round 1 ตรวจเปลี่ยนหน้าต่าง 12:15/12:30/12:45 แต่ไม่ได้ใส่ 5 ใบในหน้าต่างเหล่านั้น. O:67–69/C:206 ระบุ threshold ที่ 12:00/12:15/12:30. รายงานไม่อ้างว่าครบ outline; งานตรวจถัดไปเพิ่มเวลาเริ่มตามแต่ละรอบและหลายจาน/นอกช่วง/เปลี่ยน N/X/คืนกับจำนวน |
| V2-A–F ขั้นละเอียด | NOT_TESTED ส่วนที่ยังขาด | O:54–59/C:202: หลายรายการ/ออเดอร์ไม่ล่าสุด, ตัวเลือกแทน/stock หมดระหว่างเปลี่ยน, fixture 115→55/110, snapshot 5 ใบ, pending-payment คืน, log invariant/คืนเมนูแทน. ไม่ใช้ one-item smoke แทนชุดดังกล่าว |
| คืนซ้ำ | PASS เฉพาะปุ่มหาย; NOT_TESTED คำสั่งซ้ำภายใน | unavailable_customer_return พบปุ่มคืนไม่มีหลังคืน; ไม่มีการส่งคำสั่งซ้ำ/concurrency จึงไม่รับรอง idempotency |
| baseline contract extras / route ใหม่ | NOT_TESTED | C:200/206: รูป jpg/png/2 MB, ตัวเลือกครบขอบ 0–10, วันเปลี่ยน, วัตถุดิบซ้อน, keyboard และ direct-route deny /manager/capacity; permission-denied เดิมตรวจเพียง /manager/menu และ /manager/reports |
| fullETA/install/ระบบจริง | NOT_TESTED | US-07 สูตร/ประวัติ 7 วัน/สัดส่วนจริง; US-26 Ubuntu/สคริปต์ติดตั้ง/ถอดอินเทอร์เน็ตระบบจริง; LAN/Wi-Fi/QR หลายอุปกรณ์/โหลด/server log/production security/เงินจริงทุกชนิดไม่ได้ทดสอบ |
| กฎที่ต้องให้มนุษย์ตอบ | BLOCKED เฉพาะยืนยันกฎ/ระบบจริง | l-real-scope และ l-q-status/eta/payment/mapping/operations/environment/refund/capacity: ก./ค./ช., พร้อมเสิร์ฟ/aggregate, เงินคืน/ส่วนต่าง/ผู้อนุมัติ, สูตร X/นโยบายเมื่อเต็ม/นับคืน/เขตเวลา, Q-20/Unknown ยังคงเปิด |

ขอบเขตการรันเฉพาะครั้งนี้อนุญาต v2 ready for docs/mock เมื่อสอง checker ผ่าน จึงไม่ใช้ coverage ที่ยังไม่รันเป็นข้อกล่าวหาว่า UI เสีย และไม่อ้าง PASS ทั้ง contract. +07:00 เป็น fixture ตาม C:126 ต่างจาก UTC ที่เสนอใน F/O; เวลารันหลักฐานเป็น UTC จริง ไม่ตัดสินเขตเวลาของร้าน. หมายเหตุที่ขาดและช่อง US-12 คงเดิม.
Downstream: ปลด l-browser และ gate verify-ui เฉพาะเอกสาร/ชุด offline mock นี้ให้ evaluate-handoff; ส่งต่อ gaps และ l-real-scope/l-q-* ครบ. ไม่เปิด v3/reveal-2 ไม่แก้ plan snapshot. หากต้องเปลี่ยน scope/dependency ให้ Planner ออกรุ่นใหม่; coverage เพิ่มในงานเดิมให้สร้างสคริปต์/หลักฐานชื่อใหม่. FAIL ในชุดนี้ไม่มี; หากพบภายหลังให้แก้เฉพาะจุดไม่เกิน 2 รอบต่อปัญหา ไม่คืบหยุดพร้อมหลักฐาน (ข้อตกลงการเรียน ไม่ใช่ AC ร้าน).

| Plan/input/output hash | SHA-256 |
|---|---|
| S/plan-v2.json | `8682dcba597fd36cadcf0a4724a9a75bd866f551b337281c663ee419c059c828` |
| S/plan-v2.md | `75c5e9b06c7e26fbf7174295d165fbae64be57ea8ff807b4d96884898296ea2c` |
| H canonical/session | `249b98c493f4c1347efe36f8be059095ede9d3b23b76ada3b022cfc416c2a1cc` |
| C canonical/session | `40ad0ff84c423a225b1675bbc2a627390446b9ecfcbcbb4496a6f0605e675888` |
| Input-set 41 paths; path+TAB+SHA256+LF sorted | `c501d66b18468cc6097f4da66ae7aa31771209bc3b76a45dbd0e968afa464020` |
| S/execution/ui-checks-v2.spec.js | `5d3e348bda5e071cb35480afd30847ede3f7bb834130abff1b86a19d4d483934` |
| S/execution/ui-v2-observations.json | `bf16ddef9c6ab46303702cbb18e5a3f0fe1bb1c0c969bc511b47fba825cec941` |
| S/execution/ui-v2-evaluator-evidence.json | `fe9924ef5c94ca19994d45e78c18bbd436abb4fd934bce72361f32f74c06cb92` |

สร้างจริงก่อนรายงานนี้: spec, observations, evidence และ runtime JSON/log/meta/stdout/stderr/ภาพใน S/execution/ui-v2-evaluator-runtime; รายงานนี้เป็น output verify-ui. Output hashes ของรายงานอยู่ E/evaluation/evaluator.md; ไม่สร้าง self-hash.
