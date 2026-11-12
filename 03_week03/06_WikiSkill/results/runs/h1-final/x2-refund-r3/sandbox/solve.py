import sys
import json
from fractions import Fraction


def _int(v, name, lo=None, hi=None):
    if isinstance(v, bool) or not isinstance(v, int):
        raise ValueError(f"{name} must be an integer")
    if (lo is not None and v < lo) or (hi is not None and v > hi):
        raise ValueError(f"{name} out of range")
    return v


def _bool(v, name):
    if not isinstance(v, bool):
        raise ValueError(f"{name} must be a bool")
    return v


def _half_up(x: Fraction) -> int:
    # ปัดแบบ half up ของค่าไม่ติดลบ: n/d -> (2n + d) // (2d)
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def refund(paid, used_percent, restock):
    """คำนวณเงินที่ต้องคืนลูกค้าของคอร์สสอนชงกาแฟ (หน่วยสตางค์)

    paid         : เงินที่ลูกค้าจ่ายมา (สตางค์, จำนวนเต็ม >= 0)
    used_percent : เรียนไปแล้วกี่เปอร์เซ็นต์ (จำนวนเต็ม 0-100)
    restock      : True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
    """
    paid = _int(paid, "paid", lo=0)
    used_percent = _int(used_percent, "used_percent", lo=0, hi=100)
    restock = _bool(restock, "restock")

    # เรียนไปแล้วเกิน 80% ไม่คืนเงิน
    if used_percent > 80:
        return 0

    # คืนตามสัดส่วนที่ยังไม่ได้เรียน (เก็บเป็นเศษส่วน ยังไม่ปัด)
    amount = Fraction(paid) * Fraction(100 - used_percent, 100)

    # หักค่าดำเนินการ 12.5% (เหลือ 87.5% = 7/8) เมื่อ restock เป็น True
    if restock:
        amount *= Fraction(7, 8)

    # ปัดครั้งเดียวตอนท้าย
    return _half_up(amount)


def main():
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = refund(**data)
        out = json.dumps({"ok": True, "result": result})
    except Exception as e:  # รวม JSON เสีย, key เกิน/ขาด, ValueError
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 2
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
