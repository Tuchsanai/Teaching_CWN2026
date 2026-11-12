"""BaanKafe bill splitter.

หารบิลเป็นสตางค์ (จำนวนเต็ม) พร้อมทิป โดยไม่ใช้ float
"""
import json
import sys


def _int(x, name, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f'{name} must be int')
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f'{name} out of range')
    return x


def split_bill(total, people, tip_percent):
    """คืน list ของยอดที่แต่ละคนจ่าย (สตางค์) เรียงตามลำดับคน

    ยอดที่ต้องหาร = total + ทิป (total * tip_percent / 100) ปัดแบบ half-up ครั้งเดียวตอนท้าย
    หารไม่ลงตัว -> คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์
    """
    total = _int(total, 'total', lo=0)
    people = _int(people, 'people', lo=1)
    tip_percent = _int(tip_percent, 'tip_percent', lo=0, hi=100)

    # grand = round_half_up(total * (100 + tip_percent) / 100), ทำด้วยจำนวนเต็มล้วน
    num = total * (100 + tip_percent)
    den = 100
    grand = (2 * num + den) // (2 * den)

    base, rem = divmod(grand, people)
    return [base + 1 if i < rem else base for i in range(people)]


def main():
    try:
        data = json.loads(sys.stdin.read())
        result = split_bill(data['total'], data['people'], data['tip_percent'])
    except (ValueError, KeyError, TypeError) as e:
        print(json.dumps({'ok': False, 'error': str(e)}, ensure_ascii=False))
        return 2
    print(json.dumps({'ok': True, 'result': result}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
