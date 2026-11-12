# Trace t2-split-bill-r2 · iteration 1

- ผล: **FAIL** · คะแนน 0.60 (ผ่าน 6 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 4 ครั้ง · คำสั่งล้ม 1 ครั้ง · อ่านสกิล: ไม่

## โจทย์

ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `split_bill(total, people, tip_percent)` ในไฟล์ `solve.py` สำหรับหารบิล
- `total` = ยอดบิล (สตางค์ ตั้งแต่ 0) · `people` = จำนวนคน (ตั้งแต่ 1) · `tip_percent` = ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0–100)
- ยอดที่ต้องหาร = ยอดบิลบวกทิป
- หารเท่ากันทุกคน ถ้าหารไม่ลงตัว ให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์จนครบ
- คืน list ของยอดที่แต่ละคนจ่าย (จำนวนเต็มสตางค์) เรียงตามลำดับคน

## ผลของตัวตรวจ (Grader)

- ✓ `contract`
- ✓ `basic`
- ✓ `half_up`
- ✓ `no_drift`
- ✓ `boundary`
- ✓ `reject_value`
- ✗ `reject_type`: split_bill(10000, true, 0) ต้อง raise ValueError แต่คืนค่า [10000] · พลาด 1 จาก 4 กรณี
- ✗ `cli_ok`: stdin {"total": 10000, "people": 3, "tip_percent": 0} ต้องได้ {"ok": true, "result": [3334, 3333, 3333]} exit 0 แต่ได้ exit 0 stdout [3667, 3667, 3666]
- ✗ `cli_error`: stdin {"total": 10000, "people": 0, "tip_percent": 0} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout [3667, 3667, 3666]
- ✗ `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py

## สิ่งที่ Agent ทำ

### ขั้น 1 · Bash

```
pwd && ls -la && ls -la ./skills 2>/dev/null || echo "NO_SKILLS_DIR"
```

ผลที่ได้:

```
/workspace/wklab/suite/runs/h1-k01-train/t2-split-bill-r2/sandbox
total 8
drwxr-xr-x 2 root root 4096 Nov 13 01:49 .
drwxr-xr-x 3 root root 4096 Nov 13 01:49 ..
NO_SKILLS_DIR
```

### ขั้น 2 · Write

```
/workspace/wklab/suite/runs/h1-k01-train/t2-split-bill-r2/sandbox/solve.py
"""BaanKafe bill splitter.

All money is handled as integer satang to avoid floating-point error.
"""


def split_bill(total, people, tip_percent):
    """Split a bill (plus tip) evenly among people.

    Args:
        total: bill amount in satang (>= 0).
        people: number of people (>= 1).
        tip_percent: tip as an integer percentage (0-100).

    Returns:
        list[int]: amount each person pays in satang, in person order.
        Any remainder satang is given one each to the first people.
    """
    if not isinstance(total, int) or total < 0:
        raise ValueError("total must be a non-negative integer (satang)")
    if not isinstance(people, int) or people < 1:
        raise ValueError("people must be an integer >= 1")
    if not isinstance(tip_percent, int) or not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be an integer between 0 and 100")

    # Tip in satang, rounded half up to the nearest satang (integer math only).
    tip = (total * tip_percent * 2 + 100) // 200
    amount = total + tip

    base, remainder = divmod(amount, people)
    return [base + 1 if i < remainder else base for i in range(people)]


if __name__ == "__main__":
    print(split_bill(10000, 3, 10))  # 11000 satang over 3 -> [3667, 3667, 3666]

```

ผลที่ได้:

```
File created successfully at: /workspace/wklab/suite/runs/h1-k01-train/t2-split-bill-r2/sandbox/solve.py (file state is current in your context — no need to Read it back)
```

### ขั้น 3 · Bash

```
python3 -I -c "
from solve import split_bill as s
cases = [((10000,3,10),[3667,3667,3666]), ((0,4,0),[0,0,0,0]), ((100,3,0),[34,33,33]), ((1,5,0),[1,0,0,0,0]), ((12345,1,0),[12345]), ((999,2,15),[575,575])]
for args, exp in cases:
    got = s(*args); print(args, got, 'OK' if got==exp and sum(got)==args[0]+(args[0]*args[2]*2+100)//200 else 'FAIL')
"
```

ผลที่ได้:

```
ERROR Exit code 1
Traceback (most recent call last):
  File "<string>", line 2, in <module>
ModuleNotFoundError: No module named 'solve'
```

### ขั้น 4 · Bash

```
python3 -I -c "
import sys; sys.path.insert(0, '.')
from solve import split_bill as s
cases = [((10000,3,10),[3667,3667,3666]), ((0,4,0),[0,0,0,0]), ((100,3,0),[34,33,33]), ((1,5,0),[1,0,0,0,0]), ((12345,1,0),[12345]), ((999,2,15),[575,575])]
for args, exp in cases:
    got = s(*args); print(args, got, 'OK' if got==exp and sum(got)==args[0]+(args[0]*args[2]*2+100)//200 else 'FAIL')
"
```

ผลที่ได้:

```
(10000, 3, 10) [3667, 3667, 3666] OK
(0, 4, 0) [0, 0, 0, 0] OK
(100, 3, 0) [34, 33, 33] OK
(1, 5, 0) [1, 0, 0, 0, 0] OK
(12345, 1, 0) [12345] OK
(999, 2, 15) [575, 574] FAIL
```

**Agent พูด:** `solve.py` is written in this folder. The one failed check was a mistake in my expected value, not in the code: 999 × 15% = 149.85, which rounds to 150 satang, so the amount is 1,149 and splits to `[575, 574]`, which is what the code returns.

**File:** `solve.py`

```python
def split_bill(total, people, tip_percent):
    if not isinstance(total, int) or total < 0:
        raise ValueError("total must be a non-negative integer (satang)")
    if not isinstance(people, int) or people < 1:
        raise ValueError("people must be an integer >= 1")
    if not isinstance(tip_percent, int) or not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be an integer between 0 and 100")

    tip = (total * tip_percent * 2 + 100) // 200   # round half up, integer math
    amount = total
…(ตัด 866 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

`solve.py` is written in this folder. The one failed check was a mistake in my expected value, not in the code: 999 × 15% = 149.85, which rounds to 150 satang, so the amount is 1,149 and splits to `[575, 574]`, which is what the code returns.

**File:** `solve.py`

```python
def split_bill(total, people, tip_percent):
    if not isinstance(total, int) or total < 0:
        raise ValueError("total must be a non-negative integer (satang)")
    if not isinstance(people, int) or people < 1:
        raise ValueError("people must be an integer >= 1")
    if not isinstance(tip_percent, int) or not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be an integer between 0 and 100")

    tip = (total * tip_percent * 2 + 100) // 200   # round half up, integer math
    amount = total + tip

    base, remainder = divmod(amount, people)
    return [base + 1 if i < remainder else base for i in range(people)]
```

**Choices I made:**
- **Tip rounding:** the spec doesn't say how to handle a fractional satang, so the tip rounds half up to the nearest satang. If BaanKafe wants floor instead, change the tip line to `total * tip_percent // 100`.
- **Remainder:** the first `amount % people` people each pay one extra satang.
- **Input checks:** values outside the stated ranges raise `ValueError`.

**Checks run (all pass after correcting my expected value):**
- `(10000, 3, 10)` → `[3667, 3667, 3666]`
- `(0, 4, 0)` → `[0, 0, 0, 0]`
- `(100, 3, 0)` → `[34, 33, 33]`
- `(1, 5, 0)` → `[
…(ตัด 166 ตัวอักษร)
