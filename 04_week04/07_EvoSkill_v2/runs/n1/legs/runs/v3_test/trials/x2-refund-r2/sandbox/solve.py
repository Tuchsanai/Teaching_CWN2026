"""refund · BaanKafe"""
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


def refund(paid, used_percent, restock):
    need_int(paid, "paid", 0)
    need_int(used_percent, "used_percent", 0, 100)
    need_bool(restock, "restock")
    # นโยบาย: เรียนเกิน 80% ไม่คืน (80 พอดียังคืน)
    if used_percent > 80:
        return 0
    amount = Fraction(paid) * Fraction(100 - used_percent, 100)
    if restock:
        amount *= Fraction(875, 1000)  # หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
    # นโยบาย C2: เงินที่ร้านจ่ายออก ปัดลง ครั้งเดียวตอนท้าย
    return round_down(amount)


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = refund(**args)  # <- เปลี่ยนเป็นชื่อฟังก์ชันจริง
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
