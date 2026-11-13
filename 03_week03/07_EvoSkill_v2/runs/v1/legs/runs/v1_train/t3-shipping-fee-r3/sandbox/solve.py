from fractions import Fraction


def half_up(x):
    return int((Fraction(x) * 2 + 1) // 2)


def _need_int(v, name, low, high=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if v < low or (high is not None and v > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return v


def shipping_fee(weight_g, distance_km, express):
    _need_int(weight_g, "weight_g", 1, 30000)
    _need_int(distance_km, "distance_km", 0)
    if type(express) is not bool:
        raise ValueError("express ต้องเป็น True หรือ False")
    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + Fraction((weight_g - 5000) * 1500, 1000)
    if distance_km > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)
    return half_up(fee)
