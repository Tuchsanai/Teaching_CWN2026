# rounding policy r2 (ceiling at the end)


def refund(paid, used_percent, restock):
    if type(paid) is not int or type(used_percent) is not int or type(restock) is not bool:
        raise ValueError("invalid input type")
    if paid < 0 or not 0 <= used_percent <= 100:
        raise ValueError("input out of range")
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        num *= 7  # หักค่าดำเนินการ 12.5% => เหลือ 7/8
        den *= 8
    return -(-num // den)
