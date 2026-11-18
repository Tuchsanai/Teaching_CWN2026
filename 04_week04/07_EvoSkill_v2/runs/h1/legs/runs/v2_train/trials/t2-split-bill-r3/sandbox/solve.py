from fractions import Fraction


def _require_int(value, name, low=None, high=None):
    # ปฏิเสธ bool, float, str, None ก่อน (type(x) is int ไม่รับ subclass อย่าง bool)
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    if high is not None and value > high:
        raise ValueError(f"{name} ต้องไม่เกิน {high}")
    return value


def _half_up(x):
    """ปัดครึ่งขึ้นเป็น int, x ไม่ติดลบ"""
    return int((Fraction(x) * 2 + 1) // 2)


def split_bill(total, people, tip_percent):
    """หารบิลรวมทิป คืน list ของยอดที่แต่ละคนจ่ายเป็นสตางค์ เรียงตามลำดับคน

    total        ยอดบิลเป็นสตางค์ (int >= 0)
    people       จำนวนคน (int >= 1)
    tip_percent  ทิปเป็นเปอร์เซ็นต์ (int 0..100)
    """
    total = _require_int(total, "total", low=0)
    people = _require_int(people, "people", low=1)
    tip_percent = _require_int(tip_percent, "tip_percent", low=0, high=100)

    # ทิปเป็นเงินที่ลูกค้าจ่ายให้ร้าน จึงปัดครึ่งขึ้น ปัดครั้งเดียวตอนนี้
    tip = _half_up(Fraction(total * tip_percent, 100))
    due = total + tip

    # หารเท่ากัน เศษสตางค์ให้คนลำดับแรก ๆ คนละ 1 สตางค์
    base, remainder = divmod(due, people)
    return [base + 1 if i < remainder else base for i in range(people)]


if __name__ == "__main__":
    print(split_bill(10001, 3, 10))  # [3667, 3667, 3667]
