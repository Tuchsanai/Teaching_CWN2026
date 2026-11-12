import json
import sys


def _check_int(name, value):
    # type(...) is int ไม่รับ bool, float, str, None และค่าอื่นที่ไม่ใช่ int จริง
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม (int)")


def split_bill(total, people, tip_percent):
    _check_int("total", total)
    _check_int("people", people)
    _check_int("tip_percent", tip_percent)
    if total < 0:
        raise ValueError("total ต้องไม่ติดลบ")
    if people < 1:
        raise ValueError("people ต้องอย่างน้อย 1")
    if not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent ต้องอยู่ในช่วง 0-100")

    # ยอดที่ต้องหาร = total + total * tip_percent / 100
    # เก็บเป็นเศษ num กับตัวส่วน den ไม่ปัดระหว่างทาง แล้วปัดครั้งเดียวตอนท้าย (half-up)
    num = total * (100 + tip_percent)
    den = 100
    grand = (2 * num + den) // (2 * den)

    # หารเท่ากัน เศษสตางค์ให้คนลำดับแรก ๆ คนละ 1 สตางค์
    base = grand // people
    extra = grand - base * people
    return [base + 1 if i < extra else base for i in range(people)]


def _main():
    try:
        data = json.loads(sys.stdin.read())
        if type(data) is not dict:
            raise ValueError("input ต้องเป็น JSON object")
        for key in ("total", "people", "tip_percent"):
            if key not in data:
                raise ValueError(f"ขาด key: {key}")
        result = split_bill(data["total"], data["people"], data["tip_percent"])
    except (ValueError, RecursionError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
