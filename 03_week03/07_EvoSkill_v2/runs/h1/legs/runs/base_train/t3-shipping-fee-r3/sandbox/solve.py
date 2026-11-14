"""BaanKafe shipping fee calculator.

shipping_fee(weight_g, distance_km, express) -> int (satang)

Rules (all amounts in baht, computed exactly with Fraction, then rounded
half-up to whole satang):
  1. Base by weight:
       weight <= 1,000 g   -> 40 baht
       weight <= 5,000 g   -> 80 baht
       weight  > 5,000 g   -> 80 baht + 15 baht per kg above 5,000 g
                              (pro-rated by grams)
  2. distance > 100 km    -> +20% (multiply by 1.2)
  3. express = True       -> +50% (multiply by 1.5), applied after rule 2
"""

from fractions import Fraction

MAX_WEIGHT_G = 30_000


def shipping_fee(weight_g, distance_km, express):
    if isinstance(weight_g, bool) or not isinstance(weight_g, (int, float, Fraction)):
        raise TypeError("weight_g must be a number")
    if not (1 <= weight_g <= MAX_WEIGHT_G):
        raise ValueError("weight_g must be between 1 and 30,000 grams")
    if distance_km < 0:
        raise ValueError("distance_km must be >= 0")

    weight = Fraction(weight_g)
    distance = Fraction(distance_km)

    # 1) Base fee by weight (baht, exact)
    if weight <= 1000:
        fee = Fraction(40)
    elif weight <= 5000:
        fee = Fraction(80)
    else:
        fee = Fraction(80) + (weight - 5000) * Fraction(15, 1000)

    # 2) Long-distance surcharge: +20% when distance exceeds 100 km
    if distance > 100:
        fee *= Fraction(120, 100)

    # 3) Express surcharge: +50%, applied on top of the previous step
    if express:
        fee *= Fraction(150, 100)

    # Convert to satang and round half-up to an integer
    satang = fee * 100
    return int(satang + Fraction(1, 2))  # floor(x + 0.5), x >= 0
