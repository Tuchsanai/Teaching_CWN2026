"""BaanKafe shipping fee calculator.

shipping_fee(weight_g, distance_km, express) -> int (satang)

Rules (all money in satang, 1 baht = 100 satang):
  1. Weight tier
       weight_g <= 1000          -> 40 baht  (4000 satang)
       1000 < weight_g <= 5000   -> 80 baht  (8000 satang)
       weight_g > 5000           -> 80 baht + 15 baht per kg of excess,
                                    prorated per gram (1.5 satang per gram)
  2. distance_km > 100          -> x 1.2 (applied after step 1)
  3. express is True            -> x 1.5 (applied after step 2)
  4. Round half-up to an integer number of satang, once, at the end.
"""

import json
import sys
from fractions import Fraction

WEIGHT_MIN_G = 1
WEIGHT_MAX_G = 30000

BASE_FEE_LIGHT = 4000        # 40 baht
BASE_FEE_MEDIUM = 8000       # 80 baht
MEDIUM_LIMIT_G = 5000
EXCESS_PER_GRAM = Fraction(3, 2)   # 15 baht/kg = 1500 satang / 1000 g = 1.5 satang/g

LONG_DISTANCE_KM = 100
LONG_DISTANCE_MULT = Fraction(6, 5)   # +20%
EXPRESS_MULT = Fraction(3, 2)         # +50%


def _require_int(value, label, lo=None, hi=None):
    if type(value) is not int:
        raise ValueError(f"{label} ต้องเป็นจำนวนเต็ม")
    if lo is not None and value < lo:
        raise ValueError(f"{label} ต้องไม่น้อยกว่า {lo}")
    if hi is not None and value > hi:
        raise ValueError(f"{label} ต้องไม่เกิน {hi}")
    return value


def _require_bool(value, label):
    if type(value) is not bool:
        raise ValueError(f"{label} ต้องเป็น True หรือ False")
    return value


def _half_up(x):
    """Round a non-negative Fraction/int to the nearest int, halves go up."""
    return int((Fraction(x) * 2 + 1) // 2)


def shipping_fee(weight_g, distance_km, express):
    weight_g = _require_int(weight_g, "weight_g", WEIGHT_MIN_G, WEIGHT_MAX_G)
    distance_km = _require_int(distance_km, "distance_km", 0)
    express = _require_bool(express, "express")

    # 1. weight tier (exact, no rounding yet)
    if weight_g <= 1000:
        fee = Fraction(BASE_FEE_LIGHT)
    elif weight_g <= MEDIUM_LIMIT_G:
        fee = Fraction(BASE_FEE_MEDIUM)
    else:
        fee = BASE_FEE_MEDIUM + EXCESS_PER_GRAM * (weight_g - MEDIUM_LIMIT_G)

    # 2. long distance surcharge (strictly more than 100 km)
    if distance_km > LONG_DISTANCE_KM:
        fee *= LONG_DISTANCE_MULT

    # 3. express surcharge, multiplied on top of the previous step
    if express:
        fee *= EXPRESS_MULT

    # 4. single rounding at the end
    return _half_up(fee)


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = shipping_fee(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
