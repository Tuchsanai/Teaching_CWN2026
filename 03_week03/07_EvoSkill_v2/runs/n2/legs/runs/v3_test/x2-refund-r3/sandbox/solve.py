"""BaanKafe: คิดเงินคืนคอร์สสอนชงกาแฟ (หน่วยสตางค์)"""
import json
import sys
from fractions import Fraction


def round_down(x):
    """ปัดลง — เงินคืนเป็นเงินที่ร้านจ่ายออก ไม่จ่ายเกินสิทธิ์"""
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
    if used_percent > 80:  # เรียนเกิน 80% ไม่คืนเงิน (80 พอดียังคืน)
        return 0
    amount = Fraction(paid) * (100 - used_percent) / 100
    if restock:
        amount *= 1 - Fraction(125, 1000)  # หักค่าดำเนินการ 12.5% ของยอดคืน
    return round_down(amount)  # สมมติฐาน: ปัดลง (ร้านจ่ายออก) ปัดครั้งเดียวตอนท้าย


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
