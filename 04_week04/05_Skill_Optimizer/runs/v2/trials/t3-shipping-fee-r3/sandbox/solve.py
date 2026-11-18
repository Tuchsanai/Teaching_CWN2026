import json
import sys
from fractions import Fraction


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์"""
    if not _is_int(weight_g) or not 1 <= weight_g <= 30000:
        raise ValueError("weight_g must be int in 1..30000")
    if not _is_int(distance_km) or distance_km < 0:
        raise ValueError("distance_km must be int >= 0")
    if not isinstance(express, bool):
        raise ValueError("express must be bool")
    if express and weight_g > 20000:
        raise ValueError("express allows weight up to 20000 g")
    if distance_km == 0:
        return 0  # รับเองที่ร้าน
    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        fee = 8000 + Fraction(1500 * (weight_g - 5000), 1000)
    if distance_km > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    # ปัดครึ่งขึ้นด้วยเลขจำนวนเต็ม
    return (2 * fee.numerator + fee.denominator) // (2 * fee.denominator)


def _main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        args = [data[k] for k in ("weight_g", "distance_km", "express")]
        out, code = {"ok": True, "result": shipping_fee(*args)}, 0
    except KeyError as e:
        out, code = {"ok": False, "error": "missing key: %s" % e.args[0]}, 2
    except Exception as e:
        out, code = {"ok": False, "error": str(e) or "invalid input"}, 2
    print(json.dumps(out, ensure_ascii=False))
    sys.exit(code)


if __name__ == "__main__":
    _main()
