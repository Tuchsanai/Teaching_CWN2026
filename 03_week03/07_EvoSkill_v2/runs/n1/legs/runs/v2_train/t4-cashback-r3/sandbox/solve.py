"""โครง solve.py สำหรับฟังก์ชันคิดเงิน (สตางค์) — แก้เฉพาะฟังก์ชันหลักด้านล่าง"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (x >= 0) ใช้กับเงินที่ลูกค้าจ่าย"""
    return int((Fraction(x) * 2 + 1) // 2)


def round_down(x):
    """ปัดลง ใช้กับเงินที่ร้านจ่ายออก (cashback/rebate)"""
    return int(Fraction(x) // 1)


def need_int(value, name, low=None, high=None):
    if type(value) is not int:  # bool, float, str ไม่ผ่าน
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


RATES = {"silver": Fraction(3, 200), "gold": Fraction(1, 40), "platinum": Fraction(1, 25)}
MIN_AMOUNT = 10000  # 100 บาท
CAP = 20000  # 200 บาทต่อบิล


def cashback(amount, tier, birthday):
    # ตรวจ input ทั้งหมดก่อน early-return
    need_int(amount, "amount", 0)
    need_choice(tier, "tier", RATES)
    need_bool(birthday, "birthday")
    if amount < MIN_AMOUNT:
        return 0
    rate = RATES[tier]
    # สมมติฐาน (money-edge-policies ข้อ 2): silver ไม่ได้สิทธิ์เดือนเกิด x2
    if birthday and tier != "silver":
        rate *= 2
    value = Fraction(amount) * rate
    value = min(value, Fraction(CAP))
    return round_down(value)  # เงินที่ร้านจ่ายออก -> ปัดลงครั้งเดียว


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = cashback(**args)  # <-- เปลี่ยนชื่อ
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
