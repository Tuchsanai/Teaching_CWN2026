# Input audit ขั้น 5.0 — baseline-filtered-v2

ผลสรุป: **INPUT_READY — เฉพาะการวางแผนเอกสารและ offline mock**

ไม่ใช่การอนุมัติระบบจริง ไม่ปิดข้อค้างธุรกิจ และไม่ใช่ผลตรวจ Flow หลังกรองครบทุกเกณฑ์ ผล upstream ทั้งสามชิ้นมีอยู่จริงในสำเนา; hash ทั้ง 10 ไฟล์ตรง provenance; ไม่พบแถวหรือความสามารถที่กำหนดเพิ่มจาก US ที่กันไว้ในการตรวจขอบเขตครั้งนี้ จึงส่งต่อเพื่อให้ Planner วางงานตรวจต่อได้ตามข้อกำหนดเฉพาะรอบนี้

ตรวจเมื่อ: 2026-09-14T12:30:53.418635Z

| ชิ้นงาน | ที่มา | hash | ผลตรวจ | ข้อค้าง | พร้อมส่งต่อ |
|---|---|---|---|---|---|
| FR/NFR — fr-nfr.md | ใช้ผลอ้างอิง LAB 002; หัวเอกสารระบุ v1 และพัฒนาจาก v0; ใช้ hash ระบุสำเนาจริง ไม่เลือกจากเลขรุ่นสูงสุด | SHA-256: `da31640e540b825d4fec555627ea098f092daf4243d5d304fd4c32ae6db734cd` | มี FR 18 แถวตรงชุด US ตั้งต้น; fr-check.json รายงาน PASS 108/108, failed 0, ไม่มี regression; เป็นผล upstream ที่รับมาตาม provenance | คำถาม Q-01–Q-26 เฉพาะรหัสที่มีในเอกสารยังคงอยู่; ไม่มีหลักฐานทดสอบระบบจริง; ไม่ยืนยัน path รุ่น final นอกสำเนา | พร้อมสำหรับเอกสาร/offline mock |
| Flow รวม — flow.md | ใช้ผลอ้างอิง LAB 003 ฉบับ merge ที่ทำ scope projection ใน baseline-filtered-v2 | SHA-256: `d0a5fcd029f4f315a02fcd2c057a44907bdf7362fbce17b8664a75b82773595d` | มี 30 merged flows และ coverage US 18 รหัส; hash ของ FR ที่อ้างตรงกับ fr-nfr.md; พบข้อความพฤติกรรมและ AC ของ FR ทั้ง 18 แถวตรงตัวในหลักฐาน Flow | หัวไฟล์ยัง READINESS: BLOCKED สำหรับงานพร้อมใช้งาน; MC-01–MC-03 ยัง unresolved; flow-check.json เป็นผลก่อนกรอง ต้องมีงาน verify หลังกรองใน plan-v1 | พร้อมวางแผนและตรวจเอกสาร; ยังไม่รับรอง Flow หลังกรองครบทุกเกณฑ์ |
| Flow ประกอบ — state-machine.md | ใช้ผลอ้างอิง LAB 003 node state-machine; สำเนา scope projection ชุดเดียวกัน | SHA-256: `b4bc79de9e95f1526ca05326211a6025981b0420f3681b574e37189319f35adf` | มีไฟล์ประกอบ; hash FR ต้นทางตรง; พบข้อความพฤติกรรมและ AC ของ FR 18 แถวตรงตัว; แยกออเดอร์/ชำระเงิน/table session และเก็บส่วนรายการที่ปิดขอบเขตไว้ | ลิงก์ flow-state-machine.md/json ไม่อยู่ในสำเนาและไม่ได้ตามไปอ่าน; initial/terminal, mapping และกฎ event ที่เสนอไม่ใช่ข้อกำหนดยืนยัน | พร้อมตรวจเอกสาร โดยคงข้อค้าง |
| Flow ประกอบ — structure.md | ใช้ผลอ้างอิง LAB 003 node structure; สำเนา scope projection ชุดเดียวกัน | SHA-256: `fc8facf9088ad320d8dc3a7157edc14b337c1cb7081c3b098bcf91ceab08c560` | มีโมดูล ข้อมูล หน้าจอ สิทธิ์ และ coverage US 18 รหัส; โครงสร้างส่วนรวมอยู่ใน flow.md ด้วย | ลิงก์ flow-structure.md/json ไม่อยู่ในสำเนา; ชื่อ entity/key/cardinality และสิทธิ์ Unknown ยังไม่ยืนยัน; ไม่อ้างว่าข้อความทุกส่วนตรงตัวกับ FR หรือผ่าน verify หลังกรอง | พร้อมตรวจเอกสาร โดยคงข้อค้าง |
| UI — ui-mockup.html | ใช้ผลอ้างอิง LAB 004 ตาม provenance; ระบุรุ่นสำเนาด้วย hash; ui-check.json อ้าง HTML ในพื้นที่ work ของ LAB 004 ไม่ใช่การรันสำเนานี้ | SHA-256: `d2b7bfa0cff5700d3ca07f611c03cfa0304c54eafb51387f125e95edd11f7803` | ผล upstream 19/19, failed 0, edge pass; ตรวจ source พบ seed ฝังใน HTML, CSP ปิด network และไม่พบ URL http(s) หรือ fetch/XMLHttpRequest/WebSocket; selector ใช้ทั้งข้อความคงที่และ template | US-07 เป็นข้อความยังประมาณไม่ได้ ไม่มี ETA ตามสูตร; US-26 ไม่ได้มีตัวติดตั้งหรือหลักฐาน offline ระบบจริง; ยังไม่รัน browser ตรวจสำเนานี้ | พร้อมเป็น offline mock ตั้งต้น |
| สัญญา UI — ui-contract.md | สัญญาที่จัดให้จาก LAB 004 ในชุดใช้ผลอ้างอิง; ไม่ใช่ข้อกำหนดร้านที่เพิ่มใหม่ | SHA-256: `294b660d2e39b3745344f225400eee57c02c25b6efb108a3a7ecce7cdd060e68` | พบ selector 81 รายการ; 77 ชื่อพบใน source โดยตรง อีก 4 ชื่อเป็น menu-item-/option- template; รูปแบบบทบาท ข้อมูลจำลอง และสถานะที่ระบุตรงบริบท HTML | การตรวจ source ไม่พิสูจน์ DOM, selector uniqueness หรือการคลิก; fixture mapping และพฤติกรรมจำลองไม่ใช่การยืนยันกฎธุรกิจ | พร้อมใช้คู่กับ UI hash นี้ |
| US ตั้งต้น — us-initial.md | ใช้ผลอ้างอิงเฉพาะสำเนาที่กรองแล้วตาม provenance ของชุดนี้ | SHA-256: `56a439f6e22f4a8d17f552b023c3c8fe61556f5bd31f1f1e9b70c1f9da6049d2` | 18 แถว 18 รหัสไม่ซ้ำตรงขอบเขตที่อนุญาต; ไม่มีแถว US ที่กันไว้; US-20 คงรหัสอ้าง US-14 ภายในเซลล์ | ช่องเพื่อของ US-12 เป็นข้อความปิดรายละเอียดในสำเนาที่ให้มา; ไม่เปิดต้นฉบับเพื่อกู้ข้อความ ไม่แก้ US/AC หรือขยายรหัสอ้างเป็นงานใหม่ | พร้อมเป็นขอบเขตตั้งต้น |
| หลักฐาน FR — fr-check.json | ใช้ผลอ้างอิง upstream ที่ provenance ระบุ | SHA-256: `1b0c604da9288ce926ba4c98eb258107b130f309f85b1ee96403e02ba0d0f98c` | JSON อ่านได้; pairs=108, passed=108, failed=0, format_valid=true; ไม่ได้รัน checker ซ้ำ | ตัวรายงานไม่มี hash ของ target FR ภายใน; การผูกสำเนากับผลใช้ provenance และ FR hash ที่ Flow อ้าง ไม่อ้างการพิสูจน์ต้นทางอิสระ | พร้อมเป็นหลักฐาน upstream |
| หลักฐาน Flow — flow-check.json | ใช้ผลอ้างอิง upstream ของ customer, kitchen-front, manager, state-machine, structure และ merge | SHA-256: `3be4ccd3d045951e7c69e523e6ce2dfab052d45ece39d453741f310435d1c700` | ทั้ง 6 ส่วน execution_completed=true, schema_errors ว่าง และ scope/hash/evidence checks เป็น true; merge รายงาน 30 flows และ unresolved 3 | ผลก่อน scope projection เท่านั้น; unresolved ตาม node ไม่ใช่จำนวนประเด็นไม่ซ้ำที่นำมาบวกกัน; ไม่ยกระดับเป็น PASS ของ Flow หลังกรอง | พร้อมเป็นหลักฐาน upstream |
| หลักฐาน UI — ui-check.json | ใช้ผลอ้างอิง mock smoke checks จาก LAB 004 | SHA-256: `c09bf23c92abf0cd9c570f71ff890c1b572f8846c4d2ff8f5d2c3323be448af7` | checks 19 รายการผ่านทั้งหมด; browser=launch; scope ระบุ mock เท่านั้น | ไม่ใช่ผล LAN, load, security จริง หรือผล browser run ในขั้น 5.0 นี้ | พร้อมเป็นหลักฐาน upstream |
| ที่มา — provenance.md | manifest ที่ให้มาใน baseline-filtered-v2 | SHA-256: `8059b1b47647d690ed7a73e6b4b9751e209edb3905868a4729269fb79330739a` | คำนวณ SHA-256 ใหม่ตรงรายการทั้ง 10/10 ไฟล์; ใช้ผลอ้างอิงตามที่มา ไม่อ้างเป็นงานนักศึกษา | อ้าง ../provenance.md แต่ไม่เปิดตามข้อจำกัด scope; ไม่มี input-source.md ในชุดนี้; ใช้ manifest นี้และ mapping ใน audit สำหรับรอบอ้างอิง | พร้อมเป็นหลักฐานที่มาระดับสำเนานี้ |

