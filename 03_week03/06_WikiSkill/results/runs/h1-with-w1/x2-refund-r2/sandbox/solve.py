from fractions import Fraction
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


FEE_RATE = Fraction(125, 1000)  # ค่าดำเนินการ 12.5%
CUTOFF_PERCENT = 80             # เรียนเกินนี้ไม่คืนเงิน


def refund(paid, used_percent, restock):
    """คืนเงินคอร์สชงกาแฟ (หน่วยสตางค์ จำนวนเต็ม ปัดครึ่งขึ้น)

    paid         : เงินที่ลูกค้าจ่าย (สตางค์, ตั้งแต่ 0)
    used_percent : เรียนไปแล้วกี่เปอร์เซ็นต์ (0–100)
    restock      : True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
    """
    paid = _int(paid, 'paid', lo=0)
    used_percent = _int(used_percent, 'used_percent', lo=0, hi=100)
    restock = _bool(restock, 'restock')

    if used_percent > CUTOFF_PERCENT:
        return 0

    amount = Fraction(paid * (100 - used_percent), 100)
    if restock:
        amount -= amount * FEE_RATE

    # ปัดครั้งเดียวตอนท้าย แบบครึ่งขึ้น
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
