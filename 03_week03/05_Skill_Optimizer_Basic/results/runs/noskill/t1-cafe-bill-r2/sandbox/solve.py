def cafe_bill(items, member):
    total = sum(i["price"] * i["qty"] for i in items)  # satang
    num, den = total * 107, 100
    if total >= 50000:  # 500 baht
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    return (num * 2 + den) // (den * 2)  # round half up, exact integer math
