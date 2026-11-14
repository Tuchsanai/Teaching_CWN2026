"""BaanKafe: ค่าปรับชำระเงินช้าของลูกค้าขายส่ง (หน่วยสตางค์)"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้น — เงินที่ลูกค้าจ่าย (ค่าปรับ)"""
    return int((Fraction(x) * 2 + 1) // 2)


def need_int(value, name, low=None, high=None):
    if type(value) is not int:  # ปฏิเสธ float, str, bool
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def late_fee(amount, days_late):
    need_int(amount, "amount", 0)
    need_int(days_late, "days_late", 0, 365)
    if days_late <= 3:  # ช้าไม่เกิน 3 วัน ไม่คิดค่าปรับ
        return 0
    amt = Fraction(amount)
    fee = amt * Fraction(75, 10000) * days_late  # 0.75%/วัน นับทุกวัน
    cap = amt * Fraction(15, 100)  # สูงสุด 15%
    return half_up(min(fee, cap))  # ปัดครั้งเดียวตอนท้าย (half-up)


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
