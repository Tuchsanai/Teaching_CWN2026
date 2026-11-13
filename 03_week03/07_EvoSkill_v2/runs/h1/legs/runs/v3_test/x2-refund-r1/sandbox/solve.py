"""คิดเงินคืนของคอร์สสอนชงกาแฟ BaanKafe

refund(paid, used_percent, restock)
- paid:         เงินที่ลูกค้าจ่ายมา หน่วยสตางค์ (int, ตั้งแต่ 0)
- used_percent: เรียนไปแล้วกี่เปอร์เซ็นต์ (int, 0–100)
- restock:      True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน

กติกา:
1. คืนตามสัดส่วนที่ยังไม่ได้เรียน: paid * (100 - used_percent) / 100
2. ถ้าเรียนไปแล้วเกิน 80% (used_percent > 80) ไม่คืนเงิน (คืน 0)
3. ถ้า restock เป็น True หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
4. ผลลัพธ์เป็นจำนวนเต็มสตางค์ ใช้ Fraction คำนวณทุกขั้น แล้วปัดครึ่งขึ้นครั้งเดียวตอนท้าย
"""

import json
import sys
from fractions import Fraction

FEE_RATE = Fraction(125, 1000)   # 12.5%
NO_REFUND_ABOVE = 80             # เรียนเกิน 80% ไม่คืนเงิน


def _require_int(value, label, lo=None, hi=None):
    if type(value) is not int:
        raise ValueError(f"{label} ต้องเป็นจำนวนเต็ม")
    if lo is not None and value < lo:
        raise ValueError(f"{label} ต้องไม่น้อยกว่า {lo}")
    if hi is not None and value > hi:
        raise ValueError(f"{label} ต้องไม่เกิน {hi}")
    return value


def _require_flag(value, label):
    if type(value) is not bool:
        raise ValueError(f"{label} ต้องเป็น True หรือ False")
    return value


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม สำหรับค่าที่ไม่ติดลบ"""
    return int((Fraction(x) * 2 + 1) // 2)


def refund(paid, used_percent, restock):
    """คืนค่าเป็นจำนวนเต็มสตางค์ (int)"""
    _require_int(paid, "paid", lo=0)
    _require_int(used_percent, "used_percent", lo=0, hi=100)
    _require_flag(restock, "restock")

    if used_percent > NO_REFUND_ABOVE:
        return 0

    amount = Fraction(paid) * (100 - used_percent) / 100
    if restock:
        amount *= 1 - FEE_RATE
    return _half_up(amount)


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = refund(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
