from fractions import Fraction


def _round_half_up(x):
    x = Fraction(x)
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def _num(name, v):
    if isinstance(v, bool) or not isinstance(v, (int, float, Fraction)):
        raise ValueError(f"{name} must be a number, got {v!r}")
    if isinstance(v, float) and (v != v or v in (float("inf"), float("-inf"))):
        raise ValueError(f"{name} must be finite")
    return Fraction(str(v)) if isinstance(v, float) else Fraction(v)


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์"""
    w = _num("weight_g", weight_g)
    d = _num("distance_km", distance_km)
    if not isinstance(express, bool):
        raise ValueError("express must be a bool")
    if w < 1 or w > 30000:
        raise ValueError("weight_g must be in 1..30000")
    if d < 0:
        raise ValueError("distance_km must be >= 0")

    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        fee = 8000 + (w - 5000) * Fraction(3, 2)  # 15 บาท/กก. = 1.5 สตางค์/กรัม
    if d > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    return _round_half_up(fee)
