# Input audit — ขั้น 5.0

ผลสรุป: **BLOCKED** — หยุดก่อน plan-v1 และไม่ส่ง baseline ชุดนี้ให้ Planner ผลตรวจ hash และหลักฐาน upstream ครบ แต่ Flow และเอกสารประกอบมีข้อความเนื้อหาของ US ที่กันไว้นอก 18 แถวอยู่ในทะเบียนสมมติฐาน/ข้อค้าง การติดป้าย “ยังไม่ยืนยัน” ไม่ทำให้เนื้อหาที่เปิดเผยแล้วกลายเป็นเพียงรหัสอ้างอิง

ตรวจวันที่ 2026-09-14 โดยใช้ผลอ้างอิงตาม provenance จริง ไม่เลือกรุ่นจากเลขสูงสุด ไม่สร้าง FR/Flow ทดแทน และไม่แก้ US/AC ตัวเลข หน่วย หรือสัดส่วนทดสอบ

ใช้ข้อกำหนดเฉพาะการรันผลอ้างอิงเป็นขอบเขต: อ่านเฉพาะสำเนา baseline, provenance และผลตรวจที่ระบุ ไม่อ่าน README ของ LAB หรือ input/README.md ไม่อ่าน reveal ไม่ตามลิงก์ไปต้นทาง และไม่เรียก agent/CLI เพิ่ม สร้างไฟล์นี้ใน cwd ที่กำหนดโดยเปิดไฟล์แบบห้ามเขียนทับ

