# ผลลูป FR/NFR จากการรันจริง

ใช้ผลอ้างอิงจาก LAB 001: [fr-nfr-v0.md](../../001_LAB_Single_Prompt_Baseline/reference/step-02/round-1/fr-nfr-v0.md) ผลวันที่ 2026-09-14 10:28:10–10:31:52 UTC; มี [สำเนา baseline](step-01/round-1/fr-nfr-v0.md) และ [ที่มา/ข้อมูลรัน](run-meta.md)

เริ่ม 2026-09-14 11:01:00 UTC จบ 11:08:59 UTC ด้วย Codex CLI 0.154.0, gpt-6-astra (ตาม flag ที่สั่ง CLI ไม่ยืนยันกลับ), effort high (ค่าที่สั่งผ่าน flag) รัน session ใหม่ทีละขั้นตามลำดับ input/run-loop.sh และใช้ loop-support.py ตรวจตาราง/คะแนน/เหตุหยุด หยุดเมื่อ checker round-1 PASS 90/90 จึงไม่มี fixer หรือ checker รอบ 2–3

| ขั้น | Prompt | ผลนักศึกษา | ตัวอย่างอ้างอิง | ผลตรวจ | ข้อบกพร่อง | การแก้ไข | ขั้นถัดไป |
|---|---|---|---|---|---|---|---|
| 01 generator round-1 | [Generator](../prompts/step-01-generator.md) | | [v1 ฉบับเต็ม](step-01/round-1/fr-nfr-v1.md) | checker round-1: PASS 90/90 | ไม่พบข้อ FAIL จาก checker | ปรับวิธีตรวจและ traceability จาก v0 ในการสร้าง v1 | 02 checker round-1 |
| 02 checker round-1 | [Checker](../prompts/step-02-checker.md) + [เกณฑ์](../prompts/checker-criteria.md) | | [feedback ฉบับเต็ม](step-02/round-1/feedback.md) | PASS 90/90; FAIL 0 คู่ | ไม่พบข้อที่ต้องแก้ตาม rubric; ยังมีคำถามรอยืนยัน | ไม่เรียก fixer เพราะผ่านแล้ว | หยุด: pass; ส่งต่อ v1 |

## เวลาและโทเคนจากแต่ละ log

| ขั้น/รอบ | ระยะเวลา (วินาที) | input_tokens | cached_input_tokens | output_tokens | reasoning_output_tokens | สถานะและหลักฐาน |
|---|---:|---:|---:|---:|---:|---|
| generator round-1 | 297 | 320575 | 279296 | 16797 | 564 | completed; [log](step-01/round-1/log.jsonl), [run-meta](step-01/round-1/run-meta.md) |
| checker round-1 | 173 | 377083 | 333056 | 9111 | 257 | completed; PASS 90/90; [log](step-02/round-1/log.jsonl), [run-meta](step-02/round-1/run-meta.md) |

รวม 2 calls, checker 1 รอบ, 470 วินาทีของการเรียก, wall ทั้งชุด 479 วินาที, input 697658 + output 25908 = 723566 โทเคน ไม่บวก cache หรือ reasoning ซ้ำ ทั้งสอง log มี turn.completed และไม่มี turn.failed ค่า SCORE ของ generator เป็น null เพราะไม่ได้ให้คะแนน ไม่ใช่คะแนนศูนย์

## ก่อน–หลังเทียบ LAB 001

