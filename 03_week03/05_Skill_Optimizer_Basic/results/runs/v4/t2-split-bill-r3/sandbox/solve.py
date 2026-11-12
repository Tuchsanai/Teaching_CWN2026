import json
import sys


def _check_int(value, name):
    if type(value) is not int:
        raise ValueError(f"{name} must be an int")


def split_bill(total, people, tip_percent):
    _check_int(total, "total")
    _check_int(people, "people")
    _check_int(tip_percent, "tip_percent")
    if total < 0:
        raise ValueError("total must be >= 0")
    if people < 1:
        raise ValueError("people must be >= 1")
    if not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be between 0 and 100")

    # half-up rounding once, integer arithmetic only
    grand = (total * (100 + tip_percent) + 50) // 100
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]


def _parse(arg):
    try:
        return int(arg)
    except ValueError:
        raise ValueError(f"invalid integer: {arg}")


def main(argv):
    try:
        if len(argv) != 3:
            raise ValueError("usage: solve.py TOTAL PEOPLE TIP_PERCENT")
        result = split_bill(*[_parse(a) for a in argv])
    except ValueError as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
