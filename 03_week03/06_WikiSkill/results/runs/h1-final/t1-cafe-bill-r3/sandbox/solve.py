import json
import sys
from fractions import Fraction

# หน่วยทั้งหมดเป็นสตางค์
BULK_THRESHOLD = 50000          # 500 บาท
BULK_RATE = Fraction(5, 100)    # ลด 5% เมื่อยอดตั้งแต่ 500 บาทขึ้นไป
MEMBER_RATE = Fraction(10, 100) # สมาชิกลดเพิ่ม 10%
VAT_RATE = Fraction(7, 100)     # VAT 7% (ขั้นสุดท้าย)


def _half_up(x: Fraction) -> int:
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def _int(v, name, lo=None, hi=None):
    if isinstance(v, bool) or not isinstance(v, int):
        raise ValueError(f"{name} must be an integer")
    if (lo is not None and v < lo) or (hi is not None and v > hi):
        raise ValueError(f"{name} out of range")
    return v


def _bool(v, name):
    if not isinstance(v, bool):
        raise ValueError(f"{name} must be a bool")
    return v


def _validate_items(items):
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    lines = []
    for i, it in enumerate(items):
        if not isinstance(it, dict):
            raise ValueError(f"items[{i}] must be a dict")
        if set(it.keys()) != {"price", "qty"}:
            raise ValueError(f"items[{i}] must have exactly the keys price and qty")
        price = _int(it["price"], f"items[{i}].price", lo=0)
        qty = _int(it["qty"], f"items[{i}].qty", lo=1)
        lines.append((price, qty))
    return lines


def cafe_bill(items, member):
    lines = _validate_items(items)
    _bool(member, "member")

    # ยอดรวมเป็นจำนวนเต็มสตางค์ ไม่มีการปัดระหว่างทาง
    subtotal = sum(price * qty for price, qty in lines)
    total = Fraction(subtotal)

    # เทียบเกณฑ์ด้วยยอดที่ยังไม่ปัด (subtotal เป็นจำนวนเต็มอยู่แล้ว)
    if subtotal >= BULK_THRESHOLD:
        total *= 1 - BULK_RATE
    if member:
        total *= 1 - MEMBER_RATE
    total *= 1 + VAT_RATE

    return _half_up(total)


def main():
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = cafe_bill(**data)
        out = json.dumps({"ok": True, "result": result})
    except Exception as e:  # รวม JSON เสีย, key เกิน/ขาด, ValueError
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 2
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
