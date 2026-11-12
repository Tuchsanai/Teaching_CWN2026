"""คิดราคาขายส่งเมล็ดกาแฟ BaanKafe

หน่วยเป็นสตางค์ทั้งหมด ตัวคูณทุกตัวเก็บเป็นเศษส่วนจำนวนเต็ม
และปัดเศษครั้งเดียวที่ขั้นสุดท้ายแบบครึ่งปัดขึ้น
"""
import json
import sys

# (จำนวนถุงขั้นต่ำ, ส่วนลดเป็นหน่วยต่อพัน) เรียงจากมากไปน้อย ใช้อัตราเดียว
BULK_TIERS = ((50, 75), (10, 35))
COUPON_PERMILLE = 25      # คูปอง 2.5%
VAT_PERCENT = 7           # VAT 7%


def bulk_price(unit_price, qty, coupon):
    if type(unit_price) is not int or unit_price < 0:
        raise ValueError("unit_price ต้องเป็นจำนวนเต็มสตางค์ตั้งแต่ 0")
    if type(qty) is not int or not 1 <= qty <= 1000:
        raise ValueError("qty ต้องเป็นจำนวนเต็มตั้งแต่ 1 ถึง 1000")
    if type(coupon) is not bool:
        raise ValueError("coupon ต้องเป็น true หรือ false")

    bulk = 0
    for min_qty, permille in BULK_TIERS:
        if qty >= min_qty:
            bulk = permille
            break
    coupon_rate = COUPON_PERMILLE if coupon else 0

    # ราคารวม x (1000 - ส่วนลดขายส่ง) x (1000 - คูปอง) x (100 + VAT) ทั้งหมดอยู่ในตัวเศษ
    # ตัวส่วนคือ 1000 x 1000 x 100
    num = unit_price * qty * (1000 - bulk) * (1000 - coupon_rate) * (100 + VAT_PERCENT)
    den = 1000 * 1000 * 100
    return (2 * num + den) // (2 * den)


def _main():
    try:
        payload = json.loads(sys.stdin.read())
        if not isinstance(payload, dict):
            raise ValueError("input ต้องเป็น JSON object")
        for key in ("unit_price", "qty", "coupon"):
            if key not in payload:
                raise ValueError("ขาด key: " + key)
        result = bulk_price(payload["unit_price"], payload["qty"], payload["coupon"])
    except ValueError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
