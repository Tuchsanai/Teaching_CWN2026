def split_bill(total, people, tip_percent):
    """หารบิลของร้าน BaanKafe

    total        : ยอดบิลเป็นสตางค์ (จำนวนเต็ม >= 0)
    people       : จำนวนคน (จำนวนเต็ม >= 1)
    tip_percent  : ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0–100)

    คืน list ของยอดที่แต่ละคนจ่ายเป็นสตางค์ (จำนวนเต็ม) เรียงตามลำดับคน
    """
    if not isinstance(total, int) or isinstance(total, bool) or total < 0:
        raise ValueError("total must be a non-negative integer (satang)")
    if not isinstance(people, int) or isinstance(people, bool) or people < 1:
        raise ValueError("people must be an integer >= 1")
    if not isinstance(tip_percent, int) or isinstance(tip_percent, bool) \
            or not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be an integer in 0..100")

    # ทิปคำนวณด้วยจำนวนเต็มล้วน ปัดครึ่งขึ้นเป็นสตางค์ที่ใกล้ที่สุด
    tip = (total * tip_percent + 50) // 100
    amount = total + tip

    # หารเท่ากัน เศษสตางค์ให้คนลำดับแรก ๆ คนละ 1 สตางค์
    base, remainder = divmod(amount, people)
    return [base + 1 if i < remainder else base for i in range(people)]


if __name__ == "__main__":
    print(split_bill(10000, 3, 10))  # 11000 / 3 -> [3667, 3667, 3666]
