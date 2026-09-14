# Evaluation — Dynamic Workflow รอบ 0

PHASE=evaluate; ROUND=0; Task=CHG-010; Owner=Evaluator; Decision=**STOP_WITH_GAPS**.

ข้อเปลี่ยน N=5 → N=3 ปรากฏตรงกันใน FR/Flow/UI และคง AC อื่นใน snapshot แต่หลักฐาน runtime ยังไม่ครบเกณฑ์ของแผน มี regression fail 1 กรณี และ scenarios ที่ผลิตไม่ตรงรูปแบบขั้นตอนของ runner จึงไม่ตัดสิน COMPLETE. หยุดตามข้อจำกัด pre-run round 0 ใน change-conditions.md; ไม่เปิด REPLAN หรือรอบแก้เอง ไม่ได้หยุดเพราะมีหลักฐานว่างบหมดหรือข้อเดิมไม่คืบ.

เอกสารนี้ใช้ชื่อไฟล์สั้นสัมพัทธ์จากขั้น `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/`; path ที่เริ่มด้วยรหัส LAB สัมพัทธ์จาก `AI_Workflow_Engineering_for_SA/` และ resolve `../../../` จาก cwd ขั้นนี้. ลิงก์ในเอกสารอ้างจากตำแหน่งเอกสาร.

## หลักฐานและขอบเขตการประเมิน

อ่าน [แผนรอบ 0](plan-round-0.md), [plan-v4](plan-v4.json), [impact](impact-analysis-change.md), [execution](round-0/execution.md), ชิ้นงานสี่ไฟล์ใน round-0, [tests.json](round-0/tests.json) และ [ui-run-meta.json](round-0/ui-run-meta.json). ใช้ [manifest](../change-baseline/manifest.md), snapshots FR/Flow/UI/scenario index ที่กำหนด, [conditions](../change-conditions.md) และแผนก่อนเปลี่ยน `005_LAB_Dynamic_Workflow_Replanning/reference/step-07-plan-v3/plan-v3.json` เป็น baseline/สายที่มา ไม่รับช่วงผลผ่านในประวัติ.

อ่าน [shared-tests-v2.json](../shared-tests-v2.json), [shared-tests-notes.md](../shared-tests-notes.md), [shared-test-baseline-dom.json](../shared-test-baseline-dom.json) และโค้ด `006_LAB_Test_Scenarios_Traceability/tests/run-scenarios.py` เพื่อวิเคราะห์ขอบเขตและ schema. การตรวจใน evaluate นี้เป็นการอ่าน JSON/source, เทียบ diff/รหัส และคำนวณ hash; ไม่รัน browser, runner หรือ adapter ซ้ำ ไม่อ่านผล Single หรือเอกสารปลายทางของ source index.

ตรวจ input_manifest ของ plan-v4 ตรงกับไฟล์ทั้ง 7 รายการ; hash ชิ้นงานสี่ไฟล์ตรง execution. HTML และ shared suite ตรง hash ที่ ui-run-meta ระบุ:

| หลักฐาน | SHA-256 ที่ตรวจได้ |
|---|---|
| round-0/fr-nfr-v3.md | 69f0dc70cee374b91cf1fd6fdddb245f0029d461a9e4977328b5b7093903968c |
| round-0/flow-v3.md | 83c307455aaf559dfff220369eeaad325f43b3ab9f0b43a00a8a5a9e1217646c |
| round-0/ui-mockup-v3.html | c5be50a922d4ebb498110cc4b30712571b0f3edebe44aa925d22e3afc9d14447 |
| round-0/ui-scenarios-v3.json | 89ac2c6a88dea6bd60d61de715b6de62129d26d6488de2a35fc9efd32be0243b |
| ../shared-tests-v2.json | 85cb7472f75ab962e7ea156d4b8fa220f397eb1cf5c635d77c669c5fcec21abc |
| round-0/tests.json | 2404e51b25d1ce0cc0b9054d67d6a2e46952cd200ca49bbe7b8bc36793b5c1e7 |
| round-0/ui-run-meta.json | 1dc0ddcef01f1ec8b1b0f6251ee41e311d7aa74eb3ed3282d25165c4cd0020e9 |

