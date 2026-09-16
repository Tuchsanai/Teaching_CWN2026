# ผลทดลองใหม่และการประเมิน
สรุปจาก metadata ณ 2026-09-12T14:06:04.533850+00:00 · [อ่านหลักฐานแบบเปิดดูได้](index.html) · [CSV](scores.csv) · [usage ทั้งหมด](usage-summary.json)
[ตัวชี้วัดเฉพาะ Lab](lab-metrics.html) · [ผลการใช้ C](transfer-review.html)
## ข้อค้นพบที่ใช้สอนได้
Lab1 และ Lab2 ครบ 12 เกณฑ์ทั้ง P/S ใน A/B; Lab1 ฝั่ง Skill มีคำว่า “ขอ取消ออเดอร์” ปนในสองร่าง แม้คะแนนความครบถ้วนเต็ม จึงต้องตรวจภาษาเพิ่มก่อนใช้ ไม่แก้ไฟล์ raw เพื่อทำให้ผลสวย
Lab3 ตามรูบริกเดิม P=10/12 และ S=11/12 ทั้ง A/B แต่ข้อคิวทับกัน: แก้วร้าวอาจเป็นความเสี่ยง P1 และข้อความของเสียที่ข้อมูลขาดอาจจัด P2 เบื้องต้นได้ จึงมี sensitivity แบบ post-hoc (วิเคราะห์เพิ่มเติมหลังเห็นผล) ที่รับเหตุผลดังกล่าวอย่างเท่าเทียม ซึ่งทั้งสองฝ่ายได้ 12/12 ความต่างหนึ่งคะแนนไม่ใช่หลักฐานว่า Skill เหนือกว่าโดยทั่วไป
Lab2 ทุกเงื่อนไขเลือก start/rollback ตรงเหตุและขอหลักฐาน known-good v1 ก่อนลงมือเมื่อ snapshot ไม่ให้ผลนั้น ถือเป็นการขอข้อมูลที่เหมาะสม AI ไม่ได้รันบริการจริง; ภาพและเลขจองที่ผ่านเป็นการทดสอบ runtime อัตโนมัติแยกต่างหาก ดู [snapshot ต้นทาง runtime](browser/pilot-runtime) และผลล่าสุดใน browser/
## ตารางร่างดิบกับคะแนนประเมิน
คะแนนในตารางเป็นผู้จัดทำแพ็กเกจ (AI worker) อ่านเทียบรูบริกและต้นทาง ไม่ใช่ AI ใน trial ให้คะแนนตนเอง และยังไม่มีผู้ประเมินมนุษย์อิสระ คะแนนฉบับแก้/accuracy รายข้ออ้าง/เวลาคน/คำใบ้/การแก้ของมนุษย์ = not-measured
| Trial / ร่างดิบ | ประเมินร่างแรก /12 | sensitivity /12 | ฉบับแก้ | วินาทีเครื่อง | native read |
|---|---|---|---|---|---|
| [lab1-A-P](experiments/lab1-A-P/answer.md) · [รายข้อ](experiments/lab1-A-P/evaluation.md) | 12 | 12 | not-measured | 85.552 | None |
| [lab1-A-S-confirmed](experiments/lab1-A-S-confirmed/answer.md) · [รายข้อ](experiments/lab1-A-S-confirmed/evaluation.md) | 12 | 12 | not-measured | 80.822 | True |
| [lab1-B-P](experiments/lab1-B-P/answer.md) · [รายข้อ](experiments/lab1-B-P/evaluation.md) | 12 | 12 | not-measured | 88.659 | None |
| [lab1-B-S-confirmed](experiments/lab1-B-S-confirmed/answer.md) · [รายข้อ](experiments/lab1-B-S-confirmed/evaluation.md) | 12 | 12 | not-measured | 78.509 | True |
| [lab2-A-P](experiments/lab2-A-P/answer.md) · [รายข้อ](experiments/lab2-A-P/evaluation.md) | 12 | 12 | not-measured | 74.174 | None |
| [lab2-A-S](experiments/lab2-A-S/answer.md) · [รายข้อ](experiments/lab2-A-S/evaluation.md) | 12 | 12 | not-measured | 70.564 | True |
| [lab2-B-P](experiments/lab2-B-P/answer.md) · [รายข้อ](experiments/lab2-B-P/evaluation.md) | 12 | 12 | not-measured | 72.467 | None |
| [lab2-B-S](experiments/lab2-B-S/answer.md) · [รายข้อ](experiments/lab2-B-S/evaluation.md) | 12 | 12 | not-measured | 68.96 | True |
| [lab3-A-P](experiments/lab3-A-P/answer.md) · [รายข้อ](experiments/lab3-A-P/evaluation.md) | 10 | 12 | not-measured | 71.075 | None |
| [lab3-A-S-confirmed](experiments/lab3-A-S-confirmed/answer.md) · [รายข้อ](experiments/lab3-A-S-confirmed/evaluation.md) | 11 | 12 | not-measured | 74.476 | True |
| [lab3-B-P](experiments/lab3-B-P/answer.md) · [รายข้อ](experiments/lab3-B-P/evaluation.md) | 10 | 12 | not-measured | 72.175 | None |
| [lab3-B-S-confirmed](experiments/lab3-B-S-confirmed/answer.md) · [รายข้อ](experiments/lab3-B-S-confirmed/evaluation.md) | 11 | 12 | not-measured | 80.246 | True |

