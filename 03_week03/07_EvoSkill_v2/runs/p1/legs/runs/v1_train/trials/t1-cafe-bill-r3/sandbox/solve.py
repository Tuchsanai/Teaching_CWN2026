def cafe_bill(items, member):
    total = sum(i["price"] * i["qty"] for i in items)
    if total >= 50000:
        total = total * 95 // 100
    if member:
        total = total * 90 // 100
    return total * 107 // 100