สอง hash ท้ายคำนวณใน evaluate เพื่อระบุไฟล์ที่อ่าน ไม่ใช่ hash รับรองอิสระจากผู้รัน. tests ระบุภาพ 19 ไฟล์และตรวจพบไฟล์ครบ; การประเมินนี้อ่านผล assertions และ error ของ runner ไม่ได้อ้างตรวจภาพด้วยสายตา.

## ผล UI จริงและความหมายของ 3 รอบ

ผลจากผู้ทดลองภายนอก: **19 fixture mock cases — pass 18, fail 1, skip 0**. US-21 ผ่าน 6 กรณี; regression นอก US-21 ผ่าน 12 ตก 1 จาก 13 กรณี. ไม่ใช่การผ่านครบทุก AC หรือครบทุก scenario ที่ Dynamic ผลิต.

ui-run-meta ระบุใช้ shared-tests-v2.json ไม่ใช่ ui-scenarios-v3.json; browser=launch และไม่มี fallback. คำสั่งมี `--allow-fail` และโค้ด runner คืน exit 0 ได้แม้มี failed scenarios ดังนั้น exit_code=0 ไม่ใช่หลักฐานว่าผ่านทั้งหมด.

| รอบ fixture อิสระ | N−1: ตะกร้าถัดไปหลังส่ง 2 ออเดอร์ | N: ตะกร้าถัดไปหลังส่ง 3 ออเดอร์ |
|---|---|---|
| 1 | TS-US-21-101 PASS | TS-US-21-102 PASS |
| 2 | TS-US-21-103 PASS | TS-US-21-104 PASS |
| 3 | TS-US-21-105 PASS | TS-US-21-106 PASS |

แต่ละกรณีเปิด context ใหม่ตาม run_one และเริ่ม btn-reset แล้วตั้งช่วง 11:30–13:30, capacity-limit=3. กรณี N−1 จบด้วย expect_hidden ของ capacity-message หลังใส่ตะกร้าที่ยังไม่ส่ง. กรณี N จบด้วย expect_text “ครัวเต็ม” และ “รอประมาณ” หลังเตรียมตะกร้าใบถัดไป โดยยังไม่กดยืนยันใบที่ 4. จึงมีหลักฐานคำเตือนก่อนการยืนยันถัดไปเฉพาะลำดับนี้ 3/3 และการไม่เตือนที่ N−1 3/3; ไม่ใช่การรันครบ US-21 ทั้งชุดสามรอบ.

ชุดนี้ใช้โต๊ะเดิม ไม่ได้เปิด session ลูกค้าใหม่เพื่อยืนยันความหมาย “ลูกค้าใหม่” แยกต่างหาก; ไม่มี assertion ของ order count/confirmed_at โดยตรง, จำนวนจานหลายจานในหนึ่งออเดอร์, count=4, การคลิกหลังคำเตือน หรือข้อความ X/หน่วยนาที/ป้ายจำลองครบถ้วน. ทุกกรณี US-21 ตั้ง N=3 ทับหลัง reset จึงไม่พิสูจน์ค่าเริ่มต้น/reset คืน 3 ด้วย runtime. ไม่มีการข้ามรอยต่อเวลาในหกกรณีนี้.

**Failure ที่คงตามจริง:** TS-US-09-101, step 18, expect_text(testid=payment-summary-total, value=“0 บาท”) ล้มเหลวตอนตรวจ visibility: element(s) not found; timeout 2500 ms. ผลอยู่ใน tests.json และอ้าง [ภาพที่ runner บันทึก](round-0/shots/008-TS-US-09-101.png). Error snapshot มีข้อความยอดหลังปรับรายการ 0 บาทที่ส่วนอื่น แต่ไม่ทำให้ assertion ที่กำหนดผ่าน. UI source ทั้ง baseline และ v3 ไม่มี selector payment-summary-total; diff ไม่ได้แก้ส่วนคืนรายการ จึงมีหลักฐานความไม่ตรงกันของ selector กับ UI และยังไม่พิสูจน์ว่า N=3 ทำให้เกิด defect นี้. ห้ามลบ failure, เปลี่ยนเป็น PASS หรืออ้างว่าพิสูจน์ธุรกรรมคืนเงินจริงแล้ว.

