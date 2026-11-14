"""late_fee(amount, days_late) — ค่าปรับชำระช้าของลูกค้าขายส่ง BaanKafe (หน่วยสตางค์)

กฎ: ช้า <= 3 วัน ไม่คิด; ช้า > 3 วัน คิดวันละ 0.75% นับทุกวัน (รวม 3 วันแรก);
เพดาน 15% ของยอดค้าง; ปัดครึ่งขึ้นครั้งเดียวตอนท้าย

สมมติฐาน:
- ค่าปรับเป็นเงินที่ลูกค้าจ่าย -> ปัดครึ่งขึ้น (half-up) เป็นสตางค์
- amount = 0 ใช้สูตรปกติ (ค่าปรับ 0) ไม่ error
- ทุกพารามิเตอร์ต้องเป็น int (ปฏิเสธ float/str/bool/None)
"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (x >= 0)"""
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
    if days_late <= 3:
        return 0
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
