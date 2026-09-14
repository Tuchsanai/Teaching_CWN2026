# Impact — Single Prompt, US-21 N=3

สถานะส่งมอบ: **STOP_WITH_GAPS** — สร้างชิ้นงานครบ แต่ input บางส่วนไม่พบและ UI/regression **NOT_RUN**. ไม่มีผลรับรอง UI หรือระบบจริงจากรอบนี้.

**โจทย์สมมติ ไม่ใช่ต้นฉบับ:** เปลี่ยนเฉพาะค่า N ที่ใช้ทดสอบ US-21 จาก 5 เป็น 3. คงหน้าต่าง 15 นาทีเริ่มนาที 00/15/30/45, จำนวน 3 จาก 3 รอบ, ข้อความ “ครัวเต็ม รอประมาณ X นาที” ก่อนยืนยันเมื่อจำนวนออเดอร์ยืนยันแล้วถึง N; ไม่เพิ่มกฎปฏิเสธออเดอร์จากความจุ. ต้นฉบับ `docs/case-study-source.md` ยังคง N=5 และไม่ถูกแก้.

## Input และการควบคุม

อ่าน baseline snapshot ทุกไฟล์ตาม manifest, เงื่อนไขร่วม, แผนก่อนเปลี่ยน และต้นฉบับเฉพาะ path ที่ manifest ระบุ. Paths หลักฐานที่ขึ้นต้นด้วยชื่อ LAB หรือ docs/ ในเอกสารนี้สัมพัทธ์จาก AI_Workflow_Engineering_for_SA/; การอ่านจาก cwd ขั้นนี้ resolve ด้วย `../../../`. ลิงก์ชิ้นงานในขั้นนี้สัมพัทธ์จากไฟล์ปัจจุบัน. ไม่อ่านผลอีกวิธี ไม่อ่าน HTML บทเรียน และไม่เปิดลิงก์ต้นฉบับอื่นตามข้อความภายในเอกสาร.

เงื่อนไขร่วมระบุ Codex CLI 0.154.0; โมเดล gpt-6-astra ตาม flag ที่ผู้ทดลองกำหนด (ไม่ได้ตรวจยืนยันกลับ); effort high; เพดานรวมต่อวิธี 3600 วินาทีและ input+output 8000000 tokens โดยอ่าน usage หลังจบ ไม่ใช่ hard token cap. รอบนี้ทำภายในคำขอเดียว ไม่มีการเรียก Planner/Executor/Evaluator หรือผู้ช่วย/CLI เพิ่ม. เวลา/โทเคนจริงให้ผู้ทดลองอ่านจาก log; ไม่สร้างตัวเลขต้นทุน คะแนน rubric หรือข้อสรุปความคุ้มค่า.

แผนก่อนเปลี่ยนมีขอบเขต 26 US และสายข้อกำหนด→ข้อมูล→Flow→ชุดตรวจ→UI→ตรวจส่งต่อ; snapshot ที่ใช้ทดลองยังมี 21 US. ใช้แผนเพื่อวิเคราะห์ dependency และข้อค้าง ไม่ดำเนินงานขยาย US-17/18/22/23/24 หรือเปิดผลการทดลองอีกวิธี. รหัส US/FR/NFR/MRG/C-V2/MOD/SCR/Q เดิมเป็นรหัสโดเมนและคงไว้; รหัสขั้นของการทดลองนี้ใช้ CHG- เท่านั้น. สถานะ/ผลตรวจในแผนเดิมเป็นประวัติ ไม่ใช่ผลของ v3 นี้.

## ส่วนเปลี่ยน / ใช้ซ้ำ / ต้องตรวจใหม่

