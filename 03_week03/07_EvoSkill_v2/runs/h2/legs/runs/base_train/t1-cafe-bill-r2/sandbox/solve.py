"""BaanKafe checkout: cafe_bill(items, member).

Money is handled in integer satang (1 baht = 100 satang) to avoid float error.
Each step rounds half-up to the nearest satang:

1. subtotal = sum(price * qty)
2. subtotal >= 500 baht (50,000 satang) -> 5% off
3. member=True -> a further 10% off (applied to the amount after step 2)
4. VAT 7% added last
"""


def _round_half_up(numerator, denominator):
    """Return numerator / denominator rounded half-up to an integer.

    Both values must be non-negative integers and denominator > 0.
    """
    return (2 * numerator + denominator) // (2 * denominator)


def cafe_bill(items, member):
    """Return the amount the customer must pay, as an integer number of satang.

    items:  list of {"price": satang per piece (int >= 0), "qty": pieces (int >= 1)}
    member: True applies an extra 10% discount.
    """
    subtotal = 0
    for item in items:
        price = item["price"]
        qty = item["qty"]
        if not isinstance(price, int) or isinstance(price, bool) or price < 0:
            raise ValueError(f"price must be a non-negative integer (satang): {price!r}")
        if not isinstance(qty, int) or isinstance(qty, bool) or qty < 1:
            raise ValueError(f"qty must be an integer >= 1: {qty!r}")
        subtotal += price * qty

    total = subtotal

    # Bulk discount: subtotal of 500 baht or more gets 5% off.
    if total >= 50_000:
        total = _round_half_up(total * 95, 100)

    # Member discount: a further 10% off the amount after the bulk discount.
    if member:
        total = _round_half_up(total * 90, 100)

    # VAT 7% is added last.
    total = _round_half_up(total * 107, 100)

    return total


if __name__ == "__main__":
    # Quick self-checks (amounts in satang).
    assert cafe_bill([], False) == 0
    # 600 baht -> -5% = 570 -> +VAT 7% = 609.90 baht
    assert cafe_bill([{"price": 60_000, "qty": 1}], False) == 60_990
    # 499.99 baht -> below 500, no bulk discount -> 49999*1.07 = 53498.93 -> 53499 satang
    assert cafe_bill([{"price": 49_999, "qty": 1}], False) == 53_499
    # Exactly 500 baht qualifies: 50000*0.95 = 47500, *1.07 = 50825 satang
    assert cafe_bill([{"price": 25_000, "qty": 2}], False) == 50_825
    # Member on top: 47500*0.90 = 42750, *1.07 = 45742.5 -> half-up 45743 satang
    assert cafe_bill([{"price": 25_000, "qty": 2}], True) == 45_743
    # Multiple lines are summed before discounts.
    assert cafe_bill(
        [{"price": 4_500, "qty": 3}, {"price": 9_000, "qty": 4}], False
    ) == cafe_bill([{"price": 49_500, "qty": 1}], False)
    print("all checks passed")
