def cafe_bill(items, member):
    total = sum(i["price"] * i["qty"] for i in items)
    num, den = 107, 100
    if total >= 50000:  # 500 baht
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    # exact integer arithmetic, round half up once at the end
    return (total * num * 2 + den) // (den * 2)
