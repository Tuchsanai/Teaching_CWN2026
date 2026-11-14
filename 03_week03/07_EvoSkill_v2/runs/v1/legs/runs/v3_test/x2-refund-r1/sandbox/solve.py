import json
import sys
from fractions import Fraction


def need_int(v, name, low=None, high=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and v < low) or (high is not None and v > high):
        raise ValueError(f"{name} อยู่นอกช่วง")
    return v


def need_bool(v, name):
    if type(v) is not bool:
        raise ValueError(f"{name} ต้องเป็น True/False")
    return v


def refund(paid, used_percent, restock):
    # สมมติฐาน: เงินคืนเป็นเงินที่ร้านจ่ายออก -> ปัดลง (floor) ครั้งเดียวตอนจบ
    need_int(paid, "paid", 0)
    need_int(used_percent, "used_percent", 0, 100)
    need_bool(restock, "restock")
    if used_percent > 80:
        return 0
    amount = Fraction(paid * (100 - used_percent), 100)
    if restock:
        amount *= Fraction(875, 1000)  # หัก 12.5%
    return int(amount // 1)


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = refund(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
