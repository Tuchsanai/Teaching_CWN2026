"""คำนวณเงินคืนคอร์สสอนชงกาแฟ ของ BaanKafe.

หน่วยทั้งหมดเป็นสตางค์ (จำนวนเต็ม)
- paid: เงินที่ลูกค้าจ่ายมา (>= 0)
- used_percent: เปอร์เซ็นต์ที่เรียนไปแล้ว (จำนวนเต็ม 0-100)
- restock: True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
"""

FEE_NUMERATOR = 7      # ค่าดำเนินการ 12.5% => ยอดคืนคงเหลือ 87.5% = 7/8
FEE_DENOMINATOR = 8
FULL_REFUND_LIMIT = 80  # เรียนเกิน 80% ไม่คืนเงิน


def refund(paid: int, used_percent: int, restock: bool) -> int:
    """คืนจำนวนเงินที่ต้องคืนให้ลูกค้า (สตางค์, จำนวนเต็ม)

    ปัดเศษแบบปัดขึ้นเมื่อ .5 (round half up) ที่หน่วยสตางค์สุดท้าย
    """
    if isinstance(paid, bool) or not isinstance(paid, int) or paid < 0:
        raise ValueError("paid ต้องเป็นจำนวนเต็มสตางค์ที่ไม่ติดลบ")
    if isinstance(used_percent, bool) or not isinstance(used_percent, int) \
            or not 0 <= used_percent <= 100:
        raise ValueError("used_percent ต้องเป็นจำนวนเต็ม 0-100")

    # เรียนเกิน 80% ไม่คืนเงิน
    if used_percent > FULL_REFUND_LIMIT:
        return 0

    # ยอดตามสัดส่วนที่ยังไม่ได้เรียน = paid * (100 - used_percent) / 100
    # หักค่าดำเนินการ (restock) = คูณ 7/8 ; รวมเป็นตัวหาร 800 เพื่อคงความเป็นจำนวนเต็ม
    numerator = paid * (100 - used_percent)
    if restock:
        numerator *= FEE_NUMERATOR
        denominator = 100 * FEE_DENOMINATOR
    else:
        denominator = 100

    # ปัดเศษแบบ round half up ด้วยจำนวนเต็มล้วน
    return (numerator * 2 + denominator) // (denominator * 2)


if __name__ == "__main__":
    # ตัวอย่างการทดสอบอย่างง่าย
    assert refund(80000, 0, True) == 70000    # 800 บาท, ไม่ได้เรียน, หักค่าดำเนินการ -> 700 บาท
    assert refund(80000, 0, False) == 80000   # ไม่หักค่าดำเนินการ -> 800 บาท
    assert refund(80000, 50, False) == 40000  # เรียนไป 50% -> คืน 400 บาท
    assert refund(80000, 50, True) == 35000   # เรียนไป 50% หักค่าดำเนินการ -> 350 บาท
    assert refund(80000, 80, False) == 16000  # เกิน 80% ไม่ถึง -> ยังคืน 20%
    assert refund(80000, 81, False) == 0      # เกิน 80% ไม่คืนเงิน
    assert refund(80000, 100, True) == 0
    assert refund(0, 10, True) == 0
    assert refund(1, 0, True) == 1            # 1 สตางค์ * 0.875 = 0.875 -> ปัดเป็น 1
    assert refund(1, 0, False) == 1
    print("ทดสอบผ่านทั้งหมด")
