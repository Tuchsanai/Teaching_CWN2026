from fractions import Fraction


def _need_int(name, v, lo=None, hi=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if lo is not None and v < lo:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {lo}")
    if hi is not None and v > hi:
        raise ValueError(f"{name} ต้องไม่เกิน {hi}")


def bulk_price(unit_price, qty, coupon):
    _need_int("unit_price", unit_price, lo=0)
    _need_int("qty", qty, lo=1, hi=1000)
    if type(coupon) is not bool:
        raise ValueError("coupon ต้องเป็น bool")

    total = Fraction(unit_price * qty)
    if qty >= 50:
        total *= Fraction(925, 1000)  # ลด 7.5% (อัตราเดียว)
    elif qty >= 10:
        total *= Fraction(965, 1000)  # ลด 3.5%
    if coupon:
        total *= Fraction(975, 1000)  # คูปองลดอีก 2.5% (ต่อจากส่วนลดปริมาณ)
    total *= Fraction(107, 100)  # VAT 7% ขั้นสุดท้าย

    # ปัดครั้งเดียวตอนท้าย แบบครึ่งขึ้น (โจทย์ไม่ระบุโหมด)
    return int((total * 2 + 1) // 2)


if __name__ == "__main__":
    import json, sys
    try:
        data = json.loads(sys.stdin.read())
        if type(data) is not dict:
            raise ValueError("อินพุตต้องเป็น JSON object")
        result = bulk_price(**data)
    except Exception as e:  # ValueError, TypeError, KeyError, JSONDecodeError
        print(json.dumps({"ok": False, "error": str(e) or type(e).__name__}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))
    sys.exit(0)