| ขั้น | ผลงานและส่วนเปลี่ยน | ใช้ซ้ำ | ต้องตรวจใหม่ภายนอก |
|---|---|---|---|
| CHG-01 | [fr-nfr-v3.md](fr-nfr-v3.md): US-21/FR-21 และวิธีตรวจใช้ N=3; แยกที่มาข้อเปลี่ยนสมมติ; ปรับ mapping ส่งต่อ | 20 US อื่น, 20 FR อื่น, NFR 17 แถว, รหัสเดิม/คำถาม/AC อื่น | ความสอดคล้องกับโจทย์, 3/3 รอบ, regression ที่กระทบหน้าก่อนยืนยัน |
| CHG-02 | [flow-v3.md](flow-v3.md): fixture MRG-34/35 ใช้ N=3; คำอธิบายก่อนมี3/เมื่อมี3; ทำ clock fixture ให้ตรง +07:00 ของ UI เดิม | MRG-01–35 และ state/module/screen IDs; count ยืนยันแล้ว, หน้าต่าง15นาที, ไม่เพิ่ม hard block | before/at/above N, ทุกขอบเวลา, ช่วง start/end, ผลต่อการส่งและข้อมูลนับ |
| CHG-03 | [ui-mockup-v3.html](ui-mockup-v3.html): capacitySeed.limit 5→3, ข้อความค่าเริ่ม N=3, ป้าย v3/สมมติและ NOT_RUN | selectors/payload, capacityWindow/notice/save/submit handlers, ค่า X=10, ช่วง11:30–13:30, seed/clock/reset เดิมยกเว้น N, ราคา/คิว/เงิน/สิทธิ์/หน้าจอทั้งหมด | runtime/DOM/ปุ่ม/คำเตือนก่อนยืนยัน/viewport/console; ไม่อนุมานผ่านจาก source |
| CHG-04 | [ui-scenarios-v3.json](ui-scenarios-v3.json): คง schema role→path สามบทบาท; ชี้ fixture Markdown ใหม่ใน scenarios/ | ชื่อ key customer, kitchen-front, manager และ selectors/เกณฑ์จากสัญญา snapshot | สคริปต์ร่วมอ่านรูปแบบ Markdown ได้จริงหรือไม่, 3 context, boundary และ regression; ยังเทียบรหัส scenario ต้นฉบับไม่ได้ |
| CHG-05 | impact ฉบับนี้: dependency, หลักฐาน static, gaps และส่งต่อ | ข้อค้างเดิมจาก snapshot/แผน | ผลจากสคริปต์ร่วมภายหลัง, usage/wall จาก log ภายนอก |

สัญญา v3 ใช้ `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/ui-contract-v2.md` เป็นฐานที่อ่านได้ แล้วใช้ delta ใน FR/Flow นี้: ค่าเริ่ม/reset/test N=5→N=3 และชุด 4→5 ออเดอร์เป็น 2→3; คง selector และพฤติกรรมอื่น. ไม่แก้หรือสร้างสัญญาต้นฉบับย้อนหลัง.

ลบหัว execution/handoff/hash ประวัติจากสำเนา FR/Flow ที่ไม่ใช่ผลรอบนี้ แล้วใส่สถานะและที่มาปัจจุบัน. FR ยังคงตารางข้อกำหนดเต็มและ traceability; ตาราง mapping ที่เดิมบอกว่ารอ Flow/UI v2 ใช้ mapping จาก snapshot กับไฟล์ v3 ปัจจุบันแทน. ไม่เปลี่ยนความหมาย AC อื่น. ทะเบียน Flow ที่อ้าง B/S/R หรือ state-machine/structure ยังเป็น locator ประวัติใน snapshot ไม่ใช่การรับรองว่าตรวจไฟล์ภายนอกเหล่านั้นแล้ว.

## ผลกระทบต่อพฤติกรรมและ regression

