"""แม่แบบ solve.py สำหรับฟังก์ชันคิดเงินของ BaanKafe — คัดลอกไปแล้วแก้เฉพาะตัวฟังก์ชันหลัก"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (x ไม่ติดลบ) — ใช้กับเงินที่ลูกค้าต้องจ่าย"""
    return int((Fraction(x) * 2 + 1) // 2)


def round_down(x):
    """ปัดลง — ใช้กับเงินที่ร้านจ่ายออก (เงินคืน/คูปอง/แต้ม)"""
    return int(Fraction(x) // 1)


def need_int(value, name, low=None, high=None):
    if type(value) is not int:  # bool, float, str ไม่ผ่านทั้งหมด
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def need_bool(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def my_function(a, b):  # <- เปลี่ยนชื่อ/พารามิเตอร์ตามโจทย์
    need_int(a, "a", 0)
    need_bool(b, "b")
    amount = Fraction(a)          # คิดด้วย Fraction ตลอด ห้ามใช้ float
    # ... คูณ/ลดตามลำดับที่โจทย์ระบุ ไม่ปัดระหว่างทาง ...
    return half_up(amount)        # ปัดครั้งเดียวตอนท้าย


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
