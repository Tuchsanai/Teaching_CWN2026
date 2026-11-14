"""BaanKafe: คิดเงินคืนสมาชิก (หน่วยสตางค์)"""
import json
import sys
from fractions import Fraction

RATES = {
    "silver": Fraction(15, 1000),
    "gold": Fraction(25, 1000),
    "platinum": Fraction(4, 100),
}
MIN_AMOUNT = 100 * 100  # 100 บาท
CAP = 200 * 100  # 200 บาทต่อบิล


def round_down(x):
    """ปัดลง — เงินที่ร้านจ่ายออก"""
    return int(Fraction(x) // 1)


def cashback(amount, tier, birthday):
    # ข้อสันนิษฐาน: โบนัสเดือนเกิด 2 เท่า ใช้กับทุกระดับ (โจทย์ไม่ได้จำกัดระดับ)
    # เงินคืนเป็นเงินที่ร้านจ่ายออก จึงปัดลง; เพดานใช้หลังคูณและปัดเศษแล้ว
    if type(amount) is not int or amount < 0:
        raise ValueError("amount ต้องเป็นจำนวนเต็มสตางค์ตั้งแต่ 0")
    if type(tier) is not str or tier not in RATES:
        raise ValueError("tier ต้องเป็น silver, gold หรือ platinum")
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น True หรือ False")

    if amount < MIN_AMOUNT:
        return 0
    value = Fraction(amount) * RATES[tier]
    if birthday:
        value *= 2
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
