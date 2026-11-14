def cafe_bill(items, member):
    sub = sum(i["price"] * i["qty"] for i in items)
    num, den = sub, 1
    if sub >= 50000:
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100
    return (2 * num + den) // (2 * den)  # round half up, exact integer math
