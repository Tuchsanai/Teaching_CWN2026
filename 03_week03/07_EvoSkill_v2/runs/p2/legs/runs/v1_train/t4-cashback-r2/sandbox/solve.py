from fractions import Fraction

# กติกาปัดเศษ B: คำนวณด้วย Fraction ตลอด แล้วปัดขึ้น (ceil) ครั้งเดียวตอนท้าย
_RATES = {
    "silver": Fraction(15, 1000),    # 1.5%
    "gold": Fraction(25, 1000),      # 2.5%
    "platinum": Fraction(4, 100),    # 4%
}
_MIN_AMOUNT = 10000   # 100 บาท (ต่ำกว่านี้ไม่ได้เงินคืน; พอดี 100 บาทได้)
_CAP = 20000          # 200 บาทต่อบิล (ใช้หลังคูณ 2 เท่า)


def cashback(amount, tier, birthday):
    if amount < _MIN_AMOUNT:
        return 0
    value = Fraction(amount) * _RATES[tier]
    if birthday:
        value *= 2
    value = min(value, Fraction(_CAP))
    return -((-value.numerator) // value.denominator)  # ceil
