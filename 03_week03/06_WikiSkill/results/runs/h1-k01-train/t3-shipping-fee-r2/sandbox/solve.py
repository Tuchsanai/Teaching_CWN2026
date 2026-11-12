"""ค่าส่งเมล็ดกาแฟ BaanKafe

คืนค่าเป็นจำนวนเต็มสตางค์ (1 บาท = 100 สตางค์)
ใช้เลขเศษส่วน (Fraction) ระหว่างคำนวณ เพื่อไม่ให้เกิดความคลาดเคลื่อนจากทศนิยม
และปัดเศษครึ่งขึ้นเป็นสตางค์ตอนท้าย
"""

from fractions import Fraction

# ค่าคงที่ (หน่วย: สตางค์)
_BASE_LIGHT = 40 * 100       # ไม่เกิน 1,000 กรัม = 40 บาท
_BASE_MEDIUM = 80 * 100      # ไม่เกิน 5,000 กรัม = 80 บาท
_HEAVY_THRESHOLD_G = 5_000   # เกิน 5,000 กรัม คิดส่วนเกินเพิ่ม
_EXTRA_PER_KG = 15 * 100     # ส่วนเกิน 5,000 กรัม กิโลกรัมละ 15 บาท
_MIN_WEIGHT_G = 1
_MAX_WEIGHT_G = 30_000
_FAR_KM = 100                # เกิน 100 กม. คิดเพิ่ม 20%
_FAR_MULTIPLIER = Fraction(6, 5)
_EXPRESS_MULTIPLIER = Fraction(3, 2)  # ส่งด่วน คิดเพิ่ม 50%


def shipping_fee(weight_g, distance_km, express):
    """คำนวณค่าส่งเมล็ดกาแฟ และคืนค่าเป็นจำนวนเต็มสตางค์

    weight_g: น้ำหนักเป็นกรัม (1–30,000)
    distance_km: ระยะทางเป็นกิโลเมตร (ตั้งแต่ 0)
    express: True = ส่งด่วน
    """
    if isinstance(weight_g, bool) or not isinstance(weight_g, (int, float)):
        raise TypeError("weight_g ต้องเป็นตัวเลข")
    if not (_MIN_WEIGHT_G <= weight_g <= _MAX_WEIGHT_G):
        raise ValueError("weight_g ต้องอยู่ระหว่าง 1 ถึง 30,000 กรัม")
    if isinstance(distance_km, bool) or not isinstance(distance_km, (int, float)):
        raise TypeError("distance_km ต้องเป็นตัวเลข")
    if distance_km < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")

    weight = Fraction(weight_g)
    distance = Fraction(distance_km)

    # 1) ค่าส่งตามน้ำหนัก
    if weight <= 1_000:
        fee = Fraction(_BASE_LIGHT)
    elif weight <= _HEAVY_THRESHOLD_G:
        fee = Fraction(_BASE_MEDIUM)
    else:
        # เกิน 5,000 กรัม: ค่าฐาน 80 บาท + ส่วนเกินตามสัดส่วนกรัม
        excess_g = weight - _HEAVY_THRESHOLD_G
        fee = _BASE_MEDIUM + excess_g * _EXTRA_PER_KG / 1000

    # 2) ระยะทางเกิน 100 กม. คิดเพิ่ม 20%
    if distance > _FAR_KM:
        fee *= _FAR_MULTIPLIER

    # 3) ส่งด่วน คิดเพิ่ม 50% (คูณต่อจากข้อก่อน)
    if express:
        fee *= _EXPRESS_MULTIPLIER

    # ปัดครึ่งขึ้นเป็นสตางค์ (ค่าไม่ติดลบ จึงใช้ floor(x + 1/2) ได้)
    return int(fee + Fraction(1, 2))
