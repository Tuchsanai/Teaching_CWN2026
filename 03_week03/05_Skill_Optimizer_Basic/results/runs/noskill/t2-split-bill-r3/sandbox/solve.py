def split_bill(total, people, tip_percent):
    """หารบิลระหว่าง``people`` คน คืน list ยอดจ่ายของแต่ละคน (สตางค์)

    ยอดรวม = total + ทิป โดยทิปปัดเศษครึ่งขึ้นเป็นสตางค์ (ใช้จำนวนเต็มล้วน)
    ถ้าหารไม่ลงตัว คนแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์
    """
    if total < 0:
        raise ValueError("total must be >= 0")
    if people < 1:
        raise ValueError("people must be >= 1")
    if not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be between 0 and 100")

    tip = (total * tip_percent * 2 + 100) // 200  # round half up
    grand = total + tip
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
