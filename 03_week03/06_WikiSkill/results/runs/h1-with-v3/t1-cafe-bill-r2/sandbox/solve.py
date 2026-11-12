import json
import sys

# หน่วยเป็นสตางค์ทั้งหมด
THRESHOLD = 500 * 100            # ยอดตั้งแต่ 500 บาทขึ้นไป
BULK_NUM, BULK_DEN = 95, 100     # ลด 5%
MEMBER_NUM, MEMBER_DEN = 90, 100 # สมาชิกลดอีก 10% (ลดต่อจากยอดหลังลด 5%)
VAT_NUM, VAT_DEN = 107, 100      # VAT 7% เป็นขั้นสุดท้าย


def _check_int(value, name):
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม (สตางค์)")
    return value


def cafe_bill(items, member):
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    if type(member) is not bool:
        raise ValueError("member ต้องเป็น true หรือ false")

    subtotal = 0
    for i, item in enumerate(items):
        if type(item) is not dict:
            raise ValueError(f"items[{i}] ต้องเป็น object")
        if "price" not in item or "qty" not in item:
            raise ValueError(f"items[{i}] ต้องมี price และ qty")
        price = _check_int(item["price"], f"items[{i}].price")
        qty = _check_int(item["qty"], f"items[{i}].qty")
        if price < 0:
            raise ValueError(f"items[{i}].price ต้องไม่ติดลบ")
        if qty < 1:
            raise ValueError(f"items[{i}].qty ต้องอย่างน้อย 1")
        subtotal += price * qty

    # สะสมเป็นตัวเศษ num และตัวส่วน den โดยไม่ปัดระหว่างทาง
    num, den = subtotal, 1
    if subtotal >= THRESHOLD:
        num *= BULK_NUM
        den *= BULK_DEN
    if member:
        num *= MEMBER_NUM
        den *= MEMBER_DEN
    num *= VAT_NUM
    den *= VAT_DEN

    # ปัดครั้งเดียวแบบครึ่งปัดขึ้น (half-up)
    return (2 * num + den) // (2 * den)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if type(data) is not dict:
            raise ValueError("input ต้องเป็น JSON object")
        missing = [k for k in ("items", "member") if k not in data]
        if missing:
            raise ValueError("ขาด key: " + ", ".join(missing))
        result = cafe_bill(data["items"], data["member"])
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
