import json
import sys


def _check_int(name, value, low=None, high=None):
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    if high is not None and value > high:
        raise ValueError(f"{name} ต้องไม่เกิน {high}")
    return value


def split_bill(total, people, tip_percent):
    """คืน list ของยอดที่แต่ละคนจ่าย (สตางค์ จำนวนเต็ม) เรียงตามลำดับคน"""
    total = _check_int("total", total, low=0)
    people = _check_int("people", people, low=1)
    tip_percent = _check_int("tip_percent", tip_percent, low=0, high=100)

    # ยอดหลังทิป = ยอดบิล คูณ (100 + ทิป) แล้วหารด้วย 100 เก็บเป็นตัวเศษ num กับตัวส่วน den ยังไม่ปัด
    num = total * (100 + tip_percent)
    den = 100
    # ปัดครึ่งขึ้นครั้งเดียวที่ขั้นสุดท้าย
    grand = (2 * num + den) // (2 * den)

    # หารเท่ากัน เศษสตางค์ให้คนลำดับแรก ๆ คนละ 1 สตางค์
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input ต้องเป็น JSON object")
        missing = [k for k in ("total", "people", "tip_percent") if k not in data]
        if missing:
            raise ValueError("ขาด key: " + ", ".join(missing))
        result = split_bill(data["total"], data["people"], data["tip_percent"])
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
