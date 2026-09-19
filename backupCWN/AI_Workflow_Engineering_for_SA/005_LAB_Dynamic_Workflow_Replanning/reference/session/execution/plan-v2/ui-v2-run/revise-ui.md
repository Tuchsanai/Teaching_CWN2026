# Executor — revise-ui

TASK_ID: revise-ui; RUN_ID: ui-v2-run; PLAN: plan-v2; UTC: 2026-09-14T13:44:04.140341Z
**STATUS: EXECUTED — ส่งต่อ Evaluator verify-ui; ไม่ใช่ PASS.**

## Gates ที่ตรวจจริง

ตรวจเฉพาะรายชื่อ plan-v* ภายใน session ก่อนเริ่มและก่อนส่งต่อ: เลขสูงสุด v2 คู่ JSON/Markdown มีครบ ไม่มีรุ่นใหม่ค้าง. พบ revise-ui หนึ่งรายการ kind=revise/status=planned outputs สองไฟล์ตรงแผน; ไม่แก้ snapshot. ใช้ PLAN_READY/PASS จาก evaluations/plan-v2-review.md ซึ่ง hash คู่แผนและ impact ยังตรง สำหรับความสอดคล้องแผนที่ตรวจแล้ว ไม่รับรองแผนใหม่เอง.

- verify-fr: PASS เอกสาร; hash FR v2 และ producer execution ตรงผลตรวจ.
- verify-flow: PASS เอกสาร; F-01 closed; hash Flow/state/structure และ producer execution ตรงผลตรวจ.
- verify-test-outline: PASS เอกสาร; hash outline v2/FR/Flow และ producer execution ตรงผลตรวจ. สำเนา session outline/execution มีจริงตามผล transfer ที่ Evaluator อธิบาย ไม่ใช้ path source เดิมที่ล้าสมัย.
- ตรวจ hash bindings เป้าหมาย/producer ที่เกี่ยวข้อง 13 รายการใน 4 reports (3+2+4+4) ตรงก่อนผลิตและก่อนรายงาน. ไม่อ้างตรวจ manifest ทุกไฟล์หรือรับรอง chain นอกชุดตาม l-provenance.
- baseline session/ui-mockup.html เท่ากับ baseline-filtered-v2/ui-mockup.html SHA-256 d2b7bfa0cff5700d3ca07f611c03cfa0304c54eafb51387f125e95edd11f7803. Contract/provenance ผูกตาม hash ด้านล่าง. ไม่แก้ baseline/input/prompts.
- l-plan-gate/l-check-gates อนุญาต offline mock; l-real-scope/l-q-* ยัง BLOCKED เฉพาะการรับรองกฎ/ระบบจริง. l-browser เป็น gate ของ verify-ui/handoff รอบถัดไป; งานนี้ไม่มีผล browser และไม่ปลด gate นั้น.

## ผลงานจริงและการใช้ซ้ำ

สร้าง UI HTML ไฟล์เดียว 80,956 bytes >20000 เปิด file:// ได้ตามการออกแบบ ฝัง CSS/JS/seed ไม่มี CDN/fetch; คง CSP connect-src none และ img-src data เดิม. CSS และ mock-seed ตรง baseline ทุกไบต์. เก็บ script เดิมและเพิ่มเฉพาะ integration/render/state ใหม่ ไม่แทน baseline ด้วย UI เขียนใหม่. Handler submitOrder/choosePayment/confirmPayment/addItem/saveMenu/deleteMenu/saveMapping/slots/cashMessage/openMenu คง source เดิมที่เทียบแล้ว 10 ฟังก์ชัน; ไม่หมายถึง regression ผ่าน.

เพิ่มการทำไม่ได้ราย item, แจ้งลูกค้าทุกออเดอร์ที่มีปัญหาใน active session, เลือกเมนู/ตัวเลือกและ preview ก่อนเปลี่ยน, คืนรายการและบันทึก adjustment. คิวใช้รายการแทนจริง/ซ่อนรายการคืนจากสิ่งที่ต้องทำ; เก็บ item/order/payment snapshot เดิม. หน้าลูกค้า/หน้าร้านใช้ adjustedTotal ชุดเดียวกันแยกจาก original. payment/order/table state และ payment log ไม่ถูกเปลี่ยนจาก item resolution.

