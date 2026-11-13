import json
import sys


def _check_int(v, name):
    if type(v) is not int:
        raise ValueError(f"{name} must be int")
    return v


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (ปัด half-up ครั้งเดียวตอนท้าย)"""
    _check_int(weight_g, "weight_g")
    _check_int(distance_km, "distance_km")
    if type(express) is not bool:
        raise ValueError("express must be bool")
    if not 1 <= weight_g <= 30000:
        raise ValueError("weight_g out of range")
    if distance_km < 0:
        raise ValueError("distance_km must be >= 0")

    # หน่วย: สตางค์ x 1000 (15 บาท/กก. = 1500 สตางค์/กก. = 1.5 สตางค์/กรัม)
    if weight_g <= 1000:
        num = 4000 * 1000
    elif weight_g <= 5000:
        num = 8000 * 1000
    else:
        num = 8000 * 1000 + (weight_g - 5000) * 1500
    den = 1000
    if distance_km > 100:  # +20% = x6/5
        num *= 6
        den *= 5
    if express:  # +50% = x3/2
        num *= 3
        den *= 2
    return (2 * num + den) // (2 * den)


def main(argv):
    try:
        if len(argv) != 3:
            raise ValueError("usage: solve.py WEIGHT_G DISTANCE_KM EXPRESS(true|false)")
        try:
            w, d = int(argv[0]), int(argv[1])
        except ValueError:
            raise ValueError("weight and distance must be integers")
        e = argv[2].lower()
        if e not in ("true", "false"):
            raise ValueError("express must be true or false")
        print(json.dumps({"ok": True, "result": shipping_fee(w, d, e == "true")}))
        return 0
    except ValueError as ex:
        print(json.dumps({"ok": False, "error": str(ex)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
