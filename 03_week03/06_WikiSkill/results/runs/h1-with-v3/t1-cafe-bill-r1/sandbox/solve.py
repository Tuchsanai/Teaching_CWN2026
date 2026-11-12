import json
import sys

PERCENT = 100
BULK_THRESHOLD = 50000  # 500 บาท (หน่วยสตางค์)
BULK_KEEP = 95          # ลด 5% เหลือ 95%
MEMBER_KEEP = 90        # ลด 10% เหลือ 90%
VAT_MULT = 107          # บวก VAT 7% = คูณ 107%


def _int_field(value, name):
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    return value


def _subtotal(items):
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    total = 0
    for i, item in enumerate(items):
        if type(item) is not dict:
            raise ValueError(f"items[{i}] ต้องเป็น dict")
        if "price" not in item or "qty" not in item:
            raise ValueError(f"items[{i}] ต้องมี price และ qty")
        price = _int_field(item["price"], f"items[{i}].price")
        qty = _int_field(item["qty"], f"items[{i}].qty")
        if price < 0:
            raise ValueError(f"items[{i}].price ต้องไม่ติดลบ")
        if qty < 1:
            raise ValueError(f"items[{i}].qty ต้องอย่างน้อย 1")
        total += price * qty
    return total


def cafe_bill(items, member):
    subtotal = _subtotal(items)
    if type(member) is not bool:
        raise ValueError("member ต้องเป็น true หรือ false")

    # เก็บทุกขั้นเป็นเศษ num กับตัวส่วน den โดยยังไม่ปัด
    # เงื่อนไขส่วนลดปริมาณใช้ยอดก่อนหักส่วนลดสมาชิก
    num, den = subtotal, 1
    if subtotal >= BULK_THRESHOLD:
        num *= BULK_KEEP
        den *= PERCENT
    if member:
        num *= MEMBER_KEEP
        den *= PERCENT
    num *= VAT_MULT
    den *= PERCENT

    # ปัดครั้งเดียวที่ขั้นสุดท้าย แบบครึ่งปัดขึ้น
    return (2 * num + den) // (2 * den)


def main():
    try:
        payload = json.loads(sys.stdin.read())
        if type(payload) is not dict:
            raise ValueError("input ต้องเป็น JSON object")
        if "items" not in payload or "member" not in payload:
            raise ValueError("ต้องมี key items และ member")
        result = cafe_bill(payload["items"], payload["member"])
    except (ValueError, RecursionError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
