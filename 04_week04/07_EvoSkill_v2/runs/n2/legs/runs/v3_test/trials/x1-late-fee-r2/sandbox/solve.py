"""BaanKafe: ค่าปรับชำระช้าของลูกค้าขายส่ง (หน่วยสตางค์)"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ)"""
    return int((Fraction(x) * 2 + 1) // 2)


def need_int(value, name, low=None, high=None):
    if type(value) is not int:  # bool, float, str ไม่ผ่าน
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def late_fee(amount, days_late):
    need_int(amount, "amount", 0)
    need_int(days_late, "days_late", 0, 365)
    if days_late <= 3:  # ช้าไม่เกิน 3 วัน ไม่คิดค่าปรับ
        return 0
    # สมมติฐาน: ค่าปรับเป็นเงินที่ลูกค้าจ่าย -> ปัดครึ่งขึ้นครั้งเดียวตอนจบ
    # คิดอัตรา 0.75%/วัน นับทุกวัน (รวม 3 วันแรก) แล้วจำกัดเพดาน 15% ก่อนคูณยอด
    rate = min(Fraction(75, 10000) * days_late, Fraction(15, 100))
    return half_up(Fraction(amount) * rate)


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
