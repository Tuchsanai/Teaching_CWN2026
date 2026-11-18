import json
import math
import sys
from fractions import Fraction


def shipping_fee(weight_g, distance_km, express):
    if type(weight_g) is not int or not (1 <= weight_g <= 30000):
        raise ValueError("weight_g must be int in 1..30000")
    if type(distance_km) not in (int, float) or not math.isfinite(distance_km) or distance_km < 0:
        raise ValueError("distance_km must be a number >= 0")
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
        fee = 8000 + Fraction(3, 2) * (weight_g - 5000)  # 1.5 satang per gram
    if Fraction(distance_km) > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    return int((fee * 2 + 1) // 2)


def main():
    a = json.load(sys.stdin)
    print(shipping_fee(a["weight_g"], a["distance_km"], a["express"]))


if __name__ == "__main__":
    main()