| สิ่งที่เปรียบเทียบ | LAB 001: v0 | LAB 002: v1 / รอบสุดท้าย | หลักฐานและขอบเขต |
|---|---|---|---|
| จำนวน FR ในขอบเขตร่วม 18 US | 18 | 18 | นับแถว FR จริงและ ID ไม่ซ้ำ |
| จำนวน US ที่มี FR ในขอบเขตร่วม | 18 | 18 | อ่านคอลัมน์ US ของ FR ไม่ใช้ traceability แทน |
| จำนวน AC ที่มีตัวเลขในขอบเขตร่วม | 18 | 18 | หน่วยนับคือช่อง AC ต่อแถว FR; ไม่นับเลขในรหัสอ้าง |
| จำนวน FR / US ที่มี FR / ช่อง AC มีตัวเลข ทั้งไฟล์ | 26 / 26 / 26 | 18 / 18 / 18 | ขอบเขต LAB 002 ตัด 8 US ตาม Input; ไม่ใช่ regression |
| คะแนนเอกสารตามเกณฑ์ LAB 002 | ไม่ได้ตรวจ v0 ด้วย rubric นี้ | 90/90; PASS | LAB 001 มี self-check คนละเกณฑ์ จึงไม่แปลงคะแนน |
| ข้อ FAIL ของ LAB 002 รอบ 1 → รอบสุดท้าย | ไม่ใช้ผล LAB 001 เป็นรอบ 1 ของลูป | 0 → 0 คู่; round-1 คือรอบสุดท้าย | [รายงาน 90 คู่](step-02/round-1/feedback.md) |
| ผล self-check ตามเกณฑ์เดิม LAB 001 | ผ่าน 13 / ตรวจไม่ได้ 1 / ไม่ผ่าน 0 จาก 14 รายการ | ไม่ได้ใช้ self-check ชุดเดิมตรวจ v1 | [self-check LAB 001](../../001_LAB_Single_Prompt_Baseline/reference/step-03/round-1/self-check.md) |
| จำนวน CLI calls / รอบ checker ของลูป | 3 calls / ไม่มีรอบ checker แบบ LAB 002 | 2 calls / 1 รอบ | LAB 001 รวมวิเคราะห์ US ร่าง FR/NFR และ self-check |
| โทเคนรวม input + output ของแต่ละ LAB | 1,560,066 | 723,566 | LAB 001: 3 logs; LAB 002: loop-log.json; ไม่บวก cache ซ้ำ |
| เวลารวมการเรียก CLI (วินาที) | 875 | 470 | ผลรวม end_epoch − start_epoch ของ calls |
| wall ตั้งแต่เริ่ม call แรกถึงจบ call สุดท้าย (วินาที) | 875 | 479 | LAB 002 รวมช่วงส่งต่อ 9 วินาที; ไม่รวมการจัดเอกสารสรุป |
| ค่าใช้จ่ายเงินจริง | ไม่มีข้อมูล | ไม่มีข้อมูล | ไม่มีหลักฐานยอดเงินจริง ไม่คำนวณจากราคาเดา |

นับจากไฟล์จริงด้วย [count-evidence.py](count-evidence.py) และเก็บผลใน [document-counts.json](document-counts.json) รันซ้ำจากโฟลเดอร์ LAB ด้วย `python3 reference/count-evidence.py` จำนวน AC ในที่นี้คือช่อง AC ของ FR ที่มีตัวเลขอารบิก/ไทยหลังตัดรหัส US/FR/NFR/AC/Q/DI ออก ไม่ได้แยกแต่ละเงื่อนไขย่อยหรือรวม AC ใน NFR จึงเป็นตัวชี้วัดโครงสร้างที่ทำซ้ำได้ ไม่ใช่คะแนนความครบของกฎ

ค่าใช้จ่าย LAB 001 นับทั้ง 3 calls ที่มีจริงใน reference/step-01 ถึง step-03; เฉพาะ call สร้าง v0 ใช้ 398983 โทเคนและ 222 วินาที สอง LAB มีขอบเขตและงานต่างกัน จึงใช้ยอดรวมนี้แสดงภาระของชุดงานเท่านั้น ไม่สรุปว่าลูปถูกกว่าหรือเร็วกว่า Single Prompt จากตัวเลขนี้

## regression

ไม่พบ — checker รอบแรกเป็นรอบสุดท้าย จึงไม่มีผล checker ก่อนหน้าให้เทียบคู่ที่เคย PASS ข้อสรุปนี้ไม่ได้พิสูจน์ว่าการแก้หลายรอบปลอด regression เพราะชุดนี้ไม่ได้เรียก fixer การลดทั้งไฟล์จาก 26 เหลือ 18 US เป็นขอบเขตที่กำหนด ไม่ใช่ข้อหายระหว่างแก้

## ลูปช่วยตรงไหน และยังสรุปอะไรไม่ได้

