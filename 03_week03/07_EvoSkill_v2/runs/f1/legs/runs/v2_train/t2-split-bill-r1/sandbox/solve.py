"""BaanKafe: split_bill — หารบิล (หน่วยสตางค์)"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม — เงินที่ลูกค้าจ่าย"""
    return int((Fraction(x) * 2 + 1) // 2)


def need_int(value, name, low=None, high=None):
    if type(value) is not int:  # ปฏิเสธ bool และ float
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def split_bill(total, people, tip_percent):
    need_int(total, "total", 0)
    need_int(people, "people", 1)
    need_int(tip_percent, "tip_percent", 0, 100)
    # ยอดบิล + ทิป ปัดครึ่งขึ้นเป็นสตางค์ครั้งเดียวก่อนหาร (ลูกค้าจ่าย)
    grand = half_up(Fraction(total) * (100 + tip_percent) / 100)
    base, extra = divmod(grand, people)
    # คนแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์
    return [base + 1] * extra + [base] * (people - extra)


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
