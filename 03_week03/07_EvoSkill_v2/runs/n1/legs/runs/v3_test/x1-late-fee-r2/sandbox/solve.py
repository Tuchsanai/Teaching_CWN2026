"""late_fee — ค่าปรับชำระช้าของลูกค้าขายส่ง BaanKafe (หน่วยสตางค์)

กฎ: ช้า <= 3 วัน ไม่คิดค่าปรับ; ช้า > 3 วัน คิดวันละ 0.75% ของยอดค้าง
นับทุกวันที่ช้า (รวม 3 วันแรก); ค่าปรับสูงสุด 15% ของยอดค้าง

สมมติฐาน (brief เงียบ):
- amount เป็น int >= 0, days_late เป็น int 0-365; float/str/bool/None -> ValueError
- ค่าปรับเป็นเงินที่ลูกค้าจ่าย -> ปัดครึ่งขึ้น ครั้งเดียวตอนท้าย (หลังใช้เพดาน)
- ตรวจ input ครบก่อนคืน 0 ในทุกสาขา
"""
import json
import sys
from fractions import Fraction

GRACE_DAYS = 3
DAILY_RATE = Fraction(75, 10000)  # 0.75%
CAP_RATE = Fraction(15, 100)      # 15%


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
    if days_late <= GRACE_DAYS:
        return 0
    rate = min(DAILY_RATE * days_late, CAP_RATE)
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
