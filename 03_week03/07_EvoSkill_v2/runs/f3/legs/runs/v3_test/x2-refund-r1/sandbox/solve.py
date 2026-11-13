"""คิดเงิน BaanKafe — template: คัดลอกเป็น solve.py แล้วแก้เฉพาะฟังก์ชันหลัก"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (x ไม่ติดลบ)"""
    return int((Fraction(x) * 2 + 1) // 2)


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
    if used_percent > 80:
        return 0
    amount = Fraction(paid) * Fraction(100 - used_percent, 100)
    if restock:
        amount *= Fraction(875, 1000)
    return half_up(amount)


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = refund(**args)  # เปลี่ยนเป็นชื่อฟังก์ชันจริง
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
