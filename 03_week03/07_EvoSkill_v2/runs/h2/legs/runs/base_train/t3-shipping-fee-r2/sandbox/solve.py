"""ค่าส่งเมล็ดกาแฟ BaanKafe

คำนวณทั้งหมดด้วย Decimal ในหน่วยสตางค์ เพื่อไม่ให้เกิดความคลาดเคลื่อนจากเลขทศนิยมของ float
ผลลัพธ์เป็นจำนวนเต็มสตางค์ (ปัดเศษแบบ ROUND_HALF_UP เมื่อมีเศษสตางค์)
"""

from decimal import Decimal, ROUND_HALF_UP

MIN_WEIGHT_G = 1
MAX_WEIGHT_G = 30_000

# หน่วยเป็นสตางค์ (1 บาท = 100 สตางค์)
FEE_UP_TO_1KG = 40 * 100
FEE_UP_TO_5KG = 80 * 100
# ส่วนที่เกิน 5,000 กรัม คิดกิโลกรัมละ 15 บาท => 15 * 100 / 1000 = 1.5 สตางค์ต่อกรัม
EXCESS_PER_GRAM = Decimal("1.5")

FAR_THRESHOLD_KM = 100
FAR_MULTIPLIER = Decimal("1.2")      # ระยะทางเกิน 100 กม. เพิ่ม 20%
EXPRESS_MULTIPLIER = Decimal("1.5")  # ส่งด่วนเพิ่ม 50% (คูณต่อจากข้อก่อน)


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์

    weight_g    : น้ำหนักเป็นกรัม 1–30,000
    distance_km : ระยะทางเป็นกิโลเมตร (ตั้งแต่ 0)
    express     : True = ส่งด่วน
    """
    weight = Decimal(str(weight_g))
    distance = Decimal(str(distance_km))

    if not (MIN_WEIGHT_G <= weight <= MAX_WEIGHT_G):
        raise ValueError(f"weight_g must be between {MIN_WEIGHT_G} and {MAX_WEIGHT_G}, got {weight_g}")
    if distance < 0:
        raise ValueError(f"distance_km must be >= 0, got {distance_km}")

    # ค่าส่งฐานตามน้ำหนัก (สตางค์)
    if weight <= 1000:
        fee = Decimal(FEE_UP_TO_1KG)
    elif weight <= 5000:
        fee = Decimal(FEE_UP_TO_5KG)
    else:
        fee = Decimal(FEE_UP_TO_5KG) + (weight - 5000) * EXCESS_PER_GRAM

    # ระยะทางเกิน 100 กม. (ไม่รวม 100 เอง)
    if distance > FAR_THRESHOLD_KM:
        fee *= FAR_MULTIPLIER

    # ส่งด่วน คูณต่อจากข้อก่อนหน้า
    if express:
        fee *= EXPRESS_MULTIPLIER

    return int(fee.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


if __name__ == "__main__":
    cases = [
        # (weight_g, distance_km, express, expected_satang)
        (500, 10, False, 4000),        # 40 บาท
        (1000, 10, False, 4000),       # ขอบ 1 กก. ยังอยู่ในขั้น 40 บาท
        (1001, 10, False, 8000),       # 80 บาท
        (5000, 10, False, 8000),       # ขอบ 5 กก. ยังอยู่ 80 บาท
        (6000, 10, False, 9500),       # 80 + 1000g*1.5 สตางค์ = 95 บาท
        (30000, 150, True, 81900),     # ((80 + 375) * 1.2) * 1.5 = 819 บาท
        (2000, 100, False, 8000),      # 100 กม. พอดี ไม่คิดเพิ่ม
        (2000, 100.5, False, 9600),    # เกิน 100 กม. => 80 * 1.2 = 96 บาท
        (2000, 50, True, 12000),       # ส่งด่วน 80 * 1.5 = 120 บาท
        (1, 0, False, 4000),
    ]
    ok = True
    for w, d, e, expected in cases:
        got = shipping_fee(w, d, e)
        status = "OK " if got == expected else "FAIL"
        if got != expected:
            ok = False
        print(f"{status} weight={w:>6} dist={d:>6} express={str(e):<5} -> {got} (expected {expected})")
    print("ALL PASSED" if ok else "SOME TESTS FAILED")
