import json
import sys

EXPECTED_KEYS = ("unit_price", "qty", "coupon")


def bulk_price(unit_price, qty, coupon):
    if type(unit_price) is not int:
        raise ValueError("unit_price ต้องเป็นจำนวนเต็ม (สตางค์)")
    if unit_price < 0:
        raise ValueError("unit_price ต้องไม่ติดลบ")
    if type(qty) is not int:
        raise ValueError("qty ต้องเป็นจำนวนเต็ม")
    if qty < 1 or qty > 1000:
        raise ValueError("qty ต้องอยู่ระหว่าง 1 ถึง 1000")
    if type(coupon) is not bool:
        raise ValueError("coupon ต้องเป็น true หรือ false")

    # ส่วนลดซื้อจำนวนมาก ใช้อัตราเดียว เก็บเป็นตัวเศษ (bulk_num) ต่อตัวส่วน 1000
    if qty >= 50:
        bulk_num = 75  # 7.5%
    elif qty >= 10:
        bulk_num = 35  # 3.5%
    else:
        bulk_num = 0

    # ทุกขั้นเก็บเป็นตัวเศษ num กับตัวส่วน den โดยยังไม่ปัด
    num = unit_price * qty
    den = 1

    num *= 1000 - bulk_num
    den *= 1000

    if coupon:
        num *= 1000 - 25  # คูปองลดอีก 2.5% จากราคาหลังลดจำนวนมาก
        den *= 1000

    num *= 107  # VAT 7% เป็นขั้นสุดท้าย
    den *= 100

    # ปัดครั้งเดียว แบบครึ่งปัดขึ้น
    return (2 * num + den) // (2 * den)


def _fail(message):
    print(json.dumps({"ok": False, "error": message}))
    sys.exit(2)


def _main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except (ValueError, OSError):
        _fail("input ต้องเป็น JSON ที่ถูกต้อง")

    if type(data) is not dict:
        _fail("input ต้องเป็น JSON object")

    missing = [k for k in EXPECTED_KEYS if k not in data]
    if missing:
        _fail("ขาด key: " + ", ".join(missing))

    extra = [k for k in data if k not in EXPECTED_KEYS]
    if extra:
        _fail("key ไม่รู้จัก: " + ", ".join(str(k) for k in extra))

    try:
        result = bulk_price(**{k: data[k] for k in EXPECTED_KEYS})
    except ValueError as exc:
        _fail(str(exc))

    print(json.dumps({"ok": True, "result": result}))
    sys.exit(0)


if __name__ == "__main__":
    _main()
