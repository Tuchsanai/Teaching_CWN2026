"""BaanKafe cashback calculator

กติกา
- amount   : ยอดซื้อ เป็นจำนวนเต็มสตางค์ตั้งแต่ 0 (bool, float, str ไม่รับ)
- tier     : "silver" 1.5% · "gold" 2.5% · "platinum" 4% (ค่าอื่น raise ValueError)
- birthday : bool, True = ซื้อในเดือนเกิด ได้เงินคืน 2 เท่า
- ยอดซื้อต่ำกว่า 100 บาท (10000 สตางค์) ไม่ได้เงินคืน (ได้ 0)
- เงินคืนสูงสุด 200 บาท (20000 สตางค์) ต่อบิล คิดหลังคูณเดือนเกิดแล้ว
- ผลเป็นจำนวนเต็มสตางค์ ปัดลง (ร้านไม่จ่ายเกิน) ปัดครั้งเดียวตอนท้ายสุด
"""
import json
import sys
from fractions import Fraction
from math import floor

RATES = {
    "silver": Fraction(15, 1000),  # 1.5%
    "gold": Fraction(25, 1000),    # 2.5%
    "platinum": Fraction(4, 100),  # 4%
}
MIN_AMOUNT = 10000   # 100 บาท
MAX_CASHBACK = 20000  # 200 บาท


def need_int(value, name, low=None):
    # bool และ float ไม่ใช่ int ตามเงื่อนไขนี้
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def need_bool(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def need_str(value, name, allowed):
    if type(value) is not str:
        raise ValueError(f"{name} ต้องเป็นข้อความ")
    if value not in allowed:
        raise ValueError(f"{name} ไม่ถูกต้อง")
    return value


def round_down(x):
    """ปัดลงเป็นจำนวนเต็ม (x ไม่ติดลบ)"""
    return floor(Fraction(x))


def cashback(amount, tier, birthday):
    """คืนค่าเงินคืนสมาชิกเป็นจำนวนเต็มสตางค์"""
    amount = need_int(amount, "amount", low=0)
    tier = need_str(tier, "tier", tuple(RATES))
    birthday = need_bool(birthday, "birthday")

    if amount < MIN_AMOUNT:
        return 0

    multiplier = 2 if birthday else 1
    value = Fraction(amount) * RATES[tier] * multiplier
    return min(round_down(value), MAX_CASHBACK)


def main():
    try:
        args = json.loads(sys.stdin.read())
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = cashback(**args)
    except (ValueError, TypeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
