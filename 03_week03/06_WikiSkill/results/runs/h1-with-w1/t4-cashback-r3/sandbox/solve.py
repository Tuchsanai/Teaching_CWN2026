"""คิดเงินคืนสมาชิกร้านกาแฟ BaanKafe (หน่วยเงินเป็นสตางค์ จำนวนเต็ม)."""
import json
import sys
from fractions import Fraction

MIN_AMOUNT = 10000  # ยอดซื้อขั้นต่ำ 100 บาท (สตางค์)
CAP = 20000  # เงินคืนสูงสุด 200 บาทต่อบิล (สตางค์)
BIRTHDAY_MULT = 2  # ซื้อในเดือนเกิดได้ 2 เท่า
RATES = {
    'silver': Fraction(15, 1000),  # 1.5%
    'gold': Fraction(25, 1000),  # 2.5%
    'platinum': Fraction(4, 100),  # 4%
}


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


def _round_half_up(x):
    """ปัดเศษ half-up ของ Fraction ที่ไม่ติดลบ ให้เป็นจำนวนเต็ม (ปัดครั้งเดียว)."""
    n, d = x.numerator, x.denominator
    return (2 * n + d) // (2 * d)


def cashback(amount, tier, birthday):
    """คืนค่าเงินคืนเป็นสตางค์ (จำนวนเต็ม)."""
    amount = _int(amount, 'amount', lo=0)
    if not (isinstance(tier, str) and tier in RATES):
        raise ValueError('tier must be one of silver, gold, platinum')
    birthday = _bool(birthday, 'birthday')

    if amount < MIN_AMOUNT:
        return 0

    exact = Fraction(amount) * RATES[tier] * (BIRTHDAY_MULT if birthday else 1)
    return min(CAP, _round_half_up(exact))


def main():
    try:
        data = json.loads(sys.stdin.read())
        result = cashback(data['amount'], data['tier'], data['birthday'])
    except (ValueError, KeyError, TypeError) as e:
        print(json.dumps({'ok': False, 'error': str(e)}))
        return 2
    print(json.dumps({'ok': True, 'result': result}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
