def refund(paid, used_percent, restock):
    """คืนเงินเป็นจำนวนเต็มสตางค์ (ปัดลง เพื่อไม่คืนเกินสิทธิ์)

    - คืนตามสัดส่วนที่ยังไม่ได้เรียน
    - เรียนเกิน 80% ไม่คืน
    - restock=True หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
    ใช้เลขจำนวนเต็มล้วนเพื่อเลี่ยงความคลาดเคลื่อนของ float
    """
    if used_percent > 80:
        return 0
    amount = paid * (100 - used_percent)  # หน่วย: สตางค์ x 100
    if restock:
        return amount * 7 // 800  # x 0.875 / 100
    return amount // 100
