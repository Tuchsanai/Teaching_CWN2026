"""BaanKafe: คิดเงินคืนของคอร์สสอนชงกาแฟ

หน่วยเงินเป็นสตางค์ (จำนวนเต็ม) ทั้งหมด
- paid: เงินที่ลูกค้าจ่ายมา (สตางค์ ตั้งแต่ 0)
- used_percent: เรียนไปแล้วกี่เปอร์เซ็นต์ (จำนวนเต็ม 0-100)
- restock: True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน

กฎ:
- คืนตามสัดส่วนที่ยังไม่ได้เรียน: paid * (100 - used_percent) / 100
- เรียนไปแล้วเกิน 80% ไม่คืนเงิน (คืน 0)
- ถ้า restock=True หักค่าดำเนินการ 12.5% ของยอดที่จะคืน (คงเหลือ 7/8)
- ปัดเศษแบบ half-up ครั้งเดียวตอนท้าย ด้วยจำนวนเต็มล้วน (ไม่ใช้ float)
"""

import json
import sys
from fractions import Fraction


def _int(x, name, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f'{name} must be int')
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f'{name} out of range')
    return x


def _bool(x, name):
    if not isinstance(x, bool):
        raise ValueError(f'{name} must be bool')
    return x


def refund(paid, used_percent, restock):
    """คืนค่าเงินคืนลูกค้าเป็นจำนวนเต็มสตางค์"""
    paid = _int(paid, 'paid', lo=0)
    used_percent = _int(used_percent, 'used_percent', lo=0, hi=100)
    restock = _bool(restock, 'restock')

    if used_percent > 80:
        return 0

    # คิดเป็นเศษส่วนทั้งหมดก่อน แล้วปัดครั้งเดียวตอนท้าย
    amount = Fraction(paid * (100 - used_percent), 100)
    if restock:
        amount *= Fraction(7, 8)  # หัก 12.5%

    # half-up: ปัดเศษ .5 ขึ้น (ค่าไม่ติดลบ จึงใช้ floor ได้)
    num, den = amount.numerator, amount.denominator
    return (2 * num + den) // (2 * den)


def main():
    try:
        data = json.loads(sys.stdin.read())
        result = refund(data['paid'], data['used_percent'], data['restock'])
    except (ValueError, KeyError, TypeError) as e:
        print(json.dumps({'ok': False, 'error': str(e)}))
        return 2
    print(json.dumps({'ok': True, 'result': result}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
