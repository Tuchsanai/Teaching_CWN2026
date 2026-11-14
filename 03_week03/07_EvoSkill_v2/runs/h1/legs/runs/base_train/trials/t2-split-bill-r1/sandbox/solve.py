def split_bill(total, people, tip_percent):
    """หารบิลของร้าน BaanKafe

    total       -- ยอดบิลเป็นสตางค์ (จำนวนเต็ม >= 0)
    people      -- จำนวนคน (จำนวนเต็ม >= 1)
    tip_percent -- ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0-100)

    คืน list ของยอดที่แต่ละคนจ่ายเป็นสตางค์ (จำนวนเต็ม) เรียงตามลำดับคน
    """
    if not isinstance(total, int) or total < 0:
        raise ValueError("total ต้องเป็นจำนวนเต็มตั้งแต่ 0")
    if not isinstance(people, int) or people < 1:
        raise ValueError("people ต้องเป็นจำนวนเต็มตั้งแต่ 1")
    if not isinstance(tip_percent, int) or not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent ต้องเป็นจำนวนเต็ม 0-100")

    # ยอดบิลบวกทิป ปัดเศษทิปเป็นสตางค์ที่ใกล้ที่สุด (ปัดขึ้นเมื่อเท่ากึ่งกลาง) ด้วยจำนวนเต็มล้วน
    tip = (total * tip_percent + 50) // 100
    amount = total + tip

    # หารเท่ากัน เศษสตางค์ให้คนลำดับแรก ๆ คนละ 1 สตางค์
    base, remainder = divmod(amount, people)
    return [base + 1 if i < remainder else base for i in range(people)]


if __name__ == "__main__":
    print(split_bill(10000, 3, 10))  # 11000 หารสาม -> [3667, 3667, 3666]
    print(split_bill(0, 4, 0))       # [0, 0, 0, 0]
    print(split_bill(2555, 2, 15))   # 2555 + 383 = 2938 -> [1469, 1469]
