"""ค่าปรับการชำระเงินช้าของลูกค้าขายส่ง BaanKafe (หน่วยเป็นสตางค์ จำนวนเต็ม)

กติกา
- ช้าไม่เกิน 3 วัน ไม่คิดค่าปรับ
- ช้าเกิน 3 วัน คิดวันละ 0.75% ของยอดค้างชำระ นับทุกวันที่ช้า (รวม 3 วันแรก)
- ค่าปรับสูงสุด 15% ของยอดค้างชำระ
- คืนค่าปรับเป็นจำนวนเต็มสตางค์ (ปัดแบบ half-up ครั้งเดียวตอนท้าย)
"""

import json
import sys
from fractions import Fraction

GRACE_DAYS = 3
DAILY_RATE = Fraction(75, 10000)   # 0.75% ต่อวัน
CAP_RATE = Fraction(15, 100)       # 15% สูงสุด
MAX_DAYS = 365


def _int(x, name, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f'{name} must be int')
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f'{name} out of range')
    return x


def _round_half_up(fr):
    """ปัดเศษ Fraction (ไม่ติดลบ) เป็นจำนวนเต็มแบบ half-up"""
    return (2 * fr.numerator + fr.denominator) // (2 * fr.denominator)


def late_fee(amount, days_late):
    """คืนค่าปรับ (สตางค์, จำนวนเต็ม) ของยอดค้างชำระ amount ที่ชำระช้า days_late วัน"""
    amount = _int(amount, 'amount', lo=0)
    days_late = _int(days_late, 'days_late', lo=0, hi=MAX_DAYS)

    if days_late <= GRACE_DAYS:
        return 0

    raw = Fraction(amount) * DAILY_RATE * days_late      # ยังไม่ปัด
    cap = Fraction(amount) * CAP_RATE                    # เพดาน (ยังไม่ปัด)
    fee = min(raw, cap)
    return _round_half_up(fee)


def main():
    try:
        data = json.loads(sys.stdin.read())
        result = late_fee(data['amount'], data['days_late'])
    except (ValueError, KeyError, TypeError) as e:
        print(json.dumps({'ok': False, 'error': str(e)}))
        return 2
    print(json.dumps({'ok': True, 'result': result}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