การตรวจขอบเขตและรุ่น

- ขอบเขตใช้เฉพาะแถว US-01–US-08, US-10–US-13, US-15–US-16, US-19–US-20, US-25–US-26 รวม 18 แถวใน us-initial.md:3–20 ไม่ขยายจากรหัสในเซลล์ และไม่เปิด reveal
- FR มี 18 แถว; ตาราง coverage ใน Flow และ structure มี 18 รหัสไม่ซ้ำ การปรากฏ US-20 ซ้ำในหัวข้อคัดข้อความตรงตัวไม่ใช่ US แถวใหม่ เลข v2 ในชื่อชุดกรองไม่ใช่รุ่น FR ที่ผ่านสูงกว่า v1 และไม่ใช้เลขรุ่นเป็นหลักฐานผ่าน
- ตรวจรหัสแบบมีขอบเขตคำเพื่อไม่ตีความ CUS-09 ซึ่งเป็น Flow ID ว่าเป็น US-09 รหัสนอกชุดที่เหลือคือ US-14 ในบริบทการอ้างเดิม/ข้อค้าง และ US-23 ในบริบทจำกัดงานรายงาน ไม่พบแถว FR หรือ acceptance criteria ใหม่ของรหัสเหล่านี้
- US-20 ที่ us-initial.md:18 คง US-14; FR-20 ที่ fr-nfr.md:35, Flow ที่ flow.md:91 และ ui-contract.md:115 คง DI-04/A-03 เป็นข้อสงสัย ไม่อนุมัติแก้ dependency ส่วน flow.md:94 และ ui-mockup.html:356 จำกัดรายงานไว้ที่การตรวจสิทธิ์ US-25/placeholder ไม่มีเนื้อหารายงานที่ใช้งานได้ สิทธิ์ Unknown ใน Flow/structure ยังไม่ถือเป็นฟังก์ชันที่อนุมัติ
- ตรวจเนื้อหา Flow ขั้นตอนหลัก/ทางเลือก/ข้อผิดพลาด รวม state, entity, screen, permission และข้อค้าง เทียบขอบเขตตั้งต้น; พบข้อความปิดรายละเอียดใน Flow 21 จุด, state-machine 8 จุด, structure 7 จุด และ US ตั้งต้น 1 จุด ตัวอย่าง flow.md:74,312,502 ไม่กู้ข้อความที่ปิดไว้ ไม่อ่าน scope-filter.diff หรือต้นฉบับก่อนกรอง
- SHA ของ FR ใน flow.md:13 และ state-machine.md:15 ตรงไฟล์ปัจจุบัน ข้อความพฤติกรรมและ AC ของ FR ทั้ง 18 แถวพบตรงตัวใน Flow และ state-machine เป็นหลักฐานความสอดคล้องระดับข้อความที่คัดไว้ ไม่พิสูจน์ว่าทุก transition, guard, mapping หรือ UI ทำงานถูกต้องหลังกรอง
- สัญญา UI ระบุ fixture และข้อค้างเดียวกับ HTML; source มี selector จากฟังก์ชัน button และ template ที่ ui-mockup.html:324,344,345 จึงไม่ตัดสินว่า selector หายจากการค้น literal อย่างเดียว ยังไม่ตรวจการสร้าง DOM จริง
- UI ส่วน US-07 ที่ ui-mockup.html:346 เป็นข้อความ “ยังประมาณไม่ได้” เพราะ seed ไม่มีค่าเฉลี่ยที่ต้องใช้ จึงยังไม่มี ETA ตาม FR-07 แม้ FR/Flow ครอบคลุม ส่วน US-26 เป็นบริบทติดตั้ง/ออฟไลน์ ไม่ใช่สิ่งที่ UI เดิมพิสูจน์ได้ หน้ารายงานเป็น placeholder ตรวจสิทธิ์เท่านั้น