## เวลารอบหลัก (หนึ่งครั้งต่อชุด ไม่มีนัยสำคัญทางสถิติ)
| Lab | P: A/B วินาที | S: A/B วินาที |
|---|---|---|
| lab1 | 85.552 / 88.659 | 80.822 / 78.509 |
| lab2 | 74.174 / 72.467 | 70.564 / 68.96 |
| lab3 | 71.075 / 72.175 | 74.476 / 80.246 |

## รอบที่ไม่ใช้สรุปความต่าง และรอบถ่ายโอน
| Trial | สถานะ | วินาที | เหตุที่แยก |
|---|---|---|---|
| [lab1-A-S](experiments/lab1-A-S/answer.md) | สำเร็จ | 74.68 | CLI เลือกชื่อ Skill แต่ JSONL ไม่มี file-read event จึงยังยืนยัน native ไม่ได้ ไม่นับในตารางหลัก |
| [lab1-B-S](experiments/lab1-B-S/answer.md) | สำเร็จ | 75.288 | CLI เลือกชื่อ Skill แต่ JSONL ไม่มี file-read event จึงยังยืนยัน native ไม่ได้ ไม่นับในตารางหลัก |
| [lab1-C-S-transfer](experiments/lab1-C-S-transfer/answer.md) | สำเร็จ | 81.246 | C: การใช้ซ้ำในบริบทใหม่ ดู transfer-review แยก |
| [lab2-C-S-transfer](experiments/lab2-C-S-transfer/answer.md) | สำเร็จ | 73.721 | C: การใช้ซ้ำในบริบทใหม่ ดู transfer-review แยก |
| [lab3-A-S](experiments/lab3-A-S/answer.md) | สำเร็จ | 91.864 | CLI เลือกชื่อ Skill แต่ JSONL ไม่มี file-read event จึงยังยืนยัน native ไม่ได้ ไม่นับในตารางหลัก |
| [lab3-B-S](experiments/lab3-B-S/answer.md) | สำเร็จ | 66.261 | CLI เลือกชื่อ Skill แต่ JSONL ไม่มี file-read event จึงยังยืนยัน native ไม่ได้ ไม่นับในตารางหลัก |
| [lab3-C-S-transfer](experiments/lab3-C-S-transfer/answer.md) | สำเร็จ | 65.249 | C: การใช้ซ้ำในบริบทใหม่ ดู transfer-review แยก |

