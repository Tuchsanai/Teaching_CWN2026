def split_bill(total, people, tip_percent):
    """หารบิลของร้าน BaanKafe

    total       : ยอดบิลเป็นสตางค์ (>= 0)
    people      : จำนวนคน (>= 1)
    tip_percent : ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0-100)

    คืน list ของยอดที่แต่ละคนจ่าย (จำนวนเต็มสตางค์) เรียงตามลำดับคน
    """
    if not isinstance(total, int) or total < 0:
        raise ValueError("total must be a non-negative integer (satang)")
    if not isinstance(people, int) or people < 1:
        raise ValueError("people must be an integer >= 1")
    if not isinstance(tip_percent, int) or not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be an integer between 0 and 100")

    # ทิปคำนวณเป็นจำนวนเต็มสตางค์ ปัดเศษแบบปัดขึ้นเมื่อ .5 (ไม่ใช้ float)
    tip = (total * tip_percent + 50) // 100
    amount = total + tip

    base, remainder = divmod(amount, people)
    # คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์จนครบส่วนที่เหลือ
    return [base + 1 if i < remainder else base for i in range(people)]


if __name__ == "__main__":
    print(split_bill(10000, 3, 10))  # 11000 หาร 3 -> [3667, 3667, 3666]
    print(split_bill(999, 4, 0))     # -> [250, 250, 250, 249]
