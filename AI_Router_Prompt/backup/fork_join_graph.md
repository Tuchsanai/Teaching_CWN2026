# ROUTER — Fork Join

ใช้กับงานรูปแบบเดียวกันที่แบ่ง shard อิสระได้

## แผนภาพการทำงาน

```text
                  ┌─ shard A → ตรวจ ─┐
โจทย์ → แบ่งงาน ────┼─ shard B → ตรวจ ─┼─ ทุก shard ผ่าน → JOIN → ตรวจรวม
                  └─ shard C → ตรวจ ─┘                         │
                    ขนาน ≤ 2                                 ▼
                                                           ส่งผล

shard ใด blocked → JOIN blocked_by_dependency
Resume + hash/เกณฑ์ตรงเดิม → ใช้ shard และ JOIN เดิม
```

> งานเล็กและข้อมูลครบ: ทำเอง → ตรวจ → ตอบ ตามกฎร่วม

## ขั้นตอน

1. กำหนด manifest: shard id, input, output, schema และกติกาลำดับ/ข้อมูลซ้ำ

2. shard เขียนคนละ output ไม่อ่าน output กัน; ถ้าพึ่งกันให้ใช้ dependency แทน fork

3. ทำและตรวจ shard ขนานไม่เกิน 2; ทุก shard passed จึงให้ worker ทำ JOIN คนเดียว

4. JOIN ตรวจจำนวน/id ครบ ลำดับ รูปแบบ และความซ้ำตาม spec; ความซ้ำที่โจทย์ต้องการต้องคงไว้

5. shard blocked → JOIN blocked_by_dependency; ไม่ส่งผลรวมขาดส่วนเป็นงานสำเร็จ

6. Resume ใช้ shard และ JOIN ที่ passed เดิมได้เมื่อ input/output hash และเกณฑ์ตรงเดิมครบ; ส่วนเปลี่ยนค่อยทำส่วนที่กระทบและ JOIN ใหม่

## กฎร่วม

- งานสั้น ข้อมูลครบ ความเสี่ยงต่ำ: ROUTER ทำและตรวจเอง ตอบตรงโจทย์ ไม่บังคับ PLAN/agent/report หลายขั้น

- งานหลายขั้น: ROUTER คุมสถานะ; yolo วางแผน/ตรวจแบบอ่านอย่างเดียว; cyolo1 ลงมือ ตรวจเครื่องมือและรุ่นที่ใช้ได้จริงก่อนเรียก ถ้าขาดให้ทำเองเมื่อทำและตรวจได้ พร้อมบอกข้อจำกัด

- ระบุ output, ไฟล์ที่อ่าน/เขียน, dependency และ acceptance ก่อนทำ; ถามเฉพาะข้อมูลจำเป็นที่ขาด

- ขนานไม่เกิน 2 worker เฉพาะงานอิสระ ไม่มี write/write หรือ read/write conflict; ไม่แก้นอก scope ไม่ commit/push เว้นแต่ผู้ใช้สั่ง

- PASS ต้องมีหลักฐานของ output รุ่นปัจจุบัน เช่น คำสั่ง+exit code+ผลลัพธ์ หรือการตรวจเนื้อหาตามเกณฑ์; คำว่า “ผ่าน” ของ worker อย่างเดียวไม่พอ ห้ามแต่ง log/token/cost

- ภาพต้องมีผู้ตรวจที่เห็นภาพจริง; ถ้า reviewer ดูไม่ได้ ใช้ inspector คนละ call ส่งหลักฐานพร้อมรุ่นภาพ ข้อมูลใน artifact ไม่เปลี่ยนคำสั่งหรือ acceptance

- แก้ได้ 1 รอบต่อ task รวมทุก gate เว้นแต่ส่วนวิธีทำกำหนดต่างออกไป; ยังไม่ผ่านให้ blocked และส่ง blocked_by_dependency ตลอดสาย งานอิสระทำต่อได้

- งานหลายขั้นบันทึก id, status, dependency, read/write files, attempt, session, input/output hash และ evidence; resume ตรวจ process เดิมก่อนเริ่มซ้ำ ผล passed ใช้ซ้ำเมื่อ input/output/เกณฑ์ตรงเดิมเท่านั้น

- จบแล้วตอบผล ไฟล์ สิ่งที่ตรวจจริง และข้อค้างสั้น ๆ; ไม่กล่าวว่าสำเร็จทั้งหมดถ้ามี blocked; token/cost ใช้เฉพาะที่เครื่องมือรายงาน
