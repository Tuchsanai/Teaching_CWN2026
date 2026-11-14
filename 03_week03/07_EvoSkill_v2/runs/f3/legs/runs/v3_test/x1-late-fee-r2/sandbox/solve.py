"""BaanKafe: ค่าปรับชำระช้า (หน่วยสตางค์)"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ — ค่าปรับเป็นเงินที่ลูกค้าจ่ายให้ร้าน"""
    return int((Fraction(x) * 2 + 1) // 2)


def need_int(value, name, low=None, high=None):
    if type(value) is not int:  # bool และ float ไม่ใช่ int
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def late_fee(amount, days_late):
    # validate ก่อนคำนวณเสมอ
    need_int(amount, "amount", 0)
    need_int(days_late, "days_late", 0, 365)
    if days_late <= 3:  # ช้าไม่เกิน 3 วัน ไม่คิดค่าปรับ
        return 0
    # 0.75% ต่อวัน นับทุกวันที่ช้า (รวม 3 วันแรก) สูงสุด 15% ของยอด
    fee = min(Fraction(amount) * Fraction(75, 10000) * days_late,
              Fraction(amount) * Fraction(15, 100))
    return half_up(fee)  # ปัดครั้งเดียวตอนท้าย


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
