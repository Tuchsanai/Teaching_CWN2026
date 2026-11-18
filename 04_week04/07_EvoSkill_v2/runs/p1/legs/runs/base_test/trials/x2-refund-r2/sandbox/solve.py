def refund(paid, used_percent, restock):
    """คืนเงินคอร์ส (หน่วยสตางค์) เป็นจำนวนเต็ม ใช้เลขจำนวนเต็มล้วน ไม่มีปัญหา float"""
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)  # หาร 100 = ยอดตามสัดส่วน
    den = 100
    if restock:
        num *= 7  # หัก 12.5% => คงเหลือ 87.5% = 7/8
        den *= 8
    # ปัดครึ่งขึ้น (round half up) ที่ขั้นตอนสุดท้ายครั้งเดียว
    return (2 * num + den) // (2 * den)
