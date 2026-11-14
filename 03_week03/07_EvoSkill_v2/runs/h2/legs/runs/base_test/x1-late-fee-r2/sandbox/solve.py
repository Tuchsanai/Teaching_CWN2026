"""ค่าปรับการชำระเงินล่าช้าของลูกค้าขายส่ง BaanKafe

กติกา
- amount   : ยอดค้างชำระ หน่วยเป็นสตางค์ (จำนวนเต็ม >= 0)
- days_late: จำนวนวันที่ชำระช้า (จำนวนเต็ม 0–365)
- ช้าไม่เกิน 3 วัน ไม่คิดค่าปรับ
- ช้าเกิน 3 วัน คิดวันละ 0.75% ของยอดค้างชำระ นับทุกวันที่ช้า (รวม 3 วันแรก)
- ค่าปรับสูงสุดไม่เกิน 15% ของยอดค้างชำระ
- ผลลัพธ์เป็นจำนวนเต็มสตางค์ (ปัดเศษแบบ half-up)

คำนวณด้วยจำนวนเต็มล้วนเพื่อหลีกเลี่ยงความคลาดเคลื่อนของ float
อัตรา 0.75% = 75/10000, เพดาน 15% = 1500/10000
"""

GRACE_DAYS = 3
DAILY_RATE_BP = 75      # 0.75% ต่อวัน หน่วยเป็น basis point ของ 1/10000
MAX_RATE_BP = 1500      # 15% หน่วยเป็น basis point ของ 1/10000
MAX_DAYS = 365


def late_fee(amount: int, days_late: int) -> int:
    """คืนค่าปรับเป็นจำนวนเต็มสตางค์"""
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if isinstance(days_late, bool) or not isinstance(days_late, int):
        raise TypeError("days_late ต้องเป็นจำนวนเต็ม")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if not 0 <= days_late <= MAX_DAYS:
        raise ValueError(f"days_late ต้องอยู่ระหว่าง 0 ถึง {MAX_DAYS}")

    if days_late <= GRACE_DAYS:
        return 0

    # อัตราที่ใช้จริงหลังติดเพดาน: min(0.75% * วันที่ช้า, 15%)
    rate_bp = min(DAILY_RATE_BP * days_late, MAX_RATE_BP)

    # ปัดเศษครึ่งขึ้น: floor((amount * rate_bp + 5000) / 10000)
    return (amount * rate_bp + 5000) // 10000
