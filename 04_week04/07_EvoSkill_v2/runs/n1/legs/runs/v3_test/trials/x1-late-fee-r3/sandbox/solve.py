"""late_fee · BaanKafe ค่าปรับชำระช้า (ลูกค้าขายส่ง)"""
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


def late_fee(amount, days_late):
    need_int(amount, "amount", 0)
    need_int(days_late, "days_late", 0, 365)
    # ช้าไม่เกิน 3 วัน ไม่คิดค่าปรับ
    if days_late <= 3:
        return 0
    # วันละ 0.75% นับทุกวันที่ช้า (รวม 3 วันแรก) เป็น Fraction ไม่ปัดกลางทาง
    fee = Fraction(amount) * Fraction(75, 10000) * days_late
    # เพดาน 15% ของยอดค้างชำระ
    fee = min(fee, Fraction(amount) * Fraction(15, 100))
    # นโยบาย: เงินเข้าร้าน -> ปัด half-up ครั้งเดียวตอนท้าย
    return half_up(fee)


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
