from fractions import Fraction
import json
import sys

# หน่วยเป็นสตางค์ทั้งหมด
MIN_AMOUNT = 10000   # ยอดซื้อขั้นต่ำ 100 บาท
CAP = 20000          # เงินคืนสูงสุดต่อบิล 200 บาท
RATES = {
    "silver": Fraction(15, 1000),    # 1.5%
    "gold": Fraction(25, 1000),      # 2.5%
    "platinum": Fraction(4, 100),    # 4%
}


def _half_up(x: Fraction) -> int:
    """ปัดเศษแบบ half up เป็นจำนวนเต็ม (x ไม่ติดลบ)"""
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def _int(v, name, lo=None):
    if isinstance(v, bool) or not isinstance(v, int):
        raise ValueError(f"{name} must be an integer")
    if lo is not None and v < lo:
        raise ValueError(f"{name} out of range")
    return v


def _bool(v, name):
    if not isinstance(v, bool):
        raise ValueError(f"{name} must be a bool")
    return v


def cashback(amount, tier, birthday):
    amount = _int(amount, "amount", lo=0)
    if not isinstance(tier, str) or tier not in RATES:
        raise ValueError("tier must be one of silver, gold, platinum")
    birthday = _bool(birthday, "birthday")

    # เกณฑ์ขั้นต่ำเทียบกับยอดจริง ยังไม่ปัด
    if amount < MIN_AMOUNT:
        return 0

    rate = RATES[tier]
    if birthday:
        rate *= 2  # เดือนเกิดได้ 2 เท่า

    # ปัดครั้งเดียวตอนท้าย แล้วค่อยเทียบเพดาน
    refund = _half_up(amount * rate)
    return min(refund, CAP)


def main():
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = cashback(**data)
        out = json.dumps({"ok": True, "result": result})
    except Exception as e:  # รวม JSON เสีย, key เกิน/ขาด, ValueError
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 2
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
