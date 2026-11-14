from fractions import Fraction


def shipping_fee(weight_g, distance_km, express):
    """Return shipping fee in integer satang (1 baht = 100 satang)."""
    if isinstance(weight_g, bool) or not 1 <= weight_g <= 30000:
        raise ValueError("weight_g must be between 1 and 30000")
    if isinstance(distance_km, bool) or distance_km < 0:
        raise ValueError("distance_km must be >= 0")

    w = Fraction(weight_g)
    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        # 15 baht/kg = 1500 satang per 1000 g, proportional to grams
        fee = Fraction(8000) + (w - 5000) * Fraction(1500, 1000)

    if distance_km > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)

    # exact arithmetic, round half up to whole satang
    return int((fee * 2 + 1) // 2)
