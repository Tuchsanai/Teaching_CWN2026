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


def split_bill(total, people, tip_percent):
    total = _int(total, "total", lo=0)
    people = _int(people, "people", lo=1)
    tip_percent = _int(tip_percent, "tip_percent", lo=0, hi=100)

    # ยอดที่ต้องหาร = ยอดบิล + ทิป (เก็บเป็นเศษส่วน ปัดครั้งเดียวตอนท้าย)
    amount = _half_up(Fraction(total) * (100 + tip_percent) / 100)

    base, remainder = divmod(amount, people)
    # คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์จนครบ
    return [base + 1 if i < remainder else base for i in range(people)]


def main():
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = split_bill(**data)
        out = json.dumps({"ok": True, "result": result})
    except Exception as e:  # รวม JSON เสีย, key เกิน/ขาด, ValueError
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 2
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
