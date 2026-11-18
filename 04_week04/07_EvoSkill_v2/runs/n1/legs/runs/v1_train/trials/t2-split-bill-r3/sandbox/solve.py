"""split_bill · BaanKafe"""
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


def split_bill(total, people, tip_percent):
    # ตรวจ input ทุกตัวก่อนคำนวณ
    need_int(total, "total", 0)
    need_int(people, "people", 1)
    need_int(tip_percent, "tip_percent", 0, 100)
    # นโยบาย: ยอดรวม (บิล+ทิป) เป็นเงินที่ลูกค้าจ่าย -> half-up ครั้งเดียว
    grand = half_up(Fraction(total) * (100 + tip_percent) / 100)
    # หารเท่ากัน เศษกระจายให้คนแรก ๆ คนละ 1 สตางค์ (ผลรวม = grand)
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = split_bill(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
