def refund(paid, used_percent, restock):
    """คืนเงินคอร์ส (หน่วยสตางค์ เป็นจำนวนเต็ม) ปัดเศษลง"""
    if used_percent > 80:
        return 0
    # สัดส่วนที่ยังไม่ได้เรียน = (100 - used)/100 ; หลังหักค่าดำเนินการ 12.5% = x 7/8
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        num *= 7
        den *= 8
    return num // den
