def cafe_bill(items, member):
    total = sum(i["price"] * i["qty"] for i in items)  # satang
    num, den = 107, 100
    if total >= 50000:
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    # round half up, once, at the end (exact integer arithmetic)
    return (total * num * 2 + den) // (den * 2)
