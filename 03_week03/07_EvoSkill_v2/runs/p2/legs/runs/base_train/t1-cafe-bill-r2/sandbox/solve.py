def cafe_bill(items, member):
    """Return amount to pay in integer satang."""
    total = sum(i["price"] * i["qty"] for i in items)
    num, den = total, 1
    if total >= 50000:      # 500 baht or more -> 5% off
        num, den = num * 95, den * 100
    if member:              # member -> extra 10% off
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100   # VAT 7% last
    # exact integer arithmetic, round half up only once at the end
    return (2 * num + den) // (2 * den)
