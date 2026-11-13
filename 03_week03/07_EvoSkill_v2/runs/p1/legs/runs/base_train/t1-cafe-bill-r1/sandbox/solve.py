def cafe_bill(items, member):
    """Return amount due in integer satang (exact arithmetic, rounded half-up once at the end)."""
    total = sum(i["price"] * i["qty"] for i in items)  # satang
    num, den = total, 1
    if total >= 50000:  # 500 baht
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100  # VAT 7%
    return (2 * num + den) // (2 * den)
