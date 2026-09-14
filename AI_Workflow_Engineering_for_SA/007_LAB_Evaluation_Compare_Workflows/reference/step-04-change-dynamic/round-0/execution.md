# Execution — Dynamic Workflow / round 0

PHASE=execute; ROUND=0; Plan=plan-v4. สถานะ **EXECUTED_WAITING_EXTERNAL_TESTS** เป็นสถานะงาน AI; ไม่มีคำตัดสิน evaluate และไม่ได้เปลี่ยนสถานะออเดอร์เพราะข้อเปลี่ยนนี้.

ผลิตสี่ชิ้นงานพร้อมบันทึกฉบับนี้ตาม CHG-002 → CHG-003 → CHG-004 → CHG-005 → CHG-006 → CHG-007 → CHG-008. เปลี่ยนเฉพาะ N ทดสอบ US-21 จาก 5 เป็น 3 คงหน้าต่าง 15 นาทีเริ่ม 00/15/30/45, ข้อความ “ครัวเต็ม รอประมาณ X นาที” ก่อนยืนยัน และเกณฑ์ 3 จาก 3 รอบ. เมื่อเต็มยังยืนยันตะกร้าที่ถูกต้องได้; ไม่เพิ่มกฎปฏิเสธออเดอร์.

path เต็มในบันทึกนี้สัมพัทธ์จาก `AI_Workflow_Engineering_for_SA/`; จาก cwd ขั้นนี้ resolve `../../../` และจาก `round-0/` resolve `../../../../`. basename กับลิงก์ไฟล์คู่กันอ้างจาก round-0. ไม่มีการอ่านผล Single, ผลรอบอื่น หรือ markdown ปลายทางของดัชนี scenarios; ไม่ตามลิงก์ประวัติใน FR/Flow. ไม่แก้แผนหรือ baseline ไม่ใช้ work/ ไม่ใช้ git add/commit/push ไม่เรียกผู้ช่วยหรือ AI CLI เพิ่ม ไม่รัน browser และไม่เรียก phase ถัดไป.

## ลำดับงานที่ทำจริง

Owner ของทุกแถวคือ Executor ในการเรียกนี้; done หมายถึงผลิต/ตรวจ source ภายใน execute เท่านั้น ไม่ใช่ผ่าน AC runtime. inputs/outputs เต็มตาม plan-v4; ตารางย่อใช้ basename.

| Task | Dependency | Inputs ที่ใช้ | Outputs / หลักฐาน | State / stop rule ที่ใช้ |
|---|---|---|---|---|
| CHG-002 | CHG-001 | plan-round-0.md, plan-v4.json, impact-analysis-change.md, fr-nfr-v2.md | fr-nfr-v3.md | done; เปลี่ยน N และ provenance เท่านั้น |
| CHG-003 | CHG-002 | fr-nfr-v2.md, fr-nfr-v3.md | execution.md#CHG-003 | done; เทียบแถวเกณฑ์ก่อนส่ง Flow |
| CHG-004 | CHG-003 | flow-v2.md, fr-nfr-v3.md | flow-v3.md | done; คงรหัสและ transition |
| CHG-005 | CHG-004 | flow-v2.md, flow-v3.md, fr-nfr-v3.md, ui-mockup-v2.html | execution.md#CHG-005 | done; ตรวจสัญญาจำนวน/เวลาใน source และบันทึก gaps |
| CHG-006 | CHG-005 | ui-scenarios.json, ui-mockup-v2.html, fr-nfr-v3.md, flow-v3.md | ui-scenarios-v3.json | done; parse/mapping ก่อนผลิต UI |
| CHG-007 | CHG-006 | ui-mockup-v2.html, fr-nfr-v3.md, flow-v3.md, ui-scenarios-v3.json | ui-mockup-v3.html | done; แก้ตรงจุดและใช้ source เดิม |
| CHG-008 | CHG-002–CHG-007 | แผนสามไฟล์และชิ้นงานสี่ไฟล์ | execution.md | done; ตรวจ source, บันทึก hashes/diff/gaps แล้วหยุด |
| CHG-009 | CHG-008 | ชิ้นงานสี่ไฟล์และ execution.md | tests.json โดยผู้ทดลอง | waiting_external; ไม่ได้รันใน execute |
| CHG-010 | CHG-008, CHG-009 | แผน, ผล execute, tests.json | evaluation-round-0.md | waiting_external; ผู้ทดลองเป็นผู้เรียก |

