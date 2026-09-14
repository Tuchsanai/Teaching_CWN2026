# Evaluator — verify-test-outline plan-v2
REVIEW_MODE: artifacts; TASK_ID: draft-test-outline; VERIFY_TASK: verify-test-outline; RUN_ID: outline-v2-review.
UTC: 2026-09-14T13:33:13.741164Z; ตรวจ v2 ครั้งที่ 1; แก้ artifacts 0 รอบ.
ผล: **PASS เฉพาะเอกสาร test outline v2**; Mock runtime / AC ระบบจริง **NOT_TESTED** ทุกข้อ; การยืนยันกฎที่ขาด **BLOCKED**.
Path จากราก LAB: S=reference/session; B=reference/step-00-input/baseline-filtered-v2; O=S/test-outline-v2.md; V=S/fr-nfr-v2.md; F=S/flow-v2.md; C=B/ui-contract.md; R=reference/step-03-reveal-1/reveal-1.md; E=reference/step-05-execute-v2/draft-test-outline/evaluation.
วิธีจริง: Python SHA-256 จาก bytes, Draft7Validator+FormatChecker/UTC/unique IDs/DAG; parse ตาราง AC/source locator/Flow mapping; อ่าน delta และ regression. ไม่รัน browser/HTML/DOM/LAN.
Gate PASS: v2 เป็นเลขล่าสุด; schema/UTC/IDs/11-task DAG/cancel ผ่าน; verify-plan manifest 29/29 และ verify-flow manifest 26/26 hash ตรง. ใช้ผล JSON/Markdown/diff/human limits และ FR ตั้งต้นที่ตรวจแล้ว ไม่ audit FR/Flow เดิมทั้งชุดซ้ำ.
Reuse PASS: fr-v2-check PASS ผูก FR hash ปัจจุบัน; flow-v2-check PASS_DOCUMENTS_ONLY ผูก F/state/structure ปัจจุบัน; F-01 closed เฉพาะเอกสาร. Outline v1 BLOCKED ยังคงเป็นประวัติ.
Transfer PASS: artifact-transfer.json ตรวจ source=destination byte-identical 2/2; O 47485 bytes และ execution report 14916 bytes ตรง SHA ที่แจ้ง; มี outputs ตามแผนจริง.
ข้อความ PASS: AC O ตรง source 21/21; scope/source locators/FR locators/Flow-ID sets ตรง 21/21; delta R→V ตาราง US ตรง 3×6=18 เซลล์; อีก 18×6 ใช้ fr-v2-check ที่ hash ตรง. O อ้างอีก 5 คอลัมน์ผ่าน source locator ตาม O:10.