- Generator ทำวิธีตรวจชัดขึ้น: [v0](step-01/round-1/fr-nfr-v0.md) และ [v1](step-01/round-1/fr-nfr-v1.md) แถว FR-10 คง 30 ออเดอร์/2 เครื่อง/3 รอบเหมือนเดิม แต่ v1 ระบุเก็บหลักฐานแยกรอบและไม่ใช้ค่าเฉลี่ยข้ามรอบกลบข้อผิดพลาด FR-15 ระบุว่าเห็นสถานะจ่ายแล้วอย่างเดียวไม่พิสูจน์ log ชื่อผู้ใช้และเวลาครบ
- Checker ให้หลักฐานรายคู่ 90 คู่และยืนยันหมวด NFR ที่เกี่ยวข้องครบ 15 รหัส ดู [feedback round-1](step-02/round-1/feedback.md) เงื่อนไขหยุดช่วยไม่ให้เรียก fixer หลัง PASS
- จำนวน FR, US ที่มี FR และช่อง AC มีตัวเลขในขอบเขตร่วมเป็น 18 → 18 ทั้งหมด baseline มีโครงสร้างนี้ครบอยู่แล้ว จึงไม่อ้างว่าลูปเพิ่ม coverage ตามตัวชี้วัดเหล่านี้
- ยังวัดประโยชน์ของการแก้ตาม Feedback ไม่ได้: ไม่มี FAIL ไม่มี fixer และไม่มีรอบตรวจซ้ำ จึงไม่มีหลักฐานว่าคะแนนเพิ่มหรือข้อบกพร่องลดลงจากการวนหลายรอบ
- PASS เป็นผลตรวจเอกสารตามเกณฑ์ที่อนุญาตให้เปิดคำถามเมื่อข้อมูลขาด ยังมีหมายเหตุ ก./ค./ช., รหัส US-14 ใน US-20, นิยามสถานะ “เสร็จแล้ว/พร้อมเสิร์ฟ” และรายละเอียดจุดเริ่มเวลา/เขตเวลา/การติดตั้งรอยืนยันตามท้าย feedback ไม่ใช่ผลทดสอบระบบจริง
- ผู้สร้างและผู้ตรวจใช้โมเดลเดียวกันคนละ session ความผิดพลาดอาจสัมพันธ์กัน และไม่ได้ตรวจ baseline ใหม่ด้วย rubric 90 คู่ จึงไม่สรุปการเปลี่ยนคะแนนของ v0 เป็น v1

## รูปแบบ log และการส่งต่อ

[loop-log.json](loop-log.json) เก็บทุก call ใน rounds พร้อม step/log/duration/usage/result/score เพื่อเทียบแต่ละ JSONL ส่วน [loop-log.schema-compatible.json](loop-log.schema-compatible.json) ใช้ schema เดิมที่ rounds เก็บเฉพาะ checker และ calls เก็บการเรียกทั้งหมด ข้อกำหนด rounds สองรูปแบบขัดกันเพราะ schema เดิมห้าม field เพิ่ม จึงเก็บสองมุมมองของหลักฐานชุดเดียวกันโดยไม่แก้ input/ หรือ prompts/ [loop-log-original.json](loop-log-original.json) คือ log จาก helper ก่อนย้าย work/ ซึ่งยังอ้าง path ขณะรัน

stop_reason = pass; เพดาน checker 3 รอบ คะแนนไม่เพิ่ม 2 รอบติด และเวลา 1800 วินาที ไม่ถึงเพดานใด เรียกจริง 1 รอบจึงมี no_improvement_streak = 0 รายงานปิดท้ายด้วย RESULT/SCORE ถูกต้อง ไม่พบข้อบกพร่องรูปแบบ prompt ในการรันนี้

ส่งต่อ [final/fr-nfr-input.md](final/fr-nfr-input.md) ซึ่งตรงกับ v1 แบบ byte-for-byte พร้อม feedback รอบ 1 ให้ LAB 003/005 เลือกใช้โดยบันทึก “ใช้ผลอ้างอิง” ไม่แก้ไฟล์ของ LAB ปลายทางเอง work/ เหลือ .gitkeep เท่านั้น กิจกรรมเพิ่มเกณฑ์ E1 ยังไม่ได้รัน เพราะชุดนี้ต้องคง prompt และ Input เดิม
