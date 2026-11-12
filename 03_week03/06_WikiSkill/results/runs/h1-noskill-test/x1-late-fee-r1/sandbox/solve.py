"""ค่าปรับลูกค้าขายส่งที่ชำระเงินช้า (BaanKafe)

กฎ:
- amount    = ยอดค้างชำระ หน่วยเป็นสตางค์ (จำนวนเต็ม >= 0)
- days_late = จำนวนวันที่ชำระช้า (จำนวนเต็ม 0-365)
- ช้าไม่เกิน 3 วัน: ไม่คิดค่าปรับ
- ช้าเกิน 3 วัน: คิดวันละ 0.75% ของยอดค้างชำระ นับทุกวันที่ช้า (รวม 3 วันแรก)
- ค่าปรับสูงสุดไม่เกิน 15% ของยอดค้างชำระ
- ผลลัพธ์เป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้น)

คำนวณด้วยจำนวนเต็มล้วนเพื่อหลีกเลี่ยงความคลาดเคลื่อนของทศนิยม
0.75% = 75 / 10000, 15% = 15 / 100
"""

GRACE_DAYS = 3
MAX_DAYS = 365
DAILY_RATE_NUM = 75        # 0.75%  = 75 / 10000
DAILY_RATE_DEN = 10000
CAP_NUM = 15               # 15%    = 15 / 100
CAP_DEN = 100


def late_fee(amount: int, days_late: int) -> int:
    """คืนค่าปรับ (สตางค์, จำนวนเต็ม) ของยอดค้างชำระ amount ที่ชำระช้า days_late วัน"""
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if isinstance(days_late, bool) or not isinstance(days_late, int):
        raise TypeError("days_late ต้องเป็นจำนวนเต็ม")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if not 0 <= days_late <= MAX_DAYS:
        raise ValueError(f"days_late ต้องอยู่ในช่วง 0-{MAX_DAYS}")

    # ช้าไม่เกิน 3 วัน ไม่คิดค่าปรับ
    if days_late <= GRACE_DAYS:
        return 0

    # ค่าปรับดิบ = amount * 0.75% * days_late, ปัดครึ่งขึ้นเป็นจำนวนเต็ม
    numerator = amount * DAILY_RATE_NUM * days_late
    fee = (numerator + DAILY_RATE_DEN // 2) // DAILY_RATE_DEN

    # เพดาน 15% ของยอดค้างชำระ (ผลลัพธ์เป็นจำนวนเต็ม จึงใช้ floor ได้โดยไม่เปลี่ยนความหมาย)
    cap = amount * CAP_NUM // CAP_DEN
    return min(fee, cap)


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน: ยอดค้าง 1,000 บาท = 100,000 สตางค์
    for days in (0, 3, 4, 10, 20, 21, 365):
        print(f"days_late={days:>3}  fee={late_fee(100_000, days)} สตางค์")
