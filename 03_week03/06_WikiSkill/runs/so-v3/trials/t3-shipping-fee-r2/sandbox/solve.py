import json
import sys
from fractions import Fraction


def _int(v):
    if type(v) is not int:
        raise ValueError("ตัวเลขต้องเป็น int")
    return v


def shipping_fee(weight_g, distance_km, express):
    weight_g = _int(weight_g)
    distance_km = _int(distance_km)
    if type(express) is not bool:
        raise ValueError("express ต้องเป็น bool")
    if not 1 <= weight_g <= 30000:
        raise ValueError("น้ำหนักต้องอยู่ระหว่าง 1-30000 กรัม")
    if distance_km < 0:
        raise ValueError("ระยะทางต้องไม่ติดลบ")
    if express and weight_g > 20000:
        raise ValueError("ส่งด่วนรับน้ำหนักไม่เกิน 20000 กรัม")
    if distance_km == 0:
        return 0
    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        fee = 8000 + Fraction((weight_g - 5000) * 1500, 1000)
    if distance_km > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)
    n, d = fee.numerator, fee.denominator
    return (2 * n + d) // (2 * d)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("ต้องเป็น JSON object")
        args = [data[k] for k in ("weight_g", "distance_km", "express")]
        out = {"ok": True, "result": shipping_fee(*args)}
        code = 0
    except (ValueError, KeyError) as e:
        out = {"ok": False, "error": "ขาด key " + str(e) if isinstance(e, KeyError) else str(e)}
        code = 2
    print(json.dumps(out, ensure_ascii=False))
    sys.exit(code)


if __name__ == "__main__":
    main()
