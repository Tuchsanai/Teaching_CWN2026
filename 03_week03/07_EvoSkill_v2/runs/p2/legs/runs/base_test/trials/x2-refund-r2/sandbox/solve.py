def refund(paid, used_percent, restock):
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)  # หน่วย: สตางค์ x 100
    den = 100
    if restock:
        num *= 7  # หัก 12.5% => เหลือ 7/8
        den *= 8
    return (2 * num + den) // (2 * den)  # ปัดครึ่งขึ้น ครั้งเดียวตอนท้าย