| ชิ้นงาน | ที่มา | hash | ผลตรวจ | ข้อค้าง | พร้อมส่งต่อ |
|---|---|---|---|---|---|
| FR/NFR: `fr-nfr.md` | `002_LAB_Loop_FR_NFR/reference/final/fr-nfr-input.md` | SHA-256 `da31640e540b825d4fec555627ea098f092daf4243d5d304fd4c32ae6db734cd` — ตรง provenance | หัวเอกสาร v1; ใช้ผลอ้างอิง LAB 002 final ตาม provenance; fr-check.json รายงาน PASS 108/108, failed 0, regressions ว่าง; มี FR 18 แถวและ coverage ตรง US ตั้งต้น | คำถาม Q-01–Q-26 ตามรหัสที่มีในต้นฉบับ; ยังไม่ทดสอบระบบจริง | รายชิ้นพร้อมวิเคราะห์; ระงับส่งต่อทั้งชุด |
| Flow รวม: `flow.md` | `003_LAB_Static_Graph_Flow_Structure/reference/step-04-merge/flows-merged.md` | SHA-256 `11a2bd2c3d5b3f13f0ab596618de6f011a1737be621b3bc7271471948235a449` — ตรง provenance | ใช้ผลอ้างอิง LAB 003 step-04-merge; merge 30 flows, coverage 18 US; schema_errors ว่างและ scope/hash/evidence checks เป็น true ตาม upstream; เนื้อหาระบุ READINESS: BLOCKED | พบเนื้อหาที่กันไว้ใน A-04/A-05; ข้อค้างธุรกิจ MC-01–MC-03 ยัง unresolved | ไม่พร้อม |
| เอกสารประกอบ Flow: state machine: `state-machine.md` | `003_LAB_Static_Graph_Flow_Structure/reference/step-02-state-machine/state-machine.md` | SHA-256 `01182925516cfd21bf24ab1b00291ecf952eb3371179a1714340903b27b9d57c` — ตรง provenance | ใช้ผลอ้างอิง LAB 003 step-02-state-machine; hash ตรงทั้ง provenance และ flow.md:28; upstream ตรวจ node เสร็จ ไม่มี schema error | พบเนื้อหาที่กันไว้ใน A-04/A-05; transition และ mapping ยังไม่ยืนยัน | ไม่พร้อม |
| เอกสารประกอบ Flow: structure: `structure.md` | `003_LAB_Static_Graph_Flow_Structure/reference/step-03-structure/structure.md` | SHA-256 `a6963600ae6fcf76a9726457cad0a38f2ac6f34f8c5ecb565ad1edafbce50cc7` — ตรง provenance | ใช้ผลอ้างอิง LAB 003 step-03-structure; hash ตรงทั้ง provenance และ flow.md:31; upstream ตรวจ node เสร็จ ไม่มี schema error | พบเนื้อหาที่กันไว้ใน A-04/A-05; โครงสร้าง/สิทธิ์บางส่วนยังเป็นข้อเสนอ | ไม่พร้อม |
| UI Mock-up: `ui-mockup.html` | `004_LAB_Conditional_Graph_UI_Mockup/reference/final/ui-mockup.html` | SHA-256 `d2b7bfa0cff5700d3ca07f611c03cfa0304c54eafb51387f125e95edd11f7803` — ตรง provenance | ใช้ผลอ้างอิง LAB 004 final; ui-check.json จาก round-1 รายงาน smoke checks ผ่าน 19/19, failed 0, edge pass; เป็นผล upstream | US-07 ยังประมาณเวลาไม่ได้; US-26 ไม่มีการติดตั้ง/บริการจริง; fixture ไม่ยืนยันกฎธุรกิจ | รายชิ้นใช้ตรวจ mock ได้; ระงับส่งต่อทั้งชุด |
| สัญญา UI: `ui-contract.md` | `004_LAB_Conditional_Graph_UI_Mockup/input/ui-contract.md` | SHA-256 `294b660d2e39b3745344f225400eee57c02c25b6efb108a3a7ecce7cdd060e68` — ตรง provenance | ใช้ผลอ้างอิง fixture จาก LAB 004 input; hash ตรง provenance; ใช้ชื่อสถานะและข้อค้าง DI-04/A-03, DI-07/A-05 สอดคล้องกับ HTML | ไม่ใช่ AC ธุรกิจเพิ่มเติม; ข้อจำกัด mock และการตรวจเพิ่มตามท้ายสัญญา | ประกอบ UI ได้; ระงับส่งต่อทั้งชุด |
| หลักฐานตรวจ FR: `fr-check.json` | `002_LAB_Loop_FR_NFR/reference/e1-set/step-02/round-2/check-report.json` | SHA-256 `1b0c604da9288ce926ba4c98eb258107b130f309f85b1ee96403e02ba0d0f98c` — ตรง provenance | ใช้ผลอ้างอิง e1-set/step-02/round-2; JSON อ่านได้; PASS 108/108; base 90 และ e1 18; regression 92 คู่ ไม่มี regression | เป็นหลักฐาน upstream ที่ provenance ผูกไว้; JSON ไม่บรรจุ hash ของ FR เป้าหมายโดยตรง | หลักฐานครบตามชุดที่อนุญาต |
| หลักฐานตรวจ Flow: `flow-check.json` | `003_LAB_Static_Graph_Flow_Structure/reference/check-report.json` | SHA-256 `3be4ccd3d045951e7c69e523e6ce2dfab052d45ece39d453741f310435d1c700` — ตรง provenance | ใช้ผลอ้างอิง LAB 003; ทั้ง 6 node execution_completed=true, schema_errors ว่าง; original_files_unchanged=true | merge ยัง unresolved 3; ผล scope_ok ของ upstream ไม่หักล้างเนื้อหาหลุดที่ตรวจพบครั้งนี้ | หลักฐานครบ; ไม่ใช่การอนุมัติธุรกิจ |
| หลักฐานตรวจ UI: `ui-check.json` | `004_LAB_Conditional_Graph_UI_Mockup/reference/round-1/ui-check.json` | SHA-256 `c09bf23c92abf0cd9c570f71ff890c1b572f8846c4d2ff8f5d2c3323be448af7` — ตรง provenance | ใช้ผลอ้างอิง LAB 004 round-1; checks 19 รายการผ่านทั้งหมด; scope ระบุ mock smoke checks | html ในรายงานอ้าง work/ui-mockup.html ขณะที่สำเนาจาก final; ผูกที่มาผ่าน provenance ไม่ได้ยืนยัน byte identity ของไฟล์ที่รันทดสอบจาก JSON โดยตรง | หลักฐานครบตามชุดที่อนุญาต; ไม่ใช่ผลรันใหม่ |
| US ตั้งต้น: `us-initial.md` | provenance ระบุคัดจาก `appendix-a-restaurant.md` เฉพาะ 18 แถว | SHA-256 `0774ad4090f007be09a4141cf7d6e78c0523828eef98d4041de3e86abfe3d689` — คำนวณครั้งนี้ | 18 แถวไม่ซ้ำ: US-01–US-08, US-10–US-13, US-15–US-16, US-19–US-20, US-25–US-26 | provenance ไม่ระบุ hash ต้นฉบับ/ผล extract แยก; ไม่อ้างว่าตรวจเทียบต้นทางแล้ว | ใช้เป็นขอบเขตตรวจ; ระงับส่งต่อทั้งชุด |
| บัญชีที่มา: `provenance.md` | บัญชีสำเนาของการรันผลอ้างอิงใน cwd | SHA-256 `4d363e3ba34085cb452c136235cb58dd49c799b12afa8a02246b3648deb19279` — คำนวณครั้งนี้ | ทั้ง 9 รายการที่ระบุ hash มีไฟล์และตรงทั้งหมด | เป็นคำรับรองที่มาภายในชุด input; ไม่ได้อ่านต้นทางซ้ำ | หลักฐานประกอบ audit |

