"""late_fee · BaanKafe"""
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


def late_fee(amount, days_late):
    """ค่าปรับชำระช้า (สตางค์)
    นโยบาย: ไม่เกิน 3 วัน = 0; เกิน 3 วันคิด 0.75%/วัน ทุกวันที่ช้า (รวม 3 วันแรก)
    เพดาน 15% ของยอด; เงินเข้าร้าน -> ปัด half-up ครั้งเดียวตอนท้าย"""
    need_int(amount, "amount", 0)
    need_int(days_late, "days_late", 0, 365)
    if days_late <= 3:
        return 0
    rate = min(Fraction(75, 10000) * days_late, Fraction(15, 100))
    return half_up(Fraction(amount) * rate)


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = late_fee(**args)  # <- เปลี่ยนเป็นชื่อฟังก์ชันจริง
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
