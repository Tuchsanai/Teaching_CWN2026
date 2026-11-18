import json
import sys


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (คำนวณด้วยเศษส่วนแม่นตรง ปัดครึ่งขึ้นครั้งเดียวตอนท้าย)"""
    if not _is_int(weight_g) or not 1 <= weight_g <= 30000:
        raise ValueError("weight_g must be int in 1..30000")
    if not _is_int(distance_km) or distance_km < 0:
        raise ValueError("distance_km must be int >= 0")
    if not isinstance(express, bool):
        raise ValueError("express must be bool")
    if distance_km == 0:
        return 0  # นโยบาย: 0 กม. ไม่คิดค่าส่ง
    if express and weight_g > 20000:
        raise ValueError("express allowed up to 20000 g")

    # ค่าฐานเป็นสตางค์ = num/den
    if weight_g <= 1000:
        num, den = 4000, 1
    elif weight_g <= 5000:
        num, den = 8000, 1
    else:
        # ส่วนเกิน (g) * 1500 สตางค์ / 1000 g
        num, den = 16000 + 3 * (weight_g - 5000), 2
    if distance_km > 100:
        num, den = num * 12, den * 10
    if express:
        num, den = num * 15, den * 10
    return (2 * num + den) // (2 * den)


def main():
    try:
        data = json.load(sys.stdin)
        fee = shipping_fee(data["weight_g"], data["distance_km"], data["express"])
    except (ValueError, KeyError, TypeError) as e:
        print(json.dumps({"error": str(e)}))
        return 1
    print(json.dumps({"fee_satang": fee}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
