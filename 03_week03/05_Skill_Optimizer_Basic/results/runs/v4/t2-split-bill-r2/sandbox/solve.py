import json
import sys


def _check(v, lo, hi, name):
    if type(v) is not int:
        raise ValueError(f"{name} must be int")
    if v < lo or (hi is not None and v > hi):
        raise ValueError(f"{name} out of range")


def split_bill(total, people, tip_percent):
    _check(total, 0, None, "total")
    _check(people, 1, None, "people")
    _check(tip_percent, 0, 100, "tip_percent")
    # half-up rounding once at the end
    grand = (total * (100 + tip_percent) + 50) // 100
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]


def main(argv):
    try:
        if len(argv) != 3:
            raise ValueError("usage: solve.py total people tip_percent")
        vals = []
        for s in argv:
            s2 = s.strip()
            if not (s2.isascii() and s2.lstrip("-").isdigit() and s2.count("-") <= 1):
                raise ValueError("arguments must be integers")
            vals.append(int(s2))
        print(json.dumps({"ok": True, "result": split_bill(*vals)}))
        return 0
    except ValueError as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
