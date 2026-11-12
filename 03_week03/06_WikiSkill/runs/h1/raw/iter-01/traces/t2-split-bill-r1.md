# Trace t2-split-bill-r1 · iteration 1

- ผล: **FAIL** · คะแนน 0.50 (ผ่าน 5 จาก 10 ข้อตรวจ)
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
- ✗ `half_up`: split_bill(1010, 1, 5) คาด [1061] ได้ [1060] · พลาด 3 จาก 3 กรณี
- ✓ `no_drift`
- ✓ `boundary`
- ✓ `reject_value`
- ✗ `reject_type`: split_bill(10000.0, 2, 0) ต้อง raise ValueError แต่คืนค่า [5000.0, 5000.0] · พลาด 4 จาก 4 กรณี
- ✗ `cli_ok`: stdin {"total": 10000, "people": 3, "tip_percent": 0} ต้องได้ {"ok": true, "result": [3334, 3333, 3333]} exit 0 แต่ได้ exit 0 stdout [3667, 3667, 3666]
[0, 0, 0, 0]
[1998]
- ✗ `cli_error`: stdin {"total": 10000, "people": 0, "tip_percent": 0} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout [3667, 3667, 3666]
[0, 0, 0, 0]
[1998]
- ✗ `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py

## สิ่งที่ Agent ทำ

### ขั้น 1 · Bash

```
ls -la ./skills 2>/dev/null && find ./skills -maxdepth 3 -type f 2>/dev/null | head -50; echo "---"; ls -la
```

ผลที่ได้:

```
---
total 8
drwxr-xr-x 2 root root 4096 Nov 13 01:49 .
drwxr-xr-x 3 root root 4096 Nov 13 01:49 ..
```

### ขั้น 2 · Write

```
/workspace/wklab/suite/runs/h1-k01-train/t2-split-bill-r1/sandbox/solve.py
"""BaanKafe bill splitter.

All money values are integers in satang (1 baht = 100 satang).
"""


def split_bill(total: int, people: int, tip_percent: int) -> list[int]:
    """Split a bill (plus tip) evenly among `people`.

    Args:
        total: bill amount in satang, >= 0.
        people: number of people, >= 1.
        tip_percent: tip as an integer percentage, 0-100.

    Returns:
        List of amounts (satang) each person pays, in person order.
        The first `remainder` people pay one extra satang so the total is exact.

    Tip is computed with integer math and rounded down to the whole satang.
    """
    if total < 0:
        raise ValueError("total must be >= 0")
    if people < 1:
        raise ValueError("people must be >= 1")
    if not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be between 0 and 100")

    tip = total * tip_percent // 100
    amount = total + tip

    base, remainder = divmod(amount, people)
    return [base + 1 if i < remainder else base for i in range(people)]


if __name__ == "__main__":
    # Quick examples
    print(split_bill(10000, 3, 10))  # 11000 / 3 -> [3667, 3667, 3666]
    print(split_bill(0, 4, 0))       # [0, 0, 0, 0]
    print(split_bill(999, 1, 100))   # [1998]

```

ผลที่ได้:

```
File created successfully at: /workspace/wklab/suite/runs/h1-k01-train/t2-split-bill-r1/sandbox/solve.py (file state is current in your context — no need to Read it back)
```

### ขั้น 3 · Bash

```
python3 -I solve.py && python3 -I -c "
from solve import split_bill
import random
for _ in range(10000):
    t=random.randint(0,10**7); p=random.randint(1,50); tp=random.randint(0,100)
    r=split_bill(t,p,tp)
    assert len(r)==p and sum(r)==t+t*tp//100
    assert max(r)-min(r)<=1 and r==sorted(r,reverse=True)
print('random checks ok')"
```

ผลที่ได้:

```
ERROR Exit code 1
[3667, 3667, 3666]
[0, 0, 0, 0]
[1998]
Traceback (most recent call last):
  File "<string>", line 2, in <module>
ModuleNotFoundError: No module named 'solve'
```

**Agent พูด:** The examples pass. The random check failed only because `-I` also drops the current directory from the import path, so I'll rerun it with the path set explicitly.

### ขั้น 4 · Bash

```
python3 -c "
import sys; sys.path.insert(0,'.')
from solve import split_bill
import random
for _ in range(10000):
    t=random.randint(0,10**7); p=random.randint(1,50); tp=random.randint(0,100)
    r=split_bill(t,p,tp)
    assert len(r)==p and sum(r)==t+t*tp//100
    assert max(r)-min(r)<=1 and r==sorted(r,reverse=True)
print('random checks ok')"
```

ผลที่ได้:

```
random checks ok
```

**Agent พูด:** I wrote `split_bill(total, people, tip_percent)` in `solve.py` in the current folder. The examples and 10,000 random checks pass. The checks confirmed that the list length equals `people`, the amounts sum to total plus tip, and the amounts differ by at most 1 satang with the extra satang going to the first people.

The `./skills` folder doesn't exist, so there was no skill to follow.

The function returns a list of integer satang amounts, with one entry per person in order. For example, `split_bill(10000, 3, 10)` returns `[3667, 3667, 3666]`.

Choices I made that the spec didn't cover:
- **Tip rounding:** the tip is `total * tip_percent // 100`, rounded down to a whole satang. If BaanKafe wants round-half-up instead, that's a one-line change.
- **Input validation:** the function raises `Va
…(ตัด 72 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

I wrote `split_bill(total, people, tip_percent)` in `solve.py` in the current folder. The examples and 10,000 random checks pass. The checks confirmed that the list length equals `people`, the amounts sum to total plus tip, and the amounts differ by at most 1 satang with the extra satang going to the first people.

The `./skills` folder doesn't exist, so there was no skill to follow.

The function returns a list of integer satang amounts, with one entry per person in order. For example, `split_bill(10000, 3, 10)` returns `[3667, 3667, 3666]`.

Choices I made that the spec didn't cover:
- **Tip rounding:** the tip is `total * tip_percent // 100`, rounded down to a whole satang. If BaanKafe wants round-half-up instead, that's a one-line change.
- **Input validation:** the function raises `ValueError` for `total < 0`, `people < 1`, or `tip_percent` outside 0–100.
