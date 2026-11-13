# rounding policy r1 (half-up, rounded once at the end)


def bulk_price(unit_price, qty, coupon):
    if type(unit_price) is not int or type(qty) is not int or type(coupon) is not bool:
        raise ValueError("invalid input type")
    if unit_price < 0 or not (1 <= qty <= 1000):
        raise ValueError("input out of range")

    num = unit_price * qty
    den = 1
    if qty >= 50:
        num *= 925
        den *= 1000
    elif qty >= 10:
        num *= 965
        den *= 1000
    if coupon:
        num *= 975
        den *= 1000
    num *= 107
    den *= 100
    return (2 * num + den) // (2 * den)
