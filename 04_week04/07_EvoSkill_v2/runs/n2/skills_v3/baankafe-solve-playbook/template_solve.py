"""แม่แบบ solve.py ของ BaanKafe — แก้เฉพาะฟังก์ชันหลักด้านล่าง"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ)"""
    return int((Fraction(x) * 2 + 1) // 2)


def round_down(x):
    """ปัดเศษทิ้ง (x ไม่ติดลบ)"""
    return int(Fraction(x) // 1)


def need_int(value, name, low=None, high=None):
    if type(value) is not int:  # bool และ float และ str ไม่ผ่าน
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def need_bool(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


# ---- ตัวอย่างฟังก์ชันหลัก (แก้ตามโจทย์) ----
def example(total, flag):
    need_int(total, "total", 0)
    need_bool(flag, "flag")
    amount = Fraction(total)
    if flag:
        amount *= Fraction(90, 100)
    return half_up(amount * Fraction(107, 100))


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = example(**args)  # <- เปลี่ยนชื่อฟังก์ชัน
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
