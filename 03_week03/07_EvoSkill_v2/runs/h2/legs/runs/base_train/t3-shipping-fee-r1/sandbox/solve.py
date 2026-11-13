"""BaanKafe shipping fee calculator.

shipping_fee(weight_g, distance_km, express) -> int (satang)

Rules:
- Base fee by weight (grams):
    weight <= 1,000            -> 40 baht
    1,000 < weight <= 5,000    -> 80 baht
    weight > 5,000             -> 80 baht + 15 baht per kg of the excess over 5,000 g
                                  (prorated by grams)
- Distance over 100 km        -> +20% (multiply by 1.20)
- Express                     -> +50% (multiply by 1.50), applied after the distance surcharge
- Result is returned as an integer number of satang (1 baht = 100 satang),
  rounded half-up to the nearest satang.
"""

from decimal import Decimal, ROUND_HALF_UP

MIN_WEIGHT_G = 1
MAX_WEIGHT_G = 30_000


def _to_decimal(value) -> Decimal:
    # Going through str() avoids binary float artifacts such as 0.1 -> 0.1000000000000000055...
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def shipping_fee(weight_g, distance_km, express: bool = False) -> int:
    weight = _to_decimal(weight_g)
    distance = _to_decimal(distance_km)

    if not (MIN_WEIGHT_G <= weight <= MAX_WEIGHT_G):
        raise ValueError(f"weight_g must be between {MIN_WEIGHT_G} and {MAX_WEIGHT_G}, got {weight_g}")
    if distance < 0:
        raise ValueError(f"distance_km must be >= 0, got {distance_km}")

    # Base fee in baht
    if weight <= 1000:
        fee = Decimal(40)
    elif weight <= 5000:
        fee = Decimal(80)
    else:
        fee = Decimal(80) + (weight - 5000) * Decimal("15") / Decimal(1000)

    # Long-distance surcharge: strictly more than 100 km
    if distance > 100:
        fee *= Decimal("1.2")

    # Express surcharge, applied on top of the distance surcharge
    if express:
        fee *= Decimal("1.5")

    # Convert baht to satang and round half-up to an integer
    satang = (fee * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(satang)


if __name__ == "__main__":
    # Quick sanity checks
    assert shipping_fee(500, 10, False) == 4000          # 40 baht
    assert shipping_fee(1000, 10, False) == 4000         # boundary: <= 1000 -> 40
    assert shipping_fee(1001, 10, False) == 8000         # 80 baht
    assert shipping_fee(5000, 100, False) == 8000        # 100 km is not over 100
    assert shipping_fee(5000, 100.5, False) == 9600      # 80 * 1.2 = 96 baht
    assert shipping_fee(6000, 10, False) == 9500         # 80 + 15 = 95 baht
    assert shipping_fee(5500, 10, False) == 8750         # 80 + 7.5 = 87.5 baht
    assert shipping_fee(1000, 10, True) == 6000          # 40 * 1.5 = 60 baht
    # 30,000 g: 80 + 25000/1000*15 = 455 baht; *1.2 = 546; *1.5 = 819 baht
    assert shipping_fee(30000, 150, True) == 81900
    print("all checks passed")
