import json
import sys
from fractions import Fraction


def need_int(value, name, low=None, high=None):
    if type(value) is not int:  # ปฏิเสธ bool, float, str
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def refund(paid, used_percent, restock):
    need_int(paid, "paid", 0)
    need_int(used_percent, "used_percent", 0, 100)
    if type(restock) is not bool:
        raise ValueError("restock ต้องเป็น True หรือ False")
    if used_percent > 80:  # เรียนเกิน 80% ไม่คืนเงิน
        return 0
    value = Fraction(paid * (100 - used_percent), 100)
    if restock:
        value *= Fraction(875, 1000)  # หักค่าดำเนินการ 12.5%
    # เงินที่ร้านจ่ายออก -> ปัดลง (floor) ครั้งเดียวท้ายสุด
    return int(value // 1)


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