คง front-total เป็นราคา snapshot ตาม contract เดิม; เพิ่ม front-adjusted-total/customer-adjusted-total/resolution-order-total เป็นยอดหลังปรับ. ไม่เปลี่ยน selector เดิมเงียบ ๆ. คง data-order-id เฉพาะ outer order article ใน kitchen-queue/front-orders; child/button ใช้ data-id/data-item-id. Selector inventory แบบ literal ที่ตรวจ source คงครบ 77 รายการ; dynamic selectors/uniqueness/DOM จริงต้องรัน browser.

เพิ่มผู้จัดการตั้งช่วง/N/X จำลองและ route #/manager/capacity; ค่าเริ่ม 11:30–13:30/N=5/X=10. ใช้นาฬิกาที่แสดง +07:00 ตามคำสั่งรันเฉพาะ (แทนข้อเสนอ UTC ใน Flow/outline) และ confirmed_at ของ submit ที่สำเร็จ แบ่ง 15 นาทีเริ่ม 00/15/30/45. ไม่ใช้ timezone เครื่อง. ถึงเพดานแสดงครัวเต็มและป้าย X จำลองก่อนปุ่มส่ง; ไม่มี guard ปฏิเสธออเดอร์เพราะเต็ม. ค่า X กรอกเป็น fixture ไม่สร้างสูตรใหม่/ไม่ใช้แทน ETA US-07. Reset ล้างส่วนเพิ่มพร้อม seed เดิม.

## Mapping US → FR → Flow → UI

| US | FR | Flow | UI / ขอบเขต |
|---|---|---|---|
| US-01 | FR-01 | MRG-01<br>MRG-12 | table-select / btn-open-menu / menu-list (แทน QR จำลอง) |
| US-02 | FR-02 | MRG-01<br>MRG-04<br>MRG-12<br>MRG-13 | active-table / session-id / front-order[data-table-id] |
| US-03 | FR-03 | MRG-02<br>MRG-04<br>MRG-14 | order-mode / pickup-slot / takeaway-id / kitchen-order |
| US-04 | FR-04 | MRG-03<br>MRG-04<br>MRG-32<br>MRG-33 | option-<id> / item-total / replacement-option-<id> / replacement-preview |
| US-05 | FR-05 | MRG-05 | btn-status-next / customer-order-status; อิสระจาก item-state |
| US-06 | FR-06 | MRG-08<br>MRG-09<br>MRG-18 | menu-item-<id> / option-<id> / order-message / resolution-message; stock ตรวจตอนส่ง/เปลี่ยน |
| US-07 | FR-07 | MRG-03<br>MRG-04 | ข้อความเวลารอตะกร้า ยังประมาณไม่ได้; capacity-message ไม่ใช้แทน ETA |
| US-08 | FR-08 | MRG-03<br>MRG-04<br>MRG-06<br>MRG-07<br>MRG-10<br>MRG-11<br>MRG-32<br>MRG-33 | payment-status / pay-cash / pay-promptpay / cash-message / customer-adjusted-total / front-adjusted-total |
| US-09 | FR-09 | MRG-31<br>MRG-32<br>MRG-33 | btn-item-unavailable → customer-unavailable-alert + btn-change-menu / btn-return-item → ยอดปรับ |
| US-10 | FR-10 | MRG-04 | kitchen-order[data-order-id][data-received-at]; submitOrder เดิม |
| US-11 | FR-11 | MRG-05 | btn-status-next → status ภายใน front-order (สถานะอาหาร); F-01 runtime รอตรวจ |
| US-12 | FR-12 | MRG-08<br>MRG-18<br>MRG-19 | ingredient-select / btn-out-of-stock / menu-item-<id> / option-<id>; catalog แยก item pending |
| US-13 | FR-13 | MRG-09<br>MRG-20 | btn-restock; เปิดเฉพาะตามแมป ไม่มีการตัดสินใจแทนลูกค้า |
| US-14 | FR-14 | MRG-31<br>MRG-32<br>MRG-33 | item-resolution / item-state → replacement-preview / btn-change-menu / btn-return-item → kitchen item |
| US-15 | FR-15 | MRG-04<br>MRG-06<br>MRG-07<br>MRG-10<br>MRG-11<br>MRG-13<br>MRG-14<br>MRG-32<br>MRG-33 | front-order / front-payment-status / payment-log / front-adjusted-total; log เดิมไม่ถูกเปลี่ยน |
| US-16 | FR-16 | MRG-12<br>MRG-13<br>MRG-15<br>MRG-16<br>MRG-17 | front-table-select / btn-close-table / session-id; คืนรายการไม่ปิดโต๊ะ |
| US-19 | FR-19 | MRG-21<br>MRG-22<br>MRG-23<br>MRG-24<br>MRG-25<br>MRG-32<br>MRG-33 | menu-admin / admin-menu-price / front-total snapshot / item-adjustment-event / ยอดปรับแยก |
| US-20 | FR-20 | MRG-23<br>MRG-25 | mapping-* / btn-save-mapping / mapping-list; คง Q-20 อ้าง US-14 |
| US-21 | FR-21 | MRG-34<br>MRG-35 | nav-capacity / capacity-start,end,limit,wait-minutes / btn-save-capacity → capacity-message ก่อน btn-submit-order |
| US-25 | FR-25 | MRG-26<br>MRG-27<br>MRG-28 | role-* / staff-user,pin / auth-message / nav-* / account-*; เพิ่มสิทธิ์ route capacity เฉพาะ manager |
| US-26 | FR-26 | MRG-29<br>MRG-30 | CSP/offline single HTML จำลอง; ไม่มี UI ติดตั้งระบบจริง (NOT_TESTED) |