รอบ native เดิมสี่รอบไม่ได้ล้มเหลวในการตอบ แต่ไม่ผ่านเกณฑ์หลักฐานการอ่านไฟล์ จึงเปิดเผยและรัน S-confirmed เพิ่มอีกสี่รอบโดยใส่คำขอให้เปิดอ่าน SKILL.md อย่างชัดเจน เก็บรอบเดิมครบ ไม่มีการ retry paid failure เงียบ ๆ ผล main จึงมีลำดับเวลา S ที่ช้ากว่า P ใน Lab1/3 และมี instrumentation เพิ่ม เป็นข้อจำกัดการเปรียบเทียบเวลา/โทเคน
## ต้นทุนที่แยกไว้
จำนวนคำขอทดลอง/สาธิตที่มี raw logs ครบใน experiments และ creation: **22**; input **997,119**, cached input **829,312**, output **44,430**, reasoning output **3,712**; input + output **1,041,549** โทเคนตาม CLI
cached input เป็นส่วนหนึ่งของ input และ reasoning เป็นรายละเอียดของ output ไม่บวกซ้ำ ไม่คำนวณราคา subscription จากราคา API ค่า input ของ CLI สะสมตามการทำงานหลาย tool turns และอาจมี cached context; S-confirmed มีต้นทุนเปิดอ่านเพื่อพิสูจน์ gate เพิ่ม ไม่ถือว่าเป็นต้นทุน Skill โดยธรรมชาติทั้งหมด
ต้นทุนเตรียม input-only directory วัดจริงแยกใน [launcher-prepare-checks.json](build/launcher-prepare-checks.json) เป็นเวลาสคริปต์ ไม่ใช่เวลาติดตั้งเครื่องทั้งห้อง เวลาคนติดตั้ง/ออกแบบ Skill/เขียนคำขอ/ตรวจร่างไม่ได้วัด ไม่ประมาณเป็นศูนย์
| สาธิต AI สร้าง/ปรับ Skill | วินาทีเครื่อง | ผล |
|---|---|---|
| [create](creation/create/answer.md) | 83.508 | exit 0 |
| [improve](creation/improve/answer.md) | 71.123 | exit 0 |
| [rerun-C](creation/rerun-C/answer.md) | 105.185 | exit 0 |

การสาธิตสร้าง/ปรับ/ทำ C ใหม่ใช้ launcher จริง อยู่หลังการทดลองหลัก แยกเป็นต้นทุนสร้างและบำรุงรักษา ตัวอย่าง flawed v1 ของการ hard-code วันเป็นตัวอย่างผู้สอนแต่งที่ติดป้าย ไม่อ้างว่าเป็นความผิดที่โมเดลทำจริง ผล C หลังปรับเป็น assisted transfer เพราะผู้สร้าง Skill มีข้อมูล C อยู่แล้ว
## ข้อจำกัดและเงื่อนไขปรับปรุง
นี่คือ technical pilot ไม่ใช่การศึกษากับผู้เรียนจริง มีหนึ่ง sample ต่อเงื่อนไข/ชุด การสลับลำดับ P-A/S-B/S-A/P-B ใช้ในการออกแบบและรอบเริ่มต้น แต่การยืนยัน native เพิ่มทำให้ลำดับผล main ของ Lab1/3 ไม่สมดุลเต็มที่ ไม่วิเคราะห์นัยสำคัญ ไม่อ้างลดเวลาคนหรือจำนวนการแก้ที่ไม่ได้วัด
ผู้จัดทำ AI worker เป็นผู้ประเมินเอง ไม่ blind; รูบริกคิว Lab3 มีส่วนทับกัน; ความยาวคำตอบ คำขอ native gate เครือข่าย และ cache ต่างกัน; input directories เป็นการแยกบริบท ไม่ใช่ OS sandbox ตรวจ trace ว่าอ่านเฉพาะข้อมูล/คู่มือ/Skill ที่ให้ ดู [package audit](build/package-audit.json)
การศึกษาต่อควรล็อกกติกาคิวที่ชัดก่อนเริ่ม เก็บ rubric/hash ก่อนดูผล ทำซ้ำหลายกลุ่มกับข้อมูลใหม่ ให้คนตรวจแบบไม่เห็น P/S และนับเวลา/คำใบ้/การแก้จริง แยกเวลาสร้างและปรับ Skill แล้วค่อยตัดสินความคุ้มจากการใช้ซ้ำ