## ขอบเขตและเนื้อหาที่เปิดเผยก่อนเวลา

นับจากรหัสคอลัมน์แรกของ `us-initial.md:3` ถึง `us-initial.md:20` เท่านั้น รวม 18 แถว; ตาราง coverage ใน FR และ us_coverage ของ Flow merge ตรงกัน การอ้าง US-14 ในเซลล์ US-20 ไม่เพิ่ม US-14 เป็นงาน และรายการรหัสที่กันออกไม่ถือเป็น reveal ไม่ใช้จำนวนการพบรหัสด้วย text search เป็นจำนวน US

เหตุหยุดที่พบจาก baseline โดยไม่อ่าน reveal:

| ตำแหน่งหลักฐาน | สิ่งที่พบและเหตุผล |
|---|---|
| `flow.md:514`, ซ้ำในประวัติ `flow.md:573`; `state-machine.md:210`; `structure.md:155` | A-05 อธิบาย “รอลูกค้าตัดสินใจ” เป็นสถานะรายการตาม US-14 ซึ่งไม่มีใน US ตั้งต้น 18 แถว เป็นเนื้อหาพฤติกรรม/สถานะนอกขอบเขต ไม่ใช่แค่รหัส US-14 ในเซลล์ US-20 แม้ระบุว่าเป็นข้อเสนอและยังไม่สร้าง transition ก็เปิดเผยเนื้อหาแล้ว |
| `flow.md:513`, ซ้ำในประวัติ `flow.md:572`; `state-machine.md:209`; `structure.md:154` | A-04 อธิบายการบันทึกค่าตั้งของ US-21 แยกตามสถานการณ์และความสัมพันธ์กับนิยาม US-07 เป็นรายละเอียดนอก 18 แถว ไม่ใช่รายการ excluded |
| `flow.md:312`; `state-machine.md:118`; `structure.md:128` | คำอธิบายขอบเขต state ยังนำสถานะรายการข้างต้นมาพูดถึง แม้ระบุไม่สร้างงานนั้น จึงต้องตรวจทั้งสมมติฐาน ประวัติ และข้อความประกอบเมื่อเตรียม baseline ใหม่ |

