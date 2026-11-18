from fractions import Fraction


def _require_int(value, name, low=None, high=None):
    if type(value) is not int:  # ปฏิเสธ bool, float, str, None
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    if high is not None and value > high:
        raise ValueError(f"{name} ต้องไม่เกิน {high}")
    return value


def _half_up(x):
    """ปัดครึ่งขึ้นเป็น int สำหรับค่าที่ไม่ติดลบ (Fraction)"""
    return int((Fraction(x) * 2 + 1) // 2)


def split_bill(total, people, tip_percent):
    """หารบิลให้คนจ่ายเท่ากันเป็นสตางค์ทั้งหมด

    total        ยอดบิลเป็นสตางค์ (int, >= 0)
    people       จำนวนคน (int, >= 1)
    tip_percent  ทิปเป็นเปอร์เซ็นต์ (int, 0–100)

    คืน list[int] ของยอดที่แต่ละคนจ่าย (สตางค์) เรียงตามลำดับคน
    คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์เมื่อหารไม่ลงตัว
    """
    total = _require_int(total, "total", low=0)
    people = _require_int(people, "people", low=1)
    tip_percent = _require_int(tip_percent, "tip_percent", low=0, high=100)

    # ยอดที่ต้องหาร = ยอดบิล + ทิป (คูณทั้งหมดก่อน แล้วปัดครั้งเดียว)
    amount_due = _half_up(Fraction(total) * (100 + tip_percent) / 100)

    base, remainder = divmod(amount_due, people)
    return [base + 1 if i < remainder else base for i in range(people)]


if __name__ == "__main__":
    print(split_bill(10001, 3, 10))
