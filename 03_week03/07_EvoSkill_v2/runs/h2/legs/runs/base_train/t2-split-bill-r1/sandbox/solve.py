def split_bill(total, people, tip_percent):
    """หารบิลของร้าน BaanKafe

    total       ยอดบิล (สตางค์ ตั้งแต่ 0)
    people      จำนวนคน (ตั้งแต่ 1)
    tip_percent ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0-100)

    คืน list ของยอดที่แต่ละคนจ่าย (จำนวนเต็มสตางค์) เรียงตามลำดับคน
    """
    if total < 0:
        raise ValueError("total must be >= 0")
    if people < 1:
        raise ValueError("people must be >= 1")
    if not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be between 0 and 100")

    # ยอดที่ต้องหาร = ยอดบิล + ทิป ใช้จำนวนเต็มล้วน ปัดเศษแบบ half-up ให้เป็นสตางค์
    amount = (total * (100 + tip_percent) + 50) // 100

    base, remainder = divmod(amount, people)
    # คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์ จนครบส่วนที่เหลือ
    return [base + 1 if i < remainder else base for i in range(people)]


if __name__ == "__main__":
    print(split_bill(10000, 3, 10))  # 11000 หาร 3 -> [3667, 3667, 3666]
    print(split_bill(0, 4, 0))       # [0, 0, 0, 0]
