"""BaanKafe cashier bill calculator.

Units: all money is in satang (1 baht = 100 satang), handled as integers
so no floating-point drift creeps in.

Rules, applied in this order:
1. Subtotal = sum(price * qty).
2. If subtotal >= 500 baht (50,000 satang), take 5% off.
3. If the customer is a member, take a further 10% off the discounted amount.
4. Add 7% VAT on the final amount.

Each percentage is rounded half-up to the nearest satang at its own step.
"""

from typing import Iterable, Mapping

BAHT = 100
BULK_THRESHOLD = 500 * BAHT  # 50,000 satang
BULK_DISCOUNT_PCT = 5
MEMBER_DISCOUNT_PCT = 10
VAT_PCT = 7


def _percent_of(amount: int, pct: int) -> int:
    """Return amount * pct / 100, rounded half-up to an integer satang."""
    return (amount * pct + 50) // 100


def cafe_bill(items: Iterable[Mapping], member: bool) -> int:
    """Return the amount the customer must pay, in whole satang.

    items:  iterable of {"price": satang per piece, "qty": pieces (>= 1)}
    member: True applies the extra 10% member discount.
    """
    subtotal = 0
    for item in items:
        price = int(item["price"])
        qty = int(item["qty"])
        if price < 0:
            raise ValueError("price must not be negative")
        if qty < 1:
            raise ValueError("qty must be at least 1")
        subtotal += price * qty

    amount = subtotal

    if subtotal >= BULK_THRESHOLD:
        amount -= _percent_of(amount, BULK_DISCOUNT_PCT)

    if member:
        amount -= _percent_of(amount, MEMBER_DISCOUNT_PCT)

    amount += _percent_of(amount, VAT_PCT)

    return amount


if __name__ == "__main__":
    # Quick sanity checks (values in satang).
    # 2 x 300 baht = 600 baht -> 5% off = 570 -> VAT 7% = 609.90 baht
    assert cafe_bill([{"price": 30000, "qty": 2}], member=False) == 60990
    # Same, member: 570 -> 10% off = 513 -> VAT = 548.91 baht
    assert cafe_bill([{"price": 30000, "qty": 2}], member=True) == 54891
    # Under 500 baht, no bulk discount: 100 baht -> VAT 107 baht
    assert cafe_bill([{"price": 10000, "qty": 1}], member=False) == 10700
    # Exactly 500 baht triggers the 5% discount: 475 -> VAT 508.25
    assert cafe_bill([{"price": 50000, "qty": 1}], member=False) == 50825
    # Empty cart costs nothing
    assert cafe_bill([], member=True) == 0
    print("all checks passed")
