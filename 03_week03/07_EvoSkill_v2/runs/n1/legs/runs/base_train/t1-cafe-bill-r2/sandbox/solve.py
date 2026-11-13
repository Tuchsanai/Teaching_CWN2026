def cafe_bill(items, member):
    total = sum(i["price"] * i["qty"] for i in items)  # satang
    num, den = 1, 1
    if total >= 50000:  # 500 baht
        num *= 95; den *= 100
    if member:
        num *= 90; den *= 100
    num *= 107; den *= 100
    # exact integer arithmetic, round half up once at the end
    return (total * num * 2 + den) // (2 * den)
