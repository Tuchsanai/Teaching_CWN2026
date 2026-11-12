"""คำนวณเงินคืนคอร์สสอนชงกาแฟ ของร้าน BaanKafe

หน่วยทั้งหมดเป็นสตางค์ (จำนวนเต็ม) เพื่อหลีกเลี่ยงปัญหาทศนิยมของ float
"""

REFUND_CUTOFF_PERCENT = 80   # เรียนไปเกินค่านี้ (มากกว่า 80%) ไม่คืนเงิน
HANDLING_FEE_NUMERATOR = 125  # ค่าดำเนินการ 12.5% = 125/1000
HANDLING_FEE_DENOMINATOR = 1000


def refund(paid: int, used_percent: int, restock: bool) -> int:
    """คืนจำนวนเงิน (สตางค์, จำนวนเต็ม) ที่ต้องคืนให้ลูกค้า

    paid         -- เงินที่ลูกค้าจ่าย (สตางค์, >= 0)
    used_percent -- เปอร์เซ็นต์ที่เรียนไปแล้ว (จำนวนเต็ม 0-100)
    restock      -- True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน

    ผลลัพธ์ปัดเศษลง (floor) ทุกขั้นตอนเหลือเฉพาะจำนวนเต็มสตางค์
    """
    if isinstance(paid, bool) or not isinstance(paid, int) or paid < 0:
        raise ValueError("paid ต้องเป็นจำนวนเต็มสตางค์ที่ >= 0")
    if isinstance(used_percent, bool) or not isinstance(used_percent, int) \
            or not 0 <= used_percent <= 100:
        raise ValueError("used_percent ต้องเป็นจำนวนเต็ม 0-100")

    if used_percent > REFUND_CUTOFF_PERCENT:
        return 0

    # ยอดตามสัดส่วนที่ยังไม่ได้เรียน = paid * (100 - used_percent) / 100
    # เก็บเป็นตัวตั้ง (ยังไม่หาร 100) เพื่อคงความแม่นยำของจำนวนเต็ม
    scaled = paid * (100 - used_percent)

    if restock:
        # หักค่าดำเนินการ 12.5%: เหลือ 87.5% = 7/8 ของยอด
        # ยอด = scaled / 100 * (1 - 125/1000) = scaled * 875 / 100000
        return scaled * (HANDLING_FEE_DENOMINATOR - HANDLING_FEE_NUMERATOR) \
            // (100 * HANDLING_FEE_DENOMINATOR)

    return scaled // 100


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    print(refund(100000, 0, False))   # 100000 (ยังไม่เรียนเลย ไม่หักค่าดำเนินการ)
    print(refund(100000, 0, True))    # 87500  (หักค่าดำเนินการ 12.5%)
    print(refund(100000, 30, False))  # 70000
    print(refund(100000, 30, True))   # 61250
    print(refund(100000, 80, True))   # 17500  (80% ยังคืนได้: 20000 - 12.5%)
    print(refund(100000, 81, True))   # 0
