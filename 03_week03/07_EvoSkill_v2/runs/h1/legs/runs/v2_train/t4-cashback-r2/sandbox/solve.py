"""คำนวณเงินคืนสมาชิกร้าน BaanKafe

หน่วยทั้งหมดเป็นสตางค์ (จำนวนเต็ม)
- amount  : ยอดซื้อ (สตางค์, >= 0)
- tier    : "silver" | "gold" | "platinum" (ตรงตัวอักษร)
- birthday: True ถ้าซื้อในเดือนเกิด (ได้เงินคืน 2 เท่า)

กติกา
- อัตราเงินคืน: silver 1.5%, gold 2.5%, platinum 4%
- ยอดซื้อต่ำกว่า 100 บาท (10000 สตางค์) ไม่ได้เงินคืน (ยอด 100 บาทพอดีได้)
- เดือนเกิด ได้เงินคืน 2 เท่า
- เพดานเงินคืน 200 บาท (20000 สตางค์) ต่อบิล ใช้หลังคูณทุกตัวแล้ว
- ผลลัพธ์เป็นจำนวนเต็มสตางค์ ปัดครึ่งขึ้นครั้งเดียวตอนท้าย
"""
import json
import sys
from fractions import Fraction

# อัตราเงินคืนเป็นเศษส่วน (1.5% = 15/1000, 2.5% = 25/1000, 4% = 40/1000)
RATES = {
    "silver": Fraction(15, 1000),
    "gold": Fraction(25, 1000),
    "platinum": Fraction(40, 1000),
}
MIN_AMOUNT = 100 * 100      # 100 บาท เป็นสตางค์
MAX_CASHBACK = 200 * 100    # 200 บาท เป็นสตางค์
BIRTHDAY_MULTIPLIER = 2


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม สำหรับค่าที่ไม่ติดลบ"""
    return int((Fraction(x) * 2 + 1) // 2)


def cashback(amount, tier, birthday):
    """คืนค่าเงินคืนเป็นจำนวนเต็มสตางค์"""
    if type(amount) is not int:
        raise ValueError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if not isinstance(tier, str) or tier not in RATES:
        raise ValueError('tier ต้องเป็น "silver", "gold" หรือ "platinum"')
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น True หรือ False")

    if amount < MIN_AMOUNT:
        return 0

    value = Fraction(amount) * RATES[tier]
    if birthday:
        value *= BIRTHDAY_MULTIPLIER
    value = min(value, MAX_CASHBACK)
    return _half_up(value)


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = cashback(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
