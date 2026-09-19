# Impact analysis — ข้อเปลี่ยน US-21 / round 0

สถานะ: วิเคราะห์และวางแผนแล้ว ยังไม่ได้ execute/evaluate ใช้ path สัมพัทธ์จาก `AI_Workflow_Engineering_for_SA/` resolve `../../../` จาก cwd ขั้นนี้ การเปลี่ยน N เป็นโจทย์สมมติเพื่อทดลอง ไม่ได้แก้ต้นฉบับ

## หลักฐาน input

| Path | SHA-256 ที่อ่านได้ |
|---|---|
| `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/manifest.md` | `53a7bbb43f9024ebbe71f97f2f5acac80e5810bee67534dcc0a353d4ac0ab88f` |
| `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/fr-nfr-v2.md` | `2cbdde11bb3fd5e62f338a1ea74f65d11112f3ea56e8a10ed9d24b08a1dcf0bb` |
| `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/flow-v2.md` | `8fe7983eb45a7222424c7fafe34adf78874da75e7e7cf3ab013d4955d1159f9c` |
| `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/ui-mockup-v2.html` | `249b98c493f4c1347efe36f8be059095ede9d3b23b76ada3b022cfc416c2a1cc` |
| `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/ui-scenarios.json` | `171392ecc2b4dabcd45755552f378827c06616d012c71cc2174a93dcc9b27219` |
| `007_LAB_Evaluation_Compare_Workflows/reference/change-conditions.md` | `6d115d575eeaf179ea3427adaa3159bdd26f9ef45c076455c73f322d61a0cbe7` |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-07-plan-v3/plan-v3.json` | `2cc75857183b0fefd5f2631638442494dce2ff63436b8fa768ad5c2c13420125` |


hash ของ FR/Flow/UI/scenario index และแผนเดิมตรง manifest 5/5 ส่วน manifest กับ change-conditions คำนวณเพื่ออ้างรุ่น ไม่มี hash authority ใน manifest ให้เทียบ ไม่ตามลิงก์ประวัติในเอกสาร ไม่อ่านผล single

## แผนเดิม → ข้อมูลใหม่ → งานเปลี่ยน

แผนเดิมมี producer/check แยกและ data-contract ระหว่าง FR กับ Flow เพื่อรองรับ 26 US ข้อมูลใหม่ในงานนี้ให้ใช้ snapshot 21 US และแก้ N ทดสอบ US-21 เท่านั้น จึงรักษาหลัก dependency และการตรวจซ้ำ แต่ย่อ outputs ให้ตรงงานสี่ชิ้นพร้อม execution แยกการตรวจอิสระไป evaluate หลังผลสคริปต์ภายนอก ตาราง mapping ครบทั้ง 13 task อยู่ใน plan-round-0.md และ plan-v4.json#/plan_diff

งานเพิ่ม: CHG-001 วิเคราะห์ข้อเปลี่ยน/ตรึง inputs, CHG-006 ออกแบบ threshold/boundary/หลักฐานสามรอบ, CHG-008 บันทึก execution, CHG-009 ผลสคริปต์ภายนอก งานแยก: ตรวจก่อนส่งต่อ CHG-003/005 และตัดสิน CHG-010 งานยกเลิกใน scope ทดลอง: การผลิตสัญญาข้อมูล/state/structure/UI contract/outline แยกไฟล์และงานเปิด US เพิ่ม; การตรวจสัญญาที่จำเป็นรวมใน Flow/scenarios จัดลำดับ FR → ตรวจ → Flow → ตรวจ → scenarios → UI → execution → script → evaluate

## จุดกระทบและขอบเขตใช้ซ้ำ

| ชิ้นงาน/หลักฐาน baseline | จุดเปลี่ยนที่วางแผน | ส่วนใช้ซ้ำ | ต้องตรวจใหม่ |
|---|---|---|---|
| fr-nfr-v2.md:40,129,209 | N ทดสอบใน US-21/FR-21, วิธีทดสอบ และ provenance ที่เคยกล่าวว่า N=5 มาจาก AC จริง | AC อื่น, 21 US/21 FR/17 NFR, traceability, คำถามเดิม | allowlist diff; คง 15 นาที/ขอบ/3 จาก 3/ข้อความก่อนยืนยัน; ระบุ N=3 เป็นข้อทดลอง |
| flow-v2.md:134–146,161 | fixture ก่อนมี 3 ใบ/เมื่อมี 3 ใบ และ AC US-21 | MRG-34/35, C-V2-01/02/03, MOD-12/02, SCR-17/03, MRG-03/04 | นับ confirmed orders ก่อนลูกค้าใหม่ยืนยัน; ไม่เพิ่ม capacity rejection/สถานะ |
| ui-mockup-v2.html:305,498 | capacitySeed.limit 5→3 และคำอธิบาย N=5→N=3 | layout, selectors, role, reset, setting form, capacityWindow/Notice และ submitOrder | reset/default/configuration, count 2/3/4, คำเตือนก่อน click และยืนยันต่อได้ |
| ui-mockup-v2.html:472–484 | ไม่มีเหตุให้เปลี่ยนอัลกอริทึมตามข้อเปลี่ยนนี้ | หน้าต่าง floor(mm/15), confirmed_at, count >= limit, X fixture | runtime รอยต่อ 00/15/30/45, ไม่เป็น rolling window, X มีป้ายจำลอง |
| ui-scenarios.json:1–5 | เพิ่มเนื้อหา scenario ที่ใช้กับ v3 ในไฟล์ใหม่ โดยเก็บ key/value index เดิมเป็น provenance | customer / kitchen-front / manager และค่า path อ้างอิงต้นทางเดิม | parse/schema, target round-0, traceability, 3 repetitions, regression และข้อจำกัด coverage |
| execution.md / tests.json / evaluation-round-0.md | ผลใหม่ตาม phase/เจ้าของที่ระบุ | ใช้แบบแยก producer/check ของแผนเดิม | provenance/hash/ผลจริง ไม่รับช่วง PASS เดิม |

ตารางใช้ basename เป็นชื่อหลักฐาน; path เต็มแบบสัมพัทธ์อยู่ในตาราง input ข้างต้น outputs ชิ้นงานทั้งหมดอยู่ `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/round-0/` ส่วนคำตัดสินอยู่ `007_LAB_Evaluation_Compare_Workflows/reference/step-04-change-dynamic/evaluation-round-0.md`

## ข้อจำกัดที่พบจากการอ่าน

- ui-scenarios.json เป็น index ของสามไฟล์ markdown ไม่ได้บรรจุ test cases ไม่มี scenario ID ให้พิสูจน์ว่าเก็บครบ จึงไม่อ้างว่าอ่านหรือผ่านชุดปลายทาง เก็บ path เดิมใน source_refs พร้อมบอกฐานการ resolve เดิม; ห้ามคัด index ไปใช้แล้วอ้างว่าเป็น executable scenarios หาก coverage สำคัญยังพิสูจน์ไม่ได้ให้ evaluator ระบุ gap
- FR/Flow ยังกล่าวถึงคำถาม “ถึง N เป็นเตือนหรือห้ามยืนยัน” ให้คงประวัติคำถามพร้อมแยกคำสั่งทดลองนี้ว่าไม่เพิ่มกฎปฏิเสธ ไม่สร้างคำตอบธุรกิจส่วนอื่นหรือสูตร X ใหม่
- Flow ยก fixture UTC แต่ UI ใช้ +07:00 และช่วง [เริ่ม,สิ้นสุด) การทดสอบใช้ clock ของ UI พร้อม timezone ชัดเจน คงความต่างเดิมเป็นข้อจำกัดไม่เปลี่ยนเวลาเพราะ N เปลี่ยน
- อย่าแทนเลข 5 ทั้งไฟล์ เพราะ AC อื่นมีเวลา 5 วินาที, 5 จาก 5, fixture หรือข้อมูลที่ไม่เกี่ยวข้อง
- การยืนยันต่อได้เมื่อเต็มไม่ลบกฎปฏิเสธเดิมของเมนูหมด/session ปิด/ตะกร้าผิด เงื่อนไขทดสอบต้องใช้ตะกร้าถูกต้องเพื่อแยกผล capacity
- X=10 นาทีเป็นค่าแสดงจำลองเดิม คงป้ายใกล้ข้อความและไม่อ้างเป็น ETA US-07, SLA หรือค่าจริง
- ไม่รับช่วง PASS ของแผนเดิม ไม่เปิด scope US-17/18/22/23/24 ที่ไม่มีแถวใน snapshot ไม่สร้างผลยืนยันระบบจริงจาก UI mock

## ตรวจใหม่และการหยุด

ตรวจ CHG-AC-01–08 ตาม plan-v4.json ครอบคลุม diff, threshold, ยืนยันต่อ, รอยต่อ, สามรอบ, reset/configuration/X, ID/AC และ regression โดยใช้หลักฐานตามรุ่นจริง การรักษา source ไม่เท่ากับผล runtime การทดสอบ N=3 ต้องผ่าน 3 จาก 3 รอบ ไม่ใช้เพียงการตั้งค่า N หรือจำนวนออเดอร์เป็นหลักฐาน

change-conditions.md จำกัด pre-run ที่ round 0 แม้กติกาทั่วไปแก้ได้สองรอบ ดังนั้น evaluate ครบเกณฑ์ให้ COMPLETE ถ้าไม่ครบให้ STOP_WITH_GAPS พร้อมหลักฐานและข้อเสนอแก้ที่ยังไม่ได้ทำ ไม่เปิด REPLAN รอบ 1/2 เอง งบรวม 3600 วินาที/8000000 input+output tokens ผู้ทดลองอ่านค่าจริงจาก log หลังจบ รวมต้นทุนทุก phase/แก้/orchestration ไม่มีข้อมูลต้นทุนเงินจริง

การวิเคราะห์นี้ไม่มี feedback จาก evaluate ก่อนหน้าเพราะ ROUND=0 ไม่มีการผลิตชิ้นงาน execute หรือผล tests ในการเรียกนี้
