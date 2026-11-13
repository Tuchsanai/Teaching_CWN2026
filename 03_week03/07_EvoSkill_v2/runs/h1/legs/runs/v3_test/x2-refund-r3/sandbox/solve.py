"""คิดเงินคืนคอร์สสอนชงกาแฟ ของ BaanKafe

refund(paid, used_percent, restock) -> int (สตางค์)

- paid           : เงินที่ลูกค้าจ่าย (สตางค์, int, ตั้งแต่ 0)
- used_percent   : เรียนไปแล้วกี่เปอร์เซ็นต์ (int, 0–100)
- restock        : True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน

กติกา:
1. เรียนไปแล้วเกิน 80% (used_percent > 80) ไม่คืนเงิน -> 0
2. ยอดคืนตามสัดส่วนที่ยังไม่ได้เรียน = paid * (100 - used_percent) / 100
3. ถ้า restock = True หักค่าดำเนินการ 12.5% ของยอดที่จะคืน -> คูณ 7/8
4. ปัดครึ่งขึ้นเป็นสตางค์ครั้งเดียวตอนท้าย (คำนวณด้วย Fraction ไม่ใช้ float)
"""

import json
import sys
from fractions import Fraction

FEE_RATE = Fraction(125, 1000)   # 12.5%
USED_LIMIT = 80                  # เกินนี้ไม่คืนเงิน


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม รับ Fraction ที่ไม่ติดลบ"""
    return int((Fraction(x) * 2 + 1) // 2)


def refund(paid, used_percent, restock):
    if type(paid) is not int:
        raise ValueError("paid ต้องเป็นจำนวนเต็ม (สตางค์)")
    if paid < 0:
        raise ValueError("paid ต้องไม่น้อยกว่า 0")
    if type(used_percent) is not int:
        raise ValueError("used_percent ต้องเป็นจำนวนเต็ม")
    if used_percent < 0 or used_percent > 100:
        raise ValueError("used_percent ต้องอยู่ระหว่าง 0 ถึง 100")
    if type(restock) is not bool:
        raise ValueError("restock ต้องเป็น True หรือ False")

    if used_percent > USED_LIMIT:
        return 0

    amount = Fraction(paid * (100 - used_percent), 100)
    if restock:
        amount -= amount * FEE_RATE
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
