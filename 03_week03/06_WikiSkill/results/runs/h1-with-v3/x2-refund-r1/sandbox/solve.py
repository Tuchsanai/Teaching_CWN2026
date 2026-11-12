import json
import sys

CUTOFF_PERCENT = 80
FEE_PER_MILLE = 125  # ค่าดำเนินการ 12.5% = 125/1000
MILLE = 1000


def refund(paid, used_percent, restock):
    """คืนเงินของคอร์สสอนชงกาแฟ (หน่วยสตางค์ จำนวนเต็ม)

    paid          เงินที่ลูกค้าจ่าย (สตางค์, >= 0)
    used_percent  เรียนไปแล้วกี่เปอร์เซ็นต์ (จำนวนเต็ม 0-100)
    restock       True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
    """
    if type(paid) is not int:
        raise ValueError("paid ต้องเป็นจำนวนเต็ม (int) หน่วยสตางค์")
    if paid < 0:
        raise ValueError("paid ต้องไม่ติดลบ")
    if type(used_percent) is not int:
        raise ValueError("used_percent ต้องเป็นจำนวนเต็ม (int)")
    if not 0 <= used_percent <= 100:
        raise ValueError("used_percent ต้องอยู่ในช่วง 0-100")
    if type(restock) is not bool:
        raise ValueError("restock ต้องเป็น bool (True/False)")

    if used_percent > CUTOFF_PERCENT:
        return 0

    # เก็บทุกขั้นเป็นเศษ num / ตัวส่วน den ก่อน แล้วปัดครั้งเดียวตอนท้าย
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        num = num * (MILLE - FEE_PER_MILLE)
        den = den * MILLE

    # ปัดครึ่งขึ้น (half-up)
    return (2 * num + den) // (2 * den)


def _main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input ต้องเป็น JSON object")
        args = {}
        for key in ("paid", "used_percent", "restock"):
            if key not in data:
                raise ValueError(f"ขาด key: {key}")
            args[key] = data[key]
        result = refund(**args)
    except ValueError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