## หลักฐาน input และรุ่น

อ่าน manifest, change-conditions, snapshot สี่ไฟล์ และแผนก่อนเปลี่ยนตาม path ที่กำหนด. แผนก่อนเปลี่ยนมี 13 งาน ใช้เป็นประวัติ dependency; ผลิตตาม scope snapshot 21 US และ CHG ของ plan-v4. ตรวจ SHA-256 ของ input 7 รายการตาม plan-v4 ก่อนผลิตและตรวจซ้ำหลังผลิต ได้ตรงทั้ง 7 รายการ. FR/Flow/UI/scenario index/แผนเดิมตรง manifest 5 รายการ; manifest และ conditions ใช้ hash ที่แผนรอบนี้บันทึก ไม่อ้างว่ามี authority hash ภายใน manifest ของสองไฟล์นี้.

| Input path | SHA-256 |
|---|---|
| `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/manifest.md` | `53a7bbb43f9024ebbe71f97f2f5acac80e5810bee67534dcc0a353d4ac0ab88f` |
| `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/fr-nfr-v2.md` | `2cbdde11bb3fd5e62f338a1ea74f65d11112f3ea56e8a10ed9d24b08a1dcf0bb` |
| `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/flow-v2.md` | `8fe7983eb45a7222424c7fafe34adf78874da75e7e7cf3ab013d4955d1159f9c` |
| `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/ui-mockup-v2.html` | `249b98c493f4c1347efe36f8be059095ede9d3b23b76ada3b022cfc416c2a1cc` |
| `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/ui-scenarios.json` | `171392ecc2b4dabcd45755552f378827c06616d012c71cc2174a93dcc9b27219` |
| `007_LAB_Evaluation_Compare_Workflows/reference/change-conditions.md` | `6d115d575eeaf179ea3427adaa3159bdd26f9ef45c076455c73f322d61a0cbe7` |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-07-plan-v3/plan-v3.json` | `2cc75857183b0fefd5f2631638442494dce2ff63436b8fa768ad5c2c13420125` |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/plan-round-0.md` | `0fdffd8b77d21b1f4407edd1651f028f5d6acb9cbe923cba515c12b046d1b88e` |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/plan-v4.json` | `aa21813391bdbd4b0a456ac84bdaf8f3eb63bb2a0024810b27e36ef69c668e07` |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/impact-analysis-change.md` | `49acf7e65de0b20afe2af9cc66e17df692b0821a7be7e8471944019a3e436c4f` |

ui-contract-v2.md ที่ manifest กล่าวถึงไม่ได้อ่าน เพราะไม่ใช่ dependency ที่ต้องเปิดเพิ่มใน execute. สถานะและ hash ของเอกสารประวัติที่ FR/Flow อ้างยังเป็นข้อความจาก snapshot ไม่ใช่การตรวจไฟล์ปลายทางหรือผลรอบนี้.

<a id="CHG-003"></a>
## CHG-003 — FR/NFR และ AC ที่ตรึงก่อน Flow

ใช้ Python อ่านไฟล์และเทียบทุกแถวที่ขึ้นต้นด้วย US-/FR-/NFR- รวมแถว traceability; แถวเท่ากันตรงตัวเมื่ออนุญาตเพียง `ทดสอบด้วย N=5` → `ทดสอบด้วย N=3` และ `เตรียมช่วงเร่งด่วนและ N=5;` → `เตรียมช่วงเร่งด่วนและ N=3;`. แถว US หลักยัง 21, FR 21 และ NFR 17; ลำดับและรหัสเดิมคงอยู่. NFR ทุกแถวและ AC อื่นเท่าเดิมทั้งข้อความ ไม่อาศัยจำนวนรหัสอย่างเดียว.

ตำแหน่งเปลี่ยนจาก `fr-nfr-v2.md` → [fr-nfr-v3.md](fr-nfr-v3.md):