| US | Locator O → V:FR → F:coverage | ผลระดับเอกสาร / หลักฐาน | Mock / ระบบจริง |
|---|---|---|---|
| US-01 | 26 → 50 → 34 | PASS — QR/จุดวัด/3 วินาที/18 จาก 20 คงเดิม | NOT_TESTED / NOT_TESTED |
| US-02 | 27 → 51 → 35 | PASS — table_id/20 โต๊ะ/19 จาก 20; seed ไม่แทนชุดจริง | NOT_TESTED / NOT_TESTED |
| US-03 | 28 → 52 → 36 | PASS — ช่วงรับ 15 นาที/ขั้นต่ำ 20 นาที/10 ใบ แยก capacity | NOT_TESTED / NOT_TESTED |
| US-04 | 29 → 53 → 37 | PASS — ตัวเลือก/ยอดก่อนยืนยัน/19 จาก 20; ตรวจซ้ำหลังเปลี่ยน | NOT_TESTED / NOT_TESTED |
| US-05 | 30 → 54 → 38 | PASS — ครัว→ลูกค้าไม่รีเฟรช/5 วินาที/18 จาก 20; O:58 | NOT_TESTED / NOT_TESTED |
| US-06 | 31 → 55 → 39 | PASS — ปิด catalog/ปฏิเสธตะกร้าเก่า แยกรายการในคิว; O:59 | NOT_TESTED / NOT_TESTED |
| US-07 | 32 → 56 → 40 | PASS — สูตร/7 วัน/สองช่วง/10 นาที/80% คงเดิม; X ไม่ใช่ ETA | NOT_TESTED / NOT_TESTED |
| US-08 | 33 → 57 → 41 | PASS — ยอดลูกค้า–หน้าร้าน/19 จาก 20/สองวิธี/3 จาก 3; O:55–57 | NOT_TESTED / NOT_TESTED |
| US-09 | 34 → 127 → 42 | PASS — R:12; สองปุ่ม/ลดยอด/ครัวกด→แจ้ง 10 วินาที LAN/5 จาก 5; O:50,54–56 | NOT_TESTED / NOT_TESTED |
| US-10 | 35 → 58 → 43 | PASS — timestamp/monotonic/มือถือ 2 เครื่อง/30 ใบ×3 รอบ; 3 วินาที/18 จาก 20 | NOT_TESTED / NOT_TESTED |
| US-11 | 36 → 59 → 44 | PASS — F-01: OrderEvent→MOD-06/SCR-08/front-order; 1 แตะ/5 วินาที/18 จาก 20; O:58 | NOT_TESTED / NOT_TESTED |
| US-12 | 37 → 60 → 45 | PASS — ทั้งจาน/เฉพาะตัวเลือก/5 ชนิด/5 จาก 5; ช่องเพื่อยังปิด; O:59 | NOT_TESTED / NOT_TESTED |
| US-13 | 38 → 61 → 46 | PASS — เปิดคืนตามแมป/10 วินาที/9 จาก 10; ไม่ตัดสินใจแทนลูกค้า | NOT_TESTED / NOT_TESTED |
| US-14 | 39 → 128 → 47 | PASS — R:13; item รอ→เปลี่ยน/ลบ; ลูกค้าเลือก→ครัว 10 วินาที LAN/5 จาก 5; O:50,54–56 | NOT_TESTED / NOT_TESTED |
| US-15 | 40 → 62 → 48 | PASS — table/T-001/00:00/payment events/log/20 จาก 20 ทั้งสามเกณฑ์; O:57 | NOT_TESTED / NOT_TESTED |
| US-16 | 41 → 63 → 49 | PASS — session โต๊ะใหม่ไม่ปนเก่า/5 จาก 5; ไม่เพิ่ม guard จ่ายครบ | NOT_TESTED / NOT_TESTED |
| US-19 | 42 → 64 → 50 | PASS — jpg/png/2 MB/0–10/1 นาที/ราคาเดิม 5 จาก 5; snapshot แยกยอดปรับ O:55,57 | NOT_TESTED / NOT_TESTED |
| US-20 | 43 → 65 → 51 | PASS — แมปแยกเมนู/1 นาที/5 จาก 5; คงรหัสอ้าง US-14 และ Q-20 | NOT_TESTED / NOT_TESTED |
| US-21 | 44 → 129 → 52 | PASS — R:14; O:63–73 มี N=5/3 รอบ/15 นาที/00/15/30/45/แจ้งก่อนยืนยัน | NOT_TESTED / NOT_TESTED |
| US-25 | 45 → 66 → 53 | PASS — ชื่อ 3–20/PIN 4–6/ผิด 5/ล็อก 5 นาที/3×2=6 จาก 6; report placeholder | NOT_TESTED / NOT_TESTED |
| US-26 | 46 → 67 → 54 | PASS — Ubuntu/สคริปต์เดียว/30 นาที/ข้อมูลในร้าน/ถอดเน็ต 20 ใบ; ยังไม่มีระบบจริง | NOT_TESTED / NOT_TESTED |

