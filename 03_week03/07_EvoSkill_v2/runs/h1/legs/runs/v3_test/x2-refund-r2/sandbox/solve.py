"""คิดเงินคืนคอร์สสอนชงกาแฟ ของร้าน BaanKafe

กฎ:
- คืนตามสัดส่วนที่ยังไม่ได้เรียน = paid * (100 - used_percent) / 100
- เรียนไปแล้วเกิน 80% (used_percent > 80) ไม่คืนเงิน
- ถ้า restock เป็น True หักค่าดำเนินการ 12.5% ของยอดที่จะคืน (คงเหลือ 7/8)
- คำนวณเป็นเศษส่วนทั้งหมด แล้วปัดครึ่งขึ้นเป็นสตางค์ครั้งเดียวตอนท้าย
"""

import json
import sys
from fractions import Fraction

FEE_KEEP = Fraction(7, 8)      # หักค่าดำเนินการ 12.5% คงเหลือ 87.5% = 7/8
NO_REFUND_ABOVE = 80           # เรียนเกินเปอร์เซ็นต์นี้ไม่คืนเงิน


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม สำหรับค่าที่ไม่ติดลบ"""
    return int((Fraction(x) * 2 + 1) // 2)


def refund(paid, used_percent, restock):
    """คืนค่าเงินที่ต้องคืนลูกค้า เป็นจำนวนเต็มสตางค์

    paid: เงินที่ลูกค้าจ่าย (สตางค์, int, ไม่ติดลบ)
    used_percent: เรียนไปแล้วกี่เปอร์เซ็นต์ (int, 0–100)
    restock: True = หักค่าดำเนินการ 12.5% (bool)
    """
    if type(paid) is not int:
        raise ValueError("paid ต้องเป็นจำนวนเต็มสตางค์")
    if paid < 0:
        raise ValueError("paid ต้องไม่ติดลบ")
    if type(used_percent) is not int:
        raise ValueError("used_percent ต้องเป็นจำนวนเต็ม")
    if used_percent < 0 or used_percent > 100:
        raise ValueError("used_percent ต้องอยู่ระหว่าง 0 ถึง 100")
    if type(restock) is not bool:
        raise ValueError("restock ต้องเป็น True หรือ False")

    if used_percent > NO_REFUND_ABOVE:
        return 0

    amount = Fraction(paid * (100 - used_percent), 100)
    if restock:
        amount *= FEE_KEEP
    return _half_up(amount)


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = refund(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
