def cafe_bill(items, member):
    """Return the amount to pay in integer satang (rounded half up once, at the end)."""
    subtotal = sum(i["price"] * i["qty"] for i in items)
    num, den = subtotal * 100, 100
    if subtotal >= 50000:      # 500 baht = 50,000 satang
        num *= 95; den *= 100
    if member:
        num *= 90; den *= 100
    num *= 107; den *= 100
    return (2 * num + den) // (2 * den)
