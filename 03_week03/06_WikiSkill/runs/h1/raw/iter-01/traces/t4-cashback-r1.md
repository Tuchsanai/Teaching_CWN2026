# Trace t4-cashback-r1 · iteration 1

- ผล: **FAIL** · คะแนน 0.40 (ผ่าน 4 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 3 ครั้ง · คำสั่งล้ม 0 ครั้ง · อ่านสกิล: ไม่

## โจทย์

ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cashback(amount, tier, birthday)` ในไฟล์ `solve.py` สำหรับคิดเงินคืนสมาชิก
- `amount` = ยอดซื้อ (สตางค์ ตั้งแต่ 0) · `tier` = "silver" "gold" หรือ "platinum" · `birthday` = True คือซื้อในเดือนเกิด
- อัตราเงินคืน: silver 1.5% · gold 2.5% · platinum 4%
- ยอดซื้อต่ำกว่า 100 บาท ไม่ได้เงินคืน
- เดือนเกิด ได้เงินคืน 2 เท่า
- เงินคืนสูงสุด 200 บาทต่อบิล
- คืนเงินคืน เป็นจำนวนเต็มสตางค์

## ผลของตัวตรวจ (Grader)

- ✓ `contract`
- ✓ `basic`
- ✗ `half_up`: cashback(10020, "gold", false) คาด 251 ได้ 250 · พลาด 3 จาก 3 กรณี
- ✗ `no_drift`: cashback(10020, "silver", true) คาด 301 ได้ 300 · พลาด 3 จาก 3 กรณี
- ✓ `boundary`
- ✓ `reject_value`
- ✗ `reject_type`: cashback(20000.0, "gold", false) ต้อง raise ValueError แต่ raise TypeError · พลาด 4 จาก 5 กรณี
- ✗ `cli_ok`: stdin {"amount": 20000, "tier": "gold", "birthday": false} ต้องได้ {"ok": true, "result": 500} exit 0 แต่ได้ exit 0 stdout 0
150
300
20000
20000
0
250
- ✗ `cli_error`: stdin {"amount": 20000, "tier": "bronze", "birthday": false} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout 0
150
300
20000
20000
0
250
- ✗ `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py

## สิ่งที่ Agent ทำ

### ขั้น 1 · Bash

```
pwd && ls -la && (ls -la skills 2>/dev/null || echo "NO_SKILLS_DIR")
```

ผลที่ได้:

```
/workspace/wklab/suite/runs/h1-k01-train/t4-cashback-r1/sandbox
total 8
drwxr-xr-x 2 root root 4096 Nov 13 01:49 .
drwxr-xr-x 3 root root 4096 Nov 13 01:49 ..
NO_SKILLS_DIR
```

### ขั้น 2 · Write

```
/workspace/wklab/suite/runs/h1-k01-train/t4-cashback-r1/sandbox/solve.py
"""BaanKafe cashback calculator.

ยอดซื้อ (amount) และเงินคืน ใช้หน่วย "สตางค์" (1 บาท = 100 สตางค์) เป็นจำนวนเต็มทั้งหมด
เพื่อหลีกเลี่ยงปัญหาทศนิยมของ float
"""

# อัตราเงินคืนต่อระดับสมาชิก เก็บเป็นส่วนในพัน (permille) เพื่อใช้จำนวนเต็ม
# silver 1.5% = 15/1000, gold 2.5% = 25/1000, platinum 4% = 40/1000
RATE_PERMILLE = {
    "silver": 15,
    "gold": 25,
    "platinum": 40,
}

MIN_PURCHASE = 100 * 100      # ยอดซื้อขั้นต่ำ 100 บาท = 10,000 สตางค์
MAX_CASHBACK = 200 * 100      # เงินคืนสูงสุดต่อบิล 200 บาท = 20,000 สตางค์
BIRTHDAY_MULTIPLIER = 2       # เดือนเกิด ได้เงินคืน 2 เท่า


def cashback(amount, tier, birthday=False):
    """คำนวณเงินคืนสมาชิก (หน่วยสตางค์, จำนวนเต็ม)

    amount   : ยอดซื้อ หน่วยสตางค์ (int, >= 0)
    tier     : "silver" | "gold" | "platinum"
    birthday : True ถ้าซื้อในเดือนเกิด

    กติกา:
      1. ยอดซื้อต่ำกว่า 100 บาท -> ไม่ได้เงินคืน (0)
      2. เงินคืน = ยอดซื้อ * อัตราของระดับสมาชิก (ปัดทิ้งเศษเป็นสตางค์จำนวนเต็ม)
      3. เดือนเกิด -> คูณ 2
      4. จำกัดไม่เกิน 200 บาทต่อบิล
    """
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")

    key = tier.strip().lower() if isinstance(tier, str) else tier
    if key not in RATE_PERMILLE:
        raise ValueError(f"tier ไม่ถูกต้อง: {tier!r} (ต้องเป็น silver, gold หรือ platinum)")

    if amount < MIN_PURCHASE:
        return 0

    result = amount * RATE_PERMILLE[key] // 1000

    if birthday:
        result *= BIRTHDAY_MULTIPLIER

    return min(result, MAX_CASHBACK)


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน (หน่วยสตางค์)
    print(cashback(5000, "gold"))                 # 0   ต่ำกว่า 100 บาท
    print(cashback(10000, "silver"))              # 150 = 1.50 บาท
    print(cashback(10000, "silver", True))        # 300 = 3.00 บาท
    print(cashback(1000000, "platinum"))          # 20000 = 200 บาท (ถึงเพดาน)
    print(cashback(1000000, "platinum", True))    # 20000 = 200 บาท (ถึงเพดาน)
    print(cashback(333, "gold"))                  # 0   ต่ำกว่า 100 บาท
    print(cashback(10001, "gold"))                # 250 = 2.50 บาท (ปัดทิ้งเศษ)

```

ผลที่ได้:

```
File created successfully at: /workspace/wklab/suite/runs/h1-k01-train/t4-cashback-r1/sandbox/solve.py (file state is current in your context — no need to Read it back)
```

### ขั้น 3 · Bash

```
python3 solve.py && python3 -c "
from solve import cashback as c
assert c(0,'silver')==0
assert c(9999,'platinum')==0
assert c(10000,'silver')==150
assert c(10000,'gold')==250
assert c(10000,'platinum')==400
assert c(10000,'platinum',True)==800
assert c(1000000,'gold')==20000
assert c(1000000,'gold',True)==20000
assert c(15000,'silver',True)==450
assert c(10001,'gold')==250
assert c(100000,'silver')==1500
assert c(100000,'silver',True)==3000
assert c(100000,'platinum')==4000
print('all asserts passed')
"
```

ผลที่ได้:

```
0
150
300
20000
20000
0
250
all asserts passed
```

**Agent พูด:** สร้างไฟล์ `solve.py` ในโฟลเดอร์ปัจจุบันแล้ว และทดสอบผ่านทั้งหมด (โฟลเดอร์ `./skills` ไม่มีอยู่ จึงไม่มีสกิลให้อ่าน)

**ไฟล์:** `/workspace/wklab/suite/runs/h1-k01-train/t4-cashback-r1/sandbox/solve.py`

**วิธีคิด**
1. ยอดซื้อต่ำกว่า 100 บาท (10,000 สตางค์) คืน 0
2. เงินคืน = ยอดซื้อ × อัตรา (silver 1.5%, gold 2.5%, platinum 4%)
3. ถ้าเป็นเดือนเกิด (`birthday=True`) คูณ 2
4. จำกัดสูงสุด 200 บาท (20,000 สตางค์)

ทุกค่าคำนวณเป็นจำนวนเต็มสตางค์ โดยใช้ `amount * permille // 1000` จึงไม่มีปัญหาทศนิยมของ float

**การตัดสินใจที่ผมเลือกเอง** (โจทย์ไม่ได้ระบุ ถ้าต้องการต่างออกไปบอกได้)
- **การปัดเศษ:** ปัดทิ้งเศษสตางค์ (floor) เช่น 10,001 สตางค์ × 2.5% = 250.025 → 250
- **ตัวพิมพ์ของ tier:** รับ `"Gold"` หรือ `" gold "` ได้ เพราะ normalize ก่อนเทียบ
- **ข้อมูลผิดประเภท:** `tier` ที่ไม่รู้จักจะ raise
…(ตัด 351 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

สร้างไฟล์ `solve.py` ในโฟลเดอร์ปัจจุบันแล้ว และทดสอบผ่านทั้งหมด (โฟลเดอร์ `./skills` ไม่มีอยู่ จึงไม่มีสกิลให้อ่าน)

**ไฟล์:** `/workspace/wklab/suite/runs/h1-k01-train/t4-cashback-r1/sandbox/solve.py`

**วิธีคิด**
1. ยอดซื้อต่ำกว่า 100 บาท (10,000 สตางค์) คืน 0
2. เงินคืน = ยอดซื้อ × อัตรา (silver 1.5%, gold 2.5%, platinum 4%)
3. ถ้าเป็นเดือนเกิด (`birthday=True`) คูณ 2
4. จำกัดสูงสุด 200 บาท (20,000 สตางค์)

ทุกค่าคำนวณเป็นจำนวนเต็มสตางค์ โดยใช้ `amount * permille // 1000` จึงไม่มีปัญหาทศนิยมของ float

**การตัดสินใจที่ผมเลือกเอง** (โจทย์ไม่ได้ระบุ ถ้าต้องการต่างออกไปบอกได้)
- **การปัดเศษ:** ปัดทิ้งเศษสตางค์ (floor) เช่น 10,001 สตางค์ × 2.5% = 250.025 → 250
- **ตัวพิมพ์ของ tier:** รับ `"Gold"` หรือ `" gold "` ได้ เพราะ normalize ก่อนเทียบ
- **ข้อมูลผิดประเภท:** `tier` ที่ไม่รู้จักจะ raise `ValueError`, `amount` ติดลบจะ raise `ValueError`, และ `amount` ที่ไม่ใช่จำนวนเต็มจะ raise `TypeError`

**ผลทดสอบ**
- ตัวอย่างใน `__main__` ให้ผลถูกต้อง เช่น platinum ยอด 10,000 บาท ได้ 20,000 สตางค์ (ถึงเพดาน 200 บาท)
- assert 13 กรณี ผ่านทั้งหมด รวมกรณีขอบ: ยอด 9,999 และ 10,000 สตางค์, ยอดที่ทำให้ถึงเพดาน, และเดือนเกิดที่ต้องคูณก่อนนำไปเทียบเพดาน
