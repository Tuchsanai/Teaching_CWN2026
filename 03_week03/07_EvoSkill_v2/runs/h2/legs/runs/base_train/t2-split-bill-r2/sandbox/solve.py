def split_bill(total, people, tip_percent):
    """หารบิลของร้าน BaanKafe

    total       : ยอดบิล (สตางค์, >= 0)
    people      : จำนวนคน (>= 1)
    tip_percent : ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0–100)

    คืน list ของยอดที่แต่ละคนจ่าย (จำนวนเต็มสตางค์) เรียงตามลำดับคน
    """
    if total < 0:
        raise ValueError("total must be >= 0")
    if people < 1:
        raise ValueError("people must be >= 1")
    if not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be between 0 and 100")

    # ทิปคิดเป็นสตางค์แบบจำนวนเต็ม (ปัดลง) เพื่อไม่ให้เกิดเศษทศนิยม
    tip = total * tip_percent // 100
    amount = total + tip

    # หารเท่ากัน ส่วนที่เหลือให้คนลำดับแรก ๆ คนละ 1 สตางค์
    base, remainder = divmod(amount, people)
    return [base + 1 if i < remainder else base for i in range(people)]


if __name__ == "__main__":
    assert split_bill(10000, 3, 0) == [3334, 3333, 3333]
    assert split_bill(10000, 4, 10) == [2750, 2750, 2750, 2750]
    assert split_bill(0, 5, 50) == [0, 0, 0, 0, 0]
    assert split_bill(12345, 1, 15) == [14196]
    assert sum(split_bill(9999, 7, 33)) == 9999 + 9999 * 33 // 100
    print("ok")