| จุดเชื่อม | เกณฑ์ที่ต้องคงและหลักฐานที่ต้องเก็บ |
|---|---|
| US-21 → MRG-35 → SCR-03 | count=2 ยังไม่เต็มแม้มีตะกร้าใบที่3; หลังใบที่3ยืนยันแล้ว ลูกค้าใหม่เห็นเต็มก่อนใบที่4; count=4 ยังเต็ม; ตะกร้าถูกต้องยังส่งได้ |
| US-21 → MRG-04 / US-10 | นับเมื่อ submit สำเร็จเท่านั้น; หลายจานหนึ่งใบยังนับหนึ่ง; เลข monotonic/ลำดับคิวไม่เปลี่ยน; ไม่เอา T-001 หรือจำนวนจานเป็น count |
| US-21 → US-03/07 | 15 นาทีของ pickup และขั้นต่ำ20นาทีคงเดิม; ETA สูตร/ข้อมูล7วัน/ช่วงวัด/สัดส่วน80%คงเดิม; X เป็นตัวเลขจำลองและไม่ใช่ ETA |
| US-21 → US-06/12/13/20 | ไม่เพิ่มปฏิเสธจากความจุ; คงปฏิเสธวัตถุดิบหมดและแมปทั้งจาน/เฉพาะตัวเลือก; submit ที่ปฏิเสธต้องไม่เพิ่ม count |
| US-21 → US-09/14/08/15/19 | คืน/เปลี่ยนรายการไม่เพิ่มออเดอร์หรือลด count ใน fixture; snapshot/adjusted total และ payment-log ต้องแยก; ไม่ประกาศคืนเงินจริง |
| US-21 → US-16/25 | สลับบทบาทไม่ reset count; ปิดโต๊ะแยก session แต่เก็บยืนยันเดิม; manager capacity ใช้สิทธิ์เดิม; reset คืน N=3 |
| US อื่น | QR/โต๊ะ/ตัวเลือก, สถานะครัว→ลูกค้าและครัว→หน้าร้าน, PromptPay3กรณี, เมนู/ราคา/รูป/แมป, PIN/URL และ Ubuntu/offline ใช้ AC เต็มเดิม |

Fixtures ที่ส่งเพิ่มเพื่อให้ JSON ชี้ไฟล์ที่มีอยู่:

- [scenarios/customer.md](scenarios/customer.md): CHG-C01–C07; ลูกค้า/ยอด/จ่าย/ตัวเลือก/ETA/ขนาดจอ.
- [scenarios/kitchen-front.md](scenarios/kitchen-front.md): CHG-K01–K06; คิว/สถานะ/วัตถุดิบ/คืนเปลี่ยน5กรณี/เงิน/session/เกณฑ์ระบบจริง.
- [scenarios/manager.md](scenarios/manager.md): CHG-21-R1/R2/R3, CHG-21-B01–B06, CHG-M01–M04; threshold/boundary/ตั้งค่า/สิทธิ์และ regression ผู้จัดการ.

สามรอบ N=3 แยก context/reset ที่ 12:00,12:15,12:30; แต่ละรอบตรวจ count 2→3→4 และลูกค้าใหม่ก่อนยืนยัน. รอยต่อ 00/15/30/45 เป็นชุดเพิ่ม ไม่เปลี่ยนตัวหาร AC 3 รอบ. ยังไม่มีรอบใดถูกรัน.

## ข้อค้าง

