"""คิดค่าส่งเมล็ดกาแฟของร้าน BaanKafe

หน่วยการคำนวณทั้งหมดเป็นสตางค์ (1 บาท = 100 สตางค์) ใช้ Fraction เพื่อไม่ให้เกิดความคลาดเคลื่อนของทศนิยมแบบ float
"""

from fractions import Fraction

MIN_WEIGHT_G = 1
MAX_WEIGHT_G = 30_000
LIGHT_LIMIT_G = 1_000
MID_LIMIT_G = 5_000
LONG_DISTANCE_KM = 100

FEE_LIGHT_SATANG = 4_000   # 40 บาท
FEE_MID_SATANG = 8_000     # 80 บาท
EXTRA_PER_KG_SATANG = 1_500  # 15 บาท ต่อกิโลกรัม (ส่วนที่เกิน 5,000 กรัม)


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์

    weight_g    : น้ำหนักเป็นกรัม (1–30,000)
    distance_km : ระยะทางเป็นกิโลเมตร (ตั้งแต่ 0)
    express     : True = ส่งด่วน (คิดเพิ่ม 50%)

    ขั้นตอน:
      1. ค่าส่งตามน้ำหนัก
         - ไม่เกิน 1,000 กรัม  -> 40 บาท
         - ไม่เกิน 5,000 กรัม  -> 80 บาท
         - เกิน 5,000 กรัม     -> 80 บาท + 15 บาท/กก. ของส่วนที่เกิน (คิดตามสัดส่วนกรัม)
      2. ระยะทางเกิน 100 กม. คิดเพิ่ม 20%
      3. ส่งด่วนคิดเพิ่ม 50% (คูณต่อจากข้อ 2)
      4. ปัดเศษเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้น)

    ตัวอย่าง:
      shipping_fee(2000, 50, False)    -> 8000   (80 บาท)
      shipping_fee(6000, 150, True)    -> 17100  (171 บาท)
    """
    weight = Fraction(str(weight_g))
    distance = Fraction(str(distance_km))

    if not (MIN_WEIGHT_G <= weight <= MAX_WEIGHT_G):
        raise ValueError(f"weight_g ต้องอยู่ในช่วง {MIN_WEIGHT_G}–{MAX_WEIGHT_G} กรัม")
    if distance < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")

    if weight <= LIGHT_LIMIT_G:
        fee = Fraction(FEE_LIGHT_SATANG)
    elif weight <= MID_LIMIT_G:
        fee = Fraction(FEE_MID_SATANG)
    else:
        extra_g = weight - MID_LIMIT_G
        fee = FEE_MID_SATANG + Fraction(EXTRA_PER_KG_SATANG) * extra_g / 1_000

    if distance > LONG_DISTANCE_KM:
        fee *= Fraction(6, 5)  # +20%

    if express:
        fee *= Fraction(3, 2)  # +50%

    # fee >= 0 เสมอ จึงปัดครึ่งขึ้นได้ด้วย floor(x + 1/2)
    return int(fee + Fraction(1, 2))
