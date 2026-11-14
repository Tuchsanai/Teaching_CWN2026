def refund(paid, used_percent, restock):
    if used_percent > 80:
        return 0
    # คิดด้วยจำนวนเต็มล้วนเพื่อเลี่ยงปัญหา float; ปัดครึ่งขึ้น
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        num *= 875   # หัก 12.5% => เหลือ 87.5% = 875/1000
        den *= 1000
    return (2 * num + den) // (2 * den)
