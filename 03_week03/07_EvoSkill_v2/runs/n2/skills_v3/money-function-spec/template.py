"""ฟังก์ชันคิดเงิน (หน่วยสตางค์) · half-up ครั้งเดียวตอนท้าย · ตรวจ input เข้ม"""
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


def need_choice(value, name, choices):
    if type(value) is not str or value not in choices:
        raise ValueError(f"{name} ไม่อยู่ในรายการที่กำหนด")
    return value


# ตัวอย่างโครง (เปลี่ยนชื่อ/พารามิเตอร์ตามโจทย์):
def my_function(amount, flag):
    need_int(amount, "amount", 0)
    need_bool(flag, "flag")
    x = Fraction(amount)
    # ... คูณ/บวกด้วย Fraction ตามลำดับในโจทย์ ไม่ปัดกลางทาง ...
    return half_up(x)


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = my_function(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
