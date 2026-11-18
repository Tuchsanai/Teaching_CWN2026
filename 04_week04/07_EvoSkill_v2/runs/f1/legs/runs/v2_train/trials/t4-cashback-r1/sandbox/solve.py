"""แม่แบบ solve.py ของ BaanKafe — แก้เฉพาะฟังก์ชันหลัก (ชื่อ/พารามิเตอร์ตามโจทย์)"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้น (เงินที่ลูกค้าจ่าย) x ไม่ติดลบ"""
    return int((Fraction(x) * 2 + 1) // 2)


def round_down(x):
    """ปัดลง (เงินที่ร้านจ่ายออก เช่น cashback) x ไม่ติดลบ"""
    return int(Fraction(x) // 1)


def need_int(value, name, low=None, high=None):
    if type(value) is not int:  # bool, float, str, None ไม่ผ่าน
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def need_bool(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def need_choice(value, name, choices):
    if type(value) is not str or value not in choices:
        raise ValueError(f"{name} ต้องเป็นหนึ่งใน {sorted(choices)}")
    return value


# ตัวอย่าง: ตรวจ list ของ dict
# if type(items) is not list: raise ValueError("items ต้องเป็น list")
# for it in items:
#     if type(it) is not dict: raise ValueError("แต่ละรายการต้องเป็น dict")
#     price = need_int(it.get("price"), "price", 0); qty = need_int(it.get("qty"), "qty", 1)


RATES = {"silver": Fraction(3, 200), "gold": Fraction(5, 200), "platinum": Fraction(4, 100)}
RATES["gold"] = Fraction(25, 1000)
MIN_AMOUNT = 10000  # 100 บาท
CAP = 20000  # 200 บาทต่อบิล


def cashback(amount, tier, birthday):
    amount = need_int(amount, "amount", 0)
    need_choice(tier, "tier", RATES)
    need_bool(birthday, "birthday")
    if amount < MIN_AMOUNT:
        return 0
    value = amount * RATES[tier]
    # นโยบายร้าน C1: เดือนเกิดคูณ 2 เฉพาะ gold/platinum (silver ไม่ได้สิทธิ์)
    if birthday and tier != "silver":
        value *= 2
    return min(CAP, round_down(value))  # เงินที่ร้านจ่ายออก -> ปัดลง


TARGET = "cashback"


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = globals()[TARGET](**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
