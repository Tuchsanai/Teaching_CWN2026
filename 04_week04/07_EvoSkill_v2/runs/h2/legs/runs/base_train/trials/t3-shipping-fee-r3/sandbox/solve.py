"""คำนวณค่าส่งเมล็ดกาแฟของร้าน BaanKafe"""

from decimal import Decimal, ROUND_HALF_UP


def shipping_fee(weight_g, distance_km, express=False):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์

    weight_g    : น้ำหนักเป็นกรัม (1–30,000)
    distance_km : ระยะทางเป็นกิโลเมตร (ตั้งแต่ 0)
    express     : True = ส่งด่วน (คิดเพิ่ม 50%)
    """
    weight = Decimal(str(weight_g))
    distance = Decimal(str(distance_km))

    if not (1 <= weight <= 30000):
        raise ValueError("weight_g ต้องอยู่ในช่วง 1–30,000 กรัม")
    if distance < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")

    # ค่าส่งตามน้ำหนัก (บาท)
    if weight <= 1000:
        fee = Decimal(40)
    elif weight <= 5000:
        fee = Decimal(80)
    else:
        # เกิน 5,000 กรัม: 80 บาท + กิโลกรัมละ 15 บาท ตามสัดส่วนของส่วนที่เกิน
        fee = Decimal(80) + (weight - 5000) * Decimal(15) / Decimal(1000)

    # ระยะทางเกิน 100 กม. เพิ่ม 20%
    if distance > 100:
        fee *= Decimal("1.2")

    # ส่งด่วนเพิ่ม 50% (คูณต่อจากข้อก่อนหน้า)
    if express:
        fee *= Decimal("1.5")

    # แปลงเป็นสตางค์ แล้วปัดเศษครึ่งขึ้นให้เป็นจำนวนเต็ม
    satang = (fee * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(satang)
