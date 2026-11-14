from fractions import Fraction

_RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(4, 100)}
_MIN_AMOUNT = 10000   # 100 บาท (สตางค์)
_CAP = 20000          # 200 บาท (สตางค์)


def cashback(amount, tier, birthday):
    # ตรวจ input ก่อนทุกอย่าง
    if type(amount) is not int or amount < 0:
        raise ValueError("amount must be int >= 0")
    if type(tier) is not str or tier not in _RATES:
        raise ValueError("invalid tier")
    if type(birthday) is not bool:
        raise ValueError("birthday must be bool")
    if amount < _MIN_AMOUNT:
        return 0
    value = Fraction(amount) * _RATES[tier]
    if birthday:
        value *= 2  # โจทย์: เดือนเกิดได้ 2 เท่า (ทุกระดับ รวม silver)
    # ข้อสันนิษฐาน: เงินที่ร้านจ่ายออก ปัดทิ้ง (floor) แล้วจึงใช้เพดาน
    return min(_CAP, int(value // 1))
