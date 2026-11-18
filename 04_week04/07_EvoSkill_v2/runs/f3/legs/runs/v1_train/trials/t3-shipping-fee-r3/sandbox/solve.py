from fractions import Fraction


def _is_int(v):
    return type(v) is int


def shipping_fee(weight_g, distance_km, express):
    """ค่าส่งเป็นสตางค์ (int). ตรวจ input ครบก่อนคำนวณ.
    นโยบายเสริม (baankafe-known-policies):
      S1: distance_km == 0 -> รับเองที่ร้าน ค่าส่ง 0
      S2: express และ weight_g > 20000 -> ValueError
    """
    if not _is_int(weight_g) or not 1 <= weight_g <= 30000:
        raise ValueError("weight_g must be int in 1..30000")
    if not _is_int(distance_km) or distance_km < 0:
        raise ValueError("distance_km must be int >= 0")
    if type(express) is not bool:
        raise ValueError("express must be bool")
    if express and weight_g > 20000:
        raise ValueError("express supports at most 20000 g")
    if distance_km == 0:
        return 0

    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        fee = 8000 + Fraction((weight_g - 5000) * 1500, 1000)
    if distance_km > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)
    return int((fee * 2 + 1) // 2)  # half-up


if __name__ == "__main__":
    print(shipping_fee(500, 20, False), shipping_fee(3000, 150, False),
          shipping_fee(5106, 150, True), shipping_fee(5217, 50, True))
