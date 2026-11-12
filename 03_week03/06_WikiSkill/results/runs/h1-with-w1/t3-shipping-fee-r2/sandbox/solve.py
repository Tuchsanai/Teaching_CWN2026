"""ค่าส่งเมล็ดกาแฟ BaanKafe

หน่วยเงินเป็นสตางค์ (จำนวนเต็ม) ทุกการคำนวณใช้ Fraction และปัดครั้งเดียวตอนท้ายแบบ half-up
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


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นสตางค์ (จำนวนเต็ม)

    weight_g    : น้ำหนักกรัม 1–30,000
    distance_km : ระยะทางกิโลเมตร ตั้งแต่ 0
    express     : True = ส่งด่วน (คูณ 1.5)
    """
    weight_g = _int(weight_g, 'weight_g', 1, 30000)
    distance_km = _int(distance_km, 'distance_km', 0)
    express = _bool(express, 'express')

    # ฐานราคาเป็นสตางค์ (1 บาท = 100 สตางค์)
    # เกิน 5,000 กรัม: กิโลกรัมละ 15 บาท = 1,500 สตางค์ต่อ 1,000 กรัม = 3/2 สตางค์ต่อกรัม (คิดตามสัดส่วน)
    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        fee = 8000 + (weight_g - 5000) * Fraction(3, 2)

    # ระยะทางเกิน 100 กม. คิดเพิ่ม 20%
    if distance_km > 100:
        fee *= Fraction(6, 5)

    # ส่งด่วน คิดเพิ่ม 50% (คูณต่อจากข้อก่อน)
    if express:
        fee *= Fraction(3, 2)

    # ปัดครั้งเดียวตอนท้ายแบบ half-up
    return (2 * fee.numerator + fee.denominator) // (2 * fee.denominator)


def main():
    try:
        data = json.loads(sys.stdin.read())
        result = shipping_fee(data['weight_g'], data['distance_km'], data['express'])
    except (ValueError, KeyError, TypeError) as e:
        print(json.dumps({'ok': False, 'error': str(e)}))
        return 2
    print(json.dumps({'ok': True, 'result': result}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
