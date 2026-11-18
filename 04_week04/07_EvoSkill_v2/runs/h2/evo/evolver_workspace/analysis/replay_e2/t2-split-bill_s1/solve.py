"""หารบิลร้าน BaanKafe

ยอดทั้งหมดเป็นสตางค์ (จำนวนเต็ม) ไม่มี float ในการคำนวณเงิน
"""
import math
from fractions import Fraction


def _need_int(value, name, low=None, high=None):
    """จำนวนเต็มจริง: ไม่รับ bool, float, str และตรวจช่วงตามที่ระบุ"""
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    if high is not None and value > high:
        raise ValueError(f"{name} ต้องไม่เกิน {high}")
    return value


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ): 2.5 -> 3, 2.4 -> 2"""
    return math.floor(Fraction(x) + Fraction(1, 2))


def split_bill(total, people, tip_percent):
    """หารบิลให้ people คน หลังบวกทิป

    total        ยอดบิลเป็นสตางค์ (จำนวนเต็ม >= 0)
    people       จำนวนคน (จำนวนเต็ม >= 1)
    tip_percent  ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0-100)

    คืน list ของยอดที่แต่ละคนจ่ายเป็นสตางค์ เรียงตามลำดับคน
    คนลำดับต้น ๆ จ่ายเพิ่มคนละ 1 สตางค์เมื่อหารไม่ลงตัว
    """
    _need_int(total, "total", low=0)
    _need_int(people, "people", low=1)
    _need_int(tip_percent, "tip_percent", low=0, high=100)

    # ทิปเป็นเงินที่ลูกค้าจ่ายเข้าร้าน จึงปัดครึ่งขึ้น และปัดครั้งเดียวตรงนี้
    tip = _half_up(Fraction(total * tip_percent, 100))
    amount = total + tip

    base, rem = divmod(amount, people)
    return [base + 1] * rem + [base] * (people - rem)


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน: บิล 100.00 บาท ทิป 10% หาร 3 คน
    print(split_bill(10000, 3, 10))
