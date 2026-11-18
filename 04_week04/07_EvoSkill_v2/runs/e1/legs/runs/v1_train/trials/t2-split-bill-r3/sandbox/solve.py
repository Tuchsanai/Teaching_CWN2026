"""แม่แบบ solve.py สำหรับโจทย์คิดเงิน BaanKafe — แก้เฉพาะฟังก์ชันหลัก (เปลี่ยนชื่อ/พารามิเตอร์ตามโจทย์)"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (x ไม่ติดลบ) — ใช้กับเงินที่ลูกค้าจ่าย/ค่าส่ง/ยอดหาร"""
    return int((Fraction(x) * 2 + 1) // 2)


def round_down(x):
    """ปัดลง (x ไม่ติดลบ) — ใช้กับเงินที่ร้านจ่ายออก เช่น เงินคืน"""
    return int(Fraction(x) // 1)


def need_int(value, name, low=None, high=None):
    if type(value) is not int:  # bool, float, str, None ไม่ใช่ int
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


def split_bill(total, people, tip_percent):
    need_int(total, "total", 0)
    need_int(people, "people", 1)
    need_int(tip_percent, "tip_percent", 0, 100)
    grand = half_up(Fraction(total * (100 + tip_percent), 100))
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = split_bill(**args)  # เปลี่ยนชื่อฟังก์ชัน
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
