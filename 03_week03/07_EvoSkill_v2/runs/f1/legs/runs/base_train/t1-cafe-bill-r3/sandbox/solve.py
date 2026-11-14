def cafe_bill(items, member):
    """Return amount payable in whole satang (integer arithmetic, rounded half-up once at the end)."""
    total = sum(i["price"] * i["qty"] for i in items)
    num, den = total, 1
    if total >= 50000:      # 500 baht
        num *= 95; den *= 100
    if member:
        num *= 90; den *= 100
    num *= 107; den *= 100  # VAT 7%
    return (2 * num + den) // (2 * den)
