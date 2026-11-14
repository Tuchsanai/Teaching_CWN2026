"""คิดเงินคืนสำหรับคอร์สสอนชงกาแฟของ BaanKafe.

หน่วยเงินทั้งหมดเป็นสตางค์ (จำนวนเต็ม)
"""

REFUND_CUTOFF_PERCENT = 80  # เรียนไปแล้วเกินค่านี้ ไม่คืนเงิน
RESTOCK_FEE_NUMERATOR = 1   # ค่าดำเนินการ 12.5% = 1/8 ของยอดที่จะคืน
RESTOCK_FEE_DENOMINATOR = 8


def refund(paid: int, used_percent: int, restock: bool) -> int:
    """คืนจำนวนเงินที่ต้องคืนลูกค้า (สตางค์, จำนวนเต็ม).

    paid         -- เงินที่ลูกค้าจ่ายมา (สตางค์, >= 0)
    used_percent -- เปอร์เซ็นต์ที่เรียนไปแล้ว (จำนวนเต็ม 0-100)
    restock      -- True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน

    กติกา:
      1. คืนตามสัดส่วนที่ยังไม่ได้เรียน: paid * (100 - used_percent) / 100
      2. ถ้า used_percent > 80 ไม่คืนเงินเลย
      3. ถ้า restock เป็น True หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
      4. ผลลัพธ์ปัดลงเป็นจำนวนเต็มสตางค์ (ไม่คืนเกินที่ควรคืน)
    """
    if isinstance(paid, bool) or not isinstance(paid, int):
        raise TypeError("paid ต้องเป็นจำนวนเต็ม (สตางค์)")
    if paid < 0:
        raise ValueError("paid ต้องไม่ติดลบ")
    if isinstance(used_percent, bool) or not isinstance(used_percent, int):
        raise TypeError("used_percent ต้องเป็นจำนวนเต็ม")
    if not 0 <= used_percent <= 100:
        raise ValueError("used_percent ต้องอยู่ระหว่าง 0 ถึง 100")

    if used_percent > REFUND_CUTOFF_PERCENT:
        return 0

    # คำนวณด้วยจำนวนเต็มล้วนเพื่อหลีกเลี่ยงข้อผิดพลาดของทศนิยม
    # ยอดคืนก่อนหักค่าดำเนินการ = paid * (100 - used) / 100
    # ถ้าหักค่าดำเนินการ        = ยอดนั้น * 7 / 8
    # รวมเป็นตัวหาร 800 (= 100 * 8)
    if restock:
        numerator = paid * (100 - used_percent) * (RESTOCK_FEE_DENOMINATOR - RESTOCK_FEE_NUMERATOR)
        denominator = 100 * RESTOCK_FEE_DENOMINATOR
    else:
        numerator = paid * (100 - used_percent)
        denominator = 100

    return numerator // denominator
