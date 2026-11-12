import json
import math
import sys
from fractions import Fraction

# อัตราเงินคืน (เศษส่วนเพื่อคำนวณแม่นยำ ไม่ใช้ float)
RATES = {
    'silver': Fraction(15, 1000),   # 1.5%
    'gold': Fraction(25, 1000),     # 2.5%
    'platinum': Fraction(4, 100),   # 4%
}
MIN_AMOUNT = 10000        # 100 บาท (หน่วยสตางค์) ต่ำกว่านี้ไม่ได้เงินคืน
MAX_CASHBACK = 20000      # 200 บาท (หน่วยสตางค์) เพดานต่อบิล
BIRTHDAY_MULTIPLIER = 2   # ซื้อในเดือนเกิดได้ 2 เท่า


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


def cashback(amount, tier, birthday):
    """คืนค่าเงินคืนเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้น ปัดครั้งเดียวตอนท้าย)"""
    amount = _int(amount, 'amount', lo=0)
    if not isinstance(tier, str) or tier not in RATES:
        raise ValueError('tier must be one of silver, gold, platinum')
    birthday = _bool(birthday, 'birthday')

    if amount < MIN_AMOUNT:
        return 0

    multiplier = BIRTHDAY_MULTIPLIER if birthday else 1
    exact = Fraction(amount) * RATES[tier] * multiplier
    rounded = math.floor(exact + Fraction(1, 2))  # half-up
    return min(rounded, MAX_CASHBACK)


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
