"""BaanKafe cashback (หน่วยสตางค์)"""
import json
import sys
from fractions import Fraction

RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(4, 100)}
MIN_AMOUNT = 100 * 100   # ต่ำกว่า 100 บาท ไม่ได้เงินคืน
CAP = 200 * 100          # สูงสุด 200 บาทต่อบิล


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount ต้องเป็นจำนวนเต็ม >= 0")
    if type(tier) is not str or tier not in RATES:
        raise ValueError("tier ไม่ถูกต้อง")
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น True หรือ False")
    if amount < MIN_AMOUNT:
        return 0
    value = amount * RATES[tier]
    # มาตรฐานร้าน: โบนัสเดือนเกิด x2 ไม่ใช้กับ silver
    if birthday and tier != "silver":
        value *= 2
    # เงินที่ร้านจ่ายออก -> ปัดลง ครั้งเดียว แล้วค่อยใช้เพดาน
    return min(int(value // 1), CAP)


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
