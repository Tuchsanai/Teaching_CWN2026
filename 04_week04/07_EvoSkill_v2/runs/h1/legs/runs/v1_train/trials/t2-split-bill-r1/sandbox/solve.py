from fractions import Fraction


def _require_int(value, name, low=None, high=None):
    # ปฏิเสธ bool, float, str, None ก่อน (bool เป็นลูกของ int ใน Python)
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    if high is not None and value > high:
        raise ValueError(f"{name} ต้องไม่เกิน {high}")
    return value


def split_bill(total, people, tip_percent):
    """หารบิล (หน่วยสตางค์) พร้อมทิป

    - ยอดที่ต้องหาร = total + ทิป (total * tip_percent / 100)
    - ปัดเศษครั้งเดียวที่ยอดรวม แบบปัดครึ่งขึ้น (half-up)
    - หารเท่ากัน หารไม่ลงตัวให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์
    - คืน list ของยอดแต่ละคน (int สตางค์) เรียงตามลำดับคน
    """
    total = _require_int(total, "total", low=0)
    people = _require_int(people, "people", low=1)
    tip_percent = _require_int(tip_percent, "tip_percent", low=0, high=100)

    # ทิปรวมอยู่ในยอดก่อนปัด: (total * (100 + tip%)) / 100 ด้วย Fraction ไม่มี float
    exact = Fraction(total) * (100 + tip_percent) / 100
    grand_total = int(exact * 2 + 1) // 2  # ปัดครึ่งขึ้นครั้งเดียว (exact >= 0)

    base, remainder = divmod(grand_total, people)
    return [base + 1 if i < remainder else base for i in range(people)]


if __name__ == "__main__":
    print(split_bill(10000, 3, 10))
