import json
import math
import sys
from fractions import Fraction


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์"""
    if type(weight_g) is not int or not (1 <= weight_g <= 30000):
        raise ValueError("weight_g must be an int in 1..30000")
    if type(distance_km) not in (int, float):
        raise ValueError("distance_km must be a number")
    if isinstance(distance_km, float) and not math.isfinite(distance_km):
        raise ValueError("distance_km must be finite")
    if distance_km < 0:
        raise ValueError("distance_km must be >= 0")
    if type(express) is not bool:
        raise ValueError("express must be a bool")
    if express and weight_g > 20000:
        raise ValueError("express supports at most 20000 g")

    if distance_km == 0:  # รับเองที่ร้าน
        return 0

    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + Fraction(3, 2) * (weight_g - 5000)  # 1.5 สตางค์/กรัม

    if Fraction(distance_km) > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    return int((fee * 2 + 1) // 2)  # half-up


def main():
    d = json.load(sys.stdin)
    print(shipping_fee(d["weight_g"], d["distance_km"], d["express"]))


if __name__ == "__main__":
    main()
