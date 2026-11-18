def split_bill(total, people, tip_percent):
    """หารบิลของร้าน BaanKafe

    total        : ยอดบิลเป็นสตางค์ (จำนวนเต็ม >= 0)
    people       : จำนวนคน (จำนวนเต็ม >= 1)
    tip_percent  : ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0-100)

    คืน list ของยอดที่แต่ละคนจ่ายเป็นสตางค์ (จำนวนเต็ม) เรียงตามลำดับคน
    ทิปที่เป็นเศษสตางค์จะปัดลง (ไม่เกินเปอร์เซ็นต์ที่กำหนด)
    เศษสตางค์จากการหารจะให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์
    """
    if not isinstance(total, int) or isinstance(total, bool) or total < 0:
        raise ValueError("total ต้องเป็นจำนวนเต็มสตางค์ที่ >= 0")
    if not isinstance(people, int) or isinstance(people, bool) or people < 1:
        raise ValueError("people ต้องเป็นจำนวนเต็มที่ >= 1")
    if (not isinstance(tip_percent, int) or isinstance(tip_percent, bool)
            or not 0 <= tip_percent <= 100):
        raise ValueError("tip_percent ต้องเป็นจำนวนเต็ม 0-100")

    amount = total + (total * tip_percent) // 100
    base, remainder = divmod(amount, people)
    return [base + 1 if i < remainder else base for i in range(people)]


if __name__ == "__main__":
    assert split_bill(10000, 3, 0) == [3334, 3333, 3333]
    assert split_bill(10000, 4, 10) == [2750, 2750, 2750, 2750]
    assert split_bill(0, 2, 50) == [0, 0]
    assert split_bill(999, 1, 15) == [1148]
    assert sum(split_bill(12345, 7, 13)) == 12345 + (12345 * 13) // 100
    print("ผ่านทุกเคสทดสอบ")