| baseline line → output line | Diff ที่อนุญาต |
|---|---|
| 1–4 → 1–8 | หัว v3, TASK_ID CHG-002, phase/round/plan และสถานะปัจจุบัน; เพิ่มคำอธิบายข้อทดลองและประวัติ v2 |
| 18 → 22 | หัวตารางระบุว่าคง 21 แถวโดย US-21 เปลี่ยนเฉพาะ N ทดสอบ |
| 40 → 44 | US-21: N=5 → N=3 เพียงจุดเดียวในแถว |
| 129 → 133 | FR-21: N ใน AC และวิธีตรวจเป็น 3; ข้อความอื่นของแถวเท่าเดิม |
| 209 → 213 | แยก provenance ว่า N=3 เป็นโจทย์สมมติแทน N=5 ต้นฉบับ; X=10 ยัง fixture |

ไม่แก้ Q-V2-CAPACITY หรือคำถามธุรกิจอื่น; คำอธิบายต้นเอกสารระบุว่าคำสั่งทดลองไม่เพิ่มกฎปฏิเสธมีผลกับฉบับนี้ ข้อค้างเดิมไม่ใช่เหตุให้เพิ่ม hard block. ส่วนส่งต่อ/hash/ผลตรวจ v2 ด้านล่างคงเป็นประวัติ ไม่ใช่คำสั่งดำเนิน phase เพิ่ม.

<a id="CHG-005"></a>
## CHG-005 — Flow และสัญญาข้อมูลที่ใช้ซ้ำ

เทียบลำดับการปรากฏของ MRG, MOD, SCR และ C-V2 ด้วย regex ระหว่าง baseline กับ v3 แล้วเท่าเดิมทุกลำดับ. ตาราง coverage 21 US ใช้สร้าง mapping scenarios. ไม่มีการเพิ่ม transition หรือแก้สถานะออเดอร์/item/payment/table.

ตำแหน่งเปลี่ยนจาก `flow-v2.md` → [flow-v3.md](flow-v3.md):

| baseline line → output line | Diff ที่อนุญาต |
|---|---|
| 1 → 1 | ชื่อ v3 และ N ทดสอบ |
| 3–4 → 3–8 | TASK_ID CHG-004, phase/round/plan, สถานะปัจจุบัน และ authority v3; แยกเอกสารประวัติและ timezone fixture |
| 146 → 150 | fixture ก่อนมี 3/เมื่อมี 3; N=3 จากโจทย์สมมติแทน N=5 ในต้นฉบับ |
| 161 → 165 | AC US-21/FR-21 เปลี่ยนเฉพาะ N ทดสอบเป็น 3 |

ตรวจ source UI เดิมที่นำมาใช้ซ้ำ: `submitOrder` บันทึก `confirmed_at` เมื่อเกิดออเดอร์จริง; `capacityWindow` นับ `s.orders` ตาม timestamp ในช่วง `[start,end)` โดย floor นาทีหาร 15, ความยาว 15 นาที และ +07:00; `capacityNoticeHTML` แสดงเมื่อช่วงเร่งด่วน active และ count >= limit. ใน `customerHTML` คำเตือนอยู่ก่อนปุ่ม `btn-submit-order`; ปุ่มไม่มี disabled จาก capacity และ `submitOrder` ไม่มี capacity rejection. เงื่อนไขเดิมสำหรับ session ปิด, ตะกร้าว่าง/เมนูหรือตัวเลือกหมด, ราคาเปลี่ยน และช่วงรับหมดอายุคงอยู่.

นี่เป็นข้อสังเกต source ไม่ใช่ผลลำดับ DOM/click จริง. Clock UTC ของตัวอย่าง Flow กับ +07:00 ของ UI เป็นความต่างเดิม; เก็บไว้พร้อมป้ายสมมติฐาน และออกแบบกรณีรอยต่อใน +07:00 ของ UI. ไม่ตอบสูตร X/นโยบายคืน/เปลี่ยน/ข้ามวันเพิ่ม.

## CHG-006 — Scenario specification

[ui-scenarios-v3.json](ui-scenarios-v3.json) ใช้ schema `dynamic-change-scenarios` version `1.0.0`; เป็นข้อกำหนดกรณีทดสอบเชิงโครงสร้าง ไม่ใช่สคริปต์หรือ schema ของชุดร่วมที่ได้รับยืนยัน. มี 23 กรณี: CHG-SC-001–010 สำหรับข้อเปลี่ยน และ CHG-REG-001–013 สำหรับ regression; แต่ละกรณีมี id, US/FR/Flow/module/screen refs, preconditions, steps, expected, repetitions และสถานะ NOT_TESTED พร้อม actual=null/evidence ว่าง.

