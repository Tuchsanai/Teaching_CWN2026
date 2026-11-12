def cafe_bill(items, member):
    subtotal = sum(i["price"] * i["qty"] for i in items)  # satang
    num, den = subtotal, 1
    if subtotal >= 50000:  # 500 baht
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100  # VAT last
    return (2 * num + den) // (2 * den)  # round half up, once, at the end
