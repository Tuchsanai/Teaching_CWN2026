import json
import sys


def need_int(v, name, low=None, high=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and v < low) or (high is not None and v > high):
        raise ValueError(f"{name} อยู่นอกช่วง")
    return v


def split_bill(total, people, tip_percent):
    need_int(total, "total", 0)
    need_int(people, "people", 1)
    need_int(tip_percent, "tip_percent", 0, 100)
    # สมมติฐาน: ยอดรวมรวมทิปปัดครึ่งขึ้นครั้งเดียว (เงินที่ลูกค้าจ่าย)
    grand = (2 * total * (100 + tip_percent) + 100) // 200
    base, rem = divmod(grand, people)
    return [base + 1 if i < rem else base for i in range(people)]


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = split_bill(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
