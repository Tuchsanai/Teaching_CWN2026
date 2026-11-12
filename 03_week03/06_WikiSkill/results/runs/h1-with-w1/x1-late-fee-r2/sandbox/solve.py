"""ค่าปรับลูกค้าขายส่งที่ชำระเงินช้า (BaanKafe)

หน่วยเงินเป็นสตางค์ (จำนวนเต็ม) คำนวณด้วย Fraction และปัดเศษ half-up ครั้งเดียวตอนท้าย
"""
import json
import sys
from fractions import Fraction

GRACE_DAYS = 3          # ช้าไม่เกินนี้ไม่คิดค่าปรับ
DAILY_RATE = Fraction(75, 10000)   # 0.75% ต่อวัน
CAP_RATE = Fraction(15, 100)       # เพดาน 15% ของยอดค้างชำระ


def _int(x, name, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f'{name} must be int')
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f'{name} out of range')
    return x


def late_fee(amount, days_late):
    """คืนค่าปรับ (สตางค์, จำนวนเต็ม) ของยอดค้าง `amount` ที่ช้า `days_late` วัน"""
    amount = _int(amount, 'amount', lo=0)
    days_late = _int(days_late, 'days_late', lo=0, hi=365)

    if days_late <= GRACE_DAYS:
        return 0

    fee = amount * DAILY_RATE * days_late          # นับทุกวันที่ช้า รวม 3 วันแรก
    cap = amount * CAP_RATE
    fee = min(fee, cap)

    # ปัดครึ่งขึ้น (half-up) ครั้งเดียว
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
