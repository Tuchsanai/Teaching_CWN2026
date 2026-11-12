import json
import sys
from fractions import Fraction

REFUND_CUTOFF_PERCENT = 80          # เรียนเกิน 80% ไม่คืนเงิน
HANDLING_FEE = Fraction(125, 1000)  # ค่าดำเนินการ 12.5%


def _half_up(x: Fraction) -> int:
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


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


def refund(paid, used_percent, restock):
    paid = _int(paid, "paid", lo=0)
    used_percent = _int(used_percent, "used_percent", lo=0, hi=100)
    restock = _bool(restock, "restock")

    if used_percent > REFUND_CUTOFF_PERCENT:
        return 0

    # คืนตามสัดส่วนที่ยังไม่ได้เรียน (ยังไม่ปัดเศษ)
    amount = Fraction(paid * (100 - used_percent), 100)
    if restock:
        amount *= 1 - HANDLING_FEE  # หักค่าดำเนินการ 12.5% ของยอดคืน

    # ปัดเศษ half up ครั้งเดียวตอนท้าย
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
