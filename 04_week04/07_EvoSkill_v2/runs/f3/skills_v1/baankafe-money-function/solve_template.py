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


# ---- ตัวอย่างโครง (เปลี่ยนชื่อ/พารามิเตอร์ให้ตรงโจทย์) ----
def example_fn(amount, member):
    need_int(amount, "amount", 0)          # 1) ตรวจ input ทุกตัวก่อน
    need_bool(member, "member")
    x = Fraction(amount)                   # 2) คำนวณด้วย Fraction
    if member:
        x *= Fraction(90, 100)
    return half_up(x)                      # 3) ปัดครั้งเดียวตอนท้าย


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = example_fn(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