CHG-SC-001–010 ต้องรันทุกกรณีใน repetition 1/2/3 ด้วย initial state อิสระ; รอยต่อแต่ละเวลาแยก fixture. ชุดนี้ออกแบบ 3 รอบ แต่จำนวนรอบ runtime ที่ execute ทำจริงคือ **0**. สามออเดอร์ไม่ใช่สามรอบ. มี count=2/3/4, คำเตือนก่อนกดยืนยัน, ยืนยันต่อ, จำนวนจาน/ตะกร้า/เปิดหน้า, reset/configuration/role และรอยต่อ 12:00/12:15/12:30/12:45/13:00.

เก็บ object `source_refs` เท่ากับ index เดิมครบทั้ง customer/kitchen-front/manager และค่า path เดิมตรงตัว. ฐาน resolve ของอ้างอิงเดิมคือ `006_LAB_Test_Scenarios_Traceability/reference/step-00-input/` ตาม source ใน manifest; ไม่ย้ายไปอ้างจาก round-0 และไม่ได้เปิดสาม markdown ปลายทาง. ไม่มีหลักฐานว่าเก็บ legacy case IDs/coverage ครบ และไม่อ้างว่าสาม path นั้นเป็น executable suite.

รอยต่อก่อนหนึ่งวินาที/ตรงขอบต้องใช้ external fixture adapter: เปลี่ยนเฉพาะ seed.clock.initial ในสำเนาที่โหลดเข้าหน่วยความจำก่อน script เริ่ม และใช้ data-minutes ของปุ่ม advance เดิมเพื่อเดินหนึ่งวินาที. เอกสาร scenarios ระบุวิธีและข้อจำกัดโดยไม่ได้รัน adapter. ผู้ทดลองต้องบันทึก hash ชิ้นงานเดิม/fixture ที่แปลงและ override จริง; ถ้าชุดร่วมไม่รองรับให้ NOT_TESTED ห้ามปัดเวลาแล้วอ้างว่าตรวจตรงขอบ. ไม่เพิ่มช่องตั้งเวลา/API/เครื่องมือ debug ลง UI ส่งมอบ.

## CHG-007 / CHG-008 — UI และผล self-check

[ui-mockup-v3.html](ui-mockup-v3.html) เปลี่ยน 4 จุด:

| บรรทัดเดิม = บรรทัดใหม่ | Diff |
|---|---|
| 17 | ป้าย UI v2 → UI v3 พร้อมข้อทดลอง N=3 |
| 22 | สถานะรอ runtime v2 → รอผลตรวจภายนอกและ evaluate รอบ 0 |
| 305 | capacitySeed.limit: 5 → 3 |
| 498 | ข้อความค่าเริ่มต้น N=5 → N=3 |

Python ย้อน 4 replacements แล้วได้ source เท่า baseline ทุก byte เมื่อ encode UTF-8; ไม่มีการแทนเลข 5 ทั่วไฟล์. เปรียบเทียบลำดับ data-testid/data-action และ button calls เดิมได้เท่ากัน; JSON seed ส่วน mock-seed เท่าเดิม. reset ยัง clone capacitySeed, saveCapacity และ role switching ใช้ code เดิมทั้งหมด; X=10 และป้ายจำลองเดิมยังอยู่.

ตรวจด้วย Python `json.loads` ได้ทั้ง plan-v4 และ scenarios; ตรวจ unique scenario IDs, coverage 21 US ทุกแถวมีกรณีอ้างอิง และ source_refs เท่าดัชนีเดิม. ดึง inline JavaScript ไปยัง stdin ของ `node --check`: exit code 0 ไม่มี syntax error. คำสั่งนี้ตรวจไวยากรณ์เท่านั้น ไม่ execute JavaScript/DOM และไม่ได้เปิด browser. ไม่มีการรันชุดร่วม ไม่มี runtime observation หรือผล PASS ที่สร้างขึ้นใน phase นี้.

## Regression ที่ส่งต่อ

