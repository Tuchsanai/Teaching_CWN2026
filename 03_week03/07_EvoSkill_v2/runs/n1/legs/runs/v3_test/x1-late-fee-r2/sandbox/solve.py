"""BaanKafe: ค่าปรับชำระช้าของลูกค้าขายส่ง (หน่วยสตางค์)"""
import json
import sys
from fractions import Fraction

GRACE_DAYS = 3
DAILY_RATE = Fraction(75, 10000)  # 0.75% ต่อวัน
MAX_RATE = Fraction(15, 100)      # เพดาน 15%


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (x ไม่ติดลบ)"""
    return int((Fraction(x) * 2 + 1) // 2)


def need_int(value, name, low=None, high=None):
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def late_fee(amount, days_late):
    need_int(amount, "amount", 0)
    need_int(days_late, "days_late", 0, 365)
    if days_late <= GRACE_DAYS:
        return 0
    fee = half_up(amount * DAILY_RATE * days_late)
    cap = half_up(amount * MAX_RATE)
    return min(fee, cap)


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = late_fee(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