PASS delta3US: O:50 แยกชุด 5 จาก 5 ของ US-09/14 ครอบเปลี่ยนและคืน ไม่ใช้ smoke แทน; O:67–69 มี N=5 สามรอบจริงในแผน ไม่อ้างว่ารันแล้ว.
PASS state/ยอด: O:54–59 แยก item/order/payment/table และ O:12 แยก AI snapshot; ไม่ใช้สถานะจ่ายแทนสถานะอาหาร ไม่ลบ snapshot หรือสร้าง log ยืนยันเงินจากการคืน.
PASS robustness: O:56 คืนซ้ำไม่หักซ้ำเป็นสมมติฐาน mock รอ Q-V2-REFUND/STATE; ปุ่ม disabled ไม่พิสูจน์คำสั่งซ้ำภายใน. O:73 boundary เป็น fixture; ทั้งสองไม่ใช่ AC ธุรกิจใหม่.
PASS ขอบเขต US-21: O:63,67,71,73 ติดป้าย UTC/[start,end)/X เป็น fixture; ปุ่มยังใช้ได้เป็นข้อเสนอ mock ตาม F:144–146 ไม่ตัดสินนโยบายรับออเดอร์จริงเมื่อเต็ม.
PASS แผน UI: O:16–18,77 คง data-testid/fixture ตาม C, scope data-order-id และรอ selector/contract v2; การรักษา selector/พฤติกรรมใน HTML จริงยัง NOT_TESTED.
ข้อสังเกตไม่บล็อก: O:40 “ข้าม 00:00 ไม่ reset” ต้องใช้ความหมายไม่กด btn-reset; เลขรับต้องรีเซ็ต T-001 เมื่อวันใหม่ตาม AC ในแถวเดียวกันและ C ห้ามใช้ข้อความย่อนี้เป็น expected ว่าเลขไม่รีเซ็ต.
ข้อสังเกตส่งต่อ: O:7,83 และ execution:7 เป็นข้อความก่อน transfer; ลิงก์ execution.md ใช้ได้ที่ source แต่ไม่ตรงตำแหน่งสำเนา S. ให้ใช้ S/execution/plan-v2/outline-v2-run/draft-test-outline.md และ artifact-transfer.json เป็น mapping; ไม่แก้หลักฐานเดิม.
BLOCKED เฉพาะกฎ/ระบบจริง: ก./ค./ช., Q เดิม/Q-V2-REFUND/STATE/CAPACITY, เสร็จแล้ว↔พร้อมเสิร์ฟ/aggregate/ETA, เงินคืน/ส่วนต่าง/ซ้ำ/ผู้อนุมัติ, X/เขตเวลา/นับคืน/เปลี่ยน N, Q-20/Unknown; O:79 และ plan #/limits l-real-scope/l-q-*.
NOT_TESTED: browser/คลิก/DOM/roles/reset/responsive; QR/Wi-Fi/LAN/หลายอุปกรณ์/เวลา/โหลด/concurrency/สัดส่วนทุก AC; ETA 7 วัน/server log/security; Ubuntu/ติดตั้ง/เก็บข้อมูล/ถอดอินเทอร์เน็ต/เงินจริง.
Downstream: ปลด gate verify-test-outline เฉพาะเอกสารให้ revise-ui ตาม FR+Flow+O hashes นี้; verify-ui และ evaluate-handoff ยังต้องรอผลใหม่. ไม่เปลี่ยน snapshot หรือใช้ผลนี้รับรองระบบจริง.
ข้อบกพร่องที่บังคับแก้ก่อนส่งต่อ: ไม่พบ; หาก scope/dependency เปลี่ยนให้ส่ง Planner ทำรุ่นใหม่. จำกัดแก้ 2 รอบต่อปัญหา ไม่คืบหยุดพร้อมหลักฐาน; เป็นข้อตกลงการเรียน ไม่ใช่ AC ร้าน.
Plan JSON SHA-256: `8682dcba597fd36cadcf0a4724a9a75bd866f551b337281c663ee419c059c828`; Markdown: `75c5e9b06c7e26fbf7174295d165fbae64be57ea8ff807b4d96884898296ea2c`.
Input-set SHA-256: `d96e4239b712e9b866235071a4436682d7ebbf3069dbb216fb4c3a04e5eaaa90`; manifest ใน E/evaluator.md: path จากราก LAB+TAB+SHA256+LF เรียง path; รวมอ่านเนื้อหาและ hash-only dependencies.
Target O SHA-256: `50b3c1a7e68a5ca3a56cff2939f55cd591ae2c60c63bd3577625bc442dd2b763`; execution report: `dc9e94d3e20a7bf904c846b0f5fa6a30f9422b7828963168fc652be1e51d9eb4`.
FR SHA-256: `2cbdde11bb3fd5e62f338a1ea74f65d11112f3ea56e8a10ed9d24b08a1dcf0bb`; Flow: `8fe7983eb45a7222424c7fafe34adf78874da75e7e7cf3ab013d4955d1159f9c`.
Reveal-1 SHA-256: `1fde792db1fdcf211be4a171fd88c61184ce892720832023fcaefad6a67f8917`; output report hashes อยู่ E/evaluator.md (ไม่ทำ self-hash).
สร้างจริง: S/evaluations/test-outline-v2-check.md; S/evaluations/plan-v2/outline-v2-review.md; E/test-outline-v2-check.md (รายงานเดียวกันสามสำเนา) และ E/evaluator.md.
ไม่เปิด README/reveal-2/เว็บ ไม่เรียก agent/AI CLI เพิ่ม ไม่ใช้บัญชีจริง/บริการเงินจริง และไม่แก้ input/prompts/แผน/หลักฐานเดิม.
