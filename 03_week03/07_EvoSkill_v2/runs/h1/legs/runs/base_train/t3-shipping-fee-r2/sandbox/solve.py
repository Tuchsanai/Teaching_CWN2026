"""ฟังก์ชันคิดค่าส่งเมล็ดกาแฟ ของร้าน BaanKafe."""

from decimal import Decimal, ROUND_HALF_UP


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่ง (บาท) เป็นจำนวนเต็มสตางค์

    weight_g    : น้ำหนักเป็นกรัม (1–30,000)
    distance_km : ระยะทางเป็นกิโลเมตร (ตั้งแต่ 0)
    express     : True = ส่งด่วน
    """
    if not 1 <= weight_g <= 30_000:
        raise ValueError("weight_g ต้องอยู่ระหว่าง 1–30,000 กรัม")
    if distance_km < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")

    weight = Decimal(str(weight_g))
    distance = Decimal(str(distance_km))

    # 1) ค่าส่งตามน้ำหนัก (หน่วยบาท)
    if weight <= 1000:
        fee = Decimal(40)
    elif weight <= 5000:
        fee = Decimal(80)
    else:
        # เกิน 5,000 กรัม: 80 บาท + กิโลกรัมละ 15 บาท ตามสัดส่วนของกรัมที่เกิน
        fee = Decimal(80) + (weight - 5000) / Decimal(1000) * Decimal(15)

    # 2) ระยะทางเกิน 100 กม. เพิ่ม 20%
    if distance > 100:
        fee *= Decimal("1.2")

    # 3) ส่งด่วนเพิ่ม 50% (คูณต่อจากข้อก่อนหน้า)
    if express:
        fee *= Decimal("1.5")

    # แปลงเป็นสตางค์ และปัดเศษแบบครึ่งขึ้น
    satang = (fee * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(satang)
