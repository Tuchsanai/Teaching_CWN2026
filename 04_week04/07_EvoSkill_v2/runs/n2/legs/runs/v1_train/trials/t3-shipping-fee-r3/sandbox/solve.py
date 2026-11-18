from fractions import Fraction


def shipping_fee(weight_g, distance_km, express):
    # Input validation (bool is rejected for ints)
    if type(weight_g) is not int or not 1 <= weight_g <= 30000:
        raise ValueError("weight_g must be int 1-30000")
    if type(distance_km) is not int or distance_km < 0:
        raise ValueError("distance_km must be int >= 0")
    if type(express) is not bool:
        raise ValueError("express must be bool")
    # Assumption (house rules): express accepts at most 20,000 g
    if express and weight_g > 20000:
        raise ValueError("express supports at most 20000 g")
    # Assumption (house rules): distance 0 = pickup at the shop -> free
    if distance_km == 0:
        return 0
    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        fee = 8000 + Fraction(1500 * (weight_g - 5000), 1000)
    if distance_km > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)
    return int((fee * 2 + 1) // 2)  # half-up, once at the end
