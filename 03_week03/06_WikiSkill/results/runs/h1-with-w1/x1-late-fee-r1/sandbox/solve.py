"""BaanKafe: คิดค่าปรับลูกค้าขายส่งที่ชำระเงินช้า

กฎ:
- ช้าไม่เกิน 3 วัน ไม่คิดค่าปรับ
- ช้าเกิน 3 วัน คิดวันละ 0.75% ของยอดค้างชำระ นับทุกวันที่ช้า (รวม 3 วันแรก)
- ค่าปรับสูงสุด 15% ของยอดค้างชำระ
- หน่วยเป็นสตางค์ (จำนวนเต็ม) ผลลัพธ์ปัดเศษแบบ half-up เป็นจำนวนเต็มสตางค์
"""

import json
import sys
from fractions import Fraction

RATE_PER_DAY = Fraction(3, 400)   # 0.75% = 3/400
CAP_RATE = Fraction(3, 20)        # 15% = 3/20
GRACE_DAYS = 3
MAX_DAYS = 365


def _int(x, name, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f'{name} must be int')
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f'{name} out of range')
    return x


def late_fee(amount, days_late):
    """คืนค่าปรับ (สตางค์, จำนวนเต็ม) ของยอดค้างชำระ `amount` ที่ช้า `days_late` วัน"""
    amount = _int(amount, 'amount', lo=0)
    days_late = _int(days_late, 'days_late', lo=0, hi=MAX_DAYS)

    if days_late <= GRACE_DAYS:
        return 0

    raw = amount * RATE_PER_DAY * days_late          # Fraction, ยังไม่ปัด
    cap = amount * CAP_RATE                          # เพดาน 15%
    fee = min(raw, cap)                              # เทียบเพดานก่อนปัด

    # ปัดครั้งเดียวแบบ half-up: floor(fee + 1/2)
    num, den = fee.numerator, fee.denominator
    return (2 * num + den) // (2 * den)


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
