"""BaanKafe: หารบิลให้ลูกค้า (คำนวณเป็นจำนวนเต็มสตางค์ล้วน ไม่ใช้ float)"""

import json
import sys


def _require_int(value, label, lo=None, hi=None):
    # ใช้ type() is int เพื่อปฏิเสธ bool, float และ str
    if type(value) is not int:
        raise ValueError(f"{label} ต้องเป็นจำนวนเต็ม")
    if lo is not None and value < lo:
        raise ValueError(f"{label} ต้องไม่น้อยกว่า {lo}")
    if hi is not None and value > hi:
        raise ValueError(f"{label} ต้องไม่เกิน {hi}")
    return value


def split_bill(total, people, tip_percent):
    """หารบิลให้คนทั้งหมด คืน list ของยอดที่แต่ละคนจ่าย (สตางค์ int) เรียงตามลำดับคน

    total        ยอดบิลเป็นสตางค์ (>= 0)
    people       จำนวนคน (>= 1)
    tip_percent  ทิปเป็นเปอร์เซ็นต์ จำนวนเต็ม 0–100
    """
    total = _require_int(total, "total", lo=0)
    people = _require_int(people, "people", lo=1)
    tip_percent = _require_int(tip_percent, "tip_percent", lo=0, hi=100)

    # ทิป = total * tip_percent / 100 ปัดครึ่งขึ้นครั้งเดียว (ตัวเศษไม่ติดลบ จึงใช้ (x + 50) // 100 ได้)
    tip = (total * tip_percent + 50) // 100
    due = total + tip

    # หารให้ลงตัว คนลำดับแรกๆ ได้เพิ่มคนละ 1 สตางค์
    base, extra = divmod(due, people)
    return [base + 1 if i < extra else base for i in range(people)]


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = split_bill(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
