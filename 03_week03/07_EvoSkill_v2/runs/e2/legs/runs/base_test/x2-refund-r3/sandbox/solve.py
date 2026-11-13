def refund(paid, used_percent, restock):
    """คืนเงินเป็นสตางค์ (จำนวนเต็ม) - คิดด้วยเลขจำนวนเต็ม ปัดเศษลงครั้งเดียวตอนท้าย"""
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    if restock:
        return num * 7 // 800   # หัก 12.5% => คูณ 7/8
    return num // 100