## ตรวจข้อเปลี่ยนและ regression ตาม plan-v4

PASS_SOURCE หมายถึงตรวจเอกสาร/source ตรงเกณฑ์เท่านั้น; PARTIAL หมายถึงมีหลักฐานบางส่วน; NOT_MEASURED หมายถึงยังไม่มีการวัดพฤติกรรมที่ต้องการ ไม่ใช่ runtime fail ที่สร้างขึ้นใหม่.

| เกณฑ์ | ผลประเมิน | หลักฐานและช่องว่าง |
|---|---|---|
| CHG-AC-01 FR/Flow | PASS_SOURCE | fr-nfr-v3.md:44,133 เปลี่ยน N ทดสอบเป็น 3 คง 15 นาที, 00/15/30/45, 3 จาก 3 และข้อความก่อนยืนยัน; flow-v3.md:150,165 ใช้ fixture/AC N=3. ข้อห้ามเพิ่ม capacity rejection ระบุใน provenance ปัจจุบัน |
| CHG-AC-02 threshold/สิ่งที่นับ | PARTIAL | TS-US-21-101–106 ให้ผล N−1/N ข้างต้น; count>3, นับหลายจาน/การเปิดหน้า, count จริงและลูกค้าใหม่แยก session ยังไม่วัดครบ |
| CHG-AC-03 ยืนยันต่อเมื่อเต็ม | NOT_MEASURED | shared suite ไม่มีการส่งใบที่ 4 หลังเห็นคำเตือน ไม่มีผล enabled/click/new order/count=4. source ที่ไม่เพิ่ม hard block ใช้แทนหลักฐาน runtime ไม่ได้ |
| CHG-AC-04 ขอบหน้าต่าง | NOT_MEASURED | ไม่มีผลก่อน/ตรง 12:00,12:15,12:30,12:45,13:00 หรือการตัดออเดอร์หน้าต่างเก่า. การเริ่ม mock ที่ 12:00 ไม่ใช่การตรวจข้ามรอยต่อ 00 และไม่พิสูจน์ fixed แทน rolling window |
| CHG-AC-05 ครบสามรอบ | PARTIAL | มี threshold N−1/N สามรอบอิสระจริง แต่ไม่มีชุดครบคำเตือน/ยืนยันต่อ/ขอบเวลาสามรอบตามแผน จึงยังไม่ผ่านเกณฑ์รวม |
| CHG-AC-06 seed/reset/configuration/X | PARTIAL | UI:305 และ :498 เป็น 3; shared suite ใช้ฟอร์มตั้ง 3 ได้. reset คืน 3, เปลี่ยน N ค่าอื่น, สลับบทบาทหลังมี count และ X/ป้ายจำลองครบถ้วนยังไม่มีผลตรงเกณฑ์ |
| CHG-AC-07 คง AC/ID | PASS_SOURCE เฉพาะ snapshot | แถว US/FR/NFR เท่ากันตรงตัวหลังอนุญาตเฉพาะ N ทดสอบ US-21; มี 21 US,21 FR,17 NFR รวม NFR-V2-09/14. ลำดับ MRG/MOD/SCR/C-V2 และ data-testid/data-action เท่าเดิม; ความครบของ legacy scenario IDs ยังพิสูจน์ไม่ได้ |
| CHG-AC-08 regression offline | FAIL / มีส่วนยังไม่วัด | regression 12 PASS,1 FAIL ตามตารางด้านล่าง; ไม่ครอบคลุมทุกเส้นทางและทุกจำนวนตัวอย่างตาม AC |

