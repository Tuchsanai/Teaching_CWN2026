from fractions import Fraction


def _require_int(value, label, lo=None, hi=None):
    # type(...) is int ปฏิเสธ bool, float และ str ทุกกรณี
    if type(value) is not int:
        raise ValueError(f"{label} ต้องเป็นจำนวนเต็ม")
    if lo is not None and value < lo:
        raise ValueError(f"{label} ต้องไม่น้อยกว่า {lo}")
    if hi is not None and value > hi:
        raise ValueError(f"{label} ต้องไม่เกิน {hi}")
    return value


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม สำหรับค่าที่ไม่ติดลบ"""
    return int((Fraction(x) * 2 + 1) // 2)


def split_bill(total, people, tip_percent):
    """หารบิลให้คนละเท่า ๆ กัน (หน่วยสตางค์) รวมทิปก่อนหาร

    total        ยอดบิลเป็นสตางค์ (>= 0)
    people       จำนวนคน (>= 1)
    tip_percent  ทิปเป็นเปอร์เซ็นต์ จำนวนเต็ม 0–100

    คืน list ของยอดที่แต่ละคนจ่าย (int สตางค์) เรียงตามลำดับคน
    คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์เมื่อหารไม่ลงตัว
    """
    total = _require_int(total, "total", lo=0)
    people = _require_int(people, "people", lo=1)
    tip_percent = _require_int(tip_percent, "tip_percent", lo=0, hi=100)

    # ยอดที่ต้องหาร = บิล + ทิป คำนวณเป็นเศษส่วนแล้วปัดครึ่งขึ้นครั้งเดียว
    # เพราะยอดที่หารต้องเป็นจำนวนเต็มสตางค์ (บิลเป็นจำนวนเต็มอยู่แล้ว จึงเท่ากับปัดทิปแล้วบวก)
    grand_total = _half_up(Fraction(total) * (100 + tip_percent) / 100)

    base, extra = divmod(grand_total, people)
    return [base + 1 if i < extra else base for i in range(people)]


if __name__ == "__main__":
    print(split_bill(10000, 3, 0))    # [3334, 3333, 3333]
    print(split_bill(10000, 4, 10))   # [2750, 2750, 2750, 2750]
    print(split_bill(1, 1, 50))       # [2]
