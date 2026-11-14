"""refund(paid, used_percent, restock) — เงินคืนคอร์สสอนชงกาแฟ BaanKafe หน่วยสตางค์

สมมติฐาน (brief เงียบ):
- เงินคืนเป็นเงินที่ร้านจ่ายออก จึงปัดลง (floor) ครั้งเดียวที่ผลสุดท้าย
- used_percent > 80 → คืน 0 (พอดี 80 ยังคืนตามสัดส่วน)
- restock=True หักค่าดำเนินการ 12.5% ของยอดที่จะคืน (คูณ 7/8)
- ตัวเลขต้องเป็น int เท่านั้น (ปฏิเสธ float/str/bool/None), restock ต้องเป็น bool
"""
import json
import sys
from fractions import Fraction


def round_down(x):
    """ปัดลง ใช้กับเงินที่ร้านจ่ายออก"""
    return int(Fraction(x) // 1)


def need_int(value, name, low=None, high=None):
    if type(value) is not int:  # bool, float, str ไม่ผ่าน
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def need_bool(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def refund(paid, used_percent, restock):
    need_int(paid, "paid", 0)
    need_int(used_percent, "used_percent", 0, 100)
    need_bool(restock, "restock")
    if used_percent > 80:
        return 0
    amount = Fraction(paid) * (100 - used_percent) / 100
    if restock:
        amount *= Fraction(875, 1000)  # หัก 12.5%
    return round_down(amount)


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