Diff ทั้งไฟล์แยกจาก runtime: FR เปลี่ยนหัว/provenance, หัวตาราง, แถว US-21, FR-21 และที่มา N. Flow เปลี่ยนหัว/provenance, fixture และแถว AC US-21; ไม่มี transition ใหม่. UI ต่างจาก baseline เพียงสี่บรรทัด 17,22,305,498: ป้ายรุ่น/สถานะ, capacitySeed.limit และคำอธิบาย N. ส่วน capacityWindow (:472–479), capacityNoticeHTML (:480–484), ตำแหน่งคำเตือนก่อนปุ่ม (:348) และ submitOrder (:377 เป็นต้นไป) ใช้ source เดิม. confirmed_at และ floor นาทีหาร 15 เป็นเพียงข้อสังเกต source; ไม่อนุมาน PASS ของขอบเวลาหรือยืนยันต่อ.

| US | กรณี shared / ผลจริง | ขอบเขตที่สังเกตได้ |
|---|---|---|
| US-01 | TS-US-01-101 PASS | menu-list มองเห็น |
| US-02 | TS-US-02-101 PASS | front-orders มีโต๊ะ 02 |
| US-03 | TS-US-03-101 PASS | คิวมีสั่งกลับบ้านและ 12:30 |
| US-04 | TS-US-04-101 PASS | ยอดรายการ 60 และตัวเลือกไข่ในคิว |
| US-05 | TS-US-05-101 PASS | สถานะลูกค้าเป็นกำลังทำ |
| US-06 | TS-US-06-101 PASS | ส่งตะกร้าแล้วแสดงข้อความหมด |
| US-08 | TS-US-08-101,102 PASS | ข้อความเงินสด/ค้างจ่าย และยังไม่จ่าย→จ่ายแล้วตาม fixture |
| US-09 | TS-US-09-101 FAIL | selector ยอดหลังคืนไม่พบใน step 18 |
| US-11 | TS-US-11-101 PASS | หน้าร้านเห็นกำลังทำ |
| US-12 | TS-US-12-101 PASS | customer-order-status เป็นรับออเดอร์ตาม fixture |
| US-14 | TS-US-14-101 PASS | คิวมีรอลูกค้าตัดสินใจ |
| US-25 | TS-US-25-101 PASS | ข้อความปฏิเสธและซ่อน screen-manager |
| US-07,10,13,15,16,19,20,26 | NOT_MEASURED เป็นเกณฑ์ราย US | ไม่มี case ที่ระบุ US เหล่านี้โดยตรงใน shared suite; การถูกใช้เป็นขั้นตอนร่วมไม่รับรองทุก AC |

US-21 แสดงผลรายกรณีในตารางสามรอบด้านบน. ทุก PASS ในตาราง regression จำกัด assertions ของ fixture; ไม่รับรองเวลา LAN, จำนวนตัวอย่างเดิม, การคืน/เปลี่ยนครบสองทาง, stock restoration, ปิด/เปิดรอบโต๊ะ, จัดการเมนู/ภาพ/แมป, PIN lock หรือสิทธิ์ครบ matrix. NFR ระบบจริงด้าน Security/Load/LAN/Availability/Ubuntu/เงินจริง/ETA และข้อมูล 7 วันยังไม่มีหลักฐาน. คงเกณฑ์เดิมไว้ทั้งหมด.

## Schema ของ scenarios ที่ผลิตเทียบกับ runner

[ui-scenarios-v3.json](round-0/ui-scenarios-v3.json) parse เป็น JSON ได้ มี schema label dynamic-change-scenarios 1.0.0 และ 23 IDs ไม่ซ้ำ (CHG-SC-001–010, CHG-REG-001–013). source_refs เท่ากับ index baseline ทั้งสาม key/value. ทั้ง 23 กรณีคง NOT_TESTED, actual=null และ evidence ว่าง; เป็นสถานะ ณ execute ไม่ใช่ผล shared runtime ที่นำมาย้ายลงแทนกันได้.