ทุกแถวเป็นการออกแบบจาก snapshot พร้อมการรักษา source; ยังไม่ใช่ผล runtime. จำนวนตัวอย่างและสัดส่วน AC เดิมใน FR/NFR ไม่ลดให้เท่าจำนวน fixture.

| US | กรณีที่ออกแบบ | ผล runtime / เหตุผล |
|---|---|---|
| US-01 | CHG-REG-001 | NOT_TESTED — ผู้ทดลองยังไม่ได้รันชุดร่วมใน phase นี้ |
| US-02 | CHG-REG-001 | NOT_TESTED — ผู้ทดลองยังไม่ได้รันชุดร่วมใน phase นี้ |
| US-03 | CHG-REG-002 | NOT_TESTED — ผู้ทดลองยังไม่ได้รันชุดร่วมใน phase นี้ |
| US-04 | CHG-REG-003, CHG-REG-007 | NOT_TESTED — ผู้ทดลองยังไม่ได้รันชุดร่วมใน phase นี้ |
| US-05 | CHG-REG-004 | NOT_TESTED — ผู้ทดลองยังไม่ได้รันชุดร่วมใน phase นี้ |
| US-06 | CHG-SC-004, CHG-REG-005 | NOT_TESTED — ผู้ทดลองยังไม่ได้รันชุดร่วมใน phase นี้ |
| US-07 | CHG-SC-010, CHG-REG-012 | NOT_TESTED — ผู้ทดลองยังไม่ได้รันชุดร่วมใน phase นี้ |
| US-08 | CHG-REG-003, CHG-REG-006, CHG-REG-007, CHG-REG-008 | NOT_TESTED — ผู้ทดลองยังไม่ได้รันชุดร่วมใน phase นี้ |
| US-09 | CHG-REG-006, CHG-REG-007 | NOT_TESTED — ผู้ทดลองยังไม่ได้รันชุดร่วมใน phase นี้ |
| US-10 | CHG-REG-004 | NOT_TESTED — ผู้ทดลองยังไม่ได้รันชุดร่วมใน phase นี้ |
| US-11 | CHG-REG-004 | NOT_TESTED — ผู้ทดลองยังไม่ได้รันชุดร่วมใน phase นี้ |
| US-12 | CHG-REG-005 | NOT_TESTED — ผู้ทดลองยังไม่ได้รันชุดร่วมใน phase นี้ |
| US-13 | CHG-REG-005 | NOT_TESTED — ผู้ทดลองยังไม่ได้รันชุดร่วมใน phase นี้ |
| US-14 | CHG-REG-006, CHG-REG-007 | NOT_TESTED — ผู้ทดลองยังไม่ได้รันชุดร่วมใน phase นี้ |
| US-15 | CHG-REG-002, CHG-REG-004, CHG-REG-006, CHG-REG-007, CHG-REG-008 | NOT_TESTED — ผู้ทดลองยังไม่ได้รันชุดร่วมใน phase นี้ |
| US-16 | CHG-SC-004, CHG-REG-001, CHG-REG-009 | NOT_TESTED — ผู้ทดลองยังไม่ได้รันชุดร่วมใน phase นี้ |
| US-19 | CHG-REG-003, CHG-REG-006, CHG-REG-007, CHG-REG-010 | NOT_TESTED — ผู้ทดลองยังไม่ได้รันชุดร่วมใน phase นี้ |
| US-20 | CHG-REG-005, CHG-REG-010 | NOT_TESTED — ผู้ทดลองยังไม่ได้รันชุดร่วมใน phase นี้ |
| US-21 | CHG-SC-001, CHG-SC-002, CHG-SC-003, CHG-SC-004, CHG-SC-005, CHG-SC-006, CHG-SC-007, CHG-SC-008, CHG-SC-009, CHG-SC-010 | NOT_TESTED — ผู้ทดลองยังไม่ได้รันชุดร่วมใน phase นี้ |
| US-25 | CHG-REG-011 | NOT_TESTED — ผู้ทดลองยังไม่ได้รันชุดร่วมใน phase นี้ |
| US-26 | CHG-REG-013 | NOT_TESTED — ผู้ทดลองยังไม่ได้รันชุดร่วมใน phase นี้ |

ข้อจำกัดที่ต้องส่งต่อเป็น gaps:

