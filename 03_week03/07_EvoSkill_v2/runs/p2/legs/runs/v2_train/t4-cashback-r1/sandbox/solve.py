from fractions import Fraction

_RATES = {"silver": Fraction(3, 200), "gold": Fraction(1, 40), "platinum": Fraction(1, 25)}


def cashback(amount, tier, birthday):
    # กติกา H: คำนวณแม่นยำด้วย Fraction ปัดครึ่งขึ้นครั้งเดียวตอนท้าย + ตรวจอินพุต
    if tier not in _RATES:
        raise ValueError("invalid tier")
    if amount < 0:
        raise ValueError("amount must be >= 0")
    if amount < 10000:  # ต่ำกว่า 100 บาท ไม่ได้เงินคืน (พอดี 100 บาท ได้)
        return 0
    x = amount * _RATES[tier]
    if birthday:
        x *= 2
    x = min(x, Fraction(20000))  # เพดาน 200 บาทต่อบิล หลังคูณ 2
    return int((2 * x.numerator + x.denominator) // (2 * x.denominator))
