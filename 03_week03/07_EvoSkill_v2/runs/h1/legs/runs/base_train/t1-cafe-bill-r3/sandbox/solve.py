"""BaanKafe cashier bill calculator."""

from fractions import Fraction
from math import floor

# Thresholds and rates (money in satang: 1 baht = 100 satang)
BULK_THRESHOLD = 500 * 100  # 500 baht
BULK_DISCOUNT = Fraction(5, 100)
MEMBER_DISCOUNT = Fraction(10, 100)
VAT_RATE = Fraction(7, 100)


def cafe_bill(items, member):
    """Return the amount the customer must pay, in whole satang.

    items  -- list of {"price": unit price in satang, "qty": quantity (>= 1)}
    member -- True applies an extra 10% discount

    Order of calculation:
      1. subtotal = sum(price * qty)
      2. subtotal >= 500 baht -> 5% off
      3. member -> further 10% off (applied to the discounted amount)
      4. 7% VAT added last

    Exact fractions are used throughout; only the final result is rounded
    (half up) to an integer number of satang.
    """
    subtotal = 0
    for item in items:
        price = int(item["price"])
        qty = int(item["qty"])
        if price < 0 or qty < 1:
            raise ValueError("price must be >= 0 and qty must be >= 1")
        subtotal += price * qty

    total = Fraction(subtotal)

    if subtotal >= BULK_THRESHOLD:
        total *= 1 - BULK_DISCOUNT

    if member:
        total *= 1 - MEMBER_DISCOUNT

    total *= 1 + VAT_RATE

    return floor(total + Fraction(1, 2))


if __name__ == "__main__":
    # ตัวอย่าง: กาแฟ 65 บาท x 2 + เค้ก 120 บาท x 3 (ไม่ใช่สมาชิก)
    sample = [
        {"price": 6500, "qty": 2},
        {"price": 12000, "qty": 3},
    ]
    print(cafe_bill(sample, member=False))  # subtotal 49,000 satang < 500 บาท
    print(cafe_bill(sample, member=True))