| รหัส | ข้อค้าง/ผลต่อข้อสรุป |
|---|---|
| CHG-G01 | `docs/ui-contract.md` ตาม manifest ไม่พบที่ path ที่ระบุ. อ่านสัญญา snapshot ui-contract-v2.md ได้ แต่ไม่อ้างว่าตรวจเทียบสัญญาเดิมที่หายแล้ว |
| CHG-G02 | baseline ui-scenarios.json ชี้ `../step-01-fanout/customer/scenarios-customer.md`, `../step-01-fanout/kitchen-front/scenarios-kitchen-front.md`, `../step-01-fanout/manager/scenarios-manager.md`; ทั้งสามไม่มีไฟล์เมื่อ resolve จาก directory ของ baseline JSON. ไม่ค้นหาสำเนาอื่นนอก manifest; ไม่อ่านผลอีกวิธี. Fixture ทดแทนไม่ได้รับรองรักษารหัส/coverage ของ scenario ต้นฉบับครบ และไม่ได้ใช้เป็นต้นฉบับใหม่ |
| CHG-G03 | รูปแบบ JSON role→path คงเดิม แต่ยังไม่ได้รันสคริปต์ร่วม จึงยังไม่ยืนยันความเข้ากันได้ของ Markdown fixture/ตัวตรวจ หรือ regression ครบตาม scenarios เดิมที่ขาด |
| CHG-G04 | แผนร่วม26 US เทียบ snapshot21 US: คงขอบเขต snapshot เพื่อไม่เปลี่ยนโจทย์นอก N. ไม่อ้างครอบคลุมเพิ่มอีก5 US; ผลผ่านเดิมในแผนไม่ใช่ผล v3 |
| CHG-G05 | Q-V2-CAPACITY: สูตร X/ความสัมพันธ์ ETA, เขตเวลา/ข้ามวัน/การนับคืนเปลี่ยน/เปลี่ยน N ยังไม่มีคำตอบธุรกิจ. สำหรับโจทย์ทดลองนี้ยืนยันเพียงต้องเตือนและไม่เพิ่มปฏิเสธออเดอร์; [start,end), +07:00, นับรวมสองช่องทาง, ไม่ลดยอดนับเมื่อคืน เป็นสมมติฐาน fixture เดิม |
| CHG-G06 | UI มีปุ่มขยับเป็นนาที จึงยังไม่ทดสอบหนึ่งวินาทีก่อนขอบ. confirmed_at อยู่ภายใน state แต่ไม่มี selector สำหรับอ่านโดยตรง; received_at ของใบครัวใช้แทนหลักฐาน field นี้ไม่ได้. ไม่เพิ่ม hook เพื่ออ้างว่าตรวจได้ |
| CHG-G07 | คง Q-05/07/11 เรื่องสถานะ/ETA; Q-V2-REFUND/STATE เรื่องยอด/เงินจริง/aggregate; Q-20 เรื่องอ้าง US-14; หมายเหตุ ก./ค./ช.; คำถามอื่นทุกข้อใน FR. จำนวนโต๊ะ seed3ไม่พิสูจน์ AC5หรือ20โต๊ะ; ไม่มีข้อมูล7วัน/เงินจริง/server/LAN/หลายเครื่อง/โหลด/security/Ubuntu install |

## ตรวจไฟล์ที่ทำจริง — ไม่ใช่การทดสอบ UI

อ่าน/hash input และเทียบกับ manifest: snapshot5ไฟล์และ plan-v3 ตรง SHA-256 ที่ manifest ระบุ. ใช้การเทียบข้อความตารางข้อกำหนด: US21แถวและ FR21แถวคงรหัสครบ; ทุกแถวนอก US-21/FR-21 ตรง baseline ทุกอักขระ; สองแถวนี้ต่างเฉพาะ N=5→N=3. NFR17แถวตรง baseline ทุกอักขระ. AC ที่คัดใน Flow คงเดิมยกเว้นค่า N ของ US-21.

เปรียบเทียบไฟล์ HTML กับ snapshot พบเพียงสี่ตำแหน่งที่ตั้งใจเปลี่ยน (ป้ายรุ่น/สมมติ, สถานะรอทดสอบ, capacitySeed.limit, ข้อความค่าเริ่มต้น); ไม่มีการ execute JavaScript หรือ browser. JSON parse ได้ มีสาม role keys เดิมและชี้ไฟล์ Markdown ที่มีอยู่จริง. สแกนไฟล์ส่งมอบเพื่อไม่ให้มี absolute path/รหัสงานทีมภายใน/การอ้างพื้นที่เขียนต้องห้าม. การตรวจเหล่านี้พิสูจน์ความต่างของไฟล์เท่านั้น ไม่ใช่ PASS ของ UI/AC.

