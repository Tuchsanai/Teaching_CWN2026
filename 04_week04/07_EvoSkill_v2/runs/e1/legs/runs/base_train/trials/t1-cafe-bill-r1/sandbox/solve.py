def cafe_bill(items, member):
    """Return the amount to pay in integer satang.

    Subtotal >= 500 baht (50000 satang) -> 5% off; member -> a further 10% off;
    then 7% VAT. Computed with exact integer arithmetic, rounding half up once
    at the end.
    """
    total = sum(i["price"] * i["qty"] for i in items)
    num, den = total, 1
    if total >= 50000:
        num *= 95
        den *= 100
    if member:
        num *= 90
        den *= 100
    num *= 107
    den *= 100
    return (2 * num + den) // (2 * den)
