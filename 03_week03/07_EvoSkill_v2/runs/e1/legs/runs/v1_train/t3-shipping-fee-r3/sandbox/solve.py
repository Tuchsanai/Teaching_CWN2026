from fractions import Fraction


def _half_up(x):
    return int((Fraction(x) * 2 + 1) // 2)


def shipping_fee(weight_g, distance_km, express):
    if type(weight_g) is not int or not (1 <= weight_g <= 30000):
        raise ValueError("weight_g ต้องเป็นจำนวนเต็ม 1-30000")
    if type(distance_km) is not int or distance_km < 0:
        raise ValueError("distance_km ต้องเป็นจำนวนเต็ม >= 0")
    if type(express) is not bool:
        raise ValueError("express ต้องเป็น True/False")

    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + Fraction((weight_g - 5000) * 1500, 1000)
    if distance_km > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(3, 2)
    return _half_up(fee)
