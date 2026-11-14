"""BaanKafe: คิดเงินคืนสมาชิก (หน่วยสตางค์)"""
import json
import sys
from fractions import Fraction

RATES = {"silver": Fraction(3, 200), "gold": Fraction(1, 40), "platinum": Fraction(1, 25)}
MIN_AMOUNT = 100 * 100  # ต่ำกว่า 100 บาท ไม่ได้เงินคืน
CAP = 200 * 100  # สูงสุด 200 บาทต่อบิล


def round_down(x):
    """ปัดลง — เงินคืนเป็นเงินที่ร้านจ่ายออก"""
    return int(Fraction(x) // 1)


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount ต้องเป็นจำนวนเต็มสตางค์ ตั้งแต่ 0")
    if type(tier) is not str or tier not in RATES:
        raise ValueError("tier ต้องเป็น silver, gold หรือ platinum")
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น True หรือ False")

    if amount < MIN_AMOUNT:
        return 0
    value = amount * RATES[tier]
    # มาตรฐานร้าน: โบนัสเดือนเกิด x2 ไม่ใช้กับ silver (เฉพาะ gold/platinum)
    if birthday and tier != "silver":
        value *= 2
    # ปัดลงก่อน แล้วค่อยใช้เพดาน (ผลเท่ากับเพดานก่อนเพราะ CAP เป็นจำนวนเต็ม)
    return min(round_down(value), CAP)


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
