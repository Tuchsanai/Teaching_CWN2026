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

    # อัตราคูณเป็นหน่วย 1/1000 (ลดตามจำนวน ใช้อัตราเดียว)
    if qty >= 50:
        tier = 1000 - 75
    elif qty >= 10:
        tier = 1000 - 35
    else:
        tier = 1000
    cpn = 975 if coupon else 1000  # ลดคูปองซ้อนต่อจากส่วนลดจำนวน (คูณกัน)

    num = unit_price * qty * tier * cpn * 107
    den = 1000 * 1000 * 100
    # ปัดครึ่งขึ้นครั้งเดียวตอนท้าย ด้วยจำนวนเต็มล้วน
    return (2 * num + den) // (2 * den)


if __name__ == "__main__":
    import json, sys
    try:
        data = json.loads(sys.stdin.read())
        if type(data) is not dict:
            raise ValueError("อินพุตต้องเป็น JSON object")
        result = bulk_price(**data)
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e) or type(e).__name__}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))
    sys.exit(0)
