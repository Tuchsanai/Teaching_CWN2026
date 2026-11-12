import json
import sys


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (คำนวณด้วยจำนวนเต็มล้วน ปัด half-up ครั้งเดียว)"""
    if type(weight_g) is not int or type(distance_km) is not int or type(express) is not bool:
        raise ValueError("invalid input type")
    if weight_g < 1 or weight_g > 30000:
        raise ValueError("weight_g must be 1..30000")
    if distance_km < 0:
        raise ValueError("distance_km must be >= 0")

    # หน่วย: สตางค์ x 1000  (15 บาท/กก. = 1500 สตางค์/1000 กรัม)
    if weight_g <= 1000:
        num = 4000 * 1000
    elif weight_g <= 5000:
        num = 8000 * 1000
    else:
        num = 8000 * 1000 + (weight_g - 5000) * 1500
    den = 1000
    if distance_km > 100:
        num *= 120
        den *= 100
    if express:
        num *= 150
        den *= 100
    return (2 * num + den) // (2 * den)


def _main(argv):
    try:
        if len(argv) != 3:
            raise ValueError("usage: solve.py WEIGHT_G DISTANCE_KM EXPRESS(true/false)")
        flag = argv[2].lower()
        if flag not in ("true", "false"):
            raise ValueError("express must be true or false")
        result = shipping_fee(int(argv[0]), int(argv[1]), flag == "true")
    except ValueError as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
