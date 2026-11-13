"""ค่าปรับลูกค้าขายส่งของ BaanKafe ที่ชำระเงินช้า

หน่วย: amount เป็นสตางค์ (int) ผลลัพธ์เป็นสตางค์ (int)
"""
import json
import sys
from fractions import Fraction

GRACE_DAYS = 3                     # ช้าไม่เกิน 3 วัน ไม่คิดค่าปรับ
DAILY_RATE = Fraction(75, 10000)   # 0.75% ต่อวัน
CAP_RATE = Fraction(15, 100)       # เพดาน 15% ของยอดค้างชำระ
MAX_DAYS = 365


def _require_int(value, label, lo=None, hi=None):
    if type(value) is not int:
        raise ValueError(f"{label} ต้องเป็นจำนวนเต็ม")
    if lo is not None and value < lo:
        raise ValueError(f"{label} ต้องไม่น้อยกว่า {lo}")
    if hi is not None and value > hi:
        raise ValueError(f"{label} ต้องไม่เกิน {hi}")
    return value


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม รับค่าที่ไม่ติดลบ"""
    return int((Fraction(x) * 2 + 1) // 2)


def late_fee(amount, days_late):
    """คืนค่าปรับ (สตางค์, int) สำหรับยอดค้าง amount ที่ชำระช้า days_late วัน

    - ช้าไม่เกิน 3 วัน: ไม่มีค่าปรับ
    - ช้าเกิน 3 วัน: 0.75% ต่อวันของยอดค้าง นับทุกวัน (รวม 3 วันแรก)
    - เพดาน: 15% ของยอดค้าง
    - ปัดครึ่งขึ้นเป็นสตางค์ครั้งเดียวตอนท้าย
    """
    amount = _require_int(amount, "amount", lo=0)
    days_late = _require_int(days_late, "days_late", lo=0, hi=MAX_DAYS)

    if days_late <= GRACE_DAYS:
        return 0

    raw = amount * DAILY_RATE * days_late    # Fraction ที่ยังไม่ปัด
    cap = amount * CAP_RATE
    return _half_up(min(raw, cap))


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = late_fee(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
