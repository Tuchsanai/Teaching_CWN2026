def cafe_bill(items, member):
    total = sum(i["price"] * i["qty"] for i in items)  # satang
    num, den = total, 1
    if total >= 50000:  # 500 baht
        num *= 95
        den *= 100
    if member:
        num *= 90
        den *= 100
    num *= 107
    den *= 100
    # round half up, once, at the very end (exact integer arithmetic)
    return (2 * num + den) // (2 * den)
