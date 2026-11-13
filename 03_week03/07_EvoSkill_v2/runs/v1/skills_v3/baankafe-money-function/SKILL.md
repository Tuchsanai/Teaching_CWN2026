---
name: baankafe-money-function
description: ใช้ทุกครั้งที่โจทย์ให้เขียนฟังก์ชันคิดเงิน/ราคา/ส่วนลด/ค่าส่ง/เงินคืน/หารบิล เป็นสตางค์ในไฟล์ solve.py (ร้าน BaanKafe) — บอกมาตรฐานการปัดเศษ การตรวจ input แบบเข้มงวด และขั้นตอนทดสอบก่อนส่ง
---

# เขียนฟังก์ชันคิดเงินสตางค์ (solve.py) ให้ผ่านตัวตรวจ

ตัวตรวจแบ่งเป็นกลุ่ม: **Normal / Boundary / NoDrift / Reject** + **ส่วน CLI (`main()`)** · ประวัติคะแนน: ไม่ทำอะไรเลย ~0.5 → ตรวจ input + half-up ได้ ~0.7 → เพิ่ม main() CLI + test_solve.py ได้ ~0.9–1.0 (ที่หลุดล่าสุดคือยอมรับ float ในพารามิเตอร์ตัวเลข) · ที่เคยขาด ~0.3 คือสิ่งที่ brief ไม่ได้เขียน แต่ตัวตรวจให้คะแนน: **`main()` CLI ใน solve.py** (ข้อ 4) และ **ไฟล์ `test_solve.py`** (ข้อ 6) · ต้องทำทุกข้อทุกครั้งแม้ brief ไม่พูดถึง

