"""ค่าปรับการชำระเงินช้าของลูกค้าขายส่ง BaanKafe

กติกา
- amount    : ยอดค้างชำระ หน่วยเป็นสตางค์ (จำนวนเต็ม >= 0)
- days_late : จำนวนวันที่ชำระช้า (จำนวนเต็ม 0–365)
- ช้าไม่เกิน 3 วัน            -> ไม่คิดค่าปรับ
- ช้าเกิน 3 วัน               -> คิด 0.75% ของยอดค้างต่อวัน นับทุกวันที่ช้า (รวม 3 วันแรก)
- ค่าปรับสูงสุด               -> 15% ของยอดค้างชำระ
- ผลลัพธ์                     -> จำนวนเต็มสตางค์ (ปัดเศษแบบ half-up)

การคำนวณใช้จำนวนเต็มล้วนเพื่อหลีกเลี่ยงความคลาดเคลื่อนของทศนิยม (float)
"""

GRACE_DAYS = 3
DAILY_RATE_NUM = 75        # 0.75% = 75 / 10_000
DAILY_RATE_DEN = 10_000
CAP_NUM = 15               # 15% = 15 / 100
CAP_DEN = 100
MAX_DAYS = 365


def _round_div(numerator: int, denominator: int) -> int:
    """หารจำนวนเต็มที่ไม่เป็นลบ แล้วปัดเศษแบบ half-up"""
    return (2 * numerator + denominator) // (2 * denominator)


def late_fee(amount: int, days_late: int) -> int:
    """คืนค่าปรับเป็นจำนวนเต็มสตางค์

    >>> late_fee(10000, 3)
    0
    >>> late_fee(10000, 4)
    300
    >>> late_fee(10000, 30)
    1500
    """
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if isinstance(days_late, bool) or not isinstance(days_late, int):
        raise TypeError("days_late ต้องเป็นจำนวนเต็ม")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if not 0 <= days_late <= MAX_DAYS:
        raise ValueError(f"days_late ต้องอยู่ในช่วง 0–{MAX_DAYS}")

    if days_late <= GRACE_DAYS:
        return 0

    # ค่าปรับดิบ = amount * 0.75% * days_late
    fee = _round_div(amount * DAILY_RATE_NUM * days_late, DAILY_RATE_DEN)

    # เพดาน = 15% ของยอดค้างชำระ
    cap = _round_div(amount * CAP_NUM, CAP_DEN)

    return min(fee, cap)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
