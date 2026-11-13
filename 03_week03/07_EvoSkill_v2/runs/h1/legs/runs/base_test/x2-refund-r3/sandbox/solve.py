"""คิดเงินคืนคอร์สสอนชงกาแฟ BaanKafe

หน่วยเงินทั้งหมดเป็นสตางค์ (จำนวนเต็ม)
"""

REFUND_CUTOFF_PERCENT = 80   # เรียนไปแล้วเกินค่านี้ ไม่คืนเงิน
RESTOCK_FEE_NUM = 1          # ค่าดำเนินการ 12.5% = 1/8 ของยอดที่จะคืน
RESTOCK_FEE_DEN = 8


def refund(paid: int, used_percent: int, restock: bool) -> int:
    """คืนจำนวนเงินที่ต้องคืนลูกค้า (สตางค์, จำนวนเต็ม)

    paid          -- เงินที่ลูกค้าจ่ายมา (สตางค์, >= 0)
    used_percent  -- เปอร์เซ็นต์ที่เรียนไปแล้ว (จำนวนเต็ม 0-100)
    restock       -- True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
    """
    if isinstance(paid, bool) or not isinstance(paid, int) or paid < 0:
        raise ValueError("paid ต้องเป็นจำนวนเต็มสตางค์ที่ >= 0")
    if isinstance(used_percent, bool) or not isinstance(used_percent, int) \
            or not 0 <= used_percent <= 100:
        raise ValueError("used_percent ต้องเป็นจำนวนเต็ม 0-100")

    # เรียนไปแล้วเกิน 80% ไม่คืนเงิน
    if used_percent > REFUND_CUTOFF_PERCENT:
        return 0

    # ยอดคืนตามสัดส่วนที่ยังไม่ได้เรียน = paid * (100 - used) / 100
    # หากหักค่าดำเนินการ คูณด้วย (1 - 1/8) = 7/8 เพิ่ม
    # รวมเป็นตัวหาร 100 * 8 = 800 เพื่อคำนวณด้วยจำนวนเต็มล้วนและปัดเศษครั้งเดียวตอนท้าย
    numerator = paid * (100 - used_percent) * 8
    if restock:
        numerator = numerator * (RESTOCK_FEE_DEN - RESTOCK_FEE_NUM)  # * 7
        denominator = 100 * RESTOCK_FEE_DEN * RESTOCK_FEE_DEN        # 6400
    else:
        denominator = 100 * RESTOCK_FEE_DEN                          # 800

    # ปัดเศษแบบ round half up ให้เป็นจำนวนเต็มสตางค์
    return (2 * numerator + denominator) // (2 * denominator)


if __name__ == "__main__":
    # ตัวอย่าง/ทดสอบอย่างง่าย
    assert refund(10000, 0, False) == 10000   # ยังไม่เรียนเลย คืนเต็ม
    assert refund(10000, 20, False) == 8000   # เรียนไป 20% คืน 80%
    assert refund(10000, 20, True) == 7000    # หัก 12.5% ของ 8000 = 1000 -> 7000
    assert refund(10000, 80, False) == 2000   # ถึง 80% ยังคืนได้
    assert refund(10000, 81, False) == 0      # เกิน 80% ไม่คืน
    assert refund(10000, 100, True) == 0
    assert refund(0, 10, True) == 0
    assert refund(1001, 0, True) == 876       # 1001 * 7/8 = 875.875 -> 876
    print("ผ่านทุกเคส")
