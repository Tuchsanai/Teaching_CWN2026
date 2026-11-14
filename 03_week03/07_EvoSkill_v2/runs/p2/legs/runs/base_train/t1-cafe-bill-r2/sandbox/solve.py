def cafe_bill(items, member):
    """Return the amount to pay in integer satang.

    Total >= 500 baht (50000 satang) -> 5% off; member -> a further 10% off;
    then 7% VAT last. Exact integer arithmetic, rounded half-up once at the end.
    """
    total = sum(i["price"] * i["qty"] for i in items)
    num = total * 107
    den = 100
    if total >= 50000:
        num *= 95
        den *= 100
    if member:
        num *= 90
        den *= 100
    return (2 * num + den) // (2 * den)