## 1) มาตรฐานปัดเศษ: half-up เสมอ
- ผลลัพธ์เป็นจำนวนเต็มสตางค์ ปัด **ครึ่งขึ้น (half up)** ห้าม floor / `int()` / `round()` ของ Python (banker's rounding) / float
- ห้ามใช้ float เด็ดขาด ใช้ `fractions.Fraction` หรือเลขจำนวนเต็มล้วน
- **ปัดครั้งเดียว ตอนท้ายสุด** ไม่ปัดระหว่างขั้น (เช่น ลด 5% → ลด 10% → VAT ให้คูณเป็นเศษส่วนต่อกันแล้วปัดทีเดียว) ยกเว้นโจทย์ระบุชัดว่าให้ปัดขั้นไหน
- แม้โจทย์ cashback/ค่าส่ง ไม่เขียนว่าปัดแบบไหน ก็ใช้ half-up (การใช้ floor ทำให้ NoDrift เช่น 10020 silver x2 ควรได้ 301 ไม่ใช่ 300 พลาด)
- เพดาน (max/cap) ใช้ `min(cap, ปัดแล้ว)` ; เกณฑ์ขั้นต่ำ/ขีดแบ่ง ตรวจจากค่า **ก่อนคำนวณ** ตามคำว่า "ตั้งแต่ = >=", "เกิน = >", "ไม่เกิน = <=", "ต่ำกว่า = <" อ่านให้ตรง ขอบเขตพอดีคือ Boundary test
- หน่วย: บาท→สตางค์ ×100 ; อัตรา % ใช้ `Fraction(p,100)`

## 2) ตรวจ input เข้มงวด → `raise ValueError` (Reject test)
ทุกพารามิเตอร์ต้องตรวจก่อนคำนวณ:
- จำนวนเต็ม: ต้อง `type(v) is int` — **ปฏิเสธ float (4500.0), str ('2'), bool (True), None** ทั้งหมด
- **ตัวเลขทุกตัวใน brief ถือเป็น int เท่านั้น แม้ brief ไม่ได้เขียนว่า "จำนวนเต็ม"** รวมถึงปริมาณที่ดูเหมือนค่าต่อเนื่อง เช่น ระยะทาง (กม.) น้ำหนัก (กรัม) เงิน (สตางค์) จำนวนคน/ชิ้น เปอร์เซ็นต์ → `distance_km=100.0` หรือ `100.5` ต้อง raise ValueError (เคยพลาด: ยอมรับ float ที่ distance_km เพราะ brief เขียนแค่ "ตั้งแต่ 0" แล้วเสีย 0.1) · อย่ายอม `(int, float)` และไม่ต้องกังวลเรื่อง nan/inf เพราะ float ถูกปฏิเสธทั้งหมดอยู่แล้ว · ข้อยกเว้นมีเฉพาะเมื่อ brief เขียนชัดว่ารับทศนิยม
- ใช้ helper `need_int(value, name, low, high)` ใน template.py กับ **ทุก** พารามิเตอร์ตัวเลข อย่าเขียนเช็กเองแบบหลวม ๆ
- ตรวจช่วงตามที่ brief ระบุ: เช่น qty ≥ 1, price ≥ 0, total ≥ 0, people ≥ 1, tip 0–100, weight 1–30000, distance ≥ 0, amount ≥ 0 (ค่าติดลบ/นอกช่วง → ValueError)
- bool flag (member, express, birthday): ต้อง `type(v) is bool` ไม่ใช่ 0/1 หรือ "yes"
- ค่าที่เป็น enum (เช่น tier): ต้องเป็น `str` และอยู่ในชุดที่อนุญาตเท่านั้น (ชื่ออื่น เช่น "bronze" → ValueError) ; ตรวจชนิดก่อน `in` เพื่อกัน unhashable
- list ต้องเป็น `type(items) is list` และแต่ละ item ต้องเป็น `dict` ที่มี key ครบ (ขาด key → ValueError ไม่ใช่ KeyError/TypeError) ; list ว่างให้คืน 0 ตามสูตร ถ้าโจทย์ไม่ห้าม
- ต้องเป็น **ValueError** เท่านั้น (ไม่ใช่ TypeError/KeyError/AssertionError)
- ตรวจให้ครบทุกพารามิเตอร์ก่อนจะ return อะไรก็ตาม (เช่น cashback ที่ amount < 100 บาท คืน 0 ได้ก็ต่อเมื่อ tier/birthday ผ่านการตรวจแล้ว)

## 3) หารบิล/แจกเศษ
ถ้าให้หารเท่ากันแล้วเศษ 1 สตางค์ให้คนแรก ๆ: `base, extra = divmod(grand, people)` → `[base+1]*extra + [base]*(people-extra)` ; ผลรวมต้องเท่ากับ grand เสมอ ; grand = half_up(total*(100+tip)/100)

## 4) ต้องมี `main()` CLI ท้ายไฟล์ solve.py (บังคับ — เคยขาดแล้วเสีย ~0.2)
- อ่าน JSON object จาก stdin → เรียกฟังก์ชันด้วย `fn(**args)` (key = ชื่อพารามิเตอร์)
- สำเร็จ: พิมพ์ `{"ok": true, "result": ...}` (json.dumps) แล้ว exit code 0
- `ValueError`/`TypeError` (รวม JSON ไม่ใช่ object): พิมพ์ `{"ok": false, "error": "ข้อความ"}` แล้ว exit code **2**
- ท้ายไฟล์ `if __name__ == "__main__": sys.exit(main())`
- ทดสอบจริง: `echo '{"items":[{"price":4500,"qty":2}],"member":false}' | python3 solve.py; echo $?` และเคสผิด (ต้อง exit 2)
- `from solve import fn` ต้องยังใช้ได้ (ห้ามรันอะไรตอน import)

## 5) แม่แบบ — คัดลอกจาก `template.py` ในโฟลเดอร์สกิลนี้ (รวม main) แล้วแก้ชื่อฟังก์ชัน/ตัวฟังก์ชัน ใส่ docstring ภาษาไทยสั้น ๆ ให้ฟังก์ชันและ helper

## 6) ขั้นตอนก่อนส่ง (ทำจริง ไม่ข้าม)
1. เขียน `solve.py` ในโฟลเดอร์ทำงาน (ชื่อฟังก์ชันตรง brief) พร้อม `main()` ตามข้อ 4
2. เขียน **`test_solve.py`** ไว้ข้าง ๆ (unittest, `from solve import <fn>`) แยก class Normal / Boundary / NoDrift / Reject ตามกลุ่มด้านบน: ค่าปกติ, ขอบเขตพอดี (เช่น 49999/50000), เคสเศษลงตรง .5 ต้องปัดขึ้น, reject = ค่าลบ, 0 ที่ต้อง ≥1, float, str, bool, enum ผิด ; คำนวณค่าคาดหวังด้วยมือ/Fraction อีกวิธี ไม่ใช่ copy จากผลของโค้ดตัวเอง
3. รัน: `PYTHONPATH=. python3 -m unittest -q test_solve` (หมายเหตุ: **อย่าใช้ `python3 -I`** เพราะตัด cwd ออกจาก path ทำให้ import solve ไม่เจอ) ให้ผ่านทั้งหมด แล้วรันทดสอบ CLI ตามข้อ 4
4. ตอบสรุปสั้น ๆ ว่าทำอะไร ทดสอบอะไรจริง
