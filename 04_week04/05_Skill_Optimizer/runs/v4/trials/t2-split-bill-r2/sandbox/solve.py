import json
import sys


def _check_int(name, value, lo, hi=None):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be int")
    if value < lo or (hi is not None and value > hi):
        raise ValueError(f"{name} out of range")


def split_bill(total, people, tip_percent):
    _check_int("total", total, 0)
    _check_int("people", people, 1)
    _check_int("tip_percent", tip_percent, 0, 100)
    # total * (100 + tip) / 100 สตางค์ ปัดครึ่งขึ้นครั้งเดียวตอนท้าย (เลขจำนวนเต็มล้วน)
    grand = (total * (100 + tip_percent) + 50) // 100
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]


def main():
    data = json.load(sys.stdin)
    if not isinstance(data, dict):
        raise ValueError("input must be a JSON object")
    try:
        args = (data["total"], data["people"], data["tip_percent"])
    except KeyError as e:
        raise ValueError(f"missing {e}")
    json.dump(split_bill(*args), sys.stdout)
    sys.stdout.write("\n")


if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
