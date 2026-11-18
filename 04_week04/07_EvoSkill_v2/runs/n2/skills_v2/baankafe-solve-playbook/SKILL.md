---
name: baankafe-solve-playbook
description: ขั้นตอนเขียน solve.py สำหรับโจทย์ฟังก์ชันคิดเงินของร้าน BaanKafe (ราคา ส่วนลด VAT ค่าส่ง เงินคืน หารบิล) ให้ผ่านเทสต์ครบทั้ง Normal, Boundary, NoDrift และ Reject — ใช้ทุกครั้งที่ได้โจทย์ "ต้องการฟังก์ชัน ... ในไฟล์ solve.py"
---

# Playbook: เขียน `solve.py` ของ BaanKafe

ผลของ epoch ก่อนพบว่า Solver ได้แค่ ~0.4–0.6 เพราะคำนวณสูตรหลักถูก แต่ **พลาด 2 อย่างเสมอ**:
1. ไม่ตรวจ input → เทสต์กลุ่ม Reject (ต้อง `raise ValueError`) ตกหมด
2. ไม่รู้กติกาที่ "ไม่ได้เขียนในโจทย์" แต่เทสต์ตรวจ (ดู skill `baankafe-house-rules`)

**ผล epoch 1 (หลังใช้สกิลรอบแรก) ได้ 0.6–0.9 ยังไม่เต็ม สาเหตุที่เหลือ:**
- solve.py ที่ไม่มี `main()` (CLI อ่าน JSON จาก stdin) ได้แค่ ~0.7 ส่วนที่มี `main()` ได้ ~0.9 → **ต้องมี `main()` และบล็อก `if __name__ == "__main__": sys.exit(main())` เสมอ** (คัดลอกจาก `template_solve.py` ได้ทันที) รูปแบบผลลัพธ์: สำเร็จ → พิมพ์ `{"ok": true, "result": ...}` exit 0; ValueError/TypeError → พิมพ์ `{"ok": false, "error": "..."}` exit code 2
- ต้องส่งมอบ `test_solve.py` ที่ **ครบ** ด้วย (ผลงานเต็มคะแนนมี 2 ไฟล์: solve.py + test_solve.py) ดู `template_test_solve.py` — เดิมเขียนแค่ 3 เทสต์ ซึ่งน้อยเกินไป
- เคสนโยบายร้านใน `baankafe-house-rules` ที่ดูเหมือนขัดกับโจทย์ (เช่น silver ไม่ได้ x2 เดือนเกิด) **ต้องใช้ตามนโยบายร้าน** ไม่ใช่ปฏิเสธ — Solver ที่ปฏิเสธเสียคะแนน cashback ไป 0.1–0.2

ตัวตรวจให้คะแนนเป็นกลุ่ม: Normal / Boundary / NoDrift (ทศนิยมเพี้ยน-ปัดเศษ) / Reject (input ผิด) ต้องได้ครบทุกกลุ่ม

