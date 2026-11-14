def split_bill(total, people, tip_percent):
    """หารบิลของ BaanKafe

    total       : ยอดบิล (สตางค์, จำนวนเต็ม >= 0)
    people      : จำนวนคน (จำนวนเต็ม >= 1)
    tip_percent : ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0–100)

    คืน list ของยอดที่แต่ละคนจ่าย (สตางค์, จำนวนเต็ม) เรียงตามลำดับคน
    คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์เมื่อหารไม่ลงตัว
    """
    if total < 0:
        raise ValueError("total must be >= 0")
    if people < 1:
        raise ValueError("people must be >= 1")
    if not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be between 0 and 100")

    # ทิปเป็นจำนวนเต็มสตางค์ ปัดเศษแบบ half-up ด้วยจำนวนเต็มล้วน (ไม่ใช้ float)
    tip = (total * tip_percent + 50) // 100
    amount = total + tip

    base, extra = divmod(amount, people)
    # extra คนแรกจ่ายเพิ่ม 1 สตางค์
    return [base + 1 if i < extra else base for i in range(people)]


if __name__ == "__main__":
    assert split_bill(10000, 3, 10) == [3667, 3667, 3666]  # 11000 / 3
    assert split_bill(1000, 4, 0) == [250, 250, 250, 250]
    assert split_bill(0, 2, 50) == [0, 0]
    assert sum(split_bill(12345, 7, 15)) == 12345 + (12345 * 15 + 50) // 100
    print("ok")
