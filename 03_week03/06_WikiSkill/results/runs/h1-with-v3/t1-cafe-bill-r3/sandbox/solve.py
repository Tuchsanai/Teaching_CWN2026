import json
import sys

# อัตราทั้งหมดเป็นเศษส่วนจำนวนเต็ม (ตัวเศษ, ตัวส่วน) หน่วยเงินเป็นสตางค์
BULK_THRESHOLD = 50000   # 500 บาท
BULK_RATE = (95, 100)    # ลด 5% เมื่อยอดรวมถึงเกณฑ์
MEMBER_RATE = (90, 100)  # ลดเพิ่ม 10% สำหรับสมาชิก
VAT_RATE = (107, 100)    # บวก VAT 7% เป็นขั้นสุดท้าย


def _check_items(items):
    if not isinstance(items, list):
        raise ValueError("items ต้องเป็น list")
    if len(items) == 0:
        raise ValueError("items ต้องมีอย่างน้อย 1 รายการ")
    subtotal = 0
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"items[{index}] ต้องเป็น object")
        if "price" not in item or "qty" not in item:
            raise ValueError(f"items[{index}] ต้องมี key price และ qty")
        price = item["price"]
        qty = item["qty"]
        if type(price) is not int or price < 0:
            raise ValueError(f"items[{index}].price ต้องเป็นจำนวนเต็มสตางค์ที่ไม่ติดลบ")
        if type(qty) is not int or qty < 1:
            raise ValueError(f"items[{index}].qty ต้องเป็นจำนวนเต็มตั้งแต่ 1")
        subtotal += price * qty
    return subtotal


def cafe_bill(items, member):
    if type(member) is not bool:
        raise ValueError("member ต้องเป็น true หรือ false")
    num = _check_items(items)
    den = 1

    if num >= BULK_THRESHOLD:
        num *= BULK_RATE[0]
        den *= BULK_RATE[1]
    if member:
        num *= MEMBER_RATE[0]
        den *= MEMBER_RATE[1]
    num *= VAT_RATE[0]
    den *= VAT_RATE[1]

    # ปัดครั้งเดียวที่ขั้นสุดท้าย แบบครึ่งปัดขึ้น (half-up)
    return (2 * num + den) // (2 * den)


def main():
    try:
        payload = json.loads(sys.stdin.read())
        if not isinstance(payload, dict):
            raise ValueError("stdin ต้องเป็น JSON object")
        missing = [key for key in ("items", "member") if key not in payload]
        if missing:
            raise ValueError("ขาด key: " + ", ".join(missing))
        result = cafe_bill(items=payload["items"], member=payload["member"])
    except ValueError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