Mapping นี้อธิบาย implementation/ส่วนใช้ซ้ำ ไม่รับรองพฤติกรรม runtime หรือ AC; US-26 รองรับเพียง mock offline ไม่ใช่ระบบติดตั้ง.

## Locator และสัญญาทดสอบใหม่

ดู [ui-contract-v2.md](/root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/ui-contract-v2.md) ส่วน Selectors เพิ่มและ scope ที่บังคับ: ระบุ element/payload/ความหมายครบ รวม replacement-option-<option_id> และยอดปรับที่เป็น dynamic testid. รายชื่อหลัก: btn-item-unavailable, customer-unavailable-alert, item-resolution, replacement-menu, btn-change-menu, btn-return-item, nav-capacity, capacity-start, capacity-end, capacity-limit, capacity-wait-minutes, btn-save-capacity, capacity-message. รายชื่อเพิ่มเติม: customer-item-resolutions, customer-resolution-order, item-state, replacement-preview, resolution-message, resolution-order-total, customer-adjusted-total, history-adjusted-total, front-adjusted-total, refund-policy-note, item-adjustment-event, capacity-settings, capacity-setting-message, capacity-window. ใช้ scope order/article → item/testid ตาม contract; ไม่ใช้ data-item-id ลอย ๆ เพราะ li และ button อาจอ้าง item เดียวกัน.

## ตรวจเบื้องต้นจริงและสิ่งที่ยังไม่ได้รัน

ตรวจจริง: exclusive-create ป้องกันทับไฟล์; current plan/dependency bindings/baseline SHA; ขนาด HTML; exact CSS/seed/source functions; literal selector inventory เดิม; source scope data-order-id outer article; CSP และไม่พบ external request API ใน source. ตรวจ syntax ของ script ด้วย node --check ผ่าน exit 0 (stdin ในหน่วยความจำ ไม่มี browser/ไม่มี script execution). ทั้งหมดเป็น static/syntax เท่านั้น **ไม่ใช่ UI PASS**. ไม่มีการรัน tests/ui-check.py, Playwright, browser click/DOM/responsive/keyboard, ไม่สร้าง screenshot และไม่เขียน img/.

