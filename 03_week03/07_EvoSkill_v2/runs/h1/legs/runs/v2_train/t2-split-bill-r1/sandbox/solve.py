from fractions import Fraction


def _require_int(value, label, lo=None, hi=None):
    if type(value) is not int:
        raise ValueError(f"{label} ต้องเป็นจำนวนเต็ม")
    if lo is not None and value < lo:
        raise ValueError(f"{label} ต้องไม่น้อยกว่า {lo}")
    if hi is not None and value > hi:
        raise ValueError(f"{label} ต้องไม่เกิน {hi}")
    return value


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม รับ Fraction ที่ไม่ติดลบ"""
    return int((Fraction(x) * 2 + 1) // 2)


def split_bill(total, people, tip_percent):
    """หารบิลให้คนเท่า ๆ กันหลังบวกทิป หน่วยเป็นสตางค์

    total: ยอดบิลเป็นสตางค์ (int >= 0)
    people: จำนวนคน (int >= 1)
    tip_percent: ทิปเป็นเปอร์เซ็นต์ (int 0-100)

    คืน list ของ int ยอดที่แต่ละคนจ่าย เรียงตามลำดับคน
    คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์ถ้าหารไม่ลงตัว
    """
    _require_int(total, "total", lo=0)
    _require_int(people, "people", lo=1)
    _require_int(tip_percent, "tip_percent", lo=0, hi=100)

    # ยอดรวมที่มีทิป ปัดครึ่งขึ้นครั้งเดียวเป็นสตางค์ เพื่อให้หารได้เป็นจำนวนเต็ม
    grand_total = _half_up(Fraction(total * (100 + tip_percent), 100))

    base, extra = divmod(grand_total, people)
    return [base + 1 if i < extra else base for i in range(people)]


def main():
    import json
    import sys

    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = split_bill(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
