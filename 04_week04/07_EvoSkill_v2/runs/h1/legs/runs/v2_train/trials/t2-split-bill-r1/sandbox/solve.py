"""BaanKafe: หารบิลพร้อมทิป (หน่วยเป็นสตางค์ ทั้งหมดเป็นจำนวนเต็ม)"""


def _require_int(value, name, low=None, high=None):
    # ปฏิเสธ bool, float, str, None (ห้ามแปลงค่าเงียบ ๆ)
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    if high is not None and value > high:
        raise ValueError(f"{name} ต้องไม่เกิน {high}")
    return value


def split_bill(total, people, tip_percent):
    """คืน list ของยอดที่แต่ละคนจ่าย (สตางค์ ตามลำดับคน)

    - total: ยอดบิลเป็นสตางค์ (>= 0)
    - people: จำนวนคน (>= 1)
    - tip_percent: ทิปเป็นเปอร์เซ็นต์ จำนวนเต็ม 0-100

    ทิปเป็นเงินที่ลูกค้าจ่ายให้ร้าน จึงปัดครึ่งขึ้น (half-up) ครั้งเดียวตอนท้าย
    ส่วนเศษจากการหารไม่ลงตัว คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์
    """
    _require_int(total, "total", low=0)
    _require_int(people, "people", low=1)
    _require_int(tip_percent, "tip_percent", low=0, high=100)

    # ยอดที่ต้องหาร = total + total * tip% ปัดครึ่งขึ้นครั้งเดียว
    # (total * (100 + tip) / 100) + 0.5 แล้ว floor ด้วยจำนวนเต็มล้วน
    grand = (total * (100 + tip_percent) + 50) // 100

    base, remainder = divmod(grand, people)
    return [base + 1 if i < remainder else base for i in range(people)]


if __name__ == "__main__":
    print(split_bill(10000, 3, 10))  # ตัวอย่าง: 100 บาท, 3 คน, ทิป 10%
