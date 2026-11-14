from fractions import Fraction


def _volume_discount(qty: int) -> Fraction:
    """ส่วนลดตามปริมาณ (ใช้อัตราเดียว): >=50 ถุง 7.5%, >=10 ถุง 3.5%, อื่น ๆ 0%"""
    if qty >= 50:
        return Fraction(75, 1000)
    if qty >= 10:
        return Fraction(35, 1000)
    return Fraction(0)


def bulk_price(unit_price, qty, coupon):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นจำนวนเต็มสตางค์

    unit_price : ราคาต่อถุง (สตางค์, ตั้งแต่ 0)
    qty        : จำนวนถุง (1–1000)
    coupon     : True = มีคูปองลดอีก 2.5%

    ลำดับการคิด:
      1) ยอดตั้งต้น = unit_price × qty
      2) ลดตามปริมาณ (อัตราเดียว) 3.5% หรือ 7.5%
      3) ถ้ามีคูปอง ลดอีก 2.5% บนยอดหลังข้อ 2 (ต่อเนื่อง)
      4) บวก VAT 7% เป็นขั้นสุดท้าย
      5) ปัดครั้งเดียวเป็นจำนวนเต็มสตางค์ ด้วยโหมดปัดครึ่งเข้าเลขคู่ (round-half-even)
    """
    if unit_price < 0:
        raise ValueError("unit_price ต้องตั้งแต่ 0 สตางค์ขึ้นไป")
    if not 1 <= qty <= 1000:
        raise ValueError("qty ต้องอยู่ในช่วง 1–1000 ถุง")

    total = Fraction(unit_price) * qty                     # 1) ยอดตั้งต้น (สตางค์)
    total *= 1 - _volume_discount(qty)                     # 2) ลดตามปริมาณ
    if coupon:
        total *= 1 - Fraction(25, 1000)                    # 3) คูปองลดอีก 2.5%
    total *= 1 + Fraction(7, 100)                          # 4) VAT 7% ขั้นสุดท้าย
    return round(total)                                    # 5) ปัดครั้งเดียว (ครึ่งเข้าเลขคู่)


if __name__ == "__main__":
    print(bulk_price(10000, 10, False))   # ตัวอย่าง: 100 บาท × 10 ถุง ไม่มีคูปอง
    print(bulk_price(10000, 50, True))    # ตัวอย่าง: 100 บาท × 50 ถุง มีคูปอง
