from fractions import Fraction


def split_bill(total, people, tip_percent):
    """หารบิลของ BaanKafe

    total        : ยอดบิลเป็นสตางค์ (int, >= 0)
    people       : จำนวนคน (int, >= 1)
    tip_percent  : ทิปเป็นเปอร์เซ็นต์ (int, 0-100)

    คืน list[int] ยอดที่แต่ละคนจ่ายเป็นสตางค์ เรียงตามลำดับคน

    กติกาที่เลือกตีความ:
    - ทิป = ยอดบิล × tip_percent / 100 ปัดลง (ตัดเศษสตางค์ทิ้ง) ที่ขั้นสุดท้ายของทิป
    - ยอดที่ต้องหาร = ยอดบิล + ทิป
    - หารเท่ากัน เศษสตางค์ให้คนลำดับแรก ๆ คนละ 1 สตางค์
    """
    if not isinstance(total, int) or isinstance(total, bool) or total < 0:
        raise ValueError("total ต้องเป็นจำนวนเต็มสตางค์ตั้งแต่ 0 ขึ้นไป")
    if not isinstance(people, int) or isinstance(people, bool) or people < 1:
        raise ValueError("people ต้องเป็นจำนวนเต็มตั้งแต่ 1 ขึ้นไป")
    if not isinstance(tip_percent, int) or isinstance(tip_percent, bool) or not (0 <= tip_percent <= 100):
        raise ValueError("tip_percent ต้องเป็นจำนวนเต็มระหว่าง 0 ถึง 100")

    # ทิป: คำนวณเป็น Fraction แล้วปัดลงครั้งเดียวที่ขั้นสุดท้าย
    tip = (Fraction(total) * Fraction(tip_percent, 100)).__floor__()

    # ยอดที่ต้องหาร = ยอดบิล + ทิป
    amount = total + tip

    # หารให้ผลรวมตรงเป๊ะ คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์
    q, r = divmod(amount, people)
    shares = [q + 1 if i < r else q for i in range(people)]
    return shares


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    print(split_bill(10001, 3, 10))  # 10001 + ทิป 1000 = 11001 -> [3667, 3667, 3667]
    print(split_bill(1000, 3, 0))    # 1000 หาร 3 -> [334, 333, 333]