ส่งต่อ verify-ui ให้รัน baseline 19 checks และ extras ทุกข้อใน ui-contract-v2, test-outline-v2 V2-A–F, snapshot 5 ใบ, กรณี payment ทั้งสามสถานะ, F-01 สถานะอาหารลูกค้า/หน้าร้าน, catalog ทั้งจาน/เฉพาะตัวเลือก/คืน stock, session/role/direct route และ reset. รัน US-09/14 ชุด 5 จาก 5 แยกแต่ละ US ครอบสองทาง; จุดวัด 10 วินาที LAN แยกครัว→ลูกค้ากับลูกค้า→ครัว. US-21 N=5 สาม context/รอบที่ 12:00,12:15,12:30 พร้อม 4→5 ใบและยืนยันใบถัดไป; boundary 00/15/30/45 ต้องเพิ่มตาม outline ไม่ใช้ภาพ 3 ใบแทนผ่าน 3 จาก 3 รอบ.

NOT_RUN: regression ทั้ง 19, V2-A–F, ทุกชุด 5 จาก 5/3 จาก 3, browser/offline network interception/DOM/click/role/reset/responsive/ภาพ. NOT_TESTED: LAN/Wi-Fi/QR/หลายอุปกรณ์/โหลด/concurrency/สัดส่วนและวินาทีทุก AC, ETA/ข้อมูล 7 วัน/server log/security, Ubuntu/ติดตั้ง/ถอดอินเทอร์เน็ตระบบจริง, การชำระ/โอน/คืนเงินจริง. ไม่อ้างผล upstream 19/19 หรือผลเอกสาร PASS เป็นผล UI v2.

## ข้อค้างและสมมติฐาน

Q เดิม/หมายเหตุ ก./ค./ช., เสร็จแล้ว↔พร้อมเสิร์ฟ/aggregate/ETA, refund/ผู้อนุมัติ/ส่วนต่าง/คืนซ้ำ, X/เขตเวลา/รอยต่อ/นับคืน/เปลี่ยน N/นโยบายเมื่อเต็ม, Q-20 อ้าง US-14 และ Unknown permissions ยังคงเปิด. Offline mock ป้ายสมมติฐาน: จานละ 1, เมนูแทนใช้ราคาและตัวเลือกที่แสดงก่อนยืนยัน, คง order/item ID แล้วเพิ่ม revision, duplicate resolved เป็น no-op, returned ไม่ปิดโต๊ะ/ไม่เปลี่ยน order/payment; ช่วงวันเดียว [start,end), N จำนวนเต็มบวก, X จำนวนเต็มไม่ติดลบ, confirmed order รวมทั้งสองช่องทาง, คืน/เปลี่ยนไม่ลดยอดนับ. ตัวเลข 115→55/110 เป็น expected fixture ไม่ใช่ผลรัน. รายการรอไม่มี timeout ตัดสินใจแทน. ก่อนขอบเวลา 1 วินาทีไม่มีปุ่ม fixture รองรับ จึงยัง NOT_TESTED.

นโยบายคืนเงินจริงยัง BLOCKED; คำว่า คืนรายการแล้ว ไม่ใช่โอนเงินคืนแล้ว. ยังไม่สร้าง evaluator report/spec/observations และไม่เรียก agent/AI CLI เพิ่ม/เว็บ/reveal-2/README. ส่ง path ทั้งสี่ด้านล่างให้ Evaluator ใช้ต่อโดยไม่เรียกผู้ตรวจเพิ่มเอง.

## Plan/input hashes (SHA-256)

Input-set hash (absolute path+TAB+SHA256+LF เรียง path; 25 ไฟล์): `70b0f1d8630f3f4eead1a7e75bbb26453483945e037113ec1104ee892d06a4f7`.

