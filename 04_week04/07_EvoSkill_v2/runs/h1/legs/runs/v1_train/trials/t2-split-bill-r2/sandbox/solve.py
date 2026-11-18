from fractions import Fraction


def _require_int(value, name, low=None, high=None):
    if type(value) is not int:  # ปฏิเสธ bool, float, str, None
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    if high is not None and value > high:
        raise ValueError(f"{name} ต้องไม่เกิน {high}")
    return value


def split_bill(total, people, tip_percent):
    """หารบิลให้คนทั้งหมดเท่ากันเป็นสตางค์ (จำนวนเต็ม)

    total       ยอดบิลเป็นสตางค์ (>= 0)
    people      จำนวนคน (>= 1)
    tip_percent ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0-100)

    คืน list ของยอดที่แต่ละคนจ่าย (สตางค์ จำนวนเต็ม) เรียงตามลำดับคน
    คนลำดับต้น ๆ จ่ายเพิ่มคนละ 1 สตางค์เมื่อหารไม่ลงตัว
    """
    _require_int(total, "total", low=0)
    _require_int(people, "people", low=1)
    _require_int(tip_percent, "tip_percent", low=0, high=100)

    # ยอดรวมหลังทิปคำนวณแบบเศษส่วนก่อน แล้วปัดครั้งเดียวแบบครึ่งขึ้น
    exact = Fraction(total) + Fraction(total * tip_percent, 100)
    amount = int((exact * 2 + 1) // 2)

    base, remainder = divmod(amount, people)
    return [base + 1 if i < remainder else base for i in range(people)]


if __name__ == "__main__":
    print(split_bill(10000, 3, 10))  # 10000 + ทิป 10% = 11000 -> [3667, 3667, 3666]
