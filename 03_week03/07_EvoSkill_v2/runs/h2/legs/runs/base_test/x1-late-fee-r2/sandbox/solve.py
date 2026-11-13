"""ค่าปรับการชำระเงินล่าช้าของลูกค้าขายส่ง BaanKafe

กฎ:
- ช้าไม่เกิน 3 วัน ไม่คิดค่าปรับ
- ช้าเกิน 3 วัน คิดค่าปรับวันละ 0.75% ของยอดค้างชำระ นับทุกวันที่ช้า (รวม 3 วันแรก)
- ค่าปรับสูงสุด 15% ของยอดค้างชำระ
- ผลลัพธ์เป็นจำนวนเต็มสตางค์

การคำนวณใช้จำนวนเต็มล้วน (ไม่ใช้ float) เพื่อหลีกเลี่ยงความคลาดเคลื่อนของทศนิยม
การปัดเศษ: ปัดครึ่งขึ้น (half up) ไปยังสตางค์ที่ใกล้ที่สุด
"""

# 0.75% = 75 / 10000, 15% = 1500 / 10000
_DAILY_RATE_NUM = 75
_CAP_RATE_NUM = 1500
_RATE_DEN = 10000
_GRACE_DAYS = 3


def late_fee(amount: int, days_late: int) -> int:
    """คืนค่าปรับ (สตางค์, จำนวนเต็ม) สำหรับยอดค้างชำระ `amount` ที่ช้า `days_late` วัน"""
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if isinstance(days_late, bool) or not isinstance(days_late, int):
        raise TypeError("days_late ต้องเป็นจำนวนเต็ม")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if not 0 <= days_late <= 365:
        raise ValueError("days_late ต้องอยู่ระหว่าง 0 ถึง 365")

    if days_late <= _GRACE_DAYS:
        return 0

    # ค่าปรับดิบ (ตัวเศษ เทียบกับตัวหาร _RATE_DEN) และเพดาน 15%
    raw = amount * _DAILY_RATE_NUM * days_late
    cap = amount * _CAP_RATE_NUM
    fee_num = min(raw, cap)

    # ปัดครึ่งขึ้นเป็นสตางค์
    return (fee_num + _RATE_DEN // 2) // _RATE_DEN


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    print(late_fee(100_000, 3))   # 0      (ไม่เกิน 3 วัน)
    print(late_fee(100_000, 4))   # 3000   (0.75% x 4 วัน = 3%)
    print(late_fee(100_000, 10))  # 7500   (0.75% x 10 วัน = 7.5%)
    print(late_fee(100_000, 30))  # 15000  (ถึงเพดาน 15%)
    print(late_fee(100_000, 365)) # 15000  (ถึงเพดาน 15%)
    print(late_fee(333, 5))       # 12     (333 x 3.75% = 12.4875 -> 12)
    print(late_fee(0, 100))       # 0
