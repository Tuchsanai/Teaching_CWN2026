import json
import sys


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (ปัด half-up ครั้งเดียวตอนท้าย)"""
    if type(weight_g) is not int or not 1 <= weight_g <= 30000:
        raise ValueError("weight_g must be int 1-30000")
    if type(distance_km) is not int or distance_km < 0:
        raise ValueError("distance_km must be int >= 0")
    if type(express) is not bool:
        raise ValueError("express must be bool")

    # ฐาน (สตางค์) x2 เพื่อให้เป็นจำนวนเต็ม: ส่วนเกินกรัมละ 1.5 สตางค์
    if weight_g <= 1000:
        base2 = 4000 * 2
    elif weight_g <= 5000:
        base2 = 8000 * 2
    else:
        base2 = 16000 + 3 * (weight_g - 5000)
    far_n = 6 if distance_km > 100 else 5      # x6/5 หรือ x1
    exp_n = 3 if express else 2                # x3/2 หรือ x1
    num = base2 * far_n * exp_n
    den = 2 * 5 * 2
    return (num + den // 2) // den


def main(argv):
    try:
        if len(argv) != 3:
            raise ValueError("usage: solve.py WEIGHT_G DISTANCE_KM EXPRESS(true|false)")
        w, d = argv[0], argv[1]
        if not (w.lstrip("-").isdigit() and d.lstrip("-").isdigit()):
            raise ValueError("weight and distance must be integers")
        e = {"true": True, "false": False}.get(argv[2].lower())
        result = shipping_fee(int(w), int(d), e)
        print(json.dumps({"ok": True, "result": result}))
        return 0
    except ValueError as ex:
        print(json.dumps({"ok": False, "error": str(ex)}))
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