จุดเหล่านี้เพียงพอให้ BLOCKED ตามกติกาก่อน plan-v1; ไม่จำเป็นต้องเปิดเนื้อหา US ที่กันไว้เพื่อยืนยันซ้ำ ไม่แก้/ตัดข้อความต้นทางในรอบนี้ ผู้จัดเตรียมต้องจัดทำ baseline รุ่นใหม่ที่ไม่มีเนื้อหานอกขอบเขต พร้อม provenance/hash และหลักฐานตรวจที่สัมพันธ์กับรุ่นใหม่ แล้วตรวจ gate นี้อีกครั้งโดยเก็บชุดเดิมไว้

## ความสอดคล้องของรุ่นและขอบเขตหลักฐาน

FR มีหัวเอกสาร v1 แม้ถูกเก็บใต้ final; ใช้รุ่นนี้เพราะ provenance ระบุสำเนาและ hash พร้อมผลตรวจ round-2 ไม่ถือว่า final หรือเลขรอบสูงกว่าแปลว่าผ่านโดยอัตโนมัติ `flow.md:13` อ้าง hash FR ตรงกับ `fr-nfr.md` และ `flow.md:28,31` อ้าง hash state-machine/structure ตรงสำเนา จึงยืนยันความสอดคล้องของ dependency ทั้งสามรายการได้โดยตรง

UI ใช้ final จาก LAB 004 ตาม provenance และผลตรวจ round-1; contract เป็น fixture จาก LAB เดียวกัน HTML ยังคงข้อค้างสถานะ การแมป และขอบเขต mock สอดคล้องกับ Flow ไม่พบหลักฐานในชุดนี้ว่าใช้ข้อกำหนดคนละชุด แต่ไม่มี manifest ใน UI-check ที่ผูก hash FR/Flow/HTML ที่รันทดสอบโดยตรง จึงรับผล upstream ตาม provenance เท่านั้น ไม่อ้างว่าตรวจ chain จากต้นทางหรือรัน UI รุ่นนี้ซ้ำแล้ว

ผล FR 108/108 เป็นผลตรวจเอกสาร upstream; ผล Flow ตรวจ schema/coverage/evidence ไม่ใช่การคลี่คลายกฎธุรกิจ; ผล UI 19/19 เป็น smoke checks ไม่ใช่ผ่าน AC/NFR ทั้งหมด รอบนี้ตรวจการมีอยู่ อ่าน JSON คำนวณ SHA-256 เทียบ manifest ตรวจ coverage และอ่านข้อความ/โค้ดที่เกี่ยวข้องเท่านั้น

## ข้อค้างธุรกิจและส่วน UI ที่ยังไม่มี

