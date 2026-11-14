def refund(paid, used_percent, restock):
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        num *= 875  # หักค่าดำเนินการ 12.5%
        den *= 1000
    # ปัดครั้งเดียวตอนท้าย (half up) ด้วยเลขจำนวนเต็ม
    return (2 * num + den) // (2 * den)
