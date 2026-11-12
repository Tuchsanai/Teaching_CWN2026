def split_bill(total, people, tip_percent):
    """หารบิลของ BaanKafe.

    total       : ยอดบิลเป็นสตางค์ (>= 0)
    people      : จำนวนคน (>= 1)
    tip_percent : ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0–100)

    คืน list ของยอดที่แต่ละคนจ่าย (จำนวนเต็มสตางค์) เรียงตามลำดับคน
    คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์เมื่อหารไม่ลงตัว
    """
    if total < 0:
        raise ValueError("total must be >= 0")
    if people < 1:
        raise ValueError("people must be >= 1")
    if not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be between 0 and 100")

    # ทิปเป็นสตางค์แบบจำนวนเต็ม (ปัดลง) เพื่อให้ผลรวมเป็นจำนวนเต็มเสมอ
    tip = total * tip_percent // 100
    amount = total + tip

    base, remainder = divmod(amount, people)
    return [base + 1 if i < remainder else base for i in range(people)]


if __name__ == "__main__":
    print(split_bill(10000, 3, 10))  # ยอด 11000 หาร 3 -> [3667, 3667, 3666]
    print(split_bill(0, 4, 0))       # [0, 0, 0, 0]
