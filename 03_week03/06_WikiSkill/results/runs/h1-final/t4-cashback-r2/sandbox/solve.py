"""คำนวณเงินคืนสมาชิกของ BaanKafe

หน่วยทั้งหมดเป็นสตางค์ (จำนวนเต็ม) ผลลัพธ์เป็นจำนวนเต็มสตางค์
"""
import json
import sys
from fractions import Fraction

MIN_AMOUNT_SATANG = 10000   # 100 บาท: ต่ำกว่านี้ไม่ได้เงินคืน
MAX_CASHBACK_SATANG = 20000  # 200 บาทต่อบิล

# อัตราเงินคืนเป็นเศษส่วนเพื่อไม่ให้มี float
RATES = {
    "silver": Fraction(15, 1000),    # 1.5%
    "gold": Fraction(25, 1000),      # 2.5%
    "platinum": Fraction(40, 1000),  # 4%
}


def _half_up(x: Fraction) -> int:
    n, d = x.numerator, x.denominator
    return (2 * n + d) // (2 * d)


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


def cashback(amount, tier, birthday):
    """คืนจำนวนเงินคืนเป็นสตางค์

    amount   : ยอดซื้อ (สตางค์, >= 0)
    tier     : "silver" | "gold" | "platinum"
    birthday : True ถ้าซื้อในเดือนเกิด (ได้เงินคืน 2 เท่า)
    """
    amount = _int(amount, "amount", lo=0)
    if not isinstance(tier, str) or tier not in RATES:
        raise ValueError("tier must be one of 'silver', 'gold', 'platinum'")
    birthday = _bool(birthday, "birthday")

    if amount < MIN_AMOUNT_SATANG:
        return 0

    raw = Fraction(amount) * RATES[tier]
    if birthday:
        raw *= 2
    return min(_half_up(raw), MAX_CASHBACK_SATANG)


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
