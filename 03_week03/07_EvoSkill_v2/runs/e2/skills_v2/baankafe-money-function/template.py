"""template ฟังก์ชันคิดเงิน (สตางค์, half-up, ตรวจ input เข้ม)"""
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

def FUNCTION_NAME(a, b, c):  # TODO: เปลี่ยนชื่อ/พารามิเตอร์ให้ตรงโจทย์
    # 1) ตรวจ input ทุกตัวก่อน (ValueError)
    need_int(a, "a", 0)          # TODO: ช่วงตามโจทย์
    need_int(b, "b", 0)
    need_bool(c, "c")
    # 2) คำนวณด้วย Fraction ต่อเนื่องตามลำดับในโจทย์ (ไม่ปัดระหว่างทาง)
    amount = Fraction(a)
    # amount *= Fraction(95, 100)   # ตัวอย่าง: ลด 5%
    # 3) ปัดครึ่งขึ้นครั้งเดียวตอนท้าย แล้วค่อยใช้ cap (min/max) ถ้ามี
    return half_up(amount)


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = FUNCTION_NAME(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
