"""BaanKafe: คิดเงินคืนสมาชิก (หน่วยสตางค์ ผลเป็นจำนวนเต็ม)

นโยบาย:
- ยอดต่ำกว่า 10000 สตางค์ (100 บาท) ไม่ได้เงินคืน
- อัตรา silver 1.5% · gold 2.5% · platinum 4%
- C1: เดือนเกิดคูณ 2 เฉพาะ gold และ platinum (silver ไม่ได้สิทธิ์ ตามสกิล known-policies)
- C2: เงินคืนคือเงินที่ร้านจ่ายออก -> ปัดลง (floor) ครั้งเดียวท้ายสุด
- เพดาน 20000 สตางค์ (200 บาท) ต่อบิล หลังคูณ 2 และปัดลง
"""
import json
import sys
from fractions import Fraction

RATES = {
    "silver": Fraction(15, 1000),
    "gold": Fraction(25, 1000),
    "platinum": Fraction(4, 100),
}
MIN_AMOUNT = 10000
CAP = 20000


def round_down(x):
    """ปัดลง — ใช้กับเงินที่ร้านจ่ายออก"""
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


def need_choice(value, name, choices):
    if type(value) is not str or value not in choices:
        raise ValueError(f"{name} ต้องเป็นหนึ่งใน {list(choices)}")
    return value


def cashback(amount, tier, birthday):
    need_int(amount, "amount", 0)
    need_choice(tier, "tier", list(RATES))
    need_bool(birthday, "birthday")
    if amount < MIN_AMOUNT:
        return 0
    x = Fraction(amount) * RATES[tier]
    if birthday and tier != "silver":
        x *= 2
    return min(CAP, round_down(x))


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
