"""คิดเงินคืนสำหรับคอร์สสอนชงกาแฟ ของร้าน BaanKafe

กติกา
- คืนเงินตามสัดส่วนของส่วนที่ยังไม่ได้เรียน
- ถ้าเรียนไปแล้วเกิน 80% ไม่คืนเงินเลย
- ถ้า restock=True จะหักค่าดำเนินการ 12.5% ของยอดที่จะคืน
- ผลลัพธ์เป็นจำนวนเต็มสตางค์ (ปัดทิ้งเศษสตางค์) คำนวณด้วยจำนวนเต็มล้วนเพื่อไม่ให้เกิดความคลาดเคลื่อนจากทศนิยม
"""


def refund(paid: int, used_percent: int, restock: bool) -> int:
    """คืนยอดเงินที่ต้องคืนให้ลูกค้า (หน่วยเป็นสตางค์ จำนวนเต็ม)

    paid          เงินที่ลูกค้าจ่ายมา (สตางค์, >= 0)
    used_percent  เปอร์เซ็นต์ที่เรียนไปแล้ว (จำนวนเต็ม 0-100)
    restock       True = หักค่าดำเนินการ 12.5%
    """
    if isinstance(paid, bool) or not isinstance(paid, int):
        raise TypeError("paid ต้องเป็นจำนวนเต็ม (สตางค์)")
    if paid < 0:
        raise ValueError("paid ต้องไม่ติดลบ")
    if isinstance(used_percent, bool) or not isinstance(used_percent, int):
        raise TypeError("used_percent ต้องเป็นจำนวนเต็ม")
    if not 0 <= used_percent <= 100:
        raise ValueError("used_percent ต้องอยู่ในช่วง 0-100")

    # เรียนเกิน 80% ไม่คืนเงิน
    if used_percent > 80:
        return 0

    unused = 100 - used_percent
    if restock:
        # ยอดคืนสุทธิ = paid * unused/100 * (1 - 12.5%) = paid * unused * 7 / 800
        return paid * unused * 7 // 800
    # ยอดคืนเต็ม = paid * unused / 100
    return paid * unused // 100


if __name__ == "__main__":
    assert refund(10000, 0, False) == 10000
    assert refund(10000, 0, True) == 8750      # หักค่าดำเนินการ 1250
    assert refund(10000, 50, False) == 5000
    assert refund(10000, 50, True) == 4375
    assert refund(10000, 80, False) == 2000    # เกิน 80% ไม่ได้ ตรง 80 ยังคืนได้
    assert refund(10000, 81, False) == 0
    assert refund(10000, 100, True) == 0
    assert refund(0, 0, True) == 0
    assert refund(999, 33, True) == 585        # 999*67*7/800 = 585.66... ปัดทิ้งเป็น 585
    print("ผ่านทุกเคส")
