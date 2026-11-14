from fractions import Fraction


def _half_up(x):
    x = Fraction(x)
    return (x.numerator * 2 + x.denominator) // (x.denominator * 2)


def _is_int(v):
    return type(v) is int


def shipping_fee(weight_g, distance_km, express):
    if not _is_int(weight_g) or not 1 <= weight_g <= 30000:
        raise ValueError("weight_g must be int 1-30000")
    if not _is_int(distance_km) or distance_km < 0:
        raise ValueError("distance_km must be int >= 0")
    if type(express) is not bool:
        raise ValueError("express must be bool")
    if express and weight_g > 20000:
        raise ValueError("express supports at most 20000 g")
    if distance_km == 0:
        return 0  # customer pickup

    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + Fraction(3, 2) * (weight_g - 5000)
    if distance_km > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    return _half_up(fee)