| Path | SHA-256 |
|---|---|
| /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/004_LAB_Conditional_Graph_UI_Mockup/tests/ui-check.py | `1e6d6560924ad265e28fe67885eebeaeea44c5a1888055a944e474ee0cb37c45` |
| /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/input/reveal-1.md | `1fde792db1fdcf211be4a171fd88c61184ce892720832023fcaefad6a67f8917` |
| /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/prompts/02-executor.md | `2a0d15ee16677804a38bb3151869ba98119ae0799e8f1f6a9a1a1c8424d5b571` |
| /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/prompts/06-executor-ui-v2.md | `b7d58ea8bed5fb7c5cb1e93ae450f4bb654bd106a68914e2848e53f0e2f0d873` |
| /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/flow-v2-check.md | `8eb49dba6953c6d63a3eb833f54a67c74bad9b42978a83ea97408d21e18f8c1d` |
| /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/fr-v2-check.md | `b21ee2b862656cf871d69117c44d2d5168154360da088c929bf87e033151819b` |
| /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/plan-v2-review.md | `470d9248beca3760f63b1df7b54b5bcc24fc18cce5c1994ab3adebcf8403cd0e` |
| /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/plan-v2-validation.json | `a5b468a83cb2dde8ac5489f0c53214d28c68d41350cdd20e91e6a5c310bb25f3` |
| /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/evaluations/test-outline-v2-check.md | `0f982d0c0d6ee72264eca64f36bc6b0105edcaafab122f2d1654562d43cd3c2f` |
| /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/execution/plan-v2/flow-v2-run/revise-flow.md | `860a4f6b24b83172708864633dba4368771d76473c3f8dc11e7d975e9f84f0a7` |
| /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/execution/plan-v2/fr-v2-run/revise-fr.md | `571c4226e328461c807411303a66737876618d768bcbc19d261b76a32dfd745b` |
| /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/execution/plan-v2/outline-v2-run/draft-test-outline.md | `dc9e94d3e20a7bf904c846b0f5fa6a30f9422b7828963168fc652be1e51d9eb4` |
| /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/flow-v2.md | `8fe7983eb45a7222424c7fafe34adf78874da75e7e7cf3ab013d4955d1159f9c` |
| /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/fr-nfr-v2.md | `2cbdde11bb3fd5e62f338a1ea74f65d11112f3ea56e8a10ed9d24b08a1dcf0bb` |
| /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/impact-analysis-v2.md | `b4b5dcfbe1d03d1e31d59758b2a9476cecf00b65b0226914ac29f199894ecfb3` |
| /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/plan-v2.json | `8682dcba597fd36cadcf0a4724a9a75bd866f551b337281c663ee419c059c828` |
| /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/plan-v2.md | `75c5e9b06c7e26fbf7174295d165fbae64be57ea8ff807b4d96884898296ea2c` |
| /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/state-machine-v2.md | `efe13a4cbb843c056884478fa8e5a0ab201c9641a579ae355cedb07867218d0a` |
| /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/structure-v2.md | `f1a935fc0cf2779d225ce050a12b5df108c53a149fa0885ac7ce78828ae2290d` |
| /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/test-outline-v2.md | `50b3c1a7e68a5ca3a56cff2939f55cd591ae2c60c63bd3577625bc442dd2b763` |
| /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/ui-mockup.html | `d2b7bfa0cff5700d3ca07f611c03cfa0304c54eafb51387f125e95edd11f7803` |
| /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/provenance.md | `8059b1b47647d690ed7a73e6b4b9751e209edb3905868a4729269fb79330739a` |
| /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-contract.md | `294b660d2e39b3745344f225400eee57c02c25b6efb108a3a7ecce7cdd060e68` |
| /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-00-input/baseline-filtered-v2/ui-mockup.html | `d2b7bfa0cff5700d3ca07f611c03cfa0304c54eafb51387f125e95edd11f7803` |
| /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-03-reveal-1/reveal-1.md | `1fde792db1fdcf211be4a171fd88c61184ce892720832023fcaefad6a67f8917` |

## Outputs

| Output | SHA-256 |
|---|---|
| /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/ui-mockup-v2.html | `249b98c493f4c1347efe36f8be059095ede9d3b23b76ada3b022cfc416c2a1cc` |
| /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/ui-contract-v2.md | `40ad0ff84c423a225b1675bbc2a627390446b9ecfcbcbb4496a6f0605e675888` |

Execution report: /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/session/execution/plan-v2/ui-v2-run/revise-ui.md; summary: /root/workspace/CWN/Teaching/AI_Workflow_Engineering_for_SA/005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/execution.md. Summary บันทึก hash ของ report หลังเขียน; ไม่ใส่ self-hash วนกลับ. สร้างจริงเฉพาะ HTML, contract, execution report และ summary ตาม absolute paths ที่สั่ง; ไม่ทับเวอร์ชันเดิม/หลักฐานเดิม.
