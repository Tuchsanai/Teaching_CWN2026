"""BaanKafe cashback (หน่วยสตางค์)

สมมติฐาน:
- ยอดต่ำกว่า 10000 สตางค์ (100 บาท) ได้ 0; เทียบกับยอดดิบ (>= 10000 ได้สิทธิ์)
- เดือนเกิดคูณ 2 กับทุกระดับ แล้วจึงใช้เพดาน 20000 สตางค์ (200 บาท)
- เงินคืนเป็นเงินที่ร้านจ่ายออก -> ปัดลง ครั้งเดียวตอนท้าย
- ตรวจ input ก่อน early-return ทุกกรณี
"""
import json
import sys
from fractions import Fraction

RATES = {"silver": Fraction(3, 200), "gold": Fraction(1, 40), "platinum": Fraction(1, 25)}
MIN_AMOUNT = 10000
CAP = 20000


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount ต้องเป็นจำนวนเต็ม >= 0")
    if type(tier) is not str or tier not in RATES:
        raise ValueError("tier ไม่ถูกต้อง")
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น True หรือ False")
    if amount < MIN_AMOUNT:
        return 0
    value = Fraction(amount) * RATES[tier]
    if birthday:
        value *= 2
    value = min(value, Fraction(CAP))
    return int(value // 1)


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = cashback(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
