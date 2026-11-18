"""cashback · BaanKafe"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (x ไม่ติดลบ)"""
    return int((Fraction(x) * 2 + 1) // 2)


def round_down(x):
    """ปัดลง (ใช้กับเงินที่ร้านจ่ายออก เช่นเงินคืน) x ไม่ติดลบ"""
    return int(Fraction(x) // 1)


def need_int(value, name, low=None, high=None):
    if type(value) is not int:  # bool และ float ไม่ใช่ int
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def need_bool(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(4, 100)}


def cashback(amount, tier, birthday):
    """เงินคืนสมาชิก (สตางค์)
    นโยบาย: ตรวจ input ทุกตัวก่อน; amount < 10000 -> 0;
    C1: silver ไม่ได้สิทธิ์เดือนเกิด (คูณ 2 เฉพาะ gold/platinum);
    C2: เงินที่ร้านจ่ายออก ปัดลง แล้วจึงจำกัดเพดาน 20000 สตางค์/บิล"""
    need_int(amount, "amount", 0)
    if type(tier) is not str or tier not in RATES:
        raise ValueError("tier ต้องเป็น silver/gold/platinum")
    need_bool(birthday, "birthday")
    if amount < 10000:
        return 0
    value = amount * RATES[tier]
    if birthday and tier != "silver":
        value *= 2
    return min(round_down(value), 20000)


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
