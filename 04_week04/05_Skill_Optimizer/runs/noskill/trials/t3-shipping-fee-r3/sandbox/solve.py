from fractions import Fraction
from decimal import Decimal, ROUND_HALF_UP


def shipping_fee(weight_g, distance_km, express):
    """Return shipping fee as integer satang."""
    w = Fraction(Decimal(str(weight_g)))
    d = Fraction(Decimal(str(distance_km)))
    if w < 1 or w > 30000:
        raise ValueError("weight_g must be between 1 and 30000")
    if d < 0:
        raise ValueError("distance_km must be >= 0")

    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        fee = 8000 + (w - 5000) * Fraction(1500, 1000)  # 15 baht/kg in satang
    if d > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    return int((Decimal(fee.numerator) / Decimal(fee.denominator))
               .quantize(Decimal(1), rounding=ROUND_HALF_UP))