ข้อค้างธุรกิจ — nonblocking สำหรับตรวจเอกสาร/offline mock เท่านั้น

- หมายเหตุ ก./ค./ช. ไม่มีนิยามในสำเนา: คง A-02 และ Q-08/Q-12/Q-20/Q-07 ไม่เติมกฎร้านหรือเปลี่ยนเป็น AC ใหม่
- MC-01 / DI-07 / A-05: mapping “เสร็จแล้ว” กับ “พร้อมเสิร์ฟ” และขอบเขตสถานะยังไม่ยืนยัน; MC-02: วิธีจ่ายสองแบบกับ PromptPay ปิดและจุดเริ่ม 10 นาที; MC-03 / DI-04 / A-03: US-20 อ้าง US-14 และข้อเสนอเชื่อม US-12/US-13 ยัง unresolved
- คงคำถามอื่นที่มีใน FR/Flow เช่น เงื่อนไขปิดโต๊ะเมื่อค้างงาน/ค้างจ่าย, แมปและวัตถุดิบหมดซ้อน, ขอบเขตเลขออเดอร์/วัน, นิยาม MB, สิทธิ์ที่ยัง Unknown และสภาพก่อนติดตั้ง ไม่ตัดสินแทนเจ้าของข้อกำหนด
- สถานะ READINESS: BLOCKED ใน flow.md:5 และข้อความ handoff ธุรกิจ BLOCKED ใน ui-mockup.html:22 ยังคงมีผลต่อการอ้างว่าระบบพร้อมใช้งาน การสรุป INPUT_READY ครั้งนี้อาศัยข้อกำหนดเฉพาะการรันที่จำกัดอยู่ที่เอกสาร/offline mock ไม่ใช่การลบล้างหลักฐานเดิม
- แผนงาน AI ต้องแยกจาก state machine รายการ/ออเดอร์/ชำระเงิน/โต๊ะ; การเปลี่ยนสถานะงานในแผนไม่เปลี่ยนสถานะธุรกิจ

