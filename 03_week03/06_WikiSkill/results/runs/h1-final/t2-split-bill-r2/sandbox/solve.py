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

    # ยอดบิล + ทิป = total * (100 + tip) / 100 ; ปัด half up ครั้งเดียวตรงนี้
    amount = _half_up(Fraction(total * (100 + tip_percent), 100))

    # หารเท่ากัน เศษสตางค์ให้คนลำดับแรก ๆ คนละ 1 สตางค์
    base, remainder = divmod(amount, people)
    return [base + 1] * remainder + [base] * (people - remainder)


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
