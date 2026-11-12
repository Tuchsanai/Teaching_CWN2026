"""BaanKafe: คำนวณเงินคืนของคอร์สสอนชงกาแฟ (หน่วยเป็นสตางค์ จำนวนเต็ม)

กติกา
- คืนตามสัดส่วนของส่วนที่ยังไม่ได้เรียน: paid * (100 - used_percent) / 100
- เรียนไปแล้วเกิน 80% (used_percent > 80) ไม่คืนเงิน
- restock=True หักค่าดำเนินการ 12.5% ของยอดที่จะคืน (เหลือ 7/8)
- ปัดเศษแบบ half-up ครั้งเดียวตอนท้าย ด้วยจำนวนเต็มล้วน (ไม่ใช้ float)
"""

import json
import sys


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
    """คืนยอดเงินที่ต้องคืนลูกค้า (สตางค์ จำนวนเต็ม)

    paid: เงินที่ลูกค้าจ่าย (สตางค์, >= 0)
    used_percent: เปอร์เซ็นต์ที่เรียนไปแล้ว (0-100)
    restock: True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
    """
    paid = _int(paid, 'paid', lo=0)
    used_percent = _int(used_percent, 'used_percent', lo=0, hi=100)
    restock = _bool(restock, 'restock')

    if used_percent > 80:
        return 0

    # ยอดเป็นเศษส่วน num/den โดย den = 800 (100 สำหรับสัดส่วน × 8 สำหรับค่าดำเนินการ 12.5%)
    # ไม่หักค่าดำเนินการ: paid*(100-used)/100 = paid*(100-used)*8/800
    # หักค่าดำเนินการ:    paid*(100-used)*7/800
    den = 800
    num = paid * (100 - used_percent) * (7 if restock else 8)

    # ปัดครึ่งขึ้น (half-up) ด้วยจำนวนเต็มล้วน
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
