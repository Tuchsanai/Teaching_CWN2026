def refund(paid, used_percent, restock):
    """คืนเงินคอร์ส (หน่วยสตางค์, จำนวนเต็ม)

    - คืนตามสัดส่วนที่ยังไม่ได้เรียน
    - เรียนเกิน 80% ไม่คืน
    - restock=True หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
    ใช้เลขจำนวนเต็มล้วนเพื่อเลี่ยงปัญหาทศนิยม ปัดครึ่งขึ้นเมื่อเศษสตางค์
    """
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        num *= 875  # คงเหลือ 87.5%
        den *= 1000
    return (2 * num + den) // (2 * den)  # round half up