โค้ด runner main รับ array หรือ object ที่มี scenarios เป็น array ของ object; รูปแบบระดับบนนี้รับได้. แต่ perform(page, step) ใช้ step.get('action') และต้องมี testid โดยรองรับเพียง click, fill, expect_text, expect_visible, expect_hidden; expect_text ต้องมี value. ในไฟล์ที่ผลิต steps ทั้งหมด **55 รายการเป็น string** ไม่มี action/testid ในแต่ละ step จึง **ไม่เข้ากันกับ runner โดยตรง**. หากส่งตรงให้ runner ตามโค้ด จะล้มที่ step แรกเมื่อเรียก .get บน string; ข้อนี้เป็นข้อสรุปจากการตรวจรูปแบบและโค้ด ไม่ใช่ผลรันเพิ่ม 23 failures.

runner ไม่แปลง procedures/expected/fixture/repetitions/repeat_protocol ให้เป็น actions หรือ assertions อัตโนมัติ; us ที่ผลิตเป็น array ก็ไม่มีการขยายเป็นผลราย US. ต้องมี mapping/adapter ที่ตรวจได้ก่อนใช้กรณีเหล่านี้. runner ไม่มี action สำหรับ adapter ตั้ง clock/เดินวินาทีที่ scenarios เสนอ จึงยังไม่มีหลักฐานขอบเวลา. การระบุ schema_version เองหรือ parse JSON ผ่านไม่เท่ากับผ่านสัญญา runner. tests.json ใช้ TS IDs จาก shared suite จึงไม่รับรองว่า CHG scenario ใดถูก execute แล้ว.

## ข้อจำกัดของ input และการควบคุมการทดลอง

Baseline ui-scenarios.json เป็น source index สาม path ไม่มีรายละเอียดเดิมหรือ case IDs. การคง source_refs พิสูจน์ได้เฉพาะการเก็บดัชนี; ไม่พิสูจน์รักษา legacy cases/coverage ครบ. shared-tests-notes ระบุ path docs/ui-contract.md ใน manifest ไม่มีจริง และมี snapshot สัญญา v2 อีกชื่อ; บันทึกเป็นข้อจำกัดการเตรียม input ตาม notes ไม่ใช้เป็นคะแนนประสิทธิภาพ workflow.

notes ระบุการตรึงชุดแรกหลังเริ่มเรียก AI แม้ก่อนอ่านชิ้นงานผล จึงไม่ตรงเงื่อนไขตรึงก่อนเรียกทั้งหมด. รุ่นใช้จริง shared-tests-v2 ตรึงที่ 2026-09-14T15:25:55.743727+00:00; แก้ setup US-21 จาก rush-start/rush-end เป็น capacity-start/capacity-end และเข้า nav-capacity ตาม baseline DOM. DOM evidence แสดงฟอร์ม capacity หลัง navigation; บันทึก setup attempt ที่ใช้ fill กับ select แล้วแก้เป็น select_option เป็นงานเตรียม fixture ไม่ใช่ผล scenario. ตาม notes ไม่เปลี่ยน expected หรือ regression นอก US-21; evaluate นี้ไม่อ่านผลอีกวิธีและไม่อ้างยืนยันการใช้ suite ของอีกวิธีเอง.

Flow fixture UTC กับ UI +07:00 เป็นข้อจำกัดเดิมที่ชิ้นงานระบุ; ไม่เปลี่ยนเขตเวลาเพื่อข้อเปลี่ยน N. pre-run หนึ่งคู่ไม่ใช่ค่าเฉลี่ย และไม่ควบคุมความแปรผันบริการ/แคช/ลำดับอ่านตาม conditions. ผลนี้ไม่ใช่ข้อสรุปเปรียบเทียบ Single กับ Dynamic.

## ช่องว่างที่ส่งต่อและ stop rule

