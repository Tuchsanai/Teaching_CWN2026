"""BaanKafe cafe bill calculator.

ทุกค่าเงินเป็นสตางค์ (int). ลำดับการคิด:
1. ยอดรวม = sum(price * qty)
2. ถ้ายอดรวม >= 50,000 สตางค์ (500 บาท) ลด 5%
3. ถ้า member = True ลดอีก 10% (คูณต่อจากข้อ 2)
4. บวก VAT 7% เป็นขั้นสุดท้าย
5. ปัดเศษแบบ half up ครั้งเดียวตอนท้าย
"""

from fractions import Fraction
import json
import sys

THRESHOLD_SATANG = 50_000  # 500 บาท


def _half_up(x: Fraction) -> int:
    """ปัดเศษ half up ของ Fraction ไม่ติดลบเป็นจำนวนเต็ม"""
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


def cafe_bill(items, member):
    if not isinstance(items, list):
        raise ValueError("items must be a list")

    subtotal = 0
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"items[{i}] must be a dict")
        if "price" not in item or "qty" not in item:
            raise ValueError(f"items[{i}] must have 'price' and 'qty'")
        price = _int(item["price"], f"items[{i}].price", lo=0)
        qty = _int(item["qty"], f"items[{i}].qty", lo=1)
        subtotal += price * qty

    member = _bool(member, "member")

    # คำนวณด้วย Fraction ทั้งหมด ปัดครั้งเดียวตอนท้าย
    total = Fraction(subtotal)
    if subtotal >= THRESHOLD_SATANG:
        total *= Fraction(95, 100)  # ลด 5%
    if member:
        total *= Fraction(90, 100)  # ลดอีก 10%
    total *= Fraction(107, 100)  # VAT 7%

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
