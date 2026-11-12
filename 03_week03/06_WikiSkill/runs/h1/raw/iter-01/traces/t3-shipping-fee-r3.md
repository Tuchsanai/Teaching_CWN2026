# Trace t3-shipping-fee-r3 · iteration 1

- ผล: **FAIL** · คะแนน 0.60 (ผ่าน 6 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 4 ครั้ง · คำสั่งล้ม 1 ครั้ง · อ่านสกิล: ไม่

## โจทย์

ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `shipping_fee(weight_g, distance_km, express)` ในไฟล์ `solve.py` สำหรับคิดค่าส่งเมล็ดกาแฟ
- `weight_g` = น้ำหนัก 1–30,000 กรัม · `distance_km` = ระยะทาง (ตั้งแต่ 0) · `express` = True คือส่งด่วน
- ไม่เกิน 1,000 กรัม 40 บาท · ไม่เกิน 5,000 กรัม 80 บาท · เกิน 5,000 กรัม 80 บาท บวกส่วนที่เกิน 5,000 กรัม กิโลกรัมละ 15 บาท (คิดตามสัดส่วนของกรัม)
- ระยะทางเกิน 100 กม. คิดเพิ่ม 20%
- ส่งด่วน คิดเพิ่ม 50% (คูณต่อจากข้อก่อน)
- คืนค่าส่ง เป็นจำนวนเต็มสตางค์

## ผลของตัวตรวจ (Grader)

- ✓ `contract`
- ✓ `basic`
- ✓ `half_up`
- ✓ `no_drift`
- ✓ `boundary`
- ✓ `reject_value`
- ✗ `reject_type`: shipping_fee(1000.0, 10, false) ต้อง raise ValueError แต่คืนค่า 4000 · พลาด 3 จาก 5 กรณี
- ✗ `cli_ok`: stdin {"weight_g": 3000, "distance_km": 150, "express": false} ต้องได้ {"ok": true, "result": 9600} exit 0 แต่ได้ exit 0 stdout (ว่าง)
- ✗ `cli_error`: stdin {"weight_g": 0, "distance_km": 10, "express": false} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout (ว่าง)
- ✗ `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py

## สิ่งที่ Agent ทำ

### ขั้น 1 · Bash

```
ls -la && ls -la ./skills 2>/dev/null; echo "exit: $?"
```

ผลที่ได้:

```
total 8
drwxr-xr-x 2 root root 4096 Nov 13 01:49 .
drwxr-xr-x 3 root root 4096 Nov 13 01:49 ..
exit: 2
```

### ขั้น 2 · Write

```
/workspace/wklab/suite/runs/h1-k01-train/t3-shipping-fee-r3/sandbox/solve.py
"""คิดค่าส่งเมล็ดกาแฟของร้าน BaanKafe

หน่วยการคำนวณทั้งหมดเป็นสตางค์ (1 บาท = 100 สตางค์) ใช้ Fraction เพื่อไม่ให้เกิดความคลาดเคลื่อนของทศนิยมแบบ float
"""

from fractions import Fraction

MIN_WEIGHT_G = 1
MAX_WEIGHT_G = 30_000
LIGHT_LIMIT_G = 1_000
MID_LIMIT_G = 5_000
LONG_DISTANCE_KM = 100

FEE_LIGHT_SATANG = 4_000   # 40 บาท
FEE_MID_SATANG = 8_000     # 80 บาท
EXTRA_PER_KG_SATANG = 1_500  # 15 บาท ต่อกิโลกรัม (ส่วนที่เกิน 5,000 กรัม)


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์

    weight_g    : น้ำหนักเป็นกรัม (1–30,000)
    distance_km : ระยะทางเป็นกิโลเมตร (ตั้งแต่ 0)
    express     : True = ส่งด่วน (คิดเพิ่ม 50%)

    ขั้นตอน:
      1. ค่าส่งตามน้ำหนัก
         - ไม่เกิน 1,000 กรัม  -> 40 บาท
         - ไม่เกิน 5,000 กรัม  -> 80 บาท
         - เกิน 5,000 กรัม     -> 80 บาท + 15 บาท/กก. ของส่วนที่เกิน (คิดตามสัดส่วนกรัม)
      2. ระยะทางเกิน 100 กม. คิดเพิ่ม 20%
      3. ส่งด่วนคิดเพิ่ม 50% (คูณต่อจากข้อ 2)
      4. ปัดเศษเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้น)

    ตัวอย่าง:
      shipping_fee(2000, 50, False)    -> 8000   (80 บาท)
      shipping_fee(6000, 150, True)    -> 17100  (171 บาท)
    """
    weight = Fraction(str(weight_g))
    distance = Fraction(str(distance_km))

    if not (MIN_WEIGHT_G <= weight <= MAX_WEIGHT_G):
        raise ValueError(f"weight_g ต้องอยู่ในช่วง {MIN_WEIGHT_G}–{MAX_WEIGHT_G} กรัม")
    if distance < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")

    if weight <= LIGHT_LIMIT_G:
        fee = Fraction(FEE_LIGHT_SATANG)
    elif weight <= MID_LIMIT_G:
        fee = Fraction(FEE_MID_SATANG)
    else:
        extra_g = weight - MID_LIMIT_G
        fee = FEE_MID_SATANG + Fraction(EXTRA_PER_KG_SATANG) * extra_g / 1_000

    if distance > LONG_DISTANCE_KM:
        fee *= Fraction(6, 5)  # +20%

    if express:
        fee *= Fraction(3, 2)  # +50%

    # fee >= 0 เสมอ จึงปัดครึ่งขึ้นได้ด้วย floor(x + 1/2)
    return int(fee + Fraction(1, 2))

```

ผลที่ได้:

```
File created successfully at: /workspace/wklab/suite/runs/h1-k01-train/t3-shipping-fee-r3/sandbox/solve.py (file state is current in your context — no need to Read it back)
```

### ขั้น 3 · Bash

```
python3 -I -c '
from solve import shipping_fee as f
cases = [
 ((2000,50,False),8000),
 ((6000,150,True),17100),
 ((1,0,False),4000),
 ((1000,0,False),4000),
 ((1001,0,False),8000),
 ((5000,100,False),8000),
 ((5000,100.5,False),9600),
 ((5001,0,False),8002),
 ((30000,0,False),45500),
 ((30000,200,True),68250),
]
ok=True
for args,exp in cases:
    got=f(*args)
    print(args, got, "OK" if got==exp else f"FAIL expected {exp}")
    ok &= got==exp
for bad in [(0,1,False),(30001,1,False),(100,-1,False)]:
    try: f(*bad); print("no error", bad); ok=False
    except ValueError as e: print("ValueError", bad, e)
print("ALL OK" if ok else "SOME FAILED")
'
```

ผลที่ได้:

```
ERROR Exit code 1
Traceback (most recent call last):
  File "<string>", line 2, in <module>
ModuleNotFoundError: No module named 'solve'
```

**Agent พูด:** The `-I` flag drops the current directory from `sys.path`, so the import failed. I'll put the test in a separate directory and pass the module path explicitly.

### ขั้น 4 · Bash

```
mkdir -p /tmp/shipping_check && cat > /tmp/shipping_check/check.py <<'EOF'
import sys
sys.path.insert(0, "/workspace/wklab/suite/runs/h1-k01-train/t3-shipping-fee-r3/sandbox")
from solve import shipping_fee as f
cases = [
 ((2000,50,False),8000),
 ((6000,150,True),17100),
 ((1,0,False),4000),
 ((1000,0,False),4000),
 ((1001,0,False),8000),
 ((5000,100,False),8000),
 ((5000,100.5,False),9600),
 ((5001,0,False),8002),
 ((30000,0,False),45500),
 ((30000,200,True),68250),
]
ok = True
for args, exp in cases:
    got = f(*args)
    print(args, got, "OK" if got == exp else f"FAIL expected {exp}")
    ok &= got == exp
for bad in [(0,1,False),(30001,1,False),(100,-1,False)]:
    try:
        f(*bad); print("no error", bad); ok = False
    except ValueError as e:
        print("ValueError", bad, e)
print("ALL OK" if ok else "SOME FAILED")
EOF
python3 -I /tmp/shipping_check/check.py; rm -rf /tmp/shipping_check
```

ผลที่ได้:

```
(2000, 50, False) 8000 OK
(6000, 150, True) 17100 OK
(1, 0, False) 4000 OK
(1000, 0, False) 4000 OK
(1001, 0, False) 8000 OK
(5000, 100, False) 8000 OK
(5000, 100.5, False) 9600 OK
(5001, 0, False) 8002 OK
(30000, 0, False) 45500 OK
(30000, 200, True) 81900 FAIL expected 68250
ValueError (0, 1, False) weight_g ต้องอยู่ในช่วง 1–30000 กรัม
ValueError (30001, 1, False) weight_g ต้องอยู่ในช่วง 1–30000 กรัม
ValueError (100, -1, False) distance_km ต้องไม่ติดลบ
SOME FAILED
```

**Agent พูด:** The one failure was a mistake in my hand-calculated expected value, not in the code. For 30,000 g, 200 km, express: 45,500 × 1.2 = 54,600 × 1.5 = **81,900 satang**. I had left out the distance surcharge. The code's output is correct.

I'm not going to re-run the whole check. Every other case passed, including the expected values I had already verified by hand.

## Result

I created `solve.py` in the current folder. There was no `./skills` folder, so no skill applied.

```python
shipping_fee(weight_g, distance_km, express) -> int   # satang
```

**Calculation order:**
1. **Weight base:** ≤1,000 g → 4,000 satang (40 baht); ≤5,000 g → 8,000 satang (80 baht); above 5,000 g → 8,000 + 1,500 × (excess g / 1,000) satang.
2. **Distance:** strictly over 100 km → ×1.2. Exactly 100 km gets no surcharg
…(ตัด 1022 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

The one failure was a mistake in my hand-calculated expected value, not in the code. For 30,000 g, 200 km, express: 45,500 × 1.2 = 54,600 × 1.5 = **81,900 satang**. I had left out the distance surcharge. The code's output is correct.

I'm not going to re-run the whole check. Every other case passed, including the expected values I had already verified by hand.

## Result

I created `solve.py` in the current folder. There was no `./skills` folder, so no skill applied.

```python
shipping_fee(weight_g, distance_km, express) -> int   # satang
```

**Calculation order:**
1. **Weight base:** ≤1,000 g → 4,000 satang (40 baht); ≤5,000 g → 8,000 satang (80 baht); above 5,000 g → 8,000 + 1,500 × (excess g / 1,000) satang.
2. **Distance:** strictly over 100 km → ×1.2. Exactly 100 km gets no surcharge.
3. **Express:** `True` → ×1.5, applied after the distance surcharge.
4. **Rounding** to whole satang.

**Choices I made where the spec was open:**
- **Exact arithmetic:** I used `Fraction` so there are no float rounding errors.
- **Rounding:** half up, so 5,001 g gives 8,002 satang (8,001.5 rounds up). If the shop wants truncation or banker's rounding, this is a one-line change.
- **Invalid input:** `weight_g` outside 1–30,000 or a negative `distance_km` raises `ValueError` rather than returning 0.

**Checks run** (with `python3 -I`, from a temporary directory):
- `(2000, 50, False)` → 8000 (80 baht)
- `(6000, 150, True)` → 17100 (171 baht)
- `(1, 0, False)` → 4000
- `(1001, 0, False)` → 
…(ตัด 322 ตัวอักษร)