| รหัส | ช่องว่าง | แนวทางที่ต้องมีหากผู้ทดลองเปิดงานใหม่ภายหลัง — ยังไม่ได้ทำ |
|---|---|---|
| CHG-GAP-01 | TS-US-09-101 FAIL | ตรวจสัญญา selector/ยอดหลังคืนกับ baseline และ fixture โดยรักษาผลเดิม; มีผลตรวจใหม่ที่แยกเหตุ UI หรือ test mismatch |
| CHG-GAP-02 | ยืนยันหลังคำเตือน/count=4/ลูกค้าใหม่ยังไม่วัด | เก็บ DOM ก่อนคลิกและ new order/count หลังคลิกใน session ที่ถูกต้อง ครบสามรอบ |
| CHG-GAP-03 | ขอบเวลา 00/15/30/45 และ fixed window ยังไม่วัด | เก็บ clock/confirmed_at/window/count ก่อนและตรงขอบ รวม 13:00 ผ่าน adapter ที่ระบุ override/hash ได้ ครบสามรอบ |
| CHG-GAP-04 | scenarios ไม่ตรง runner | แปลง string steps เป็น action/testid/value และ assertions พร้อมรองรับ repetitions/fixture โดยเก็บ traceability; ไม่อ้างว่าแปลงแล้วในรอบนี้ |
| CHG-GAP-05 | reset/X/การนับและ regression ยังไม่ครบ | เพิ่มหลักฐานตาม CHG-AC-02/06/08 และเกณฑ์เดิม แยก mock ออกจากระบบจริง |
| CHG-GAP-06 | input index/การตรึง suite ไม่ครบเงื่อนไข | เตรียมรายละเอียด scenarios และตรึงชุดก่อนเรียกในการทดลองใหม่; ไม่ย้อนหลังแก้ความหมายของรอบนี้ |

CHG-010 ประเมินเสร็จและหยุดด้วย STOP_WITH_GAPS; สถานะนี้เป็นการจบ phase evaluate ไม่ใช่การรับรองว่าข้อเปลี่ยนครบ. แผนเดิม → ข้อมูลใหม่ → งานเพิ่ม/แยก/ยกเลิก/จัดลำดับได้บันทึกไว้ใน plan-round-0/plan-v4/impact แล้ว; execution มีผลตาม dependency และ external tests มีจริง แต่หลักฐานยังไม่ผ่าน gate รวม. ไม่แก้ state ในแผน, คะแนน, ชิ้นงาน, tests หรือสถานะออเดอร์ และไม่สร้างรอบ 1/2.

## ต้นทุนที่ต้องนับ

สายงานที่มีหลักฐานถึงการเรียกนี้คือ plan round 0 + execute round 0 + evaluate round 0 รวม **3 phase calls**; การเรียกปัจจุบันนับ evaluate หนึ่งครั้ง ไม่เรียกผู้ช่วยหรือ AI CLI เพิ่ม. จำนวนนี้เป็นเฉพาะสาย phase ที่ทราบ ไม่แทนยอดรวมจาก log หากมีการเรียกซ้ำ/ล้มเหลวอื่น. ต้องรวมทุก plan/execute/evaluate/repair และ orchestration รวมงานอ่าน/ตรวจ/เขียนและเตรียม/รัน fixture ที่เกิดจริงตามประเภทต้นทุน ไม่ซ่อนเพราะหยุดหรือทดสอบตก.

เวลารวม AI calls, input/output tokens, cache usage, เงิน และงบคงเหลือ: **ไม่มีข้อมูลที่ยืนยันในการประเมินนี้**; ผู้ทดลองอ่าน log หลังจบเอง. เพดาน 3600 วินาทีและ 8000000 input+output tokens เป็นข้อจำกัด ไม่ใช่การใช้จริง. ui-run-meta.duration_s=16.257 เป็นเวลารันสคริปต์ UI ภายนอกที่บันทึกไว้เท่านั้น ไม่ใช่เวลา evaluate หรือเวลารวม workflow. เครื่องมือ/โมเดล/effort ตามการกำหนดรันของผู้ทดลอง ไม่ยืนยันชื่อโมเดลย้อนจากตัวโมเดล.