## ขั้นตอน
1. อ่านโจทย์ทีละบรรทัด ขีดเส้นใต้ทุกตัวเลข ขอบเขต ("ตั้งแต่ 0", "ตั้งแต่ 1", "0–100", "≥ 500 บาท") และทุก "ลำดับ" ของการคูณ/ลด/บวก
2. **แปลงหน่วย**: input/output เป็นสตางค์ (จำนวนเต็ม) แต่โจทย์พูดเป็นบาท → 500 บาท = 50000 สตางค์, 100 บาท = 10000, 200 บาท = 20000
3. อ่าน skill `baankafe-house-rules` ตัดสินกติกาปัดเศษและเงื่อนไขพิเศษ
4. เขียนด้วย `fractions.Fraction` ทั้งหมด (ห้าม float, ห้ามปัดกลางทาง) ปัดครั้งเดียวตอนท้าย
5. **ตรวจ input ทุกตัวแปรที่โจทย์ระบุประเภท/ช่วง** แล้ว `raise ValueError` (ดูแม่แบบ `template_solve.py`)
6. ทดสอบเอง: รัน `PYTHONPATH=. python3 -c "from solve import f; ..."` (หมายเหตุ `python3 -I` จะ import solve ไม่ได้) ลองค่า ขอบ ±1 ของทุกเกณฑ์, ค่าที่ทำให้เกิด .5 พอดี, ค่าผิดประเภท
7. เขียน `test_solve.py` (unittest) ให้ครบ 4 กลุ่มตาม `template_test_solve.py` อย่างน้อย 12 เทสต์: Normal ≥3, Boundary ≥3 (ทุกเกณฑ์ทั้งด้านที่ผ่านและไม่ผ่าน เช่น 49999/50000, 1000/1001, 9999/10000), NoDrift ≥2 (ค่าที่ปัดครึ่งแล้วต่างจากปัดทิ้ง/float), Reject ≥4 (ทุกพารามิเตอร์: ลบ/0, float, str, bool, tier ผิด) รวมเคสนโยบายซ่อนด้วย ค่าที่คาดหวังให้คำนวณมือด้วย Fraction แยกต่างหากแล้วใส่เป็นตัวเลขตายตัว แล้วรัน `python3 -m unittest -q test_solve` ให้ผ่าน
7.5 ทดสอบ CLI: `echo '{...}' | python3 solve.py` ต้องพิมพ์ JSON ok:true และ input ผิดต้อง exit 2
8. ในคำตอบสุดท้าย บอกสั้น ๆ ว่าตีความข้อที่โจทย์ไม่ชัดอย่างไร

## กฎตรวจ input (Reject) — สำคัญที่สุด
- จำนวนเต็ม: ต้อง `type(v) is int` (ปฏิเสธ `float` เช่น 4500.0, `str` เช่น "2", และ `bool` เพราะ `True` เป็น int ใน Python)
- ช่วงตามโจทย์: "ตั้งแต่ 0" → ต้อง ≥0, "ตั้งแต่ 1" → ≥1 (qty, people), "1–30,000" → ปฏิเสธ 0, ลบ, เกิน 30000, "0–100" → ปฏิเสธ -1, 101
- flag (`member`, `express`, `birthday`): ต้อง `type(v) is bool` ไม่รับ 0/1/"yes"
- enum (`tier`): ต้องเป็น `str` และอยู่ในชุดที่กำหนด ไม่งั้น ValueError
- list/dict: `items` ต้องเป็น list, แต่ละตัวต้องเป็น dict มี key ครบ ตรวจ price/qty ทีละตัว (qty ≥1, price ≥0)
- ใช้ `ValueError` เท่านั้น (ไม่ใช่ TypeError/KeyError/AssertionError) แม้ input จะผิดประเภท
- ตรวจ **ก่อน** คำนวณ และตรวจก่อน early-return (เช่น ก่อน `if amount < 10000: return 0`) เสมอ

## กฎความแม่นยำ (NoDrift)
- ใช้ `Fraction(num, den)` ของอัตรา (5% = 95/100, VAT = 107/100, 1.5% = 15/1000)
- ห้ามปัดระหว่างขั้น: คูณลดทุกขั้นแบบ exact แล้วปัดตอนจบ ยกเว้นโจทย์สั่งให้ปัดขั้นนั้นชัดเจน (ดู house-rules กรณี "ทิป")
- ฟังก์ชันปัด (x ≥ 0):
  - half-up: `int((Fraction(x)*2 + 1) // 2)`
  - floor: `int(Fraction(x) // 1)`
- ห้ามใช้ `round()` (ปัดแบบ banker) ห้ามใช้ `/` กับ int

## แม่แบบ
ดู `template_solve.py` และ `template_test_solve.py` ในโฟลเดอร์นี้ (helper `half_up`, `round_down`, `need_int`, `need_bool` และ `main()` อ่าน JSON จาก stdin) คัดลอกแล้วแก้ฟังก์ชันหลัก ไฟล์ solve.py ต้องมีฟังก์ชันชื่อตามโจทย์ระดับ module และ import ได้โดยไม่มี side-effect