ข้อค้างไฟล์และ mapping — แยกจากข้อค้างธุรกิจ

- ไฟล์หลัก ผลตรวจ upstream และเอกสารประกอบ state-machine.md/structure.md มีครบตาม manifest ไม่พบหลักฐานจำเป็นของการตรวจสำเนารอบนี้หาย
- ไม่มี input-source.md ภายในชุดนี้; ข้อกำหนดเฉพาะรอบให้ตรวจพร้อม provenance.md จึงใช้ provenance เป็น manifest และบันทึก mapping นี้โดยไม่สร้างไฟล์ต้นทางทดแทน: input/fr-nfr-input.md → fr-nfr.md; Flow รวม → flow.md; work/state-machine.md → state-machine.md; work/structure.md → structure.md; UI LAB 004 → ui-mockup.html คู่กับ ui-contract.md
- hash ในรายการแหล่งข้อมูลประวัติของ Flow เช่น work/state-machine.md และ work/structure.md เป็น hash ก่อนกรอง จึงไม่ใช่ expected hash ของสำเนาปัจจุบัน ใช้ SHA ใน provenance ของชุดนี้ตรวจสำเนา และคงประวัติเดิมโดยไม่แก้ไข
- ลิงก์เอกสารราย node/JSON, review-record, เอกสารต้นทาง และ ../provenance.md ที่ไม่มีในสำเนาไม่ได้ตามไปอ่าน ไม่อ้างว่าตรวจไฟล์เหล่านั้นแล้ว ข้อจำกัดนี้เป็น nonblocking สำหรับงานเอกสารตามคำสั่งรอบนี้ แต่ยังไม่พิสูจน์สายที่มาภายนอกชุดหรือผลรันหลังกรองอย่างอิสระ