- ยังไม่มี tests.json ที่รันกับ hash ผลผลิตนี้, หลักฐานคำเตือนก่อนคลิก, การยืนยัน 3→4, ผลขอบเวลา หรือ repetition 1–3. Source/syntax ไม่ทดแทนหลักฐานเหล่านี้.
- ไม่ทราบ schema ของ shared runner; ต้อง mapping/adapter ตามข้อมูลจริง. Legacy markdown ยังไม่ได้อ่าน จึงพิสูจน์การรักษาทุกกรณีของชุดเดิมไม่ได้.
- UI ไม่มี public API สำหรับตั้งเวลาวินาที; boundary fixture ต้อง adapter ภายนอก. คำสั่ง session เก่าถ้าปุ่มถูกซ่อนและ runner เรียกไม่ได้ต้องระบุสาขานั้น NOT_TESTED; การเห็นหน้าว่างไม่พิสูจน์ server guard.
- Regression รูปภาพต้อง payload จริงของชุดร่วม; หากไม่มีต้องระบุ NOT_TESTED. การตรวจ DOM ในแท็บเดียวไม่พิสูจน์ LAN/โหลด/หลายเครื่อง/สัดส่วนตัวอย่างเดิม.
- Ubuntu installation, availability/offline ระบบจริง, security/auth/log จริง, สูตร ETA/ข้อมูล 7 วัน/ความแม่นยำ และธุรกรรมเงินจริงยังไม่มีหลักฐาน. X=10 และนโยบายคืน/เปลี่ยน/ขอบเขตเวลาเป็น mock assumptions เดิม.

## Hash ผลผลิตสำหรับผู้ทดลอง

| Output path | SHA-256 |
|---|---|
| `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/fr-nfr-v3.md` | `69f0dc70cee374b91cf1fd6fdddb245f0029d461a9e4977328b5b7093903968c` |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/flow-v3.md` | `83c307455aaf559dfff220369eeaad325f43b3ab9f0b43a00a8a5a9e1217646c` |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/ui-mockup-v3.html` | `c5be50a922d4ebb498110cc4b30712571b0f3edebe44aa925d22e3afc9d14447` |
| `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/ui-scenarios-v3.json` | `89ac2c6a88dea6bd60d61de715b6de62129d26d6488de2a35fc9efd32be0243b` |

ไม่ใส่ self-hash ของ execution.md; ผู้ทดลองคำนวณหลังไฟล์ปิดได้. ไม่มีไฟล์ tests.json หรือ evaluation ที่สร้างโดย execute.

## ต้นทุนและการหยุด

การเรียกนี้นับเป็น execute round 0 หนึ่ง AI call. มีหลักฐานการเรียก plan round 0 ก่อนหน้าจากเอกสารแผน; evaluate ยังรอผู้ทดลอง. ไม่มีการเรียกผู้ช่วย/AI CLI เพิ่มหรือเรียกตัวเอง. การตรวจและการเขียนทั้งหมดใน execute นี้เป็นงานภายใน call เดียว ไม่ใช่ phase evaluate แทรก; ต้นทุน orchestration รวมในต้นทุนของการเรียกด้วย.

เวลารวมจริง, input/output tokens, cache/usage และต้นทุนเงิน: **ไม่มีข้อมูล**; ผู้ทดลองอ่าน log หลังจบเอง ไม่ประมาณหรือแต่ง. ต้นทุนรวมต้องนับทุก plan/execute/evaluate/การแก้และ orchestration รวมกรณีล้มเหลว/หยุด; เพดานรวม 3600 วินาทีและ input+output 8000000 tokens ตาม conditions ไม่ใช่ยอดที่ใช้ไป. ข้อความนี้ไม่อ้างว่าตรวจว่างบคงเหลือพอแล้ว.

หยุดที่ execute round 0 ตาม CHG-008. รอผู้ทดลองรัน CHG-009 ด้วยไฟล์/hash ข้างต้นแล้วเรียก evaluate round 0 สำหรับ CHG-010. ไม่แก้ plan หรือรับช่วงผลผ่านเดิม; ไม่ตัดสิน COMPLETE/REPLAN/STOP_WITH_GAPS ใน execute. เงื่อนไข pre-run จำกัดรอบ 0; evaluator ต้องพิจารณา STOP_WITH_GAPS หากหลักฐานยังไม่ครบ แทนการเปิดรอบแก้เอง.
