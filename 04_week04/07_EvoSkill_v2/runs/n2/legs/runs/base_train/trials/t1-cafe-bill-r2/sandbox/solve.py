def cafe_bill(items, member):
    total = sum(i["price"] * i["qty"] for i in items)  # satang
    a = 95 if total >= 50000 else 100
    b = 90 if member else 100
    num = total * a * b * 107
    den = 1_000_000
    return (2 * num + den) // (2 * den)  # round half up, single rounding at the end
