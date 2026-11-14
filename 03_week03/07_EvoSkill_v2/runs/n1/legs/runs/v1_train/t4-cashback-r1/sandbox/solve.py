"""BaanKafe cashback (หน่วยสตางค์)

สมมติฐาน (โจทย์ไม่ได้ระบุ):
- เงินคืนเป็นเงินที่ร้านจ่ายออก -> ปัดลง ครั้งเดียวท้ายสุด
- เกณฑ์ "ต่ำกว่า 100 บาท" เทียบกับยอดดิบ (amount < 10000 -> 0)
- เดือนเกิดคูณ 2 กับทุก tier แล้วค่อยใช้เพดาน 200 บาท (20000 สตางค์)
- input ผิดชนิด/ช่วง raise ValueError ก่อน early-return ทุกกรณี
"""
import json
import sys
from fractions import Fraction

RATES = {
    "silver": Fraction(15, 1000),
    "gold": Fraction(25, 1000),
    "platinum": Fraction(4, 100),
}
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


def need_choice(value, name, choices):
    if type(value) is not str or value not in choices:
        raise ValueError(f"{name} ไม่อยู่ในรายการที่อนุญาต")
    return value


def cashback(amount, tier, birthday):
    need_int(amount, "amount", 0)
    need_choice(tier, "tier", RATES)
    need_bool(birthday, "birthday")
    if amount < MIN_AMOUNT:
        return 0
    value = Fraction(amount) * RATES[tier]
    if birthday:
        value *= 2
    return round_down(min(value, CAP))


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
