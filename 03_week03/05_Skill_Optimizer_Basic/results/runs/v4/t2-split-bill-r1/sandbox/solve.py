import json
import sys


def _check(name, v, lo, hi=None):
    if type(v) is not int:
        raise ValueError(f"{name} must be int")
    if v < lo or (hi is not None and v > hi):
        raise ValueError(f"{name} out of range")


def split_bill(total, people, tip_percent):
    _check("total", total, 0)
    _check("people", people, 1)
    _check("tip_percent", tip_percent, 0, 100)
    # ปัด half-up ครั้งเดียวตอนท้าย: total*(100+tip)/100
    grand = (total * (100 + tip_percent) + 50) // 100
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]


def main(argv):
    try:
        if len(argv) != 3:
            raise ValueError("usage: solve.py total people tip_percent")
        try:
            args = [int(a) for a in argv]
        except ValueError:
            raise ValueError("arguments must be integers")
        print(json.dumps({"ok": True, "result": split_bill(*args)}))
        return 0
    except ValueError as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
