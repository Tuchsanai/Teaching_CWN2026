"""BaanKafe cashier: compute the amount a customer must pay.

All money is handled as integer satang (1 baht = 100 satang) so there are no
floating-point errors. Every percentage step is rounded to the nearest satang
(half up), and the result is an integer number of satang.

Rules, applied in order:
1. Subtotal = sum(price * qty).
2. If the subtotal is >= 500 baht (50000 satang), take 5% off.
3. If member is True, take a further 10% off the discounted amount.
4. Add 7% VAT on the final amount.
"""


def _pct(amount: int, percent: int) -> int:
    """Return amount * percent / 100, rounded half up to a whole satang.

    amount is never negative here, so (2*n + d) // (2*d) is round-half-up.
    """
    n = amount * percent
    d = 100
    return (2 * n + d) // (2 * d)


def cafe_bill(items, member: bool) -> int:
    """Return the total in satang that the customer must pay."""
    subtotal = 0
    for item in items:
        price = int(item["price"])
        qty = int(item["qty"])
        if price < 0 or qty < 1:
            raise ValueError("price must be >= 0 and qty must be >= 1")
        subtotal += price * qty

    total = subtotal

    # 5% off when the pre-discount subtotal reaches 500 baht.
    if subtotal >= 50000:
        total -= _pct(total, 5)

    # Member: a further 10% off the already-discounted amount.
    if member:
        total -= _pct(total, 10)

    # VAT 7% is the final step.
    total += _pct(total, 7)

    return total


if __name__ == "__main__":
    # Quick examples (amounts in satang).
    print(cafe_bill([{"price": 4500, "qty": 2}], False))   # 90 baht -> 96.30 baht = 9630
    print(cafe_bill([{"price": 15000, "qty": 4}], False))  # 600 baht -> 570 -> 609.90 = 60990
    print(cafe_bill([{"price": 15000, "qty": 4}], True))   # 600 -> 570 -> 513 -> 548.91 = 54891