| ประเภท | ข้อค้าง / ผลต่อการใช้ต่อ |
|---|---|
| ธุรกิจ | หมายเหตุ ก./ค./ช. ไม่มีนิยาม คงเป็นข้อค้าง ไม่เติมจากเว็บและไม่แต่ง AC |
| ธุรกิจ | MC-01: mapping “เสร็จแล้ว” กับ “พร้อมเสิร์ฟ” และจุดวัด ETA; MC-02: ทางเลือก PromptPay เมื่อปิดบริการและจุดเริ่มเวลา; MC-03: รหัสอ้างใน US-20 กับกฎปิด/เปิด ยัง unresolved ตาม `flow.md:239–241` |
| ธุรกิจ | คำถามใน `fr-nfr.md` ช่วงท้ายยังคงเดิม เช่น สเปกชุดทดสอบ ค่าเฉลี่ยเมื่อประวัติไม่พอ คำสั่งชนกัน/ซ้ำ การเปิดคืนหลายวัตถุดิบ เขตเวลาและ log เงื่อนไขปิดโต๊ะ สิทธิ์ และสภาพติดตั้ง ห้ามใช้พฤติกรรม fixture เป็นคำตอบธุรกิจ |
| UI ยังไม่มีจาก LAB ก่อน | US-07: `ui-mockup.html:346` แสดงว่ายังประมาณเวลาไม่ได้ เพราะ seed ไม่มีค่าเฉลี่ย 7 วันและต่อเมนู และ mapping ยังไม่ยืนยัน จึงไม่มี ETA ที่คำนวณครบตาม AC; ui-check ไม่มี check ของ US-07 |
| UI/ระบบยังไม่มีจาก LAB ก่อน | US-26: ไม่มีสคริปต์ติดตั้ง Ubuntu หรือบริการ/ข้อมูลถาวรจริงในชุด UI; mock ทำงานในหน่วยความจำและสลับบทบาทในแท็บเดียว; ui-check ไม่มี check ของ US-26 ไม่กำหนดหน้าติดตั้งใหม่แทนต้นฉบับ |
| ขอบเขต UI | หน้ารายงานเป็น placeholder ตรวจสิทธิ์ US-25 ตาม `ui-contract.md` และ `ui-mockup.html:356` ไม่ถือว่ารายงานเต็มเป็น input ที่หายหรือเพิ่มงานนอกขอบเขต |
| ไฟล์ / หลักฐาน | ไม่พบ file blocker ในชุดเฉพาะการรันนี้: baseline และ check ทั้งสามชิ้นมีครบ รวม state-machine/structure ตาม provenance ไม่พบ `input-source.md` ใน cwd แต่ข้อกำหนดเฉพาะให้ใช้ provenance และยืนยันว่าไม่มีไฟล์ต้องอ่านอื่น จึงไม่ตั้งไฟล์นี้หรือ README เป็น blocker เพิ่ม |
| Gate ก่อนเปิด reveal | มีเนื้อหาที่กันไว้หลุดใน baseline เป็น blocker ของการส่งต่อครั้งนี้ แยกจากข้อค้างธุรกิจและไม่ถูกยกเว้นด้วยผล upstream ที่ผ่าน |

ข้อค้างธุรกิจข้างต้นอาจให้วิเคราะห์/mock ต่อภายใต้ข้อจำกัดได้ตามโจทย์ แต่ gate เนื้อหาก่อน reveal ไม่ผ่าน จึงยังส่งชุดนี้ให้ Planner ไม่ได้ แผนงาน AI ต้องแยกจาก state machine ของรายการ/ออเดอร์/ชำระเงิน/โต๊ะ; รอบนี้ไม่ได้สร้างแผนหรือเปลี่ยน state machine

## หลักฐานที่ใช้และการส่งต่อ

รายการหลักฐานที่อ่านจริงและ hash อยู่ในตารางครบ 11 ไฟล์: `provenance.md`, `us-initial.md`, `fr-nfr.md`, `fr-check.json`, `flow.md`, `state-machine.md`, `structure.md`, `flow-check.json`, `ui-mockup.html`, `ui-contract.md`, `ui-check.json` เส้นทางต้นทางที่อยู่ในตารางเป็นข้อมูลจาก provenance ไม่ได้เปิดอ่านต้นทาง

สร้างจริงเพียง `input-audit.md` ใน cwd นี้ ส่งต่อได้เฉพาะรายงานผล BLOCKED เพื่อให้ผู้จัดเตรียมแก้ชุด input; ยังไม่มี baseline ชุดที่พร้อมส่งให้ Planner และไม่เริ่ม plan-v1 ไม่สร้างหรือเขียนทับไฟล์หลักฐานเดิม

ยังไม่ทดสอบ: ไม่รัน browser/smoke checks ใหม่ ไม่ตรวจ responsive/ฟิลด์รูป/หลายตัวเลือก/วันเปลี่ยน/หลายวัตถุดิบเพิ่มตามท้าย UI contract ไม่ทดสอบ LAN/Wi-Fi หลายเครื่อง โหลด เวลาและสัดส่วนตัวอย่างตาม AC ความแม่นยำ ETA ความปลอดภัยจริง การติดตั้ง Ubuntu หรือการทำงานออฟไลน์จริง และไม่ใช้บัญชีหรือการชำระเงินจริง
