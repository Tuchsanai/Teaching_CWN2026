"""BaanKafe: คิดเงินคืนสมาชิก (หน่วยสตางค์)

สมมติฐานตามนโยบายร้าน (brief เงียบ):
- เงินคืนเป็นเงินที่ร้านจ่ายออก -> ปัดลง (floor) ครั้งเดียวตอนท้าย
- โบนัสเดือนเกิด (2 เท่า) ใช้กับ gold และ platinum เท่านั้น silver ไม่ได้สิทธิ์
- เพดาน 200 บาท (20000 สตางค์) ใช้หลังคำนวณและปัดแล้ว
"""
import json
import sys
from fractions import Fraction

RATES = {
    "silver": Fraction(15, 1000),
    "gold": Fraction(25, 1000),
    "platinum": Fraction(4, 100),
}
BONUS_TIERS = ("gold", "platinum")
MIN_AMOUNT = 10000   # 100 บาท
CAP = 20000          # 200 บาท


def round_down(x):
    return int(Fraction(x) // 1)


def need_int(value, name, low=None, high=None):
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def need_bool(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def cashback(amount, tier, birthday):
    need_int(amount, "amount", 0)
    if type(tier) is not str or tier not in RATES:
        raise ValueError("tier ต้องเป็น silver, gold หรือ platinum")
    need_bool(birthday, "birthday")
    if amount < MIN_AMOUNT:
        return 0
    rate = RATES[tier]
    if birthday and tier in BONUS_TIERS:
        rate *= 2
    return min(round_down(Fraction(amount) * rate), CAP)


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = cashback(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
