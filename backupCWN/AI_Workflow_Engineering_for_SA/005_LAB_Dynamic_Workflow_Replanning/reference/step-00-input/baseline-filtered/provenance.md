# ที่มาของข้อมูล — ใช้ผลอ้างอิง

ใช้สำเนาตาม path จริง ไม่เปลี่ยนต้นทาง; พื้นที่ work ใน prompt ถูกย้ายมา reference/session เพื่อจำกัดการเขียนไฟล์ตามขอบเขตการรันนี้

| ต้นทาง | สำเนา | SHA-256 |
|---|---|---|
| 002_LAB_Loop_FR_NFR/reference/final/fr-nfr-input.md | fr-nfr.md | da31640e540b825d4fec555627ea098f092daf4243d5d304fd4c32ae6db734cd |
| 003_LAB_Static_Graph_Flow_Structure/reference/step-04-merge/flows-merged.md | flow.md | 11a2bd2c3d5b3f13f0ab596618de6f011a1737be621b3bc7271471948235a449 |
| 003_LAB_Static_Graph_Flow_Structure/reference/step-02-state-machine/state-machine.md | state-machine.md | 01182925516cfd21bf24ab1b00291ecf952eb3371179a1714340903b27b9d57c |
| 003_LAB_Static_Graph_Flow_Structure/reference/step-03-structure/structure.md | structure.md | a6963600ae6fcf76a9726457cad0a38f2ac6f34f8c5ecb565ad1edafbce50cc7 |
| 004_LAB_Conditional_Graph_UI_Mockup/reference/final/ui-mockup.html | ui-mockup.html | d2b7bfa0cff5700d3ca07f611c03cfa0304c54eafb51387f125e95edd11f7803 |
| 004_LAB_Conditional_Graph_UI_Mockup/input/ui-contract.md | ui-contract.md | 294b660d2e39b3745344f225400eee57c02c25b6efb108a3a7ecce7cdd060e68 |
| 002_LAB_Loop_FR_NFR/reference/e1-set/step-02/round-2/check-report.json | fr-check.json | 1b0c604da9288ce926ba4c98eb258107b130f309f85b1ee96403e02ba0d0f98c |
| 003_LAB_Static_Graph_Flow_Structure/reference/check-report.json | flow-check.json | 3be4ccd3d045951e7c69e523e6ce2dfab052d45ece39d453741f310435d1c700 |
| 004_LAB_Conditional_Graph_UI_Mockup/reference/round-1/ui-check.json | ui-check.json | c09bf23c92abf0cd9c570f71ff890c1b572f8846c4d2ff8f5d2c3323be448af7 |

US ตั้งต้นคัดเฉพาะ 18 แถวจาก appendix-a-restaurant.md; รหัส US ที่ถูกอ้างภายในเซลล์ไม่ขยายขอบเขต
ผลตรวจ FR 108/108; Flow ดู flow-check.json โดยยังมีคำถามธุรกิจค้าง; UI 19/19 smoke checks เป็นผล upstream ไม่ใช่ผลรันใหม่
Flow ฉบับรวมเชื่อม state-machine.md และ structure.md ที่คัดจาก node ต้นทางเดียวกัน
ข้อสมมติในการรัน: ใช้ผลอ้างอิงที่ตรวจแล้ว; ไม่ยืนยันระบบจริงหรือผล LAN จาก mock-up


# Baseline ที่ปิดข้อมูลสำหรับขั้นแรก

ต้นทางเก็บครบใน parent; ชุดนี้ตัดเฉพาะส่วนข้อความที่อธิบายข้อมูลยังไม่เปิดออก ไม่แก้ FR/AC ตั้งต้น
| ไฟล์ | SHA-256 ชุดที่ใช้ |
|---|---|
| flow-check.json | 3be4ccd3d045951e7c69e523e6ce2dfab052d45ece39d453741f310435d1c700 |
| flow.md | 197204069563217cfc0c33dd66453c7396f40d9834ee42575110a331032cc702 |
| fr-check.json | 1b0c604da9288ce926ba4c98eb258107b130f309f85b1ee96403e02ba0d0f98c |
| fr-nfr.md | da31640e540b825d4fec555627ea098f092daf4243d5d304fd4c32ae6db734cd |
| state-machine.md | fd397f74322233e740ed5319c1d7ca87f7291d11bd186c48563c8e7f02b118ee |
| structure.md | ac8cb1f7358eb57c5881d5e4320e0e77b2853520a4d35bff214c3b8777b69865 |
| ui-check.json | c09bf23c92abf0cd9c570f71ff890c1b572f8846c4d2ff8f5d2c3323be448af7 |
| ui-contract.md | 294b660d2e39b3745344f225400eee57c02c25b6efb108a3a7ecce7cdd060e68 |
| ui-mockup.html | d2b7bfa0cff5700d3ca07f611c03cfa0304c54eafb51387f125e95edd11f7803 |
| us-initial.md | 0774ad4090f007be09a4141cf7d6e78c0523828eef98d4041de3e86abfe3d689 |

ผลตรวจรอบแรก BLOCKED อยู่ ../input-audit.md; Planner รับเฉพาะ baseline-filtered และไม่อ่าน diff/ต้นฉบับที่ปิดข้อมูล