สร้างทั้งหมด8ไฟล์: ชิ้นงานหลัก5ไฟล์และ scenario fixture ประกอบ3ไฟล์. เขียนเฉพาะ cwd และ scenarios/; ไม่แก้ baseline/ต้นฉบับ/แผน/log หรือไฟล์อื่น, ไม่ใช้ git add/commit/push.

## หลักฐาน SHA-256 ของ input ที่อ่าน

| Path จาก AI_Workflow_Engineering_for_SA/ | SHA-256 |
|---|---|
| `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/manifest.md` | `53a7bbb43f9024ebbe71f97f2f5acac80e5810bee67534dcc0a353d4ac0ab88f` |
| `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/fr-nfr-v2.md` | `2cbdde11bb3fd5e62f338a1ea74f65d11112f3ea56e8a10ed9d24b08a1dcf0bb` |
| `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/flow-v2.md` | `8fe7983eb45a7222424c7fafe34adf78874da75e7e7cf3ab013d4955d1159f9c` |
| `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/ui-mockup-v2.html` | `249b98c493f4c1347efe36f8be059095ede9d3b23b76ada3b022cfc416c2a1cc` |
| `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/ui-contract-v2.md` | `40ad0ff84c423a225b1675bbc2a627390446b9ecfcbcbb4496a6f0605e675888` |
| `007_LAB_Evaluation_Compare_Workflows/reference/change-baseline/ui-scenarios.json` | `171392ecc2b4dabcd45755552f378827c06616d012c71cc2174a93dcc9b27219` |
| `007_LAB_Evaluation_Compare_Workflows/reference/change-conditions.md` | `6d115d575eeaf179ea3427adaa3159bdd26f9ef45c076455c73f322d61a0cbe7` |
| `005_LAB_Dynamic_Workflow_Replanning/reference/step-07-plan-v3/plan-v3.json` | `2cc75857183b0fefd5f2631638442494dce2ff63436b8fa768ad5c2c13420125` |
| `docs/case-study-source.md` | `23294c6b1b6fa1ac76f83b2c60a21c4d2cdf6efa5b6b777d4d9224d7e5e0af3d` |

## หลักฐาน SHA-256 ของชิ้นงาน

| Path ภายในขั้นนี้ | SHA-256 |
|---|---|
| `fr-nfr-v3.md` | `224768c2f478b4e7dd81730725b5f573f397d79e48656e4d624c044515c49322` |
| `flow-v3.md` | `c6de4610e0de30d4c51364882421ef3afd664ecaed7ccc7e38ef96841bb48a27` |
| `ui-mockup-v3.html` | `7c6917543619622510eaedc777368883b4b91798a617204a4b6dd94650c6d1aa` |
| `ui-scenarios-v3.json` | `d9113ea0de88a1110711894c7ba041e6319845b868a3fcfe0a0f388b460ef3b0` |
| `scenarios/customer.md` | `45ab38bea180db7b73af428d2139e4996237722699769cd8d7bdca8949e69681` |
| `scenarios/kitchen-front.md` | `d362c0390580c628ea4b326e8c49cddad35fce0cd404efeebf371e78a0335b49` |
| `scenarios/manager.md` | `d4c07234f8aec0b3be5c1875301c035a3f50bc0517cb12ca50818e0d862bb468` |

impact.md ไม่ใส่ hash ของตัวเองเพื่อหลีกเลี่ยง self-reference. ผู้ทดลองผูก hash ชิ้นงานกับผลจากสคริปต์เดียวกันภายนอกภายหลัง แล้วแยกผล threshold3/3, boundary, regression, ช่องว่างของ input และข้อจำกัดระบบจริงออกจากกัน. หากเกณฑ์ยังไม่ครบให้คง STOP_WITH_GAPS พร้อมผลจริง; ไม่แทน NOT_RUN ด้วย PASS. Usage/wall และต้นทุนอื่นให้บันทึกจาก log หลังจบเท่านั้น.
