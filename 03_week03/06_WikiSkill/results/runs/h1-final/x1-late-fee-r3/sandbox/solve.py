import sys
import json
from fractions import Fraction


def _half_up(x: Fraction) -> int:
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def _int(v, name, lo=None, hi=None):
    if isinstance(v, bool) or not isinstance(v, int):
        raise ValueError(f"{name} must be an integer")
    if (lo is not None and v < lo) or (hi is not None and v > hi):
        raise ValueError(f"{name} out of range")
    return v


def late_fee(amount, days_late):
    """คิดค่าปรับลูกค้าขายส่งที่ชำระช้า (หน่วยสตางค์)

    - ช้าไม่เกิน 3 วัน ไม่คิดค่าปรับ
    - ช้าเกิน 3 วัน คิด 0.75% ของยอดค้างต่อวัน นับทุกวันที่ช้า
    - ค่าปรับสูงสุด 15% ของยอดค้างชำระ
    - ปัดเศษ half up ครั้งเดียวตอนท้าย
    """
    amount = _int(amount, "amount", lo=0)
    days_late = _int(days_late, "days_late", lo=0, hi=365)
    if days_late <= 3:
        return 0
    raw = Fraction(75, 10000) * days_late * amount
    cap = Fraction(15, 100) * amount
    return _half_up(min(raw, cap))


def main():
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = late_fee(**data)
        out = json.dumps({"ok": True, "result": result})
    except Exception as e:  # รวม JSON เสีย, key เกิน/ขาด, ValueError
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 2
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