หลักฐานที่ใช้จริง

1. input/README.md เฉพาะส่วนที่มา/วิธีเตรียมสำเนา (บรรทัด 3–70) และสัญญาแผน/ประวัติ (82–105); ไม่อ่าน README หลักของ LAB และไม่ตามลิงก์ออกไป
2. provenance.md และทั้ง 10 ไฟล์ในตาราง SHA ของ manifest: fr-nfr.md, flow.md, state-machine.md, structure.md, ui-mockup.html, ui-contract.md, us-initial.md, fr-check.json, flow-check.json, ui-check.json
3. ผลตรวจใน session นี้: คำนวณ SHA-256 10/10 ตรง manifest, นับชุด US/FR/coverage, ตรวจข้อความ FR/AC ที่คัดใน Flow/state, ตรวจขอบเขตเนื้อหา และตรวจ source UI เทียบสัญญา ทั้งหมดเป็นการตรวจไฟล์ ไม่ใช่ผลทดสอบระบบ

การส่งต่อให้ Planner

ส่งเฉพาะ input-audit.md นี้และ baseline ที่ตรวจแล้ว ได้แก่ provenance.md พร้อม 10 ไฟล์ที่มี hash ในตาราง ไม่ส่ง scope-filter.diff, ต้นฉบับก่อนกรอง, reveal หรือไฟล์ประวัตินอกสำเนา ไม่สร้าง FR, Flow หรือ plan-v1 ทดแทนในขั้นนี้

Planner ต้องคงงาน verify ความสอดคล้องหลัง scope projection ใน plan-v1 พร้อมอ้าง hash ชุดนี้ แยก reuse/recheck และข้อจำกัดให้ตรงหลักฐาน ไม่แปลงผล upstream เป็นผลตรวจใหม่ เก็บแผนเป็น snapshot และเก็บผลปฏิบัติงาน/ประเมินใน execution/evaluations ตามสัญญาแผน การวางงานดังกล่าวเป็นข้อเสนอการตรวจ ไม่ใช่ AC ธุรกิจใหม่

สิ่งที่ยังไม่ทดสอบ: ไม่รัน checker FR/Flow ใหม่, ไม่รัน browser/Playwright หรือ smoke checks ของ HTML สำเนานี้, ไม่พิสูจน์ทุก mapping หลังกรอง, ไม่ทดสอบ LAN/Wi-Fi หลายอุปกรณ์ ความเร็ว/โหลด สูตร ETA และสัดส่วนตัวอย่างจริง การติดตั้ง Ubuntu การถอดอินเทอร์เน็ต ความปลอดภัยจริง หรือการชำระเงินจริง ไม่มีการใช้บัญชีจริงหรือบริการชำระเงินจริง

ไฟล์ที่สร้างจริงในขั้นนี้มีเพียง reference/step-00-input/baseline-filtered-v2/input-audit.md; ไม่แก้ไฟล์ baseline หรือหลักฐานเดิม
