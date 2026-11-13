def refund(paid, used_percent, restock):
    if used_percent > 80:
        return 0
    # คืนตามสัดส่วนที่ยังไม่ได้เรียน; หักค่าดำเนินการ 12.5% (= คูณ 7/8) ด้วยเลขจำนวนเต็มล้วน
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        num *= 7
        den *= 8
    return (2 * num + den) // (2 * den)  # ปัดครึ่งขึ้น
