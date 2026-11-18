"""แม่แบบ solve.py สำหรับฟังก์ชันคิดเงินของ BaanKafe — แก้เฉพาะฟังก์ชันหลักและชื่อ"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (x ไม่ติดลบ) — ใช้กับเงินที่ลูกค้าจ่าย"""
    return int((Fraction(x) * 2 + 1) // 2)


def round_down(x):
    """ปัดลง — ใช้กับเงินที่ร้านจ่ายออก เช่น เงินคืน"""
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


def refund(paid, used_percent, restock):
    """เงินคืนคอร์สสอนชงกาแฟ (สตางค์)

    - คืนตามสัดส่วนที่ยังไม่ได้เรียน: paid x (100-used)/100
    - เรียนเกิน 80% (81 ขึ้นไป) ไม่คืนเงิน ; พอดี 80% ยังคืน
    - restock=True หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
    - เงินคืนคือเงินที่ร้านจ่ายออก -> ปัดลง (floor) ครั้งเดียวตอนท้าย
    """
    need_int(paid, "paid", 0)
    need_int(used_percent, "used_percent", 0, 100)
    need_bool(restock, "restock")
    if used_percent > 80:
        return 0
    x = Fraction(paid) * (100 - used_percent) / 100
    if restock:
        x *= Fraction(875, 1000)
    return round_down(x)


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = refund(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
