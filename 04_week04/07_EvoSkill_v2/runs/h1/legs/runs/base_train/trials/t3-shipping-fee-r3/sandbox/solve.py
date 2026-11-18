"""ค่าส่งเมล็ดกาแฟ BaanKafe

shipping_fee(weight_g, distance_km, express) -> int (หน่วยเป็นสตางค์)

กติกา
- ฐานตามน้ำหนัก
  - ไม่เกิน 1,000 กรัม  : 40 บาท
  - ไม่เกิน 5,000 กรัม  : 80 บาท
  - เกิน 5,000 กรัม     : 80 บาท + (กรัมที่เกิน 5,000 × 15 บาท/1,000 กรัม) คิดตามสัดส่วนกรัม
- ระยะทางเกิน 100 กม. คิดเพิ่ม 20% (คูณ 1.2)
- ส่งด่วน คิดเพิ่ม 50% (คูณ 1.5) คูณต่อจากข้อระยะทาง
- ผลลัพธ์เป็นจำนวนเต็มสตางค์ ปัดเศษแบบ half-up (0.5 ปัดขึ้น)

คำนวณด้วย Fraction ทั้งหมด เพื่อไม่ให้เกิดความคลาดเคลื่อนจาก float
"""

from fractions import Fraction
import math

MAX_WEIGHT_G = 30_000
LONG_DISTANCE_KM = 100
SATANG_PER_BAHT = 100


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์

    weight_g    : น้ำหนัก 1–30,000 กรัม
    distance_km : ระยะทาง (กม.) ตั้งแต่ 0 ขึ้นไป
    express     : True = ส่งด่วน
    """
    w = Fraction(weight_g)
    d = Fraction(distance_km)

    if not (1 <= w <= MAX_WEIGHT_G):
        raise ValueError(f"weight_g ต้องอยู่ระหว่าง 1–{MAX_WEIGHT_G} กรัม: {weight_g}")
    if d < 0:
        raise ValueError(f"distance_km ต้องไม่ติดลบ: {distance_km}")

    # 1) ค่าฐานตามน้ำหนัก (บาท)
    if w <= 1000:
        base_baht = Fraction(40)
    elif w <= 5000:
        base_baht = Fraction(80)
    else:
        base_baht = Fraction(80) + (w - 5000) * Fraction(15, 1000)

    fee = base_baht * SATANG_PER_BAHT  # แปลงเป็นสตางค์

    # 2) ระยะทางเกิน 100 กม. เพิ่ม 20%
    if d > LONG_DISTANCE_KM:
        fee *= Fraction(6, 5)

    # 3) ส่งด่วนเพิ่ม 50% (คูณต่อจากข้อก่อนหน้า)
    if express:
        fee *= Fraction(3, 2)

    # 4) ปัดเป็นจำนวนเต็มสตางค์ แบบ half-up
    return math.floor(fee + Fraction(1, 2))


if __name__ == "__main__":
    cases = [
        # (weight_g, distance_km, express, expected_satang)
        (1, 0, False, 4000),          # 40 บาท
        (1000, 10, False, 4000),      # ขอบ 1,000 กรัม
        (1001, 10, False, 8000),      # 80 บาท
        (5000, 10, False, 8000),      # ขอบ 5,000 กรัม
        (5001, 10, False, 8002),      # 80.015 บาท -> 8001.5 สต. -> 8002
        (6000, 50, False, 9500),      # 80 + 15 = 95 บาท
        (6000, 150, False, 11400),    # 95 * 1.2 = 114 บาท
        (6000, 50, True, 14250),      # 95 * 1.5 = 142.5 บาท
        (6000, 150, True, 17100),     # 95 * 1.2 * 1.5 = 171 บาท
        (30000, 100, False, 45500),   # 80 + 25,000 * 0.015 = 455 บาท
    ]

    ok = True
    for w, d, e, expected in cases:
        got = shipping_fee(w, d, e)
        status = "OK " if got == expected else "NG "
        if got != expected:
            ok = False
        print(f"{status}weight={w:>6} g dist={d:>5} km express={str(e):<5} -> {got} สต. (expected {expected})")

    for bad in [(0, 10, False), (30001, 10, False), (100, -1, False)]:
        try:
            shipping_fee(*bad)
            ok = False
            print("NG  ไม่โยน ValueError:", bad)
        except ValueError:
            print("OK  ValueError:", bad)

    print("ALL PASSED" if ok else "SOME FAILED")
